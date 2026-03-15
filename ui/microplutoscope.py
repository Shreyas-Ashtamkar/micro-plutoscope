"""Main application module for Micro Plutoscope."""
import streamlit as st
from .components import render_sidebar, render_code_editor, render_output_section

# move to utils later
def callback_code_executer():
    """Callback function which will take the code from the session and execute it and store the output in session again"""
    pass


class App:
    """Main application class for Micro Plutoscope."""
    
    def __init__(self):
        """Initialize the application."""
        self._configure_page()
    
    def _configure_page(self) -> None:
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="Micro Plutoscope",
            page_icon="📊",
            layout="wide"
        )
    
    def render(self) -> None:
        """Run the main application."""
        # Render sidebar
        sidebar_actions = render_sidebar()
        
        # Render main content
        st.subheader("Micro Plutoscope")
        
        # Render code editor
        render_code_editor(callback_code_executer)
        
        
        # st.divider()
        
        # Render output
        render_output_section()
        
        # Handle sidebar actions
        if sidebar_actions["new_query"]:
            st.info("New query created.")
