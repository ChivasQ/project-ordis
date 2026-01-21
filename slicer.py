import librosa
import soundfile
from slicer2 import Slicer

audio, sr = librosa.load('ordis_raw_01.wav', sr=None, mono=True)

slicer = Slicer(
    sr=sr,
    threshold=-40,      # Порог тишины в dB (для Ордиса может понадобиться подстройка)
    min_length=5000,    # Минимальная длина куска (5000 мс = 5 сек)
    min_interval=500,   # Минимальная длина тишины для разреза
    hop_size=10,
    max_sil_kept=500    # Сколько тишины оставить по краям (важно для Piper!)
)

chunks = slicer.slice(audio)
for i, chunk in enumerate(chunks):
    soundfile.write(f'dataset/ordis_{i:04d}.wav', chunk, sr)