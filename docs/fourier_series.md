# Síntesis mediante Series de Fourier

## Introducción

Las Series de Fourier constituyen una de las herramientas fundamentales del análisis de señales, ya que permiten representar una señal periódica como la suma de componentes senoidales de distintas frecuencias, amplitudes y fases. Este principio demuestra que cualquier función periódica que cumpla las condiciones de Dirichlet puede aproximarse mediante una combinación de funciones seno y coseno.

En este proyecto se implementa la síntesis de tres señales periódicas de interés: pulso, diente de sierra y triangular. El objetivo es analizar cómo evoluciona la aproximación al incrementar el número de armónicos y estudiar el fenómeno de Gibbs en señales con discontinuidades.

---

## Fundamento teórico

La representación trigonométrica de una Serie de Fourier está dada por

**Serie de Fourier:**

```text
x(t) = a₀/2 + Σ[aₙ cos(nω₀t) + bₙ sin(nω₀t)]
```

donde:

- a₀ representa el valor medio de la señal.
- aₙ son los coeficientes de los cosenos.
- bₙ son los coeficientes de los senos.
- ω₀ = 2πf₀ es la frecuencia angular fundamental.

Cada función periódica posee una expresión analítica distinta para sus coeficientes. En este trabajo se utilizan dichas expresiones conocidas, evitando el cálculo numérico de las integrales de Fourier y obteniendo resultados exactos.

---

## Implementación analítica

La síntesis de las señales se realiza mediante expresiones analíticas de sus coeficientes de Fourier. Esta metodología presenta diversas ventajas:

- evita errores asociados a métodos numéricos;
- reduce el costo computacional;
- simplifica la implementación;
- permite concentrar el análisis en la convergencia de la serie y en el estudio del efecto Gibbs.

Cada señal se obtiene sumando una cantidad finita de armónicos sobre la frecuencia fundamental.

---

## Cantidad de armónicos

El parámetro `armonicos` determina la cantidad de términos utilizados en la aproximación.

Para un número reducido de armónicos la señal presenta una aproximación poco precisa, observándose bordes suavizados y una diferencia apreciable respecto de la señal ideal.

Al incrementar la cantidad de armónicos, la aproximación converge progresivamente hacia la función original. Sin embargo, en las señales con discontinuidades aparece una sobreoscilación característica denominada **fenómeno de Gibbs**, cuya amplitud permanece prácticamente constante aun cuando el número de armónicos aumenta, aunque su ancho disminuye.

El análisis de este comportamiento constituye el objetivo principal del proyecto.

---

## Frecuencia de muestreo

El parámetro `fs` define la frecuencia de muestreo utilizada para representar la señal en tiempo discreto.

Una frecuencia de muestreo elevada produce una representación temporal más precisa y permite visualizar correctamente armónicos de mayor frecuencia.

La frecuencia máxima representable está determinada por el criterio de Nyquist

**Criterio de Nyquist**

```text
fNyquist = fs / 2
```

Por este motivo, la frecuencia de muestreo debe seleccionarse considerando el mayor armónico empleado en la síntesis para evitar aliasing.

---

## Script de validación

Con el propósito de verificar el correcto funcionamiento de las implementaciones se desarrolló el script `plot_validacion.py`.

Este script permite:

- seleccionar la señal a sintetizar (`pulso`, `diente` o `triangular`);
- modificar la cantidad de armónicos;
- variar la frecuencia de muestreo;
- visualizar gráficamente la señal sintetizada.

Esta herramienta facilita el estudio del proceso de convergencia de las Series de Fourier y permite observar experimentalmente la aparición del fenómeno de Gibbs al aproximar señales con discontinuidades.

---

## Objetivo

La implementación desarrollada tiene como finalidad proporcionar una herramienta didáctica para analizar el comportamiento de las Series de Fourier y comprender la influencia de la cantidad de armónicos y de la frecuencia de muestreo sobre la aproximación de señales periódicas, relacionando la teoría matemática con su implementación computacional.