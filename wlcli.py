#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
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


def get_profile(args):
    print "get_profile()"


def get_contact(args):
    print "get_contact()"


def get_list(args):
    print "get_list()"


def get_task(args):
    print "get_task()"


options = {
    "get-profile" : get_profile,
    "get-contact" : get_contact,
    "get-list" : get_list,
    "get-task" : get_task,
}


if __name__ == '__main__':
    args = parsers()
    options[args.subparser_name](args)
