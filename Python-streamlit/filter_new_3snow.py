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

# Custom CSS for dark sidebar with white text, visible title, and light green background for selected filter
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

    /* Ensure dropdown icon (SVG) is black */
    [data-testid="stSidebar"] .stSelectbox [data-testid="stMarkdownContainer"] svg {
        color: black !important;
    }

    /* Light green background for selected month in dropdown */
    [data-testid="stSidebar"] .stSelectbox select:focus {
        background-color: #d4f1d4 !important;  /* Light green background when selected */
    }
    
    /* Fix the background color of selected options */
    .stSelectbox select option:checked {
        background-color: #d4f1d4 !important;  /* Light green background for selected option */
    }

    /* Dropdown button icon style */
    .stSelectbox select {
        color: black !important; /* Ensures the dropdown text is black */
    }
    
    /* Ensure title is visible */
    h1 {
        display: block !important;
        visibility: visible !important;
    }

    /* Reduce top padding */
    .block-container {
        padding-top: 3.1rem;
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
    # Title with proper positioning
    st.markdown("<h1 style='text-align: left; margin-top: 0; padding-top: 0;'>📊 A/B টেস্টিং রিপোর্ট</h1>", 
               unsafe_allow_html=True)
    
    # Show a loading spinner while loading data
    with st.spinner('ডেটা লোড হচ্ছে...'):
        # Load data
        df, error = load_data()

    if error:
        st.error(f"ডেটা লোড করতে ত্রুটি: {error}")
    else:
        st.success(f"ডেটা আপডেট হয়েছে: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
        st.snow()  # Add snowfall effect here
        # st.balloons()  # You can remove this line if using snowfall instead
        
        # --- MONTH-WISE FILTER --- 
        st.sidebar.header("ফিল্টার")
        
        # Extract unique months from the data
        df['month'] = df['date'].dt.to_period('M')  # Creates 'YYYY-MM' format
        unique_months = df['month'].unique()
        
        # Add "All" option to the months list
        all_months = ["All"] + sorted(unique_months.tolist())
        
        # Multiselect to select multiple months
        selected_months = st.sidebar.multiselect(
            "মাস নির্বাচন করুন", 
            options=all_months,
            default=["All"],
            format_func=lambda x: "All" if x == "All" else x.strftime('%B %Y')  # Shows "March 2025" or "All"
        )
        
        # Filter data based on selected months
        if "All" in selected_months:
            filtered_df = df.drop(columns=['month'])
        else:
            filtered_df = df[df['month'].isin(selected_months)].drop(columns=['month'])
        
        # Add index column starting from 1
        filtered_df.reset_index(drop=True, inplace=True)
        filtered_df.index += 1  # Start index from 1
        
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
