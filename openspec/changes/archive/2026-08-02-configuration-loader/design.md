## Context

The Event Dispatcher produces DispatchContext objects, but the application lacks user preferences. See proposal.md for motivation. The Configuration Loader sits between the Event Dispatcher and the future Action Runner in the pipeline.

## Goals / Non-Goals

**Goals:**
- Load YAML configuration into domain objects (Profile, Action)
- Validate configuration structure and report clear errors
- Resolve DispatchContext to an Action or report no match
- Keep configuration parsing isolated from the domain model

**Non-Goals:**
- Executing actions (deferred to Sprint 7)
- Configuration reloading at runtime
- Configuration editing or generation
- Supporting configuration formats other than YAML

## Decisions

### 1. YAML as configuration format
**Decision**: Use YAML for user configuration files.
**Rationale**: YAML is human-readable, widely used for configuration in Linux tools, and has good Python library support (PyYAML). It balances readability with sufficient structure for nested mappings.
**Alternatives considered**: TOML (less common for complex nested structures), JSON (less human-friendly for manual editing), INI (insufficient for nested mappings).

### 2. Configuration file location
**Decision**: Load configuration from `~/.config/mouseflow/config.yaml` following XDG Base Directory Specification.
**Rationale**: Standard location for user configuration on Linux, predictable for users, follows platform conventions.
**Alternatives considered**: Custom path via CLI flag (adds complexity, defer to future), current directory (not user-friendly for a daemon).

### 3. Validation strategy
**Decision**: Validate configuration structure immediately after loading, before converting to domain objects. Use explicit validation functions that return structured errors.
**Rationale**: Separates validation logic from parsing and domain conversion, makes errors clear and testable, prevents partial state.
**Alternatives considered**: Validate during parsing (couples parsing to validation), validate lazily on resolution (delays error discovery).

### 4. Resolution approach
**Decision**: Use a simple dictionary lookup: application name → Profile → event key → Action. Return None if any lookup fails.
**Rationale**: Deterministic, O(1) lookup, easy to understand and test. Matches the domain model structure directly.
**Alternatives considered**: Pattern matching or glob-based application names (adds complexity, defer to future), priority-based rule ordering (unnecessary for initial implementation).

### 5. Error reporting
**Decision**: Raise custom exceptions (ConfigurationError, ValidationError) with descriptive messages. The application layer catches and reports these to the user.
**Rationale**: Clear separation between infrastructure errors and domain logic, testable error conditions, actionable error messages for users.
**Alternatives considered**: Return Result/Either types (adds complexity without clear benefit in Python), print errors directly (couples loader to output).

## Risks / Trade-offs

- **[YAML parsing errors]** → Mitigation: Validate structure explicitly after parsing, catch PyYAML exceptions and wrap in ConfigurationError with file/line context.
- **[Configuration file permissions]** → Mitigation: Check file readability before loading, report clear error if file cannot be read.
- **[Future action type extensions]** → Mitigation: Use ActionType enum in domain model, validation rejects unknown types explicitly, making future additions straightforward.
- **[Application name matching]** → Mitigation: Start with exact string matching. Future work can add pattern matching or aliases without changing the core resolution logic.
