import sqlite3
import json
from datetime import datetime

DB_NAME = "police_patrol.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create Crimes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crimes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crime_type TEXT NOT NULL,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            severity INTEGER DEFAULT 1,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create Patrol Routes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patrol_routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT NOT NULL,
            route_name TEXT,
            waypoints TEXT, -- JSON stored as text
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create Vehicle Status Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            vehicle_id TEXT PRIMARY KEY,
            driver_name TEXT,
            last_lat REAL,
            last_lng REAL,
            status TEXT DEFAULT 'Active'
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def add_crime(crime_type, lat, lng, severity):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO crimes (crime_type, lat, lng, severity) VALUES (?, ?, ?, ?)',
                   (crime_type, lat, lng, severity))
    conn.commit()
    conn.close()

def save_patrol_route(vehicle_id, route_name, waypoints_list):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    waypoints_json = json.dumps(waypoints_list)
    cursor.execute('INSERT INTO patrol_routes (vehicle_id, route_name, waypoints) VALUES (?, ?, ?)',
                   (vehicle_id, route_name, waypoints_json))
    conn.commit()
    conn.close()

def get_recent_crimes(limit=100):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT lat, lng, severity FROM crimes ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    
    # Add some initial sample data for Anantapur
    # (Optional: Link this to your CSV upload logic in app.py)
    add_crime("Theft", 14.6819, 77.6006, 3)
    add_crime("Accident", 14.6910, 77.6100, 5)
    print("Sample data added.")
