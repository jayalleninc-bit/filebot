from dataclasses import dataclass
from pathlib import Path
@dataclass
class Ctx: series=None; season=None; episode=None; absolute=None; title=None; year=None
def rend(pat:str, c:Ctx, ext:str)->Path:
    s=lambda x:(x or '').replace('/','-').strip()
    d={'series':s(c.series),'season':c.season or 0,'episode':c.episode or 0,'absolute':c.absolute or 0,'title':s(c.title),'year':c.year or 0}
    return Path(pat.format(**d)+ext)
