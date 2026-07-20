"""
Cálculo del error de reconstrucción mediante Series de Fourier.

Evalúa el error únicamente en los tramos de continuidad,
excluyendo los puntos de discontinuidad.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from auxiliar.funciones_auxiliares.amplitude_vs_time_aux import generar_diente_sierra
from auxiliar.funciones_auxiliares.fourier_series_aux import fourier_diente_sierra


def calcular_margen_gibbs(
    frecuencia: float,
    fs: int,
    armonicos: int,
    factor: float = 1.0,
) -> int:
    """
    Estima el margen de exclusión alrededor
    de discontinuidades debido al fenómeno de Gibbs.
    """

    tiempo_gibbs = factor / (armonicos * frecuencia)

    muestras = int(tiempo_gibbs * fs)

    return muestras


def detectar_tramos_continuidad(
    senal: np.ndarray,
    margen: int,
    umbral: float = 0.5,
) -> np.ndarray:
    """
    Obtiene los índices correspondientes a tramos continuos.

    Los puntos próximos a saltos son eliminados.

    Parámetros
    ----------
    señal:
        Señal original generada por amplitude_vs_time.

    margen:
        Cantidad de muestras eliminadas alrededor
        de cada discontinuidad.

    umbral:
        Salto mínimo para considerar discontinuidad.

    Retorna
    -------
    np.ndarray
        Índices pertenecientes a zonas continuas.
    """

    diferencia = np.abs(np.diff(senal))

    discontinuidades = np.where(diferencia > umbral)[0]

    mascara = np.ones(len(senal), dtype=bool)

    for idx in discontinuidades:
        inicio = max(0, idx - margen)

        fin = min(len(senal), idx + margen)

        mascara[inicio:fin] = False

    return np.where(mascara)[0]


def calcular_error_continuidad(
    senal_original: np.ndarray,
    senal_fourier: np.ndarray,
    indices_continuidad: np.ndarray,
) -> dict:
    """
    Calcula el error entre señal original
    y reconstrucción Fourier en regiones continuas.

    Parámetros
    ----------
    señal_original:
        Señal generada por amplitude_vs_time.

    señal_fourier:
        Señal sintetizada mediante Fourier.

    indices_continuidad:
        Índices donde se evalúa el error.

    Retorna
    -------
    dict
        Estadísticos del error.
    """

    error = senal_original[indices_continuidad] - senal_fourier[indices_continuidad]

    error_abs = np.abs(error)

    referencia = np.abs(senal_original[indices_continuidad])

    error_rel = np.zeros_like(error_abs)

    mascara = referencia > 1e-12

    error_rel[mascara] = (error_abs[mascara] / referencia[mascara]) * 100

    return {
        "error_medio": np.mean(error_abs),
        "error_maximo": np.max(error_abs),
        "error_rms": np.sqrt(np.mean(error**2)),
        "error_relativo_medio_%": np.mean(error_rel),
        "indices_evaluados": indices_continuidad,
    }


# ======================================
# EJEMPLO
# ======================================
# Aplicacion de la funcion comparation a la funcion diente_sierra

frecuencia = 10
amplitud = 1
fs = 48000
fase = np.pi
duracion = 1
armonicos = 20

# Seleccionar solamente los tramos continuos de la senal
senal = generar_diente_sierra(
    frecuencia=frecuencia, amplitud=amplitud, duracion=duracion, fs=fs, fase=fase
)

# Calculo del margen de muestras en el entorno de la discontinuidad

margen = calcular_margen_gibbs(
    frecuencia=frecuencia,
    fs=fs,
    armonicos=armonicos,
)

# Calculo de los puntos en los cuales la senal es continua
indices_continuidad = detectar_tramos_continuidad(senal=senal, margen=margen)

senal_f = fourier_diente_sierra(
    frecuencia=frecuencia,
    amplitud=amplitud,
    duracion=duracion,
    fs=fs,
    armonicos=armonicos,
)


# indices_continuidad_f = detectar_tramos_continuidad
# Calculo del error

resultado = calcular_error_continuidad(
    senal_original=senal,
    senal_fourier=senal_f,
    indices_continuidad=indices_continuidad,
)

print(resultado)
print(senal[0])
print(senal_f[0])
print(margen)

# Gráfico


# Tiempo
tiempo = np.arange(len(senal)) / fs


# Índices utilizados para calcular el error
indices = resultado["indices_evaluados"]


# Ventana de visualización
t_inicio = 0.0
t_fin = 0.2

i_inicio = int(t_inicio * fs)
i_fin = int(t_fin * fs)


# Seleccionar puntos evaluados dentro de la ventana
indices_plot = indices[(indices >= i_inicio) & (indices <= i_fin)]


plt.figure(figsize=(12, 5))


plt.figure(figsize=(12, 5))


# Señal original
"""
plt.plot(
    tiempo[i_inicio:i_fin], senal[i_inicio:i_fin], label="Señal original", linewidth=1
)
"""

# Serie Fourier
plt.plot(
    tiempo[i_inicio:i_fin],
    senal_f[i_inicio:i_fin],
    label=f"Serie de Fourier ({armonicos} armónicos)",
    linewidth=0.8,
    color="black",
)


# Puntos utilizados para el cálculo del error
# Seleccionar el 10 % de los puntos evaluados
cantidad_puntos = int(0.01 * len(indices_plot))

indices_mostrar = np.linspace(0, len(indices_plot) - 1, cantidad_puntos, dtype=int)

indices_plot_10 = indices_plot[indices_mostrar]


plt.scatter(
    tiempo[indices_plot_10],
    senal[indices_plot_10],
    s=5,
    color="red",
    label="Puntos de evaluación\n expuestos en el gráfico (1.00 %)",
)


plt.xlabel("Tiempo [s]")
plt.ylabel("Amplitud")


plt.title(
    "Reconstrucción Fourier del diente de sierra\n"
    f"Error medio={resultado['error_medio']:.5f} | "
    f"Error valor eficaz={resultado['error_rms']:.5f} | "
    f"Error máximo={resultado['error_maximo']:.5f} | "
    f"Error relativo={resultado['error_relativo_medio_%']:.2f} | "
    f"Margen={margen} muestras"
)


plt.grid(True)
plt.legend()
plt.tight_layout()

plt.show()
