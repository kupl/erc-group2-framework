from rich.panel import Panel
import os

def clear_terminal():
    # Windows 운영 체제
    if os.name == 'nt':
        _ = os.system('cls')

    # macOS, Linux 운영 체제
    else:
        _ = os.system('clear')

PANEL_TITLE = "ERC"
PANEL_BORDER_STYLE = "blue"

class MyPanel():
    def __init__(self) :
        self.buffer = ""
        self.msg = ""

    def flush(self):
        self.buffer = ""
        self.msg = ""

    def get_panel(self, msg) :
        clear_terminal()
        self.buffer += self.msg + "\n"
        if self.buffer == "\n":
            self.buffer = ""
        self.msg = msg
        return Panel(self.buffer + self.msg, title=PANEL_TITLE, border_style=PANEL_BORDER_STYLE, expand=False)
    
    def update(self, msg) :
        self.msg = msg
        return Panel(self.buffer + self.msg, title=PANEL_TITLE, border_style=PANEL_BORDER_STYLE, expand=False)
    
MY_PANEL = MyPanel()

# def get_panel(msg) :
#     return Panel(msg, title=PANEL_TITLE, border_style=PANEL_BORDER_STYLE)



