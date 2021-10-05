# Generate EXE with pyinstaller --onefile webscraper.py --hidden-import jinja2 --add-data C:\Users\RemCa\AppData\Local\Programs\Python\Python38-32\Lib\site-packages\pandas\io\formats\templates\html.tpl;pandas\io\formats\templates
import os
import os.path
import time
import json
import math
from os import system
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

# Defining method that checks if a class exists
def check_exists_by_class_name(content, class_name):
    try:
        content.find_element_by_class_name(class_name)
    except NoSuchElementException:
        return(False)
    return(True)

# Defining method that checks if an advertisement passes the requirements
def check_all_criteria(content, PRIVATE_DEALER):

    # If private dealer is disabled, return false if a car with a private dealer is found
    if PRIVATE_DEALER == "False":
        if check_exists_by_class_name(content, "private-car-en") == True:
            return(False)

    # Check other criteria such as mileage, price, and such
    if "manual" not in content.text.lower() and "mileage" in content.text.lower() and int(MAX_PRICE) >= int(str(content.find_element_by_class_name('price-amount').text).replace(',','').replace('$','')) and int(MIN_YEAR) <= int(str(content.find_element_by_class_name('result-title').text.split(' ')[0])):
        return(True)
    else:
        return(False)

# Round up to nearest thousand
def roundup(x):
    return(int(math.ceil(x / 1000.0)) * 1000)

# Print a car object from json
def print_json_car(car):
    return("[%s]   %-6s %-8s $%-7s %-12s %-13s %-6s %-20s %s\n" % (car["date"], car["year"], car["mileage"], car["price"], car["brand"], car["name"], car["dealer"], car["market_value"], car["link"])) 
    
