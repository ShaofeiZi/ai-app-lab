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

import { STSToken } from "@/lib/vePhone";

// 这个文件放的是前后端共享或前端内部复用的数据结构。
// 初学者可以把它看成“对象的说明书”，告诉我们某份数据应该长什么样。

// 模型相关类型
export interface Model {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
}

// 环境配置相关类型
export interface EnvironmentConfig {
  apiKey?: string;
  serviceUrl?: string;
}

// UIMessage 是“页面上可能出现的消息形态”的联合类型。
export type UIMessage = UIChatMessage | UIButtonMessage | UIThinkingMessage;

export interface UIChatMessage {
  id: string;
  isFinish: boolean;
  content: string;
  isUser: boolean;
  timestamp: number;
}

export interface UIButtonMessage {
  id: string;
  isFinish?: boolean;
  content: string;
  isUser: boolean;
  isButton: boolean;
  timestamp: number;
}

export interface UIThinkingMessage {
  id: string;
  // isThinking 为 true 表示这类消息不是普通对话文本，而是执行过程说明。
  isThinking: true;
  executionState: {
    status: 'executing' | 'completed' | 'idle';
    currentStep: string;
    completedSteps: string[];
    isExecuting: boolean;
  };
  showExecutionStatus: boolean;
  timestamp: number;
}

// Conversation 更偏向通用聊天产品的数据结构，
// 当前 demo 里真正高频使用的是后面的 SessionBackendResponse / SessionResponse。
export interface Conversation {
  id: string;
  title: string;
  messages: UIMessage[];
  createdAt: string;
  updatedAt: string;
}


export type AgentType = 'ui-tars' |  'doubao-vision-pro';

export type ErrorResponse = {
  error: {
    code: number
    message: string
  }
}

export type SessionBackendResponse = ErrorResponse & {
  // thread_id 是浏览器和后端共享的会话主键。
  thread_id: string
  // chat_thread_id 是 Agent 内部使用的对话上下文 ID。
  chat_thread_id: string
  userInfo: {
    accountId: string
    userId: string
    name: string
  }
  pod: {
    product_id: string
    pod_id: string
    expired_time: number
    token: STSToken
    size: { width: number, height: number }
    account_id: string
  }
}

export type SessionResponse = {
  // SessionResponse 对比 SessionBackendResponse 少了 thread_id / chat_thread_id / error，
  // 更适合前端把“真正的会话内容”放进全局状态。
  userInfo: {
    accountId: string
    userId: string
    name: string
  }
  pod: {
    product_id: string
    pod_id: string
    expired_time: number
    token: STSToken
    size: { width: number, height: number }
    account_id: string
  }
}
