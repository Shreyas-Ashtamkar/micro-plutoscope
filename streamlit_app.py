"""
Micro Plutoscope - Main entry point.

This is the main entry point for the Streamlit application.
"""
from frontend import FrontendMain


def main() -> None:
    """Run the Micro Plutoscope application."""
    app = FrontendMain()
    app.render()


if __name__ == "__main__":
    main()

