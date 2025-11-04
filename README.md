# 🖌️ Sketch Tool – Aplicación de Procesamiento de Imágenes con OpenCV y Tkinter

**Sketch Tool** es una herramienta interactiva desarrollada en Python que permite realizar múltiples operaciones de procesamiento y análisis de imágenes mediante una interfaz gráfica sencilla e intuitiva.  
Combina el poder de **OpenCV**, **NumPy** y **Tkinter** para ofrecer funciones como extracción de paleta de colores, selección de regiones, modificación de tonos HSV, detección de contornos, alteración de colores, combinación de imágenes y detección de figuras geométricas.

---

## 🚀 Características principales

- 🖼️ **Carga y visualización** de imágenes en formato `.jpg`, `.png`, `.jpeg`, `.bmp`.
- 🎨 **Extracción de paleta de colores** usando *K-Means clustering*.
- ✂️ **Selección interactiva de regiones (ROI)** sobre la imagen.
- 🌈 **Modificación de Tono, Saturación y Brillo (HSV)** con deslizadores en tiempo real.
- 🔍 **Detección y dibujo de contornos** sobre figuras en la imagen.
- 🧩 **Combinación de imágenes** (suma o resta) con escalado automático.
- 🎯 **Alteración de rangos de color** para editar zonas específicas.
- 🔳 **Cierre de contornos** y cálculo de áreas sólidas mediante operaciones morfológicas.
- 📐 **Dibujo automático de figuras geométricas** (triángulos, cuadrados, círculos, etc.).
- ↩️ **Historial de cambios** con funciones *Deshacer / Rehacer*.
- 💾 **Guardado y exportación** de resultados y paletas generadas.

---

## 🧠 Tecnologías utilizadas

- [Python 3.8+](https://www.python.org/)
- [OpenCV](https://opencv.org/)
- [NumPy](https://numpy.org/)
- [Tkinter](https://docs.python.org/3/library/tkinter.html)
- [Pillow (PIL)](https://pillow.readthedocs.io/en/stable/)

---

## 🛠️ Instalación

Clona este repositorio y entra en la carpeta del proyecto:

```bash
git clone https://github.com/tuusuario/sketch-tool.git
cd AyudaDibujo
```

Crea un entorno virtual (opcional pero recomendado):

```bash
python -m venv venv
source venv/bin/activate   # En macOS/Linux
venv\Scripts\activate      # En Windows
```

Instala las dependencias necesarias:

```bash
pip install opencv-python numpy pillow
```

Ejecucion:

```bash
python main.py
```
