# DistribuyeSemQuim
Script para distribuir los estudiantes en grupos para la semana de la química
# Distribución Óptima de Estudiantes — Semana de la Química 🧪

Este script en Google Colab permite distribuir estudiantes acreditados por escuela en distintos grupos de laboratorio para una jornada académica, respetando criterios de capacidad, equidad y agrupamiento.

## 🚀 Funcionalidades principales

- ✅ **Distribución automática** de estudiantes en grupos, respetando capacidad máxima por grupo.
- ⚖️ Selección dinámica del algoritmo según el contexto:
  - **Algoritmo de equilibrio** si hay más lugar que estudiantes.
  - **Algoritmo de saturación** si hay más estudiantes que capacidad.
- 🔁 **Refinamiento final** por bloques de 10 estudiantes para minimizar la **suma de cuadrados de capacidad ociosa**, sin subdividir escuelas innecesariamente.
- ➕ Agrupamiento de **excedentes en grupos extra (GE1, GE2, …)** de hasta 20 personas.
- 📊 **Resumen detallado por escuela** con:
  - Total acreditado
  - Total asignado
  - No asignado
  - Grupos en los que fue distribuida la escuela

## 📤 Exportación

El resultado se exporta automáticamente a tu Google Sheet:

- `Distribución python`: distribución final por grupo.
- `Resumen por escuela`: debajo de la tabla principal.
- Consola de Colab: imprime el resumen general de ejecución.

## 📈 Criterios aplicados

1. Ningún grupo puede superar su capacidad máxima.
2. Si hay lugar de sobra, se busca una distribución equitativa (capacidad ociosa promedio similar).
3. Si hay sobrecupo, se llenan todos los grupos al máximo.
4. Las escuelas se agrupan en la menor cantidad de grupos posible (fragmentación limitada).
5. El refinamiento solo redistribuye bloques de 10 estudiantes **sin subdividir más a las escuelas**.

## 📚 Requisitos

- Cuenta de Google con acceso al Google Sheet que contiene:
  - Una hoja `"Estudiantes acreditados"` con columnas: `Escuela`, `Cantidad`.
  - Una hoja `"Asignación de Elementos y Coordinadores"` con:
    - Nombre de grupo (columna A)
    - Capacidad máxima (columna F)

## 🛠 Cómo usar

1. Abrí el notebook en Google Colab.
2. Autenticá tu cuenta de Google.
3. Indicá la URL de tu Google Sheet. Podés definir la variable de entorno
   `SHEET_URL` antes de ejecutar el script o ingresarla manualmente cuando se
   te solicite. Si querés fijarla de antemano, ejecutá en una celda:

   ```python
   import os
   os.environ["SHEET_URL"] = "https://mi-sheet.google.com/..."
   ```
4. Ejecutá todas las celdas.
5. Revisá la hoja `Distribución python` con los resultados y el resumen.

## 🧾 Ejemplo de resumen en consola

🧾 Resumen de ejecución:
🔢 Total estudiantes acreditados: 314
📦 Capacidad total disponible: 300
⚙️ Algoritmo utilizado: saturación
🔁 Bloques de 10 movidos: 3
➕ Grupos extra creados: GE1, GE2


## 📜 Licencia

MIT — Usalo, adaptalo y compartilo libremente.
