import streamlit as st
import pandas as pd
import time
from datetime import datetime

# Configuration
st.set_page_config(
    page_title="📊 A/B টেস্টিং রিপোর্ট", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# File path - use raw string or forward slashes
CSV_PATH = r'C:/Users/DA/Desktop/strmlit.csv'

@st.cache_data(ttl=60)  # Cache for 60 seconds
def load_data():
    try:
        df = pd.read_csv(CSV_PATH, encoding='utf-8-sig')
        # Convert 'date' column to datetime (if not already)
        df['date'] = pd.to_datetime(df['date'], format='%d.%m.%y')  # Adjust format if needed
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)

# Main app
def main():
    st.title("📊 A/B টেস্টিং রিপোর্ট")
    
    # Show a loading spinner while loading data
    with st.spinner('ডেটা লোড হচ্ছে...'):
        # Load data
        df, error = load_data()

    if error:
        st.error(f"ডেটা লোড করতে ত্রুটি: {error}")
    else:
        st.success(f"ডেটা আপডেট হয়েছে: {datetime.now().strftime('%H:%M:%S')}")
        st.balloons()  # Show balloons effect on successful data load
        
        # --- MONTH-WISE FILTER ---
        st.sidebar.header("ফিল্টার")
        
        # Extract unique months from the data
        df['month'] = df['date'].dt.to_period('M')  # Creates 'YYYY-MM' format
        unique_months = df['month'].unique()
        
        # Dropdown to select month
        selected_month = st.sidebar.selectbox(
            "মাস নির্বাচন করুন", 
            options=unique_months,
            format_func=lambda x: x.strftime('%B %Y')  # Shows "March 2025" instead of "2025-03"
        )
        
        # Filter data based on selection
        filtered_df = df[df['month'] == selected_month].drop(columns=['month'])
        
        # Display filtered data
        st.dataframe(filtered_df, use_container_width=True)
    
    # Manual refresh with a progress bar
    if st.button("ডেটা রিফ্রেশ করুন"):
        progress_bar = st.progress(0)  # Initialize the progress bar
        for i in range(100):
            time.sleep(0.05)  # Simulate the refreshing process
            progress_bar.progress(i + 1)  # Update progress
        st.cache_data.clear()  # Clear the cache after refreshing
        #st.experimental_rerun()  # Optionally rerun the script

    # Auto-refresh toggle
    auto_refresh = st.checkbox("স্বয়ংক্রিয় রিফ্রেশ সক্রিয় করুন", True)
    if auto_refresh:
        progress_bar = st.progress(0)  # Initialize the progress bar for auto-refresh
        for i in range(100):
            time.sleep(0.05)  # Simulate the refreshing process
            progress_bar.progress(i + 1)  # Update progress
        #st.experimental_rerun()  # Auto-refresh on every loop

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
