"""Establece la cantidad de armónicos asociado a la diferencia entre sus valores eficaces sucesivos"""

from __future__ import annotations

import numpy as np

from app.services.fourier_series import (
    coeficientes_diente_sierra,
    coeficientes_pulso,
    coeficientes_triangular,
)

# Asociación entre el tipo de señal y la función
# que calcula sus coeficientes de Fourier.
FUNCIONES_COEFICIENTES = {
    "diente_sierra": coeficientes_diente_sierra,
    "pulso": coeficientes_pulso,
    "triangular": coeficientes_triangular,
}


def calcular_rms_coeficientes(
    a0: float,
    an: np.ndarray,
    bn: np.ndarray,
) -> float:
    """
    Calcula el valor RMS mediante
    el teorema de Parseval.
    """

    return np.sqrt((a0**2) / 4 + 0.5 * np.sum(an**2 + bn**2))


def determinar_armonicos_rms(
    tipo_senal: str,
    amplitud: float,
    tolerancia: float,
    max_armonicos: int,
) -> tuple[int, float]:
    """
    Determina la cantidad mínima de armónicos
    necesaria para satisfacer el criterio
    de convergencia del valor RMS.

    Parámetros
    ----------
    tipo_senal : str
        Tipo de señal.

        Valores permitidos:

        - "diente_sierra"
        - "pulso"
        - "triangular"

    amplitud : float
        Amplitud pico.

    tolerancia : float
        Error relativo máximo permitido.

    max_armonicos : int
        Cantidad máxima de armónicos.

    Retorna
    -------
    tuple

        armonicos
            Cantidad mínima de armónicos.

        rms
            Valor RMS alcanzado.
    """

    try:
        funcion_coeficientes = FUNCIONES_COEFICIENTES[tipo_senal]

    except KeyError as exc:
        raise ValueError(
            f"Tipo de señal no válido: '{tipo_senal}'. "
            "Valores permitidos: "
            "'diente_sierra', 'pulso', 'triangular'."
        ) from exc

    rms_anterior = 0.0

    for armonicos in range(1, max_armonicos + 1):
        a0, an, bn = funcion_coeficientes(
            amplitud=amplitud,
            armonicos=armonicos,
        )

        rms_actual = calcular_rms_coeficientes(
            a0=a0,
            an=an,
            bn=bn,
        )

        if armonicos > 1:
            error_relativo = abs(rms_actual - rms_anterior) / max(
                rms_actual,
                np.finfo(float).eps,
            )

            if error_relativo < tolerancia:
                return armonicos, rms_actual

        rms_anterior = rms_actual

    raise RuntimeError("No se alcanzó el criterio de paro.")


def calcular_serie_rms(
    tipo_senal: str,
    amplitud: float,
    max_armonicos: int,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Calcula el valor RMS acumulado para N = 1..max_armonicos, para
    visualizar la convergencia relativa a medida que se agregan armónicos.

    Parámetros
    ----------
    tipo_senal : str
        Tipo de señal ("diente_sierra", "pulso" o "triangular").

    amplitud : float
        Amplitud pico.

    max_armonicos : int
        Cantidad de puntos (armónicos) a calcular.

    Retorna
    -------
    tuple[np.ndarray, np.ndarray]

        armonicos
            N = 1..max_armonicos.

        rms
            Valor RMS acumulado en cada N.
    """

    try:
        funcion_coeficientes = FUNCIONES_COEFICIENTES[tipo_senal]

    except KeyError as exc:
        raise ValueError(
            f"Tipo de señal no válido: '{tipo_senal}'. "
            "Valores permitidos: "
            "'diente_sierra', 'pulso', 'triangular'."
        ) from exc

    armonicos = np.arange(1, max_armonicos + 1)
    rms = np.empty(max_armonicos)

    for i, n in enumerate(armonicos):
        a0, an, bn = funcion_coeficientes(amplitud=amplitud, armonicos=int(n))
        rms[i] = calcular_rms_coeficientes(a0=a0, an=an, bn=bn)

    return armonicos, rms
