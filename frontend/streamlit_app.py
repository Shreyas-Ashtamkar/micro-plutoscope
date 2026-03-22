"""Main application module for Micro Plutoscope."""
import streamlit as st
from .components import render_sidebar, render_code_editor, render_output_section
from utils import ensure_sqlite_db_path
from backend.engine import CodeExecutor

# move to utils later
def callback_code_executer(*args):
    """Callback function which will take the code from the session and execute it and store the output in session again"""
    code:str = args[0]
    lang:str = args[1]
    return CodeExecutor(timeout=10).run(code=code,language=lang)
    # return f"Run {lang} code -\n{code}"


class App:
    """Main application class for Micro Plutoscope."""
    
    def __init__(self):
        """Initialize the application."""
        ensure_sqlite_db_path()
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
        code_input, language, run_button = render_code_editor()
        
        if run_button:
            st.session_state["output_text"] = callback_code_executer(code_input, language)
        
        # st.divider()
        
        # Render output
        render_output_section()
        
        # Handle sidebar actions
        if sidebar_actions["new_code"]:
            st.info("New code created.")
