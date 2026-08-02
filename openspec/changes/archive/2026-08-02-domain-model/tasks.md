## 1. Domain Objects - Core Types

- [x] 1.1 Create `src/mouseflow/domain.py` module
- [x] 1.2 Define `MouseButton` enum with values: BTN_SIDE, BTN_EXTRA, BTN_FORWARD, BTN_BACK
- [x] 1.3 Define `WheelAxis` enum with values: REL_HWHEEL, REL_WHEEL
- [x] 1.4 Define `EventType` enum or union type for event classification

## 2. Domain Objects - Event Representation

- [x] 2.1 Implement `MouseEvent` dataclass (frozen) with button/wheel type and value
- [x] 2.2 Add factory function or class method for creating button events
- [x] 2.3 Add factory function or class method for creating wheel events

## 3. Domain Objects - Window and Application

- [x] 3.1 Implement `Application` dataclass (frozen) with app_name field
- [x] 3.2 Implement `Window` dataclass (frozen) with title field
- [x] 3.3 Add default values for unknown/untitled cases

## 4. Domain Objects - Actions and Profiles

- [x] 4.1 Implement `ActionType` enum (KEYBOARD, COMMAND)
- [x] 4.2 Implement `Action` dataclass (frozen) with type and payload fields
- [x] 4.3 Implement `Profile` dataclass (frozen) with app_name and mappings dict
- [x] 4.4 Add factory functions for common action types (keyboard shortcut, command)

## 5. Testing

- [x] 5.1 Write unit tests for MouseEvent creation and equality
- [x] 5.2 Write unit tests for Application and Window creation and equality
- [x] 5.3 Write unit tests for Action and Profile creation and equality
- [x] 5.4 Write unit tests for immutability (frozen dataclass behavior)

## 6. Integration and Refactoring

- [x] 6.1 Update Input Engine to return MouseEvent domain objects
- [x] 6.2 Update Window Resolver to return Application and Window domain objects
- [x] 6.3 Update __main__.py to use domain objects in output formatting
- [x] 6.4 Verify all existing tests still pass after refactoring
