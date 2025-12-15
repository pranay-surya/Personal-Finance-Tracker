import pandas as pd
import matplotlib.pyplot as plt
from database import get_all_transactions


def load_dataframe():
    data = get_all_transactions()
    if not data:
        raise Exception("No transactions found in database.")

    df = pd.DataFrame(
        data,
        columns=["date", "type", "category", "amount"]
    )

    # FIX 1: Convert types explicitly
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    # Remove invalid rows
    df = df.dropna(subset=["date", "amount"])

    return df


# ================= BAR CHART =================
def monthly_expense_bar():
    df = load_dataframe()

    expense_df = df.loc[df["type"] == "expense"].copy()
    if expense_df.empty:
        raise Exception("No expense data available.")

    expense_df["month"] = expense_df["date"].dt.to_period("M")

    monthly_sum = expense_df.groupby("month")["amount"].sum()

    if monthly_sum.empty:
        raise Exception("No numeric expense data to plot.")

    monthly_sum.plot(kind="bar", title="Monthly Expenses")
    plt.xlabel("Month")
    plt.ylabel("Amount")
    plt.tight_layout()
    plt.show()


# ================= PIE CHART =================
def category_pie_chart():
    df = load_dataframe()

    expense_df = df.loc[df["type"] == "expense"].copy()
    if expense_df.empty:
        raise Exception("No expense data available.")

    category_sum = expense_df.groupby("category")["amount"].sum()

    if category_sum.empty:
        raise Exception("No numeric category data to plot.")

    category_sum.plot(
        kind="pie",
        autopct="%1.1f%%",
        title="Expense Distribution by Category"
    )
    plt.ylabel("")
    plt.tight_layout()
    plt.show()


# ================= LINE CHART =================
def expense_trend_line():
    df = load_dataframe()

    expense_df = df.loc[df["type"] == "expense"].copy()
    if expense_df.empty:
        raise Exception("No expense data available.")

    daily_sum = expense_df.groupby("date")["amount"].sum()

    if daily_sum.empty:
        raise Exception("No numeric trend data to plot.")

    daily_sum.plot(kind="line", marker="o", title="Expense Trend Over Time")
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.tight_layout()
    plt.show()
