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

import { Button } from "../ui/button"
import ClearIcon from '@/assets/icon-clear.svg'
import ClearDisabledIcon from '@/assets/icon-clear-disabled.svg'
import Image from 'next/image'
import { useMemo, useState } from 'react'
import { useCloudAgent } from '@/hooks/useCloudAgent'
import { fetchAPI } from '@/lib/fetch'
import { MessageListAtom } from "@/app/atom"
import { useAtomValue } from "jotai"
import { cn } from "@/lib/utils"
import { SessionBackendResponse } from "@/types"
import { changeAgentChatThreadId } from "@/lib/cloudAgent"



const ResetChat = (props: { className?: string }) => {
  // 用 loading 状态防止用户在网络请求还没结束时重复点击。
  const [isResetting, setIsResetting] = useState(false)
  const cloudAgent = useCloudAgent()
  const messages = useAtomValue(MessageListAtom)

  // 只有当前存在 thread 且已经有消息时，清空上下文这个动作才有意义。
  const disabled = useMemo(() => {
    return isResetting || !cloudAgent?.threadId || messages.length === 0
  }, [isResetting, cloudAgent?.threadId, messages?.length])

  const handleReset = async () => {
    // 没有活动线程，或者已经在重置中时，不需要重复发请求。
    if (!cloudAgent?.threadId || isResetting) {
      return
    }

    setIsResetting(true)

    try {
      // 先取消可能仍在运行的 Agent，避免旧请求和新会话交叉。
      await cloudAgent.cancel().catch(
        (error) => console.error('取消会话失败:', error)
      )
      // 再向后端申请一个新的 thread_id，真正开始一个“干净”的上下文。
      const data = await fetchAPI('/api/session/reset', {
        method: 'POST',
        body: JSON.stringify({ thread_id: cloudAgent.threadId }),
      }) as SessionBackendResponse

      if (data.thread_id) {
        // 前端本地也必须同步新 thread_id，否则后续消息还会打到旧会话上。
        cloudAgent.setThreadId(data.thread_id)
        changeAgentChatThreadId(data.chat_thread_id)
        console.log('会话重置成功:', data.thread_id, data.chat_thread_id)
      }
    } catch (error) {
      console.error('重置会话失败:', error)
    } finally {
      // 稍微延迟一下再解除 loading，给用户一个明确的操作反馈。
      setTimeout(() => {
        setIsResetting(false)
      }, 500)
    }
  }

  return (
    <Button
      variant="outline"
      className={cn(
        "m-[20px] border-[#C9CDD4] text-[#4E5969] hover:bg-gray-50 hover:cursor-pointer rounded-[4px] disabled:text-[#C7CCD6] disabled:bg-[#F6F8FA] disabled:cursor-not-allowed",
        props.className
      )}
      onClick={handleReset}
      disabled={disabled}
    >
      {isResetting ? (
        <>
          <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-1"></div>
          重置中...
        </>
      ) : (
        <>
          <Image src={disabled ? ClearDisabledIcon : ClearIcon} alt="clear icon" width={16} height={16} />
          清除上下文
        </>
      )}
    </Button>
  )
}

export default ResetChat
