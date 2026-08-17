import streamlit as st
from datetime import datetime, UTC
import hashlib
from pathlib import Path
import random
import math

import matplotlib.pyplot as plt
from starplot import Constellation

from tools.plot import make_zenith_plot
from tools.choose_observer import haversine, constellation_centroid, choose_observer_zenith, create_observer
from tools.constellation_english_names import english_names

root = Path(__file__).resolve().parent.parent

def get_daily_seed():
    today_str = datetime.now(UTC).strftime("%Y-%m-%d")

    secret_key = st.secrets["secret_key"]
    
    hash = hashlib.sha256(f"{today_str}{secret_key}".encode('utf-8'))

    return int(hash.hexdigest(), 16)

def get_daily_constellation(rng, c_list):

    return c_list[rng.randint(0, 88)]

@st.cache_resource
def initialize_system():

    return {"status": "Database Loaded Successfully"}

sys_status = initialize_system()

@st.cache_data
def load_constellation_data():
    """
    Queries Starplot's database for all 88 IAU constellations, 
    combining the two halves of Serpens into a single entry.
    """
    const_dict = {}
    
    for c in Constellation.all():
        abbr = c.iau_id.lower()
        
        # skip the split Serpens entries
        if abbr in ["ser1", "ser2"]:
            continue
            
        const_dict[abbr] = c.name
        
    # manually set ser
    const_dict["ser"] = "Serpens"
    
    return const_dict, list(const_dict.keys())

constellation_dict, constellation_list = load_constellation_data()

if "rng" not in st.session_state:
    st.session_state.rng = random.Random(get_daily_seed())
if "target_constellation" not in st.session_state:
    st.session_state.target_constellation = get_daily_constellation(st.session_state.rng, constellation_list)  # Hardcoded for now!
if "cache_data" not in st.session_state:
    st.session_state.cache_data = [{
        'guess': '',
        'observer_ra': 0.0,
        'observer_dec': 0.0,
        'counter': [0]*88,
        'zenith_plot': None,
        'nadir_plot': None
    }]
if "game_won" not in st.session_state:
    st.session_state.game_won = False
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "zenith"
if "is_loading" not in st.session_state:
    st.session_state.is_loading = False
if "viewing_turn_idx" not in st.session_state:
    st.session_state.viewing_turn_idx = len(st.session_state.cache_data)-1

def update_cache(guess):

    ob_ra, ob_dec = choose_observer_zenith(st.session_state.target_constellation, guess, st.session_state.rng)

    counter = list(st.session_state.cache_data[-1]['counter'])

    for i, abbr in enumerate(constellation_list):

        ra, dec = constellation_centroid(abbr)

        if abbr == guess:
            counter[i] = -math.inf

        if haversine(ra, dec, ob_ra, ob_dec)*2 < math.pi:
            counter[i] += 1

    st.session_state.cache_data.append({
        'guess': guess,
        'observer_ra': ob_ra,
        'observer_dec': ob_dec,
        'counter': counter.copy(),
        'zenith_plot': None,
        'nadir_plot': None
    })

    # free memory after 5 turns
    cutoff = len(st.session_state.cache_data) - 1 - 4
    for entry in st.session_state.cache_data[:cutoff]:
        for plot_key in ('zenith_plot', 'nadir_plot'):
            if entry[plot_key] is not None:
                plt.close(entry[plot_key])
                entry[plot_key] = None
    return

def add_plot_to_cache(guess_id: int, plot_type):

    if guess_id > len(st.session_state.cache_data)-1 or guess_id < len(st.session_state.cache_data)-1-4:
        raise ValueError('Tried to get plot outside of cache range')
    
    if st.session_state.cache_data[guess_id][plot_type] is not None:
        return
    
    ra = st.session_state.cache_data[guess_id]['observer_ra']
    dec = st.session_state.cache_data[guess_id]['observer_dec']

    observer = create_observer(ra, dec)
    counter_dict = dict(zip(constellation_list, st.session_state.cache_data[guess_id]['counter']))
    guess_name = constellation_dict[st.session_state.cache_data[guess_id]['guess']]

    last_err = None
    fig = None
    for _ in range(3):
        try:
            fig = make_zenith_plot(observer=observer, counter=counter_dict, plot_type=plot_type, guess=guess_name)
            break
        except AttributeError as e:
            if "get_renderer" not in str(e):
                raise
            last_err = e
            plt.close('all')  # clear out any leftover half-built figures from a prior interrupted run
    else:
        raise last_err

    st.session_state.cache_data[guess_id][plot_type] = fig
    return

