#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  4 21:18:13 2018

@author: blickfeldkurier
"""
import sys
import getpass
import syslog
import argparse
import os.path
import configparser
from mastodon import Mastodon
import usb.core

def printmsg(message, priority=syslog.LOG_INFO):
    """Print a message to Console or Syslog"""
    print(message)
    syslog.syslog(priority, message)

def get_entpoint(vendor_id, device_id):#idVendor=0x0416, idProduct=0x5011
    """Connnect to printer"""
    dev = usb.core.find(idVendor=vendor_id, idProduct=device_id)
    dev.set_configuration()
    cfg = dev.get_active_configuration()
    intf = cfg[(0, 0)]
    endpoint = usb.util.find_descriptor(intf, custom_match=lambda e: \
                                  usb.util.endpoint_direction(e.bEndpointAddress) == \
                                  usb.util.ENDPOINT_OUT)
    return endpoint

def register_app(args):
    """Register Mastodon app if first run and populate config"""
    config = configparser.ConfigParser()
    base_url = ""
    email = ""
    passwd = ""
    is_correct = False
    vendor_id = ""
    device_id = ""
    while is_correct is False:
        print("Enter Mastodon Credentials:")
        base_url = input('Enter Mastodon Url: ')
        email = input('Enter Mastodon E-Mail: ')
        passwd = getpass.getpass(prompt='Mastodon Password: ')
        print("Enter USB Values as Hex (0xDEADBEAF)")
        vendor_id = input("Vendor ID: ")
        device_id = input("Device ID: ")
        print("Are these Values O.k:")
        print("\tUrl: " + base_url)
        print("\tE-Mail: " + email)
        print("\tand the Password")
        boolstr = input("[Y/N]: ")
        if boolstr.lower() == "y":
            is_correct = True

    (client_id, client_secret) = Mastodon.create_app('mastposd', scopes=['read'], api_base_url=base_url)
    api = Mastodon(client_id, client_secret, api_base_url=base_url)
    token = api.log_in(email, passwd, scopes=["read"])
    config["printer"] = {"vendor_id":vendor_id,
                         "device_id":device_id}
    config["mastodon"] = {"base_url":base_url,
                          "client_id":client_id,
                          "client_secret":client_secret,
                          "access_token":token}
    with open(args.config, 'w') as configfile:
        config.write(configfile)
    print("Wrote Ini File to: " + args.config + "\n")
    print("Setup Complete - Please restart mastposd")
    exit(0)

def mastodon_init(args):
    """Read config and initialise Mastodon"""
    config = configparser.ConfigParser()
    config.read(args.config)
    api = Mastodon(client_id=config["mastodon"]["client_id"],
                   access_token=config["mastodon"]["access_token"],
                   api_base_url=config["mastodon"]["base_url"])
    return (config, api)

def main(args):
    """Connect to Printer and Watch Mastodon"""
    (config, api) = mastodon_init(args)
    endpoint = get_entpoint(0x0416, 0x5011)

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description='Print Mastodon Toots on Pos Printer')
    PARSER.add_argument('-c', '--config', default="/etc/mastosd.ini", type=str,
                        help="Path to config file. (Default: /etc/mastosd.ini)")
    PARSER.add_argument('-s', '--setup', action='store_true', default=False,
                        help="Run Setup and create INI File")
    ARGS = PARSER.parse_args()

    if ARGS.setup is True:
        register_app(ARGS)
        exit(0)

    if os.path.isfile(ARGS.config) is False:
        printmsg("Config file not found: " + ARGS.config,
                 priority=syslog.LOG_ERR)
        exit(1)

    main(ARGS)
    exit(0)
