from datetime import datetime
from pathlib import Path

import pandas as pd


# ============================================================
# RUTAS DEL PROYECTO
# ============================================================

# Localiza automáticamente la raíz del proyecto a partir
# de la ubicación de este script.
RUTA_PROYECTO = Path(__file__).resolve().parent.parent

# Zona Gold / Curated del Data Lakehouse.
RUTA_GOLD = RUTA_PROYECTO / "data" / "gold" / "resumen_estudiantes"

# Carpeta donde se guardarán los resultados finales.
RUTA_SALIDA = RUTA_PROYECTO / "output" / "resultados"


# ============================================================
# COLUMNAS ESPERADAS
# ============================================================

COLUMNAS_ESPERADAS = [
    "Student_ID",
    "Promedio_GPA_Historico",
    "Promedio_Asistencia",
    "Total_Cursos_Tomados",
    "Ultimo_Semestre_Cursado",
]


# ============================================================
# VALIDACIÓN ESTRUCTURAL
# ============================================================

def validar_estructura(datos):
    """
    Comprueba que los datos provenientes de Gold tengan
    la estructura necesaria para realizar la exportación.
    """

    errores = []

    # Comprobar columnas.
    if set(datos.columns) != set(COLUMNAS_ESPERADAS):
        errores.append(
            "Las columnas de Gold no coinciden con las esperadas."
        )

    # Comprobar que existan registros.
    if datos.empty:
        errores.append("Gold no contiene registros.")

    # Comprobar valores nulos.
    cantidad_nulos = int(datos.isna().sum().sum())

    if cantidad_nulos > 0:
        errores.append(
            f"Gold contiene {cantidad_nulos} valores nulos."
        )

    # Comprobar Student_ID duplicados.
    duplicados = int(datos["Student_ID"].duplicated().sum())

    if duplicados > 0:
        errores.append(
            f"Gold contiene {duplicados} identificadores duplicados."
        )

    # Si se detectó algún problema, detener la exportación.
    if errores:
        mensaje = "\n".join(f"- {error}" for error in errores)
        raise ValueError(
            "La validación estructural de Gold falló:\n" + mensaje
        )

    print("Validación estructural: APROBADA")
    print(f"Valores nulos: {cantidad_nulos}")
    print(f"Identificadores duplicados: {duplicados}")

    return cantidad_nulos, duplicados


# ============================================================
# VALIDACIÓN DE COHERENCIA
# ============================================================

def validar_coherencia(datos):
    """
    Comprueba que los indicadores almacenados en Gold
    contengan valores coherentes.
    """

    errores = []

    # Student_ID no debe estar vacío.
    ids_vacios = (
        datos["Student_ID"]
        .astype(str)
        .str.strip()
        .eq("")
        .sum()
    )

    if ids_vacios > 0:
        errores.append(
            f"Se encontraron {ids_vacios} Student_ID vacíos."
        )

    # GPA:
    # En el dataset utilizado el GPA se trabaja en escala de 0 a 4.
    gpa_invalidos = (
        (datos["Promedio_GPA_Historico"] < 0)
        | (datos["Promedio_GPA_Historico"] > 4)
    ).sum()

    if gpa_invalidos > 0:
        errores.append(
            f"Se encontraron {gpa_invalidos} GPA fuera del rango 0-4."
        )

    # Asistencia:
    # Debe encontrarse entre 0 y 100 por ciento.
    asistencia_invalida = (
        (datos["Promedio_Asistencia"] < 0)
        | (datos["Promedio_Asistencia"] > 100)
    ).sum()

    if asistencia_invalida > 0:
        errores.append(
            f"Se encontraron {asistencia_invalida} valores de "
            "asistencia fuera del rango 0-100."
        )

    # La cantidad total de cursos no puede ser negativa.
    cursos_invalidos = (
        datos["Total_Cursos_Tomados"] < 0
    ).sum()

    if cursos_invalidos > 0:
        errores.append(
            f"Se encontraron {cursos_invalidos} valores negativos "
            "en Total_Cursos_Tomados."
        )

    # El último semestre registrado debe ser positivo.
    semestres_invalidos = (
        datos["Ultimo_Semestre_Cursado"] <= 0
    ).sum()

    if semestres_invalidos > 0:
        errores.append(
            f"Se encontraron {semestres_invalidos} valores inválidos "
            "en Ultimo_Semestre_Cursado."
        )

    if errores:
        mensaje = "\n".join(f"- {error}" for error in errores)
        raise ValueError(
            "La validación de coherencia falló:\n" + mensaje
        )

    print("Validación de coherencia: APROBADA")
    print("Student_ID vacíos: 0")
    print("GPA fuera de rango: 0")
    print("Asistencia fuera de rango: 0")
    print("Cursos con valores negativos: 0")
    print("Semestres inválidos: 0")

    return {
        "ids_vacios": int(ids_vacios),
        "gpa_invalidos": int(gpa_invalidos),
        "asistencia_invalida": int(asistencia_invalida),
        "cursos_invalidos": int(cursos_invalidos),
        "semestres_invalidos": int(semestres_invalidos),
    }


