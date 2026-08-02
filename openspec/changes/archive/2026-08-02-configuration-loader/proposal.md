## Why

The Event Dispatcher produces DispatchContext objects containing mouse events and window information, but the application has no knowledge of user preferences. A configuration layer is needed to load user-defined mappings and resolve which action, if any, should be associated with a dispatched event.

## What Changes

- New Configuration Loader component that loads user-defined YAML configuration files
- Configuration validation with clear error reporting for invalid or missing files
- Action resolution: given a DispatchContext, determine if a matching action exists
- Resolved action production: when a mapping exists, produce a domain Action object
- Missing configuration handling: report when no action is configured for a context

## Capabilities

### New Capabilities
- `configuration-loader`: Loads user configuration from YAML files, validates configuration data, translates configuration into domain objects (Profile, Action), and resolves which action matches a dispatched context.

### Modified Capabilities
<!-- None - this is a new capability -->

## Impact

- **New module**: `src/mouseflow/config_loader.py`
- **Dependencies**: Will use PyYAML for configuration parsing
- **Domain**: Consumes DispatchContext from Event Dispatcher, produces Action objects
- **Pipeline position**: Sits between Event Dispatcher and Action Runner (future)
- **Testing**: Requires unit tests for loading, validation, and resolution logic
