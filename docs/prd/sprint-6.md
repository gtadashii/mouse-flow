# PRD — Sprint 6

# Title

Configuration Loader

---

# Objective

Enable MouseFlow to load user-defined mappings and resolve which action, if any, should be associated with a dispatched event.

At the end of this sprint, the application should determine whether a dispatched event matches a configured action.

No actions are executed during this sprint.

---

# Problem

The Event Dispatcher produces a complete event context containing information about the mouse interaction and the active application.

However, the application still has no knowledge of user preferences.

A configuration layer is required to translate user-defined mappings into domain objects that can be consumed by future components.

---

# User Story

As a Linux user,

I want MouseFlow to load my configuration,

so that the application knows which action should be executed for each mouse interaction.

---

# Success Criteria

When an event context is produced:

- the user configuration is consulted;
- the matching rule is identified, if one exists;
- a resolved action is returned;
- if no rule matches, the application reports that no action is configured.

---

# Scope

This sprint includes:

- loading configuration files;
- validating configuration data;
- resolving mappings;
- producing resolved actions.

---

# Out of Scope

This sprint does not include:

- keyboard simulation;
- shell execution;
- launching applications;
- gesture recognition;
- configuration reloading;
- configuration editing.

---

# Functional Requirements

## Configuration Loading

The application shall load user-defined configuration during startup.

---

## Configuration Validation

Invalid configuration shall be detected and reported.

The application should provide clear feedback when configuration cannot be loaded.

---

## Action Resolution

Given a dispatched event context, the application shall determine whether a matching action exists.

---

## Resolved Action

When a mapping exists, the application shall produce a domain object representing the resolved action.

The action is only resolved during this sprint.

It is not executed.

---

## Missing Configuration

When no mapping matches the current context, the application shall report that no action was found.

Example:

```text
Application: Firefox

Event: BTN_SIDE

No action configured.
```

---

# Non-functional Requirements

The solution should:

- support future configuration extensions;
- isolate configuration parsing from the domain model;
- provide deterministic rule resolution;
- remain easy to understand and maintain.

---

# Design Principles

This sprint should prioritize:

- explicit configuration;
- predictable resolution;
- clear validation errors;
- separation between configuration format and domain objects.

---

# Responsibilities

The Configuration Loader is responsible for:

- loading user configuration;
- validating configuration;
- translating configuration into domain objects;
- resolving which action matches a dispatched context.

The Configuration Loader is not responsible for:

- executing actions;
- interacting with operating system APIs;
- reading mouse events;
- determining the active window.

---

# Expected Behavior

The application starts.

The user configuration is loaded successfully.

A mouse event occurs.

The Event Dispatcher produces a dispatch context.

The Configuration Loader searches for a matching rule.

If a rule exists, a resolved action is produced.

If no rule exists, the application reports that no action was configured.

The application continues processing future events.

---

# Acceptance Criteria

The sprint is complete when:

- configuration can be loaded successfully;
- invalid configuration is reported gracefully;
- dispatched events can be matched against configuration;
- a resolved action is produced when a rule exists;
- the absence of a matching rule is handled correctly.

---

# Risks

Potential challenges include:

- invalid configuration files;
- ambiguous mappings;
- future compatibility with new action types;
- coupling configuration format to the domain model.

Configuration parsing should remain isolated from the rest of the application.

---

# Future Work

The next sprint will introduce the Action Runner, responsible for executing resolved actions.
