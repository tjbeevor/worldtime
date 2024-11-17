import streamlit as st
import pytz
from datetime import datetime
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Global Time Sync",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with neon/cyberpunk styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&family=Roboto+Mono&display=swap');

/* Main background and theme */
.stApp {
    background-color: #000000;
    color: #fff;
}

/* Main title styling */
.big-title {
    font-family: 'Poppins', sans-serif;
    font-size: 3.5rem !important;
    font-weight: 600 !important;
    background: linear-gradient(120deg, #00ff00, #00ffff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    padding: 20px 0;
    text-align: center;
    text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #000000;
    border-right: 1px solid #00ff00;
}

/* Button styling */
.stButton > button {
    width: 100%;
    background-color: #000000 !important;
    color: #00ff00 !important;
    border: 1px solid #00ff00 !important;
    border-radius: 10px;
    padding: 10px 20px;
    font-family: 'Poppins', sans-serif;
    font-weight: 600;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    border-color: #00ffff !important;
    color: #00ffff !important;
    box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
}

/* Select box styling */
.stSelectbox > div > div {
    background-color: #000000 !important;
    border: 1px solid #00ff00 !important;
}

.stSelectbox > div > div:hover {
    border-color: #00ffff !important;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'locations' not in st.session_state:
    st.session_state.locations = [
        {'city': 'New York', 'timezone': 'America/New_York'},
        {'city': 'London', 'timezone': 'Europe/London'},
        {'city': 'Tokyo', 'timezone': 'Asia/Tokyo'}
    ]

def get_available_timezones():
    """Return an organized dictionary of all timezones"""
    all_timezones = pytz.all_timezones
    timezone_dict = {}
    
    def get_city_name(tz):
        return tz.split('/')[-1].replace('_', ' ')
    
    for tz in all_timezones:
        region = tz.split('/')[0]
        if region not in timezone_dict:
            timezone_dict[region] = []
        city_name = get_city_name(tz)
        timezone_dict[region].append((f"{city_name} ({tz})", tz))
    
    return dict(sorted(timezone_dict.items()))

def get_current_time(timezone_str):
    """Get current time in specified timezone"""
    try:
        tz = pytz.timezone(timezone_str)
        return datetime.now(tz).strftime('%I:%M %p')
    except pytz.exceptions.UnknownTimeZoneError:
        return "Invalid Timezone"

def create_circular_visualization():
    """Create circular visualization using plotly"""
    fig = go.Figure()
    
    # Calculate current hour for time indicator
    current_utc = datetime.now(pytz.UTC)
    current_hour = current_utc.hour + current_utc.minute / 60
    
    # Setup the polar plot
    hours = list(range(24))
    r = [1] * 24  # Constant radius for the hour markers
    
    # Add hour markers
    fig.add_trace(go.Scatterpolar(
        r=r,
        theta=[(h * 360/24) for h in hours],
        text=[f"{h:02d}:00" for h in hours],
        mode='text+markers',
        marker=dict(size=8, color='#00ff00'),
        textfont=dict(color='#00ff00', size=10),
        showlegend=False
    ))
    
    # Add timezone arcs
    colors = ['#00ff00', '#00ffff', '#ff00ff', '#ffff00', '#ff3300', '#ff0099']
    for idx, location in enumerate(st.session_state.locations):
        tz = pytz.timezone(location['timezone'])
        local_time = current_utc.astimezone(tz)
        offset = local_time.utcoffset().total_seconds() / 3600
        
        # Business hours in local time (8 AM to 6 PM)
        start_hour = (8 - offset) % 24
        end_hour = (18 - offset) % 24
        
        # Create arc for business hours
        theta = []
        r = []
        for h in range(24):
            if start_hour <= h <= end_hour:
                theta.append(h * 360/24)
                r.append(0.8 - idx * 0.15)
        
        fig.add_trace(go.Scatterpolar(
            r=r,
            theta=theta,
            mode='lines',
            line=dict(width=20, color=colors[idx % len(colors)]),
            name=f"{location['city']} ({get_current_time(location['timezone'])})",
            opacity=0.7
        ))
    
    # Add current time indicator
    fig.add_trace(go.Scatterpolar(
        r=[0, 0.9],
        theta=[current_hour * 360/24] * 2,
        mode='lines',
        line=dict(color='#ff0000', width=2),
        showlegend=False
    ))
    
    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 1]),
            angularaxis=dict(
                visible=True,
                rotation=90,
                direction='clockwise',
                period=24
            ),
            bgcolor='black'
        ),
        showlegend=True,
        paper_bgcolor='black',
        plot_bgcolor='black',
        legend=dict(
            font=dict(color='#00ff00'),
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='#00ff00'
        ),
        height=700
    )
    
    return fig

# Main title
st.markdown('<h1 class="big-title">⚡ Global Time Sync</h1>', unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown('<h2 style="color: #00ff00;">⚙️ Configure Locations</h2>', unsafe_allow_html=True)

# Location management
available_timezones = get_available_timezones()
region = st.sidebar.selectbox('Select Region 🌎', list(available_timezones.keys()))

selected_timezone_names = {loc['timezone'] for loc in st.session_state.locations}
available_locations = [(city, tz) for city, tz in available_timezones[region] 
                      if tz not in selected_timezone_names]

if available_locations:
    selected_location = st.sidebar.selectbox(
        'Choose Location 📍',
        available_locations,
        format_func=lambda x: x[0]
    )
    
    if st.sidebar.button('➕ Add Location'):
        if len(st.session_state.locations) < 6:
            city, timezone = selected_location
            st.session_state.locations.append({'city': city, 'timezone': timezone})
            st.rerun()

# Display current locations
st.sidebar.markdown('---')
st.sidebar.markdown('<h3 style="color: #00ff00;">🗺️ Current Locations</h3>', unsafe_allow_html=True)

# Progress bar
locations_used = len(st.session_state.locations)
st.sidebar.progress(locations_used / 6, text=f'Using {locations_used}/6 locations')

# Remove buttons
for idx, location in enumerate(st.session_state.locations):
    if st.sidebar.button(f'❌ Remove {location["city"]}', key=f'remove_{idx}'):
        st.session_state.locations.pop(idx)
        st.rerun()

# Display the circular visualization
st.plotly_chart(create_circular_visualization(), use_container_width=True)

# Auto-refresh
st.empty()
st.experimental_rerun()

# Footer
st.markdown("""
<div style="background: rgba(0,0,0,0.8); padding: 20px; border-radius: 10px; border: 1px solid #00ff00; margin-top: 2rem;">
    <h3 style="color: #00ff00; font-family: 'Poppins', sans-serif;">💡 Quick Guide</h3>
    <ul style="color: #00ff00; font-family: 'Poppins', sans-serif;">
        <li>Add up to 6 locations from the sidebar</li>
        <li>Colored arcs show business hours (8 AM - 6 PM)</li>
        <li>The red line shows current time</li>
        <li>Overlapping arcs indicate optimal meeting times</li>
    </ul>
</div>
""", unsafe_allow_html=True)
