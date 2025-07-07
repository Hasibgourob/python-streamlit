import streamlit as st
import pandas as pd
import time
from datetime import datetime

# Configuration with custom CSS
st.set_page_config(
    page_title="📊 A/B টেস্টিং রিপোর্ট", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark sidebar with white text and proper title visibility
st.markdown(
    """
    <style>
    /* Dark sidebar with white text */
    [data-testid="stSidebar"] {
        background-color: #111111;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* White dropdown icon */
    [data-testid="stSidebar"] .stSelectbox [data-testid="stMarkdownContainer"] svg {
        color: white !important;
    }
    
    /* Ensure title is fully visible at top */
    .stApp {
        margin-top: -50px;
    }
    h1 {
        padding-top: 0;
        margin-top: 0;
    }
    
    /* Adjust main content area */
    .block-container {
        padding-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# File path - use raw string or forward slashes
CSV_PATH = r'C:/Users/DA/Desktop/strmlit.csv'

@st.cache_data(ttl=60)  # Cache for 60 seconds
def load_data():
    try:
        df = pd.read_csv(CSV_PATH, encoding='utf-8-sig')
        # Convert 'date' column to datetime with dd-mm-yyyy format
        df['date'] = pd.to_datetime(df['date'], dayfirst=True)  # For dd-mm-yyyy format
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)

# Main app
def main():
    # Title at the very top
    st.markdown("<h1 style='padding-top: 0; margin-top: 0;'>📊 A/B টেস্টিং রিপোর্ট</h1>", 
               unsafe_allow_html=True)
    
    # Show a loading spinner while loading data
    with st.spinner('ডেটা লোড হচ্ছে...'):
        # Load data
        df, error = load_data()

    if error:
        st.error(f"ডেটা লোড করতে ত্রুটি: {error}")
    else:
        st.success(f"ডেটা আপডেট হয়েছে: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
        st.balloons()  # Show balloons effect on successful data load
        
        # --- MONTH-WISE FILTER ---
        st.sidebar.header("ফিল্টার")
        
        # Extract unique months from the data
        df['month'] = df['date'].dt.to_period('M')  # Creates 'YYYY-MM' format
        unique_months = df['month'].unique()
        
        # Add "All" option to the months list
        all_months = ["All"] + sorted(unique_months.tolist())
        
        # Dropdown to select month
        selected_month = st.sidebar.selectbox(
            "মাস নির্বাচন করুন", 
            options=all_months,
            format_func=lambda x: "All" if x == "All" else x.strftime('%B %Y')  # Shows "March 2025" or "All"
        )
        
        # Filter data based on selection
        if selected_month == "All":
            filtered_df = df.drop(columns=['month'])
        else:
            filtered_df = df[df['month'] == selected_month].drop(columns=['month'])
        
        # Display filtered data with full width and format date as dd-mm-yyyy
        st.dataframe(filtered_df.style.format({'date': lambda x: x.strftime('%d-%m-%Y') if not pd.isnull(x) else ''}), 
                   use_container_width=True)
    
    # Manual refresh with a progress bar
    if st.button("ডেটা রিফ্রেশ করুন"):
        progress_bar = st.progress(0)  # Initialize the progress bar
        for i in range(100):
            time.sleep(0.05)  # Simulate the refreshing process
            progress_bar.progress(i + 1)  # Update progress
        st.cache_data.clear()  # Clear the cache after refreshing

    # Auto-refresh toggle
    auto_refresh = st.checkbox("স্বয়ংক্রিয় রিফ্রেশ সক্রিয় করুন", True)
    if auto_refresh:
        progress_bar = st.progress(0)  # Initialize the progress bar for auto-refresh
        for i in range(100):
            time.sleep(0.05)  # Simulate the refreshing process
            progress_bar.progress(i + 1)  # Update progress

if __name__ == "__main__":
    # This prevents the ScriptRunContext warnings
    import streamlit.runtime.scriptrunner as scriptrunner
    if not scriptrunner.get_script_run_ctx():
        from streamlit.web import cli as stcli
        import sys
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
    else:
        main()