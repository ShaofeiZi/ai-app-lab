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

	"mcp_server_mobile_use/internal/mobile_use/config"
	"mcp_server_mobile_use/internal/mobile_use/consts"
	"mcp_server_mobile_use/internal/mobile_use/service"

	"github.com/mark3labs/mcp-go/mcp"
)

func CheckAuth(ctx context.Context) error {
	// 每个工具真正执行前都先检查 context 里的鉴权结果，
	// 这样工具文件本身不需要重复解析请求头或环境变量。
	authResult := ctx.Value(consts.AuthResult{})
	if authResult == nil || authResult.(string) != consts.AuthResultOk {
		return fmt.Errorf("auth failed")
	}
	return nil
}

func GetMobileUseConfig(ctx context.Context) (*config.MobileUseConfig, error) {
	// server 层已经把请求里的产品、设备、TOS、鉴权信息拼成了 MobileUseConfig，
	// 这里直接取出给后续 service 层使用。
	mobileUseConfig := ctx.Value(consts.MobileUseConfigKey{})
	if mobileUseConfig == nil {
		return nil, fmt.Errorf("mobile use config not found")
	}
	conf := mobileUseConfig.(config.MobileUseConfig)
	return &conf, nil
}

func CallResultError(err error) (*mcp.CallToolResult, error) {
	// MCP 协议要求工具调用返回结构化结果。
	// 这里把 Go 的 error 转成 MCP 的错误结果，便于上层模型识别“这次工具失败了”。
	toolResult := &mcp.CallToolResult{
		Content: []mcp.Content{},
		IsError: true,
	}
	if err != nil {
		toolResult.Content = append(toolResult.Content, mcp.NewTextContent(err.Error()))
	}
	return toolResult, nil
}

func CallResultSuccess(content string) (*mcp.CallToolResult, error) {
	return mcp.NewToolResultText(content), nil
}

func InitMobileUseService(ctx context.Context, mobileUseConfig *config.MobileUseConfig) (service.MobileUseProvider, error) {
	// 这里把 context 中准备好的配置组装成 provider。
	// 初学者可以理解为：MCP 工具层本身不直接打云接口，而是先得到一个“会操作云手机的服务对象”。
	if mobileUseConfig == nil {
		return nil, fmt.Errorf("mobile use config is nil")
	}
	if mobileUseConfig.AuthInfo.AccessKeyId == "" || mobileUseConfig.AuthInfo.SecretAccessKey == "" {
		return nil, fmt.Errorf("get acep auth info failed")
	}
	if mobileUseConfig.BizInfo.ProductId == "" || mobileUseConfig.BizInfo.DeviceId == "" {
		return nil, fmt.Errorf("get acep biz info failed")
	}

	opts := []service.Option{
		service.WithAccessKey(mobileUseConfig.AuthInfo.AccessKeyId),
		service.WithSecretKey(mobileUseConfig.AuthInfo.SecretAccessKey),
		service.WithProductID(mobileUseConfig.BizInfo.ProductId),
		service.WithDeviceID(mobileUseConfig.BizInfo.DeviceId),
	}

	if mobileUseConfig.BizInfo.ACEPHost != "" {
		opts = append(opts, service.WithHost(mobileUseConfig.BizInfo.ACEPHost))
	}

	if mobileUseConfig.AuthInfo.SessionToken != "" {
		opts = append(opts, service.WithSessionToken(mobileUseConfig.AuthInfo.SessionToken))
	}
	if mobileUseConfig.TosInfo.TosBucket != "" {
		opts = append(opts, service.WithBucket(mobileUseConfig.TosInfo.TosBucket))
	}
	if mobileUseConfig.TosInfo.TosRegion != "" {
		opts = append(opts, service.WithRegion(mobileUseConfig.TosInfo.TosRegion))
	}
	if mobileUseConfig.TosInfo.TosEndpoint != "" {
		opts = append(opts, service.WithEndpoint(mobileUseConfig.TosInfo.TosEndpoint))
	}
	if mobileUseConfig.TosInfo.TosAccessKey != "" {
		opts = append(opts, service.WithTosAccessKey(mobileUseConfig.TosInfo.TosAccessKey))
	}
	if mobileUseConfig.TosInfo.TosSecretKey != "" {
		opts = append(opts, service.WithTosSecretKey(mobileUseConfig.TosInfo.TosSecretKey))
	}
	if mobileUseConfig.TosInfo.TosSessionToken != "" {
		opts = append(opts, service.WithTosSessionToken(mobileUseConfig.TosInfo.TosSessionToken))
	}

	handler := service.NewMobileUseImpl(opts...)
	return handler, nil
}

func GetInt64Param(args map[string]interface{}, key string) (int64, error) {
	// MCP 参数是动态 map，数字有时会被反序列化成 int，有时是 float64。
	// 这里统一兜底成 int64，避免每个工具自己重复写类型判断。
	val, exists := args[key]
	if !exists {
		return 0, fmt.Errorf("%s is required", key)
	}

	switch v := val.(type) {
	case int:
		return int64(v), nil
	case int64:
		return v, nil
	case float64:
		return int64(v), nil
	default:
		return 0, fmt.Errorf("%s must be an integer, got %T", key, val)
	}
}

func CheckArgs(args any) (map[string]interface{}, error) {
	// 请求里没有参数，或者参数不是预期的 map 结构时，尽早失败。
	if args == nil {
		return nil, fmt.Errorf("args is nil")
	}
	res, ok := args.(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("args is invalid")
	}
	return res, nil
}
