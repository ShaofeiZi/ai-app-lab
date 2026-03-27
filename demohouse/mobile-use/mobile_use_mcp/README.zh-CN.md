# 火山引擎云手机（ACEP）- Mobile Use MCP Server

[English](README_en.md) | 简体中文

## 产品说明

**OS Agent - Mobile Use** 是基于火山引擎云手机（ACEP）与方舟大模型能力构建的通用 AI Agent 方案，主要用于在 Android 移动环境中完成开放式自动化任务。

**Mobile Use MCP Server** 则是这套方案中的工具服务层。它预置了 Agent 在移动端任务中常用的云手机操作能力，并以标准 MCP 协议对外暴露，方便集成到自动化平台、工作流编排系统或自定义 Agent Runtime 中。

- **版本**：`v0.0.1`
- **分类**：视频云、云手机
- **标签**：`OS-Agent`、`Cloud Phone`、`Mobile`
- **补充说明**：该工具集基于 MCP（Model Context Protocol）实现，核心价值在于把底层云手机能力封装为标准化 Tool 接口，降低上层 Agent 集成成本。

## MCP Tools

### 工具列表

| Tool Name | 说明 |
| --- | --- |
| `take_screenshot` | 获取云手机屏幕截图 |
| `text_input` | 向云手机输入文本 |
| `tap` | 点击指定坐标 `[x, y]` |
| `swipe` | 执行滑动操作 |
| `home` | 返回主屏幕 |
| `back` | 返回上一个页面 |
| `menu` | 打开菜单页面 |
| `autoinstall_app` | 自动下载并安装应用 |
| `launch_app` | 启动应用 |
| `close_app` | 关闭正在运行的应用 |
| `list_apps` | 列出已安装应用 |

### 工具详细说明

### 1. `take_screenshot`

**说明**：对云手机当前屏幕截图，并返回截图地址与屏幕尺寸信息。

**输入参数**：

```json
{
  "type": "object",
  "properties": {}
}
```

**输出示例**：

```json
{
  "result": {
    "screenshot_url": "Screenshot download URL",
    "width": 1080,
    "height": 1920
  }
}
```

### 2. `text_input`

**说明**：向云手机当前输入焦点位置输入指定文本。

**输入参数**：

```json
{
  "type": "object",
  "properties": {
    "text": {
      "description": "The text to input",
      "type": "string"
    }
  },
  "required": [
    "text"
  ]
}
```

**输出示例**：

```json
{
  "result": "Input text successfully"
}
```

### 3. `tap`

**说明**：在屏幕指定坐标执行点击。

**输入参数**：

```json
{
  "type": "object",
  "properties": {
    "x": {
      "description": "The x coordinate of the tap point",
      "type": "number"
    },
    "y": {
      "description": "The y coordinate of the tap point",
      "type": "number"
    }
  },
  "required": [
    "x",
    "y"
  ]
}
```

**输出示例**：

```json
{
  "result": "Tap the screen successfully"
}
```

### 4. `swipe`

**说明**：执行滑动手势，默认持续时间为 `300ms`。

**输入参数**：

```json
{
  "type": "object",
  "properties": {
    "from_x": {
      "description": "The x coordinate of the start point",
      "type": "number"
    },
    "from_y": {
      "description": "The y coordinate of the start point",
      "type": "number"
    },
    "to_x": {
      "description": "The x coordinate of the end point",
      "type": "number"
    },
    "to_y": {
      "description": "The y coordinate of the end point",
      "type": "number"
    }
  },
  "required": [
    "from_x",
    "from_y",
    "to_x",
    "to_y"
  ]
}
```

**输出示例**：

```json
{
  "result": "Swipe the screen successfully"
}
```

### 5. `home`

**说明**：模拟按下 Home 键。

**输入参数**：

```json
{
  "type": "object",
  "properties": {}
}
```

**输出示例**：

```json
{
  "result": "Go home successfully"
}
```

### 6. `back`

**说明**：模拟按下返回键。

**输入参数**：

```json
{
  "type": "object",
  "properties": {}
}
```

**输出示例**：

```json
{
  "result": "Back successfully"
}
```

### 7. `menu`

**说明**：模拟按下菜单键。

**输入参数**：

```json
{
  "type": "object",
  "properties": {}
}
```

**输出示例**：

```json
{
  "result": "Open the Menu successfully"
}
```

### 8. `autoinstall_app`

**说明**：下载指定应用并在云手机中自动安装。

**输入参数**：

```json
{
  "type": "object",
  "properties": {
    "app_name": {
      "description": "The app name to be uploaded"
    },
    "download_url": {
      "description": "The download url of the app",
      "type": "string"
    }
  },
  "required": [
    "download_url",
    "app_name"
  ]
}
```

**输出示例**：

```json
{
  "result": "Apk is being installed"
}
```

### 9. `launch_app`

**说明**：按包名启动应用。

**输入参数**：

```json
{
  "type": "object",
  "properties": {
    "package_name": {
      "description": "The package name of apk",
      "type": "string"
    }
  },
  "required": [
    "package_name"
  ]
}
```

**输出示例**：

