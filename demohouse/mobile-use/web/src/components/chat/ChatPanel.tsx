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

"use client";
import React, { useState, useEffect } from "react";
import { useAtom, useSetAtom, useAtomValue } from "jotai";
import { useCloudAgent, ChatMessage } from "@/hooks/useCloudAgent";
import { useTimeoutState } from "@/hooks/useTimeoutPhone";
import TimeoutView from "./TimeoutView";
import ChatView from "./ChatView";
import WelcomeView from "./WelcomeView";
import { MessageListAtom, SessionDataAtom, initMessageListAtom, initMessageStatusAtom, saveMessageListAtom } from "@/app/atom";
import ResetChat from "./ResetChat";

// 示例任务
const sampleTasks = [
  {
    id: 'task-2',
    title: '',
    description: '安装百度地图并从上海抖音新江湾广场导航到上海外滩',
  },
  {
    id: 'task-3',
    title: '',
    description: '安装大众点评APP，搜一下附近5km评价最好的火锅店',
  },
];

const ChatPanel: React.FC = () => {
  const [messages, setMessages] = useAtom(MessageListAtom);
  const [isCalling, setCalling] = useState(false);
  const [isCanceling, setCanceling] = useState(false);
  const [chatMode, setChatMode] = useState<'welcome' | 'chat' | 'init'>('init') // 明确的模式状态
  const cloudAgent = useCloudAgent();
  const { timeoutState } = useTimeoutState();
  const setSessionData = useSetAtom(SessionDataAtom);
  const initMessageList = useSetAtom(initMessageListAtom);
  const saveMessageList = useSetAtom(saveMessageListAtom);
  const initMessageStatus = useAtomValue(initMessageStatusAtom)

  // 如果当前 chatThreadId 对应的历史消息已经存在于 sessionStorage，
  // 这里会把它恢复出来，避免刷新页面后聊天区变空。
  useEffect(() => {
    if (cloudAgent?.threadId) {
      initMessageList();
    }
  }, [cloudAgent?.threadId, initMessageList]);

  // welcome / chat / init 三种模式的意义：
  // init: 还没决定该显示什么；
  // welcome: 没有历史消息，显示欢迎与样例任务；
  // chat: 已经有消息，直接进入对话界面。
  useEffect(() => {
    if (chatMode !== 'init' || initMessageStatus === false) {
      return
    }
    if (messages.length > 0) {
      setChatMode('chat');
    } else {
      setChatMode('welcome')
    }
  }, [messages, chatMode, initMessageStatus]);

  // 只要消息变了，就尽量持久化，保证刷新后能恢复上下文。
  useEffect(() => {
    if (messages.length > 0 && cloudAgent?.threadId) {
      saveMessageList();
    }
  }, [messages, cloudAgent?.threadId, saveMessageList]);


  const appendUserMessage = (message: string) => {
    // 用户消息先本地落一条，这样界面能立刻反馈“发送成功”，
    // 不需要等后端真正开始流式返回后才看到自己刚输入的内容。
    const newMessage: ChatMessage = {
      id: `${Date.now()}`,
      content: message,
      isUser: true,
      isFinish: true,
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, newMessage]);
    // 明确切换到聊天模式
    setChatMode('chat');
  };

  const handleCancel = async () => {
    // 取消按钮会通知后端停止当前任务，并把本地按钮状态切到“取消中”。
    setCanceling(true);
    await cloudAgent?.cancel();
    setCanceling(false);
  };

  const handleSendMessage = async (text: string) => {
    if (text.trim() === "") return;

    // 发送流程是“先追加用户消息，再发起 agent 调用”。
    appendUserMessage(text);
    setCalling(true);
    try {
      await cloudAgent?.call?.(text);
    } finally {
      setCalling(false);
    }
  };

  const handleRetry = () => {
    // 超时后重新体验时，最简单稳定的做法是：
    // 清空 threadId 和会话数据，然后整页刷新，从首页重新开始。
    cloudAgent?.setThreadId("");
    // 清空会话数据
    setSessionData(null);
    window.location.reload();
  };

  // 超时状态优先级最高，只要体验时间结束，就不再显示正常聊天区。
  if (timeoutState !== "active") {
    return <TimeoutView timeoutState={timeoutState} onRetry={handleRetry} />;
  }

  // 根据模式切换欢迎页或聊天页。
  if (chatMode === 'chat') {
    return (
      <>
        <ResetChat className='absolute z-10 top-0 right-0' />
        <ChatView
          messages={messages}
          handleSendMessage={handleSendMessage}
          handleCancel={handleCancel}
          isCalling={isCalling}
          isCanceling={isCanceling}
        />

      </>

    );
  }

  if (chatMode === 'welcome') {
    return (
      <WelcomeView
        handleSendMessage={handleSendMessage}
        handleCancel={handleCancel}
        isCalling={isCalling}
        isCanceling={isCanceling}
        sampleTasks={sampleTasks}
      />
    );
  }

  return <></>
};

export default ChatPanel;
