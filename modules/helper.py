from datetime import datetime

def str_to_datetime(s):
    import re
    t = [int(x) for x in re.findall(r"(.*)-(.*)-([0-9]*) (.*):(.*):([0-9]*)", s)[0] \
         if len(x) > 0]
    return datetime(*t)
