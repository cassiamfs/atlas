import streamlit as st
import pandas as pd
import requests
from streamlit_lottie import st_lottie
import time

clusters_df = pd.read_csv("frontend/60_clusters.csv")
#import os
#import json
#from streamlit_oauth import OAuth2Component
#import google.oauth2.credentials
#from google.cloud import firestore

#def get_prediction(query, top_k, regions=None, budget=None, seclusion=None):
    #params = {'query': query, 'top_k': top_k}
    #if regions:
        #params['regions'] = regions
    #if budget:
        #params['budget'] = budget
    #if seclusion:
        #params['seclusion_min'] = seclusion[0]
        #params['seclusion_max'] = seclusion[1]

    #base_url = 'https://atlas-626932554468.europe-southwest1.run.app/'

    #response = requests.get(f'{base_url}/predict_city', params=params)
    #return response

    #def get_alternatives_by_cluster(cluster_id, exclude_id):
    #params = {
        #'cluster_id': cluster_id,
        #'exclude_id': exclude_id,
        #'count': 2 #Alternatives amount
    #}
    #base_url = 'https://atlas-917734968327.europe-southwest1.run.app'

    #try:
        #response = requests.get(f'{base_url}/alternatives_by_cluster', params=params)
        #if response.status_code == 200:
            #return response.json().get('alternatives', [])
    #except requests.exceptions.RequestException as e:
        #st.error(f"Error{e}")

    #return []

#FUNCTIONS

def analyze_cities(data):

    # Dictionary to store all information about each city
    # Structure: {city_name: {'categories': {category: [ratings]}, 'all_ratings': [all_ratings]}}
    city_data = {}

    # STEP 1: Collect all city data from the input
    for category, content in data.items():
        # Skip if category doesn't have predictions (safety check)
        if 'predictions' not in content:
            continue

        # Process each place in this category
        for place in content['predictions']:
            city = place['city']
            rating = place['rating']

            # Initialize city entry if it doesn't exist
            if city not in city_data:
                city_data[city] = {'categories': {}, 'all_ratings': []}

            # Initialize category list for this city if it doesn't exist
            if category not in city_data[city]['categories']:
                city_data[city]['categories'][category] = []

            # Store the rating in both category-specific and overall lists
            city_data[city]['categories'][category].append(rating)
            city_data[city]['all_ratings'].append(rating)

    # Initialize results dictionary
    results = {
        'counts': {},           # How many places each city has per category
        'best_per_category': {},  # Best city for each category
        'overall_best': None    # Best city overall
    }

    # STEP 2: Count how many places each city has in each category
    for category in data.keys():
        if 'predictions' in data[category]:
            city_counts = {}  # Will store {city: count} for this category

            # Count places for each city in this category
            for place in data[category]['predictions']:
                city = place['city']
                city_counts[city] = city_counts.get(city, 0) + 1

            results['counts'][category] = city_counts

    # STEP 3: Find the best city for each category (highest average rating)
    for category in data.keys():
        if 'predictions' not in data[category]:
            continue

        best_city = None
        best_avg = 0

        # Check each city that appears in this category
        for city, info in city_data.items():
            if category in info['categories']:
                # Calculate average rating for this city in this category
                ratings_in_category = info['categories'][category]
                avg = sum(ratings_in_category) / len(ratings_in_category)

                # Update best city if this one is better
                if avg > best_avg:
                    best_avg = avg
                    best_city = city

        # Store the best city info if we found one
        if best_city:
            results['best_per_category'][category] = {
                'city': best_city,
                'avg_rating': round(best_avg, 2),
                'count': len(city_data[best_city]['categories'][category])
            }

    # STEP 4: Find overall best city (highest average across ALL categories)
    best_city = None
    best_avg = 0

    # Check each city's overall performance
    for city, info in city_data.items():
        # Calculate average of ALL ratings for this city
        overall_avg = sum(info['all_ratings']) / len(info['all_ratings'])

        # Update best city if this one is better
        if overall_avg > best_avg:
            best_avg = overall_avg
            best_city = city

    # Store overall best city information
    results['overall_best'] = {
        'city': best_city,
        'avg_rating': round(best_avg, 2),
        'total_places': len(city_data[best_city]['all_ratings']),
        'categories': list(city_data[best_city]['categories'].keys())
    }

    return results

