from pathlib import Path
import streamlit as st

# Define path relative to this script file
dir = Path(__file__).resolve().parent / "docs"


def load_file(filename):
    file_path = dir / filename
    if file_path.exists():
        return file_path.read_text(encoding="utf-8")
    return f"Error: Could not find ({filename})."

def show():
    with st.sidebar:
        st.markdown("### Table of Contents")
        st.markdown("- [Quick Start Guide](#quick-start-guide)")
        st.markdown("- [Choosing the Constellation](#choosing-the-constellation)")
        st.markdown("- [About the Plots](#about-the-plots)")
        st.markdown("- [Navigating through Previous Plots](#navigating-through-previous-plots)")
        st.markdown("- [Strategies](#strategies)")
        st.markdown("- [Source Code](#source-code)")

    st.header("Quick Start Guide")
    st.markdown(load_file("quick_start_guide.md"))

    st.header("Choosing the Constellation")
    st.markdown(load_file("choosing_the_constellation.md"))

    st.header("About the Plots")
    st.markdown(load_file("about_the_plots.md"))

    st.header("Navigating through Previous Plots")
    st.markdown(load_file("previous_plots.md"))

    st.header("Strategies")
    st.markdown(load_file("strategies.md"))

    st.header("Source Code")
    st.markdown(load_file("source_code.md"))
    
if __name__ == "__main__":
    show()