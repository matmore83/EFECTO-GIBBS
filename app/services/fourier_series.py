"""
Síntesis mediante Series de Fourier.

Este módulo implementa la reconstrucción de señales periódicas mediante
Series de Fourier en sus dos formas:

- Expansión en senos y cosenos.
- Expansión en magnitud y fase.

Se contemplan las siguientes señales:

- Pulso.
- Diente de sierra.
- Triangular.
"""

from __future__ import annotations

import numpy as np


def _vector_tiempo(
    duracion: float,
    fs: int,
) -> np.ndarray:
    """
    Genera el vector temporal.

    Parámetros
    ----------
    duracion : float
        Duración de la señal [s].

    fs : int
        Frecuencia de muestreo [Hz].

    Retorna
    -------
    np.ndarray
        Vector temporal.
    """

    return np.arange(0, duracion, 1 / fs)


def _frecuencia_angular(
    frecuencia: float,
) -> float:
    """
    Calcula la frecuencia angular fundamental.

    Parámetros
    ----------
    frecuencia : float
        Frecuencia fundamental [Hz].

    Retorna
    -------
    float
        Frecuencia angular [rad/s].
    """

    return 2 * np.pi * frecuencia


def _validar_parametros(
    frecuencia: float,
    amplitud: float,
    duracion: float,
    fs: int,
    armonicos: int,
) -> None:
    """
    Valida los parámetros de entrada de las funciones de síntesis.
    """

    if frecuencia <= 0:
        raise ValueError("La frecuencia debe ser mayor que cero.")

    if amplitud < 0:
        raise ValueError("La amplitud no puede ser negativa.")

    if duracion <= 0:
        raise ValueError("La duración debe ser mayor que cero.")

    if fs <= 0:
        raise ValueError("La frecuencia de muestreo debe ser mayor que cero.")

    if armonicos <= 0:
        raise ValueError("La cantidad de armónicos debe ser mayor que cero.")


