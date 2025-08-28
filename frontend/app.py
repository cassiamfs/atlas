import streamlit as st
import pandas as pd
#from atlas_roots.functions import get_data
import requests
#from atlas_roots.functions import search_places_df
from streamlit_lottie import st_lottie
import time

def get_prediction(query, top_k):
    response = requests.get('https://atlas-917734968327.europe-southwest1.run.app/predict_city', params = {'query': query, 'top_k': top_k})
    return response

def add_bg_from_url():
    st.markdown(
        f"""
        <style>
        /* Fondo general */
        .stApp {{
            background-image: url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1172&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}

        /* Colorear textos generales */
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {{
            color: white !important;
            text-shadow:
                -2px -2px 0 #000033,
                 2px -2px 0 #000033,
                -2px 2px 0 #000033,
                 2px 2px 0 #000033,
                -2px 0px 0 #000033,
                 2px 0px 0 #000033,
                 0px -2px 0 #000033,
                 0px 2px 0 #000033;
        }}

        /* Estilo para el text area */
        textarea, .stTextArea textarea {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            color: black !important;
            border: 1px solid white !important;
        }}

        /* Placeholder del text area */
        textarea::placeholder {{
            color: black !important;
            opacity: 0.4 !important;
        }}

        /* Estilo para el number input */
        .stNumberInput input {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            color: black !important;
            border: 1px solid white !important;
        }}

        /* Botón principal de Streamlit */
        div.stButton > button {{
            background-color: rgba(0, 0, 0, 0.7) !important; /* Fondo oscuro */
            color: white !important; /* Texto claro */
            border: 1px solid white !important;
        }}

        /* Hover del botón */
        div.stButton > button:hover *{{
            background-color: rgba(255, 255, 255, 0.7) !important; /* Fondo claro*/
            color: rgba(0, 0, 0, 1) !important; /* texto oscuro*/
            text-shadow: none !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def load_lottieurl(url):
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()

add_bg_from_url()

st.set_page_config(page_title="Atlas Roots", page_icon="🌎", layout="wide")

st.title("Atlas Roots🌍")
st.markdown("Find cities based on your description with AI✨")
st.markdown("Try your luck by getting a destination with us ✈️")

# ⚡ Cargamos el CSV automáticamente (sin que el usuario tenga que subirlo)
#df = get_data('/home/alonzo/code/alonz0gc/taxifare-website/cassiamfs/atlas/atlas_roots/.csv/filtered_cities_final.csv')

# Input de descripción del usuario
use_description = st.toggle("My own description 🤓", value=True)

# Region filtering
#use_region_filter = st.toggle("Filter by region 🗺️")

#selected_regions = []
#if use_region_filter:
    #all_regions = df['region'].unique().tolist()
    #selected_regions = st.multiselect("Choose regions:", options=all_regions, default=[])

#Box for description if activated
user_query = ""
if use_description:
    user_query = st.text_area(
        "🔥✍️ Describe your destination:",
        placeholder="Example: Quiet town near the sea with museums"
    )

top_k = st.number_input(
    "Results Amount",
    min_value=1,
    max_value=5,
    value=3,
    step=1,
    format="%d"
)

if st.button("Search🔎") and user_query.strip():
    with st.spinner("🧭Working on it... Get ready for your travel🧳"):

        #breakpoint()
        results_api = get_prediction(user_query, top_k)
        results = results_api.json()['predictions']
        #results = search_places_df(df, user_query, top_k)

    st.markdown(
    """
    <h2 style='
        color: white;
        text-shadow:
            -2px -2px 0 #000033,
             2px -2px 0 #000033,
            -2px  2px 0 #000033,
             2px  2px 0 #000033,
            -2px  0px 0 #000033,
             2px  0px 0 #000033,
             0px -2px 0 #000033,
             0px  2px 0 #000033;
    '>
        Here you have😁🌟
    </h2>
    """,
    unsafe_allow_html=True
)
    for r in results:
        st.markdown(f"""
        **📍 City:** {r['id']}""")
        st.markdown(f"""
        **🌐 Country:** {r['name']}""")
        st.markdown(f"""
        **📝 About it:** {r['description']}""")
        st.markdown(f"""
        **🔢 Score (This will not be in the final):** {r['score']:.2f}""")
        st.markdown(f"""
        """)
        time.sleep(.7)
        #breakpoint()
        map_df = pd.DataFrame([{"lat": r["latitude"], "lon": r["longitude"]} for r in results])


    # Show the map with possible destinations
    st.map(map_df)

    #Animation
    lottie_travel = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_ydo1amjm.json")

    st_lottie(lottie_travel, speed=1, height=300, key="travel")

    st.markdown(
    """
    <h2 style='
        text-align: center;
        color: white;
        text-shadow:
            -2px -2px 0 #000033,
             2px -2px 0 #000033,
            -2px  2px 0 #000033,
             2px  2px 0 #000033,
            -2px  0px 0 #000033,
             2px  0px 0 #000033,
             0px -2px 0 #000033,
             0px  2px 0 #000033;
    '>
        Enjoy your travel and thanks for trusting us
    </h2>
    <h1 style='text-align: center;'>😎🎒</h1>
    """,
    unsafe_allow_html=True
)
