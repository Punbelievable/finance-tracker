import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, time
from time import sleep


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
            sleep(1)
            
            user_info = authenticate_user(auth_result['token']['id_token'])

            if user_info:
                st.session_state.user = user_info
                st.rerun()
    else:
            custom_css = """
            <style>
                .profile-container {
                    background-color: #333842;
                    border-radius: 12px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);  /* Subtle shadow for depth */
                    text-align: center;
                    border: 1px solid #444c56;
                }
                .name {
                    color: #58a6ff;
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }
                .email {
                    color: #adbac7;
                    font-size: 16px;
                }
            </style>
            """
            st.markdown(custom_css, unsafe_allow_html=True)
            
            welcome_html = f"""
            <div class="profile-container">
                <div class="name">{st.session_state.user['name']}</div>
                <div class="email">{st.session_state.user['email']}</div>
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
                
            time = st.time_input("Select Time", value=time(12, 0), step=15 * 60)
                
            desc = st.text_input("Description")
            # step: increment value
            amount = st.number_input("Amount ($)", min_value=0.01, step=0.01)
            category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Bills", "Shopping", "Other"])


            if st.form_submit_button("Add Transaction"):
                try:
                    transaction_datetime = datetime.combine(date, time)
                        
                    # Add transaction to Firestore
                    # Create Firestore document
                    transaction_data = {
                        "Date": transaction_datetime,
                        "Description": desc,
                        "Amount": float(amount),
                        "Category": category
                    }
                        
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




            st.subheader("Statistics")
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
            
            
            
            # Trend for current month
            current_month = datetime.today().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            monthly_transactions = st.session_state.transactions[
                (st.session_state.transactions["Date"].dt.month == current_month.month) &
                (st.session_state.transactions["Date"].dt.year == current_month.year)
            ]

            if not monthly_transactions.empty:
                # Group by day of the month
                by_day = monthly_transactions.groupby(monthly_transactions["Date"].dt.day)["Amount"].sum()
                
                # Ensure all days in the month are represented with zeros
                days_in_month = (current_month.replace(month=current_month.month % 12 + 1, day=1) - 
                                current_month).days if current_month.month != 12 else 31
                all_days = pd.Series(0, index=range(1, days_in_month + 1))
                by_day_full = all_days.add(by_day, fill_value=0)
                
                # Plot daily spending
                by_day_full.plot(ax=ax2, marker="o", label="Daily Spending")
                ax2.set_title(f"Spending in {current_month.strftime('%B %Y')}")
                ax2.set_xlabel("Day of Month")
                ax2.set_ylabel("Amount ($)")
                
                # Customize x-axis to show all days in the month
                ax2.set_xticks(range(1, days_in_month + 1))
                
                # Add vertical grid lines
                ax2.grid(True, which="major", axis="x", linestyle="--", alpha=0.7)
                
                ax2.legend()
            else:
                ax2.text(0.5, 0.5, "No data for this month", ha="center", va="center")
                ax2.set_title(f"Spending in {current_month.strftime('%B %Y')}")
                ax2.set_xlabel("Day of Month")
                ax2.set_ylabel("Amount ($)")
                days_in_month = (current_month.replace(month=current_month.month % 12 + 1, day=1) - 
                                current_month).days if current_month.month != 12 else 31
                ax2.set_xticks(range(1, days_in_month + 1))
                ax2.grid(True, which="major", axis="x", linestyle="--", alpha=0.7)

            # Adjust layout to prevent overlap
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("No transactions yet. Add one above!")
else:
    st.warning("Please login to access your finance tracker")