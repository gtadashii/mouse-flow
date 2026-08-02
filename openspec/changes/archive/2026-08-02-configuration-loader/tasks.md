## 1. Setup

- [x] 1.1 Add PyYAML dependency to project
- [x] 1.2 Create configuration loader module structure (`src/mouseflow/config_loader.py`)
- [x] 1.3 Define custom exceptions (ConfigurationError, ValidationError) in domain or config module

## 2. Configuration Loading

- [x] 2.1 Write tests for loading valid YAML configuration file
- [x] 2.2 Implement YAML file loading function
- [x] 2.3 Write tests for missing configuration file scenario
- [x] 2.4 Implement missing file error handling
- [x] 2.5 Write tests for empty configuration file scenario
- [x] 2.6 Implement empty file validation

## 3. Configuration Validation

- [x] 3.1 Write tests for valid configuration structure
- [x] 3.2 Implement configuration structure validation
- [x] 3.3 Write tests for invalid action type
- [x] 3.4 Implement action type validation
- [x] 3.5 Write tests for missing required fields
- [x] 3.6 Implement required field validation
- [x] 3.7 Write tests for invalid mapping format
- [x] 3.8 Implement mapping format validation

## 4. Domain Object Translation

- [x] 4.1 Write tests for translating configuration to Profile domain objects
- [x] 4.2 Implement configuration to Profile translation
- [x] 4.3 Write tests for translating mappings to Action domain objects
- [x] 4.4 Implement mapping to Action translation (keyboard and command types)

## 5. Action Resolution

- [x] 5.1 Write tests for resolving action when matching rule exists
- [x] 5.2 Implement action resolution logic (dictionary lookup)
- [x] 5.3 Write tests for no profile for application scenario
- [x] 5.4 Write tests for no mapping for event scenario
- [x] 5.5 Write tests for null WindowInfo scenario
- [x] 5.6 Implement missing configuration reporting

## 6. Integration

- [x] 6.1 Write integration test for full pipeline: load config → resolve action
- [x] 6.2 Create example configuration file for testing
- [x] 6.3 Verify all acceptance criteria from PRD are met
