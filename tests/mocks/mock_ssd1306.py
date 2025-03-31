"""
Mock version of the SSD1306 display driver that inherits from the actual SSD1306 class
but replaces any I2C hardware interactions with mocks.
"""

import os
import fcntl
from unittest.mock import MagicMock, patch
from PIL import Image, ImageDraw
from src.handlers.peripheral_drivers.ssd1306 import SSD1306
from src.utils.constants import (
    PIXEL_WIDTH,
    PIXEL_HEIGHT,
    I2C_BUS,
    SSD1306_I2C_ADDR,
)


class MockSSD1306(SSD1306):
    """
    A mock implementation of the SSD1306 OLED display that inherits from the real SSD1306.
    All I2C hardware interactions are mocked to allow for testing without actual hardware.
    """

    def __init__(
        self,
        thread_manager,
        i2c_bus=I2C_BUS,
        width=PIXEL_WIDTH,
        height=PIXEL_HEIGHT,
    ):
        """
        Initialize the mock SSD1306 display.
        Override the __init__ method of the parent class to avoid opening real I2C device.

        Parameters
        ----------
        thread_manager : ThreadManager
            Thread manager instance
        i2c_bus : int, optional
            The I2C bus number (not actually used in mock)
        width : int, optional
            The width of the display in pixels
        height : int, optional
            The height of the display in pixels
        """
        # Don't call super().__init__() to avoid actual hardware interaction
        # Instead, set up the necessary attributes directly
        self.thread_manager = thread_manager
        self.width = width
        self.height = height
        self.pages = height // 8

        # Create a mock I2C device
        self.i2c_dev = MagicMock()

        # Create a blank image buffer for drawing
        self.image = Image.new("1", (self.width, self.height), color=0)
        self.draw = ImageDraw.Draw(self.image)

        # Track command history for testing/debugging
        self.command_history = []

        # Initialize the display (without actually writing to hardware)
        self.initialize_display()

        print("MockSSD1306 initialized")

    def write_command(self, cmd):
        """
        Mock sending a command to the I2C device.
        Records the command instead of sending to hardware.

        Parameters
        ----------
        cmd : int
            The command byte that would be sent to the I2C device
        """
        self.command_history.append(cmd)
        # Don't actually send anything to hardware

    def write_data(self, data):
        """
        Mock writing data to the I2C device.
        Records the data length instead of sending to hardware.

        Parameters
        ----------
        data : bytes
            The data that would be written to the I2C device
        """
        self.command_history.append(f"Data: {len(data)} bytes")
        # Don't actually send anything to hardware

    def get_image(self):
        """
        Returns the current image buffer.
        Useful for testing and displaying in emulators.

        Returns
        -------
        PIL.Image.Image
            The current display image
        """
        return self.image.copy()

    def get_command_history(self):
        """
        Returns the command history for testing purposes.

        Returns
        -------
        list
            List of commands and data sent to the display
        """
        return self.command_history.copy()

    def __del__(self):
        """
        Clean up resources when the object is deleted.
        Override to avoid closing actual hardware.
        """
        # Clean up the image but skip the hardware shutdown
        self.image = None
        self.draw = None
        print("MockSSD1306 cleaned up")


# Test code if run directly
if __name__ == "__main__":
    # Create a simple mock thread manager
    class MockThreadManager:
        pass

    # Initialize the mock display
    display = MockSSD1306(MockThreadManager())

    # Test drawing operations
    display.clear_screen()
    display.draw_text("Hello, Mock World!", x=10, y=10, font_size=12)
    display.draw_line(0, 30, 127, 30)
    display.draw_circle(64, 48, 15)

    # Display command history
    print("\nCommand History:")
    for cmd in display.get_command_history():
        print(f"- {cmd}")

    # Save the image for visual inspection
    display.get_image().save("mock_display_test.png")
    print("\nTest image saved as mock_display_test.png")
