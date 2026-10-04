from pyspark.sql import SparkSession

# cargar datos del dataset
spark = SparkSession.builder.appName("Consulta Gold").getOrCreate()
print("Conectando a los datos...")
ruta_gold = "../data/gold/resumen_estudiantes"
df_gold = spark.read.parquet(ruta_gold)
df_gold.createOrReplaceTempView("estudiantes")

# consulta 1: Los 5 alumnos con mejores notas 
print("\n--- 1. Top 5 mejores promedios ---")
spark.sql("""
    SELECT Student_ID, Promedio_GPA_Historico, Promedio_Asistencia
    FROM estudiantes 
    ORDER BY Promedio_GPA_Historico DESC 
    LIMIT 5
""").show()

# Consulta 2: Los 10 alumnos con peor asistencia 
print("\n--- 2. Alumnos con peor asistencia ---")
spark.sql("""
    SELECT Student_ID, Promedio_Asistencia 
    FROM estudiantes 
    ORDER BY Promedio_Asistencia ASC
    LIMIT 10
""").show()

# consulta 3: Alumnos de primer año con notas criticas
print("\n--- 3. Alumnos de 1er semestre en riesgo academico ---")
spark.sql("""
    SELECT Student_ID, Promedio_GPA_Historico
    FROM estudiantes
    WHERE Ultimo_Semestre_Cursado = 1 AND Promedio_GPA_Historico < 2.0
    ORDER BY Promedio_GPA_Historico ASC
    LIMIT 10
""").show()

# Consulta 4: Los 10 alumnos con mas cursos tomados
print("\n--- 4. Alumnos con mayor carga academica ---")
spark.sql("""
    SELECT Student_ID, Total_Cursos_Tomados
    FROM estudiantes
    ORDER BY Total_Cursos_Tomados DESC
    LIMIT 10
""").show()

spark.stop()