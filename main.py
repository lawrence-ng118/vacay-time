# IMPORTING ALL NEEDED LIBRARIES
import requests
import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.mouse_button import MouseButton
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import re
from datetime import date
from tkinter import *

# CREATING TKINTER WINDOW FOR INPUTS
root = Tk()
root.title('Select Inputs')

# Update List function for getting selected currencies to webscrape
selected = []
def UpdateList(var,text):
    try:
        val = int(var.get()) # If not selected it will give 0 as int, which will trigger `else` block
    except ValueError:
        val = var.get()
    if val: # if val is not empty, ie, if val is any selected value
        selected.append(text)
    else: # if val is 0 
        selected.remove(text) # Remove the corresponding text from the list

currencies = ["EUR", "USD", "GBP", "CAD", "AUD", "ALL", "DZD", "AOA", "AMD", "AZN", "BSD", "BHD", "BDT", 
    "BBD", "BYN", "BZD", "BMD", "BOB", "BAM", "BWP", "BRL", "GBP", "BND", "BGN", "BIF", "KHR", 
    "CAD", "CVE", "KYD", "XOF", "XAF", "XPF", "CLP", "CNY", "COP", "CRC", "HRK", "CUP", "CZK", 
    "DKK", "DJF", "DOP", "XCD", "EGP", "ETB", "FJD", "GMD", "GEL", "GHS", "GTQ", "GNF", 
    "HTG", "HNL", "HKD", "ISK", "INR", "IDR", "IRR", "IQD", "ILS", "JMD", "JPY", "JOD", "KZT", 
    "KES", "KRW", "KWD", "KGS", "LAK", "LBP", "LSL", "LYD", "MOP", "MKD", "MWK", "MYR", "MUR", 
    "MXN", "MDL", "MAD", "MMK", "NAD", "NPR", "ANG", "NZD", "NIO", "NGN", "NOK", "OMR", "PKR", 
    "PAB", "PYG", "PEN", "PLN", "PHP", "QAR", "RON", "RUB", "RWF", "SAR", "RSD", "SCR", "SGD", 
    "SOS", "ZAR", "LKR", "SDG", "SZL", "SEK", "CHF", "SYP", "TWD", "TZS", "THB", "TTD", "TND", 
    "TRY", "TMT", "UGX", "UAH", "AED", "UYU", "USD", "UZS", "VES", "VND", "YER", "ZMW"]

# Labels and Entries and Checboxes for: wanted currencies, original currency, and how many years back theyd want to consider
Label(root, text="Pick the currencies you wish to look at:").grid(row=0, column=1, columnspan = 8)

