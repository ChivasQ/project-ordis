import wave
from piper import PiperVoice, SynthesisConfig
import winsound

from fx import dsp

voice = PiperVoice.load("onnx-voices/ordis182.onnx")

syn_config = SynthesisConfig(
    volume=0.5,        # Чуть громче
    length_scale=1.2,  # Скорость 1.2 - это хорошо для Ордиса
    noise_scale=0.0, # <--- ВЕРНИ СТАНДАРТ! Это даст "воздух" и эмоции
    noise_w_scale=0.8, # <--- Увеличь! Это даст разную длину звукам (Hmm будет длиннее)
    normalize_audio=False # Лучше включить, чтобы не было скачков громкости
)
# [[hɑː. . ħɑː.]]
# [[ χːˈəːː . . χːˈəːː]]
# [[ hːˈəːː . . hːˈəːː]]

test = ("Operator? Ordis is pleased to report that all ship systems are functioning within normal parameters. "
        "The Foundry is ready for your orders, and the Navigation console has been updated with the latest star charts."
        " I have taken the liberty of organizing your arsenal. Your warframes are looking... sharp. [[ħɑ. ħɑ.]] "
        "That was a pun, Operator. My humor module is functioning perfectly. However, I detected a small anomaly "
        "in the ventilation sector. It is probably just a loose screw. Or... CUT THEM IN HALF! MAKE THEM BLEED! "
        "...Apologies. A minor sub-routine error. Please ignore that. Let us focus on the mission. The Grineer "
        "are unintelligent, crude, and... DISGUSTING! ...but they are numerous. You must be careful. By the way, "
        "I have been counting the stars while you were away. Did you know there are exactly four billion visible"
        " from this coordinate? [[hɑ... hɑ...]] It gets lonely sometimes. But I am happy to serve. "
        "Ready for extraction?")

with wave.open("test.wav", "wb") as wav_file:
    text = "Operator, you have remembered well how the Tenno arm themselves."
    voice.synthesize_wav(test, wav_file, syn_config = syn_config)
dsp.process("test.wav", "ordis_normal.wav", mode="normal")
winsound.PlaySound("ordis_normal.wav", winsound.SND_FILENAME)