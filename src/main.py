# filepath: c:\Users\zdavi\OneDrive\Documents\GitHub\CA-Launcher\src\main.py
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import subprocess
import os
import json

ITEMS_FILE = "items.json"
APP_VERSION = "1.0.0"

root = tk.Tk()
root.title("CA Launcher")
root.geometry("600x400")
root.iconbitmap("icons/icon.ico")

selected_item = None  # Track selected item globally

def add_file():
    window = tk.Toplevel(root)
    window.title("Add File/Script")
    window.transient(root)
    window.focus_force()
    window.grab_set()
    tk.Label(window, text="Select a File or Script:", font=("Arial", 14)).pack()
    file_path = filedialog.askopenfilename(title="Select a File or Script")

    if not file_path:
        window.destroy()
        return

    custom_name = custom_name_dialog(window)
    if custom_name is None:
        window.destroy()
        return

    description = description_dialog(window)

    # Checkbox to enable icon selection
    tk.Label(window, text="(Optional)", font=("Arial", 12)).pack(pady=(0, 10))
    tk.Label(window, text="You can add a custom icon for your shortcut.", font=("Arial", 12)).pack(pady=(0, 10))
    icon_var = tk.BooleanVar()
    icon_checkbox = tk.Checkbutton(window, text="Add Icon?", variable=icon_var, font=("Arial", 14))
    icon_checkbox.pack()

    # Add another line of text below the checkbox
    tk.Label(window, text="The Icon has to be 32x32", font=("Arial", 12, "bold"), fg="blue").pack(pady=(0, 10))

    def confirm_selection():
        icon_path = filedialog.askopenfilename(
            title="Select an Icon",
            filetypes=[("Image Files", "*.png;*.jpg;*.ico")]
        ) if icon_var.get() else None
        add_to_list(file_path, custom_name, description, icon_path)
        save_item(file_path, custom_name, description, icon_path)  # <--- Only save here!
        window.destroy()

    tk.Button(
        window,
        text="Confirm",
        command=confirm_selection,
        font=("Arial", 14),
        bg="#ADD8E6",                # Light blue background
        activebackground="#ADD8E6"    # Light blue on click/hover
    ).pack(pady=(10, 10))

def run_program(file_path):
    try:
        if file_path.endswith(".ps1"):
            subprocess.run(f'powershell -ExecutionPolicy Bypass -File "{file_path}"', shell=True)
        elif file_path.endswith(".vbs") or file_path.endswith(".js"):
            subprocess.run(f'wscript "{file_path}"', shell=True)
        else:
            subprocess.Popen(f'"{file_path}"', shell=True)
    except Exception as e:
        print(f"Error launching: {e}")

def edit_name_dialog(parent, current_name):
    dialog = tk.Toplevel(parent)
    dialog.title("Edit Name")
    dialog.transient(parent)      # Ensure dialog is always on top of parent
    dialog.focus_force()          # Focus the dialog window
    dialog.grab_set()
    tk.Label(dialog, text="Enter new item name:", font=("Arial", 14)).pack(padx=10, pady=10)
    entry = tk.Entry(dialog, width=30, font=("Arial", 14))
    entry.insert(0, current_name)
    entry.pack(padx=10, pady=5)
    entry.focus_set()
    result = {"value": None}

    def on_ok():
        result["value"] = entry.get()
        dialog.destroy()

    def on_cancel():
        result["value"] = None
        dialog.destroy()

    btn_frame = tk.Frame(dialog)
    btn_frame.pack(pady=(0, 10))

    ok_btn = tk.Button(btn_frame, text="OK", command=on_ok, bg="#ADD8E6", activebackground="#ADD8E6", font=("Arial", 14))
    ok_btn.pack(side="left", padx=(0, 10))
    cancel_btn = tk.Button(btn_frame, text="Cancel", command=on_cancel, bg="#FFB6B6", activebackground="#FFB6B6", font=("Arial", 14))
    cancel_btn.pack(side="left")

    dialog.bind('<Return>', lambda event: on_ok())
    dialog.bind('<Escape>', lambda event: on_cancel())
    dialog.wait_window()
    return result["value"]

