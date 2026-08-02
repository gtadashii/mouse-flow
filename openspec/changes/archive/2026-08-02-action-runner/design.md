## Context

The Configuration Loader resolves actions from DispatchContext objects, producing Action domain objects. See proposal.md for motivation. The Action Runner is the final stage of the pipeline, responsible for executing these actions on the operating system.

## Goals / Non-Goals

**Goals:**
- Execute keyboard shortcuts with minimal latency
- Execute shell commands in the user's environment
- Launch applications as separate processes
- Report execution results clearly
- Handle failures gracefully without terminating the application
- Isolate execution from the event pipeline

**Non-Goals:**
- Gesture recognition or interpretation
- Macro recording or playback
- Configuration reloading at runtime
- Plugin system for custom action types
- Complex workflow automation

## Decisions

### 1. Keyboard simulation library
**Decision**: Use `pynput` for keyboard simulation.
**Rationale**: Cross-platform, well-maintained, provides both keyboard and mouse control. Works on Wayland with appropriate permissions. Simpler API than raw evdev for keyboard simulation.
**Alternatives considered**: 
- `python-xlib` (X11 only, doesn't work on Wayland)
- Raw evdev injection (requires root, complex setup)
- `xdotool` subprocess (X11 only, adds process overhead)

### 2. Shell command execution
**Decision**: Use `subprocess.run()` with `shell=True` for command execution.
**Rationale**: Simple, well-understood, inherits user's shell environment. Sufficient for the use case (swaymsg, application launchers, etc.).
**Alternatives considered**:
- `subprocess.Popen()` with `shell=False` (more secure but requires parsing commands manually)
- `os.system()` (deprecated, less control)

### 3. Asynchronous execution
**Decision**: Execute actions synchronously in the current implementation, but design the interface to allow future async execution.
**Rationale**: Most actions (keyboard shortcuts, quick commands) are fast. Async adds complexity. If long-running commands become a problem, we can add async later without changing the interface.
**Alternatives considered**:
- Always async with asyncio (adds complexity, may be premature)
- Thread pool for all actions (overkill for fast actions)

### 4. Error handling strategy
**Decision**: Catch all exceptions at the Action Runner boundary, log them, and continue processing.
**Rationale**: The event pipeline must remain responsive. A failed action should not prevent future events from being processed. Errors should be visible to the user but not fatal.
**Alternatives considered**:
- Let exceptions propagate (would terminate the application)
- Return Result types (adds complexity without clear benefit)

### 5. Execution result reporting
**Decision**: Print execution results to stdout in a structured format.
**Rationale**: Simple, visible to the user, can be parsed by external tools if needed. Matches the existing pattern used by other components (e.g., format_dispatch_context).
**Alternatives considered**:
- Logging module (more complex, may be overkill)
- GUI notifications (adds dependency, not needed for MVP)

### 6. Action type dispatch
**Decision**: Use a simple if/elif chain based on ActionType enum.
**Rationale**: Only two action types currently (KEYBOARD, COMMAND). Simple and clear. Can be refactored to a registry pattern if more types are added.
**Alternatives considered**:
- Strategy pattern with action handlers (over-engineering for 2 types)
- Registry with decorators (unnecessary complexity)

## Risks / Trade-offs

- **[Wayland permissions]** → Mitigation: Document required permissions. Test on actual Wayland environment. Provide clear error messages if permissions are missing.
- **[Keyboard simulation reliability]** → Mitigation: Test with various keyboard layouts. Handle edge cases (e.g., special characters). Provide fallback to command-based execution if needed.
- **[Long-running commands]** → Mitigation: Monitor execution times. If this becomes a problem, add async execution or timeout mechanism.
- **[Security of shell commands]** → Mitigation: Commands come from user configuration, not untrusted sources. Document security implications. Consider adding command validation in the future.
- **[Error visibility]** → Mitigation: Ensure errors are printed clearly. Consider adding a verbose mode for debugging.
