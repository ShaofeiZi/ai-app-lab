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

import { ApiHandler, withMiddleware } from "../../_utils/middleware";
import * as url from "url";
import { fetchServer } from "../../_utils/fetch";

const target = url.resolve(process.env.CLOUD_AGENT_BASE_URL || "", 'api/v1/agent/stream')

const _post: ApiHandler = async (request: Request, middlewareResult) => {
  const { message, thread_id, pod_id } = await request.json();
  // 这里固定加上 is_stream: true，告诉下游后端走流式响应模式，
  // 前端才能实时看到 think / tool 事件。
  // `pod_id` 虽然当前新版后端主要从 session 中恢复设备信息，
  // 但这里仍保持透传，兼容现有调用协议。
  const response = await fetchServer(target, middlewareResult, { message, thread_id, pod_id, is_stream: true }, 'POST');
  return response;
};

export const POST = withMiddleware(_post);
