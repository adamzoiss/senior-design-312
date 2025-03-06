"""
Senior Project : Hardware Encryption Device
Team 312
File : gpio_interface.py
Description: This will handle the interface setup with the rpi.
             GPIO pins will be set up and alerts created. Callbacks
             will be handled in the InterfaceManager.
"""

import lgpio
from src.utils.constants import *


class GPIOHandler:
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
        # Initialize GPIO
        self._init_gpio()
        # Initialize alerts
        self._init_alerts()
        # Initialize the callbacks
        self._init_callbacks()

    def __del__(self):
        """
        Closes the GPIO chip handle.
        """
        self._cancel_callbacks()
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
        lgpio.gpio_set_debounce_micros(self.handle, ENC_A, 50)
        lgpio.gpio_set_debounce_micros(self.handle, ENC_B, 50)
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
        # Alert for incoming packet
        # lgpio.gpio_claim_alert(self.handle, G0, lgpio.RISING_EDGE)

    def _encoder_callback(self, chip, gpio, level, timestamp):
        # print(
        #     (
        #         f"Chip: {chip} | "
        #         f"GPIO{gpio} | "
        #         f"Level: {level} | "
        #         f"Timestamp: {timestamp}"
        #     )
        # )
        pass

    def _switch_callback(self, chip, gpio, level, timestamp):
        # print(
        #     (
        #         f"Chip: {chip} | "
        #         f"GPIO{gpio} | "
        #         f"Level: {level} | "
        #         f"Timestamp: {timestamp}"
        #     )
        # )
        pass

    def _init_callbacks(self):
        """
        Initializes the GPIO callbacks.

        This method sets up the callbacks for the rotary encoder and push buttons.
        """
        # Encoder callbacks
        self.enc_a_cb = lgpio.callback(
            self.handle, ENC_A, lgpio.BOTH_EDGES, self._encoder_callback
        )
        self.enc_b_cb = lgpio.callback(
            self.handle, ENC_B, lgpio.BOTH_EDGES, self._encoder_callback
        )
        # Switch callbacks
        self.sw1_cb = lgpio.callback(
            self.handle, SW_1, lgpio.RISING_EDGE, self._switch_callback
        )
        self.sw2_cb = lgpio.callback(
            self.handle, SW_2, lgpio.RISING_EDGE, self._switch_callback
        )
        self.sw3_cb = lgpio.callback(
            self.handle, SW_3, lgpio.BOTH_EDGES, self._switch_callback
        )
        self.sw4_cb = lgpio.callback(
            self.handle, SW_4, lgpio.RISING_EDGE, self._switch_callback
        )
        self.sw5_cb = lgpio.callback(
            self.handle, SW_5, lgpio.RISING_EDGE, self._switch_callback
        )
        # Packet callback
        # self.pkt_cb = lgpio.callback(
        #     self.handle, G0, lgpio.RISING_EDGE, self._pkt_callback
        # )

    def _cancel_callbacks(self):
        """
        Cancels the GPIO callbacks.

        This method cancels the callbacks for the rotary encoder and push buttons.
        """
        self.enc_a_cb.cancel()
        self.enc_b_cb.cancel()
        self.sw1_cb.cancel()
        self.sw2_cb.cancel()
        self.sw3_cb.cancel()
        self.sw4_cb.cancel()
        self.sw5_cb.cancel()
        # self.pkt_cb.cancel()


if __name__ == "__main__":
    import time

    gpio_interface = GPIOHandler()
    while True:
        time.sleep(1)
