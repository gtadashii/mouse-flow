# PRD — Sprint 3

# Title

Window Resolver

---

# Objective

Enable MouseFlow to determine which application is currently focused.

At the end of this sprint, the application should continuously resolve the active window and expose its application name and window title.

This sprint focuses exclusively on window identification.

No mouse events are processed or associated with windows yet.

---

# Problem

MouseFlow is intended to execute different actions depending on the active application.

To support this behavior, the application must reliably identify which window currently has focus.

Without this capability, MouseFlow cannot provide application-specific behavior.

---

# User Story

As a Linux user,

I want MouseFlow to identify the currently focused application,

so that future versions can execute different actions depending on where I am working.

---

# Success Criteria

When MouseFlow is executed:

- the currently focused application is identified;
- the application name is displayed;
- the window title is displayed;
- the information reflects the current focused window.

---

# Scope

This sprint includes:

- obtaining information about the focused window;
- identifying the application name;
- identifying the window title;
- presenting the resolved information.

---

# Out of Scope

This sprint does not include:

- mouse event processing;
- event routing;
- configuration loading;
- action execution;
- application-specific mappings;
- caching or performance optimizations.

---

# Functional Requirements

## Active Window Resolution

The application shall determine which window currently has focus.

---

## Application Identification

The application shall expose the application identifier.

Example:

```text
Firefox
```

---

## Window Title

The application shall expose the current window title.

Example:

```text
ChatGPT
```

---

## User Feedback

The resolved information shall be presented in a human-readable format.

Example:

```text
Application

Firefox

Title

ChatGPT
```

---

# Non-functional Requirements

The solution should:

- return consistent results;
- require no user configuration;
- support future compositor integrations;
- isolate window resolution from other application components.

---

# Design Principles

This sprint should prioritize:

- reliability;
- compositor independence where practical;
- clean abstractions;
- separation of concerns;
- future extensibility.

---

# Expected Behavior

The user starts MouseFlow.

The application determines which window currently has focus.

The application retrieves the associated application name.

The application retrieves the current window title.

The resolved information is displayed to the user.

If the user changes focus to another application and requests the information again, the newly focused window is reported.

---

# Acceptance Criteria

The sprint is complete when:

- the focused application can be identified;
- the window title can be identified;
- the reported information matches the currently focused window;
- failures are handled gracefully without crashing the application.

---

# Risks

Potential challenges include:

- compositor-specific behavior;
- incomplete window metadata;
- unsupported desktop environments;
- future compatibility with additional compositors.

These challenges should not affect the public interface exposed by the Window Resolver.

---

# Future Work

The next sprint will combine mouse events and window information, allowing MouseFlow to determine which action should be executed for a specific application.
