Weather Data Logger System

A Python console application that fetches live weather data using WeatherAPI, validates it, stores it in a MySQL database, and provides weather history/statistics.

Features
Check live weather by city
Validate weather data before saving
Save reports in MySQL
View weather history and last search
Find hottest and coldest city searched
Count total searches
Export history to a text file
View weather statistics
Track failed validations and logs
Tech Stack
Python
MySQL
WeatherAPI
requests
mysql-connector-python
python-dotenv
Setup
Clone the repository
Install dependencies:
pip install requests mysql-connector-python python-dotenv
Create a .env file:
API_KEY=your_weatherapi_key
host=localhost
password=your_mysql_password
database=weather_db
Create the MySQL table:
CREATE TABLE weather_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100),
    country VARCHAR(100),
    temperature FLOAT,
    humidity INT,
    wind_speed FLOAT,
    weather_condition VARCHAR(100),
    search_date DATE,
    search_time TIME,
    validation_status VARCHAR(20)
);
Run
python main.py
Author

udayini vale
