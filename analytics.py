import pandas as pd
from database import get_all_transactions


def monthly_summary(year, month):
    data = get_all_transactions()

    if not data:
        return None

    df = pd.DataFrame(
        data,
        columns=["date", "type", "category", "amount"]
    )

    # Convert date column to datetime
    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")


    # Filter by selected month and year
    df = df[(df["date"].dt.year == year) & (df["date"].dt.month == month)]

    if df.empty:
        return None

    total_income = df[df["type"] == "income"]["amount"].sum()
    total_expense = df[df["type"] == "expense"]["amount"].sum()
    savings = total_income - total_expense

    return {
        "income": float(total_income),
        "expense": float(total_expense),
        "savings": float(savings)
    }



def export_to_csv(filename="expense_data.csv"):
    data = get_all_transactions()

    if not data:
        return False

    df = pd.DataFrame(
        data,
        columns=["date", "type", "category", "amount"]
    )

    df.to_csv(filename, index=False)
    return True
