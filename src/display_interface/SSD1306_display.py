"""
Senior Project : Hardware Encryption Device
Team 312
File : SSD1306_display.py
Description: Interfaces with the SSD1306 OLED display.
"""

import fcntl
import os
from PIL import Image, ImageDraw, ImageFont
from src.utils.interface_constants import *


class SSD1306:
    """
    A class to represent the SSD1306 OLED display.

    Attributes
    ----------
    width : int
        The width of the display in pixels.
    height : int
        The height of the display in pixels.
    pages : int
        The number of pages (each page is 8 rows) in the display.
    i2c_dev : int
        The file descriptor for the I2C device.
    image : PIL.Image.Image
        The image object to draw on.
    draw : PIL.ImageDraw.ImageDraw
        The drawing object to draw on the image.
    """

    def __init__(self, i2c_bus=1, width=128, height=64):
        """
        Initializes the SSD1306 display with the given I2C bus, width, and height.

        Parameters
        ----------
        i2c_bus : int, optional
            The I2C bus number to use. Defaults to 1.
        width : int, optional
            The width of the display in pixels. Defaults to 128.
        height : int, optional
            The height of the display in pixels. Defaults to 64.
        """
        self.width = width
        self.height = height
        self.pages = height // 8  # 64 rows -> 8 pages of 8 rows each
        self.i2c_dev = os.open(f"/dev/i2c-{i2c_bus}", os.O_RDWR)
        fcntl.ioctl(self.i2c_dev, I2C_SLAVE, SSD1306_I2C_ADDR)
        self.initialize_display()

        # Create a blank image to draw on
        self.image = Image.new("1", (self.width, self.height), color=0)
        self.draw = ImageDraw.Draw(self.image)

    def write_command(self, cmd):
        """
        Sends a command to the I2C device.

        Parameters
        ----------
        cmd : int
            The command byte to be sent to the I2C device.

        Raises
        ------
        OSError
            If there is an error writing to the I2C device.
        """

        os.write(self.i2c_dev, bytes([0x00, cmd]))

    def write_data(self, data):
        """
        Writes data to the I2C device.

        Parameters
        ----------
        data : bytes
            The data to be written to the I2C device. It should be in bytes format.

        Raises
        ------
        OSError
            If there is an error writing to the I2C device.
        """

        os.write(self.i2c_dev, bytes([0x40]) + data)

    def initialize_display(self):
        """
        Initializes the display with a series of commands.

        This method sends a sequence of initialization commands to the display
        to set it up for use. The commands configure various settings such as
        display on/off, memory addressing mode, column and page addresses,
        multiplex ratio, display offset, start line, segment re-map, COM output
        scan direction, COM pins hardware configuration, contrast control,
        pre-charge period, VCOMH deselect level, entire display on, and normal
        display mode.
        """
        init_cmds = [
            0xAE,  # Display OFF
            0x20,
            0x00,  # Memory Addressing Mode: Horizontal
            0x21,
            0x00,
            0x7F,  # Set Column Address 0-127
            0x22,
            0x00,
            0x07,  # Set Page Address 0-7
            0xA8,
            0x3F,  # Multiplex Ratio: 63
            0xD3,
            0x00,  # Display Offset: 0
            0x40,  # Start Line: 0
            0xA1,  # Segment Re-map
            0xC8,  # COM Output Scan Direction
            0xDA,
            0x12,  # COM Pins Hardware Config
            0x81,
            0x7F,  # Contrast Control
            0xD9,
            0xF1,  # Pre-charge Period
            0xDB,
            0x40,  # VCOMH Deselect Level
            0xA4,  # Entire Display ON
            0xA6,  # Normal Display Mode
            0xAF,  # Display ON
        ]
        for cmd in init_cmds:
            self.write_command(cmd)

    def clear_screen(self):
        """
        Clears the display by writing 0x00 to all GDDRAM and resets the image.

        This method performs the following steps:
        1. Resets the image by creating a new blank image with the same dimensions.
        2. Sets the column address range from 0x00 to 0x7F.
        3. Sets the page address range from 0x00 to 0x07.
        4. Writes 0x00 to all columns in each page to clear the display.

        This effectively clears the display by setting all pixels to off.
        """
        self.image = Image.new("1", (self.width, self.height), color=0)
        self.draw = ImageDraw.Draw(self.image)

        self.write_command(0x21)  # Set Column Address
        self.write_command(0x00)  # Column Start
        self.write_command(0x7F)  # Column End
        self.write_command(0x22)  # Set Page Address
        self.write_command(0x00)  # Page Start
        self.write_command(0x07)  # Page End

        for _ in range(128 * (64 // 8)):  # 128 * 8
            self.write_data(bytes([0x00]))  # Clear all pixels
        # for _ in range(self.pages):
        #     self.write_data(bytes([0x00] * self.width))

    def display_image(self):
        """
        Displays the image stored in the `self.image` attribute on the screen.

        This method converts the image into a format suitable for the display by
        iterating over the image pixels and creating a buffer of bytes. Each byte
        represents 8 vertical pixels in a column. The buffer is then sent to the
        display in pages of 8 rows.

        Raises
        ------
        AttributeError
            If `self.image` is not defined or does not have a `load` method.
        """
        buffer = []

        self.draw_line(0, 15, 127, 15, fill=1)
        self.draw_line(0, 16, 127, 16, fill=1)

        pixels = self.image.load()

        for page in range(0, self.height, 8):  # 8 rows per page
            for x in range(self.width):  # Iterate over columns
                byte = 0
                for bit in range(8):
                    if pixels[x, page + bit]:  # If pixel is on
                        byte |= 1 << bit
                buffer.append(byte)

        for page in range(8):
            self.write_command(0xB0 + page)  # Set Page Start Address
            self.write_command(0x00)  # Lower Column Start Address
            self.write_command(0x10)  # Upper Column Start Address
            self.write_data(bytes(buffer[page * 128 : (page + 1) * 128]))

    def clear_rectangle(self, x1, y1, x2, y2):
        """
        Clears a rectangular area on the display by setting the specified rectangle's pixels to 0 (off).

        Parameters
        ----------
        x1 : int
            The x-coordinate of the top-left corner of the rectangle.
        y1 : int
            The y-coordinate of the top-left corner of the rectangle.
        x2 : int
            The x-coordinate of the bottom-right corner of the rectangle.
        y2 : int
            The y-coordinate of the bottom-right corner of the rectangle.
        """
        self.write_command(0x21)  # Set Column Address
        self.write_command(0x00)  # Column Start
        self.write_command(0x7F)  # Column End
        self.write_command(0x22)  # Set Page Address
        self.write_command(0x00)  # Page Start
        self.write_command(0x07)  # Page End

        self.draw.rectangle((x1, y1, x2, y2), fill=0)

    def start_scroll_vertical_right(
        self, start_page=0, end_page=7, speed=2, vertical_offset=1
    ):
        """
        Initiates a vertical and right scroll on the display.

        Parameters
        ----------
        start_page : int, optional
            The starting page address for the scroll. Defaults to 0.
        end_page : int, optional
            The ending page address for the scroll. Defaults to 7.
        speed : int, optional
            The scroll speed, where 0 is the slowest and 7 is the fastest. Defaults to 2.
        vertical_offset : int, optional
            The vertical scroll offset. Defaults to 1.
        """
        self.write_command(0x29)  # Vertical & Right Scroll
        self.write_command(0x00)  # Dummy byte
        self.write_command(start_page)  # Start Page
        self.write_command(speed)  # Scroll speed (0-7)
        self.write_command(end_page)  # End Page
        self.write_command(vertical_offset)  # Vertical scroll offset
        self.write_command(0x2F)  # Start scrolling

    def start_scroll_vertical_left(
        self, start_page=0, end_page=7, speed=2, vertical_offset=1
    ):
        """
        Initiates a vertical and left scroll on the display.

        Parameters
        ----------
        start_page : int, optional
            The starting page address for the scroll. Defaults to 0.
        end_page : int, optional
            The ending page address for the scroll. Defaults to 7.
        speed : int, optional
            The speed of the scroll, where 0 is the fastest and 7 is the slowest. Defaults to 2.
        vertical_offset : int, optional
            The vertical scroll offset. Defaults to 1.
        """
        self.write_command(0x2A)  # Vertical & Left Scroll
        self.write_command(0x00)  # Dummy byte
        self.write_command(start_page)  # Start Page
        self.write_command(speed)  # Scroll speed (0-7)
        self.write_command(end_page)  # End Page
        self.write_command(vertical_offset)  # Vertical scroll offset
        self.write_command(0x2F)  # Start scrolling

    def stop_scroll(self):
        """
        Stops the scrolling on the display.

        This method sends a command to the display to stop any ongoing scrolling
        operation. It writes the command `0x2E` to the display controller to
        achieve this.
        """
        self.write_command(0x2E)  # Stop scrolling

    def draw_text(self, text, x=0, y=0, font_size=12):
        """
        Draws text on the image at the specified coordinates with the given font size.

        Parameters
        ----------
        text : str
            The text to be drawn.
        x : int, optional
            The x-coordinate of the text. Defaults to 0.
        y : int, optional
            The y-coordinate of the text. Defaults to 0.
        font_size : int, optional
            The size of the font. Defaults to 12.

        Raises
        ------
        IOError
            If the specified font file cannot be found, the default font is used.
        """
        try:
            font = ImageFont.truetype(
                "arial.ttf", font_size
            )  # Use built-in Arial font
        except IOError:
            font = ImageFont.load_default()
        self.draw.text((x, y), text, font=font, fill=1)

    def draw_line(self, x1, y1, x2, y2, fill=1):
        """
        Draws a line on the display.

        Parameters
        ----------
        x1 : int
            The x-coordinate of the starting point of the line.
        y1 : int
            The y-coordinate of the starting point of the line.
        x2 : int
            The x-coordinate of the ending point of the line.
        y2 : int
            The y-coordinate of the ending point of the line.
        fill : int, optional
            The color or pattern to fill the line with. Default is 1.
        """
        self.draw.line([x1, y1, x2, y2], fill=fill)


if __name__ == "__main__":
    display = SSD1306()
    display.clear_screen()
    display.draw_text("Hello, World!", x=0, y=0, font_size=12)
    display.display_image()
