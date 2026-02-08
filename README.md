# decir-qwen

Daemon de text-to-speech usando Qwen3-TTS con voice cloning.

Mantiene el modelo cargado en memoria (GPU) para generar audio más rápido.

## Requisitos

- Qwen3-TTS instalado en `~/apps/qwen3-tts/`
- GPU NVIDIA con CUDA (opcional, funciona en CPU pero más lento)
- PulseAudio (`paplay`)

## Instalación

```bash
# Crear symlinks en ~/bin
ln -sf ~/robotin/apps/decir-qwen/decir_qwen ~/bin/decir_qwen
ln -sf ~/robotin/apps/decir-qwen/decird_qwen ~/bin/decird_qwen
chmod +x ~/robotin/apps/decir-qwen/*.py ~/robotin/apps/decir-qwen/decir*
```

## Uso

```bash
# Iniciar el daemon (carga el modelo, ~8s)
decird_qwen start

# Enviar texto para leer
decir_qwen "Hola, esto es una prueba"

# También acepta stdin
echo "Texto desde pipe" | decir_qwen

# Ver estado
decird_qwen status

# Detener
decird_qwen stop
```

## Voces incluidas

El repo incluye 4 voces para clonación en `voices/`:
- `Lionel.mp3` (default)
- `Brian.mp3`
- `Carlos.mp3`
- `Claudio.mp3`

## Configuración

Variables de entorno:
- `DECIRD_QWEN_VOICE`: Ruta al archivo de audio de referencia para voice cloning (default: `voices/Lionel.mp3`)

## Rendimiento

- Primera frase después de iniciar: ~3-4s (modelo ya cargado)
- Sin daemon (slg-gobot-say): ~9s (incluye carga del modelo)
- CPU en lugar de GPU: ~60-120s

## Archivos

- `~/.decir_qwen/text_stream`: Archivo donde se escribe el texto a leer
- `~/.decir_qwen/daemon.pid`: PID del daemon
- `~/.decir_qwen/daemon.log`: Log del daemon
