from typing import Dict, Optional
from pydantic import BaseModel, ConfigDict
import dagger

class DaggerContext(BaseModel):
    """Context manager for Dagger operations
    
    Manages:
    - Dagger client instance
    - Extension containers
    - Pipeline state
    - Resource cleanup
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    client: Optional[dagger.Client] = None
    containers: Dict[str, dagger.Container] = {}
    pipeline_state: Dict[str, any] = {}  # Track pipeline execution state
    
    def get_client(self) -> dagger.Client:
        """Get Dagger client instance
        
        Returns:
            Active Dagger client
            
        Raises:
            RuntimeError if client not initialized
        """
        if not self.client:
            raise RuntimeError("Dagger client not initialized")
        return self.client
        
    def get_container(self, name: str) -> dagger.Container:
        """Get container for extension
        
        Args:
            name: Extension name
            
        Returns:
            Container instance
            
        Raises:
            KeyError if container not found
        """
        if name not in self.containers:
            raise KeyError(f"Container not found for extension: {name}")
        return self.containers[name]

    async def __aenter__(self):
        """Enter async context and initialize resources"""
        # Client is passed in from orchestrator
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context and cleanup resources"""
        # Clear containers
        self.containers.clear()
        
        # Clear pipeline state
        self.pipeline_state.clear()
        
        # Client is managed by dagger.connection() 