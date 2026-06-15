import torch
import os
from TTS.api import TTS

# 1. Hardware Check
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"\n[VOICE PROTOCOL] Initializing neural net on {device.upper()}...")

# 2. Auto-Accept Coqui Terms of Service
os.environ["COQUI_TOS_AGREED"] = "1"

# 3. Load Model (This downloads the AI brain the very first time you run it)
print("[VOICE PROTOCOL] Loading XTTS-v2 Voice Engine. Standby...")
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

# 4. The Payload
text_to_speak = "Hello Atharv. I am Friday. All neural pathways are connected, and my systems are fully online."
reference_audio = "friday_sample.wav"
output_file = "first_words.wav"

# 5. Generate Output
print(f"[VOICE PROTOCOL] Cloning voice from {reference_audio} and generating speech...")
tts.tts_to_file(text=text_to_speak,
                speaker_wav=reference_audio,
                language="en",
                file_path=output_file)

print(f"\n[VOICE PROTOCOL] SUCCESS! Audio saved as {output_file}. Go listen to it!")