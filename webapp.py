import streamlit as st
import pandas as pd
import time
from datetime import datetime

# Configuration
st.set_page_config(
    page_title=" A/B 📊টেস্টিং রিপোর্ট", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# File path - use raw string or forward slashes
CSV_PATH = r'C:/Users/DA/Desktop/strmlit.csv'
 
@st.cache_data(ttl=60)  # Cache for 60 seconds
def load_data():
    try:
        df = pd.read_csv(CSV_PATH, encoding='utf-8-sig')
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)

# Main app
def main():
    st.title("📊 A/B টেস্টিং রিপোর্ট")
    
    # Load data
    df, error = load_data()
    
    # Display status
    if error:
        st.error(f"ডেটা লোড করতে ত্রুটি: {error}")
    else:
        st.success(f"ডেটা আপডেট হয়েছে: {datetime.now().strftime('%H:%M:%S')}")
        st.dataframe(df, use_container_width=True)
    
    # Manual refresh
    if st.button("ডেটা রিফ্রেশ করুন"):
        st.cache_data.clear()
        st.experimental_rerun()
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("স্বয়ংক্রিয় রিফ্রেশ সক্রিয় করুন", True)
    if auto_refresh:
        time.sleep(5)  # Refresh every 5 seconds
        #st.experimental_rerun()

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