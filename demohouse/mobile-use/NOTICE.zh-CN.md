# 第三方依赖声明

[English](NOTICE.md) | 简体中文

本文档用于说明本项目中包含的第三方组件及其许可证信息。中文版本在不改变原意的前提下补充了说明性描述，便于在做合规审查、二次分发或内部归档时快速定位依赖来源。

## OpenAI Python Library

本产品包含由 OpenAI 开发的软件组件：

- 官网：`https://openai.com/`
- 源码仓库：`https://github.com/openai/openai-python`
- 版权声明：Copyright (c) 2020 OpenAI
- 许可证：Apache License 2.0

原文许可证说明如下：

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

补充说明：

- 该段许可证原文建议保留英文，以避免法律表述在翻译过程中发生歧义。
- 如需对外分发或做更严格的许可证审计，建议同时保留上游仓库中的 `LICENSE` 文件原文。

## 其他第三方依赖

以下依赖按许可证类型分类列出，便于快速确认项目的开源合规边界。

### MIT License 许可组件

以下库使用 MIT License：

- **FastAPI** - Copyright (c) 2018 Sebastián Ramírez
- **LangChain** - Copyright (c) 2022 LangChain Inc.
- **LangGraph** - Copyright (c) 2023 LangChain Inc.
- **Pydantic** - Copyright (c) 2017 Samuel Colvin
- **Next.js** - Copyright (c) 2016-present Vercel, Inc.
- **React** - Copyright (c) Facebook, Inc. and its affiliates
- **Tailwind CSS** - Copyright (c) Tailwind Labs, Inc.

MIT License 文本可参考：

`https://opensource.org/licenses/MIT`

### BSD 许可组件

- **Uvicorn** - BSD-3-Clause License
- **HttpX** - BSD-3-Clause License

### 其他 Apache 2.0 许可组件

- **Volcengine SDK** - Apache License 2.0

## 合规使用建议

- 若你在企业内部使用本项目，通常应结合依赖锁文件和实际构建产物再次核对许可证覆盖范围。
- 若你准备对外发布衍生应用，建议补充一份更完整的 SBOM 或依赖清单，而不仅依赖本说明文件。
- 当上游依赖版本发生升级时，应同步检查许可证是否有变化。

## 说明

完整许可证文本与版权声明，请以各第三方项目仓库中的 `LICENSE` 文件或官方发布信息为准。本文档更适合作为当前仓库的阅读入口和索引，而不是法律意义上的唯一依据。