```json
{
  "result": "Launch app successfully"
}
```

### 10. `close_app`

**说明**：关闭正在运行的应用。

**输入参数**：

```json
{
  "type": "object",
  "properties": {
    "package_name": {
      "description": "The package name of apk",
      "type": "string"
    }
  },
  "required": [
    "package_name"
  ]
}
```

**输出示例**：

```json
{
  "result": "Close app successfully"
}
```

### 11. `list_apps`

**说明**：列出云手机中已安装的应用。

**输入参数**：

```json
{
  "type": "object",
  "properties": {}
}
```

**输出示例**：

```json
{
  "result": {
    "AppList": [
      {
        "app_id": "",
        "app_name": "抖音",
        "app_status": "undeployed",
        "package_name": "com.ss.android.ugc.aweme"
      }
    ]
  }
}
```

## 支持的平台

当前文档列出的接入对象包括：

- Ark
- Trae
- Python
- Cursor

这里更适合把它理解为“可对接的使用环境或开发入口”，而不是严格意义上的唯一运行平台。

## 产品开通

- [Volcano Engine Cloud Phone](https://www.volcengine.com/product/ACEP)
  需要提前确认是否具备兼容 MCP 的云手机资源、业务 ID 以及设备实例。
- [Volcano Engine TOS](https://www.volcengine.com/product/TOS)
  用于相关对象存储能力。
- [Volcano Engine ARK](https://www.volcengine.com/product/ark)
  用于模型能力接入。

若你不确定资源侧要求，建议先联系对应的产品或交付同学确认。

## 快速开始

### 1. 构建

确保已安装 Go `1.23+`：

```bash
./build.sh
```

构建完成后，二进制产物会位于 `output/` 目录中：

- `output/mobile_use_mcp`：MCP Server 主程序
- `output/cap_tos` 等：辅助工具程序

### 2. 本地部署

MCP Server 支持三种启动模式：

- `stdio`
- `streamable-http`
- `sse`

#### 2.1 `stdio` 模式

适合通过标准输入输出与 MCP Server 通信的场景。启动前需要设置以下环境变量：

| Variable Name | 说明 |
| --- | --- |
| `ACEP_ACCESS_KEY` | 云手机 Access Key |
| `ACEP_SECRET_KEY` | 云手机 Secret Key |
| `ACEP_PRODUCT_ID` | 云手机业务 ID |
| `ACEP_DEVICE_ID` | 云手机设备 ID |
| `TOS_ACCESS_KEY` | TOS Access Key |
| `TOS_SECRET_KEY` | TOS Secret Key |
| `ACEP_TOS_BUCKET` | TOS Bucket 名称 |
| `ACEP_TOS_REGION` | TOS Region |
| `ACEP_TOS_ENDPOINT` | TOS Endpoint |

**Go 示例：通过 `stdio` 连接 MCP Server 并调用 `take_screenshot`**

```go
// stdio method call example
func main() {
    ctx := context.Background()
    // Path to the MCP Server executable file
    cmd := "./output/mobile_use_mcp"
    // Environment variables (replace with actual values)
    env := []string{
        "ACEP_ACCESS_KEY=<your-access-key>",
        "ACEP_SECRET_KEY=<your-secret-key>",
        "ACEP_PRODUCT_ID=<your-product-id>",
        "ACEP_DEVICE_ID=<your-device-id>",
        "TOS_ACCESS_KEY=<tos-access-key>",
        "TOS_SECRET_KEY=<tos-secret-key>",
        "ACEP_TOS_BUCKET=<tos-bucket>",
        "ACEP_TOS_REGION=<tos-region>",
        "ACEP_TOS_ENDPOINT=<tos-endpoint>",
    }
    args := []string{"--transport", "stdio"}
    cli, err := mobile_use_client.NewMobileUseStdioClient(ctx, cmd, env, args...)
    if err != nil {
        log.Fatal(err)
    }
    defer cli.Close()
    req := mcp.CallToolRequest{}
    req.Params.Name = "take_screenshot"
    req.Params.Arguments = map[string]interface{}{}
    result, err := cli.CallTool(ctx, req)
    if err != nil {
        log.Fatal(err)
    }
    log.Println("Screenshot result:", result)
}
```

> 说明：请将示例中的 `<your-access-key>`、`<your-secret-key>`、`<your-product-id>`、`<your-device-id>`、`<tos-access-key>`、`<tos-secret-key>`、`<tos-bucket>`、`<tos-region>`、`<tos-endpoint>` 替换为真实值。调用其他工具时，只需要修改 `req.Params.Name` 和 `Arguments`。

#### 2.2 HTTP 模式

适合通过 HTTP 与 MCP Server 通信的场景。

**启动命令：**

```bash
./output/mobile_use_mcp --transport (sse/streamable-http) --port 8080
```

- `--transport` / `-t`：指定启动模式，支持 `stdio`、`sse` 和 `streamable-http`，默认 `stdio`
- `--port` / `-p`：指定 HTTP 监听端口，仅在 `sse` 与 `streamable-http` 模式下生效，默认 `8080`

**SSE 请求头字段说明：**

| Header Name | 说明 |
| --- | --- |
| `Authorization` | 认证 Token |
| `X-ACEP-ProductId` | 云手机业务 ID |
| `X-ACEP-DeviceId` | 云手机实例 ID |
| `X-ACEP-TosBucket` | TOS Bucket 名称 |
| `X-ACEP-TosRegion` | TOS Region |
| `X-ACEP-TosEndpoint` | TOS Endpoint |
| `X-ACEP-TosSession` | TOS Session Token |

**SSE 模式 `AuthInfo` 字段说明：**

| Field Name | Type | 说明 |
| --- | --- | --- |
| `AccessKeyId` | string | 火山引擎 Access Key ID，必填 |
| `SecretAccessKey` | string | 火山引擎 Secret Access Key，必填 |
| `CurrentTime` | string | 当前时间，RFC3339 格式，必填 |
| `ExpiredTime` | string | 过期时间，RFC3339 格式，必填 |
| `SessionToken` | string | 临时 Token，可选 |

```go
// Token generation
// Assuming AuthInfo struct is defined as follows
type AuthInfo struct {
	AccessKeyId     string `json:"AccessKeyId"`
	SecretAccessKey string `json:"SecretAccessKey"`
	CurrentTime     string `json:"CurrentTime"`
	ExpiredTime     string `json:"ExpiredTime"`
	SessionToken    string `json:"SessionToken"`
}

func GenerateAuthToken(accessKey, secretKey, sessionToken string) (string, error) {
	now := time.Now().Format(time.RFC3339)
	expired := time.Now().Add(24 * time.Hour).Format(time.RFC3339)
	auth := &AuthInfo{
		AccessKeyId:     accessKey,
		SecretAccessKey: secretKey,
		CurrentTime:     now,
		ExpiredTime:     expired,
		SessionToken:    sessionToken,
	}
	authBytes, err := json.Marshal(auth)
	if err != nil {
		return "", err
	}
	authToken := base64.StdEncoding.EncodeToString(authBytes)
	return authToken, nil
}
```

**Go 示例：通过 SSE 调用 `take_screenshot`**

```go
// SSE method call example
func main() {
    ctx := context.Background()
    baseUrl := "http://0.0.0.0:8080/sse"
    cli, err := mobile_use_client.NewMobileUseSSEClient(ctx, baseUrl, map[string]string{
        "Authorization":      authToken,             // Authentication token
        "X-ACEP-ProductId":   "<your-product-id>",   // Cloud Phone Business ID
        "X-ACEP-DeviceId":    "<your-device-id>",    // Cloud Phone Instance ID
        "X-ACEP-TosBucket":   "<your-tos-bucket>",   // TOS Bucket Name
        "X-ACEP-TosRegion":   "<your-tos-region>",   // TOS Region
        "X-ACEP-TosEndpoint": "<your-tos-endpoint>", // TOS Endpoint
        "X-ACEP-TosSession":  "",
    })
    if err != nil {
        log.Fatal(err)
    }
    defer cli.Close()
    req := mcp.CallToolRequest{}
    req.Params.Name = "take_screenshot"
    req.Params.Arguments = map[string]interface{}{}
    result, err := cli.CallTool(ctx, req)
    if err != nil {
        log.Fatal(err)
    }
    log.Println("Screenshot result:", result)
}
```

**Go 示例：通过 `streamable-http` 调用 `take_screenshot`**

```go
func main() {
    ctx := context.Background()
    baseUrl := "http://0.0.0.0:8080/mcp"
    cli, err := mobile_use_client.NewMobileUseStreamableHTTPClient(ctx, baseUrl, map[string]string{
        "Authorization":      authToken,             // Authentication token
        "X-ACEP-ProductId":   "<your-product-id>",   // Cloud Phone Business ID
        "X-ACEP-DeviceId":    "<your-device-id>",    // Cloud Phone Instance ID
        "X-ACEP-TosBucket":   "<your-tos-bucket>",   // TOS Bucket Name
        "X-ACEP-TosRegion":   "<your-tos-region>",   // TOS Region
        "X-ACEP-TosEndpoint": "<your-tos-endpoint>", // TOS Endpoint
        "X-ACEP-TosSession":  "",
    })
    if err != nil {
        log.Fatal(err)
    }
    defer cli.Close()
    req := mcp.CallToolRequest{}
    req.Params.Name = "take_screenshot"
    req.Params.Arguments = map[string]interface{}{}
    result, err := cli.CallTool(ctx, req)
    if err != nil {
        log.Fatal(err)
    }
    log.Println("Screenshot result:", result)
}
```

> 说明：请将 `<your-access-key>`、`<your-secret-key>`、`<your-product-id>`、`<your-device-id>` 等占位符替换为真实配置。调用其他工具时，同样只需修改工具名和参数。

### 3. 其他说明

- 服务启动后，可以通过任意兼容 MCP 协议的客户端与其通信。
- 如需查看具体接口细节和参数格式，请以工具文档或源码中的实现为准。
- 若你需要自定义构建参数或进行交叉编译，可以进一步查看 `build.sh`。

## License

`volcengine/mcp-server` 使用 MIT License。
