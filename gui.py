#!/usr/bin/python

from gi.repository import Gtk
#from vkmusic import VKMusic

class VKGtk(Gtk.Window):
    
    def __init__(self):
        super(self.__class__, self).__init__()
        
        self.p = False
        
        self.st = st = Gtk.Notebook()
        
        align = Gtk.Alignment.new(0.5, 0.5, 0.6, 0.0)
        
        mailEntry = Gtk.Entry()
        passEntry = Gtk.Entry()
        passEntry.set_invisible_char(u'\u2022')
        passEntry.set_visibility(False)
        self.mailEntry = mailEntry
        self.passEntry = passEntry
        
        loginButton = Gtk.Button("Login")
        loginButton.connect("clicked", self.on_login)
        
        table = Gtk.Table(3, 3, True)
        table.attach(Gtk.Label("E-Mail"),   0, 1, 0, 1)
        table.attach(Gtk.Label("Password"), 0, 1, 1, 2)
        table.attach(mailEntry,             1, 3, 0, 1)
        table.attach(passEntry,             1, 3, 1, 2)
        table.attach(loginButton,           2, 3, 2, 3)
        
        align.add(table)
        st.append_page(align)
        
        st.set_show_tabs(False)
        self.add(st)
        
        self.connect("destroy", Gtk.main_quit)
        self.set_title("VKMusicDownloader")
        self.set_size_request(500, 300)
        self.show_all()
        
    def createMusicPage(self):
        vbox = Gtk.VBox()
        
        store = Gtk.ListStore(bool, int, str, str, str)
        self.store = store
        fc = self.vk.filesCount()
        for i in range(fc):
            fi = self.vk.fileInfo(i)
            l = [True, i + 1, fi.author, fi.title, fi.duration]
            store.append(l)
        
        tree = Gtk.TreeView(store)
        tree.set_rules_hint(True)
        
        renderer = Gtk.CellRendererToggle()
        column = Gtk.TreeViewColumn("Download", renderer, active = 0)
        renderer.connect("toggled", self.cell_toggled, store)
        column.set_sort_column_id(0)
        tree.append_column(column)
        columns = ['#', 'Artist', 'Title', 'Duration']
        for i in range(len(columns)):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(columns[i], renderer, text=i+1)
            column.set_sort_column_id(i+1)
            tree.append_column(column)
            
        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.SHADOW_ETCHED_IN)
        sw.set_policy(Gtk.POLICY_AUTOMATIC, Gtk.POLICY_AUTOMATIC)
        sw.add(tree)
        self.tree = tree
        vbox.add(sw)
        downloadButton = Gtk.Button("Download")
        downloadButton.connect("clicked", self.on_download)
        al = Gtk.Alignment(1, 1, 0, 0)
        al.add(downloadButton)
        vbox.pack_start(al, False)
        return vbox
        
    def createDownloadPage(self):
        al = Gtk.Alignment(0.5, 0.5, 0.8, 0)
        vbox = Gtk.VBox()
        alLabel = Gtk.Alignment(0, 0, 0, 0)
        alLabel.add(Gtk.Label("Total"))
        vbox.add(alLabel)
        self.totalProgress = Gtk.ProgressBar()
        vbox.add(self.totalProgress)
        alLabel = Gtk.Alignment(0, 0, 0, 0)
        self.progressLabel = Gtk.Label("Current")
        alLabel.add(self.progressLabel)
        vbox.add(alLabel)
        self.localProgress = Gtk.ProgressBar()
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
        for i in range(self.fc):
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
        Gtk.main_iteration()
        
    def cell_toggled(self, widget, path, model):
        model[path][0] = not model[path][0]
        if model[path][0]:
            self.dc -= 1
        else:
            self.dc += 1

def run():
    window = VKGtk()
    Gtk.main()

if __name__ == "__main__":
    run()
