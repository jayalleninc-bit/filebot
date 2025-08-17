import requests
class TMDb:
  def __init__(self,api_key:str,language='en-US'):
    self.b='https://api.themoviedb.org/3'; self.k=api_key; self.l=language; self.s=requests.Session()
  def _get(self,p,**q): q.setdefault('api_key',self.k); q.setdefault('language',self.l); r=self.s.get(self.b+p,params=q,timeout=20); r.raise_for_status(); return r.json()
  def search_movie(self,q,year=None):
    d=self._get('/search/movie',query=q,include_adult=False,year=year) if year else self._get('/search/movie',query=q,include_adult=False); r=d.get('results') or []; return r[0] if r else None
  def search_tv(self,q,year=None):
    d=self._get('/search/tv',query=q,include_adult=False,first_air_date_year=year) if year else self._get('/search/tv',query=q,include_adult=False); r=d.get('results') or []; return r[0] if r else None
  def episode_title(self,tv,sea,ep):
    try: return self._get(f'/tv/{tv}/season/{sea}/episode/{ep}').get('name')
    except Exception: return None
