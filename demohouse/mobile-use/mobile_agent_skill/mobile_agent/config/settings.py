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

import os
import json
import re
import tomli
from pathlib import Path
from typing import Dict, Optional
from pydantic import BaseModel, Field, ValidationError
from pydantic_settings import BaseSettings
import logging
from dotenv import load_dotenv

# 启动时先把 .env 文件里的环境变量读进来。
# 这样本地开发时不需要把所有配置都写进系统环境变量。
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ROOT_DIR 用来把相对配置文件路径转换成仓库内的绝对位置。
ROOT_DIR = Path(__file__).parent.parent.parent

MOBILE_USE_MCP_NAME = "mobile"


class ServerConfig(BaseModel):
    """服务器配置"""

    host: str = "0.0.0.0"
    port: int = 8000


class LLMConfig(BaseModel):
    """LLM配置"""

    model: str = ""
    api_key: str = ""
    base_url: str = ""
    max_tokens: Optional[int] = None
    temperature: float = 0.0


class MCPConfig(BaseModel):
    """MCP配置"""

    name: str = ""
    url: str = ""
    headers: Dict[str, str] = Field(default_factory=dict, description="MCP请求头")


class MobileUseServiceConfig(BaseModel):
    url: str = Field(
        default_factory=lambda: os.environ.get(
            "MOBILE_USE_SERVICE_URL", "http://127.0.0.1:8001"
        )
    )
    timeout_seconds: float = Field(
        default_factory=lambda: float(
            os.environ.get("MOBILE_USE_SERVICE_TIMEOUT", "30")
        )
    )


class SkillPolicyConfig(BaseModel):
    allowlist: Optional[list[str]] = None
    denylist: list[str] = Field(default_factory=list)


class AgentConfig(BaseModel):
    name: str = ""
    modelKey: str = ""
    temperature: float = 0.0
    step_interval: int = 0.8
    action_wait_interval: int = 1
    max_steps: int = 256
    input_price_per_1k: float = 0
    output_price_per_1k: float = 0


class Settings(BaseSettings):
    """应用程序设置"""

    app_name: str = "Mobile Agent API"
    app_version: str = "0.1.0"
    # 这里保存的是 HTTP 服务本身的监听地址，而不是业务接口地址。
    server: ServerConfig = Field(
        default_factory=lambda: ServerConfig(
            host=os.environ.get("UVICORN_SERVER_HOST", "0.0.0.0"),
            port=int(os.environ.get("UVICORN_SERVER_PORT", "8000")),
        )
    )
    # env 主要用于区分开发 / 生产等运行环境。
    env: str = Field(default_factory=lambda: os.environ.get("ENV", "production"))
    config_path: Optional[str] = Field(default=None, description="配置文件路径")

    llms: Dict[str, LLMConfig] = Field(default_factory=dict, description="LLM配置")

    agents: Dict[str, AgentConfig] = Field(
        default_factory=dict, description="Agent配置"
    )

    mcp: MCPConfig = MCPConfig()

    mobile_use_mcp: MCPConfig = MCPConfig(
        name=MOBILE_USE_MCP_NAME,
        url="",
    )
    mobile_use_service: MobileUseServiceConfig = MobileUseServiceConfig()
    skill_policy: SkillPolicyConfig = SkillPolicyConfig()

    class Config:
        env_prefix = "MOBILE_"  # 环境变量前缀
        case_sensitive = False

    def _replace_env_vars(self, config_data):
        """递归替换配置文件中的环境变量占位符。

        例如 TOML 里写 `${ARK_API_KEY}`，
        加载后会自动替换成当前进程环境变量里的真实值。
        这样配置文件可以提交模板，而敏感信息仍然放在环境变量里。
        """
        if isinstance(config_data, dict):
            return {
                key: self._replace_env_vars(value) for key, value in config_data.items()
            }
        elif isinstance(config_data, list):
            return [self._replace_env_vars(item) for item in config_data]
        elif isinstance(config_data, str):
            # 匹配 ${ENV_VAR_NAME} 格式
            pattern = r"\$\{([^}]+)\}"

            def replace_match(match):
                env_var = match.group(1)
                return os.environ.get(
                    env_var, match.group(0)
                )  # 如果环境变量不存在，保持原样

            return re.sub(pattern, replace_match, config_data)
        else:
            return config_data

    def load_from_file(self, config_file: Optional[str] = None) -> "Settings":
        """从文件加载配置"""
        file_path = config_file or self.config_path

        if not file_path:
            logger.info("No config file specified, using default settings")
            return self

        file_path = Path(file_path)
        if not file_path.is_absolute():
            file_path = ROOT_DIR / file_path

        if not file_path.exists():
            logger.warning(f"Config file {file_path} not found, using default settings")
            return self

        try:
            if file_path.suffix == ".json":
                with open(file_path, "r") as f:
                    config_data = json.load(f)
            elif file_path.suffix == ".toml":
                with open(file_path, "rb") as f:
                    config_data = tomli.load(f)
            else:
                logger.error(f"Unsupported config file format: {file_path.suffix}")
                return self

                # 新增：替换环境变量
            config_data = self._replace_env_vars(config_data)

            # 这里不是直接把整个 Settings 对象替换掉，
            # 而是把配置文件里的字段逐个合并到当前实例上。
            # 这样环境变量中已经给出的默认值仍然可以保留。
            for key, value in config_data.items():
                if hasattr(self, key):
                    if isinstance(value, dict) and isinstance(
                        getattr(self, key), BaseModel
                    ):
                        current_config = getattr(self, key)
                        for sub_key, sub_value in value.items():
                            if hasattr(current_config, sub_key):
                                setattr(current_config, sub_key, sub_value)
                    else:
                        setattr(self, key, value)

            logger.info(f"Loaded config from {file_path}")
        except (json.JSONDecodeError, tomli.TOMLDecodeError, ValidationError) as e:
            logger.error(f"Failed to load config from {file_path}: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error when loading config: {e}")

        return self

    def apply_env_overrides(self) -> "Settings":
        """让显式传入的运行时环境变量覆盖配置文件默认值。"""
        self.server.host = os.environ.get("UVICORN_SERVER_HOST", self.server.host)
        self.server.port = int(
            os.environ.get("UVICORN_SERVER_PORT", str(self.server.port))
        )
        self.env = os.environ.get("ENV", self.env)
        self.mobile_use_mcp.url = os.environ.get(
            "MOBILE_USE_MCP_URL", self.mobile_use_mcp.url
        )
        self.mobile_use_service.url = os.environ.get(
            "MOBILE_USE_SERVICE_URL", self.mobile_use_service.url
        )
        self.mobile_use_service.timeout_seconds = float(
            os.environ.get(
                "MOBILE_USE_SERVICE_TIMEOUT",
                str(self.mobile_use_service.timeout_seconds),
            )
        )
        return self


