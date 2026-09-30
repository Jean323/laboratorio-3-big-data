import os
import pandas as pd

#Variables con la ubicación del archivo
RUTA_ENTRADA = os.path.join("data", "raw", "students_raw.csv")
RUTA_SALIDA = os.path.join("data", "processed", "students_limpios.csv")
RUTA_LOG = os.path.join("data", "processed", "reporte_calidad.txt")

#Lee los datos iniciales
print("INICIANDO PROCESO DE LIMPIEZA DE DATOS")
dataframe = pd.read_csv(RUTA_ENTRADA)
registros_iniciales = len(dataframe)
print(f"Registros iniciales cargados desde /data/raw: {registros_iniciales}")

#Elimina las filas duplicadas
dataframe = dataframe.drop_duplicates()
registros_sin_duplicar = len(dataframe)
duplicados_eliminados = registros_iniciales - registros_sin_duplicar
print(f"Filas duplicadas eliminadas: {duplicados_eliminados}")

#Elimina las filas con datos nulos
columnas_clave = ["Student_ID", "Semester", "Sem_GPA"]
dataframe = dataframe.dropna(subset=columnas_clave)
registros_sin_nulos = len(dataframe)
nulos_eliminados = registros_sin_duplicar - registros_sin_nulos
print(f"Filas con nulos eliminadas: {nulos_eliminados}")

#Elimina las filas datos inválidos
dataframe = dataframe[(dataframe["Attendance"] >= 0) & (dataframe["Attendance"] <= 100) & (dataframe["Course_Load"] > 0)]
registros_finales = len(dataframe)
invalidos_eliminados = registros_sin_nulos - registros_finales
print(f"Filas con asistencia o carga académica inválidas eliminadas: {invalidos_eliminados}")

os.makedirs(os.path.dirname(RUTA_SALIDA), exist_ok=True)
dataframe.to_csv(RUTA_SALIDA, index=False)
print(f"Datos limpios guardados exitosamente en: {RUTA_SALIDA}")
with open(RUTA_LOG, "w") as log:
    log.write("REPORTE DE CALIDAD DE LOS DATOS\n")
    log.write(f"Total de registros recibidos: {registros_iniciales}\n")
    log.write(f"Duplicados removidos: {duplicados_eliminados}\n")
    log.write(f"Registros con campos nulos eliminados: {nulos_eliminados}\n")
    log.write(f"Registros con campos inconsistentes removidos: {invalidos_eliminados}\n")
    log.write(f"Registros limpios finales: {registros_finales}\n")
print(f"Reporte de calidad generado en: {RUTA_LOG}")
print("PROCESO FINALIZADO CON ÉXITO")