try:
    # Setting up window and colors
    system("title "+ "Autotrader Monitor")
    color = "\033[1;31;40m"

    # Reading the options file and getting the settings
    current_dir = os.path.dirname(os.path.realpath(__file__))
    with open(current_dir + "\options.json") as file:
        data = json.load(file)
    CAR_TYPES = data["car_types"]
    DISTANCE = data["distance"]
    MAX_MILEAGE = data["max_mileage"]
    MAX_PRICE = data["max_price"]
    MIN_YEAR = data["min_year"]
    PRIVATE_DEALER = data["private_dealer"]

    # Loading the chrome driver
    print("Loading chrome driver...")
    coptions = Options()
    #coptions.add_argument('--headless')
    coptions.add_argument('--disable-gpu')
    coptions.add_argument('disable-blink-features=AutomationControlled')
    coptions.add_argument('--lang=en_US')
    coptions.add_argument('user-agent=fake-useragent')
    coptions.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(current_dir + "/chromedriver.exe", options=coptions)

    # Loading the webpages
    cars_list = []
    curr_date_time_file = str(datetime.now().strftime("%Y-%m-%d %H:%M")) 
    data_json = {}
    data_json["ads"] = []
    for car_type in CAR_TYPES:
        if PRIVATE_DEALER == "True":
            web_link = "https://www.autotrader.ca/cars/" + car_type + "/on/kitchener/?rcp=1000&rcs=0&srt=4&yRng=" + MIN_YEAR + "%2C&pRng=%2C" + MAX_PRICE + "&oRng=%2C" + MAX_MILEAGE + "&prx=" + DISTANCE + "&prv=Ontario&loc=N2E1P6&hprc=True&wcp=True&sts=New-Used&inMarket=advancedSearch"
        else:
            web_link = "https://www.autotrader.ca/cars/" + car_type + "/on/kitchener/?rcp=1000&rcs=0&srt=4&yRng=" + MIN_YEAR + "%2C&pRng=%2C" + MAX_PRICE + "&oRng=%2C" + MAX_MILEAGE + "&prx=" + DISTANCE + "&prv=Ontario&loc=N2E1P6&hprc=True&wcp=True&sts=New-Used&adtype=Dealer&inMarket=advancedSearch"

        print("\nLoading webpage for " + car_type + ": " + web_link)
        while True:
            try:
                driver.get(web_link)
                my_elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "en-ca")))
                break
            except TimeoutException:
                print("Page didn't load after 10 seconds, trying again!")
                continue
        print("Done, starting the scraping...")
        time.sleep(0.5)

        # Saving ads
        saved_ads = []
        for content in driver.find_elements_by_class_name("result-item"):
            if check_all_criteria(content, PRIVATE_DEALER) == True:
                saved_ads.append(content)
        print("Saved " + str(len(saved_ads)) + " ads")

        # Processing all saved ads and processing them into a json object
        for ad in saved_ads:
            
            # Getting a chunk of data that contains a lot of useful information for later
            car_various_data = ad.find_element_by_class_name('result-title')
            
            # Dealing with price
            car_price = ad.find_element_by_class_name('price-amount').text.replace(',','').replace('$','')

            # Dealing with above or below market value data
            if check_exists_by_class_name(ad, "price-delta-text") == True:
                car_market_value = ad.find_element_by_class_name('price-delta-text').text
                car_market_value_cost = car_market_value.split()[0]
                car_market_value_direction = car_market_value.split()[1]
                if(car_market_value_direction == "BELOW"):
                    car_market_value_direction = "B"
                else:
                    car_market_value_cost = ""
                    car_market_value_direction = ""
                car_market_value = "%s %-6s" % (car_market_value_direction, car_market_value_cost)
            else:
                car_market_value = ""

            # Dealing with dealer
            if check_exists_by_class_name(ad, "private-car-en") == True or check_exists_by_class_name(ad, "svg_privateBadge") == True:
                car_dealer = "PRIV"
            else:
                car_dealer = "DEAL"
            
            # Dealing with mileage
            car_mileage = ad.find_element_by_class_name('kms').text.split(' ')[1].replace(',','')

            # Dealing with brand
            car_brand = car_various_data.text.split(' ')[1].lower().capitalize()

            # Dealing with name
            car_name = car_various_data.text.split(' ')[2].lower().capitalize()

            # Dealing with year
            car_year = car_various_data.text.split(' ')[0]

            # Dealing with link
            car_link = str(car_various_data.get_attribute('href'))

            data_json['ads'].append({
                'date': curr_date_time_file,
                'price': car_price,
                'market_value': car_market_value,
                'dealer': car_dealer,
                'mileage': car_mileage,
                'brand': car_brand,
                'name': car_name,
                'year': car_year,
                'link': car_link,
            })

    # Checking if the old data file is empty or not
    if os.path.isfile("saved\scraped.json") == False:
        fileCreate = open(current_dir + "\saved\scraped.json", "w+")

    # Getting size of scraped.json file
    scraped_file_size = os.path.getsize("saved\scraped.json")
    if scraped_file_size == 0:
        # Creating a JSON object if the JSON file is empty
        data_json_read = {}
        data_json_read["ads"] = []
    else:
        # Reading the old data file and getting the info if the JSOn file is not empty
        with open(current_dir + "\saved\scraped.json") as file:
            data_json_read = json.load(file)

    # Looping through all cars that were just found
    data_json_out = {}
    data_json_out["ads"] = []
    num_new_cars = 0
    for car in data_json["ads"]:
        found_car = False

        # Looping through all previous cars
        for car_read in data_json_read["ads"]:

            # If a car was already found previously, append the previous car
            if car["price"] == car_read["price"] and car["mileage"] == car_read["mileage"] and car["brand"] == car_read["brand"] and car["name"] == car_read["name"] and car["year"] == car_read["year"]:
                found_car = True
                data_json_out["ads"].append(car_read)
                break

        # If a car wasn't found previously, aka it's new, append the new car
        if found_car == False:
            data_json_out["ads"].append(car)
            num_new_cars += 1

    # Removing duplicates
    for car in data_json_out["ads"]:
        for car_compare in data_json_out["ads"]:
            if car["price"] == car_compare["price"] and car["mileage"] == car_compare["mileage"] and car["brand"] == car_compare["brand"] and car["name"] == car_compare["name"] and car["year"] == car_compare["year"]:
                data_json_out["ads"].remove(car_compare)

    # Printing the data to the summary file
    printed_endl_condition = 1000
    open("saved\scraped.txt", "w").close()
    file_text = open("saved\scraped.txt", "a")

    # Sorting the lists
    data_json_out["ads"] = sorted(data_json_out["ads"], key=lambda x: x["brand"], reverse=False)
    data_json_out["ads"] = sorted(data_json_out["ads"], key=lambda x: int(x["year"]), reverse=True)
    data_json_out["ads"] = sorted(data_json_out["ads"], key=lambda x: int(x["price"]), reverse=False)

    # Looping through cars that will be printed to file
    file_text.write("[" + curr_date_time_file + "] Total of " + str(num_new_cars) + " new car ads found since last scan\n")
    for car in data_json_out["ads"]:

        # Checking if a line needs to be printed
        if int(car["price"]) > printed_endl_condition:
            file_text.write("\n--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n\n")
            printed_endl_condition = roundup(int(car["price"]))
        file_text.write(print_json_car(car))
    file_text.write("\n--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n\n")

    # Saving new JSON file
    with open("saved\scraped.json", "w") as file_out_json:
        json.dump(data_json_out, file_out_json, sort_keys=True, indent=4)

    # Ending program once everything is done
    print("\nScraping over, exiting")
    file.close()
    driver.quit()

except Exception as e:
    print("Unknown Exception", e, "caught, library error is likely")
    os.system('pause')
