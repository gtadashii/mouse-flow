## Why

The application can now detect mouse events, identify the focused application, and resolve the appropriate action, but no action is actually performed. A dedicated execution layer is needed to translate resolved actions into operating system interactions, completing the pipeline from input detection to action execution.

## What Changes

- New Action Runner component that executes resolved actions on the operating system
- Support for keyboard shortcut execution (e.g., Alt+Left, Ctrl+Shift+P)
- Support for shell command execution (e.g., swaymsg workspace next)
- Support for application launch execution
- Execution result reporting with status feedback
- Graceful failure handling that prevents execution errors from terminating the application

## Capabilities

### New Capabilities
- `action-runner`: Executes resolved actions on the operating system, including keyboard shortcuts, shell commands, and application launches. Reports execution results and handles failures gracefully without affecting the event pipeline.

### Modified Capabilities
<!-- None - this is a new capability -->

## Impact

- **New module**: `src/mouseflow/runner.py`
- **Dependencies**: Will require a library for keyboard simulation (e.g., pynput, evdev output)
- **Domain**: Consumes Action objects from Configuration Loader
- **Pipeline position**: Final stage of the pipeline, after Configuration Loader
- **Testing**: Requires unit tests for each action type and integration tests for the complete pipeline
- **System**: Will interact with operating system APIs for keyboard simulation and process execution
