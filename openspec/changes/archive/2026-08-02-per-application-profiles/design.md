## Context

The Configuration Loader currently resolves actions by looking up application-specific profiles directly. With the introduction of per-application profiles and a global fallback, a new profile resolution layer is needed to select the appropriate profile before action resolution occurs.

The domain model already supports multiple profiles via the `Configuration` object, which contains a collection of `Profile` objects. The `WindowResolver` provides the focused application name via `WindowInfo`. The challenge is to introduce profile selection logic that respects precedence rules while maintaining the existing pipeline structure.

## Goals / Non-Goals

**Goals:**
- Introduce deterministic profile selection with application-specific profiles taking priority over global
- Provide global profile fallback when no application-specific profile matches
- Maintain backward compatibility with existing application-specific configurations
- Keep profile resolution logic separate from action resolution logic
- Report which profile was selected for user feedback

**Non-Goals:**
- Profile inheritance or merging between profiles
- Runtime profile reloading or editing
- Multiple global profiles or complex precedence chains
- Profile synchronization across multiple configuration sources

## Decisions

### 1. Profile resolution location
**Decision:** Create a new `ProfileResolver` component that sits between the Event Dispatcher and Configuration Loader in the pipeline.
**Rationale:** Separates profile selection from action resolution, maintaining single responsibility. The Configuration Loader remains focused on resolving actions from a given profile, while ProfileResolver handles profile selection.
**Alternatives considered:**
- Embed profile resolution in Configuration Loader (mixes concerns, makes loader responsible for both profile selection and action resolution)
- Embed profile resolution in Event Dispatcher (dispatcher should focus on combining events with window context, not profile selection)

### 2. Global profile representation
**Decision:** Represent the global profile as a special `Profile` object with a reserved app_name (e.g., `"global"` or `"*"`).
**Rationale:** Reuses existing domain objects, maintains consistency with the domain model, and avoids introducing new concepts. The Configuration Parser translates the `global:` YAML key into a Profile with the reserved name.
**Alternatives considered:**
- Separate `GlobalProfile` domain object (adds complexity, breaks symmetry with application profiles)
- Implicit global profile (no explicit representation, harder to test and reason about)

### 3. Profile resolution interface
**Decision:** Define a `ProfileResolver` protocol with a `resolve(configuration: Configuration, window_info: WindowInfo | None) -> Profile | None` method.
**Rationale:** Follows the existing pattern used by `WindowResolver` (protocol-based dependency inversion). Enables testing with mocks and future compositor support. Returns `Profile | None` to handle the case where no profile is available.
**Alternatives considered:**
- Return `Profile` with empty mappings (hides the "no profile" case, makes it harder to report)
- Raise exception when no profile found (breaks pipeline flow, requires exception handling)

### 4. Configuration format
**Decision:** Support a `global:` key at the top level of the YAML configuration alongside application-specific profiles.
**Rationale:** Clear and explicit syntax. Easy to parse and validate. Maintains backward compatibility (existing configs without `global:` continue to work).
**Example:**
```yaml
global:
  BTN_SIDE:
    keyboard: alt+left

firefox:
  BTN_SIDE:
    keyboard: alt+left

vscode:
  BTN_SIDE:
    keyboard: ctrl+-
```
**Alternatives considered:**
- Use a special application name like `"*"` in config (less intuitive, harder to document)
- Separate config file for global profile (adds complexity, harder to manage)

### 5. Pipeline integration
**Decision:** The ProfileResolver receives `Configuration` and `WindowInfo`, and returns the selected `Profile`. The Configuration Loader then receives the selected `Profile` and `DispatchContext` to resolve the action.
**Rationale:** Maintains clear pipeline stages. ProfileResolver selects the profile, Configuration Loader resolves the action. Each component has a single responsibility.
**Alternatives considered:**
- ProfileResolver returns `Action | None` directly (combines profile selection and action resolution, loses visibility into which profile was selected)

## Risks / Trade-offs

- **[Global profile name collision]** → Mitigation: Reserve a specific name (e.g., `"global"`) and validate that no application uses this name. Report clear error if collision detected.
- **[Precedence complexity]** → Mitigation: Keep precedence rules simple (application-specific always wins). Document clearly. Avoid inheritance or merging.
- **[Backward compatibility]** → Mitigation: Existing configs without `global:` key continue to work unchanged. ProfileResolver returns `None` when no profile matches and no global exists.
- **[Profile visibility]** → Mitigation: ProfileResolver reports which profile was selected. This information flows through the pipeline for user feedback.
