"""
Senior Project : Hardware Encryption Device
Team 312
File : interface_manager.py
Description: This will handle the interface with the rpi. GPIO pins will be set up
    and the interface will be handled through this class.
"""

import lgpio
import time
from src.managers.navigation_manager import *


class InterfaceManager:
    def __init__(self, chip_number=0):
        self.handle = lgpio.gpiochip_open(chip_number)

        self._init_gpio()
        self._init_alerts()
        self._init_callbacks()

        # position variable
        self.position = 0
        # Adding last state values for the encoders
        self.last_state_a = 0
        self.last_state_b = 0

    def __del__(self):
        lgpio.gpiochip_close(self.handle)
        self._cancel_callbacks()

    def _init_gpio(self):
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
        # Alerts when the rotary encoder
        lgpio.gpio_claim_alert(self.handle, ENC_A, lgpio.BOTH_EDGES)
        lgpio.gpio_claim_alert(self.handle, ENC_B, lgpio.BOTH_EDGES)
        # Alerts for the switches
        lgpio.gpio_claim_alert(self.handle, SW_1, lgpio.BOTH_EDGES)
        lgpio.gpio_claim_alert(self.handle, SW_2, lgpio.BOTH_EDGES)
        lgpio.gpio_claim_alert(self.handle, SW_3, lgpio.BOTH_EDGES)
        lgpio.gpio_claim_alert(self.handle, SW_4, lgpio.BOTH_EDGES)
        lgpio.gpio_claim_alert(self.handle, SW_5, lgpio.BOTH_EDGES)

    def _encoder_callback(self, chip, gpio, level, timestamp):
        # Logic for reading encoders
        if gpio == ENC_A:
            if self.last_state_a != level:
                if self.position < 5:  # Upper bound for encoder position
                    self.position += 1
                print(f"Position: {self.position}, dir=ccw")
        elif gpio == ENC_B:  # Lower bound for encoder position
            if self.last_state_b != level:
                if self.position > -5:
                    self.position -= 1
                print(f"Position: {self.position}, dir=cw")

        self.last_state_a = level
        self.last_state_b = level

    def _init_callbacks(self):
        self.enc_a_cb = lgpio.callback(
            self.handle, ENC_A, lgpio.BOTH_EDGES, self._encoder_callback
        )
        self.enc_b_cb = lgpio.callback(
            self.handle, ENC_B, lgpio.BOTH_EDGES, self._encoder_callback
        )

    def _cancel_callbacks(self):
        self.enc_a_cb.cancel()
        self.enc_b_cb.cancel()


if __name__ == "__main__":
    try:
        interface = InterfaceManager()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting Program...")
    finally:
        del interface
