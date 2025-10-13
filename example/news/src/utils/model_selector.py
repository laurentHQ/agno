#!/usr/bin/env python3
"""
Model Selector Utility
Reusable component for multi-model AI selection across agents
"""

from dataclasses import dataclass
from enum import Enum
import os
from typing import Any

# Import base Agent class
try:
    from agno.agent import Agent
    from agno.models.anthropic import Claude

    AGNO_AVAILABLE = True
except ImportError:
    AGNO_AVAILABLE = False

# Model imports with error handling
try:
    from agno.models.openai import OpenAIChat

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from agno.models.google import Gemini

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class ModelType(Enum):
    """Supported AI model types"""

    CLAUDE = "claude"
    OPENAI = "openai"
    GEMINI = "gemini"


@dataclass
class ModelConfig:
    """Configuration for an AI model"""

    name: str
    display_name: str
    model_id: str
    env_key: str
    package_required: str | None = None
    description: str = ""
    is_default: bool = False


class ModelRegistry:
    """Registry of available AI models with their configurations"""

    MODELS = {
        ModelType.CLAUDE: ModelConfig(
            name="claude",
            display_name="Claude 4.5 Sonnet (Anthropic)",
            model_id="claude-sonnet-4-5",
            env_key="ANTHROPIC_API_KEY",
            description="Alternative, most stable and reliable",
        ),
        ModelType.OPENAI: ModelConfig(
            name="openai",
            display_name="GPT-5 Mini (OpenAI)",
            model_id="gpt-5-mini",
            env_key="OPENAI_API_KEY",
            package_required="openai",
            description="Default, requires OpenAI API key",
            is_default=True,
        ),
        ModelType.GEMINI: ModelConfig(
            name="gemini",
            display_name="Gemini 2.5 Flash (Google)",
            model_id="gemini-2.5-flash",
            env_key="GOOGLE_API_KEY",
            package_required="google-genai",
            description="Alternative, requires Google API key",
        ),
    }

    @classmethod
    def get_model_config(cls, model_type: ModelType) -> ModelConfig:
        """Get configuration for a specific model type"""
        return cls.MODELS[model_type]

    @classmethod
    def get_all_models(cls) -> dict[ModelType, ModelConfig]:
        """Get all model configurations"""
        return cls.MODELS.copy()


class ModelAvailability:
    """Checks model availability based on packages and API keys"""

    @staticmethod
    def check_package_availability() -> dict[ModelType, bool]:
        """Check which model packages are available"""
        return {
            ModelType.CLAUDE: True,  # Always available with agno
            ModelType.OPENAI: OPENAI_AVAILABLE,
            ModelType.GEMINI: GEMINI_AVAILABLE,
        }

    @staticmethod
    def check_api_key_availability() -> dict[ModelType, bool]:
        """Check which API keys are available"""
        registry = ModelRegistry()
        availability = {}

        for model_type, config in registry.get_all_models().items():
            availability[model_type] = bool(os.getenv(config.env_key))

        return availability

    @staticmethod
    def get_available_models() -> list[ModelType]:
        """Get list of fully available models (package + API key)"""
        package_availability = ModelAvailability.check_package_availability()
        api_key_availability = ModelAvailability.check_api_key_availability()

        available = []
        for model_type in ModelType:
            if package_availability.get(model_type, False) and api_key_availability.get(
                model_type, False
            ):
                available.append(model_type)

        return available

    @staticmethod
    def get_model_status() -> dict[ModelType, dict[str, bool]]:
        """Get detailed status for all models"""
        package_availability = ModelAvailability.check_package_availability()
        api_key_availability = ModelAvailability.check_api_key_availability()

        status = {}
        for model_type in ModelType:
            status[model_type] = {
                "package_available": package_availability.get(model_type, False),
                "api_key_available": api_key_availability.get(model_type, False),
                "fully_available": (
                    package_availability.get(model_type, False)
                    and api_key_availability.get(model_type, False)
                ),
            }

        return status


