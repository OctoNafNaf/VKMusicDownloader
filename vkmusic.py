#!/usr/bin/python

import re, urllib, os, json, sys, http.cookiejar
from urllib.request import urlretrieve
from html.parser import HTMLParser
from urllib.parse import urlparse

class FormParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.url = None
        self.params = {}
        self.in_form = False
        self.form_parsed = False
        self.method = "GET"

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == "form":
            if self.form_parsed:
                raise RuntimeError("Second form on page")
            if self.in_form:
                raise RuntimeError("Already in form")
            self.in_form = True 
        if not self.in_form:
            return
        attrs = dict((name.lower(), value) for name, value in attrs)
        if tag == "form":
            self.url = attrs["action"] 
            if "method" in attrs:
                self.method = attrs["method"]
        elif tag == "input" and "type" in attrs and "name" in attrs:
            if attrs["type"] in ["hidden", "text", "password"]:
                self.params[attrs["name"]] = attrs["value"] if "value" in attrs else ""

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "form":
            if not self.in_form:
                raise RuntimeError("Unexpected end of <form>")
            self.in_form = False
            self.form_parsed = True

class VKMusic:
    at_file = '.access_token'
    fdir = 'vk_music'
    client_id = '3321812'
    scope = ['audio', 'offline']

    def __init__(self, email=None, passw=None, cookie='cookie.txt'):
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
                         urllib.request.HTTPRedirectHandler())
        self.opener = opener
        if not email or not passw:
            try:
                self.access_token = self.loadAccessToken()
            except:
                raise VKMusicError('Token file not found')
            self.loggedIn = self.testAccessToken()
        else:
            self.cookieFile = cookie
            if os.path.exists(self.cookieFile):
                os.remove(self.cookieFile)
            self.loggedIn = self.doLogin(email, passw)

        if self.loggedIn:
            self.mlist = self.getMusicList()

    def __del__(self):
        if os.path.exists(self.cookieFile):
            os.remove(self.cookieFile)
    
    def doLogin(self, email, passw):
        opener = self.opener
        response = opener.open("http://oauth.vk.com/oauth/authorize?" + \
                               "redirect_uri=http://oauth.vk.com/blank.html&" + \
                               "response_type=token&" + \
                               "client_id=%s&scope=%s&display=wap" % (self.client_id, ",".join(self.scope))
                              )
        doc = response.read()
        parser = FormParser()
        parser.feed(doc)
        parser.close()
        if not parser.form_parsed or parser.url is None or "pass" not in parser.params or \
          "email" not in parser.params:
              raise RuntimeError("Something wrong")
        parser.params["email"] = email
        parser.params["pass"] = passw
        if parser.method == "post":
            #parser.url = parser.url.replace('https', 'http')
            response = opener.open(parser.url, urllib.parse.urlencode(parser.params))
        doc = response.read()   
        
        parser = FormParser()
        parser.feed(doc)
        parser.close()
        if urlparse(response.url).path != "/blank.html":
            if not parser.form_parsed or parser.url is None:
                  raise RuntimeError("Something wrong")
            if parser.method == "post":
                response = opener.open(parser.url, urllib.parse.urlencode(parser.params))
            else:
                raise NotImplementedError("Method '%s'" % params.method)
        url = response.geturl()
        def split_key_value(kv_pair):
            kv = kv_pair.split("=")
            return kv[0], kv[1]
        answer = dict(split_key_value(kv_pair) for kv_pair in urlparse(url).fragment.split("&"))
        if "access_token" not in answer or "user_id" not in answer:
            return False
        else:
            self.access_token = answer["access_token"]
            self.saveAccessToken(self.access_token)
            self.vk_id = answer["user_id"] 
            return True

    def testAccessToken(self):
        users = self.apiMethod('users.get')
        if isinstance(users, list):
            self.vk_id = users[0]['uid'] or None
            return self.vk_id != None
        return False
 
    def saveAccessToken(self, access_token):
        with open(self.at_file, 'w') as f:
            f.write(access_token)

    def loadAccessToken(self):
        with open(self.at_file) as f:
            return f.read().strip()

    def apiMethod(self, name, **kvargs):
        opener = self.opener
        kvargs['access_token'] = self.access_token
        response = opener.open('https://api.vk.com/method/' + name,
                               bytearray(urllib.parse.urlencode(kvargs), 'utf-8'))
        return json.loads(response.read().decode("utf-8"))['response']
            
    def getMusicList(self):
        mlist = self.apiMethod("audio.get", uid = self.vk_id, count=144)
        self.count = len(mlist)
        return mlist
        
    def isLoggedIn(self):
        return self.loggedIn
        
    def filesCount(self):
        return self.count
        
    def fileInfo(self, i):
        return FileInfo(self.mlist[i])
        
    def setDir(self, newdir):
        self.fdir = newdir
    
    def fileDownload(self, i, fname, sfunc):
        try:
            os.makedirs(self.fdir)
        except OSError:
            pass
        link = self.fileInfo(i).link
        path = os.path.join(self.fdir, fname)
        urlretrieve(link, path, sfunc)
        
class VKMusicError(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)

class FileInfo:
    def __init__(self, fi):
        self.uid = fi['aid']
        self.srcuid = fi['owner_id']
        self.link = fi['url']
        self.duration = fi['duration']
        self.author = fi['artist']
        self.title = fi['title']
        
    def strFormat(self):
        return '%s - %s (%s)' % (self.author, self.title, self.duration)
        
    def pathAuthor(self):
        return self.author.replace('/', ' and ').replace('\\', ' and ')
        
    def pathTitle(self):
        return self.title.replace('/', ' and ').replace('\\', ' and ')
