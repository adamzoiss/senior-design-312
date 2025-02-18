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
from src.gpio_interface.gpio_interface import *


class InterfaceManager(GPIOInterface):
    def __init__(self, chip_number=0):
        # Call base class constructor
        super().__init__(chip_number)
        # Initialize the callbacks
        self._init_callbacks()
        #################################################
        # Position variable for menu navigation
        self.position = -1
        # Last state values for the encoders
        self.last_state_a = 0
        self.last_state_b = 0
        # States for the switches - Bit positions represent switches
        #   where SW_5 is the MSB
        self.sw_states = 0b00000
        #################################################
        # Display set up
        display = SSD1306()
        self.nav = NavigationManager(display)
        self.nav.display.clear_screen()
        self.nav.get_screen(Menu)
        self.nav.display.display_image()
        ##################################################

    def __del__(self):
        super().__del__()
        self._cancel_callbacks()

    def _encoder_callback(self, chip, gpio, level, timestamp):
        # Logic for encoder alerts
        if gpio == ENC_A:
            # Check for if the encoder has been moved counter-clockwise
            if self.last_state_a != level:
                # Lower bound for valid encoder position
                if self.position >= 0:
                    self.position -= 1
                # print(f"Position: {self.position}, dir=ccw")
        elif gpio == ENC_B:
            # Check for if the encoder has been moved clockwise
            if self.last_state_b != level:
                # Upper bound for valid encoder position
                if self.position < len(self.nav.CURRENT_SCREEN.SELECTIONS) - 1:
                    self.position += 1
                # print(f"Position: {self.position}, dir=cw")

        # Update last states for the encoders
        self.last_state_a = level
        self.last_state_b = level
        # Update menu selection
        self.nav.update_menu_selection(self.position)
        self.nav.display.display_image()

    def _switch_callback(self, chip, gpio, level, timestamp):
        # print(gpio, timestamp)
        if gpio == SW_1:
            print("SW1")
            print(self.nav.CURRENT_SCREEN.CURRENT_SELECTION)
            try:
                if self.position == self.nav.CURRENT_SCREEN.SELECTIONS["MODE"]:
                    self.nav.display.clear_screen()
                    self.nav.get_screen(Mode)
                    self.nav.display.display_image()
                    print("Mode Menu")
                    self.position = -1
            except KeyError:
                pass

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
            if type(self.nav.CURRENT_SCREEN) != Menu:
                self.nav.display.clear_screen()
                self.nav.get_screen(Menu)
                self.nav.display.display_image()
                self.position = -1
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