def edit_name(file_path, name_label):
    current_name = name_label.cget("text")
    new_name = edit_name_dialog(root, current_name)
    if new_name:
        update_name(file_path, new_name)
        name_label.config(text=new_name)

def edit_description(file_path, desc_label):
    new_description = description_dialog(root)
    if new_description:
        update_description(file_path, new_description)
        desc_label.config(text=new_description)

def delete_item(file_path, frame_item):
    global selected_item
    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{file_path}'?")
    if confirm:
        update_items(file_path)
        frame_item.destroy()
        if selected_item == frame_item:
            selected_item = None

def select_item(event):
    global selected_item
    frame_item = event.widget
    while frame_item and not isinstance(frame_item, tk.Frame):
        frame_item = frame_item.master

    if not frame_item:
        return

    if selected_item and selected_item != frame_item:
        selected_item.config(bg="SystemButtonFace")

    selected_item = frame_item
    selected_item.config(bg="#ADD8E6")

def add_to_list(file_path, custom_name, description, icon_path=None):
    frame_item = tk.Frame(scrollable_frame, bg="SystemButtonFace", borderwidth=1, relief="solid")
    frame_item.pack(fill="x", expand=True, pady=2)

    default_icon_path = os.path.join("icons", "default_icon.png")
    if not icon_path or not os.path.exists(icon_path):
        icon_path = default_icon_path

    # Limit icon size for performance
    icon_image = None
    if os.path.exists(icon_path):
        try:
            icon_image = tk.PhotoImage(file=icon_path)
            # Resize if needed (for PNG only)
            if icon_image.width() > 32 or icon_image.height() > 32:
                icon_image = icon_image.subsample(
                    max(1, icon_image.width() // 32),
                    max(1, icon_image.height() // 32)
                )
            icon_label = tk.Label(frame_item, image=icon_image)
            icon_label.image = icon_image
            icon_label.grid(row=0, column=0, padx=5, sticky="w")
        except Exception as e:
            print(f"Warning: Could not load icon '{icon_path}': {e}")

    display_name = custom_name if custom_name else os.path.basename(file_path)
    name_label = tk.Label(frame_item, text=display_name, anchor="w", cursor="hand2", font=("Arial", 16))
    name_label.grid(row=0, column=1, sticky="w", padx=(0, 10))

    desc_label = tk.Label(frame_item, text=description if description else "", anchor="e", font=("Arial", 16))
    desc_label.grid(row=0, column=2, sticky="e")

    frame_item.grid_columnconfigure(1, weight=1)
    frame_item.grid_columnconfigure(2, weight=1)

    frame_item.bind("<Button-1>", select_item)
    name_label.bind("<Button-1>", select_item)
    desc_label.bind("<Button-1>", select_item)

    frame_item.bind("<Double-Button-1>", lambda e, path=file_path: run_program(path))
    name_label.bind("<Double-Button-1>", lambda e, path=file_path: run_program(path))
    desc_label.bind("<Double-Button-1>", lambda e, path=file_path: run_program(path))

    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="Edit Name", command=lambda: edit_name(file_path, name_label))
    menu.add_command(label="Edit Description", command=lambda: edit_description(file_path, desc_label))
    menu.add_command(label="Delete", command=lambda: delete_item(file_path, frame_item))

    frame_item.bind("<Button-3>", lambda e: menu.post(e.x_root, e.y_root))
    name_label.bind("<Button-3>", lambda e: menu.post(e.x_root, e.y_root))
    desc_label.bind("<Button-3>", lambda e: menu.post(e.x_root, e.y_root))

def save_item(file_path, custom_name, description, icon_path):
    try:
        with open(ITEMS_FILE, "r") as f:
            items = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        items = []
    items.append({"path": file_path, "name": custom_name, "description": description, "icon": icon_path})
    with open(ITEMS_FILE, "w") as f:
        json.dump(items, f, indent=4)

def update_items(file_path):
    try:
        with open(ITEMS_FILE, "r") as f:
            items = json.load(f)
        items = [item for item in items if item["path"] != file_path]
        with open(ITEMS_FILE, "w") as f:
            json.dump(items, f, indent=4)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

def update_name(file_path, new_name):
    try:
        with open(ITEMS_FILE, "r") as f:
            items = json.load(f)
        for item in items:
            if item["path"] == file_path:
                item["name"] = new_name
        with open(ITEMS_FILE, "w") as f:
            json.dump(items, f, indent=4)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

def update_description(file_path, new_description):
    try:
        with open(ITEMS_FILE, "r") as f:
            items = json.load(f)
        for item in items:
            if item["path"] == file_path:
                item["description"] = new_description
        with open(ITEMS_FILE, "w") as f:
            json.dump(items, f, indent=4)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

def load_items():
    try:
        with open(ITEMS_FILE, "r") as f:
            items = json.load(f)
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict) and "path" in item and "name" in item and "description" in item:
                    add_to_list(item["path"], item["name"], item["description"], item.get("icon"))
    except (FileNotFoundError, json.JSONDecodeError):
        pass

