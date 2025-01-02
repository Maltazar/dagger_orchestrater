# Example Extension

This is a reference implementation demonstrating how to build extensions for the pipeline orchestrator.

## Features

- Container setup and configuration
- Source code mounting and management
- Variable processing and substitution
- State management and cleanup
- Validation and execution logic

## Configuration

Example configuration in your pipeline YAML:

```yaml
example:
  - name: example-1
    location: ./example
    vars:
      message: "Hello World"
      commands:
        - echo "Starting example"
        - echo "${message}"
        - python script.py
    execution_settings:
      timeout_seconds: 300
      max_attempts: 3
```

## Implementation Details

The example extension demonstrates:

1. Container Management
   - Uses Python slim image
   - Mounts source code
   - Installs dependencies
   - Sets up environment

2. Validation
   - Checks container state
   - Verifies source code
   - Validates variables
   - Checks command format

3. Execution
   - Processes variables
   - Executes commands
   - Captures outputs
   - Updates state

4. Cleanup
   - Cleans up resources
   - Manages state

## Usage

1. Add the example configuration to your pipeline YAML
2. Place your source code in the specified location
3. Run the pipeline

## Development

To create your own extension:

1. Copy this example as a template
2. Modify the configuration structure
3. Implement your specific logic
4. Follow the validation and execution patterns

## Best Practices

- Always validate configuration
- Handle errors gracefully
- Clean up resources
- Use proper logging
- Document configuration format 