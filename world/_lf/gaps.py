import csv, collections
R="/mnt/d/Luke/dev/Rimworld/world/_lf/live_tiles.csv"
T=[r for r in csv.DictReader(open(R,encoding='utf-8'))]
land=[r for r in T if r['waterCovered'].lower() not in ('true','1')]
def f(r,k): return float(r[k])
riv=[r for r in land if int(r['riverCount'])>0]
rd =[r for r in land if int(r['roadCount'])>0]
both=[r for r in land if int(r['riverCount'])>0 and int(r['roadCount'])>0]
print("land %d | river %d | road %d | river+road %d"%(len(land),len(riv),len(rd),len(both)))
print("river+road by hilliness:", dict(collections.Counter(r['hilliness'] for r in both)))
print("river+road & elev<=389:", sum(1 for r in both if f(r,'elevation')<=389))
print("VALLEY gate  (Mtn + elev<=389 + river + road):",
      sum(1 for r in both if r['hilliness']=='Mountainous' and f(r,'elevation')<=389))
print("  ...relax elevation:", sum(1 for r in both if r['hilliness']=='Mountainous'))
print("  ...relax road     :", sum(1 for r in riv if r['hilliness']=='Mountainous' and f(r,'elevation')<=389))
print()
hot=[r for r in land if f(r,'temperature')>=2.26 and f(r,'rainfall')<=1210 and r['hilliness'] in ('Flat','SmallHills','LargeHills')]
print("BADLANDS gate minus elevation:", len(hot), "| of those elev>=746:", sum(1 for r in hot if f(r,'elevation')>=746))
el=sorted(f(r,'elevation') for r in hot)
print("  their elevation p50/p90/p99/max: %.0f %.0f %.0f %.0f"%(el[len(el)//2],el[int(len(el)*.9)],el[int(len(el)*.99)],el[-1]))
print()
sw=sorted(f(r,'swampiness') for r in land)
print("SWAMPHILL: max swampiness on the planet %.3f (needs >=0.548); tiles>=0.3: %d"%(sw[-1],sum(1 for x in sw if x>=0.3)))
print()
g=[r for r in land if -34.5<=f(r,'temperature')<=14.9 and r['hilliness'] in ('LargeHills','Mountainous','Impassable')]
print("GLACIER eligible %d ; also Crater/Rift-eligible (Mtn/Imp, no river/road): %d"%(
  len(g), sum(1 for r in g if r['hilliness'] in ('Mountainous','Impassable') and int(r['riverCount'])==0 and int(r['roadCount'])==0)))
print()
print("temperature deciles:", ["%.0f"%sorted(f(r,'temperature') for r in land)[int(len(land)*q/10)] for q in range(10)])
print("rainfall deciles:   ", ["%.0f"%sorted(f(r,'rainfall') for r in land)[int(len(land)*q/10)] for q in range(10)])
print("elevation deciles:  ", ["%.0f"%sorted(f(r,'elevation') for r in land)[int(len(land)*q/10)] for q in range(10)])
