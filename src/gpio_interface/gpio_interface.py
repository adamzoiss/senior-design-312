"""
Senior Project : Hardware Encryption Device
Team 312
File : gpio_interface.py
Description: This will handle the interface setup with the rpi. 
             GPIO pins will be set up and alerts created. Callbacks
             will be handled in the InterfaceManager.
"""

import lgpio
from utils.interface_constants import *


class GPIOInterface:
    """
    A class to handle the GPIO interface setup with the Raspberry Pi.

    Attributes
    ----------
    handle : int
        The handle for the GPIO chip.

    Methods
    -------
    __init__(chip_number=0)
        Initializes the GPIO interface.
    __del__()
        Closes the GPIO chip handle.
    _init_gpio()
        Initializes the GPIO pins.
    _init_alerts()
        Initializes the GPIO alerts.
    """

    def __init__(self, chip_number=0):
        """
        Initializes the GPIO interface.

        Parameters
        ----------
        chip_number : int, optional
            The chip number for the GPIO interface. Defaults to 0.
        """
        self.handle = lgpio.gpiochip_open(chip_number)
        self._init_gpio()
        self._init_alerts()

    def __del__(self):
        """
        Closes the GPIO chip handle.
        """
        lgpio.gpiochip_close(self.handle)

    def _init_gpio(self):
        """
        Initializes the GPIO pins.

        This method sets up the GPIO pins for the rotary encoder and push buttons.
        It also sets the debounce time for the pins.
        """
        # Initializing the rotary encoder
        lgpio.gpio_claim_input(self.handle, ENC_A, lgpio.SET_PULL_UP)
        lgpio.gpio_claim_input(self.handle, ENC_B, lgpio.SET_PULL_UP)
        # Initializing the push buttons
        lgpio.gpio_claim_input(self.handle, SW_1, lgpio.SET_PULL_UP)
        lgpio.gpio_claim_input(self.handle, SW_2, lgpio.SET_PULL_UP)
        lgpio.gpio_claim_input(self.handle, SW_3, lgpio.SET_PULL_UP)
        lgpio.gpio_claim_input(self.handle, SW_4, lgpio.SET_PULL_UP)
        lgpio.gpio_claim_input(self.handle, SW_5, lgpio.SET_PULL_UP)
        # Setting debounce for encoders
        lgpio.gpio_set_debounce_micros(self.handle, ENC_A, DEBOUNCE_MICRO)
        lgpio.gpio_set_debounce_micros(self.handle, ENC_B, DEBOUNCE_MICRO)
        # Setting debounce for push buttons
        lgpio.gpio_set_debounce_micros(self.handle, SW_1, DEBOUNCE_MICRO)
        lgpio.gpio_set_debounce_micros(self.handle, SW_2, DEBOUNCE_MICRO)
        lgpio.gpio_set_debounce_micros(self.handle, SW_3, DEBOUNCE_MICRO)
        lgpio.gpio_set_debounce_micros(self.handle, SW_4, DEBOUNCE_MICRO)
        lgpio.gpio_set_debounce_micros(self.handle, SW_5, DEBOUNCE_MICRO)

    def _init_alerts(self):
        """
        Initializes the GPIO alerts.

        This method sets up alerts for the rotary encoder and push buttons.
        """
        # Alerts when the rotary encoder
        lgpio.gpio_claim_alert(self.handle, ENC_A, lgpio.BOTH_EDGES)
        lgpio.gpio_claim_alert(self.handle, ENC_B, lgpio.BOTH_EDGES)
        # Alerts for the switches
        lgpio.gpio_claim_alert(self.handle, SW_1, lgpio.RISING_EDGE)
        lgpio.gpio_claim_alert(self.handle, SW_2, lgpio.RISING_EDGE)
        lgpio.gpio_claim_alert(self.handle, SW_3, lgpio.BOTH_EDGES)
        lgpio.gpio_claim_alert(self.handle, SW_4, lgpio.RISING_EDGE)
        lgpio.gpio_claim_alert(self.handle, SW_5, lgpio.RISING_EDGE)
