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

import { KeyCode, ButtonAction, TouchAction } from '../type';
import { catchLog } from './decorator';

export class PhoneTool {
  // pointerId 可以理解成“当前这根手指”的编号。
  cursorId = 0;
  vePhone: any;

  constructor(vePhoneInstance?: any) {
    // vePhone 是真正和云手机通信的底层 SDK 实例。
    this.vePhone = vePhoneInstance;
  }


  // 模拟按下再抬起 Home 键。
  @catchLog()
  async home() {
    await this.vePhone.sendKeycodeMessage({
      keycode: KeyCode.Home,
      action: ButtonAction.DOWN,
    });
    await this.vePhone.sendKeycodeMessage({
      keycode: KeyCode.Home,
      action: ButtonAction.UP,
    });
  }

  // 模拟系统返回键。
  @catchLog()
  async back() {
    await this.vePhone.sendKeycodeMessage({
      keycode: KeyCode.Back,
      action: ButtonAction.DOWN,
    });
    await this.vePhone.sendKeycodeMessage({
      keycode: KeyCode.Back,
      action: ButtonAction.UP,
    });
  }

  // 模拟任务切换键，用于打开最近应用列表。
  @catchLog()
  async appSwitch() {
    await this.vePhone.sendKeycodeMessage({
      keycode: KeyCode.APP_SWITCH,
      action: ButtonAction.DOWN,
    });
    await this.vePhone.sendKeycodeMessage({
      keycode: KeyCode.APP_SWITCH,
      action: ButtonAction.UP,
    });
  }

  // 点击本质上是一次“按下 + 抬起”的触摸序列。
  @catchLog()
  async touch(x: number, y: number) {
    await this.vePhone.sendTouchMessage({
      action: TouchAction.TOUCH_START,
      pointerId: this.cursorId,
      x,
      y,
    });
    await this.vePhone.sendTouchMessage({
      action: TouchAction.TOUCH_END,
      pointerId: this.cursorId,
      x,
      y,
    });
  }

  // 请求云手机截图，并把结果返回给上层。
  @catchLog()
  async screenShot() {
    const result = await this.vePhone.screenShot(false);
    return result;
  }

  // scroll 只是 swipe 的一个特例：x 固定在中间，只改纵向坐标。
  @catchLog()
  async scroll(y1: number, y2: number) {
    await this.swipe(0.5, y1, 0.5, y2);
  }

  // swipe 会模拟手指从起点滑到终点。
  @catchLog()
  async swipe(x1: number, y1: number, x2: number, y2: number) {
    await this.vePhone.sendTouchMessage({
      action: TouchAction.TOUCH_START,
      pointerId: this.cursorId,
      x: x1,
      y: y1,
    });
    await this.vePhone.sendTouchMessage({
      action: TouchAction.TOUCH_MOVE,
      pointerId: this.cursorId,
      x: x2,
      y: y2,
    });
    return new Promise(resolve => {
      // 这里把 TOUCH_END 放到下一个事件循环里，
      // 给前面的 start/move 留出被 SDK 消费的机会。
      setTimeout(() => {
        this.vePhone.sendTouchMessage({
          action: TouchAction.TOUCH_END,
          pointerId: this.cursorId,
          x: x2,
          y: y2,
        });
        resolve(true);
      }, 0);
    });
  }
}
