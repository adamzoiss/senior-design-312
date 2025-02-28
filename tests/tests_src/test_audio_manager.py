import pytest
from src.managers.audio_manager import AudioManager


@pytest.fixture()
def audio_manager():
    return AudioManager()


def test_creation(audio_manager):
    assert audio_manager is not None
