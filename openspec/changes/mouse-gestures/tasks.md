## 1. Domain Model Extension

- [x] 1.1 Add GestureDirection enum to domain.py with values: UP, DOWN, LEFT, RIGHT
- [x] 1.2 Add Gesture dataclass to domain.py with direction field
- [x] 1.3 Write tests for GestureDirection enum values and equality
- [x] 1.4 Write tests for Gesture creation, immutability, and equality

## 2. Gesture Recognition Component

- [x] 2.1 Create GestureRecognizer class in gesture.py with state tracking (cumulative_x, cumulative_y, is_active)
- [x] 2.2 Implement gesture button detection (BTN_EXTRA press activates gesture mode)
- [x] 2.3 Implement movement accumulation while gesture mode is active
- [x] 2.4 Implement gesture direction recognition on button release using threshold-based algorithm
- [x] 2.5 Implement state reset when gesture button is released
- [x] 2.6 Write tests for gesture activation and deactivation
- [x] 2.7 Write tests for movement accumulation
- [x] 2.8 Write tests for directional gesture recognition (all four directions)
- [x] 2.9 Write tests for ambiguous movement (no gesture recognized)
- [x] 2.10 Write tests for state reset after button release

## 3. Input Engine Integration

- [x] 3.1 Modify Input Engine to yield REL_X and REL_Y events (currently filtered out)
- [x] 3.2 Integrate GestureRecognizer into event processing loop
- [x] 3.3 Route button events through GestureRecognizer to detect gesture button
- [x] 3.4 Route movement events through GestureRecognizer when gesture mode is active
- [x] 3.5 Yield Gesture objects when gesture is recognized on button release
- [x] 3.6 Write tests for Input Engine yielding movement events
- [x] 3.7 Write integration tests for gesture recognition through Input Engine

## 4. Event Dispatcher Extension

- [x] 4.1 Extend DispatchContext to accept Gesture objects (in addition to MouseEvent)
- [x] 4.2 Update Event Dispatcher to handle both MouseEvent and Gesture inputs
- [x] 4.3 Ensure WindowInfo is queried and included when dispatching Gesture events
- [x] 4.4 Write tests for DispatchContext with Gesture
- [x] 4.5 Write tests for Event Dispatcher handling Gesture events

## 5. Configuration Loader Extension

- [x] 5.1 Extend Profile domain object to include gesture mappings (dict[GestureDirection, Action])
- [x] 5.2 Update Configuration Parser to parse "gestures" section in YAML
- [x] 5.3 Add validation for gesture direction values (UP, DOWN, LEFT, RIGHT)
- [x] 5.4 Update Configuration Loader to resolve actions for Gesture events
- [x] 5.5 Write tests for parsing gesture mappings from YAML
- [x] 5.6 Write tests for gesture direction validation
- [x] 5.7 Write tests for action resolution with Gesture events
- [x] 5.8 Write tests for backward compatibility (configs without gestures)

## 6. Pipeline Integration

- [x] 6.1 Update main event loop to handle both MouseEvent and Gesture in pipeline
- [x] 6.2 Ensure ProfileResolver works with Gesture-based DispatchContext
- [x] 6.3 Ensure Action Runner executes actions for Gesture events
- [x] 6.4 Write end-to-end integration tests for complete gesture flow
- [x] 6.5 Write tests for gesture with application-specific profile
- [x] 6.6 Write tests for gesture with global profile fallback

## 7. User Feedback and Reporting

- [x] 7.1 Update format_dispatch_context to display gesture information
- [x] 7.2 Add gesture direction to output format (e.g., "Gesture: LEFT")
- [x] 7.3 Write tests for gesture reporting format

## 8. Configuration Examples and Documentation

- [x] 8.1 Update examples/config.yaml with gesture mapping examples
- [x] 8.2 Update architecture.md with GestureRecognizer component
- [x] 8.3 Update pipeline diagram to show gesture recognition stage
- [x] 8.4 Update domain model documentation with Gesture objects
