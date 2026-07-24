# Error Analysis

## Introducción

El fenómeno de Gibbs produce una sobreoscilación característica en las aproximaciones mediante Series de Fourier cuando la señal original presenta discontinuidades. Aunque el número de armónicos aumente, la amplitud relativa de dicha sobreoscilación no desaparece, sino que se concentra en una región cada vez más reducida alrededor del salto.

Con el objetivo de cuantificar este comportamiento, se implementó el módulo `error_analysis.py`, encargado de comparar la señal ideal con la señal sintetizada mediante Series de Fourier y calcular el error porcentual en el entorno de las discontinuidades.

---

# Diseño del módulo

El módulo fue desarrollado de manera modular, dividiendo el problema en funciones independientes. Cada una cumple una única responsabilidad, facilitando la reutilización del código y la construcción de pruebas unitarias.

Las funciones implementadas son:

- `error_absoluto()`
- `error_porcentual()`
- `obtener_discontinuidades()`
- `error_entorno()`
- `error_analysis()`

Esta organización permite mantener un diseño claro y desacoplado, donde cada función puede validarse individualmente.

---

# Cálculo del error absoluto

La función `error_absoluto()` calcula la diferencia absoluta entre la señal ideal y la señal sintetizada.

Matemáticamente,

$$
e(n)=\left|x_{ideal}(n)-x_{Fourier}(n)\right|
$$

donde:

- $x_{ideal}(n)$ representa la señal original.
- $x_{Fourier}(n)$ corresponde a la aproximación obtenida mediante Series de Fourier.

El resultado es un vector que contiene el error para cada muestra temporal.
---

# Cálculo del error porcentual

La función `error_porcentual()` expresa el error absoluto como un porcentaje de la amplitud nominal de la señal.

El error porcentual se calcula mediante

$$
e_{\%}(n)=
\frac{\left|x_{ideal}(n)-x_{Fourier}(n)\right|}
{A}\times100
$$

donde:

- $A$ es la amplitud nominal de la señal.

De esta forma es posible comparar señales distintas utilizando una misma métrica.

---

# Detección de discontinuidades

El fenómeno de Gibbs únicamente aparece en las discontinuidades de la señal.

Para detectar automáticamente las discontinuidades se calcula la diferencia entre muestras consecutivas:

$$
\Delta x(n)=\left|x(n+1)-x(n)\right|
$$

Aquellos puntos cuya diferencia supera un umbral preestablecido son considerados discontinuidades.

Este procedimiento evita indicar manualmente la posición de cada salto y permite que el algoritmo funcione para distintas señales periódicas.

---

# Extracción del entorno de análisis

Una vez detectadas las discontinuidades, no resulta necesario estudiar toda la señal, sino únicamente una pequeña región alrededor de cada salto.

Para ello se implementó la función `error_entorno()`, la cual extrae una ventana de muestras alrededor de cada discontinuidad.

Este procedimiento concentra el análisis únicamente sobre la zona donde aparece el fenómeno de Gibbs.

---

# Función principal

Finalmente, la función `error_analysis()` integra todas las etapas anteriores.

Su funcionamiento consiste en:

1. Calcular el error absoluto.
2. Obtener el error porcentual.
3. Detectar automáticamente las discontinuidades.
4. Extraer el entorno de análisis.
5. Calcular las métricas principales.

Como resultado devuelve un diccionario con:

- Error absoluto.
- Error porcentual.
- Índices de discontinuidad.
- Error localizado en el entorno.
- Error máximo.
- Error promedio.

Esta información constituye la base para el estudio cuantitativo del fenómeno de Gibbs y será utilizada posteriormente para comparar distintas aproximaciones mediante Series de Fourier.

---

# Ventajas del diseño

La implementación propuesta presenta las siguientes ventajas:

- Código modular y reutilizable.
- Separación de responsabilidades.
- Fácil mantenimiento.
- Posibilidad de realizar pruebas unitarias sobre cada función.
- Integración sencilla con los módulos de síntesis y análisis del proyecto.

Este enfoque sigue la misma filosofía utilizada durante el desarrollo del resto de la API, permitiendo mantener una arquitectura consistente y escalable.