def _amplitud_fase(
    an: np.ndarray,
    bn: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Convierte coeficientes seno-coseno a magnitud y fase.

    Parámetros
    ----------
    an : np.ndarray
        Coeficientes del coseno.

    bn : np.ndarray
        Coeficientes del seno.

    Retorna
    -------
    tuple[np.ndarray, np.ndarray]

        amplitud
            Magnitud de cada armónico.

        fase
            Fase de cada armónico [rad].
    """

    amplitud = np.sqrt(an**2 + bn**2)
    fase = np.arctan2(-bn, an)

    return amplitud, fase


def sintetizar_seno_coseno(
    frecuencia: float,
    duracion: float,
    fs: int,
    a0: float,
    an: np.ndarray,
    bn: np.ndarray,
) -> np.ndarray:
    """
    Sintetiza una señal periódica a partir de sus coeficientes
    de la Serie de Fourier en forma seno-coseno.

    La señal sintetizada responde a:

        x(t) = a0/2 +
               Σ [an*cos(n*w0*t) + bn*sin(n*w0*t)]

    Parámetros
    ----------
    frecuencia : float
        Frecuencia fundamental [Hz].

    duracion : float
        Duración de la señal [s].

    fs : int
        Frecuencia de muestreo [Hz].

    a0 : float
        Coeficiente constante.

    an : np.ndarray
        Coeficientes del coseno.

    bn : np.ndarray
        Coeficientes del seno.

    Retorna
    -------
    np.ndarray
        Señal sintetizada.
    """

    t = _vector_tiempo(duracion, fs)
    w0 = _frecuencia_angular(frecuencia)

    señal = np.full_like(t, a0 / 2)

    for n in range(1, len(an) + 1):
        señal += an[n - 1] * np.cos(n * w0 * t) + bn[n - 1] * np.sin(n * w0 * t)

    return señal


def coeficientes_pulso(
    amplitud: float,
    armonicos: int,
) -> tuple[float, np.ndarray, np.ndarray]:
    """
    Calcula los coeficientes analíticos de la Serie de Fourier
    para un pulso simétrico de ciclo útil 50 %.

    Parámetros
    ----------
    amplitud : float
        Amplitud pico.

    armonicos : int
        Cantidad de armónicos.

    Retorna
    -------
    tuple

        a0
            Coeficiente constante.

        an
            Coeficientes del coseno.

        bn
            Coeficientes del seno.
    """

    if amplitud < 0:
        raise ValueError("La amplitud no puede ser negativa.")

    if armonicos <= 0:
        raise ValueError("La cantidad de armónicos debe ser mayor que cero.")

    a0 = 0.0

    an = np.zeros(armonicos)
    bn = np.zeros(armonicos)

    for n in range(1, armonicos + 1):
        if n % 2 == 1:
            bn[n - 1] = (4 * amplitud) / (np.pi * n)

    return a0, an, bn


def magnitud_fase_pulso(
    amplitud: float,
    armonicos: int,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Obtiene la representación en magnitud y fase
    de la Serie de Fourier de un pulso.

    Parámetros
    ----------
    amplitud : float
        Amplitud pico.

    armonicos : int
        Cantidad de armónicos.

    Retorna
    -------
    tuple[np.ndarray, np.ndarray]

        magnitud
            Magnitud de cada armónico.

        fase
            Fase de cada armónico [rad].
    """

    _, an, bn = coeficientes_pulso(
        amplitud,
        armonicos,
    )

    return _amplitud_fase(an, bn)


def fourier_pulso(
    frecuencia: float,
    amplitud: float,
    duracion: float,
    fs: int,
    armonicos: int,
) -> np.ndarray:
    """
    Sintetiza un pulso mediante su Serie de Fourier.
    """

    _validar_parametros(
        frecuencia=frecuencia,
        amplitud=amplitud,
        duracion=duracion,
        fs=fs,
        armonicos=armonicos,
    )

    a0, an, bn = coeficientes_pulso(
        amplitud,
        armonicos,
    )

    return sintetizar_seno_coseno(
        frecuencia=frecuencia,
        duracion=duracion,
        fs=fs,
        a0=a0,
        an=an,
        bn=bn,
    )


def coeficientes_diente_sierra(
    amplitud: float,
    armonicos: int,
) -> tuple[float, np.ndarray, np.ndarray]:
    """
    Calcula los coeficientes analíticos de la Serie de Fourier
    para una onda diente de sierra.

    Parámetros
    ----------
    amplitud : float
        Amplitud pico.

    armonicos : int
        Cantidad de armónicos.

    Retorna
    -------
    tuple
        a0, an y bn.
    """

    if amplitud < 0:
        raise ValueError("La amplitud no puede ser negativa.")

    if armonicos <= 0:
        raise ValueError("La cantidad de armónicos debe ser mayor que cero.")

    a0 = 0.0

    an = np.zeros(armonicos)
    bn = np.zeros(armonicos)

    for n in range(1, armonicos + 1):
        bn[n - 1] = 2 * amplitud * ((-1) ** (n + 1)) / (np.pi * n)

    return a0, an, bn


def magnitud_fase_diente_sierra(
    amplitud: float,
    armonicos: int,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Obtiene la representación en magnitud y fase
    de la Serie de Fourier de una onda diente de sierra.
    """

    _, an, bn = coeficientes_diente_sierra(
        amplitud,
        armonicos,
    )

    return _amplitud_fase(an, bn)


def fourier_diente_sierra(
    frecuencia: float,
    amplitud: float,
    duracion: float,
    fs: int,
    armonicos: int,
) -> np.ndarray:
    """
    Sintetiza una onda diente de sierra mediante
    Series de Fourier.

    Parámetros
    ----------
    frecuencia : float
        Frecuencia fundamental [Hz].

    amplitud : float
        Amplitud pico.

    duracion : float
        Duración de la señal [s].

    fs : int
        Frecuencia de muestreo [Hz].

    armonicos : int
        Cantidad de armónicos utilizados.

    Retorna
    -------
    np.ndarray
        Señal sintetizada.
    """

    _validar_parametros(
        frecuencia=frecuencia,
        amplitud=amplitud,
        duracion=duracion,
        fs=fs,
        armonicos=armonicos,
    )

    a0, an, bn = coeficientes_diente_sierra(
        amplitud,
        armonicos,
    )

    return sintetizar_seno_coseno(
        frecuencia=frecuencia,
        duracion=duracion,
        fs=fs,
        a0=a0,
        an=an,
        bn=bn,
    )


def coeficientes_triangular(
    amplitud: float,
    armonicos: int,
) -> tuple[float, np.ndarray, np.ndarray]:
    """
    Calcula los coeficientes analíticos de la Serie de Fourier
    para una onda triangular simétrica.

    Parámetros
    ----------
    amplitud : float
        Amplitud pico.

    armonicos : int
        Cantidad de armónicos.

    Retorna
    -------
    tuple
        a0, an y bn.
    """
    if amplitud < 0:
        raise ValueError("La amplitud no puede ser negativa.")

    if armonicos <= 0:
        raise ValueError("La cantidad de armónicos debe ser mayor que cero.")

    a0 = 0.0

    an = np.zeros(armonicos)
    bn = np.zeros(armonicos)

    for n in range(1, armonicos + 1):
        if n % 2 == 0:
            continue

        bn[n - 1] = (8 * amplitud) / (np.pi**2 * n**2) * ((-1) ** ((n - 1) // 2))

    return a0, an, bn


def magnitud_fase_triangular(
    amplitud: float,
    armonicos: int,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Obtiene la representación en magnitud y fase
    de la Serie de Fourier de una onda triangular.
    """

    _, an, bn = coeficientes_triangular(
        amplitud,
        armonicos,
    )

    return _amplitud_fase(an, bn)


def fourier_triangular(
    frecuencia: float,
    amplitud: float,
    duracion: float,
    fs: int,
    armonicos: int,
) -> np.ndarray:
    """
    Sintetiza una onda triangular mediante
    Series de Fourier.

    Parámetros
    ----------
    frecuencia : float
        Frecuencia fundamental [Hz].

    amplitud : float
        Amplitud pico.

    duracion : float
        Duración de la señal [s].

    fs : int
        Frecuencia de muestreo [Hz].

    armonicos : int
        Cantidad de armónicos utilizados.

    Retorna
    -------
    np.ndarray
        Señal sintetizada.
    """

    _validar_parametros(
        frecuencia=frecuencia,
        amplitud=amplitud,
        duracion=duracion,
        fs=fs,
        armonicos=armonicos,
    )

    a0, an, bn = coeficientes_triangular(
        amplitud,
        armonicos,
    )

    return sintetizar_seno_coseno(
        frecuencia=frecuencia,
        duracion=duracion,
        fs=fs,
        a0=a0,
        an=an,
        bn=bn,
    )