class ModelSelector:
    """Interactive model selection utility"""

    def __init__(self, title: str = "Choose AI Model", show_descriptions: bool = True):
        """
        Initialize model selector

        Args:
            title: Title to display for model selection
            show_descriptions: Whether to show model descriptions
        """
        self.title = title
        self.show_descriptions = show_descriptions
        self.registry = ModelRegistry()
        self.availability = ModelAvailability()

    def display_available_models(self) -> dict[str, ModelType]:
        """
        Display available models and return choice mapping

        Returns:
            Dictionary mapping choice numbers to model types
        """
        print(f"🤖 {self.title}:")

        model_status = self.availability.get_model_status()
        choice_mapping = {}
        option_num = 1

        # First show fully available models
        for model_type in ModelType:
            config = self.registry.get_model_config(model_type)
            status = model_status[model_type]

            if status["fully_available"]:
                display_text = f"  {option_num}. {config.display_name}"
                if config.is_default:
                    display_text += " - Default"
                if self.show_descriptions:
                    display_text += f" ({config.description})"

                print(display_text)
                choice_mapping[str(option_num)] = model_type
                option_num += 1

        # Then show unavailable models with reasons
        print()
        for model_type in ModelType:
            config = self.registry.get_model_config(model_type)
            status = model_status[model_type]

            if not status["fully_available"]:
                reasons = []
                if not status["package_available"]:
                    if config.package_required:
                        reasons.append(f"install {config.package_required} package")
                    else:
                        reasons.append("package not available")

                if not status["api_key_available"]:
                    reasons.append(f"set {config.env_key}")

                reason_text = " and ".join(reasons)
                print(f"  ⚠️  {config.display_name} not available ({reason_text})")

        return choice_mapping

    def get_user_choice(self, choice_mapping: dict[str, ModelType]) -> ModelType:
        """
        Get user's model choice

        Args:
            choice_mapping: Mapping of choice numbers to model types

        Returns:
            Selected model type
        """
        if not choice_mapping:
            print("❌ No models available!")
            raise RuntimeError("No AI models available")

        max_choice = len(choice_mapping)
        default_model = self._get_default_model(choice_mapping)

        prompt = f"\nEnter your choice (1-{max_choice}"
        if default_model:
            default_config = self.registry.get_model_config(default_model)
            prompt += f", or press Enter for {default_config.display_name}"
        prompt += "): "

        try:
            choice = input(prompt).strip()

            # Handle empty input (default)
            if not choice and default_model:
                return default_model

            # Handle valid choice
            if choice in choice_mapping:
                return choice_mapping[choice]

            # Invalid choice
            print(f"❌ Invalid choice: {choice}")
            if default_model:
                print(
                    f"💡 Using default: {self.registry.get_model_config(default_model).display_name}"
                )
                return default_model
            return list(choice_mapping.values())[0]  # First available

        except EOFError:
            # Handle EOF (e.g., when piping input)
            if default_model:
                return default_model
            return list(choice_mapping.values())[0]  # First available

    def _get_default_model(self, choice_mapping: dict[str, ModelType]) -> ModelType | None:
        """Get the default model from available choices"""
        for model_type in choice_mapping.values():
            config = self.registry.get_model_config(model_type)
            if config.is_default:
                return model_type
        return None

    def select_model(self) -> ModelType:
        """
        Full interactive model selection process

        Returns:
            Selected model type
        """
        choice_mapping = self.display_available_models()
        return self.get_user_choice(choice_mapping)


class ModelFactory:
    """Factory for creating AI model instances"""

    @staticmethod
    def create_model(model_type: ModelType) -> Any:
        """
        Create an AI model instance

        Args:
            model_type: Type of model to create

        Returns:
            AI model instance

        Raises:
            RuntimeError: If model cannot be created
        """
        if not AGNO_AVAILABLE:
            raise RuntimeError("Agno framework not available")

        registry = ModelRegistry()
        config = registry.get_model_config(model_type)

        # Check availability
        status = ModelAvailability.get_model_status()[model_type]
        if not status["fully_available"]:
            missing = []
            if not status["package_available"]:
                missing.append(f"package {config.package_required}")
            if not status["api_key_available"]:
                missing.append(f"API key {config.env_key}")

            raise RuntimeError(f"Cannot create {config.display_name}: missing {', '.join(missing)}")

        # Create model instance
        if model_type == ModelType.CLAUDE:
            return Claude(id=config.model_id)
        if model_type == ModelType.OPENAI:
            return OpenAIChat(id=config.model_id)
        if model_type == ModelType.GEMINI:
            return Gemini(id=config.model_id)
        raise RuntimeError(f"Unknown model type: {model_type}")


