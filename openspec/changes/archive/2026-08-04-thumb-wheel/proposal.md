## Why

Modern mice provide horizontal thumb wheels that generate continuous input, but MouseFlow currently conflates thumb wheel events with gesture identifiers (REL_HWHEEL maps to GESTURE_LEFT/GESTURE_RIGHT). Thumb wheel interactions need their own identity in the domain model and pipeline so users can assign distinct actions to thumb wheel movements independent of gestures.

## What Changes

- Introduce dedicated thumb wheel input identifiers (`THUMB_WHEEL_LEFT`, `THUMB_WHEEL_RIGHT`) in the domain model, separate from gesture identifiers.
- Update the Input Engine to recognize thumb wheel events (REL_HWHEEL) and produce `UserInput` objects with thumb wheel identifiers instead of gesture identifiers.
- Ensure thumb wheel `UserInput` objects flow through the existing action resolution pipeline (dispatcher, profile resolver, configuration loader, action runner) without modification to those components.
- Support configuration of thumb wheel actions in user profiles via YAML.

## Capabilities

### New Capabilities
- `thumb-wheel-recognition`: Recognizes thumb wheel movement from raw device events, determines direction (left/right), and produces thumb wheel `UserInput` domain objects for the pipeline.

### Modified Capabilities
- `domain-model`: Add `THUMB_WHEEL_LEFT` and `THUMB_WHEEL_RIGHT` values to `InputIdentifier` enum to represent thumb wheel directions as distinct input types.
- `input-engine`: Change REL_HWHEEL event conversion to produce thumb wheel `UserInput` identifiers instead of gesture identifiers.

## Impact

- **Domain model** (`domain.py`): New `InputIdentifier` enum values.
- **Input Engine** (`engine.py`): Updated `mouse_event_to_userinput` mapping for wheel events.
- **Configuration Parser** (`parser.py`): Must accept thumb wheel identifiers in YAML mappings.
- **User configuration**: Users can now define thumb wheel action mappings in their profiles.
- **No impact** on Event Dispatcher, Profile Resolver, Action Runner, or Window Resolver — they operate on `UserInput`/`InputIdentifier` and remain agnostic.
