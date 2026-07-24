# Carga de archivos de audio

## Objetivo

El módulo `import_service.py` permite importar archivos de audio para ser utilizados como señales de entrada dentro de la aplicación.

Su función principal es convertir un archivo almacenado en disco en un vector de muestras digitales junto con su frecuencia de muestreo, permitiendo posteriormente aplicar procesamiento digital de señales, análisis espectral o síntesis mediante Series de Fourier.

---

# Fundamento teórico

Una señal de audio digital puede representarse como una secuencia discreta de muestras:

\[
x[n]
\]

obtenidas mediante el proceso de muestreo de una señal analógica.

Cada archivo de audio almacena principalmente dos tipos de información:

- Las muestras de amplitud de la señal.
- La frecuencia de muestreo.

La frecuencia de muestreo se expresa como

\[
f_s
\]

y representa la cantidad de muestras registradas por segundo.

Por ejemplo,

- 44100 Hz
- 48000 Hz
- 96000 Hz

---

# Lectura del archivo

La lectura del audio se realiza utilizando la biblioteca **SoundFile**, que permite acceder a distintos formatos de audio sin necesidad de modificar el algoritmo de procesamiento.

Durante la carga se obtiene:

- La señal de audio.
- La frecuencia de muestreo.

El módulo devuelve ambos valores mediante:

```python
senal, fs = cargar_audio(...)
```

---

# Conversión a mono

Muchos archivos de audio poseen más de un canal.

Por ejemplo:

- Mono
- Estéreo
- Multicanal

Para simplificar el procesamiento, el módulo convierte automáticamente cualquier señal estéreo en una señal monofónica mediante el promedio de ambos canales.

Matemáticamente,

$$
x_{mono}[n] =
\frac{x_L[n] + x_R[n]}{2}
$$

donde

- $x_L[n]$ corresponde al canal izquierdo.
- $x_R[n]$ corresponde al canal derecho.

Esta operación conserva la información general de la señal y simplifica los algoritmos posteriores.

---

# Normalización

Dependiendo del formato de almacenamiento, la amplitud del audio puede encontrarse en diferentes escalas.

Para evitar diferencias entre archivos, todas las señales se normalizan dividiendo por su valor máximo absoluto.

La normalización se realiza mediante

$$
x_{norm}[n] =
\frac{x[n]}
{\max\left(|x[n]|\right)}
$$

De esta manera, la amplitud queda comprendida entre

$$
-1 \le x_{norm}[n] \le 1
$$

permitiendo trabajar con una escala uniforme para todos los archivos.

---

# Validaciones implementadas

Antes de cargar el archivo se realizan distintas verificaciones:

- Existencia del archivo.
- Formato soportado.
- Correcta lectura del contenido.

En caso de detectarse algún problema se generan excepciones descriptivas para facilitar el diagnóstico del error.

---

# Formatos soportados

El módulo admite los formatos de audio implementados por **SoundFile**, entre ellos:

- WAV
- FLAC
- AIFF
- OGG

La validación de la extensión evita intentar abrir archivos incompatibles.

---

# Salida del módulo

La función devuelve una tupla formada por:

- Señal de audio normalizada (`np.ndarray`).
- Frecuencia de muestreo (`int`).

Esta información será utilizada posteriormente por los módulos encargados de:

- Síntesis mediante Series de Fourier.
- Transformada Rápida de Fourier (FFT).
- Análisis del fenómeno de Gibbs.
- Visualización temporal y espectral.