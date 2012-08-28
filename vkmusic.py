#!/usr/bin/python

import pycurl, StringIO, re, urllib, os, getpass, json, sys
from urllib import urlretrieve

class VKMusic:
    fdir = 'vk_music'

    def __init__(self, email, passw, cookie='cookie.txt'):
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
        d = self.d = StringIO.StringIO()
        c = self.c = pycurl.Curl()

        c.setopt(c.VERBOSE, 0)
        c.setopt(c.WRITEFUNCTION, d.write)
        c.setopt(c.COOKIEJAR, self.cookieFile)
        c.setopt(c.COOKIEFILE, self.cookieFile)
        c.setopt(c.URL, 'vk.com/login.php?email=' + 
                            email + '&pass=' + passw)
        c.perform()
        c.setopt(c.URL, 'vk.com/feed')
        c.setopt(c.WRITEFUNCTION, d.write)
        c.perform()
        data = d.getvalue()
        id_match = re.findall(r"id: (\d+),", data)
        vk_id = -1
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
        
class FileInfo:
    def __init__(self, fi):
        self.uid = fi[0]
        self.srcuid = fi[1]
        self.link = fi[2]
        self.duration = fi[4]
        self.author = fi[5]
        self.title = fi[6]
        
    def strFormat(self):
        return '%s - %s (%s)' % (self.author, self.title, self.duration)
        
    def pathAuthor(self):
        return self.author.replace('/', ' and ').replace('\\', ' and ')
        
    def pathTitle(self):
        return self.title.replace('/', ' and ').replace('\\', ' and ')
        
