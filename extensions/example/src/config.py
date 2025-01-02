"""Bootstrap configuration for example extension.

This module handles environment setup and container configuration
based on the configuration received from the core pipeline.
"""

from typing import Optional
import dagger

from pipeline_orchestrater.core.logging import get_logger
from .models import ExampleConfig

logger = get_logger(__name__)

class ExampleBootstrap:
    """Handles environment and container setup for the example extension"""
    
    def __init__(self, config: ExampleConfig):
        """Initialize with parsed config from core pipeline"""
        self.config = config
        
    async def setup_container(self, client: dagger.Client) -> Optional[dagger.Container]:
        """Setup and configure container based on config
        
        Args:
            client: Dagger client from core pipeline
            
        Returns:
            Configured container or None if setup fails
        """
        try:
            # Basic container setup
            container = client.container().from_("python:3.12-slim")
            
            # Add any config-specific setup
            if self.config.execution_settings.get("debug"):
                container = container.with_env_variable("DEBUG", "true")
                
            # Add any required tools
            container = container.with_exec(["apt-get", "update"])
            container = container.with_exec(["apt-get", "install", "-y", "git"])
            
            return container
            
        except Exception as e:
            logger.error("Failed to setup container", error=str(e))
            return None
            
    def get_env_vars(self) -> dict[str, str]:
        """Get environment variables based on config"""
        env_vars = {
            "APP_NAME": self.config.name,
            "APP_ENV": self.config.execution_settings.get("environment", "dev")
        }
        
        # Add any config-specific env vars
        env_vars.update(self.config.execution_settings.get("env_vars", {}))
        
        return env_vars 