class AgentBuilder:
    """Builder for creating agents with model selection"""

    def __init__(self, tools: list[Any], instructions: str, markdown: bool = True):
        """
        Initialize agent builder

        Args:
            tools: List of tools for the agent
            instructions: Agent instructions
            markdown: Whether to enable markdown
        """
        self.tools = tools
        self.instructions = instructions
        self.markdown = markdown

    def build_with_model_selection(
        self, title: str = "Choose AI Model", show_descriptions: bool = True
    ) -> Agent:
        """
        Build agent with interactive model selection

        Args:
            title: Title for model selection
            show_descriptions: Whether to show model descriptions

        Returns:
            Configured agent
        """
        selector = ModelSelector(title=title, show_descriptions=show_descriptions)
        model_type = selector.select_model()
        model = ModelFactory.create_model(model_type)

        return Agent(
            model=model, tools=self.tools, instructions=self.instructions, markdown=self.markdown
        )

    def build_with_model_type(self, model_type: ModelType) -> Agent:
        """
        Build agent with specific model type

        Args:
            model_type: Type of model to use

        Returns:
            Configured agent
        """
        model = ModelFactory.create_model(model_type)

        return Agent(
            model=model, tools=self.tools, instructions=self.instructions, markdown=self.markdown
        )

    def build_with_model_name(self, model_name: str) -> Agent:
        """
        Build agent with model name string

        Args:
            model_name: Name of model ("claude", "openai", "gemini")

        Returns:
            Configured agent
        """
        try:
            model_type = ModelType(model_name.lower())
            return self.build_with_model_type(model_type)
        except ValueError:
            registry = ModelRegistry()
            default_config = registry.get_model_config(ModelType.CLAUDE)
            print(f"⚠️  Unknown model: {model_name}, using default ({default_config.display_name})")
            return self.build_with_model_type(ModelType.CLAUDE)


# Convenience functions for backward compatibility
def create_model_from_choice(model_choice: str) -> Any:
    """
    Create model from choice string (backward compatibility)

    Args:
        model_choice: Model choice string

    Returns:
        AI model instance
    """
    try:
        model_type = ModelType(model_choice.lower())
        return ModelFactory.create_model(model_type)
    except ValueError:
        return ModelFactory.create_model(ModelType.CLAUDE)


def get_model_selection_info() -> dict[str, Any]:
    """
    Get comprehensive model selection information

    Returns:
        Dictionary with model availability and configuration info
    """
    registry = ModelRegistry()
    availability = ModelAvailability()

    return {
        "models": registry.get_all_models(),
        "availability": availability.get_model_status(),
        "available_models": availability.get_available_models(),
        "package_availability": availability.check_package_availability(),
        "api_key_availability": availability.check_api_key_availability(),
    }


def interactive_model_selection(title: str = "Choose AI Model") -> ModelType:
    """
    Simple function for interactive model selection

    Args:
        title: Title to display

    Returns:
        Selected model type
    """
    selector = ModelSelector(title=title)
    return selector.select_model()


if __name__ == "__main__":
    # Demo usage
    print("🚀 Model Selector Demo")
    print("=" * 30)

    # Show model info
    info = get_model_selection_info()
    print("Available models:")
    for model_type in ModelType:
        config = info["models"][model_type]
        status = info["availability"][model_type]
        print(f"  {config.display_name}: {'✅' if status['fully_available'] else '❌'}")

    print("\n" + "=" * 30)

    # Interactive selection demo
    try:
        selected = interactive_model_selection("Demo Model Selection")
        config = ModelRegistry.get_model_config(selected)
        print(f"✅ Selected: {config.display_name}")
    except Exception as e:
        print(f"❌ Error: {e}")
