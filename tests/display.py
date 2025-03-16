import fcntl
import os

# Constants
I2C_BUS = 1
SSD1306_I2C_ADDR = 0x3C  # Adjust if necessary
I2C_SLAVE = 0x0703
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 64

# Open I2C device
i2c_dev = os.open(f"/dev/i2c-{I2C_BUS}", os.O_RDWR)
fcntl.ioctl(i2c_dev, I2C_SLAVE, SSD1306_I2C_ADDR)


def write_command(cmd):
    """Send a command byte to the SSD1306 display."""
    os.write(i2c_dev, bytes([0x00, cmd]))


def write_data(data: int):
    """Send data bytes to the SSD1306 display."""
    os.write(i2c_dev, bytes([0x40]) + data)


def initialize_display():
    """Initialize the SSD1306 OLED display."""
    commands = [
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
    for cmd in commands:
        write_command(cmd)


def clear_display():
    """Clears the display by filling the GDDRAM with 0x00."""
    write_command(0x21)  # Column address
    write_command(0x00)  # Start column
    write_command(0x7F)  # End column
    write_command(0x22)  # Page address
    write_command(0x00)  # Start page
    write_command(0x07)  # End page

    for _ in range(DISPLAY_WIDTH * (DISPLAY_HEIGHT // 8)):  # 128 * 8
        write_data(bytes([0x00]))  # Clear all pixels


def draw_horizontal_line(y=32):
    """
    Draws a horizontal line at the given `y` position.
    The line spans the full width of the display.
    """
    page = y // 8  # Each page stores 8 vertical pixels
    bit_pos = y % 8  # The bit position inside the byte

    # Set page and column range
    write_command(0xB0 + page)  # Set page start address
    write_command(0x00)  # Lower column start address
    write_command(0x10)  # Upper column start address

    # Send data for each column in the page
    for _ in range(DISPLAY_WIDTH):
        write_data(
            bytes([1 << bit_pos])
        )  # Set the bit for the horizontal line


# Run display sequence
initialize_display()
clear_display()
draw_horizontal_line()
