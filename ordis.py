from openai import OpenAI
import threading
import queue
import re
import sounddevice as sd
import numpy as np
from piper import PiperVoice, SynthesisConfig
from memory import OrdisMemory
from fx import OrdisFX

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

voice = PiperVoice.load("onnx-voices/ordis182.onnx")
MODEL_NAME = 'google/gemma-3n-e4b'
audio_queue = queue.Queue()
memory = OrdisMemory()
fx = OrdisFX()

syn_config = SynthesisConfig(
    volume=0.7,
    length_scale=1.2,
    noise_scale=0.2,
    noise_w_scale=0.8)

with open("system-prompt.txt", 'r', encoding='utf-8') as f:
    base_system_prompt = f.read()

messages = [
    {'role': 'system', 'content': base_system_prompt}
]

def save_background(u_text, a_text):
    memory.save_interaction(u_text, a_text)


def synthesize_text(text):
    text = text.strip().replace("*", "")
    if not text: return None, 0

    try:
        parts = re.split(r'--', text)

        final_audio_chunks = []
        sample_rate = voice.config.sample_rate

        for i, part in enumerate(parts):
            part = part.strip()
            if not part: continue

            stream = voice.synthesize(part, syn_config=syn_config)
            audio_bytes = b"".join(chunk.audio_int16_bytes for chunk in stream)
            data_float = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

            mode = "glitch" if i == 1 else "normal"

            processed_chunk = fx.process(data_float, mode=mode)

            if processed_chunk is not None:
                final_audio_chunks.append(processed_chunk)

        if not final_audio_chunks:
            return None, 0

        # Склеиваем все части в один массив
        full_audio = np.concatenate(final_audio_chunks)
        return full_audio, sample_rate

    except Exception as e:
        print(f"TTS/FX Error: {e}")
        return None, 0

def audio_player_worker():
    while True:
        item = audio_queue.get()
        if item is None: break
        data, fs = item
        if data is not None:
            sd.play(data, fs)
            sd.wait()
        audio_queue.task_done()


player_thread = threading.Thread(target=audio_player_worker, daemon=True)
player_thread.start()

while True:
    try:
        user_input = input("\nOperator: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        found_memories = memory.get_relevant_context(user_input)

        if found_memories:
            current_system_content = f"""{base_system_prompt}
            IMPORTANT: RELEVANT MEMORIES FROM PAST CONVERSATIONS:
            {found_memories}
            Use these memories to answer if relevant.
            """
        else:
            current_system_content = base_system_prompt

        messages[0] = {'role': 'system', 'content': current_system_content}
        messages.append({'role': 'user', 'content': user_input})

        stream = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            stream=True,
        )

        print("Ordis: ", end='', flush=True)

        buffer = ""
        full_answer = ""

        sentence_end_pattern = re.compile(r'(?<=[.!?\n:;])\s+')

        for chunk in stream:
            delta = chunk.choices[0].delta
            if not delta.content: continue

            content = delta.content
            print(content, end='', flush=True)
            buffer += content
            full_answer += content

            parts = sentence_end_pattern.split(buffer)
            if len(parts) > 1:
                for sentence in parts[:-1]:
                    if sentence.strip() and len(sentence.strip()) > 2:
                        audio_data, sr = synthesize_text(sentence)
                        if audio_data is not None:
                            audio_queue.put((audio_data, sr))
                buffer = parts[-1]

        if buffer.strip():
            audio_data, sr = synthesize_text(buffer)
            if audio_data is not None:
                audio_queue.put((audio_data, sr))

        messages.append({'role': 'assistant', 'content': full_answer})

        save_thread = threading.Thread(
            target=save_background,
            args=(user_input, full_answer)
        )
        save_thread.start()

    except KeyboardInterrupt:
        break
    except Exception as e:
        print(e)

audio_queue.put(None)
player_thread.join()