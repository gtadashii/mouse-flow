"""Tests for gesture domain objects."""

import pytest

from mouseflow.domain import Gesture, GestureDirection


class TestGestureDirection:
    def test_gesture_direction_values(self) -> None:
        """Test that GestureDirection enum has correct values."""
        assert GestureDirection.UP.value == "UP"
        assert GestureDirection.DOWN.value == "DOWN"
        assert GestureDirection.LEFT.value == "LEFT"
        assert GestureDirection.RIGHT.value == "RIGHT"

    def test_gesture_direction_equality(self) -> None:
        """Test GestureDirection enum equality."""
        assert GestureDirection.UP == GestureDirection.UP
        assert GestureDirection.DOWN == GestureDirection.DOWN
        assert GestureDirection.LEFT == GestureDirection.LEFT
        assert GestureDirection.RIGHT == GestureDirection.RIGHT

    def test_gesture_direction_inequality(self) -> None:
        """Test GestureDirection enum inequality."""
        assert GestureDirection.UP != GestureDirection.DOWN  # type: ignore[comparison-overlap]
        assert GestureDirection.LEFT != GestureDirection.RIGHT  # type: ignore[comparison-overlap]
        assert GestureDirection.UP != GestureDirection.LEFT  # type: ignore[comparison-overlap]

    def test_gesture_direction_immutability(self) -> None:
        """Test that GestureDirection enum values cannot be modified."""
        with pytest.raises(AttributeError):
            GestureDirection.UP = "MODIFIED"  # type: ignore[misc]


class TestGesture:
    def test_gesture_creation(self) -> None:
        """Test Gesture object creation."""
        gesture = Gesture(direction=GestureDirection.UP)
        assert gesture.direction == GestureDirection.UP

    def test_gesture_all_directions(self) -> None:
        """Test Gesture creation with all directions."""
        for direction in GestureDirection:
            gesture = Gesture(direction=direction)
            assert gesture.direction == direction

    def test_gesture_equality(self) -> None:
        """Test Gesture object equality."""
        gesture1 = Gesture(direction=GestureDirection.LEFT)
        gesture2 = Gesture(direction=GestureDirection.LEFT)
        assert gesture1 == gesture2

    def test_gesture_inequality(self) -> None:
        """Test Gesture object inequality."""
        gesture1 = Gesture(direction=GestureDirection.LEFT)
        gesture2 = Gesture(direction=GestureDirection.RIGHT)
        assert gesture1 != gesture2

    def test_gesture_immutability(self) -> None:
        """Test that Gesture objects are immutable."""
        gesture = Gesture(direction=GestureDirection.UP)
        with pytest.raises(AttributeError):
            gesture.direction = GestureDirection.DOWN  # type: ignore[misc]

    def test_gesture_hashable(self) -> None:
        """Test that Gesture objects are hashable."""
        gesture = Gesture(direction=GestureDirection.UP)
        # Should be able to use in sets and as dict keys
        gesture_set = {gesture}
        assert gesture in gesture_set
