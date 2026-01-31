import sounddevice as sd
import numpy as np
import queue
import threading
from faster_whisper import WhisperModel

# Для CPU на Windows/Linux лучше всего int8
whisper = WhisperModel("tiny", device="cpu", compute_type="int8", cpu_threads=8)

audio_queue = queue.Queue()


def audio_callback(indata, frames, time, status):
    audio_queue.put(indata.copy())


def transcriber():
    print("Ordis is listening")
    buffer = []
    while True:
        chunk = audio_queue.get()
        buffer.append(chunk)

        # Накопим хотя бы 2-3 секунды
        if len(buffer) > 10:  # Зависит от blocksize
            audio_data = np.concatenate(buffer).flatten().astype(np.float32)

            # Простейший порог громкости (чтобы не транскрибировать тишину)
            if np.max(np.abs(audio_data)) < 0.01:
                buffer = []
                continue

            segments, _ = whisper.transcribe(audio_data,
                                             beam_size=5,
                                             initial_prompt="Ordis, Tenno, Warframe, Grineer, Corpus, Void, Lotus.",)
            for segment in segments:
                if segment.text.strip():
                    print(f"Operator: {segment.text}")
                    # Здесь должен быть вызов твоего LLM цикла

            buffer = []


# Запуск
threading.Thread(target=transcriber, daemon=True).start()

with sd.InputStream(samplerate=16000, channels=1, callback=audio_callback, blocksize=4000):
    while True:
        sd.sleep(100)