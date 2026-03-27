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

import { useAtom, useAtomValue, useSetAtom } from "jotai";
import { useRef } from "react";
import { useCloudAgent } from "./useCloudAgent";
import { TimeoutStateAtom, CountdownAtom, VePhoneAtom, SessionDataAtom, StartTimeAtom } from "@/app/atom";



const useTimeoutPhone = () => {
  const [vePhone] = useAtom(VePhoneAtom);
  const sessionTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const countdownTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const setTimeoutState = useSetAtom(TimeoutStateAtom);
  const setSessionData = useSetAtom(SessionDataAtom);
  const setStartTime = useSetAtom(StartTimeAtom);
  const setCountdownTime = useSetAtom(CountdownAtom);
  const cloudAgent = useCloudAgent()

  const clear = () => {
    // clear 同时负责清掉“每秒递减倒计时”的 interval 和“整段体验结束”的 timeout。
    if (countdownTimeoutRef.current) {
      clearInterval(countdownTimeoutRef.current)
      countdownTimeoutRef.current = null
    }
    if (sessionTimeoutRef.current) {
      clearTimeout(sessionTimeoutRef.current);
      sessionTimeoutRef.current = null
    }
  }

  const initCountdown = (countdownTime: number) => {
    clear()
    console.log('initCountdown', countdownTime)
    // 一旦后端告诉我们剩余体验时长，就重新初始化整套倒计时状态。
    setStartTime(performance.now());
    setCountdownTime(countdownTime);
    countdownTimeoutRef.current = setInterval(() => {
      console.log('countdownTimeoutRef')
      setCountdownTime(prev => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    sessionTimeoutRef.current = setTimeout(handleEnd, countdownTime * 1000);
  }

  const handleEnd = async () => {
    // 倒计时结束时，先停掉仍在执行的 Agent 请求。
    if (cloudAgent?.cancel) {
      await cloudAgent?.cancel?.()
    }
    // 然后重置云手机画面客户端，避免过期实例还残留在 UI 中。
    vePhone?.reset();
    // 最后切换 UI 到“体验已结束”状态，并清掉本地会话数据。
    setTimeoutState('experienceTimeout');
    setSessionData(null);
    // 清除开始时间
    setStartTime(null);
  }

  return initCountdown
}


export const useTimeoutState = () => {
  // 这个 hook 只是把几个分散的 atom 组合成一份更方便页面消费的只读状态。
  const countdownTime = useAtomValue(CountdownAtom);
  const timeoutState = useAtomValue(TimeoutStateAtom);
  const startTime = useAtomValue(StartTimeAtom);
  return {
    countdownTime,
    timeoutState,
    startTime
  }
}

export default useTimeoutPhone;
