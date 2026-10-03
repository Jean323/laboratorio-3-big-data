# Transformacion  de Datos: Silver a Gold
#Encargado: Charloth Salgado
#Se tomaran los datos limpios del archivo students_limpios.csv y aplicaremos reglas utilizando PySpark. 
# El objetivo es generar tablas optimizadas que seran guardadas en formato Parquet
#para ser consultados por parte del equipo de analisis.
# 
#NOTA: se adjunta un archivo transformacion.ipynb , donde se puede ejecutar el codigo por bloques con una breve descripcion (se necesita jupyter notebook)

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, sum, max, when

spark =SparkSession.builder.appName("Transformacion_zona_gold").getOrCreate() 
print("sesion iniciada - Spark")

print("Leyendo datos...")

entrada= "../data/processed/students_limpios.csv"
limpio= spark.read.csv(entrada, header=True, inferSchema=True)
print("Datos leidos correctamente")

limpio.printSchema()
limpio.show(5)

print("Aplicando Transformaciones...")
df_trans = limpio.withColumn(
    "Estado_Riesgo",
    when(col("Sem_GPA") < 2.0, "En Riesgo").otherwise("Estable")
)

df_gold = df_trans.groupBy("Student_ID").agg(
    avg("Sem_GPA").alias("Promedio_GPA_Historico"),
    avg("Attendance").alias("Promedio_Asistencia"),
    sum("Course_Load").alias("Total_Cursos_Tomados"),
    max("Semester").alias("Ultimo_Semestre_Cursado")
)
print("-----Transformaciones Exitosas-----")

df_gold.show(10)

salida = "../data/gold/resumen_estudiantes"
df_gold.write.mode("overwrite").parquet(salida)
print(" Datos guardados en archivo Parquet resumen_estudiantes")

df_prueba = spark.read.parquet(salida)
print("Lectura de Parquet exitosa. Mostrando datos:")
df_prueba.show(5)