if st.session_state.game_won:
    # --- VICTORY SCREEN ---
    st.balloons()
    target_name = constellation_dict[st.session_state.target_constellation]
    st.success(
        f"Congratulations! You guessed **{target_name}** in"
        f" {len(st.session_state.cache_data)-1} turns!"
    )

    col1, col2 = st.columns(2)

    url = f"https://noirlab.edu/public/media/archives/lineart/original/{target_name.lower().replace(" ", "")}-outline.png"
    with col1:
        st.image(url, width="stretch")

    with col2:
        st.subheader(target_name, anchor=False)
        st.markdown(f"**English Name:** {english_names[st.session_state.target_constellation]}")
        st.markdown(
            f"[More about {target_name}](https://noirlab.edu/public/education/constellations/{target_name.lower().replace(" ", "")}/)"
        )
        st.markdown(f"**Puzzle Date:** {datetime.now(UTC).strftime("%B %d, %Y")}")
        st.caption("Image credit: NOIRLab")
        st.caption(f"Image URL: {url}")
        st.write("")

        if st.button("Play Again", type="primary"):
            st.session_state.clear()
            st.rerun()

elif len(st.session_state.cache_data) > 1:
    idx = st.session_state.viewing_turn_idx
    plot_type = f'{st.session_state.view_mode}_plot'

    if st.session_state.cache_data[idx][plot_type] is None:
        with st.spinner("Preparing plot..."):
            add_plot_to_cache(idx, plot_type)
        st.session_state.is_loading = False
        st.rerun()
    else:
        st.pyplot(st.session_state.cache_data[idx][plot_type], transparent=True)
        st.session_state.is_loading = False

with st.sidebar:
    
    st.markdown("##### Daily Constellation")
    current_turn = len(st.session_state.cache_data)
    st.markdown(f"**Current Turn:** {current_turn if not st.session_state.game_won else 'Winner!'}")
    st.divider()
    is_loading = st.session_state.is_loading

    if len(st.session_state.cache_data) > 1 and not st.session_state.game_won:
        st.markdown("###### Plot View")

        max_turn = len(st.session_state.cache_data) - 1
        min_turn = max(1, max_turn - 4)
        is_zenith = st.session_state.view_mode == "zenith"

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(":material/arrow_back:", key="prev_btn",
                         disabled=is_loading or st.session_state.viewing_turn_idx <= min_turn,
                         use_container_width=True) and not st.session_state.is_loading:
                st.session_state.viewing_turn_idx -= 1
                st.session_state.is_loading = True
                st.rerun()

        with col2:
            toggle_icon = ":material/arrow_downward:" if is_zenith else ":material/arrow_upward:"
            if st.button(toggle_icon, key="view_toggle_btn",
                         disabled=is_loading, use_container_width=True) and not st.session_state.is_loading:
                st.session_state.view_mode = (
                    "nadir" if is_zenith else "zenith"
                )
                st.session_state.is_loading = True
                st.rerun()

        with col3:
            if st.button(":material/arrow_forward:", key="next_btn",
                         disabled=is_loading or st.session_state.viewing_turn_idx >= max_turn,
                         use_container_width=True) and not st.session_state.is_loading:
                st.session_state.viewing_turn_idx += 1
                st.session_state.is_loading = True
                st.rerun()

    with st.form("guess_form", clear_on_submit=True):
        st.subheader("Make a Guess")

        available_options = []
        for i, abbr in enumerate(constellation_dict.keys()):
            name = constellation_dict[abbr]

            if abbr in [d['guess'] for d in st.session_state.cache_data]:
                continue

            count = st.session_state.cache_data[-1]['counter'][i]

            available_options.append(f'{name} ({abbr}) [{count}/{current_turn-1}]')

        available_options.sort()

        selected_display = st.selectbox(
            "Search Constellation:",
            options=available_options,
            index=None,
        )
        
        submit_btn = st.form_submit_button(
            "Submit",
            use_container_width=True,
            disabled=st.session_state.is_loading
        )

        if submit_btn and selected_display and not st.session_state.is_loading:

            st.session_state.is_loading = True
            
            user_guess = selected_display.split("(")[1].split(")")[0].strip()
            
            if st.session_state.game_won:
                st.warning("You already won! Please reset the game.")
            elif user_guess in [d['guess'] for d in st.session_state.cache_data]:
                st.error(f"You already guessed {constellation_list[user_guess]}!")
            else:
                
                update_cache(user_guess)
                
                if user_guess == st.session_state.target_constellation:
                    st.session_state.game_won = True
                
                st.session_state.view_mode = "zenith"
                st.session_state.viewing_turn_idx = len(st.session_state.cache_data) - 1
                st.rerun()
    
    st.divider()
    st.markdown("###### Guess History")
    with st.container(height=200):
        for guess in reversed([d['guess'] for d in st.session_state.cache_data[1:]]):
            st.write(constellation_dict[guess])