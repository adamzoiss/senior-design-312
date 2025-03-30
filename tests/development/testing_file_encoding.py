import pyaudio
import opuslib
import struct

# Audio settings
INPUT_INDEX = 4
OUTPUT_INDEX = 0
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
FRAMES_PER_BUFFER = 960  # 20ms frame at 48kHz
OUTPUT_FILE = "recorded_audio.opus"

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Open input stream
input_stream = audio.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    input_device_index=INPUT_INDEX,
    frames_per_buffer=FRAMES_PER_BUFFER,
)

# Create Opus encoder
encoder = opuslib.Encoder(
    RATE, CHANNELS, application=opuslib.APPLICATION_AUDIO
)

# Open file to write encoded audio
with open(OUTPUT_FILE, "wb") as file:
    print("Recording... Press Ctrl+C to stop.")
    try:
        while True:
            data = input_stream.read(
                FRAMES_PER_BUFFER, exception_on_overflow=False
            )
            encoded = encoder.encode(data, FRAMES_PER_BUFFER)

            # Write the length of the encoded frame first (to aid decoding)
            file.write(
                struct.pack("H", len(encoded))
            )  # Store frame size (2 bytes)
            file.write(encoded)  # Store actual Opus frame data
    except KeyboardInterrupt:
        print("\nRecording stopped.")

# Close input stream
input_stream.stop_stream()
input_stream.close()

# Open file to read encoded audio
with open(OUTPUT_FILE, "rb") as file:
    encoded_data = file.read()

# Decode Opus audio
decoder = opuslib.Decoder(RATE, CHANNELS)
decoded_frames = []
offset = 0

while offset < len(encoded_data):
    try:
        # Read stored frame size first
        frame_size = struct.unpack_from("H", encoded_data, offset)[0]
        offset += 2  # Move past the frame size bytes

        # Extract frame data
        chunk = encoded_data[offset : offset + frame_size]
        offset += frame_size  # Move past the actual frame data

        # Decode the frame
        decoded = decoder.decode(chunk, FRAMES_PER_BUFFER)
        decoded_frames.append(decoded)
    except (opuslib.exceptions.OpusError, struct.error) as e:
        print(f"Opus decoding error: {e}")
        break

# Combine all decoded frames
decoded_audio = b"".join(decoded_frames)

# Open output stream
output_stream = audio.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    output=True,
    output_device_index=OUTPUT_INDEX,
    frames_per_buffer=FRAMES_PER_BUFFER,
)

# Play the decoded audio
print("Playing back...")
output_stream.write(decoded_audio)

# Close streams and terminate PyAudio
output_stream.stop_stream()
output_stream.close()
audio.terminate()

print("Playback finished.")
