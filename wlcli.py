#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
from WunderlistAPI import WunderlistAPI
from auth import email, password
from datetime import datetime


def parsers():
    parser = argparse.ArgumentParser(description = "unofficial commandline tool for wunderlist")
    parser.add_argument("-d", "--display-done", help = "show the completed tasks/subtasks aligned", action = "store_true")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", help = "increase output verbosity", action = "store_true")
    group.add_argument("-c", "--column", help = "put output in two columns, default length is 40", type = int)

    subparsers = parser.add_subparsers(help = "functions currently supported", dest = 'subparser_name')

    parser_getprofile = subparsers.add_parser("get-profile", help = "get user's profile")
    
    parser_getcontact = subparsers.add_parser("get-contact", help = "get user's contacts")

    parser_getlist = subparsers.add_parser("get-list", help = "get info of all lists")

    parser_gettask = subparsers.add_parser("get-task", help = "get info of task in a list")
    parser_gettask.add_argument("list_id", type = str, action = 'store', help = "id of the list")
    
    parser_gettask = subparsers.add_parser("task-info", help = "get detail info of a task")
    parser_gettask.add_argument("task_id", type = str, action = 'store', help = "id of the task")
    
    parser_gettask = subparsers.add_parser("task-done", help = "mark a task as completed")
    parser_gettask.add_argument("task_id", type = str, action = 'store', help = "id of the task")
    
    parser_gettask = subparsers.add_parser("task-undo", help = "mark a task as to-do")
    parser_gettask.add_argument("task_id", type = str, action = 'store', help = "id of the task")

    return parser.parse_args()



def print_table(lines, column_length, mark = "MARKBREAKLINE", title = [ "Key", "Value" ]):
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
    lines = [ [ mark ], title, [ mark ] ] + lines + [ [ mark ] ]
    # Print
    for line in lines:
        if line[0] == mark:
            print breakline
        else:
            line0 = line[0] if line[0] else ""
            line1 = line[1] if line[1] else ""
            print format_line % (line0[:column_first].ljust(column_first), line1[:column_second].ljust(column_second))



def get_profile(api, args):
    profile = api.get_profile()
    if args.verbose:
        print json.dumps(profile, indent = 4)
    else:
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
    contacts = api.get_contacts()
    if args.verbose:
        print json.dumps(contacts, indent = 4)
    else:
        lines = []
        mark = "MARKBREAKLINECONTACTS"
        for contact in contacts:
            lines += [
                [ "Name", contact['name'] ],
                [ "Type", contact['type'] ],
                [ "Is Pro?", "Yes" if contact['pro'] else "No" ],
                [ "ID", contact['id'] ],
                [ "Email", contact['email'] ],
                [ "Last Updated", contact['updated_at'] ],
            ] + [ [mark] ]
        print_table(lines[:-1], args.column, mark)



def get_list(api, args):
    lists = api.get_lists(True)
    if args.verbose:
        print json.dumps(lists, indent = 4)
    else:
        lines = [ [ list['id'], list['title'] ] for list in lists]
        print_table(lines, args.column, title = [ "List ID", "Title" ])



def get_task(api, args):
    tasks = api.get_tasks_by_list(args.list_id, True)
    if args.verbose:
        filtered = []
        if args.display_done:
            for task in tasks:
                if not task['parent_id'] and task['completed_at']:
                    filtered.append(task)
        else:
            for task in tasks:
                if not task['parent_id'] and not task['completed_at']:
                    filtered.append(task)
        print json.dumps(filtered, indent = 4)
    else:
        mark = "MARKBREAKLINETASK"
        lines = []
        for task in tasks:
            if not task['parent_id'] and not task['completed_at']:
                lines += [ [ task['id'], task['title'] ] ]
        if args.display_done:
            lines += [ [mark] ]
            tasks = sorted(tasks, key = lambda item : datetime.strptime(item['updated_at'], '%Y-%m-%dT%H:%M:%SZ'), reverse = True)
            for task in tasks:
                if not task['parent_id'] and task['completed_at']:
                    lines += [ [ task['id'], task['title'] ] ]
        print_table(lines, args.column, mark, title = [ "Task ID", "Title" ])



def task_info(api, args):
    task = api.get_task(args.task_id)
    if args.verbose:
        print json.dumps(task, indent = 4)
    else:
        lines = [
            [ "Title", task['title'] ],
            [ "Type", task['type'] ],
            [ "ID", task['id'] ],
            [ "List ID", task['list_id'] ],
            [ "Parent ID", task['parent_id'] ],
            [ "Assgined To", task['assignee_id'] ],
            [ "Starred", "Yes" if task['starred'] else "No" ],
            [ "Due Date", task['due_date'] ],
            [ "Created", task['created_at'] ],
            [ "Last Updated", task['updated_at'] ],
            [ "Completed", task['completed_at'] ],
            [ "Note", task['note'] ],
        ]
        print_table(lines, args.column)



def task_done(api, args):
    task = api.check_task(args.task_id)
    if args.verbose:
        print json.dumps(task, indent = 4)
    else:
        lines = [
            [ "Title", task['title'] ],
            [ "Type", task['type'] ],
            [ "ID", task['id'] ],
            [ "Last Updated", task['updated_at'] ],
            [ "Completed", task['completed_at'] ],
        ]
        print_table(lines, args.column)




def task_undo(api, args):
    task = api.uncheck_task(args.task_id)
    if args.verbose:
        print json.dumps(task, indent = 4)
    else:
        lines = [
            [ "Title", task['title'] ],
            [ "Type", task['type'] ],
            [ "ID", task['id'] ],
            [ "Last Updated", task['updated_at'] ],
            [ "Completed", task['completed_at'] ],
        ]
        print_table(lines, args.column)



if __name__ == '__main__':
    args = parsers()
    api = WunderlistAPI(email, password)
    eval(args.subparser_name.replace('-', '_'))(api, args)
