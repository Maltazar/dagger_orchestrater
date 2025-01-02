from typing import Dict, Type
from pydantic import BaseModel, ConfigDict
import dagger

from ..models.config import PipelineConfig
from ..handlers.extension import ExtensionHandler
from ..core.logging import get_logger
from ..core.context import DaggerContext

logger = get_logger(__name__)

class PipelineOrchestrator(BaseModel):
    """Main pipeline orchestrator
    
    Responsible for:
    - Managing pipeline execution flow
    - Coordinating extension operations
    - Handling runtime state via context
    - Managing cleanup and resources
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    config: PipelineConfig
    context: DaggerContext
    registered_extensions: Dict[str, ExtensionHandler] = {}

    async def register_extension(self, name: str, handler_cls: Type[ExtensionHandler], client: dagger.Client) -> bool:
        """Register and initialize a single extension
        
        Extension registration flow:
        1. Validate extension configuration
        2. Check extension compatibility
        3. Initialize extension instance
        4. Setup extension resources
        5. Register with orchestrator
        
        Args:
            name: Extension name
            handler_cls: Extension handler class
            client: Dagger client instance
        
        Returns:
            True if registration successful
        """
        logger.info("Registering extension", name=name)
        
        try:
            # 1. Get and validate extension configuration
            pipeline = self.config.get_pipeline()
            if name not in pipeline.extensions:
                logger.error("No configuration found for extension", name=name)
                return False
                
            ext_config = pipeline.extensions[name]
            
            # 2. Check extension compatibility
            if not await self._validate_extension_compatibility(name, handler_cls):
                logger.error("Extension compatibility check failed", name=name)
                return False
            
            # 3. Initialize extension instance
            handler = handler_cls(
                name=name,
                config=ext_config,
                client=client,
                execution_defaults=pipeline.core.execution_defaults
            )
            
            # 4. Setup extension resources
            try:
                logger.info("Initializing extension", name=name)
                if not await handler.initialize():
                    logger.error("Extension initialization failed", name=name)
                    return False
                    
                # Validate extension configuration
                logger.info("Validating extension configuration", name=name)
                if not await handler.validate_config():
                    logger.error("Extension configuration validation failed", name=name)
                    return False
                    
            except Exception as e:
                logger.exception("Extension setup failed", name=name, error=str(e))
                await handler.cleanup()  # Cleanup on failure
                return False
            
            # 5. Register with orchestrator
            self.registered_extensions[name] = handler
            logger.info("Successfully registered extension", name=name)
            return True

        except Exception as e:
            logger.exception("Failed to register extension", name=name, error=str(e))
            return False
            
    async def _validate_extension_compatibility(self, name: str, handler_cls: Type[ExtensionHandler]) -> bool:
        """Validate extension compatibility with the pipeline
        
        Checks:
        1. Extension meets version requirements
        2. Extension dependencies are satisfied
        
        Args:
            name: Extension name
            handler_cls: Extension handler class
            
        Returns:
            True if extension is compatible
        """
        try:
            # Check version compatibility
            if hasattr(handler_cls, 'check_version'):
                if not await handler_cls.check_version():
                    logger.error("Extension version incompatible", name=name)
                    return False
                    
            # Check dependencies
            if hasattr(handler_cls, 'check_dependencies'):
                if not await handler_cls.check_dependencies():
                    logger.error("Extension dependencies not satisfied", name=name)
                    return False
                    
            return True
            
        except Exception as e:
            logger.exception("Extension compatibility check failed", name=name, error=str(e))
            return False

    async def execute(self) -> bool:
        """Execute the pipeline
        
        Pipeline execution flow:
        1. Initialize pipeline context and resources
        2. Setup extension containers and environments
        3. Execute extensions in order with proper error handling
        4. Handle cleanup on completion or failure
        
        Returns:
            True if pipeline executed successfully
        """
        logger.info("Starting pipeline execution")
        
        try:
            # 1. Initialize pipeline context
            async with self.context as ctx:
                logger.info("Initializing pipeline context")
                
                # 2. Setup extension environments
                for ext_name, handler in self.registered_extensions.items():
                    try:
                        logger.info("Setting up extension", name=ext_name)
                        
                        # Create container for extension and store in context
                        base_image = handler.get_base_image()
                        container = ctx.client.container().from_(base_image)
                        ctx.containers[ext_name] = container
                        
                        # Setup extension with its container
                        if not await handler.setup_container(container):
                            logger.error("Failed to setup extension container", name=ext_name)
                            return False
                            
                    except Exception as e:
                        logger.exception("Extension setup failed", name=ext_name, error=str(e))
                        return False
                
                # 3. Execute extensions in order
                for ext_name, handler in self.registered_extensions.items():
                    try:
                        # Get extension's container from context
                        container = ctx.containers.get(ext_name)
                        if not container:
                            logger.error("Container not found for extension", name=ext_name)
                            return False
                            
                        # Validate extension before execution
                        logger.info("Validating extension", name=ext_name)
                        if not await handler.run_with_retries("validate", container):
                            logger.error("Extension validation failed", name=ext_name)
                            return False

                        # Execute extension
                        logger.info("Executing extension", name=ext_name)
                        if not await handler.run_with_retries("execute", container):
                            logger.error("Extension execution failed", name=ext_name)
                            return False

                    except Exception as e:
                        logger.exception("Extension failed", name=ext_name, error=str(e))
                        return False
                    
                    finally:
                        # Ensure extension cleanup happens even on failure
                        try:
                            await handler.cleanup(container)
                        except Exception as e:
                            logger.error("Extension cleanup failed", name=ext_name, error=str(e))
                
                logger.info("Pipeline execution completed successfully")
                return True
                
        except Exception as e:
            logger.exception("Pipeline execution failed", error=str(e))
            return False
        
        finally:
            # 4. Final pipeline cleanup
            logger.info("Performing pipeline cleanup")
            await self._cleanup()

    async def _cleanup(self) -> None:
        """Clean up pipeline resources
        
        This method ensures all resources are properly cleaned up,
        including:
        - Extension resources
        - Container resources
        - Temporary files/directories
        """
        try:
            # Clean up any remaining extension resources
            for ext_name, handler in self.registered_extensions.items():
                try:
                    await handler.cleanup()
                except Exception as e:
                    logger.error("Failed to cleanup extension", name=ext_name, error=str(e))
            
            # Clear registered extensions
            self.registered_extensions.clear()
            
            # Additional cleanup as needed...
            
        except Exception as e:
            logger.exception("Pipeline cleanup failed", error=str(e))
            
        finally:
            logger.info("Pipeline cleanup completed") 