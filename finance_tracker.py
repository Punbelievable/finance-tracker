import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, time
import time;

from oauth import google_login
from firebase_config import initialize_firebase
from auth import authenticate_user

db = initialize_firebase()


# Setup
# page_title: title of the page shown in the browser tab
# layout: centered, wide, or sidebar
# page_icon: favicon
st.set_page_config(page_title="My Finance Tracker", layout="centered", page_icon="💰")
st.title("💰 Personal Finance Tracker")


# Google OAuth Login
if 'user' not in st.session_state:
    st.session_state.user = {
        'email': None,
        'name': None,
    }

with st.sidebar:
    if 'user' not in st.session_state or not st.session_state.user.get('email'):
        # Raw result from OAuth    
        auth_result = google_login()
        

        if auth_result and 'token' in auth_result:
            # Ensure timing sync
            time.sleep(1)
            
            user_info = authenticate_user(auth_result['token']['id_token'])

            if user_info:
                st.session_state.user = user_info
                st.rerun()
    else:
            custom_css = """
            <style>
                .welcome-container {
                    background-color: #f8f9fa;
                    border-radius: 10px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }
                .welcome-header {
                    color: #4CAF50;
                    font-size: 22px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }
                .welcome-email {
                    color: #666;
                    font-size: 16px;
                }
            </style>
            """
            st.markdown(custom_css, unsafe_allow_html=True)
            
            welcome_html = f"""
            <div class="welcome-container">
                <div class="welcome-header">{st.session_state.user['name']}</div>
                <div class="welcome-email">{st.session_state.user['email']}</div>
            </div>
            """
            st.markdown(welcome_html, unsafe_allow_html=True)
            
            if st.button("Logout"):
                st.session_state.clear()
                st.rerun()


# Only show app if logged in
if st.session_state.user['email']:
    
     # Initialize session state with Firestore data
    if 'transactions' not in st.session_state:
        try:
            # Load user-specific transactions
            docs = db.collection("users").document(st.session_state.user['email']).collection("transactions").stream()
            transactions = []
            
            for doc in docs:
                data = doc.to_dict()
                # Handle timestamp conversion
                if 'Date' in data and isinstance(data['Date'], datetime):
                    transactions.append({
                        "Date": data["Date"].date(),
                        "Description": data.get("Description", ""),
                        "Amount": data.get("Amount", 0.0),
                        "Category": data.get("Category", "Other")
                    })
            
            st.session_state.transactions = pd.DataFrame(transactions)
            
            if not transactions:
                st.session_state.transactions = pd.DataFrame(columns=["Date", "Description", "Amount", "Category"])
                
            st.session_state.transactions["Date"] = pd.to_datetime(st.session_state.transactions["Date"])
        except Exception as e:
            st.error(f"Error loading data: {e}")
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
            try:
                # Add transaction to Firestore
                # Create Firestore document
                transaction_data = {
                    "Date": datetime.combine(date, time.min),
                    "Description": desc,
                    "Amount": float(amount),
                    "Category": category
                }
                
                # Save to user-specific collection
                db.collection("users").document(st.session_state.user['email']).collection("transactions").add(transaction_data)
                
                
                # Update session state
                new_transaction = pd.DataFrame([transaction_data])
                new_transaction["Date"] = pd.to_datetime(new_transaction["Date"])
                st.session_state.transactions = pd.concat([st.session_state.transactions, new_transaction])
                
                st.success("Transaction added!")
                
            except Exception as e:
                st.error(f"Failed to save transaction: {e}")


    # Display transactions
    if not st.session_state.transactions.empty:
        st.subheader("Transaction History")
        
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
        by_category.plot.pie(ax=ax1, autopct="%1.1f%%", ylabel='')
        ax1.set_title("By Category")
        
        # Time trend
        by_date = st.session_state.transactions.set_index("Date").resample("W")["Amount"].sum()
        by_date.plot(ax=ax2, marker="o")
        ax2.set_title("Weekly Spending")
        ax2.set_xlabel("Date")
        ax2.set_ylabel("Amount ($)")
        
        st.pyplot(fig)
    else:
        st.info("No transactions yet. Add one above!")
else:
    st.warning("Please login to access your finance tracker")