import tkinter as tk
from tkinter import ttk
from views.todo import TodoView
from views.user import UserView
from views.profile import ProfileView
from models.user import UserModel
from models.todo import TodoModel

class DashboardView:
    def __init__(self, sidebar_frame, content_frame, username, logout_callback):
        self.sidebar_frame = sidebar_frame
        self.content_frame = content_frame
        self.username = username
        self.logout_callback = logout_callback
        self.user_model = UserModel()
        self.todo_model = TodoModel()

        self.setup_sidebar()

        # Initially show the dashboard view
        self.show_dashboard()

    def setup_sidebar(self):
        tk.Button(self.sidebar_frame, text="Dashboard", command=self.show_dashboard, width=15).pack(fill=tk.X)
        tk.Button(self.sidebar_frame, text="Todos", command=self.show_todos).pack(fill=tk.X)
        tk.Button(self.sidebar_frame, text="Users", command=self.show_users).pack(fill=tk.X)
        tk.Button(self.sidebar_frame, text="Profile", command=self.show_profile).pack(fill=tk.X)
        tk.Button(self.sidebar_frame, text="Logout", command=self.logout).pack(fill=tk.X)

    def show_dashboard(self):
        self.clear_content()
        self.create_summary_boxes()

    def show_todos(self):
        self.clear_content()
        TodoView(self.content_frame, self.username)

    def show_users(self):
        self.clear_content()
        UserView(self.content_frame)

    def show_profile(self):
        self.clear_content()
        ProfileView(self.content_frame, self.username)

    def logout(self):
        self.clear_content()
        self.logout_callback()  # Call the logout callback function

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def create_summary_boxes(self):
         # Get the user object to retrieve user ID
        user = self.user_model.find_user(self.username)
        user_id = user["_id"]

        # Top Frame for Summary Boxes
        top_frame = tk.Frame(self.content_frame)
        top_frame.pack(fill=tk.BOTH, expand=True, pady=20)

         # Configure grid layout to expand with window size
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=1)
        top_frame.grid_columnconfigure(2, weight=1)

        # Summary Box for Total Todos
        total_todos = self.todo_model.get_total_todos(user_id)  
        # Summary Box for Total Users
        total_users = self.user_model.get_total_users()
        # Summary Box for Total Completed Todos
        completed_todos = self.todo_model.get_completed_todos()

        # Create beautiful boxes for summary stats
        self.create_summary_box(top_frame, "Total Users", total_users, 0, 0)
        self.create_summary_box(top_frame, "Total Todos", total_todos, 0, 1)
        self.create_summary_box(top_frame, "Completed Todos", completed_todos, 0, 2)


    # create summary box
    def create_summary_box(self, parent, title, value, row, column):
        frame = ttk.LabelFrame(parent, text=title, padding=(20, 10))
        frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        value_label = ttk.Label(frame, text=str(value), font=("Helvetica", 24, "bold"))
        value_label.grid(row=0, column=0, pady=20, padx=20)



