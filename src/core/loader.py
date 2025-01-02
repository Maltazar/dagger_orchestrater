from importlib import import_module
from typing import Dict, Type, List
from pathlib import Path

from ..handlers.extension import ExtensionHandler
from ..core.logging import get_logger
from ..models.config import PipelineConfig

logger = get_logger(__name__)

class ExtensionLoader:
    """Dynamic extension loader"""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.discovered_extensions: Dict[str, str] = {}
    
    def discover_extensions(self) -> Dict[str, str]:
        """Find available extensions in the extensions directory
        
        Returns:
            Dict mapping extension names to their module paths
        """
        pipeline = self.config.get_pipeline()
        # Handle case where no extensions are defined
        if not pipeline.extensions:
            logger.info("No extensions defined in pipeline configuration")
            return {}
            
        required_extensions = set(pipeline.extensions.keys())
        logger.info("Discovering extensions", required=required_extensions)
        
        # Map extension names to their expected module paths
        for ext_name in required_extensions:
            module_path = f"extensions.{ext_name}.src.extension"
            self.discovered_extensions[ext_name] = module_path
            
        return self.discovered_extensions

    def validate_extension(self, ext_name: str, extension_class: Type[ExtensionHandler]) -> bool:
        """Validate that an extension meets requirements
        
        Args:
            ext_name: Name of the extension
            extension_class: The extension handler class
            
        Returns:
            True if valid, False otherwise
        """
        # Validate extension implements required interface
        if not issubclass(extension_class, ExtensionHandler):
            logger.error(
                "Extension class must inherit from ExtensionHandler",
                name=ext_name,
                class_name=extension_class.__name__
            )
            return False
            
        # Add more validation as needed
        return True
    
    def load_extension(self, name: str) -> Type[ExtensionHandler]:
        """Dynamically load an extension handler class
        
        Args:
            name: Name of the extension to load
            
        Returns:
            Extension handler class
            
        Raises:
            ImportError: If extension module cannot be imported
            AttributeError: If extension class cannot be found
        """
        try:
            if name not in self.discovered_extensions:
                raise ImportError(f"Extension {name} not discovered")
                
            module_path = self.discovered_extensions[name]
            class_name = f"{name.capitalize()}Extension"
            
            # Import the module
            module = import_module(module_path)
            
            # Get the extension class
            extension_class = getattr(module, class_name)
            
            # Validate the extension
            if not self.validate_extension(name, extension_class):
                raise ValueError(f"Extension {name} failed validation")
            
            logger.info("Successfully loaded extension", name=name, class_name=class_name)
            return extension_class
            
        except ImportError as e:
            logger.error("Failed to import extension module", name=name, error=str(e))
            raise
        except AttributeError as e:
            logger.error("Failed to find extension class", name=name, class_name=class_name, error=str(e))
            raise
            
    def load_extensions(self) -> Dict[str, Type[ExtensionHandler]]:
        """Load all discovered extensions
        
        Returns:
            Dictionary of extension names to handler classes
        """
        if not self.discovered_extensions:
            self.discover_extensions()
            
        extensions = {}
        for name in self.discovered_extensions:
            try:
                extensions[name] = self.load_extension(name)
            except (ImportError, AttributeError, ValueError) as e:
                logger.error("Failed to load extension", name=name, error=str(e))
                continue
                
        return extensions 