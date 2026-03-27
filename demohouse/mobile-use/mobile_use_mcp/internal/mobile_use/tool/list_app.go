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
	"encoding/json"

	"github.com/mark3labs/mcp-go/mcp"
)

// NewListAppTool 声明“列出所有已安装应用”的工具。
//
// 由于它只是读取当前云手机状态，不针对单个目标对象，
// 所以这里不需要额外参数。
func NewListAppTool() mcp.Tool {
	return mcp.NewTool("list_apps",
		mcp.WithDescription("List all apps installed on cloud phone"),
	)
}

// HandleListAppTool 执行 list_apps 请求。
// 这个函数很适合初学者观察“读取型工具”和“写入型工具”的共同骨架：
// 它们都会做鉴权、配置获取和错误包装，只是中间执行业务的方法不同。
func HandleListAppTool() func(context.Context, mcp.CallToolRequest) (*mcp.CallToolResult, error) {
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
		appList, err := handler.ListApps(ctx)
		if err != nil {
			return CallResultError(err)
		}

		// 这里把返回结果包成一个带字段名的 JSON 对象，
		// 方便上层消费时明确知道这份数据表示“应用列表”。
		result := map[string]interface{}{
			"AppList": appList,
		}

		// 这里故意沿用原始逻辑，忽略 json.Marshal 的错误返回值。
		// 这不是最佳实践，但当前任务只允许补注释，不改行为。
		jsonResult, _ := json.Marshal(result)
		return CallResultSuccess(string(jsonResult))
	}
}
