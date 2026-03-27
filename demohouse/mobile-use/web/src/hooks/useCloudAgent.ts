// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// Licensed under the 【火山方舟】原型应用软件自用许可协议
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at 
//     https://www.volcengine.com/docs/82379/1433703
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { useEffect } from 'react';
import { useAtomValue, useSetAtom } from 'jotai';
import { SSEMessage } from '@/lib/socket/abc';
import CloudAgent from '@/lib/cloudAgent';
import { MessageListAtom, cloudAgentAtom, saveMessageListAtom } from '@/app/atom';

interface BaseMessage {
  id: string;
  isUser?: boolean;
  isFinish: boolean;
  timestamp: number;
}

export interface ChatMessage extends BaseMessage {
  content: string;
  isUser: true;
}

export interface ThinkingMessage extends BaseMessage {
  isUser: false;
  steps: TaskStep[];
  taskId: string;
  summary?: Summary;
}

// 定义四种TaskStep类型
interface BaseStep {
  id: string;
  taskId: string;
}

export interface ToolCall {
  toolId: string;
  status: 'start' | 'stop' | 'success';
  toolType: 'tool_input' | 'tool_output';
  toolName: string;
  toolInput?: any;
  toolOutput?: any;
}

export interface UserInterruptStep extends BaseStep {
  type: 'user_interrupt';
  interruptType: 'text';
  content: string;
}

export interface Summary extends BaseStep {
  type: 'summary';
  content: string;
}

export interface ThinkStep extends BaseStep {
  type: 'think';
  content: string;
  toolCall?: ToolCall;
}

export type TaskStep = UserInterruptStep | ThinkStep;

export type Message = ChatMessage | ThinkingMessage;