def get_prediction(query, top_k, restaurant_review, museum_review, thing_to_do, park_review):
    response = requests.get('https://atlas-518816232020.europe-southwest1.run.app/search_all_in_one', params = {'city_query': query, 'top_k_places': top_k, 'restaurant_review': restaurant_review, 'museum_review': museum_review, 'thing_to_do': thing_to_do, 'park_review': park_review, 'top_k_reviews': 50})
    return response

def add_bg_from_url():
    st.markdown(
         f"""
         <style>
         .stApp {{ background-image: url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1172&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
         background-size: cover; background-position: center; background-repeat: no-repeat; }}
         h1, h2, h3, p, label, .stMarkdown {{ color: white !important; text-shadow: -2px -2px 0 #000033, 2px -2px 0 #000033, -2px 2px 0 #000033, 2px 2px 0 #000033, -2px 0px 0 #000033, 2px 0px 0 #000033, 0px -2px 0 #000033, 0px 2px 0 #000033; }}
         textarea, .stTextArea textarea {{ background-color: rgba(255, 255, 255, 0.9) !important; color: black !important; border: 1px solid white !important; }}
         textarea::placeholder {{ color: black !important; opacity: 0.4 !important; }}
         .stNumberInput input {{ background-color: rgba(255, 255, 255, 0.9) !important; color: black !important; border: 1px solid white !important; }}
         div.stButton > button {{ background-color: rgba(0, 0, 0, 0.7) !important; color: white !important; border: 1px solid white !important; }}
         div.stButton > button:hover *{{ background-color: rgba(255, 255, 255, 0.7) !important; color: rgba(0, 0, 0, 1) !important; text-shadow: none !important; }}
         @keyframes fadeIn {{ from {{opacity: 0; transform: translateY(20px);}}
        to {{opacity: 1; transform: translateY(0);}} }} h1, h2, h3 {{ animation: fadeIn 1s ease-in-out; }}
        .stButton > button {{ transition: all 0.3s ease-in-out; }} .stButton > button:hover {{ transform: scale(1.1); }}
         </style>
         """, unsafe_allow_html=True)

def load_lottieurl(url):
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()

# Web details
add_bg_from_url()
st.set_page_config(page_title="Atlas Roots", page_icon="🌎", layout="wide")

if 'page' not in st.session_state:
    st.session_state.page = 'welcome'

