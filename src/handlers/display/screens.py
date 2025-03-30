"""
Senior Project : Hardware Encryption Device
Team 312
File : screens.py
Description: This file holds various "Screens" to be used on
             the display.
"""

import threading
from collections import deque
import time

from src.handlers.display.base_screen import *
from src.utils.utils import parse_log_line
from src.utils.constants import *


class Menu(Screen):
    """
    A class to represent the menu screen.

    Attributes
    ----------
    SELECTIONS : dict
        A dictionary of selectable options.
    """

    def __init__(self, display: SSD1306):
        """
        Initializes the Menu with the specified display.

        Parameters
        ----------
        display : SSD1306
            The display object to draw on.
        """
        super().__init__(display)
        self.SELECTIONS["SETTINGS"] = 0
        self.SELECTIONS["MODE"] = 1

    def draw_screen(self):
        """
        Draws the menu screen.
        """
        self.display.draw_text("MENU", x=5, y=2, font_size=12)
        self.display.draw_text("Settings", x=5, y=20, font_size=10)
        self.display.draw_text("Mode", x=5, y=35, font_size=10)


class Settings(Screen):
    """
    A class to represent the settings screen.

    Attributes
    ----------
    SELECTIONS : dict
        A dictionary of selectable options.
    """

    def __init__(self, display: SSD1306):
        """
        Initializes the Settings with the specified display.

        Parameters
        ----------
        display : SSD1306
            The display object to draw on.
        """
        super().__init__(display)
        self.SELECTIONS["ENC"] = 0

    def draw_screen(self, en_enc=ENCRYPTION):
        """
        Draws the settings screen.
        """
        self.display.draw_text("SETTINGS", x=5, y=2, font_size=12)
        self.display.draw_text(
            f"ENC ({'ON' if en_enc else 'OFF'})",
            x=5,
            y=20,
            font_size=10,
        )


class Mode(Screen):
    """
    A class to represent the mode selection screen.

    Attributes
    ----------
    SELECTIONS : dict
        A dictionary of selectable options.
    """

    def __init__(self, display: SSD1306):
        """
        Initializes the Mode with the specified display.

        Parameters
        ----------
        display : SSD1306
            The display object to draw on.
        """
        super().__init__(display)
        self.SELECTIONS["RADIO"] = 0
        self.SELECTIONS["LOCAL"] = 1
        self.SELECTIONS["DEBUG"] = 2

    def draw_screen(self):
        """
        Draws the mode selection screen.
        """
        self.display.draw_text("MODE", x=5, y=2, font_size=12)
        self.display.draw_text("Radio", x=5, y=20, font_size=10)
        self.display.draw_text("Local", x=5, y=35, font_size=10)
        self.display.draw_text("Debug", x=5, y=50, font_size=10)


class Debug(Screen):
    """
    A class to represent the mode selection screen.

    Attributes
    ----------
    SELECTIONS : dict
        A dictionary of selectable options.
    """

    def __init__(self, display: SSD1306):
        """
        Initializes the Mode with the specified display.

        Parameters
        ----------
        display : SSD1306
            The display object to draw on.
        """
        super().__init__(display)

    def draw_screen(self):
        """
        Draws the mode selection screen.
        """
        self.display.draw_text("Debug", x=5, y=2, font_size=12)

    def display_debug_info(self, stop_event: threading.Event):
        """
        Continuously reads the latest log entries from a log file and displays them on the screen.
        Parameters
        ----------
        stop_event : threading.Event
            An event to signal when to stop reading and displaying log entries.
        Notes
        -----
        - This function reads the log file "logs/project.log" and displays the last few entries on the screen.
        - The screen is cleared and redrawn with each new log entry.
        - The function will continue to run until the `stop_event` is set.
        - It uses a deque to store and display only the last few log entries.
        - The display is updated every 0.25 seconds if no new log entries are found.
        """
        # Open the log file in read mode
        with open("logs/project.log", "r") as file:
            file.seek(0, 2)  # Move to the end of the file

            # Max entries displayed on the screen
            NUM_ENTRIES = 3
            # Create deque to store the latest log entries
            latest_logs = deque(maxlen=NUM_ENTRIES)

            # Continuously read the log file and display the latest entries
            while not stop_event.is_set():

                line = file.readline()
                if not line:
                    time.sleep(0.25)  # Wait for new log lines
                    continue

                self.display.clear_screen()
                self.draw_screen()

                formatted_entry = parse_log_line(line)
                if formatted_entry:
                    latest_logs.append(formatted_entry)  # Add new log entry

                iterator = 0
                for log in latest_logs:
                    self.display.draw_text(
                        log,
                        x=5,
                        y=20 + iterator,
                        font_size=10,
                        font_file="assets/mono-light.ttf",
                    )
                    iterator += 15

                self.display.display_image()
