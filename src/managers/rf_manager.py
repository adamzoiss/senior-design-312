import queue
from math import ceil

from src.managers.thread_manager import *
from src.managers.base_audio_manager import *
from src.handlers.peripheral_drivers.rfm69 import *
from src.utils.constants import *
from src.utils.utils import sleep_microseconds
from src.logging import *


class RFManager:
    """
    Manages RF communication and audio streaming.

    Parameters
    ----------
    handle : int
        GPIO handle for the RF module.
    thread_manager : ThreadManager
        Instance of ThreadManager to manage threads.
    audio_manager : AudioManager
        Instance of AudioManager to manage audio streams.
    """

    def __init__(
        self,
        handle,
        thread_manager: ThreadManager,
        audio_manager: BaseAudioManager,
    ):
        # Set up logging
        self.logger: logging = Logger(
            "RFManager",
            console_level=logging.DEBUG,
            console_logging=EN_CONSOLE_LOGGING,
        )

        try:
            # Assign the managers within class scope
            self.thread_manager = thread_manager
            self.audio_manager = audio_manager

            # Create transceiver object
            self.rfm69 = RFM69(
                spi_bus=SPI_BUS,
                cs_pin=SPI_CS,
                reset_pin=RST,
                frequency=RADIO_FREQ_MHZ,
                handle=handle,
            )
            self.rfm69.encryption_key = ENCRYPTION_KEY

            self.handle = handle
            # Configure GPIO alerts and callbacks
            self._init_gpio_interrupts()

            # Queue to store received packets
            self.packet_queue = queue.Queue()
            # Buffer to store collected packet data before decoding
            self.pkt_buffer = b""
            self.frame_len = 0
            self.opus_buffer = b""

            self.rfm69.listen()

            # State that the manager initialized
            self.logger.info("RFManager initialized")

        except Exception as e:
            self.logger.critical(f"Error initializing RFManager: {e}")

    def _recv_pkt_callback(self, chip, gpio, level, timestamp):
        """
        Callback function for receiving packets.

        Parameters
        ----------
        chip : int
            GPIO chip number.
        gpio : int
            GPIO pin number.
        level : int
            GPIO pin level.
        timestamp : float
            Timestamp of the event.
        """
        # Make sure that if the transmit thread is running that the
        # receive thread is not
        if self.thread_manager.is_running(TRANSMIT_THREAD):
            if self.thread_manager.is_running(RECEIVE_THREAD):
                self.thread_manager.stop_thread(RECEIVE_THREAD)
            return
        # Check if there is an incoming packet and start the listening
        # thread if so.
        if self.rfm69.payload_ready:
            # Start the thread to handle playing packet data
            if not self.thread_manager.is_running(RECEIVE_THREAD):
                self.thread_manager.start_thread(
                    RECEIVE_THREAD, self.handle_packets
                )
            elif self.thread_manager.is_paused(RECEIVE_THREAD):
                self.thread_manager.resume_thread(RECEIVE_THREAD)
            # Receive the packet
            packet = self.rfm69.receive(timeout=None)
            # Ensure the packet has data
            if packet is not None:
                # # Check if encryption is enabled, if so decrypt the packet data
                # if self.audio_manager.crypto_manager.denc_en:
                #     packet = self.audio_manager.crypto_manager.decrypt(packet)
                # Place the packet in the queue
                self.packet_queue.put(packet)

    def _init_gpio_interrupts(self):
        """
        Initialize GPIO interrupts for packet reception.

        Parameters
        ----------
        handle : int
            GPIO handle for the RF module.
        """
        lgpio.gpio_claim_input(self.handle, G0)
        lgpio.gpio_claim_alert(self.handle, G0, lgpio.RISING_EDGE)
        recv_cb = lgpio.callback(
            self.handle, G0, lgpio.RISING_EDGE, self._recv_pkt_callback
        )

    def handle_packets(self, pause_event: threading.Event):
        """
        Handle incoming packets and decode them.

        Parameters
        ----------
        stop_event : threading.Event
            Event to signal stopping the packet handling.
        """
        # Check if event is set
        if pause_event.is_set():
            self.logger.info(f"{RECEIVE_THREAD} paused...")
            pause_event.wait()  # Block here until event is cleared
            self.logger.info(f"{RECEIVE_THREAD} Resumed.")

        if not self.audio_manager.output_stream:
            self.audio_manager.open_output_stream()

        while not pause_event.is_set():
            try:
                # Get next packet, wait up to BUFFER_TIMEOUT seconds
                packet = self.packet_queue.get(timeout=BUFFER_TIMEOUT)
                if packet[0:2] == START_SEQUENCE:
                    # Check if the packet is a start sequence, if so reset the buffer
                    # and set the frame length
                    self.pkt_buffer = b""
                    self.frame_len = int.from_bytes(packet[2:4], "big")

                    self.pkt_buffer = packet[4:]
                    opus_frame = None
                else:
                    self.pkt_buffer = self.pkt_buffer + packet
                    if len(self.pkt_buffer) > self.frame_len:
                        self.pkt_buffer = self.pkt_buffer[: self.frame_len]
                        opus_frame = self.pkt_buffer

                if opus_frame:
                    # Decode and play audio
                    try:
                        # Check to see if data encryption is enabled.
                        if self.audio_manager.crypto_manager.denc_en:
                            # Check if AES is enabled.
                            if self.audio_manager.crypto_manager.mode_aes:
                                opus_frame = (
                                    self.audio_manager.crypto_manager.decrypt(
                                        opus_frame
                                    )
                                )
                            # Check if RSA is enabled.
                            elif self.audio_manager.crypto_manager.mode_rsa:
                                # TODO: Implement RSA decryption
                                pass
                            # Check if Hybrid AES is enabled.
                            elif self.audio_manager.crypto_manager.mode_hybrid:
                                opus_frame = self.audio_manager.crypto_manager.hybrid_decrypt(
                                    opus_frame
                                )

                        decoded_audio = self.audio_manager.decoder.decode(
                            bytes(opus_frame), FRAME_SIZE
                        )
                        self.audio_manager.write_output(decoded_audio)
                    except opuslib.exceptions.OpusError as e:
                        self.logger.error(
                            f"Opus decoding error: {e} | len: {len(opus_frame)}"
                        )
            except queue.Empty:
                self.audio_manager.close_output_stream()
                self.thread_manager.pause_thread(RECEIVE_THREAD)

    def handle_input_stream(self, stop_event: threading.Event):
        """
        Handle input audio stream, encode and send packets.

        Parameters
        ----------
        stop_event : threading.Event
            Event to signal stopping the input stream handling.
        """
        if not self.audio_manager.input_stream:
            self.audio_manager.open_input_stream()

        while not stop_event.is_set():
            try:
                # Read the data from the input stream
                data = self.audio_manager.input_stream.read(
                    FRAME_SIZE, exception_on_overflow=False
                )
                # Encode the data
                encoded = self.audio_manager.encoder.encode(data, FRAME_SIZE)
                # Add the length of the encoded frame, packs two bytes big
                # endian, unsigned short to the front of the encoded data.
                encoded_size = struct.pack(">H", len(encoded))

                if self.audio_manager.crypto_manager.denc_en:
                    # Check if in AES mode
                    if self.audio_manager.crypto_manager.mode_aes:
                        # Encrypt the encoded data if encryption is enabled
                        enc_encoded = (
                            self.audio_manager.crypto_manager.encrypt(encoded)
                        )
                    elif self.audio_manager.crypto_manager.mode_rsa:
                        # TODO: Implemenet RSA encryption
                        enc_encoded = encoded  #! Remove when implemented
                        pass
                    # Check if in hybrid mode
                    elif self.audio_manager.crypto_manager.mode_hybrid:
                        # Encrypt the encoded data if encryption is enabled
                        enc_encoded = (
                            self.audio_manager.crypto_manager.hybrid_encrypt(
                                encoded
                            )
                        )
                    # If encryption is enabled, use the encrypted data
                    pkt_data = enc_encoded
                else:
                    # If encryption is not enabled, use the original encoded data
                    pkt_data = encoded

                # Write the length of the encoded frame first (to aid decoding)
                pkt_buffer = START_SEQUENCE + encoded_size + pkt_data
                req_pkts = ceil(len(pkt_buffer) / 60)
                req_padding_len = (req_pkts * 60) - len(pkt_buffer)
                pkt_buffer = pkt_buffer + (b"\x00" * req_padding_len)

                for i in range(0, req_pkts):
                    # Get the packet data
                    pkt = pkt_buffer[i * PACKET_SIZE : (i + 1) * PACKET_SIZE]
                    # # Encrypt the packet if encryption is enabled
                    # if self.audio_manager.crypto_manager.denc_en:
                    #     pkt = self.audio_manager.crypto_manager.encrypt(pkt)
                    # Send the packet
                    self.rfm69.send(pkt)
                    # Delay to allow the transceiver to process the packet
                    sleep_microseconds(1400)
            except Exception as e:
                self.logger.error(f"Packet error: {e}")

        # Cleaning up the input stream.
        self.audio_manager.close_input_stream()


if __name__ == "__main__":
    import signal

    handle = lgpio.gpiochip_open(0)
    tm = ThreadManager()
    am = BaseAudioManager(tm)

    transceiver = RFManager(handle, tm, am)

    # signal.pause()
    while True:
        time.sleep(1)
        print(tm.list_threads())
