# New gumtree scraper.

# Imports
import requests
import re
from time import sleep
from datetime import datetime, timedelta
from twilio.rest import Client
from bs4 import BeautifulSoup

# Twilio Account
account_sid = 'AC14ebd7b3f9e3ce99eafb3cb573d6219f'
auth_token = '2f00faf95eae5f9eec6d7fde21d2df41'

client = Client(account_sid, auth_token)

# URLS and Headers
headers = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
}
macbook_url = 'https://www.gumtree.co.za/s-computers-laptops/western-cape/v1c9199l3100001p1?q=macbook&st=ownr'
ipad_url = 'https://www.gumtree.co.za/s-electronics/western-cape/v1c9178l3100001p1?q=ipad&st=ownr'
iphone_url = 'https://www.gumtree.co.za/s-cell-phones-accessories/western-cape/v1c9198l3100001p1?q=iphone&st=ownr'
tv_url = 'https://www.gumtree.co.za/s-tvs-displays-dvd-s/western-cape/v1c9202l3100001p1?q=tv&st=ownr'

# Variable declaration and initialisation
active = True
seen = []
hourly_check = "Check"

# MacBook Settings
class MacBookSettings():

    item_list = ['macbook', 'mac book', 'imac']

    price_target = {
        'macbook': 100000
    }

# iPhone Settings
class iPhoneSettings():

    item_list = ['iphone 7', 'iphone 6s', 'iphone 5s', 'iphone se', 'iphone 8', 'iphone x', 'iphone xs', 'iphone 11' 'iphone 6splus', 'iphone 6s plus', 'iphone 6s+', 'iphone 6s +', 'iphone 6plus', 'iphone 6 plus', 'iphone 6+', 'iphone 6 +', 'iphone 7plus', 'iphone 7 plus', 'iphone 7+', 'iphone 7 +', 'iphone 8plus', 'iphone 8 plus', 'iphone 8+', 'iphone 8 +']

    price_target = {
        'iphone 7': 3000,
        'iphone 6s': 1900,
        'iphone 5s': 600,
        'iphone se': 1300,
        'iphone 8': 4000,
        'iphone x': 6800,
        'iphone xs': 7000,
        'iphone 11': 10000,
        'iphone 6s plus': 2300,
        'iphone 6 plus': 2000,
        'iphone 7 plus': 4000,
        'iphone 8 plus': 6000
    }

# TV Settings
class TVSettings():

    item_list = ['tv']

    price_target = {
        'tv': 1500
    }

# iPad Settings
class iPadSettings():

    item_list = ['ipad']

    price_target = {
        'ipad': 1000
    }

# Monitor Settings
class MonitorSettings():

    pass

# Apple Watch monitors
class AppleWatchSettings():
    pass

# Check which item is in the title
def check_item(word, lst):
  return (x for x in lst if x in word)

# Validate the phone
def validate_iphone(title, price, time, settings):

    item = ''

    banned_words = ['buying', 'wanted' , 'looking', 'charger']
    time_limit = 8

    for x in check_item(title, settings.item_list):
        item = x
        # If item has plus, make sure item is in correct format
        if '6s plus' in item or '6s +' in item:
            item = item[:9] + ' plus'
        elif 'plus' in item or '+' in item:
            item = item[:8] + ' plus'

    # If the item was not found, return.
    if item == '':
        return

    # Boolean return logic
    if price == 'Contact for price / Negotiable':
        return True
    elif (int(time.group()) <= (time_limit)) and (any(x not in title for x in banned_words)) and (int(price) <= settings.price_target[item]):
        return True
    else:
        return False

# Validate the Macbook
def validate_macbook(title, price, time, settings):

    # Edge check to make sure it's a macbook
    if not any(x in title for x in settings.item_list):
        return False

    item = 'macbook'
    banned_words = ['buying', 'wanted' , 'looking', 'charger']
    time_limit = 8

    print(item)
    print(price)

    # Boolean return logic
    if price == 'Contact for price / Negotiable':
        return True
    elif (int(time.group()) <= (time_limit)) and (any(x not in title for x in banned_words)) and (int(price) <= settings.price_target[item]):
        return True
    else:
        return False

