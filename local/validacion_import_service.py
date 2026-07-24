"""
Validación del módulo import_service.

Carga un archivo de audio y muestra información
básica junto con su representación temporal.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt

# Agrega la raíz del proyecto al PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.import_service import cargar_audio

RUTA_AUDIO = "examples/audio_prueba.wav"


senal, fs = cargar_audio(RUTA_AUDIO)

print(f"Frecuencia de muestreo : {fs} Hz")
print(f"Cantidad de muestras   : {len(senal)}")
print(f"Duración               : {len(senal)/fs:.3f} s")
print(f"Valor máximo           : {senal.max():.3f}")
print(f"Valor mínimo           : {senal.min():.3f}")

plt.figure(figsize=(10,4))
plt.plot(senal)
plt.title("Señal cargada")
plt.xlabel("Muestras")
plt.ylabel("Amplitud")
plt.grid(True)

plt.tight_layout()
plt.show()