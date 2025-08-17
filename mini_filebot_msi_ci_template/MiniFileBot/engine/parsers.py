import re
from guessit import guessit
ABS=re.compile(r'(?<!\d)(\d{3,4})(?!\d)')
def parse_filename(name:str)->dict:
    info=guessit(name)
    m=ABS.search(name)
    if m and info.get('type')!='movie' and 'episode' not in info:
        info['type']='episode'; info['absolute']=int(m.group(1)); info.setdefault('anime',True)
    return info
