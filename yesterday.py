#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import time
from datetime import datetime, timedelta
from operator import itemgetter
from WunderlistAPI import WunderlistAPI
from auth import email, password



output_string = ""
trailing_space = " " * 4 + "\n"
blockmark = "\n" + "`" * 3 + "\n"
blockquote = trailing_space + "> "


def print_subtask(task):
    global output_string
    # Extract info needed
    is_done =  True if task['completed_at'] else False
    date = datetime.strptime(task['completed_at'], '%Y-%m-%dT%H:%M:%SZ') + timedelta(hours = 8)
    datestr = date.strftime('%H:%M %b %d')
    title = task['title']
    # Output basic info of the subtask
    if is_done:
        output_string += u"  * ✔︎ `%s` %s %s" % (datestr, title, trailing_space)
    else:
        output_string += u"  * Ø %s %s" % (title, trailing_space)



def print_task(task, child_tasks, list_dict):
    global output_string
    # Extract info needed
    is_done =  True if task['completed_at'] else False
    date = datetime.strptime(task['updated_at'], '%Y-%m-%dT%H:%M:%SZ') + timedelta(hours = 8)
    datestr = date.strftime('%H:%M %b %d')
    title = task['title']
    note = task['note']
    list = list_dict[task['list_id']]
    # Output basic info of the task
    if is_done:
        output_string += u"* ✔︎ `%s` _%s_ - %s %s" % (datestr, list, title, trailing_space)
    else:
        output_string += u"* Ø _%s_ - %s %s" % (list, title, trailing_space)
    # Output completed subtasks of the task
    for subtask in child_tasks:
        if subtask['parent_id'] == task['id']:
            print_subtask(subtask)
    # Output note appending to the task
    if note:
        note = "\n" + note.replace("\r\n", "\n").rstrip()
        output_string += note.replace("\n", blockquote) + "\n" * 2



def save_output():
    global output_string
    file = open("content.md", "w")
    file.write(output_string.encode('utf-8'))
    file.close()



def check_timerange(timestr, limit):
    min_date = datetime.utcnow() - timedelta(hours = limit)
    aim_date = datetime.strptime(timestr, '%Y-%m-%dT%H:%M:%SZ') + timedelta(hours = 8)
    return aim_date >= min_date



if __name__ == '__main__':
    last_hours = 24

    # Get all the task updated recently
    api = WunderlistAPI(email, password)
    tasks = api.read_tasks_recently(hours = last_hours)

    # Remove deleted tasks
    tasks = [ task for task in tasks if not task['deleted_at'] ]

    # Figure out listed completed tasks
    parent_tasks = [ task for task in tasks if not task['parent_id'] and task['completed_at'] and check_timerange(task['completed_at'], last_hours) ]
    parent_set = set(task['id'] for task in parent_tasks)

    # Figure out listed completed subtasks
    child_tasks = [ task for task in tasks if task['parent_id'] and task['completed_at'] and check_timerange(task['completed_at'], last_hours) ]

    # Figure out tasks contain these completed subtasks
    parent_set_plus = set(task['parent_id'] for task in child_tasks)

    # Add listed tasks of listed completed subtasks even if it's not completed
    plus_set = parent_set_plus - parent_set
    parent_tasks += [ task for task in tasks if task['id'] in plus_set ]

    # Figure out unlisted tasks of listed completed subtasks
    parent_set = set(task['id'] for task in parent_tasks)
    load_set = parent_set_plus - parent_set
    for task_id in load_set:
        parent_tasks.append(api.read_task_by_id(task_id = task_id))

    # Sort the lists
    parent_tasks = sorted(parent_tasks, key = lambda item : datetime.strptime(item['updated_at'], '%Y-%m-%dT%H:%M:%SZ'), reverse = True)
    child_tasks = sorted(child_tasks, key = lambda item : datetime.strptime(item['updated_at'], '%Y-%m-%dT%H:%M:%SZ'), reverse = False)

    # Get all the lists
    lists = api.read_lists()
    list_dict = { list['id'] : list['title'] for list in lists }

    # Output
    for task in parent_tasks:
        print_task(task, child_tasks, list_dict)
    save_output()