# Validate the iPad
def validate_ipad(title, price, time, settings):

    # Edge check to make sure it's a macbook
    if not any(x in title for x in settings.item_list):
        return False

    item = 'ipad'
    banned_words = ['buying', 'wanted' , 'looking', 'charger', 'screen protector']
    time_limit = 8

    # Boolean return logic
    if price == 'Contact for price / Negotiable':
        return True
    elif (int(time.group()) <= (time_limit)) and (any(x not in title for x in banned_words)) and (int(price) <= settings.price_target[item]):
        return True
    else:
        return False

# Validate the TV
def validate_tv(title, price, time, settings):

    # Edge check to make sure it's a macbook
    if not any(x in title for x in settings.item_list):
        return False

    item = 'tv'
    banned_words = ['buying', 'wanted' , 'looking', 'charger', 'screen protector', 'dstv']
    time_limit = 8

    # Boolean return logic
    if price == 'Contact for price / Negotiable':
        return True
    elif (int(time.group()) <= (time_limit)) and (any(x not in title for x in banned_words)) and (int(price) <= settings.price_target[item]):
        return True
    else:
        return False

# Sending the message using Twilio
def send_message(body):

    text_body = body
    message = client.messages.create(
                                from_='whatsapp:+14155238886',
                                body= text_body,
                                # to='whatsapp:+27670335474'
                                to= 'whatsapp:+27787871402'
                            )
    print('message has been sent.')

# Get the page requested
def get_soup(url):

    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, "lxml")

    return soup

# Scrape MacBook URL
def scrape_mac():

    soup = get_soup(macbook_url)
    settings = MacBookSettings()

    # Grab Info and Edge check
    title = soup.select('.view .title')[0].getText().lower()

    ## Dealing with seen iPhones (Edge Case)
    if title in seen:
        
        print("Seen Macbook")
        return
    else:
        seen.append(title)

    price = soup.select('.view .price')[0].getText().strip()
    location = soup.select('.view .location-date > span')[0].getText()
    time_ago = soup.select('.view .location-date > span')[1].getText()
    url_inner =  "https://www.gumtree.co.za" + soup.select('.view .related-ad-title')[0]['href']
    text_body = title + '\n' + price.strip() + '\n' + location + '\n' + time_ago + '\n' + url_inner

    # Uncomment for testing
    # print(title)
    # print(price)
    # print(location)
    # print(time_ago)
    # print(url_inner)

    # Formatting time and Price
    if 'hrs ago' not in time_ago:
        time_ago_value = re.search(r'\d+', time_ago)
    else:
        time_ago_value = None

    if price != 'Contact for Price' and price != 'Negotiable' and price != 'Swap/Trade':
        price_value = re.search(r'\d+,\d+', price)
        if price_value == None:
            price_value = re.search(r'\d+', price)
        price_value_text = price_value.group().replace(',', '')
    else:
        price_value_text = 'Contact for price / Negotiable'

    if time_ago_value:
        if validate_macbook(title, price_value_text, time_ago_value, settings):
            print('Validated')
            send_message(text_body)
        else:
            print('Does not meet requirements.')
    else:
        print('Too long ago (Hours)')

# Scrape iPhones URL
def scrape_iphone():

    soup = get_soup(iphone_url)
    settings = iPhoneSettings()

    # Grab Info and Edge check
    title = soup.select('.view .title')[0].getText().lower()

    ## Dealing with seen iPhones (Edge Case)
    if title in seen:
        print("Seen iPhone")
        return
    else:
        seen.append(title)

    price = soup.select('.view .price')[0].getText().strip()
    location = soup.select('.view .location-date > span')[0].getText()
    time_ago = soup.select('.view .location-date > span')[1].getText()
    url_inner =  "https://www.gumtree.co.za" + soup.select('.view .related-ad-title')[0]['href']
    text_body = title + '\n' + price.strip() + '\n' + location + '\n' + time_ago + '\n' + url_inner

    # Uncomment for testing
    # print(title)
    # print(price)
    # print(location)
    # print(time_ago)
    # print(url_inner)

    # Formatting time and Price
    if 'hrs ago' not in time_ago:
        time_ago_value = re.search(r'\d+', time_ago)
    else:
        time_ago_value = None

    if price != 'Contact for Price' and price != 'Negotiable' and price != 'Swap/Trade':
        price_value = re.search(r'\d+,\d+', price)
        if price_value == None:
            price_value = re.search(r'\d+', price)
        price_value_text = price_value.group().replace(',', '')
    else:
        price_value_text = 'Contact for price / Negotiable'

    if time_ago_value:
        if validate_iphone(title, price_value_text, time_ago_value, settings):
            print('Validated')
            send_message(text_body)
        else:
            print('Does not meet requirements.')
    else:
        print('Too long ago (Hours)')

