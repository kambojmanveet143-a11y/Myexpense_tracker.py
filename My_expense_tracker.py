import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="💰 Smart Expense Tracker",
    page_icon="💰",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
    .main {
        background-color: #f7f9fc;
    }

    .title {
        font-size: 42px;
        font-weight: 800;
        color: #1f2937;
        margin-bottom: 5px;
    }

    .subtitle {
        color: #6b7280;
        font-size: 17px;
        margin-bottom: 25px;
    }

    .card {
        padding: 20px;
        border-radius: 18px;
        background: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        text-align: center;
    }

    .card-title {
        color: #6b7280;
        font-size: 15px;
    }

    .card-value {
        font-size: 28px;
        font-weight: bold;
        margin-top: 8px;
    }

    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ---------------- SESSION STATE ----------------
if "transactions" not in st.session_state:
    st.session_state.transactions = pd.DataFrame(
        columns=["Date", "Type", "Category", "Description", "Amount"]
    )


# ---------------- SIDEBAR ----------------
st.sidebar.title("💰 Expense Tracker")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "➕ Add Transaction",
        "📊 Analytics",
        "📜 Transactions"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "Track your income and expenses easily.\n\n"
    "💡 Stay within your budget!"
)


# ---------------- TITLE ----------------
st.markdown(
    '<div class="title">💰 Smart Expense Tracker</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Manage your money. Track your spending. Build better habits.</div>',
    unsafe_allow_html=True
)


