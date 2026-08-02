# PRD — Sprint 5

# Title

Event Dispatcher

---

# Objective

Combine mouse input events with the currently focused application and produce a unified event context.

At the end of this sprint, MouseFlow should associate every supported mouse event with the active application and report the resulting context.

This sprint introduces the application's first orchestration component.

No configuration lookup or action execution is performed.

---

# Problem

The Input Engine and the Window Resolver currently operate independently.

Although both components work correctly, they provide isolated pieces of information.

Future features require a single representation containing both:

- the mouse interaction;
- the application where it occurred.

Without this orchestration layer, later components would need to coordinate multiple data sources themselves, increasing coupling and complexity.

---

# User Story

As a developer,

I want MouseFlow to combine mouse events with the active application,

so that future components can decide which action should be executed.

---

# Success Criteria

Whenever a supported mouse event occurs:

- the active application is resolved;
- a unified event context is created;
- the resulting context is displayed.

---

# Scope

This sprint includes:

- receiving domain events from the Input Engine;
- obtaining the current application from the Window Resolver;
- combining both pieces of information;
- exposing the resulting event context.

---

# Out of Scope

This sprint does not include:

- configuration loading;
- action resolution;
- keyboard simulation;
- shell execution;
- gesture recognition;
- application-specific mappings.

---

# Functional Requirements

## Event Reception

The dispatcher shall receive mouse events from the Input Engine.

---

## Window Resolution

For each received event, the dispatcher shall obtain the currently focused application.

---

## Event Context

The dispatcher shall create a unified domain object representing the interaction.

The context should contain, at minimum:

- mouse event;
- application;
- window information.

---

## User Feedback

The resulting context shall be displayed in a human-readable format.

Example:

```text
Application: Firefox

Title: ChatGPT

Event: BTN_SIDE
```

---

## Event Independence

Each mouse event shall be processed independently.

No event history or state management is required.

---

# Non-functional Requirements

The solution should:

- introduce minimal latency;
- remain independent from infrastructure implementations;
- avoid unnecessary coupling between components;
- be easy to extend with future context information.

---

# Design Principles

This sprint should prioritize:

- orchestration over business logic;
- composition over duplication;
- explicit data flow;
- clear component boundaries.

---

# Responsibilities

The Event Dispatcher is responsible for:

- receiving domain events;
- requesting the current application context;
- combining information from multiple components;
- producing a unified event context.

The Event Dispatcher is not responsible for:

- deciding which action should be executed;
- loading configuration;
- executing actions;
- interpreting gestures;
- interacting directly with operating system APIs.

---

# Expected Behavior

The application starts normally.

The Input Engine receives a supported mouse event.

The Event Dispatcher requests the currently focused application.

The dispatcher combines both pieces of information into a single domain object.

The resulting event context is displayed to the user.

The application continues waiting for the next mouse event.

---

# Acceptance Criteria

The sprint is complete when:

- every supported mouse event is associated with the currently focused application;
- the unified event context is produced for every event;
- no infrastructure details leak outside the dispatcher;
- the dispatcher depends only on domain abstractions;
- the resulting context is displayed correctly.

---

# Risks

Potential challenges include:

- synchronization between event reception and window resolution;
- unnecessary coupling between components;
- introducing business logic into the dispatcher.

The dispatcher should remain a thin orchestration layer.

---

# Future Work

The next sprint will introduce configuration loading, allowing MouseFlow to determine which action is associated with each dispatched event.