# ============================================================
# GENERACIÓN DE RESUMEN
# ============================================================

def generar_resumen(datos):
    """
    Genera indicadores generales de los datos que serán
    entregados como resultado final.

    Estos indicadores describen el conjunto exportado y no
    reemplazan las consultas analíticas realizadas en otra
    etapa del proyecto.
    """

    resumen = {
        "Estudiantes procesados": len(datos),

        "Estudiantes únicos":
            datos["Student_ID"].nunique(),

        "GPA promedio general":
            datos["Promedio_GPA_Historico"].mean(),

        "Asistencia promedio":
            datos["Promedio_Asistencia"].mean(),

        "Promedio de cursos tomados":
            datos["Total_Cursos_Tomados"].mean(),

        "Máximo de cursos acumulados":
            datos["Total_Cursos_Tomados"].max(),

        "Promedio último semestre cursado":
            datos["Ultimo_Semestre_Cursado"].mean(),
    }

    return resumen


# ============================================================
# EXPORTACIÓN
# ============================================================

def exportar_resultados(datos, resumen):
    """
    Exporta los datos de Gold y el resumen general
    a archivos CSV.
    """

    RUTA_SALIDA.mkdir(parents=True, exist_ok=True)

    archivo_estudiantes = (
        RUTA_SALIDA / "resumen_estudiantes.csv"
    )

    archivo_resumen = (
        RUTA_SALIDA / "resumen_resultados.csv"
    )

    # Exportación completa de Gold.
    datos.to_csv(
        archivo_estudiantes,
        index=False,
        encoding="utf-8-sig"
    )

    # Convierte los indicadores en una tabla de dos columnas.
    resumen_df = pd.DataFrame(
        list(resumen.items()),
        columns=["Indicador", "Resultado"]
    )

    resumen_df.to_csv(
        archivo_resumen,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"CSV principal generado: {archivo_estudiantes}")
    print(f"Resumen generado: {archivo_resumen}")

    return archivo_estudiantes, archivo_resumen


# ============================================================
# VERIFICACIÓN POST-EXPORTACIÓN
# ============================================================

