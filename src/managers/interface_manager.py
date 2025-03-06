"""
Senior Project : Hardware Encryption Device
Team 312
File : interface_manager.py
Description: This will handle the interface with the rpi. GPIO pins will be set up
    and the interface will be handled through this class.
"""

import time
from src.handlers.display_handler import *
from handlers.gpio_handler import *
from src.managers.audio_manager import *
from src.logging.logger import *
from src.managers.thread_manager import ThreadManager
from src.managers.rf_manager import *


class InterfaceManager(GPIOHandler):
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
    nav : DisplayHandler
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

    def __init__(self, thread_manager: ThreadManager, chip_number=0):
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
        # Create the thread manager
        self.thread_manager = thread_manager
        #################################################
        # Set up logging
        self.logger: logging = Logger(
            "InterfaceManager",
            overwrite=True,
            console_level=logging.INFO,
            console_logging=True,
        )
        ##################################################
        # Variable for volume
        self.volume = 50
        # Position variable for menu navigation
        self.position = -1
        # Last state values for the encoders
        self.last_state_a = 0
        self.last_state_b = 0
        ##################################################
        # Integrate audio
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        FRAME_SIZE = 960  # 20ms Opus frame at 48kHz
        PACKET_SIZE = 60  # Radio transceiver limit
        BUFFER_TIMEOUT = 2  # Max seconds to wait for a missing packet
        try:
            self.audio_man = AudioManager(
                self.thread_manager,
                frame_size=FRAME_SIZE,
                format=FORMAT,
                channels=1,
                sample_rate=RATE,
                in_device_index=3,
                out_device_index=0,
            )
        except Exception as e:
            self.logger.critical(
                f"Exception when initialing audio manager: {e}"
            )
        #################################################
        # Display set up
        try:
            self.display = SSD1306(thread_manager)
            self.nav = DisplayHandler(self.display)
            self.nav.display.clear_screen()
            self.nav.get_screen(Menu)
            self.nav.CURRENT_SCREEN.update_volume(self.volume)
            self.nav.display.refresh_display()
        except Exception as e:
            self.logger.critical(f"Exception when initialing display: {e}")
        ##################################################
        # Set up Transmitter
        try:
            self.transmitter = RFManager(
                self.handle, self.thread_manager, self.audio_man
            )
        except Exception as e:
            self.logger.critical(f"Exception when initialing transmitter: {e}")
        ##################################################
        # State that the manager initialized
        self.logger.info("InterfaceManager initialized")

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
        # If in debug mode, do not allow encoder to change volume
        if isinstance(self.nav.CURRENT_SCREEN, Debug):
            return

        # Logic for encoder alerts
        if gpio == ENC_A:
            # Check for if the encoder has been moved counter-clockwise
            if self.last_state_a != level:
                ##############################################################
                # Lower the volume
                if self.volume > 0:
                    self.volume -= 5
                ##############################################################
        elif gpio == ENC_B:
            # Check for if the encoder has been moved clockwise
            if self.last_state_b != level:
                ##############################################################
                # Raise the volume
                if self.volume < 100:
                    self.volume += 5
                ##############################################################
        self.logger.debug(
            (
                f"Chip{chip} | GPIO{gpio} | level: {level} | "
                f"Position: {self.position}"
            )
        )

        # Update last states for the encoders
        self.last_state_a = level
        self.last_state_b = level
        # Update menu selection
        self.nav.update_menu_selection(self.position)
        self.nav.CURRENT_SCREEN.update_volume(self.volume)
        self.audio_man.volume = self.volume
        self.nav.display.refresh_display()

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

        self.logger.debug(
            (
                f"Chip{chip} | GPIO{gpio} | level: {level} | "
                f"Position: {self.position}"
            )
        )

        if gpio == SW_1:  # Select button
            try:
                # If in debug mode, do not allow selection
                if isinstance(self.nav.CURRENT_SCREEN, Debug):
                    return

                # Check if the current screen is the menu
                if isinstance(self.nav.CURRENT_SCREEN, Menu):
                    if (
                        self.position
                        == self.nav.CURRENT_SCREEN.SELECTIONS["MODE"]
                    ):
                        self.nav.display.clear_screen()
                        self.nav.get_screen(Mode)
                        self.nav.CURRENT_SCREEN.update_volume(self.volume)
                        self.nav.display.refresh_display()
                        self.position = -1  # Reset selection position
                elif isinstance(self.nav.CURRENT_SCREEN, Mode):
                    if (
                        self.position
                        == self.nav.CURRENT_SCREEN.SELECTIONS["DEBUG"]
                    ):
                        self.nav.display.clear_screen()
                        self.nav.get_screen(Debug)
                        # self.nav.CURRENT_SCREEN.update_volume(self.volume)
                        self.nav.display.display_image()
                        self.position = -1  # Reset selection position

                        self.thread_manager.start_thread(
                            "Debug", self.nav.CURRENT_SCREEN.display_debug_info
                        )
                else:
                    pass
            except KeyError:
                # Excepting a key error if the selection is not found,
                # this is to prevent the program from crashing
                pass

        elif gpio == SW_2:  # Down arrow
            # If in debug mode, do not allow selection
            if isinstance(self.nav.CURRENT_SCREEN, Debug):
                return

            # Upper bound for valid selection position
            if self.position < len(self.nav.CURRENT_SCREEN.SELECTIONS) - 1:
                self.position += 1

            # Update menu selection
            self.nav.update_menu_selection(self.position)
            self.nav.CURRENT_SCREEN.update_volume(self.volume)
            self.nav.display.refresh_display()

        elif gpio == SW_3:  # TX / Monitor button
            # If in debug mode, do not allow selection
            if isinstance(self.nav.CURRENT_SCREEN, Debug):
                return

            # Checks if switch is pressed, and if so monitors audio
            # TODO Have tx rx implementation
            try:
                match level:
                    case 0:  # Button pressed
                        self.thread_manager.start_thread(
                            TRANSMIT_THREAD,
                            self.transmitter.handle_input_stream,
                        )
                    case 1:  # Button released
                        self.thread_manager.stop_thread(TRANSMIT_THREAD)
                    case _:  # Default case
                        self.logger.error("Error GPIO level is not 0 or 1")
            except Exception as e:
                self.logger.error(f"Error with exception: {e}")

        elif gpio == SW_4:  # Up arrow
            # If in debug mode, do not allow selection
            if isinstance(self.nav.CURRENT_SCREEN, Debug):
                return

            # Lower bound for valid selection position
            if self.position >= 0:
                self.position -= 1

            # Update menu selection
            self.nav.update_menu_selection(self.position)
            self.nav.CURRENT_SCREEN.update_volume(self.volume)
            self.nav.display.refresh_display()

        elif gpio == SW_5:  # Return arrow
            self.thread_manager.stop_all_threads()
            # Checks if the return arrow option is pressed and returns to menu
            if type(self.nav.CURRENT_SCREEN) != Menu:
                self.nav.display.clear_screen()
                self.nav.get_screen(Menu)
                self.nav.CURRENT_SCREEN.update_volume(self.volume)
                self.nav.display.refresh_display()
                self.position = -1  # Reset selection position


if __name__ == "__main__":
    try:
        thread_manager = ThreadManager()
        interface = InterfaceManager(thread_manager)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        interface.logger.info("\nExiting Program...\n")
    finally:
        interface.thread_manager.stop_all_threads()
        interface.nav.display.clear_and_turn_off()
        interface.logger.info("Successfully Exited.")
