"""
Senior Project : Hardware Encryption Device
Team 312
File : base_screen.py
Description: This is the base class that will be inherited by
             different "Screen" classes.  
"""

from typing import int, str
from display_interface.SSD1306_display import *


class Screen:
    """
    A class to represent a screen with selectable options.

    Attributes
    ----------
    display : SSD1306
        The display object to draw on.
    SELECTIONS : dict
        A dictionary of selectable options.
    CURRENT_SELECTION : int
        The currently selected option.
    """

    def __init__(self: int, display: SSD1306) -> list:
        """
        Initializes the Screen with the specified display.

        Parameters
        ----------
        display : SSD1306
            The display object to draw on.
        """
        self.display = display

        self.SELECTIONS = {"NO_SELECTION": None}

        self.CURRENT_SELECTION: int = self.SELECTIONS["NO_SELECTION"]

    def select(self: int, selection: str) -> list:
        """
        Selects an option and draws an arrow next to it.

        Parameters
        ----------
        selection : str
            The option to select.
        """
        ARROW_ROW_1_X = 56
        ARROW_ROW_2_X = 112
        ARROW_WIDTH = 8

        Y_START = 25
        Y_H_OFFSET = 3
        if selection is None:
            selection = "NO_SELECTION"

        if selection in self.SELECTIONS:
            self.CURRENT_SELECTION = self.SELECTIONS[selection]
            if self.CURRENT_SELECTION is None:
                # No arrow should print
                pass
            elif self.CURRENT_SELECTION < 0:
                # Do nothing
                pass
            else:
                y_offset = self.SELECTIONS[selection]
                # Bototm half of '<'
                self.display.draw_line(
                    ARROW_ROW_1_X,
                    Y_START + (15 * y_offset),
                    ARROW_ROW_1_X + ARROW_WIDTH,
                    Y_START + (15 * y_offset) - Y_H_OFFSET,
                    fill=1,
                )
                # Top half of '<'
                self.display.draw_line(
                    ARROW_ROW_1_X,
                    Y_START + (15 * y_offset),
                    ARROW_ROW_1_X + ARROW_WIDTH,
                    Y_START + (15 * y_offset) + Y_H_OFFSET,
                    fill=1,
                )
