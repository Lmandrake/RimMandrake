# -*- coding: utf-8 -*-
"""THE RELIGION TEST. Does a NON-Ash'karr world give the twelve authored factions their own
ideoligions - the thing classic mode denies? The quicktest generated its own world, so this
is a free reading of exactly that question."""
import sys, json, io, collections
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=300); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}

wi=c('jawa/world_info_get')
print("WORLD: name=%r seed=%r coverage=%s tiles=%s factions=%s"%(
    (wi.get('info') or {}).get('name'), (wi.get('info') or {}).get('seedString'),
    (wi.get('info') or {}).get('planetCoverage'), wi.get('tilesCount'),
    len((wi.get('info') or {}).get('factions') or [])))
print()
io_=c('jawa/ideo_of',{'precepts':False})
print("IDEOLIGIONS: ideologyActive=%s  ideosTotal=%s  nonPlayerBelievers=%s"%(
    io_.get('ideologyActive'), io_.get('ideosTotal'), io_.get('nonPlayerBelieversTotal')))
for q in (io_.get('ideos') or []):
    print("   id=%-4s name=%-34s culture=%-20s structure=%s memes=%s"%(
        q.get('id'), q.get('name'), q.get('culture'), q.get('structureMeme'),
        len(q.get('memes') or []) if isinstance(q.get('memes'),list) else q.get('memes')))
print()
AUTH = ['the Weight','the Balance','Meckgin','the Ascendant Genome','the Continuity Protocol']
names = [str(q.get('name')) for q in (io_.get('ideos') or [])]
print("authored ideo names present?")
for n in AUTH:
    print("   %-26s %s"%(n, "PRESENT" if any(n.lower() in x.lower() for x in names) else "absent"))
print()
lg=c('jawa/faction_leader_get',{})
rows=lg.get('rows') or []
print("LEADER TITLES (%d factions, ideoOverrodeDefCount=%s)"%(len(rows), lg.get('ideoOverrodeDefCount')))
for q in rows:
    print("   %-30s effective=%-22s ideo=%-22s def=%s"%(
        q.get('defName'), q.get('effectiveTitle'), q.get('ideoTitle'), q.get('defTitle')))
json.dump({'world':wi,'ideos':io_,'leaders':lg}, open(r"D:\Luke\dev\Rimworld\world\_lf\religion.json","w"), indent=1)
