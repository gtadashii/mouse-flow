import pytest

from mouseflow.domain import (
    GLOBAL_PROFILE_NAME,
    Action,
    ActionType,
    Application,
    ApplicationStatus,
    Configuration,
    DeviceInfo,
    DispatchContext,
    EventType,
    InputIdentifier,
    MouseButton,
    MouseEvent,
    Profile,
    ReloadResult,
    UserInput,
    ValidationResult,
    WheelAxis,
    Window,
    WindowInfo,
    command_action,
    keyboard_action,
)


class TestMouseButton:
    def test_button_values(self) -> None:
        assert MouseButton.BTN_SIDE.value == "BTN_SIDE"
        assert MouseButton.BTN_EXTRA.value == "BTN_EXTRA"
        assert MouseButton.BTN_FORWARD.value == "BTN_FORWARD"
        assert MouseButton.BTN_BACK.value == "BTN_BACK"


class TestInputIdentifier:
    def test_button_identifiers(self) -> None:
        assert InputIdentifier.BTN_SIDE.value == "BTN_SIDE"
        assert InputIdentifier.BTN_EXTRA.value == "BTN_EXTRA"
        assert InputIdentifier.BTN_FORWARD.value == "BTN_FORWARD"
        assert InputIdentifier.BTN_BACK.value == "BTN_BACK"

    def test_gesture_identifiers(self) -> None:
        assert InputIdentifier.GESTURE_UP.value == "GESTURE_UP"
        assert InputIdentifier.GESTURE_DOWN.value == "GESTURE_DOWN"
        assert InputIdentifier.GESTURE_LEFT.value == "GESTURE_LEFT"
        assert InputIdentifier.GESTURE_RIGHT.value == "GESTURE_RIGHT"

    def test_thumb_wheel_identifiers(self) -> None:
        assert InputIdentifier.THUMB_WHEEL_LEFT.value == "THUMB_WHEEL_LEFT"
        assert InputIdentifier.THUMB_WHEEL_RIGHT.value == "THUMB_WHEEL_RIGHT"


class TestUserInput:
    def test_creation(self) -> None:
        user_input = UserInput(identifier=InputIdentifier.BTN_SIDE)
        assert user_input.identifier == InputIdentifier.BTN_SIDE

    def test_equality(self) -> None:
        input1 = UserInput(identifier=InputIdentifier.BTN_SIDE)
        input2 = UserInput(identifier=InputIdentifier.BTN_SIDE)
        assert input1 == input2

    def test_inequality(self) -> None:
        input1 = UserInput(identifier=InputIdentifier.BTN_SIDE)
        input2 = UserInput(identifier=InputIdentifier.BTN_EXTRA)
        assert input1 != input2

    def test_immutability(self) -> None:
        user_input = UserInput(identifier=InputIdentifier.BTN_SIDE)
        with pytest.raises(AttributeError):
            user_input.identifier = InputIdentifier.BTN_EXTRA  # type: ignore[misc]


class TestWheelAxis:
    def test_wheel_values(self) -> None:
        assert WheelAxis.REL_HWHEEL.value == "REL_HWHEEL"
        assert WheelAxis.REL_WHEEL.value == "REL_WHEEL"


class TestMouseEvent:
    def test_button_event_creation(self) -> None:
        event = MouseEvent.button_event(MouseButton.BTN_SIDE)
        assert event.event_type == EventType.BUTTON
        assert event.button == MouseButton.BTN_SIDE
        assert event.value == 1

    def test_button_event_released(self) -> None:
        event = MouseEvent.button_event(MouseButton.BTN_EXTRA, pressed=False)
        assert event.event_type == EventType.BUTTON
        assert event.button == MouseButton.BTN_EXTRA
        assert event.value == 0

    def test_wheel_event_creation(self) -> None:
        event = MouseEvent.wheel_event(WheelAxis.REL_HWHEEL, 5)
        assert event.event_type == EventType.WHEEL
        assert event.wheel == WheelAxis.REL_HWHEEL
        assert event.value == 5

    def test_wheel_event_negative(self) -> None:
        event = MouseEvent.wheel_event(WheelAxis.REL_WHEEL, -3)
        assert event.event_type == EventType.WHEEL
        assert event.wheel == WheelAxis.REL_WHEEL
        assert event.value == -3

    def test_equality(self) -> None:
        event1 = MouseEvent.button_event(MouseButton.BTN_SIDE)
        event2 = MouseEvent.button_event(MouseButton.BTN_SIDE)
        assert event1 == event2

    def test_inequality(self) -> None:
        event1 = MouseEvent.button_event(MouseButton.BTN_SIDE)
        event2 = MouseEvent.button_event(MouseButton.BTN_EXTRA)
        assert event1 != event2

    def test_immutability(self) -> None:
        event = MouseEvent.button_event(MouseButton.BTN_SIDE)
        with pytest.raises(AttributeError):
            event.value = 99  # type: ignore[misc]


