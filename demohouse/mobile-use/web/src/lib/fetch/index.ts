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

import { toast } from "sonner";
import { SessionAffinityManager } from "./session";
import { toastRedirect } from "./redirect";
import { buildUrlWithToken } from "../utils";

const beforeFetchSessionHeaders = () => {
  // 这里维护的是“实例亲和性”。
  // 如果后端是多实例部署，后续请求尽量打到同一实例，可以减少会话不一致问题。
  const faasInstanceName = SessionAffinityManager.getFaasInstanceName();
  if (faasInstanceName) {
    return {
      'x-agent-faas-instance-name': faasInstanceName,
    }
  }
  return null;
}

const afterFetchSession = (response: Response) => {
  const faasInstanceName = SessionAffinityManager.getFaasInstanceName();
  const responseFaasInstanceName = response.headers.get('x-agent-faas-instance-name');
  if (responseFaasInstanceName && responseFaasInstanceName !== faasInstanceName) {
    // 一旦后端回了新的实例名，就用它覆盖本地记录，
    // 后续请求会优先继续命中这个实例。
    SessionAffinityManager.setFaasInstanceName(responseFaasInstanceName);
    console.log('存储新的FaaS实例名称:', responseFaasInstanceName);
  }
}

const handleErrorResponse = async (response: Response) => {
  const data = await response.json()
  if (data?.error && data?.error?.code !== 0) {
    if (response.status === 401) {
      // 401 通常意味着 token 缺失或失效，统一走重定向提示。
      toastRedirect()
      return
    }
    if (response.status === 200 && data?.error?.code === 403) {
      // 这里的 403 是业务语义上的“会话不存在”，不是 HTTP 层拒绝访问。
      toast.warning(data?.error?.message || "会话不存在，请重新开始会话")
      sessionStorage.clear()
      setTimeout(() => {
        // 保留 token 参数进行页面跳转
        window.location.replace(buildUrlWithToken('/'));
      }, 1500)
      return;
    }
    toast.warning(data.error.message)
    return;
  }
  return data;
}

const fetchAPI = async (url: string, options: RequestInit) => {
  try {

    const headers = beforeFetchSessionHeaders();

    // 当前 demo 的鉴权 token 放在页面 URL 上，所以这里要把它继续带给 API route。
    const urlParams = new URLSearchParams(window.location.search);
    const urlToken = urlParams.get('token');
    const apiUrl = urlToken ? `${url}?token=${encodeURIComponent(urlToken)}` : url;

    const response = await fetch(apiUrl, {
      ...options,
      headers: {
        ...(headers || {}),
        ...options.headers,
      },
    });
    // 响应回来后再顺手刷新一次实例亲和信息。
    afterFetchSession(response);
    const data = await handleErrorResponse(response)
    return data
  } catch (error) {
    if (error instanceof Error) {
      toast.warning(error.message)
    } else {
      toast.warning("未知错误")
    }
    return;
  }

}

const fetchSSE = async (url: string, options: RequestInit) => {
  try {
    const headers = beforeFetchSessionHeaders();
    // SSE 请求同样要带上 token，否则浏览器侧代理 route 无法通过鉴权中间件。
    const urlParams = new URLSearchParams(window.location.search);
    const urlToken = urlParams.get('token');
    const apiUrl = urlToken ? `${url}?token=${encodeURIComponent(urlToken)}` : url;
    const response = await fetch(apiUrl, {
      ...options,
      headers: {
        ...(headers || {}),
        ...options.headers,
      },
      signal: options.signal,
    });
    afterFetchSession(response);
    const contentType = response.headers.get('Content-Type') || '';
    if (contentType.includes('text/event-stream')) {
      // 只有真正拿到事件流时，才把 response.body 原样返回给上层逐段读取。
      if (!response.ok || !response.body) {
        const { error } = (await response.json().catch(() => ({ error: { message: '未知错误' } }))) || { error: { message: '未知错误' } };
        toast.warning(error.message);
        throw new Error(`HTTP错误: ${response.status}`);
      }
      return response.body
    }
    const data = await handleErrorResponse(response)
    if (!response.ok) {
      throw new Error(`HTTP错误: ${response.status}`);
    }
    return data
  } catch (error) {
    console.log(error)
    // 用户主动取消任务时会触发 AbortError，这种情况不应该再弹“网络错误”提示。
    if (error instanceof DOMException && error.name === 'AbortError') {
      console.log('请求已被中止');
      return;
    }
    if (error instanceof Error) {
      toast.warning(error.message)
    } else {
      toast.warning("未知错误")
    }
    return;
  }
}

export { fetchAPI, fetchSSE };
