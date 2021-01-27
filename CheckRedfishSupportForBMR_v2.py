#
# CheckRedfishSupportForBMR.
# Python script using Redfish API with OEM extension to check iDRAC's support
# for Redfish BMR (Bare Metal Restore / ISO Boot) support. As part of the script
# it also retrieves currently installed Firmware Version of iDRAC.
# Input:    text file with a list of iDRAC IPs.
# Output:   1 to 5 text files two of which are error logs and three containing a
#           list of iDRAC IPs, their FW versions, and the query results.
#
# _author_ = Azat Salikhov <Azat_Salikhov@Dellteam.com>
# _version_ = 2.0
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
main_err_log = "Main_Err_log_%s.txt" % cts
fw_req_err_log = "FW_Req_Err_log_%s.txt" % cts
bmr_check_unknown_log = "RfBMR_Unknown_log_%s.txt" % cts
bmr_check_success_log = "RfBMR_Supported_log_%s.txt" % cts
bmr_check_failed_log = "RfBMR_Unsupported_log_%s.txt" % cts


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
        writeToLog(fw_req_err_log, idrac_ip + ": " + str(tuple(e)) + "\n")
        return "unavailable"


def checkSupportForBmr(node_ip):
    url = (
        "https://%s/redfish/v1/Dell/Systems/System.Embedded.1/DellOSDeploymentService"
        % node_ip
    )
    response = requests.get(
        url, verify=False, auth=(idrac_username, idrac_password), timeout=10
    )
    data = response.json()
    if response.status_code != 200:
        return "Not Supported"
    else:
        return "Supported"


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

# Cycle through the supplied iDRAC list and run the queries
for idrac_ip in ftr.readlines():
    try:
        # Clean up IP by removing EOL character
        idrac_ip = idrac_ip.strip("\n\r ")

        # Call function to get the iDRAC FW version via Redfish protocol
        query1 = getIdracFwVersion(idrac_ip)

        # Check return value of 1st query then do conditionals
        if query1 == "unavailable":
            writeToLog(
                bmr_check_unknown_log, idrac_ip + ", " + query1 + ", " + "unknown\n"
            )
            print(idrac_ip + ", " + query1 + ", " + "unknown\n")
        else:
            # Call function to check if this iDRAC version supports Redfish BMR
            query2 = checkSupportForBmr(idrac_ip)
            if query2 == "Supported":
                writeToLog(
                    bmr_check_success_log,
                    idrac_ip + ", " + query1 + ", " + query2 + "\n",
                )
            else:
                writeToLog(
                    bmr_check_failed_log,
                    idrac_ip + ", " + query1 + ", " + query2 + "\n",
                )

            print(idrac_ip + ", " + query1 + ", " + query2 + "\n")

    except:  # catch *all* exceptions
        e = sys.exc_info()
        writeToLog(main_err_log, idrac_ip + ": " + str(tuple(e)) + "\n")
        print(
            idrac_ip + " -> Error inside main: ", e
        )  # (Exception Type, Exception Value, TraceBack)
        pass
