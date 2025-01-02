import src
from bs4 import BeautifulSoup
import atexit
import time
import cmd, sys

class CmdLoop(cmd.Cmd):
    intro = 'Welcome to the CDSO shell.   Type help or ? to list commands.\n'
    prompt="<CDSO_Shell> "
    

    def do_postntfy(self,arg):
        'Send Notification'
        ntfy_manager = src.NtfyManager()
        ntfy_manager.send_ticket_notification("Yeni Bilet Çıktı")
        

    def do_stopntfy(self,arg):
        'Stop Notification'
        ntfy_manager = src.NtfyManager()
        ntfy_manager.send_stop_notification()
        
    def do_startntfy(self,arg):
        'Start Notification'
        ntfy_manager = src.NtfyManager()
        ntfy_manager.send_init_notification()
    
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