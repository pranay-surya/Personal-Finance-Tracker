import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime 
from database import add_transaction, get_transactions, delete_transaction 
from analytics import monthly_summary, export_to_csv
from charts import monthly_expense_bar, category_pie_chart, expense_trend_line


# ===================== COMMON UI HELPERS ===================== 
def create_main_header(parent):
    header = tk.Label(
        parent,
        text="EXPENSE TRACKER",
        font=("Helvetica", 32, "bold"),
        bg="#2c3e50",
        fg="white",
        pady=35
    )
    header.pack(fill=tk.X)


def create_page_title(parent, title_text):
    title_box = tk.LabelFrame(
        parent,
        text=title_text,
        font=("Helvetica", 18, "bold"),
        padx=40,
        pady=15
    )
    title_box.pack(pady=30)
    return title_box

def add_back_button(parent, window):
    tk.Button(
        parent,
        text="← Back",
        width=12,
        bg="#7f8c8d",
        fg="white",
        command=window.destroy
    ).pack(anchor="w", pady=10)

# ===================== MAIN APP =====================
class ExpenseTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Expense Tracker")
        self.state("zoomed")
        self.minsize(900, 600)

        # ===== GLOBAL HEADER =====
        create_main_header(self)

        # ===== HOME BOX =====
        box = create_page_title(self, "Expense Operations")

        form_frame = tk.Frame(box)
        form_frame.pack(pady=20)

        # Date
        tk.Label(form_frame, text="Date (YYYY-MM-DD)").grid(row=0, column=0, padx=10, pady=5)
        self.date_entry = tk.Entry(form_frame, width=20)
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=0, column=1)

        # Type
        tk.Label(form_frame, text="Type").grid(row=0, column=2, padx=10)
        self.type_var = tk.StringVar(value="expense")
        ttk.Combobox(
            form_frame,
            textvariable=self.type_var,
            values=["income", "expense"],
            state="readonly",
            width=18
        ).grid(row=0, column=3)

        # Category
        tk.Label(form_frame, text="Category").grid(row=1, column=0, padx=10)
        self.category_entry = tk.Entry(form_frame, width=20)
        self.category_entry.grid(row=1, column=1)

        # Amount
        tk.Label(form_frame, text="Amount (₹)").grid(row=1, column=2, padx=10)
        self.amount_entry = tk.Entry(form_frame, width=20)
        self.amount_entry.grid(row=1, column=3)

        # Description
        tk.Label(form_frame, text="Description").grid(row=2, column=0, padx=10)
        self.desc_entry = tk.Entry(form_frame, width=48)
        self.desc_entry.grid(row=2, column=1, columnspan=3)

        # ===== BUTTONS =====
        btn_frame = tk.Frame(box)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Add Transaction",
                  width=18, bg="green", fg="white",
                  command=self.save_transaction).grid(row=0, column=0, padx=10)

        tk.Button(btn_frame, text="View Transactions",
                  width=18, bg="blue", fg="white",
                  command=self.show_transactions).grid(row=0, column=1, padx=10)

        tk.Button(btn_frame, text="Monthly Summary",
                  width=18, bg="purple", fg="white",
                  command=self.show_monthly_summary).grid(row=0, column=2, padx=10)

        tk.Button(btn_frame, text="Show Charts",
                  width=18, bg="orange", fg="white",
                  command=self.show_charts).grid(row=1, column=0, padx=10, pady=10)

        tk.Button(btn_frame, text="Export CSV",
                  width=18, bg="brown", fg="white",
                  command=self.export_csv).grid(row=1, column=1, padx=10)

    # ===================== SAVE (Updated) =====================
    def save_transaction(self):
        # 1. Input Retrieval
        trans_date = self.date_entry.get().strip()
        trans_type = self.type_var.get()
        category = self.category_entry.get().strip()
        amount_str = self.amount_entry.get().strip()
        description = self.desc_entry.get().strip()
        
        try:
            # 2. Validation
            # Date Validation
            try:
                datetime.strptime(trans_date, "%Y-%m-%d")
            except ValueError:
                 raise ValueError("Invalid Date format. Must be YYYY-MM-DD.")

            # Amount Validation
            if not amount_str:
                raise ValueError("Amount cannot be empty.")
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be a positive number.")

            # Category/Description Validation
            if not category:
                raise ValueError("Category cannot be empty.")
            if not description:
                raise ValueError("Description cannot be empty.")

            # 3. Database Operation
            add_transaction(
                trans_date,
                trans_type,
                category,
                amount,
                description
            )
            
            # 4. Success and Cleanup
            messagebox.showinfo("Success", "Transaction added successfully")
            self.category_entry.delete(0, tk.END)
            self.amount_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)
            
        except ValueError as ve:
            # Catches issues with date format, amount conversion, empty fields
            messagebox.showerror("Validation Error", str(ve))
        except Exception as e:
            # Catches database or other exceptions
            messagebox.showerror("Error", str(e))

    # ===================== VIEW TRANSACTIONS (Updated) =====================
    def show_transactions(self):
        win = tk.Toplevel(self)
        win.title("View Transactions")
        win.state("zoomed")

        create_main_header(win)
        title_box = create_page_title(win, "View Transactions")

        # --- Treeview Setup ---
        columns = ("ID", "Date", "Type", "Category", "Amount", "Description")
        
        # Create a frame for the Treeview and Scrollbar
        tree_frame = tk.Frame(win, padx=20, pady=20)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        yscroll = ttk.Scrollbar(tree_frame, orient="vertical")
        
        tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=yscroll.set
        )
        yscroll.config(command=tree.yview)
        yscroll.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)

        # Column configuration
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)
        
        tree.column("ID", width=50) # Narrow ID column
        tree.column("Description", width=200) # Wider Description column

        # Load Data
        try:
            for row in get_transactions():
                # Use ID as iid for easy reference and store full row in values
                tree.insert("", tk.END, values=row, iid=row[0])
        except Exception as e:
            messagebox.showerror("Error", f"Could not load transactions: {e}")
            return


        # --- Delete Functionality ---
        def delete_selected():
            selected_item = tree.focus()
            if not selected_item:
                messagebox.showwarning("Warning", "Please select a transaction to delete.")
                return
            
            # Get the ID (which is the first value in the row and the iid)
            trans_id = tree.item(selected_item, "values")[0] 
            
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Transaction ID: {trans_id}?"):
                try:
                    delete_transaction(trans_id)
                    tree.delete(selected_item)
                    messagebox.showinfo("Success", "Transaction deleted successfully.")
                except Exception as e:
                    messagebox.showerror("Error", str(e))


        # Delete button placed inside the title box for better layout
        delete_btn_frame = tk.Frame(title_box)
        delete_btn_frame.pack(pady=10)
        
        tk.Button(
            delete_btn_frame, 
            text="Delete Selected Transaction",
            width=30, 
            bg="red", 
            fg="white",
            command=delete_selected
        ).pack(side=tk.LEFT, padx=10)

        # Back button placed inside the title box
        add_back_button(title_box, win) 
        
    # ===================== MONTHLY SUMMARY (No change) =====================
    def show_monthly_summary(self):
        win = tk.Toplevel(self)
        win.title("Monthly Summary")
        win.state("zoomed")

        create_main_header(win)
        create_page_title(win, "Monthly Summary")
        

        select_box = tk.LabelFrame(
            win, text="Select Month & Year",
            font=("Helvetica", 16, "bold"),
            padx=30, pady=20
        )
        select_box.pack(pady=20)

        tk.Label(select_box, text="Month").grid(row=0, column=0, padx=10)
        tk.Label(select_box, text="Year").grid(row=0, column=2, padx=10)

        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        month_var = tk.StringVar(value=months[date.today().month - 1])
        year_var = tk.StringVar(value=str(date.today().year))

        ttk.Combobox(select_box, textvariable=month_var,
                     values=months, state="readonly", width=15).grid(row=0, column=1)

        ttk.Combobox(select_box, textvariable=year_var,
                     values=[str(y) for y in range(2020, date.today().year + 1)],
                     state="readonly", width=10).grid(row=0, column=3)

        result_box = tk.LabelFrame(
            win, text="Summary Details",
            font=("Helvetica", 16, "bold"),
            padx=50, pady=30
        )
        result_box.pack(pady=40)

        income_lbl = tk.Label(result_box, font=("Helvetica", 18))
        expense_lbl = tk.Label(result_box, font=("Helvetica", 18))
        savings_lbl = tk.Label(result_box, font=("Helvetica", 18))

        income_lbl.pack(pady=10)
        expense_lbl.pack(pady=10)
        savings_lbl.pack(pady=10)

        def load_summary():
            m = months.index(month_var.get()) + 1
            y = int(year_var.get())
            result = monthly_summary(y, m)

            if not result:
                income_lbl.config(text="No data for selected month")
                expense_lbl.config(text="")
                savings_lbl.config(text="")
                return

            income_lbl.config(text=f"Total Income   : ₹ {result['income']:.2f}")
            expense_lbl.config(text=f"Total Expense : ₹ {result['expense']:.2f}")
            savings_lbl.config(text=f"Savings       : ₹ {result['savings']:.2f}")

        tk.Button(win, text="Show Summary",
                  bg="purple", fg="white",
                  font=("Helvetica", 14),
                  width=20,
                  command=load_summary).pack(pady=20)

        load_summary()
        
    # ===================== CHARTS (Updated) =====================
    def show_charts(self):
        win = tk.Toplevel(self)
        win.title("Charts")
        win.state("zoomed")

        # Global header (full width)
        create_main_header(win)

        # Page title box (NOT full width)
        page_box = create_page_title(win, "Charts")
        
        # Function to safely call chart functions and handle exceptions
        def plot_chart(chart_func):
            try:
                chart_func()
            except Exception as e:
                # Catching exceptions from charts.py (e.g., "No data available.")
                messagebox.showwarning("Plotting Error", str(e))

        # Buttons INSIDE the box
        tk.Button(
            page_box,
            text="Monthly Expense (Bar)",
            width=30,
            command=lambda: plot_chart(monthly_expense_bar) # Use safe wrapper
        ).pack(pady=10)

        tk.Button(
            page_box,
            text="Category-wise Expense (Pie)",
            width=30,
            command=lambda: plot_chart(category_pie_chart) # Use safe wrapper
        ).pack(pady=10)

        tk.Button(
            page_box,
            text="Expense Trend (Line)",
            width=30,
            command=lambda: plot_chart(expense_trend_line) # Use safe wrapper
        ).pack(pady=10)
        
        # Add back button to chart window
        add_back_button(page_box, win)


    # ===================== EXPORT (No change) =====================
    def export_csv(self):
        if export_to_csv():
            messagebox.showinfo("Success", "expense_data.csv created")
        else:
            messagebox.showwarning("Warning", "No data to export")


# ===================== RUN APP =====================
if __name__ == "__main__":
    ExpenseTrackerApp().mainloop()