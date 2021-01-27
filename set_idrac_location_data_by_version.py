#!/usr/bin/env python2
# Python script to import Physical Location Data namely Building, Rack, Rack_U
# into iDRACs' manufacturer-specific list of attributes via racadm. Linux-only.
#
# _author_ =  Azat Salikhov for Dell Inc.
# _date_ = June 26, 2020

# Pull-in libraries
import sys
from pexpect import pxssh

# Declare variables
idrac_ip = ""
idrac_ver = ""
building = ""
rack = ""
rack_u = ""
count_s = 0
count_f = 0

# Create variable to point to logfile
logfile = "CSV_to_iDRAC_log.txt"

# Pass in filename wih iDRAC IPs and corresponding Location Data fields
try:
    idrac_location_data = sys.argv[1]
except:
    print(
        "\n- FAIL, you must pass in a .CSV file with a list of iDRAC's data: IP, iDRAC version, building, rack, and rack_u"
    )
    sys.exit()

# Open a file with iDRAC IPs and their Location Data
try:
    ftr = open(idrac_location_data, "r")
except:
    print('/n-FAIL, "%s" file doesn\'t exist' % idrac_location_data)
    sys.exit()

# Cycle through the supplied iDRAC data and set each iDRAC's Location Attributes correspondingly
for idracData in ftr.readlines():
    idrac_ip, idrac_ver, building, rack, rack_u = idracData.split(
        ","
    )  # split csv strings into variables
    try:
        # Setup connection properties and login into iDRAC
        session = pxssh.pxssh()
        session.force_password = True
        session.timeout = 10
        username = "root"
        password = "calvin"
        session.login(
            idrac_ip, username, password, sync_multiplier=5, auto_prompt_reset=False
        )
        print("Logged in to " + idrac_ip +
              " and setting its location attributes..")
        # Send racadm commands to appropriate system variables based on iDRAC version
        if idrac_ver[0] == "2":
            session.sendline(
                "racadm set System.Location.DataCenter " + building
            )  # run command
            session.prompt()  # match the prompt
            session.sendline("racadm set System.Location.Rack.Name " + rack)
            session.prompt()
            session.sendline("racadm set System.Location.Rack.Slot " + rack_u)
            session.prompt()
        elif idrac_ver[0] == "3" or "4":
            session.sendline(
                "racadm set system.servertopology.DataCenterName " + building
            )
            session.prompt()
            session.sendline(
                "racadm set system.servertopology.RackName " + rack)
            session.prompt()
            session.sendline(
                "racadm set system.servertopology.RackSlot " + rack_u)
            session.prompt()
        else:
            print("This version of iDRAC is not supported..yet")

        count_s += 1
        print("Writing query results to a logfile..")
        # Open logfile for writing/appending and dump the output to logfile
        f = open(logfile, "a")
        f.write(
            "Successfuly set location data for iDRAC at " +
            idrac_ip + ".\n" + session.before + "\n"
        )
        f.flush()
        f.close()
        print("Closing connection and logging out.")
        session.sendline("quit")
        session.logout()
        session.close()
        print("-------------------------------------")
    except pxssh.ExceptionPexpect as e:
        count_f += 1
        # Catch errors and output them to console
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print("pxssh failure on " + idrac_ip + ": ")
        print(e)
        print("Bypassing " + idrac_ip +
              " and moving to the next node in the list.")
        print("Writing query results to a logfile..")
        # Open logfile for writing/appending then log the failure
        f = open(logfile, "a")
        f.write(
            "pxssh failure on "
            + idrac_ip
            + "\nBypassing it and moving to the next node.\n"
        )
        f.flush()
        f.close()
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        # Do not logout and close the session, but continue to the next IP in the list
        pass

print("Successfuly updated " + count_s +
      " iDRACs. " + count_f + " have failed.")
