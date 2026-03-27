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

import { safeJSONParse } from '@/lib/utils';
import { EVENT_KEY, MapKey, SSEMessage } from '@/lib/socket/abc';
import { fetchAPI, fetchSSE } from './fetch';
import { getDefaultStore } from 'jotai';
import { cloudAgentAtom, MessageListAtom, saveMessageListAtom } from '@/app/atom';

const MOBILE_USE_THREAD_ID_KEY = 'mobile_use:thread_id'
const MOBILE_USE_CHAT_THREAD_ID_KEY = 'mobile_use:chat_thread_id'
export const MOBILE_USE_PRODUCT_ID_KEY = 'mobile_use:product_id'
export const MOBILE_USE_POD_ID_KEY = 'mobile_use:pod_id'

class CloudAgent {
  private _ready: boolean;
  private handler: Map<keyof MapKey, MapKey[keyof MapKey]> = new Map();
  private _threadId: string | undefined;
  private _chatThreadId: string | undefined;
  private _abortController?: AbortController;
  private _podId?: string;
  private _productId?: string;

  constructor() {
    // CloudAgent 是浏览器里“和后端 Agent 打交道”的总入口。
    // 它会记住 threadId、chatThreadId、podId、productId，并负责发起 SSE 请求。
    this._ready = false;
    this._threadId = sessionStorage.getItem(MOBILE_USE_THREAD_ID_KEY) || undefined;
    this._chatThreadId = sessionStorage.getItem(MOBILE_USE_CHAT_THREAD_ID_KEY) || undefined
    this._podId = localStorage.getItem(MOBILE_USE_POD_ID_KEY) || undefined;
    this._productId = localStorage.getItem(MOBILE_USE_PRODUCT_ID_KEY) || undefined;
    this.handler.set(EVENT_KEY.MESSAGE, () => { });
    this.handler.set(EVENT_KEY.DONE, () => { });
  }

  get ready() {
    return this._ready;
  }

  get threadId() {
    return this._threadId;
  }

  get chatThreadId() {
    return this._chatThreadId
  }

  get podId() {
    return this._podId;
  }

  get productId() {
    return this._productId;
  }

  setProductPodId(productId: string, podId: string) {
    // productId / podId 既存在内存里，也持久化到 localStorage，
    // 这样刷新页面后还能恢复最近一次操作的云手机目标。
    this._productId = productId;
    this._podId = podId;
    localStorage.setItem(MOBILE_USE_PRODUCT_ID_KEY, productId);
    localStorage.setItem(MOBILE_USE_POD_ID_KEY, podId);
  }

  setThreadId(threadId: string) {
    if (this._threadId === threadId) {
      return;
    }
    this._threadId = threadId;
    sessionStorage.setItem(MOBILE_USE_THREAD_ID_KEY, threadId);
  }

  setChatThreadId(chatThreadId: string) {
    if (this._chatThreadId === chatThreadId) {
      return;
    }
    this._chatThreadId = chatThreadId
    sessionStorage.setItem(MOBILE_USE_CHAT_THREAD_ID_KEY, chatThreadId)
  }

  closeConnection() {
    // AbortController 是浏览器里取消 fetch / SSE 的标准办法。
    if (this._abortController) {
      this._abortController.abort();
      this._abortController = undefined;
    }
  }

  async call(message: string) {
    if (!this._podId) {
      throw new Error('podId is required');
    }

    // 新任务开始前先关掉上一条还没彻底结束的连接，避免两个事件流混在一起。
    this.closeConnection();

    this._abortController = new AbortController();
    try {
      await this._call(message);
    } catch (error) {
      // 如果是中止错误，则不需要抛出
      if (error instanceof DOMException && error.name === 'AbortError') {
        console.log('SSE连接已主动关闭');
        return;
      }
      throw error;
    } finally {
      this._abortController = undefined;
    }
  }

  private async _call(message: string) {
    // 这里请求的是浏览器侧的 `/api/agent/stream`，
    // 实际上它还会再转发到 Python Agent 服务。
    const readable = await fetchSSE(`/api/agent/stream`, {
      method: 'POST',
      body: JSON.stringify({
        thread_id: this._threadId,
        message,
        pod_id: this._podId,
      }),
      signal: this._abortController?.signal,
    });

    // 当后端返回的是普通错误 JSON、空响应，或 fetchSSE 已经做过错误提示时，
    // 这里不再继续把它当作 ReadableStream 使用，否则会触发 getReader 运行时异常。
    if (!readable || typeof readable.getReader !== 'function') {
      throw new Error('Agent 流式响应未建立成功');
    }

    const reader = readable.getReader();
    const decoder = new TextDecoder();

    let buffer = '';

    // SSE 的底层是不断到达的文本块。
    // 这里自己做一层按 `\n\n` 分帧，再把 `data: ...` 解析成结构化事件。
    try {
      // eslint-disable-next-line no-constant-condition
      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          (this.handler.get(EVENT_KEY.DONE) as MapKey[typeof EVENT_KEY.DONE])?.();
          break;
        }

        // fetch 返回的是 Uint8Array，需要先解码成字符串再做切分。
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim() === '') {
            continue;
          }

          try {
            if (typeof line === 'string' && line.startsWith('data: ')) {
              this._onMessage(line as `data: ${string}`);
            }
          } catch (error) {
            console.error('解析消息失败:', error, line);
          }
        }
      }
    } catch (error) {
      // 处理SSE流读取过程中的错误
      console.log('SSE连接断开:', error);
      // 触发DONE事件，通知前端SSE连接已断开
      throw error;
    } finally {
      (this.handler.get(EVENT_KEY.DONE) as MapKey[typeof EVENT_KEY.DONE])?.();
    }
  }

  async cancel() {
    if (!this._threadId) {
      throw new Error('threadId is required');
    }
    // 本地先中断连接，再通知后端停止执行。
    this.closeConnection()
    await fetchAPI(`/api/agent/cancel`, {
      method: 'POST',
      body: JSON.stringify({
        thread_id: this._threadId,
      }),
    });
  }

  private _onMessage(data: `data: ${string}`) {
    // "[DONE]" 是约定好的流结束标记，不再走 JSON 解析分支。
    const jsonStr = data.split('data: ')[1];
    if (jsonStr === '[DONE]') {
      (this.handler.get(EVENT_KEY.DONE) as MapKey[typeof EVENT_KEY.DONE])?.();
      return;
    }
    const json: SSEMessage = safeJSONParse(jsonStr);
    if (!json) {
      return;
    }
    this.handler.get(EVENT_KEY.MESSAGE)?.(json);
  }

  onMessageDone(handler: () => void) {
    this.handler.set(EVENT_KEY.DONE, handler);
  }

  onMessage(handler: (json: SSEMessage) => void) {
    this.handler.set(EVENT_KEY.MESSAGE, handler);
  }

  offMessageDone() {
    this.handler.set(EVENT_KEY.DONE, () => { });
  }

  offMessage() {
    this.handler.set(EVENT_KEY.MESSAGE, () => { });
  }
}

export const changeAgentChatThreadId = (chatThreadId: string) => {
  const store = getDefaultStore()
  const cloudAgent = store.get(cloudAgentAtom)
  if (cloudAgent) {
    if (cloudAgent.chatThreadId === chatThreadId) { return }
    // chatThreadId 变化代表“换了一段新的对话上下文”，
    // 原来的消息列表就不应该继续沿用。
    store.set(MessageListAtom, [])
    cloudAgent.setChatThreadId(chatThreadId)
  }
}

export default CloudAgent;
