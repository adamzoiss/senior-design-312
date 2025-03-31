import time
import random
import queue
from unittest.mock import MagicMock


class MockRFM69:
    """
    Mock implementation of the RFM69 radio module for testing.
    Simulates the behavior of the real RFM69 module without requiring hardware.
    """

    def __init__(
        self, spi_bus, cs_pin, reset_pin, frequency, handle, **kwargs
    ):
        """
        Initialize the mock RFM69 with the same parameters as the real one.
        """
        self.spi_bus = spi_bus
        self.cs_pin = cs_pin
        self.reset_pin = reset_pin
        self.frequency = frequency
        self.handle = handle
        self.encryption_key = kwargs.get("encryption_key", None)
        self.high_power = kwargs.get("high_power", True)

        # Operation state tracking
        self._mode = "idle"  # Can be 'idle', 'tx', 'rx', 'sleep'
        self._last_packet = None

        # Use queues instead of lists for better thread safety
        self._send_queue = queue.Queue()
        self._receive_queue = queue.Queue()

        # Performance simulation parameters
        self.tx_delay_per_byte = (
            0.00006  # 100 microseconds per byte for transmission
        )
        self.rx_delay_per_byte = (
            0.00006  # 100 microseconds per byte for reception
        )
        self.processing_delay = 0.0  # 0ms for packet processing

        # Stats for performance testing
        self.packets_sent = 0
        self.packets_received = 0
        self.bytes_sent = 0
        self.bytes_received = 0

        # Simulate payload_ready flag
        self.payload_ready = False

    def reset(self):
        """Mock reset functionality."""
        self._mode = "idle"
        time.sleep(0.01)  # Simulate reset time

    def idle(self):
        """Enter idle mode."""
        self._mode = "idle"

    def sleep(self):
        """Enter sleep mode."""
        self._mode = "sleep"

    def listen(self):
        """Enter receive mode."""
        self._mode = "rx"
        # Whenever there are packets in the receive queue, set payload_ready
        self.payload_ready = not self._receive_queue.empty()

    def transmit(self):
        """Enter transmit mode."""
        self._mode = "tx"
        # Process the send queue
        if not self._send_queue.empty():
            try:
                packet = self._send_queue.get_nowait()
                self._last_packet = packet
                self.packets_sent += 1
                self.bytes_sent += len(packet)
                # Simulate transmission time
                time.sleep(len(packet) * self.tx_delay_per_byte)
                self._send_queue.task_done()
            except queue.Empty:
                pass

    def send(self, data, **kwargs):
        """
        Send a packet of data.

        Args:
            data: The data to send
            **kwargs: Additional parameters (keep_listening, etc.)

        Returns:
            bool: True if the packet was sent successfully
        """
        if not isinstance(data, (bytes, bytearray)):
            data = bytes(data)

        # Queue the packet for sending
        self._send_queue.put(data)

        # Simulate transmission delay
        send_delay = len(data) * self.tx_delay_per_byte + self.processing_delay
        time.sleep(send_delay)

        # Update stats
        self.packets_sent += 1
        self.bytes_sent += len(data)

        # Automatically add this packet to the receive queue to simulate reception
        # (only in test mode to simulate a loopback)
        self._receive_queue.put(data)
        self.payload_ready = True

        # Handle keep_listening parameter
        if kwargs.get("keep_listening", False):
            self.listen()
        else:
            self.idle()

        return True  # Assume success in the mock

    def receive(self, **kwargs):
        """
        Receive a packet of data.

        Args:
            **kwargs: Additional parameters (timeout, etc.)

        Returns:
            bytes: The received packet data or None if no packet
        """
        timeout = kwargs.get("timeout", 0.5)

        # If no packets in queue, either wait for timeout or return None
        if self._receive_queue.empty():
            if timeout:
                # Wait a bit to see if a packet arrives
                time.sleep(min(timeout, 0.01))
                if self._receive_queue.empty():
                    return None
            else:
                return None

        try:
            # Get the next packet from the queue
            packet = self._receive_queue.get(block=False)

            # Update the payload_ready flag
            self.payload_ready = not self._receive_queue.empty()

            # Simulate processing delay
            receive_delay = (
                len(packet) * self.rx_delay_per_byte + self.processing_delay
            )
            time.sleep(receive_delay)

            # Update stats
            self.packets_received += 1
            self.bytes_received += len(packet)

            # Mark task as done
            self._receive_queue.task_done()

            # Handle keep_listening parameter
            if kwargs.get("keep_listening", True):
                self.listen()
            else:
                self.idle()

            return packet
        except queue.Empty:
            return None

    @property
    def rssi(self):
        """Get the mock RSSI (signal strength)."""
        return -random.randint(30, 90)  # Return a realistic RSSI value

    def add_test_packet_to_receive_queue(self, data):
        """
        Add a packet to the receive queue for testing.
        This is a testing-specific method not in the real RFM69.
        """
        if not isinstance(data, (bytes, bytearray)):
            data = bytes(data)
        self._receive_queue.put(data)
        self.payload_ready = True

    def clear_queues(self):
        """Clear all packet queues for testing."""
        # Create new queues instead of trying to clear existing ones
        self._send_queue = queue.Queue()
        self._receive_queue = queue.Queue()
        self.payload_ready = False

    def get_stats(self):
        """Return performance statistics."""
        return {
            "packets_sent": self.packets_sent,
            "packets_received": self.packets_received,
            "bytes_sent": self.bytes_sent,
            "bytes_received": self.bytes_received,
            "send_queue_size": self._send_queue.qsize(),
            "receive_queue_size": self._receive_queue.qsize(),
        }
