import os

if os.name == 'nt':
    is_win = True
    is_linux = False
    is_mac = False
else:
    import sys

    is_win = False
    plat = sys.platform.lower()
    is_mac = plat[:6] == 'darwin'
    is_linux = not is_mac
