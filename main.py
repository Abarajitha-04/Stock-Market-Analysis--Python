import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

import sqlite3
import random
from datetime import datetime, timedelta

class StockDatabase:
    def __init__(self, db_name='stock_data.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS companies (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    name TEXT NOT NULL UNIQUE
                                );''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS stocks (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    company_id INTEGER,
                                    date TEXT NOT NULL,
                                    open REAL,
                                    high REAL,
                                    low REAL,
                                    close REAL,
                                    volume INTEGER,
                                    FOREIGN KEY (company_id) REFERENCES companies(id)
                                );''')
            c=self.conn.cursor()
            c.execute("SELECT * FROM companies")
            print(c.fetchall())

    def add_company(self, name):
        with self.conn:
                self.conn.execute("INSERT INTO companies (name) VALUES (?)", (name,))
                
    
    def get_company_id(self, name):
        with self.conn:
            company = self.conn.execute("SELECT id FROM companies WHERE name=?", (name,)).fetchone()
            if company:
                return company[0]
            else:
                self.add_company(name)
                return self.conn.execute("SELECT id FROM companies WHERE name=?", (name,)).fetchone()[0]

    def add_stock_data(self, company_id, date, open_price, high_price, low_price, close_price, volume):
        with self.conn:
        # Check if the company_id exists in the companies table
            c = self.conn.cursor()
            c.execute("SELECT id FROM companies WHERE id=?", (company_id,))
            company = c.fetchone()
        
            if company:
            # Company exists, proceed to add stock data
                self.conn.execute('''INSERT INTO stocks (company_id, date, open, high, low, close, volume)
                                VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                                (company_id, date, open_price, high_price, low_price, close_price, volume))
                messagebox.showinfo("Success", "Stock data added successfully!")
            else:
            # Company does not exist
                messagebox.showerror("Error", "Invalid Company")

    # def generate_random_stock_data(self):
    #     companies = ['Company A', 'Company B', 'Company C']
    #     today = datetime.today()
    #     start_date = today.replace(day=1) - timedelta(days=1)
    #     start_date = start_date.replace(day=1)
    #     end_date = start_date.replace(day=1) + timedelta(days=32)
    #     end_date = end_date.replace(day=1) - timedelta(days=1)
        
    #     for company in companies:
    #         company_id = self.get_company_id(company)
    #         previous_close = random.uniform(50, 200)  # Initial random starting close price
    #         current_date = start_date
    #         volume = random.randint(1000, 100000)
            
    #         while current_date <= end_date:
    #             open_price = previous_close  # Today's close is yesterday's close
    #             close_price = random.uniform(0.9 * open_price, open_price*1.1) # Today's open is today's close
    #             high_price = max(open_price, random.uniform(open_price, 1.1 * open_price))
    #             low_price = min(open_price, random.uniform(0.9 * open_price, open_price))
                
                
    #             self.add_stock_data(company_id, current_date.strftime('%Y-%m-%d'), open_price, high_price, low_price, close_price, volume)
    #             previous_close = close_price  # Update previous close for the next day
    #             current_date += timedelta(days=1)

    def get_stock_data(self, company_name, month):
        company_id = self.get_company_id(company_name)
        return self.conn.execute('''SELECT date, open, close, high, low, volume 
                                    FROM stocks 
                                    WHERE company_id=? AND strftime('%Y-%m', date)=?''', 
                                    (company_id, month)).fetchall()


