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
        self.position = -1
        # Last state values for the encoders
        self.last_state_a = 0
        self.last_state_b = 0
        # States for the switches
        # bit positions represent switches where SW_5 is the MSB
        self.sw_states = 0b00000

        ##################################################
        display = SSD1306()
        self.nav = NavigationManager(display)
        self.nav.display.clear_screen()
        self.nav.get_screen(Menu)
        self.nav.display.display_image()
        ##################################################

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
        lgpio.gpio_claim_alert(self.handle, SW_1, lgpio.RISING_EDGE)
        lgpio.gpio_claim_alert(self.handle, SW_2, lgpio.RISING_EDGE)
        lgpio.gpio_claim_alert(self.handle, SW_3, lgpio.RISING_EDGE)
        lgpio.gpio_claim_alert(self.handle, SW_4, lgpio.RISING_EDGE)
        lgpio.gpio_claim_alert(self.handle, SW_5, lgpio.RISING_EDGE)

    def _encoder_callback(self, chip, gpio, level, timestamp):
        # Logic for reading encoders
        if gpio == ENC_A:
            if self.last_state_a != level:
                # if self.position < 5:  # Upper bound for encoder position

                # if (
                #     self.position < len(self.nav.CURRENT_SCREEN.SELECTIONS) - 1
                # ):  # Upper bound for encoder position
                #     self.position += 1

                if self.position >= 0:
                    self.position -= 1

                print(f"Position: {self.position}, dir=ccw")
        elif gpio == ENC_B:  # Lower bound for encoder position
            if self.last_state_b != level:
                # if self.position > -5:

                # if self.position >= 0:
                #     self.position -= 1

                if (
                    self.position < len(self.nav.CURRENT_SCREEN.SELECTIONS) - 1
                ):  # Upper bound for encoder position
                    self.position += 1

                print(f"Position: {self.position}, dir=cw")

        self.last_state_a = level
        self.last_state_b = level

        key = next(
            (
                k
                for k, v in self.nav.CURRENT_SCREEN.SELECTIONS.items()
                if v == self.position
            ),
            None,
        )
        # print(key)

        self.nav.select(key)
        self.nav.display.display_image()

    def _switch_callback(self, chip, gpio, level, timestamp):
        # print(gpio, timestamp)
        if gpio == SW_1:
            print("SW1")
            print(self.nav.CURRENT_SCREEN.CURRENT_SELECTION)
            if self.position == self.nav.CURRENT_SCREEN.SELECTIONS["MODE"]:
                self.nav.display.clear_screen()
                self.nav.get_screen(Mode)
                self.nav.display.display_image()
                print("Mode Menu")
        elif gpio == SW_2:
            self.sw_states ^= 1 << 1
            print("SW2")
        elif gpio == SW_3:
            self.sw_states ^= 1 << 2
            print("SW3")
        elif gpio == SW_4:
            self.sw_states ^= 1 << 3
            print("SW4")
        elif gpio == SW_5:
            self.sw_states ^= 1 << 4
            print("SW5")
        print("-" * 20)

    def _init_callbacks(self):
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
            self.handle, SW_3, lgpio.RISING_EDGE, self._switch_callback
        )
        self.sw4_cb = lgpio.callback(
            self.handle, SW_4, lgpio.RISING_EDGE, self._switch_callback
        )
        self.sw5_cb = lgpio.callback(
            self.handle, SW_5, lgpio.RISING_EDGE, self._switch_callback
        )

    def _cancel_callbacks(self):
        self.enc_a_cb.cancel()
        self.enc_b_cb.cancel()
        self.sw1_cb.cancel()
        self.sw2_cb.cancel()
        self.sw3_cb.cancel()
        self.sw4_cb.cancel()
        self.sw5_cb.cancel()


if __name__ == "__main__":
    try:
        interface = InterfaceManager()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting Program...")
    finally:
        del interface
