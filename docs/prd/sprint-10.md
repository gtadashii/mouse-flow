# PRD — Sprint 10

# Title

Thumb Wheel

---

# Objective

Enable MouseFlow to recognize thumb wheel interactions and resolve them as executable actions.

At the end of this sprint, users should be able to associate horizontal thumb wheel movements with different actions depending on the active application.

Thumb wheel interactions become an additional input source within the existing action resolution pipeline.

---

# Problem

Modern mice provide horizontal thumb wheels capable of generating continuous input.

Unlike mouse buttons, thumb wheel interactions represent a stream of movement rather than a single event.

To fully support programmable mice, MouseFlow must recognize thumb wheel movement and integrate it into the existing action resolution process.

---

# User Story

As a Linux user,

I want to assign actions to my mouse thumb wheel,

so that I can perform continuous interactions such as changing browser tabs or navigating editors more efficiently.

---

# Success Criteria

When the thumb wheel is moved:

- movement is recognized;
- the movement direction is determined;
- the configured action is resolved;
- the corresponding action is executed.

---

# Scope

This sprint includes:

- thumb wheel recognition;
- movement direction detection;
- continuous input handling;
- action resolution using thumb wheel events.

---

# Out of Scope

This sprint does not include:

- configurable sensitivity;
- acceleration curves;
- momentum or inertia;
- gesture combinations;
- analog value customization.

---

# Functional Requirements

## Thumb Wheel Recognition

The application shall recognize thumb wheel interactions.

---

## Direction Detection

The application shall determine the direction of movement.

Initial supported directions include:

- Left
- Right

---

## Continuous Processing

Thumb wheel movement shall be processed as a continuous interaction.

The application shall remain responsive while the wheel is being moved.

---

## Action Resolution

Thumb wheel interactions shall participate in the existing action resolution pipeline.

---

## User Feedback

The recognized movement shall be reported.

Example:

```text
Application: Firefox

Thumb Wheel: Right

Action: Next Tab
```

---

# Non-functional Requirements

The solution should:

- respond with minimal latency;
- avoid unnecessary processing during continuous movement;
- remain deterministic;
- support future improvements to continuous input handling.

---

# Design Principles

This sprint should prioritize:

- responsiveness;
- predictable behavior;
- smooth continuous processing;
- separation between input recognition and action execution.

---

# Responsibilities

The thumb wheel input layer is responsible for:

- recognizing thumb wheel movement;
- determining movement direction;
- producing thumb wheel domain objects.

It is not responsible for:

- executing actions;
- loading configuration;
- deciding which action should be executed.

---

# Expected Behavior

The application starts.

The user rotates the thumb wheel.

MouseFlow recognizes the continuous movement.

The movement direction is identified.

A thumb wheel domain object is produced.

The interaction enters the existing action resolution pipeline.

The configured action is executed.

The application continues processing future thumb wheel interactions.

---

# Acceptance Criteria

The sprint is complete when:

- thumb wheel movement is recognized;
- movement direction is correctly identified;
- thumb wheel interactions participate in the action resolution pipeline;
- continuous movement does not interrupt normal application execution;
- application-specific mappings are respected.

---

# Risks

Potential challenges include:

- noisy continuous input;
- excessive event generation;
- inconsistent hardware behavior;
- future support for configurable sensitivity.

The implementation should remain simple while providing a solid foundation for future continuous input improvements.

---

# Future Work

The next sprint will introduce daemon mode, allowing MouseFlow to run continuously as a background service.
