#!/usr/bin/python

import sys, tui, gui

if __name__ == "__main__":
    args = sys.argv
    if len(args) == 1:
        vopt = 'tui'
    else:
        vopt = args[1]
    if vopt == 'tui':
        tui.run()
    elif vopt == 'gui':
        gui.run()
    else:
        print "Unknown option '%s'" % vopt
