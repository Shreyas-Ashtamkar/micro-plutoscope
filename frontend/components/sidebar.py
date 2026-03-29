"""Sidebar components for Micro Plutoscope app."""

import hashlib
import streamlit as st
from backend import list_codes, load_code, delete_code


def load_saved_code(filename: str) -> bool:
    """
    Load a saved code into session state.

    Returns:
        True if loaded successfully, False otherwise
    """
    data = load_code(filename)
    if data:
        st.session_state["editor_code"] = data["content"]
        st.session_state["code_filename"] = filename
        st.session_state["saved_code_hash"] = hashlib.sha256(
            data["content"].encode()
        ).hexdigest()
        st.session_state["language_select"] = data["language"]
        return True
    return False


def clear_editor():
    """Clear the editor and filename."""
    st.session_state["editor_code"] = ""
    st.session_state["code_filename"] = ""
    st.session_state["saved_code_hash"] = None
    st.session_state["language_select"] = "python"


def is_code_modified() -> bool:
    """Check if current code has been modified since last save."""
    saved_hash = st.session_state.get("saved_code_hash")
    if saved_hash is None:
        return False
    current_code = st.session_state.get("editor_code", "")
    current_hash = hashlib.sha256(current_code.encode()).hexdigest()
    return current_hash != saved_hash


def render_sidebar(*args) -> dict:
    """
    Render the sidebar with navigation and code management.

    Returns:
        dict: User interactions from sidebar
    """
    st.sidebar.title("Menu")

    # Top Section - New Code Button
    new_code = st.sidebar.button("🆕 New Code", use_container_width=True)
    if new_code:
        clear_editor()
        st.rerun()

    st.sidebar.divider()

    # Recent Codes Section (last 5 modified)
    st.sidebar.subheader("⏱️ Recent Codes")

    saved_codes = list_codes(metadata_only=True)

    if not saved_codes:
        st.sidebar.write("No recent codes yet")
    else:
        recent = sorted(saved_codes, key=lambda x: x.get("modified", ""), reverse=True)[
            :5
        ]
        for code in recent:
            if st.sidebar.button(
                code["file"],
                key=f"recent_{code['file']}",
                use_container_width=True,
            ):
                load_saved_code(code["file"])
                st.rerun()

    st.sidebar.divider()

    # Saved Codes Section
    st.sidebar.subheader("📁 Saved Codes")

    if not saved_codes:
        st.sidebar.write("No saved codes yet")
    else:
        for code in saved_codes:
            key_load = f"load_{code['file']}"
            key_del = f"del_{code['file']}"

            cols = st.sidebar.columns([4, 1])
            with cols[0]:
                if st.button(
                    code["file"],
                    key=key_load,
                    use_container_width=True,
                ):
                    load_saved_code(code["file"])
                    st.rerun()
            with cols[1]:
                if st.button("🗑️", key=key_del, help="Delete"):
                    result = delete_code(code["file"])
                    if result == "deleted":
                        st.success(f"Deleted: {code['file']}")
                        st.rerun()
                    elif result == "permission_denied":
                        st.error("Cannot delete important file")
                    else:
                        st.error("File not found")

    st.sidebar.divider()

    # Bottom Section - Settings
    st.sidebar.subheader("⚙️ Settings")
    with st.sidebar.container(border=True, vertical_alignment="bottom"):
        st.button(".env", key="dot_env", use_container_width=True)

    return {"new_code": new_code}
