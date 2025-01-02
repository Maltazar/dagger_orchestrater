import sys
import structlog
import logging
from typing import Any
from rich.console import Console

# Use separate consoles for different outputs
stdout_console = Console()  # For collapsed view
stderr_console = Console(stderr=True)  # For debug/verbose output

def setup_logging() -> None:
    """Configure structured logging for debug mode"""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(colors=True)
        ],
        wrapper_class=structlog.make_filtering_bound_logger(20),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )

class PipelineLogger:
    """Pipeline logger that integrates with Dagger's TUI"""
    
    def __init__(self, name: str):
        self.name = name
        self.debug_logger = structlog.get_logger(name)
    
    def info(self, msg: str, **kwargs: Any) -> None:
        """Log info message in TUI format"""
        # Print to both stdout (for collapsed view) and stderr (for verbose)
        stdout_console.print(f"  {msg}", highlight=False)
        stderr_console.print(f"│ {msg}", highlight=False)
        self.debug_logger.info(msg, **kwargs)
    
    def error(self, msg: str, **kwargs: Any) -> None:
        """Log error message in TUI format"""
        stdout_console.print(f"  ✘ {msg}", style="red", highlight=False)
        stderr_console.print(f"│ ✘ {msg}", style="red", highlight=False)
        self.debug_logger.error(msg, **kwargs)
    
    def warning(self, msg: str, **kwargs: Any) -> None:
        """Log warning message in TUI format"""
        stdout_console.print(f"  ! {msg}", style="yellow", highlight=False)
        stderr_console.print(f"│ ! {msg}", style="yellow", highlight=False)
        self.debug_logger.warning(msg, **kwargs)
    
    def debug(self, msg: str, **kwargs: Any) -> None:
        """Log debug message - only in debug logger"""
        self.debug_logger.debug(msg, **kwargs)

def get_logger(name: str) -> PipelineLogger:
    """Get a pipeline logger instance"""
    return PipelineLogger(name) 