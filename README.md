
# Consultor de Precios

## Descripción

Aplicación desarrollada con **Python y Streamlit** para consultar, filtrar y analizar costos y precios, con exportación de resultados a Excel.

<p align="left">
  <a href="https://costos-reporteycargaprecios.streamlit.app/">
    <img src="https://img.shields.io/badge/Demo-Online-28A745?logo=googlechrome&logoColor=white&style=for-the-badge" height="40">
  </a>
  <a href="https://www.linkedin.com/in/claudiogabrielalonso/">
    <img src="https://img.shields.io/badge/LinkedIn-Perfil-0A66C2?logo=linkedin&logoColor=white&style=for-the-badge" height="40">
  </a>
</p>


## Sobre el proyecto

**Consultor de Precios** centraliza la consulta y preparación de datos de costos y precios para facilitar su análisis y generación de reportes.


## Objetivo

Facilitar el análisis de:

-   Precios por producto y fecha.
-   Diferencias entre precios.
-   Filtros por fecha y moneda.
-   Resultados consolidados.


## Funcionalidades

-   Filtro por rango de fechas.
-   Filtro por moneda.
-   Selección de precios por producto.
-   Consulta desde SQLite o SQL Server.
-   Transformación y normalización de datos.
-   Exportación a Excel.


## Tecnologías

-   **Python**
-   **Streamlit**
-   **Pandas / NumPy**
-   **SQLite / SQL Server**
-   **pyodbc**
-   **openpyxl**


## Arquitectura

```text
Usuario
   ↓
Streamlit
   ↓
Filtros y consultas
   ↓
Base de datos
   ↓
Pandas
   ↓
Transformación y consolidación
   ↓
Excel