#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import socket
import StringIO
import gzip
import json
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
        self.apiurl_profile = "https://api.wunderlist.com/me"
        self.apiurl_settings = "https://api.wunderlist.com/me/settings"
        self.apiurl_contacts = "https://api.wunderlist.com/me/contacts"


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
    def wunderlist_api_call(self, request_url, request_headers, request_data = None):
        data = {}
        request_data = urllib.urlencode(request_data) if request_data else None
        api_request = urllib2.Request(url = request_url, headers = request_headers, data = request_data)
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


    # Wrapper for read-only Wunderlist private API call
    def wunderlist_api_call_read(self, url):
        self.login()
        headers = { 'Authorization' : self.token }
        return self.wunderlist_api_call(url, headers)


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
        return self.wunderlist_api_call_read(self.apiurl_profile)


    # Get user settings via https://api.wunderlist.com/me/settings
    def get_settings(self):
        return self.wunderlist_api_call_read(self.apiurl_settings)


    # Get user contacts via https://api.wunderlist.com/me/contacts
    def get_contacts(self):
        return self.wunderlist_api_call_read(self.apiurl_contacts)




if __name__ == '__main__':
    api = WunderlistAPI(email, password)
    print api.is_login, api.token
    api.login()
    print api.is_login, api.token
    print json.dumps(api.get_profile(), indent = 4)
    print json.dumps(api.get_settings(), indent = 4)
    print json.dumps(api.get_contacts(), indent = 4)