for idx,i in enumerate(currencies): # a for loop for making checkboxes for all currencies
    var = StringVar(value = " ")
    Checkbutton(root,text=i,variable=var,command=lambda i=i,var=var: UpdateList(var,i),onvalue=i).grid(row=(idx//10)+1,column=idx%10)
    
Label(root, text="Type out original currency from the options above (follow currency code):").grid(row=15, column=0, columnspan= 7)
from_currency_entry = Entry()
from_currency_entry.grid(row=15, column = 7, columnspan= 3)
Label(root, text= "How many years back would you like to consider? (number) (0 for current year").grid(row=16, column=0, columnspan= 7)
how_many_years_back_entry = Entry()
how_many_years_back_entry.grid(row=16, column = 7, columnspan= 3)

# function getting the data from the text boxes on original currency and how many years back
def get_data():
    global from_currency
    global how_many_years_back
    from_currency = from_currency_entry.get().upper()
    how_many_years_back = int(how_many_years_back_entry.get())
    root.destroy()

Button(root, text="Submit", command=get_data).grid(row = 17, column=0) # submit button that triggers above function

root.mainloop() # open window

# getting current year
currentdate = date.today()
current_year = int(currentdate.year)

exchange_rates = {} # dictionary containing all webscraped data

# going thru all the exchange rates
for to_currency in selected:
    history = {} # dictionary containing history of exchange rate for one currency
    if to_currency != from_currency:
        for j in range(0, how_many_years_back+1): # for loop going thru each year and getting all the dates and rates from the page
            search_year = int(current_year - j)
            link = f"https://www.exchange-rates.org/exchange-rate-history/{from_currency}-{to_currency}-{search_year}"

            # getting all relevant parts of the html code
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')
            data = soup.find_all('tr')

            # removing rows in table that are not needed
            for sflkdjasfjlk in range(0,5):
                data.pop(0)
            
            remove_this = ['<tr>', '<td>', '<span class="w">', '<span class="n">', '</span>', '</td>', '</tr>', '<span class="nowrap">', '<tr class="odd">', '\n']
            for i in data: # going thru all rows containing the data
                try:
                    string_i = str(i)
                    # removing tags
                    for eww in remove_this:
                        string_i = string_i.replace(eww,"")
    
                    # REMOVED EVERTHING EXCEPT THE <A>
                    if "</a>" in string_i:
                        string_i = string_i.replace("</a>", "")
                        string_i = string_i[string_i.index(">")+1:]
                        i_hate_this = string_i[string_i.index("<"):string_i.index(">")+1]
                        string_i = string_i.replace(i_hate_this,"")
                   
                    # FORMAT THE RAW LINE
                    date = string_i[string_i.index(str(search_year))+4:string_i.index(str("1 "+str(from_currency)))]
                    rate = string_i[(string_i.index(date)+len(date)):string_i.index(to_currency)+len(to_currency)]

                    # appending to history dictionary
                    history[str(date)] = rate.replace("1 PHP = ", "").replace(to_currency, "")
                except: # to account for rows that dont have exchange rates in them
                    pass

    if to_currency != from_currency: # to account for when it will accidentally try to add the original currency to the exchange rates dictionary
        exchange_rates[to_currency] = history

# print(exchange_rates)

pd.options.display.max_rows = 9999 # display all rows
df = pd.DataFrame(exchange_rates) # create dataframe

# ARRANGING TABLE BY DATE AND MAKING THE DATE THE INDEX AS WELL
df.reset_index(inplace=True, names="date") # making date a normal column to allow for converting to standardized format
df['date'] = pd.to_datetime(df['date']) # converting to consistent format
df.sort_values(by=['date'], inplace=True, ascending=True) # arranging table by date
df = df.set_index('date') # making the date the index

# filling in missing dates
start = df.index[0].date()
end = df.index[len(df)-1].date()
new_dates = pd.date_range(start=start, end=end, freq='D') # creating range of dates from the earliest date to latest date
df = df.reindex(new_dates) # reindexing using all dates including those that were missing
df = df.rename_axis('date') # naming the index "date"

# interpolating for missing data values
for to_currency in selected:
    df[to_currency] = pd.to_numeric(df[to_currency], errors='coerce') # converting each column to a numeric insetad of object type column
df = df.interpolate()

# df
from datetime import date
currentdate = date.today()
current_year = currentdate.year
current_month = currentdate.month
current_day = currentdate.day

data_dictionary_means = {} # dictionary for all important mean points

for monthshift in [1, 3, 6, 9]: # past 1, 3, 6, 9 years
    if (monthshift >= current_month) & (how_many_years_back > 0): # check if needs to go back one year when going back x months
        # adds past x months : mean of all data since date x months ago to dictionary
        data_dictionary_means['Past '+str(monthshift)+' Month(s)'] = dict(df[df.index.date > date(current_year-1, current_month-(monthshift-12), current_day-1)].mean())
        # print('Past '+str(monthshift)+' Month(s)', date(current_year-1, current_month-(monthshift-12), current_day-1))
    elif (monthshift < current_month): # same thing here, just no need to subtract 1 from the current year
        data_dictionary_means['Past '+str(monthshift)+' Month(s)'] = dict(df[df.index.date > date(current_year, current_month-monthshift, current_day-1)].mean())
        # print('Past '+str(monthshift)+' Month(s)', date(current_year, current_month-monthshift, current_day-1))
        
if (how_many_years_back > 0): # check if its possible to output past 365 days data
    yearshift = 1
    while yearshift <= how_many_years_back: # keep outputting past x year(s) until can no longer access older data
        data_dictionary_means['Past '+str(yearshift)+' Year(s)'] = dict(df[df.index.date > date(current_year-yearshift, current_month, current_day-1)].mean())
        # print('Past '+str(yearshift)+' Year(s)', date(current_year-yearshift, current_month, current_day-1))
        yearshift += 1

data_dictionary_means["Since "+str(start)] = dict(df.mean()) # getting the mean of all the data in the dataframe

data_dictionary_mins = {} # dictionary for all important mean points

for monthshift in [1, 3, 6, 9]: # past 1, 3, 6, 9 years
    if (monthshift >= current_month) & (how_many_years_back > 0): # check if needs to go back one year when going back x months
        # adds past x months : mean of all data since date x months ago to dictionary
        data_dictionary_mins['Past '+str(monthshift)+' Month(s)'] = dict(df[df.index.date > date(current_year-1, current_month-(monthshift-12), current_day-1)].min())
        # print('Past '+str(monthshift)+' Month(s)', date(current_year-1, current_month-(monthshift-12), current_day-1))
    elif (monthshift < current_month): # same thing here, just no need to subtract 1 from the current year
        data_dictionary_mins['Past '+str(monthshift)+' Month(s)'] = dict(df[df.index.date > date(current_year, current_month-monthshift, current_day-1)].min())
        # print('Past '+str(monthshift)+' Month(s)', date(current_year, current_month-monthshift, current_day-1))
        
if (how_many_years_back > 0): # check if its possible to output past 365 days data
    yearshift = 1
    while yearshift <= how_many_years_back: # keep outputting past x year(s) until can no longer access older data
        data_dictionary_mins['Past '+str(yearshift)+' Year(s)'] = dict(df[df.index.date > date(current_year-yearshift, current_month, current_day-1)].min())
        # print('Past '+str(yearshift)+' Year(s)', date(current_year-yearshift, current_month, current_day-1))
        yearshift += 1

data_dictionary_mins["Since "+str(start)] = dict(df.min()) # getting the mean of all the data in the dataframe

data_dictionary_maxs = {} # dictionary for all important mean points

for monthshift in [1, 3, 6, 9]: # past 1, 3, 6, 9 years
    if (monthshift >= current_month) & (how_many_years_back > 0): # check if needs to go back one year when going back x months
        # adds past x months : mean of all data since date x months ago to dictionary
        data_dictionary_maxs['Past '+str(monthshift)+' Month(s)'] = dict(df[df.index.date > date(current_year-1, current_month-(monthshift-12), current_day-1)].max())
        # print('Past '+str(monthshift)+' Month(s)', date(current_year-1, current_month-(monthshift-12), current_day-1))
    elif (monthshift < current_month): # same thing here, just no need to subtract 1 from the current year
        data_dictionary_maxs['Past '+str(monthshift)+' Month(s)'] = dict(df[df.index.date > date(current_year, current_month-monthshift, current_day-1)].max())
        # print('Past '+str(monthshift)+' Month(s)', date(current_year, current_month-monthshift, current_day-1))
        
if (how_many_years_back > 0): # check if its possible to output past 365 days data
    yearshift = 1
    while yearshift <= how_many_years_back: # keep outputting past x year(s) until can no longer access older data
        data_dictionary_maxs['Past '+str(yearshift)+' Year(s)'] = dict(df[df.index.date > date(current_year-yearshift, current_month, current_day-1)].max())
        # print('Past '+str(yearshift)+' Year(s)', date(current_year-yearshift, current_month, current_day-1))
        yearshift += 1

data_dictionary_maxs["Since "+str(start)] = dict(df.max()) # getting the mean of all the data in the dataframe
