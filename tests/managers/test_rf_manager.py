import pytest
import lgpio
from src.managers.rf_manager import *
from src.utils.rf_constants import *

@pytest.fixture
def tst_rf_manager():
    return NRF24l01()


def test_rf_manager_init(tst_rf_manager):
    """Test if the NRF24l01 object initializes correctly."""
    assert tst_rf_manager.spi is not None, "SPI should be initialized"
    assert tst_rf_manager.h is not None, "GPIO should be initialized"

def test_rf_manager_ce_high(tst_rf_manager):
    """Test setting CE pin high."""
    tst_rf_manager.set_ce_high()
    # Verify the pin state (this might need a mock or specific library support)
    assert lgpio.gpio_read(tst_rf_manager.h, CE_PIN) == 1, "CE pin should be high"

def test_rf_manager_ce_low(tst_rf_manager):
    """Test setting CE pin low."""
    tst_rf_manager.set_ce_low()
    # Verify the pin state (this might need a mock or specific library support)
    # assert lgpio.gpio_read(tst_rf_manager.h, CE_PIN) == 0, "CE pin should be low"

def test_tx_buffer(tst_rf_manager):
    """Test writing to the TX buffer."""
    test_data = [0x01, 0x02, 0x03, 0x04, 0x05]
    tst_rf_manager.write_tx_buffer(test_data)
    # Verify the buffer content (this might need a mock or specific library support)
    # assert tst_rf_manager.read_tx_buffer() == test_data, "TX buffer should match written data"


@pytest.mark.parametrize("address, value", [
    (Register.CONFIG, 0x7F),  # Test with max byte value
    (Register.CONFIG, 0x00),  # Test with zero
    (Register.CONFIG, 0x01),  # Test with arbitrary value
])
def test_register_write_read(tst_rf_manager, address, value):
    """Test writing and reading a register."""
    tst_rf_manager.write_register(address, value)
    read_value = tst_rf_manager.read_register(address)
    assert read_value & value == value, f"Expected {value:#X}, but got {read_value:#X}"
