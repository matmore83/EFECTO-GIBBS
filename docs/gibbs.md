# Fenómeno de Gibbs

## Descripción

El fenómeno de Gibbs es un efecto característico de las aproximaciones mediante Series de Fourier cuando se reconstruyen señales que presentan discontinuidades, como un tren de pulsos o una onda diente de sierra.

Aunque al aumentar la cantidad de armónicos la aproximación mejora en la mayor parte de la señal, en las proximidades de cada discontinuidad aparece un sobreimpulso (overshoot) y una oscilación que no desaparecen completamente. Lo que sí disminuye al incrementar el número de armónicos es el ancho de la región donde ocurre este efecto.

Este comportamiento es inherente a las Series de Fourier y no representa un error de implementación.

## Implementación en la API

La API incorpora un módulo específico (`error_analysis.py`) destinado a cuantificar el fenómeno de Gibbs mediante la comparación entre la señal ideal y la señal sintetizada por Series de Fourier.

El análisis se desarrolla en cuatro etapas:

1. **Cálculo del error absoluto**

   * Se obtiene la diferencia punto a punto entre la señal ideal y la aproximación de Fourier.

2. **Cálculo del error porcentual**

   * El error absoluto se normaliza respecto de la amplitud nominal de la señal, permitiendo expresar el resultado en porcentaje.

3. **Detección automática de discontinuidades**

   * Se localizan los saltos de la señal analizando las diferencias entre muestras consecutivas.
   * Si no se especifica un umbral, éste se calcula automáticamente como el 50 % del salto máximo detectado.

4. **Análisis local del entorno de Gibbs**

   * Una vez identificadas las discontinuidades, se extrae una ventana de muestras alrededor de cada una.
   * Sobre estas regiones se calculan las principales métricas del fenómeno.

## Métricas obtenidas

El módulo devuelve la siguiente información:

* Error absoluto.
* Error porcentual.
* Índices de las discontinuidades detectadas.
* Error localizado alrededor de cada discontinuidad.
* Error máximo producido por el fenómeno de Gibbs.
* Error promedio en el entorno de las discontinuidades.
* Cantidad total de discontinuidades presentes en la señal.

Estas métricas permiten evaluar cuantitativamente la calidad de la aproximación de Fourier y analizar cómo disminuye el error al incrementar el número de armónicos.
