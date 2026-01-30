import os
import json
from pydub import AudioSegment
from tqdm import tqdm

INPUT_DIR = "dataset_ordis_wiki/audio"
OUTPUT_DIR = "ordis_cleared_chunks"
UNPACK_DIR = "ordis_restored"

MAP_FILE = "audio_mapping.json"
MAX_DURATION_MS = (30 * 60 * 1000) - 1
SILENCE_GAP = 500
TARGET_SAMPLE_RATE = 22050
TARGET_CHANNELS = 1

def unpack_audio():
    map_path = os.path.join(OUTPUT_DIR, MAP_FILE)
    if not os.path.exists(map_path):
        print(f"err {map_path}")
        return

    if not os.path.exists(UNPACK_DIR):
        os.makedirs(UNPACK_DIR)

    with open(map_path, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    for chunk_name, file_entries in mapping.items():
        chunk_path = os.path.join(OUTPUT_DIR, chunk_name)

        if not os.path.exists(chunk_path):
            print(f" [!] not found {chunk_name}")
            continue

        print(f"Processing {chunk_name}...")
        big_audio = AudioSegment.from_wav(chunk_path)

        for entry in tqdm(file_entries, leave=False):
            original_name = entry["original_name"]
            start = entry["start"]
            end = start + entry["duration"]

            slice_audio = big_audio[start:end]

            slice_audio = slice_audio.set_frame_rate(TARGET_SAMPLE_RATE).set_channels(TARGET_CHANNELS)

            new_name = original_name.replace(".ogg", ".wav")
            slice_audio.export(os.path.join(UNPACK_DIR, new_name), format="wav")

unpack_audio()