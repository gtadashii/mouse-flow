## 1. Dependencies Setup

- [x] 1.1 Add i3ipc dependency to pyproject.toml
- [x] 1.2 Install dependencies with uv

## 2. Resolver Module

- [x] 2.1 Create src/mouseflow/resolver.py module
- [x] 2.2 Define WindowInfo dataclass with app_name and title fields
- [x] 2.3 Define WindowResolver protocol
- [x] 2.4 Implement SwayResolver class using i3ipc
- [x] 2.5 Implement resolve() function that returns WindowInfo

## 3. Error Handling

- [x] 3.1 Handle case when no window has focus
- [x] 3.2 Handle missing application name
- [x] 3.3 Handle missing window title
- [x] 3.4 Handle Sway IPC connection failures

## 4. User Feedback

- [x] 4.1 Implement format_window_info() function
- [x] 4.2 Display resolved window information in main

## 5. Integration

- [x] 5.1 Update __main__.py to use resolver
- [x] 5.2 Display window information after device discovery

## 6. Testing

- [x] 6.1 Write tests for WindowInfo dataclass
- [x] 6.2 Write tests for SwayResolver with mocked i3ipc
- [x] 6.3 Write tests for error handling scenarios
- [x] 6.4 Write tests for format_window_info()

## 7. Quality Checks

- [x] 7.1 Run all quality checks (make check)
- [x] 7.2 Verify pre-commit hooks pass
- [x] 7.3 Test with real Sway session

## 8. Documentation

- [x] 8.1 Update README with window resolver usage
- [x] 8.2 Document Sway IPC requirements
- [x] 8.3 Add troubleshooting for window resolution issues
