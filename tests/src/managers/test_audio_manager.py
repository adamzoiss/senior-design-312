import pytest
from src.managers.thread_manager import ThreadManager
from src.managers.audio_manager import AudioManager


@pytest.fixture()
def thread_manager():
    return ThreadManager()


@pytest.fixture()
def audio_manager():
    return AudioManager(thread_manager)


def test_creation(audio_manager):
    assert audio_manager is not None
