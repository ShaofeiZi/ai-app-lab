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

export interface STSToken {
  // 这组字段是云服务临时凭证，作用类似“限时钥匙”。
  AccessKeyID: string;
  SecretAccessKey: string;
  SessionToken: string;
  CurrentTime: string;
  ExpiredTime: string;
}

export interface StartConfig {
  productId: string;
  podId: string;
  token: STSToken;
  rotation?: 'portrait';
  // 是否锁住屏幕方向，常见于移动设备场景。
  isScreenLock?: boolean; // !isPc
  mute?: boolean;
  audioAutoPlay?: boolean;
  remoteWindowSize?: {
    // 这里是固定分辨率约定，便于 Agent 侧统一理解坐标系统。
    width: 1080;
    height: 1920;
  };
}

export interface VePhoneConstructorParams {
  userId: string;
  accountId: string;
  phoneHost?: string;
  isPC: boolean;
  domId: string;
  isDebug: boolean;
  enableLocalKeyboard: boolean;
  enableSyncClipboard: boolean;
  enableLocalMouseScroll: boolean;
  enableLocationService?: boolean;
  disableInteraction?: boolean;
}

export interface VePhoneStatic {
  // SDK 本身暴露的是一个构造函数。
  new(params: VePhoneConstructorParams): VePhone;
  isRtcSupported: () => boolean;
}

export const enum KeyCode {
  Home = 3,
  Back = 4,
  Menu = 82,
  APP_SWITCH = 187,
}

export const enum ButtonAction {
  DOWN = 0,
  UP = 1,
  MOVE = 2,
}

export const enum TouchAction {
  TOUCH_START = 0,
  TOUCH_END = 1,
  TOUCH_MOVE = 2,
}

export const enum PCKeyAction {
  PC_TOUCH_UP = 0,
  PC_TOUCH_DOWN = 1,
  PC_TOUCH_MOVE = 2,
  WHEEL = 8,
}

export const enum MouseButton {
  LEFT = 0,
  CENTER = 1,
  RIGHT = 2,
}

export interface VePhone {
  // on 用来监听 SDK 运行过程中抛出的各种事件，比如启动成功、失败、横竖屏切换等。
  on: (
    event: string,
    callback: (data: unknown) => void | Promise<void>,
  ) => void;
  setAutoRecycleTime: (time: number) => void;
  setIdleTime: (time: number) => void;
  start: (config: StartConfig) => void;
  stop: () => void;
  destroy: () => void;
  getVersion: () => string;
  getConnectionState: () => string;
  screenShot: (isSavedOnPod: boolean) => Promise<{
    /**
     * 截图结果:
     * 0 表示成功；
     * 负数一般表示失败，并附带不同失败原因。
     */
    result: number;
    /** 保存在云手机实例内部的截图路径。 */
    savePath: string;
    /** 错误码，成功时通常为 0。 */
    errorCode?: number;
    /** 错误信息，成功时通常为空字符串。 */
    message: string;
    /** 截图成功时提供下载链接，链接通常有时效限制。 */
    downloadUrl?: string;
  }>;
  launchApp: (appId: string) => Promise<{ result: number; message: string }>;
  sendTouchMessage: (params: {
    action: TouchAction;
    pointerId: number;
    x: number;
    y: number;
  }) => Promise<void>;
  getRemoteBackgroundAppList: () => Promise<string[]>;
  sendClipBoardMessage: (text: string) => Promise<void>;
  sendKeycodeMessage: (params: {
    keycode?: number;
    action?: ButtonAction;
  }) => Promise<void>;
  sendMouseMessage: (mouseMessage: {
    button?: MouseButton;
    action: PCKeyAction;
    wheel?: number;
    x: number;
    y: number;
  }) => void;
  startVideoStream: () => Promise<{
    success: boolean;
    code: number;
    message: string;
  }>;
  startSendAudioStream: () => Promise<{
    success: boolean;
    code: number;
    message: string;
  }>;
  stopVideoStream: () => Promise<{
    success: boolean;
    code: number;
    message: string;
  }>;
  stopSendAudioStream: () => Promise<{
    success: boolean;
    code: number;
    message: string;
  }>;
}
