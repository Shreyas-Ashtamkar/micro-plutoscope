"""Code editor components for Micro Plutoscope app."""

import hashlib
from typing import Callable
import streamlit as st
from code_editor import code_editor
from backend import save_code
from frontend.state import (
    KEY_EDITOR_CODE,
    KEY_EDITOR_FILENAME,
    KEY_EDITOR_LANGUAGE,
    KEY_EDITOR_THEME,
    KEY_FILE_LAST_LOADED,
    KEY_FILE_PENDING,
    KEY_FILE_SAVED_HASH,
    KEY_UI_OUTPUT,
    KEY_UI_RESET_EDITOR,
)


def save_handler() -> None:
    """Save current code to database."""
    name = st.session_state.get(KEY_EDITOR_FILENAME, "").strip()
    if not name:
        st.error("Please enter a filename")
        return
    code = st.session_state.get(KEY_EDITOR_CODE, "")
    if not code.strip():
        st.error("Cannot save empty code")
        return
    lang = st.session_state.get(KEY_EDITOR_LANGUAGE, "python")
    file_hash, status = save_code(name, code, lang)
    if status in ("created", "updated"):
        st.session_state[KEY_FILE_SAVED_HASH] = hashlib.sha256(
            code.encode()
        ).hexdigest()
        if status == "created":
            st.success(f"Created: {file_hash[:16]}...")
        else:
            st.success(f"Updated: {file_hash[:16]}...")
    else:
        st.info("No changes to save")


def render_code_editor(code_executor: Callable = lambda *args, **kwargs: None) -> None:
    """
    Render the code editor section.

    Displays a code editor with language selection, theme toggle, filename input,
    and run/save buttons. Manages code persistence through session state.
    """
    with st.expander("Code", expanded=True):
        col1, col2, col3, col4, col5 = st.columns(
            [1, 1, 1, 0.4, 0.4], vertical_alignment="bottom"
        )

        with col1:
            language = st.selectbox(
                "Language",
                ["sql", "python", "javascript", "json", "java"],
                key=KEY_EDITOR_LANGUAGE,
            )

        with col2:
            theme = st.selectbox(
                "Theme", ["hc-black", "vs-dark", "vs-light"], key=KEY_EDITOR_THEME
            )

        with col3:
            st.text_input(
                "Filename",
                key=KEY_EDITOR_FILENAME,
                placeholder="Enter filename...",
            )

        with col4:
            st.button(
                "▶ Run",
                use_container_width=True,
                type="primary",
                on_click=code_executor,
            )

        with col5:
            st.button("💾 Save", use_container_width=True, on_click=save_handler)

        editor_settings = {
            "custom_btns": [
                {
                    "name": "copy",
                    "feather": "Copy",
                    "hasText": True,
                    "showWithIcon": True,
                    "commands": ["copyAll"],
                    "style": {"top": "0.5rem", "right": "0.4rem"},
                },
                {
                    "name": "Run",
                    "feather": "Play",
                    "primary": True,
                    "hasText": True,
                    "showWithIcon": True,
                    "commands": ["submit"],
                    "style": {"bottom": "0.44rem", "right": "0.4rem"},
                },
            ],
            "lang_info": {
                "name": "language info",
                "css": "\nbackground-color: #bee1e5;\n\nbody > #root .ace-streamlit-dark~& {\n   background-color: #262830;\n}\n\n.ace-streamlit-dark~& span {\n   color: #fff;\n    opacity: 0.6;\n}\n\nspan {\n   color: #000;\n    opacity: 0.5;\n}\n\n.code_editor-info.message {\n    width: inherit;\n    margin-right: 75px;\n    order: 2;\n    text-align: center;\n    opacity: 0;\n    transition: opacity 0.7s ease-out;\n}\n\n.code_editor-info.message.show {\n    opacity: 0.6;\n}\n\n.ace-streamlit-dark~& .code_editor-info.message.show {\n    opacity: 0.5;\n}\n",
                "style": {
                    "order": "1",
                    "display": "flex",
                    "flexDirection": "row",
                    "alignItems": "center",
                    "width": "100%",
                    "height": "2.5rem",
                    "padding": "0rem 0.6rem",
                    "padding-bottom": "0.2rem",
                    "margin-bottom": "-5px",
                    "borderRadius": "8px 8px 0px 0px",
                    "zIndex": "9993",
                },
                "info": [{"name": language, "style": {"width": "100px"}}],
            },
        }

        input_code = st.session_state[KEY_EDITOR_CODE]

        # Detect a newly loaded file and arm the one-shot editor reset flag
        pending = st.session_state[KEY_FILE_PENDING]
        last_loaded = st.session_state[KEY_FILE_LAST_LOADED]
        if pending != last_loaded:
            st.session_state[KEY_FILE_LAST_LOADED] = pending
            st.session_state[KEY_UI_RESET_EDITOR] = True

        # Consume the reset flag — only active for a single render pass
        should_reset = st.session_state[KEY_UI_RESET_EDITOR]
        if should_reset:
            st.session_state[KEY_UI_RESET_EDITOR] = False

        response = code_editor(
            code=input_code,
            height=[20, 40],
            key="code_editor",
            focus=True,
            theme=theme,
            lang=language,
            buttons=editor_settings["custom_btns"],
            options={"showLineNumbers": True, "showInvisibles": False},
            response_mode="debounce",
            allow_reset=should_reset,
        )

        # Persist latest text on user interaction (change or submit), not on mount
        if (
            response
            and isinstance(response, dict)
            and response.get("type") in ("change", "submit")
        ):
            if response.get("text") is not None:
                st.session_state[KEY_EDITOR_CODE] = response["text"]
            if response.get("type") == "submit":
                code_executor()


def render_output_section() -> None:
    """Render the output section."""
    output = st.session_state.get(KEY_UI_OUTPUT)
    if output is not None:
        st.code(output, language="bash")
    else:
        st.code("Output will appear here...", language="bash")
