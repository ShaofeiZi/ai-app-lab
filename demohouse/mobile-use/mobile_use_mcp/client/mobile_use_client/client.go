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

package mobile_use_client

import (
	"context"

	"github.com/mark3labs/mcp-go/client"
	"github.com/mark3labs/mcp-go/client/transport"
	"github.com/mark3labs/mcp-go/mcp"
)

// NewMobileUseSSEClient 创建一个基于 SSE 的 MCP 客户端。
//
// 可以把它理解成一个“已经帮你完成好几步准备动作”的工厂函数：
// 1. 先按 baseUrl 创建连接对象；
// 2. 再启动客户端，让它开始真正收发消息；
// 3. 最后发送 initialize 握手，告诉服务端自己支持的协议版本和客户端身份。
//
// 这样上层调用方只需要拿到返回值，就能直接继续调用 MCP 工具，
// 不必在每个地方重复写启动和握手代码。
func NewMobileUseSSEClient(ctx context.Context, baseUrl string, headers map[string]string) (*client.Client, error) {
	var (
		cli *client.Client
		err error
	)
	// headers 用来透传鉴权或业务相关的 HTTP 头。
	// 没有额外头部时，就走默认构造逻辑。
	if len(headers) > 0 {
		cli, err = client.NewSSEMCPClient(baseUrl, client.WithHeaders(headers))
	} else {
		cli, err = client.NewSSEMCPClient(baseUrl)
	}
	if err != nil {
		return nil, err
	}
	if err := cli.Start(ctx); err != nil {
		return nil, err
	}

	// initialize 属于 MCP 协议级别的“自报家门”。
	// 客户端需要在这里明确声明自己支持的协议版本和自己的实现信息。
	initReq := mcp.InitializeRequest{}
	initReq.Params.ProtocolVersion = mcp.LATEST_PROTOCOL_VERSION
	initReq.Params.ClientInfo = mcp.Implementation{
		Name:    "mobile_use_mcp_client",
		Version: "0.0.1",
	}

	// 如果握手失败，说明连接虽然建起来了，但协议层还没有准备好，
	// 此时不能把客户端当作可用对象返回。
	_, err = cli.Initialize(ctx, initReq)
	if err != nil {
		return nil, err
	}
	return cli, nil
}

// NewMobileUseStdioClient 创建一个通过标准输入输出通信的 MCP 客户端。
//
// 这种模式常见于“本地启动一个子进程作为 MCP Server”的场景。
// 调用方需要提供：
// - cmd: 可执行程序路径
// - env: 子进程启动时使用的环境变量
// - args: 传给该程序的命令行参数
//
// 和网络型客户端不同，这里不需要显式调用 Start，
// 因为 stdio 通道在客户端创建时就已经绑定好了。
func NewMobileUseStdioClient(ctx context.Context, cmd string, env []string, args ...string) (*client.Client, error) {
	cli, err := client.NewStdioMCPClient(
		cmd,
		env,
		args...,
	)
	if err != nil {
		return nil, err
	}

	// 传输层虽然换成了 stdio，但协议层的初始化步骤并不会变。
	// 这正好说明“怎么传消息”和“消息按什么协议组织”是两件分开的事。
	initReq := mcp.InitializeRequest{}
	initReq.Params.ProtocolVersion = mcp.LATEST_PROTOCOL_VERSION
	initReq.Params.ClientInfo = mcp.Implementation{
		Name:    "mobile_use_mcp_client",
		Version: "0.0.1",
	}

	_, err = cli.Initialize(ctx, initReq)
	if err != nil {
		return nil, err
	}
	return cli, nil
}

// NewMobileUseStreamableHTTPClient 创建一个基于 Streamable HTTP 的 MCP 客户端。
//
// 它和 SSE 版本的流程几乎一致：
// 先创建对象，再 Start，再 Initialize。
// 单独保留这个函数，是为了让调用方按传输协议清晰选型，
// 而不是自己到处判断该调哪个底层构造函数。
func NewMobileUseStreamableHTTPClient(ctx context.Context, addr string, headers map[string]string) (*client.Client, error) {
	cli, err := client.NewStreamableHttpClient(addr, transport.WithHTTPHeaders(headers))
	if err != nil {
		return nil, err
	}
	if err := cli.Start(ctx); err != nil {
		return nil, err
	}

	// 每创建一个新的客户端实例，都要独立完成一次协议握手。
	initReq := mcp.InitializeRequest{}
	initReq.Params.ProtocolVersion = mcp.LATEST_PROTOCOL_VERSION
	initReq.Params.ClientInfo = mcp.Implementation{
		Name:    "mobile_use_mcp_client",
		Version: "0.0.1",
	}

	_, err = cli.Initialize(ctx, initReq)
	if err != nil {
		return nil, err
	}
	return cli, nil
}