def custom_name_dialog(parent):
    dialog = tk.Toplevel(parent)
    dialog.title("Custom Name")
    dialog.transient(parent)      # Ensure dialog is always on top of parent
    dialog.focus_force()          # Focus the dialog window
    dialog.grab_set()
    tk.Label(dialog, text="Enter a custom name:", font=("Arial", 14)).pack(padx=10, pady=10)
    entry = tk.Entry(dialog, width=30, font=("Arial", 14))
    entry.pack(padx=10, pady=5)
    entry.focus_set()
    result = {"value": None}

    def on_ok():
        result["value"] = entry.get()
        dialog.destroy()

    def on_cancel():
        result["value"] = None
        dialog.destroy()

    btn_frame = tk.Frame(dialog)
    btn_frame.pack(pady=(0, 10))

    ok_btn = tk.Button(btn_frame, text="OK", command=on_ok, bg="#ADD8E6", activebackground="#ADD8E6", font=("Arial", 14))
    ok_btn.pack(side="left", padx=(0, 10))
    cancel_btn = tk.Button(btn_frame, text="Cancel", command=on_cancel, bg="#FFB6B6", activebackground="#FFB6B6", font=("Arial", 14))
    cancel_btn.pack(side="left")

    dialog.bind('<Return>', lambda event: on_ok())
    dialog.bind('<Escape>', lambda event: on_cancel())
    dialog.wait_window()
    return result["value"]

def description_dialog(parent):
    dialog = tk.Toplevel(parent)
    dialog.title("Description")
    dialog.transient(parent)      # Ensure dialog is always on top of parent
    dialog.focus_force()          # Focus the dialog window
    dialog.grab_set()
    tk.Label(dialog, text="Enter a description:", font=("Arial", 14)).pack(padx=10, pady=10)
    entry = tk.Entry(dialog, width=30, font=("Arial", 14))
    entry.pack(padx=10, pady=5)
    entry.focus_set()
    result = {"value": None}

    def on_ok():
        result["value"] = entry.get()
        dialog.destroy()

    def on_cancel():
        result["value"] = None
        dialog.destroy()

    btn_frame = tk.Frame(dialog)
    btn_frame.pack(pady=(0, 10))

    ok_btn = tk.Button(btn_frame, text="OK", command=on_ok, bg="#ADD8E6", activebackground="#ADD8E6", font=("Arial", 14))
    ok_btn.pack(side="left", padx=(0, 10))
    cancel_btn = tk.Button(btn_frame, text="Cancel", command=on_cancel, bg="#FFB6B6", activebackground="#FFB6B6", font=("Arial", 14))
    cancel_btn.pack(side="left")

    dialog.bind('<Return>', lambda event: on_ok())
    dialog.bind('<Escape>', lambda event: on_cancel())
    dialog.wait_window()
    return result["value"]

