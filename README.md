# Autotrader Scraper

## Author
Remus Calugarescu

## Last Major Modification
October 5, 2021

## Purpose
This is a webscraper that searched autotrader.ca for cars of your choice. You can check options.json to change various settings for searching, currently the following settings exist, Currently the distance calculation is relative to Kitchener, Ontario, Canada since that's where my friends and I live
~~~~
car_types:      The brand and then type of car put in this format as an example "toyota/corolla" or "bmw/3%20series" (spaces should be replaced with "%20")

distance:       The maximum distance in kilometeres one is willing to travel from postal code N2E1P6 to see the car

max_mileage:    The maximum amount of mileage (in km) that a car can have

max_price:      The maximum price a car can have in CAD$

min_year:       The minimum year that a car needs to be

private_dealer: The option of accepting cars with private dealers, can either be "True" or "False"
~~~~

![Scraped]()

## Notable Technologies Used
- Python
- Selenium

## Setup Commands
~~~~
NOTE: This only works on Windows for now, since I only have WSL installed for linux development, I can't run selenium in it
$ pip install -r requirements.txt
~~~~
