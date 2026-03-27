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

import * as url from "url"
import { type ApiHandler, withMiddleware } from "../../_utils/middleware";
import { fetchServer } from "../../_utils/fetch";

const target = url.resolve(process.env.CLOUD_AGENT_BASE_URL || "", 'api/v1/session/create')

// 这个 route 本身不直接创建云手机会话，
// 它只是把浏览器请求转发给 Python agent 服务，顺便复用统一中间件处理鉴权和错误。
const _post: ApiHandler = async (request: Request, middlewareResult) => {
  const { thread_id, product_id, pod_id } = await request.json();
  // withUserInfo: true 表示把中间件里解析出来的用户信息一并带给下游，
  // 这样后端可以把 accountId/userId/name 回写到响应里。
  const response = await fetchServer(
    target,
    middlewareResult,
    { thread_id, product_id, pod_id },
    'POST',
    { withUserInfo: true }
  )
  return response
};

// POST 最终导出的是“包好中间件的版本”，而不是原始 _post。
export const POST = withMiddleware(_post);
