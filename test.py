import tkinter as tk
import sqlite3
from firebase_admin import credentials, firestore, initialize_app
import Adafruit_DHT
import time
import random

# Initialize Firebase
cred = credentials.Certificate("iot-irrigation-d58cc-7f31ca2b31db.json")
firebase_app = initialize_app(cred)

# Initialize Firestore database
db = firestore.client()

# SQLite setup
conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# Create a table named 'data'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS data (
        id INTEGER PRIMARY KEY,
        temp VARCHAR(10),
        humi VARCHAR(10),
        moist VARCHAR(10)
    )
''')
conn.commit()

DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

# Function to read sensor values
def read_sensor():
    humi, temp = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)

    if humi is not None and temp is not None:
        formatted_temp = "{0:0.1f}".format(temp)
        formatted_humi = "{0:0.1f}".format(humi)
        formatted_moist = "{0:0.1f}".format(generate_moist())  # Generate moist data
        # Print sensor values
        print("Temp={} Humidity={} Moisture={}".format(formatted_temp, formatted_humi, formatted_moist))
        return formatted_temp, formatted_humi, formatted_moist
    else:
        print("Sensor failure. Check wiring.")
        return None, None, None

def generate_moist():
    return random.randint(1, 100)

def generate_data():
    formatted_temp, formatted_humi, formatted_moist = read_sensor()

    if formatted_temp is not None and formatted_humi is not None and formatted_moist is not None:
        # Display the generated data in the Tkinter window
        temp_label.config(text=f"Temperature: {formatted_temp}C")
        humi_label.config(text=f"Humidity: {formatted_humi}%")
        moist_label.config(text=f"Moisture: {formatted_moist}%")

        # Update the Firebase document
        update_firebase(formatted_temp, formatted_humi, formatted_moist)

    root.after(3000, generate_data)

def update_firebase(temp, humi, moist):
    # Document ID to update
    document_id = "Lpwoehp7wjCoQcbRUNo1"

    # Reference to the document in the 'plants' collection
    plant_ref = db.collection('plants').document(document_id)

    # Update the document fields with the generated values
    plant_ref.update({
        'temp': temp,
        'humi': humi,
        'moist': moist,
    })

# Tkinter setup
root = tk.Tk()
root.title("Smart Irrigation System")

# Labels to display the generated data
temp_label = tk.Label(root, text="")
temp_label.pack(pady=5)

humi_label = tk.Label(root, text="")
humi_label.pack(pady=5)

moist_label = tk.Label(root, text="")
moist_label.pack(pady=5)

# Check if a row with id = 1 already exists
cursor.execute("SELECT 1 FROM data WHERE id = 1 LIMIT 1")
existing_row = cursor.fetchone()

# If no row exists, insert the initial row with NULL values
if not existing_row:
    cursor.execute('''
        INSERT INTO data (id, temp, humi, moist) VALUES (1, NULL, NULL, NULL)
    ''')
    conn.commit()

# Initial call to generate_data
generate_data()

# Start the Tkinter event loop
root.mainloop()

# Close the SQLite connection
conn.close()
