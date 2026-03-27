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

package tool

import (
	"context"
	"fmt"

	"github.com/mark3labs/mcp-go/mcp"
)

// NewTerminateTool 声明“终止当前任务”的工具。
//
// reason 被设计成必填参数，
// 是为了让这次终止操作至少留下一条明确原因，方便日志排查和上层展示。
func NewTerminateTool() mcp.Tool {
	return mcp.NewTool("terminate",
		mcp.WithDescription("Terminate the current task"),
		mcp.WithString("reason",
			mcp.Description("The reason for terminating the task"),
			mcp.Required(),
		),
	)
}

// HandleTerminate 处理 terminate 请求。
//
// 和其他工具不同的是，这里当前实现不会调用 service 层去停止某个真实后台任务，
// 而是在鉴权和参数校验通过后，直接返回一条确认文本。
// 这意味着它现在更像一个“终止意图确认接口”，而不是完整的任务中断实现。
// 本次只把这一点解释清楚，不改变既有行为。
func HandleTerminate() func(context.Context, mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	return func(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		err := CheckAuth(ctx)
		if err != nil {
			return CallResultError(err)
		}
		mobileUseConfig, err := GetMobileUseConfig(ctx)
		if err != nil || mobileUseConfig == nil {
			return CallResultError(err)
		}
		args, err := CheckArgs(req.Params.Arguments)
		if err != nil {
			return CallResultError(err)
		}
		reason, ok := args["reason"].(string)
		if !ok || reason == "" {
			return CallResultError(fmt.Errorf("reason is required"))
		}

		// 成功结果里直接回显终止原因，
		// 方便调用方在界面或日志里立即看到这次终止是为什么发生的。
		return CallResultSuccess(fmt.Sprintf("Task terminated: %s", reason))
	}
}
