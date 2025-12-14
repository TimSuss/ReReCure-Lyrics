"""Input handling for keyboard and footswitch controls."""
import sys
from enum import Enum
from typing import Optional, Callable, Any


class InputAction(Enum):
    """Enumeration of possible input actions."""
    FORWARD = "forward"
    BACKWARD = "backward"
    QUIT = "quit"
    NONE = "none"


class InputHandler:
    """Handles input from keyboard and footswitch."""

    def __init__(self):
        """Initialize the input handler."""
        self.action_callbacks = {
            InputAction.FORWARD: None,
            InputAction.BACKWARD: None,
            InputAction.QUIT: None,
        }

    def register_callback(self, action: InputAction, callback: Callable):
        """
        Register a callback for a specific action.

        Args:
            action: The action to register
            callback: Function to call when action occurs
        """
        self.action_callbacks[action] = callback

    def handle_key(self, key: str) -> InputAction:
        """
        Map keyboard input to actions.

        Args:
            key: The key pressed

        Returns:
            The corresponding action
        """
        # Map various keys to actions
        key_lower = key.lower() if isinstance(key, str) else key

        # Forward actions
        if key_lower in ['right', 'key_right', 'n', 'f', ' ', '\n']:
            return InputAction.FORWARD

        # Backward actions
        if key_lower in ['left', 'key_left', 'b', 'p']:
            return InputAction.BACKWARD

        # Quit actions
        if key_lower in ['q', '\x1b']:  # \x1b is ESC
            return InputAction.QUIT

        return InputAction.NONE

    def execute_action(self, action: InputAction):
        """
        Execute the callback for a given action.

        Args:
            action: The action to execute
        """
        if action in self.action_callbacks and self.action_callbacks[action]:
            self.action_callbacks[action]()


class FootswitchHandler:
    """Handles footswitch input using evdev on Linux."""

    def __init__(self, device_path: Optional[str] = None):
        """
        Initialize footswitch handler.

        Args:
            device_path: Path to the input device (e.g., /dev/input/event0)
        """
        self.device_path = device_path
        self.device = None
        self.enabled = False

        # Only import evdev on Linux
        if sys.platform.startswith('linux'):
            try:
                import evdev
                self.evdev = evdev
                self.enabled = True
            except ImportError:
                print("Warning: evdev not installed. Footswitch support disabled.")
                print("Install with: pip install evdev")
                self.enabled = False

    def find_footswitch_device(self) -> Optional[str]:
        """
        Attempt to find a footswitch device automatically.

        Returns:
            Path to the device if found, None otherwise
        """
        if not self.enabled:
            return None

        devices = [self.evdev.InputDevice(path) for path in self.evdev.list_devices()]

        for device in devices:
            # Look for devices that might be footswitches
            # You may need to customize this based on your specific footswitch
            name = device.name.lower()
            if 'footswitch' in name or 'foot' in name or 'pedal' in name:
                return device.path

        return None

    def connect(self) -> bool:
        """
        Connect to the footswitch device.

        Returns:
            True if connected successfully, False otherwise
        """
        if not self.enabled:
            return False

        try:
            if not self.device_path:
                self.device_path = self.find_footswitch_device()

            if self.device_path:
                self.device = self.evdev.InputDevice(self.device_path)
                print(f"Connected to footswitch: {self.device.name}")
                return True
            else:
                print("No footswitch device found.")
                return False

        except Exception as e:
            print(f"Error connecting to footswitch: {e}")
            return False

    def read_event(self) -> Optional[InputAction]:
        """
        Read an event from the footswitch.

        Returns:
            InputAction if a relevant event occurred, None otherwise
        """
        if not self.device:
            return None

        try:
            event = self.device.read_one()
            if event is None:
                return None

            # Check for key press events
            if event.type == self.evdev.ecodes.EV_KEY:
                # Key down event
                if event.value == 1:
                    # Map different key codes to actions
                    # You may need to adjust these based on your footswitch
                    if event.code in [self.evdev.ecodes.KEY_RIGHT,
                                     self.evdev.ecodes.KEY_PAGEDOWN,
                                     self.evdev.ecodes.KEY_DOWN]:
                        return InputAction.FORWARD
                    elif event.code in [self.evdev.ecodes.KEY_LEFT,
                                       self.evdev.ecodes.KEY_PAGEUP,
                                       self.evdev.ecodes.KEY_UP]:
                        return InputAction.BACKWARD

        except Exception as e:
            print(f"Error reading footswitch event: {e}")

        return None


