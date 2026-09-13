import csv, statistics as st
from collections import Counter

auth = {int(r['tile']): r for r in csv.DictReader(open('world/ASHKARR_WORLDMAP_tiles.csv'))}
live = {int(r['tile']): r for r in csv.DictReader(open('Transient/v24_tiles_live.csv'))}

# A. repo CSV vs live: biome drift on the whole planet
drift = Counter((auth[t]['biome'], live[t]['biome']) for t in live if t in auth and auth[t]['biome'] != live[t]['biome'])
print("A. authoring-CSV vs LIVE biome drift (top 12):")
for (a,b),n in drift.most_common(12): print(f"   {n:5d}  {a} -> {b}")
print(f"   total drifted tiles: {sum(drift.values())} / {len(live)}")

pl = [t for t in live if live[t]['biome']=='AB_PropaneLakes']
lk = [t for t in live if live[t]['biome']=='RUT_PropaneLake']
def q(vals): 
    s=sorted(vals); n=len(s)
    return s[int(0.10*n)], st.median(s), s[int(0.90*n)]

arcs = [float(auth[t]['arc']) for t in pl if t in auth]
temps = [float(live[t]['temperature']) for t in pl]
elevs = [float(live[t]['elevation']) for t in pl]
print(f"\nB. AB_PropaneLakes LIVE: {len(pl)} tiles (sheet: 2531)")
print(f"   arc min/max {min(arcs):.0f}/{max(arcs):.0f}  p10/med/p90 {q(arcs)[0]:.1f}/{q(arcs)[1]:.1f}/{q(arcs)[2]:.1f} (sheet 139.3/151.3/166.0, range 132-179)")
print(f"   temp p10/med/p90 {q(temps)[0]:.1f}/{q(temps)[1]:.1f}/{q(temps)[2]:.1f} (sheet -73.0/-62.2/-47.8)  above -42C: {sum(1 for x in temps if x > -42)}")
print(f"   elev median {st.median(elevs):.0f} (sheet 670)  water tiles: {sum(1 for t in pl if float(live[t]['elevation'])<=0)} (sheet 0)")

# coldest land on planet
land = [(float(r['temperature']), r['biome']) for r in live.values() if float(r['elevation'])>0]
coldest = min(land)
print(f"   coldest land tile on planet: {coldest[0]:.1f}C in {coldest[1]} (sheet: -81.7 in this def)")

regs = Counter(auth[t]['region'] for t in pl if t in auth)
print("   regions (authoring CSV):", dict(regs.most_common()))

arcs_lk = [float(auth[t]['arc']) for t in lk if t in auth]
temps_lk = [float(live[t]['temperature']) for t in lk]
w_lk = sum(1 for t in lk if t in auth and auth[t]['water']=='1')
regs_lk = Counter(auth[t]['region'] for t in lk if t in auth)
print(f"\nC. RUT_PropaneLake LIVE: {len(lk)} tiles (sheet 57)  water=1: {w_lk}  arc {min(arcs_lk):.0f}-{max(arcs_lk):.0f} (sheet 170-179)  temp med {st.median(temps_lk):.1f} (sheet -79.0)")
print(f"   regions: {dict(regs_lk)}")
print(f"   lake elevation<=0 (engine water test): {sum(1 for t in lk if float(live[t]['elevation'])<=0)}/{len(lk)}")

# D. cap purity: every tile past arc 165 is this def or the lake
past165 = [t for t in live if t in auth and float(auth[t]['arc'])>165]
other = Counter(live[t]['biome'] for t in past165 if live[t]['biome'] not in ('AB_PropaneLakes','RUT_PropaneLake'))
print(f"\nD. tiles past arc 165: {len(past165)}; NOT propane def/lake: {sum(other.values())} {dict(other.most_common(5))}")

# E. dew-point law across whole nightside: any tile with annual mean < -42 NOT in a propane-family def?
cold_other = Counter(live[t]['biome'] for t in live if t in auth and float(live[t]['temperature']) < -42
                     and live[t]['biome'] not in ('AB_PropaneLakes','RUT_PropaneLake'))
print(f"E. tiles colder than -42C in OTHER biomes: {dict(cold_other.most_common(8))}")
