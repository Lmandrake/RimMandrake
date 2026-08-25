from common import *
import pickle,html
tiles,nb,roads,setts,objs=load()
d=pickle.load(open(O+'final.pkl','rb')); NR=d['newroads']; plan=d['plan']
# window: the region the owner screenshotted + the Dew Belt trade country
LAT0,LAT1,LON0,LON1=-80,10,-120,-20
W,H=1500,1350
def px(t):
    tt=tiles[t]
    x=(tt['lon']-LON0)/(LON1-LON0)*W; y=(LAT1-tt['lat'])/(LAT1-LAT0)*H
    return x,y
def inwin(t):
    tt=tiles[t]
    return LON0-3<=tt['lon']<=LON1+3 and LAT0-3<=tt['lat']<=LAT1+3
FCOL={'Hutt Cartel':'#ff4444','Homestead Defense League':'#44ddaa','Deep Desert Tribes':'#ffcc33'}
def svg(fn,G,pos,title):
    o=['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'%(W,H+40,W,H+40)]
    o.append('<rect width="100%%" height="100%%" fill="#12100e"/>')
    # faint terrain: hilliness
    for t,tt in tiles.items():
        if not inwin(t): continue
        if tt['water']:
            x,y=px(t); o.append('<circle cx="%.1f" cy="%.1f" r="3.1" fill="#22406a"/>'%(x,y))
        elif tt['hill'] in ('LargeHills','Mountainous'):
            x,y=px(t); c='#4a4036' if tt['hill']=='LargeHills' else '#6b5c48'
            o.append('<circle cx="%.1f" cy="%.1f" r="3.1" fill="%s"/>'%(x,y,c))
    seen=set()
    for a,dd in G.items():
        if not inwin(a): continue
        for b,df in dd.items():
            k=(min(a,b),max(a,b))
            if k in seen: continue
            seen.add(k)
            x1,y1=px(a); x2,y2=px(b)
            if abs(x1-x2)>W/2: continue
            w=2.2 if df=='StoneRoad' else 1.3
            c='#e8d5a0' if df=='StoneRoad' else '#b99a63'
            o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f"/>'%(x1,y1,x2,y2,c,w))
    for s in setts:
        t=pos[s['id']]
        if not inwin(t): continue
        x,y=px(t); c=FCOL.get(s['factionName'],'#8899aa')
        r=5 if s['factionName']=='Hutt Cartel' else 4
        o.append('<circle cx="%.1f" cy="%.1f" r="%d" fill="%s" stroke="#000" stroke-width="0.7"/>'%(x,y,r,c))
    o.append('<text x="14" y="%d" fill="#eee" font-family="monospace" font-size="22">%s</text>'%(H+28,html.escape(title)))
    o.append('</svg>')
    open(fn,'w').write('\n'.join(o))
    print('wrote',fn)
svg(O+'cmp_before.svg',roads,{o['id']:o['tile'] for o in setts},'BEFORE  red=Hutt  teal=moisture farmers  yellow=Tusken')
svg(O+'cmp_after.svg',NR,{o['id']:plan.get(o['id'],o['tile']) for o in setts},'AFTER  red=Hutt  teal=moisture farmers  yellow=Tusken')
