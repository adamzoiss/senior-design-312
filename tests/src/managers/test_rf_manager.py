import pytest
import time
import threading
import queue
import math
import sys
from unittest.mock import patch, MagicMock

# Import the mock classes directly
from tests.mocks.mock_lgpio import MockLgpio
from tests.mocks.mock_spidev import MockSpiDev

# Create a mock for spidev module before importing anything that uses it
sys.modules["spidev"] = MagicMock()
sys.modules["spidev"].SpiDev = MockSpiDev

from src.managers.thread_manager import ThreadManager
from src.managers.base_audio_manager import BaseAudioManager
from src.managers.rf_manager import RFManager
from tests.mocks.mock_rfm69 import MockRFM69
from tests.mocks.mock_base_audio_manager import MockBaseAudioManager
from src.utils.constants import *


# Create fixtures for testing
@pytest.fixture
def mock_lgpio(monkeypatch):
    """Mock lgpio module for testing"""
    mock_lgpio_instance = MockLgpio()
    monkeypatch.setattr("src.managers.rf_manager.lgpio", mock_lgpio_instance)
    monkeypatch.setattr(
        "src.handlers.peripheral_drivers.rfm69.lgpio", mock_lgpio_instance
    )
    return mock_lgpio_instance


@pytest.fixture
def thread_manager():
    """Create a thread manager instance for testing"""
    return ThreadManager()


@pytest.fixture
def audio_manager(thread_manager):
    """Create a mock audio manager for testing"""
    return MockBaseAudioManager(thread_manager)


@pytest.fixture
def mock_rfm69():
    """Create a mock RFM69 instance for testing"""
    return MockRFM69(
        spi_bus=SPI_BUS,
        cs_pin=SPI_CS,
        reset_pin=RST,
        frequency=RADIO_FREQ_MHZ,
        handle=1,
    )


@pytest.fixture
def rf_manager(thread_manager, audio_manager, mock_lgpio, monkeypatch):
    """Create an RF manager with mocked RFM69 for testing"""
    # Patch the RFM69 class to use our mock
    monkeypatch.setattr("src.managers.rf_manager.RFM69", MockRFM69)
    # Create RF Manager with a mock handle
    handle = 1
    return RFManager(handle, thread_manager, audio_manager)


# Tests
def test_rf_manager_initialization(rf_manager):
    """Test that the RF manager initializes properly"""
    assert rf_manager is not None
    assert rf_manager.rfm69 is not None
    assert rf_manager.thread_manager is not None
    assert rf_manager.audio_manager is not None
    assert rf_manager.packet_queue is not None


def test_packet_sending(rf_manager, capfd):
    """Test packet sending performance"""
    # Create test data
    test_data = bytes([i % 256 for i in range(60000)])  # 60KB of test data
    # Increased from 1KB to 60KB to generate 1000 packets of 60 bytes each

    with capfd.disabled():
        print("\n--- Starting RF packet sending performance test ---")

    # Create a queue for packets instead of a list
    packets_queue = queue.Queue()
    packet_size = PACKET_SIZE  # From constants

    # Split data into packets
    packet_count = 0
    for i in range(0, len(test_data), packet_size):
        packet = test_data[i : i + packet_size]
        packets_queue.put(packet)
        packet_count += 1
        # Limit to exactly 1000 packets for consistent comparison with receiving test
        if packet_count >= 1000:
            break

    # Measure time to send all packets
    start_time = time.time()

    total_bytes = 0
    packets_sent = 0

    # Process each packet from the queue
    while not packets_queue.empty():
        try:
            packet = packets_queue.get(block=False)
            # Simulate encryption if enabled
            if rf_manager.audio_manager.crypto_manager.denc_en:
                packet = rf_manager.audio_manager.crypto_manager.encrypt(
                    packet
                )
            rf_manager.rfm69.send(packet)
            total_bytes += len(packet)
            packets_sent += 1
            packets_queue.task_done()
        except queue.Empty:
            break

    end_time = time.time()
    duration = end_time - start_time

    # Calculate metrics
    total_kb = total_bytes / 1024
    throughput_kbps = (total_kb * 8) / duration if duration > 0 else 0
    avg_time_per_packet_ms = (
        (duration * 1000) / packets_sent if packets_sent > 0 else 0
    )
    packets_per_second = packets_sent / duration if duration > 0 else 0

    # Get stats from the mock radio
    stats = rf_manager.rfm69.get_stats()

    with capfd.disabled():
        print(f"\nRF Packet Sending Performance:")
        print(f"Total packets sent: {packets_sent}")
        print(f"Total data sent: {total_kb:.2f} KB")
        print(f"Total time: {duration:.4f} seconds")
        print(f"Throughput: {throughput_kbps:.2f} kbps")
        print(f"Average time per packet: {avg_time_per_packet_ms:.2f} ms")
        print(f"Packets per second: {packets_per_second:.2f}")
        print(f"Mock RFM69 stats: {stats}")
        print("\n--- Ending RF packet sending performance test ---")

    assert duration > 0, "Sending timing should be measurable"
    assert stats["packets_sent"] == packets_sent, "Not all packets were sent"
    assert (
        packets_sent == 1000
    ), f"Expected 1000 packets, but sent {packets_sent}"


