"""Gesture recognition component.

This module provides gesture recognition functionality by tracking mouse movement
while a gesture button is held and recognizing directional gestures based on
cumulative movement thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass

from mouseflow.domain import Gesture, GestureDirection, MouseButton, MouseEvent

# Threshold in pixels for gesture recognition
GESTURE_THRESHOLD = 50


@dataclass
class GestureRecognizer:
    """Recognizes directional mouse gestures.

    Tracks cumulative mouse movement while a gesture button is held and
    recognizes directional gestures (UP, DOWN, LEFT, RIGHT) when the button
    is released.
    """

    cumulative_x: int = 0
    cumulative_y: int = 0
    is_active: bool = False
    _gesture_button: MouseButton = MouseButton.BTN_EXTRA

    def process_event(self, event: MouseEvent) -> Gesture | None:
        """Process a mouse event and return a Gesture if recognized.

        Args:
            event: The mouse event to process.

        Returns:
            A Gesture object if a gesture was recognized, None otherwise.
        """
        # Check for gesture button press/release
        if event.button == self._gesture_button:
            if event.value == 1:  # Button pressed
                self._activate()
                return None
            if event.value == 0:  # Button released
                return self._deactivate()

        # Track movement if gesture mode is active
        if self.is_active and event.event_type.value == "WHEEL":
            # Note: We'll need to handle REL_X and REL_Y events separately
            # For now, this is a placeholder
            pass

        return None

    def process_movement(self, delta_x: int, delta_y: int) -> None:
        """Process mouse movement deltas.

        Args:
            delta_x: Horizontal movement delta.
            delta_y: Vertical movement delta.
        """
        if self.is_active:
            self.cumulative_x += delta_x
            self.cumulative_y += delta_y

    def _activate(self) -> None:
        """Activate gesture mode and reset tracking state."""
        self.is_active = True
        self.cumulative_x = 0
        self.cumulative_y = 0

    def _deactivate(self) -> Gesture | None:
        """Deactivate gesture mode and recognize gesture if threshold met.

        Returns:
            A Gesture object if a gesture was recognized, None otherwise.
        """
        if not self.is_active:
            return None

        self.is_active = False
        gesture = self._recognize_gesture()

        # Reset state
        self.cumulative_x = 0
        self.cumulative_y = 0

        return gesture

    def _recognize_gesture(self) -> Gesture | None:
        """Recognize gesture direction based on cumulative movement.

        Returns:
            A Gesture object if a direction is recognized, None otherwise.
        """
        abs_x = abs(self.cumulative_x)
        abs_y = abs(self.cumulative_y)

        # Check if movement exceeds threshold
        if abs_x < GESTURE_THRESHOLD and abs_y < GESTURE_THRESHOLD:
            return None

        # Determine primary direction
        if abs_x > abs_y:
            # Horizontal movement is dominant
            if self.cumulative_x > 0:
                return Gesture(direction=GestureDirection.RIGHT)
            return Gesture(direction=GestureDirection.LEFT)
        # Vertical movement is dominant
        if self.cumulative_y > 0:
            return Gesture(direction=GestureDirection.DOWN)
        return Gesture(direction=GestureDirection.UP)
