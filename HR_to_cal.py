#!/usr/bin/env python3

import requests
import json
from pprint import pprint
import csv

# Call to PeopleHR API to get data
url = 'https://api.peoplehr.net/Employee'
payload={'APIKey':'<< Your API token here >>',
	'Action':'GetAllEmployeeDetail',
	'IncludeLeavers':'false'}

# You have to call as json, output is "inbound"
r = requests.post(url, json=payload)
results = r.json()['Results']

# Data we need
permitted = {"EmployeeId", "FirstName", "LastName", "StartDate", "DateOfBirth"}

#From results list take DisplayValue that is listed in permitted
list_of_people = [{key:x[key]['DisplayValue'] for key in permitted} for x in results]



#list_of_people
#pprint(_)
