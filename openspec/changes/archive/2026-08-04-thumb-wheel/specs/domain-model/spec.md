## ADDED Requirements

### Requirement: Thumb wheel input identifiers
The system SHALL provide distinct input identifiers for thumb wheel directions.

#### Scenario: Thumb wheel left identifier exists
- **WHEN** the domain model is loaded
- **THEN** InputIdentifier contains the value THUMB_WHEEL_LEFT

#### Scenario: Thumb wheel right identifier exists
- **WHEN** the domain model is loaded
- **THEN** InputIdentifier contains the value THUMB_WHEEL_RIGHT

#### Scenario: Thumb wheel identifiers are distinct from gesture identifiers
- **WHEN** the domain model is loaded
- **THEN** THUMB_WHEEL_LEFT and THUMB_WHEEL_RIGHT are separate enum values from GESTURE_LEFT and GESTURE_RIGHT
