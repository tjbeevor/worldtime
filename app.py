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

# Custom CSS with traditional styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&family=Roboto+Mono&display=swap');

.big-title {
    font-family: 'Poppins', sans-serif;
    font-size: 2.5rem !important;
    font-weight: 600 !important;
    color: #1a237e;
    padding: 20px 0;
    text-align: center;
}

.stButton > button {
    width: 100%;
    background-color: #1a237e !important;
    color: white !important;
    border: none !important;
    border-radius: 5px;
    padding: 10px 20px;
    font-family: 'Poppins', sans-serif;
    font-weight: 600;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background-color: #283593 !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.stSelectbox > div > div {
    background-color: white !important;
    border: 1px solid #e0e0e0 !important;
}

.footer {
    background: #f5f5f5;
    padding: 20px;
    border-radius: 5px;
    border: 1px solid #e0e0e0;
    margin-top: 2rem;
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
        marker=dict(size=8, color='#1a237e'),
        textfont=dict(color='#1a237e', size=10),
        showlegend=False
    ))
    
    # Professional color palette
    colors = [
        '#1a237e',  # Dark Blue
        '#0277bd',  # Blue
        '#00838f',  # Teal
        '#2e7d32',  # Green
        '#5d4037',  # Brown
        '#283593'   # Indigo
    ]
    
    # Add timezone arcs
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
        line=dict(color='#d32f2f', width=2),
        showlegend=False
    ))
    
    # Update layout with white background
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 1]),
            angularaxis=dict(
                visible=True,
                rotation=90,
                direction='clockwise',
                period=24,
                gridcolor='#e0e0e0',
                linecolor='#9e9e9e'
            ),
            bgcolor='white'
        ),
        showlegend=True,
        paper_bgcolor='white',
        plot_bgcolor='white',
        legend=dict(
            font=dict(color='#1a237e'),
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#e0e0e0'
        ),
        height=700,
        margin=dict(t=30, b=30)
    )
    
    return fig

# Main title
st.markdown('<h1 class="big-title">🌍 Global Time Sync</h1>', unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown('<h2 style="color: #1a237e;">⚙️ Configure Locations</h2>', unsafe_allow_html=True)

# Location management
available_timezones = get_available_timezones()
region = st.sidebar.selectbox('Select Region', list(available_timezones.keys()))

selected_timezone_names = {loc['timezone'] for loc in st.session_state.locations}
available_locations = [(city, tz) for city, tz in available_timezones[region] 
                      if tz not in selected_timezone_names]

if available_locations:
    selected_location = st.sidebar.selectbox(
        'Choose Location',
        available_locations,
        format_func=lambda x: x[0]
    )
    
    if st.sidebar.button('Add Location'):
        if len(st.session_state.locations) < 6:
            city, timezone = selected_location
            st.session_state.locations.append({'city': city, 'timezone': timezone})
            st.rerun()

# Display current locations
st.sidebar.markdown('---')
st.sidebar.markdown('<h3 style="color: #1a237e;">Current Locations</h3>', unsafe_allow_html=True)

# Progress bar
locations_used = len(st.session_state.locations)
st.sidebar.progress(locations_used / 6, text=f'Using {locations_used}/6 locations')

# Remove buttons
for idx, location in enumerate(st.session_state.locations):
    if st.sidebar.button(f'Remove {location["city"]}', key=f'remove_{idx}'):
        st.session_state.locations.pop(idx)
        st.rerun()

# Display the circular visualization
st.plotly_chart(create_circular_visualization(), use_container_width=True)

# Add refresh button
if st.button('Refresh Time'):
    st.rerun()

# Footer
st.markdown("""
<div class="footer">
    <h3 style="color: #1a237e; font-family: 'Poppins', sans-serif;">📝 Quick Guide</h3>
    <ul style="color: #424242; font-family: 'Poppins', sans-serif;">
        <li>Add up to 6 locations from the sidebar</li>
        <li>Colored arcs show business hours (8 AM - 6 PM)</li>
        <li>The red line shows current time</li>
        <li>Overlapping arcs indicate optimal meeting times</li>
        <li>Click the refresh button to update the current time</li>
    </ul>
</div>
""", unsafe_allow_html=True)
