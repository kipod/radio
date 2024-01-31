from flask import Flask, Response
import pyaudio

# import audio_processing as audioRec

app = Flask(__name__)


def genHeader(sampleRate, bitsPerSample, channels, samples):
    # Some veeery big number here instead of: #samples * channels * bitsPerSample // 8
    DATA_SIZE = 102400000
    o = bytes("RIFF", "ascii")  # (4byte) Marks file as RIFF
    o += (DATA_SIZE + 36).to_bytes(4, "little")  # (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE", "ascii")  # (4byte) File type
    o += bytes("fmt ", "ascii")  # (4byte) Format Chunk Marker
    o += (16).to_bytes(4, "little")  # (4byte) Length of above format data
    o += (1).to_bytes(2, "little")  # (2byte) Format type (1 - PCM)
    o += (channels).to_bytes(2, "little")  # (2byte)
    o += (sampleRate).to_bytes(4, "little")  # (4byte)
    o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4, "little")  # (4byte)
    o += (channels * bitsPerSample // 8).to_bytes(2, "little")  # (2byte)
    o += (bitsPerSample).to_bytes(2, "little")  # (2byte)
    o += bytes("data", "ascii")  # (4byte) Data Chunk Marker
    o += DATA_SIZE.to_bytes(4, "little")  # (4byte) Data size in bytes
    return o


FORMAT = pyaudio.paInt16
CHUNK = 8192
RATE = 44100
bitsPerSample = 16  # 16
CHANNELS = 1
wav_header = genHeader(RATE, bitsPerSample, CHANNELS, CHUNK)

audio = pyaudio.PyAudio()

# start Recording
stream = audio.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    input_device_index=3,
    frames_per_buffer=CHUNK,
)


@app.route("/")
def audio_stream():
    def sound():
        data = wav_header
        data += stream.read(CHUNK, exception_on_overflow=False)
        yield (data)
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            yield (data)

    return Response(sound(), mimetype="audio/wav")
