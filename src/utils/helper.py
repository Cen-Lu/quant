import yaml
from pathlib import Path

def load_config() -> dict:
    """Load YAML configuration"""
    config_path = Path(__file__).parent.parent / "../config/config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)