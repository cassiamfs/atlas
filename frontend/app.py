import streamlit as st
import pandas as pd
import requests
from streamlit_lottie import st_lottie
import time

# --- (Las funciones get_prediction, add_bg_from_url, load_lottieurl no cambian) ---

def get_prediction(query, top_k):
    # NOTA: Para que el filtro funcione bien, es mejor pedir más resultados a la API
    # y luego filtrarlos. Considera aumentar 'top_k' si es posible en tu API.
    response = requests.get('https://atlas-917734968327.europe-southwest1.run.app/predict_city', params = {'query': query, 'top_k': top_k})
    return response

def add_bg_from_url():
    # (Este código CSS se mantiene igual)
    st.markdown(
         f"""
         <style>
         .stApp {{ background-image: url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1172&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"); background-size: cover; background-position: center; background-repeat: no-repeat; }}
         h1, h2, h3, p, label, .stMarkdown {{ color: white !important; text-shadow: -2px -2px 0 #000033, 2px -2px 0 #000033, -2px 2px 0 #000033, 2px 2px 0 #000033, -2px 0px 0 #000033, 2px 0px 0 #000033, 0px -2px 0 #000033, 0px 2px 0 #000033; }}
         textarea, .stTextArea textarea {{ background-color: rgba(255, 255, 255, 0.9) !important; color: black !important; border: 1px solid white !important; }}
         textarea::placeholder {{ color: black !important; opacity: 0.4 !important; }}
         .stNumberInput input {{ background-color: rgba(255, 255, 255, 0.9) !important; color: black !important; border: 1px solid white !important; }}
         div.stButton > button {{ background-color: rgba(0, 0, 0, 0.7) !important; color: white !important; border: 1px solid white !important; }}
         div.stButton > button:hover *{{ background-color: rgba(255, 255, 255, 0.7) !important; color: rgba(0, 0, 0, 1) !important; text-shadow: none !important; }}
         </style>
         """, unsafe_allow_html=True)

def load_lottieurl(url):
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()

# --- INTERFAZ DE STREAMLIT ---

add_bg_from_url()
st.set_page_config(page_title="Atlas Roots", page_icon="🌎", layout="wide")

st.title("Atlas Roots🌍")
st.markdown("Find cities based on your description with AI✨")
st.markdown("Try your luck by getting a destination with us ✈️")

# --- INICIO: NUEVOS FILTROS ---
st.markdown("---")

use_region_filter = st.toggle("Filter by Region 🗺️")
selected_regions = []
region_map = {1: 'North America', 2: 'South America', 3: 'Asia', 4: 'Oceania', 5: 'Europe', 6: 'Africa', 7: 'Middle East'}
if use_region_filter:
    selected_regions = st.multiselect(
        "Region",
        options=list(region_map.keys()),
        format_func=lambda x: region_map[x],
        default=[]
    )

use_seclusion_filter = st.toggle("👤 Level of Crowdedness (1: Very quiet, 5: Very crowded)")
seclusion_range = (1, 5)
if use_seclusion_filter:
    seclusion_range = st.slider(
    "Nivel de Aislamiento (1: Muy tranquilo, 5: Muy concurrido)",
    min_value=1, max_value=5, value=(1, 5)
)


use_budget_filter = st.toggle("Filter by Budget 💸")
selected_budgets = []
budget_map = {1: "💰 Low Budget", 2: "💰💰 Mid Range", 3: "💰💰💰 Luxury"}
if use_budget_filter:
    selected_budgets = st.multiselect(
    "Budget",
    options=list(budget_map.keys()),
    format_func=lambda x: budget_map[x],
    default=[]
)
st.markdown("---")

use_description = st.toggle("Use my own description 🤓", value=True)
user_query = ""
if use_description:
    user_query = st.text_area(
    "🔥✍️ Describe your destination:",
    placeholder="Example: Quiet town near the sea with museums"
)

top_k = st.number_input(
    "Amount of results",
    min_value=1,
    max_value=5,
    value=3,
    step=1,
    format="%d"
)


if st.button("Search🔎") and user_query.strip():
    loading_placeholder = st.empty()
    lottie_loading_url = "https://assets10.lottiefiles.com/packages/lf20_ydo1amjm.json"
    lottie_loading = load_lottieurl(lottie_loading_url)

    with loading_placeholder.container():
        st.markdown("<h3 style='text-align: center;'>🧭Working on it... Get ready for your travel🧳</h3>", unsafe_allow_html=True)
        if lottie_loading:
            st_lottie(lottie_loading, speed=1, height=140, key="loading")

    results_api = get_prediction(user_query, top_k)
    results = results_api.json()['predictions']
    loading_placeholder.empty()

    #if results:
        #df = pd.DataFrame(results)

        # Aplicar filtro de región
        #df_filtered = df
        #if selected_regions:
            #df_filtered = df[df_filtered['region'].isin(selected_regions)]

        # Aplicar filtro de seclusion
        #df_filtered = df_filtered[
            #(df_filtered['seclusion'] >= seclusion_range[0]) &
            #(df_filtered['seclusion'] <= seclusion_range[1])
        #]

        # Aplicar filtro de budget
        #if selected_budgets:
            #df_filtered = df_filtered[df_filtered['budget_level'].isin(selected_budgets)]

        #final_results = df_filtered.to_dict('records')
    #else:
        #final_results = []


    st.markdown("<h2>Here you have😁🌟</h2>", unsafe_allow_html=True)

    #for r in final_results:
    for r in results:
            #image_path_jpg = f"images/{r['id']}.jpg"
            #image_path_png = f"images/{r['id']}.png"

            #if os.path.exists(image_path_jpg):
                #st.image(image_path_jpg, use_column_width=True)
            #elif os.path.exists(image_path_png):
                #st.image(image_path_png, use_column_width=True)
            #MOSTRAR IMAGEN LOCAL

            st.markdown(f"### **📍 {r['city']}")
            st.markdown(f"**🌐 Country:** {r['country']}")
            st.markdown(f"**📝 About it:** {r['short_description']}")
            st.markdown(f"**👤 Seclusion:** {'👤' * r['seclusion']}")
            st.markdown(f"**💸 Budget:** {budget_map[r['budget_level']]}")
            st.markdown("---")
            time.sleep(.7)

    map_df = pd.DataFrame([{"lat": r["latitude"], "lon": r["longitude"]} for r in results])
    st.map(map_df)

    lottie_travel_url = "https://assets10.lottiefiles.com/packages/lf20_ydo1amjm.json"
    lottie_travel = load_lottieurl(lottie_travel_url)
    if lottie_travel:
        st_lottie(lottie_travel, speed=1, height=300, key="travel")

    st.markdown("<h2 style='text-align: center;'>Enjoy your travel! 😎🎒</h2>", unsafe_allow_html=True)
