## Context

MouseFlow processes input through a pipeline: raw evdev events → Input Engine → UserInput → Event Dispatcher → Profile Resolver → Configuration Loader → Action Runner. Currently, REL_HWHEEL events are mapped to GESTURE_LEFT/GESTURE_RIGHT identifiers, conflating thumb wheel input with gesture input. See proposal.md for motivation.

## Goals / Non-Goals

**Goals:**
- Introduce dedicated thumb wheel identifiers in the domain model
- Route REL_HWHEEL events to thumb wheel identifiers instead of gesture identifiers
- Maintain pipeline compatibility — no changes to dispatcher, profile resolver, action runner, or action executor
- Support thumb wheel mappings in YAML configuration

**Non-Goals:**
- Configurable sensitivity or acceleration curves
- Momentum, inertia, or analog value customization
- Gesture combinations involving thumb wheel
- Vertical wheel (REL_WHEEL) support — already handled or out of scope

## Decisions

### Decision 1: New InputIdentifier values instead of reusing gesture identifiers

**Choice:** Add `THUMB_WHEEL_LEFT` and `THUMB_WHEEL_RIGHT` to the `InputIdentifier` enum.

**Alternatives considered:**
- Reuse `GESTURE_LEFT`/`GESTURE_RIGHT` — rejected because thumb wheel and gestures are semantically different inputs. Users need independent mappings (e.g., thumb wheel changes tabs, gesture switches workspaces).
- Create a separate `ThumbWheelInput` domain object — rejected because it breaks the unified `UserInput` pipeline. The existing design already handles diverse inputs (buttons, gestures, wheel) through a single `UserInput` with `InputIdentifier`.

**Rationale:** Adding enum values is the minimal change that preserves the unified pipeline while giving thumb wheel its own identity. Configuration, profile resolution, and action resolution all work via `InputIdentifier` — no downstream changes needed.

### Decision 2: Update existing REL_HWHEEL mapping in Input Engine

**Choice:** Modify `mouse_event_to_userinput` to map `WheelAxis.REL_HWHEEL` to `THUMB_WHEEL_LEFT`/`THUMB_WHEEL_RIGHT` instead of `GESTURE_LEFT`/`GESTURE_RIGHT`.

**Alternatives considered:**
- Create a separate conversion function for thumb wheel — rejected because the existing function already handles wheel events; splitting adds unnecessary complexity.
- Add a new `WheelEvent` internal type — rejected because `MouseEvent` with `EventType.WHEEL` already represents wheel events adequately.

**Rationale:** Single-function mapping keeps the conversion logic centralized and easy to follow. The change is a simple value swap in the mapping dictionary.

### Decision 3: No new pipeline components

**Choice:** Thumb wheel UserInput objects flow through the existing pipeline without new stages.

**Rationale:** The pipeline is identifier-agnostic. Event Dispatcher combines UserInput with WindowInfo, Profile Resolver selects profiles, Configuration Loader looks up mappings by InputIdentifier, and Action Runner executes actions. None of these need to know whether the identifier came from a button, gesture, or thumb wheel.

## Risks / Trade-offs

- **[Breaking change for existing configs]** Users who mapped GESTURE_LEFT/GESTURE_RIGHT expecting thumb wheel behavior will need to update their configs to use THUMB_WHEEL_LEFT/THUMB_WHEEL_RIGHT. → Mitigation: This is the correct semantic separation. Document the change clearly.
- **[Hardware variability]** Different mice may report thumb wheel events differently (some may use REL_WHEEL instead of REL_HWHEEL). → Mitigation: Out of scope for this sprint. The current implementation targets REL_HWHEEL which is the standard thumb wheel axis. Future hardware support can be added as needed.
