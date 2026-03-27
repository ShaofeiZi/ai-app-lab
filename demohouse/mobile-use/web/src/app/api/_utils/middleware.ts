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

import { NextRequest, NextResponse } from "next/server";
import { APIError } from '../../../lib/exception/apiError';

export type ApiHandler = (req: NextRequest, middlewareResult: MiddlewareResult) => Promise<NextResponse> | NextResponse;

export interface MiddlewareResult {
  accountId: string;
  userId: string;
  name: string;
  faasInstanceName: string | null;
  authToken: string | null;
  token: string | null;
}

// 统一包装 API handler，把认证、实例亲和和错误格式收敛到一处，
// 避免每个 route 都重复维护相同的样板代码。
export function withMiddleware(handler: ApiHandler) {
  return async function (req: NextRequest) {
    try {
      // 先跑认证逻辑；失败时直接返回标准 JSON 错误体，不再进入具体业务 handler。
      const authResult = await checkAuth(req);
      if ('error' in authResult && authResult.isError) {
        return NextResponse.json({ error: authResult.error }, { status: 401 });
      }
      if (!('accountId' in authResult)) {
        return NextResponse.json({ error: authResult.error }, { status: 401 });
      }
      const response = await handler(req, {
        ...authResult,
        authToken: authResult.token,
        // 将上游网关注入的实例名透传给下游，便于请求继续命中同一 agent 实例。
        faasInstanceName: req.headers.get('x-agent-faas-instance-name'),
      });
      return response
    } catch (error) {
      // 这里统一兜住所有 route 内抛出的异常，保证前端总能收到结构稳定的响应。
      console.error("Response Error:", error)
      if (error && (error instanceof APIError)) {
        console.error("API Error:", error);
        return NextResponse.json(
          {
            error: {
              code: (error as APIError).code,
              message: (error as Error).message,
            },
          },
          { status: 200 }
        );
      }
      console.error("Server Error:", error)
      return NextResponse.json(
        {
          error: {
            code: "InternalError",
            message: "网络连接异常，请刷新后重试",
          },
        },
        { status: 500 }
      );
    }
  };
}

// 当前仓库中的认证逻辑是一个最小示例：
// 只要求 query string 中带 token，并把它回填为 authToken 供后续调用使用。
// 如果后续接入真实 IAM，这里会是替换认证实现的主要入口。
async function checkAuth(req: NextRequest) {
  try {
    const token = req.nextUrl.searchParams.get('token');
    if (!token) {
      return getIAMError("InvalidCredentials", "请提供网站访问 API KEY");
    }
    const accountId = '1234567890';
    return {
      accountId,
      name: 'User',
      userId: accountId,
      token
    };
  } catch (error) {
    console.error("认证错误:", error);
    return getIAMError("InternalError", "认证失败");
  }
}


function getIAMError(code: string | number, message: string) {
  // 统一 IAM 风格错误结构，确保鉴权失败与其他调用方的错误处理约定兼容。
  console.error("IAM错误:", code, message);
  return {
    error: {
      code: code,
      message: message,
    },
    isError: true
  }
}
