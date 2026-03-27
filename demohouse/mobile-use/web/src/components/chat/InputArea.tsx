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

import React, { useEffect, useRef, useState } from 'react';
import Image from 'next/image';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils/css';
import cancelButtonIcon from '@/assets/cancel-button.svg';
import sendButtonIcon from '@/assets/send-button.svg';
import QuestionnAire from '@/assets/questionnaire.svg';
import { Tooltip, TooltipContent, TooltipTrigger, TooltipArrow, TooltipProvider } from '@/components/ui/tooltip';

interface InputAreaProps {
  handleSendMessage: (text: string) => void;
  handleCancel: () => void;
  isCalling: boolean;
  isCanceling: boolean;
  inputValue?: string;
  onTextChange?: (text: string) => void;
}

const InputArea: React.FC<InputAreaProps> = ({
  handleSendMessage,
  handleCancel,
  isCalling,
  isCanceling,
  inputValue,
  onTextChange,
}) => {
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const [internalInputText, setInternalInputText] = useState('');
  const [isComposing, setIsComposing] = useState(false);

  // 这个组件既支持“自己管理输入值”，也支持“父组件把输入值传进来控制”。
  // 这就是受控 / 非受控两种模式。
  const isControlled = inputValue !== undefined && onTextChange !== undefined;

  // 获取当前输入值
  const currentInputValue = isControlled ? inputValue : internalInputText;

  // 页面一打开就把焦点放到输入框，用户可以直接开始输入。
  useEffect(() => {
    inputRef.current?.focus();
  }, [inputRef]);

  // 输入变化时一边更新文本，一边根据内容高度自动撑开输入框，
  // 这样多行任务描述不会把文字挤成一团。
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;

    // 根据内容自动调整高度
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 120)}px`;
    }

    if (isControlled) {
      // 受控模式下，真正的数据源在父组件手里。
      onTextChange(newValue);
    } else {
      // 非受控模式下，这个组件自己保存输入值。
      setInternalInputText(newValue);
    }
  };

  // handleSend 只负责“把当前输入交给外部发送逻辑”，
  // 真正的网络请求和消息追加在父组件里完成。
  const handleSend = () => {
    if (currentInputValue.trim() !== '' && !isCalling) {
      handleSendMessage(currentInputValue);

      // 发送后立即清空输入框，给用户“这一条已经提交”的清晰反馈。
      if (isControlled) {
        onTextChange('');
      } else {
        setInternalInputText('');
      }

      // 文本清空后，也把输入框高度收回去。
      if (inputRef.current) {
        inputRef.current.style.height = 'auto';
      }
    }
  };

  // Enter 发送、Shift+Enter 换行是聊天输入框里很常见的交互规则。
  // 这里还额外处理了输入法组合状态，避免中文输入过程中误发送。
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // 如果按下 Enter 键，并且没有同时按下 Shift 键，且不在输入法组合状态
    if (e.key === 'Enter' && !e.shiftKey && !isComposing && !isCalling && currentInputValue.trim() !== '') {
      e.preventDefault(); // 阻止默认的换行行为
      handleSend(); // 触发发送消息函数
    }
  };

  return (
    <div className="relative flex flex-col items-end gap-2 p-3 bg-white rounded-xl border border-[rgba(221,228,237,1)]">
      <style jsx global>{`
        textarea::-webkit-scrollbar {
          width: 6px;
          height: 6px;
        }
        textarea::-webkit-scrollbar-track {
          background: transparent;
          border-radius: 6px;
        }
        textarea::-webkit-scrollbar-thumb {
          background-color: #e5e7eb;
          border-radius: 6px;
        }
        textarea::-webkit-scrollbar-thumb:hover {
          background-color: #d1d5db;
        }
      `}</style>
      <Textarea
        ref={inputRef}
        className={cn('resize-none flex-1', 'h-[120px]', 'placeholder-gray-400', 'border-none', 'box-shadow-none')}
        style={{
          scrollbarWidth: 'thin',
          scrollbarColor: '#E5E7EB transparent',
        }}
        value={currentInputValue}
        onChange={handleInputChange}
        placeholder="请输入你的任务，让 Mobile Use 帮你完成"
        onCompositionStart={() => setIsComposing(true)}
        onCompositionEnd={() => setIsComposing(false)}
        onKeyDown={handleKeyDown}
        // disabled={isCalling}
      />
      <div className="flex w-full justify-between items-center">
        <Button
          className="h-[30px] rounded-[6px] border border-[#EAEDF1] bg-[#F6F8FA] text-[#737A87] font-normal px-3 cursor-pointer hover:bg-[#737A87]/10"
          onClick={() => {
            window.open('https://bytedance.larkoffice.com/share/base/form/shrcn0fT1SGEG19AI0ONIIHf3oh', '_blank');
          }}
        >
          <Image src={QuestionnAire} alt="QuestionnAire" width={15} height={13} />
          问卷反馈
        </Button>
        <TooltipProvider delayDuration={0}>
          {isCalling ? (
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  className={cn(
                    'relative ml-2 h-[28px] w-[44px]',
                    'cursor-pointer',
                    'shadow-none focus:shadow-none focus-visible:shadow-none',
                    'bg-transparent',
                    'bg-cover bg-center',
                  )}
                  style={{ backgroundImage: `url(${cancelButtonIcon.src})` }}
                  onClick={handleCancel}
                  disabled={isCanceling}
                />
              </TooltipTrigger>
              <TooltipContent>
                <TooltipArrow className="fill-black" />
                <p>停止任务</p>
              </TooltipContent>
            </Tooltip>
          ) : (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  className="ml-2 bg-[linear-gradient(149.14deg,#7E83FF_13.01%,#735CFF_46.75%,#3671FF_85.57%)] text-white h-[28px] w-[44px] rounded-[14px] flex items-center justify-center shadow-md transition-all duration-200 hover:shadow-lg active:shadow-md disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0 disabled:hover:shadow-md disabled:hover:scale-100 cursor-pointer"
                  variant="default"
                  size="default"
                  onClick={handleSend}
                  disabled={currentInputValue.trim() === '' || isCalling}
                >
                  <Image src={sendButtonIcon} alt="send" width={15} height={13} />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <TooltipArrow className="fill-black" />
                <p>发送消息</p>
              </TooltipContent>
            </Tooltip>
          )}
        </TooltipProvider>
      </div>
    </div>
  );
};

export default InputArea;
