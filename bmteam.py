#%%
import pandas as pd
#import pygwalker as pyg
import numpy as np
import plotly.express as px
import pymysql
import streamlit as st
#%%
# Set page configuration
st.set_page_config(
    page_title="Rok BM",
    page_icon=":table:",
    layout="wide",
    initial_sidebar_state="expanded",
)
#%%
def app():
    password_placeholder = st.empty()

    password = password_placeholder.text_input("Enter Password:", type="password",key="fhgf")

    if password == "123":
        
        st.success("Password is correct. Access granted!")
        # Clear the password field
        password_placeholder.empty()
        # Put the content of your app here
        st.write("Welcome to the protected Streamlit app!")
        # %%
        
        # %%
        # %% 
        #from_date = '2023-11-01'
        #to_date = '2023-12-01'
        # %%
        st.title("Sales report without ebook and course")
        st.write("Sales")

        # %%
        conn = pymysql.connect(host='192.168.10.107',
                                port=int(3306),
                                user='da-nahid',
                                # username='ds_reports',
                                passwd='%#bo2YCp#ZtTXwNP'
                                )
        # %%
        # Create two columns for input
        col1, col2 = st.columns(2)

        # Get the input dates from the user
        with col1:
            from_date = st.date_input("From:", value=None)

        with col2:
            to_date = st.date_input("To:", value=None)
            
            
        # %%
        #from_date = '2024-01-01'
        #to_date = '2024-02-01'
        Academic = [411,23,412,413,90,91,1996]
        ForeignBooks=[403, 406] 
        NonFiction=[31,32,9,10,14,15,18,19,21,22,26,27,28,404,42,6,79,29,36,41,620,7,34,405,409,8,17,266,24]
        Fiction=[363,364,407,408,410,414,13,11,12,35,20]
        Religious=[30]
        SuperStore=[2086]
        Electronics=[2024]
        BigganBaksho=[1982]
            
        academic_str = ','.join(map(str, Academic))
        ForeignBooks_str=','.join(map(str, ForeignBooks))
        NonFiction_str=','.join(map(str, NonFiction))
        Fiction_str=','.join(map(str, Fiction))
        Religious_str=','.join(map(str, Religious))
        SuperStore_str=','.join(map(str, SuperStore))
        Electronics_str=','.join(map(str, Electronics))
        BigganBaksho_str=','.join(map(str, BigganBaksho))
        #%% 
        st.write("For Academic"+str(Academic))
        st.write("For ForeignBooks"+str(ForeignBooks))
        st.write("For NonFiction"+str(NonFiction))
        st.write("For Fiction"+str(Fiction))
        st.write("For Religious"+str(Religious))
        st.write("For SuperStore"+str(SuperStore))
        st.write("For Electronics"+str(Electronics))
        st.write("For BigganBaksho"+str(BigganBaksho))
            
        #%%
        query1 = f"""
            SELECT
            year(a.sdt) as Year,
            monthname(a.sdt) as Month_Name,
            #cops.barcode_value,
            a.id as Order_ID,
            d.id Product_ID,
            d.nm as Product_Name,
            concat(e.clng,".",e.nm) Cat_Path_Name,
            concat(e.lng,".",e.id) Cat_Path,
            SUBSTRING_INDEX( SUBSTRING_INDEX( e.lng, '.', 3 ), '.',- 1 ) "Mother_Category_ID",
            SUBSTRING_INDEX( SUBSTRING_INDEX( e.clng, '.', 3 ), '.',- 1 ) "Mother_Category",
            e.id as LastCategory_ID,
            e.nm as Category_Name,
            a.order_type,
            case d.product_type_id 
            when 1 then "Book"
            when 2 then "Electronics"
            when 6 then "Superstore"
            else "Unkonwn"
            end as product_type_id,
            sum(c.prc*c.qty)  AS Price,
            sum(c.qty) as Qty,
            a.order_source_type as Order_Source,
            case 
            when substring_index(SUBSTRING_INDEX(e.lng, '.', 3), '.', -1) in (403, 406) then 'ForeignBooks'
            when substring_index(SUBSTRING_INDEX(e.lng, '.', 3), '.', -1) in (31,32,9,10,14,15,18,19,21,22,26,27,28,404,42,6,79,20,29,36,41,620,7,34,405,409,8,17,266,24) then 'Creative Non Fiction'
            when substring_index(SUBSTRING_INDEX(e.lng, '.', 3), '.', -1) in (363,364,407,408,410,414,13,11,12,35,20) then 'Creative Fiction'
            when substring_index(SUBSTRING_INDEX(e.lng, '.', 4), '.', -1) = 81 then 'Islamic'
            when substring_index(SUBSTRING_INDEX(e.lng, '.', 3), '.', -1) in (411, 23, 412, 413, 90, 91, 1996) then 'AcademicBooks'
            when substring_index(SUBSTRING_INDEX(e.lng, '.', 2), '.', -1) in (2086) and e.id not in (1982) then 'SuperStore'
            when substring_index(SUBSTRING_INDEX(e.lng, '.', 2), '.', -1) in (2024) and e.id not in (1982) then 'Electronics'
            when e.id=1982 then 'BigganBaksho' else 'Others Category' end   as BookCat
            FROM
            rokomari.cust_order a
            #left join rokomari.cust_order_product_selection cops on a.id = cops.cust_order_id 
             JOIN rokomari.cust_order_product c ON a. id = c.cust_order_id #and c.product_id=cops.product_id
             JOIN rokomari.product d ON c.product_id = d.id
             JOIN rokomari.category e ON e.id = d.category_id
            WHERE
            a.ost NOT IN ( 5,6 )
            AND c.st NOT IN ( 2,3 )
            and a.odt >= '{from_date}'
            AND a.odt <= '{to_date}'
            #Academic 411,23,412,413,90,91,1996,31
            #Super store 2024,2086
            #Non Fiction 30,6,7,8,14,15,17,18,21, 22,24, 26,34,620,409,405,41,36,32,42,29,19,404,9,10
            #Fiction: 363,364,407,410,408,13,414
            #religious=30
            #AND SUBSTRING_INDEX( SUBSTRING_INDEX( e.lng, '.', 3 ), '.',- 1 )  IN ({academic_str})
            and d.product_type_id not in (7)
            AND a.order_type NOT in ( 'DATAENTRYPURPOSE', 'STOCK_PURCHASE', 'EVENTPURPOSE', 'EXCHANGEORDER','GIFTVOUCHER')
            GROUP BY Order_ID, 
            Product_ID
            #cops.barcode_value
            """

            #df = pd.read_sql_query(query1, conn)
        Cat = pd.read_sql_query(query1.format(
            from_date=from_date, to_date=to_date), conn)
    


        # %% 
        #pyg.walk(Cat,dark='light')
        #st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")

                                   
        # %%
        st.sidebar.header("Please_Filter_Here")

        #  %%
        orderType = st.sidebar.multiselect(
            "Select the Order Type:",
            options=Cat["order_type"].unique(),
            default=Cat["order_type"].unique()
        )
        # %%
        CatType = st.sidebar.multiselect(
            "Select the CatType:",
            options=Cat["BookCat"].unique(),
            default=Cat["BookCat"].unique()
        )
        # %%
        motherCat = st.sidebar.multiselect(
            "Select the Mother Category:",
            options=Cat["Mother_Category"].unique(),
            default=Cat["Mother_Category"].unique(),
        )

        # %%
        productType = st.sidebar.multiselect(
            "Select the Product Type:",
            options=Cat["product_type_id"].unique(),
            default=Cat["product_type_id"].unique()
        )

        # %%
        df_selection = Cat.query(
            "order_type == @orderType & Mother_Category==@motherCat & product_type_id == @productType & BookCat==@CatType" 
        )

        # %%
        # Check if the dataframe is empty:
        if df_selection.empty:
            st.warning("No data available based on the current filter settings!")
            st.stop() # This will halt the app from further execution.

        # %%
        # TOP KPI's
        total_sales = int(df_selection["Price"].sum())

        # %%
        average_P_Amount = round(df_selection["Price"].mean(), 1)

        # %%
        #Product_count =  int(df_selection["barcode_value"].count())
        # %%
        Order_Count =  int(df_selection["Order_ID"].nunique())

        # %%
        left_column, middle_column, right_column = st.columns(3)

        with left_column:
            st.subheader("Total Sales:")
            st.subheader(f"BDT  {total_sales:}")
        with middle_column:
            st.subheader("Avg_P_Amount:")
            st.subheader(f" BDT {average_P_Amount:}")
        #with right_column:
            #st.subheader("Barcode:")
            #st.subheader(f"{Product_count:}")
            #st.markdown("""---""")
        with right_column:
            st.subheader("Order_Count:")
            st.subheader(f"{Order_Count:}")
            st.markdown("""---""")
    
        # %%
        sales_by_product_line = (
            df_selection.groupby(by=["Month_Name"])[["Price"]].sum()
        )

        # %%
        st.write('Order_Amount')
        st.dataframe(sales_by_product_line)  
        
        # %%
        sales_by_product_line1 = df_selection.groupby(by=["Month_Name"])[["Order_ID"]].nunique()
        st.write('Order_Count')
        st.dataframe(sales_by_product_line1)  

        # %%
        #Pivot the data
        pivoted_data = df_selection.pivot_table(
            index="BookCat",
            columns=["Year", "Month_Name"],
            values=["Price", "Order_ID", "Qty"],
            aggfunc={'Price': 'sum', 'Qty':'sum', 'Order_ID': 'nunique'},
            fill_value=0
        )# Optional: Fill missing values with 0)

            # Print the pivoted DataFrame
            #print(pivoted_data)
        # %%
        st.write('Cat_type wise amount and barcode count')
        st.dataframe(pivoted_data)
        
        # %%
        Order_Source = df_selection.groupby(['Year','Month_Name','Order_Source']).agg({'Price': 'sum', 'Qty':'sum', 'Order_ID':'nunique'}).reset_index()
        #%%
        st.write('Order_Source wise sales amount and Order count')
        st.dataframe(Order_Source)  
    
        # %%
        #category=Cat.groupby('Category_Name')['barcode_value'].count().reset_index()

        category = df_selection.groupby(['Mother_Category','Cat_Path_Name','Category_Name']).agg({'Price': 'sum', 'Qty':'sum', 'Order_ID':'nunique'}).reset_index()
        #%%
        st.write('Last_cat wise sales amount and Order count')
        st.dataframe(category)  
        
        #%%
        Book = df_selection.groupby(['Product_ID','Product_Name']).agg({'Price': 'sum', 'Qty':'sum', 'Order_ID':'nunique'}).reset_index()
        st.write('Product sales')
        st.dataframe(Book)
       #%%
    elif password != "":
        st.error("Incorrect password. Access denied.")

if __name__ == "__main__":
    app()
# %%