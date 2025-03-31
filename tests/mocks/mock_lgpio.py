from unittest.mock import MagicMock


class MockLgpio:
    # Constants
    LOW = 0
    HIGH = 1
    RISING_EDGE = 1
    FALLING_EDGE = 2
    BOTH_EDGES = 3
    SET_PULL_UP = 0

    # Mock GPIO pins
    ENC_A = 10
    ENC_B = 11
    SW_1 = 20
    SW_2 = 21
    SW_3 = 22
    SW_4 = 23
    SW_5 = 24

    def gpio_claim_output(self, *args, **kwargs):
        return 0

    def gpio_claim_input(self, *args, **kwargs):
        return 0

    def gpio_claim_alert(self, *args, **kwargs):
        return 0

    def gpio_write(self, *args, **kwargs):
        return 0

    def gpio_set_debounce_micros(self, *args, **kwargs):
        return 0

    def callback(self, *args, **kwargs):
        return MagicMock()

    def gpiochip_open(self, *args, **kwargs):
        return 1  # Mock handle

    def gpiochip_close(self, *args, **kwargs):
        return 0
