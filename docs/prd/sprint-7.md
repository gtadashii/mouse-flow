# PRD — Sprint 7

# Title

Action Runner

---

# Objective

Enable MouseFlow to execute actions previously resolved by the Configuration Loader.

At the end of this sprint, configured mouse interactions should produce visible effects on the operating system.

The Action Runner is responsible only for executing actions.

It does not decide which action should be executed.

---

# Problem

The application is now capable of:

- detecting mouse events;
- identifying the focused application;
- resolving the appropriate action.

However, no action is actually performed.

A dedicated execution layer is required to translate resolved actions into operating system interactions.

---

# User Story

As a Linux user,

I want MouseFlow to execute the action configured for my mouse interaction,

so that my mouse buttons become programmable.

---

# Success Criteria

When a resolved action is produced:

- the corresponding action is executed;
- the execution is reported;
- execution failures are handled gracefully;
- the application continues processing future events.

---

# Scope

This sprint includes:

- executing keyboard shortcuts;
- executing shell commands;
- launching applications;
- reporting execution results.

---

# Out of Scope

This sprint does not include:

- gesture recognition;
- thumb wheel interpretation;
- configuration reloading;
- macros;
- plugin support.

---

# Functional Requirements

## Keyboard Actions

The application shall execute configured keyboard shortcuts.

---

## Shell Actions

The application shall execute configured shell commands.

---

## Application Launch

The application shall launch configured applications.

---

## Execution Feedback

The application shall report the executed action.

Example:

```text
Application: Firefox

Event: BTN_SIDE

Action: Alt+Left

Status: Executed
```

---

## Failure Handling

Execution failures shall be reported without terminating the application.

The application shall continue processing future events.

---

# Non-functional Requirements

The solution should:

- execute actions with minimal latency;
- isolate operating system interactions;
- remain extensible for future action types;
- prevent execution failures from affecting the event pipeline.

---

# Design Principles

This sprint should prioritize:

- separation between resolution and execution;
- explicit execution flow;
- reliability;
- extensibility;
- minimal coupling.

---

# Responsibilities

The Action Runner is responsible for:

- receiving resolved actions;
- executing operating system interactions;
- reporting execution results.

The Action Runner is not responsible for:

- loading configuration;
- interpreting mouse events;
- determining the active application;
- deciding which action should be executed.

---

# Expected Behavior

The application starts.

The user presses a configured mouse button.

The Input Engine produces a MouseEvent.

The Event Dispatcher produces a DispatchContext.

The Configuration Loader resolves the configured action.

The Action Runner receives the resolved action.

The configured action is executed.

The application continues waiting for the next event.

---

# Acceptance Criteria

The sprint is complete when:

- keyboard shortcuts can be executed;
- shell commands can be executed;
- applications can be launched;
- execution failures do not terminate the application;
- the pipeline remains responsive after repeated executions.

---

# Risks

Potential challenges include:

- operating system permissions;
- unavailable external commands;
- execution failures;
- future action types.

The Action Runner should remain a generic execution layer capable of supporting additional action implementations without changing the rest of the application.

---

# Future Work

The next sprint will introduce per-application profiles, allowing different configurations to coexist depending on the active application.