def test_packet_receiving(rf_manager, capfd):
    """Test packet receiving performance"""
    # Number of test packets to generate
    num_packets = (
        1000  # Increased from 20 to 1000 for better performance measurement
    )

    with capfd.disabled():
        print("\n--- Starting RF packet receiving performance test ---")

    # Generate test packets with the START_SEQUENCE and size info
    for i in range(num_packets):
        # Create packet with header (similar to what handle_input_stream does)
        payload = bytes([i % 256 for i in range(56)])  # Some test data
        encoded_size = len(payload).to_bytes(2, byteorder="big")
        packet = START_SEQUENCE + encoded_size + payload
        rf_manager.rfm69.add_test_packet_to_receive_queue(packet)

    # Measure time to receive and process all packets
    start_time = time.time()

    # Simulate receiving packets - use a queue instead of a list
    received_packets_queue = queue.Queue()
    total_bytes = 0

    while rf_manager.rfm69.payload_ready:
        packet = rf_manager.rfm69.receive(timeout=0.1)
        if packet:
            received_packets_queue.put(packet)
            total_bytes += len(packet)

    end_time = time.time()
    duration = end_time - start_time

    # Calculate metrics
    total_packets = received_packets_queue.qsize()
    total_kb = total_bytes / 1024
    throughput_kbps = (total_kb * 8) / duration if duration > 0 else 0
    avg_time_per_packet_ms = (
        (duration * 1000) / total_packets if total_packets > 0 else 0
    )

    # Get stats from the mock radio
    stats = rf_manager.rfm69.get_stats()

    with capfd.disabled():
        print(f"\nRF Packet Receiving Performance:")
        print(f"Total packets received: {total_packets}")
        print(f"Total data received: {total_kb:.2f} KB")
        print(f"Total time: {duration:.4f} seconds")
        print(f"Throughput: {throughput_kbps:.2f} kbps")
        print(f"Average time per packet: {avg_time_per_packet_ms:.2f} ms")
        print(f"Packets per second: {total_packets/duration:.2f}")
        print(f"Mock RFM69 stats: {stats}")
        print("\n--- Ending RF packet receiving performance test ---")

    assert duration > 0, "Receiving timing should be measurable"
    assert total_packets > 0, "No packets were received"
    assert (
        total_packets == num_packets
    ), f"Expected {num_packets} packets, but received {total_packets}"


