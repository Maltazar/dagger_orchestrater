from typing import Dict, Optional
import logging
import dagger
from ..models.context import ModuleContext
from ..models.config import ModuleExecutionConfig

logger = logging.getLogger(__name__)

class ContextManager:
    """Manages module execution contexts"""
    
    def __init__(self, client: dagger.Client):
        self.client = client
        # Base workspace for shared resources
        self.base_workspace = (
            client.container()
            .from_("alpine:latest")
            .with_workdir("/workspace")
            .with_exec(["mkdir", "-p", "/workspace"])
        )
        # Track extension-specific containers
        self.extension_containers: Dict[str, dagger.Container] = {}
    
    def _get_extension_container(self, extension_name: str) -> dagger.Container:
        """Get or create an extension-specific container"""
        if extension_name not in self.extension_containers:
            # Let the extension define its own container in its execution
            self.extension_containers[extension_name] = self.base_workspace
        return self.extension_containers[extension_name]
    
    async def create_context(self, 
                           extension_name: str,
                           secrets: Dict[str, dict],
                           execution_config: ModuleExecutionConfig) -> ModuleContext:
        """Create a new context with extension-specific container"""
        try:
            workspace = self._get_extension_container(extension_name)
            
            return ModuleContext(
                client=self.client,
                workspace=workspace,
                secrets=secrets,
                execution_config=execution_config
            )
            
        except Exception as e:
            logger.error(f"Failed to create extension context: {e}")
            raise
    
    def update_extension_container(self, 
                                 extension_name: str, 
                                 container: dagger.Container) -> None:
        """Update an extension's container"""
        self.extension_containers[extension_name] = container 