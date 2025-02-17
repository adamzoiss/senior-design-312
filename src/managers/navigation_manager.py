"""
Senior Project : Hardware Encryption Device
Team 312
File : navigation_manager.py
Description: Handles interfacing with the display and navigation options.
"""

from display_interface.screens import *


class NavigationManager(Menu, Mode):
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
        Initializes the NavigationManager with the specified display.

        Parameters
        ----------
        display : SSD1306
            The display object to draw on.
        """
        self.display = display
        self.MENU = Menu(display)
        self.MODE = Mode(display)

        self.CURRENT_SCREEN = self.MENU

    def get_screen(self, screen: Screen):
        """
        Sets the current screen and draws its content.

        Parameters
        ----------
        screen : Screen
            The screen to set as the current screen.
        """
        if screen is Menu:
            self.CURRENT_SCREEN = self.MENU
            # Draw text
            self.display.draw_text("MENU", x=5, y=2, font_size=12)
            self.display.draw_text("Settings", x=5, y=20, font_size=10)
            self.display.draw_text("Mode", x=5, y=35, font_size=10)
        elif screen is Mode:
            self.CURRENT_SCREEN = self.MODE
            # Draw text
            self.display.draw_text("Mode Select", x=5, y=2, font_size=12)
            self.display.draw_text("Radio", x=5, y=20, font_size=10)
            self.display.draw_text("Local", x=5, y=35, font_size=10)
            self.display.draw_text("Debug", x=5, y=50, font_size=10)
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


if __name__ == "__main__":
    # Example Usage
    display = SSD1306()
    navigation = NavigationManager(display)
    display.clear_screen()
    #####################################
    navigation.get_screen(Menu)
    navigation.select("SETTINGS")
    navigation.select("MODE")

    # display.display_image()
    # display.clear_screen()
    # #####################################
    # navigation.get_screen(Mode)
    # navigation.select("RADIO")
    # navigation.select("LOCAL")
    # navigation.select("DEBUG")

    # display.display_image()
    # display.clear_screen()
    #####################################
    # Draw horizontal lines
    display.draw_line(0, 15, 127, 15, fill=1)
    display.draw_line(0, 16, 127, 16, fill=1)
    display.display_image()
    # display.image.save("your_image.png")
    #####################################
