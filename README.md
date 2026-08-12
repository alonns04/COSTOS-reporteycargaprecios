
# Gestor de Costos y Precios

## Descripción

Aplicación desarrollada con **Python y Streamlit** para gestionar, consultar y exportar información de costos y precios. Permite aplicar filtros por fecha y moneda, seleccionar precios y preparar los datos para su análisis y descarga en Excel.

<p align="left">
  <a href="https://costos-reporteycargaprecios.streamlit.app/">
    <img src="https://img.shields.io/badge/Demo-Online-28A745?logo=googlechrome&logoColor=white&style=for-the-badge" height="40">
  </a>
  <a href="https://www.linkedin.com/in/claudiogabrielalonso/">
    <img src="https://img.shields.io/badge/LinkedIn-Perfil-0A66C2?logo=linkedin&logoColor=white&style=for-the-badge" height="40">
  </a>
</p>


## Sobre el proyecto

**Gestor de Costos y Precios** permite consultar, filtrar y consolidar información de costos y precios para facilitar su análisis y posterior exportación.

La aplicación centraliza la lógica de carga, transformación y preparación de los datos, generando un dataset ordenado y listo para reportes.


## Objetivo

Facilitar el análisis de:

- Precios por producto y fecha.
- Diferencias entre precios seleccionados.
- Filtros por rango temporal y moneda.
- Consolidación de resultados.
- Exportación de información para análisis.

----------

## Funcionalidades

- Selección de rango de fechas.
- Filtro por moneda (Dólar / Peso).
- Selección del primer o último precio por producto.
- Consulta de datos desde SQLite o SQL Server.
- Transformación y normalización del DataFrame.
- Consolidación de información.
- Exportación de resultados a Excel.


## Módulos

| Módulo | Descripción |
|---|---|
| `app.py` | Interfaz Streamlit y flujo principal de la aplicación. |
| `main.py` | Lógica de consultas, filtros y generación del archivo Excel. |
| `connection.py` | Conexión a la base de datos y obtención del DataFrame. |
| `transformador.py` | Normalización y renombrado de columnas para análisis. |
| `query.txt` | Consulta SQL principal utilizada para obtener los datos. |
| `requirements.txt` | Dependencias del proyecto. |
| `extracciondelabase/` | Utilidades auxiliares para extracción y preparación de datos. |
| `cifrardb/` | Recursos relacionados con cifrado o almacenamiento de la base de datos. |


## Tecnologías

### Lenguaje

`Python`

### Framework

`Streamlit`

### Procesamiento de datos

`Pandas` · `NumPy`

### Bases de datos

`SQLite` · `SQL Server`

### Herramientas

`pyodbc` · `openpyxl` · `python-dotenv`

## Arquitectura

```text
Usuario
   ↓
Streamlit
   ↓
Consulta / Filtros
   ↓
Conexión a base de datos
   ↓
DataFrame
   ↓
Transformación y normalización
   ↓
Agrupación / selección de precios
   ↓
Resultado / Excel
```

## Datos y procesamiento

La aplicación puede trabajar con **SQLite** como base local y con **SQL Server** como fuente de datos principal, según la configuración del entorno.

La extracción se realiza mediante consultas SQL y posteriormente los datos son procesados con `Pandas` para:

- Normalizar y estandarizar columnas.
- Convertir fechas a formatos utilizables.
- Aplicar filtros por fecha, moneda y precio.
- Seleccionar el primer o último precio por producto.
- Consolidar la información.
- Preparar el dataset final para análisis y exportación.
   

## Instalación y ejecución

### Crear el entorno virtual

```bash
python -m venv venv

```

### Activar el entorno virtual

#### Windows

```bash
venv\Scripts\activate

```

#### Linux / macOS

```bash
source venv/bin/activate

```

### Instalar dependencias

```bash
pip install -r requirements.txt

```

### Ejecutar la aplicación

```bash
streamlit run app.py

```

La aplicación estará disponible en:

```text
http://localhost:8501

```
## Configuración

La conexión a la base de datos se configura mediante **variables de entorno**.

Se recomienda utilizar un archivo `.env` para almacenar la configuración y agregarlo al `.gitignore` para evitar versionar credenciales.

### Variables de entorno

```env
USE_SQLITE=true

SQL_SERVER=
SQL_PORT=
SQL_DATABASE=
SQL_USER=
SQL_PASSWORD=
ODBC_DRIVER=

SQLITE_DB_PATH=
```

### SQLite

Si se configura:

```env
USE_SQLITE=true
```

la aplicación utiliza una base de datos **SQLite local**.

La ubicación de la base se define mediante:

```env
SQLITE_DB_PATH=
```

### SQL Server

Si se configura:

```env
USE_SQLITE=false
```

la aplicación utiliza **SQL Server** como fuente de datos.

Los parámetros de conexión se definen mediante:

```env
SQL_SERVER=
SQL_PORT=
SQL_DATABASE=
SQL_USER=
SQL_PASSWORD=
ODBC_DRIVER=