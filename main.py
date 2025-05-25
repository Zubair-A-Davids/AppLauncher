import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import subprocess
import os
import json

ITEMS_FILE = "items.json"

root = tk.Tk()
root.title("Portable Launcher")
root.geometry("600x400")

selected_item = None  # Track selected item globally

def add_file():
    window = tk.Toplevel(root)
    window.title("Add File/Script")
    
    tk.Label(window, text="Select a File or Script:").pack()
    file_path = filedialog.askopenfilename(title="Select a File or Script")
    
    if not file_path:
        window.destroy()
        return
    
    custom_name = simpledialog.askstring("Custom Name", "Enter a custom name:", parent=window)
    description = simpledialog.askstring("Description", "Enter a description:", parent=window)

    # Checkbox to enable icon selection
    icon_var = tk.BooleanVar()
    icon_checkbox = tk.Checkbutton(window, text="Add Icon?", variable=icon_var)
    icon_checkbox.pack()

    def confirm_selection():
        icon_path = filedialog.askopenfilename(title="Select an Icon Image", filetypes=[("Image Files", "*.png;*.jpg;*.ico")]) if icon_var.get() else None
        add_to_list(file_path, custom_name, description, icon_path)
        window.destroy()

    tk.Button(window, text="Confirm", command=confirm_selection).pack()

def run_program(file_path):
    try:
        if file_path.endswith(".ps1"):
            subprocess.run(f"powershell -ExecutionPolicy Bypass -File \"{file_path}\"", shell=True)
        elif file_path.endswith(".vbs") or file_path.endswith(".js"):
            subprocess.run(f"wscript \"{file_path}\"", shell=True)
        else:
            subprocess.Popen(f'"{file_path}"', shell=True)
    except Exception as e:
        print(f"Error launching: {e}")

def edit_name(file_path, name_label):
    new_name = simpledialog.askstring("Edit Name", "Enter new item name:", parent=root)
    if new_name:
        update_name(file_path, new_name)
        name_label.config(text=new_name)

def edit_description(file_path, desc_label):
    new_description = simpledialog.askstring("Edit Description", "Enter new description:", parent=root)
    if new_description:
        update_description(file_path, new_description)
        desc_label.config(text=new_description)

def delete_item(file_path, frame_item):
    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{file_path}'?")
    if confirm:
        update_items(file_path)
        frame_item.destroy()

def select_item(event):
    global selected_item

    frame_item = event.widget
    while frame_item and not isinstance(frame_item, tk.Frame):
        frame_item = frame_item.master  

    if not frame_item or frame_item == frame:
        return

    if selected_item and selected_item != frame_item:
        selected_item.config(bg="SystemButtonFace")  
        selected_item.update_idletasks()  

    selected_item = frame_item
    selected_item.config(bg="yellow")  
    selected_item.update_idletasks()  

def add_to_list(file_path, custom_name, description, icon_path=None):
    frame_item = tk.Frame(frame, bg="SystemButtonFace", borderwidth=1, relief="solid")
    frame_item.pack(fill="x", pady=2)

    default_icon_path = os.path.join("icons", "default_icon.png")  # Ensure correct default icon path

    if not icon_path or not os.path.exists(icon_path):  # Use default if missing
        icon_path = default_icon_path

    if os.path.exists(icon_path):  # Ensure valid image file
        icon_image = tk.PhotoImage(file=icon_path)
        icon_label = tk.Label(frame_item, image=icon_image)
        icon_label.image = icon_image  # Prevent garbage collection issues
        icon_label.pack(side="left", padx=5)
    else:
        print(f"Warning: Icon not found '{icon_path}'")  # Debug log

    display_name = custom_name if custom_name else os.path.basename(file_path)
    name_label = tk.Label(frame_item, text=display_name, anchor="w", cursor="hand2", font=("Arial", 14))
    name_label.pack(side="left", fill="x", expand=True)

    desc_label = tk.Label(frame_item, text=description if description else "", anchor="e", font=("Arial", 14))
    desc_label.pack(side="right")

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

    save_item(file_path, custom_name, description, icon_path)

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

# UI Components
add_file_button = tk.Button(root, text="Add File/Script", command=add_file, font=("Arial", 14))
main_frame = tk.Frame(root)

add_file_button.pack(side="bottom", fill="x", pady=5)

frame = tk.Frame(main_frame)
# Frame to hold both labels in one row
header_frame = tk.Frame(main_frame)
header_frame.pack(fill="x", padx=10, pady=5)

# Label for "Item List" aligned to the left
item_list_label = tk.Label(header_frame, text="Item List", font=("Arial", 16, "bold"))
item_list_label.pack(side="left")

# Label for "Item Description" aligned to the right
item_description_label = tk.Label(header_frame, text="Item Description", font=("Arial", 14, "bold"))
item_description_label.pack(side="right")

frame.pack(pady=5, fill="both", expand=True)

load_items()

add_file_button.pack(pady=5)
main_frame.pack(pady=10, fill="both", expand=True)

root.mainloop()