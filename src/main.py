import asyncio
import dagger
from dagger import dag
# from dagger.log import configure_logging
# import logging
import sys
from pydantic import BaseModel, ConfigDict

from .core.logging import setup_logging, get_logger
from .core.bootstrap import PipelineBootstrap

logger = get_logger(__name__)
# configure_logging(logging.DEBUG)

@dagger.object_type
class DaggerOrchestrator(BaseModel):
    """Main Dagger module class"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    @dagger.function
    async def execute(self, src: dagger.Directory, config_file: str) -> bool:
        """Execute pipeline from config file"""
        setup_logging()
        logger.info("Starting pipeline execution via Dagger", config_file=config_file)
        return await run_pipeline(src, config_file)

    @dagger.function
    async def validate(self, src: dagger.Directory, config_file: str) -> bool:
        """Validate pipeline configuration"""
        setup_logging()
        logger.info("Validating pipeline configuration", config_file=config_file)
        validated = await validate_config(src, config_file)
        if not validated:
            raise Exception("Pipeline configuration validation failed")
        return validated

async def run_pipeline(src: dagger.Directory, config_file: str) -> bool:
    """Run pipeline from config file"""
    try:
        # Configure Dagger with logging
        config = dagger.Config(log_output=True)
        
        # Use newer connection context manager with global client
        async with dagger.connection(config):
            # First phase: Bootstrap pipeline
            orchestrator, loaded_extensions = await PipelineBootstrap.bootstrap(src, config_file, dag)
            
            # Second phase: Runtime execution with context
            async with orchestrator.context as ctx:
                # Register extensions
                for name, handler_cls in loaded_extensions.items():
                    if not await orchestrator.register_extension(name, handler_cls, ctx.client):
                        logger.error("Failed to register extension", name=name)
                        return False
                
                # Execute pipeline
                logger.info("Starting pipeline execution")
                return await orchestrator.execute()
        
    except Exception as e:
        logger.exception("Pipeline execution failed", error=str(e))
        return False

async def validate_config(src: dagger.Directory, config_file: str) -> bool:
    """Validate pipeline configuration"""
    try:
        # Use newer connection context manager with global client
        async with dagger.connection(dagger.Config(log_output=sys.stderr)):
            # First phase: Bootstrap pipeline
            orchestrator, loaded_extensions = await PipelineBootstrap.bootstrap(src, config_file, dag)
            
            # If no extensions defined, validation is successful
            if not loaded_extensions:
                logger.info("No extensions to validate")
                return True
            
            # Second phase: Extension validation with context
            async with orchestrator.context as ctx:
                # Validate by attempting registration
                for name, handler_cls in loaded_extensions.items():
                    if not await orchestrator.register_extension(name, handler_cls, ctx.client):
                        logger.error("Failed to register extension", name=name)
                        return False
                    
                return True
        
    except Exception as e:
        logger.exception("Config validation failed", error=str(e))
        return False

def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("""
Usage: 
    Via Dagger (recommended):
        dagger call execute --config-path=dagger_example.yaml
        dagger call validate --config-path=dagger_example.yaml
        
    Direct execution (development only):
        python -m src.main dagger_example.yaml
        """)
        sys.exit(1)    
    asyncio.run(run_pipeline(sys.argv[1]))

if __name__ == "__main__":
    main()
