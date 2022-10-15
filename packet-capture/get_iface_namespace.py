#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# https://docs.openstack.org/keystoneauth/latest/api/keystoneauth1.session.html
# https://docs.openstack.org/python-neutronclient/latest/user/python-api.html
# https://docs.openstack.org/python-neutronclient/latest/reference/index.html
# https://docs.openstack.org//python-neutronclient/latest/doc-python-neutronclient.pdf

import sys
import argparse
import urllib3

from keystoneauth1.identity import v3
from keystoneauth1 import session
from neutronclient.v2_0 import client as neutron_client
import json


# FOR TEST:  port_id = ""

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Parser command-line options
parser = argparse.ArgumentParser()
# parser.add_argument("-i", "--interface", dest='iface', help="Network interface.", required=True)
parser.add_argument("-p", "--port-id", dest='port_id', help="Openstack port ID.", required=True)
if len(sys.argv)==1:
     parser.print_help(sys.stderr)
     print("\n")
     exit(1)
args = parser.parse_args()


# Disable SSL Warnings when using self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# API
IDENTITY_API = "https://200.137.75.159:5000/v3"

# OpenStack User and Project. From the OpenRC file.
PROJECT_NAME = "PRJ_LUCIANOBF"
PROJECT_DOMAIN_ID = "default"
USER_DOMAIN_NAME = "Default"
USERNAME = "lucianobf"
PASSWORD = "ssX#20201-mp"

auth = v3.Password(auth_url=IDENTITY_API,
                   username=USERNAME,
                   password=PASSWORD,
                   project_name=PROJECT_NAME,
                   user_domain_name=USER_DOMAIN_NAME,
                   project_domain_id=PROJECT_DOMAIN_ID)
# Create a session with the credentials
# param verify : False when using self-signed certificates
sess = session.Session(auth=auth, verify=False)
# Create neutron client with the session created
neutron = neutron_client.Client(session=sess)

# Get info
port_info = neutron.show_port(args.port_id)
#print(json.dumps(port_info, indent=4))
device_id = port_info['port']["device_id"]
port_owner = port_info['port']["device_owner"]
os_host = port_info['port']["binding:host_id"]

namespace = ""

if port_owner == "network:router_gateway":
    iface = "qg-"+args.port_id[:11]
    namespace = "qrouter-"+device_id
elif port_owner == "network:router_interface":
    iface = "qr-"+args.port_id[:11]
    namespace = "qrouter-"+device_id
elif port_owner == "compute:nova":
    iface = "tap"+args.port_id[:11]

print(f"")
print(f"  Openstack Port ID: {bcolors.BOLD}{args.port_id}{bcolors.ENDC}")
print(f"OpenStack Device ID: {bcolors.BOLD}{device_id}{bcolors.ENDC}\n")
print(f"    Linux Namespace: {bcolors.BOLD}{namespace}{bcolors.ENDC}")
print(f"    Linux Interface: {bcolors.BOLD}{iface}{bcolors.ENDC}")
print(f"")

if namespace:
    print(f"{bcolors.BOLD}[ALERT] {bcolors.WARNING}The script {bcolors.BOLD+bcolors.UNDERLINE}stratified-capture_v2.py{bcolors.ENDC} {bcolors.WARNING}must be run in {os_host}.{bcolors.ENDC}")
    print("")
    print(f"To enter in namespace:")
    print(f"    # {bcolors.OKCYAN}sudo ip netns exec {namespace} bash{bcolors.ENDC}")
    print(f"")
    print(f"Inside namespace:")
    print(f"    # {bcolors.OKCYAN}python3 stratified-capture_v3.py -i {iface} -t [normal|attack|all] -o <OUT_DIR>{bcolors.ENDC}")

else:
    print(f"{bcolors.BOLD}[ALERT] {bcolors.WARNING}The script {bcolors.BOLD+bcolors.UNDERLINE}stratified-capture_v2.py{bcolors.ENDC} {bcolors.WARNING}must be run in {os_host}.{bcolors.ENDC}")
    print("")
    print(f"    # {bcolors.OKCYAN}python3 stratified-capture_v3.py -i {iface} -t [normal|attack|all] -o <OUT_DIR>{bcolors.ENDC}")
    

print(f"")