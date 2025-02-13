"""
Senior Project : Hardware Encryption Device
Team 312
File : rf_manager.py
Description: This will handle the connection to the NRF24 RF module. Any data being
    sent or received via RF waves will be handled through this class.
"""

import spidev
import lgpio
import time
from src.utils.rf_constants import *

# GPIO settings
CE_PIN = 25  # Chip Enable pin (GPIO pin number)

class NRF24l01:
    """Class to handle nRF24L01 operations."""

    def __init__(self):
        """Initialize the nRF24L01 class."""

        self.h = None
        
        self._init_spi() # Initialize SPI
        self._init_gpio() # Initialize GPIO


    def _init_spi(self):
        """Initialize SPI connection."""
        try:
            self.spi = spidev.SpiDev() # Create SPI object
            self.spi.open(SPI_BUS, SPI_DEVICE) # Open SPI port
            self.spi.max_speed_hz = 1000000 # Set SPI speed (1 MHz)
            self.spi.mode = 0
        except Exception as e:
            print(f"Error initializing SPI: {e}")
            raise

    def _init_gpio(self):
        """Initialize GPIO for nRF24L01."""
        try:
            self.h = lgpio.gpiochip_open(0)  # Open GPIO chip
            lgpio.gpio_claim_output(self.h, CE_PIN, 0)  # Set CE pin as output and low
        except Exception as e:
            print(f"Error initializing GPIO: {e}")
            raise

    def set_ce_high(self):
        """Set CE pin high."""
        lgpio.gpio_write(self.h, CE_PIN, 1)  # Set CE pin high

    def set_ce_low(self):
        """Set CE pin low."""
        lgpio.gpio_write(self.h, CE_PIN, 0)  # Set CE pin low

    def __del__(self):
        """Destructor to close SPI connection."""
        self._close()

    def read_register(self, reg):
        """Read a single register from the nRF24L01."""
        reg = SPICommand.R_REGISTER | (reg & Register.REGISTER_MASK)
        response = self.spi.xfer2([reg, 0xFF])
        return response[1]
    
    def write_register(self, reg, value):
        """Write a value to a register on the nRF24L01."""
        reg = SPICommand.W_REGISTER | (reg & Register.REGISTER_MASK)
        self.spi.xfer2([reg, value])

    def read_all_registers(self):
        """Read all the registers of the nRF24L01 and return as a dictionary."""
        register_values = {}
        for reg in REGISTER_ADDRESSES:
            value = self.read_register(reg)
            register_values[reg] = value
        return register_values

    def _close(self):
        """Close the SPI connection."""
        self.spi.close()
        lgpio.gpiochip_close(self.h)  # Close GPIO chip

    def write_payload(self, payload):
        """Write a payload to the TX FIFO."""
        self.spi.xfer2([SPICommand.W_TX_PAYLOAD] + list(payload))

    def read_payload(self):
        """Read a payload from the RX FIFO."""
        response = self.spi.xfer2([SPICommand.R_RX_PAYLOAD] + [0x00] * 32)
        return response[1:]
    
    def activate(self):
        """Activate the nRF24L01."""
        self.spi.xfer2([SPICommand.ACTIVATE, 0x73])

    def flush_tx(self):
        """Flush the TX FIFO."""
        self.spi.xfer2([SPICommand.FLUSH_TX])

    def flush_rx(self):
        """Flush the RX FIFO."""
        self.spi.xfer2([SPICommand.FLUSH_RX])
    
    def tx_mode(self):
        """Set the nRF24L01 to TX mode."""
        self.write_register(0x00, 0x0E)  # Set CONFIG register to enable TX mode

    def rx_mode(self):
        """Set the nRF24L01 to RX mode."""
        self.write_register(0x00, 0x0F)  # Set CONFIG register to enable RX mode







def close_gpio():
    """Close GPIO resources."""
    lgpio.gpiochip_close(0)  # Close GPIO chip



def read_register(spi, reg):
    """Read a single register from the nRF24L01."""
    reg = SPICommand.R_REGISTER | (reg & Register.REGISTER_MASK)  # Ensure proper read command
    response = spi.xfer2([reg, 0xFF])  # Send read command and dummy byte
    return response[1]  # Second byte is the register value

