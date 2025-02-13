"""
Senior Project : Hardware Encryption Device
Team 312
File : rf_constants.py
Description: This will handle the constatns for the NRF24 RF module.
"""

# nRF24L01 Register addresses (0x00 to 0x1D)
REGISTER_ADDRESSES = list(range(0x00, 0x1E))

# SPI device settings
SPI_BUS = 0  # Adjust based on your SPI setup (usually 0 or 1)
SPI_DEVICE = 0  # Adjust based on chip select (CS) line used

# Define constants for register operations
class SPICommand:
    R_REGISTER          = 0x00  # Base command for reading registers
    W_REGISTER          = 0x20  # Base command for writing registers
    R_RX_PAYLOAD        = 0x61  # Command to read RX payload
    W_TX_PAYLOAD        = 0xA0  # Command to write TX payload
    FLUSH_TX            = 0xE1  # Command to flush TX FIFO
    FLUSH_RX            = 0xE2  # Command to flush RX FIFO
    REUSE_TX_PL         = 0xE3  # Command to reuse TX payload
    ACTIVATE            = 0x50  # Command to activate the nRF24L01
    R_RX_PL_WID         = 0x60  # Command to read RX payload width
    W_ACK_PAYLOAD       = 0xA8  # Command to write ACK payload
    W_TX_PAYLOAD_NO_ACK = 0xB0  # Command to write TX payload without ACK
    NOP                 = 0xFF  # No operation command

class Register:
    REGISTER_MASK = 0x1F  # Mask to limit to valid register addresses
    CONFIG        = 0x00  # Configuration register
    EN_AA         = 0x01  # Enable Auto Acknowledgment register
    EN_RXADDR     = 0x02  # Enable RX addresses register
    SETUP_AW      = 0x03  # Setup Address Width register
    SETUP_RETR    = 0x04  # Setup Auto ReTransmission register
    RF_CH         = 0x05  # RF Channel register
    RF_SETUP      = 0x06  # RF Setup register
    STATUS        = 0x07  # Status register
    OBSERVE_TX    = 0x08  # Transmit observe register
    CD            = 0x09  # Carrier Detect register
    RX_ADDR_P0    = 0x0A  # Receive address data pipe 0
    RX_ADDR_P1    = 0x0B  # Receive address data pipe 1
    RX_ADDR_P2    = 0x0C  # Receive address data pipe 2
    RX_ADDR_P3    = 0x0D  # Receive address data pipe 3
    RX_ADDR_P4    = 0x0E  # Receive address data pipe 4
    RX_ADDR_P5    = 0x0F  # Receive address data pipe 5
    TX_ADDR       = 0x10  # Transmit address
    RX_PW_P0      = 0x11  # Number of bytes in RX payload in data pipe 0
    RX_PW_P1      = 0x12  # Number of bytes in RX payload in data pipe 1
    RX_PW_P2      = 0x13  # Number of bytes in RX payload in data pipe 2
    RX_PW_P3      = 0x14  # Number of bytes in RX payload in data pipe 3
    RX_PW_P4      = 0x15  # Number of bytes in RX payload in data pipe 4
    RX_PW_P5      = 0x16  # Number of bytes in RX payload in data pipe 5
    FIFO_STATUS   = 0x17  # FIFO Status register

    DYNPD         = 0x1C  # Dynamic payload length enable register
    FEATURE       = 0x1D  # Feature register







class CONFIG_REGISTER:
    # Bit masks for the CONFIG register
    MASK_RX_DR  = 0b01000000  # Mask RX data ready interrupt
    MASK_TX_DS  = 0b00100000  # Mask TX data sent interrupt
    MASK_MAX_RT = 0b00010000  # Mask max retransmit interrupt
    EN_CRC      = 0b00001000  # Enable CRC
    CRCO        = 0b00000100  # CRC encoding scheme (1: 2-byte, 0: 1-byte)
    PWR_UP      = 0b00000010  # Power up
    PRIM_RX     = 0b00000001  # Primary RX mode

class EN_AA_REGISTER:
    # Bit masks for the EN_AA register
    ENAA_P5 = 0b00100000  # Enable auto acknowledgment on pipe 5
    ENAA_P4 = 0b00010000  # Enable auto acknowledgment on pipe 4
    ENAA_P3 = 0b00001000  # Enable auto acknowledgment on pipe 3
    ENAA_P2 = 0b00000100  # Enable auto acknowledgment on pipe 2
    ENAA_P1 = 0b00000010  # Enable auto acknowledgment on pipe 1
    ENAA_P0 = 0b00000001  # Enable auto acknowledgment on pipe 0

class EN_RXADDR_REGISTER:
    # Bit masks for the EN_RXADDR register
    ERX_P5 = 0b00100000  # Enable RX address on pipe 5
    ERX_P4 = 0b00010000  # Enable RX address on pipe 4
    ERX_P3 = 0b00001000  # Enable RX address on pipe 3
    ERX_P2 = 0b00000100  # Enable RX address on pipe 2
    ERX_P1 = 0b00000010  # Enable RX address on pipe 1
    ERX_P0 = 0b00000001  # Enable RX address on pipe 0

class SETUP_AW_REGISTER:
    # Bit masks for the SETUP_AW register
    AW = 0b00000011  # Address width (3 bits)

class SETUP_RETR_REGISTER:
    # Bit masks for the SETUP_RETR register
    ARD = 0b11110000  # Auto retransmit delay (4 bits)
    ARC = 0b00001111  # Auto retransmit count (4 bits)

class RF_CH_REGISTER:
    # Bit masks for the RF_CH register
    RF_CH = 0b01111111  # RF channel (7 bits)

class RF_SETUP_REGISTER:
    # Bit masks for the RF_SETUP register
    PLL_LOCK  = 0b00010000  # PLL lock
    RF_DR     = 0b00001000  # RF data rate (1: 2Mbps, 0: 1Mbps)
    RF_PWR    = 0b00000110  # RF power (2 bits)
    LNA_HCURR = 0b00000001  # LNA current

class STATUS_REGISTER:
    # Bit masks for the STATUS register
    RX_DR   = 0b01000000  # Data ready RX FIFO interrupt
    TX_DS   = 0b00100000  # Data sent TX FIFO interrupt
    MAX_RT  = 0b00010000  # Max retransmit interrupt
    RX_P_NO = 0b00001110  # Received pipe number (3 bits)
    TX_FULL = 0b00000001  # TX FIFO full

class OBSERVE_TX_REGISTER:
    # Bit masks for the OBSERVE_TX register
    PLOS_CNT = 0b11110000  # Payload lost count (4 bits)
    ARC_CNT  = 0b00001111  # Auto retransmit count (4 bits)

class CD_REGISTER:
    # Bit masks for the CD register
    CD = 0b00000001  # Carrier detect

