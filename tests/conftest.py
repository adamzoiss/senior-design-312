import sys
from unittest.mock import MagicMock

# Import the mock classes from the dedicated mock file
from tests.mocks.mock_lgpio import MockLgpio
from tests.mocks.mock_spidev import MockSpiDev


# Mock necessary modules for tests that might not be available
def pytest_configure(config):
    # Create mocks only if they're not already in sys.modules (to prevent conflicts)
    if "spidev" not in sys.modules:
        sys.modules["spidev"] = MagicMock()
        sys.modules["spidev"].SpiDev = MockSpiDev

    if "lgpio" not in sys.modules:
        sys.modules["lgpio"] = MockLgpio()
