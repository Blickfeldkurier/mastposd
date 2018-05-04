#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  4 21:18:13 2018

@author: blickfeldkurier
"""
import syslog
import argparse
import daemon

def printmsg(args, message, priority=syslog.LOG_INFO):
    """Print a message to Console or Syslog"""
    if args.debug is True:
        print(message)
    else:
        syslog.syslog(priority, message)

def main(args):
    """Connect to Printer and Watch Mastodon"""
    pass

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description='Print Mastodon Toots on Pos Printer')
    PARSER.add_argument('-d', '--debug', action='store_true', default=False,
                        help="Debug Mode: Do not Daemonize")
    ARGS = PARSER.parse_args()
    if ARGS.debug is True:
        main(ARGS)
    else:
        with daemon.DaemonContext():
            main(ARGS)
