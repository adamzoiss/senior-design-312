"""
Senior Project : Hardware Encryption Device
Team 312
File : interface_constants.py
Description: This will handle the constants for the interface/GPIO module.
"""

# GPIO BCM Pin numbers for the ANO rotarty encoder and push buttons
SW_1 = 26  # GPIO pin for push button 1 - pin 37
SW_2 = 19  # GPIO pin for push button 2 - pin 35
SW_3 = 13  # GPIO pin for push button 3 - pin 33
SW_4 = 6  # GPIO pin for push button 4 - pin 31
SW_5 = 5  # GPIO pin for push button 5 - pin 29

ENC_A = 21  # GPIO pin for rotary encoder A - pin 40
ENC_B = 20  # GPIO pin for rotary encoder B - pin 38

# GPIO pin numbers I2C BUS
I2C_SDA = 2  # GPIO pin for I2C SDA - pin 3
I2C_SCL = 3  # GPIO pin for I2C SCL - pin 5

# Display Address
I2C_SLAVE = 0x0703  # ioctl command to set device address
SSD1306_I2C_ADDR = 0x3C  # Common I2C address for SSD1306

# Debounce time in microseconds
DEBOUNCE_MICRO = 1000  # 10ms
