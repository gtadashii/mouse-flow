## Context

The project has device discovery working (Sprint 1). The application can find and identify a supported mouse. Now we need to continuously read events from that device.

Constraints:
- Python 3.13+
- evdev library for input device access
- Must work on Linux/Wayland (primary target: Sway)
- Requires access to /dev/input devices
- Application must run continuously until interrupted

## Goals / Non-Goals

**Goals:**
- Open the selected device and maintain a handle
- Read events continuously in a loop
- Filter for supported event types (BTN_SIDE, BTN_EXTRA, BTN_FORWARD, REL_HWHEEL)
- Display event names in real-time
- Handle SIGINT gracefully and release resources

**Non-Goals:**
- Event interpretation or action execution (future sprints)
- Window/application detection (Sprint 3)
- Configuration loading (Sprint 6)
- Gesture recognition (Sprint 9)
- Event filtering beyond supported types

## Decisions

### Decision 1: Use evdev's read_loop() for continuous event reading

**Choice:** evdev.InputDevice.read_loop()

**Rationale:** evdev provides a built-in generator that yields events as they arrive. It handles blocking I/O efficiently and is the idiomatic way to read from input devices in Python.

**Alternatives considered:**
- Manual select/poll: More complex, requires handling timeouts and multiple file descriptors
- Async I/O: Unnecessary complexity for single-device reading; adds async overhead
- Threading: Not needed; single-threaded event loop is sufficient

### Decision 2: Filter events by type and code at the application level

**Choice:** Check event.type and event.code after receiving each event

**Rationale:** evdev delivers all events from the device. We filter in Python to only process the events we care about. This keeps the logic simple and testable.

**Alternatives considered:**
- evdev's grab mode: Takes exclusive control of device, which may interfere with normal mouse usage
- Kernel-level filtering: Not supported by evdev; all events must be read

### Decision 3: Use signal handler for graceful shutdown

**Choice:** Register SIGINT handler to catch Ctrl+C and clean up

**Rationale:** The device handle must be closed properly to avoid resource leaks. A signal handler ensures cleanup happens even when the user interrupts the application.

**Alternatives considered:**
- try/finally block: Works but less explicit about interrupt handling
- Context manager: Good for setup/teardown but doesn't handle signals directly

### Decision 4: Separate event stream logic from device discovery

**Choice:** Create a new `engine` module that takes a device path and streams events

**Rationale:** Single responsibility principle. Device discovery finds the device; the engine reads events. This separation makes each component testable and reusable.

**Alternatives considered:**
- Add event reading to discovery module: Violates single responsibility
- Create a generic input framework: Over-engineering for current needs

### Decision 5: Display event code names, not raw values

**Choice:** Use evdev's ecodes module to map event codes to human-readable names

**Rationale:** Users need to see "BTN_SIDE" not "275". evdev provides reverse mappings via ecodes.BTN.get() or similar.

**Alternatives considered:**
- Display raw numeric codes: Not user-friendly
- Custom mapping table: Unnecessary; evdev already provides this

## Risks / Trade-offs

**Risk:** Device disconnection during execution
→ **Mitigation:** Catch OSError when reading fails and exit gracefully with a message

**Risk:** High CPU usage from busy-waiting
→ **Mitigation:** read_loop() blocks until events arrive, so CPU usage is minimal when idle

**Risk:** Signal handling complexity
→ **Mitigation:** Use Python's signal module with a simple handler that sets a flag or raises KeyboardInterrupt

**Trade-off:** No exclusive device control (grab mode)
→ **Acceptance:** We want the mouse to continue working normally for regular use. Grab mode would prevent that.

**Trade-off:** Single-threaded design
→ **Acceptance:** Sufficient for current needs. If we need concurrent processing later, we can add threading or async.
