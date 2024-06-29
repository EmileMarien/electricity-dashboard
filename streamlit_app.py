import streamlit as st
from css import apply_custom_css
from menu import menu

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Electricity Meter Dashboard',
    page_icon=':electric_plug:',  # This is an emoji shortcode. Could be a URL too.
)

# Hide Streamlit's default menu and footer using custom CSS
apply_custom_css()

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.write("")
with col2:
    st.image("data/logo_lama.png", use_column_width='always') # caption='Lama Icon'
with col3:
    st.write("")
st.write("# Lama energies")
st.write("laten we die daken nekeer volleggen")
st.write("blabla")

# Initialize st.session_state.role to None
if "role" not in st.session_state:
    st.session_state.role = None

# Retrieve the role from Session State to initialize the widget
st.session_state._role = st.session_state.role

def set_role():
    # Callback function to save the role selection to Session State
    st.session_state.role = st.session_state._role


# Selectbox to choose role
st.selectbox(
    "Select your role:",
    [None, "user", "investor"],
    key="_role",
    on_change=set_role,
)
menu() # Render the dynamic menu! 