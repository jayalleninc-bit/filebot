import os
from dataclasses import dataclass
from pathlib import Path
from typing import List
import yaml
from .parsers import parse_filename
from .providers.tmdb import TMDb
from .providers.tvdb import TVDB
from .providers.anilist import AniList
from .renamers import Ctx, rend
from .utils import apply_action

VIDEO={'.mkv','.mp4','.avi','.mov','.wmv','.m4v','.ts'}

@dataclass
class Settings:
  movie_dir: Path; tv_dir: Path; pattern_movie: str; pattern_episode: str; pattern_anime_abs: str
  action: str; dry_run: bool; skip_samples: bool; max_depth: int; preference: str

class Engine:
  def __init__(self,cfg:dict):
    paths=cfg.get('paths',{}); prov=cfg.get('providers',{}); beh=cfg.get('behavior',{}); patt=cfg.get('patterns',{})
    self.s=Settings(Path(paths.get('movie_dir','./Movies')),Path(paths.get('tv_dir','./TV')),
      patt.get('movie','{title} ({year})/{title} ({year})'),
      patt.get('episode','{series}/Season {season:02}/{series} - S{season:02}E{episode:02} - {title}'),
      patt.get('anime_absolute','{series}/{series} - {absolute:03}'),
      beh.get('action','move'),beh.get('dry_run',True),beh.get('skip_samples',True),int(beh.get('max_depth',5)),prov.get('preference','Auto'))
    tm=prov.get('tmdb',{}); tv=prov.get('tvdb',{}); an=prov.get('anilist',{})
    self.tmdb=TMDb(api_key=os.getenv('TMDB_API_KEY',tm.get('api_key','')),language=tm.get('language','en-US'))
    self.tvdb=None; k=os.getenv('TVDB_API_KEY',tv.get('api_key',''))
    if k: self.tvdb=TVDB(api_key=k,pin=os.getenv('TVDB_PIN',tv.get('pin')))
    self.anilist= AniList() if an.get('enabled',True) else None

  def walk(self,root:Path):
    for dp,_,fns in os.walk(root):
      for fn in fns:
        p=Path(dp)/fn
        if p.suffix.lower() in VIDEO: yield p

  def tmdb_movie(self,info):
    t=info.get('title') or info.get('movie_title') or info.get('series'); y=info.get('year')
    if not t: return None
    r=self.tmdb.search_movie(t,y)
    if not r: return None
    name=r.get('title') or r.get('name') or t
    y=(r.get('release_date') or '0000')[:4]
    try: y=int(y)
    except Exception: y=info.get('year')
    return name,y

  def tmdb_series(self,info):
    t=info.get('series') or info.get('title')
    return self.tmdb.search_tv(t) if t else None

  def tvdb_map(self,series,absno):
    if not self.tvdb: return None
    s=self.tvdb.search_series(series)
    if not s: return None
    sid=s.get('tvdb_id') or s.get('id')
    if not sid: return None
    m=self.tvdb.build_absolute_map(sid)
    return m.get(int(absno))

  def plan_for(self,p:Path):
    info=parse_filename(p.name); ext=p.suffix
    if info.get('type')=='movie':
      mv=self.tmdb_movie(info)
      if not mv: return None
      title,year=mv; rel=rend(self.s.pattern_movie,Ctx(title=title,year=year),ext)
      return p, self.s.movie_dir/rel
    if info.get('type')=='episode':
      si=self.tmdb_series(info); series=(si or {}).get('name') or info.get('series') or info.get('title') or 'Unknown'
      season=info.get('season'); ep=info.get('episode'); absno=info.get('absolute')
      if absno and not (season and ep):
        hit=self.tvdb_map(series,absno)
        if hit: season,ep=hit['season'],hit['episode']
      if absno and not (season and ep):
        rel=rend(self.s.pattern_anime_abs,Ctx(series=series,absolute=absno),ext); return p, self.s.tv_dir/rel
      if not (season and ep):
        rel=rend(self.s.pattern_anime_abs,Ctx(series=series,absolute=absno),ext); return p, self.s.tv_dir/rel
      rel=rend(self.s.pattern_episode,Ctx(series=series,season=int(season),episode=int(ep)),ext); return p, self.s.tv_dir/rel
    return None

  def plan_batch(self,root:Path):
    out=[]; 
    for f in self.walk(root):
      pl=self.plan_for(f)
      if pl: out.append(pl)
    return out

  def execute(self,plans:List[tuple]):
    for src,dst in plans:
      print(f"{'[DRY-RUN] ' if self.s.dry_run else ''}{src} -> {dst}")
      apply_action(src,dst,self.s.action,self.s.dry_run)
