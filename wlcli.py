#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
from datetime import datetime
from operator import itemgetter
from WunderlistAPI import WunderlistAPI
from auth import email, password


def parsers():
    parser = argparse.ArgumentParser(description = "unofficial commandline tool for wunderlist")
    parser.add_argument("-d", "--display-done", help = "show the completed tasks/subtasks aligned", action = "store_true")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", help = "increase output verbosity", action = "store_true")
    group.add_argument("-c", "--column", help = "put output in two columns, default length is 40", type = int)

    subparsers = parser.add_subparsers(help = "functions currently supported", dest = 'subparser_name')

    parser_readprofile = subparsers.add_parser("read-profile", help = "get user's profile")
    
    parser_readcontact = subparsers.add_parser("read-contact", help = "get user's contacts")

    parser_readlist = subparsers.add_parser("read-list", help = "get info of all lists")

    parser_readtask = subparsers.add_parser("read-task", help = "get info of task in a list")
    parser_readtask.add_argument("list_id", type = str, action = 'store', help = "id of the list")
    
    parser_readsubtask = subparsers.add_parser("read-subtask", help = "get info of subtasks of a task")
    parser_readsubtask.add_argument("task_id", type = str, action = 'store', help = "id of the task")
    
    parser_taskinfo = subparsers.add_parser("task-info", help = "get detail info of a task")
    parser_taskinfo.add_argument("task_id", type = str, action = 'store', help = "id of the task")
    
    parser_taskdone = subparsers.add_parser("task-done", help = "mark a task/subtask as completed")
    parser_taskdone.add_argument("task_id", type = str, action = 'store', help = "id of the task")
    
    parser_taskundo = subparsers.add_parser("task-undo", help = "mark a task/subtask as to-do")
    parser_taskundo.add_argument("task_id", type = str, action = 'store', help = "id of the task")
    
    parser_createlist = subparsers.add_parser("create-list", help = "create a list with title")
    parser_createlist.add_argument("title", type = str, action = 'store', help = "title of the list")

    parser_createtask = subparsers.add_parser("create-task", help = "create a task with title")
    parser_createtask.add_argument("list_id", type = str, action = 'store', help = "id of the list")
    parser_createtask.add_argument("title", type = str, action = 'store', help = "title of the task")

    parser_createsubtask = subparsers.add_parser("create-subtask", help = "create a subtask with title")
    parser_createsubtask.add_argument("task_id", type = str, action = 'store', help = "id of the parent task")
    parser_createsubtask.add_argument("title", type = str, action = 'store', help = "title of the subtask")

    parser_updatelist = subparsers.add_parser("update-list", help = "update a list")
    parser_updatelist.add_argument("list_id", type = str, action = 'store', help = "id of the list")
    parser_updatelist.add_argument("title", type = str, action = 'store', help = "title of the list")
    
    parser_updatetask = subparsers.add_parser("update-task", help = "update a task")
    parser_updatetask.add_argument("task_id", type = str, action = 'store', help = "id of the task")
    parser_updatetask.add_argument("title", type = str, action = 'store', help = "title of the task")
    
    parser_updatesubtask = subparsers.add_parser("update-subtask", help = "update a subtask")
    parser_updatesubtask.add_argument("task_id", type = str, action = 'store', help = "id of the subtask")
    parser_updatesubtask.add_argument("title", type = str, action = 'store', help = "title of the subtask")
    
    parser_delete = subparsers.add_parser("delete", help = "delete a list/task/subtask")
    parser_delete.add_argument("item_id", type = str, action = 'store', help = "id of the list/task/subtask")

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



def read_profile(api, args):
    profile = api.read_profile()
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



def read_contact(api, args):
    contacts = api.read_contacts()
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



def read_list(api, args):
    lists = api.read_lists(True)
    if args.verbose:
        print json.dumps(lists, indent = 4)
    else:
        lines = [ [ list['id'], list['title'] ] for list in lists]
        print_table(lines, args.column, title = [ "List ID", "Title" ])



