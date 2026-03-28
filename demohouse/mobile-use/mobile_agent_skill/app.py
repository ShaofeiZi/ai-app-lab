# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# Licensed under the 【火山方舟】原型应用软件自用许可协议
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at 
#     https://www.volcengine.com/docs/82379/1433703
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 导入配置
from mobile_agent.middleware.middleware import (
    ResponseMiddleware,
    AuthMiddleware,
)
from mobile_agent.config.settings import settings
from mobile_agent.routers.base import register_routers


# 这里把整个后端服务的“骨架”搭起来：
# 包括应用对象本身、中间件，以及所有业务路由。
app = FastAPI(
    title=settings.app_name,
    description="HTTP Server for Mobile Agent",
    version=settings.app_version,
)


@app.get("/health")
def health_check():
    # 给启动脚本和运维检查一个稳定、轻量的探活入口，
    # 避免只看端口监听就误判服务真的可用。
    return {"status": "ok", "service": settings.app_name, "env": settings.env}

# CORS 允许浏览器里的前端页面跨域访问这个后端接口。
# Demo 阶段这里放得比较宽松，方便本地开发和嵌入不同宿主环境。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 先统一响应格式，再做鉴权。
# 这样无论业务成功还是失败，前端看到的 JSON 结构都比较稳定。
app.add_middleware(ResponseMiddleware)
# 账户鉴权中间件会把账户信息挂到 request.state 上，
# 后面的路由处理函数就不需要自己重复读请求头了。
app.add_middleware(AuthMiddleware)

# 最后集中注册路由，把 session 和 agent 两组接口挂到应用上。
register_routers(app)
