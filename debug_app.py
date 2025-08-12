import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Debug Test",
    page_icon="🔍",
    layout="wide"
)

def main():
    """Minimal debug version."""
    
    st.title("🔍 Debug Test")
    st.write("If you can see this, the app is working!")
    
    # Test basic functionality
    st.subheader("Basic Test")
    
    if st.button("Click me"):
        st.success("Button works!")
    
    # Test sidebar
    st.sidebar.header("Sidebar Test")
    st.sidebar.write("Sidebar is working!")
    
    # Test session state
    if 'test_counter' not in st.session_state:
        st.session_state.test_counter = 0
    
    if st.button("Increment Counter"):
        st.session_state.test_counter += 1
    
    st.write(f"Counter: {st.session_state.test_counter}")

if __name__ == "__main__":
    main()
