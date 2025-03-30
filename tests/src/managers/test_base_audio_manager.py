import pytest
from src.managers.thread_manager import ThreadManager
from src.managers.base_audio_manager import *
from tests.src.mocks.mock_base_audio_manager import *

# from src.utils.constants import *


@pytest.fixture()
def thread_manager():
    return ThreadManager()


@pytest.fixture()
def core_audio_manager():
    return MockBaseAudioManager(thread_manager)


def test_creation(core_audio_manager):
    assert core_audio_manager is not None


def test_stream(core_audio_manager):
    core_audio_manager.open_input_stream()

    # Read the entire mock audio file into memory
    FILE = "tests/src/audio/48k_960.wav"
    with wave.open(FILE, "rb") as wf:
        raw_file_data = wf.readframes(wf.getnframes())

    # Make sure the raw data is read in correctly
    chunk_size = 960 * 2
    while core_audio_manager.audio_data:
        data = core_audio_manager.input_stream.read(960)
        raw_data = raw_file_data[:chunk_size]
        raw_file_data = raw_file_data[chunk_size:]
        assert data == raw_data
