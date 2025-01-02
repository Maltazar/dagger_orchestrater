"""Example extension demonstrating core functionality of ExtensionHandler.

This extension serves as a reference implementation showing how to:
1. Implement container setup and configuration
2. Handle source code mounting
3. Process variables and substitutions
4. Manage state and cleanup
5. Implement validation and execution logic
"""

from typing import Optional, Dict, Any
import dagger
from pipeline_orchestrater.handlers.extension import ExtensionHandler
from pipeline_orchestrater.core.logging import get_logger
from pipeline_orchestrater.models.config import PipelineConfig, ExecutionDefaults

from .models import ExampleConfig, ExampleState, ExampleResult
from .config import ExampleBootstrap

logger = get_logger(__name__)

class ExampleExtension(ExtensionHandler):
    """Example extension demonstrating ExtensionHandler functionality
    
    This extension receives its configuration from the core pipeline,
    which parses the main YAML file. The extension's config section
    should look like:
    
    ```yaml
    example:
      - name: example-1
        location: ./example
        message: "Hello World"
        commands:
          - command: "echo Starting example"
          - command: "echo ${message}"
            working_dir: "/app"
            env_vars:
              DEBUG: "true"
          - command: "python script.py"
        execution_settings:
          timeout_seconds: 300
          max_attempts: 3
          debug: true
          environment: dev
          env_vars:
            EXAMPLE_MODE: test
    ```
    """
    
    def __init__(self, name: str, config: Dict[str, Any], client: dagger.Client, execution_defaults: ExecutionDefaults):
        """Initialize extension with config from core pipeline
        
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
        
        # Parse config using model (config already validated by core)
        self.example_config = ExampleConfig(**config)
        
        # Initialize bootstrap helper
        self.bootstrap = ExampleBootstrap(self.example_config)
        
    async def setup_container(self) -> Optional[dagger.Container]:
        """Setup container for example extension
        
        Uses bootstrap helper to setup and configure container
        based on provided configuration.
        """
        try:
            # Get base container from bootstrap
            container = await self.bootstrap.setup_container(self.client)
            if not container:
                return None
                
            # Mount source code
            container = await self._mount_source(container)
            if not container:
                return None
                
            # Add environment variables
            env_vars = self.bootstrap.get_env_vars()
            for key, value in env_vars.items():
                container = container.with_env_variable(key, value)
            
            # Store container ID in state
            self.state.container_id = await container.id()
            
            return container
            
        except Exception as e:
            logger.exception("Failed to setup container", error=str(e))
            return None
            
    async def validate(self) -> bool:
        """Validate example extension readiness"""
        try:
            # 1. Check container
            if not self.container:
                logger.error("Container not initialized")
                return False
                
            # 2. Verify source mounted
            if "/src" not in self.state.mounted_paths:
                logger.error("Source code not mounted")
                return False
                
            # 3. Validate configuration
            if not self.example_config.message:
                logger.error("Required field 'message' not found")
                return False
                
            # 4. Validate commands
            if not self.example_config.commands:
                logger.error("No commands specified")
                return False
                
            return True
            
        except Exception as e:
            logger.exception("Validation failed", error=str(e))
            return False
            
    async def execute(self) -> bool:
        """Execute example extension logic"""
        try:
            result = ExampleResult(
                success=True,
                message="Execution started",
                command_outputs=[],
                errors=[]
            )
            
            # Execute each command
            for cmd in self.example_config.commands:
                try:
                    # Update state
                    self.state.current_command = cmd.command
                    
                    # Setup command environment
                    container = self.container
                    if cmd.working_dir:
                        container = container.with_workdir(cmd.working_dir)
                    
                    for key, value in cmd.env_vars.items():
                        container = container.with_env_variable(key, value)
                    
                    # Process variables
                    command = cmd.command.replace("${message}", self.example_config.message)
                    
                    # Execute command
                    output = await container.with_exec(["sh", "-c", command]).stdout()
                    
                    # Store result
                    result.command_outputs.append(output)
                    logger.info("Command executed", 
                              command=command,
                              working_dir=cmd.working_dir,
                              output=output)
                    
                except Exception as e:
                    result.success = False
                    result.errors.append(str(e))
                    logger.error("Command failed",
                               command=cmd.command,
                               error=str(e))
            
            # Update state with results
            self.state.results = result.command_outputs
            
            return result.success
            
        except Exception as e:
            logger.exception("Execution failed", error=str(e))
            return False
            
    async def _custom_cleanup(self) -> None:
        """Custom cleanup for example extension"""
        try:
            # Reset state
            self.state = ExampleState()
            
        except Exception as e:
            logger.error("Custom cleanup failed", error=str(e)) 