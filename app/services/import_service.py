"""
Carga de archivos de audio.

Permite importar señales de audio para su posterior análisis
o procesamiento mediante Series de Fourier.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf

EXTENSIONES_VALIDAS = {
    ".wav",
    ".flac",
    ".ogg",
    ".aiff",
    ".aif",
}


def cargar_audio(
    ruta: str | Path,
) -> tuple[np.ndarray, int]:
    """
    Carga un archivo de audio.

    Parámetros
    ----------
    ruta : str | Path
        Ruta del archivo.

    Retorna
    -------
    tuple[np.ndarray, int]

        señal
            Señal de audio normalizada.

        fs
            Frecuencia de muestreo [Hz].

    Raises
    ------
    FileNotFoundError
        Si el archivo no existe.

    ValueError
        Si el formato no es soportado.

    RuntimeError
        Si ocurre un error durante la lectura.
    """

    ruta = Path(ruta)

    if not ruta.exists():
        raise FileNotFoundError(
            f"No existe el archivo: {ruta}"
        )

    if ruta.suffix.lower() not in EXTENSIONES_VALIDAS:
        raise ValueError(
            f"Formato no soportado: {ruta.suffix}"
        )

    try:
        señal, fs = sf.read(ruta)

    except Exception as exc:
        raise RuntimeError(
            "No fue posible leer el archivo."
        ) from exc

    señal = np.asarray(señal, dtype=float)

    # Conversión a mono
    if señal.ndim == 2:
        señal = np.mean(
            señal,
            axis=1,
        )

    # Normalización
    maximo = np.max(np.abs(señal))

    if maximo > 0:
        señal = señal / maximo

    return señal, fs