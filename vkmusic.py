#!/usr/bin/python

import pycurl, StringIO, re, urllib, os, getpass, json, sys
from urllib import urlretrieve

class VKMusic:
    def __init__(self, email, passw):
        if os.path.exists('cookie.txt'):
            os.remove('cookie.txt')
        self.loggedIn = self.doLogin(email, passw)
        self.mlist = self.getMusicList()
    
    def doLogin(self, email, passw):
        d = self.d = StringIO.StringIO()
        c = self.c = pycurl.Curl()

        c.setopt(c.VERBOSE, 0)
        c.setopt(c.WRITEFUNCTION, d.write)
        c.setopt(c.COOKIEJAR, 'cookie.txt')
        c.setopt(c.COOKIEFILE, 'cookie.txt')
        c.setopt(c.URL, 'vk.com/login.php?email=' + 
                            email + '&pass=' + passw)
        c.perform()
        c.setopt(c.URL, 'vk.com/feed')
        c.setopt(c.WRITEFUNCTION, d.write)
        c.perform()
        data = d.getvalue()
        id_match = re.findall(r"id: (\d+),", data)
        if len(id_match) > 0:
            vk_id = int(id_match[0])
        self.vk_id = vk_id
        if vk_id != -1:
            return True
        else:
            return False
            
    def getMusicList(self):
        c = self.c
        d = self.d
        vk_id = self.vk_id
        
        c.setopt(c.WRITEFUNCTION, d.write)
        c.setopt(c.URL, 'http://vk.com/audio')
        c.setopt(c.POST, 1)
        c.setopt(c.POSTFIELDS, 
                    'act=load_audios_silent&al=1&edit=0&gid=0&id=' + 
                    str(vk_id))
        c.perform()
        c.close()
        s = d.getvalue()
        s = s.decode("cp1251").encode("utf-8")
        s = s[s.find('{"all":')+7:s.find('<!>{"sum')-1]
        s = s.replace("'", '"')
        try:
            j = json.loads(s)
        except:
            print 'Error while parsing music list :('
            exit(1)
        return j
            
    def isLoggedIn(self):
        return self.loggedIn
        
    def filesCount(self):
        return len(self.mlist)
        
    def fileInfo(self, i):
        return self.mlist[i]
