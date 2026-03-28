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

import uvicorn
import logging
from mobile_agent.config.settings import settings


# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    # main 是整个 Python 服务进程的启动入口。
    # 初学者可以把它理解成“先把启动参数打印出来，再把 Web 服务器真正跑起来”的总开关。
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.env}")
    logger.info(
        f"Server config: host={settings.server.host}, port={settings.server.port}"
    )

    # 这里交给 uvicorn 启动 FastAPI 应用。
    # "app:app" 的前一个 app 是文件名 `app.py`，
    # 后一个 app 是这个文件里导出的 FastAPI 实例对象。
    uvicorn.run("app:app", host=settings.server.host, port=settings.server.port)


if __name__ == "__main__":
    main()
