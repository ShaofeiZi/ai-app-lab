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

// NewCloseAppTool 声明“关闭应用”这个工具。
//
// 这里要求调用方传 package_name，
// 因为包名才是系统内部稳定且唯一的应用标识。
func NewCloseAppTool() mcp.Tool {
	return mcp.NewTool("close_app",
		mcp.WithDescription("Close a running app on the cloud phone"),
		mcp.WithString("package_name",
			mcp.Description("The package name of apk"),
			mcp.Required(),
		),
	)
}

// HandleCloseAppTool 处理真正的 close_app 请求。
// 它沿用本项目工具层的固定模板：鉴权、取配置、初始化服务、校验参数、执行操作、返回 MCP 结果。
func HandleCloseAppTool() func(context.Context, mcp.CallToolRequest) (*mcp.CallToolResult, error) {
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
		packageName, ok := args["package_name"].(string)
		if !ok || packageName == "" {
			return CallResultError(fmt.Errorf("package_name is required"))
		}

		// 参数合法后，交给 service 层去关闭目标应用。
		err = handler.CloseApp(ctx, packageName)
		if err != nil {
			return CallResultError(err)
		}

		// 成功时返回统一的文本结果，便于上层直接展示。
		return CallResultSuccess("Close app successfully")
	}
}
