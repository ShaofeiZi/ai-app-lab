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

import { StartConfig, STSToken, VePhoneConstructorParams } from '../type';
import { VE_PHONE_CONFIG, DOM_ID } from './config';
import { EventEmitter } from 'eventemitter3';
import { VePhoneError } from './error';
import { PhoneTool } from './tool';
import { Camera } from './camera';
import logger from '@/lib/vePhone/log';
import UMDLoader from '../loader';
// import VePhoneSDK from '@volcengine/vephone'

type InstanceOptions = Partial<
  Pick<
    VePhoneConstructorParams,
    | 'userId'
    | 'isPC'
    | 'isDebug'
    | 'enableLocalKeyboard'
    | 'enableSyncClipboard'
    | 'enableLocalMouseScroll'
    | 'enableLocationService'
    | 'disableInteraction'
  >
>;

class VePhoneClient extends EventEmitter {
  private vePhone: any | null = null;
  private podId: string | undefined;
  private productId: string | undefined;
  private podSize:
    | {
      width: number;
      height: number;
    }
    | undefined;
  private stsToken: STSToken | undefined;
  private vePhoneSDK: any | null = null;
  private accountId: string | undefined;
  static VePhoneEvent = {
    Starting: 'starting',
    StartSuccess: 'start-success',
    Stop: 'stop',
    Destroy: 'destroy',
    StartError: 'start-error',
  };
  tool!: PhoneTool;
  camera!: Camera;

  constructor() {
    super();
  }

  reset() {
    // reset 用于“彻底回到未初始化状态”。
    // 它不只是断开连接，还会清掉当前 podId、token、尺寸等缓存。
    this.stop();
    this.destroy();
    this.vePhone = null;
    this.podId = undefined;
    this.productId = undefined;
    this.podSize = undefined;
    this.stsToken = undefined;
    this.accountId = undefined;
  }

  setPodInitInfo({
    podId,
    stsToken,
    podSize,
    productId,
    accountId,
  }: {
    podId: string;
    productId: string;
    podSize: {
      width: number;
      height: number;
    };
    stsToken: STSToken;
    accountId: string;
  }) {
    // 这些信息都来自后端 create_session 的返回值。
    // 前端自己并不知道该连接哪台云手机、token 是什么，所以必须先由后端灌进来。
    this.podId = podId;
    this.accountId = accountId;
    this.productId = productId;
    this.podSize = podSize;
    this.stsToken = stsToken;
  }

  async init(options?: InstanceOptions) {
    // 云手机 SDK 依赖浏览器环境，因此服务端渲染阶段不能调用这里。
    if (typeof window === 'undefined') {
      throw new Error('VePhoneClient init can only be called in client-side environment');
    }

    // SDK 是通过 UMDLoader 动态加载的，而不是静态 import。
    // 这样可以避免服务端构建阶段直接触发浏览器专属代码。
    if (!this.vePhoneSDK) {
      try {
        const loader = UMDLoader.getInstance();
        this.vePhoneSDK = await loader.loadVePhoneSDK();
        logger.info('VePhone SDK loaded successfully');
      } catch (error) {
        console.error('Failed to load vePhoneSDK:', error);
        throw new Error('Failed to load vePhoneSDK');
      }
    }

    // this.vePhoneSDK = VePhoneSDK;

    // 这里是创建 vePhone SDK 实例时的默认选项。
    // 比如默认关闭本地键盘、开启定位服务，以及按 PC 模式运行。
    const params = Object.assign(
      {
        isPC: true,
        isDebug: false,
        enableLocalKeyboard: false, // 开启云端键盘
        enableLocationService: true, // 开启定位服务
        // 禁用交互， 禁用后， 无法进行交互
        // disableInteraction: true, // 禁用交互， 禁用后， 无法进行交互
        // enableSyncClipboard: false, // 禁用同步剪贴板
        // enableLocalMouseScroll: false, // 禁用本地鼠标滚动
      },
      options,
    );
    const sdkInitConfig = {
      ...VE_PHONE_CONFIG,
      domId: DOM_ID,
      accountId: this.accountId,
      ...params,
    };

    // 真正的 SDK 实例在这里创建。
    // 后面的 tool / camera 都是基于这个底层实例做的进一步封装。
    this.vePhone = new this.vePhoneSDK(sdkInitConfig);

    // this.vePhone._localKeyboardHandler.destroy();
    // this.vePhone._keyboardDisableHandler.setEnabled(false);
    this.tool = new PhoneTool(this.vePhone);
    this.camera = new Camera(this.vePhone);
    logger.info('vePhoneSDK version', this.vePhone.getVersion());
    logger.info('sdkInitConfig', sdkInitConfig);
    this.bindEvent();
  }

