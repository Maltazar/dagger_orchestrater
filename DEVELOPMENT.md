# Dagger Orchestrator Development Guide

## Core Architecture

### Overview
The Dagger Orchestrator is a modular pipeline system built on Dagger.io. It provides a framework for executing infrastructure operations through containerized extensions.

### Core Components

#### 1. Context Management (`src/core/context.py`)
- Manages Dagger client lifecycle
- Handles container creation and caching
- Provides container access for extensions

```python
DaggerContext
├── client: dagger.Client
└── containers: Dict[str, dagger.Container]
```

#### 2. Extension System (`src/handlers/extension.py`)
- Defines base interface for all extensions
- Handles retry logic and error management
- Standardizes container operations

```python
ExtensionHandler
├── setup_container()  # Container initialization
├── validate()        # Configuration validation
└── execute()         # Main extension logic
```

#### 3. Configuration (`src/models/config.py`)
- Defines pipeline configuration structure
- Handles extension-specific configs
- Manages execution defaults

```python
PipelineConfig
├── core: CoreConfig
│   └── execution_defaults: ExecutionDefaults
└── extensions: Dict[str, Dict]
```

#### 4. Dynamic Loading (`src/core/loader.py`)
- Dynamically loads extension modules
- Handles import errors gracefully
- Maintains extension independence

```python
ExtensionLoader
├── load_extension()     # Single extension
└── load_extensions()    # Multiple extensions
```

#### 5. Orchestration (`src/core/orchestrator.py`)
- Manages pipeline execution flow
- Coordinates extension operations
- Handles pipeline state

### Execution Flow

1. Pipeline Initialization:
   ```mermaid
   graph TD
   A[Load Config] --> B[Initialize Context]
   B --> C[Load Extensions]
   C --> D[Validate Config]
   D --> E[Start Pipeline]
   ```

2. Extension Execution:
   ```mermaid
   graph TD
   A[Setup Container] --> B[Validate Extension]
   B --> C[Execute Extension]
   C --> D[Handle Results]
   ```

## Development Guide

### Setting Up Development Environment

1. Install dependencies:
```bash
uv sync .
```

2. Run tests:
```bash
pytest tests/
```

### Creating a New Extension

1. Create extension structure:
```
extensions/
└── your_extension/
    ├── README.md           # Extension documentation
    ├── pyproject.toml      # Extension dependencies
    └── src/
        ├── __init__.py
        ├── extension.py    # Main extension class
        ├── models.py       # Extension-specific models
        └── config.py       # Extension configuration
```

2. Implement extension class:
```python
from core.handlers.extension import ExtensionHandler

class YourExtension(ExtensionHandler):
    async def setup_container(self) -> dagger.Container:
        """Setup extension container"""
        return await self.client.container().from_("base-image:tag")
    
    async def validate(self) -> bool:
        """Validate extension configuration"""
        return True
    
    async def execute(self) -> bool:
        """Execute extension logic"""
        return True
```

3. Define extension configuration:
```python
from pydantic import BaseModel

class YourExtensionConfig(BaseModel):
    option1: str
    option2: int = 42
```

### Extension Development Guidelines

1. Container Management
- Use `self.container` for operations
- Implement proper cleanup
- Cache effectively

2. Error Handling
- Use provided retry mechanism
- Log errors appropriately
- Return clear status

3. Configuration
- Validate all inputs
- Use type hints
- Document options

4. Testing
- Test container operations
- Validate configurations
- Mock external services

### Running the Pipeline

1. Development mode:
```bash
python -m src.main config.yaml
```

2. Production mode:
```bash
# Execute pipeline
dagger call [method] --source=. [args]

# Example
dagger call execute --source=. --config-path=dagger_example.yaml

# Validate config
dagger call validate --source=. --config-path=dagger_example.yaml
```

### Best Practices

1. Extension Development
- Keep extensions independent
- Use proper typing
- Follow container best practices
- Implement thorough validation

2. Error Handling
- Use structured logging
- Implement proper retries
- Clean up resources

3. Configuration
- Use clear naming
- Document all options
- Validate inputs

4. Testing
- Write unit tests
- Test container operations
- Validate configurations
- Test error conditions

### Debugging

1. Enable debug logging:
```python
setup_logging(level="DEBUG")
```

2. Container debugging:
```python
# In extension
await self.container.with_exec(["sh"]).stdout()
```

3. Configuration validation:
```python
# Validate extension config
await handler.validate()
```

## Contributing

1. Fork repository
2. Create feature branch
3. Implement changes
4. Add tests
5. Submit pull request

## Extension Publishing

1. Package extension:
```bash
uv build
```

2. Publish to PyPI:
```bash
uv publish
```

3. Install in projects:
```bash
uv add your-extension
``` 