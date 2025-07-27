# ⬇️ INSTALAR LIBRERÍAS NECESARIAS
!pip install --quiet gspread gspread-formatting pandas
# 📚 IMPORTACIONES
import gspread
from google.colab import auth
from google.auth import default
import os
import pandas as pd
import math
import copy
from itertools import zip_longest
from collections import defaultdict

# 🔐 AUTENTICACIÓN
auth.authenticate_user()
creds, _ = default()
gc = gspread.authorize(creds)

# 📄 ABRIR PLANILLA
sheet_url = os.environ.get("SHEET_URL")
if not sheet_url:
    sheet_url = input("🔗 Ingresá la URL del Google Sheet: ").strip()
spreadsheet = gc.open_by_url(sheet_url)
hoja_escuelas = spreadsheet.worksheet("Estudiantes acreditados")
hoja_grupos = spreadsheet.worksheet("Asignación de Elementos y Coordinadores")

# 📥 LEER ESCUELAS
escuelas_data = hoja_escuelas.get_all_values()[1:]
escuelas = []
for row in escuelas_data:
    try:
        nombre = row[0].strip()
        cantidad = int(row[1])
        escuelas.append((nombre, cantidad))
    except:
        continue

totales_originales = dict(escuelas)
escuelas.sort(key=lambda x: x[1], reverse=True)

# 📥 LEER GRUPOS
grupos_data = hoja_grupos.get_all_values()[1:]
grupos = []
for row in grupos_data:
    try:
        nombre = row[0]
        capacidad = int(row[5])
        grupos.append({
            "nombre": nombre,
            "capacidad_max": capacidad,
            "capacidad_usada": 0,
            "asignaciones": {}
        })
    except:
        continue

# 📊 DATOS GENERALES
total_estudiantes = sum(c for _, c in escuelas)
capacidad_total = sum(g["capacidad_max"] for g in grupos)

# 🔣 FUNCIÓN ORDENAMIENTO POR OCIOSIDAD PROMEDIO
def ordenar_por_ociosidad_promedio(grupos, total_estudiantes):
    capacidad_total = sum(g["capacidad_max"] for g in grupos)
    ociosidad_promedio = (capacidad_total - total_estudiantes) / len(grupos)
    return sorted(
        grupos,
        key=lambda g: abs((g["capacidad_max"] - g["capacidad_usada"]) - ociosidad_promedio)
    )

#PARTE 2

# 🔁 FUNCIONES DE DISTRIBUCIÓN

def distribuir_por_equilibrio():
    pendientes = []
    for escuela, cantidad_total in escuelas:
        cantidad_restante = cantidad_total
        while cantidad_restante > 0:
            grupo_asignado = None
            for grupo in ordenar_por_ociosidad_promedio(grupos, total_estudiantes):
                libre = grupo["capacidad_max"] - grupo["capacidad_usada"]
                if libre >= cantidad_restante:
                    grupo["asignaciones"][escuela] = grupo["asignaciones"].get(escuela, 0) + cantidad_restante
                    grupo["capacidad_usada"] += cantidad_restante
                    grupo_asignado = grupo
                    cantidad_restante = 0
                    break
            if grupo_asignado is None:
                if cantidad_restante <= 10:
                    pendientes.append((escuela, cantidad_restante))
                    cantidad_restante = 0
                else:
                    pendientes.append((escuela, 10))
                    cantidad_restante -= 10

    a_reintentar = pendientes.copy()
    pendientes.clear()
    for escuela, cantidad in a_reintentar:
        grupo_asignado = None
        for grupo in ordenar_por_ociosidad_promedio(grupos, total_estudiantes):
            libre = grupo["capacidad_max"] - grupo["capacidad_usada"]
            if libre >= cantidad:
                grupo["asignaciones"][escuela] = grupo["asignaciones"].get(escuela, 0) + cantidad
                grupo["capacidad_usada"] += cantidad
                grupo_asignado = grupo
                break
        if grupo_asignado is None:
            pendientes.append((escuela, cantidad))
    return pendientes

