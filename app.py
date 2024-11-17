import streamlit as st
import pytz
from datetime import datetime
import json

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

/* Custom component container */
.timezone-circle {
    background: #000000;
    border-radius: 15px;
    border: 1px solid #00ff00;
    padding: 20px;
    margin: 20px 0;
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
}

/* Progress bar */
.stProgress > div > div {
    background-color: #00ff00 !important;
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

def create_circle_visualization_html(locations):
    """Generate HTML/JavaScript for the circular visualization"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://d3js.org/d3.v7.min.js"></script>
        <style>
            #timezone-circle {{
                width: 100%;
                height: 600px;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
        </style>
    </head>
    <body>
        <div id="timezone-circle"></div>
        <script>
            const width = 600;
            const height = 600;
            const radius = 200;
            const centerX = width / 2;
            const centerY = height / 2;

            const svg = d3.select("#timezone-circle")
                .append("svg")
                .attr("width", width)
                .attr("height", height)
                .style("background", "black");

            // Create gradient definitions
            const defs = svg.append("defs");
            const gradient = defs.append("linearGradient")
                .attr("id", "neon-gradient")
                .attr("x1", "0%")
                .attr("y1", "0%")
                .attr("x2", "100%")
                .attr("y2", "100%");

            gradient.append("stop")
                .attr("offset", "0%")
                .attr("stop-color", "#00ff00");

            gradient.append("stop")
                .attr("offset", "100%")
                .attr("stop-color", "#00ffff");

            // Draw base circles
            const timezones = {json.dumps(locations)};
            const timezonesData = timezones.map((tz, i) => ({{
                ...tz,
                radius: radius - (i * 40),
                color: d3.interpolateRainbow(i / timezones.length)
            }}));

            // Add circles for each timezone
            timezonesData.forEach((tz, i) => {{
                svg.append("circle")
                    .attr("cx", centerX)
                    .attr("cy", centerY)
                    .attr("r", tz.radius)
                    .attr("fill", "none")
                    .attr("stroke", "#333")
                    .attr("stroke-width", 1);

                // Add business hours arc
                const arc = d3.arc()
                    .innerRadius(tz.radius - 15)
                    .outerRadius(tz.radius + 15)
                    .startAngle(Math.PI * (8 / 12)) // 8 AM
                    .endAngle(Math.PI * (18 / 12)); // 6 PM

                svg.append("path")
                    .attr("d", arc)
                    .attr("transform", `translate(${{centerX}},${{centerY}})`)
                    .attr("fill", tz.color)
                    .attr("opacity", 0.5);

                // Add timezone label
                svg.append("text")
                    .attr("x", centerX + 5)
                    .attr("y", centerY - tz.radius)
                    .attr("fill", tz.color)
                    .attr("font-family", "monospace")
                    .attr("font-size", "14px")
                    .text(tz.city);
            }});

            // Add hour markers
            for (let i = 0; i < 24; i++) {{
                const angle = (i * 15) - 90;
                const radian = (angle * Math.PI) / 180;
                const x = centerX + (radius + 10) * Math.cos(radian);
                const y = centerY + (radius + 10) * Math.sin(radian);

                svg.append("text")
                    .attr("x", x)
                    .attr("y", y)
                    .attr("text-anchor", "middle")
                    .attr("alignment-baseline", "middle")
                    .attr("fill", "#00ff00")
                    .attr("font-family", "monospace")
                    .attr("font-size", "12px")
                    .text(i.toString().padStart(2, '0'));
            }}

            // Add center text
            svg.append("text")
                .attr("x", centerX)
                .attr("y", centerY - 20)
                .attr("text-anchor", "middle")
                .attr("fill", "#00ff00")
                .attr("font-family", "monospace")
                .attr("font-size", "16px")
                .text("we can chat in");

            const timeDisplay = svg.append("text")
                .attr("x", centerX)
                .attr("y", centerY + 10)
                .attr("text-anchor", "middle")
                .attr("fill", "#ffffff")
                .attr("font-family", "monospace")
                .attr("font-size", "24px");

            svg.append("text")
                .attr("x", centerX)
                .attr("y", centerY + 30)
                .attr("text-anchor", "middle")
                .attr("fill", "#ff9900")
                .attr("font-family", "monospace")
                .attr("font-size", "12px")
                .text("for up to 2.5 hours");

            // Update time
            function updateTime() {{
                const now = new Date();
                const hours = now.getHours().toString().padStart(2, '0');
                const minutes = now.getMinutes().toString().padStart(2, '0');
                const seconds = now.getSeconds().toString().padStart(2, '0');
                timeDisplay.text(`${{hours}}:${{minutes}}:${{seconds}}`);

                // Update clock hand
                const angle = ((hours % 12 + minutes / 60) * 30 - 90) * (Math.PI / 180);
                const handLength = radius - 20;
                const x2 = centerX + handLength * Math.cos(angle);
                const y2 = centerY + handLength * Math.sin(angle);

                svg.select(".clock-hand").remove();
                svg.append("line")
                    .attr("class", "clock-hand")
                    .attr("x1", centerX)
                    .attr("y1", centerY)
                    .attr("x2", x2)
                    .attr("y2", y2)
                    .attr("stroke", "#ff0000")
                    .attr("stroke-width", 2);

                svg.append("circle")
                    .attr("cx", centerX)
                    .attr("cy", centerY)
                    .attr("r", 5)
                    .attr("fill", "#ff0000");
            }}

            setInterval(updateTime, 1000);
            updateTime();
        </script>
    </body>
    </html>
    """
    return html_content

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
st.components.v1.html(
    create_circle_visualization_html(st.session_state.locations),
    height=650
)

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
