from flask import Flask, render_template, request
import requests
import sqlite3

app = Flask(__name__)

API_KEY = '4c12e4b08ac9e4cb451626bfd8c8cf77'
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

# Create database and table
conn = sqlite3.connect('weather_log.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT,
        temperature REAL,
        humidity REAL,
        wind_speed REAL,
        description TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()
conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city_name = request.form['city']
        weather_data = get_weather_data(city_name)
        if weather_data:
            log_to_database(city_name, weather_data)
        return render_template('index.html', weather_data=weather_data)
    return render_template('index.html', weather_data="")

def get_weather_data(city):
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric'  
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if response.status_code == 200:
        weather_data = {
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'description': data['weather'][0]['description']
        }
        return weather_data
    else:
        return None

def log_to_database(city, weather_data):
    conn = sqlite3.connect('weather_log.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO weather_logs (city, temperature, humidity, wind_speed, description)
        VALUES (?, ?, ?, ?, ?)
    ''', (city, weather_data['temperature'], weather_data['humidity'], weather_data['wind_speed'], weather_data['description']))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    app.run(debug=True)
