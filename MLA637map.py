import streamlit as st
from streamlit_folium import folium_static
import mergin
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
import os
import shutil

# Set page config
st.set_page_config(
    page_title="Ecosystem Services Interactive Map",
    page_icon="🌍",
    layout="wide"
)

# Add title and description
st.title("Ecosystem Services Interactive Map")
st.markdown("""
This application displays ecosystem services data from the MLA637 project.
Use the sidebar to filter by user username and explore the data.
""")

# Sidebar controls
st.sidebar.header("Data Filters")

@st.cache_data(ttl=60)

# Function to download the Mergin Maps project
@st.cache_data
if st.button("Refresh Data"):
    st.cache_data.clear()
    st.experimental_rerun()
def download_mergin_project():
    # Define the directory path
    project_directory = './MLA637'

    # Check if the directory exists and remove it if it does
    if os.path.exists(project_directory):
        st.write(f"Removing existing directory: {project_directory}")
        shutil.rmtree(project_directory)

    # Show a status message during download
    with st.spinner("Downloading project data from Mergin Maps..."):
        try:
            # In a real app, you might want to handle credentials more securely
            # For example, using st.secrets or environment variables
            client = mergin.MerginClient(
                login=st.secrets["mergin_login"],
                password=st.secrets["mergin_password"]
            )
            client.download_project('MLA Workspace/MLA637', './MLA637')
            return True
        except Exception as e:
            st.error(f"Error downloading project: {e}")
            return False


# Function to load and process the GeoPackage data
@st.cache_data
def load_geodata():
    try:
        gdf = gpd.read_file('./MLA637/ecosystem_service.gpkg')
        if gdf.crs != 'EPSG:4326':
            gdf = gdf.to_crs(epsg=4326)

        # Fill NaN values in the relevant columns with an empty string before filtering
        gdf['provisioning_type'] = gdf['provisioning_type'].fillna('')
        gdf['regulating_type'] = gdf['regulating_type'].fillna('')
        gdf['cultural_type'] = gdf['cultural_type'].fillna('')
        gdf['supporting_type'] = gdf['supporting_type'].fillna('')

        return gdf
    except Exception as e:
        st.error(f"Error loading geodata: {e}")
        return None


