#!/usr/bin/env python3

from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from pprint import pprint
import requests
import json
import csv

# Read file with API key
with open('peopleHR_APIkey.txt', 'r') as fp:
    apikey = fp.read().strip()

# Call to PeopleHR API to get data
url = 'https://api.peoplehr.net/Employee'
payload = {'APIKey': apikey,
	'Action':'GetAllEmployeeDetail',
	'IncludeLeavers':'false'}

# You have to call as json, output is "inbound"
inbound = requests.post(url, json=payload)
results = inbound.json()['Result']

# Data we need
permitted = {"EmployeeId", "FirstName", "LastName", "StartDate", "DateOfBirth"}

#From results list take DisplayValue that is listed in permitted
list_of_people = [{key:x[key]['DisplayValue'] for key in permitted} for x in results]

# Now we are starting with callendar


# To have a look un-comment next line
pprint(list_of_people)
