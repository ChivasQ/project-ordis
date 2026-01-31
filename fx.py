import soundfile as sf
import time
import winsound
import numpy as np
import librosa
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
    Delay,
    Phaser,
)
from pedalboard import (
    Pedalboard, Distortion, Bitcrush, HighpassFilter,
    Compressor, Delay, Reverb, Gain, PeakFilter, Chorus
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

        self.board_glitch = Pedalboard([
            PitchShift(semitones=-4),
            Distortion(drive_db=14.0),

            # Phaser(rate_hz=2.0, depth=0.5, centre_frequency_hz=1200, feedback=0.7),

            Bitcrush(bit_depth=8.5),

            Delay(delay_seconds=0.02, feedback=0.6, mix=0.5),

            PeakFilter(gain_db=10.0, cutoff_frequency_hz=4000, q=6.0),

            LowpassFilter(cutoff_frequency_hz=4000),

            Compressor(threshold_db=-15, ratio=10),

            Gain(gain_db=-2.0)
        ])

    def _apply_tail_repeat(self, audio, sr, repeat_ms=250, count=2):
        num_samples = int(sr * (repeat_ms / 1000))
        if len(audio) < num_samples:
            return audio

        tail = audio[-num_samples:]
        repeated_part = np.tile(tail, count)
        return np.concatenate([audio, repeated_part])

    def process(self, audio_data, mode="normal"):
        try:
            if audio_data.ndim == 1:
                audio_data = audio_data[np.newaxis, :]
            board = self.board_glitch if mode == "glitch" else self.board_clean
            processed = board(audio_data, 22050)
            return processed.flatten()

        except Exception as e:
            print(f"Error processing audio: {e}")

    def process_wav(self, input_path, output_path, mode="normal"):
        try:
            audio, sample_rate = sf.read(input_path)

            if len(audio.shape) > 1:
                audio = np.mean(audio, axis=1)

            effect_board = self.board_glitch if mode == "glitch" else self.board_clean
            processed_audio = effect_board(audio, sample_rate)

            if mode == "glitch":
                processed_audio = self._apply_tail_repeat(processed_audio, sample_rate, repeat_ms=500, count=3)

            sf.write(output_path, processed_audio, sample_rate)
            print(f"File saved: {output_path} [{mode}]")

        except Exception as e:
            print(f"Error processing audio: {e}")


# ofx = OrdisFX()
#
# start_time = time.time()
# ofx.process_wav("test.wav", "ordis_glitch.wav", mode="glitch")
# end_time = time.time()
# elapsed = end_time - start_time
# print(elapsed)
# winsound.PlaySound("ordis_glitch.wav", winsound.SND_FILENAME)
