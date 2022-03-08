# Generate EXE with pyinstaller --onefile webscraper.py --hidden-import jinja2 --add-data C:\Users\RemCa\AppData\Local\Programs\Python\Python38-32\Lib\site-packages\pandas\io\formats\templates\html.tpl;pandas\io\formats\templates
import os
import os.path
import json
import math
import smtplib
import ssl
from os import system
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

RED = '\033[1;31m'
GREEN = '\033[1;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[1;34m'

# Method that colors a string and returns it
def color_str(string, color):
   colored_string = color + string + '\033[0m'
   return colored_string

# Defining method that checks if a class exists
def check_exists_by_class_name(content, class_name):
   try:
      content.find_element_by_class_name(class_name)
   except NoSuchElementException:
      return(False)
   return(True)

# Defining method that checks if an advertisement passes the requirements
def check_all_criteria(content, PRIVATE_DEALER, MAX_PRICE, MIN_YEAR):
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

# Constructing the saved ads list
def construct_saved_ads(saved_ads, content, PRIVATE_DEALER, MAX_PRICE, MIN_YEAR ):
   if check_all_criteria(content, PRIVATE_DEALER, MAX_PRICE, MIN_YEAR) == True:
      saved_ads.append(content)

# Processing sthe ads list
def process_ad(data_json, ad, curr_date_time_file):
   # Getting a chunk of data that contains a lot of useful information for later
   car_various_data = ad.find_element_by_class_name('result-title')

   # Dealing with price
   car_price = ad.find_element_by_class_name('price-amount').text.replace(',','').replace('$','')

   # Dealing with above or below market value data
   if check_exists_by_class_name(ad, "price-delta-text") == True:
      car_market_value = ad.find_element_by_class_name('price-delta-text').text
      car_market_value_cost = car_market_value.split()[0].replace(',', '').replace('$', '')
      car_market_value_direction = car_market_value.split()[1]
      car_market_value_percent = str(float("{:.2f}".format((float(car_market_value_cost) / (float(car_price) + float(car_market_value_cost))) * 100)))
      if(car_market_value_direction == "BELOW"):
         car_market_value_cost = "$" + car_market_value_cost
         car_market_value_direction = "B"
         car_market_value_percent = "%" + car_market_value_percent
      else:
         car_market_value_cost = ""
         car_market_value_direction = ""
         car_market_value_percent = ""
      car_market_value = "%s %-7s %s" % (car_market_value_direction, car_market_value_cost, car_market_value_percent)
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

