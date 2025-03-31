import pytest
import time
import sys
from src.managers.thread_manager import ThreadManager
from src.managers.base_audio_manager import *
from tests.mocks.mock_base_audio_manager import *
from src.utils.constants import *


@pytest.fixture()
def thread_manager():
    return ThreadManager()


@pytest.fixture()
def base_audio_manager():
    return MockBaseAudioManager(thread_manager)


def test_creation(base_audio_manager):
    assert base_audio_manager is not None


def test_stream(base_audio_manager):
    base_audio_manager.open_input_stream()

    # Read the entire mock audio file into memory
    FILE = "tests/src/audio/48k_960.wav"
    with wave.open(FILE, "rb") as wf:
        raw_file_data = wf.readframes(wf.getnframes())

    # Make sure the raw data is read in correctly
    chunk_size = FRAME_SIZE * 2
    while base_audio_manager.audio_data:
        # Reading the audio data from the mocked input stream
        data = base_audio_manager.input_stream.read(FRAME_SIZE)

        # Reading the data from the raw audio file
        raw_data = raw_file_data[:chunk_size]
        raw_file_data = raw_file_data[chunk_size:]

        # Asserting the raw and mock data are the same
        assert data == raw_data


def test_encryption(base_audio_manager):
    base_audio_manager.open_input_stream()

    # Read the entire mock audio file into memory
    FILE = "tests/src/audio/48k_960.wav"
    with wave.open(FILE, "rb") as wf:
        raw_file_data = wf.readframes(wf.getnframes())

    # Make sure the raw data is read in correctly
    chunk_size = FRAME_SIZE * 2
    while base_audio_manager.audio_data:
        # Reading the audio data from the mocked input stream
        data = base_audio_manager.input_stream.read(FRAME_SIZE)
        # Encrypting the data
        enc_data = base_audio_manager.crypto_manager.encrypt(data)

        # Reading the data from the raw audio file
        raw_data = raw_file_data[:chunk_size]
        raw_file_data = raw_file_data[chunk_size:]
        # Encrypting the raw data
        enc_raw_data = base_audio_manager.crypto_manager.encrypt(raw_data)

        # Asserting the raw and mock data are the same
        assert enc_data == enc_raw_data

        assert data == raw_data


def test_decryption(base_audio_manager):
    base_audio_manager.open_input_stream()

    # Read the entire mock audio file into memory
    FILE = "tests/src/audio/48k_960.wav"
    with wave.open(FILE, "rb") as wf:
        raw_file_data = wf.readframes(wf.getnframes())

    # Make sure the raw data is read in correctly
    chunk_size = FRAME_SIZE * 2
    while base_audio_manager.audio_data:
        # Reading the audio data from the mocked input stream
        data = base_audio_manager.input_stream.read(FRAME_SIZE)
        # Encrypting the data
        enc_data = base_audio_manager.crypto_manager.encrypt(data)
        # Decrypting the data
        dec_data = base_audio_manager.crypto_manager.decrypt(enc_data)

        # Reading the data from the raw audio file
        raw_data = raw_file_data[:chunk_size]
        raw_file_data = raw_file_data[chunk_size:]
        # Encrypting the raw data
        enc_raw_data = base_audio_manager.crypto_manager.encrypt(raw_data)
        # Decrypting the data
        dec_raw_data = base_audio_manager.crypto_manager.decrypt(enc_raw_data)

        # Asserting the raw and mock data are the same
        assert dec_data == dec_raw_data


