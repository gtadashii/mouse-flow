# PRD — Sprint 8

# Title

Per-Application Profiles

---

# Objective

Enable MouseFlow to support different configurations for different applications.

At the end of this sprint, the application should resolve the appropriate profile based on the currently focused application before selecting an action.

This allows the same mouse interaction to produce different behaviors depending on the active application.

---

# Problem

A single global configuration is sufficient for simple use cases, but it limits the flexibility of the application.

Users often expect the same mouse button to perform different actions depending on the application they are currently using.

To support this behavior, MouseFlow must introduce application-specific profiles while preserving predictable resolution rules.

---

# User Story

As a Linux user,

I want different applications to have different mouse mappings,

so that my mouse behaves according to the context in which I am working.

---

# Success Criteria

When a mouse event occurs:

- the active application is identified;
- the corresponding profile is selected;
- the action is resolved using that profile;
- if no application-specific profile exists, the global profile is used.

---

# Scope

This sprint includes:

- application-specific profiles;
- global profile fallback;
- profile resolution;
- deterministic precedence rules.

---

# Out of Scope

This sprint does not include:

- profile inheritance;
- profile editing;
- profile reloading;
- multiple configuration files;
- profile synchronization.

---

# Functional Requirements

## Profile Resolution

The application shall determine which profile applies to the current application.

---

## Application Profiles

Users shall be able to define mappings that are specific to an application.

---

## Global Profile

The application shall support a global profile used when no application-specific profile matches.

---

## Resolution Order

Profile selection shall follow deterministic precedence rules.

Application-specific mappings shall take priority over global mappings.

---

## User Feedback

The application shall report which profile was selected.

Example:

```text
Application: Firefox

Profile: firefox

Event: BTN_SIDE

Action: Alt+Left
```

---

# Non-functional Requirements

The solution should:

- provide deterministic profile resolution;
- remain easy to understand;
- avoid duplicated configuration;
- support future profile extensions.

---

# Design Principles

This sprint should prioritize:

- predictability;
- explicit configuration;
- clear precedence rules;
- minimal user surprise.

---

# Responsibilities

The profile resolution layer is responsible for:

- selecting the appropriate profile;
- applying precedence rules;
- providing the selected profile to the configuration resolution process.

It is not responsible for:

- executing actions;
- parsing configuration files;
- interacting with the operating system.

---

# Expected Behavior

The application starts.

Configuration is loaded.

The user presses a configured mouse button.

The active application is identified.

MouseFlow selects the matching application profile.

If no matching profile exists, the global profile is selected.

The resolved profile is used to determine the appropriate action.

The action is executed.

The application continues processing future events.

---

# Acceptance Criteria

The sprint is complete when:

- application-specific profiles are supported;
- a global fallback profile is available;
- precedence rules are deterministic;
- profile selection is reported correctly;
- existing global configurations continue to work.

---

# Risks

Potential challenges include:

- ambiguous application identification;
- conflicting mappings;
- precedence complexity;
- future support for profile inheritance.

The resolution process should remain simple and predictable.

---

# Future Work

The next sprint will introduce mouse gestures, allowing continuous pointer movement to become an additional source of actions.