def verificar_exportacion(datos_originales, archivo_csv):
    """
    Vuelve a leer el CSV generado y comprueba que la
    exportación conserve la información proveniente de Gold.
    """

    datos_exportados = pd.read_csv(
        archivo_csv,
        encoding="utf-8-sig",
        dtype={"Student_ID": "str"},
    )

    # Verificar cantidad de filas.
    filas_coinciden = (
        len(datos_originales) == len(datos_exportados)
    )

    # Verificar columnas.
    columnas_coinciden = (
        list(datos_originales.columns)
        == list(datos_exportados.columns)
    )

    if not filas_coinciden:
        raise ValueError(
            "La cantidad de filas del CSV no coincide con Gold."
        )

    if not columnas_coinciden:
        raise ValueError(
            "Las columnas del CSV no coinciden con Gold."
        )

    # Comparación completa de los valores.
    pd.testing.assert_frame_equal(
        datos_originales.reset_index(drop=True),
        datos_exportados,
        check_dtype=False,
        check_exact=False,
        rtol=1e-12,
        atol=1e-12,
    )

    print("Verificación post-exportación: APROBADA")
    print("Filas coinciden con Gold: SÍ")
    print("Columnas coinciden con Gold: SÍ")
    print("Valores coinciden con Gold: SÍ")

    return {
        "filas": filas_coinciden,
        "columnas": columnas_coinciden,
        "valores": True,
    }


# ============================================================
# REPORTE DE EJECUCIÓN
# ============================================================

