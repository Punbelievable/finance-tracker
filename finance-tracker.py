import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Setup
# page_title: title of the page shown in the browser tab
# layout: centered, wide, or sidebar
# page_icon: favicon
st.set_page_config(page_title="My Finance Tracker", layout="centered", page_icon="💰")
st.title("💰 Personal Finance Tracker")

# Initialize session state to store transactions
if 'transactions' not in st.session_state:
    st.session_state.transactions = pd.DataFrame(columns=["Date", "Description", "Amount", "Category"])


# Add transaction form
with st.form("transaction_form"):
    st.subheader("Add New Transaction")
    date = st.date_input("Date", datetime.today())
    desc = st.text_input("Description")
    # step: increment value
    amount = st.number_input("Amount ($)", min_value=0.01, step=0.01)
    category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Bills", "Shopping", "Other"])


    if st.form_submit_button("Add Transaction"):
        new_transaction = pd.DataFrame([[date, desc, amount, category]], 
                                      columns=["Date", "Description", "Amount", "Category"])
        # Concatenate the new transaction to the existing transactions
        st.session_state.transactions = pd.concat([st.session_state.transactions, new_transaction])
        st.success("Transaction added!")


# Display transactions
if not st.session_state.transactions.empty:
    st.subheader("Transaction History")
    
    st.session_state.transactions["Date"] = pd.to_datetime(st.session_state.transactions["Date"])
    
    display_df = (
        st.session_state.transactions
        .sort_values("Date", ascending=False)
        .reset_index(drop=True)
    )

    # Start numbering from 1 instead of 0
    display_df.index = display_df.index + 1
    st.dataframe(display_df)

    # Summary stats
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Spent", f"${st.session_state.transactions['Amount'].sum():.2f}")
    with col2:
        st.metric("Most Spent On", st.session_state.transactions['Category'].mode()[0])
    

    # Visualizations
    st.subheader("Spending Breakdown")
    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(17, 8))
    
    # Pie chart
    by_category = st.session_state.transactions.groupby("Category")["Amount"].sum()
    by_category.plot.pie(ax=ax1, autopct="%1.1f%%")
    ax1.set_title("By Category")
    
    # Time trend
    st.session_state.transactions["Date"] = pd.to_datetime(st.session_state.transactions["Date"])
    by_date = st.session_state.transactions.set_index("Date").resample("W")["Amount"].sum()
    by_date.plot(ax=ax2, marker="o")
    ax2.set_title("Weekly Spending")
    
    st.pyplot(fig)
else:
    st.info("No transactions yet. Add one above!")