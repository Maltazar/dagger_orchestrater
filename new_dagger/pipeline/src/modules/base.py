from abc import ABC, abstractmethod
from typing import Type
import asyncio
import logging
from pydantic import BaseModel, ValidationError
from ..models.config import ModuleConfig
from ..models.context import ModuleContext
from ..models.results import ModuleResult

logger = logging.getLogger(__name__)

class BaseModule(ABC):
    """Base class for all pipeline modules"""
    
    def __init__(self, context: ModuleContext):
        self.context = context
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def get_config_model(self) -> Type[BaseModel]:
        """Return the configuration model for this module"""
        pass
    
    def validate_config(self, config: dict) -> BaseModel:
        """Validate module configuration using module's config model"""
        try:
            # Validate base config (execution settings)
            base_config = ModuleConfig.model_validate(config)
            
            # Get and validate module-specific config
            config_model = self.get_config_model()
            module_config = config_model.model_validate(config)
            
            # Merge execution settings from base config
            if hasattr(module_config, 'execution'):
                module_config.execution = base_config.execution
                
            return module_config
            
        except ValidationError as e:
            self.logger.error(f"Configuration validation failed: {e}")
            raise
    
    async def execute_with_timeout(self, coro, timeout: float):
        """Execute coroutine with timeout"""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            self.logger.error(f"Operation timed out after {timeout} seconds")
            raise
    
    async def execute_with_retry(self, operation, config: dict):
        """Execute operation with retry logic"""
        retry_config = self.context.execution_config.retry
        attempt = 1
        last_exception = None
        delay = retry_config.delay_seconds
        
        while attempt <= retry_config.max_attempts:
            try:
                self.logger.info(f"Attempt {attempt} of {retry_config.max_attempts}")
                return await operation(config)
            except Exception as e:
                last_exception = e
                error_type = e.__class__.__name__
                
                if error_type not in retry_config.retry_on_exceptions:
                    self.logger.error(f"Non-retryable error: {error_type}")
                    raise
                
                if attempt == retry_config.max_attempts:
                    self.logger.error(f"All retry attempts failed: {e}")
                    raise
                
                self.logger.warning(f"Attempt {attempt} failed: {e}")
                
                if retry_config.exponential_backoff:
                    delay *= 2
                
                await asyncio.sleep(delay)
                attempt += 1
        
        raise last_exception
    
    @abstractmethod
    async def validate(self, config: dict) -> bool:
        """Validate module configuration before execution"""
        pass
    
    @abstractmethod
    async def pre_execute(self, config: dict) -> ModuleResult:
        """Run pre-execution tasks (e.g., dependency checks)"""
        pass
    
    @abstractmethod
    async def execute(self, config: dict) -> ModuleResult:
        """Execute the module's main logic"""
        pass
    
    @abstractmethod
    async def post_execute(self, config: dict, result: ModuleResult) -> ModuleResult:
        """Run post-execution tasks (e.g., cleanup)"""
        pass
    
    async def run(self, config: dict) -> ModuleResult:
        """Main entry point for module execution with retry and timeout"""
        try:
            self.logger.info(f"Starting module execution with config: {config}")
            
            # Validate configuration
            validated_config = self.validate_config(config)
            if not await self.validate(validated_config):
                return ModuleResult(
                    success=False,
                    message="Configuration validation failed",
                    error="Invalid configuration"
                )
            
            # Execute with timeout and retry
            timeout = self.context.execution_config.timeout_seconds
            
            async def full_execution(config):
                # Pre-execution
                pre_result = await self.pre_execute(config)
                if not pre_result.success:
                    return pre_result
                
                # Main execution
                result = await self.execute(config)
                if not result.success:
                    return result
                
                # Post-execution
                return await self.post_execute(config, result)
            
            result = await self.execute_with_timeout(
                self.execute_with_retry(full_execution, validated_config),
                timeout
            )
            
            if result.success:
                self.logger.info("Module execution completed successfully")
            else:
                self.logger.error(f"Module execution failed: {result.error}")
            
            return result
            
        except Exception as e:
            self.logger.exception("Unexpected error during module execution")
            return ModuleResult(
                success=False,
                message="Module execution failed",
                error=str(e)
            )