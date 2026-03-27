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

import { Message } from "@/hooks/useCloudAgent";
import CloudAgent from "@/lib/cloudAgent";
import { VePhoneClient } from "@/lib/vePhone";
import { SessionResponse } from "@/types";
import { atom } from "jotai";

// 这里把“前端共享状态”集中定义在一起。
// 可以把 atom 理解成一块全局的小状态仓库，多个组件都能订阅和修改。

// 从 sessionStorage 根据 chatThreadId 读取消息列表。
// 之所以不用 threadId，而用 chatThreadId，
// 是因为 reset 会保留外层 threadId，但会切换到新的对话上下文。
export const getMessagesFromStorage = (chatThreadId?: string): Message[] => {
  if (typeof window === 'undefined' || !chatThreadId) return [];
  try {
    const key = `mobile_use:${chatThreadId}:messages`;
    const stored = sessionStorage.getItem(key);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
};

// 每次消息列表更新后都可以把它持久化到 sessionStorage，
// 这样刷新页面时还能把历史对话恢复出来。
export const saveMessagesToStorage = (messages: Message[], chatThreadId?: string): void => {
  if (typeof window === 'undefined' || !chatThreadId) return;
  try {
    const key = `mobile_use:${chatThreadId}:messages`;
    sessionStorage.setItem(key, JSON.stringify(messages));
  } catch {
    // 忽略存储错误
  }
};

// 当前正在展示的云手机 pod ID。
export const PodIdAtom = atom<string | undefined>(undefined);
export const VePhoneAtom = atom<VePhoneClient>(
  new VePhoneClient()
);

// 浏览器侧的 CloudAgent 客户端实例，负责发请求和接收 SSE。
export const cloudAgentAtom = atom<CloudAgent | null>(null);

// 当前聊天页面上渲染的消息数组。
export const MessageListAtom = atom<Message[]>([]);

export const initMessageStatusAtom = atom<boolean>(false)

// 这是一个“带副作用的 atom”：
// 调用它时会从存储里读出历史消息，并同步到 MessageListAtom。
export const initMessageListAtom = atom(
  null,
  (get, set) => {
    const cloudAgent = get(cloudAgentAtom);
    const chatThreadId = cloudAgent?.chatThreadId;

    if (chatThreadId) {
      const storedMessages = getMessagesFromStorage(chatThreadId);
      set(MessageListAtom, storedMessages);
      set(initMessageStatusAtom, true) // 标记初始化结束，避免页面在未知状态下过早渲染
    }
  }
);

// 与上面的 initMessageListAtom 相反，这个 atom 负责把内存里的消息写回存储。
export const saveMessageListAtom = atom(
  null,
  (get, set) => {
    const cloudAgent = get(cloudAgentAtom);
    const chatThreadId = cloudAgent?.chatThreadId;
    const messages = get(MessageListAtom);

    saveMessagesToStorage(messages, chatThreadId);
  }
);


export const TimeoutStateAtom = atom<'active' | 'experienceTimeout'>('active');
// 倒计时时间（秒）。云手机体验通常是限时的，所以前端需要一直展示剩余时间。
export const CountdownAtom = atom<number>(30 * 60); // 30分钟
// 记录倒计时从什么时候开始，便于 UI 做进一步展示或调试。
export const StartTimeAtom = atom<number | null>(null);
// 后端返回的当前会话详情，例如 pod token、分辨率、有效期等。
export const SessionDataAtom = atom<SessionResponse | null>(null);
