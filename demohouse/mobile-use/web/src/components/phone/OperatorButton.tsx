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

import { useState } from 'react';
import { Button } from '../ui/button';

const OperatorButton = ({
  callback,
  icon,
}: {
  callback: () => Promise<void> | void;
  icon: React.ReactNode;
}) => {
  // loading 表示当前按钮触发的异步操作是否尚未完成。
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    try {
      setLoading(true);
      // 具体执行什么操作由外部传入，当前组件只负责统一的按钮行为。
      await callback();
    } catch (error) {
      console.error(error);
    } finally {
      // 无论成功还是失败，都要恢复按钮可点击状态。
      setLoading(false);
    }
  };

  return (
    <Button variant="outline" onClick={handleClick} disabled={loading}>
      {loading ? (
        <div className="w-4 h-4 rounded-full border-2 border-gray-300 border-t-black animate-spin" />
      ) : (
        icon
      )}
    </Button>
  );
};

export default OperatorButton;
