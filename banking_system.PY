"""
BANKING MANAGEMENT SYSTEM - PROFESSIONAL DASHBOARD VERSION
Complete Working Code - Fixed Receipt Display
"""

import csv
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ==================== DATA FUNCTIONS ====================

def load_accounts():
    accounts = []
    try:
        if os.path.exists('accounts.csv'):
            with open('accounts.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row['Balance'] = float(row['Balance'])
                    accounts.append(row)
    except:
        pass
    return accounts

def save_accounts(accounts):
    try:
        with open('accounts.csv', 'w', newline='') as f:
            fieldnames = ['Account_Number', 'Name', 'Account_Type', 'Balance', 'Phone', 'Email']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for acc in accounts:
                writer.writerow(acc)
        return True
    except:
        return False

def load_transactions():
    transactions = []
    try:
        if os.path.exists('transactions.csv'):
            with open('transactions.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row['Amount'] = float(row['Amount'])
                    transactions.append(row)
    except:
        pass
    return transactions

def save_transaction(transaction):
    try:
        file_exists = os.path.exists('transactions.csv')
        with open('transactions.csv', 'a', newline='') as f:
            fieldnames = ['Transaction_ID', 'Account_Number', 'Type', 'Amount', 'Date', 'Description']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(transaction)
        return True
    except:
        return False

def generate_transaction_id():
    return f"TXN{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

# ==================== ACCOUNT TYPES ====================

ACCOUNT_TYPES = ['Savings', 'Checking', 'Student', 'Fixed Deposit']

# ==================== BANKING OPERATIONS ====================

def create_account(accounts, data):
    try:
        acc_num = data['account_number']
        name = data['name'].title()
        acc_type = data['account_type']
        balance = data['initial_balance']
        phone = data.get('phone', 'N/A')
        email = data.get('email', 'N/A')
        
        if not acc_num or not name:
            return accounts, "Error: Account number and name required"
        if balance < 0:
            return accounts, "Error: Balance cannot be negative"
        
        for acc in accounts:
            if acc['Account_Number'] == acc_num:
                return accounts, "Error: Account number already exists"
        
        new_account = {
            'Account_Number': acc_num,
            'Name': name,
            'Account_Type': acc_type,
            'Balance': balance,
            'Phone': phone,
            'Email': email
        }
        accounts.append(new_account)
        save_accounts(accounts)
        
        if balance > 0:
            transaction = {
                'Transaction_ID': generate_transaction_id(),
                'Account_Number': acc_num,
                'Type': 'DEPOSIT',
                'Amount': balance,
                'Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Description': f'Initial deposit'
            }
            save_transaction(transaction)
        
        return accounts, f"Success: Account {acc_num} created"
    except Exception as e:
        return accounts, f"Error: {str(e)}"

def deposit(accounts, acc_num, amount):
    try:
        if amount <= 0:
            return accounts, "Error: Amount must be positive", None
        
        for acc in accounts:
            if acc['Account_Number'] == acc_num:
                old_balance = acc['Balance']
                acc['Balance'] += amount
                save_accounts(accounts)
                
                transaction = {
                    'Transaction_ID': generate_transaction_id(),
                    'Account_Number': acc_num,
                    'Type': 'DEPOSIT',
                    'Amount': amount,
                    'Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Description': 'Deposit'
                }
                save_transaction(transaction)
                return accounts, f"Success: Deposited ${amount:.2f}", acc['Balance']
        
        return accounts, f"Error: Account {acc_num} not found", None
    except Exception as e:
        return accounts, f"Error: {str(e)}", None

def withdraw(accounts, acc_num, amount):
    try:
        if amount <= 0:
            return accounts, "Error: Amount must be positive", None
        
        for acc in accounts:
            if acc['Account_Number'] == acc_num:
                if acc['Balance'] >= amount:
                    acc['Balance'] -= amount
                    save_accounts(accounts)
                    
                    transaction = {
                        'Transaction_ID': generate_transaction_id(),
                        'Account_Number': acc_num,
                        'Type': 'WITHDRAWAL',
                        'Amount': amount,
                        'Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'Description': 'Withdrawal'
                    }
                    save_transaction(transaction)
                    return accounts, f"Success: Withdrew ${amount:.2f}", acc['Balance']
                else:
                    return accounts, f"Error: Insufficient funds", None
        
        return accounts, f"Error: Account {acc_num} not found", None
    except Exception as e:
        return accounts, f"Error: {str(e)}", None

def transfer(accounts, from_acc, to_acc, amount):
    try:
        if amount <= 0:
            return accounts, "Error: Amount must be positive"
        if from_acc == to_acc:
            return accounts, "Error: Cannot transfer to same account"
        
        source = None
        target = None
        
        for acc in accounts:
            if acc['Account_Number'] == from_acc:
                source = acc
            if acc['Account_Number'] == to_acc:
                target = acc
        
        if not source:
            return accounts, f"Error: Source account {from_acc} not found"
        if not target:
            return accounts, f"Error: Target account {to_acc} not found"
        
        if source['Balance'] >= amount:
            source['Balance'] -= amount
            target['Balance'] += amount
            save_accounts(accounts)
            
            transaction1 = {
                'Transaction_ID': generate_transaction_id(),
                'Account_Number': from_acc,
                'Type': 'TRANSFER_OUT',
                'Amount': amount,
                'Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Description': f'Transfer to {to_acc}'
            }
            save_transaction(transaction1)
            
            transaction2 = {
                'Transaction_ID': generate_transaction_id(),
                'Account_Number': to_acc,
                'Type': 'TRANSFER_IN',
                'Amount': amount,
                'Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Description': f'Transfer from {from_acc}'
            }
            save_transaction(transaction2)
            
            return accounts, f"Success: Transferred ${amount:.2f}"
        else:
            return accounts, f"Error: Insufficient funds"
    except Exception as e:
        return accounts, f"Error: {str(e)}"

def view_account_details(accounts, acc_num):
    try:
        account = None
        for acc in accounts:
            if acc['Account_Number'] == acc_num:
                account = acc
                break
        
        if not account:
            return f"Error: Account {acc_num} not found"
        
        transactions = load_transactions()
        acc_trans = [t for t in transactions if t['Account_Number'] == acc_num]
        
        result = f"""
{'='*50}
ACCOUNT DETAILS
{'='*50}
Account Number: {account['Account_Number']}
Account Holder: {account['Name']}
Account Type: {account.get('Account_Type', 'Savings')}
Balance: ${account['Balance']:,.2f}
Phone: {account.get('Phone', 'N/A')}
Email: {account.get('Email', 'N/A')}

TRANSACTION HISTORY
{'='*50}
"""
        
        if acc_trans:
            for t in acc_trans[-10:]:
                result += f"{t['Date'][:10]} - {t['Type']}: ${t['Amount']:,.2f}\n"
        else:
            result += "No transactions found\n"
        
        result += f"{'='*50}"
        return result
    except Exception as e:
        return f"Error: {str(e)}"

def get_stats(accounts):
    total = sum(a['Balance'] for a in accounts)
    return {
        'total_balance': total,
        'total_accounts': len(accounts)
    }

# ==================== PRINT RECEIPT FUNCTION ====================

def print_receipt(transaction_type, account, amount, new_balance, transaction_id):
    """Generate and display a printable receipt"""
    receipt_window = tk.Toplevel()
    receipt_window.title("Transaction Receipt")
    receipt_window.geometry("500x600")
    receipt_window.configure(bg='white')
    receipt_window.transient()
    receipt_window.grab_set()
    
    # Center the window
    receipt_window.update_idletasks()
    x = (receipt_window.winfo_screenwidth() // 2) - (500 // 2)
    y = (receipt_window.winfo_screenheight() // 2) - (600 // 2)
    receipt_window.geometry(f'500x600+{x}+{y}')
    
    # Create receipt content
    receipt_text = f"""
╔══════════════════════════════════════════════════════════════╗
║                      BANKING RECEIPT                         ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}        ║
║  Receipt #: {transaction_id[:20]}                           ║
║                                                              ║
║  Transaction Type: {transaction_type}                        ║
║                                                              ║
║  Account Number: {account['Account_Number']}                 ║
║  Account Holder: {account['Name']}                           ║
║  Account Type: {account.get('Account_Type', 'Savings')}      ║
║                                                              ║
║  Amount: ${amount:,.2f}                                      ║
║                                                              ║
║  New Balance: ${new_balance:,.2f}                            ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║           Thank you for banking with us!                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    
    # Create text widget with receipt
    text_widget = tk.Text(receipt_window, wrap=tk.WORD, font=('Courier', 11), 
                          bg='white', fg='black', padx=20, pady=20, height=28, width=55)
    text_widget.pack(fill='both', expand=True)
    text_widget.insert('1.0', receipt_text)
    text_widget.config(state='disabled')
    
    # Buttons frame
    button_frame = tk.Frame(receipt_window, bg='white')
    button_frame.pack(fill='x', pady=10)
    
    def save_receipt():
        filename = f"receipt_{transaction_id[:10]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write(receipt_text)
        messagebox.showinfo("Saved", f"Receipt saved as {filename}")
    
    def copy_to_clipboard():
        receipt_window.clipboard_clear()
        receipt_window.clipboard_append(receipt_text)
        messagebox.showinfo("Copied", "Receipt copied to clipboard! You can paste it anywhere.")
    
    tk.Button(button_frame, text="💾 Save Receipt", command=save_receipt,
              bg='#10b981', fg='white', font=('Arial', 10, 'bold'),
              padx=15, pady=5, relief='flat', cursor='hand2').pack(side='left', padx=10)
    
    tk.Button(button_frame, text="📋 Copy to Clipboard", command=copy_to_clipboard,
              bg='#3b82f6', fg='white', font=('Arial', 10, 'bold'),
              padx=15, pady=5, relief='flat', cursor='hand2').pack(side='left', padx=10)
    
    tk.Button(button_frame, text="✖ Close", command=receipt_window.destroy,
              bg='#ef4444', fg='white', font=('Arial', 10, 'bold'),
              padx=15, pady=5, relief='flat', cursor='hand2').pack(side='right', padx=10)

# ==================== MAIN APPLICATION ====================

class BankingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🏦 Banking Management System")
        self.root.geometry("1300x750")
        self.root.configure(bg='#f0f2f5')
        
        self.accounts = load_accounts()
        self.create_ui()
    
    def create_ui(self):
        # Header
        header = tk.Frame(self.root, bg='#1a1a2e', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # Title in header
        title_frame = tk.Frame(header, bg='#1a1a2e')
        title_frame.pack(side='left', padx=30, pady=20)
        
        tk.Label(title_frame, text="🏦", font=('Arial', 32), bg='#1a1a2e', fg='#e94560').pack(side='left')
        tk.Label(title_frame, text="BANKING SYSTEM", font=('Arial', 20, 'bold'), 
                bg='#1a1a2e', fg='white').pack(side='left', padx=10)
        
        # Stats in header
        stats = get_stats(self.accounts)
        stats_frame = tk.Frame(header, bg='#1a1a2e')
        stats_frame.pack(side='right', padx=30, pady=15)
        
        tk.Label(stats_frame, text=f"${stats['total_balance']:,.0f}", 
                font=('Arial', 20, 'bold'), bg='#1a1a2e', fg='#e94560').pack(side='left', padx=20)
        tk.Label(stats_frame, text="Total Balance", font=('Arial', 10), bg='#1a1a2e', fg='#aaa').pack(side='left')
        
        # Main content area
        main = tk.Frame(self.root, bg='#f0f2f5')
        main.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left sidebar
        sidebar = tk.Frame(main, bg='white', width=280)
        sidebar.pack(side='left', fill='y', padx=(0, 20))
        sidebar.pack_propagate(False)
        
        tk.Label(sidebar, text="Quick Actions", font=('Arial', 16, 'bold'), 
                bg='white', fg='#1a1a2e').pack(pady=(20, 15))
        
        # Buttons
        buttons = [
            ("➕ Create Account", "#10b981", self.create_account_dialog),
            ("💰 Deposit", "#3b82f6", self.deposit_dialog),
            ("💸 Withdraw", "#ef4444", self.withdraw_dialog),
            ("🔄 Transfer", "#8b5cf6", self.transfer_dialog),
            ("📊 View Account", "#f59e0b", self.view_account_dialog),
            ("🔄 Refresh", "#6b7280", self.refresh_data)
        ]
        
        for text, color, cmd in buttons:
            btn = tk.Button(sidebar, text=text, command=cmd,
                           font=('Arial', 11), bg=color, fg='white',
                           bd=0, padx=20, pady=12, cursor='hand2',
                           activebackground=color, activeforeground='white')
            btn.pack(fill='x', padx=15, pady=5)
        
        # Right content area
        self.content = tk.Frame(main, bg='#f0f2f5')
        self.content.pack(side='left', fill='both', expand=True)
        
        # Show dashboard
        self.show_dashboard()
        
        # Status bar
        self.status = tk.Label(self.root, text="✅ System Ready", bd=1, relief=tk.SUNKEN, 
                               anchor=tk.W, bg='#f0f2f5', font=('Arial', 9))
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
    
    def show_dashboard(self):
        self.clear_content()
        
        # Welcome
        welcome = tk.Frame(self.content, bg='#f0f2f5')
        welcome.pack(fill='x', pady=(0, 20))
        tk.Label(welcome, text="Dashboard", font=('Arial', 24, 'bold'),
                bg='#f0f2f5', fg='#1a1a2e').pack(side='left')
        tk.Label(welcome, text=datetime.now().strftime("%A, %B %d, %Y"),
                font=('Arial', 11), bg='#f0f2f5', fg='#666').pack(side='right')
        
        # Stats cards
        stats = get_stats(self.accounts)
        cards_frame = tk.Frame(self.content, bg='#f0f2f5')
        cards_frame.pack(fill='x', pady=10)
        
        cards = [
            ("💰 Total Balance", f"${stats['total_balance']:,.0f}", "#e94560"),
            ("👥 Total Accounts", str(stats['total_accounts']), "#3b82f6"),
            ("📈 Today's Transactions", "0", "#10b981"),
            ("⭐ Active Accounts", str(stats['total_accounts']), "#f59e0b")
        ]
        
        for i, (title, value, color) in enumerate(cards):
            card = tk.Frame(cards_frame, bg='white', relief='ridge', bd=0, 
                           highlightbackground='#e5e7eb', highlightthickness=1)
            card.grid(row=0, column=i, padx=10, sticky='nsew')
            cards_frame.columnconfigure(i, weight=1)
            
            tk.Label(card, text=title, font=('Arial', 11), bg='white', fg='#666').pack(anchor='w', padx=20, pady=(15, 5))
            tk.Label(card, text=value, font=('Arial', 28, 'bold'), bg='white', fg=color).pack(anchor='w', padx=20, pady=(0, 15))
        
        # Recent transactions
        tk.Label(self.content, text="Recent Transactions", font=('Arial', 16, 'bold'),
                bg='#f0f2f5', fg='#1a1a2e').pack(anchor='w', pady=(30, 15))
        
        self.create_transactions_table()
        
        # Charts
        self.create_charts()
    
    def create_transactions_table(self):
        table_frame = tk.Frame(self.content, bg='white', relief='ridge', bd=0, 
                               highlightbackground='#e5e7eb', highlightthickness=1)
        table_frame.pack(fill='x', pady=10)
        
        headers = ['ID', 'Account', 'Type', 'Amount', 'Date']
        for i, header in enumerate(headers):
            tk.Label(table_frame, text=header, font=('Arial', 10, 'bold'),
                    bg='#f8f9fa', fg='#1a1a2e', padx=15, pady=10).grid(row=0, column=i, sticky='nsew')
            table_frame.columnconfigure(i, weight=1)
        
        transactions = load_transactions()
        for row, trans in enumerate(transactions[-6:], 1):
            color = '#fef2f2' if trans['Type'] == 'WITHDRAWAL' else '#f0fdf4'
            
            tk.Label(table_frame, text=trans['Transaction_ID'][:10], font=('Arial', 9),
                    bg=color, padx=15, pady=8).grid(row=row, column=0, sticky='nsew')
            tk.Label(table_frame, text=trans['Account_Number'], font=('Arial', 9),
                    bg=color, padx=15, pady=8).grid(row=row, column=1, sticky='nsew')
            
            type_color = '#10b981' if trans['Type'] in ['DEPOSIT', 'TRANSFER_IN'] else '#ef4444'
            tk.Label(table_frame, text=trans['Type'], font=('Arial', 9),
                    bg=color, fg=type_color, padx=15, pady=8).grid(row=row, column=2, sticky='nsew')
            
            amount_text = f"+${trans['Amount']:,.0f}" if trans['Type'] in ['DEPOSIT', 'TRANSFER_IN'] else f"-${trans['Amount']:,.0f}"
            tk.Label(table_frame, text=amount_text, font=('Arial', 9),
                    bg=color, fg=type_color, padx=15, pady=8).grid(row=row, column=3, sticky='nsew')
            tk.Label(table_frame, text=trans['Date'][:10], font=('Arial', 9),
                    bg=color, padx=15, pady=8).grid(row=row, column=4, sticky='nsew')
    
    def create_charts(self):
        chart_frame = tk.Frame(self.content, bg='#f0f2f5')
        chart_frame.pack(fill='x', pady=20)
        
        transactions = load_transactions()
        deposits = sum(t['Amount'] for t in transactions if t['Type'] in ['DEPOSIT', 'TRANSFER_IN'])
        withdrawals = sum(t['Amount'] for t in transactions if t['Type'] in ['WITHDRAWAL', 'TRANSFER_OUT'])
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        # Bar chart
        ax1.bar(['Deposits', 'Withdrawals'], [deposits, withdrawals], color=['#10b981', '#ef4444'])
        ax1.set_title('Deposits vs Withdrawals', fontweight='bold')
        ax1.set_ylabel('Amount ($)')
        
        # Pie chart
        type_balances = {}
        for a in self.accounts:
            t = a.get('Account_Type', 'Savings')
            type_balances[t] = type_balances.get(t, 0) + a['Balance']
        
        if type_balances:
            colors = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6']
            ax2.pie(type_balances.values(), labels=type_balances.keys(), autopct='%1.1f%%', colors=colors)
            ax2.set_title('Balance by Account Type', fontweight='bold')
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
    
    def create_account_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Account")
        dialog.geometry("450x500")
        dialog.configure(bg='white')
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Create New Account", font=('Arial', 18, 'bold'),
                bg='white', fg='#1a1a2e').pack(pady=20)
        
        fields = [
            ("Account Number:", "acc_num"),
            ("Account Holder:", "acc_name"),
            ("Account Type:", "acc_type"),
            ("Initial Balance:", "acc_balance"),
            ("Phone:", "acc_phone"),
            ("Email:", "acc_email")
        ]
        
        entries = {}
        for label, key in fields:
            frame = tk.Frame(dialog, bg='white')
            frame.pack(fill='x', padx=30, pady=5)
            tk.Label(frame, text=label, font=('Arial', 10), bg='white', width=15, anchor='w').pack(side='left')
            
            if key == 'acc_type':
                entries[key] = ttk.Combobox(frame, values=ACCOUNT_TYPES, width=25)
                entries[key].set('Savings')
            else:
                entries[key] = tk.Entry(frame, font=('Arial', 10), width=27, bg='#f8f9fa', relief='flat', bd=1)
            entries[key].pack(side='left', padx=10)
        
        def create():
            try:
                balance = float(entries['acc_balance'].get()) if entries['acc_balance'].get() else 0
            except:
                messagebox.showerror("Error", "Invalid balance")
                return
            
            data = {
                'account_number': entries['acc_num'].get().strip(),
                'name': entries['acc_name'].get().strip(),
                'account_type': entries['acc_type'].get(),
                'initial_balance': balance,
                'phone': entries['acc_phone'].get().strip(),
                'email': entries['acc_email'].get().strip()
            }
            
            self.accounts, msg = create_account(self.accounts, data)
            
            if "Success" in msg:
                messagebox.showinfo("Success", msg)
                self.refresh_data()
                dialog.destroy()
            else:
                messagebox.showerror("Error", msg)
        
        tk.Button(dialog, text="Create Account", command=create,
                 bg='#10b981', fg='white', font=('Arial', 11, 'bold'),
                 padx=30, pady=10, relief='flat', cursor='hand2').pack(pady=20)
    
    def deposit_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Deposit Money")
        dialog.geometry("400x350")
        dialog.configure(bg='white')
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Deposit Money", font=('Arial', 18, 'bold'),
                bg='white', fg='#1a1a2e').pack(pady=20)
        
        frame = tk.Frame(dialog, bg='white')
        frame.pack(pady=20)
        
        tk.Label(frame, text="Account Number:", font=('Arial', 11), bg='white').grid(row=0, column=0, pady=10, padx=10)
        acc_entry = tk.Entry(frame, font=('Arial', 11), width=20)
        acc_entry.grid(row=0, column=1, pady=10)
        
        tk.Label(frame, text="Amount ($):", font=('Arial', 11), bg='white').grid(row=1, column=0, pady=10, padx=10)
        amt_entry = tk.Entry(frame, font=('Arial', 11), width=20)
        amt_entry.grid(row=1, column=1, pady=10)
        
        def do_deposit():
            try:
                amount = float(amt_entry.get())
            except:
                messagebox.showerror("Error", "Invalid amount")
                return
            
            acc_num = acc_entry.get().strip()
            account = None
            for acc in self.accounts:
                if acc['Account_Number'] == acc_num:
                    account = acc
                    break
            
            if not account:
                messagebox.showerror("Error", f"Account {acc_num} not found")
                return
            
            self.accounts, msg, new_balance = deposit(self.accounts, acc_num, amount)
            
            if "Success" in msg:
                messagebox.showinfo("Success", msg)
                # Show receipt
                print_receipt("DEPOSIT", account, amount, new_balance, generate_transaction_id())
                self.refresh_data()
                dialog.destroy()
            else:
                messagebox.showerror("Error", msg)
        
        tk.Button(dialog, text="Deposit", command=do_deposit,
                 bg='#10b981', fg='white', font=('Arial', 11, 'bold'),
                 padx=30, pady=8, relief='flat', cursor='hand2').pack(pady=20)
    
    def withdraw_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Withdraw Money")
        dialog.geometry("400x350")
        dialog.configure(bg='white')
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Withdraw Money", font=('Arial', 18, 'bold'),
                bg='white', fg='#1a1a2e').pack(pady=20)
        
        frame = tk.Frame(dialog, bg='white')
        frame.pack(pady=20)
        
        tk.Label(frame, text="Account Number:", font=('Arial', 11), bg='white').grid(row=0, column=0, pady=10, padx=10)
        acc_entry = tk.Entry(frame, font=('Arial', 11), width=20)
        acc_entry.grid(row=0, column=1, pady=10)
        
        tk.Label(frame, text="Amount ($):", font=('Arial', 11), bg='white').grid(row=1, column=0, pady=10, padx=10)
        amt_entry = tk.Entry(frame, font=('Arial', 11), width=20)
        amt_entry.grid(row=1, column=1, pady=10)
        
        def do_withdraw():
            try:
                amount = float(amt_entry.get())
            except:
                messagebox.showerror("Error", "Invalid amount")
                return
            
            acc_num = acc_entry.get().strip()
            account = None
            for acc in self.accounts:
                if acc['Account_Number'] == acc_num:
                    account = acc
                    break
            
            if not account:
                messagebox.showerror("Error", f"Account {acc_num} not found")
                return
            
            self.accounts, msg, new_balance = withdraw(self.accounts, acc_num, amount)
            
            if "Success" in msg:
                messagebox.showinfo("Success", msg)
                # Show receipt
                print_receipt("WITHDRAWAL", account, amount, new_balance, generate_transaction_id())
                self.refresh_data()
                dialog.destroy()
            else:
                messagebox.showerror("Error", msg)
        
        tk.Button(dialog, text="Withdraw", command=do_withdraw,
                 bg='#ef4444', fg='white', font=('Arial', 11, 'bold'),
                 padx=30, pady=8, relief='flat', cursor='hand2').pack(pady=20)
    
    def transfer_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Transfer Money")
        dialog.geometry("450x400")
        dialog.configure(bg='white')
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Transfer Money", font=('Arial', 18, 'bold'),
                bg='white', fg='#1a1a2e').pack(pady=20)
        
        frame = tk.Frame(dialog, bg='white')
        frame.pack(pady=20)
        
        tk.Label(frame, text="From Account:", font=('Arial', 11), bg='white').grid(row=0, column=0, pady=10, padx=10)
        from_entry = tk.Entry(frame, font=('Arial', 11), width=20)
        from_entry.grid(row=0, column=1, pady=10)
        
        tk.Label(frame, text="To Account:", font=('Arial', 11), bg='white').grid(row=1, column=0, pady=10, padx=10)
        to_entry = tk.Entry(frame, font=('Arial', 11), width=20)
        to_entry.grid(row=1, column=1, pady=10)
        
        tk.Label(frame, text="Amount ($):", font=('Arial', 11), bg='white').grid(row=2, column=0, pady=10, padx=10)
        amt_entry = tk.Entry(frame, font=('Arial', 11), width=20)
        amt_entry.grid(row=2, column=1, pady=10)
        
        def do_transfer():
            try:
                amount = float(amt_entry.get())
            except:
                messagebox.showerror("Error", "Invalid amount")
                return
            
            from_acc = from_entry.get().strip()
            account = None
            for acc in self.accounts:
                if acc['Account_Number'] == from_acc:
                    account = acc
                    break
            
            if not account:
                messagebox.showerror("Error", f"Source account {from_acc} not found")
                return
            
            self.accounts, msg = transfer(self.accounts, from_acc, to_entry.get().strip(), amount)
            
            if "Success" in msg:
                messagebox.showinfo("Success", msg)
                # Get updated balance
                updated_balance = 0
                for acc in self.accounts:
                    if acc['Account_Number'] == from_acc:
                        updated_balance = acc['Balance']
                        break
                # Show receipt
                print_receipt("TRANSFER", account, amount, updated_balance, generate_transaction_id())
                self.refresh_data()
                dialog.destroy()
            else:
                messagebox.showerror("Error", msg)
        
        tk.Button(dialog, text="Transfer", command=do_transfer,
                 bg='#8b5cf6', fg='white', font=('Arial', 11, 'bold'),
                 padx=30, pady=8, relief='flat', cursor='hand2').pack(pady=20)
    
    def view_account_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("View Account")
        dialog.geometry("400x300")
        dialog.configure(bg='white')
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="View Account Details", font=('Arial', 18, 'bold'),
                bg='white', fg='#1a1a2e').pack(pady=20)
        
        frame = tk.Frame(dialog, bg='white')
        frame.pack(pady=20)
        
        tk.Label(frame, text="Account Number:", font=('Arial', 11), bg='white').pack(pady=10)
        acc_entry = tk.Entry(frame, font=('Arial', 11), width=20)
        acc_entry.pack(pady=5)
        
        def view():
            acc_num = acc_entry.get().strip()
            if not acc_num:
                messagebox.showerror("Error", "Enter account number")
                return
            
            details = view_account_details(self.accounts, acc_num)
            
            if "Error" in details:
                messagebox.showerror("Error", details)
            else:
                result = tk.Toplevel(dialog)
                result.title(f"Account {acc_num}")
                result.geometry("600x500")
                result.configure(bg='white')
                
                text = tk.Text(result, wrap=tk.WORD, font=('Consolas', 10), bg='white')
                text.pack(fill='both', expand=True, padx=10, pady=10)
                text.insert('1.0', details)
                text.config(state='disabled')
        
        tk.Button(dialog, text="View Details", command=view,
                 bg='#3b82f6', fg='white', font=('Arial', 11, 'bold'),
                 padx=30, pady=8, relief='flat', cursor='hand2').pack(pady=20)
    
    def refresh_data(self):
        self.accounts = load_accounts()
        self.show_dashboard()
        self.status.config(text=f"✅ Refreshed - {datetime.now().strftime('%H:%M:%S')}")
    
    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

# ==================== MAIN ====================

def main():
    root = tk.Tk()
    app = BankingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()