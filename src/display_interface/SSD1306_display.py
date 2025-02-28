"""
Senior Project : Hardware Encryption Device
Team 312
File : SSD1306_display.py
Description: Interfaces with the SSD1306 OLED display.
"""

import fcntl
import os
from typing import int, str
from PIL import Image, ImageDraw, ImageFont
from src.utils.interface_constants import *
import struct


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

    def __init__(self, i2c_bus: int = 1, width: int = 128, height: int = 64):
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

    def __del__(self):
        self.clear_and_turn_off()

    def clear_and_turn_off(self):
        """
        Clears the display and turns it off.

        This method clears the display by writing 0x00 to all GDDRAM and then
        sends the command to turn off the display.
        """
        self.clear_screen()
        self.write_command(0xAE)  # Display OFF

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

    def write_data(self, data: int):
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
            0xD5,
            0x80,  # Set display clock divide ratio/oscillator frequency
            0xA8,
            0x3F,  # Multiplex ratio (64)
            0xD3,
            0x00,  # Display offset
            0x40,  # Start line (0)
            0x8D,
            0x14,  # Enable charge pump
            0x20,
            0x00,  # Set memory addressing mode to Horizontal
            0xA1,  # Segment re-map (mirror horizontally)
            0xC8,  # COM output scan direction (mirror vertically)
            0xDA,
            0x12,  # Set COM pins hardware configuration
            0x81,
            0xCF,  # Set contrast control
            0xD9,
            0xF1,  # Set pre-charge period
            0xDB,
            0x40,  # Set VCOMH deselect level
            0xA4,  # Output follows RAM content
            0xA6,  # Normal display mode
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
        # #####################################
        # Lines separating yellow from blue segment
        self.draw_line(0, 15, 127, 15, fill=1)
        self.draw_line(0, 16, 127, 16, fill=1)
        # #####################################
        # Display interface usage on screen
        self.draw_circle(102, 40, 10, fill=None)
        self.draw_circle(102, 40, 23, fill=None)
        # Switch 1 - Select
        self.draw_text("SEL", 95, 36, font_size=8)
        # Switch 2 - Down arrow
        self.draw_text(
            "D", 99, 51, font_size=14, font_file="assets/Arrows.ttf"
        )
        # Switch 3 - Transmit/Monitor
        # TODO - implement
        # Switch 4 - Up arrow
        self.draw_text(
            "C", 99, 18, font_size=14, font_file="assets/Arrows.ttf"
        )
        # Switch 5 - Return arrow
        self.draw_rotated_text(
            "u", 86, 40, angle=90, font_size=12, font_file="assets/arrow_7.ttf"
        )
        # #####################################

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

    def clear_rectangle(self, x1: int, y1: int, x2: int, y2: int):
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
        self,
        start_page: int = 0,
        end_page: int = 7,
        speed: int = 2,
        vertical_offset: int = 1,
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
        self,
        start_page: int = 0,
        end_page: int = 7,
        speed: int = 2,
        vertical_offset: int = 1,
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

    def draw_text(
        self,
        text: str,
        x: int = 0,
        y: int = 0,
        font_size: int = 12,
        font_file: int = "assets/arial.ttf",
    ):
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
                font_file, font_size
            )  # Use built-in Arial font
            # print("Font loaded!")
        except IOError:
            font = ImageFont.load_default()
        self.draw.text((x, y), text, font=font, fill=1)

    def draw_line(self, x1: int, y1: int, x2: int, y2: int, fill: int = 1):
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

    def draw_circle(
        self, x: int, y: int, radius: int, outline: int = 1, fill: int = 0
    ):
        """
        Draws a circle on the display.

        Parameters
        ----------
        x : int
            The x-coordinate of the center of the circle.
        y : int
            The y-coordinate of the center of the circle.
        radius : int
            The radius of the circle.
        outline : int, optional
            The color or pattern to outline the circle with. Default is 1.
        fill : int, optional
            The color or pattern to fill the circle with. Default is 0.
        """
        self.draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            outline=outline,
            fill=fill,
        )

    def draw_rotated_text(
        self,
        text: str,
        x: int = 0,
        y: int = 0,
        angle: int = 0,
        font_size: int = 12,
        font_file: int = "assets/arial.ttf",
    ):
        """
        Draws rotated text on the display at the specified coordinates.

        Parameters
        ----------
        text : str
            The text to be drawn.
        x : int, optional
            The x-coordinate of the text. Defaults to 0.
        y : int, optional
            The y-coordinate of the text. Defaults to 0.
        angle : int, optional
            The angle to rotate the text counterclockwise. Defaults to 0.
        font_size : int, optional
            The size of the font. Defaults to 12.
        font_file : str, optional
            The font file to use. Defaults to "assets/arial.ttf".
        """
        try:
            font = ImageFont.truetype(font_file, font_size)
        except IOError:
            font = ImageFont.load_default()

        # Create a temporary image to render the text
        text_size = self.draw.textbbox((0, 0), text, font=font)
        text_width = text_size[2] - text_size[0]
        text_height = text_size[3] - text_size[1]

        text_image = Image.new("1", (text_width, text_height), color=0)
        temp_draw = ImageDraw.Draw(text_image)
        temp_draw.text((0, 0), text, font=font, fill=1)

        # Rotate the text image
        rotated_text = text_image.rotate(angle, expand=True)

        # Get new dimensions after rotation
        rotated_width, rotated_height = rotated_text.size

        # Paste the rotated text onto the main image with transparency
        self.image.paste(
            rotated_text,
            (x - rotated_width // 2, y - rotated_height // 2),
            rotated_text,
        )


if __name__ == "__main__":
    display = SSD1306()
    display.clear_screen()
    display.draw_text("Hello, World!", x=0, y=0, font_size=12)
    display.display_image()

    import time

    display.clear_screen()
    start_time = time.time()
    display.draw_text("Hello, World!", x=0, y=0, font_size=12)
    display.display_image()
    end_time = time.time()
    time_taken = (end_time - start_time) * 1_000_000  # Convert to microseconds
    print(f"Time taken to display image: {time_taken:.2f} microseconds")

    import time

    time.sleep(5)
    del display
