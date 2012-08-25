#!/usr/bin/python

import pycurl, StringIO, re, urllib, os, getpass, json, sys
from urllib import urlretrieve

def dlProgress(count, blockSize, totalSize):
    percent = int(count*blockSize*100/totalSize)
    yet = float(count*blockSize) / (1024.0 * 1024.0)
    tot = float(totalSize) / (1024.0 * 1024.0)
    sys.stdout.write("\r" + "%d%% %.2f/%.2f Mb" % (percent, yet, tot))
    sys.stdout.flush()

if __name__ == "__main__":
    email = 'o'
    passw = 'o'
    uid = ""
    d = StringIO.StringIO()
    c = pycurl.Curl()
    c.setopt(c.COOKIEJAR, 'cookie.txt')
    c.setopt(c.COOKIEFILE, 'cookie.txt')
    c.setopt(c.URL, 'vk.com/login.php?email='+email+'&pass='+passw)
    c.perform()
    c.setopt(c.WRITEFUNCTION, d.write)
    c.setopt(c.URL, 'http://vk.com/audio')
    c.setopt(c.POST, 1)
    c.setopt(c.POSTFIELDS, 'act=load_audios_silent&al=1&edit=0&gid=0&id='+uid)
    c.perform()
    c.close()
    s = d.getvalue()
    s = s.decode("cp1251").encode("utf-8")
    s = s[s.find('{"all":')+7:s.find('<!>{"sum')-1]
    s = s.replace("'", '"')
    
    j = json.loads(s)
    
    try:
        os.makedirs('vk_music')
    except OSError:
        pass
    cnt = 0
    for je in j:
		cnt = cnt + 1
    print 'Found %d files.' % (cnt)
    cnt = 1
    for je in j:
        author = je[5]
        name = je[6]
        author = author.replace('/', ' and ')
        name = name.replace('/', ' and ')
        author = author.replace('\\', ' and ')
        name = name.replace('\\', ' and ')
        print str(cnt) + '. Downloading %s - %s (%s)' % (author, name, je[4])
        urlretrieve(je[2], r'vk_music/' + author + ' - ' + name + '.mp3', reporthook=dlProgress)
        print ' OK'
        cnt = cnt + 1
