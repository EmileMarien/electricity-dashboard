import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Building Components", page_icon="🏠", layout="wide")

# Hide Streamlit's default menu and footer using custom CSS
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
#footer {visibility: hidden;}
div[data-testid="stToolbar"] {visibility: hidden;}
div[data-testid="stDecoration"] {visibility: hidden;}
div[data-testid="stStatusWidget"] {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("🏠 Building Components Visualization")

# Component data organized by type
COMPONENT_TYPES = {
    "Wall": [
        {"name": "Exterior Wall 1", "description": "Insulated exterior wall", "image": "🧱"},
        {"name": "Exterior Wall 2", "description": "Brick exterior wall", "image": "🧱"},
        {"name": "Interior Wall 1", "description": "Drywall partition", "image": "🧱"},
        {"name": "Interior Wall 2", "description": "Load-bearing wall", "image": "🧱"},
    ],
    "Roof": [
        {"name": "Roof Panel 1", "description": "Sloped roof panel", "image": "🏠"},
        {"name": "Roof Panel 2", "description": "Flat roof section", "image": "🏠"},
        {"name": "Roof Insulation", "description": "Thermal insulation layer", "image": "🏠"},
    ],
    "Door": [
        {"name": "Front Door", "description": "Main entrance door", "image": "🚪"},
        {"name": "Interior Door 1", "description": "Standard interior door", "image": "🚪"},
        {"name": "Interior Door 2", "description": "Sliding door", "image": "🚪"},
        {"name": "Back Door", "description": "Rear entrance", "image": "🚪"},
    ],
    "Window": [
        {"name": "Window 1", "description": "Double-glazed window", "image": "🪟"},
        {"name": "Window 2", "description": "Triple-glazed window", "image": "🪟"},
        {"name": "Skylight", "description": "Roof window", "image": "🪟"},
    ],
    "Floor": [
        {"name": "Ground Floor", "description": "Concrete foundation", "image": "⬛"},
        {"name": "First Floor", "description": "Wooden floor structure", "image": "⬛"},
    ],
}

# Create main layout: components list on left, 3D view on right
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Components")
    
    # Search/filter box
    search_query = st.text_input("🔍 Search components", "", key="search_components")
    
    # Create scrollable component list
    component_list_html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                margin: 0;
                padding: 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
            .component-sidebar {
                height: 600px;
                overflow-y: auto;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                background-color: #f9f9f9;
            }
            .component-type-header {
                font-weight: bold;
                font-size: 18px;
                margin-top: 15px;
                margin-bottom: 10px;
                color: #333;
            }
            .component-item {
                display: flex;
                align-items: center;
                padding: 10px;
                margin: 5px 0;
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.2s;
            }
            .component-item:hover {
                background-color: #e8f4f8;
            }
            .component-icon {
                font-size: 30px;
                margin-right: 15px;
            }
            .component-info {
                flex: 1;
            }
            .component-name {
                font-weight: 600;
                color: #222;
            }
            .component-description {
                font-size: 12px;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="component-sidebar">
    '''
    
    for component_type, component_list in COMPONENT_TYPES.items():
        # Filter components based on search query
        filtered_components = [
            c for c in component_list 
            if search_query.lower() in c["name"].lower() or 
               search_query.lower() in c["description"].lower() or
               search_query.lower() in component_type.lower()
        ]
        
        if filtered_components:
            component_list_html += f'<div class="component-type-header">📁 {component_type}</div>'
            
            for component in filtered_components:
                component_list_html += f'''
                <div class="component-item">
                    <div class="component-icon">{component["image"]}</div>
                    <div class="component-info">
                        <div class="component-name">{component["name"]}</div>
                        <div class="component-description">{component["description"]}</div>
                    </div>
                </div>
                '''
    
    component_list_html += '''
        </div>
    </body>
    </html>
    '''
    components.html(component_list_html, height=600)

with col2:
    st.subheader("3D Building View")
    
    # CSS-based 3D house visualization (since Three.js CDN is blocked)
    threejs_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { 
                margin: 0; 
                overflow: hidden;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 600px;
                background: linear-gradient(to bottom, #87CEEB 0%, #87CEEB 70%, #7CFC00 70%, #7CFC00 100%);
                perspective: 1000px;
            }
            .house-container {
                transform-style: preserve-3d;
                animation: rotate 20s infinite linear;
                position: relative;
            }
            @keyframes rotate {
                from { transform: rotateY(0deg); }
                to { transform: rotateY(360deg); }
            }
            .house {
                width: 200px;
                height: 200px;
                position: relative;
                transform-style: preserve-3d;
            }
            .wall {
                position: absolute;
                width: 200px;
                height: 200px;
                background: linear-gradient(to bottom, #DEB887, #C19A6B);
                border: 2px solid #8B7355;
            }
            .front {
                transform: translateZ(100px);
            }
            .back {
                transform: translateZ(-100px) rotateY(180deg);
            }
            .right {
                transform: rotateY(90deg) translateZ(100px);
            }
            .left {
                transform: rotateY(-90deg) translateZ(100px);
            }
            .door {
                position: absolute;
                width: 50px;
                height: 90px;
                background: #654321;
                border: 2px solid #4a3319;
                bottom: 0;
                left: 75px;
                border-radius: 3px 3px 0 0;
            }
            .window {
                position: absolute;
                width: 40px;
                height: 40px;
                background: #87CEEB;
                border: 3px solid #4682B4;
                top: 50px;
            }
            .window-left {
                left: 20px;
            }
            .window-right {
                right: 20px;
            }
            .roof {
                position: absolute;
                width: 0;
                height: 0;
                border-left: 120px solid transparent;
                border-right: 120px solid transparent;
                border-bottom: 100px solid #8B4513;
                top: -80px;
                left: -20px;
                transform-origin: center;
            }
            .info-text {
                position: absolute;
                top: 20px;
                left: 50%;
                transform: translateX(-50%);
                color: white;
                font-size: 18px;
                font-weight: bold;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                z-index: 1000;
            }
        </style>
    </head>
    <body>
        <div class="info-text">🏠 3D Building Model (Interactive)</div>
        <div class="house-container">
            <div class="house">
                <div class="wall front">
                    <div class="window window-left"></div>
                    <div class="window window-right"></div>
                    <div class="door"></div>
                </div>
                <div class="wall back">
                    <div class="window window-left"></div>
                    <div class="window window-right"></div>
                </div>
                <div class="wall right"></div>
                <div class="wall left"></div>
                <div class="roof"></div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Render the 3D scene
    components.html(threejs_html, height=600)

# Insight calculator buttons below the 3D view
st.markdown("---")
st.subheader("Insight Calculators")

calculator_buttons_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        .calculator-buttons {
            display: flex;
            justify-content: center;
            gap: 15px;
            padding: 10px;
        }
        .calculator-btn {
            padding: 12px 30px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .calculator-btn:hover {
            background-color: #45a049;
        }
        .calculator-btn.epb {
            background-color: #2196F3;
        }
        .calculator-btn.epb:hover {
            background-color: #0b7dda;
        }
        .calculator-btn.meetstaat {
            background-color: #FF9800;
        }
        .calculator-btn.meetstaat:hover {
            background-color: #e68900;
        }
        .calculator-btn.lastenboek {
            background-color: #9C27B0;
        }
        .calculator-btn.lastenboek:hover {
            background-color: #7b1fa2;
        }
    </style>
</head>
<body>
    <div class="calculator-buttons">
        <button class="calculator-btn epb" onclick="alert('EPB Calculator - Energy Performance of Buildings')">
            📊 EPB Calculator
        </button>
        <button class="calculator-btn meetstaat" onclick="alert('Meetstaat - Measurement Report')">
            📏 Meetstaat
        </button>
        <button class="calculator-btn lastenboek" onclick="alert('Lastenboek - Specifications Book')">
            📋 Lastenboek
        </button>
    </div>
</body>
</html>
"""

components.html(calculator_buttons_html, height=100)

# Add some information below
st.markdown("---")
st.info("""
**About the Insight Calculators:**
- **EPB Calculator**: Calculate the Energy Performance of Buildings (EPB) based on component properties
- **Meetstaat**: Generate detailed measurement reports for construction components
- **Lastenboek**: Create comprehensive specifications documentation for building projects
""")
