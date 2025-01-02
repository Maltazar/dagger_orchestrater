"""Example extension package.

This extension demonstrates how to:
1. Receive configuration from core pipeline
2. Use bootstrap configuration for setup
3. Handle container and environment setup
4. Execute commands with proper state management
"""

from .extension import ExampleExtension
from .config import ExampleBootstrap
from .models import ExampleConfig, ExampleCommand, ExampleState, ExampleResult

__all__ = [
    'ExampleExtension',
    'ExampleBootstrap',
    'ExampleConfig',
    'ExampleCommand',
    'ExampleState',
    'ExampleResult'
] 