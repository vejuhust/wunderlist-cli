#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import socket
import StringIO
import gzip
import json
from inspect import getargspec
from operator import itemgetter
from datetime import datetime
from auth import email, password



class WunderlistAPI():
    
    # Constructor
    def __init__(self, email, password):
        # Status
        self.account_email = email
        self.account_password = password
        self.is_login = False
        self.token = ''
        # Constants
        self.login_url = "https://api.wunderlist.com/login"
        self.login_headers = {
            'Accept' : 'application/json',
            'Accept-Encoding' : 'gzip,deflate',
            'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host' : 'api.wunderlist.com',
            'Origin' : 'https://www.wunderlist.com',
        }
        self.tokenfile_name = "token.json"
        self.apiurl_root = "https://api.wunderlist.com/"
        self.apiurl_profile = "https://api.wunderlist.com/me"
        self.apiurl_settings = "https://api.wunderlist.com/me/settings"
        self.apiurl_contacts = "https://api.wunderlist.com/me/contacts"
        self.apiurl_services = "https://api.wunderlist.com/me/services"
        self.apiurl_quota = "https://api.wunderlist.com/me/quota"
        self.apiurl_events = "https://api.wunderlist.com/me/events"
        self.apiurl_shares = "https://api.wunderlist.com/me/shares"
        self.apiurl_reminders = "https://api.wunderlist.com/me/reminders"
        self.apiurl_lists = "https://api.wunderlist.com/me/lists"
        self.apiurl_tasks = "https://api.wunderlist.com/me/tasks"


    # Save token in a file
    def tokenfile_save(self, content):
        file = open(self.tokenfile_name, 'w')
        file.write(content)
        file.close()


    # Load token from a file
    def tokenfile_load(self):
        file = open(self.tokenfile_name, 'r')
        content = file.read()
        file.close()
        return json.loads(content)


    # Decode gzipped response content
    def decode_content(self, retval):
        if retval.info().has_key('content-encoding'):
            fileobj = StringIO.StringIO()
            fileobj.write(retval.read())
            fileobj.seek(0)
            gzip_file = gzip.GzipFile(fileobj=fileobj)
            content = gzip_file.read()
        else:
            content = retval.read()
        return content


    # Call Wunderlist private API
    def wunderlist_api_call(self, request_url, request_headers, request_data = None, method = None):
        data = {}
        request_data = urllib.urlencode(request_data) if request_data else None
        api_request = urllib2.Request(url = request_url, headers = request_headers, data = request_data)
        if method:
            api_request.get_method = lambda: method
        try:
            api_response = urllib2.urlopen(api_request, timeout = 5)
        except urllib2.URLError, error:
            error_code = error.code if hasattr(error, 'code') else ''
            error_reason = error.reason if hasattr(error, 'reason') else ''
            print "API Error:", error_code, error_reason
        except Exception as error:
            print "API Error:", error
        else:
            content = self.decode_content(api_response)
            data = json.loads(content)
        return data


    # Prepare for any Wunderlist private API calls
    def prepare_wunderlist_api_call(self):
        self.login()
        return { 'Authorization' : self.token }


    # Wrapper for Wunderlist private API call with GET method
    def wunderlist_api_call_get(self, url, param = None):
        headers = self.prepare_wunderlist_api_call()
        if param:
            url += '?' + urllib.urlencode(param)
        return self.wunderlist_api_call(url, headers)


    # Wrapper for Wunderlist private API call with POST method
    def wunderlist_api_call_post(self, url, data):
        headers = self.prepare_wunderlist_api_call()
        return self.wunderlist_api_call(url, headers, data)


    # Wrapper for Wunderlist private API call with PUT method
    def wunderlist_api_call_put(self, url, data):
        headers = self.prepare_wunderlist_api_call()
        return self.wunderlist_api_call(url, headers, data, 'PUT')


    # Wrapper for Wunderlist private API call with DELETE method
    def wunderlist_api_call_delete(self, url):
        headers = self.prepare_wunderlist_api_call()
        return self.wunderlist_api_call(url, headers, None, 'DELETE')


    # Login with account and password
    def wunderlist_login(self, email, password):
        login_data = { 'email' : self.account_email, 'password' : self.account_password }
        data = self.wunderlist_api_call(self.login_url, self.login_headers, login_data)
        if data:
            self.tokenfile_save(json.dumps(data))
        return data


    # Check login status and get token
    def login(self):
        if not self.is_login or len(self.token) == 0:
            try:
                data = self.tokenfile_load()
                self.token = data['token']
            except Exception as error:
                print "Token Error:", error
                data = self.wunderlist_login(email, password)
                self.token = data['token'] if data.has_key('token') else ''
            finally:
                if len(self.token) > 0:
                    self.is_login = True


    # Get user profile via https://api.wunderlist.com/me
    def get_profile(self):
        return self.wunderlist_api_call_get(self.apiurl_profile)


    # Get user settings via https://api.wunderlist.com/me/settings
    def get_settings(self):
        return self.wunderlist_api_call_get(self.apiurl_settings)


    # Get user contacts via https://api.wunderlist.com/me/contacts
    def get_contacts(self):
        return self.wunderlist_api_call_get(self.apiurl_contacts)


    # Get user's services via https://api.wunderlist.com/me/services
    def get_services(self):
        return self.wunderlist_api_call_get(self.apiurl_services)


    # Get user's quota via https://api.wunderlist.com/me/quota
    def get_quota(self):
        return self.wunderlist_api_call_get(self.apiurl_quota)


    # Get user's events via https://api.wunderlist.com/me/events
    def get_events(self):
        return self.wunderlist_api_call_get(self.apiurl_events)


    # Get user's sharing via https://api.wunderlist.com/me/shares
    def get_shares(self):
        return self.wunderlist_api_call_get(self.apiurl_shares)


    # Get user's reminders sorted by date via https://api.wunderlist.com/me/reminders
    def get_reminders(self, sort = False):
        tasks = self.wunderlist_api_call_get(self.apiurl_reminders)
        if sort:
            tasks = sorted(tasks, key = lambda item : datetime.strptime(item['date'], '%Y-%m-%dT%H:%M:%SZ'), reverse = True)
        return tasks


    # Get user's all lists sorted by position via https://api.wunderlist.com/me/lists
    def get_lists(self, sort = False):
        lists = self.wunderlist_api_call_get(self.apiurl_lists)
        if sort:
            lists = sorted(lists, key = itemgetter('position'), reverse = False)
        return lists


    # Get user's all tasks sorted by list_id, completed, position via https://api.wunderlist.com/me/tasks
    def get_tasks(self, sort = False):
        tasks = self.wunderlist_api_call_get(self.apiurl_tasks)
        if sort:
            tasks = sorted(tasks, key = itemgetter('list_id', 'completed_at', 'position'), reverse = False)
        return tasks


    # Get user's all the tasks in a list via https://api.wunderlist.com/me/tasks
    def get_tasks_by_list(self, list_id, sort = False):
        tasks = self.wunderlist_api_call_get(self.apiurl_tasks, { 'list_id' : list_id })
        if sort:
            tasks = sorted(tasks, key = itemgetter('completed_at', 'position'), reverse = False)
        return tasks


    # Create a new list with title
    def create_list(self, title):
        return self.wunderlist_api_call_post(self.apiurl_lists, { 'title' : title })


    # Create a new task with title, note*, list_id*, parent_id*, starred*, due_date*, assignee_id* (* opitonal)
    def create_task(self, title, note = None, list_id = None, parent_id = None, starred = None, due_date = None, assignee_id = None):
        task_info = {}
        params = getargspec(self.create_task).args
        for key in params[1:]:
            value = eval(key)
            if value:
                task_info[key] = value
        return self.wunderlist_api_call_post(self.apiurl_tasks, task_info)


    # Modify title of a list
    def modify_list(self, list_id, title):
        return self.wunderlist_api_call_put(self.apiurl_root + list_id, { 'title' : title })


    # Modify title/note/list_id/parent_id/starred/due_date/assignee_id of a task, now parent_id can't be changed
    def modify_task(self, task_id, title = None, note = None, list_id = None, parent_id = None, starred = None, due_date = None, assignee_id = None):
        task_info = {}
        params = getargspec(self.modify_task).args
        for key in params[2:]:
            value = eval(key)
            if value:
                task_info[key] = value
        task = self.wunderlist_api_call_put(self.apiurl_root + task_id, task_info) if task_info else {}
        return task


    # Delete a list as per its list_id
    def remove_list(self, list_id):
        return self.wunderlist_api_call_delete(self.apiurl_root + list_id)
    
    
    # Delete a task as per its task_id
    def remove_task(self, task_id):
        return self.wunderlist_api_call_delete(self.apiurl_root + task_id)


    # Complete a task as per its task_id
    def check_task(self, task_id):
        return self.wunderlist_api_call_put(self.apiurl_root + task_id, { 'completed_at' : 'now' })


    # Uncomplete a task as per its task_id
    def uncheck_task(self, task_id):
        return self.wunderlist_api_call_put(self.apiurl_root + task_id, { 'completed_at' : '' })



