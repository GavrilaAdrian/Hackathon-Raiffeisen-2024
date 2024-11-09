import pyaudio
import wave
import numpy as np
import time

# Parameters
FORMAT = pyaudio.paInt16 # Audio format (bytes per sample)
CHANNELS = 1 # Mono audio
RATE = 44100 # Sample rate (samples/second)
CHUNK = 1024 # Chunk size (samples)

THRESHOLD = 4500  # Adjust this threshold based on your environment (noise background, microphone quality, etc.) recommended value: 1500-3000
SILENCE_DURATION = 2  # Duration of silence to stop recording (in seconds)
MAX_RECORDING_DURATION = 20  # Maximum recording duration (in seconds)
MIN_RECORDING_DURATION = 2  # Minimum recording duration required (in seconds)

def is_silent(data):
    return np.abs(np.frombuffer(data, dtype=np.int16)).mean() < THRESHOLD

def record_audio(filename):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    
    print("Recording...")
    frames = []
    silent_chunks = 0
    start_time = time.time()
    
    while True:
        if time.time() - start_time > MAX_RECORDING_DURATION:
            print("Maximum recording duration reached")
            break

        data = stream.read(CHUNK)
        frames.append(data)

        if time.time() - start_time > MIN_RECORDING_DURATION:
            if is_silent(data):
                silent_chunks += 1
            else:
                silent_chunks = 0
            
            if silent_chunks > (SILENCE_DURATION * RATE / CHUNK):
                print("Silence detected for {} seconds. Stopping recording...".format(SILENCE_DURATION))
                break

    print("Recording stopped")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

if __name__ == "__main__":
    record_audio("output.wav")
    print("Audio saved as output.wav")