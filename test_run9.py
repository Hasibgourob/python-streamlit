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
st.markdown("""
    <style>
        /* Background and text tweaks */
        .stApp {
            background-color:#d2b4de;
            color: #4B2C20;
        }

        /* Button style */
        .stButton>button {
            background-color: #a3e4d7 ;
            color: black;
            border-radius: 8px;
            border: none;
            padding: 0.5em 1em;
        }

        .stButton>button:hover {
            background-color: #52ff9a;
            font-weight: bold;
            color: black;
        }

        /* Input fields */
        .stTextInput>div>div>input {
            background-color: #d4e6f1;
        }

        /* Header color */
        h1, h2, h3, h4 {
            color: #4B2C20;
        }
    </style>
""", unsafe_allow_html=True)


def app():
    password_placeholder = st.empty()
    password = password_placeholder.text_input("Enter Password:", type="password", key="fhgf")

    if password == "123":
        st.success("Password is correct. Access granted!")
        password_placeholder.empty()
        st.write("Welcome to the protected Streamlit app!")

        # 👇 Then continue with file upload and query logic
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

            # SQL Queries (q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12)
            q1 = f"""
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

            q2 = f"""
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
            
            q3 = f"""
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
            
            q4 = f'''
            SELECT p.id, p.pdt as entry_date
            FROM product p
            JOIN company c on p.supplier_id = c.id
            WHERE pdt >= '2025-01-01'
            AND product_type_id IN ({product_type_filter})
            AND c.communicator_id IN (1117083)
            GROUP BY p.id
            '''
            
            q5 = f'''
            SELECT pl.barcode_value, 
                   pl.previous_status,
                   pl.current_status,
                   pl.created,
                   pcibl.is_stock_barcode,
                   cop.prc
            FROM cust_order co
            JOIN cust_order_product cop ON co.id = cop.cust_order_id
            JOIN cust_order_product_selection cops ON cop.cust_order_id = cops.cust_order_id
                                               AND cop.product_id = cops.product_id
            JOIN product_copy_inventory_box_log pcibl ON cops.barcode_value = pcibl.barcode_value
            JOIN product p ON cop.product_id = p.id
            JOIN product_copy_inventory_box_status_change_log pl ON pcibl.barcode_value = pl.barcode_value
            JOIN company c ON p.supplier_id = c.id
            WHERE p.product_type_id IN ({product_type_filter})
            AND pl.current_status = 'SOLD'
            AND cop.st NOT IN (2, 3, 4)
            AND co.ost IN (3, 4)
            AND co.order_type NOT IN ('COURSE_ORDER', 'DATAENTRYPURPOSE', 'EBOOK_ORDER', 'EVENTPURPOSE', 'EXCHANGEORDER', 'GIFTVOUCHER', 'STOCK_PURCHASE')
            AND c.communicator_id IN (1117083)
            AND pcibl.created >= '2025-01-01';
            '''
            # new supplier entry list from this to that date

            q6 = f'''
            select c.id as supplier_id,
                c.nm
            from product p
            join company c on p.supplier_id = c.id
            where c.created >='2025-06-01' and c.created < '2025-07-01'
            and p.product_type_id in (2,6)
            group by 1;
            '''


            # supplier sales vs purchase
            q7 = f'''
            SELECT
                    p.supplier_id,
                sum(cop.prc) as Total_Sales_amount,
            #        count(distinct cops.barcode_value) as Total_sales_quantity
                    sum(case
                        when box.purchase_price is null then boxlog.purchase_price
                        when boxlog.purchase_price is null then box.purchase_price
                    end) as Purchase_Amount

            FROM cust_order co
            join cust_order_product cop on co.id = cop.cust_order_id
            join cust_order_product_selection cops on cop.cust_order_id = cops.cust_order_id
                                            and cop.product_id = cops.product_id
            JOIN product p ON cops.product_id = p.id
            # join product_cat pc on p.id = pc.product_id
            left join product_copy_inventory_box box on cops.barcode_value = box.barcode_value
                                                                            AND box.barcode_value IS NOT NULL
            left join product_copy_inventory_box_log boxlog on cops.barcode_value = boxlog.barcode_value
                                                                        AND box.barcode_value IS NULL
                                                                        AND boxlog.barcode_value IS NOT NULL
            WHERE
            co.ost in (3,4)
            and cop.st not in (2,3)
            # and pc.category_id=1982
            and p.product_type_id in (2,6)
            and co.order_type not in ('DATAENTRYPURPOSE', 'STOCK_PURCHASE', 'EVENTPURPOSE',
                                        'EXCHANGEORDER','GIFTVOUCHER', 'EBOOK_ORDER', 'COURSE_ORDER')
            and p.supplier_id in ({supplier_filter} )
            GROUP BY 1;
            '''

            # life time order amount
            q8= f'''
            select p.supplier_id,
                sum(cop.prc*cop.order_place_time_qty) as total_sells
            FROM cust_order co
            join cust_order_product cop on co.id = cop.cust_order_id
            join product p on cop.product_id = p.id
            where p.supplier_id in ({supplier_filter} )
            and
            #     co.ost in (3,4)
            # cop.st not in (2,3)
            p.product_type_id in (2,6)
            and co.order_type not in ('DATAENTRYPURPOSE', 'STOCK_PURCHASE', 'EVENTPURPOSE',
                                        'EXCHANGEORDER','GIFTVOUCHER', 'EBOOK_ORDER', 'COURSE_ORDER')
            group by 1;
            '''

            # na_total
            q9 = f''' 
            select
            p.supplier_id,
            sum(cop.order_place_time_qty * cop.prc) as na_total
            from cust_order co
            join cust_order_product cop on co.id = cop.cust_order_id
            join product p on cop.product_id = p.id
            where
            #     co.ost in (3,4)
            cop.st in (2)
            and p.product_type_id in (2,6)
            and co.order_type not in ('DATAENTRYPURPOSE', 'STOCK_PURCHASE', 'EVENTPURPOSE',
                                        'EXCHANGEORDER','GIFTVOUCHER', 'EBOOK_ORDER', 'COURSE_ORDER')
            and p.supplier_id in ({supplier_filter})
            group by 1;
            '''
            # ues panel or not
            q10= f'''
            SELECT s.id AS supplier_id,
                CASE
                    WHEN si.supplier_id IS NOT NULL OR sr.seller_id IS NOT NULL THEN 'Yes'
                    ELSE 'No'
                END AS use_panel
            FROM supplier s
            LEFT JOIN seller_product_inbox si ON s.id = si.supplier_id
            LEFT JOIN seller_product_edit_request sr ON s.id = sr.seller_id
            WHERE s.id IN ({supplier_filter})
            GROUP BY 1;
            '''


            # cp
            q11= f'''
            select pp.supplier_id,
            sum(dis) as cp
            from pro_purchase pp
            join (
                select pp.supplier_id, pp.id as ppid
                from pro_purchase pp
                join pro_purchase_product ppp on pp.id = ppp.pro_purchase_id
                join product p on ppp.product_id = p.id
                where pp.supplier_id in ({supplier_filter})
                and p.product_type_id in (2,6)
                group by 1,2
                ) a on a.ppid = pp.id
                and pp.supplier_id = a.supplier_id
            group by 1;
            '''

            # purchase time
            q12= f'''
            SELECT
             p.supplier_id,
            co.id as order_id,
            co.cdt as approved_date,
            pp.id as purchase_id,
            pp.pdt as purchase_date

            FROM cust_order co
            join cust_order_product cop on co.id = cop.cust_order_id
            join cust_order_product_selection cops on cop.cust_order_id = cops.cust_order_id
                                            and cop.product_id = cops.product_id
            JOIN product p ON cops.product_id = p.id
            # join product_cat pc on p.id = pc.product_id
            # left join product_copy_inventory_box box on cops.barcode_value = box.barcode_value
            #                                                                 AND box.barcode_value IS NOT NULL
            left join product_copy_inventory_box_log boxlog on cops.barcode_value = boxlog.barcode_value
            #                                                             AND box.barcode_value IS NULL
            #                                                             AND boxlog.barcode_value IS NOT NULL
            join pro_purchase pp on boxlog.pro_purchase_id = pp.id
            WHERE
            co.ost in (3,4)
            and cop.st not in (2,3)
            # and pc.category_id=1982
            and p.product_type_id in (2,6)
            and co.order_type not in ('DATAENTRYPURPOSE', 'STOCK_PURCHASE', 'EVENTPURPOSE',
                                        'EXCHANGEORDER','GIFTVOUCHER', 'EBOOK_ORDER', 'COURSE_ORDER')
            and co.cdt >= '2024-12-01' and co.cdt < '2025-06-01'
            and p.supplier_id in ({supplier_filter} )
            and boxlog.is_stock_barcode = 0
            GROUP BY 1,2,3,4
            having cdt<pdt;
            '''

            # category count
            q13= f'''
            select supplier_id,
                count(distinct category_id) as category_count
            from product p
            where
                product_type_id in (2,6)
            and supplier_id in ({supplier_filter} )
            group by 1;
            '''

            query_choice = st.selectbox("Select Query to Run", [
                "Supplier Product Availability", 
                "Total Sales", 
                "Seller Payment Method",
                "Entry vs Sale", 
                "New Supplier Entry List",
                "Supplier Sales vs Purchase",
                "Lifetime Order Amount",
                "NA Total",
                "Use Panel or Not",
                "CP",
                "Purchase Time",
                "Category Count"
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

                    latest_query = "SELECT odt FROM cust_order ORDER BY odt DESC LIMIT 1;"
                    latest_df = pd.read_sql_query(latest_query, conn)

                    if not latest_df.empty:
                        last_odt = pd.to_datetime(latest_df.iloc[0, 0])
                        timestamp = last_odt.strftime('%Y-%m-%d') + '&nbsp;&nbsp;&nbsp;&nbsp;' + last_odt.strftime('%H:%M:%S')

                        st.markdown(f"""
                        <span style='font-size:22px;'>
                            📅 Database updated:
                            <span style='background-color: white; padding: 4px 8px; border-radius: 16px; color: black;'>
                                {timestamp}
                            </span>
                        </span>
                        <br><br>
                        """, unsafe_allow_html=True)


                    else:
                        st.warning("Could not fetch last update timestamp.")



                    # Execute the corresponding query based on user selection
                    if query_choice == "Supplier Product Availability":
                        result = pd.read_sql_query(q1, conn)
                    elif query_choice == "Total Sales":
                        result = pd.read_sql_query(q2, conn)
                    elif query_choice == "Seller Payment Method":
                        result = pd.read_sql_query(q3, conn)

                        # Find missing supplier_ids or those with null/blank payment methods
                        missing_suppliers = []
                        for supplier_id in supplier_ids:
                            if supplier_id not in result['supplier_id'].values or result[result['supplier_id'] == supplier_id]['payment_mode'].isnull().any():
                                missing_suppliers.append(supplier_id)

                        # Add missing suppliers to the DataFrame with payment_mode set to 'CASH'
                        missing_data = pd.DataFrame({
                            'supplier_id': missing_suppliers,
                            'payment_mode': ['CASH'] * len(missing_suppliers)
                        })

                        # Append the missing suppliers to the result
                        result = pd.concat([result, missing_data], ignore_index=True)

                    elif query_choice == "Entry vs Sale":
                        prod = pd.read_sql_query(q4, conn)
                        sa = pd.read_sql_query(q5, conn)
                        s = sa[sa['current_status'] == 'SOLD']
                        s['id'] = s['barcode_value'].str.split("#").str[0].astype(int)
                        l = pd.merge(prod, s, on='id', how='inner')
                        l['ym'] = l.created.dt.to_period('M')
                        l['dif'] = l.created - l.entry_date
                        l1 = l[l.dif <= pd.to_timedelta(30, unit='D')]
                        prod['ym'] = prod.entry_date.dt.to_period('M')
                        l2 = pd.merge(prod.groupby('ym').agg({
                            'id': 'nunique'
                        }).reset_index(),
                            l1.groupby('ym').agg({
                                'id': 'nunique'
                            }).reset_index(), on='ym'
                        ).rename(columns={'id_x': 'entry', 'id_y': 'sold'})
                        l2['percentage'] = l2.sold / l2.entry * 100
                        result = l2

                    elif query_choice == "New Supplier Entry List":
                        result = pd.read_sql_query(q6, conn)
                    elif query_choice == "Supplier Sales vs Purchase":
                        result = pd.read_sql_query(q7, conn)                    
                    elif query_choice == "Lifetime Order Amount":
                        result = pd.read_sql_query(q8, conn)                    
                    elif query_choice == "NA Total":
                        result = pd.read_sql_query(q9, conn)                    
                    elif query_choice == "Use Panel or Not":
                        result = pd.read_sql_query(q10, conn) 
                    elif query_choice == "CP":
                        result = pd.read_sql_query(q11, conn) 
                    elif query_choice == "Purchase Time":
                        result = pd.read_sql_query(q12, conn) 
                    elif query_choice == "Category Count":
                        result = pd.read_sql_query(q13, conn) 

                    st.write(f"{query_choice} Results:")
                    st.dataframe(result)
                    st.download_button(
                        label="Download CSV",
                        data=result.to_csv(index=False),
                        file_name=f"{query_choice.replace(' ', '_').lower()}.csv",
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
