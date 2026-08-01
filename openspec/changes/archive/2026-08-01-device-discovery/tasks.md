## 1. Dependencies Setup

- [x] 1.1 Add evdev dependency to pyproject.toml
- [x] 1.2 Install dependencies with uv

## 2. Device Discovery Module

- [x] 2.1 Create src/mouseflow/discovery.py module
- [x] 2.2 Implement device enumeration function using evdev
- [x] 2.3 Implement capability checking logic (BTN_LEFT, BTN_RIGHT, BTN_SIDE/BTN_EXTRA)
- [x] 2.4 Implement find_supported_device() function

## 3. Device Identification

- [x] 3.1 Define supported device criteria (capability flags)
- [x] 3.2 Implement is_supported_device() function
- [x] 3.3 Handle edge cases (no devices, multiple devices)

## 4. User Feedback

- [x] 4.1 Implement device name extraction from evdev device
- [x] 4.2 Implement success message output ("Found device: <name>")
- [x] 4.3 Implement failure message output ("No supported mouse found.")

## 5. Main Entry Point

- [x] 5.1 Update src/mouseflow/__main__.py to call discovery
- [x] 5.2 Handle successful device detection
- [x] 5.3 Handle missing device case (exit with non-zero status)

## 6. Testing

- [x] 6.1 Write tests for device enumeration
- [x] 6.2 Write tests for capability checking
- [x] 6.3 Write tests for find_supported_device()
- [x] 6.4 Write tests for success/failure messages
- [x] 6.5 Mock evdev devices for testing

## 7. Integration

- [x] 7.1 Run all quality checks (make check)
- [x] 7.2 Verify pre-commit hooks pass
- [x] 7.3 Test with real mouse device if available

## 8. Documentation

- [x] 8.1 Update README with device discovery usage
- [x] 8.2 Document required permissions (input group)
