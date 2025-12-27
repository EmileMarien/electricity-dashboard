import streamlit as st
import streamlit.components.v1 as components

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

            /* Ensure ALL sidebar toggle buttons are visible */
            button[data-testid="stSidebarCollapseButton"],
            button[data-testid="collapsedControl"],
            button[data-testid="baseButton-headerNoPadding"],
            div[data-testid="collapsedControl"],
            [data-testid="stSidebarCollapsedControl"],
            .stSidebarCollapsedControl,
            button[kind="headerNoPadding"] {
                visibility: visible !important;
                display: flex !important;
                opacity: 1 !important;
                z-index: 999999 !important;
            }
            
            /* Custom sidebar toggle button (fallback) */
            #custom-sidebar-toggle {
                position: fixed;
                top: 14px;
                left: 14px;
                z-index: 1000000;
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 8px 12px;
                cursor: pointer;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                font-size: 16px;
                display: none;
                transition: all 0.2s ease;
            }
            
            #custom-sidebar-toggle:hover {
                background: #f3f4f6;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }

            /* Metrics */
            .stMetric { border: 1px solid var(--border); border-radius: 12px; padding: 8px; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Add custom JavaScript to handle sidebar toggle
    components.html(
        """
        <div id="custom-sidebar-toggle" onclick="toggleSidebar()">☰ Menu</div>
        <script>
            function toggleSidebar() {
                // Try to find and click the native Streamlit sidebar toggle button
                const selectors = [
                    'button[data-testid="stSidebarCollapseButton"]',
                    'button[data-testid="collapsedControl"]',
                    '[data-testid="stSidebarCollapsedControl"] button',
                    'button[kind="headerNoPadding"]',
                    'section[data-testid="stSidebar"] button[kind="headerNoPadding"]',
                    '.stSidebar button'
                ];
                
                for (const selector of selectors) {
                    const btn = parent.document.querySelector(selector);
                    if (btn) {
                        btn.click();
                        return;
                    }
                }
                
                // Fallback: try to toggle sidebar visibility directly
                const sidebar = parent.document.querySelector('section[data-testid="stSidebar"]');
                if (sidebar) {
                    const isCollapsed = sidebar.getAttribute('aria-expanded') === 'false' || 
                                       sidebar.style.width === '0px' ||
                                       sidebar.classList.contains('st-emotion-cache-1cypcdb');
                    if (isCollapsed) {
                        sidebar.style.width = '';
                        sidebar.style.minWidth = '';
                        sidebar.setAttribute('aria-expanded', 'true');
                    }
                }
            }
            
            function checkSidebarState() {
                const sidebar = parent.document.querySelector('section[data-testid="stSidebar"]');
                const toggle = document.getElementById('custom-sidebar-toggle');
                
                if (!sidebar || !toggle) return;
                
                // Check if sidebar is collapsed
                const sidebarRect = sidebar.getBoundingClientRect();
                const isCollapsed = sidebarRect.width < 50;
                
                toggle.style.display = isCollapsed ? 'block' : 'none';
            }
            
            // Check periodically
            setInterval(checkSidebarState, 500);
            checkSidebarState();
        </script>
        """,
        height=0,
    )