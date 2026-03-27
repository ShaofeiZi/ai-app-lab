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

// NewLaunchAppTool 声明“启动应用”这个工具的调用契约。
//
// 对模型来说，这里的名字、描述和参数说明就像一份轻量接口文档，
// 它会根据这些信息决定是否调用这个工具以及如何传参。
func NewLaunchAppTool() mcp.Tool {
	return mcp.NewTool("launch_app",
		mcp.WithDescription("Open an app that has been installed on the cloud phone"),
		mcp.WithString("package_name",
			mcp.Description("The package name of apk"),
			mcp.Required(),
		),
	)
}

// HandleLaunchAppTool 返回 launch_app 的真正执行器。
// NewLaunchAppTool 负责“告诉别人怎么用”，这里负责“收到请求后怎么做”。
func HandleLaunchAppTool() func(context.Context, mcp.CallToolRequest) (*mcp.CallToolResult, error) {
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

		// 只有在拿到有效包名之后，才触发底层启动应用的动作。
		err = handler.LaunchApp(ctx, packageName)
		if err != nil {
			return CallResultError(err)
		}

		// 返回可读文本，让调用方清楚知道这次调用已经完成。
		return CallResultSuccess("Launch app successfully")
	}
}
