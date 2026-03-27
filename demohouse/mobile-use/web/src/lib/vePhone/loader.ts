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

'use client';

import { VePhoneStatic } from "./type";

declare global {
  interface Window {
    // SDK 脚本加载完成后，会把构造函数挂到全局 window 上。
    vePhoneSDK: VePhoneStatic;
  }
}

class UMDLoader {
  private static instance: UMDLoader;
  // loadPromise 用来记住“当前是否已经有人在加载脚本”。
  // 这样多个地方同时请求 SDK 时，可以复用同一个 Promise，避免重复插入 script 标签。
  private loadPromise: Promise<VePhoneStatic> | null = null;
  private isLoaded = false;

  static getInstance(): UMDLoader {
    if (!UMDLoader.instance) {
      UMDLoader.instance = new UMDLoader();
    }
    return UMDLoader.instance;
  }

  async loadVePhoneSDK(): Promise<VePhoneStatic> {
    // 如果 SDK 已经就绪，直接返回全局对象。
    if (this.isLoaded && window.vePhoneSDK) {
      return window.vePhoneSDK;
    }

    // 如果别的地方已经在加载，就直接等待同一个 Promise。
    if (this.loadPromise) {
      return this.loadPromise;
    }

    // 这个 SDK 依赖浏览器 DOM 和 window，对服务端环境无效。
    if (typeof window === 'undefined') {
      throw new Error('VePhone SDK can only be loaded in client environment');
    }

    this.loadPromise = new Promise((resolve, reject) => {
      // 先看看页面里是不是已经有对应 script 标签了。
      const existingScript = document.querySelector('script[src="/vephone-sdk.js"]');
      if (existingScript && window.vePhoneSDK) {
        this.isLoaded = true;
        resolve(window.vePhoneSDK);
        return;
      }

      const script = document.createElement('script');
      script.src = '/vephone-sdk.js';
      script.async = true;

      script.onload = () => {
        // 脚本下载成功后，还要确认它确实把 SDK 挂到了 window 上。
        if (window.vePhoneSDK) {
          this.isLoaded = true;
          console.log('VePhone SDK loaded successfully');
          resolve(window.vePhoneSDK);
        } else {
          reject(new Error('VePhone SDK not found on window object'));
        }
      };

      script.onerror = () => {
        reject(new Error('Failed to load VePhone SDK'));
      };

      // 只在页面里还没有这个脚本时才真正插入，避免重复下载。
      if (!existingScript) {
        document.head.appendChild(script);
      }
    });

    return this.loadPromise;
  }

  isSDKLoaded(): boolean {
    // 双重判断更稳妥：既要标记为已加载，也要真的能从 window 读到 SDK。
    return this.isLoaded && !!window.vePhoneSDK;
  }
}

export default UMDLoader;
