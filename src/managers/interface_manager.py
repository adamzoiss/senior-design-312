"""
Senior Project : Hardware Encryption Device
Team 312
File : interface_manager.py
Description: This will handle the interface with the rpi. GPIO pins will be set up
    and the interface will be handled through this class.
"""

import time
from src.managers.navigation_manager import *
from src.gpio_interface.gpio_interface import *
from src.managers.audio_manager import *


class InterfaceManager(GPIOInterface):
    """
    A class to manage the interface with the Raspberry Pi, including GPIO pins setup and handling.

    Attributes
    ----------
    position : int
        The current position for menu navigation.
    last_state_a : int
        The last state value for encoder A.
    last_state_b : int
        The last state value for encoder B.
    nav : NavigationManager
        The navigation manager for the display.
    audio_man : AudioManager
        The audio manager for handling audio operations.

    Methods
    -------
    __init__(chip_number=0)
        Initializes the InterfaceManager with the given chip number.
    __del__()
        Cleans up resources and cancels callbacks.
    _encoder_callback(chip, gpio, level, timestamp)
        Handles the encoder callback events.
    _switch_callback(chip, gpio, level, timestamp)
        Handles the switch callback events.
    _init_callbacks()
        Initializes the GPIO callbacks.
    _cancel_callbacks()
        Cancels the GPIO callbacks.
    """

    def __init__(self, chip_number=0):
        """
        Initializes the InterfaceManager with the given chip number.

        Parameters
        ----------
        chip_number : int, optional
            The chip number for the GPIO interface. Defaults to 0.
        """
        # Call base class constructor
        super().__init__(chip_number)
        #################################################
        # Position variable for menu navigation
        self.position = -1
        # Last state values for the encoders
        self.last_state_a = 0
        self.last_state_b = 0
        #################################################
        # Display set up
        self.display = SSD1306()
        self.nav = NavigationManager(self.display)
        self.nav.display.clear_screen()
        self.nav.get_screen(Menu)
        self.nav.display.display_image()
        ##################################################
        # Integrate audio
        self.audio_man = AudioManager()
        ##################################################
        print("Program Started")

    def __del__(self):
        """
        Cleans up resources and cancels callbacks.
        """
        super().__del__()

    def _encoder_callback(self, chip, gpio, level, timestamp):
        """
        Handles the encoder callback events.

        Parameters
        ----------
        chip : int
            The chip number.
        gpio : int
            The GPIO pin number.
        level : int
            The level of the GPIO pin.
        timestamp : int
            The timestamp of the event.
        """
        # Logic for encoder alerts
        if gpio == ENC_A:
            # Check for if the encoder has been moved counter-clockwise
            if self.last_state_a != level:
                # Lower bound for valid encoder position
                if self.position >= 0:
                    self.position -= 1
        elif gpio == ENC_B:
            # Check for if the encoder has been moved clockwise
            if self.last_state_b != level:
                # Upper bound for valid encoder position
                if self.position < len(self.nav.CURRENT_SCREEN.SELECTIONS) - 1:
                    self.position += 1

        # Update last states for the encoders
        self.last_state_a = level
        self.last_state_b = level
        # Update menu selection
        self.nav.update_menu_selection(self.position)
        self.nav.display.display_image()

    def _switch_callback(self, chip, gpio, level, timestamp):
        """
        Handles the switch callback events.

        Parameters
        ----------
        chip : int
            The chip number.
        gpio : int
            The GPIO pin number.
        level : int
            The level of the GPIO pin.
        timestamp : int
            The timestamp of the event.
        """
        if gpio == SW_1:
            print(f"SW1: {level}")
            print(self.nav.CURRENT_SCREEN.CURRENT_SELECTION)
            try:
                if self.position == self.nav.CURRENT_SCREEN.SELECTIONS["MODE"]:
                    self.nav.display.clear_screen()
                    self.nav.get_screen(Mode)
                    self.nav.display.display_image()
                    print("Mode Menu")
                    self.position = -1
                elif True:  # TODO ADD MORE FUNCTIONALITY
                    pass
            except KeyError:
                pass
        elif gpio == SW_2:
            # Down arrow
            # TODO Implement
            if self.position < len(self.nav.CURRENT_SCREEN.SELECTIONS) - 1:
                self.position += 1

            # Update menu selection
            self.nav.update_menu_selection(self.position)
            self.nav.display.display_image()
            print(f"SW2: {level}")
        elif gpio == SW_3:
            print(f"SW3: {level}")
            # Checks if switch is pressed, and if so monitors audio
            # TODO Have tx rx implementation
            match level:
                case 0:
                    if (
                        self.audio_man.thread is None
                        or not self.audio_man.thread.is_alive()
                    ):
                        self.audio_man.start_thread()
                case 1:
                    self.audio_man.stop_thread()
                case _:
                    print("Error GPIO level is not 0 or 1")

        elif gpio == SW_4:
            # Up arrow
            # TODO Implement
            # Lower bound for valid encoder position
            if self.position >= 0:
                self.position -= 1

            # Update menu selection
            self.nav.update_menu_selection(self.position)
            self.nav.display.display_image()
            print(f"SW4: {level}")
        elif gpio == SW_5:
            print(f"SW5: {level}")
            # Checks if the return arrow option is pressed and returns to menu
            if type(self.nav.CURRENT_SCREEN) != Menu:
                self.nav.display.clear_screen()
                self.nav.get_screen(Menu)
                self.nav.display.display_image()
                self.position = -1
        print("-" * 20)


if __name__ == "__main__":
    try:
        interface = InterfaceManager()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting Program...\n")
    finally:
        interface.nav.display.clear_and_turn_off()
        print("Successfully Exited.")
