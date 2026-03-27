# Mobile Use Web

[English](README.md) | 简体中文

## 📁 模块简介

`web/` 是 Mobile Use 的前端界面层，基于 Next.js 构建。它的职责不只是“展示一个聊天框”，而是承接完整的任务输入、流式结果渲染、会话交互和云手机可视化反馈，因此它更像一个轻量的 Agent 控制台。

对于阅读仓库的人来说，这个目录最适合用来理解：

- 用户是如何输入任务的
- Agent 返回的流式消息如何被渲染
- 前后端 API 是如何衔接的
- 页面如何展示等待、执行中、超时等状态

## 🧱 项目结构

```text
src/
├── app/                    # Next.js App Router 入口
│   ├── api/                # API 路由处理器
│   ├── chat/               # 聊天页
│   ├── layout.tsx          # 根布局
│   ├── page.tsx            # 首页
│   └── globals.css         # 全局样式
├── components/             # 可复用 UI 组件
│   ├── ui/                 # 基础 UI 组件（shadcn/ui）
│   ├── chat/               # 聊天相关组件
│   ├── phone/              # 云手机/屏幕相关组件
│   ├── common/             # 通用组件
│   └── resize/             # 可伸缩面板组件
├── hooks/                  # 自定义 React Hooks
├── lib/                    # 工具库与基础能力封装
├── styles/                 # 附加样式
├── types/                  # TypeScript 类型定义
└── assets/                 # 静态资源
```

## 🚦 快速开始

### 前置要求

- Node.js >= 20
- npm 包管理器

如果你使用的是 `pnpm` 或 `yarn`，也可以自行调整命令，但仓库文档默认以 `npm` 为例。

### 安装与启动

1. **进入目录**

```bash
cd demohouse/mobile-use/web
```

2. **安装依赖**

```bash
npm install
```

3. **配置环境变量**

```bash
cp .env.example .env
```

然后编辑 `.env`，至少设置：

```env
CLOUD_AGENT_BASE_URL=http://localhost:8000/mobile-use/
```

该地址指向后端 Agent 服务入口。前端所有会话创建、消息流转与取消操作都依赖它。

4. **启动开发服务器**

```bash
npm run dev
```

5. **访问页面**

在浏览器中打开：

```text
http://localhost:8080?token=123456
```

这个 URL 里的 `token` 是示例环境中用于访问鉴权的查询参数。实际部署时，你可能会把这部分接入更完整的认证流程。

## 🏭 生产构建

```bash
# Build for production
npm run build

# Start production server
npm run start
```

通常在验证完开发模式后，再使用这两个命令检查生产构建是否正常。

## 🔧 配置项

### 环境变量

| 变量 | 含义 | 默认值 |
| --- | --- | --- |
| `CLOUD_AGENT_BASE_URL` | 后端 Agent 服务地址 | 必填 |

### Next.js 配置

项目当前使用 Next.js 的 standalone 输出模式，便于容器化部署：

```typescript
const nextConfig: NextConfig = {
  output: "standalone",
};
```

这意味着构建产物更适合被打包并在相对独立的运行环境中部署。

## 📌 阅读建议

- 想看页面入口与整体布局：优先查看 `src/app/`
- 想看聊天消息和执行状态如何渲染：优先查看 `src/components/chat/`
- 想看云手机区域与操作逻辑：优先查看 `src/components/phone/`
- 想看前端如何连接后端流式接口：优先查看 `src/lib/` 与 `src/hooks/`

## ✅ 适用场景

这个前端模块适合作为：

- Mobile Use 的官方演示界面
- 自定义业务控制台的起点
- 调试 Agent 行为的可视化工具
- 验证 SSE 消息结构与前端渲染逻辑的参考实现
