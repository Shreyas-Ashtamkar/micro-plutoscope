"""
Micro Plutoscope - Main entry point.

This is the main entry point for the Streamlit application.
"""
from frontend import FrontendMain

app = FrontendMain()
app.render()