import os
import json
from pydub import AudioSegment
from tqdm import tqdm

INPUT_DIR = "dataset_ordis_wiki/audio"
OUTPUT_DIR = "ordis_processed_chunks"
UNPACK_DIR = "ordis_restored"

MAP_FILE = "audio_mapping.json"
MAX_DURATION_MS = (30 * 60 * 1000) - 1
SILENCE_GAP = 500


def pack_audio():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.ogg')]
    files.sort()

    current_chunk = AudioSegment.empty()
    chunk_index = 1
    mapping = {}

    silence = AudioSegment.silent(duration=SILENCE_GAP)

    print(f">>> Files found: {len(files)}")

    for filename in tqdm(files):
        file_path = os.path.join(INPUT_DIR, filename)

        try:
            audio = AudioSegment.from_file(file_path)

            if len(current_chunk) + len(audio) + len(silence) > MAX_DURATION_MS:
                chunk_name = f"ordis_chunk_{chunk_index:03d}.wav"
                export_path = os.path.join(OUTPUT_DIR, chunk_name)

                print(f"   [Save] {chunk_name} ({len(current_chunk) / 1000 / 60:.1f} min)...")
                current_chunk.export(export_path, format="wav")

                current_chunk = AudioSegment.empty()
                chunk_index += 1

            chunk_name = f"ordis_chunk_{chunk_index:03d}.wav"
            start_time = len(current_chunk)

            if chunk_name not in mapping:
                mapping[chunk_name] = []

            mapping[chunk_name].append({
                "original_name": filename,
                "start": start_time,
                "duration": len(audio)
            })

            current_chunk += audio + silence

        except Exception as e:
            print(f" [!] Err {filename}: {e}")

    if len(current_chunk) > 0:
        chunk_name = f"ordis_chunk_{chunk_index:03d}.wav"
        export_path = os.path.join(OUTPUT_DIR, chunk_name)
        print(f"   [Save] Save last {chunk_name}...")
        current_chunk.export(export_path, format="wav")

    map_path = os.path.join(OUTPUT_DIR, MAP_FILE)
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=4)

pack_audio()