# =========================================================
# DASHBOARD
# =========================================================
if menu == "🏠 Dashboard":

    df = st.session_state.transactions

    if len(df) == 0:
        income = 0
        expense = 0
    else:
        income = df.loc[df["Type"] == "Income", "Amount"].sum()
        expense = df.loc[df["Type"] == "Expense", "Amount"].sum()

    balance = income - expense

    # -------- SUMMARY CARDS --------
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="card">
                <div class="card-title">💵 Total Income</div>
                <div class="card-value">₹{income:,.2f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="card">
                <div class="card-title">💸 Total Expense</div>
                <div class="card-value">₹{expense:,.2f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="card">
                <div class="card-title">💰 Current Balance</div>
                <div class="card-value">₹{balance:,.2f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("## 📈 Financial Overview")

    if len(df) == 0:
        st.info("No transactions yet. Add your first transaction from the sidebar.")

    else:
        # -------- PIE CHART --------
        col1, col2 = st.columns(2)

        with col1:
            type_data = df.groupby("Type")["Amount"].sum().reset_index()

            fig = px.pie(
                type_data,
                names="Type",
                values="Amount",
                hole=0.55,
                title="Income vs Expense"
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            expense_df = df[df["Type"] == "Expense"]

            if len(expense_df) > 0:
                category_data = (
                    expense_df.groupby("Category")["Amount"]
                    .sum()
                    .reset_index()
                )

                fig2 = px.bar(
                    category_data,
                    x="Category",
                    y="Amount",
                    title="Expenses by Category",
                    text_auto=True
                )

                st.plotly_chart(fig2, use_container_width=True)

        # -------- RECENT TRANSACTIONS --------
        st.markdown("## 🕒 Recent Transactions")

        recent = df.sort_values(
            by="Date",
            ascending=False
        ).head(5)

        st.dataframe(
            recent,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# ADD TRANSACTION
# =========================================================
elif menu == "➕ Add Transaction":

    st.header("➕ Add New Transaction")

    with st.form("transaction_form"):

        col1, col2 = st.columns(2)

        with col1:
            transaction_date = st.date_input(
                "📅 Date",
                value=date.today()
            )

            transaction_type = st.selectbox(
                "💳 Transaction Type",
                ["Expense", "Income"]
            )

            category = st.selectbox(
                "📂 Category",
                [
                    "Food",
                    "Shopping",
                    "Travel",
                    "Bills",
                    "Education",
                    "Entertainment",
                    "Health",
                    "Salary",
                    "Business",
                    "Other"
                ]
            )

        with col2:
            amount = st.number_input(
                "💰 Amount (₹)",
                min_value=0.0,
                step=100.0
            )

            description = st.text_input(
                "📝 Description",
                placeholder="e.g. College fees, lunch, salary..."
            )

        submitted = st.form_submit_button(
            "➕ Add Transaction",
            use_container_width=True
        )

        if submitted:

            if amount <= 0:
                st.error("Please enter an amount greater than ₹0.")

            else:
                new_transaction = pd.DataFrame(
                    [{
                        "Date": transaction_date,
                        "Type": transaction_type,
                        "Category": category,
                        "Description": description,
                        "Amount": amount
                    }]
                )

                st.session_state.transactions = pd.concat(
                    [
                        st.session_state.transactions,
                        new_transaction
                    ],
                    ignore_index=True
                )

                st.success("✅ Transaction added successfully!")
                st.balloons()


# =========================================================
# ANALYTICS
# =========================================================
elif menu == "📊 Analytics":

    st.header("📊 Expense Analytics")

    df = st.session_state.transactions

    if len(df) == 0:
        st.warning("No data available for analytics.")

    else:

        expense_df = df[df["Type"] == "Expense"].copy()

        if len(expense_df) > 0:

            # Category Analysis
            category_data = (
                expense_df.groupby("Category")["Amount"]
                .sum()
                .reset_index()
                .sort_values("Amount", ascending=False)
            )

            st.subheader("📂 Spending by Category")

            fig = px.pie(
                category_data,
                names="Category",
                values="Amount",
                hole=0.4
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            # Bar Chart
            st.subheader("📊 Category Comparison")

            fig2 = px.bar(
                category_data,
                x="Category",
                y="Amount",
                text_auto=True
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

            # Daily expenses
            st.subheader("📅 Daily Expenses")

            daily = (
                expense_df.groupby("Date")["Amount"]
                .sum()
                .reset_index()
            )

            fig3 = px.line(
                daily,
                x="Date",
                y="Amount",
                markers=True,
                title="Daily Spending"
            )

            st.plotly_chart(
                fig3,
                use_container_width=True
            )

        else:
            st.info("No expenses available for analysis.")


# =========================================================
# TRANSACTIONS
# =========================================================
elif menu == "📜 Transactions":

    st.header("📜 All Transactions")

    df = st.session_state.transactions

    if len(df) == 0:
        st.info("No transactions found.")

    else:

        # -------- FILTERS --------
        col1, col2 = st.columns(2)

        with col1:
            filter_type = st.selectbox(
                "Filter by Type",
                ["All", "Income", "Expense"]
            )

        with col2:
            categories = ["All"] + sorted(
                df["Category"].unique().tolist()
            )

            filter_category = st.selectbox(
                "Filter by Category",
                categories
            )

        filtered_df = df.copy()

        if filter_type != "All":
            filtered_df = filtered_df[
                filtered_df["Type"] == filter_type
            ]

        if filter_category != "All":
            filtered_df = filtered_df[
                filtered_df["Category"] == filter_category
            ]

        st.dataframe(
            filtered_df.sort_values(
                "Date",
                ascending=False
            ),
            use_container_width=True,
            hide_index=True
        )

        # -------- DOWNLOAD --------
        csv = filtered_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Download Transactions CSV",
            data=csv,
            file_name="expense_tracker.csv",
            mime="text/csv",
            use_container_width=True
        )

        # -------- DELETE ALL --------
        st.markdown("---")

        if st.button(
            "🗑️ Delete All Transactions",
            use_container_width=True
        ):

            st.session_state.transactions = pd.DataFrame(
                columns=[
                    "Date",
                    "Type",
                    "Category",
                    "Description",
                    "Amount"
                ]
            )

            st.success("All transactions deleted.")
            st.rerun()