class GPIOPedalHandler:
    """Handles GPIO-based pedal board input on Raspberry Pi."""

    def __init__(self, forward_pin: int = 27, backward_pin: int = 17,
                 forward_led_pin: int = 23, backward_led_pin: int = 22):
        """
        Initialize GPIO pedal handler.

        Args:
            forward_pin: GPIO pin for forward button (default: 27)
            backward_pin: GPIO pin for backward button (default: 17)
            forward_led_pin: GPIO pin for forward LED (default: 23)
            backward_led_pin: GPIO pin for backward LED (default: 22)
        """
        self.enabled = False
        self.forward_btn = None
        self.backward_btn = None
        self.forward_led = None
        self.backward_led = None
        self.pending_action = None

        # Only import gpiozero on systems where it's available
        try:
            from gpiozero import Button, LED
            self.Button = Button
            self.LED = LED
            self.enabled = True

            # Initialize buttons with pull-up and debounce
            self.forward_btn = Button(forward_pin, pull_up=True, bounce_time=0.05)
            self.backward_btn = Button(backward_pin, pull_up=True, bounce_time=0.05)

            # Initialize LEDs
            self.forward_led = LED(forward_led_pin)
            self.backward_led = LED(backward_led_pin)

            # Set up button press handlers
            self.forward_btn.when_pressed = self._on_forward_pressed
            self.backward_btn.when_pressed = self._on_backward_pressed

            print("GPIO pedal board initialized successfully")
            print(f"  Forward button: GPIO {forward_pin}, LED: GPIO {forward_led_pin}")
            print(f"  Backward button: GPIO {backward_pin}, LED: GPIO {backward_led_pin}")

        except ImportError:
            print("Warning: gpiozero not installed. GPIO pedal support disabled.")
            print("Install with: pip install gpiozero")
            self.enabled = False
        except Exception as e:
            print(f"Warning: Could not initialize GPIO pedals: {e}")
            print("GPIO pedal support disabled.")
            self.enabled = False

    def _on_forward_pressed(self):
        """Callback when forward button is pressed."""
        self.pending_action = InputAction.FORWARD
        # Flash LED briefly
        if self.forward_led:
            self.forward_led.on()

    def _on_backward_pressed(self):
        """Callback when backward button is pressed."""
        self.pending_action = InputAction.BACKWARD
        # Flash LED briefly
        if self.backward_led:
            self.backward_led.on()

    def read_event(self) -> Optional[InputAction]:
        """
        Read a pending event from the GPIO pedals.

        Returns:
            InputAction if a button was pressed, None otherwise
        """
        if not self.enabled:
            return None

        action = self.pending_action
        if action:
            self.pending_action = None
            # Turn off the LED after a short time
            # (LEDs will turn off on next check when no action is pending)
            return action

        # Turn off LEDs when no action is pending
        if self.forward_led:
            self.forward_led.off()
        if self.backward_led:
            self.backward_led.off()

        return None

    def cleanup(self):
        """Clean up GPIO resources."""
        if self.enabled:
            try:
                if self.forward_btn:
                    self.forward_btn.close()
                if self.backward_btn:
                    self.backward_btn.close()
                if self.forward_led:
                    self.forward_led.off()
                    self.forward_led.close()
                if self.backward_led:
                    self.backward_led.off()
                    self.backward_led.close()
            except Exception as e:
                print(f"Error cleaning up GPIO: {e}")
