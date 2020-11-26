from urllib.request import urlopen
from urllib.error import HTTPError
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import smtplib, ssl
import time

import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow,Flow
from google.auth.transport.requests import Request
import os
import pickle

def find_other(url, tag, class_={}):  
    try:
        html = urlopen(str(url))
        bs = BeautifulSoup(html.read(), 'lxml')
    except Exception as e:
        return e

    try:
        tag = bs.find_all(str(tag),class_)
    except AttributeError as ae:
        return 'Tag was not found'
    if tag == None:
        return 'Tag is None'
    return tag

def sold_out(url):
    if find_other(url,'div',{'class':'sold-out-block'}):
        return True
    return False

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
sheet_id = '1Vf2ZCtc5Adz68M4bDo-MR_6Q8QWy_CFW6F0J4WPaSSo'
# here enter the id of your google sheet
SAMPLE_SPREADSHEET_ID_input = sheet_id
SAMPLE_RANGE_NAME = 'A1:AA1000'

def main():
    global values_input, service
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES) # here enter the name of your downloaded JSON file
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result_input = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID_input,
                                range=SAMPLE_RANGE_NAME).execute()
    values_input = result_input.get('values', [])

    if not values_input and not values_expansion:
        print('No data found.')



#retrieve price from website
def get_price(bag_url):
    if sold_out(bag_url) == False:    
        try:
            span = find_other(bag_url,'span',{'class':'price-new'})
        except:
            price = 'Price could not be retrieved. Check url'
            print(bag_url)

        try:
            price = str(span[0].get_text()).strip(' \xa0CHF 00')
            price = price.replace(',','')
            price = price.replace('.','')
            price = int(price)
            print('Item available for CHF',price)
            print(bag_url)
        except:
            price = 'Error formatting price. Check website.'
            print(bag)
    else:
        print('Item currently sold out:',bag_url)
        return 20000000
    return int(price)
    
    


#send email notification
def send_email():
    sheet_id = '1Vf2ZCtc5Adz68M4bDo-MR_6Q8QWy_CFW6F0J4WPaSSo'
    pw = 'wBJwSTP7GXK7bD7'

    port = 465  # For SSL
    password = pw

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("lv2778883@gmail.com", pw)
        # TODO: Send email here


        sender_email = "lv2778883@gmail.com"
        receiver_email = "lv2778883@gmail.com"
        message = f"""Subject: Hi there \n
        The price of {x} is currently at {price} CHF. \n \n
        The declared target price is CHF {y}"""

        # Send email here

        server.sendmail(sender_email, receiver_email, message)
        
        server.quit()

for i in range(10): 
    print('Starting script')
    main()
    df=pd.DataFrame(values_input[1:], columns=values_input[0])

    #iterate over spreadsheet values:
    bag = df['URL']
    target = df['Target']
    for x,y in zip(bag, target):
        price = int(get_price(x))
        if int(y) >= price:
            print('The declared target price is',y)
            print('Sending Email ...')
            send_email()
            print('Email sent!')
            print()
        else:
            print('No Email sent! The declared target price is',y)
            print()
    time.sleep(60*60)
