import pytest
from src.managers.crypto_manager import CryptoManager


@pytest.fixture()
def crypto_manager():
    return CryptoManager()


def test_creation(crypto_manager):
    assert crypto_manager is not None
