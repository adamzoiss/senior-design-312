import pyaudio

p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    print(
        f"{i}: {dev['name']} - {dev['maxInputChannels']} in / {dev['maxOutputChannels']} out"
    )
p.terminate()
