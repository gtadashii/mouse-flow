## Context

MouseFlow currently processes discrete mouse button events through a pipeline: Input Engine → Event Dispatcher → Configuration Loader → Action Runner. This sprint introduces gesture recognition as an additional input source.

The Input Engine already tracks relative mouse movement (REL_X, REL_Y) but currently filters it out. Gesture recognition requires capturing this movement data while a gesture button is held, analyzing the cumulative displacement, and producing a Gesture domain object when the button is released.

The existing pipeline architecture supports this extension naturally: gesture recognition becomes a new component that produces Gesture objects, which flow through the same dispatch and resolution pipeline as button events.

## Goals / Non-Goals

**Goals:**
- Recognize four directional gestures (Up, Down, Left, Right) with deterministic logic
- Integrate gesture recognition into the existing pipeline without modifying core components
- Keep gesture recognition stateless between gesture attempts (no history or learning)
- Maintain backward compatibility with existing button-only configurations
- Provide clear user feedback when gestures are recognized

**Non-Goals:**
- Diagonal gestures (up-left, up-right, etc.) - future extension
- Multi-stroke gestures - future extension
- Gesture recording or custom gesture creation - out of scope
- Gesture sensitivity configuration - use fixed threshold initially
- Gesture visualization or UI feedback during gesture execution

## Decisions

### 1. Gesture Button Selection
**Decision:** Use a dedicated gesture button (BTN_EXTRA by default) to activate gesture mode.

**Rationale:** Separating gesture activation from regular buttons prevents accidental gesture triggers. BTN_EXTRA is chosen as default because it's commonly available on productivity mice and less frequently used than BTN_SIDE.

**Alternatives considered:**
- Use any button with modifier key (e.g., Shift+click) - adds complexity, requires keyboard coordination
- Use mouse movement threshold without button - causes false positives during normal use
- Make button configurable per-application - adds configuration complexity without clear benefit for MVP

### 2. Gesture Recognition Algorithm
**Decision:** Use simple threshold-based directional recognition:
- Track cumulative REL_X and REL_Y while gesture button is held
- When button releases, compare absolute values:
  - If |REL_X| > |REL_Y| and |REL_X| > threshold: Left or Right (based on sign)
  - If |REL_Y| > |REL_X| and |REL_Y| > threshold: Up or Down (based on sign)
  - Otherwise: no gesture recognized

**Rationale:** Simple, deterministic, easy to understand and test. Threshold prevents accidental triggers from small movements. Comparing absolute values ensures clear directional intent.

**Alternatives considered:**
- Velocity-based recognition - adds complexity, harder to tune
- Machine learning / pattern matching - over-engineering for four directions
- Angle-based recognition with sectors - more complex than needed for cardinal directions

### 3. Gesture Threshold
**Decision:** Use a fixed threshold of 50 pixels (configurable in code, not via config file initially).

**Rationale:** 50 pixels is large enough to prevent accidental triggers but small enough to feel responsive. Making it configurable adds complexity without clear benefit for MVP. Can be exposed in configuration later if needed.

**Alternatives considered:**
- Configurable threshold via YAML - adds configuration complexity
- Adaptive threshold based on screen resolution - over-engineering
- No threshold (any movement counts) - causes false positives

### 4. Gesture State Management
**Decision:** Gesture recognition state (cumulative movement, active flag) lives in a GestureRecognizer class that persists across events but resets when gesture button is released.

**Rationale:** State must persist across multiple REL_X/REL_Y events to accumulate movement. Resetting on button release ensures clean state for next gesture. Keeping state in a dedicated class maintains single responsibility.

**Alternatives considered:**
- Stateless recognition (analyze each event independently) - impossible, need cumulative movement
- Global state in Input Engine - violates single responsibility
- State in Event Dispatcher - wrong layer, dispatcher should be stateless

### 5. Pipeline Integration
**Decision:** GestureRecognizer sits between Input Engine and Event Dispatcher. It consumes raw events (button + movement) and produces either MouseEvent or Gesture objects, which flow into Event Dispatcher.

**Rationale:** Maintains pipeline architecture. GestureRecognizer is a transformation stage like Input Engine. Event Dispatcher doesn't need to know about gesture internals, just receives Gesture objects like it receives MouseEvent objects.

**Alternatives considered:**
- Integrate gesture recognition into Input Engine - violates single responsibility
- Integrate into Event Dispatcher - dispatcher should remain stateless
- Separate gesture pipeline parallel to button pipeline - adds complexity, duplicates resolution logic

### 6. Domain Model Extension
**Decision:** Add GestureDirection enum and Gesture dataclass to domain.py. Gesture contains direction field.

**Rationale:** Gesture is a first-class domain concept like MouseEvent. Using enum for direction provides type safety. Keeping Gesture simple (just direction) allows future extension (e.g., adding magnitude, duration) without breaking changes.

**Alternatives considered:**
- Represent gesture as special MouseEvent - conflates different concepts, loses type safety
- Use string for direction - loses type safety, allows invalid values
- Complex Gesture object with magnitude, duration, etc. - over-engineering for MVP

### 7. Configuration Format
**Decision:** Extend YAML configuration to support gesture mappings alongside button mappings:

```yaml
profiles:
  - app_name: firefox
    mappings:
      BTN_SIDE:
        type: keyboard
        payload: alt+left
    gestures:
      LEFT:
        type: keyboard
        payload: alt+left
      RIGHT:
        type: keyboard
        payload: alt+right
```

**Rationale:** Keeps gesture configuration close to button configuration for the same application. Using direction names (LEFT, RIGHT, etc.) is clear and maps directly to GestureDirection enum. Separate "gestures" section prevents confusion with button mappings.

**Alternatives considered:**
- Mix gestures and buttons in same mappings section - confusing, hard to distinguish
- Separate gesture configuration file - adds complexity, splits related config
- Use gesture names as strings in mappings - loses type safety

## Risks / Trade-offs

**[False positives from small movements]** → Mitigation: 50-pixel threshold prevents accidental triggers. If still problematic, threshold can be increased in code.

**[No diagonal gestures]** → Mitigation: Explicitly out of scope for MVP. Architecture supports future extension by adding more GestureDirection values.

**[Gesture button conflicts with other actions]** → Mitigation: BTN_EXTRA chosen as default because it's rarely used. If conflicts arise, button can be changed in code.

**[Movement tracking adds latency]** → Mitigation: Cumulative tracking is O(1) per event. Recognition only happens on button release. No performance impact on normal button events.

**[State management complexity]** → Mitigation: GestureRecognizer is a single class with clear state lifecycle (reset on button release). Easy to test and reason about.

**[Configuration format changes]** → Mitigation: Adding "gestures" section is backward compatible. Existing configurations without gestures continue to work.
