#!/usr/bin/env python3
"""
Model Configuration CLI for Finance News AgentOS
Interactive tool to configure AI models before running AgentOS
"""

import os
from pathlib import Path
import sys

import yaml

# Add paths for imports
current_dir = Path(__file__).parent.parent  # Points to src/
project_root = current_dir.parent  # Points to project root (example/news/)
sys.path.insert(0, str(current_dir / "utils"))

from config_loader import ConfigLoader, validate_agentos_config


def display_banner():
    """Display configuration banner"""
    print("=" * 60)
    print("🤖 Finance News AgentOS - Model Configuration")
    print("=" * 60)


def check_api_keys():
    """Check which API keys are available"""
    keys = {}
    keys["claude"] = bool(os.getenv("ANTHROPIC_API_KEY"))
    keys["openai"] = bool(os.getenv("OPENAI_API_KEY"))
    keys["gemini"] = bool(os.getenv("GOOGLE_API_KEY"))

    print("\n🔑 API Key Status:")
    for model, available in keys.items():
        status = "✅ Available" if available else "❌ Missing"
        print(f"  {model.capitalize()}: {status}")

    return keys


def display_current_config():
    """Display current configuration"""
    try:
        loader = ConfigLoader()
        config = loader.load_config()

        print("\n📋 Current Configuration:")
        print(f"  Primary Model: {config.primary_model}")
        print(f"  Database: {config.database.type}")
        print(f"  Server Port: {config.server.port}")

        model_config = config.models.get(config.primary_model)
        if model_config:
            print(f"  Model Details: {model_config.display_name}")
            print(f"  Temperature: {model_config.temperature}")

    except Exception as e:
        print(f"⚠️  Could not load current config: {e}")


def select_model(available_keys):
    """Interactive model selection"""
    available_models = [model for model, available in available_keys.items() if available]

    if not available_models:
        print("\n❌ No API keys found! Please set up at least one API key in your .env file:")
        print("  - ANTHROPIC_API_KEY for Claude")
        print("  - OPENAI_API_KEY for OpenAI GPT")
        print("  - GOOGLE_API_KEY for Gemini")
        return None

    print("\n🤖 Available Models:")
    for i, model in enumerate(available_models, 1):
        print(f"  {i}. {model.capitalize()}")

    while True:
        try:
            choice = input(f"\nSelect model (1-{len(available_models)}) or 'q' to quit: ").strip()

            if choice.lower() == "q":
                return None

            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(available_models):
                return available_models[choice_idx]
            print("❌ Invalid choice. Please try again.")

        except ValueError:
            print("❌ Please enter a valid number.")


def update_config(new_model):
    """Update configuration with new model"""
    config_file = project_root / "config" / "agentos_config.yaml"

    try:
        with open(config_file) as f:
            config_data = yaml.safe_load(f)

        # Update primary model
        config_data["model"]["primary"] = new_model

        # Write back to file
        with open(config_file, "w") as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)

        print(f"\n✅ Configuration updated! Primary model set to: {new_model}")
        return True

    except Exception as e:
        print(f"❌ Failed to update configuration: {e}")
        return False


def validate_final_config():
    """Validate the final configuration"""
    print("\n🔧 Validating configuration...")
    if validate_agentos_config():
        print("✅ Configuration is valid and ready to use!")
        return True
    print("❌ Configuration validation failed!")
    return False


def display_start_commands():
    """Display commands to start AgentOS"""
    print("\n🚀 Ready to start! Use one of these commands:")
    print("  # Lightweight SQLite version:")
    print("  python finance_agentos_lite.py")
    print()
    print("  # Or using startup script:")
    print("  ./scripts/start_agentos.sh lite")
    print()
    print("  # Full version with PostgreSQL:")
    print("  python finance_agentos.py")


def main():
    """Main configuration flow"""
    display_banner()

    # Check API keys
    available_keys = check_api_keys()

    # Display current config
    display_current_config()

    # Interactive model selection
    print("\n" + "-" * 40)
    selected_model = select_model(available_keys)

    if selected_model is None:
        print("\n👋 Configuration cancelled.")
        return

    # Update configuration
    if update_config(selected_model):
        # Validate final configuration
        if validate_final_config():
            display_start_commands()
        else:
            print("\n⚠️  Please fix configuration issues before starting.")
    else:
        print("\n❌ Configuration update failed.")


if __name__ == "__main__":
    main()
