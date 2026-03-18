"""Sidebar components for Micro Plutoscope app."""
import streamlit as st


def render_sidebar() -> dict:
    """
    Render the sidebar with navigation and code management.
    
    Returns:
        dict: User interactions from sidebar
    """
    st.sidebar.title("Menu")
    
    # Top Section - New Code Button
    new_code = st.sidebar.button("🆕 New Code", use_container_width=True)
    
    st.sidebar.divider()
    
    # Middle Section - Saved Codes
    st.sidebar.subheader("📁 Saved Codes")
    st.sidebar.write("No saved codes yet")
    
    st.sidebar.divider()
    
    # Middle Section - Recent Codes
    st.sidebar.subheader("⏱️ Recent Codes")
    st.sidebar.write("No recent codes yet")
    
    st.sidebar.divider()
    
    # Bottom Section - Settings
    st.sidebar.subheader("⚙️ Settings")
    with st.sidebar.container(border=True, vertical_alignment="bottom"):
        st.button(".env", key="dot_env", use_container_width=True)
    
    
    return {"new_code": new_code}