def test_end_to_end_transmission(
    rf_manager, audio_manager, thread_manager, capfd
):
    """Test end-to-end audio transmission through the RF manager simulating a complete audio file"""
    with capfd.disabled():
        print("\n--- Starting end-to-end RF transmission test ---")

    # Setup input stream for the audio manager
    audio_manager.open_input_stream()

    # Patch the thread start to avoid actually starting threads
    original_start_thread = thread_manager.start_thread
    thread_manager.start_thread = MagicMock()

    # Define test parameters
    audio_frames = (
        100  # Simulate 100 frames (~2 seconds of audio at 20ms frames)
    )
    total_audio_size = 0
    total_encoded_size = 0
    total_packets = 0
    total_received_packets = 0
    total_decoded_size = 0

    # Measure time to process and send all audio frames
    start_time = time.time()

    # Process each simulated audio frame
    for frame_idx in range(audio_frames):
        # Get the next frame of audio data
        audio_data = audio_manager.input_stream.read(FRAME_SIZE)
        total_audio_size += len(audio_data)

        # Encode the audio data
        encoded = audio_manager.encoder.encode(audio_data, FRAME_SIZE)
        encoded_size = len(encoded).to_bytes(2, byteorder="big")
        total_encoded_size += len(encoded)

        # Form the packet with the required format
        pkt_buffer = START_SEQUENCE + encoded_size + encoded

        # Calculate required packets and padding
        req_pkts = math.ceil(len(pkt_buffer) / PACKET_SIZE)
        req_padding_len = (req_pkts * PACKET_SIZE) - len(pkt_buffer)
        pkt_buffer = pkt_buffer + (b"\x00" * req_padding_len)

        # Split into packets and send
        for i in range(req_pkts):
            pkt = pkt_buffer[i * PACKET_SIZE : (i + 1) * PACKET_SIZE]
            # Encrypt if needed
            if audio_manager.crypto_manager.denc_en:
                pkt = audio_manager.crypto_manager.encrypt(pkt)
            rf_manager.rfm69.send(pkt)
            total_packets += 1

    # Now simulate receiving these packets
    received_packets_queue = queue.Queue()
    while rf_manager.rfm69.payload_ready:
        packet = rf_manager.rfm69.receive(timeout=0.1)
        if packet:
            # Decrypt if needed
            if audio_manager.crypto_manager.denc_en:
                packet = audio_manager.crypto_manager.decrypt(packet)
            received_packets_queue.put(packet)
            rf_manager.packet_queue.put(packet)
            total_received_packets += 1

    # Process the packets in the queue (similar to handle_packets)
    pkt_buffer = b""
    frame_len = 0
    complete_frames = 0

    # Process all packets in the queue
    while not rf_manager.packet_queue.empty():
        packet = rf_manager.packet_queue.get(timeout=0.1)

        # Handle packet according to its structure
        if packet[0:2] == START_SEQUENCE:
            # Start a new frame if we encounter a start sequence
            # First, save any complete frame we might have
            if (
                "opus_frame" in locals()
                and opus_frame
                and len(opus_frame) == frame_len
            ):
                complete_frames += 1

            # Reset buffer for new frame
            pkt_buffer = b""
            frame_len = int.from_bytes(packet[2:4], "big")
            pkt_buffer = packet[4:]
            opus_frame = None
        else:
            pkt_buffer = pkt_buffer + packet
            if len(pkt_buffer) >= frame_len:
                pkt_buffer = pkt_buffer[:frame_len]
                opus_frame = pkt_buffer

        # If we have a complete opus frame, decode it
        if (
            "opus_frame" in locals()
            and opus_frame
            and len(opus_frame) == frame_len
        ):
            try:
                decoded_audio = audio_manager.decoder.decode(
                    bytes(opus_frame), FRAME_SIZE
                )
                total_decoded_size += len(decoded_audio)
                # In a real scenario, this would be sent to the output stream
                assert len(decoded_audio) > 0, "Decoded audio is empty"
            except Exception as e:
                print(f"Error decoding: {e}")

    end_time = time.time()
    duration = end_time - start_time

    # Restore the original thread start function
    thread_manager.start_thread = original_start_thread

    # Calculate metrics
    audio_kb = total_audio_size / 1024
    encoded_kb = total_encoded_size / 1024
    decoded_kb = total_decoded_size / 1024
    compression_ratio = (
        total_audio_size / total_encoded_size if total_encoded_size > 0 else 0
    )
    throughput_kbps = (encoded_kb * 8) / duration if duration > 0 else 0

    with capfd.disabled():
        print(f"\nEnd-to-End RF Transmission Performance:")
        print(f"Total audio frames: {audio_frames}")
        print(f"Complete frames decoded: {complete_frames}")
        print(f"Total packets sent: {total_packets}")
        print(f"Total packets received: {total_received_packets}")
        print(f"Raw audio size: {audio_kb:.2f} KB")
        print(
            f"Encoded size: {encoded_kb:.2f} KB (compression ratio: {compression_ratio:.2f}x)"
        )
        print(f"Decoded audio size: {decoded_kb:.2f} KB")
        print(f"Total time: {duration:.4f} seconds")
        print(f"Throughput: {throughput_kbps:.2f} kbps")
        print(f"Packets per second: {total_packets/duration:.2f}")
        print("\n--- Ending end-to-end RF transmission test ---")

    # Assertions to verify the test ran correctly
    assert duration > 0, "Transmission timing should be measurable"
    assert total_received_packets > 0, "No packets were received"
    assert complete_frames > 0, "No complete frames were decoded"
    # We may not get all frames due to packet loss simulation, but should get most
    assert (
        complete_frames >= audio_frames * 0.9
    ), f"Expected at least 90% of {audio_frames} frames, but got {complete_frames}"
    assert total_decoded_size > 0, "No audio was decoded"


if __name__ == "__main__":
    pytest.main(["-v", "test_rf_manager.py"])