def generar_reporte(
    datos,
    resumen,
    archivo_csv,
    archivo_resumen,
    cantidad_nulos,
    duplicados,
    validaciones_coherencia,
    verificacion,
):
    """
    Genera un reporte TXT que deja evidencia de la lectura,
    validación y exportación de los datos.
    """

    archivo_reporte = (
        RUTA_SALIDA / "reporte_exportacion.txt"
    )

    reporte = [
        "============================================================",
        "REPORTE DE GENERACIÓN Y EXPORTACIÓN DE RESULTADOS",
        "============================================================",
        "",
        f"Fecha de ejecución: {datetime.now():%d/%m/%Y %H:%M:%S}",
        "",
        "1. ORIGEN DE LOS DATOS",
        "------------------------------------------------------------",
        "Zona: Gold / Curated",
        "Formato de origen: Parquet",
        f"Ruta de origen: {RUTA_GOLD}",
        f"Registros recibidos: {len(datos)}",
        f"Estudiantes únicos: {datos['Student_ID'].nunique()}",
        f"Columnas recibidas: {len(datos.columns)}",
        "",
        "2. VALIDACIÓN ESTRUCTURAL",
        "------------------------------------------------------------",
        "Columnas esperadas: OK",
        "Dataset vacío: NO",
        f"Valores nulos encontrados: {cantidad_nulos}",
        f"Student_ID duplicados: {duplicados}",
        "Resultado validación estructural: APROBADO",
        "",
        "3. VALIDACIÓN DE COHERENCIA",
        "------------------------------------------------------------",
        f"Student_ID vacíos: {validaciones_coherencia['ids_vacios']}",
        f"GPA fuera del rango esperado: "
        f"{validaciones_coherencia['gpa_invalidos']}",
        f"Asistencias fuera del rango esperado: "
        f"{validaciones_coherencia['asistencia_invalida']}",
        f"Cursos con valores negativos: "
        f"{validaciones_coherencia['cursos_invalidos']}",
        f"Semestres inválidos: "
        f"{validaciones_coherencia['semestres_invalidos']}",
        "Resultado validación de coherencia: APROBADO",
        "",
        "4. RESUMEN GENERAL DE LOS DATOS",
        "------------------------------------------------------------",
        f"Estudiantes procesados: "
        f"{resumen['Estudiantes procesados']}",
        f"Estudiantes únicos: "
        f"{resumen['Estudiantes únicos']}",
        f"GPA promedio general: "
        f"{resumen['GPA promedio general']:.2f}",
        f"Asistencia promedio: "
        f"{resumen['Asistencia promedio']:.2f}%",
        f"Promedio de cursos tomados: "
        f"{resumen['Promedio de cursos tomados']:.2f}",
        f"Máximo de cursos acumulados: "
        f"{resumen['Máximo de cursos acumulados']}",
        f"Promedio último semestre cursado: "
        f"{resumen['Promedio último semestre cursado']:.2f}",
        "",
        "5. EXPORTACIÓN",
        "------------------------------------------------------------",
        "Formato principal generado: CSV",
        f"Registros exportados: {len(datos)}",
        f"Columnas exportadas: {len(datos.columns)}",
        "Codificación: UTF-8",
        "Columna de índice adicional: NO",
        f"Archivo principal: {archivo_csv}",
        f"Archivo de resumen: {archivo_resumen}",
        "",
        "6. VERIFICACIÓN POST-EXPORTACIÓN",
        "------------------------------------------------------------",
        f"Filas coinciden con Gold: "
        f"{'SÍ' if verificacion['filas'] else 'NO'}",
        f"Columnas coinciden con Gold: "
        f"{'SÍ' if verificacion['columnas'] else 'NO'}",
        f"Valores coinciden con Gold: "
        f"{'SÍ' if verificacion['valores'] else 'NO'}",
        "",
        "RESULTADO FINAL: EXPORTACIÓN EXITOSA",
        "",
        "Los datos de la zona Gold fueron validados y exportados",
        "correctamente sin modificar los archivos originales.",
        "============================================================",
    ]

    archivo_reporte.write_text(
        "\n".join(reporte) + "\n",
        encoding="utf-8"
    )

    print(f"Reporte generado: {archivo_reporte}")

    return archivo_reporte


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    print("=" * 60)
    print("GENERACIÓN Y EXPORTACIÓN DE RESULTADOS")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Comprobar existencia de Gold
    # --------------------------------------------------------

    if not RUTA_GOLD.is_dir():
        raise FileNotFoundError(
            f"No existe la carpeta Gold: {RUTA_GOLD}"
        )

    # --------------------------------------------------------
    # 2. Leer datos preparados
    # --------------------------------------------------------

    print("\n[1/6] Leyendo datos desde Gold...")

    datos = pd.read_parquet(
        RUTA_GOLD,
        engine="pyarrow"
    )

    print("Lectura de Gold completada.")
    print(f"Filas recibidas: {len(datos)}")
    print(f"Columnas: {', '.join(datos.columns)}")

    # --------------------------------------------------------
    # 3. Validación estructural
    # --------------------------------------------------------

    print("\n[2/6] Realizando validación estructural...")

    cantidad_nulos, duplicados = validar_estructura(datos)

    # --------------------------------------------------------
    # 4. Validación de coherencia
    # --------------------------------------------------------

    print("\n[3/6] Realizando validación de coherencia...")

    validaciones_coherencia = validar_coherencia(datos)

    # --------------------------------------------------------
    # 5. Generar resumen
    # --------------------------------------------------------

    print("\n[4/6] Generando resumen de resultados...")

    resumen = generar_resumen(datos)

    print("Resumen generado correctamente.")

    # --------------------------------------------------------
    # 6. Exportar
    # --------------------------------------------------------

    print("\n[5/6] Exportando resultados...")

    archivo_csv, archivo_resumen = exportar_resultados(
        datos,
        resumen
    )

    # --------------------------------------------------------
    # 7. Verificar exportación
    # --------------------------------------------------------

    print("\n[6/6] Verificando archivos exportados...")

    verificacion = verificar_exportacion(
        datos,
        archivo_csv
    )

    # --------------------------------------------------------
    # 8. Generar reporte
    # --------------------------------------------------------

    generar_reporte(
        datos,
        resumen,
        archivo_csv,
        archivo_resumen,
        cantidad_nulos,
        duplicados,
        validaciones_coherencia,
        verificacion,
    )

    print("\n" + "=" * 60)
    print("PROCESO FINALIZADO CORRECTAMENTE")
    print("=" * 60)

    print("\nArchivos generados:")
    print(f"- {archivo_csv}")
    print(f"- {archivo_resumen}")
    print(f"- {RUTA_SALIDA / 'reporte_exportacion.txt'}")

# _
if __name__ == "__main__":
    main()