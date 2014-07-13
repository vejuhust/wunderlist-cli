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


    # Login with account and password
    def wunderlist_login(self, email, password):
        data = {}
        login_data = { 'email' : self.account_email, 'password' : self.account_password }
        login_request = urllib2.Request(url = self.login_url, headers = self.login_headers, data = urllib.urlencode(login_data))
        try:
            login_response = urllib2.urlopen(login_request, timeout = 5)
        except urllib2.URLError, error:
            error_code = error.code if hasattr(error, 'code') else ''
            error_reason = error.reason if hasattr(error, 'reason') else ''
            print "Login Error:", error_code, error_reason
        except Exception as error:
            print "Login Error:", error
        else:
            content = self.decode_content(login_response)
            self.tokenfile_save(content)
            data = json.loads(content)
        return data


    # Check login status and get token
    def login(self):
        if not self.is_login or len(self.token) == 0:
            try:
                data = self.tokenfile_load()
                self.token = data['token']
            except Exception as error:
                print "Load Error:", error
                data = self.wunderlist_login(email, password)
                self.token = data['token'] if data.has_key('token') else ''
            finally:
                if len(self.token) > 0:
                    self.is_login = True
                #print json.dumps(data, sort_keys = True, indent = 4)




if __name__ == '__main__':
    api = WunderlistAPI(email, password)
    print api.is_login, api.token
    api.login()
    print api.is_login, api.token