  bindEvent() {
    if (!this.vePhone) {
      return;
    }
    // SDK 内部会抛出一些底层事件，这里把和页面真正相关的部分重新转发或记录。
    (this.vePhone as any).on('message-received', (params: unknown) => {
      const { msg } = params as { msg: { command: number } };
      const { command } = msg;
      if (command === 8) {
        logger.info('timeout exit');
      }
    });

    (this.vePhone as any).on('on-screen-rotation', (params: unknown) => {
      this.emit('on-screen-rotation', params);
    });

    window.addEventListener('beforeunload', () => {
      // 用户关闭页面前，如果连接还活着，尽量主动 stop + destroy，
      // 避免浏览器直接退出时把远端会话留在半开状态。
      if (!this.vePhone?.getConnectionState) {
        return;
      }
      const connectionState = this.vePhone?.getConnectionState?.();
      if (connectionState === 'CONNECTED') {
        this.vePhone?.stop();
        this.vePhone.destroy();
      }
    });

    window.addEventListener('error', event => {
      const { errorCode, errorMessage } = event as unknown as {
        errorCode: number;
        errorMessage: string;
      };
      logger.info('error', event, errorCode, errorMessage);
    });
  }

  async start(
    config?: Partial<Pick<StartConfig, 'rotation' | 'isScreenLock' | 'mute' | 'audioAutoPlay'>> &
      Pick<StartConfig, 'podId'>,
    instanceOptions?: InstanceOptions,
  ) {
    // start 是真正把“已经初始化好的 SDK”连接到某一台具体云手机实例的步骤。
    console.log('podid', config);
    if (config?.podId) {
      this.podId = config?.podId;
    }
    if (!this.podId) {
      throw Error('pod id is required');
    }

    if (!this.vePhone) {
      await this.init({ userId: `mobileuse-${this.podId}`, ...instanceOptions });
    }

    // 这些 sessionConfig 都来自后端分配 pod 时返回的状态。
    // 前端只负责原样喂给 SDK，不自己生成鉴权信息。
    const sessionConfig = {
      productId: this.productId,
      remoteWindowSize: {
        width: this.podSize?.width,
        height: this.podSize?.height,
      },
      token: {
        AccessKeyID: this.stsToken?.AccessKeyID,
        SecretAccessKey: this.stsToken?.SecretAccessKey,
        SessionToken: this.stsToken?.SessionToken,
        CurrentTime: this.stsToken?.CurrentTime,
        ExpiredTime: this.stsToken?.ExpiredTime,
      },
    };

    // 这里是连接时的运行参数，例如是否静音、是否自动播放声音、是否锁屏。
    const phoneConfig = Object.assign(
      {
        // rotation: 'auto',
        isScreenLock: false,
        mute: false,
        audioAutoPlay: true,
      },
      config,
    );

    const params = {
      ...sessionConfig,
      ...phoneConfig,
    };
    // 在真正 start 前先发一个 starting 事件，
    // 这样外层 UI 可以先进入加载态。
    this.emit(VePhoneClient.VePhoneEvent.Starting);
    try {
      if (!this.vePhone) {
        return;
      }
      const result = await this.vePhone.start(params);
      this.emit(VePhoneClient.VePhoneEvent.StartSuccess);
      logger.info('start result', result);
      // 这里额外配置 SDK 侧的回收与空闲时间。
      // 它们决定了长时间无操作时，客户端和 pod 如何自动释放资源。
      this.vePhone.setAutoRecycleTime(120 * 60);
      this.vePhone.setIdleTime(60);
      return result;
    } catch (error) {
      logger.error('start error', error);
      this.emit(VePhoneClient.VePhoneEvent.StartError, new VePhoneError(error as VePhoneError));
    }
  }

  async changePodId(podId: string) {
    // 切换 pod 的核心逻辑是：如果当前已经连着旧 pod，就先停掉，再启动新 pod。
    if (this.podId) {
      const connectionState = this.vePhone?.getConnectionState?.();
      if (connectionState === 'CONNECTED') {
        await this.stop();
      }
    }
    this.podId = podId;
    const result = await this.start({ podId });
    logger.info('changePodId result', result);
    return result;
  }

  async refresh() {
    // refresh 的场景通常是“还是这台 pod，但我想重新建立一次连接”。
    if (!this.podId) {
      return;
    }
    const connectionState = this.vePhone?.getConnectionState?.();
    if (connectionState === 'CONNECTED') {
      await this.stop();
    }
    const result = await this.start({ podId: this.podId });
    logger.info('refresh result', result);
    return result;
  }

  async stop() {
    try {
      if (!this.vePhone) {
        return;
      }
      // stop 是“停止当前连接”，但并不清空本地缓存字段。
      const result = await this.vePhone.stop();
      logger.info('stop result', result);
      this.emit(VePhoneClient.VePhoneEvent.Stop);
    } catch (error) {
      logger.error('stop error', error);
    }
  }

  async destroy() {
    try {
      if (!this.vePhone) {
        return;
      }
      // destroy 比 stop 更彻底，通常用于页面退出或 reset 阶段。
      const result = await this.vePhone.destroy();
      logger.info('destroy result', result);
      this.emit(VePhoneClient.VePhoneEvent.Destroy);
    } catch (error) {
      logger.error('destroy error', error);
    }
  }

  onWithDisposer(event: string, callback: (params: unknown) => void): void | (() => void) {
    // 这里返回一个 disposer，方便 React 组件在 useEffect 清理阶段注销监听。
    this.on(event, callback);

    return () => {
      this.off(event, callback);
    };
  }

  onceWithDisposer(event: string, callback: (params: unknown) => void): void | (() => void) {
    // onceWithDisposer 适合“我只关心第一次成功/失败事件”的场景。
    this.once(event, callback);

    return () => {
      this.off(event, callback);
    };
  }
}

export { VePhoneClient };
