import queue
from math import ceil

from src.managers.thread_manager import *
from src.managers.audio_manager import *
from src.handlers.peripheral_drivers.rfm69 import *
from src.utils.interface_constants import *


class RFManager:
    def __init__(
        self,
        handle,
        thread_manager: ThreadManager,
        audio_manager: AudioManager,
    ):

        # Assign the managers within class scope
        self.thread_manager = thread_manager
        self.rfm69 = RFM69(
            spi_bus=SPI_BUS,
            cs_pin=SPI_CS,
            reset_pin=RST,
            frequency=RADIO_FREQ_MHZ,
            handle=handle,
        )
        self.audio_manager = audio_manager

        # Configure GPIO alerts and callbacks
        self._init_gpio_interrupts(handle)
        # Queue to store received packets
        self.packet_queue = queue.Queue()

        # Buffer to store collected packet data before decoding
        self.opus_buffer = b""

    def _recv_pkt_callback(self, chip, gpio, level, timestamp):
        # Make sure that if the transmit thread is running that the
        # receive thread is not
        if self.thread_manager.is_running(TRANSMIT_THREAD):
            if self.thread_manager.is_running():
                self.thread_manager.stop_thread(RECEIVE_THREAD)
            return
        # Check if there is an incomming packet and start the listening
        # thread if so.
        if self.rfm69.payload_ready:
            # Start the thread to handle playing packet data
            if not self.thread_manager.is_running(RECEIVE_THREAD):
                self.thread_manager.start_thread(
                    RECEIVE_THREAD, self.handle_packets
                )
            # Receive the packet
            packet = self.rfm69.receive(timeout=None)
            # Ensure the packet has data
            if packet is not None:
                # Place the packet in the queue
                self.packet_queue.put(packet)

    def _init_gpio_interrupts(self, handle):
        lgpio.gpio_claim_alert(handle, G0, lgpio.RISING_EDGE)
        recv_cb = lgpio.callback(
            handle, G0, lgpio.RISING_EDGE, self._recv_pkt_callback
        )

    def handle_packets(self, stop_event: threading.Event):
        if not self.audio_manager.output_stream:
            self.audio_manager._open_output_stream()

        while not stop_event.is_set():
            try:
                # Get next packet, wait up to BUFFER_TIMEOUT seconds
                packet = self.packet_queue.get(timeout=BUFFER_TIMEOUT)
                if packet[0:2] == START_SEQUENCE:
                    pkt_buffer = b""
                    frame_len = int.from_bytes(packet[2:4], "big")
                    pkt_buffer = packet[4:]
                    opus_frame = None
                else:
                    pkt_buffer = pkt_buffer + packet
                    if len(pkt_buffer) > frame_len:
                        pkt_buffer = pkt_buffer[:frame_len]
                        opus_frame = pkt_buffer

                if opus_frame:
                    # Decode and play audio
                    try:
                        decoded_audio = self.audio_manager.decoder.decode(
                            opus_frame, FRAME_SIZE
                        )
                        self.audio_manager.write_output(decoded_audio)
                    except opuslib.exceptions.OpusError as e:
                        print(
                            f"Opus decoding error: {e} | len: {len(opus_frame)}"
                        )
            except queue.Empty:
                self.audio_manager._close_streams()
                self.thread_manager.stop_thread(RECEIVE_THREAD)

    def handle_input_stream(self, stop_event: threading.Event):
        if not self.audio_manager.input_stream:
            self.audio_manager._open_input_stream()

        while not stop_event.is_set():
            try:
                data = self.audio_manager.input_stream.read(
                    FRAME_SIZE, exception_on_overflow=False
                )
                encoded = self.audio_manager.encoder.encode(data, FRAME_SIZE)
                encoded_size = struct.pack(">H", len(encoded))

                # Write the length of the encoded frame first (to aid decoding)
                pkt_buffer = START_SEQUENCE + encoded_size + encoded
                req_pkts = ceil(len(pkt_buffer) / 60)
                req_padding_len = (req_pkts * 60) - len(pkt_buffer)
                pkt_buffer = pkt_buffer + (b"\x00" * req_padding_len)

                for i in range(0, req_pkts):
                    pkt = pkt_buffer[i * PACKET_SIZE : (i + 1) * PACKET_SIZE]
                    self.rfm69.send(pkt)

            except Exception as e:
                print(e)
