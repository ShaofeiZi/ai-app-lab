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

import React, { useEffect, useRef } from 'react';
import MessageList from './MessageList';
import InputArea from './InputArea';
import { Message } from '@/hooks/useCloudAgent';

interface ChatViewProps {
  messages: Message[];
  handleSendMessage: (text: string) => void;
  handleCancel: () => void;
  isCalling: boolean;
  isCanceling: boolean;
}

const ChatView: React.FC<ChatViewProps> = ({
  messages,
  handleSendMessage,
  handleCancel,
  isCalling,
  isCanceling
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 每次消息更新后都把视口滚到最底部，
  // 这样用户不用手动拖动滚动条去追最新的执行步骤。
  const scrollToBottom = (): void => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex flex-col h-full">
      {/* 上半部分是可滚动消息区，下半部分是固定输入框。 */}
      <div
        className="flex-1 overflow-y-auto mb-6"
        style={{
          scrollbarWidth: 'thin',
          scrollbarColor: '#E5E7EB transparent',
        }}
      >
        <style jsx>{`
          div::-webkit-scrollbar {
            width: 6px;
            height: 6px;
          }
          div::-webkit-scrollbar-track {
            background: transparent;
            border-radius: 6px;
          }
          div::-webkit-scrollbar-thumb {
            background-color: #e5e7eb;
            border-radius: 6px;
          }
          div::-webkit-scrollbar-thumb:hover {
            background-color: #d1d5db;
          }
        `}</style>
        <MessageList messages={messages} />
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区始终固定在底部，方便连续发起任务。 */}
      <InputArea
        handleSendMessage={handleSendMessage}
        handleCancel={handleCancel}
        isCalling={isCalling}
        isCanceling={isCanceling}
      />
    </div>
  );
};

export default ChatView;
