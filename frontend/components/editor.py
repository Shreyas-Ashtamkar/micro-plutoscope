"""Code editor components for Micro Plutoscope app."""
from typing import Callable
import streamlit as st
from code_editor import code_editor


def render_code_editor(code_executor:Callable=None) -> tuple[str, str, bool]:
    """
    Render the code editor section.
    
    Returns:
        tuple: Code input, language, theme, and run button state
    """
    with st.expander("Code", expanded=True):
        col1, col2, col3 = st.columns([1, 1, 0.4], vertical_alignment="bottom")
        
        with col1:
            language = st.selectbox("Language", ["sql", "python", "javascript", "json", "java"], key="language_select")
        
        with col2:
            theme = st.selectbox("Theme", ["hc-black", "vs-dark", "vs-light"], key="theme_select")
        
        with col3:
            run_button = st.button("▶ Run", use_container_width=True, type="primary", on_click=code_executor)
            
        editor_settings = {
            "custom_btns" :[
                {
                    "name": "copy",
                    "feather": "Copy",
                    "hasText": True,
                    "showWithIcon":True,
                    "commands": ["copyAll"],
                    "style": {"top":"0.5rem", "right": "0.4rem"},
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
            "lang_info" : {
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
            }
        }
        
        input_code = ""

        response = code_editor(
            code=input_code,
            height=[20, 40],
            key="code_editor",
            focus=True,
            theme=theme,
            lang=language,
            buttons=editor_settings["custom_btns"],
            options={
                "showLineNumbers":True,
                "showInvisibles":False
            },
            response_mode="debounce",
            # info=editor_settings["lang_info"],
        )

        # Persist latest text whenever the editor sends data back (debounce or submit)
        if response and isinstance(response, dict):
            if response.get("text") is not None:
                st.session_state["editor_code"]     = response["text"]
                st.session_state["editor_language"] = language
            if response.get("type") == "submit":
                code_executor()


def render_output_section() -> None:
    """Render the output section."""
    # with st.expander("Output:", expanded=True):
    if "output_text" in st.session_state and st.session_state["output_text"] is not None:
        st.code(st.session_state["output_text"], language="bash")
    else:
        st.code("Output will appear here...", language="bash")
        
