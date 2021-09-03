# Script to ingest an excel .xlsx and upload license plates of interest to Verkada Command
# depends on argparse1.1, numpy1.20.3, pandas1.3.2, requests2.26.0, openpyxl3.0.7
#Python3.9.5
import sys, argparse
import time
from typing import IO
import numpy as np
from numpy.core.numeric import ones_like
import pandas as pd
from pandas.core.arrays.string_ import StringArray
import requests

parser = argparse.ArgumentParser(description="script to upload plates as license plates of interest in Verkada Command.")
parser.add_argument('-i', '--inputfile', required=True, help="Excel file to take plates from (Make sure descriptions are in the A column and the license plates are in the B column)", dest= 'inputFile')
parser.add_argument('-o', '--orgid', required=True, help="Verkada Command Organization ID", dest= 'orgId')
parser.add_argument('-t', '--token', required=True, help="Verkada Command API Token", dest= 'token')
parser.add_argument('-d', '--delete', required=False, help="True/False toggle if you want to delete plates from the file", dest= 'deleteToggle')

class argValues:
    pass

args = parser.parse_args(namespace=argValues)

baseUrl = 'https://api.verkada.com'
endpoint = '/orgs/' + argValues.orgId + '/license_plate_of_interest'

url = baseUrl + endpoint

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "x-api-key": argValues.token
}

plates = pd.read_excel(io = argValues.inputFile, usecols= 'A:B', engine= "openpyxl")

plates = plates.to_numpy(np.str_)

#strip out the - character from the plates
plates = np.char.replace(plates, '-', '')

for item in plates:
    plateDescription = item[0]
    plateNumber = item[1]
    payload = {
        "licensePlate": plateNumber,
        "description": plateDescription
    }
    if argValues.deleteToggle != 'True':
        fail= True
        failCount = 0
        while failCount < 3:
            #do api call and wait 1/4 of a second so we don't exceed the rate-limit
            response = requests.request("POST", url, json=payload, headers=headers)
            if not response.ok:
                failCount+=1
                time.sleep(0.25)
                print('retrying to upload licence plate:' + ' ' + plateNumber + '\n')
            else:
                print('successfully uploaded license plate: ' + plateNumber + '\n')
                fail = False
                break
        if fail:
            print('FAILED TO UPLOAD LICENSE PLATE: ' + plateNumber + ' WITH STATUS CODE:' + ' ' + response.status_code + '\n')


        #below request is for deleting the plates
    else:
        
        fail= True
        failCount = 0
        while failCount < 3:
            #do api call and wait 1/4 of a second so we don't exceed the rate-limit
            response = requests.request("DELETE", url + '/' + plateNumber, headers=headers)
            if not response.ok:
                failCount+=1
                time.sleep(0.25)
                print('retrying to delete licence plate:' + ' ' + plateNumber + '\n')
            else:
                print('successfully deleted license plate: ' + plateNumber + '\n')
                fail = False
                break
        if fail:
            print('FAILED TO DELETE LICENSE PLATE: ' + plateNumber + ' WITH STATUS CODE:' + ' ' + str(response.status_code) + '\n')

    time.sleep(0.25)




