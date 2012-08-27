#!/usr/bin/python

from vkmusic import VKMusic
from urllib import urlretrieve
import getpass, sys, os

def showProgress(count, blockSize, totalSize):
    percent = int(count*blockSize*100/totalSize)
    yet = float(count*blockSize) / (1024.0 * 1024.0)
    tot = float(totalSize) / (1024.0 * 1024.0)
    sys.stdout.write("\r" + "%d%% %.2f/%.2f Mb" % (percent, yet, tot))
    sys.stdout.flush()

if __name__ == "__main__":
    email = raw_input('E-Mail: ')
    passw = getpass.getpass()
    
    vk = VKMusic(email, passw)
	
    loggedIn = vk.isLoggedIn()
    if not loggedIn:
        print >> sys.stderr, u'Wrong password/e-mail :('
        exit(0)
   
        
    files = vk.filesCount()
    print 'Found %d files.' % (files)
    st = raw_input('Print all? [y]/n ')
    
    if not st.startswith('n'):
        for i in xrange(files):
            j = vk.fileInfo(i)
            print str(i + 1) + '. %s - %s (%s)' % (j[5], j[6], j[4])
            
    print ''
    st = raw_input('Start downloading? [y]/n ')
    if not st.startswith('n'):
				
        try:
            os.makedirs('vk_music')
        except OSError:
            pass
        for i in xrange(files):
            j = vk.fileInfo(i)
            author = j[5]
            name = j[6]
            author = author.replace('/', ' and ').replace('\\', ' and ')
            name = name.replace('/', ' and ').replace('\\', ' and ')
            print str(i + 1) + '. Downloading %s - %s (%s)' % (author, name, j[4])
            urlretrieve(j[2], 'vk_music/' + author + ' - ' + name + '.mp3', reporthook=showProgress)
            print ' OK'
            
    if os.path.exists('cookie.txt'):
        os.remove('cookie.txt')
