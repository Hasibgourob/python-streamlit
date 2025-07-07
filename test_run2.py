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

            # Check if 'supplier_id' column exists in the uploaded file
            if 'supplier_id' not in df.columns:
                st.error("The uploaded file does not contain a 'supplier_id' column.")
                return

            # Extract the supplier_id column and convert it to a list
            supplier_ids = df['supplier_id'].dropna().astype(int).tolist()  # Drop NaN values and convert to integers

            if len(supplier_ids) == 0:
                st.warning("The supplier_id column is empty.")
                return

            # Format the list of supplier IDs into a comma-separated string for the SQL query
            supplier_filter = ', '.join(map(str, supplier_ids))

            # Static product_type_id filter (as per your requirement, it's always [2, 6])
            product_type_filter = '2, 6'

            # SQL Queries
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

            query2 = f"""
                SELECT p.supplier_id,
                    SUM(cop.prc * cop.qty) AS total_sell_amount
                FROM cust_order co
                JOIN cust_order_product cop ON co.id = cop.cust_order_id
                JOIN product p ON cop.product_id = p.id
                WHERE p.supplier_id IN ({supplier_filter})
                AND p.product_type_id IN ({product_type_filter})
                AND co.ost IN (3, 4)
                AND cop.st NOT IN (2, 3)
                AND co.order_type NOT IN ('DATAENTRYPURPOSE', 'STOCK_PURCHASE', 'EVENTPURPOSE',
                        'EXCHANGEORDER', 'GIFTVOUCHER', 'EBOOK_ORDER', 'COURSE_ORDER')
                GROUP BY 1;
            """

            # Create a selectbox to choose which query to run
            query_choice = st.selectbox("Select Query to Run", ["Supplier Product Availability", "Total Sales"])

            # Button to execute the selected query
            if st.button("Run Query"):
                # Connect to the MySQL database
                conn = pymysql.connect(
                    host='192.168.10.111',
                    port=45316,
                    user='saiful',
                    database='rokomari_qs',
                    password='@Ruu!Z%cGfPvWigF'
                )

                # Execute the selected query and display results
                try:
                    if query_choice == "Supplier Product Availability":
                        query = query1
                    else:
                        query = query2
                    
                    result = pd.read_sql_query(query, conn)
                    st.write(f"Query Result - {query_choice}:")
                    st.dataframe(result)

                except Exception as e:
                    st.error(f"Error executing query: {e}")

                finally:
                    conn.close()

    elif password != "":
        st.error("Incorrect password. Access denied.")

if __name__ == "__main__":
    app()