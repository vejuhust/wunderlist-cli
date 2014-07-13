#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import socket
import StringIO
import gzip
import json
from auth import email, password



login_url = "https://api.wunderlist.com/login"
login_headers = {
    'Accept' : 'application/json',
    'Accept-Encoding' : 'gzip,deflate',
    'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
    'Host' : 'api.wunderlist.com',
    'Origin' : 'https://www.wunderlist.com',
}
token_filename = "token.json"


# Decode gzipped response content
def decode_content(retval):
    if retval.info().has_key('content-encoding'):
        fileobj = StringIO.StringIO()
        fileobj.write(retval.read())
        fileobj.seek(0)
        gzip_file = gzip.GzipFile(fileobj=fileobj)
        content = gzip_file.read()
    else:
        content = retval.read()
    return content


# Save token in a file
def token_save(content):
    file = open(token_filename, "w")
    file.write(content)
    file.close()


# Load token from a file
def token_load():
    file = open(token_filename, "r")
    content = file.read()
    file.close()
    return json.loads(content)


# Login with account and password
def login(email, password):
    data = {}
    login_data = { 'email' : email, 'password' : password }
    login_request = urllib2.Request(url = login_url, headers = login_headers, data = urllib.urlencode(login_data))
    try:
        login_response = urllib2.urlopen(login_request, timeout = 5)
    except urllib2.URLError, error:
        error_code = error.code if hasattr(error, 'code') else ''
        error_reason = error.reason if hasattr(error, 'reason') else ''
        print "Error:", error_code, error_reason
    except Exception as error:
        print "Error:", error
    else:
        content = decode_content(login_response)
        token_save(content)
        data = json.loads(content)
    return data


try:
    data = token_load()
except Exception as error:
    data = login(email, password)
finally:
    print json.dumps(data, sort_keys = True, indent = 4)


exit(0)
