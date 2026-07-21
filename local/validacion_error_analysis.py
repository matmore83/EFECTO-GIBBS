"""
Validación del módulo error_analysis.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# Agrega la raíz del proyecto al PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.error_analysis import error_analysis
from app.services.fourier_series import fourier_pulso

# ===========================================
# Parámetros
# ===========================================

fs = 5000
duracion = 1
frecuencia = 5
amplitud = 1
armonicos = 20


# ===========================================
# Señal ideal
# ===========================================

t = np.arange(0, duracion, 1 / fs)

senal_ideal = np.sign(np.sin(2 * np.pi * frecuencia * t))


# ===========================================
# Señal sintetizada
# ===========================================

senal_fourier = fourier_pulso(
    frecuencia=frecuencia,
    amplitud=amplitud,
    duracion=duracion,
    fs=fs,
    armonicos=armonicos,
)


# ===========================================
# Análisis del error
# ===========================================

resultado = error_analysis(
    señal_ideal=senal_ideal,
    señal_fourier=senal_fourier,
    amplitud=amplitud,
)


# ===========================================
# Gráficos
# ===========================================

plt.figure(figsize=(12, 7))

plt.subplot(3, 1, 1)

plt.plot(
    t,
    senal_ideal,
    label="Ideal",
)

plt.plot(
    t,
    senal_fourier,
    label="Fourier",
)

plt.title("Comparación de señales")
plt.grid(True)
plt.legend()


plt.subplot(3, 1, 2)

plt.plot(
    t,
    resultado["error_porcentual"],
)

plt.title("Error porcentual")
plt.grid(True)


plt.subplot(3, 1, 3)

plt.plot(
    resultado["error_entorno"],
)

plt.title("Error en el entorno de las discontinuidades")
plt.grid(True)

plt.tight_layout()
plt.show()


print()

print("========== RESULTADOS ==========")

print(f"Error máximo: {resultado['error_maximo']:.3f} %")

print(f"Error promedio: {resultado['error_promedio']:.3f} %")

print()

print("Discontinuidades encontradas:")

print(resultado["indices_discontinuidad"])
