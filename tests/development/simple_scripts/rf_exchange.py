from src.handlers.peripheral_drivers.rfm69 import *
from src.handlers.gpio_handler import *
import queue

packet_queue = queue.Queue()
gpio_handler = GPIOHandler()


def _recv_pkt_callback(chip, gpio, level, timestamp):
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
    # Check if there is an incoming packet and start the listening
    # thread if so.
    if rfm69.payload_ready:
        packet = rfm69.receive(timeout=None)
        # Ensure the packet has data
        if packet is not None:
            # Place the packet in the queue
            # self.logger.debug(f"PACKET [{packet.hex()}]")
            packet_queue.put(packet)

    packet = packet_queue.get()
    print("\n" + ("-" * 40))
    print(f"Received: {packet}")
    print("-" * 40)


def _init_gpio_interrupts():
    """
    Initialize GPIO interrupts for packet reception.

    Parameters
    ----------
    handle : int
        GPIO handle for the RF module.
    """
    lgpio.gpio_claim_input(gpio_handler.handle, G0)
    lgpio.gpio_claim_alert(gpio_handler.handle, G0, lgpio.RISING_EDGE)
    recv_cb = lgpio.callback(
        gpio_handler.handle, G0, lgpio.RISING_EDGE, _recv_pkt_callback
    )


if __name__ == "__main__":
    try:

        rfm69 = RFM69(
            spi_bus=SPI_BUS,
            cs_pin=SPI_CS,
            reset_pin=RST,
            frequency=RADIO_FREQ_MHZ,
            handle=gpio_handler.handle,
        )

        rfm69.encryption_key = ENCRYPTION_KEY

        _init_gpio_interrupts()

        rfm69.listen()

        while True:

            data = "Hello from transmitter!"
            # Comment the send line on the device that is acting as the receiver.
            rfm69.send(bytes(f"{data}\r\n", "utf-8"))
            time.sleep(1)

    except Exception as e:
        print(f"Exception: {e}")
