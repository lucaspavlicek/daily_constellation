import os
from pathlib import Path
import streamlit as st

data_dir = Path(__file__).resolve().parent.parent / "data"
data_dir.mkdir(parents=True, exist_ok=True)

os.environ["STARPLOT_DATA_PATH"] = str(data_dir)
os.environ["STARPLOT_DOWNLOAD_PATH"] = str(data_dir)

st.set_page_config(
    page_title="Constellation of the day",
    layout="wide",
)

game_page = st.Page("daily_constellation.py", title="Daily Constellation", url_path="", default=True)
how_to_page = st.Page("how_to_play.py", title="How to Play", url_path="how-to-play")

pg = st.navigation([game_page, how_to_page], position="top") # or "sidebar" / "top"

pg.run()