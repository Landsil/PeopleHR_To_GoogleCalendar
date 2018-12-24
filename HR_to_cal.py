import requests
import json

# Call to PeopleHR API to get data
url = 'https://api.peoplehr.net/Employee'
payload={'APIKey':'<< Your API token here >>',
	'Action':'GetAllEmployeeDetail',
	'IncludeLeavers':'false'}

 You have to call as json, output is "inbound"
inbound = requests.post(url, json=payload)

# Data we need
permitted = {"EmployeeId", "FirstName", "LastName", "StartDate", "DateOfBirth"}

existing.update((key, val) for (key, val) in inbound.items() if key in permitted)



#inbound.json()