def read_task(api, args):
    tasks = api.read_tasks_by_list(args.list_id, True)
    if args.verbose:
        if args.display_done:
            filtered = [ task for task in tasks if not task['parent_id'] and task['completed_at'] ]
        else:
            filtered = [ task for task in tasks if not task['parent_id'] and not task['completed_at'] ]
        print json.dumps(filtered, indent = 4)
    else:
        mark = "MARKBREAKLINETASK"
        lines = [ [ task['id'], task['title'] ] for task in tasks if not task['parent_id'] and not task['completed_at'] ]
        if args.display_done:
            lines += [ [mark] ]
            tasks = sorted(tasks, key = lambda item : datetime.strptime(item['updated_at'], '%Y-%m-%dT%H:%M:%SZ'), reverse = True)
            lines += [ [ task['id'], task['title'] ] for task in tasks if not task['parent_id'] and task['completed_at'] ]
        print_table(lines, args.column, mark, title = [ "Task ID", "Title" ])



def read_subtask(api, args):
    task = api.read_task(args.task_id)
    parent_id = task['id']
    list_id = task['list_id']
    tasks = api.read_tasks_by_list(list_id, True)
    subtasks = [ task for task in tasks if task['parent_id'] == parent_id ]
    if args.verbose:
        filtered = []
        if args.display_done:
            filtered = subtasks
        else:
            filtered = [ task for task in subtasks if not task['completed_at'] ]
        print json.dumps(filtered, indent = 4)
    else:
        mark = "MARKBREAKLINESUBTASK"
        lines = [ [ task['id'], task['title'] ] for task in subtasks if not task['completed_at'] ]
        if args.display_done:
            lines += [ [mark] ]
            tasks = sorted(subtasks, key = itemgetter('position'), reverse = False)
            lines += [ [ task['id'], task['title'] ] for task in tasks if task['completed_at'] ]
        print_table(lines, args.column, mark, title = [ "Sub-task ID", "Title" ])



def task_info(api, args):
    task = api.read_task(args.task_id)
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



def create_list(api, args):
    list = api.create_list(args.title)
    if args.verbose:
        print json.dumps(list, indent = 4)
    else:
        lines = [
            [ "Title", list['title'] ],
            [ "Type", list['type'] ],
            [ "ID", list['id'] ],
            [ "Last Updated", list['updated_at'] ],
        ]
        print_table(lines, args.column)



def create_task(api, args):
    task = api.create_task(title = args.title, list_id = args.list_id)
    if args.verbose:
        print json.dumps(task, indent = 4)
    else:
        lines = [
            [ "Title", task['title'] ],
            [ "Type", task['type'] ],
            [ "ID", task['id'] ],
            [ "List ID", task['list_id'] ],
            [ "Last Updated", task['updated_at'] ],
        ]
        print_table(lines, args.column)



def create_subtask(api, args):
    task = api.create_task(title = args.title, parent_id = args.task_id)
    if args.verbose:
        print json.dumps(task, indent = 4)
    else:
        lines = [
            [ "Title", task['title'] ],
            [ "Type", task['type'] ],
            [ "ID", task['id'] ],
            [ "Parent ID", task['parent_id'] ],
            [ "Last Updated", task['updated_at'] ],
        ]
        print_table(lines, args.column)



def update_list(api, args):
    list = api.update_list(args.list_id, args.title)
    if args.verbose:
        print json.dumps(list, indent = 4)
    else:
        lines = [
            [ "Title", list['title'] ],
            [ "Type", list['type'] ],
            [ "ID", list['id'] ],
            [ "Last Updated", list['updated_at'] ],
        ]
        print_table(lines, args.column)



def update_task(api, args):
    task = api.update_task(args.task_id, args.title)
    if args.verbose:
        print json.dumps(task, indent = 4)
    else:
        lines = [
            [ "Title", task['title'] ],
            [ "Type", task['type'] ],
            [ "ID", task['id'] ],
            [ "Last Updated", task['updated_at'] ],
        ]
        print_table(lines, args.column)



def update_subtask(api, args):
    update_task(api, args)



def delete(api, args):
    item = api.remove(args.item_id)
    print json.dumps(item, indent = 4)




if __name__ == '__main__':
    args = parsers()
    api = WunderlistAPI(email, password)
    eval(args.subparser_name.replace('-', '_'))(api, args)
