# Structure

```
# Ensure proper package structure
pipeline/src/pipeline/
├── __init__.py           # Package initialization
├── models/
│   ├── __init__.py      # Export models
│   ├── config.py        # Base configuration models
│   ├── context.py       # Context models
│   ├── dependencies.py  # Dependency models
│   ├── results.py       # Result models
│   └── state.py         # State models
├── core/
│   ├── __init__.py      # Export core components
│   ├── context.py       # Context management
│   ├── dependencies.py  # Dependency management
│   ├── loader.py        # Module loading
│   ├── orchestrator.py  # Pipeline orchestration
│   └── state.py        # State management
├── modules/
│   ├── __init__.py      # Export base module
│   └── base.py         # Base module interface
└── __main__.py          # Entry point for running the pipeline
```