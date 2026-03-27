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

func NewTextInputTool() mcp.Tool {
	return mcp.NewTool("text_input",
		mcp.WithDescription("Input text on the screen"),
		mcp.WithString("text",
			mcp.Description("The text to input"),
			mcp.Required(),
		),
	)
}

func HandleTextInput() func(context.Context, mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	return func(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		err := CheckAuth(ctx)
		if err != nil {
			return CallResultError(err)
		}
		mobileUseConfig, err := GetMobileUseConfig(ctx)
		if err != nil || mobileUseConfig == nil {
			return CallResultError(err)
		}
		handler, err := InitMobileUseService(ctx, mobileUseConfig)
		if err != nil {
			return CallResultError(err)
		}
		// 输入文字前先清空已有输入框内容，减少“旧内容残留 + 新内容追加”的问题。
		err = handler.InputTextClear(ctx)
		if err != nil {
			return CallResultError(err)
		}
		args, err := CheckArgs(req.Params.Arguments)
		if err != nil {
			return CallResultError(err)
		}
		// 这里显式取出 text 参数并校验类型，
		// 因为 MCP 的 arguments 本质上仍是动态 map，不是强类型结构体。
		text, ok := args["text"].(string)
		if !ok {
			return CallResultError(fmt.Errorf("text is required"))
		}
		err = handler.InputText(ctx, text)
		if err != nil {
			return CallResultError(err)
		}
		return CallResultSuccess("Input text successfully")
	}
}
