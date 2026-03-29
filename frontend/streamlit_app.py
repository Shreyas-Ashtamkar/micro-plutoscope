"""Main application module for Micro Plutoscope."""

import streamlit as st
from .components import render_sidebar, render_code_editor, render_output_section
from .state import init_state, KEY_EDITOR_CODE, KEY_EDITOR_LANGUAGE, KEY_UI_OUTPUT
from utils import ensure_sqlite_db_path
from backend import CodeExecutor


class App:
    """Main application class for Micro Plutoscope."""

    def __init__(self, timeout: int = 10):
        """Initialize the application."""
        ensure_sqlite_db_path()
        self._configure_page()
        self._code_executor = CodeExecutor(timeout=timeout)

    def _configure_page(self, title="Micro Plutoscope", icon="📊") -> None:
        """Configure Streamlit page settings."""
        st.set_page_config(page_title=title, page_icon=icon, layout="wide")

    def code_executor(self) -> bool:
        """Execute the current editor code and store the result in session state."""
        st.session_state[KEY_UI_OUTPUT] = "loading..."
        st.session_state[KEY_UI_OUTPUT] = self._code_executor.run(
            code=st.session_state[KEY_EDITOR_CODE],
            language=st.session_state.get(KEY_EDITOR_LANGUAGE, "python"),
        )
        return self._code_executor.error != ""

    def render(self) -> None:
        """Run the main application."""
        init_state()

        sidebar_actions = render_sidebar()

        st.subheader("Micro Plutoscope")

        render_code_editor(code_executor=self.code_executor)

        render_output_section()

        if sidebar_actions["new_code"]:
            st.info("New code created.")
