#!/usr/bin/python

import gtk
from vkmusic import VKMusic

class VKGtk(gtk.Window):
    
    def __init__(self):
        super(self.__class__, self).__init__()
        
        self.p = False
        
        self.st = st = gtk.Notebook()
        
        align = gtk.Alignment(0.5, 0.5, 0.6, 0)
        
        mailEntry = gtk.Entry()
        passEntry = gtk.Entry()
        passEntry.set_invisible_char(u'\u2022')
        passEntry.set_visibility(False)
        self.mailEntry = mailEntry
        self.passEntry = passEntry
        
        loginButton = gtk.Button("Login")
        loginButton.connect("clicked", self.on_login)
        
        table = gtk.Table(3, 3, True)
        table.attach(gtk.Label("E-Mail"),   0, 1, 0, 1)
        table.attach(gtk.Label("Password"), 0, 1, 1, 2)
        table.attach(mailEntry,             1, 3, 0, 1)
        table.attach(passEntry,             1, 3, 1, 2)
        table.attach(loginButton,           2, 3, 2, 3)
        
        align.add(table)
        st.append_page(align)
        
        st.set_show_tabs(False)
        self.add(st)
        
        self.connect("destroy", gtk.main_quit)
        self.set_title("VKMusicDownloader")
        self.set_size_request(500, 300)
        self.show_all()
        
    def createMusicPage(self):
        vbox = gtk.VBox()
        
        store = gtk.ListStore(bool, int, str, str, str)
        self.store = store
        fc = self.vk.filesCount()
        for i in xrange(fc):
            fi = self.vk.fileInfo(i)
            l = [True, i + 1, fi.author, fi.title, fi.duration]
            store.append(l)
        
        tree = gtk.TreeView(store)
        tree.set_rules_hint(True)
        
        renderer = gtk.CellRendererToggle()
        column = gtk.TreeViewColumn("Download", renderer, active = 0)
        renderer.connect("toggled", self.cell_toggled, store)
        column.set_sort_column_id(0)
        tree.append_column(column)
        columns = ['#', 'Artist', 'Title', 'Duration']
        for i in xrange(len(columns)):
            renderer = gtk.CellRendererText()
            column = gtk.TreeViewColumn(columns[i], renderer, text=i+1)
            column.set_sort_column_id(i+1)
            tree.append_column(column)
            
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(tree)
        self.tree = tree
        vbox.add(sw)
        downloadButton = gtk.Button("Download")
        downloadButton.connect("clicked", self.on_download)
        al = gtk.Alignment(1, 1, 0, 0)
        al.add(downloadButton)
        vbox.pack_start(al, False)
        return vbox
        
    def createDownloadPage(self):
        al = gtk.Alignment(0.5, 0.5, 0.8, 0)
        vbox = gtk.VBox()
        alLabel = gtk.Alignment(0, 0, 0, 0)
        alLabel.add(gtk.Label("Total"))
        vbox.add(alLabel)
        self.totalProgress = gtk.ProgressBar()
        vbox.add(self.totalProgress)
        alLabel = gtk.Alignment(0, 0, 0, 0)
        self.progressLabel = gtk.Label("Current")
        alLabel.add(self.progressLabel)
        vbox.add(alLabel)
        self.localProgress = gtk.ProgressBar()
        vbox.add(self.localProgress)
        vbox.set_spacing(5)
        al.add(vbox)
        return al
        
    def on_login(self, button):
        email = self.mailEntry.get_text()
        passw = self.passEntry.get_text()
        self.vk = VKMusic(email, passw)
        self.dc = self.fc = self.vk.filesCount()
        if self.vk.isLoggedIn():
            self.st.append_page(self.createMusicPage())
            self.resize(800, 500)
            self.show_all()
            self.st.next_page()
            
    def on_download(self, button):
        self.st.append_page(self.createDownloadPage())
        self.resize(500, 300)
        self.show_all()
        self.st.next_page()
        self.k = 0
        for i in xrange(self.fc):
            if self.store[i][0]:
                fi = self.vk.fileInfo(i)
                text = "%d. %s" % (i + 1, fi.strFormat())
                self.progressLabel.set_text(text)
                fname = "%s - %s.mp3" % (fi.pathAuthor(), fi.pathTitle())
                self.vk.fileDownload(i, fname, self.show_progress)
                self.k += 1
            
    def show_progress(self, a, b, c):
        lp = float(a * b) / c
        tp = float(self.k) / self.dc + lp / self.dc
        self.totalProgress.set_fraction(tp)
        self.totalProgress.set_text("%.2f%%" % (tp * 100))
        self.localProgress.set_fraction(lp)
        self.localProgress.set_text("%.2f%%" % (lp * 100))
        gtk.main_iteration()
        
    def cell_toggled(self, widget, path, model):
        model[path][0] = not model[path][0]
        if model[path][0]:
            self.dc -= 1
        else:
            self.dc += 1

def run():
    window = VKGtk()
    gtk.main()

if __name__ == "__main__":
    run()