# Scrape TV URL
def scrape_tv():

    soup = get_soup(tv_url)
    settings = TVSettings()

    # Grab Info and Edge check
    title = soup.select('.view .title')[0].getText().lower()

    ## Dealing with seen iPhones (Edge Case)
    if title in seen:
        print("Seen TV")
        return
    else:
        seen.append(title)

    price = soup.select('.view .price')[0].getText().strip()
    location = soup.select('.view .location-date > span')[0].getText()
    time_ago = soup.select('.view .location-date > span')[1].getText()
    url_inner =  "https://www.gumtree.co.za" + soup.select('.view .related-ad-title')[0]['href']
    text_body = title + '\n' + price.strip() + '\n' + location + '\n' + time_ago + '\n' + url_inner

    # Formatting time and Price
    if 'hrs ago' not in time_ago:
        time_ago_value = re.search(r'\d+', time_ago)
    else:
        time_ago_value = None

    if price != 'Contact for Price' and price != 'Negotiable' and price != 'Swap/Trade':
        price_value = re.search(r'\d+,\d+', price)
        if price_value == None:
            price_value = re.search(r'\d+', price)
        price_value_text = price_value.group().replace(',', '')
    else:
        price_value_text = 'Contact for price / Negotiable'

    if time_ago_value:
        if validate_tv(title, price_value_text, time_ago_value, settings):
            print('Validated')
            send_message(text_body)
        else:
            print('Does not meet requirements.')
    else:
        print('Too long ago by hours')

    # Uncomment for testing
    # print(title)
    # print(price)
    # print(location)
    # print(time_ago)
    # print(url_inner)

# Scrape ipad URL
def scrape_ipad():

    soup = get_soup(ipad_url)
    settings = iPadSettings()

    # Grab Info and Edge check
    title = soup.select('.view .title')[0].getText().lower()

    ## Dealing with seen iPhones (Edge Case)
    if title in seen:
        print("Seen iPad")
        return
    else:
        seen.append(title)

    price = soup.select('.view .price')[0].getText().strip()
    location = soup.select('.view .location-date > span')[0].getText()
    time_ago = soup.select('.view .location-date > span')[1].getText()
    url_inner =  "https://www.gumtree.co.za" + soup.select('.view .related-ad-title')[0]['href']
    text_body = title + '\n' + price.strip() + '\n' + location + '\n' + time_ago + '\n' + url_inner

    # Uncomment for testing
    # print(title)
    # print(price)
    # print(location)
    # print(time_ago)
    # print(url_inner)

    # Formatting time and Price
    if 'hrs ago' not in time_ago:
        time_ago_value = re.search(r'\d+', time_ago)
    else:
        time_ago_value = None

    if price != 'Contact for Price' and price != 'Negotiable' and price != 'Swap/Trade':
        price_value = re.search(r'\d+,\d+', price)
        if price_value == None:
            price_value = re.search(r'\d+', price)
        price_value_text = price_value.group().replace(',', '')
    else:
        price_value_text = 'Contact for price / Negotiable'

    if time_ago_value:
        if validate_ipad(title, price_value_text, time_ago_value, settings):
            print('Validated')
            send_message(text_body)
        else:
            print('Does not meet requirements.')
    else:
        print('Too long ago by hours')

# Main program
def run():

    time = datetime.now()

    while active:
        scrape_iphone()
        scrape_mac()
        scrape_tv()
        scrape_ipad()
        if (datetime.now().minute == 00) and (datetime.now().second <= 20):
            send_message(hourly_check)
        if datetime.now() > (time + timedelta(minutes=10)):
            seen = []
            time = datetime.now()
        sleep(20)

# Run the program
run()