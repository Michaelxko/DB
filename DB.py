import customtkinter as ctk
from tkinter import Toplevel, messagebox, StringVar, BooleanVar
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

def get_custom_entry(frame):
    entry_var = StringVar()
    entry = ctk.CTkEntry(frame, textvariable=entry_var, placeholder_text="Custom")
    entry.pack(side='left')
    return entry_var

def get_all_inputs():
    root = ctk.CTk()
    root.withdraw()

    def on_submit():
        selected_origins = [origin for origin, var in origins_vars.items() if var.get()]
        selected_destinations = [destination for destination, var in destinations_vars.items() if var.get()]

        if custom_origin_var.get():
            selected_origins.append(custom_origin_var.get())

        if custom_destination_var.get():
            selected_destinations.append(custom_destination_var.get())

        if not selected_origins or not selected_destinations:
            messagebox.showerror("Error", "Please select at least one origin and one destination.", parent=dialog)
            return

        selected_traveler = traveler_var.get()
        print(f"Selected Traveler: {selected_traveler}")
        trip_date = date_entry.get() + ".2024"
        departure_time = departure_time_entry.get()
        arrival_time = arrival_time_entry.get()

        inputs.update({
            'traveler': selected_traveler,
            'date': trip_date,
            'departure': departure_time,
            'arrival': arrival_time,
            'origins': selected_origins,
            'destinations': selected_destinations
        })
        dialog.destroy()

    def on_close():
        inputs['closed'] = True
        dialog.destroy()

    dialog = ctk.CTkToplevel()
    dialog.title("Travel Information")
    dialog.geometry("320x730")  # Adjust size for additional options

    inputs = {}
    
    traveler_var = StringVar(value="michael")  # Default selection
    traveler_frame = ctk.CTkFrame(dialog)
    traveler_frame.pack(fill='x', padx=10, pady=5)
    date_frame = ctk.CTkFrame(dialog)
    date_frame.pack(fill='x', padx=10, pady=5)
    time_frame = ctk.CTkFrame(dialog)
    time_frame.pack(fill='x', padx=10, pady=5)
    origin_frame = ctk.CTkFrame(dialog)
    origin_frame.pack(fill='x', padx=10, pady=5)
    destination_frame = ctk.CTkFrame(dialog)
    destination_frame.pack(fill='x', padx=10, pady=5)
    

    # Origin selection
    ctk.CTkLabel(origin_frame, text="Select Stations:").pack(side='top', pady=5)
    origins_vars = {origin: BooleanVar(value=False) for origin in ["Darmstadt Hbf", "FRA Frankfurt Airport", "Mainz Hbf", "Frankfurt(Main)Hbf"]}
    for origin, var in origins_vars.items():
        ctk.CTkCheckBox(origin_frame, text=origin, variable=var).pack(anchor='w', pady=5)

    custom_origin_var = get_custom_entry(origin_frame)

    # Destination selection
    ctk.CTkLabel(destination_frame, text="Select Stations:").pack(side='top', pady=5)
    destinations_vars = {destination: BooleanVar(value=False) for destination in ["Solingen Hbf", "Köln Hbf", "Köln Messe/Deutz"]}
    for destination, var in destinations_vars.items():
        ctk.CTkCheckBox(destination_frame, text=destination, variable=var).pack(anchor='w', pady=5)

    custom_destination_var = get_custom_entry(destination_frame)

    # Date entry
    ctk.CTkLabel(date_frame, text="Fahrdaten:").pack(side='top')
    ctk.CTkLabel(date_frame, text="Date:").pack(anchor="nw",side='top', padx=5)
    date_entry = ctk.CTkEntry(date_frame, placeholder_text="TT.MM")
    date_entry.pack(side='left', padx=5)

    
    ctk.CTkLabel(time_frame, text="Departure:").pack(side='top')
    #ctk.CTkLabel(time_frame, text="Departure:").pack(anchor="nw",side='top', padx=5)
    departure_time_entry = ctk.CTkEntry(time_frame, placeholder_text="Departure Time")
    departure_time_entry.pack(side='left', padx=5)
    arrival_time_entry = ctk.CTkEntry(time_frame, placeholder_text="Arrival Time")
    arrival_time_entry.pack(side='left', padx=5)

    ctk.CTkLabel(traveler_frame, text="Start:").pack(side='top', pady=5)
    ctk.CTkRadioButton(traveler_frame, text="Darmstadt", variable=traveler_var, value="michael").pack(anchor='w', pady=2)
    ctk.CTkRadioButton(traveler_frame, text="Solingen", variable=traveler_var, value="shira").pack(anchor='w', pady=2)

    # Submit button
    submit_button = ctk.CTkButton(dialog, text="Submit", command=on_submit)
    submit_button.pack(side='bottom', padx=10, pady=10)

    

    dialog.protocol("WM_DELETE_WINDOW", on_close)
    dialog.wait_window(dialog)

    return inputs