# About dialog function
def show_about():
    about_text = (
        f"Compact App Launcher v{APP_VERSION}\n\n"
        "Compact App Launcher is a user-friendly application that allows you to save shortcuts of your frequently used files or scripts and access them conveniently from a single interface.\n\n"
        "Features:\n"
        "• Add and organize shortcuts to files, scripts, and documents\n"
        "• Assign custom names, descriptions, and icons to each shortcut\n"
        "• Edit or remove shortcuts as needed\n"
        "• Launch files and scripts directly from the application\n"
        "• Simple and intuitive graphical user interface\n\n"
        "Technologies Used:\n"
        "• Python 3\n"
        "• Tkinter (for the GUI)\n\n"
        "► zdavids112@gmail.com's First Python Project\n"
    )
    about_win = tk.Toplevel(root)
    about_win.title("About CA Launcher")
    about_win.transient(root)
    about_win.grab_set()
    about_win.geometry("600x500")
    about_win.resizable(False, False)
    tk.Label(
        about_win,
        text="About CA Launcher",
        font=("Arial", 20, "bold")
    ).pack(pady=(20, 10))
    text_widget = tk.Text(
        about_win,
        wrap="word",
        font=("Arial", 14),
        padx=20,
        pady=10,
        height=20,
        width=60,
        bg=about_win.cget("bg"),
        borderwidth=0
    )
    text_widget.insert("1.0", about_text)

    # Add bold tags
    text_widget.tag_configure("bold", font=("Arial", 14, "bold"))
    # Make "CA Launcher v..." bold
    text_widget.tag_add("bold", "1.0", "1.end")
    # Make "Features:" bold
    features_index = text_widget.search("Features:", "1.0", tk.END)
    if features_index:
        text_widget.tag_add("bold", features_index, f"{features_index} + {len('Features:')}c")
    # Make "Technologies Used:" bold
    tech_index = text_widget.search("Technologies Used:", "1.0", tk.END)
    if tech_index:
        text_widget.tag_add("bold", tech_index, f"{tech_index} + {len('Technologies Used:')}c")

    text_widget.config(state="disabled")
    text_widget.pack(expand=True, fill="both")
    tk.Button(
        about_win,
        text="Close",
        command=about_win.destroy,
        font=("Arial", 14),
        bg="#ADD8E6",
        activebackground="#ADD8E6"
    ).pack(pady=(0, 20))

# UI Components
add_file_button = tk.Button(
    root,
    text="Add File/Script",
    command=add_file,
    font=("Century Gothic", 16, "bold"),
    bg="#ADD8E6",  # Light blue background
    activebackground="#73C0DA"  # Light blue highlight on click/hover
)
main_frame = tk.Frame(root)
main_frame.pack(pady=10, fill="both", expand=True)

# Header row // The Item List and Item Description labels
header_frame = tk.Frame(main_frame)
header_frame.pack(fill="x", padx=10, pady=5)
item_list_label = tk.Label(header_frame, text="Item Name", font=("Arial", 18, "bold"))
item_list_label.pack(side="left")
item_description_label = tk.Label(header_frame, text="Item Description", font=("Arial", 18, "bold"))
item_description_label.pack(side="right")

# Scrollable area (optimized)
canvas = tk.Canvas(main_frame, borderwidth=0, highlightthickness=0)
scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

scrollable_frame = tk.Frame(canvas)
scrollable_frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

def on_frame_configure(event):
    # Set canvas scrollregion to the size of the inner frame
    canvas.configure(scrollregion=canvas.bbox("all"))
    # Make the inner frame width match the canvas width
    canvas.itemconfig(scrollable_frame_id, width=canvas.winfo_width())

scrollable_frame.bind("<Configure>", on_frame_configure)
canvas.bind("<Configure>", on_frame_configure)

load_items()
add_file_button.pack(pady=5)

# Add this to your UI, for example as a menu:
menubar = tk.Menu(root)
help_menu = tk.Menu(menubar, tearoff=0)
help_menu.add_command(label="About", command=show_about)
menubar.add_cascade(label="Menu", menu=help_menu)
root.config(menu=menubar)

root.mainloop()