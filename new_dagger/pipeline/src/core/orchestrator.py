from typing import Dict, Set
import asyncio
import logging
import dagger
import yaml
from datetime import datetime
from pydantic import ValidationError

from ..models.config import PipelineConfig, ModuleExecutionConfig
from ..models.results import ModuleResult
from ..models.state import ModuleState
from ..models.status import PipelineStatus, PipelineStatusInfo
from .loader import ModuleLoader
from .context import ContextManager
from .dependencies import DependencyManager
from .state import StateManager

logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    """Main pipeline orchestrator"""
    
    def __init__(self, config_path: str, dagger_client: dagger.Client):
        self.config_path = config_path
        self.client = dagger_client
        self.context_manager = ContextManager(dagger_client)
        self.status = PipelineStatus()
        self.dependency_manager = DependencyManager()
        self.state_manager = StateManager()
        self.metrics: Dict[str, Dict[str, float]] = {}
    
    def _validate_basic_config(self, config_data: dict) -> None:
        """Validate basic pipeline configuration structure"""
        if not isinstance(config_data, dict):
            raise ValueError("Pipeline configuration must be a dictionary")
        
        if len(config_data) != 1:
            raise ValueError("Pipeline configuration must have exactly one root key")
        
        pipeline_name = next(iter(config_data.keys()))
        pipeline_config = config_data[pipeline_name]
        
        if not isinstance(pipeline_config, dict):
            raise ValueError("Pipeline configuration must be a dictionary")
        
        required_keys = {'execution_defaults'}
        missing_keys = required_keys - set(pipeline_config.keys())
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {missing_keys}")
    
    def _load_config(self) -> PipelineConfig:
        """Load and validate pipeline configuration"""
        try:
            self.status.status = PipelineStatus.VALIDATING
            
            # Load YAML
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Basic structure validation
            self._validate_basic_config(config_data)
            
            # Full validation through Pydantic
            config = PipelineConfig.model_validate(config_data)
            
            # Update stats
            self.status.stats.modules_total = len(config.modules)
            
            return config
            
        except (yaml.YAMLError, ValidationError) as e:
            self.status.status = PipelineStatus.FAILED
            self.status.error = str(e)
            raise
    
    def _record_metric(self, module_name: str, metric_name: str, value: float) -> None:
        """Record a module execution metric"""
        if module_name not in self.metrics:
            self.metrics[module_name] = {}
        self.metrics[module_name][metric_name] = value
    
    async def _execute_module(self, 
                            module_name: str, 
                            execution_config: ModuleExecutionConfig) -> ModuleResult:
        """Execute a single module with metrics"""
        try:
            # Create module context through context manager
            context = await self.context_manager.create_context(
                self.secrets,
                execution_config,
                base_image=execution_config.base_image
            )
            
            # Load and execute module with context
            module = ModuleLoader.load_module(module_name, context)
            result = await module.run(execution_config)
            
            # Cleanup
            await self.context_manager.cleanup_context(context)
            
            return result
            
        except Exception as e:
            logger.exception(f"Error executing module {module_name}")
            raise
    
    async def _execute_parallel_group(self, 
                                    modules: Set[str],
                                    execution_config: ModuleExecutionConfig) -> Dict[str, ModuleResult]:
        """Execute a group of modules in parallel"""
        tasks = [
            self._execute_module(module_name, execution_config)
            for module_name in modules
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return dict(zip(modules, results))
    
    async def execute(self) -> PipelineStatus:
        """Execute the pipeline with status tracking"""
        self.status.stats.start_time = datetime.now()
        
        try:
            # Load and validate configuration
            self.config = self._load_config()
            
            # Get execution groups
            module_groups = self.dependency_manager.get_parallel_groups(
                list(self.config.modules.keys())
            )
            
            self.status.status = PipelineStatus.RUNNING
            logger.info(f"Execution groups: {module_groups}")
            
            results = {}
            async with dagger.Connection() as client:
                context_manager = ContextManager(client)
                
                # Execute each group
                for group in module_groups:
                    group_results = await self._execute_parallel_group(
                        group,
                        context_manager,
                        self.config.execution_defaults
                    )
                    results.update(group_results)
                    
                    # Update stats
                    self.status.stats.modules_completed += len([
                        r for r in group_results.values()
                        if not isinstance(r, Exception) and r.success
                    ])
                    self.status.stats.modules_failed += len([
                        r for r in group_results.values()
                        if isinstance(r, Exception) or not r.success
                    ])
                    
                    # Check for failures
                    if any(
                        isinstance(result, Exception) or not result.success
                        for result in group_results.values()
                    ):
                        self.status.status = PipelineStatus.FAILED
                        break
            
            if self.status.status != PipelineStatus.FAILED:
                self.status.status = PipelineStatus.COMPLETED
            
            return self.status
            
        except Exception as e:
            self.status.status = PipelineStatus.FAILED
            self.status.error = str(e)
            return self.status
            
        finally:
            # Update final stats
            self.status.stats.end_time = datetime.now()
            if self.status.stats.start_time:
                self.status.stats.duration_seconds = (
                    self.status.stats.end_time - self.status.stats.start_time
                ).total_seconds()
            self.status.metrics = self.metrics
    
    def get_status(self) -> PipelineStatusInfo:
        """Get current pipeline status"""
        return self.status
    
    def get_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get execution metrics"""
        return self.metrics 