class TestApplication:
    def test_creation(self) -> None:
        app = Application(app_name="Firefox")
        assert app.app_name == "Firefox"

    def test_default_value(self) -> None:
        app = Application()
        assert app.app_name == "Unknown"

    def test_equality(self) -> None:
        app1 = Application(app_name="Firefox")
        app2 = Application(app_name="Firefox")
        assert app1 == app2

    def test_inequality(self) -> None:
        app1 = Application(app_name="Firefox")
        app2 = Application(app_name="Chrome")
        assert app1 != app2

    def test_immutability(self) -> None:
        app = Application(app_name="Firefox")
        with pytest.raises(AttributeError):
            app.app_name = "Chrome"  # type: ignore[misc]


class TestWindow:
    def test_creation(self) -> None:
        window = Window(title="ChatGPT")
        assert window.title == "ChatGPT"

    def test_default_value(self) -> None:
        window = Window()
        assert window.title == "Untitled"

    def test_equality(self) -> None:
        window1 = Window(title="ChatGPT")
        window2 = Window(title="ChatGPT")
        assert window1 == window2

    def test_inequality(self) -> None:
        window1 = Window(title="ChatGPT")
        window2 = Window(title="GitHub")
        assert window1 != window2

    def test_immutability(self) -> None:
        window = Window(title="ChatGPT")
        with pytest.raises(AttributeError):
            window.title = "GitHub"  # type: ignore[misc]


class TestActionType:
    def test_action_types(self) -> None:
        assert ActionType.KEYBOARD.value == "KEYBOARD"
        assert ActionType.COMMAND.value == "COMMAND"


class TestAction:
    def test_keyboard_action(self) -> None:
        action = Action(action_type=ActionType.KEYBOARD, payload="alt+left")
        assert action.action_type == ActionType.KEYBOARD
        assert action.payload == "alt+left"

    def test_command_action_creation(self) -> None:
        action = Action(action_type=ActionType.COMMAND, payload="swaymsg workspace 1")
        assert action.action_type == ActionType.COMMAND
        assert action.payload == "swaymsg workspace 1"

    def test_keyboard_action_factory(self) -> None:
        action = keyboard_action("ctrl+shift+t")
        assert action.action_type == ActionType.KEYBOARD
        assert action.payload == "ctrl+shift+t"

    def test_command_action_factory(self) -> None:
        action = command_action("echo hello")
        assert action.action_type == ActionType.COMMAND
        assert action.payload == "echo hello"

    def test_equality(self) -> None:
        action1 = keyboard_action("alt+left")
        action2 = keyboard_action("alt+left")
        assert action1 == action2

    def test_inequality(self) -> None:
        action1 = keyboard_action("alt+left")
        action2 = keyboard_action("alt+right")
        assert action1 != action2

    def test_immutability(self) -> None:
        action = keyboard_action("alt+left")
        with pytest.raises(AttributeError):
            action.payload = "alt+right"  # type: ignore[misc]


class TestProfile:
    def test_creation(self) -> None:
        mappings = {InputIdentifier.BTN_SIDE: keyboard_action("alt+left")}
        profile = Profile(app_name="firefox", mappings=mappings)
        assert profile.app_name == "firefox"
        assert len(profile.mappings) == 1
        assert InputIdentifier.BTN_SIDE in profile.mappings

    def test_empty_profile(self) -> None:
        profile = Profile(app_name="firefox", mappings={})
        assert profile.app_name == "firefox"
        assert len(profile.mappings) == 0

    def test_equality(self) -> None:
        mappings = {InputIdentifier.BTN_SIDE: keyboard_action("alt+left")}
        profile1 = Profile(app_name="firefox", mappings=mappings)
        profile2 = Profile(app_name="firefox", mappings=mappings)
        assert profile1 == profile2

    def test_inequality(self) -> None:
        mappings1 = {InputIdentifier.BTN_SIDE: keyboard_action("alt+left")}
        mappings2 = {InputIdentifier.BTN_SIDE: keyboard_action("alt+right")}
        profile1 = Profile(app_name="firefox", mappings=mappings1)
        profile2 = Profile(app_name="firefox", mappings=mappings2)
        assert profile1 != profile2

    def test_immutability_app_name(self) -> None:
        profile = Profile(app_name="firefox", mappings={})
        with pytest.raises(AttributeError):
            profile.app_name = "chrome"  # type: ignore[misc]

    def test_immutability_mappings(self) -> None:
        profile = Profile(app_name="firefox", mappings={})
        with pytest.raises(AttributeError):
            profile.mappings = {}  # type: ignore[misc]