def distribuir_por_saturacion():
    pendientes = []
    for escuela, cantidad in escuelas:
        restantes = cantidad
        while restantes > 0:
            grupos_disponibles = sorted(grupos, key=lambda g: g["capacidad_max"] - g["capacidad_usada"], reverse=True)
            for grupo in grupos_disponibles:
                libre = grupo["capacidad_max"] - grupo["capacidad_usada"]
                if libre == 0:
                    continue
                asignar = min(restantes, libre)
                grupo["asignaciones"][escuela] = grupo["asignaciones"].get(escuela, 0) + asignar
                grupo["capacidad_usada"] += asignar
                restantes -= asignar
                if restantes == 0:
                    break
            if restantes > 0:
                pendientes.append((escuela, restantes))
                break
    return pendientes

# 🔀 SELECCIONAR ESTRATEGIA
if total_estudiantes <= capacidad_total:
    algoritmo_usado = "equilibrio"
    pendientes = distribuir_por_equilibrio()
else:
    algoritmo_usado = "saturación"
    pendientes = distribuir_por_saturacion()

# ✅ REFINAMIENTO: MOVER BLOQUES DE 10 SIN SUBDIVIDIR ESCUELAS

def suma_cuadrados(grs):
    return sum((g["capacidad_max"] - sum(g["asignaciones"].values())) ** 2 for g in grs)

def grupos_por_escuela(grupos):
    mapeo = {}
    for idx, g in enumerate(grupos):
        for esc in g["asignaciones"]:
            mapeo.setdefault(esc, set()).add(idx)
    return mapeo

grupos_opt = copy.deepcopy(grupos)
bloques_movidos = 0
mejoro = True
while mejoro:
    mejoro = False
    mapeo_escuelas = grupos_por_escuela(grupos_opt)
    for i, g1 in enumerate(grupos_opt):
        for j, g2 in enumerate(grupos_opt):
            if i == j:
                continue
            for escuela in list(g1["asignaciones"].keys()):
                if escuela in g2["asignaciones"]:
                    continue
                if len(mapeo_escuelas[escuela]) > 1:
                    continue
                cantidad = g1["asignaciones"][escuela]
                libre_en_g2 = g2["capacidad_max"] - sum(g2["asignaciones"].values())
                max_bloques = cantidad // 10
                for bloques in range(max_bloques, 0, -1):
                    mover = bloques * 10
                    if libre_en_g2 < mover:
                        continue
                    g_tmp = copy.deepcopy(grupos_opt)
                    g_tmp[i]["asignaciones"][escuela] -= mover
                    if g_tmp[i]["asignaciones"][escuela] == 0:
                        del g_tmp[i]["asignaciones"][escuela]
                    g_tmp[j]["asignaciones"][escuela] = g_tmp[j]["asignaciones"].get(escuela, 0) + mover
                    if suma_cuadrados(g_tmp) < suma_cuadrados(grupos_opt):
                        grupos_opt = g_tmp
                        bloques_movidos += bloques
                        mejoro = True
                        break
                if mejoro:
                    break
            if mejoro:
                break
        if mejoro:
            break

grupos = grupos_opt

#PARTE 3
# 📋 TABLA FINAL DE RESULTADO
tabla_final = []
for g in grupos:
    grupo_fila = {
        "Grupo": g["nombre"],
        "Capacidad máxima": g["capacidad_max"],
        "Capacidad ocupada": sum(g["asignaciones"].values()),
        "Capacidad ociosa": g["capacidad_max"] - sum(g["asignaciones"].values())
    }
    for idx, (esc, cant) in enumerate(g["asignaciones"].items(), 1):
        grupo_fila[f"Escuela {idx}"] = esc
        grupo_fila[f"Cantidad {idx}"] = cant
    tabla_final.append(grupo_fila)

