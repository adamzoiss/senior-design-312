import spidev
import time


def read_rfm69_register(register, spi_bus=0, spi_device=1, speed_hz=400000):
    """
    Reads a register from the RFM69HCW module over SPI.

    :param register: The 8-bit register address to read.
    :param spi_bus: SPI bus number (default 0).
    :param spi_device: SPI device (CE0=0, CE1=1).
    :param speed_hz: SPI clock speed in Hz.
    :return: The value read from the register.
    """
    spi = spidev.SpiDev()
    spi.open(spi_bus, spi_device)  # Open SPI bus 0, device 0
    spi.max_speed_hz = speed_hz  # Set SPI clock speed
    spi.mode = 0  # SPI Mode 0 (CPOL=0, CPHA=0)

    register_address = register & 0x7F  # Ensure MSB is 0 for reading
    response = spi.xfer(
        [register_address, 0x00]
    )  # Send address and receive response

    spi.close()  # Close SPI connection

    return response[1]  # The second byte contains the register value


# Read and print the value of register 0x10
rfm69_value = read_rfm69_register(0x10)
print(f"Register 0x10 Value: 0x{rfm69_value:02X}")
