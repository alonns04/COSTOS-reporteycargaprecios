import logging
import os
import sys

import pandas as pd
import streamlit as st

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Agregar ruta para importar módulos compartidos
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import main as modulo_main

ejecutar_consulta = modulo_main.main

IDENTIFICADOR_COL = os.getenv("IDENTIFICADOR_COL", "ObjID")

# =========================================
# CONFIGURACIÓN
# =========================================

st.set_page_config(
    page_title="Reporte COSTOS y PRECIOS",
    page_icon="logo_barras.svg",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================
# CSS
# =========================================

st.markdown("""
<style>

.small-text {
    font-size: 0.85rem;
    color: #a0a0a0;
    margin: 5px 0;
}

/* Botón descarga verde */
div[data-testid="stDownloadButton"] button {
    background-color: #28a745 !important;
    color: white !important;
    border: none !important;
}

div[data-testid="stDownloadButton"] button:hover {
    background-color: #218838 !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================
# TITLE
# =========================================

st.title("Gestor de Costos y Precios")

# =========================================
# SESSION STATE
# =========================================

if "estado_log" not in st.session_state:
    st.session_state.estado_log = []

if "df_anterior" not in st.session_state:
    st.session_state.df_anterior = None

if "df_cambios" not in st.session_state:
    st.session_state.df_cambios = None

if "excel_data" not in st.session_state:
    st.session_state.excel_data = b""

if "export_ready" not in st.session_state:
    st.session_state.export_ready = False

if "last_filter_signature" not in st.session_state:
    st.session_state.last_filter_signature = None


# =========================================
# FILTROS
# =========================================


with st.sidebar:
    st.header("Filtros")
    st.subheader("Rango de fechas")
    fecha_inicio = st.date_input("Inicio", value=None, key="fecha_inicio")
    fecha_fin = st.date_input("Fin", value=None, key="fecha_fin")
    st.subheader("Precios")
    ultimo_precio = st.checkbox("Último precio por producto", value=False, key="ultimo_precio")
    primer_precio = st.checkbox("Primer precio por producto", value=False, key="primer_precio")

    st.subheader("Moneda")
    col_moneda_1, col_moneda_2 = st.columns(2)
    with col_moneda_1:
        dolar = st.checkbox("Dólar", value=False, key="moneda_dolar")
    with col_moneda_2:
        peso = st.checkbox("Peso", value=False, key="moneda_peso")

    if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
        st.error("La fecha de inicio no puede ser mayor que la fecha de fin.")

current_filter_signature = (
    str(getattr(fecha_inicio, "isoformat", lambda: fecha_inicio)())
    + "|"
    + str(getattr(fecha_fin, "isoformat", lambda: fecha_fin)())
    + "|"
    + str(ultimo_precio)
    + "|"
    + str(primer_precio)
    + "|"
    + str(dolar)
    + "|"
    + str(peso)
)

if st.session_state.get("last_filter_signature") != current_filter_signature:
    st.session_state.last_filter_signature = current_filter_signature
    st.session_state.excel_data = b""
    st.session_state.export_ready = False

# =========================================
# EXPORTAR DATOS
# =========================================

st.header("Exportar Datos")


def exportar_excel():
    try:
        if (
            st.session_state.get("fecha_inicio")
            and st.session_state.get("fecha_fin")
            and st.session_state["fecha_inicio"] > st.session_state["fecha_fin"]
        ):
            st.session_state.estado_log.append(
                "La fecha de inicio no puede ser mayor que la fecha de fin."
            )
            st.session_state.excel_data = b""
            st.session_state.export_ready = False
            return False

        st.session_state.estado_log.append(
            "Ejecutando consulta a base de datos..."
        )

        moneda_seleccionada = None
        if st.session_state.get("moneda_dolar", False) != st.session_state.get("moneda_peso", False):
            moneda_seleccionada = "Dólar" if st.session_state.get("moneda_dolar", False) else "Peso"

        excel_bytes = ejecutar_consulta(
            start_date=st.session_state.get("fecha_inicio"),
            end_date=st.session_state.get("fecha_fin"),
            ultimo_precio=st.session_state.get("ultimo_precio", False),
            primer_precio=st.session_state.get("primer_precio", False),
            moneda=moneda_seleccionada,
        )

        if not isinstance(excel_bytes, (bytes, bytearray)):
            raise TypeError("La exportación no devolvió bytes válidos")

        st.session_state.excel_data = bytes(excel_bytes)
        st.session_state.export_ready = bool(st.session_state.excel_data)
        st.session_state.last_filter_signature = current_filter_signature
        st.session_state.estado_log.append(
            f"Archivo listo para descargar: {len(st.session_state.excel_data)} bytes"
        )
        logging.info("Archivo listo para descargar: %s bytes", len(st.session_state.excel_data))
        return True

    except Exception as e:
        st.session_state.excel_data = b""
        st.session_state.export_ready = False
        st.session_state.estado_log.append(
            f"Error: {str(e)}"
        )
        logging.exception("Error al generar el Excel")
        return False


if st.button("Exportar", key="btn_exportar_descargar"):
    exportar_excel()

if st.session_state.get("excel_data"):
    st.download_button(
        label="Descargar Excel",
        data=st.session_state.excel_data,
        file_name="resultados.xlsx",
        mime="application/vnd.openxmlformats-officedocument/spreadsheetml.sheet",
        key="btn_descargar",
    )
else:
    st.caption("Presione Exportar para generar el archivo")



# =========================================
# ESTADO
# =========================================

st.divider()

st.header("Estado")

estado_container = st.container()

with estado_container:

    logs = st.session_state.get("estado_log", [])

    if logs:

        for log in logs[-10:]:

            st.markdown(
                f"<p class='small-text' style='margin: 2px 0; font-size: 0.75rem;'>✓ {log}</p>",
                unsafe_allow_html=True
            )

    else:

        st.markdown(
            "<p class='small-text' style='margin: 2px 0; font-size: 0.72rem;'>...</p>",
            unsafe_allow_html=True
        )


st.divider()

# =========================================
# CARGAR ARCHIVO
# =========================================

st.header("Próximamente")
st.subheader("Actualizar precios")

uploaded_file = st.file_uploader(
    "Arrastra o selecciona un archivo Excel",
    type=["xlsx", "xls"],
    key="file_uploader",
    disabled=True,
)

if uploaded_file is not None and getattr(uploaded_file, "name", ""):

    try:

        df_actual = pd.read_excel(uploaded_file)

        # =========================================
        # VALIDAR OBJID
        # =========================================

        if IDENTIFICADOR_COL not in df_actual.columns:

            st.error(f"El archivo no contiene la columna {IDENTIFICADOR_COL}")
            st.stop()

        st.markdown(
            f"<p class='small-text'>Archivo cargado: "
            f"{uploaded_file.name}</p>",
            unsafe_allow_html=True
        )

        st.markdown(
            f"<p class='small-text'>"
            f"Filas: {len(df_actual)} | "
            f"Columnas: {len(df_actual.columns)}"
            f"</p>",
            unsafe_allow_html=True
        )

        # =========================================
        # COMPARAR CONTRA EXCEL ANTERIOR
        # =========================================

        cambios_detectados = []

        if st.session_state.df_anterior is not None:

            df_anterior = st.session_state.df_anterior.copy()

            merge = df_actual.merge(
                df_anterior,
                on=IDENTIFICADOR_COL,
                how="inner",
                suffixes=("_nuevo", "_anterior")
            )

            columnas = []

            for c in merge.columns:

                if c.endswith("_nuevo"):

                    columnas.append(
                        c.replace("_nuevo", "")
                    )

            for _, row in merge.iterrows():

                objid = row["ObjID"]

                for columna in columnas:

                    nuevo = row[f"{columna}_nuevo"]
                    anterior = row[f"{columna}_anterior"]

                    if str(nuevo) != str(anterior):

                        cambio = {
                            IDENTIFICADOR_COL: objid,
                            "Campo": columna,
                            "Valor Anterior": anterior,
                            "Valor Nuevo": nuevo
                        }

                        cambios_detectados.append(cambio)

                        # =========================================
                        # PRINT CONSOLA
                        # =========================================

                        print("=" * 60)

                        print(f"{IDENTIFICADOR_COL}: {objid}")

                        if "ID_nuevo" in row:
                            print(f"ID Item: {row['ID_nuevo']}")

                        print(f"Campo modificado: {columna}")
                        print(f"Valor anterior: {anterior}")
                        print(f"Valor nuevo: {nuevo}")

        # =========================================
        # GUARDAR CAMBIOS
        # =========================================

        if cambios_detectados:

            st.session_state.df_cambios = pd.DataFrame(
                cambios_detectados
            )

        else:

            st.session_state.df_cambios = None

        # =========================================
        # TABS
        # =========================================

        tabs = ["Archivo Actual"]

        if st.session_state.df_cambios is not None:
            tabs.append("Cambios")

        pestañas = st.tabs(tabs)

        # =========================================
        # TAB ARCHIVO ACTUAL
        # =========================================

        with pestañas[0]:

            with st.expander(
                "Ver previa del archivo",
                expanded=True
            ):

                st.dataframe(
                    df_actual,
                    use_container_width=True
                )

        # =========================================
        # TAB CAMBIOS
        # =========================================

        if st.session_state.df_cambios is not None:

            with pestañas[1]:

                st.warning(
                    f"Se detectaron "
                    f"{len(st.session_state.df_cambios)} cambios"
                )

                with st.expander(
                    "Ver previa del archivo Cambios",
                    expanded=True
                ):

                    st.dataframe(
                        st.session_state.df_cambios,
                        use_container_width=True
                    )

        # =========================================
        # GUARDAR ACTUAL COMO ANTERIOR
        # =========================================

        st.session_state.df_anterior = df_actual.copy()

        # =========================================
        # BOTÓN PROCESAR
        # =========================================

        col1, col2, col3 = st.columns([1, 1, 3])

        with col1:

            if st.button("Procesar", key="btn_procesar"):

                st.session_state.estado_log.append(
                    "Procesando archivo..."
                )

                st.info("Procesando archivo...")

    except Exception as e:

        st.markdown(
            f"<p class='small-text' "
            f"style='color: #ff6b6b;'>"
            f"Error: {str(e)}"
            f"</p>",
            unsafe_allow_html=True
        )

else:

    st.markdown(
        "<p class='small-text'>"
        "Carga un archivo Excel para comenzar"
        "</p>",
        unsafe_allow_html=True
    )
