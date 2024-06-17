import streamlit as st


def authenticated_menu():
    # Show a navigation menu for authenticated users
    st.sidebar.page_link("streamlit_app.py", label="Switch accounts")
    st.sidebar.page_link("pages/3_Database.py", label="Grid info")
    if st.session_state.role == "user":
        st.sidebar.page_link("pages/2_Consumer_page.py", label="Consumers")

    if st.session_state.role in ["investor"]:
        st.sidebar.page_link("pages/1_Investor_page.py", label="Investors")

    st.sidebar.success("Select a page above")


def unauthenticated_menu():
    # Show a navigation menu for unauthenticated users
    st.sidebar.page_link("streamlit_app.py", label="Log in")


def menu():
    # Determine if a user is logged in or not, then show the correct
    # navigation menu
    if "role" not in st.session_state or st.session_state.role is None:
        unauthenticated_menu()
        return
    authenticated_menu()


def menu_with_redirect():
    # Redirect users to the main page if not logged in, otherwise continue to
    # render the navigation menu
    if "role" not in st.session_state or st.session_state.role is None:
        st.switch_page("streamlit_app.py")
    menu()

