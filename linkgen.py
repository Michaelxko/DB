import urllib.parse
import pandas as pd
from datetime import datetime
import webbrowser

station_details = {
    "Darmstadt Hbf": {
        "name": "Darmstadt Hbf",
        "id": "8000068",
        "x": "8629635",
        "y": "49872504"
    },
    "Solingen Hbf": {
        "name": "Solingen Hbf",
        "id": "8000087",
        "x": "7004188",
        "y": "51160766"
    },
    "FRA Frankfurt Airport": {
        "name": "Frankfurt(M) Flughafen Fernbf",
        "id": "8070003",
        "x": "8570181",
        "y": "50053169"
    },
    "Köln Hbf": {
        "name": "Köln Hbf",
        "id": "8000207",
        "x": "6958730",
        "y": "50943029"
    },
    "Mainz Hbf": {
        "name": "Mainz Hbf",
        "id": "8000240",
        "x": "8258723",
        "y": "50001113"
    },
    "Köln Messe/Deutz": {
        "name": "Köln Messe/Deutz",
        "id": "8003368",
        "x": "6975000",
        "y": "50940872"
    }
}

def create_db_link(station_details, start_station, destination_station, date, time):
    base_url = "https://www.bahn.de/buchung/fahrplan/suche#"
    
    start_station_code = station_details[start_station]['id']
    dest_station_code = station_details[destination_station]['id']
    
    params = {
        "sts": "true",
        "so": start_station,
        "zo": destination_station,
        "kl": "2",
        "r": "9:17:KLASSE_2:1",
        "soid": f"A=1@O={start_station}@X={station_details[start_station]['x']}@Y={station_details[start_station]['y']}@U=80@L={start_station_code}@B=1@p=1708542717@",
        "zoid": f"A=1@O={destination_station}@X={station_details[destination_station]['x']}@Y={station_details[destination_station]['y']}@U=80@L={dest_station_code}@B=1@p=1708542717@",
        "sot": "ST",
        "zot": "ST",
        "soei": start_station_code,
        "zoei": dest_station_code,
        "hd": f"{date}T{time}:43",
        "hza": "D",
        "hz": "[]",
        "ar": "false",
        "s": "false",
        "d": "false",
        "vm": "00,01,02,03,04,05,06,07,08,09",
        "fm": "false",
        "bp": "false"
    }
    
    params_encoded = "&".join(f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in params.items())
    
    return base_url + params_encoded

df = pd.read_excel("fahrten.xlsx", sheet_name="Link Generator")

start_station = df.iloc[0]["Von"]
destination_station = df.iloc[0]["Bis"]
date = df.iloc[0]["Date"]
time = df.iloc[0]["Abfahrt"].split()[0] 

date = datetime.strptime(date, "%d.%m.%Y").strftime("%Y-%m-%d")

db_link = create_db_link(station_details, start_station, destination_station, date, time)
print("Generated URL:", db_link)

webbrowser.open(db_link)
