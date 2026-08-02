"""Tests for gesture recognition component."""

from mouseflow.domain import (
    Gesture,
    GestureDirection,
    MouseButton,
    MouseEvent,
)
from mouseflow.gesture import GESTURE_THRESHOLD, GestureRecognizer


class TestGestureRecognizerActivation:
    def test_gesture_button_press_activates(self) -> None:
        """Test that pressing the gesture button activates gesture mode."""
        recognizer = GestureRecognizer()
        event = MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=True)

        result = recognizer.process_event(event)

        assert result is None
        assert recognizer.is_active is True
        assert recognizer.cumulative_x == 0
        assert recognizer.cumulative_y == 0

    def test_gesture_button_release_deactivates(self) -> None:
        """Test that releasing the gesture button deactivates gesture mode."""
        recognizer = GestureRecognizer()
        # Activate first
        recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=True)
        )

        # Release
        recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=False)
        )

        assert recognizer.is_active is False
        assert recognizer.cumulative_x == 0
        assert recognizer.cumulative_y == 0

    def test_non_gesture_button_ignored(self) -> None:
        """Test that non-gesture buttons don't activate gesture mode."""
        recognizer = GestureRecognizer()
        event = MouseEvent.button_event(MouseButton.BTN_SIDE, pressed=True)

        result = recognizer.process_event(event)

        assert result is None
        assert recognizer.is_active is False


class TestGestureRecognizerMovement:
    def test_movement_tracked_when_active(self) -> None:
        """Test that movement is tracked when gesture mode is active."""
        recognizer = GestureRecognizer()
        recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=True)
        )

        recognizer.process_movement(10, 5)

        assert recognizer.cumulative_x == 10
        assert recognizer.cumulative_y == 5

    def test_movement_accumulates(self) -> None:
        """Test that movement accumulates across multiple updates."""
        recognizer = GestureRecognizer()
        recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=True)
        )

        recognizer.process_movement(10, 5)
        recognizer.process_movement(20, 15)

        assert recognizer.cumulative_x == 30
        assert recognizer.cumulative_y == 20

    def test_movement_ignored_when_inactive(self) -> None:
        """Test that movement is ignored when gesture mode is inactive."""
        recognizer = GestureRecognizer()

        recognizer.process_movement(10, 5)

        assert recognizer.cumulative_x == 0
        assert recognizer.cumulative_y == 0


class TestGestureRecognizerDirection:
    def test_right_gesture_recognized(self) -> None:
        """Test that rightward movement is recognized as RIGHT gesture."""
        recognizer = GestureRecognizer()
        recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=True)
        )
        recognizer.process_movement(GESTURE_THRESHOLD + 10, 0)

        result = recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=False)
        )

        assert result is not None
        assert isinstance(result, Gesture)
        assert result.direction == GestureDirection.RIGHT

    def test_left_gesture_recognized(self) -> None:
        """Test that leftward movement is recognized as LEFT gesture."""
        recognizer = GestureRecognizer()
        recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=True)
        )
        recognizer.process_movement(-(GESTURE_THRESHOLD + 10), 0)

        result = recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=False)
        )

        assert result is not None
        assert isinstance(result, Gesture)
        assert result.direction == GestureDirection.LEFT

    def test_down_gesture_recognized(self) -> None:
        """Test that downward movement is recognized as DOWN gesture."""
        recognizer = GestureRecognizer()
        recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=True)
        )
        recognizer.process_movement(0, GESTURE_THRESHOLD + 10)

        result = recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=False)
        )

        assert result is not None
        assert isinstance(result, Gesture)
        assert result.direction == GestureDirection.DOWN

    def test_up_gesture_recognized(self) -> None:
        """Test that upward movement is recognized as UP gesture."""
        recognizer = GestureRecognizer()
        recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=True)
        )
        recognizer.process_movement(0, -(GESTURE_THRESHOLD + 10))

        result = recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=False)
        )

        assert result is not None
        assert isinstance(result, Gesture)
        assert result.direction == GestureDirection.UP

    def test_horizontal_dominant_over_vertical(self) -> None:
        """Test that horizontal movement is recognized when it exceeds vertical."""
        recognizer = GestureRecognizer()
        recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=True)
        )
        recognizer.process_movement(GESTURE_THRESHOLD + 20, GESTURE_THRESHOLD - 10)

        result = recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=False)
        )

        assert result is not None
        assert result.direction == GestureDirection.RIGHT

    def test_vertical_dominant_over_horizontal(self) -> None:
        """Test that vertical movement is recognized when it exceeds horizontal."""
        recognizer = GestureRecognizer()
        recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=True)
        )
        recognizer.process_movement(GESTURE_THRESHOLD - 10, GESTURE_THRESHOLD + 20)

        result = recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=False)
        )

        assert result is not None
        assert result.direction == GestureDirection.DOWN


class TestGestureRecognizerThreshold:
    def test_below_threshold_no_gesture(self) -> None:
        """Test that movement below threshold doesn't produce a gesture."""
        recognizer = GestureRecognizer()
        recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=True)
        )
        recognizer.process_movement(GESTURE_THRESHOLD - 10, 0)

        result = recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=False)
        )

        assert result is None

    def test_at_threshold_gesture_recognized(self) -> None:
        """Test that movement exactly at threshold produces a gesture."""
        recognizer = GestureRecognizer()
        recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=True)
        )
        recognizer.process_movement(GESTURE_THRESHOLD, 0)

        result = recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=False)
        )

        assert result is not None
        assert result.direction == GestureDirection.RIGHT

    def test_above_threshold_gesture_recognized(self) -> None:
        """Test that movement above threshold produces a gesture."""
        recognizer = GestureRecognizer()
        recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=True)
        )
        recognizer.process_movement(GESTURE_THRESHOLD + 1, 0)

        result = recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=False)
        )

        assert result is not None


class TestGestureRecognizerStateReset:
    def test_state_reset_after_gesture(self) -> None:
        """Test that state is reset after gesture recognition."""
        recognizer = GestureRecognizer()
        recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=True)
        )
        recognizer.process_movement(100, 50)

        recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=False)
        )

        assert recognizer.cumulative_x == 0
        assert recognizer.cumulative_y == 0
        assert recognizer.is_active is False

    def test_state_reset_without_gesture(self) -> None:
        """Test that state is reset even when no gesture is recognized."""
        recognizer = GestureRecognizer()
        recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=True)
        )
        recognizer.process_movement(10, 5)

        recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=False)
        )

        assert recognizer.cumulative_x == 0
        assert recognizer.cumulative_y == 0
        assert recognizer.is_active is False

    def test_multiple_gestures_independent(self) -> None:
        """Test that multiple gesture attempts are independent."""
        recognizer = GestureRecognizer()

        # First gesture attempt
        recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=True)
        )
        recognizer.process_movement(100, 0)
        result1 = recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=False)
        )

        # Second gesture attempt
        recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=True)
        )
        recognizer.process_movement(0, 100)
        result2 = recognizer.process_event(
            MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=False)
        )

        assert result1 is not None
        assert result1.direction == GestureDirection.RIGHT
        assert result2 is not None
        assert result2.direction == GestureDirection.DOWN
