# PRD — Sprint 4

# Title

Domain Model

---

# Objective

Establish a shared domain model that represents the core concepts of MouseFlow.

At the end of this sprint, the application should expose a consistent set of domain objects that can be shared across all future components.

No new end-user functionality is introduced.

This sprint focuses on creating the language of the application.

---

# Problem

The current components operate independently.

The Input Engine produces raw mouse events.

The Window Resolver produces information about the active window.

As the project grows, passing primitive values between components will increase coupling and make the codebase harder to understand and evolve.

A shared domain model provides a common vocabulary and clear boundaries between components.

---

# User Story

As a developer,

I want the application to expose well-defined domain objects,

so that future features can communicate through a consistent and type-safe API.

---

# Success Criteria

The project defines domain objects that represent the core concepts of MouseFlow.

Future components can exchange these objects without depending on implementation details from other modules.

---

# Scope

This sprint includes:

- defining the application's domain objects;
- establishing common terminology;
- creating immutable representations where appropriate;
- providing a stable foundation for future features.

---

# Out of Scope

This sprint does not include:

- event routing;
- configuration loading;
- action execution;
- serialization;
- persistence;
- plugin support.

---

# Functional Requirements

## Mouse Event

The application shall provide an object representing a mouse event.

---

## Application

The application shall provide an object representing the active application.

---

## Window

The application shall provide an object representing the active window.

---

## Action

The application shall provide an object representing an executable action.

The action is only modeled during this sprint.

It is not executed.

---

## Profile

The application shall provide an object representing an application profile.

---

## Shared Domain

All future components shall exchange information through the domain model instead of raw primitive values whenever appropriate.

---

# Non-functional Requirements

The solution should:

- be easy to understand;
- minimize coupling between components;
- maximize type safety;
- encourage immutability;
- support future evolution without breaking existing components.

---

# Design Principles

This sprint should prioritize:

- explicit modeling;
- strong typing;
- immutable objects where practical;
- separation between domain and infrastructure;
- readability over clever abstractions.

---

# Responsibilities

The Domain Model is responsible for:

- representing business concepts;
- defining the application's ubiquitous language;
- exposing stable objects shared by other modules.

The Domain Model is not responsible for:

- reading hardware events;
- communicating with the compositor;
- executing actions;
- loading configuration files;
- interacting with the operating system.

---

# Expected Behavior

The application starts normally.

The Input Engine produces a mouse event.

Instead of exposing raw values, the event is represented by a domain object.

The Window Resolver identifies the focused application.

Instead of exposing implementation-specific data, the result is represented by domain objects.

Future components consume these domain objects without needing to understand how they were created.

---

# Acceptance Criteria

The sprint is complete when:

- the core domain concepts are represented by dedicated objects;
- domain objects are independent from infrastructure implementations;
- components exchange domain objects instead of raw structures whenever practical;
- the public domain API is clear and consistent.

---

# Risks

Potential challenges include:

- modeling concepts too early;
- introducing unnecessary abstractions;
- coupling domain objects to infrastructure concerns.

The preferred solution is the simplest domain model capable of supporting the upcoming sprints.

---

# Future Work

The next sprint will introduce the Event Dispatcher, which will combine mouse events and window information using the shared domain model.
