import requests
import re
import os
import mysql.connector
import logging
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()
failed_validations=0
logging.basicConfig(
    filename="weather_app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
def validate_city(city):
    return bool(re.fullmatch(r"[A-Za-z .]+",city))
def validate_country(country):
    return bool(re.fullmatch(r"[A-Za-z ]+", country))
def validate_temperature(temp):
    return bool(re.fullmatch(r"-?\d+(\.\d+)?", str(temp)))
def validate_humidity(humidity):
    return bool(re.fullmatch(r"\d+", str(humidity)))
def validate_wind_speed(speed):
    return bool(re.fullmatch(r"\d+(\.\d+)?", str(speed)))
def validate_condition(condition):
    return bool(re.fullmatch(r"[A-Za-z ]+", condition))

def validate_weather_data(
        city,
        country,
        temperature,
        humidity,
        wind_speed,
        condition):

    city_valid = validate_city(city)
    country_valid = validate_country(country)
    temp_valid = validate_temperature(temperature)
    humidity_valid = validate_humidity(humidity)
    wind_valid = validate_wind_speed(wind_speed)
    condition_valid = validate_condition(condition)

    print("\n----- Validation Report -----")

    print("City Validation        :", "Passed" if city_valid else "Failed")
    print("Country Validation     :", "Passed" if country_valid else "Failed")
    print("Temperature Validation :", "Passed" if temp_valid else "Failed")
    print("Humidity Validation    :", "Passed" if humidity_valid else "Failed")
    print("Wind Speed Validation  :", "Passed" if wind_valid else "Failed")
    print("Condition Validation   :", "Passed" if condition_valid else "Failed")

    return (
        city_valid and
        country_valid and
        temp_valid and
        humidity_valid and
        wind_valid and
        condition_valid
    )
def log_validation(city, status):

    with open("validation_log.txt", "a") as file:

        file.write(
            f"{datetime.now().strftime('%d-%m-%Y %I:%M %p')}\n"
        )

        file.write(f"{city}\n")
        file.write(f"{status}\n\n")

def save_invalid_record(
        city,
        country,
        temperature,
        humidity,
        wind_speed,
        condition):

    with open(
        "invalid_weather_records.txt",
        "a"
    ) as file:

        file.write(
            f"{city}, "
            f"{country}, "
            f"{temperature}, "
            f"{humidity}, "
            f"{wind_speed}, "
            f"{condition}\n"
        )

def connect_db():
    return mysql.connector.connect(
        host=os.getenv("host"),
        user="root",
        password=os.getenv("password"),
        database=os.getenv("database")
    )
API_KEY=os.getenv("API_KEY")
def get_weather(city):
    try:
        url="http://api.weatherapi.com/v1/current.json"
        params={
            "key":API_KEY,
            "q":city       
            }
        response=requests.get(url,params=params)
        response.raise_for_status()
        data=response.json()
        if "error" in data:
            print("\n City not found!")
            return None
        return data
    except Exception as e:
        print("Error:",e)
        return None
def save(data):
    try:
        conn=connect_db()
        cursor=conn.cursor()
        city=data["location"]["name"]
        country=data["location"]["country"]
        temperature=data["current"]["temp_c"]
        humidity=data["current"]["humidity"]
        wind_speed=data["current"]["wind_kph"]
        weather_condition=data["current"]["condition"]["text"]
        now=datetime.now()
        search_date=now.date()
        search_time=now.time()
        query = """INSERT INTO weather_reports(
        city,
        country,
        temperature,
        humidity,
        wind_speed,
        weather_condition,
        search_date,
        search_time,
        validation_status
        )
        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        values=(
            city,
            country,
            temperature,
            humidity,
            wind_speed,
            weather_condition,
            search_date,
            search_time,
            "PASSED"
        )
        cursor.execute(query, values)
        conn.commit()
        print("\n Weather saved Successfully")
        logging.info(f"Weather data saved for {city}")
    except Exception as e:
        print("Database Error:",e)

    finally:
        cursor.close()
        conn.close()
def check_weather():

    global failed_validations

    city_input = input("\nEnter city: ").strip()

    if not validate_city(city_input):

        print("\nInvalid City Name!")

        failed_validations += 1

        log_validation(city_input, "FAILED")

        return

    data = get_weather(city_input)

    if not data:
        return

    city = data["location"]["name"]
    country = data["location"]["country"]
    temperature = data["current"]["temp_c"]
    humidity = data["current"]["humidity"]
    wind_speed = data["current"]["wind_kph"]
    condition = data["current"]["condition"]["text"]

    print("\n----- Weather Report -----")

    print("City :", city)
    print("Country :", country)
    print("Temperature :", temperature)
    print("Humidity :", humidity)
    print("Wind Speed :", wind_speed)
    print("Weather Condition :", condition)

    valid = validate_weather_data(
        city,
        country,
        temperature,
        humidity,
        wind_speed,
        condition
    )

    if valid:

        log_validation(city, "PASSED")

        save(data)

        print("\nWeather Saved Successfully")

    else:

        failed_validations += 1

        log_validation(city, "FAILED")

        save_invalid_record(
            city,
            country,
            temperature,
            humidity,
            wind_speed,
            condition
        )

        print("\nValidation Failed")
        print("Record Not Saved")
def view_history():
    try:
        conn=connect_db()
        cursor=conn.cursor()
        query="select * from weather_reports"
        cursor.execute(query)
        records=cursor.fetchall()
        print("\nWeather History\n")
        for row in records:
            print(row)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
def last_search():
    try:
        conn=connect_db()
        cursor=conn.cursor()
        query="""
        Select * From weather_reports
        ORDER BY id DESC
        LIMIT 1
        """
        cursor.execute (query)
        record = cursor.fetchone()
        if record:
            print("\nLast Weather Search:\n")
            print(record)
        else:
            print("\nNo weather records found")
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
def hottest_city():
    try:
        conn=connect_db()
        cursor=conn.cursor()
        query="""Select city,temperature from weather_reports 
        order by temperature desc
        limit 1"""
        cursor.execute(query)
        record=cursor.fetchone()
        if record:
            print("\nHottest City:")
            print(f"City: {record[0]}")
            print(f"Temperature: {record[1]}°C")
        else:
            print("\nNo weather records found")
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
def coldest_city():
    try:
        conn=connect_db()
        cursor=conn.cursor()
        query="""select city,temperature from weather_reports 
        order by temperature asc
        limit 1"""
        cursor.execute(query)
        record=cursor.fetchone()
        if record:
            print("\nColdest City:")
            print(f"City: {record[0]}")
            print(f"Temperature: {record[1]}°C")
        else:
            print("\nNo weather records found")
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
def search_count():
    try:
        conn=connect_db()
        cursor=conn.cursor()
        query="""select count(*) from weather_reports"""
        cursor.execute(query)
        count=cursor.fetchone()
        print("\nTotal Searches:",count[0])
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
def delete_history():
    try:
        conn=connect_db()
        cursor=conn.cursor()
        query="Delete from weather_reports"
        cursor.execute(query)
        conn.commit()
        print("\nHistory deleted Successfully!!!")
        logging.info("Weather history deleted")
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
def export_history():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
        Select city,
               temperature,
               weather_condition
        from weather_reports
        """
        cursor.execute(query)
        records = cursor.fetchall()
        with open("weather_history.txt", "w") as file:
            for row in records:
                line = f"{row[0]} | {row[1]}°C | {row[2]}\n"
                file.write(line)
        print("\nExported to weather_history.txt")
        logging.info("Weather history exported to weather_history.txt")
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

def statistics():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
        Select
        Count(*),
        MAX(temperature),
        MIN(temperature),
        AVG(temperature)
        from weather_reports
        """
        cursor.execute(query)
        result = cursor.fetchone()
        if result[0]==0:
            print("No weather records found")
        else:
            print("\n__________Statistics__________")
            print("Total Searches :", result[0])
            print("Highest Temp :", result[1])
            print("Lowest Temp :", result[2])
            print("Average Temp :", round(result[3], 2))
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

while True:
    print("----------------WEATHER DATA LOGGER SYSTEM-------------------")
    print("1. Check Weather")
    print("2. View Weather History")
    print("3. Exit")
    print("4. View Last Weather Search")
    print("5. Hottest City Checked")
    print("6. Coldest City Checked")
    print("7. Weather Search Counter")
    print("8. Delete Weather History")
    print("9. Export Weather History")
    print("10. Statistics")
    print("11. Failed Validation Count")
    choice = input("\nEnter Choice: ")
    if choice == "1":
        check_weather()
    elif choice == "2":
        view_history()
    elif choice == "3":
        logging.info("Application closed by user")
        print("\nThank You!")
        break
    elif choice == "4":
        last_search()
    elif choice == "5":
        hottest_city()
    elif choice == "6":
        coldest_city()
    elif choice == "7":
        search_count()
    elif choice == "8":
        delete_history()
    elif choice == "9":
        export_history()
    elif choice == "10":
        statistics()
    elif choice == "11":
        print(
            f"\nTotal Failed Validations : {failed_validations}"
        )
    else:
        print("\nInvalid Choice!!")
