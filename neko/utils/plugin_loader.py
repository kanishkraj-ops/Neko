import importlib.util
import os
from pathlib import Path
from .logger import get_logger

logger = get_logger()

class PluginLoader:
    def __init__(self, plugin_dir=None):
        if plugin_dir is None:
            # Default to current directory's 'plugins' folder
            self.plugin_dir = Path(__file__).parent.parent / "plugins"
        else:
            self.plugin_dir = Path(plugin_dir)
            
        self.plugins = {}

    def load_plugins(self):
        if not self.plugin_dir.exists():
            return
            
        for file in self.plugin_dir.glob("*.py"):
            if file.name == "__init__.py":
                continue
                
            plugin_name = file.stem
            try:
                spec = importlib.util.spec_from_file_location(plugin_name, file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, "register"):
                    self.plugins[plugin_name] = module
                    logger.debug(f"Loaded plugin: {plugin_name}")
                else:
                    logger.warning(f"Plugin {plugin_name} missing 'register' function.")
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_name}: {e}")

    def get_plugin(self, name):
        return self.plugins.get(name)

# Global loader
_loader = PluginLoader()

def get_plugin_loader():
    return _loader
