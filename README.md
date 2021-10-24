# Autotrader Scraper

## Author
Remus Calugarescu

## Last Major Modification
October 23, 2021

## Purpose
This is a webscraper that searched autotrader.ca for cars of your choice. You can check options.json to change various settings for searching, currently the following settings exist.
~~~~
car_types:          The brand and then type of car put in this format as an example "toyota/corolla" or "bmw/3%20series" (spaces should be replaced with "%20")

distance:           The maximum distance in kilometeres one is willing to travel to see the car

postal_code:        The postal code to be used as the reference point for distance

max_mileage:        The maximum amount of mileage (in km) that a car can have

max_price:          The maximum price a car can have in CAD$

min_year:           The minimum year that a car needs to be

private_dealer:     The option of accepting cars with private dealers, can either be "True" or "False"
~~~~

## The file with results located in saved/scraped.txt
![Scraped](https://i.imgur.com/XLGqe1U.jpeg)

## Notable Technologies Used
- Python
- Selenium

## Setup Commands
~~~~
$ pip install -r requirements.txt
~~~~

## Notes
~~~~
-This only works on Windows for now, since I only have WSL installed for linux development, I can't run selenium in it
-A chrome window will open and the website will be scraped, this is required since if a headless instance of chrome is ran sometimes it freezes for currently unknown reasons
~~~~
