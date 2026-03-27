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
	"net/url"

	"github.com/mark3labs/mcp-go/mcp"
)

// NewAppUploadTool 用来声明 MCP 工具的元信息。
//
// 注意，这里还没有开始安装 App。
// 它做的是把“工具名字、功能描述、参数要求”注册给 MCP 框架，
// 这样模型在看到工具列表时，才知道该怎么正确调用它。
func NewAppUploadTool() mcp.Tool {
	return mcp.NewTool("autoinstall_app",
		mcp.WithDescription("Download and install an app in one step on the cloud phone"),
		mcp.WithString("download_url",
			mcp.Description("The download url of the app"),
			mcp.Required(),
		),
		mcp.WithString("app_name",
			mcp.Description("The app name to be uploaded"),
			mcp.Required(),
		),
	)
}

// HandleAppUploadTool 返回真正处理请求的函数。
//
// MCP Server 注册工具时，不是直接执行逻辑，
// 而是先拿到一个 handler，等模型真的发起调用时再传入 ctx 和 req。
func HandleAppUploadTool() func(context.Context, mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	return func(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		// 先检查当前请求是否已经通过认证。
		// 没有鉴权的请求，不允许继续触发云手机操作。
		err := CheckAuth(ctx)
		if err != nil {
			return CallResultError(err)
		}

		// 从 context 里取出服务端预先整理好的业务配置。
		// 这样工具层只负责“执行动作”，不负责拼装配置来源。
		mobileUseConfig, err := GetMobileUseConfig(ctx)
		if err != nil || mobileUseConfig == nil {
			return CallResultError(err)
		}

		// 把配置转换成一个真正可操作云手机的 service provider。
		handler, err := InitMobileUseService(ctx, mobileUseConfig)
		if err != nil {
			return CallResultError(err)
		}

		// 参数在 MCP 请求里是动态结构，这里先统一校验为 map。
		args, err := CheckArgs(req.Params.Arguments)
		if err != nil {
			return CallResultError(err)
		}
		downloadUrl, ok := args["download_url"].(string)
		if !ok || downloadUrl == "" {
			return CallResultError(fmt.Errorf("download_url is required"))
		}

		if !isUrl(downloadUrl) {
			return CallResultError(fmt.Errorf("download_url is invalid: %s", downloadUrl))
		}

		// 下载地址通过校验后，才调用底层安装逻辑。
		// 如果安装失败，会把原始错误包一层更清晰的业务语义再返回。
		err = handler.AutoInstallApp(ctx, downloadUrl)
		if err != nil {
			return CallResultError(fmt.Errorf("failed to install app: %w", err))
		}

		// 成功时返回简单文本，告诉调用方“安装动作已经成功触发”。
		return CallResultSuccess("Apk is being installed")
	}
}

// isUrl 是一个前置校验函数，用来挡住明显不合法的下载地址。
// 它至少检查三件事：
// 1. 字符串能否被解析成 URL；
// 2. 协议是否是 http 或 https；
// 3. 主机部分是否存在。
func isUrl(downloadUrl string) bool {
	parsedUrl, err := url.Parse(downloadUrl)
	if err != nil || (parsedUrl.Scheme != "http" && parsedUrl.Scheme != "https") || parsedUrl.Host == "" {
		return false
	}
	return true
}
