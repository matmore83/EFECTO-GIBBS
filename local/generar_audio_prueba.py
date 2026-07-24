from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf

# Crear carpeta examples si no existe
Path("examples").mkdir(exist_ok=True)

fs = 44100
duracion = 2.0

t = np.linspace(0, duracion, int(fs * duracion), endpoint=False)

# Seno de 440 Hz
senal = 0.5 * np.sin(2 * np.pi * 440 * t)

sf.write(
    "examples/audio_prueba.wav",
    senal,
    fs,
)

print("Audio generado correctamente.")