export const useCloudAgentInit = () => {
  const setCloudAgent = useSetAtom(cloudAgentAtom);
  const setMessageList = useSetAtom(MessageListAtom);
  const saveMessageList = useSetAtom(saveMessageListAtom);

  useEffect(() => {
    // 这个 hook 负责把“后端推来的 SSE 事件”翻译成“前端消息列表状态”。
    // 页面组件只负责渲染，不需要自己理解 SSE 的细节。
    const handleSSEMessage = (json: SSEMessage) => {
      setMessageList((pre: Message[]) => {
        // 一个 task_id 对应 Agent 的一次完整执行过程。
        // 因此前端会把同一 task_id 的 think / tool / summary 事件收拢到同一条 ThinkingMessage 下。
        let thinkingMessage = pre.find(message => 'taskId' in message && message.taskId === json.task_id) as
          | ThinkingMessage
          | undefined;

        if (!thinkingMessage) {
          // 第一次收到这个 task_id 的事件时，先搭一个空壳消息容器。
          thinkingMessage = {
            id: json.task_id,
            isFinish: false,
            timestamp: Date.now(),
            isUser: false,
            steps: [],
            taskId: json.task_id,
          };
          pre.push(thinkingMessage);
        }

        if (!('type' in json)) {
          return [...pre];
        }

        switch (json.type) {
          case 'think':
            // think 事件可能是流式分段到达的，所以需要按 step id 增量拼接 content。
            let thinkStep = thinkingMessage.steps.find(step => step.type === 'think' && step.id === json.id) as
              | ThinkStep
              | undefined;

            if (!thinkStep) {
              // 第一次见到这个 step，就先创建一个空内容步骤。
              thinkStep = {
                id: json.id,
                taskId: json.task_id,
                type: 'think',
                content: '',
              };

              thinkingMessage.steps.push(thinkStep);
            }

            thinkStep.content = `${thinkStep.content}${json.content}`.replaceAll('\\n', '\n');
            break;
          case 'user_interrupt':
            // user_interrupt 代表 Agent 想向用户补充提问或等待用户提供信息。
            const newUserInterruptStep: UserInterruptStep = {
              id: json.id,
              taskId: json.task_id,
              type: 'user_interrupt',
              interruptType: json.interrupt_type,
              content: json.content,
            };

            thinkingMessage.steps.push(newUserInterruptStep);
            break;
          case 'tool':
            // tool 事件会附着在某个 think step 上，
            // 这样页面既能显示“模型想了什么”，也能显示“它随后调用了什么工具”。
            let thinkStepForTool = thinkingMessage.steps.find(step => step.type === 'think' && step.id === json.id) as
              | ThinkStep
              | undefined;

            if (!thinkStepForTool) {
              // 有些时候工具事件可能先于完整 think 文本到达，因此这里也允许先建壳。
              thinkStepForTool = {
                id: json.id,
                taskId: json.task_id,
                type: 'think',
                content: '',
                toolCall: {
                  toolId: json.tool_id,
                  status: json.status,
                  toolType: json.tool_type,
                  toolName: json.tool_name,
                  toolInput: json.tool_input,
                  toolOutput: json.tool_output,
                },
              };
              thinkingMessage.steps.push(thinkStepForTool);
            } else {
              // 同一工具调用的 start / success / stop 事件会逐步把 toolCall 信息补全。
              thinkStepForTool.toolCall = {
                ...(thinkStepForTool.toolCall || {}),
                toolId: json.tool_id,
                status: json.status,
                toolType: json.tool_type,
                toolName: json.tool_name,
                toolInput: json.tool_input,
                toolOutput: json.tool_output,
              };
            }
            break;
          case 'summary':
            // summary 也是可流式拼接的，所以这里同样按 task 内单独累积。
            if (!thinkingMessage.summary) {
              // 如果summary不存在，创建新的
              const newSummary: Summary = {
                id: json.id,
                taskId: json.task_id,
                type: 'summary',
                content: '',
              };
              thinkingMessage.summary = newSummary;
            }
            thinkingMessage.summary.content = `${thinkingMessage.summary.content}${json.content}`.replaceAll(
              '\\n',
              '\n',
            );
            break;
          default:
            break;
        }

        const updatedMessages = [...pre];
        // 状态更新后异步触发一次持久化，避免刷新页面丢失过程消息。
        setTimeout(() => saveMessageList(), 0);
        return updatedMessages;
      });
    };

    const handleSSEDone = () => {
      console.log('handleSSEDone');
      setMessageList((pre: Message[]) => {
        console.log('done');
        // DONE 事件的语义是：“当前任务的流结束了”。
        // 因此前端会把最后一条未完成消息标记成完成态，按钮和 loading 也能据此恢复。
        const lastUnfinishedIndex = pre.findLastIndex(msg => !msg.isFinish);
        if (lastUnfinishedIndex >= 0) {
          const updatedMessages = [...pre];
          updatedMessages[lastUnfinishedIndex] = {
            ...updatedMessages[lastUnfinishedIndex],
            isFinish: true,
          };
          // 触发保存到 sessionStorage
          setTimeout(() => saveMessageList(), 0);
          return updatedMessages;
        }
        return pre;
      });
    };

    // CloudAgent 封装了浏览器侧的 SSE 调用与取消逻辑。
    const agent = new CloudAgent();
    agent.onMessage(handleSSEMessage);
    agent.onMessageDone(handleSSEDone);
    setCloudAgent(agent);

    // 组件卸载时把监听器解绑，防止旧页面继续响应新事件。
    return () => {
      // 清理事件监听器
      agent.offMessage();
      agent.offMessageDone();
    };
  }, [setCloudAgent, setMessageList, saveMessageList]);
};

export const useCloudAgent = () => {
  const cloudAgent = useAtomValue(cloudAgentAtom);
  return cloudAgent;
};

export const useUpdateCloudAgentPodId = () => {
  const cloudAgent = useAtomValue(cloudAgentAtom);

  const updatePod = ({ productId, podId }: { productId: string, podId: string }) => {
    if (cloudAgent) {
      cloudAgent.setProductPodId(productId, podId);
    }
  };

  return { cloudAgent, updatePod };
};
