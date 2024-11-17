import streamlit as st
import pytz
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="Global Time Sync", layout="wide", initial_sidebar_state="expanded")

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

/* Subtitle styling */
.subtitle {
    font-family: 'Poppins', sans-serif;
    font-size: 1.2rem !important;
    color: #00ff00;
    text-align: center;
    margin-bottom: 2rem;
    text-shadow: 0 0 5px rgba(0, 255, 0, 0.5);
}

/* Card styling */
.stMetric {
    background: linear-gradient(135deg, rgba(0,0,0,0.9), rgba(0,0,0,0.95));
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: 20px;
    border: 1px solid #00ff00;
    padding: 20px;
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
    margin-bottom: 1rem;
}

.stMetric:hover {
    transform: translateY(-5px);
    transition: all 0.3s ease;
    box-shadow: 0 0 30px rgba(0, 255, 0, 0.4);
    border-color: #00ffff;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #000000, #111111);
    border-right: 1px solid #00ff00;
}

/* Button styling */
.stButton>button {
    width: 100%;
    background: #000000 !important;
    color: #00ff00 !important;
    border: 1px solid #00ff00 !important;
    border-radius: 10px;
    padding: 10px 20px;
    font-family: 'Poppins', sans-serif;
    font-weight: 600;
    transition: all 0.3s ease;
    text-shadow: 0 0 5px rgba(0, 255, 0, 0.5);
    box-shadow: 0 0 10px rgba(0, 255, 0, 0.2);
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.4);
    border-color: #00ffff !important;
    color: #00ffff !important;
    text-shadow: 0 0 5px rgba(0, 255, 255, 0.5);
}

/* Selectbox styling */
.stSelectbox > div {
    background-color: #000000 !important;
    border: 1px solid #00ff00 !important;
    border-radius: 10px;
}

.stSelectbox > div:hover {
    border-color: #00ffff !important;
}

/* Custom time display */
.time-display {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.5rem;
    color: #00ffff;
    text-align: center;
    margin: 10px 0;
    text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
}

/* Footer styling */
.footer {
    background: rgba(0, 0, 0, 0.8);
    padding: 20px;
    border-radius: 10px;
    margin-top: 2rem;
    border: 1px solid #00ff00;
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
}

/* Progress bar */
.stProgress > div > div {
    background-color: #00ff00 !important;
    box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 10px;
    background: #000000;
}

::-webkit-scrollbar-thumb {
    background: #00ff00;
    border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
    background: #00ffff;
}

/* Headers */
h1, h2, h3 {
    color: #00ff00 !important;
    text-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
}

/* Markdown text */
.markdown-text {
    color: #00ff00;
    font-family: 'Poppins', sans-serif;
    text-shadow: 0 0 5px rgba(0, 255, 0, 0.2);
}