def create_bahn_guru_link(origin: str, destination: str, date: str, departure_after=None, arrival_before=None, duration=None, max_changes=None):
    base_url = "https://bahn.guru/day"
    url = f"{base_url}?origin={origin}&destination={destination}&class=2&bc=4&age=Y&date={date}"
    if departure_after:
        url += f"&departureAfter={departure_after}"
    if arrival_before:
        url += f"&arrivalBefore={arrival_before}"
    if duration is not None:
        url += f"&duration={duration}"
    if max_changes is not None:
        url += f"&maxChanges={max_changes}"
    return url

def create_bahn_guru_links(origins, destinations, date, departure_after=None, arrival_before=None, duration=None, max_changes=None):
    links = []
    for origin in origins:
        for destination in destinations:
            url = create_bahn_guru_link(origin, destination, date, departure_after, arrival_before, duration, max_changes)
            links.append({"url": url, "origin": origin, "destination": destination})
    return links

def scrape_data_and_append_to_csv(url, origin, destination, csv_path):
    response = requests.get(url).text
    soup = BeautifulSoup(response, 'html.parser')
    table = soup.find('table')
    
    if table is not None:
        print(f"Processing: Origin: {origin} - Destination: {destination}")
        rows = []
        for row in table.find_all('tr')[1:]:  # Assuming the first row is headers
            cols = row.find_all('td')
            if cols:
                col_data = [col.text.strip() for col in cols]
                
                fahrzeit_index = 2 
                if len(col_data) > fahrzeit_index and len(col_data[fahrzeit_index]) > 2:
                    col_data[fahrzeit_index] = col_data[fahrzeit_index][:-2]
                
                preis_index = 6  
                if len(col_data) > preis_index and len(col_data[preis_index]) > 3:
                    col_data[preis_index] = col_data[preis_index][:-3]
                
                rows.append(col_data)
                
        if rows:
            df = pd.DataFrame(rows)
            df['Origin'] = origin
            df['Destination'] = destination
            df.to_csv(csv_path, mode='a', header=False, index=False)
    else:
        print(f"No table found for URL: Origin: {origin} - Destination: {destination}")

import pandas as pd

def convert_csv_to_excel(csv_path, excel_path, user_inputs):
    column_names = ["Abfahrt", "Ankunft", "Fahrzeit", "Umstiege", "VIA", "Mit", "Preis", "Von", "Bis"]
    df = pd.read_csv(csv_path, header=None, names=column_names)

    df_abfahrt = df.sort_values(by="Von")
    df_ankunft = df.sort_values(by="Bis")
    df_zeit_abfahrt = df.sort_values(by="Abfahrt")
    df_zeit_ankunft = df.sort_values(by="Ankunft")

    df['Preis'] = pd.to_numeric(df['Preis'].str.replace(',', '.').str.extract(r'(\d+\.\d+)')[0], errors='coerce')
    df_preis = df.sort_values(by="Preis")

    inputs_df = pd.DataFrame([user_inputs], columns=['traveler', 'date', 'departure', 'arrival'])

    link_df = pd.DataFrame(columns=column_names)
    link_df.loc[1, 'Date'] = user_inputs['date']  # Set the date in the second row under the "Date" column

    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_abfahrt.to_excel(writer, index=False, sheet_name="Abfahrt Ort")
        df_ankunft.to_excel(writer, index=False, sheet_name="Ankunft Ort")
        df_preis.to_excel(writer, index=False, sheet_name="Preis")
        df_zeit_abfahrt.to_excel(writer, index=False, sheet_name="Abfahrt Zeit")
        df_zeit_ankunft.to_excel(writer, index=False, sheet_name="Ankunft Zeit")
        link_df.to_excel(writer, index=False, sheet_name="Link Generator")
        inputs_df.to_excel(writer, index=False, sheet_name='User Inputs')
    

def delete_csv_file(csv_path):
    try:
        os.remove(csv_path)
        print(f"Successfully deleted the data.csv file")
    except Exception as e:
        print(f"Error deleting the CSV file: {csv_path}. Error: {e}")

def main():
    user_inputs = get_all_inputs()
    
    if user_inputs.get('closed', False):
        print("Input window was closed. Exiting program.")
        return  

    traveler = user_inputs.get('traveler', '')
    date = user_inputs.get('date', '')
    departure_after = user_inputs.get('departure', '00:01')
    arrival_before = user_inputs.get('arrival', '23:59')

    selected_origins = user_inputs.get('origins', [])
    selected_destinations = user_inputs.get('destinations', [])

    if traveler.lower() == "michael":
        origins = selected_origins
        destinations = selected_destinations
    elif traveler.lower() == "shira":
        origins = selected_destinations
        destinations = selected_origins
    else:
        origins = selected_origins
        destinations = selected_destinations

    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "data.csv")
    excel_path = os.path.join(script_dir, "fahrten.xlsx")

    links = create_bahn_guru_links(origins, destinations, date, departure_after, arrival_before, duration=4, max_changes=1)

    for link_info in links:
        scrape_data_and_append_to_csv(link_info["url"], link_info["origin"], link_info["destination"], csv_path)

    convert_csv_to_excel(csv_path, excel_path, user_inputs)
    delete_csv_file(csv_path)

    return excel_path

if __name__ == "__main__":
    excel_path = main()
    os.system(f'start excel "{excel_path}"')    
