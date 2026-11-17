#!/usr/bin/env python3
"""Read what a Pyrelands savegame knows about its burn: the per-cell last-fire tick the ash field saves (ashBurnTickDeflate),
every Fire, every ember-grass and quickgrass plant, and the weather. The instrument that showed the flood
(RIMMANDRAKE_RESCUE_PYRELANDS_BLACK_RAIN_DOUSES_NEEDED_FIRE): python3 pyre_save_burn_grid.py <save.rws>."""
import re,sys,base64,zlib,numpy as np,json
def load(path):
    s=open(path,'rb').read().decode('utf-8','replace')
    out={}
    out['ticksGame']=int(re.search(r'<ticksGame>(\d+)',s).group(1))
    out['gen']=int(re.search(r'<generationTick>(\d+)',s).group(1))
    m=re.search(r'<size>\((\d+), 1, (\d+)\)',s); W,H=int(m.group(1)),int(m.group(2)); out['size']=(W,H)
    for key in ('ashBurnTickDeflate',):
        m=re.search(r'<%s>\s*([^<]+)</%s>'%(key,key),s)
        if m:
            raw=m.group(1).strip(); out['key']=key; b=base64.b64decode(raw)
            try: b=zlib.decompress(b,-15)
            except Exception as e: pass
            out['burn']=np.frombuffer(b,dtype='<i4')
            break
    # fires / plants positions
    def things(defn):
        pos=[]
        for m in re.finditer(r'<def>%s</def>\s*(?:<tickDelta>\d+</tickDelta>\s*)?<id>[^<]*</id>\s*(?:<map>\d+</map>\s*)?<pos>\((\d+), 0, (\d+)\)'%defn,s):
            pos.append((int(m.group(1)),int(m.group(2))))
        return pos
    out['fires']=things('Fire'); out['ember']=things('RM_FE_Plant_EmberGrass'); out['quick']=things('RM_FE_Plant_Quickgrass')
    out['weather']=re.findall(r'<(curWeather|lastWeather|curWeatherAge|curWeatherDuration)>([^<]+)',s)
    return out
if __name__=='__main__':
    o=load(sys.argv[1]); b=o.get('burn')
    print({k:(v if k not in('burn','fires','ember','quick') else len(v)) for k,v in o.items()})
    if b is not None:
        W,H=o['size']; print(b.shape, (b>=0).sum(), b[b>=0].min() if (b>=0).any() else None, b.max())
