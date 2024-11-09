import pyaudio
import wave

RECORDING_DURAION = 15

def record_audio(filename, duration, sample_rate=44100, channels=2, chunk_size=1024):
    audio = pyaudio.PyAudio()

    # Start Recording
    stream = audio.open(format=pyaudio.paInt16, channels=channels,
                        rate=sample_rate, input=True,
                        frames_per_buffer=chunk_size)
    print("Recording...")
    frames = []

    for _ in range(0, int(sample_rate / chunk_size * duration)):
        data = stream.read(chunk_size)
        frames.append(data)

    print("Finished recording.")

    # Stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recorded data as a WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))

if __name__ == "__main__":
    record_audio("output.wav", RECORDING_DURAION)
    print("Audio saved as output.wav")