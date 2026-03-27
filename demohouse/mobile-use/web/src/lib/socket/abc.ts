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

export interface MessageMeta {
  finish_reason?: string;
  model?: string;
  prompt_tokens?: number;
  total_tokens?: number;
}

export interface SSEContentMessageData {
  id: string;
  task_id: string;
  role: string;
  content: string;
  response_meta?: MessageMeta;
}

export interface SSEThinkMessageData extends SSEContentMessageData {
  type: "think";
}

export interface UserInterruptMessageData extends SSEContentMessageData {
  type: "user_interrupt";
  interrupt_type: "text";
}

export interface SummaryMessageData extends SSEContentMessageData {
  type: "summary";
}

export interface SSEToolCallMessageData {
  id: string;
  task_id: string;
  tool_id: string;
  type: "tool";
  status: "start" | "stop" | "success";
  tool_type: "tool_input" | "tool_output";
  tool_name: string;
  tool_input?: string;
  tool_output?: string;
}

export type SSEMessage =
  | SSEThinkMessageData
  | UserInterruptMessageData
  | SummaryMessageData
  | SSEToolCallMessageData;

/**
 * 同构的流式消息抽象层。
 * 目标不是强行实现浏览器原生 WebSocket 语义，而是为“任意可推送 SSE-like 消息的后端”
 * 提供统一接口，这样 WebClient、Electron 或其他宿主环境都可以复用同一套消费逻辑。
 */
abstract class SSELike {
  // 建立底层连接，例如浏览器中的 EventSource 或 Electron 中的桥接实现。
  abstract connect(): Promise<void>;

  // 注册消息监听器，要求外层只关心结构化后的业务消息，而不是原始传输细节。
  abstract onMessage(handler: (json: SSEMessage) => void): void;

  // 关闭连接并释放底层资源，避免页面切换或会话重置后出现幽灵事件流。
  abstract close(): void;
}

export enum EVENT_KEY {
  MESSAGE = 'message',
  DONE = 'done',
}

export interface MapKey {
  [EVENT_KEY.MESSAGE]: (json: SSEMessage) => void;
  [EVENT_KEY.DONE]: () => void;
}

export default SSELike;
