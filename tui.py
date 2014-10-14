#!/usr/bin/python

from vkmusic import VKMusic, VKMusicError
from urllib import urlretrieve
import getpass, sys, os

def userError(msg):
    print(msg, file=sys.stderr)
    exit(0)

def login():
    email = raw_input('E-Mail: ')
    passw = getpass.getpass()
    vk = VKMusic(email, passw)
    loggedIn = vk.isLoggedIn()
    if not loggedIn:
        userError(u'Wrong password/e-mail :(')
    return vk
    
def select(msg, choice, default):
    sp = ('/'.join(choice))
    sp = sp.replace(default, '[%s]' % default)
    s = input("%s (%s): " % (msg, sp))
    if (len(s) > 0) and (s[0] in choice):
        return s[0]
    return default
    
def showFiles(vk):
    files = vk.filesCount()
    print('Found %d files.' % (files))
    st = select('Print all?', 'yn', 'y')
    if st == 'y':
        for i in range(files):
            j = vk.fileInfo(i)
            print(str(i + 1) + '. ' + j.strFormat())
            
def download(vk):
    st = select('Start downloading?', 'yn', 'y')
    if st == 'y':
        for i in range(vk.filesCount()):
            j = vk.fileInfo(i)
            author = j.pathAuthor()
            name = j.pathTitle()
            print(str(i + 1) + '. Downloading ' + j.strFormat())
            vk.fileDownload(i, "%s - %s.mp3" % (author, name), showProgress)
            print(' OK')

def showProgress(count, blockSize, totalSize):
    percent = int(count*blockSize*100/totalSize)
    yet = float(count*blockSize) / (1024.0 * 1024.0)
    tot = float(totalSize) / (1024.0 * 1024.0)
    sys.stdout.write("\r" + "%d%% %.2f/%.2f Mb" % (percent, yet, tot))
    sys.stdout.flush()

def run():
    vk = None
    try:
        vk = VKMusic()
        print('from access_token')
    except VKMusicError:
        print('auth')
        vk = login()
    showFiles(vk)   
    print()
    download(vk)
        
if __name__ == "__main__":
    run()
