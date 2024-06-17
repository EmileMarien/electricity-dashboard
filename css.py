import streamlit as st

# Function to apply custom CSS styles
def apply_custom_css():
    custom_css = """
    <style>
    body {
        background-color: #D2B48C; /* Light brown background color */
        font-family: Arial, sans-serif; /* Adjust font family as needed */
    }

    .stApp {
        max-width: 800px; /* Adjust maximum width of the app */
        margin: 0 auto; /* Center align content */
        padding: 20px; /* Add padding for content */
        text-align: center; /* Center align text */
    }

    .stApp h1 {
        font-size: 3em; /* Adjust title font size */
        margin-bottom: 10px; /* Add space below title */
    }

    .stApp p {
        font-size: 1.5em; /* Adjust subtitle font size */
        margin-bottom: 20px; /* Add space below subtitle */
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    #footer {visibility: hidden;}
    div[data-testid="stToolbar"] {visibility: hidden;}
    div[data-testid="stDecoration"] {visibility: hidden;}
    div[data-testid="stStatusWidget"] {visibility: hidden;}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)