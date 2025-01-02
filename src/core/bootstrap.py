"""Bootstrap module for pipeline initialization

Handles:
- Configuration loading and validation
- Pipeline orchestrator creation
- Extension discovery
- Initial setup before runtime phase
"""

import yaml
import dagger
from typing import Tuple, Dict, Type

from ..models.config import PipelineConfig
from ..handlers.extension import ExtensionHandler
from ..core.logging import get_logger
from ..core.orchestrator import PipelineOrchestrator
from ..core.context import DaggerContext
from ..core.loader import ExtensionLoader

logger = get_logger(__name__)

class PipelineBootstrap:
    """Handles pipeline bootstrapping and initial setup"""
    
    @staticmethod
    async def load_config(src: dagger.Directory, yaml_path: str, client: dagger.Client) -> PipelineConfig:
        """Load and validate pipeline configuration
        
        Args:
            src: Source directory
            yaml_path: Path to YAML config file
            client: Dagger client instance
            
        Returns:
            Validated PipelineConfig
            
        Raises:
            Exception if config loading fails
        """
        try:
            # Read config file from container
            stdout_yaml = await client.container().from_("python:3.12").with_directory("/src", src).with_workdir("/src").with_exec(["cat", yaml_path]).stdout()
            
            # Parse YAML config
            config_dict = yaml.safe_load(stdout_yaml)
            
            # Create and validate config
            return PipelineConfig.model_validate(config_dict)
            
        except Exception as e:
            logger.error("Failed to load config", error=str(e))
            raise
    
    @staticmethod
    async def create_orchestrator(config: PipelineConfig) -> PipelineOrchestrator:
        """Create and initialize pipeline orchestrator
        
        Args:
            config: Validated pipeline configuration
            
        Returns:
            Initialized PipelineOrchestrator
        """
        # Create empty context - will be initialized during runtime
        context = DaggerContext()
        
        # Create orchestrator with config and empty context
        return PipelineOrchestrator(config=config, context=context)
    
    @staticmethod
    async def discover_extensions(config: PipelineConfig) -> Dict[str, Type[ExtensionHandler]]:
        """Discover and load extension handlers
        
        Args:
            config: Pipeline configuration
            
        Returns:
            Dictionary of extension name to handler class
        """
        # Initialize extension loader
        loader = ExtensionLoader(config)
        
        # Discover extensions
        logger.info("Discovering extensions")
        loader.discover_extensions()
        
        # Load extension handlers
        logger.info("Loading extensions")
        return loader.load_extensions()

    @classmethod
    async def bootstrap(cls, src: dagger.Directory, yaml_path: str, client: dagger.Client) -> Tuple[PipelineOrchestrator, Dict[str, Type[ExtensionHandler]]]:
        """Complete pipeline bootstrap process
        
        Performs full bootstrap sequence:
        1. Load and validate configuration
        2. Create orchestrator instance
        3. Discover and load extensions
        
        Args:
            src: Source directory
            yaml_path: Path to YAML config file
            client: Dagger client instance
            
        Returns:
            Tuple of (orchestrator, loaded_extensions)
        """
        # Load and validate config
        config = await cls.load_config(src, yaml_path, client)
        
        # Create orchestrator
        orchestrator = await cls.create_orchestrator(config)
        
        # Discover extensions
        extensions = await cls.discover_extensions(config)
        
        return orchestrator, extensions 