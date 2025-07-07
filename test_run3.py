import pandas as pd
import pymysql
import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="📊 Query Search",

    page_icon="🅡",
    layout="wide",
    initial_sidebar_state="expanded",
)

def app():
    password_placeholder = st.empty()
    password = password_placeholder.text_input("Enter Password:", type="password", key="fhgf")

    if password == "123":
        st.success("Password is correct. Access granted!")
        password_placeholder.empty()
        st.write("Welcome to the protected Streamlit app!")

        # Sidebar for uploading CSV file
        uploaded_file = st.file_uploader("Upload a CSV file with supplier_id", type="csv")

        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)

            # Check if the 'supplier_id' column exists
            if 'supplier_id' not in df.columns:
                st.error("The uploaded file does not contain a 'supplier_id' column.")
                return

            # Strip any leading/trailing spaces and ensure the column contains integers
            df['supplier_id'] = df['supplier_id'].astype(str).str.strip()  # Make sure the values are strings without spaces
            df = df[df['supplier_id'].str.isnumeric()]  

            # Convert to integers and drop any missing values
            supplier_ids = df['supplier_id'].dropna().astype(int).tolist()

            if len(supplier_ids) == 0:
                st.warning("The supplier_id column is empty or contains invalid values.")
                return

            # Convert supplier_ids to a formatted string to be used in SQL IN clause
            supplier_filter = ', '.join(map(str, supplier_ids))

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
            # Ensure the query string is clean by replacing any non-breaking spaces or hidden characters
            query3 = f"""
                SELECT sl.supplier_id, sl.payment_mode
                FROM supplier_ledger sl
                JOIN (
                    SELECT supplier_id, MAX(created) AS max_created
                    FROM supplier_ledger
                    WHERE supplier_id IN ({supplier_filter})
                    AND payment_mode NOT IN ('NONE','RETURN','CHEQUE','CASH_CREDIT','BALANCE_TRANSFER')
                    GROUP BY supplier_id
                ) latest
                ON sl.supplier_id = latest.supplier_id
                AND sl.created = latest.max_created
                AND sl.payment_mode NOT IN ('NONE','RETURN','CHEQUE','CASH_CREDIT','BALANCE_TRANSFER')
                GROUP BY 1;
            """

            # Clean non-breaking spaces (this handles hidden characters like '\xa0')
            query3 = query3.replace('\xa0', ' ')

            query_choice = st.selectbox("Select Query to Run", [
                "Supplier Product Availability", 
                "Total Sales", 
                "Seller Payment Method"
            ])

            if st.button("Run Query"):
                try:
                    conn = pymysql.connect(
                        host='192.168.10.111',
                        port=45316,
                        user='saiful',
                        database='rokomari_qs',
                        password='@Ruu!Z%cGfPvWigF'
                    )

                    if query_choice == "Supplier Product Availability":
                        query = query1

                    elif query_choice == "Total Sales":
                        query = query2

                    elif query_choice == "Seller Payment Method":
                        query = query3

                    # Run query
                    with st.spinner("Running query..."):
                        result = pd.read_sql_query(query, conn)
                        st.write(f"Query Result - {query_choice}:")
                        st.dataframe(result)
                        st.download_button(
                            label="Download CSV",
                            data=result.to_csv(index=False),
                            file_name=f"{query_choice.replace(' ', '_')}_results.csv",
                            mime="text/csv"
                        )

                except Exception as e:
                    st.error(f"Error executing query: {e}")

                finally:
                    conn.close()

    elif password != "":
        st.error("Incorrect password. Access denied.")

if __name__ == "__main__":
    app()
