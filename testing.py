


import pyaudio

# Initialize PyAudio
audio = pyaudio.PyAudio()

for i in range(audio.get_device_count()):
    device_info = audio.get_device_info_by_index(i)
    print(f"Index {i}: {device_info['name']}")
