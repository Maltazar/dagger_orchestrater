# Structure

Below is the base structure of the pipeline, it is the core of the pipeline and the main configuration for the pipeline

```
# The src folder contains the core of the dagger io orchestrator pipeline
# It is the entry point for the pipeline
# Extensions can be used to add new functionality to the pipeline

src/
├── __init__.py          # Package initialization
├── __main__.py          # Entry point for running the pipeline
├── core/
│   ├── __init__.py      # Core initialization
│   ├── context.py       # Context management
│   ├── loader.py        # Module loading
│   ├── logging.py       # Logging management
│   ├── orchestrator.py  # Pipeline orchestration
│   └── state.py         # State management
├── models/
│   ├── __init__.py      # Export models
│   ├── config.py        # Base configuration models
│   ├── context.py       # Context models
│   ├── results.py       # Result models
│   ├── state.py         # State models
│   ├── metrics.py       # Metrics models
│   └── status.py        # Status models
├── handlers/
│   ├── __init__.py      # Export handlers
│   └── extension.py     # Extension handler interface for all extensions

# The extensions folder may be located here, but the idea is that the extenssions can be installed with pip and will be available in the pipeline
# The extensions are self contained and can be used as a independent extension
# Each extension has a config.py file that contains the configuration for the extension
# Each extension has an extension.py file that contains the logic for the extension
# Each extension has a models.py file that contains the models for the extension
# Each extension has an __init__.py file that contains the initialization for the extension
# Each extension has a __main__.py file that contains the entry point for the extension
# Each extension has a README.md file that contains the documentation for the extension
# Each extension has a pyproject.toml file that contains the dependencies for the extension and the astral uv build system
extensions/
├── terraform/
│   ├── README.md
│   ├── pyproject.toml
│   └── src/
│       ├── __init__.py
│       ├── __main__.py
│       ├── models.py
│       ├── config.py
│       └── extension.py
├── ansible/
│   ├── README.md
│   ├── pyproject.toml
│   └── src/
│       ├── __init__.py
│       ├── __main__.py
│       ├── models.py
│       ├── config.py
│       └── extension.py
├── helm/
│   ├── README.md
│   ├── pyproject.toml
│   └── src/
│       ├── __init__.py
│       ├── __main__.py
│       ├── models.py
│       ├── config.py
│       └── extension.py
├── kubectl/
│   ├── README.md
│   ├── pyproject.toml
│   └── src/
│       ├── __init__.py
│       ├── __main__.py
│       ├── models.py
│       ├── config.py
│       └── extension.py
└── secrets/
    ├── README.md
    ├── pyproject.toml
    └── src/
        ├── __init__.py
        ├── __main__.py
        ├── models.py
        ├── config.py
        └── extension.py

```

## core definition

The core is the main configuration for the pipeline, it is the entry point for the pipeline and the main configuration for the pipeline
hanling of the pipeline execution, the pipeline state, the pipeline results and the pipeline metrics
downloading of files, git repositories, http urls, etc
helper methos and functions that are general to the full pipeline is located in the core pipeline to be used across individual extensions

## extension definition

The extension is the individual functionality of the different modules or tools that are used to deploy the infrastructure
like terraform, ansible, helm, kubectl, etc
extensions are self contained and can be used as a independent extension to mix and match with the different extensions for the pipeline run
extensions can be build and packages to be installed with pip and will be available in the pipeline
general methods and functions that can be used across the different extensions are located in the core pipeline, and imported in the extension
there can be no cross dependency between the extensions, they can only use the core pipeline
