from typing import Dict, Optional
import logging
import dagger
from ..models.context import ModuleContext
from ..models.config import ModuleExecutionConfig

logger = logging.getLogger(__name__)

class ContextManager:
    """Manages module execution contexts and Dagger container operations"""
    
    def __init__(self, client: dagger.Client):
        self.client = client
        # Base container configuration
        self.base_workspace = (
            client.container()
            .from_("alpine:latest")
            .with_workdir("/workspace")
        )
    
    def get_container(self, 
                     base_image: str,
                     working_dir: str = "/workspace") -> dagger.Container:
        """Get a configured Dagger container"""
        return (
            self.client.container()
            .from_(base_image)
            .with_workdir(working_dir)
        )
    
    async def create_context(self, 
                           secrets: Dict[str, dict],
                           execution_config: ModuleExecutionConfig,
                           base_image: Optional[str] = None) -> ModuleContext:
        """Create a new module context with Dagger container"""
        try:
            # Create module-specific workspace
            workspace = (
                self.base_workspace if not base_image
                else self.get_container(base_image)
            )
            
            # Configure workspace with common tools
            workspace = (
                workspace
                .with_exec(["apk", "add", "--no-cache", "curl", "git"])
                .with_mounted_directory("/workspace", self.client.host().directory("."))
            )
            
            return ModuleContext(
                client=self.client,
                workspace=workspace,
                secrets=secrets,
                execution_config=execution_config
            )
            
        except Exception as e:
            logger.error(f"Failed to create module context: {e}")
            raise
    
    async def cleanup_context(self, context: ModuleContext) -> None:
        """Cleanup module context and resources"""
        try:
            # Add cleanup logic here
            pass
        except Exception as e:
            logger.error(f"Failed to cleanup context: {e}")
            raise