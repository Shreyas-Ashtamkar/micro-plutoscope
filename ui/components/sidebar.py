"""Sidebar components for Micro Plutoscope app."""
import streamlit as st


def render_sidebar() -> dict:
    """
    Render the sidebar with navigation and query management.
    
    Returns:
        dict: User interactions from sidebar
    """
    st.sidebar.title("Menu")
    
    # Top Section - New Query Button
    new_query = st.sidebar.button("🆕 New Query", use_container_width=True)
    
    st.sidebar.divider()
    
    # Middle Section - Saved Queries
    st.sidebar.subheader("📁 Saved Queries")
    st.sidebar.write("No saved queries yet")
    
    st.sidebar.divider()
    
    # Bottom Section - Recent Queries
    st.sidebar.subheader("⏱️ Recent Queries")
    st.sidebar.write("No recent queries yet")
    
    return {"new_query": new_query}