class TestWindowInfo:
    def test_creation(self) -> None:
        app = Application(app_name="Firefox")
        window = Window(title="ChatGPT")
        info = WindowInfo(application=app, window=window)
        assert info.application.app_name == "Firefox"
        assert info.window.title == "ChatGPT"

    def test_equality(self) -> None:
        app = Application(app_name="Firefox")
        window = Window(title="ChatGPT")
        info1 = WindowInfo(application=app, window=window)
        info2 = WindowInfo(application=app, window=window)
        assert info1 == info2

    def test_inequality(self) -> None:
        app1 = Application(app_name="Firefox")
        app2 = Application(app_name="Chrome")
        window = Window(title="ChatGPT")
        info1 = WindowInfo(application=app1, window=window)
        info2 = WindowInfo(application=app2, window=window)
        assert info1 != info2

    def test_immutability(self) -> None:
        app = Application(app_name="Firefox")
        window = Window(title="ChatGPT")
        info = WindowInfo(application=app, window=window)
        with pytest.raises(AttributeError):
            info.application = Application(app_name="Chrome")  # type: ignore[misc]


class TestDispatchContext:
    def test_creation_with_window_info(self) -> None:
        event = UserInput(identifier=InputIdentifier.BTN_SIDE)
        app = Application(app_name="Firefox")
        window = Window(title="ChatGPT")
        window_info = WindowInfo(application=app, window=window)
        context = DispatchContext(event=event, window_info=window_info)
        assert context.event == event
        assert context.window_info == window_info

    def test_creation_without_window_info(self) -> None:
        event = UserInput(identifier=InputIdentifier.BTN_SIDE)
        context = DispatchContext(event=event)
        assert context.event == event
        assert context.window_info is None

    def test_equality(self) -> None:
        event = UserInput(identifier=InputIdentifier.BTN_SIDE)
        app = Application(app_name="Firefox")
        window = Window(title="ChatGPT")
        window_info = WindowInfo(application=app, window=window)
        context1 = DispatchContext(event=event, window_info=window_info)
        context2 = DispatchContext(event=event, window_info=window_info)
        assert context1 == context2

    def test_inequality(self) -> None:
        event1 = UserInput(identifier=InputIdentifier.BTN_SIDE)
        event2 = UserInput(identifier=InputIdentifier.BTN_EXTRA)
        context1 = DispatchContext(event=event1)
        context2 = DispatchContext(event=event2)
        assert context1 != context2

    def test_immutability(self) -> None:
        event = UserInput(identifier=InputIdentifier.BTN_SIDE)
        context = DispatchContext(event=event)
        with pytest.raises(AttributeError):
            context.event = UserInput(identifier=InputIdentifier.BTN_EXTRA)  # type: ignore[misc]


class TestGlobalProfileName:
    def test_global_profile_name_value(self) -> None:
        assert GLOBAL_PROFILE_NAME == "global"


class TestConfiguration:
    def test_get_profile_existing(self) -> None:
        profile = Profile(app_name="firefox", mappings={})
        config = Configuration(profiles=(profile,))
        assert config.get_profile("firefox") == profile

    def test_get_profile_nonexistent(self) -> None:
        profile = Profile(app_name="firefox", mappings={})
        config = Configuration(profiles=(profile,))
        assert config.get_profile("chrome") is None

    def test_get_profile_empty_configuration(self) -> None:
        config = Configuration()
        assert config.get_profile("firefox") is None

    def test_get_global_profile_exists(self) -> None:
        global_profile = Profile(app_name=GLOBAL_PROFILE_NAME, mappings={})
        config = Configuration(profiles=(global_profile,))
        assert config.get_global_profile() == global_profile

    def test_get_global_profile_not_exists(self) -> None:
        profile = Profile(app_name="firefox", mappings={})
        config = Configuration(profiles=(profile,))
        assert config.get_global_profile() is None

    def test_get_global_profile_empty_configuration(self) -> None:
        config = Configuration()
        assert config.get_global_profile() is None

    def test_get_global_profile_with_multiple_profiles(self) -> None:
        firefox_profile = Profile(app_name="firefox", mappings={})
        global_profile = Profile(app_name=GLOBAL_PROFILE_NAME, mappings={})
        vscode_profile = Profile(app_name="vscode", mappings={})
        config = Configuration(
            profiles=(firefox_profile, global_profile, vscode_profile),
        )
        assert config.get_global_profile() == global_profile
        assert config.get_profile("firefox") == firefox_profile
        assert config.get_profile("vscode") == vscode_profile