/* Sidebar title */
.sidebar-title {
    color: #00ff00;
    font-family: 'Poppins', sans-serif;
    font-size: 1.2rem;
    text-shadow: 0 0 5px rgba(0, 255, 0, 0.3);
    margin-bottom: 1rem;
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
    
    for region in timezone_dict:
        timezone_dict[region] = sorted(timezone_dict[region], key=lambda x: x[0])
    
    return dict(sorted(timezone_dict.items()))

def get_current_time(timezone_str):
    """Get current time in specified timezone"""
    try:
        tz = pytz.timezone(timezone_str)
        return datetime.now(tz).strftime('%I:%M %p')
    except pytz.exceptions.UnknownTimeZoneError:
        return "Invalid Timezone"

def is_business_hour(hour, timezone_str, business_start=8, business_end=18):
    """Check if given hour is within business hours in specified timezone"""
    try:
        tz = pytz.timezone(timezone_str)
        now = datetime.now(pytz.UTC)
        local_time = now.astimezone(tz)
        offset = local_time.utcoffset().total_seconds() / 3600
        adjusted_hour = (hour + int(offset)) % 24
        return business_start <= adjusted_hour <= business_end
    except pytz.exceptions.UnknownTimeZoneError:
        return False

def create_timeline_visualization():
    """Create the timeline visualization using plotly"""
    hours = list(range(24))
    fig = go.Figure()

    # Fluorescent color palette
    colors = [
        '#00ff00',  # Neon Green
        '#00ffff',  # Cyan
        '#ff00ff',  # Magenta
        '#ffff00',  # Yellow
        '#ff3300',  # Neon Orange
        '#ff0099',  # Neon Pink
    ]

    for idx, location in enumerate(st.session_state.locations):
        business_hours = [is_business_hour(h, location['timezone']) for h in hours]
        hover_text = [f"{location['city']}<br>{h:02d}:00" for h in hours]

        fig.add_trace(go.Scatter(
            x=hours,
            y=[idx] * 24,
            mode='markers',
            name=f"{location['city']} ({get_current_time(location['timezone'])})",
            marker=dict(
                size=25,
                symbol='circle',
                color=[colors[idx % len(colors)] if bh else '#1a1a1a' for bh in business_hours],
                opacity=[1 if bh else 0.3 for bh in business_hours],
                line=dict(color='#000000', width=2)
            ),
            hovertext=hover_text,
            hoverinfo='text',
            showlegend=True
        ))

    if st.session_state.locations:
        overlap = [all(is_business_hour(h, loc['timezone']) for loc in st.session_state.locations) for h in hours]
        fig.add_trace(go.Scatter(
            x=hours,
            y=[-1] * 24,
            mode='markers',
            name='Overlap ⚡',
            marker=dict(
                size=30,
                symbol='diamond',
                color=['#00ff00' if o else '#1a1a1a' for o in overlap],
                opacity=[1 if o else 0.3 for o in overlap],
                line=dict(color='#000000', width=2)
            ),
            hovertext=[f"Overlap Time<br>{h:02d}:00" for h in hours],
            hoverinfo='text',
            showlegend=True
        ))

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=dict(
            text='Time Overlap Visualization',
            font=dict(family='Poppins', size=24, color='#00ff00'),
            x=0.5,
            y=0.95
        ),
        xaxis=dict(
            tickmode='array',
            ticktext=[f'{i:02d}:00' for i in hours],
            tickvals=hours,
            gridcolor='rgba(0,255,0,0.1)',
            title=dict(text='Hours (UTC)', font=dict(family='Poppins', size=14, color='#00ff00')),
            tickfont=dict(family='Roboto Mono', color='#00ff00')
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False
        ),
        height=200 + (len(st.session_state.locations) * 60),
        showlegend=True,
        legend=dict(
            bgcolor='rgba(0,0,0,0.8)',
            bordercolor='#00ff00',
            borderwidth=1,
            font=dict(family='Poppins', size=12, color='#00ff00')
        ),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='rgba(0,0,0,0.9)',
            font=dict(family='Roboto Mono', size=12, color='#00ff00'),
            bordercolor='#00ff00'
        )
    )

    return fig

# Main title and subtitle
st.markdown('<h1 class="big-title">⚡ Global Time Sync</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Synchronize Across the Digital World</p>', unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown('<p class="sidebar-title">⚙️ Configure Locations</p>', unsafe_allow_html=True)

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
st.sidebar.markdown('<p class="sidebar-title">🗺️ Current Locations</p>', unsafe_allow_html=True)

# Progress bar
locations_used = len(st.session_state.locations)
st.sidebar.progress(locations_used / 6, text=f'Using {locations_used}/6 locations')

# Remove buttons
for idx, location in enumerate(st.session_state.locations):
    if st.sidebar.button(f'❌ Remove {location["city"]}', key=f'remove_{idx}'):
        st.session_state.locations.pop(idx)
        st.rerun()

# Current times display
cols = st.columns(3)
for idx, location in enumerate(st.session_state.locations):
    col_idx = idx % 3
    with cols[col_idx]:
        st.markdown(f"""
        <div class="stMetric">
            <p style="font-family: 'Poppins'; color: #00ff00; font-size: 1.2rem; margin-bottom: 5px;">{location['city']}</p>
            <p class="time-display">{get_current_time(location['timezone'])}</p>
        </div>
        """, unsafe_allow_html=True)

# Timeline visualization
st.plotly_chart(create_timeline_visualization(), use_container_width=True)

# Footer
st.markdown("""
<div class="footer">
    <h3 style="font-family: 'Poppins'; color: #00ff00;">💡 Quick Guide</h3>
    <ul style="font-family: 'Poppins'; color: #00ff00;">
        <li>Add up to 6 locations from the sidebar</li>
        <li>Yellow diamonds show optimal meeting times</li>
        <li>Hover over markers for detailed time information</li>
        <li>Business hours: 8 AM - 6 PM local time</li>
    </ul>
</div>
""", unsafe_allow_html=True)
