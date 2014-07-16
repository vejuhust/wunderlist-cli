#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
from WunderlistAPI import WunderlistAPI
from auth import email, password


def parsers():
    parser = argparse.ArgumentParser(description = "unofficial commandline tool for wunderlist")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", help = "increase output verbosity", action = "store_true")
    group.add_argument("-c", "--column", help = "put output in two columns, default length is 40", type = int)

    subparsers = parser.add_subparsers(help = "functions currently supported", dest = 'subparser_name')

    parser_getprofile = subparsers.add_parser("get-profile", help = "get user's profile")
    
    parser_getcontact = subparsers.add_parser("get-contact", help = "get user's contacts")

    parser_getlist = subparsers.add_parser("get-list", help = "get info of all lists")

    parser_gettask = subparsers.add_parser("get-task", help = "get info of task in a list")
    parser_gettask.add_argument("list_id", type = str, action = 'store', help = "id of the list")

    return parser.parse_args()



def print_table(lines, column_length, mark = "MARKBREAKLINE"):
    # Table design
    column_first = 20
    column_second = column_length if column_length else 40
    delimiter_vertical = "|"
    delimiter_horizontal = "-"
    delimiter_cross = "+"
    # Format
    format_line = "%s %%s %s %%s %s" % ((delimiter_vertical, ) * 3)
    format_break = "%s%s%%s%s+%s%%s%s%s" % ((delimiter_cross, ) + (delimiter_horizontal, ) * 4 + (delimiter_cross, ))
    breakline = format_break % (delimiter_horizontal * column_first, delimiter_horizontal * column_second)
    lines = [ [ mark ], [ "Key", "Value" ], [ mark ] ] + lines + [ [ mark ] ]
    # Print
    for line in lines:
        if line[0] == mark:
            print breakline
        else:
            print format_line % (line[0][:column_first].ljust(column_first), line[1][:column_second].ljust(column_second))



def get_profile(api, args):
    if args.verbose:
        print json.dumps(api.get_profile(), indent = 4)
    else:
        profile = api.get_profile()
        lines = [
            [ "Name", profile['name'] ],
            [ "Type", profile['type'] ],
            [ "ID", profile['id'] ],
            [ "Email", profile['email'] ],
            [ "Last Updated", profile['updated_at'] ],
            [ "Token", profile['token'] ],
        ]
        print_table(lines, args.column)



def get_contact(api, args):
    if args.verbose:
        print json.dumps(api.get_contacts(), indent = 4)
    else:
        lines = []
        mark = "MARKBREAKLINECONTACTS"
        contacts = api.get_contacts()
        for contact in contacts:
            lines = lines + [
                [ "Name", contact['name'] ],
                [ "Type", contact['type'] ],
                [ "Is Pro?", "Yes" if contact['pro'] else "No" ],
                [ "ID", contact['id'] ],
                [ "Email", contact['email'] ],
                [ "Last Updated", contact['updated_at'] ],
            ] + [ [mark] ]
        print_table(lines[:-1], args.column, mark)



def get_list(api, args):
    print "get_list()", args



def get_task(api, args):
    print "get_task()", args



if __name__ == '__main__':
    args = parsers()
    api = WunderlistAPI(email, password)
    eval(args.subparser_name.replace('-', '_'))(api, args)
