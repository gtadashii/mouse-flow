## Why

Mouse buttons provide a limited number of available actions. Mouse gestures allow users to perform a larger set of actions using natural pointer movements without requiring additional buttons. This sprint introduces gesture recognition as an additional source of actions alongside traditional mouse buttons.

## What Changes

- New gesture recognition component that tracks pointer movement while a gesture button is held
- Support for directional gestures (Up, Down, Left, Right)
- Gesture domain objects integrated into the existing action resolution pipeline
- Configuration support for gesture-to-action mappings
- User feedback reporting recognized gestures

## Capabilities

### New Capabilities
- `gesture-recognition`: Recognizes directional mouse gestures (Up, Down, Left, Right) performed while holding a configured gesture button, producing gesture domain objects that participate in action resolution.

### Modified Capabilities
- `domain-model`: Adds gesture-related domain objects (Gesture, GestureDirection) to represent recognized gestures as first-class domain concepts.
- `event-dispatcher`: Extends dispatch context to include gesture information when a gesture is recognized, allowing gestures to flow through the existing action resolution pipeline.
- `configuration-loader`: Adds support for gesture-to-action mappings in configuration files, allowing users to configure actions triggered by specific gestures.

## Impact

- **New module**: `src/mouseflow/gesture.py` for gesture recognition logic
- **Domain model**: New domain objects (Gesture, GestureDirection) in `domain.py`
- **Pipeline**: Gesture recognition becomes a new stage between event dispatch and action resolution
- **Configuration**: YAML format extended to support gesture mappings
- **Testing**: New tests for gesture recognition, domain objects, and pipeline integration
- **Dependencies**: No new external dependencies; uses existing evdev for pointer movement tracking
