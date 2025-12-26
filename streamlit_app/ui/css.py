import streamlit as st

# Function to apply custom CSS styles

def apply_custom_css():

    #.stApp {
#    max-width: 800px; /* Adjust maximum width of the app */
#    margin: 0 auto; /* Center align content */
#    padding: 20px; /* Add padding for content */
#    text-align: center; /* Center align text */
#}
# Apply inline style directly in Streamlit
    st.markdown(
        """
        <style>
            body {
                background-color: #C3E6CB !important; /* Important to override any conflicting styles */
                font-family: Arial, sans-serif; /* Adjust font family as needed */
            }

            .stApp h1 {
                font-size: 2.5em; /* Adjust title font size */
                margin-bottom: 10px; /* Add space below title */
            }

            .stApp p {
                font-size: 1em; /* Adjust subtitle font size */
                margin-bottom: 20px; /* Add space below subtitle */
            }

            /* Hide Streamlit elements */
            MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            div[data-testid="stToolbar"] {visibility: hidden;}
            div[data-testid="stDecoration"] {visibility: hidden;}
            div[data-testid="stStatusWidget"] {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True
    )