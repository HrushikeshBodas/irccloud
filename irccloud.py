# A Simple script to keep an irc cloud client always alive
__author__ = "S Vijaikumar"
__email__  = "vijai@vijaikumar.in"
__copyright__ = "Copyright (C) 2017 S Vijai Kumar"
__license__ = "MIT"
__version__ = "1.0"

import requests
import time
import datetime
import sys
import traceback
from os import environ

class irccloud:
    """
    This is a very simple class that takes an user's irc user name
    and password as input and keeps the connection alive to emulate
    the hearbeat produced due to real browser activity
    """
    AuthenticationToken = ""
    SessionId = ""
    KeepAliveToken = ""

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def get_authentication_token(self):
        url = "https://www.irccloud.com/chat/auth-formtoken"
        r = requests.post(url)
        response = r.json()
        if response["success"]:
            print "------> Successfully obtained authentication token."
            irccloud.AuthenticationToken = response["token"]
        else:
            print "------> Failed to obtain an authentication token."
            irccloud.AuthenticationToken = "AUTH_FAILURE"

    def get_session_id(self):
        self.get_authentication_token()
        if irccloud.AuthenticationToken == "AUTH_FAILURE":
            return irccloud.AuthenticationToken
        else:
            login_url = "https://www.irccloud.com/chat/login"
            headers = {
                "content-type": "application/x-www-form-urlencoded",
                "x-auth-formtoken":irccloud.AuthenticationToken
            }
            login_data = {
                "email" : self.email,
                "password" : self.password,
                "token" : irccloud.AuthenticationToken
            }
            r = requests.post(login_url, data = login_data, headers = headers)
            response = r.json()
            if response["success"]:
                print "------> Successfully obtained a session id."
                irccloud.SessionId = response["session"]
            else:
                print "------> Failed to obtain a session id."
                irccloud.SessionId = "SESSION_FAILURE"

    def keep_alive(self):
        stream_url = "https://www.irccloud.com/chat/stream"
        headers = {"Connection" : "keep-alive",
                   "Accept-Encoding" : "gzip,deflate,sdch",
                   "User-Agent" : "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.53 Safari/525.19",
                   "Cookie": "session={0}".format(irccloud.SessionId),
                   "Host":"www.irccloud.com"
        }
        r = requests.post(stream_url, headers = headers)
        if r.status_code == 200:
            irccloud.KeepAliveToken = "KA_ALIVE"
        else:
            irccloud.KeepAliveToken = "KA_DEAD"

    def runner(self):
        self.get_session_id()
        now = datetime.datetime.now()
        print "=================================="
        print "    IRC Cloud Keep alive Func     "
        print "=================================="
        if irccloud.SessionId == "SESSION_FAILURE":
            print "------> [{0}] Couldn't get a session initialized. Quitting.. :)".format(now.strftime("%Y-%m-%d %H:%M"))
            sys.exit(0)
        else:
            self.keep_alive()
            if irccloud.KeepAliveToken == "KA_ALIVE":
                print "------> [{0}] IRC Cloud Session is Kept alive.".format(now.strftime("%Y-%m-%d %H:%M"))
            else:
                print "------> [{0}] IRC Cloud Session could not be Kept alive.".format(now.strftime("%Y-%m-%d %H:%M"))


if __name__ == "__main__":
    try:
        email = environ.get("IRCCLOUD_USERNAME")
        password = environ.get("IRCCLOUD_PASSWORD")
        irc = irccloud(email, password)
        irc.runner()
    except KeyboardInterrupt:
        print "----> Shutdown requested. Exiting script. Thank you :)"
        sys.exit(0)
    except Exception:
        traceback.print_exc(file=sys.stdout)
        sys.exit(0)