class StockMarketApp:
    def __init__(self, root):
        self.db = StockDatabase()
        
        self.root = root
        self.root.title("Stock Market Analysis")
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(padx=10, pady=10, fill='both', expand=True)
        
        self.create_add_data_tab()
        self.create_plot_details_tab()
        self.create_add_company_tab()

    def create_add_company_tab(self):
        self.add_company_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.add_company_tab, text="Add Stock")
        
        ttk.Label(self.add_company_tab, text="New Stock Name:").grid(row=0, column=0, padx=5, pady=5)
        self.new_company_entry = ttk.Entry(self.add_company_tab)
        self.new_company_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.add_company_button = ttk.Button(self.add_company_tab, text="Add New Stock", command=self.add_new_company)
        self.add_company_button.grid(row=1, column=0, columnspan=2, pady=10)
        
    def add_new_company(self):
        new_company_name = self.new_company_entry.get().strip()
        conn=sqlite3.connect("stock_data.db")
        c=conn.cursor()
        c.execute("SELECT name FROM companies")
        r=c.fetchall()
        conn.close()
        if new_company_name:
            if new_company_name in r:
                messagebox.showerror("Error", f"Stock '{new_company_name}' already exists.")
            
            else:
                self.db.add_company(new_company_name)
                messagebox.showinfo("Success", f"Added new Stock: {new_company_name}")
            self.new_company_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Please enter a Stock name.")

    def create_add_data_tab(self):  
        self.add_data_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.add_data_tab, text="Add Data")
        
        ttk.Label(self.add_data_tab, text="Stock Name:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(self.add_data_tab)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.add_data_tab, text="Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
        self.date_entry = ttk.Entry(self.add_data_tab)
        self.date_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self.add_data_tab, text="Open Price:").grid(row=2, column=0, padx=5, pady=5)
        self.open_entry = ttk.Entry(self.add_data_tab)
        self.open_entry.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(self.add_data_tab, text="Close Price:").grid(row=3, column=0, padx=5, pady=5)
        self.close_entry = ttk.Entry(self.add_data_tab)
        self.close_entry.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(self.add_data_tab, text="Highest Price:").grid(row=4, column=0, padx=5, pady=5)
        self.high_entry = ttk.Entry(self.add_data_tab)
        self.high_entry.grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(self.add_data_tab, text="Lowest Price:").grid(row=5, column=0, padx=5, pady=5)
        self.low_entry = ttk.Entry(self.add_data_tab)
        self.low_entry.grid(row=5, column=1, padx=5, pady=5)
        
        ttk.Label(self.add_data_tab, text="Total Volume:").grid(row=6, column=0, padx=5, pady=5)
        self.volume_entry = ttk.Entry(self.add_data_tab)
        self.volume_entry.grid(row=6, column=1, padx=5, pady=5)
        
        self.submit_button = ttk.Button(self.add_data_tab, text="Submit", command=self.submit_data)
        self.submit_button.grid(row=7, column=0, columnspan=2, pady=10)

    def create_plot_details_tab(self):
        self.plot_details_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.plot_details_tab, text="Plot/Details")
        
        ttk.Label(self.plot_details_tab, text="Stock Name:").grid(row=0, column=0, padx=5, pady=5)
        self.stock_name_entry = ttk.Entry(self.plot_details_tab)
        self.stock_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.plot_details_tab, text="Month (YYYY-MM):").grid(row=1, column=0, padx=5, pady=5)
        self.month_entry = ttk.Entry(self.plot_details_tab)
        self.month_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.plot_button = ttk.Button(self.plot_details_tab, text="Plot", command=self.plot_data)
        self.plot_button.grid(row=2, column=0, pady=10)
        
        self.details_button = ttk.Button(self.plot_details_tab, text="Show Details", command=self.show_details)
        self.details_button.grid(row=2, column=1, pady=10)

    def submit_data(self):
        name = self.name_entry.get()
        date = self.date_entry.get()
        open_price = (self.open_entry.get())
        close_price =(self.close_entry.get())
        high_price = (self.high_entry.get())
        low_price = (self.low_entry.get())
        volume =(self.volume_entry.get())
        
        if not(name and date and open_price and  close_price and high_price and low_price and volume):
            messagebox.showerror("Error","Enter All The Details!!")
            return
        try:
            self.db.add_stock_data(self.db.get_company_id(name), date, float(open_price), float(high_price), float(low_price), float(close_price),int( volume))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error occurred: {str(e)}")

    def plot_data(self):
        stock_name = self.stock_name_entry.get()
        month = self.month_entry.get()
        
        data = self.db.get_stock_data(stock_name, month)
        if not data:
            messagebox.showwarning("No Data", "No data available for the selected stock and month.")
            return
        
        df = pd.DataFrame(data, columns=['date', 'open', 'close','high','low', 'volume'])
        df['date'] = pd.to_datetime(df['date'])
        
        plt.figure(figsize=(10, 6))
        plt.plot(df['date'], df['open'], label='Open', marker='o')
        
        plt.title(f'Stock Prices for {stock_name} - {month}')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def show_details(self):
        stock_name = self.stock_name_entry.get()
        month = self.month_entry.get()
        
        data = self.db.get_stock_data(stock_name, month)
        if not data:
            messagebox.showwarning("No Data", "No data available for the selected stock and month.")
            return
        
        details_window = tk.Toplevel()
        details_window.title(f"Details for {stock_name} - {month}")
        
        columns = ('date', 'open', 'close', 'high', 'low', 'volume')
        tree = ttk.Treeview(details_window, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col.capitalize())
        
        for row in data:
            tree.insert('', tk.END, values=row)
        
        tree.pack(padx=10, pady=10, fill='both', expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = StockMarketApp(root)
    root.mainloop()
