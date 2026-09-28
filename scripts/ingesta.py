import os
import pandas as pd
from datetime import datetime

#Rutas
DS_entrada = 'dataset/academic_survival_longitudinal.csv'
salida = '/data/raw'

def ingesta_data():
    print("Iniciando proceso de ingesta desde la Landing Zone...")
    
    #Leer los datos
    try:
        df = pd.read_csv(DS_entrada)
        print(f"Datos extraidos correctamente. Total filas: {len(df)}")
        print(f"Total de columnas detectadas: {len(df.columns)}")
    except FileNotFoundError:
        print("ERROR: No se encontro el archivo")

        return

    # Agregar metadatos (buena practica de data lakehouse)
    # No se modifica los datos originales, solo agrega una columna para saber cuando se ingirieron.
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df['ingestion_timestamp'] = fecha_actual
    
    print("Metadatos de ingesta añadidos con éxito.")

    # Guardar en raw
    ruta_raw = os.path.join(salida, 'students_raw.csv')
    df.to_csv(ruta_raw, index=False, encoding='utf-8')
    
    print(f"¡Ingesta completada! Los datos crudos se han guardado en: {ruta_raw}")

ingesta_data()