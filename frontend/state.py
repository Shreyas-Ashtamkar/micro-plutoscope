"""Centralized session state management for Micro Plutoscope."""

from typing import Optional
import streamlit as st


# ---------------------------------------------------------------------------
# Key constants — use these everywhere instead of raw strings
# ---------------------------------------------------------------------------

# Editor group
KEY_EDITOR_CODE = "editor_code"
KEY_EDITOR_LANGUAGE = "editor_language"
KEY_EDITOR_THEME = "editor_theme"
KEY_EDITOR_FILENAME = "editor_filename"

# File-tracking group
KEY_FILE_SAVED_HASH = "file_saved_hash"
KEY_FILE_PENDING = "file_pending"
KEY_FILE_LAST_LOADED = "file_last_loaded"

# UI group
KEY_UI_OUTPUT = "ui_output"
KEY_UI_RESET_EDITOR = "ui_reset_editor"


# ---------------------------------------------------------------------------
# Default values — single source of truth for the entire state shape
# ---------------------------------------------------------------------------

STATE_DEFAULTS: dict = {
    KEY_EDITOR_CODE: "",
    KEY_EDITOR_LANGUAGE: "python",
    KEY_EDITOR_THEME: "hc-black",
    KEY_EDITOR_FILENAME: "",
    KEY_FILE_SAVED_HASH: None,
    KEY_FILE_PENDING: None,
    KEY_FILE_LAST_LOADED: None,
    KEY_UI_OUTPUT: None,
    KEY_UI_RESET_EDITOR: False,
}


# ---------------------------------------------------------------------------
# Initializer — call once per render cycle, safe to call multiple times
# ---------------------------------------------------------------------------


def init_state() -> None:
    """Initialize all app session state keys with their defaults.

    Only sets keys that are not yet present, so existing state is never
    overwritten.  Call this at the very start of every render pass.
    """
    for key, default in STATE_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default
