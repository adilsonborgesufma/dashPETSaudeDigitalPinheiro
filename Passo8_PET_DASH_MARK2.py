import pandas as pd
import geopandas as gpd
import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
from pathlib import Path

# ================= CORREÇÃO DE CAMINHOS (LOGOS) =================
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

# ================= CONFIGURAÇÃO =================
st.set_page_config(
    page_title="Análise de UBS - Pinheiro/MA",
    layout="wide",
    page_icon="🏥"
)

# ================= LEITURA DOS DADOS =================
@st.cache_data
def load_data():
    municipio = gpd.read_file(
        r"assets/pinheiro.json"
    ).to_crs(4326)

    ubs = gpd.read_file(
        r"assets/ubs_pinheiro.json"
    ).to_crs(4326)

    return municipio, ubs

municipio, ubs = load_data()

# Campo de nome da UBS
campo_nome = "name" if "name" in ubs.columns else ubs.select_dtypes("object").columns[0]

# ================= SIDEBAR =================
with st.sidebar:

    col1, col2 = st.columns(2)

    with col1:
        st.image(ASSETS_DIR / "ufma.jpeg", use_container_width=True)

    with col2:
        st.image(ASSETS_DIR / "logo_pet.png", use_container_width=True)

    st.markdown("### 🏥 Projeto de Informação e Saúde Digital")
    st.markdown("**PET-Saúde/I&SD – UFMA**")
    st.caption("Município de Pinheiro – MA")

    st.divider()

    tile = st.radio(
        "Mapa base",
        ["OpenStreetMap", "Satélite", "Topográfico"],
        index=0
    )

    show_limites = st.checkbox("Mostrar limites municipais", True)
    cluster = st.checkbox("Agrupar UBS", True)

# ================= MAPA =================
centro = [
    municipio.geometry.centroid.y.mean(),
    municipio.geometry.centroid.x.mean()
]

tiles = {
    "OpenStreetMap": {
        "tiles": "OpenStreetMap",
        "attr": None
    },
    "Satélite": {
        "tiles": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "attr": "Esri, Maxar, Earthstar Geographics"
    },
    "Topográfico": {
        "tiles": "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        "attr": "© OpenTopoMap contributors"
    }
}

tile_cfg = tiles[tile]

m = folium.Map(
    location=centro,
    zoom_start=11,
    tiles=tile_cfg["tiles"],
    attr=tile_cfg["attr"],
    control_scale=True
)

# Limite municipal
if show_limites:
    folium.GeoJson(
        municipio,
        style_function=lambda _: dict(
            color="#2E7D32",
            weight=2,
            fillOpacity=0.15
        ),
        name="Limite Municipal"
    ).add_to(m)

# UBS (com ou sem cluster)
layer = MarkerCluster(name="UBS").add_to(m) if cluster else m

for _, r in ubs.iterrows():
    folium.Marker(
        [r.geometry.y, r.geometry.x],
        tooltip=r[campo_nome],
        popup=f"<b>{r[campo_nome]}</b>",
        icon=folium.Icon(color="red", icon="plus-sign")
    ).add_to(layer)

folium.LayerControl().add_to(m)

# ================= LAYOUT =================
st.title("📍 Distribuição Espacial das UBS – Pinheiro/MA")
st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    folium_static(m, height=520)

with col2:
    st.subheader("📊 Indicadores")
    st.metric("Total de UBS", len(ubs))

    st.subheader("🏥 Lista de UBS")
    for nome in ubs[campo_nome]:
        st.markdown(f"- {nome}")

# ================= TABELA =================
st.divider()
st.subheader("📋 Dados das UBS")

df_tabela = ubs.drop(columns="geometry")
st.dataframe(df_tabela, use_container_width=True)

# ================= EXPORTAÇÃO =================
st.divider()
st.subheader("📥 Exportar Dados")

c1, c2, c3 = st.columns(3)

with c1:
    st.download_button(
        "🗺️ GeoJSON UBS",
        ubs.to_json(),
        file_name="ubs_pinheiro_ma.geojson",
        mime="application/json"
    )

with c2:
    st.download_button(
        "📊 CSV UBS",
        df_tabela.to_csv(index=False),
        file_name="ubs_pinheiro_ma.csv",
        mime="text/csv"
    )

with c3:
    st.download_button(
        "📍 GeoJSON Município",
        municipio.to_json(),
        file_name="pinheiro_ma.geojson",
        mime="application/json"
    )

# ================= RODAPÉ (INALTERADO) =================
st.markdown("""
**Sistema:** Dashboard UBS – Pinheiro/MA<br>
**Projeto:** Programa de Educação pelo Trabalho para a Saúde: Informação e Saúde Digital (PET-Saúde/I&SD)<br>
**Tecnologias:** Python, Streamlit, GeoPandas, Folium<br>
**Base cartográfica:** OpenStreetMap<br>
**Finalidade:** Planejamento em Saúde Pública<br><br>
**Equipe:** Anne Karine Martins Assunção da Silva; Adilson Matheus Borges Machado; Jonatas da Silva Castro;<br>
Alisson Freitas Santos Brandão da Silva; Luenne Sinara Ribeiro Pinheiro; Sônia Maria Silva Luz;<br>
Lindomar Christian da Trindade Filho; Cleiciane Cordeiro Coutinho; Nalleny Perpétua dos Santos Marinho;<br>
Cleyce Jane Costa Moraes; Alice Beatriz Tomaz Tavares; Enzo Marcos Costa Guterres; Lucas Gomes da Silva;<br>
Kauã de Assis Menezes Reis; Bruna Pereira Maia Silva; Geciane Pereira Aroucha;<br><br>
**Desenvolvimento:** Adilson Matheus Borges Machado e Bruna Pereira Maia Silva
""", unsafe_allow_html=True)