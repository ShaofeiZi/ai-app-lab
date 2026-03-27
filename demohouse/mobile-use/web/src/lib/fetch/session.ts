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

// 这个文件负责管理“前端请求应该继续打到哪个 FaaS 实例”。
// 对初学者来说，可以把它理解成一种“会话粘性”机制：
// 只要当前聊天还在继续，后续请求最好落到同一个后端实例，
// 这样上下文、缓存和长连接状态更稳定。

const FAAS_INSTANCE_KEY = 'mobile_use:agent_faas_instance_name';

export class SessionAffinityManager {
  /**
   * 获取当前浏览器里保存的 FaaS 实例名。
   * 如果是在服务端环境调用，这里拿不到 sessionStorage，只能返回 null。
   */
  static getFaasInstanceName(): string | null {
    if (typeof window !== 'undefined') {
      return sessionStorage.getItem(FAAS_INSTANCE_KEY);
    }
    return null;
  }

  /**
   * 把本次请求命中的实例名保存到 sessionStorage。
   * 这样同一个标签页后续发请求时，就可以继续沿用同一个实例。
   */
  static setFaasInstanceName(instanceName: string): void {
    if (typeof window !== 'undefined') {
      sessionStorage.setItem(FAAS_INSTANCE_KEY, instanceName);
      console.log('✅ Session亲和性: 存储FaaS实例名称:', instanceName);
    }
  }

  /**
   * 清除实例绑定关系。
   * 一般在会话结束、重置或发生需要重新分配实例的场景使用。
   */
  static clearFaasInstanceName(): void {
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem(FAAS_INSTANCE_KEY);
      console.log('🗑️ Session亲和性: 清除FaaS实例名称');
    }
  }

  /**
   * 判断当前是否已经记录了活跃实例。
   */
  static hasActiveSession(): boolean {
    return this.getFaasInstanceName() !== null;
  }

  /**
   * 重置与 session 亲和性相关的本地状态。
   */
  static resetSession(): void {
    this.clearFaasInstanceName();
    // 如果未来还有其他“会话绑定”信息，也可以在这里一起清掉。
  }
}
