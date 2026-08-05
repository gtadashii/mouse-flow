## 1. Domain Model — Thumb Wheel Identifiers

- [x] 1.1 Write failing tests for THUMB_WHEEL_LEFT and THUMB_WHEEL_RIGHT in InputIdentifier enum
- [x] 1.2 Add THUMB_WHEEL_LEFT and THUMB_WHEEL_RIGHT to InputIdentifier enum in domain.py
- [x] 1.3 Verify tests pass and confirm identifiers are distinct from GESTURE_LEFT/GESTURE_RIGHT

## 2. Input Engine — Thumb Wheel Event Conversion

- [x] 2.1 Write failing tests for mouse_event_to_userinput mapping REL_HWHEEL positive value to THUMB_WHEEL_RIGHT
- [x] 2.2 Write failing tests for mouse_event_to_userinput mapping REL_HWHEEL negative value to THUMB_WHEEL_LEFT
- [x] 2.3 Update mouse_event_to_userinput in engine.py to map REL_HWHEEL to THUMB_WHEEL_LEFT/THUMB_WHEEL_RIGHT instead of GESTURE_LEFT/GESTURE_RIGHT
- [x] 2.4 Verify all engine tests pass

## 3. Configuration Parser — Thumb Wheel Mapping Support

- [x] 3.1 Write failing test for parsing a YAML config with THUMB_WHEEL_LEFT and THUMB_WHEEL_RIGHT mappings
- [x] 3.2 Verify parser resolves thumb wheel identifiers correctly (no code changes expected — InputIdentifier lookup is automatic)

## 4. Integration Verification

- [x] 4.1 Run full test suite to confirm no regressions
- [x] 4.2 Run linter and type checker to confirm code quality
