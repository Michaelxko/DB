import customtkinter as ctk
from tkinter import messagebox
import subprocess
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

current_directory = os.path.dirname(os.path.abspath(__file__))
db_script_path = os.path.join(current_directory, "DB.py")
linkgen_script_path = os.path.join(current_directory, "linkgen.py")

try:
    subprocess.run(["python", db_script_path])
    
    if messagebox.askyesno("Confirmation", "Did you copy a Connection and save the excel file?"):
        subprocess.run(["python", linkgen_script_path])

except Exception as e:
    print("An error occurred:", e)