class TestDeviceInfo:
    def test_creation(self) -> None:
        device = DeviceInfo(path="/dev/input/event0", name="Test Mouse", is_active=True)
        assert device.path == "/dev/input/event0"
        assert device.name == "Test Mouse"
        assert device.is_active is True

    def test_equality(self) -> None:
        device1 = DeviceInfo(
            path="/dev/input/event0", name="Test Mouse", is_active=True
        )
        device2 = DeviceInfo(
            path="/dev/input/event0", name="Test Mouse", is_active=True
        )
        assert device1 == device2

    def test_inequality(self) -> None:
        device1 = DeviceInfo(
            path="/dev/input/event0", name="Test Mouse", is_active=True
        )
        device2 = DeviceInfo(
            path="/dev/input/event1", name="Test Mouse", is_active=True
        )
        assert device1 != device2

    def test_immutability(self) -> None:
        device = DeviceInfo(path="/dev/input/event0", name="Test Mouse", is_active=True)
        with pytest.raises(AttributeError):
            device.name = "Other Mouse"  # type: ignore[misc]


class TestApplicationStatus:
    def test_creation_full(self) -> None:
        status = ApplicationStatus(
            is_running=True,
            device_connected=True,
            configuration_loaded=True,
            active_profile="firefox",
        )
        assert status.is_running is True
        assert status.device_connected is True
        assert status.configuration_loaded is True
        assert status.active_profile == "firefox"

    def test_creation_defaults(self) -> None:
        status = ApplicationStatus(
            is_running=True,
            device_connected=False,
            configuration_loaded=False,
        )
        assert status.active_profile is None

    def test_equality(self) -> None:
        status1 = ApplicationStatus(
            is_running=True,
            device_connected=True,
            configuration_loaded=True,
            active_profile="firefox",
        )
        status2 = ApplicationStatus(
            is_running=True,
            device_connected=True,
            configuration_loaded=True,
            active_profile="firefox",
        )
        assert status1 == status2

    def test_inequality(self) -> None:
        status1 = ApplicationStatus(
            is_running=True,
            device_connected=True,
            configuration_loaded=True,
        )
        status2 = ApplicationStatus(
            is_running=False,
            device_connected=True,
            configuration_loaded=True,
        )
        assert status1 != status2

    def test_immutability(self) -> None:
        status = ApplicationStatus(
            is_running=True,
            device_connected=True,
            configuration_loaded=True,
        )
        with pytest.raises(AttributeError):
            status.is_running = False  # type: ignore[misc]


class TestValidationResult:
    def test_valid_result(self) -> None:
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert result.errors == ()

    def test_invalid_result(self) -> None:
        result = ValidationResult(is_valid=False, errors=("Error 1", "Error 2"))
        assert result.is_valid is False
        assert result.errors == ("Error 1", "Error 2")

    def test_equality(self) -> None:
        result1 = ValidationResult(is_valid=True)
        result2 = ValidationResult(is_valid=True)
        assert result1 == result2

    def test_inequality(self) -> None:
        result1 = ValidationResult(is_valid=True)
        result2 = ValidationResult(is_valid=False, errors=("Error",))
        assert result1 != result2

    def test_immutability(self) -> None:
        result = ValidationResult(is_valid=True)
        with pytest.raises(AttributeError):
            result.is_valid = False  # type: ignore[misc]


class TestReloadResult:
    def test_success_result(self) -> None:
        result = ReloadResult(success=True)
        assert result.success is True
        assert result.message is None

    def test_success_with_message(self) -> None:
        result = ReloadResult(success=True, message="Configuration reloaded")
        assert result.success is True
        assert result.message == "Configuration reloaded"

    def test_failure_result(self) -> None:
        result = ReloadResult(success=False, message="Invalid configuration")
        assert result.success is False
        assert result.message == "Invalid configuration"

    def test_equality(self) -> None:
        result1 = ReloadResult(success=True)
        result2 = ReloadResult(success=True)
        assert result1 == result2

    def test_inequality(self) -> None:
        result1 = ReloadResult(success=True)
        result2 = ReloadResult(success=False, message="Error")
        assert result1 != result2

    def test_immutability(self) -> None:
        result = ReloadResult(success=True)
        with pytest.raises(AttributeError):
            result.success = False  # type: ignore[misc]
