#!/usr/bin/python

import pycurl, StringIO, re, urllib, os, getpass, json, sys
from urllib import urlretrieve

def dlProgress(count, blockSize, totalSize):
    percent = int(count*blockSize*100/totalSize)
    yet = float(count*blockSize) / (1024.0 * 1024.0)
    tot = float(totalSize) / (1024.0 * 1024.0)
    sys.stdout.write("\r" + "%d%% %.2f/%.2f Mb" % (percent, yet, tot))
    sys.stdout.flush()
    
d = StringIO.StringIO()
c = pycurl.Curl()
vk_id = -1
    
def doLogin():
	global c, d, vk_id
	
	d = StringIO.StringIO()
	
	if os.path.exists('cookie.txt'):
		os.remove('cookie.txt')
		
	email = raw_input('E-Mail: ')
	passw = getpass.getpass()
	
	c.setopt(c.VERBOSE, 0)
	c.setopt(c.WRITEFUNCTION, d.write)
	c.setopt(c.COOKIEJAR, 'cookie.txt')
	c.setopt(c.COOKIEFILE, 'cookie.txt')
	c.setopt(c.URL, 'vk.com/login.php?email='+email+'&pass='+passw)
	c.perform()
	
	c.setopt(c.URL, 'http://vk.com/feed')
	c.setopt(c.WRITEFUNCTION, d.write)
	c.perform()
	
	data = d.getvalue()
	id_match = re.findall(r"id: (\d+),", data)
	if len(id_match) > 0:
		vk_id = int(id_match[0])		
	if vk_id != -1:
		return True
	else:
		return False
		
def getMusicList():
    global c, d, vk_id
	
    c.setopt(c.WRITEFUNCTION, d.write)
    c.setopt(c.URL, 'http://vk.com/audio')
    c.setopt(c.POST, 1)
    c.setopt(c.POSTFIELDS, 'act=load_audios_silent&al=1&edit=0&gid=0&id=' + str(vk_id))
    c.perform()
    c.close()
    s = d.getvalue()
    s = s.decode("cp1251").encode("utf-8")
    s = s[s.find('{"all":')+7:s.find('<!>{"sum')-1]
    s = s.replace("'", '"')
    return s	

if __name__ == "__main__":
	
    logged_in = doLogin()
    if logged_in:
        print >> sys.stderr, u"Succesfully logged in: id = %s." % vk_id
    else:
        print >> sys.stderr, u'Wrong password/e-mail :('
        exit(0)
    
    s = getMusicList()
   
    try:
		j = json.loads(s)
    except:
		print 'Error while parsing music list :('
		exit(0)

    files = 0
    for je in j:
        files = files + 1
    print 'Found %d files.' % (files)
    st = raw_input('Print all? y/n ')
    if st.startswith('y'):
		cnt = 1
		for je in j:
			print str(cnt) + '. %s - %s (%s)' % (je[5], je[6], je[4])
			cnt = cnt + 1
    print ''
    st = raw_input('Start downloading? y/n ')
    if st.startswith('y'):
				
		try:
			os.makedirs('vk_music')
		except OSError:
			pass
		cnt = 1
		for je in j:
			author = je[5]
			name = je[6]
			author = author.replace('/', ' and ').replace('\\', ' and ')
			name = name.replace('/', ' and ').replace('\\', ' and ')
			print str(cnt) + '. Downloading %s - %s (%s)' % (author, name, je[4])
			urlretrieve(je[2], 'vk_music/' + author + ' - ' + name + '.mp3', reporthook=dlProgress)
			print ' OK'
			cnt = cnt + 1
	
    if os.path.exists('cookie.txt'):
        os.remove('cookie.txt')
