import requests
API='https://graphql.anilist.co'
Q="""
query ($search: String) {
  Media(search: $search, type: ANIME) { id title { romaji english native } episodes season seasonYear format synonyms }
}
"""
class AniList:
  def __init__(self): self.s=requests.Session()
  def search(self,q):
    try: r=self.s.post(API,json={'query':Q,'variables':{'search':q}},timeout=20); r.raise_for_status(); return r.json().get('data',{}).get('Media')
    except Exception: return None