if __name__ == '__main__':
    api = WunderlistAPI(email, password)
    print api.is_login, api.token
    api.login()
    print api.is_login, api.token
    print "get_profile", json.dumps(api.get_profile(), indent = 4)
    print "get_settings", json.dumps(api.get_settings(), indent = 4)
    print "get_contacts", json.dumps(api.get_contacts(), indent = 4)
    print "get_services", json.dumps(api.get_services(), indent = 4)
    print "get_quota", json.dumps(api.get_quota(), indent = 4)
    print "get_events", json.dumps(api.get_events(), indent = 4)
    print "get_shares", json.dumps(api.get_shares(), indent = 4)
    print "get_reminders", json.dumps(api.get_reminders(True), indent = 4)
    print "get_lists", json.dumps(api.get_lists(True), indent = 4)
    print "get_tasks", json.dumps(api.get_tasks(True), indent = 4)
    print "get_tasks_by_list", json.dumps(api.get_tasks_by_list("ABjMAAbobFc", True), indent = 4)
    exit(0)
    print "create_list", json.dumps(api.create_list("Test List Again & Again"), indent = 4)
    print "create_task", json.dumps(api.create_task("test task mamam - tomorrow STAR", None, "ABjMAAbzjGQ", None, "true", "2014-07-16"), indent = 4)
    print "modify_list", json.dumps(api.modify_list("ABjMAAbzjGQ", "Test list 3"), indent = 4)
    print "modify_task", json.dumps(api.modify_task("ACjMACe43cs", "HAVE FUN!!! bianji", None, "ABjMAAbzjGQ", None, "false", "2014-07-26"), indent = 4)
    print "remove_list", json.dumps(api.remove_list("ABjMAAbzi1U"), indent = 4)
    print "remove_task", json.dumps(api.remove_task("ACjMACe43ac"), indent = 4)
    print "create_task", json.dumps(api.create_task(title = "New task assigned to Wei Ye", list_id = "ABjMAAbqDys", starred = "true", assignee_id = "AAAAAACSxWE"), indent = 4)
    print "modify_task", json.dumps(api.modify_task(task_id = "ACjMACe6j8w", title = "New task assigned to dd", list_id = "ABjMAAbqDys", starred = "false", assignee_id = "AAAAAACS0lE"), indent = 4)
    print "check_task", json.dumps(api.check_task("ACjMACe6j8w"), indent = 4)
    print "uncheck_task", json.dumps(api.uncheck_task("ACjMACe6j8w"), indent = 4)

