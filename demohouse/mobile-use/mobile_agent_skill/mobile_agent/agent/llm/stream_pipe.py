# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# Licensed under the 【火山方舟】原型应用软件自用许可协议
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at 
#     https://www.volcengine.com/docs/82379/1433703
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Dict, Optional
from pydantic import BaseModel
import re


class StreamPipeMessage(BaseModel):
    """
    保存某一条流式输出在解析过程中的中间状态。

    由于模型返回的是一小段一小段的 delta，而不是一次性完整文本，
    我们需要把已经收到的内容先暂存起来，等格式足够完整时再拆出 summary 和 action。
    """

    id: str
    content: str
    summary: str
    tool_call: str
    summary_collected: bool
    last_summary_length: int = 0


class StreamPipe:
    """
    把模型的流式文本解析成“总结 + 动作”的辅助类。

    当前系统要求模型按下面的格式输出：
    Summary: ...
    Action: ...

    但流式场景下，关键字本身也可能被拆开，所以这里要做的是“增量解析”，
    而不是简单地等全部返回后再一次性 split。
    """

    pipes: Dict[str, StreamPipeMessage]

    def __init__(self):
        # `pipes` 可以理解成“按 chunk_id 分桶的流式缓冲区”。
        # 一次模型回答对应一个桶，桶里保存当前已经累计到哪里了。
        self.pipes = {}

    def create(self, id: str):
        # 某些 LangGraph 流式事件会先于模型侧第一次显式 create 到达。
        # 因此 create 需要是幂等的，避免把已经缓存的增量内容重置掉。
        if id in self.pipes:
            return self.pipes[id]

        # 为一条新的流式输出创建缓冲区。
        self.pipes[id] = StreamPipeMessage(
            id=id,
            content="",
            summary="",
            tool_call="",
            summary_collected=False,
            last_summary_length=0,
        )
        return self.pipes[id]

    def pipe(self, id: str, delta: str):
        # 每收到一个新的文本碎片，就先拼接到完整 content 上。
        chat_data = self.pipes.get(id)
        if chat_data is None:
            chat_data = self.create(id)
        chat_data.content += delta
        # 下面这些状态示例说明了为什么这里不能偷懒：
        # 1. Summ
        # 2. Summary:
        # 3. Summary: 现在我们需要点击抖音图标
        # 4. Summary: 现在我们需要点击抖音图标\n
        # 5. Summary: 现在我们需要点击抖音图标\nActi
        # 6. Summary: 现在我们需要点击抖音图标\nAction: ba
        # 7. Summary: 现在我们需要点击抖音图标\nAction: press_back()
        # 也就是说，Summary 和 Action 可能同时处在“半截生成中”的状态。

        # 检查是否可能是 Action 关键词正在生成中
        is_action_keyword_partial = False
        if not chat_data.summary_collected and "\n" in chat_data.content:
            # 检查最后一行是否可能是 Action 关键词的开始部分
            last_line = chat_data.content.split("\n")[-1]
            # 检查是否以 A, Ac, Act, Acti, Actio, Action 开头，但不是完整的 "Action:"
            action_prefixes = ["A", "Ac", "Act", "Acti", "Actio", "Action"]
            if any(
                last_line.startswith(prefix) for prefix in action_prefixes
            ) and not last_line.startswith("Action:"):
                is_action_keyword_partial = True

        # 只要已经出现 Summary:，就尝试提取当前可以确认的 summary 内容。
        if "Summary:" in chat_data.content:
            current_summary = ""
            summary_text = chat_data.content.split("Summary:")[1]

            # 如果 Summary 后面还有 Action，只保留 Summary 部分
            if "\nAction:" in summary_text:
                summary_text = summary_text.split("\nAction:")[0]
                chat_data.summary_collected = (
                    True  # 如果已经有完整的 Action 关键词，则 Summary 肯定已完成
                )

            # 处理 Action 关键词不完整的情况
            elif is_action_keyword_partial and "\n" in summary_text:
                # 取最后一个换行符之前的内容作为 summary
                summary_text = summary_text.split("\n")[0]
                chat_data.summary_collected = (
                    True  # 标记 Summary 已完成，因为已经开始生成 Action
                )

            current_summary = summary_text.strip()
            chat_data.summary = current_summary

            # 同一个 delta 里可能已经把 Action 一并返回完了，
            # 需要在返回 summary 增量前先把 tool_call 状态落盘，
            # 否则 complete() 会误判成“只有 summary 没有动作”。
            if "Action:" in chat_data.content:
                chat_data.tool_call = chat_data.content.split("Action:")[1].strip()

            # 这里返回的是“新增部分”而不是完整 summary，
            # 方便前端做流式追加渲染。
            if len(current_summary) > chat_data.last_summary_length:
                summary_delta = current_summary[chat_data.last_summary_length :]
                # 如果新增片段里已经混入了下一行 Action 的开头，就把那部分裁掉。
                if "\n" in summary_delta:
                    parts = summary_delta.split("\n", 1)
                    summary_delta = parts[0]
                chat_data.last_summary_length = len(current_summary)
                return id, summary_delta

            # 如果 summary 还没正式结束，就持续刷新它的当前值。
            if not chat_data.summary_collected and (
                (delta == "\n" and len(summary_text.strip()) > 0)
                or (len(summary_text) > 0 and summary_text[-1] == "\n")
            ):
                # 一旦检测到换行结束，就认为 summary 已经收集完成。
                chat_data.summary_collected = True

        # Action 的提取不依赖 summary 是否完整结束，只要关键字出现就先记下来。
        if "Action:" in chat_data.content:
            action_text = chat_data.content.split("Action:")[1].strip()
            chat_data.tool_call = action_text

    def complete(self, id: str):
        # 在一轮流式输出结束后，产出完整解析结果。
        if id not in self.pipes:
            # 找不到缓冲区说明上下文已经不一致，统一走错误动作分支。
            return self.error_action()

        chat_data = self.pipes[id].model_dump()

        content = chat_data.get("content", "")
        summary = chat_data.get("summary", "")
        tool_call = chat_data.get("tool_call", "")

        # summary 或 tool_call 缺失都说明格式不完整，不能进入正常执行。
        if not summary or not tool_call:
            return self.error_action(id)

        # 解析成功后立刻删除缓冲区，避免旧内容污染下一轮同 id 的处理。
        self.pipes.pop(id, None)
        return content, summary, tool_call

    def error_action(self, id: Optional[str] = None) -> tuple[str, str, str]:
        # 这里不直接抛异常，而是返回一个约定好的 error_action，
        # 让上层可以把“解析失败”也当成一种普通动作处理。
        if id and id in self.pipes:
            content = self.pipes[id].content
            self.pipes.pop(id, None)
        else:
            content = ""
        tool_call = "error_action()"
        return content, "解析失败，未找到对应的动作, 请重新遵循格式输出", tool_call


stream_pipeline = StreamPipe()
