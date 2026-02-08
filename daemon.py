#!/usr/bin/env python3
"""
Daemon de Qwen3-TTS que mantiene el modelo en memoria y procesa texto desde un archivo.
"""

import torch
import soundfile as sf
import warnings
import time
import sys
import os
import subprocess
import tempfile

# Silenciar ruido
warnings.filterwarnings("ignore")
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

# Redirigir stdout durante import
import io
old_stdout = sys.stdout
sys.stdout = io.StringIO()

from qwen_tts import Qwen3TTSModel

sys.stdout = old_stdout

# Configuración
TEXT_STREAM = os.path.expanduser("~/.decir_qwen/text_stream")
VOICES_DIR = os.path.expanduser("~/robotin/apps/decir-qwen/voices")
VOICE = os.environ.get("DECIRD_QWEN_VOICE", os.path.join(VOICES_DIR, "Lionel.mp3"))

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def play_audio(wav_file):
    """Reproduce el audio usando paplay"""
    try:
        subprocess.run(
            ["paplay", wav_file],
            check=True,
            capture_output=True
        )
    except Exception as e:
        log(f"Error reproduciendo audio: {e}")

def main():
    log("Iniciando daemon Qwen3-TTS...")

    # Detectar dispositivo
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    device_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"

    log(f"Dispositivo: {device_name}")
    log(f"Voz: {VOICE}")

    # Cargar modelo
    log("Cargando modelo...")
    sys.stdout = io.StringIO()
    model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        device_map=device,
        dtype=dtype,
    )
    sys.stdout = old_stdout
    log("Modelo cargado. Esperando texto...")

    # Abrir el archivo y posicionarse al final
    with open(TEXT_STREAM, "r") as f:
        # Ir al final del archivo
        f.seek(0, 2)

        while True:
            line = f.readline()
            if line:
                text = line.strip()
                if text:
                    log(f"Procesando: {text[:50]}{'...' if len(text) > 50 else ''}")

                    try:
                        start = time.time()

                        # Silenciar durante generación
                        sys.stdout = io.StringIO()
                        wavs, sr = model.generate_voice_clone(
                            text=text,
                            language="Spanish",
                            ref_audio=VOICE,
                            x_vector_only_mode=True,
                        )
                        sys.stdout = old_stdout

                        # Guardar en archivo temporal
                        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                            sf.write(tmp.name, wavs[0], sr)
                            tmp_path = tmp.name

                        log(f"Generado en {time.time() - start:.1f}s, reproduciendo...")

                        # Reproducir
                        play_audio(tmp_path)

                        # Limpiar
                        os.unlink(tmp_path)

                    except Exception as e:
                        sys.stdout = old_stdout
                        log(f"Error: {e}")
            else:
                # No hay nuevas líneas, esperar un poco
                time.sleep(0.1)

if __name__ == "__main__":
    main()
