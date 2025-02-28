"""
Senior Project : Hardware Encryption Device
Team 312
File : screens.py
Description: This file holds various "Screens" to be used on
             the display.
"""

from display_interface.base_screen import *


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