# 整个服务通常只需要一份全局 settings，
# 各模块通过导入它或调用 get_settings() 来共享同一套配置。
settings = Settings()

# 配置优先级是：
# 1. `MOBILE_CONFIG_PATH` 指定的文件；
# 2. 仓库根目录下默认存在的 `config.toml`；
# 3. 如果都没有，就退回到类里的默认值和环境变量。
if os.environ.get("MOBILE_CONFIG_PATH"):
    settings.config_path = os.environ.get("MOBILE_CONFIG_PATH")
    settings = settings.load_from_file().apply_env_overrides()
else:
    # 自动查找项目根目录下的 config.json
    default_config_path = Path(__file__).parent.parent.parent / "config.toml"
    if default_config_path.exists():
        settings.config_path = str(default_config_path)
        settings = settings.load_from_file().apply_env_overrides()
    else:
        settings = settings.apply_env_overrides()


def get_settings() -> Settings:
    """获取全局设置实例"""
    return settings


_models_config = {key: model_config for key, model_config in settings.llms.items()}


def get_models() -> Dict[str, LLMConfig]:
    return _models_config


def get_model_config(model_key: str) -> LLMConfig:
    # settings 里的条目有可能已经是 LLMConfig，也可能还是原始 dict。
    # 这里统一转换成 LLMConfig，调用方就能拿到稳定的类型。
    models = get_models()
    if model_key in models:
        config_dict = models[model_key]
        if isinstance(config_dict, dict):
            return LLMConfig(**config_dict)
        return config_dict
    raise ValueError(f"Model {model_key} not found in settings")


_agents_config = {key: agent_config for key, agent_config in settings.agents.items()}


def get_agents() -> Dict[str, AgentConfig]:
    return _agents_config


def get_agent_config(agent_key: str) -> AgentConfig:
    agents = get_agents()
    if agent_key in agents:
        config_dict = agents[agent_key]
        if isinstance(config_dict, dict):
            return AgentConfig(**config_dict)
        return config_dict
    raise ValueError(f"Agent {agent_key} not found in settings")
