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
import daemon
from mastodon import Mastodon

def printmsg(args, message, priority=syslog.LOG_INFO):
    """Print a message to Console or Syslog"""
    if args.debug is True:
        print(message)
    else:
        syslog.syslog(priority, message)

def register_app(args):
    """Register Mastodon app if first run and populate config"""
    config = configparser.ConfigParser()
    base_url = ""
    email = ""
    passwd = ""
    is_correct = False
    while is_correct is False:
        base_url = input('Enter Mastodon Url: ')
        email = input('Enter Mastodon E-Mail: ')
        passwd = getpass.getpass(prompt='Mastodon Password: ')
        print("Are these Values O.k:")
        print("\tUrl: " + base_url)
        print("\tE-Mail: " + email)
        print("\tand the Password")
        boolstr = input("[Y/N]: ")
        if boolstr.lower() == "y":
            is_correct = True

    (client_id, client_secret) = Mastodon.create_app('mastposd', scopes=['read'], api_base_url=base_url)
    config["mastodon"]["client_id"] = client_id
    config["mastodon"]["client_secret"] = client_secret
    api = Mastodon(client_id, client_secret, api_base_url=base_url)
    token = api.log_in(email, passwd, scopes=["read"])
    config["mastodon"]["access_token"] = token
    print("Wrote Ini File to: " + args.config + "\n")
    with open(args.config, 'w') as configfile:
        config.write(configfile)
    exit(0)

def main(args):
    """Connect to Printer and Watch Mastodon"""
    pass

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description='Print Mastodon Toots on Pos Printer')
    PARSER.add_argument('-c', '--config', default="/etc/mastosd.ini", type=str,
                        help="Path to config file. (Default: /etc/mastosd.ini)")
    PARSER.add_argument('-d', '--debug', action='store_true', default=False,
                        help="Debug Mode: Do not Daemonize")
    ARGS = PARSER.parse_args()

    if os.path.isfile(ARGS.config) is False:
        register_app(ARGS)
        exit(0)

    if ARGS.debug is True:
        main(ARGS)
    else:
        with daemon.DaemonContext():
            main(ARGS)
    exit(0)
