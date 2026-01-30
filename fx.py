import numpy as np
from pedalboard import (
    Pedalboard,
    Distortion,
    Bitcrush,
    HighpassFilter,
    LowpassFilter,
    Compressor,
    PitchShift,
    Gain,
    Reverb,
    Delay
)
from pedalboard import (
    Pedalboard, Distortion, Bitcrush, HighpassFilter,
    Compressor, Delay, Reverb, Gain, PeakFilter
)

class OrdisFX:
    def __init__(self):
        self.board_clean = Pedalboard([
            HighpassFilter(cutoff_frequency_hz=500),

            PeakFilter(gain_db=10.0, cutoff_frequency_hz=2500, q=5.0),

            Compressor(threshold_db=-20, ratio=4),

            Distortion(drive_db=5.0),

            Bitcrush(bit_depth=10),

            Delay(delay_seconds=0.015, feedback=0.6, mix=0.3),

            Reverb(room_size=0.15, damping=0.1, wet_level=0.2, dry_level=0.8),

            Gain(gain_db=3.0)
        ])

        # --- GLITCH (Bad) ---
        self.board_glitch = Pedalboard([
            PitchShift(semitones=-6),

            Distortion(drive_db=25.0),


            Bitcrush(bit_depth=8),

            Delay(delay_seconds=0.04, feedback=0.4, mix=0.4),

            Reverb(room_size=0.6, wet_level=0.5),

            LowpassFilter(cutoff_frequency_hz=7000),

            Gain(gain_db=-4.0)
        ])

    def process(self, audio_data, mode="normal"):
        try:
            if audio_data.ndim == 1:
                audio_data = audio_data[np.newaxis, :]
            board = self.board_glitch if mode == "glitch" else self.board_clean
            processed = board(audio_data, 22050)
            return processed.flatten()

        except Exception as e:
            print(f"Error processing audio: {e}")

