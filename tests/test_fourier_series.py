"""
Tests para el módulo fourier_series.py

Se verifican:

- Funciones auxiliares.
- Cálculo analítico de coeficientes.
- Síntesis de señales.
- Conversión a magnitud y fase.
- Validaciones de parámetros.
"""

import numpy as np
import pytest

from app.services.fourier_series import (
    _amplitud_fase,
    _frecuencia_angular,
    _vector_tiempo,
    coeficientes_diente_sierra,
    coeficientes_pulso,
    coeficientes_triangular,
    fourier_diente_sierra,
    fourier_pulso,
    fourier_triangular,
    magnitud_fase_diente_sierra,
    magnitud_fase_pulso,
    magnitud_fase_triangular,
)

# ==========================================================
# TESTS DE FUNCIONES AUXILIARES
# ==========================================================


def test_vector_tiempo():
    """
    Verifica que el vector temporal tenga la cantidad
    correcta de muestras.
    """

    t = _vector_tiempo(
        duracion=1,
        fs=1000,
    )

    assert len(t) == 1000
    assert np.isclose(t[0], 0.0)


def test_frecuencia_angular():
    """
    Verifica el cálculo de la frecuencia angular.
    """

    w = _frecuencia_angular(10)

    assert np.isclose(
        w,
        2 * np.pi * 10,
    )


def test_amplitud_fase():
    """
    Comprueba la conversión de coeficientes
    seno-coseno a magnitud y fase.
    """

    an = np.array([1.0])
    bn = np.array([0.0])

    A, phi = _amplitud_fase(
        an,
        bn,
    )

    assert np.isclose(A[0], 1.0)
    assert np.isclose(phi[0], 0.0)


# ==========================================================
# TESTS DE COEFICIENTES
# ==========================================================


def test_coeficientes_pulso():
    """
    Verifica los coeficientes analíticos del pulso.
    """

    a0, an, bn = coeficientes_pulso(
        amplitud=1,
        armonicos=5,
    )

    assert a0 == 0
    assert np.allclose(an, np.zeros(5))
    assert bn[0] > 0


def test_coeficientes_diente_sierra():
    """
    Verifica los coeficientes del diente de sierra.
    """

    a0, an, bn = coeficientes_diente_sierra(
        amplitud=1,
        armonicos=5,
    )

    assert a0 == 0
    assert np.allclose(an, np.zeros(5))
    assert bn[0] > 0


def test_coeficientes_triangular():
    """
    Verifica los coeficientes de la señal triangular.
    """

    a0, an, bn = coeficientes_triangular(
        amplitud=1,
        armonicos=5,
    )

    assert a0 == 0
    assert np.allclose(an, np.zeros(5))
    assert bn[0] > 0


# ==========================================================
# TESTS DE SÍNTESIS
# ==========================================================


def test_fourier_pulso():
    """
    Comprueba que la señal sintetizada tenga
    la longitud correcta.
    """

    y = fourier_pulso(
        frecuencia=10,
        amplitud=1,
        duracion=1,
        fs=1000,
        armonicos=20,
    )

    assert len(y) == 1000


def test_fourier_diente_sierra():
    """
    Comprueba la longitud de la señal sintetizada.
    """

    y = fourier_diente_sierra(
        frecuencia=10,
        amplitud=1,
        duracion=1,
        fs=1000,
        armonicos=20,
    )

    assert len(y) == 1000


def test_fourier_triangular():
    """
    Comprueba la longitud de la señal sintetizada.
    """

    y = fourier_triangular(
        frecuencia=10,
        amplitud=1,
        duracion=1,
        fs=1000,
        armonicos=20,
    )

    assert len(y) == 1000


# ==========================================================
# TESTS DE MAGNITUD Y FASE
# ==========================================================


def test_magnitud_fase_pulso():
    """
    Verifica la longitud de los vectores
    de magnitud y fase.
    """

    A, phi = magnitud_fase_pulso(
        amplitud=1,
        armonicos=10,
    )

    assert len(A) == 10
    assert len(phi) == 10


def test_magnitud_fase_diente_sierra():
    """
    Verifica la longitud de los vectores
    de magnitud y fase.
    """

    A, phi = magnitud_fase_diente_sierra(
        amplitud=1,
        armonicos=10,
    )

    assert len(A) == 10
    assert len(phi) == 10


def test_magnitud_fase_triangular():
    """
    Verifica la longitud de los vectores
    de magnitud y fase.
    """

    A, phi = magnitud_fase_triangular(
        amplitud=1,
        armonicos=10,
    )

    assert len(A) == 10
    assert len(phi) == 10


# ==========================================================
# TESTS DE VALIDACIONES
# ==========================================================


@pytest.mark.parametrize(
    "amplitud",
    [-1, -2],
)
def test_amplitud_negativa(amplitud):
    """
    No debe permitirse amplitud negativa.
    """

    with pytest.raises(ValueError):
        coeficientes_pulso(
            amplitud=amplitud,
            armonicos=5,
        )


@pytest.mark.parametrize(
    "armonicos",
    [0, -1],
)
def test_armonicos_invalidos(armonicos):
    """
    La cantidad de armónicos debe ser mayor que cero.
    """

    with pytest.raises(ValueError):
        coeficientes_diente_sierra(
            amplitud=1,
            armonicos=armonicos,
        )


@pytest.mark.parametrize(
    "frecuencia",
    [0, -10],
)
def test_frecuencia_invalida(frecuencia):
    """
    La frecuencia debe ser positiva.
    """

    with pytest.raises(ValueError):
        fourier_triangular(
            frecuencia=frecuencia,
            amplitud=1,
            duracion=1,
            fs=1000,
            armonicos=10,
        )


@pytest.mark.parametrize(
    "fs",
    [0, -1000],
)
def test_fs_invalido(fs):
    """
    La frecuencia de muestreo debe ser positiva.
    """

    with pytest.raises(ValueError):
        fourier_pulso(
            frecuencia=10,
            amplitud=1,
            duracion=1,
            fs=fs,
            armonicos=10,
        )


@pytest.mark.parametrize(
    "duracion",
    [0, -1],
)
def test_duracion_invalida(duracion):
    """
    La duración debe ser positiva.
    """

    with pytest.raises(ValueError):
        fourier_diente_sierra(
            frecuencia=10,
            amplitud=1,
            duracion=duracion,
            fs=1000,
            armonicos=10,
        )
