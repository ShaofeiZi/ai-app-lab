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

import { useState, useEffect } from 'react';
import { VePhoneClient, DOM_ID, VePhoneError } from '@/lib/vePhone';
import { cn } from '@/lib/utils/css';
import { useAtom, useAtomValue } from 'jotai';
import { Button } from '@/components/ui/button';
import { VePhoneAtom, PodIdAtom, SessionDataAtom } from '@/app/atom';

enum PhoneState {
  Init = 'init',
  Loading = 'loading',
  Ready = 'ready',
  Error = 'error',
}

const Phone = () => {
  // podId 可以理解为当前云手机实例的唯一编号。
  const [podId] = useAtom(PodIdAtom);
  const [vePhone] = useAtom(VePhoneAtom);
  const [state, setState] = useState(PhoneState.Init);
  const [error, setError] = useState<VePhoneError | null>(null);

  // 云手机的逻辑分辨率由后端会话信息决定，默认值用来兜底页面布局。
  const sessionData = useAtomValue(SessionDataAtom);
  const width = sessionData?.pod?.size?.width || 720;
  const height = sessionData?.pod?.size?.height || 1520;

  // 记录当前远端画面是竖屏还是横屏，用来调整容器比例。
  const [screenRotation, setScreenRotation] = useState('portrait');

  useEffect(() => {
    if (vePhone && podId) {
      // 当实例编号变化时，通知 SDK 切换到新的云手机。
      vePhone.changePodId(podId);
    }
  }, [podId, vePhone]);

  useEffect(() => {
    if (vePhone) {
      // 这一组事件把底层 SDK 生命周期翻译成页面状态。
      vePhone.on(VePhoneClient.VePhoneEvent.Starting, () => {
        console.log('vephone start');
        setState(PhoneState.Loading);
      });
      vePhone.on(VePhoneClient.VePhoneEvent.StartSuccess, () => {
        console.log('vephone start success');
        setState(PhoneState.Ready);
      });
      vePhone.on(VePhoneClient.VePhoneEvent.Stop, () => {
        console.log('vephone stop');
        setState(PhoneState.Init);
      });
      vePhone.on(VePhoneClient.VePhoneEvent.Destroy, () => {
        console.log('vephone destroy');
        setState(PhoneState.Init);
      });
      vePhone.on(VePhoneClient.VePhoneEvent.StartError, error => {
        console.log('vephone start error', error);
        setError(error as VePhoneError);
        setState(PhoneState.Error);
      });
    }
  }, [vePhone]);

  useEffect(() => {
    if (vePhone) {
      // onWithDisposer 返回清理函数，React 卸载组件时会自动解绑监听器。
      return vePhone.onWithDisposer('on-screen-rotation', (params: any) => {
        console.log('on-screen-rotation', params);
        if (params.appOriginDirection === 'portrait') {
          setScreenRotation('portrait');
        } else {
          setScreenRotation('landscape');
        }
      });
    }
  }, [vePhone]);

  return (
    <div
      className="gap-2 self-stretch flex flex-col justify-center items-center overflow-hidden flex-1"
      style={{
        // 这里限制一个最大高度，避免极端比例的设备把页面撑坏。
        maxHeight: width / height < 9 / 16 ? '600px' : '500px',
      }}
    >
      <div
        className={cn(
          'bg-[#d8e6fd] rounded-[16px] overflow-hidden border-[6px] border-black relative',
          // 在还没准备好时画一个简单的“手机顶部”装饰，让占位态更像设备外框。
          state !== PhoneState.Ready &&
            "before:content-[''] before:absolute before:top-0 before:left-1/2 before:-translate-x-1/2 before:w-20 before:h-6 before:bg-black before:rounded-b-xl before:z-10",
        )}
        style={
          screenRotation === 'portrait'
            ? {
                flex: 1,
              }
            : {
                width: '100%',
              }
        }
      >
        {(state === PhoneState.Init || state === PhoneState.Loading) && (
          // 初始化阶段和启动阶段都显示同一个加载遮罩。
          <div className="w-full h-full bg-black/50 flex items-center justify-center">
            <div className="w-12 h-12 rounded-full border-4 border-white border-t-transparent animate-spin" />
          </div>
        )}
        {state === PhoneState.Error && (
          // 报错时把错误码显示出来，方便开发者和用户定位问题。
          <div className="absolute top-0 left-0 z-10 w-full h-full bg-black/50 flex flex-col items-center justify-center gap-2">
            <div className="text-white">云手机初始化失败</div>
            <div className="bg-black rounded-md p-2 text-white">
              <span>错误码：{error?.errorCode}</span>
            </div>
            <Button
              variant="outline"
              onClick={() => {
                if (vePhone) {
                  // refresh 会触发 SDK 重新尝试建立连接。
                  vePhone.refresh();
                }
              }}
            >
              重试
            </Button>
          </div>
        )}

        <div
          id={DOM_ID}
          className={cn('max-h-[720px] w-full h-full relative')}
          style={{
            // 这里是真正挂载远端画面的 DOM 节点。
            // aspectRatio 根据横竖屏实时切换，避免画面被拉伸。
            aspectRatio: screenRotation === 'portrait' ? `${width} / ${height}` : `${height} / ${width}`,
          }}
        ></div>
      </div>
    </div>
  );
};

export default Phone;
