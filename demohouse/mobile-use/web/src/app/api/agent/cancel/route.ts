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
import { ApiHandler, withMiddleware } from "../../_utils/middleware";
import { fetchServer } from "@/app/api/_utils/fetch";

// 这里把基础地址和具体接口路径拼成最终转发目标。
const target = url.resolve(process.env.CLOUD_AGENT_BASE_URL || "", 'api/v1/agent/cancel')

const _post: ApiHandler = async (request: Request, middlewareResult) => {
  // 取消会话时只需要告诉后端当前线程编号，
  // 后端就能定位到对应的 Agent 任务。
  const { thread_id } = await request.json();
  const response = await fetchServer(target, middlewareResult, { thread_id }, 'POST');
  return response;
}

// 公共中间件会先完成鉴权、用户信息提取等动作，再进入真正的业务处理函数。
export const POST = withMiddleware(_post);