# 📊 RESUMEN ESCUELAS + ASIGNACIONES TEXTO
resumen = {}
no_asignados = {}
distribuciones = {}
for g in grupos:
    for esc, cant in g["asignaciones"].items():
        resumen[esc] = resumen.get(esc, 0) + cant
        distribuciones.setdefault(esc, []).append(f"{g['nombre']}: {cant}")
for esc, cant in pendientes:
    no_asignados[esc] = no_asignados.get(esc, 0) + cant

# ➕ AGRUPAR EXCEDENTES EN GRUPOS EXTRA DE A 20
excedentes = defaultdict(int)
for escuela, cantidad in pendientes:
    excedentes[escuela] += cantidad

grupo_extra_filas = []
grupos_extra_nombre = []
bloque_actual = []
contador_extras = 1

for escuela, total in excedentes.items():
    while total > 0:
        asignar = min(total, 20 - sum(x[1] for x in bloque_actual))
        bloque_actual.append((escuela, asignar))
        total -= asignar
        if sum(x[1] for x in bloque_actual) == 20 or total == 0:
            nombre = f"GE{contador_extras}"
            grupos_extra_nombre.append(nombre)
            fila = {
                "Grupo": nombre,
                "Capacidad máxima": 20,
                "Capacidad ocupada": sum(x[1] for x in bloque_actual),
                "Capacidad ociosa": 20 - sum(x[1] for x in bloque_actual)
            }
            for idx, (esc, cant) in enumerate(bloque_actual, 1):
                fila[f"Escuela {idx}"] = esc
                fila[f"Cantidad {idx}"] = cant
                resumen[esc] = resumen.get(esc, 0) + cant
                distribuciones.setdefault(esc, []).append(f"{nombre}: {cant}")
            grupo_extra_filas.append(fila)
            bloque_actual = []
            contador_extras += 1

tabla_final.extend(grupo_extra_filas)

# 📋 GENERAR RESUMEN FINAL
resumen_final = [["Escuela", "Total acreditado", "Total asignado", "No asignado", "Asignaciones"]]
for esc in sorted(set(totales_originales) | set(resumen)):
    total_acreditado = totales_originales.get(esc, 0)
    total_asignado = resumen.get(esc, 0)
    no_asignado = max(0, total_acreditado - total_asignado)
    resumen_final.append([
        esc,
        total_acreditado,
        total_asignado,
        no_asignado,
        ", ".join(distribuciones.get(esc, []))
    ])

df_resultado = pd.DataFrame(tabla_final).fillna("")
df_resumen = pd.DataFrame(resumen_final[1:], columns=resumen_final[0])

# ✍️ EXPORTAR A GOOGLE SHEETS
try:
    hoja_nueva = spreadsheet.worksheet("Distribución python")
    spreadsheet.del_worksheet(hoja_nueva)
except:
    pass
hoja_nueva = spreadsheet.add_worksheet("Distribución python", rows=300, cols=30)

hoja_nueva.update("A1", [df_resultado.columns.tolist()] + df_resultado.values.tolist())
hoja_nueva.update(f"A{len(df_resultado)+3}", [["Resumen por escuela"]] + [df_resumen.columns.tolist()] + df_resumen.values.tolist())

# 🖨️ RESUMEN EN CONSOLA
print("\n🧾 Resumen de ejecución:")
print(f"🔢 Total estudiantes acreditados: {total_estudiantes}")
print(f"📦 Capacidad total disponible:     {capacidad_total}")
print(f"⚙️  Algoritmo utilizado:            {algoritmo_usado}")
print(f"🔁 Bloques de 10 movidos:          {bloques_movidos}")
if grupo_extra_filas:
    print(f"➕ Grupos extra creados:            {', '.join(grupos_extra_nombre)}")
else:
    print("✅ No se necesitaron grupos extra.")
