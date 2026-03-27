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

package main

import (
	"flag"
	"fmt"
	"log/slog"
	"os"
	"os/signal"
	"syscall"

	"mcp_server_mobile_use/internal/mobile_use/server"
)

var (
	transport string
	port      string
)

func init() {
	// 同一组选项同时支持长参数和短参数，方便本地调试时少敲几个字符。
	flag.StringVar(&transport, "transport", "stdio", "transport type (stdio,sse,streamable-http)")
	flag.StringVar(&transport, "t", "stdio", "transport type (stdio,sse,streamable-http)")
	flag.StringVar(&port, "port", "8080", "mcp server port while serve transport is sse mode")
	flag.StringVar(&port, "p", "8080", "mcp server port while serve transport is sse mode")
}

func main() {
	flag.Parse()
	slog.Info("transport", "transport", transport, "port", port)
	s := server.NewMobileUseServer()

	// 监听进程退出信号，保证 Ctrl+C 或容器停止时能有机会做优雅关闭。
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)

	// Channel to receive server errors
	errCh := make(chan error, 1)

	// transport 决定 MCP 服务通过哪种方式对外暴露：
	// stdio 常用于本地进程集成，
	// sse 和 streamable-http 更适合网络服务形式。
	switch transport {
	case "stdio":
		if err := s.StartStdio(); err != nil {
			slog.Error("Failed to start stdio server", "error", err)
			os.Exit(1)
		}
	case "sse":
		// SSE 模式下既要监听端口，也要告诉 MCP server 自己的 base URL。
		baseUrl := fmt.Sprintf(":%s", port)
		if err := s.StartSSEWithServer(fmt.Sprintf(":%s", port), baseUrl); err != nil {
			slog.Error("Failed to start SSE server", "error", err)
			os.Exit(1)
		}
	case "streamable-http":
		if err := s.StartStreamableHTTPServer(fmt.Sprintf(":%s", port)); err != nil {
			slog.Error("Failed to start streamable-http server", "error", err)
			os.Exit(1)
		}
	default:
		slog.Error("Invalid transport", "transport", transport)
		os.Exit(1)
	}

	// WaitForDone 会在服务自然退出或被关闭时返回。
	go func() {
		if err := s.WaitForDone(); err != nil {
			errCh <- err
		} else {
			// Server completed naturally (esp. in stdio mode)
			errCh <- nil
		}
	}()

	// 主 goroutine 在这里等待两类事件：
	// 1. 收到操作系统信号；
	// 2. 服务端自身已经结束。
	select {
	case sig := <-sigCh:
		slog.Info("Received signal, shutting down gracefully", "signal", sig)
		s.Shutdown()
		slog.Info("Server shutdown complete")
	case err := <-errCh:
		if err != nil {
			slog.Error("Server error", "error", err)
			os.Exit(1)
		} else {
			slog.Info("Server completed successfully")
		}
	}
}
