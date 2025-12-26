import streamlit as st

# Function to apply custom CSS styles

def apply_custom_css():
    st.markdown(
        """
        <style>
            :root {
                --bg: #f6f8fb;
                --card-bg: #ffffff;
                --text: #111827;
                --muted: #6b7280;
                --primary: #2563eb;
                --primary-hover: #1d4ed8;
                --border: #e5e7eb;
            }

            html, body { background: var(--bg) !important; }
            .stApp { color: var(--text); }

            /* Typography */
            h1, h2, h3, h4 { color: var(--text); letter-spacing: -0.02em; }
            p, label, span { color: var(--text); }
            .small-muted { color: var(--muted); font-size: 0.9rem; }

            /* Cards */
            .ui-card {
                background: var(--card-bg);
                border: 1px solid var(--border);
                border-radius: 12px;
                box-shadow: 0 2px 10px rgba(17, 24, 39, 0.06);
                padding: 24px;
            }

            /* Buttons */
            .stButton>button {
                background: var(--primary);
                color: white;
                border: 1px solid var(--primary);
                border-radius: 8px;
                padding: 0.5rem 0.9rem;
            }
            .stButton>button:hover { background: var(--primary-hover); }

            /* Sidebar */
            div[data-testid="stSidebar"] {
                background: #ffffff;
                border-right: 1px solid var(--border);
            }

            /* Hide Streamlit chrome but keep sidebar toggle */
            footer {visibility: hidden;}
            div[data-testid="stToolbar"] {visibility: hidden;}
            div[data-testid="stDecoration"] {visibility: hidden;}
            div[data-testid="stStatusWidget"] {visibility: hidden;}

            /* Metrics */
            .stMetric { border: 1px solid var(--border); border-radius: 12px; padding: 8px; }
        </style>
        """,
        unsafe_allow_html=True,
    )