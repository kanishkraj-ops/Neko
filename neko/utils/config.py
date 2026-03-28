import os
import json
from pathlib import Path

DEFAULT_CONFIG = {
    "threads": 10,
    "timeout": 5,
    "api_keys": {
        "shodan": "",
        "nvd": ""
    },
    "defaults": {
        "lhost": "127.0.0.1",
        "lport": 4444
    }
}

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / ".neko"
        self.config_file = self.config_dir / "config.json"
        self.config = DEFAULT_CONFIG
        self.load()

    def load(self):
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True)
            
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    user_config = json.load(f)
                    self.config.update(user_config)
            except Exception:
                # If error, stay with defaults
                pass
        else:
            self.save()

    def save(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save()

# Global config instance
_config = ConfigManager()

def get_config():
    return _config
