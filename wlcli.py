#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from WunderlistAPI import WunderlistAPI
from auth import email, password


def parsers():
    parser = argparse.ArgumentParser(description = "unofficial commandline tool for wunderlist")
    parser.add_argument("-v", "--verbose", help = "increase output verbosity", action = "store_true")

    subparsers = parser.add_subparsers(help = "functions currently supported", dest = 'subparser_name')

    parser_getprofile = subparsers.add_parser("get-profile", help = "get user's profile")
    
    parser_getcontact = subparsers.add_parser("get-contact", help = "get user's contacts")

    parser_getlist = subparsers.add_parser("get-list", help = "get info of all lists")

    parser_gettask = subparsers.add_parser("get-task", help = "get info of task in a list")
    parser_gettask.add_argument("list_id", type = str, action = 'store', help = "id of the list")

    return parser.parse_args()


def get_profile(api, args):
    print "get_profile()", args


def get_contact(api, args):
    print "get_contact()", args


def get_list(api, args):
    print "get_list()", args


def get_task(api, args):
    print "get_task()", args


if __name__ == '__main__':
    args = parsers()
    api = WunderlistAPI(email, password)
    eval(args.subparser_name.replace('-', '_'))(api, args)