# Define service layers with their metadata
def get_service_layers():
    return {
        # Provisioning Services
        'food': {'name': "Food", 'color': "green", 'icon': "utensils", 'category': 'provisioning',
                 'filter_col': 'provisioning_type', 'filter_val': '1'},
        'fibrefuel': {'name': "Fibre and Fuel", 'color': "brown", 'icon': "fire", 'category': 'provisioning',
                      'filter_col': 'provisioning_type', 'filter_val': '2'},
        'genetics': {'name': "Genetic Resources", 'color': "darkgreen", 'icon': "dna", 'category': 'provisioning',
                     'filter_col': 'provisioning_type', 'filter_val': '3'},
        'pharma': {'name': "Biochemicals & Pharmaceuticals", 'color': "darkred", 'icon': "prescription-bottle-medical",
                   'category': 'provisioning', 'filter_col': 'provisioning_type', 'filter_val': '4'},
        'ornamentals': {'name': "Ornamental Resources", 'color': "purple", 'icon': "leaf", 'category': 'provisioning',
                        'filter_col': 'provisioning_type', 'filter_val': '5'},
        'freshwater': {'name': "Fresh Water", 'color': "blue", 'icon': "tint", 'category': 'provisioning',
                       'filter_col': 'provisioning_type', 'filter_val': '6'},
        'minerals': {'name': "Minerals", 'color': "gray", 'icon': "mountain", 'category': 'provisioning',
                     'filter_col': 'provisioning_type', 'filter_val': '7'},

        # Regulating Services
        'airquality': {'name': "Air Quality Regulation", 'color': "lightblue", 'icon': "wind", 'category': 'regulating',
                       'filter_col': 'regulating_type', 'filter_val': '1'},
        'climate': {'name': "Climate Regulation", 'color': "darkblue", 'icon': "cloud-sun", 'category': 'regulating',
                    'filter_col': 'regulating_type', 'filter_val': '2'},
        'water': {'name': "Water Regulation", 'color': "cyan", 'icon': "water", 'category': 'regulating',
                  'filter_col': 'regulating_type', 'filter_val': '3'},
        'hazards': {'name': "Natural Hazard Regulation", 'color': "red", 'icon': "exclamation-triangle",
                    'category': 'regulating', 'filter_col': 'regulating_type', 'filter_val': '4'},
        'pests': {'name': "Pest & Disease Regulation", 'color': "orange", 'icon': "bug", 'category': 'regulating',
                  'filter_col': 'regulating_type', 'filter_val': '5'},
        'waterpurity': {'name': "Water Purification", 'color': "lightcyan", 'icon': "filter", 'category': 'regulating',
                        'filter_col': 'regulating_type', 'filter_val': '6'},
        'pollination': {'name': "Pollination", 'color': "yellow", 'icon': "seedling", 'category': 'regulating',
                        'filter_col': 'regulating_type', 'filter_val': '7'},

        # Cultural Services
        'heritage': {'name': "Cultural Heritage", 'color': "darkred", 'icon': "landmark", 'category': 'cultural',
                     'filter_col': 'cultural_type', 'filter_val': '1'},
        'recreation': {'name': "Recreation & Tourism", 'color': "orange", 'icon': "hiking", 'category': 'cultural',
                       'filter_col': 'cultural_type', 'filter_val': '2'},
        'aesthetics': {'name': "Aesthetic Value", 'color': "pink", 'icon': "image", 'category': 'cultural',
                       'filter_col': 'cultural_type', 'filter_val': '3'},
        'religion': {'name': "Spiritual & Religious Value", 'color': "purple", 'icon': "place-of-worship",
                     'category': 'cultural', 'filter_col': 'cultural_type', 'filter_val': '4'},

        # Supporting Services
        'soilform': {'name': "Soil Formation", 'color': "saddlebrown", 'icon': "layer-group", 'category': 'supporting',
                     'filter_col': 'supporting_type', 'filter_val': '1'},
        'primaryprod': {'name': "Primary Production", 'color': "darkgreen", 'icon': "sun", 'category': 'supporting',
                        'filter_col': 'supporting_type', 'filter_val': '2'},
        'nutcycling': {'name': "Nutrient Cycling", 'color': "olive", 'icon': "recycle", 'category': 'supporting',
                       'filter_col': 'supporting_type', 'filter_val': '3'},
        'watercycling': {'name': "Water Cycling", 'color': "darkblue", 'icon': "sync", 'category': 'supporting',
                         'filter_col': 'supporting_type', 'filter_val': '4'},
        'photo': {'name': "Photosynthesis", 'color': "lime", 'icon': "leaf", 'category': 'supporting',
                  'filter_col': 'supporting_type', 'filter_val': '5'}
    }


# Function to create filtered dataframe for a specific service
def create_filtered_dataframe(gdf, service_config):
    return gdf[gdf[service_config['filter_col']].str.contains(service_config['filter_val'])]


# Function to filter data by selected usernames
def filter_by_users(gdf, selected_users):
    if not selected_users or 'All Users' in selected_users:
        return gdf
    else:
        # Assuming there's a column called 'username' or similar - adjust as needed
        # First, determine which column contains usernames
        user_column = 'Name, initials or username'

        # Check if the column exists, fallback to other possibilities if not
        if user_column not in gdf.columns:
            possible_columns = ['username', 'user', 'collector', 'surveyor', 'author', 'created_by']
            user_column = None
            for col in possible_columns:
                if col in gdf.columns:
                    user_column = col
                    break

        if user_column:
            return gdf[gdf[user_column].isin(selected_users)]
        else:
            st.warning("No user column found in data. Available columns: " + ", ".join(gdf.columns))
            return gdf


