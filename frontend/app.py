import streamlit as st
import pandas as pd
import requests
from streamlit_lottie import st_lottie
import time
import os

clusters_df = pd.read_csv("frontend/df_new.csv")


# FUNCTIONS
def get_alternatives_by_cluster(cluster_id, exclude_id):
    params = {
        "cluster_id": cluster_id,
        "exclude_id": exclude_id,
        "count": 2,  # Alternatives amount
    }
    base_url = "https://atlas-518816232020.europe-southwest1.run.app/search_all_in_one"

    try:
        response = requests.get(f"{base_url}/alternatives_by_cluster", params=params)
        if response.status_code == 200:
            return response.json().get("alternatives", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error{e}")

    return []


def analyze_cities(data):
    # Dictionary to store all information about each city
    # Structure: {city_name: {'categories': {category: [ratings]}, 'all_ratings': [all_ratings]}}
    city_data = {}

    # STEP 1: Collect all city data from the input
    for category, content in data.items():
        # Skip if category doesn't have predictions or is empty
        if not content or "predictions" not in content or not content["predictions"]:
            continue

        # Process each place in this category
        for place in content["predictions"]:
            city = place["city"]
            rating = place["rating"]

            # Initialize city entry if it doesn't exist
            if city not in city_data:
                city_data[city] = {"categories": {}, "all_ratings": []}

            # Initialize category list for this city if it doesn't exist
            if category not in city_data[city]["categories"]:
                city_data[city]["categories"][category] = []

            # Store the rating in both category-specific and overall lists
            city_data[city]["categories"][category].append(rating)
            city_data[city]["all_ratings"].append(rating)

    # Initialize results dictionary
    results = {
        "counts": {},  # How many places each city has per category
        "best_per_category": {},  # Best city for each category
        "overall_best": None,  # Best city overall
    }

    # Return empty results if no data found
    if not city_data:
        return results

    # STEP 2: Count how many places each city has in each category
    for category, content in data.items():
        if content and "predictions" in content and content["predictions"]:
            city_counts = {}  # Will store {city: count} for this category

            # Count places for each city in this category
            for place in content["predictions"]:
                city = place["city"]
                city_counts[city] = city_counts.get(city, 0) + 1

            results["counts"][category] = city_counts

    # STEP 3: Find the best city for each category (highest average rating)
    for category, content in data.items():
        if not content or "predictions" not in content or not content["predictions"]:
            continue

        best_city = None
        best_avg = 0

        # Check each city that appears in this category
        for city, info in city_data.items():
            if category in info["categories"]:
                # Calculate average rating for this city in this category
                ratings_in_category = info["categories"][category]
                avg = sum(ratings_in_category) / len(ratings_in_category)

                # Update best city if this one is better
                if avg > best_avg:
                    best_avg = avg
                    best_city = city

        # Store the best city info if we found one
        if best_city:
            results["best_per_category"][category] = {
                "city": best_city,
                "avg_rating": round(best_avg, 2),
                "count": len(city_data[best_city]["categories"][category]),
            }

    # STEP 4: Find overall best city (highest average across ALL categories)
    best_city = None
    best_avg = 0

    # Check each city's overall performance
    for city, info in city_data.items():
        # Calculate average of ALL ratings for this city
        if info["all_ratings"]:  # Make sure there are ratings
            overall_avg = sum(info["all_ratings"]) / len(info["all_ratings"])

            # Update best city if this one is better
            if overall_avg > best_avg:
                best_avg = overall_avg
                best_city = city

    # Store overall best city information
    if best_city:
        results["overall_best"] = {
            "city": best_city,
            "avg_rating": round(best_avg, 2),
            "total_places": len(city_data[best_city]["all_ratings"]),
            "categories": list(city_data[best_city]["categories"].keys()),
        }

    return results


def get_prediction(
    query,
    top_k,
    restaurant_review,
    museum_review,
    thing_to_do,
    park_review,
    seclusion,
    budget_level,
):
    response = requests.get(
        "https://atlas-518816232020.europe-southwest1.run.app/search_all_in_one",
        params={
            "city_query": query,
            "top_k_places": top_k,
            "restaurant_review": restaurant_review,
            "museum_review": museum_review,
            "thing_to_do": thing_to_do,
            "park_review": park_review,
            "top_k_reviews": 50,
            "seclusion": seclusion,
            "budget_level": budget_level,
        },
    )
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
         """,
        unsafe_allow_html=True,
    )


# Web details
add_bg_from_url()
st.set_page_config(page_title="Atlas Roots", page_icon="🌎", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "welcome"

# PÁGINA 1: BIENVENIDA
if st.session_state.page == "welcome":

    st.markdown(
        "<h1 style='text-align: center; font-size: 8em;'>Atlas Roots🌍</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h2 style='text-align: center; font-size: 2em;'>Find cities based on your description with AI✨</h2>",
        unsafe_allow_html=True,
    )
    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("Get started!🚀", use_container_width=True):
            st.session_state.page = "search"
            st.rerun()

# PÁGINA 2: BÚSQUEDA
elif st.session_state.page == "search":

    st.header("Find your next destination ✈️")
    st.markdown("Use the filters and describe your ideal place to discover")

    # FILTROS
    st.markdown("---")

    use_region_filter = st.toggle("Filter by Region 🗺️")
    selected_regions = []
    region_map = {
        1: "North America",
        2: "South America",
        3: "Asia",
        4: "Oceania",
        5: "Europe",
        6: "Africa",
        7: "Middle East",
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
                "1: Less Quiet ←→ 5: Very Quiet", min_value=1, max_value=5, value=(1, 5)
            )
            start, end = seclusion_range
            seclusion_range = [str(each) for each in range(start, end + 1)]
            seclusion_range = ",".join(seclusion_range)

    use_budget_filter = st.toggle("Filter by Budget 💸")
    selected_budgets = []
    budget_map = {1: "💰 Low Budget", 2: "💰💰 Mid Range", 3: "💰💰💰 Luxury"}

    if use_budget_filter:
        st.write("Select Budget:")
        col1, col2, _ = st.columns([1, 1, 5])
        columns = [col1, col2]

        for idx, (budget_id, budget_label) in enumerate(budget_map.items()):
            col = columns[idx % len(columns)]
            if col.checkbox(budget_label, key=f"budget_{budget_id}"):
                selected_budgets.append(str(budget_id))
        selected_budgets = ",".join(selected_budgets)

    st.markdown("---")

    # FULL DESCRIPTION
    use_description = st.toggle("Use my own words 🤓", value=True)
    user_query = ""

    if use_description:
        max_chars = 150
        user_query = st.text_area(
            "🔥✍️ Describe your destination:",
            value="Small city on the beach",
            placeholder="Example: Quiet town near the sea with museums",
            height=100,
        )

        char_count = len(user_query)
        if char_count > max_chars:
            st.error(
                f"We recommend using a maximum of 150 characters. You are using {char_count}"
            )
        else:
            st.write(f"✅")

    # RESTAURANTS DESCRIPTION
    use_description_rest = st.toggle("Restaurants 🍽️", value=True)
    user_query = ""

    if use_description_rest:
        max_chars = 150
        user_query = st.text_area(
            "✍️ Here you can specify about cuisine:",
            placeholder="Example: Asian food",
            value="Italian food",
            height=100,
        )

        char_count = len(user_query)
        if char_count > max_chars:
            st.error(
                f"We recommend using a maximum of 150 characters. You are using {char_count}"
            )
        else:
            st.write(f"✅")

    # MUSEUMS DESCRIPTION
    use_description_museum = st.toggle("Museums 🏛️", value=False)
    user_query = ""

    if use_description_museum:
        max_chars = 150
        user_query = st.text_area(
            "✍️ Here you can specify about museums:",
            placeholder="Example: Modern Art",
            height=100,
        )

        char_count = len(user_query)
        if char_count > max_chars:
            st.error(
                f"We recommend using a maximum of 150 characters. You are using {char_count}"
            )
        else:
            st.write(f"✅")

    # ACTIVITIES DESCRIPTION
    use_description_tdt = st.toggle("Things to do ⛸️🏄", value=False)
    user_query = ""

    if use_description_tdt:
        max_chars = 150
        user_query = st.text_area(
            "✍️ Here you can specify about activities:",
            placeholder="Example: Kayak",
            height=100,
        )

        char_count = len(user_query)
        if char_count > max_chars:
            st.error(
                f"We recommend using a maximum of 150 characters. You are using {char_count}"
            )
        else:
            st.write(f"✅")

    # PARKS DESCRIPTION
    use_description_park = st.toggle("Parks 🏞️", value=False)
    user_query = ""

    if use_description_park:
        max_chars = 150
        user_query = st.text_area(
            "✍️ Here you can specify about parks:",
            placeholder="Example: Green Fresh Parks",
            height=100,
        )

        char_count = len(user_query)
        if char_count > max_chars:
            st.error(
                f"We recommend using a maximum of 150 characters. You are using {char_count}"
            )
        else:
            st.write(f"✅")

    col1, col2 = st.columns([1, 9])
    with col1:
        top_k = st.number_input(
            "Amount of results", min_value=1, max_value=5, value=3, step=1, format="%d"
        )

    # FIND CITIES (Button for search)
    if st.button("Search🔎"):
        loading_placeholder = st.empty()
        with loading_placeholder.container():
            st.markdown(
                "<h3 style='text-align: center;'>🧭Working on it... Get ready for your travel🧳</h3>",
                unsafe_allow_html=True,
            )

        # results_api = get_prediction(user_query, top_k, selected_regions, selected_budgets, seclusion_range)
        # loading_placeholder.empty()

        # st.session_state.results = results_api.json().get('predictions', [])

        results_api = get_prediction(
            user_query,
            museum_review=use_description_museum,
            park_review=use_description_park,
            thing_to_do=use_description_tdt,
            restaurant_review=use_description_rest,
            top_k=top_k,
            seclusion=seclusion_range,
            budget_level=selected_budgets,
        )
        results = results_api.json()
        # st.write(results)
        best_cities = analyze_cities(results)
        loading_placeholder.empty()

        all_city_names = best_cities["counts"]["restaurants"].keys()
        best_restaurant_city = best_cities["best_per_category"]["restaurants"]
        best_museum_city = best_cities["best_per_category"]["museum"]
        best_parks_city = best_cities["best_per_category"]["parks"]

        # st.write(best_cities)

        st.markdown("<h1>Here you have😁🌟</h1>", unsafe_allow_html=True)
        st.markdown(f"🏙️ Best City Overall → {best_cities["overall_best"]["city"]}")
        st.markdown(f"🍽️ Best Restaurants → {best_restaurant_city['city']}")
        st.markdown(f"🏛️ Best Museums → {best_museum_city['city']}")
        st.markdown(f"🏞️ Best Parks → {best_parks_city['city']}")
        st.markdown("---")
        st.markdown("<h1>Results💫</h1>", unsafe_allow_html=True)
        st.markdown("---")

        for city_name in all_city_names:
            col1, col2 = st.columns(2)  # Imagen y Texto

            # Name of the CITY
            brc_name = best_restaurant_city["city"]
            brc_row = clusters_df.loc[clusters_df.city == city_name]
            cluster = brc_row.cluster.values[0]
            brc_country = brc_row.country.values[0]
            brc_description = brc_row.short_description.values[0]
            brc_seclusion = brc_row.seclusion.values[0]
            brc_budget = brc_row.budget_level.values[0]
            brc_id = brc_row.id.values[0]

            # SHOW RESULTS
            with col1:
                st.markdown(
                    f"""
                    <div style='animation: fadeIn 1s ease-in-out 1s forwards; opacity:0;'>
                        <h1>📍 {city_name}</h1>
                        <h4>🌐 Country: {brc_country}</h4>
                        <h6>📝 {brc_description}</h6>
                        <h4>👤 Quietness Level: {brc_seclusion}/5 </h4>
                        <h4>💰 Budget: {brc_budget}</h4>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col2:
                for city_image_filename in os.listdir("frontend/Ciudades"):
                    if str(brc_id) in city_image_filename:
                        file = city_image_filename
                st.write(file)
                st.image(f"frontend/Ciudades/{file}")

            col_a, col_b, col_c, col_d, col_e = st.columns(5)  # Expanders para REVIEWS

            # THINGS TO DO
            with col_a:
                with st.expander(f"Things to do:"):
                    for_tdt = results["things to do"]["predictions"]
                    brc_for_tdt = [
                        review for review in for_tdt if review["city"] == city_name
                    ]
                    for review in brc_for_tdt:
                        st.markdown(
                            f"<h4>{review["name_place"]} with rating {review["rating"]}</h4>",
                            unsafe_allow_html=True,
                        )

            # RESTAURANT REVIEWS
            with col_b:
                with st.expander(f"Restaurant Reviews:"):
                    restaurnt_reviews = results["restaurants"]["predictions"]
                    brc_rest_reviews = [
                        review
                        for review in restaurnt_reviews
                        if review["city"] == brc_name
                    ]
                    for review in brc_rest_reviews:
                        st.markdown(
                            f"<h4>{review["name_place"]}</h4>", unsafe_allow_html=True
                        )
                        st.markdown(
                            f"<h6>{review["review"]}</h6>", unsafe_allow_html=True
                        )

            # MUSEUM REVIEWS
            with col_c:
                with st.expander(f"Museum Reviews:"):
                    museum_reviews = results["museum"]["predictions"]
                    brc_museum_reviews = [
                        review
                        for review in museum_reviews
                        if review["city"] == brc_name
                    ]
                    for review in brc_museum_reviews:
                        st.markdown(
                            f"<h4>{review["name_place"]}</h4>", unsafe_allow_html=True
                        )
                        st.markdown(
                            f"<h6>{review["review"]}</h6>", unsafe_allow_html=True
                        )

            # PARK REVIEWS
            with col_d:
                with st.expander(f"Park Reviews:"):
                    parks_reviews = results["parks"]["predictions"]
                    brc_parks_reviews = [
                        review for review in parks_reviews if review["city"] == brc_name
                    ]
                    for review in brc_parks_reviews:
                        st.markdown(
                            f"<h4>{review["name_place"]}</h4>", unsafe_allow_html=True
                        )
                        st.markdown(
                            f"<h6>{review["review"]}</h6>", unsafe_allow_html=True
                        )

            # ALTERNATIVES
            with col_e:
                with st.expander(f"Similar Cities:"):
                    similar_cities = [
                        each
                        for each in clusters_df.loc[
                            clusters_df.cluster == cluster
                        ].city.values
                        if each != city_name
                    ][:2]
                    st.markdown(
                        f"<h4>{",".join(similar_cities)}</h4>", unsafe_allow_html=True
                    )

            # st.dataframe(clusters_df.loc[clusters_df.cluster == cluster])
            # st.text(similar_cities)
            st.markdown("---")
            time.sleep(0.4)

        # brc_rest_rating =  best_restaurant_city["avg_rating"]
        # brc_rest_count = best_restaurant_city["count"]

        # -------------------------------------------------------------------------

        # st.write(best_cities)
        # st.write(results)

        # SHOW MAP with the results
        map_df = clusters_df.loc[clusters_df.city.isin(all_city_names)][
            ["latitude and longitude"]
        ]
        map_df["lat"] = clusters_df["latitude and longitude"].apply(
            lambda x: float(x.split(",")[0])
        )
        map_df["lon"] = clusters_df["latitude and longitude"].apply(
            lambda x: float(x.split(",")[1])
        )

        st.map(map_df[["lat", "lon"]])

        st.markdown(
            """ #<div style='text-align: center;'>
                    #<h2>Enjoy your travel and thanks for trusting us</h2>
                    #<div style='font-size: 4em;'>😎🎒</div>
                    #</div> """,
            unsafe_allow_html=True,
        )
