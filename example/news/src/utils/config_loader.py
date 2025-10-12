#!/usr/bin/env python3
"""
Configuration Loader for Finance News AgentOS
Loads and validates configuration from YAML file
"""

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ModelConfig:
    """Model configuration"""

    model_id: str
    display_name: str
    temperature: float = 0.1
    max_tokens: int = 4000


@dataclass
class DatabaseConfig:
    """Database configuration"""

    type: str = "sqlite"
    sqlite_db_file: str = "finance_agent.db"
    sqlite_enable_history: bool = True
    postgresql_schema: str = "finance_agent"


@dataclass
class ServerConfig:
    """Server configuration"""

    host: str = "0.0.0.0"
    port: int = 8080
    reload: bool = False
    log_level: str = "info"
    title: str = "Finance News AgentOS"
    description: str = "Interactive web interface for Financial News and Market Analysis"


@dataclass
class AgentConfig:
    """Agent configuration"""

    name: str = "finance-news-agent"
    description: str = "Specialized Financial News and Market Analysis Agent"
    interactive: bool = False
    markdown: bool = True
    debug_mode: bool = False


@dataclass
class AgentOSConfig:
    """Complete AgentOS configuration"""

    primary_model: str
    models: dict[str, ModelConfig]
    database: DatabaseConfig
    server: ServerConfig
    agent: AgentConfig
    tools: dict[str, Any]
    features: dict[str, bool]


class ConfigLoader:
    """Configuration loader and validator"""

    def __init__(self, config_file: str | None = None):
        """Initialize config loader"""
        if config_file is None:
            # Default to config/agentos_config.yaml in project root
            current_dir = Path(__file__).parent.parent.parent  # Go up to project root
            self.config_file = current_dir / "config" / "agentos_config.yaml"
        else:
            self.config_file = Path(config_file)
        self._config_data: dict[str, Any] | None = None

    def load_config(self) -> AgentOSConfig:
        """Load and validate configuration"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")

        with open(self.config_file) as f:
            self._config_data = yaml.safe_load(f)

        return self._parse_config()

    def _parse_config(self) -> AgentOSConfig:
        """Parse configuration data into structured config"""
        data = self._config_data
        if data is None:
            data = {}

        # Parse model configurations
        models = {}
        model_data = data.get("model", {})
        primary_model = model_data.get("primary", "claude")

        for model_name in ["claude", "openai", "gemini"]:
            if model_name in model_data:
                model_info = model_data[model_name]
                models[model_name] = ModelConfig(
                    model_id=model_info.get("model_id", ""),
                    display_name=model_info.get("display_name", ""),
                    temperature=model_info.get("temperature", 0.1),
                    max_tokens=model_info.get("max_tokens", 4000),
                )

        # Parse database configuration
        db_data = data.get("database", {})
        database = DatabaseConfig(
            type=db_data.get("type", "sqlite"),
            sqlite_db_file=db_data.get("sqlite", {}).get("db_file", "finance_agent.db"),
            sqlite_enable_history=db_data.get("sqlite", {}).get("enable_history", True),
            postgresql_schema=db_data.get("postgresql", {}).get("schema", "finance_agent"),
        )

        # Parse server configuration
        server_data = data.get("server", {})
        server = ServerConfig(
            host=server_data.get("host", "0.0.0.0"),
            port=server_data.get("port", 8080),
            reload=server_data.get("reload", False),
            log_level=server_data.get("log_level", "info"),
            title=server_data.get("title", "Finance News AgentOS"),
            description=server_data.get(
                "description", "Interactive web interface for Financial News and Market Analysis"
            ),
        )

        # Parse agent configuration
        agent_data = data.get("agent", {})

        # DEBUG_MODE env variable overrides config file
        debug_mode = agent_data.get("debug_mode", False)
        if os.getenv("DEBUG_MODE"):
            debug_mode = os.getenv("DEBUG_MODE").lower() in ("true", "1", "yes", "on")

        agent = AgentConfig(
            name=agent_data.get("name", "finance-news-agent"),
            description=agent_data.get(
                "description", "Specialized Financial News and Market Analysis Agent"
            ),
            interactive=agent_data.get("interactive", False),
            markdown=agent_data.get("markdown", True),
            debug_mode=debug_mode,
        )

        # Parse tools and features
        tools = data.get("tools", {})
        features = data.get("features", {})

        return AgentOSConfig(
            primary_model=primary_model,
            models=models,
            database=database,
            server=server,
            agent=agent,
            tools=tools,
            features=features,
        )

    def get_model_choice(self) -> str:
        """Get the primary model choice"""
        config = self.load_config()
        return config.primary_model

    def get_model_config(self, model_name: str) -> ModelConfig | None:
        """Get configuration for a specific model"""
        config = self.load_config()
        return config.models.get(model_name)

    def validate_config(self) -> bool:
        """Validate configuration and check for required API keys"""
        try:
            config = self.load_config()

            # Check if primary model is valid
            if config.primary_model not in config.models:
                print(f"❌ Invalid primary model: {config.primary_model}")
                return False

            # Check API keys based on primary model
            model_to_env = {
                "claude": "ANTHROPIC_API_KEY",
                "openai": "OPENAI_API_KEY",
                "gemini": "GOOGLE_API_KEY",
            }

            required_key = model_to_env.get(config.primary_model)
            if required_key and not os.getenv(required_key):
                print(f"❌ Missing API key: {required_key} (required for {config.primary_model})")
                return False

            print(f"✅ Configuration valid - Primary model: {config.primary_model}")
            return True

        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
            return False

    def list_available_models(self) -> dict[str, str]:
        """List all available models and their display names"""
        config = self.load_config()
        return {name: model.display_name for name, model in config.models.items()}


def load_agentos_config(config_file: str | None = None) -> AgentOSConfig:
    """Convenience function to load AgentOS configuration"""
    loader = ConfigLoader(config_file)
    return loader.load_config()


def validate_agentos_config(config_file: str | None = None) -> bool:
    """Convenience function to validate AgentOS configuration"""
    loader = ConfigLoader(config_file)
    return loader.validate_config()


if __name__ == "__main__":
    # Test configuration loading
    try:
        loader = ConfigLoader()
        config = loader.load_config()

        print("🔧 Configuration loaded successfully!")
        print(f"Primary model: {config.primary_model}")
        print(f"Database type: {config.database.type}")
        print(f"Server port: {config.server.port}")

        # Validate configuration
        if loader.validate_config():
            print("✅ Configuration is valid!")
        else:
            print("❌ Configuration validation failed!")

        # List available models
        models = loader.list_available_models()
        print(f"Available models: {list(models.keys())}")

    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
