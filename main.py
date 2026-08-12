import io
import logging
import os
import re
from pathlib import Path

import pandas as pd

from connection import obtener_dataframe
from transformador import transformar_dataframe

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

BASE_DIR = Path(__file__).resolve().parent
QUERY_FILE = BASE_DIR / "query.txt"
OUTPUT_FILE = BASE_DIR / "resultados.xlsx"

PLACEHOLDER_VALUES = {
    "<schema>": "main",
    "<tabla>": "costos_materiales",
    "<campo_identificador>": "id_hash",
    "<campo_clave>": "tabla_hash",
    "<campo_fecha>": "fecha",
    "<campo_precio>": "precio",
    "<campo_moneda>": "moneda",
    "<campo_codigo>": "codigo_hash",
    "<campo_descripcion>": "elemento_hash",
    "<campo_unidad>": "unidad",
    "<alias_identificador>": "ObjID",
    "<alias_clave>": "ObjID_TBCustoMat",
    "<alias_fecha>": "DataRef",
    "<alias_precio>": "PrecoRevenda",
    "<alias_moneda>": "IdMoeda",
    "<alias_codigo>": "CodTabela",
    "<alias_descripcion>": "Descricao",
    "<alias_unidad>": "UnidadeCusto",
}


USE_SQLITE = os.getenv("USE_SQLITE", "true").strip().lower() in {"1", "true", "yes", "y", "si", "sí"}


def aplicar_filtros(
    df: pd.DataFrame,
    start_date=None,
    end_date=None,
    ultimo_precio: bool = False,
    primer_precio: bool = False,
    moneda: str | None = None,
) -> pd.DataFrame:
    """Aplica filtros de fecha y los checks de precio al DataFrame resultante."""
    df_filtrado = df.copy()
    if df_filtrado.empty:
        return df_filtrado

    if "DataRef" in df_filtrado.columns:
        df_filtrado["DataRef"] = pd.to_datetime(df_filtrado["DataRef"], errors="coerce")

    if start_date is not None:
        df_filtrado = df_filtrado[df_filtrado["DataRef"] >= pd.Timestamp(start_date)]

    if end_date is not None:
        end_dt = pd.Timestamp(end_date).normalize() + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
        df_filtrado = df_filtrado[df_filtrado["DataRef"] <= end_dt]

    if ultimo_precio and primer_precio:
        raise ValueError("No se pueden seleccionar 'Último precio' y 'Primer precio' al mismo tiempo")

    if ultimo_precio and "CodTabela" in df_filtrado.columns:
        df_filtrado = (
            df_filtrado.sort_values(["CodTabela", "DataRef"], ascending=[True, False])
            .drop_duplicates(subset=["CodTabela"], keep="first")
            .reset_index(drop=True)
        )

    if primer_precio and "CodTabela" in df_filtrado.columns:
        df_filtrado = (
            df_filtrado.sort_values(["CodTabela", "DataRef"], ascending=[True, True])
            .drop_duplicates(subset=["CodTabela"], keep="first")
            .reset_index(drop=True)
        )

    if moneda is not None and "IdMoeda" in df_filtrado.columns:
        if moneda == "Dólar":
            df_filtrado = df_filtrado[df_filtrado["IdMoeda"].astype(str).str.strip() == "2"]
        elif moneda == "Peso":
            df_filtrado = df_filtrado[df_filtrado["IdMoeda"].astype(str).str.strip() == "0"]

    return df_filtrado


def render_query_template(template_text: str) -> str:
    """Reemplaza placeholders del archivo de consulta por valores de ejemplo."""
    query = template_text
    for token, value in PLACEHOLDER_VALUES.items():
        query = query.replace(token, value)

    if USE_SQLITE:
        query = re.sub(r"FROM\s+main\.", "FROM ", query)
        query = re.sub(r"FROM\s+\.", "FROM ", query)

    return query


def main(
    start_date=None,
    end_date=None,
    ultimo_precio: bool = False,
    primer_precio: bool = False,
    moneda: str | None = None,
):
    """Ejecuta la consulta SQL desde el archivo query.txt con filtros opcionales."""
    try:
        query_template = QUERY_FILE.read_text(encoding="utf-8")
        query = render_query_template(query_template)

        logging.info("Ejecutando consulta desde %s...", QUERY_FILE)

        df = obtener_dataframe(query)
        df_filtrado = aplicar_filtros(
            df,
            start_date=start_date,
            end_date=end_date,
            ultimo_precio=ultimo_precio,
            primer_precio=primer_precio,
            moneda=moneda,
        )
        df_transformado = transformar_dataframe(df_filtrado)

        print("\n=== Resultados de la Consulta ===")
        print(df_transformado)
        print(f"\nTotal de registros: {len(df_transformado)}")

        logging.info("Iniciando generación del archivo Excel en memoria")
        output_bytes = io.BytesIO()
        with pd.ExcelWriter(output_bytes, engine="openpyxl") as writer:
            df_transformado.to_excel(writer, index=False, sheet_name="Resultados")
        output_bytes.seek(0)
        excel_payload = output_bytes.getvalue()
        logging.info("Bytes del Excel generados: %s", len(excel_payload))
        logging.info("Primeros bytes: %s", excel_payload[:32])

        if not excel_payload:
            raise ValueError("El archivo Excel generado está vacío")

        return excel_payload

    except FileNotFoundError:
        logging.error("El archivo query.txt no fue encontrado.")
        raise
    except Exception as e:
        logging.error(f"Error al ejecutar la consulta: {str(e)}")
        raise


if __name__ == "__main__":
    main()
