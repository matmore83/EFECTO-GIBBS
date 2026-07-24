"""
Tests del módulo import_service.

Se verifica:

- Lectura correcta de archivos.
- Frecuencia de muestreo.
- Conversión a mono.
- Normalización.
- Archivo inexistente.
- Extensión inválida.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Agrega la raíz del proyecto al PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parents[1]))

import numpy as np
import pytest
import soundfile as sf

from app.services.import_service import cargar_audio

# ---------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------

@pytest.fixture
def audio_temporal(tmp_path: Path):
    """
    Genera un archivo WAV temporal.
    """

    fs = 44100

    t = np.linspace(
        0,
        1,
        fs,
        endpoint=False,
    )

    señal = 0.5 * np.sin(2 * np.pi * 440 * t)

    ruta = tmp_path / "audio.wav"

    sf.write(
        ruta,
        señal,
        fs,
    )

    return ruta, señal, fs


# ---------------------------------------------------------------------
# Lectura correcta
# ---------------------------------------------------------------------

def test_cargar_audio(audio_temporal):
    """
    Verifica que el archivo pueda cargarse correctamente.
    """

    ruta, señal_original, fs = audio_temporal

    señal, frecuencia = cargar_audio(ruta)

    assert frecuencia == fs
    assert len(señal) == len(señal_original)


# ---------------------------------------------------------------------
# Normalización
# ---------------------------------------------------------------------

def test_normalizacion(audio_temporal):
    """
    Verifica que la señal quede normalizada.
    """

    ruta, _, _ = audio_temporal

    señal, _ = cargar_audio(ruta)

    assert np.max(np.abs(señal)) == pytest.approx(
        1.0,
        abs=1e-6,
    )


# ---------------------------------------------------------------------
# Conversión a mono
# ---------------------------------------------------------------------

def test_conversion_mono(tmp_path: Path):
    """
    Verifica la conversión automática de estéreo a mono.
    """

    fs = 44100

    t = np.linspace(
        0,
        1,
        fs,
        endpoint=False,
    )

    canal_izquierdo = np.sin(2 * np.pi * 440 * t)
    canal_derecho = np.sin(2 * np.pi * 880 * t)

    señal_estereo = np.column_stack(
        (
            canal_izquierdo,
            canal_derecho,
        )
    )

    ruta = tmp_path / "estereo.wav"

    sf.write(
        ruta,
        señal_estereo,
        fs,
    )

    señal, _ = cargar_audio(ruta)

    assert señal.ndim == 1
    assert len(señal) == fs


# ---------------------------------------------------------------------
# Archivo inexistente
# ---------------------------------------------------------------------

def test_archivo_inexistente():
    """
    Debe lanzar FileNotFoundError si el archivo no existe.
    """

    with pytest.raises(FileNotFoundError):
        cargar_audio("archivo.wav")


# ---------------------------------------------------------------------
# Extensión inválida
# ---------------------------------------------------------------------

def test_extension_invalida(tmp_path: Path):
    """
    Debe lanzar ValueError para extensiones no soportadas.
    """

    ruta = tmp_path / "archivo.txt"

    ruta.write_text("Hola")

    with pytest.raises(ValueError):
        cargar_audio(ruta)


# ---------------------------------------------------------------------
# Señal mono
# ---------------------------------------------------------------------

def test_senal_mono(audio_temporal):
    """
    Una señal mono debe permanecer mono.
    """

    ruta, _, _ = audio_temporal

    señal, _ = cargar_audio(ruta)

    assert señal.ndim == 1


# ---------------------------------------------------------------------
# Tipo de dato
# ---------------------------------------------------------------------

def test_tipo_dato(audio_temporal):
    """
    La señal debe devolverse como float.
    """

    ruta, _, _ = audio_temporal

    señal, _ = cargar_audio(ruta)

    assert np.issubdtype(
        señal.dtype,
        np.floating,
    )