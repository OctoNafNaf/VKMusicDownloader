import sys

if __name__ == "__main__":
    args = sys.argv
    if len(args) == 1:
        vopt = 'tui'
    else:
        vopt = args[1]
    if vopt == 'tui':
        import tui
        tui.run()
    elif vopt == 'gui':
        import gui
        gui.run()
    else:
        print "Unknown option '%s'" % vopt