def test_encryption_performance(base_audio_manager, capfd):
    # Explicitly disable output capture for printing results
    with capfd.disabled():
        print("\n--- Starting encryption performance test ---")

    base_audio_manager.open_input_stream()

    # Read the entire mock audio file into memory
    FILE = "tests/src/audio/48k_960.wav"
    with wave.open(FILE, "rb") as wf:
        raw_file_data = wf.readframes(wf.getnframes())

    # Prepare a list of chunks for timing
    chunks = []
    chunk_size = FRAME_SIZE * 2
    temp_data = bytes(
        raw_file_data
    )  # Create a new bytes object instead of using copy()

    while len(temp_data) >= chunk_size:
        chunk = temp_data[:chunk_size]
        chunks.append(chunk)
        temp_data = temp_data[chunk_size:]

    # Time the encryption of all chunks
    total_bytes = 0
    start_time = time.time()

    for chunk in chunks:
        base_audio_manager.crypto_manager.encrypt(chunk)
        total_bytes += len(chunk)

    end_time = time.time()
    duration = end_time - start_time

    # Calculate metrics
    total_mb = total_bytes / (1024 * 1024)  # Convert to MB
    throughput_mbps = total_mb / duration if duration > 0 else 0
    # Convert to microseconds (1 second = 1,000,000 microseconds)
    avg_time_per_chunk_us = (
        (duration * 1000000) / len(chunks) if len(chunks) > 0 else 0
    )

    # Explicitly disable output capture for printing results
    with capfd.disabled():
        print(f"\nEncryption Performance Metrics:")
        print(f"Total data processed: {total_mb:.2f} MB")
        print(f"Total time: {duration:.4f} seconds")
        print(f"Throughput: {throughput_mbps:.2f} MB/s")
        print(
            f"Average time per chunk ({chunk_size} bytes): {avg_time_per_chunk_us:.2f} µs"
        )
        print("\n---  Ending encryption performance test  ---")

    # Simple assertion to make the test pass - you may want to establish
    # minimum performance requirements for your system
    assert duration > 0, "Encryption timing should be measurable"


def test_decryption_performance(base_audio_manager, capfd):
    # Explicitly disable output capture for printing results
    with capfd.disabled():
        print("\n--- Starting decryption performance test ---")

    base_audio_manager.open_input_stream()

    # Read the entire mock audio file into memory
    FILE = "tests/src/audio/48k_960.wav"
    with wave.open(FILE, "rb") as wf:
        raw_file_data = wf.readframes(wf.getnframes())

    # Prepare a list of chunks for timing
    chunks = []
    encrypted_chunks = []
    chunk_size = FRAME_SIZE * 2
    temp_data = bytes(raw_file_data)

    while len(temp_data) >= chunk_size:
        chunk = temp_data[:chunk_size]
        # Pre-encrypt all chunks for decryption testing
        encrypted_chunk = base_audio_manager.crypto_manager.encrypt(chunk)

        chunks.append(chunk)  # Original chunks for verification
        encrypted_chunks.append(
            encrypted_chunk
        )  # Encrypted chunks for decryption testing

        temp_data = temp_data[chunk_size:]

    # Time the decryption of all chunks
    total_bytes = 0
    start_time = time.time()

    decrypted_chunks = []
    for encrypted_chunk in encrypted_chunks:
        decrypted_chunk = base_audio_manager.crypto_manager.decrypt(
            encrypted_chunk
        )
        decrypted_chunks.append(decrypted_chunk)
        total_bytes += len(encrypted_chunk)

    end_time = time.time()
    duration = end_time - start_time

    # Calculate metrics
    total_mb = total_bytes / (1024 * 1024)  # Convert to MB
    throughput_mbps = total_mb / duration if duration > 0 else 0
    # Convert to microseconds (1 second = 1,000,000 microseconds)
    avg_time_per_chunk_us = (
        (duration * 1000000) / len(encrypted_chunks)
        if len(encrypted_chunks) > 0
        else 0
    )

    # Verify decryption worked correctly
    for i, (original, decrypted) in enumerate(zip(chunks, decrypted_chunks)):
        assert original == decrypted, f"Decryption failed for chunk {i}"

    # Explicitly disable output capture for printing results
    with capfd.disabled():
        print(f"\nDecryption Performance Metrics:")
        print(f"Total data processed: {total_mb:.2f} MB")
        print(f"Total time: {duration:.4f} seconds")
        print(f"Throughput: {throughput_mbps:.2f} MB/s")
        print(
            f"Average time per chunk ({chunk_size} bytes): {avg_time_per_chunk_us:.2f} µs"
        )
        print("\n---  Ending decryption performance test  ---")

    # Simple assertion to make the test pass
    assert duration > 0, "Decryption timing should be measurable"
