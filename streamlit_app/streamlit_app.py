import streamlit as st
from ui.css import apply_custom_css
from ui.menu import menu

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title="Electricity Dashboard",
    page_icon=":electric_plug:",
    layout="wide",
)

# Hide Streamlit's default menu and footer using custom CSS
apply_custom_css()

sp1, main, sp2 = st.columns([1, 2, 1])
with main:
    st.image("data/logo_lama.png", width=160)
    st.markdown("## Welcome")
    st.caption("Sign in to continue to the platform")

# Initialize st.session_state.role to None
if "role" not in st.session_state:
    st.session_state.role = None

# Role selection
role = st.selectbox(
    "Role",
    [None, "user", "investor"],
    index=0,
    help="Choose your role to tailor the experience.",
)

col_a, col_b = st.columns([1, 1])
with col_a:
    if st.button("Continue", type="primary"):
        st.session_state.role = role
        if role is None:
            st.warning("Please select a role to continue.")
        else:
            # Go to House Builder by default after login
            try:
                st.switch_page("pages/5_House_builder.py")
            except Exception:
                pass

# Render the dynamic menu (sidebar)
menu()