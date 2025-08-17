import requests
class TVDB:
  def __init__(self,api_key:str,pin:str|None=None):
    self.k=api_key; self.pin=pin; self.b='https://api4.thetvdb.com/v4'; self.s=requests.Session(); self.t=None
    if api_key: self._login()
  def _login(self):
    r=self.s.post(self.b+'/login',json={'apikey':self.k,**({'pin':self.pin} if self.pin else {})},timeout=20); r.raise_for_status(); self.t=r.json().get('data',{}).get('token'); self.s.headers.update({'Authorization':f'Bearer {self.t}'})
  def search_series(self,q):
    if not self.t: return None
    r=self.s.get(self.b+'/search',params={'q':q,'type':'series'},timeout=20); r.raise_for_status(); d=r.json().get('data') or []; return d[0] if d else None
  def episodes_with_absolute(self,series_id:int):
    if not self.t: return []
    r=self.s.get(f'{self.b}/series/{series_id}/episodes/default',timeout=20); r.raise_for_status(); d=r.json().get('data') or {}; return d.get('episodes') or []
  def build_absolute_map(self,series_id:int):
    m={}
    for e in self.episodes_with_absolute(series_id):
      a=e.get('absoluteNumber'); s=e.get('seasonNumber'); n=e.get('number')
      if a and s and n: m[int(a)]={'season':int(s),'episode':int(n)}
    return m
