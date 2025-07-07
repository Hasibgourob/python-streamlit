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
    page_title="Not Available Product List for Supplier out of stock",
    page_icon=":Tiger:",
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
        st.title("Not Available Product List for Supplier out of stock")
        st.write("Not Available Product List")

        # %%
        conn = pymysql.connect(host='192.168.10.111',
                                port=int(45316),
                                user='saiful',
                                database='rokomari_qs',
                                password='@Ruu!Z%cGfPvWigF'
                                )        # %%
                # %%
        #conn = pymysql.connect(host='192.168.10.99',
        #                        port=int(3306),
        #                        user='nahid',
        #                        # username='ds_reports',
        #                        passwd='OPs652zUTbnXoP'
        #                        )
        # Create two columns for input
        # %%
        # %%
        # Create two columns for input
        # col1, col2 = st.columns(2)
        # with col1:
        #     from_date = st.date_input("From:", value=None)
            
        # with col2:
        #     to_date = st.date_input("To:", value=None)
            
        # %%
        # # from_date = '2024-03-15'
        # # to_date = '2024-04-30'
            
        #%%
        query1 = f"""
                    select p.id as Product_ID ,
                    p.nm as Product_name,
                    pap.communicator_person_id,
                    ac.nm as Communicator_name,
                    p.prc,
                    case
                        p.sts
                when 4 then "Supplier_Out_Of_Stock"
                end as Product_Status,
                p.qty
                from rokomari_qs.product p
                join rokomari_qs.product_admin_property pap on pap.id=p.id
                join rokomari_qs.account ac on pap.communicator_person_id = ac.id
                where p.sts=4
                and qty=0
                and p.product_type_id in (2,6);
            """

            #df = pd.read_sql_query(query1, conn)
        Cat = pd.read_sql_query(query1.format(), conn)
        
        #%%
        st.write('Supplier Out of Stock')
        st.dataframe(Cat) 
    
       #%%
    elif password != "":
        st.error("Incorrect password. Access denied.")

if __name__ == "__main__":
    app()
# %%