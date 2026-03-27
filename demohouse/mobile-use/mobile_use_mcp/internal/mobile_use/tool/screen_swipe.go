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

// NewScreenSwipeTool 声明“滑动屏幕”的工具。
//
// 这里把起点和终点拆成四个独立坐标参数，
// 这样模型在构造调用时更直接，也不需要先拼复杂对象。
func NewScreenSwipeTool() mcp.Tool {
	return mcp.NewTool("swipe",
		mcp.WithDescription("Swipe from one coordinate to another coordinate on cloud phone"),
		mcp.WithNumber("from_x",
			mcp.Description("The x coordinate of the start point"),
			mcp.Required(),
		),
		mcp.WithNumber("from_y",
			mcp.Description("The y coordinate of the start point"),
			mcp.Required(),
		),
		mcp.WithNumber("to_x",
			mcp.Description("The x coordinate of the end point"),
			mcp.Required(),
		),
		mcp.WithNumber("to_y",
			mcp.Description("The y coordinate of the end point"),
			mcp.Required(),
		),
	)
}

// HandleScreenSwipe 把动态请求参数整理成 service 层真正需要的整数坐标。
// 这里最核心的教学点是：MCP 传参常常是弱类型的，进入业务层前要先做类型收敛。
func HandleScreenSwipe() func(context.Context, mcp.CallToolRequest) (*mcp.CallToolResult, error) {
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
		args, err := CheckArgs(req.Params.Arguments)
		if err != nil {
			return CallResultError(err)
		}

		// GetInt64Param 负责兼容 int、int64、float64 等常见动态类型，
		// 避免当前文件里重复写一堆类型判断。
		fromX, err := GetInt64Param(args, "from_x")
		if err != nil {
			return CallResultError(fmt.Errorf("from_x is required"))
		}
		fromY, err := GetInt64Param(args, "from_y")
		if err != nil {
			return CallResultError(fmt.Errorf("from_y is required"))
		}
		toX, err := GetInt64Param(args, "to_x")
		if err != nil {
			return CallResultError(fmt.Errorf("to_x is required"))
		}
		toY, err := GetInt64Param(args, "to_y")
		if err != nil {
			return CallResultError(fmt.Errorf("to_y is required"))
		}

		// 完成参数收敛后，再调用底层 provider 执行真实的滑动手势。
		err = handler.ScreenSwipe(ctx, int(fromX), int(fromY), int(toX), int(toY))
		if err != nil {
			return CallResultError(err)
		}

		// 文本结果表示这次滑动动作已成功处理。
		return CallResultSuccess("Swipe the screen successfully")
	}
}
