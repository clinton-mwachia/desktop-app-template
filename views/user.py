import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from models.user import UserModel
from bson.objectid import ObjectId

class UserView:
    def __init__(self, root):
        self.root = root
        self.user_model = UserModel()
        self.page_size = 10
        self.current_page = 1

        self.users_frame = tk.Frame(root)
        self.users_frame.pack(fill=tk.BOTH, expand=True)

        self.setup_users_frame()
        self.load_users()  # Load users after setting up the UI

    def setup_users_frame(self):
        self.add_button = tk.Button(self.users_frame, text="Add User", command=self.add_user)
        self.add_button.pack(pady=10)

        self.tree_frame = tk.Frame(self.users_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(self.tree_frame, columns=("username", "email", "active", "actions"), show="headings")
        self.tree.heading("username", text="Username")
        self.tree.heading("email", text="Email")
        self.tree.heading("active", text="Status")
        self.tree.heading("actions", text="Actions")
        self.tree.column("actions", width=150, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

        self.pagination_frame = tk.Frame(self.users_frame)
        self.pagination_frame.pack(pady=10)

        self.prev_button = tk.Button(self.pagination_frame, text="Previous", command=self.prev_page)
        self.prev_button.pack(side=tk.LEFT)

        self.page_label = tk.Label(self.pagination_frame, text=f"Page {self.current_page}")
        self.page_label.pack(side=tk.LEFT)

        self.next_button = tk.Button(self.pagination_frame, text="Next", command=self.next_page)
        self.next_button.pack(side=tk.LEFT)

    def load_users(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        total_users = self.user_model.collection.count_documents({})
        start = (self.current_page - 1) * self.page_size
        users = self.user_model.collection.find().skip(start).limit(self.page_size)

        for user in users:
            self.tree.insert("", tk.END, iid=str(user['_id']),
                             values=(user['username'], user.get('email', 'No email'), 'Edit/Delete'))

        self.page_label.config(text=f"Page {self.current_page}")
        self.prev_button.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_page * self.page_size < total_users else tk.DISABLED)

    def add_user(self):
        self.add_user_window = tk.Toplevel(self.root)
        self.add_user_window.title("Add User")
        self.add_user_window.geometry("300x300")

        tk.Label(self.add_user_window, text="Username").pack(pady=5)
        self.username_entry = tk.Entry(self.add_user_window)
        self.username_entry.pack(pady=5)

        tk.Label(self.add_user_window, text="Password").pack(pady=5)
        self.password_entry = tk.Entry(self.add_user_window, show="*")
        self.password_entry.pack(pady=5)

        tk.Label(self.add_user_window, text="Email (optional)").pack(pady=5)
        self.email_entry = tk.Entry(self.add_user_window)
        self.email_entry.pack(pady=5)

        add_button = tk.Button(self.add_user_window, text="Add", command=self.save_user)
        add_button.pack(pady=10)

    def save_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        email = self.email_entry.get()
        if username and password:
            self.user_model.create_user(username, password, email)
            self.load_users()
        else:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
        self.add_user_window.destroy()

    def update_user(self, user_id):
        user = self.user_model.collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return

        self.update_user_window = tk.Toplevel(self.root)
        self.update_user_window.title("Update User")
        self.update_user_window.geometry("300x300")

        tk.Label(self.update_user_window, text="Username").pack(pady=5)
        self.username_entry = tk.Entry(self.update_user_window)
        self.username_entry.insert(0, user['username'])
        self.username_entry.pack(pady=5)

        tk.Label(self.update_user_window, text="Password").pack(pady=5)
        self.password_entry = tk.Entry(self.update_user_window, show="*")
        self.password_entry.insert(0, user['password'])
        self.password_entry.pack(pady=5)

        tk.Label(self.update_user_window, text="Email (optional)").pack(pady=5)
        self.email_entry = tk.Entry(self.update_user_window)
        self.email_entry.insert(0, user.get('email', ''))
        self.email_entry.pack(pady=5)

        save_button = tk.Button(self.update_user_window, text="Save", command=lambda: self.save_updated_user(user_id))
        save_button.pack(pady=10)

    def save_updated_user(self, user_id):
        new_username = self.username_entry.get()
        new_password = self.password_entry.get()
        new_email = self.email_entry.get()
        if new_username and new_password:
            self.user_model.update_user(user_id, username=new_username, email=new_email)
            self.load_users()
        else:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
        self.update_user_window.destroy()

    def delete_user(self, user_id):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this user?"):
            self.user_model.collection.delete_one({"_id": ObjectId(user_id)})
            self.load_users()

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        user_id = selected_item[0]

        self.action_window = tk.Toplevel(self.root)
        self.action_window.title("User Actions")

        edit_button = tk.Button(self.action_window, text="Edit", command=lambda: self.perform_action(user_id, "edit"))
        edit_button.pack(pady=5)

        delete_button = tk.Button(self.action_window, text="Delete", command=lambda: self.perform_action(user_id, "delete"))
        delete_button.pack(pady=5)

    def perform_action(self, user_id, action):
        if action == "edit":
            self.update_user(user_id)
        elif action == "delete":
            self.delete_user(user_id)
        self.action_window.destroy()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_users()

    def next_page(self):
        total_users = self.user_model.collection.count_documents({})
        if self.current_page * self.page_size < total_users:
            self.current_page += 1
            self.load_users()
