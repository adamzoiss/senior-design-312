from unittest.mock import MagicMock


class MockSpiDev:
    def __init__(self):
        self.max_speed_hz = 0
        self.mode = 0

    def open(self, *args, **kwargs):
        return

    def xfer2(self, data):
        # For reading operations, return the address byte plus a dummy byte
        if not (data[0] & 0x80):  # Check if MSB is 0 (read operation)
            return [data[0]] + [0x00] * (len(data) - 1)
        # For write operations, just return the data as is
        return data

    def close(self):
        return
