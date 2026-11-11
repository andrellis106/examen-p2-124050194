# Examen Segundo Parcial: Pipeline de datos contenerizado

**Materia:** Manejo Masivo de Datos (Big Data)
**Matrícula:** 124050194
**Pregunta asignada (último dígito 4):** unidades vendidas por **método de pago y día de la semana**.

## Arquitectura

Tres servicios en una red de Docker Compose (`pipeline`):


| Servicio | Imagen | Función |
|---|---|---|
| `hadoop` | Debian + OpenJDK 11 + Hadoop 3.3.6 (standalone) + OpenSSH | Procesa el CSV con Hadoop Streaming |
| `db` | PostgreSQL 16 | Guarda los resultados (volumen nombrado `pgdata`) |
| `api` | Python 3.12 + Flask | Expone los resultados y un CRUD |

## Cómo reproducirlo

1. **Generar el dataset** (fuera del repositorio):
   ```
   python generar_dataset.py 124050194
   ```
   Crea `ventas_124050194.csv` (~350 MB, 5 millones de registros). El CSV no se sube al repo.
2. **Configurar variables:** copiar `.env.example` a `.env`, poner una contraseña y ajustar `DATASET_DIR` a la carpeta donde está el CSV.
3. **Levantar el ambiente:**
   ```
   docker compose up -d --build
   ```
4. **Correr el job de MapReduce:**
   ```
   docker compose exec -u hduser hadoop bash /app/mapreduce/run_job.sh
   ```
5. **Cargar los resultados a la base de datos:**
   ```
   docker compose exec api python /scripts/cargar_resultados.py
   ```
6. **Consultar la API:** `http://localhost:5000/resultados`

## Evidencias

| Parte | Evidencia |
|---|---|
|  Hadoop | ![hadoop version](evidencias/01-hadoop-version.png) |
|  SSH sin contraseña (`ssh localhost`) | [ver evidencia](evidencias/02-ssh-localhost.txt) |
|  SSH de `api` a `hadoop` | [ver evidencia](evidencias/03-ssh-api-hadoop.txt) |
|  Salida del job | [ver evidencia](evidencias/04-salida-job.txt) |
|  Comparativa de resultados | [ver evidencia](evidencias/05-comparativa.txt) |
|  Respuesta de la API | [ver evidencia](evidencias/06-api-resultados.txt) |
|  Persistencia tras `down` y `up` | [ver evidencia](evidencias/07-persistencia.txt) |
|  Endpoint de escritura | [ver evidencia](evidencias/08-api-escritura.txt) |

## Endpoints de la API

|  Ruta | Descripción |
|---|---|---|
|`/resultados` | Todos los registros |
| `/resultados/<metodo_pago>` | Filtra por método de pago (opcional `?dia=Lunes`) |
|  `/resultados` | Crea un registro |
|  `/resultados/<id>` | Actualiza las unidades |
|  `/resultados/<id>` | Elimina un registro |

## Comparativa de rendimiento

| Método | Tiempo real |
|---|---|
| Hadoop Streaming (standalone) | 21.241 s |
| Script secuencial en Python | 11.426 s |

Los resultados de ambos son idénticos (verificado con `diff`).

El script secuencial tardó 11.426 s y el job de Hadoop Streaming 21.241 s. En este escenario el secuencial fue más rápido porque el archivo (~350 MB) cabe cómodamente en una sola máquina y el problema se resuelve con un único recorrido y 28 contadores en memoria. Hadoop paga costos fijos: arrancar la JVM, planificar las tareas, lanzar un proceso Python por cada map y, sobre todo, escribir y ordenar los datos intermedios en disco (Spilled Records = 10,000,000). En modo standalone además no hay varios nodos que repartan el trabajo. MapReduce conviene cuando los datos superan lo que una sola máquina puede procesar o almacenar y existe un clúster con HDFS que reparta el cómputo.

## Seguridad

- El CSV y el archivo `.env` están en `.gitignore`; el repo solo incluye `.env.example`.
- SSH solo acepta llaves (sin contraseñas); las llaves se generan al arrancar el contenedor, no en la imagen.

- 
##  Teoría

**1. Modos de Hadoop.** En el modo standalone Hadoop corre como un solo programa en una sola máquina y lee los archivos normales del disco; es el que usé en este proyecto. En el pseudo-distribuido también es una sola máquina, pero se levantan por separado todos los servicios de Hadoop (NameNode, DataNode, etc.), como si fuera un clúster pequeño. En el totalmente distribuido esos servicios están repartidos en varias computadoras. HDFS se usa en el pseudo-distribuido y en el totalmente distribuido, pero no en standalone.

**2. Por qué el dataset es un volumen y no se copia con `COPY`.** Primero, porque el CSV pesa unos 350 MB y la imagen quedaría enorme y tardaría más en construirse. Segundo, si el archivo cambia (por ejemplo, si genero otro dataset) no tengo que reconstruir la imagen, solo apunto el volumen a la carpeta. Además así el CSV no queda guardado dentro de la imagen y no se sube a GitHub por error, y lo monto en solo lectura para que el contenedor no pueda modificarlo.

**3. Qué pasa con la base de datos con `down` y con `down -v`.** Con `docker compose down` se borran los contenedores y la red, pero el volumen `pgdata` se queda, así que cuando vuelvo a hacer `up` los datos siguen ahí. Con `docker compose down -v` también se borran los volúmenes, entonces la base de datos queda vacía y tengo que volver a cargar los resultados con el script.

**4. Por qué MapReduce no siempre es más rápido.** En mi prueba el script secuencial tardó 11.426 s y Hadoop 21.241 s. Con un archivo de este tamaño el script lo lee una sola vez y listo, mientras que Hadoop gasta tiempo en arrancar Java, organizar las tareas y escribir y ordenar datos temporales en disco. Además, en modo standalone no hay varias máquinas que se repartan el trabajo. MapReduce conviene cuando los datos son tan grandes que no caben o tardan demasiado en una sola máquina, y se tiene un clúster con HDFS para repartir el trabajo.

**5. Diferencias entre `CMD` y `ENTRYPOINT`, y entre `COPY` y `ADD`.** `CMD` es el comando que se ejecuta por defecto al iniciar el contenedor, y se puede cambiar fácilmente al escribir otro comando en `docker run`. `ENTRYPOINT` es el programa fijo del contenedor; lo que escribo después se le pasa como argumentos. `COPY` solo copia archivos de mi carpeta a la imagen. `ADD` hace lo mismo, pero además puede descomprimir archivos `.tar` y descargar desde una URL; por eso conviene usar `COPY` cuando no necesito eso.
