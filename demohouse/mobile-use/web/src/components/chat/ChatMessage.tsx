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
import React from 'react';
import { useAtomValue } from 'jotai';
import { cn } from '@/lib/utils/css';
import { UIChatMessage } from '@/types';
import { SessionDataAtom } from '@/app/atom';

// 这是渲染单条消息气泡时真正需要的最小字段集合。
interface BaseMessage {
  id: string;
  content: string;
  isUser?: boolean;
  isFinish: boolean;
  timestamp: number;
}

export function UserMessage({ message }: { message: BaseMessage | UIChatMessage }) {
  const sessionData = useAtomValue(SessionDataAtom);

  // 没有文字内容时就不渲染，避免页面出现空白气泡。
  if (!message.content) return null;

  // 优先展示当前会话中的用户名，没有时退回到默认名称。
  const userName = sessionData?.userInfo?.name || '火山账户名';

  // 这里用名字首字母充当简易头像，避免必须依赖真实头像资源。
  const avatarChar = userName.charAt(0).toUpperCase();

  return (
    <div className="flex flex-col items-end">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-sm font-bold text-gray-600">{userName}</span>
        <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center" style={{ backgroundColor: '#ecf2ff' }}>
          <span className="text-[#05f] font-blod text-sm font-medium">{avatarChar}</span>
        </div>
      </div>
      <div className="max-w-[85%]">
        <div
          className={cn(
            'py-3 px-4 rounded-lg transition-all duration-200 whitespace-pre-wrap break-all',
            'bg-[rgba(227,241,255,1)] text-gray-800 hover:bg-[rgba(227,241,255,0.8)]',
          )}
        >
          <span className="text-[14px] text-[#0C0D0E]">{message.content}</span>
        </div>
      </div>
    </div>
  );
}