def write_register(spi, reg, value):
    """Write a value to a register on the nRF24L01."""
    reg = SPICommand.W_REGISTER | (reg & Register.REGISTER_MASK)  # Ensure proper write command
    spi.xfer2([reg, value])  # Send write command and value

def read_all_registers(spi):
    """Read all the registers of the nRF24L01 and return as a dictionary."""
    register_values = {}
    for reg in REGISTER_ADDRESSES:
        value = read_register(spi, reg)
        register_values[reg] = value
    return register_values

def main():
    spi = spidev.SpiDev()  # Create SPI object
    spi.open(SPI_BUS, SPI_DEVICE)  # Open SPI port
    spi.max_speed_hz = 1000000  # Set SPI speed (1 MHz)
    spi.mode = 0  # SPI mode 0 (CPOL=0, CPHA=0)

    print("Reading all nRF24L01 registers...\n")
    registers = read_all_registers(spi)

    print("Register | Hex Value | Binary Value")
    print("-" * 40)
    for reg, value in registers.items():
        print(f"   {reg:#04x}   |   {value:#04x}   | {bin(value)[2:].zfill(8)}")

    # Example: Writing to CONFIG register (0x00)
    print("\nWriting 0x0F to CONFIG register (0x00)...")
    write_register(spi, 0x00, 0xFF)

    # Verify the write
    new_value = read_register(spi, 0x00)
    print(f"New CONFIG Register Value: {new_value:#04x} ({bin(new_value)[2:].zfill(8)})")

    spi.close()  # Close SPI connection

if __name__ == "__main__":
    # main()
    nrf = NRF24l01()
    # nrf.activate()

    nrf.write_register(Register.CONFIG, 0x02)  # Set CONFIG register to enable TX mode
    nrf.write_register(Register.EN_AA, 0x00)  # Disable Auto Acknowledgment
    nrf.write_register(Register.EN_RXADDR, 0x01)  # Enable RX address
    nrf.write_register(Register.SETUP_AW, 0x03)  # Set Address Width to 5 bytes
    nrf.write_register(Register.SETUP_RETR, 0x00)  # Retransmission disabled
    nrf.write_register(Register.RF_CH, 0x02)  # Set RF Channel to 2
    nrf.write_register(Register.RF_SETUP, 0x06)  # Set RF Setup register
    nrf.write_register(Register.STATUS, 0x70)  # Set STATUS register

    nrf.set_ce_low() 

    time.sleep(1)


    registers = nrf.read_all_registers()
    print("Register | Hex Value | Binary Value")
    print("-" * 40)
    for reg, value in registers.items():
        print(f"   {reg:#04x}   |   {value:#04x}   | {bin(value)[2:].zfill(8)}")

    
    
    print("-" * 40)
    print("-" * 40)
    nrf.flush_tx()
    time.sleep(0.5)
    print("1. Reading register 0x17:", bin(nrf.read_register(0x17))[2:].zfill(8))
    print("-" * 40)
    print("-" * 40)

    print("-" * 40)
    print("-" * 40)
    nrf.write_payload([0x01, 0x02, 0x03, 0x04, 0x05, 0x06])
    nrf.write_payload([0x01, 0x02, 0x03, 0x04, 0x05, 0x06])
    nrf.write_payload([0x01, 0x02, 0x03, 0x04, 0x05])
    # nrf.write_payload([0x01, 0x02, 0x03, 0x04, 0x05])
    time.sleep(0.5)
    print("2. Reading register 0x17:", bin(nrf.read_register(0x17))[2:].zfill(8))
    print("-" * 40)
    print("Setting CE High for 5 sec, then reading FIFO STATUS REGISTER")
    nrf.set_ce_high()
    time.sleep(5)
    print("2. Reading register 0x17:", bin(nrf.read_register(0x17))[2:].zfill(8))
    print("-" * 40)

    # set_ce_high()
    # nrf.write_register(0x00, 0x0E)  # Set CONFIG register to enable TX mode
    




    # #Enter RX mode and continuously receive:
    # nrf.rx_mode()
    # nrf.flush_rx()
    
    # while True:
    #     res = nrf.read_payload()
    #     print(f"Payload Received {res}")
    #     time.sleep(1)