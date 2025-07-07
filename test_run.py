import pandas as pd
import pymysql
import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Not Available Product List for Supplier out of stock",
    page_icon=":Tiger:",
    layout="wide",
    initial_sidebar_state="expanded",
)

def app():
    password_placeholder = st.empty()
    password = password_placeholder.text_input("Enter Password:", type="password", key="fhgf")

    if password == "123":
        st.success("Password is correct. Access granted!")
        password_placeholder.empty()  # Clear the password field
        st.write("Welcome to the protected Streamlit app!")

        # Sidebar for uploading CSV file
        uploaded_file = st.file_uploader("Upload a CSV file with supplier_id", type="csv")

        if uploaded_file is not None:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)

            # Check if 'seller_id' column exists in the uploaded file
            if 'supplier_id' not in df.columns:
                st.error("The uploaded file does not contain a 'supplier_id' column.")
                return

            # Extract the seller_id column and convert it to a list
            seller_ids = df['supplier_id'].dropna().astype(int).tolist()  # Drop NaN values and convert to integers

            if len(seller_ids) == 0:
                st.warning("The supplier_id column is empty.")
                return

            # Format the list of seller IDs into a comma-separated string for the SQL query
            supplier_filter = ', '.join(map(str, seller_ids))

            # Static product_type_id filter (as per your requirement, it's always [2, 6])
            product_type_filter = '2, 6'

            # Dynamically build the query based on the selected supplier IDs
            #Supplier entry vs current available product count
            query1 = f"""
                SELECT 
                    p2.supplier_id,
                    c.nm AS supplier_nm,
                    c.created AS entry_date,
                    COUNT(DISTINCT p2.id) AS product_count,
                    SUM(IF(p2.sts = 1, 1, 0)) AS available_product_count
                FROM product p2
                JOIN company c ON p2.supplier_id = c.id
                WHERE c.id IN ({supplier_filter})  -- Supplier IDs from the CSV
                AND p2.product_type_id IN ({product_type_filter})  -- Fixed filter for product_type_id (2, 6)
                GROUP BY 1;
            """
            

            # Connect to the MySQL database
            conn = pymysql.connect(
                host='192.168.10.111',
                port=45316,
                user='saiful',
                database='rokomari_qs',
                password='@Ruu!Z%cGfPvWigF'
            )

            # Execute the query and get the results
            try:
                Cat = pd.read_sql_query(query1, conn)
                st.write("Query Result:")
                st.dataframe(Cat)
            except Exception as e:
                st.error(f"Error executing query: {e}")
            finally:
                conn.close()

    elif password != "":
        st.error("Incorrect password. Access denied.")

if __name__ == "__main__":
    app()
