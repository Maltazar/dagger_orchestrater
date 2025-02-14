import logging
import sys
from pathlib import Path
from typing import Optional

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    module_name: str = "pipeline"
) -> None:
    """Configure logging for the pipeline"""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.getLevelName(log_level))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Setup pipeline logger
    pipeline_logger = logging.getLogger(module_name)
    pipeline_logger.setLevel(logging.getLevelName(log_level))
    
    # Suppress other loggers
    for logger_name in logging.root.manager.loggerDict:
        if not logger_name.startswith(module_name):
            logging.getLogger(logger_name).setLevel(logging.WARNING) 