#PÁGINA 1: BIENVENIDA
if st.session_state.page == 'welcome':

    st.markdown("<h1 style='text-align: center; font-size: 8em;'>Atlas Roots🌍</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; font-size: 2em;'>Find cities based on your description with AI✨</h2>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("Get started!🚀", use_container_width=True):
            st.session_state.page = 'search'
            st.rerun()

#PÁGINA 2: BÚSQUEDA
elif st.session_state.page == 'search':

    st.header("Find your next destination ✈️")
    st.markdown("Use the filters and describe your ideal place to discover")

    #FILTROS
    st.markdown("---")


    use_region_filter = st.toggle("Filter by Region 🗺️")
    selected_regions = []
    region_map = {
        1: 'North America',
        2: 'South America',
        3: 'Asia',
        4: 'Oceania',
        5: 'Europe',
        6: 'Africa',
        7: 'Middle East'
    }

    if use_region_filter:
        st.write("Select Regions:")

        # The fourth column is to push the others to the left
        col1, col2, col3, _ = st.columns([1, 1, 1, 4])

        columns = [col1, col2, col3]

        for idx, (region_id, region_name) in enumerate(region_map.items()):
            col = columns[idx % len(columns)]
            if col.checkbox(region_name, key=f"region_{region_id}"):
                selected_regions.append(region_id)

    use_seclusion_filter = st.toggle("👤 Level of Quieteness")
    seclusion_range = (1, 5)
    if use_seclusion_filter:
        col1, _ = st.columns([2, 5])
        with col1:
            seclusion_range = st.slider(
                "1: Less Quiet ←→ 5: Very Quiet",
                min_value=1,
                max_value=5,
                value=(1, 5)
            )


    use_budget_filter = st.toggle("Filter by Budget 💸")
    selected_budgets = []
    budget_map = {
        1: "💰 Low Budget",
        2: "💰💰 Mid Range",
        3: "💰💰💰 Luxury"
    }

    if use_budget_filter:
        st.write("Select Budget:")
        col1, col2, _ = st.columns([1, 1, 5])
        columns = [col1, col2]

        for idx, (budget_id, budget_label) in enumerate(budget_map.items()):
            col = columns[idx % len(columns)]
            if col.checkbox(budget_label, key=f"budget_{budget_id}"):
                selected_budgets.append(budget_id)

    st.markdown("---")

    #FULL DESCRIPTION
    use_description = st.toggle("Use my own words 🤓", value=True)
    user_query = ""

    if use_description:
        max_chars = 150
        user_query = st.text_area(
            "🔥✍️ Describe your destination:", value = 'Small city on the beach',
            placeholder="Example: Quiet town near the sea with museums",
            height=100
        )

        char_count = len(user_query)
        if char_count > max_chars:
            st.error(f"We recommend using a maximum of 150 characters. You are using {char_count}")
        else:
            st.write(f"✅")

    #RESTAURANTS DESCRIPTION
    use_description_rest = st.toggle("Restaurants 🍽️", value=True)
    user_query = ""

    if use_description_rest:
        max_chars = 150
        user_query = st.text_area(
            "✍️ Here you can specify about cuisine:",
            placeholder="Example: Asian food", value='Italian food',
            height=100
        )

        char_count = len(user_query)
        if char_count > max_chars:
            st.error(f"We recommend using a maximum of 150 characters. You are using {char_count}")
        else:
            st.write(f"✅")

    #MUSEUMS DESCRIPTION
    use_description_museum = st.toggle("Museums 🏛️", value=False)
    user_query = ""

    if use_description_museum:
        max_chars = 150
        user_query = st.text_area(
            "✍️ Here you can specify about museums:",
            placeholder="Example: Modern Art",
            height=100
        )

        char_count = len(user_query)
        if char_count > max_chars:
            st.error(f"We recommend using a maximum of 150 characters. You are using {char_count}")
        else:
            st.write(f"✅")

    #ACTIVITIES DESCRIPTION
    use_description_tdt = st.toggle("Things to do ", value=False)
    user_query = ""

    if use_description_tdt:
        max_chars = 150
        user_query = st.text_area(
            "✍️ Here you can specify about activities:",
            placeholder="Example: Kayak",
            height=100
        )

        char_count = len(user_query)
        if char_count > max_chars:
            st.error(f"We recommend using a maximum of 150 characters. You are using {char_count}")
        else:
            st.write(f"✅")

    #PARKS DESCRIPTION
    use_description_park = st.toggle("Parks ", value=False)
    user_query = ""

    if use_description_park:
        max_chars = 150
        user_query = st.text_area(
            "✍️ Here you can specify about parks:",
            placeholder="Example: Green Fresh Parks",
            height=100
        )

        char_count = len(user_query)
        if char_count > max_chars:
            st.error(f"We recommend using a maximum of 150 characters. You are using {char_count}")
        else:
            st.write(f"✅")

    col1, col2 = st.columns([1, 9])
    with col1:
        top_k = st.number_input(
            "Amount of results",
            min_value=1,
            max_value=5,
            value=3,
            step=1,
            format="%d"
        )

    #FIND CITIES (Button for search)
    if st.button("Search🔎"):
        st.write('search was pressed')
        loading_placeholder = st.empty()
        lottie_loading_url = "https://assets5.lottiefiles.com/packages/lf20_1pxqjqps.json"
        lottie_loading = load_lottieurl(lottie_loading_url)

        with loading_placeholder.container():
            st.markdown("<h3 style='text-align: center;'>🧭Working on it... Get ready for your travel🧳</h3>", unsafe_allow_html=True)
            if lottie_loading:
                #Columns work as empty margins so the animation is centered
                col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 1, 1, 1, 1, 1, 1])
                with col4:
                    if lottie_loading:
                        st_lottie(
                            lottie_loading,
                            speed=1,
                            height=150,
                            key="loading"
                        )

        #results_api = get_prediction(user_query, top_k, selected_regions, selected_budgets, seclusion_range)
        #loading_placeholder.empty()

        #st.session_state.results = results_api.json().get('predictions', [])

        results_api = get_prediction(user_query, museum_review=use_description_museum, park_review=use_description_park, thing_to_do=use_description_tdt, restaurant_review=use_description_rest, top_k = top_k)
        results = results_api.json()
        st.write(results)
        best_cities = analyze_cities(results)
        loading_placeholder.empty()

        st.write(best_cities)

        st.markdown("<h2>Here you have😁🌟</h2>", unsafe_allow_html=True)

        best_restaurant_city = best_cities["best_per_category"]["restaurants"]
        brc_name = best_restaurant_city["city"]

        brc_row = clusters_df.loc[clusters_df.city== brc_name]
        st.dataframe(brc_row)

        brc_rating =  best_restaurant_city["avg_rating"]
        brc_count = best_restaurant_city["count"]

        st.header("Best city for restaurants")
        st.text(brc_name)
        st.text(f"Rating {brc_rating}")
        st.text(f"Count {brc_count}")

        restaurnt_reviews = results["restaurants"]["predictions"]
        brc_reviews = [review for review in restaurnt_reviews if review["city"] ==  brc_name]
        for review in brc_reviews:
            st.text(review["name_place"])
            st.text(review["review"])

        #SHOW RESULTS
        #for i, r in enumerate(st.session_state.results):
        #for i, r in enumerate (best_cities):
            #col1, col2 = st.columns([1, 2]) # Imagen y Texto

            #with col1:
                #image_path = f"images/{r['id']}.jpg"
                #st.image(image_path, use_column_width=True)

            #with col2:
            #st.markdown(f"""
            #<div style='animation: fadeIn 1s ease-in-out {i*0.5}s forwards; opacity:0;'>
                #<h3> ### 📍 {r['city']}</h3>
                #<hr>
            #</div>
            #""", unsafe_allow_html=True)
                #st.markdown(f"🌐 Country: {r['country']}")
                #st.markdown(f"📝 About it: {r['short_description']}")
                #st.markdown(f"👤 Seclusion: {r['seclusion']}")
                #st.markdown(f"💸 Budget: {budget_map[r['budget_level']]}")

                # Alternatives button
                #if st.button(f"Show similar alternatives", key=f"alt_{r['id']}"):
                    #alternatives = get_alternatives_by_cluster(r['cluster'], r['id'])
                    #st.session_state.alternatives[r['id']] = alternatives

                # Show Alternatives
                #if r['id'] in st.session_state.alternatives:
                    #with st.expander("✨ Similar Options"):
                        #alternatives_list = st.session_state.alternatives[r['id']]
                        #if alternatives_list:
                            #for alt in alternatives_list:
                                #st.markdown(f" {alt.get('city', 'N/A')}, {alt.get('country', 'N/A')}: {alt.get('short_description', '')}")
                        #else:
                            #st.write("No other similar options were found in our database.")
            #st.markdown("---")
            #time.sleep(.4)

        #SHOW MAP with the results
        #map_df = pd.DataFrame([{"lat": r["latitude"], "lon": r["longitude"]} for r in st.session_state.results])
        map_df = pd.DataFrame([{"lat": r["latitude"], "lon": r["longitude"]} for r in results])
        st.map(map_df)

        #https://assets5.lottiefiles.com/packages/lf20_1pxqjqps.json #robot - funciona
        #https://assets10.lottiefiles.com/packages/lf20_ydo1amjm.json #astronauta - funciona

        lottie_travel_url = "https://assets10.lottiefiles.com/packages/lf20_ydo1amjm.json"
        lottie_travel = load_lottieurl(lottie_travel_url)
        col1_b, col2_b, col3_b = st.columns([1, 1, 1])
        with col2_b:
            if lottie_travel:
                st_lottie(
                    lottie_travel,
                    speed=1,
                    height=300,
                    key="travel"
                )


        #st.markdown(""" #<div style='text-align: center;'>
                    #<h2>Enjoy your travel and thanks for trusting us</h2>
                    #<div style='font-size: 4em;'>😎🎒</div>
                    #</div> """, unsafe_allow_html=True)
