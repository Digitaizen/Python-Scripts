#
# GetIdracFwVersion. Python script using Redfish API to get iDRAC's Firmware Version.
# Input:    text file with a list of iDRAC IPs.
# Output:   two text files, one with with a list of IPs and their currently installed
#           Firmware Version and an error log file.
#
# _author_ = Azat Salikhov <Azat_Salikhov@Dellteam.com>
# _version_ = 1.0
#
# Copyright (c) 2020, Dell, Inc.
#

# Pull-in libraries >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
import requests, json, sys, warnings
from datetime import datetime

warnings.filterwarnings("ignore")

# Declare variables >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
idrac_username = "root"
idrac_password = "calvin"
# Get current timestamp for dynamic log naming
cts = datetime.now().strftime("%d-%b-%Y(%H:%M:%S)")
success_log = "iDRAC_FW_Vers_log_%s.txt" % cts
error_log = "iDRAC_FW_Vers_err_log_%s.txt" % cts


# Define functions >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def writeToLog(fn, msg):
    f = open(fn, "a")
    f.write(msg)
    f.flush()
    f.close()


def getIdracFwVersion(node_ip):
    try:
        url = "https://%s/redfish/v1/Managers/iDRAC.Embedded.1" % node_ip
        response = requests.get(
            url, verify=False, auth=(idrac_username, idrac_password), timeout=10
        )
        data = response.json()
        fw_version = data["FirmwareVersion"]
        return fw_version

    except:  # catch *all* exceptions
        e = sys.exc_info()

        # Open error logfile for writing/appending and dump the output to logfile
        writeToLog(error_log, idrac_ip + ": " + str(tuple(e)) + "\n")
        return "Error on request"


# Run main logic >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Pass in a filename wih iDRAC IPs
try:
    idrac_ip_list = sys.argv[1]
except:
    print("\n- FAIL, you must pass in a valid .TXT file with a list of iDRAC IPs!")
    sys.exit()

# Open a file with iDRAC IPs
try:
    ftr = open(idrac_ip_list, "r")
except:
    print('/n-FAIL, "%s" file doesn\'t exist' % idrac_ip_list)
    sys.exit()

# Cycle through the supplied iDRAC list and run the query
for idrac_ip in ftr.readlines():
    try:
        # Clean up IP string
        idrac_ip = idrac_ip.strip("\n\r ")

        # Call function to get the iDRAC FW version via Redfish protocol
        result = getIdracFwVersion(idrac_ip)
        if result != "Error on request":
            # Open success logfile for writing/appending and dump the output to logfile
            writeToLog(success_log, idrac_ip + ", " + result + "\n")

        # Output result of the query to the console
        print(idrac_ip + ", " + result)

    except:  # catch *all* exceptions
        e = sys.exc_info()
        # Open error logfile for writing/appending and dump the output to logfile
        writeToLog(error_log, idrac_ip + ": " + str(tuple(e)) + "\n")

        print(
            idrac_ip + " -> Error inside main: ", e
        )  # (Exception Type, Exception Value, TraceBack)
