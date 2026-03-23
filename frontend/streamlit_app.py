"""Main application module for Micro Plutoscope."""
import streamlit as st
from .components import render_sidebar, render_code_editor, render_output_section
from utils import ensure_sqlite_db_path
from backend import CodeExecutor


class App:
    """Main application class for Micro Plutoscope."""
    
    def __init__(self, timeout:int=10):
        """Initialize the application."""
        ensure_sqlite_db_path()
        self.saved_codes = []
        self.recent_codes = []
        self.settings = "/.env"
        self._configure_page()
        self._code_executor = CodeExecutor(timeout=timeout)
    
    def _configure_page(self, title="Micro Plutoscope", icon="📊") -> None:
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title=title,
            page_icon=icon,
            layout="wide"
        )
    
    def code_executor(self) -> bool:
        st.session_state["output_text"] = "loading..."
        st.session_state["output_text"] = self._code_executor.run(
            code = st.session_state["editor_code"], 
            language = st.session_state["editor_language"]
        )
        return (self._code_executor.error != "")
   
    def render(self) -> None:
        """Run the main application."""
        # Render sidebar
        sidebar_actions = render_sidebar()
        
        # Render main content
        st.subheader("Micro Plutoscope")
        
        # Render code editor
        render_code_editor(code_executor=self.code_executor)
        
        # st.divider()
        
        # Render output
        render_output_section()
        
        # Handle sidebar actions
        if sidebar_actions["new_code"]:
            st.info("New code created.")
        
        st.write(st.session_state)
