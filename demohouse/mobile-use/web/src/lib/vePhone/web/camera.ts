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

import logger from '@/lib/vePhone/log';
import UMDLoader from '../loader';

// 这里把一些常见错误码映射成更容易读懂的提示语。
const VIDEO_CODE_MSG_MAP = {
  GET_VIDEO_TRACK_FAILED: '请授权网站获取摄像头权限', // 当申请摄像头权限被用户禁止时，code 为 'GET_VIDEO_TRACK_FAILED'
  PUBLISH_FAIL: '视频流发布失败，请重试或联系客服', // 当发布视频流失败时，code 为 'PUBLISH_FAIL' ，此时可能是用户网络问题或服务异常，可以重新 start 或告知用户有异常稍后再试
} as const;

// 音频流错误同理，这些提示更偏向帮助开发者理解问题出在哪里。
const AUDIO_CODE_MSG_MAP = {
  GET_AUDIO_TRACK_FAILED: '请授权网站获取麦克风权限', // 当申请麦克风权限被用户禁止时，code 为 'GET_AUDIO_TRACK_FAILED'
  PUBLISH_FAIL: '音频流发布失败，请重试或联系客服', // 当发布音频流失败时，code 为 'PUBLISH_FAIL' ，此时可能是用户网络问题或服务异常，可以重新 start 或告知用户有异常稍后再试
} as const;

class Camera {
  constructor(private vePhone: any) {
    // 一创建就立刻绑定事件，这样远端一旦发出开始/停止推流请求，前端就能及时响应。
    this.bindEvent();
  }

  // 这是一个工厂方法：如果外部还没有拿到 SDK 实例，这里会先帮忙加载。
  static async create(vePhoneInstance?: any) {
    // 摄像头、麦克风以及 SDK 都依赖浏览器环境，不能在服务端初始化。
    if (typeof window === 'undefined') {
      throw new Error('Camera can only be initialized in client-side environment');
    }

    if (!vePhoneInstance) {
      const loader = UMDLoader.getInstance();
      const VePhoneSDK = await loader.loadVePhoneSDK();
      vePhoneInstance = VePhoneSDK;
    }

    return new Camera(vePhoneInstance);
  }

  bindEvent() {
    // 远端请求本地开始推流时，根据需要分别开启视频或音频。
    (this.vePhone as any).on('remote-stream-start-request', async (data: any) => {
      const { isAudio, isVideo } = data as {
        isAudio: boolean;
        isVideo: boolean;
      };
      logger.info('remote-stream-start-request', data);
      if (isVideo) {
        await this.startVideoStream();
      }
      if (isAudio) {
        await this.startSendAudioStream();
      }
    });
    // 远端不再需要本地流时，及时关闭推流，避免继续占用摄像头和麦克风。
    (this.vePhone as any).on('remote-stream-stop-request', async (data: any) => {
      const { isAudio, isVideo } = data as {
        isAudio: boolean;
        isVideo: boolean;
      };
      logger.info('remote-stream-stop-request', data);
      if (isVideo) {
        await this.vePhone.stopVideoStream();
      }
      if (isAudio) {
        await this.vePhone.stopSendAudioStream();
      }
    });
  }

  async startVideoStream() {
    const { success, code, message } = await this.vePhone.startVideoStream();

    if (!success) {
      // 优先使用预定义的人类可读文案，没有命中时再退回原始 code 和 message。
      const msg =
        VIDEO_CODE_MSG_MAP[code as unknown as keyof typeof VIDEO_CODE_MSG_MAP] ||
        `本地摄像头注入失败，失败 Code：${code}，错误消息：${message}`;
      logger.info(msg);
    }
  }

  async startSendAudioStream() {
    const { success, code, message } =
      await this.vePhone.startSendAudioStream();
    if (!success) {
      // 音频失败处理逻辑与视频一致，便于开发者统一排查。
      const msg =
        AUDIO_CODE_MSG_MAP[code as unknown as keyof typeof AUDIO_CODE_MSG_MAP] ||
        `本地麦克风注入失败，失败 Code：${code}，错误消息：${message}`;
      logger.info(msg);
    }
  }
}

export { Camera };
