"""Pipeline execution entry point"""
import asyncio
import logging
import sys
from pathlib import Path
import dagger

from .core.logging import setup_logging
from .core.orchestrator import PipelineOrchestrator
from .models.status import PipelineStatus

logger = logging.getLogger(__name__)

def print_status(status_info):
    """Print pipeline status in a formatted way"""
    print("\nPipeline Status Report")
    print("=====================")
    print(f"Status: {status_info.status}")
    if status_info.error:
        print(f"Error: {status_info.error}")
    
    stats = status_info.stats
    if stats.start_time:
        print("\nExecution Statistics")
        print(f"Start Time: {stats.start_time}")
        print(f"End Time: {stats.end_time if stats.end_time else 'Running'}")
        print(f"Duration: {stats.duration_seconds:.2f} seconds")
        print(f"Modules Total: {stats.modules_total}")
        print(f"Modules Completed: {stats.modules_completed}")
        print(f"Modules Failed: {stats.modules_failed}")
    
    if status_info.metrics:
        print("\nModule Metrics")
        for module, metrics in status_info.metrics.items():
            print(f"\n{module}:")
            for metric, value in metrics.items():
                print(f"  {metric}: {value}")

async def main(config_path: str) -> int:
    """Main pipeline execution"""
    try:
        # Initialize Dagger client
        async with dagger.Connection() as client:
            # Pass dagger client to orchestrator
            pipeline = PipelineOrchestrator(config_path, dagger_client=client)
            results = await pipeline.execute()
            print_status(results)
            
            status = pipeline.get_status()
            print_status(status)
            
            return 0 if status.status == PipelineStatus.COMPLETED else 1
        
    except dagger.DaggerError as e:
        logger.exception("Dagger pipeline execution failed", exc_info=e)
        return 1
    except Exception as e:
        logger.exception("Pipeline execution failed", exc_info=e)
        return 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m pipeline <config.yaml>")
        sys.exit(1)
    
    config_path = Path(sys.argv[1])
    if not config_path.exists():
        print(f"Config file not found: {config_path}")
        sys.exit(1)
    
    # Setup logging
    setup_logging(
        log_level="INFO",
        log_file=Path("pipeline.log")
    )
    
    sys.exit(asyncio.run(main(str(config_path)))) 