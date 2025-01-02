from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import dagger
import asyncio
from pydantic import BaseModel, ConfigDict, Field

from ..core.logging import get_logger
from ..models.config import ExecutionDefaults

logger = get_logger(__name__)

class ExtensionHandler(ABC, BaseModel):
    """Base class for extension handlers
    
    Core responsibilities:
    - Container lifecycle management
    - Extension state management
    - Resource cleanup
    - Version and dependency checks
    - Configuration validation
    - Error handling and retries
    
    Extension Configuration Structure:
    - name: Extension instance name
    - location: Source location (file/http/git)
    - vars: Configuration variables
    - groups: Resource groupings (if applicable)
    - execution_settings: Override defaults
    """
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra='allow'
    )
    
    name: str
    config: Dict[str, Any]
    client: dagger.Client = Field(exclude=True)
    container: Optional[dagger.Container] = Field(default=None, exclude=True)
    execution_defaults: ExecutionDefaults
    state: Dict[str, Any] = Field(default_factory=dict)

    def __init__(self, name: str, config: Dict[str, Any], client: dagger.Client, execution_defaults: ExecutionDefaults):
        """Initialize extension handler
        
        Args:
            name: Extension name
            config: Extension-specific config from pipeline YAML
            client: Dagger client instance
            execution_defaults: Default execution settings
        """
        super().__init__(
            name=name,
            config=config,
            client=client,
            execution_defaults=execution_defaults
        )

    @classmethod
    async def check_version(cls) -> bool:
        """Check if extension version is compatible"""
        try:
            # Implement version checking based on extension requirements
            return True
        except Exception as e:
            logger.error("Version check failed", error=str(e))
            return False

    @classmethod
    async def check_dependencies(cls) -> bool:
        """Check if extension dependencies are satisfied"""
        try:
            # Implement dependency checking based on extension requirements
            return True
        except Exception as e:
            logger.error("Dependency check failed", error=str(e))
            return False

    def get_base_image(self) -> str:
        """Get base image for extension container"""
        # Allow override via config or use extension-specific default
        return self.config.get("base_image", self._get_default_image())

    def _get_default_image(self) -> str:
        """Get default image for this extension type"""
        return "python:3.12"  # Override in subclasses

    async def initialize(self) -> bool:
        """Initialize the extension"""
        try:
            # 1. Validate configuration
            if not await self.validate_config():
                logger.error("Configuration validation failed", name=self.name)
                return False

            # 2. Setup container with source code
            self.container = await self.setup_container()
            if not self.container:
                logger.error("Container setup failed", name=self.name)
                return False

            # 3. Initialize extension state
            if not await self.initialize_state():
                logger.error("State initialization failed", name=self.name)
                return False

            return True
        except Exception as e:
            logger.exception("Failed to initialize extension", name=self.name, error=str(e))
            return False

    async def initialize_state(self) -> bool:
        """Initialize extension state"""
        try:
            # Initialize state with config values
            self.state["location"] = self.config.get("location")
            self.state["vars"] = self.config.get("vars", {})
            self.state["groups"] = self.config.get("groups", [])
            
            # Track container state
            self.state["container_id"] = None
            self.state["mounted_paths"] = []
            self.state["env_vars"] = {}
            
            return True
        except Exception as e:
            logger.error("Failed to initialize state", name=self.name, error=str(e))
            return False

    async def validate_config(self) -> bool:
        """Validate extension configuration"""
        try:
            # Check required fields
            required_fields = ["name", "location"]
            for field in required_fields:
                if field not in self.config:
                    logger.error(f"Missing required field: {field}", name=self.name)
                    return False

            # Validate location format
            location = self.config["location"]
            if not self._validate_location(location):
                logger.error("Invalid location format", name=self.name, location=location)
                return False

            # Validate variables if present
            if "vars" in self.config:
                if not self._validate_vars(self.config["vars"]):
                    logger.error("Invalid variables format", name=self.name)
                    return False

            return True
        except Exception as e:
            logger.error("Configuration validation failed", name=self.name, error=str(e))
            return False

    def _validate_location(self, location: str) -> bool:
        """Validate source location format"""
        # Support file, http(s), and git URLs
        if location.startswith(("./", "/", "http://", "https://", "git@")):
            return True
        return False

    def _validate_vars(self, vars: Any) -> bool:
        """Validate variables format"""
        if not isinstance(vars, (list, dict)):
            return False
        return True

    @abstractmethod
    async def setup_container(self) -> Optional[dagger.Container]:
        """Setup container for extension
        
        Implementation should:
        1. Start with base image
        2. Mount source code
        3. Install dependencies
        4. Configure environment
        5. Setup working directory
        """
        pass

    @abstractmethod
    async def validate(self) -> bool:
        """Validate extension readiness
        
        Implementation should:
        1. Check container state
        2. Verify source code
        3. Test configuration
        4. Validate dependencies
        """
        pass

    @abstractmethod
    async def execute(self) -> bool:
        """Execute extension logic
        
        Implementation should:
        1. Prepare execution environment
        2. Process variables/substitutions
        3. Run main logic
        4. Handle outputs
        5. Update state
        """
        pass

    async def run_with_retries(self, operation: str, container: Optional[dagger.Container] = None) -> bool:
        """Run an operation with retries"""
        attempts = 0
        delay = self.execution_defaults.delay_seconds

        while True:
            try:
                # Store container temporarily if provided
                original_container = self.container
                if container:
                    self.container = container

                try:
                    # Update state before operation
                    self.state["last_operation"] = operation
                    self.state["attempts"] = attempts + 1

                    if operation == "validate":
                        result = await self.validate()
                    elif operation == "execute":
                        result = await self.execute()
                    else:
                        logger.error("Invalid operation", operation=operation)
                        return False

                    # Update state after operation
                    self.state["last_result"] = result
                    return result

                finally:
                    # Restore original container
                    self.container = original_container

            except Exception as e:
                attempts += 1
                if attempts >= self.execution_defaults.max_attempts:
                    logger.exception(
                        f"Operation {operation} failed after max attempts",
                        name=self.name,
                        error=str(e)
                    )
                    return False
                
                logger.warning(
                    f"Operation {operation} failed, retrying",
                    name=self.name,
                    attempt=attempts,
                    error=str(e)
                )
                
                if self.execution_defaults.exponential_backoff:
                    delay *= 2
                
                await asyncio.sleep(delay)

    async def cleanup(self, container: Optional[dagger.Container] = None) -> None:
        """Clean up extension resources"""
        try:
            # Clean up provided container
            if container:
                try:
                    # Remove mounted volumes
                    for path in self.state.get("mounted_paths", []):
                        logger.info("Cleaning up mounted path", path=path)
                        # Implement container cleanup
                except Exception as e:
                    logger.error("Failed to cleanup container mounts", error=str(e))

            # Clean up extension's own container
            if self.container:
                try:
                    # Remove container resources
                    self.container = None
                except Exception as e:
                    logger.error("Failed to cleanup extension container", error=str(e))

            # Clean up state
            self.state.clear()

            # Allow extensions to implement custom cleanup
            await self._custom_cleanup()

        except Exception as e:
            logger.error("Failed to cleanup extension", name=self.name, error=str(e))

    async def _custom_cleanup(self) -> None:
        """Custom cleanup logic"""
        # Override in subclasses for extension-specific cleanup
        pass

    async def _mount_source(self, container: dagger.Container) -> Optional[dagger.Container]:
        """Mount source code into container"""
        try:
            location = self.config["location"]
            
            # Handle different source types
            if location.startswith(("./", "/")):
                # Local file/directory
                src = self.client.host().directory(location)
                container = container.with_mounted_directory("/src", src)
            elif location.startswith(("http://", "https://")):
                # HTTP(S) URL - implement download logic
                pass
            elif location.startswith("git@"):
                # Git repository - implement clone logic
                pass
            
            self.state["mounted_paths"].append("/src")
            return container
            
        except Exception as e:
            logger.error("Failed to mount source", error=str(e))
            return None

    async def _setup_environment(self, container: dagger.Container) -> Optional[dagger.Container]:
        """Setup container environment"""
        try:
            # Add environment variables
            for key, value in self.state.get("env_vars", {}).items():
                container = container.with_env_variable(key, str(value))
            
            # Set working directory
            container = container.with_workdir("/src")
            
            return container
            
        except Exception as e:
            logger.error("Failed to setup environment", error=str(e))
            return None