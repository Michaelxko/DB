import customtkinter as ctk
from tkinter import messagebox
import subprocess

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

subprocess.run(["python", "DB.py"])

def confirm_execution():
    dialog = ctk.CTk()
    dialog.withdraw()  

    confirmed = messagebox.askyesno("Confirmation", "Wait for the Excel to open and select a Conection, Did you select a connection?")

    dialog.destroy()

    return confirmed

if confirm_execution():
    import subprocess
    subprocess.run(["python", "linkgen.py"])
