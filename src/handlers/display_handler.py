"""
Senior Project : Hardware Encryption Device
Team 312
File : display_handler.py
Description: Handles interfacing with the display and navigation options.
"""

from src.handlers.display.screens import *
from src.managers.thread_manager import ThreadManager


class DisplayHandler(Menu, Mode):
    """
    A class to handle navigation between different screens.

    Attributes
    ----------
    display : SSD1306
        The display object to draw on.
    MENU : Menu
        The menu screen object.
    MODE : Mode
        The mode selection screen object.
    CURRENT_SCREEN : Screen
        The currently active screen.
    """

    def __init__(self, display: SSD1306):
        """
        Initializes the DisplayHandler with the specified display.

        Parameters
        ----------
        display : SSD1306
            The display object to draw on.
        """
        self.display = display
        self.MENU = Menu(self.display)
        self.MODE = Mode(self.display)
        self.DEBUG = Debug(self.display)

        self.CURRENT_SCREEN = self.MENU

    def __del__(self):
        del self.display

    def get_screen(self, screen: Screen):
        """
        Sets the current screen and draws its content.

        Parameters
        ----------
        screen : Screen
            The screen to set as the current screen.
        """
        if screen is Menu:
            # Draw menu screen
            self.CURRENT_SCREEN = self.MENU
            self.CURRENT_SCREEN.draw_screen()
        elif screen is Mode:
            # Draw mode screen
            self.CURRENT_SCREEN = self.MODE
            self.CURRENT_SCREEN.draw_screen()
        elif screen is Debug:
            # Draw debug screen
            self.CURRENT_SCREEN = self.DEBUG
            self.CURRENT_SCREEN.draw_screen()
        else:
            print("ERROR")

    def select(self, selection: str, x1=56, y1=20, x2=64, y2=60):
        """
        Selects an option on the current screen and clears the previous selection.

        Parameters
        ----------
        selection : str
            The option to select.
        x1 : int, optional
            The x-coordinate of the top-left corner of the clear rectangle. Defaults to 56.
        y1 : int, optional
            The y-coordinate of the top-left corner of the clear rectangle. Defaults to 20.
        x2 : int, optional
            The x-coordinate of the bottom-right corner of the clear rectangle. Defaults to 64.
        y2 : int, optional
            The y-coordinate of the bottom-right corner of the clear rectangle. Defaults to 60.
        """
        self.display.clear_rectangle(x1, y1, x2, y2)
        self.CURRENT_SCREEN.select(selection)

    def update_menu_selection(self, position):
        """
        Update the menu selection based on the given position.
        Args:
            position (int): The position of the encoder to determine the menu selection.
        Returns:
            None
        """
        # Get the key for the menu selections based on an integer position
        selections = self.CURRENT_SCREEN.SELECTIONS.items()
        # Get the key for the menu selections based on encoder positon
        key = next(
            (k for k, v in selections if v == position),
            None,
        )
        # Update the display based on the encoder movements
        self.select(key)


if __name__ == "__main__":
    # Example Usage
    tm = ThreadManager()
    display = SSD1306(tm)
    navigation = DisplayHandler(display)
    navigation.display.clear_screen()
    #####################################
    navigation.get_screen(Menu)
    navigation.select("SETTINGS")
    navigation.select("MODE")

    # navigation.display.display_image()
    navigation.display.clear_screen()
    # #####################################
    navigation.get_screen(Mode)
    navigation.select("RADIO")
    navigation.select("LOCAL")
    navigation.select("DEBUG")

    navigation.display.display_image()
    # navigation.display.image.save("your_image.png")
    #####################################
    import time

    time.sleep(5)
    del navigation
