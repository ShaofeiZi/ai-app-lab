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

import { handleVEFaaSError } from "@/app/api/_utils/vefaas";
import { NextResponse } from "next/server";
import { APIError } from "../../../lib/exception/apiError";
import { MiddlewareResult } from "./middleware";

// 这个函数是前端 API 路由层统一使用的“转发器”。
// 它负责把当前请求携带的用户身份、实例信息和业务参数，
// 安全地转发给真正处理逻辑的 Cloud Agent 服务。
export async function fetchServer(
  target: string,
  middlewareResult: MiddlewareResult,
  body: Record<string, any>,
  method: string,
  options: { withUserInfo: boolean } = { withUserInfo: false }
): Promise<NextResponse> {
  // 这里统一构造请求头，避免每个 API 路由都重复拼装鉴权信息。
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'X-Account-Id': middlewareResult.accountId,
    'x-faas-instance-name': middlewareResult.faasInstanceName || '',
    'Authorization': `Bearer ${middlewareResult.authToken}`
  }

  const response = await fetch(target, {
    method,
    body: JSON.stringify(body),
    headers,
  });

  if (!response.ok) {
    // 当 HTTP 状态码不是成功时，先把响应体读出来，
    // 后面才能根据具体错误内容给用户更清晰的提示。
    const errorText = await response.text();
    let errorData;
    try {
      errorData = JSON.parse(errorText);
    } catch (e) {
      // 某些异常场景返回的并不是 JSON，而是一段普通字符串。
      // 这时直接保留原始文本，避免再次解析报错。
      errorData = { message: errorText };
    }

    // 先交给平台错误适配器做一次“翻译”，
    // 再把剩余错误继续抛给上层。
    await handleVEFaaSError(errorData, response.status);
    throw new Error(`请求失败: errorData.message: ${errorData.message}  errorData.status: ${response.status}`);
  }

  if (response.headers.get('Content-Type') === 'text/event-stream') {
    // 如果后端返回的是 SSE 事件流，就要原样把流透传给浏览器，
    // 这样前端才能边接收边渲染模型思考过程和工具调用结果。
    return new NextResponse(response.body, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'x-request-target': target,
        'x-agent-faas-instance-name': response.headers.get('x-faas-instance-name') || '',
      },
    });
  }

  // 普通接口返回的是完整 JSON，可以一次性解析成对象。
  const json = await response.json();
  if (json?.error && json?.error?.code !== 0) {
    // 有些业务错误会放在 JSON 里的 error 字段中，
    // 即使 HTTP 成功，也要继续按失败处理。
    throw new APIError(json.error.code, json.error.message);
  }

  if (options.withUserInfo) {
    // 某些场景希望把当前用户信息一起返回给前端，
    // 例如重置会话后顺手刷新页面展示用的用户资料。
    return NextResponse.json({
      userInfo: {
        accountId: middlewareResult.accountId,
        userId: middlewareResult.userId,
        name: middlewareResult.name,
      },
      ...json
    }, {
      status: 200, headers: {
        'Content-Type': 'application/json',
        'x-agent-faas-instance-name': response.headers.get('x-faas-instance-name') || '',
      }
    });
  }

  // 默认情况下直接返回业务 JSON，并透传实例名给前端维持会话亲和性。
  return NextResponse.json(
    options.withUserInfo ? {
      userInfo: {
        accountId: middlewareResult.accountId,
        userId: middlewareResult.userId,
        name: middlewareResult.name,
      },
      ...json
    } : json, {
    status: 200, headers: {
      'Content-Type': 'application/json',
      'x-agent-faas-instance-name': response.headers.get('x-faas-instance-name') || '',
    }
  });
}
