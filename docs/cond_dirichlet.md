Coeficientes de Fourier de una onda diente de sierra

Calcula los coeficientes analíticos a0, an y bn correspondientes
a la Serie de Fourier de una onda diente de sierra.

description=(
    "Este endpoint calcula los coeficientes analíticos de la "
    "Serie de Fourier para una onda diente de sierra periódica. "
    "Se devuelve el coeficiente constante a0, los coeficientes "
    "del coseno (an) y los coeficientes del seno (bn) hasta la "
    "cantidad de armónicos solicitada."
)

# Condiciones de Dirichlet

Las condiciones de Dirichlet establecen los requisitos suficientes para que una señal periódica pueda representarse mediante una Serie de Fourier.

Una señal cumple las condiciones de Dirichlet si:

1. Posee un número finito de discontinuidades en un período.

2. Posee un número finito de máximos y mínimos en un período.

3. Es absolutamente integrable en un período.

Cuando estas condiciones se satisfacen, la Serie de Fourier converge:

- Al valor de la señal en los puntos donde es continua.
- Al promedio de los límites laterales en los puntos de discontinuidad.

## Aplicación en este proyecto

Las señales implementadas en esta API (pulso, diente de sierra y triangular) cumplen las condiciones de Dirichlet, por lo que pueden representarse mediante Series de Fourier.

El cálculo de los coeficientes analíticos permite reconstruir cada señal utilizando un número finito de armónicos.