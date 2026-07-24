from __future__ import annotations

import sys
from pathlib import Path

# Agrega la raíz del proyecto al PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parents[1]))

import numpy as np
import pytest

from app.services.error_analysis import (
    error_absoluto,
    error_analysis,
    error_entorno,
    error_porcentual,
    obtener_discontinuidades,
)

# ==========================================================
# ERROR ABSOLUTO
# ==========================================================


def test_error_absoluto_calculo_correcto():
    """Verifica el cálculo correcto del error absoluto."""

    ideal = np.array([1, 2, 3])
    fourier = np.array([1, 1, 2])

    esperado = np.array([0, 1, 1])

    np.testing.assert_array_equal(
        error_absoluto(
            ideal,
            fourier,
        ),
        esperado,
    )


def test_error_absoluto_longitudes_distintas():
    """Debe lanzar excepción si las señales tienen distinta longitud."""

    with pytest.raises(ValueError):
        error_absoluto(
            np.array([1, 2]),
            np.array([1]),
        )


# ==========================================================
# ERROR PORCENTUAL
# ==========================================================


def test_error_porcentual():
    """Verifica el cálculo correcto del error porcentual."""

    ideal = np.array([1.0, 1.0])
    fourier = np.array([0.5, 1.0])

    esperado = np.array([50.0, 0.0])

    np.testing.assert_allclose(
        error_porcentual(
            ideal,
            fourier,
            amplitud=1,
        ),
        esperado,
    )


def test_error_porcentual_amplitud_negativa():
    """Debe lanzar excepción si la amplitud es inválida."""

    with pytest.raises(ValueError):
        error_porcentual(
            np.array([1]),
            np.array([1]),
            amplitud=0,
        )


# ==========================================================
# DETECCIÓN DE DISCONTINUIDADES
# ==========================================================


def test_obtener_discontinuidades():
    """Detecta correctamente un salto."""

    señal = np.array(
        [
            0,
            0,
            0,
            1,
            1,
            1,
        ]
    )

    indices = obtener_discontinuidades(señal)

    assert len(indices) == 1
    assert indices[0] == 2


def test_obtener_discontinuidades_sin_saltos():
    """No debe detectar discontinuidades."""

    señal = np.zeros(100)

    indices = obtener_discontinuidades(señal)

    assert len(indices) == 0


# ==========================================================
# ERROR EN EL ENTORNO
# ==========================================================


def test_error_entorno():
    """Extrae correctamente una ventana alrededor del salto."""

    error = np.arange(100)

    indices = np.array([50])

    entorno = error_entorno(
        error,
        indices,
        ventana=5,
    )

    esperado = np.arange(45, 56)

    np.testing.assert_array_equal(
        entorno,
        esperado,
    )


def test_error_entorno_vacio():
    """Debe devolver un arreglo vacío cuando no existen discontinuidades."""

    entorno = error_entorno(
        np.arange(10),
        np.array([]),
    )

    assert entorno.size == 0


# ==========================================================
# FUNCIÓN PRINCIPAL
# ==========================================================


def test_error_analysis_diccionario():
    """Comprueba que la función principal devuelve todas las métricas."""

    ideal = np.array(
        [
            0,
            0,
            1,
            1,
        ]
    )

    fourier = np.array(
        [
            0,
            0.1,
            0.9,
            1,
        ]
    )

    resultado = error_analysis(
        señal_ideal=ideal,
        señal_fourier=fourier,
        amplitud=1,
        ventana=1,
    )

    assert "error_absoluto" in resultado
    assert "error_porcentual" in resultado
    assert "indices_discontinuidad" in resultado
    assert "cantidad_discontinuidades" in resultado
    assert "error_entorno" in resultado
    assert "error_maximo" in resultado
    assert "error_promedio" in resultado


def test_error_analysis_error_maximo():
    """El error máximo debe ser mayor o igual que el promedio."""

    ideal = np.array(
        [
            0,
            0,
            1,
            1,
        ]
    )

    fourier = np.array(
        [
            0,
            0.2,
            0.8,
            1,
        ]
    )

    resultado = error_analysis(
        ideal,
        fourier,
        amplitud=1,
    )

    assert resultado["error_maximo"] >= resultado["error_promedio"]


def test_error_analysis_cantidad_discontinuidades():
    """Verifica que la cantidad de discontinuidades sea consistente."""

    ideal = np.array(
        [
            0,
            0,
            1,
            1,
            0,
            0,
        ]
    )

    fourier = ideal.copy()

    resultado = error_analysis(
        ideal,
        fourier,
        amplitud=1,
    )

    assert resultado["cantidad_discontinuidades"] == len(
        resultado["indices_discontinuidad"]
    )
