## 1. Engine Module Setup

- [x] 1.1 Create src/mouseflow/engine.py module
- [x] 1.2 Define supported event types (BTN_SIDE, BTN_EXTRA, BTN_FORWARD, REL_HWHEEL)
- [x] 1.3 Create function to open device by path

## 2. Event Stream Implementation

- [x] 2.1 Implement event reading loop using evdev.read_loop()
- [x] 2.2 Add event filtering logic (check type and code)
- [x] 2.3 Implement event name resolution (code to human-readable name)
- [x] 2.4 Add event display (print to stdout)

## 3. Graceful Shutdown

- [x] 3.1 Implement signal handler for SIGINT (Ctrl+C)
- [x] 3.2 Add device handle cleanup on exit
- [x] 3.3 Ensure resources are released properly

## 4. Integration with Discovery

- [x] 4.1 Update __main__.py to use discovery and engine together
- [x] 4.2 Pass device path from discovery to engine
- [x] 4.3 Handle device open failures gracefully

## 5. Testing

- [x] 5.1 Write tests for event filtering logic
- [x] 5.2 Write tests for event name resolution
- [x] 5.3 Write tests for graceful shutdown
- [x] 5.4 Mock evdev events for testing
- [x] 5.5 Test with real device if available

## 6. Quality Checks

- [x] 6.1 Run all quality checks (make check)
- [x] 6.2 Verify pre-commit hooks pass
- [x] 6.3 Test continuous execution with real mouse

## 7. Documentation

- [x] 7.1 Update README with input engine usage
- [x] 7.2 Document supported events
- [x] 7.3 Add troubleshooting for device access issues
