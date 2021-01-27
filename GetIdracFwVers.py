# Python script using Redfish API to check single iDRAC firmware version
# Azat Salikhov for DELL 08/11/2020

import requests, json, sys, warnings
warnings.filterwarnings("ignore")

# Pass in iDRAC IP, username & password
try:
    idrac_ip = sys.argv[1]
    idrac_username = sys.argv[2]
    idrac_password = sys.argv[3]
except:
    print ("\n- FAIL, you must pass in these to the script:  iDRAC_IP iDRAC_username iDRAC_password")
    sys.exit()

# Point to the Redfish URI that contains the data we're looking for
url = 'https://%s/redfish/v1/Managers/iDRAC.Embedded.1' % idrac_ip

# Get the JSON with all that data
response = requests.get(url,verify=False,auth=(idrac_username,idrac_password))
systemData = response.json()

# Get the list with items in the boot order sequence
jsonString = systemData['FirmwareVersion']

# Cycle through and print the items in the list
print ("Firmware version for iDRAC at %s is: %s" % (idrac_ip, jsonString))
