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

import { APIError } from "../../../lib/exception/apiError";

// 这个函数把 VE FaaS 侧的底层错误，翻译成业务层更容易理解的错误。
export async function handleVEFaaSError(errorBody: Record<string, any>, status: number) {
  // 500 不一定都表示代码 bug，有时只是底层服务告诉我们会话已经失效。
  if (status === 500) {
    // 这里专门识别几种已知的内部错误码，并转成统一的用户提示。
    if (["internal_system_error", "internal_proxy_error"].includes(errorBody?.error_code)) {
      // 这里抛 403 风格的业务错误，是为了让前端走“重新开始会话”的分支。
      throw new APIError(403, "会话不存在，请重新开始会话");
    }
  }
  // 401 说明没有合法 token，前端应该提示用户补充访问凭证。
  if (status === 401) {
    throw new APIError(401, "请提供网站访问 Token 参数");
  }
}
