import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt

from app.services.fourier_series import (
    fourier_diente_sierra,
    fourier_pulso,
    fourier_triangular,
)

# ==================================================
# Configuración
# ==================================================

FS = 48000
DURACION = 2.0
FRECUENCIA = 2.0
AMPLITUD = 1.0
ARMONICOS = 50

# Elegir señal:
# "pulso"
# "diente"
# "triangular"

TIPO = "pulso"

# ==================================================
# Generación
# ==================================================

if TIPO == "pulso":
    senal = fourier_pulso(
        frecuencia=FRECUENCIA,
        amplitud=AMPLITUD,
        duracion=DURACION,
        fs=FS,
        armonicos=ARMONICOS,
    )

elif TIPO == "diente":
    senal = fourier_diente_sierra(
        frecuencia=FRECUENCIA,
        amplitud=AMPLITUD,
        duracion=DURACION,
        fs=FS,
        armonicos=ARMONICOS,
    )

elif TIPO == "triangular":
    senal = fourier_triangular(
        frecuencia=FRECUENCIA,
        amplitud=AMPLITUD,
        duracion=DURACION,
        fs=FS,
        armonicos=ARMONICOS,
    )

else:
    raise ValueError("Tipo de señal inválido. Use: pulso, diente o triangular.")

# ==================================================
# Gráfico
# ==================================================

plt.figure(figsize=(10, 4))

plt.plot(senal)

plt.title(
    f"{TIPO.capitalize()} - Aproximación mediante Series de Fourier\n"
    f"{ARMONICOS} armónicos"
)

plt.xlabel("Muestras")
plt.ylabel("Amplitud")

plt.grid(True)

plt.tight_layout()

plt.show()
