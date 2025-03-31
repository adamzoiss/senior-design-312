"""
Mock implementation of the GPIOHandler class for testing.
"""

import sys
from unittest.mock import MagicMock
from src.handlers.gpio_handler import GPIOHandler
from tests.mocks.mock_lgpio import MockLgpio

# Replace the real lgpio with our mock version
sys.modules["lgpio"] = MockLgpio()
import lgpio


class MockGPIOHandler(GPIOHandler):
    """
    A mock implementation of GPIOHandler for testing purposes.

    This class overrides the hardware-dependent methods to avoid
    actual hardware interactions during testing.
    """

    def __init__(self, chip_number=0):
        """
        Initialize the MockGPIOHandler without connecting to actual hardware.
        """
        # Don't call the parent constructor to avoid hardware initialization
        self.handle = lgpio.gpiochip_open(chip_number)

        # Create mock callbacks
        self.enc_a_cb = MagicMock()
        self.enc_b_cb = MagicMock()
        self.sw1_cb = MagicMock()
        self.sw2_cb = MagicMock()
        self.sw3_cb = MagicMock()
        self.sw4_cb = MagicMock()
        self.sw5_cb = MagicMock()

    def _init_gpio(self):
        """Mock implementation of GPIO initialization."""
        pass

    def _init_alerts(self):
        """Mock implementation of alerts initialization."""
        pass

    def _init_callbacks(self):
        """Mock implementation of callbacks initialization."""
        pass

    def _cancel_callbacks(self):
        """Mock implementation of callback cancellation."""
        pass
