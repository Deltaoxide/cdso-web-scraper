import src
from bs4 import BeautifulSoup
import atexit
import time
import cmd, sys

class CmdLoop(cmd.Cmd):
    intro = 'Welcome to the CDSO shell.   Type help or ? to list commands.\n'
    prompt="<CDSO_Shell> "
    

    def do_request(self,arg):
        'Send Notification'
        return src.new_request()
    
    def do_startlistener(self,arg):
        'Start Listener'
        listener = src.Listener()
        listener.start()
        
    def do_exit(self, arg):
        'Exit the shell'
        print("Exiting...")
        return True
    

        
if __name__ == "__main__":
    atexit.register(src.NtfyManager().send_stop_notification)
    CmdLoop().cmdloop()