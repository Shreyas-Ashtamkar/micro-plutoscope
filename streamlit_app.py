import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Micro Plutoscope",
    page_icon="📊",
    layout="wide"
)

# ==================== SIDEBAR ====================
st.sidebar.title("Menu")

# Top Section - New Query Button
st.sidebar.button("🆕 New Query", use_container_width=True)

st.sidebar.divider()

# Middle Section - Saved Queries
st.sidebar.subheader("📁 Saved Queries")
# Placeholder for saved queries list
st.sidebar.write("No saved queries yet")

st.sidebar.divider()

# Bottom Section - Recent Queries
st.sidebar.subheader("⏱️ Recent Queries")
# Placeholder for recent queries list
st.sidebar.write("No recent queries yet")

# ==================== MAIN CONTENT ====================
st.title("Micro Plutoscope")

# Top Section - Code Editor
st.subheader("📝 Code Editor")
code_input = st.text_area(
    "Write your code here:",
    height=300,
    placeholder="Enter your code or query...",
    label_visibility="collapsed"
)

st.divider()

# Bottom Section - Output
st.subheader("📊 Output")
# Placeholder for output
output_container = st.container()
with output_container:
    st.write("Output will appear here...")
