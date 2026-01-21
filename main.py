import wave
from piper import PiperVoice, SynthesisConfig

voice = PiperVoice.load("onnx-voices/en_US-glados-high.onnx")

syn_config = SynthesisConfig(
    volume=0.5,  # half as loud
    length_scale=1.25,  # twice as slow
    noise_scale=0.0,  # more audio variation
    noise_w_scale=.5,  # more speaking variation
    normalize_audio=False, # use raw audio from voice
)

with wave.open("test.wav", "wb") as wav_file:
    voice.synthesize_wav("Hello, my name is Glados. How can i help you?", wav_file, syn_config = syn_config)

