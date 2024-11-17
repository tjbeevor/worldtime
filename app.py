import streamlit as st
import pytz
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Timezone Overlap Visualizer", layout="wide")

# Initialize session state for locations if it doesn't exist
if 'locations' not in st.session_state:
    st.session_state.locations = [
        {'city': 'New York', 'timezone': 'America/New_York'},
        {'city': 'London', 'timezone': 'Europe/London'},
        {'city': 'Tokyo', 'timezone': 'Asia/Tokyo'}
    ]

def get_available_timezones():
    """Return a organized dictionary of major timezones"""
    major_timezones = {
        'Americas': [
            ('New York', 'America/New_York'),
            ('Los Angeles', 'America/Los_Angeles'),
            ('Toronto', 'America/Toronto'),
            ('São Paulo', 'America/Sao_Paulo')
        ],
        'Europe': [
            ('London', 'Europe/London'),
            ('Paris', 'Europe/Paris'),
            ('Berlin', 'Europe/Berlin'),
            ('Stockholm', 'Europe/Stockholm')
        ],
        'Asia': [
            ('Dubai', 'Asia/Dubai'),
            ('Singapore', 'Asia/Singapore'),
            ('Tokyo', 'Asia/Tokyo'),
            ('Shanghai', 'Asia/Shanghai')
        ],
        'Pacific': [
            ('Sydney', 'Australia/Sydney'),
            ('Melbourne', 'Australia/Melbourne'),
            ('Auckland', 'Pacific/Auckland')
        ]
    }
    return major_timezones

def get_current_time(timezone_str):
    """Get current time in specified timezone"""
    tz = pytz.timezone(timezone_str)
    return datetime.now(tz).strftime('%I:%M %p')

def is_business_hour(hour, timezone_str, business_start=8, business_end=18):
    """Check if given hour is within business hours in specified timezone"""
    tz = pytz.timezone(timezone_str)
    now = datetime.now(pytz.UTC)
    local_time = now.astimezone(tz)
    offset = local_time.utcoffset().total_seconds() / 3600
    adjusted_hour = (hour + int(offset)) % 24
    return business_start <= adjusted_hour <= business_end

def create_timeline_visualization():
    """Create the timeline visualization using plotly"""
    hours = list(range(24))
    fig = go.Figure()

    # Add traces for each location
    colors = ['rgb(59, 130, 246)', 'rgb(34, 197, 94)', 'rgb(168, 85, 247)', 
              'rgb(236, 72, 153)', 'rgb(99, 102, 241)', 'rgb(20, 184, 166)']

    for idx, location in enumerate(st.session_state.locations):
        business_hours = [is_business_hour(h, location['timezone']) for h in hours]
        
        # Create hover text
        hover_text = [f"{location['city']}: {h:02d}:00" for h in hours]

        fig.add_trace(go.Scatter(
            x=hours,
            y=[idx] * 24,
            mode='markers',
            name=f"{location['city']} ({get_current_time(location['timezone'])})",
            marker=dict(
                size=20,
                color=[colors[idx] if bh else 'lightgrey' for bh in business_hours],
                opacity=[0.8 if bh else 0.3 for bh in business_hours],
            ),
            hovertext=hover_text,
            showlegend=True
        ))

    # Add overlap trace
    if st.session_state.locations:
        overlap = [all(is_business_hour(h, loc['timezone']) for loc in st.session_state.locations) for h in hours]
        fig.add_trace(go.Scatter(
            x=hours,
            y=[-1] * 24,
            mode='markers',
            name='Overlap',
            marker=dict(
                size=20,
                color=['rgb(250, 204, 21)' if o else 'lightgrey' for o in overlap],
                opacity=[0.8 if o else 0.3 for o in overlap],
            ),
            hovertext=[f"Overlap: {h:02d}:00" for h in hours],
            showlegend=True
        ))

    # Update layout
    fig.update_layout(
        title='Timezone Overlap Visualization',
        xaxis_title='Hour (UTC)',
        yaxis_showticklabels=False,
        height=200 + (len(st.session_state.locations) * 50),
        showlegend=True,
        plot_bgcolor='white',
        xaxis=dict(
            tickmode='array',
            ticktext=[f'{i:02d}:00' for i in hours],
            tickvals=hours,
            gridcolor='lightgrey'
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False
        ),
        hovermode='x'
    )

    return fig

# Sidebar for adding/removing locations
st.sidebar.title('Location Settings')

# Add new location
available_timezones = get_available_timezones()
region = st.sidebar.selectbox('Region', list(available_timezones.keys()))

# Filter out already selected timezones
selected_timezone_names = {loc['timezone'] for loc in st.session_state.locations}
available_locations = [(city, tz) for city, tz in available_timezones[region] 
                      if tz not in selected_timezone_names]

if available_locations:
    city, timezone = st.sidebar.selectbox(
        'Add location',
        available_locations,
        format_func=lambda x: x[0]
    )
    
    if st.sidebar.button('Add Location') and len(st.session_state.locations) < 6:
        st.session_state.locations.append({'city': city, 'timezone': timezone})
        st.experimental_rerun()

# Remove locations
st.sidebar.markdown('---')
st.sidebar.subheader('Remove Locations')
for idx, location in enumerate(st.session_state.locations):
    if st.sidebar.button(f'Remove {location["city"]}'):
        st.session_state.locations.pop(idx)
        st.experimental_rerun()

# Main content
st.title('Timezone Overlap Visualizer')
st.markdown('''
Find the perfect meeting time across different timezones.
Business hours are considered to be 8 AM to 6 PM local time.
''')

# Display current time for each location
st.subheader('Current Times')
cols = st.columns(3)
for idx, location in enumerate(st.session_state.locations):
    col_idx = idx % 3
    cols[col_idx].metric(
        location['city'],
        get_current_time(location['timezone'])
    )

# Display visualization
st.plotly_chart(create_timeline_visualization(), use_container_width=True)

# Footer with information
st.markdown('---')
st.markdown('''
💡 **How to use:**
1. Add locations from the sidebar (maximum 6)
2. Yellow markers show times when all locations are within business hours
3. Hover over markers to see exact times
4. Remove locations using the sidebar buttons
''')