# Function to create the map
def create_map(gdf, service_layers):
    # Get the center of the data for map initialization
    center_lat = gdf.geometry.centroid.y.mean()
    center_lon = gdf.geometry.centroid.x.mean()

    # Create the map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=10,
        tiles='OpenStreetMap'
    )

    # Function to add a layer to the map
    def add_marker_layer(gdf, service_key, service_config):
        if gdf.empty:
            return None

        # Create a marker cluster for this layer
        marker_cluster = MarkerCluster(name=service_config['name'])

        # Add each point to the cluster
        for idx, row in gdf.iterrows():
            # Get the point coordinates
            if row.geometry is None or row.geometry.is_empty:
                continue

            try:
                lat = row.geometry.y
                lon = row.geometry.x

                # Create popup content
                popup_content = f"<b>{service_config['name']}</b><br>"
                for col in row.index:
                    if col != 'geometry' and not pd.isna(row[col]):
                        popup_content += f"{col}: {row[col]}<br>"

                # Create marker
                icon = folium.Icon(color=service_config['color'], icon=service_config['icon'], prefix='fa')
                marker = folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=icon
                )
                marker.add_to(marker_cluster)

            except Exception as e:
                st.error(f"Error adding marker: {e}")

        return marker_cluster

    # Add all service layers to the map
    for service_key, service_config in service_layers.items():
        filtered_gdf = create_filtered_dataframe(gdf, service_config)
        layer = add_marker_layer(filtered_gdf, service_key, service_config)
        if layer:
            layer.add_to(m)

    # Add layer control
    folium.LayerControl(collapsed=False).add_to(m)

    # Add a legend
    legend_html = '''
    <div style="position: fixed;
                bottom: 50px; left: 50px; width: 180px;
                background-color: white; z-index:9999; font-size:14px;
                padding: 10px; border-radius: 5px; border: 2px solid grey;">
        <h4>Ecosystem Services</h4>
        <div style="color: green;">● Provisioning</div>
        <div style="color: blue;">● Regulating</div>
        <div style="color: orange;">● Cultural</div>
        <div style="color: brown;">● Supporting</div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    return m


# Main app flow
if 'data_downloaded' not in st.session_state:
    st.session_state.data_downloaded = False

# Display a button to trigger the download
if not st.session_state.data_downloaded:
    if st.sidebar.button("Download MLA637 Data"):
        st.session_state.data_downloaded = download_mergin_project()

# If the data is downloaded, load it and display the map
if st.session_state.data_downloaded:
    gdf = load_geodata()

    if gdf is not None:
        # Get service layer definitions
        service_layers = get_service_layers()

        # Username filter in sidebar
        st.sidebar.header("Filter by User")

        # Get unique usernames from the data
        user_column = 'Your name'

        if user_column in gdf.columns:
            # Get unique users, excluding NaN values
            unique_users = sorted([user for user in gdf[user_column].dropna().unique() if user])

            # Add "All Users" option
            user_options = ['All Users'] + unique_users

            # Multi-select for users
            selected_users = st.sidebar.multiselect(
                "Select users to display:",
                options=user_options,
                default=['All Users'],
                help="Choose one or more users to filter the data. Select 'All Users' to show everyone's data."
            )

            # Filter the data by selected users
            filtered_gdf = filter_by_users(gdf, selected_users)

        else:
            st.sidebar.warning(f"Column '{user_column}' not found in the data")
            st.sidebar.write("Available columns:", gdf.columns.tolist())
            filtered_gdf = gdf
            selected_users = ['All Users']

        # Display statistics
        st.sidebar.header("Statistics")
        if user_column in gdf.columns:
            if 'All Users' in selected_users:
                st.sidebar.metric("Total Points", len(gdf))
                st.sidebar.metric("Total Users", len(gdf[user_column].dropna().unique()))
            else:
                st.sidebar.metric("Filtered Points", len(filtered_gdf))
                st.sidebar.metric("Selected Users", len(selected_users))
        else:
            st.sidebar.metric("Total Points", len(gdf))

        # Create and display the map with filtered data
        m = create_map(filtered_gdf, service_layers)

        # Display the map in the main area
        st.header("Ecosystem Services Map")
        folium_static(m, width=1000, height=600)

        # Display data table
        if st.checkbox("Show filtered data"):
            st.write(filtered_gdf)

else:
    st.info("Please download the MLA637 data using the button in the sidebar to view the map.")

# Add information about the application
st.sidebar.markdown("---")
st.sidebar.info("""
This application displays ecosystem services data from the MLA637 project.
Use the user filter above to view specific users' data.
""")
