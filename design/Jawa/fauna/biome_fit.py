#!/usr/bin/env python3
"""Score every creature against every biome, so a human decides from a shortlist of tens
instead of a catalogue of 1,260.

Two axes, deliberately NOT one:
  BELONG   - how close the creature's colouring sits to the biome's ground palette.
             Most of a biome's cast should score high here, or the place reads as a zoo.
  STANDOUT - how far it sits from that ground. The ONE super-huge set piece per biome
             should score high here, or the thing a player is meant to remember is
             camouflaged into the dirt.
A single "fit" number would have averaged those two into mush.
"""
import csv, json, math, os, collections
FA = os.path.dirname(os.path.abspath(__file__))

PAL = json.load(open(os.path.join(FA,'biome_palette.json'), encoding='utf-8'))
# A land creature stands on land. Water/lava ramps are in terrainsByFertility but are not
# the ground the animal is seen against, so they are excluded from the matching palette.
LIQUID = ('Water','Lava','Propane','Tar','Slime','Ocean','Marsh')
terr_rgb = {k:v['rgb'] for k,v in PAL['terrains'].items()}
bt = {r['biome']:(r['terrains'].split('|'), r['terrainTexPaths'].split('|'))
      for r in csv.DictReader(open(os.path.join(FA,'biome_terrain.csv'), encoding='utf-8'))}

def rgb2hsv(r,g,b):
    import colorsys; return colorsys.rgb_to_hsv(r/255,g/255,b/255)

ground = {}
for b,(names,paths) in bt.items():
    use=[(n,p) for n,p in zip(names,paths) if p in terr_rgb and not any(k.lower() in n.lower() for k in LIQUID)]
    if not use: use=[(n,p) for n,p in zip(names,paths) if p in terr_rgb]
    if not use: continue
    R=sum(terr_rgb[p][0] for _,p in use)/len(use)
    G=sum(terr_rgb[p][1] for _,p in use)/len(use)
    B=sum(terr_rgb[p][2] for _,p in use)/len(use)
    ground[b]=dict(rgb=[round(R),round(G),round(B)], hsv=rgb2hsv(R,G,B),
                   terrains=[n for n,_ in use],
                   dropped=[n for n,_ in zip(names,paths) if (n,_) not in use])

def hue_d(a,b):
    d=abs(a-b) % 1.0
    return min(d, 1-d) * 2          # 0..1

def dist(c, g):
    """Perceptual-ish distance in HSV. Hue counts less when either side is desaturated,
    because the hue of a grey pixel means nothing."""
    ch,cs,cv = c; gh,gs,gv = g
    w = min(cs,gs)
    return math.sqrt((hue_d(ch,gh)*w)**2 + (cs-gs)**2 + (cv-gv)**2*1.4)

def main():
    rows=list(csv.DictReader(open(os.path.join(FA,'sprite_features.csv'), encoding='utf-8')))
    out=os.path.join(FA,'biome_fit.csv')
    with open(out,'w',newline='',encoding='utf-8') as fh:
        w=csv.writer(fh); w.writerow(['biome','defName','label','mod','bodySize','status','belong','standout'])
        for b,g in ground.items():
            gh=g['hsv']
            for r in rows:
                try: c=(float(r['hue']),float(r['sat']),float(r['val']))
                except: continue
                d=dist(c,gh)
                w.writerow([b,r['defName'],r['label'],r['mod'],r['bodySize'],r['status'],
                            round(max(0,1-d),4), round(min(1,d),4)])
    print(f"wrote {out}: {len(ground)} biomes x {len(rows)} creatures")
    print(f"\n{'biome':30}{'ground rgb':>14}  terrains used (water/lava dropped)")
    for b in sorted(ground, key=lambda x:-int(bt and 0 or 0)):
        pass
    for b,g in ground.items():
        drop=' | dropped: '+','.join(g['dropped']) if g['dropped'] else ''
        print(f"{b:30}{str(g['rgb']):>14}  {', '.join(g['terrains'][:4])}{drop[:44]}")

if __name__=='__main__':
    main()
