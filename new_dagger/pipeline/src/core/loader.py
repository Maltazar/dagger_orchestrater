from importlib import import_module
import logging
from ..models.context import ModuleContext
from ..modules.base import BaseModule

logger = logging.getLogger(__name__)

class ModuleLoader:
    """Handles dynamic loading of pipeline modules"""
    
    @staticmethod
    def load_module(module_name: str, context: ModuleContext) -> BaseModule:
        """Load a module by name"""
        try:
            logger.debug(f"Loading module: {module_name}")
            module_path = f"{module_name}_module.src.module.{module_name}"
            module = import_module(module_path)
            module_class = getattr(module, f"{module_name.capitalize()}Module")
            
            # Validate that the class is a proper module
            if not issubclass(module_class, BaseModule):
                raise ImportError(f"Module {module_name} does not inherit from BaseModule")
                
            return module_class(context)
            
        except Exception as e:
            logger.error(f"Failed to load module {module_name}: {str(e)}")
            raise ImportError(f"Failed to load module {module_name}: {str(e)}") 