if __name__ == '__main__':
   try:
      # Setting up window and colors
      system("title "+ "Autotrader Scraper")

      # Reading the options file and getting the settings
      current_dir = os.path.dirname(os.path.realpath(__file__))
      with open(current_dir + "\options\options.json") as file:
         data = json.load(file)
      CAR_TYPES = data["car_types"]
      DISTANCE = data["distance"]
      POSTAL_CODE = data["postal_code"]
      MAX_MILEAGE = data["max_mileage"]
      MAX_PRICE = data["max_price"]
      MIN_YEAR = data["min_year"]
      PRIVATE_DEALER = data["private_dealer"]
      BELOW_THRESHOLD = data["below_threshold"]
      LOOP_AMOUNT = data["loop_amount"]

      # Reading the credentials file to get email login creds
      with open(current_dir + "\options\credentials.json") as file:
         data = json.load(file)
      EMAIL_USERNAME = data["email_username"]
      EMAIL_PASSWORD = data["email_password"]
      EMAIL_RECEIVERS = data["email_receivers"]

      # Looping, looking for new cars
      for i in range(int(LOOP_AMOUNT)):
         
         # Loading the chrome driver and its settings
         print("Loading chrome driver...")
         coptions = Options()
         coptions.add_argument('--disable-gpu')
         coptions.add_argument('disable-blink-features=AutomationControlled')
         coptions.add_argument('--lang=en_US')
         coptions.add_argument('user-agent=fake-useragent')
         coptions.add_experimental_option('excludeSwitches', ['enable-logging'])
         driver = webdriver.Chrome(current_dir + "/chromedriver.exe", options=coptions)

         # Getting the current date and time and creating a storage structure
         curr_date_time_file = str(datetime.now().strftime("%Y-%m-%d %H:%M"))
         data_json = {}
         data_json["ads"] = []

         # Looping through all the different car types, checking the page for all cars of that type, and extracting cars that fit the criteria
         for index in range(len(CAR_TYPES)):
            car_type = CAR_TYPES[index]

            # Checking whether private dealers should be included or excluded in the search from options.json
            if PRIVATE_DEALER == "True":
               web_link = "https://www.autotrader.ca/cars/" + car_type + "/?rcp=1000&rcs=0&srt=4&yRng=" + MIN_YEAR + "%2C&pRng=%2C" + MAX_PRICE + "&oRng=%2C" + MAX_MILEAGE + "&prx=" + DISTANCE + "&loc=" + POSTAL_CODE + "&hprc=True&wcp=True&sts=New-Used&inMarket=advancedSearch"
            else:
               web_link = "https://www.autotrader.ca/cars/" + car_type + "/?rcp=1000&rcs=0&srt=4&yRng=" + MIN_YEAR + "%2C&pRng=%2C" + MAX_PRICE + "&oRng=%2C" + MAX_MILEAGE + "&prx=" + DISTANCE + "&loc=" + POSTAL_CODE + "&hprc=True&wcp=True&sts=New-Used&adtype=Dealer&inMarket=advancedSearch"
            print("\nLoading webpage " + color_str(str(index+1) + "/" + str(len(CAR_TYPES)), GREEN) + " for " + car_type + ": " + web_link)

            # Waiting 10 seconds to load the page, if it doesn't load then attempt a reload
            while True:
               try:
                  driver.get(web_link)
                  WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "en-ca")))
                  break
               except TimeoutException:
                  print(color_str("Page didn't load after 10 seconds, trying again!", RED))
                  continue
            print("Done loading page, saving ads...")

            # Saving ads
            all_elements = driver.find_elements_by_class_name("result-item")

            # Determining which ads fit the criteria and save them
            saved_ads = []
            for content in all_elements:
               construct_saved_ads(saved_ads, content, PRIVATE_DEALER, MAX_PRICE, MIN_YEAR,)
            print("Saved " + color_str(str(len(saved_ads)), GREEN) + " ads, processing them")

            # Processing all saved into a json object that will be used for file output later
            for ad in saved_ads:
               process_ad(data_json, ad, curr_date_time_file)
            print("Done processing the ads into json")

         # Checking if the old data file is empty or not
         if os.path.isfile("saved\scraped.json") == False:
            file_create = open(current_dir + "\saved\scraped.json", "w+")

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
            found_once = False
            for car_compare in data_json_out["ads"]:
               if car["price"] == car_compare["price"] and car["mileage"] == car_compare["mileage"] and car["brand"] == car_compare["brand"] and car["name"] == car_compare["name"] and car["year"] == car_compare["year"]:
                  if found_once == True:
                     data_json_out["ads"].remove(car_compare)
                  found_once = True
                  
         # Sorting the lists
         data_json_out["ads"] = sorted(data_json_out["ads"], key=lambda x: x["brand"], reverse=False)
         data_json_out["ads"] = sorted(data_json_out["ads"], key=lambda x: int(x["year"]), reverse=True)
         data_json_out["ads"] = sorted(data_json_out["ads"], key=lambda x: int(x["price"]), reverse=False)
         data_json_out_best = {}
         data_json_out_best["ads"] = []

         # Printing the data to the summary files
         printed_endl_condition = 1000
         open("saved\scraped.txt", "w").close()
         open("saved\scrapedbest.txt", "w").close()
         file_text = open("saved\scraped.txt", "a")
         file_text_best = open("saved\scrapedbest.txt", "a")

         # Looping through cars that will be printed to file
         file_text.write("[" + curr_date_time_file + "] Total of " + str(num_new_cars) + " new car ads found since last scan\n")
         for car in data_json_out["ads"]:
            cur_market_value_percent = len(str.split(car["market_value"])) != 0 and float(str.split(car["market_value"])[-1].replace('%',''))

            # Checking if a line needs to be printed, and printing it if it does
            if int(car["price"]) > printed_endl_condition:
               printed_endl_condition = roundup(int(car["price"]))
               file_text.write("\n--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n\n")

            # Printing data to file
            file_text.write(print_json_car(car))
            if cur_market_value_percent >= float(BELOW_THRESHOLD):
               data_json_out_best["ads"].append(car)
         file_text.write("\n--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n\n")

         # Sorting the best deals data
         data_json_out_best["ads"] = sorted(data_json_out_best["ads"], key=lambda x: x["brand"], reverse=False)
         data_json_out_best["ads"] = sorted(data_json_out_best["ads"], key=lambda x: int(x["year"]), reverse=True)
         data_json_out_best["ads"] = sorted(data_json_out_best["ads"], key=lambda x: int(x["price"]), reverse=False)
         data_json_out_best["ads"] = sorted(data_json_out_best["ads"], key=lambda x: float(str.split(x["market_value"])[-1].replace('%','')), reverse=True)
         file_text_best.write("\n--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n\n")

         # Printing data to file
         for car in data_json_out_best["ads"]:
            file_text_best.write(print_json_car(car))
         file_text_best.write("\n--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n\n")

         # Saving new JSON file
         with open("saved\scraped.json", "w") as file_out_json:
            json.dump(data_json_out, file_out_json, sort_keys=True, indent=4)

         # Ending program once everything is done
         print("\nScraping over, exiting")
         file.close()
         file_text.close()
         file_text_best.close()
         driver.quit()

         # Initialize email stuff
         sender_pass = EMAIL_PASSWORD
         sender_email = EMAIL_USERNAME
         receiver_emails = EMAIL_RECEIVERS
         context = ssl.create_default_context()

         # Generating the message
         counter = 0
         for car in data_json_out_best["ads"]:
            if car["date"] == curr_date_time_file:
               counter += 1

         # Sending email if some new good deals were found
         if counter != 0:
            message = "Subject: " + str(counter) + " new deals\n\n"
            message += "Minimum threshhold: " + str(BELOW_THRESHOLD) + "%\n"
            for car in data_json_out_best["ads"]:
               if car["date"] == curr_date_time_file:
                  message += print_json_car(car) + "\n\n\n"

            # Send the emails to receivers
            for current_email in receiver_emails:
               with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                  server.login(sender_email, sender_pass)
                  server.sendmail(sender_email, current_email, message)
            print(color_str(str(counter) + " new cars found, sent an email!"), BLUE)
         else:
            print(color_str("No new cars found", BLUE))

   except Exception as e:
      print("Unknown Exception", e, "caught, library error is likely")
      try:
         driver.quit()
      finally:
         os.system('pause')
