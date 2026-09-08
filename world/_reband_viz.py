import csv, math, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
rows=list(csv.DictReader(open('world/ASHKARR_WORLDMAP_tiles.csv')))
plan={p['tile']:p['to'] for p in json.load(open('world/backside_reband_plan.json'))}
COL={'AB_RockyCrags':'#3a3a44','RUT_NightsideIce':'#dfe9f2','BiomeGRimond':'#5b8fc7',
     'AB_PropaneLakes':'#6b4a86','RUT_PropaneLake':'#2a1a3a','AB_MycoticJungle':'#3f6b3a'}
def biome(r): return plan.get(int(r['tile']), r['biome'])
fig,axs=plt.subplots(1,2,figsize=(16,8),subplot_kw={'projection':'polar'})
for ax,(title,pick) in zip(axs,[('BEFORE',lambda r:r['biome']),('AFTER (reband)',biome)]):
    cap=[r for r in rows if float(r['arc'])>=90]
    th=[math.radians(float(r['lon'])) for r in cap]
    rr=[180-float(r['arc']) for r in cap]  # arc180=antipode at center
    cs=[COL.get(pick(r),'#111') for r in cap]
    ax.scatter(th,rr,c=cs,s=14,marotate=0) if False else ax.scatter(th,rr,c=cs,s=16)
    ax.set_title(title); ax.set_ylim(0,90); ax.set_yticklabels([]); ax.grid(alpha=.2)
import matplotlib.patches as mp
leg=[mp.Patch(color=c,label=b.replace('AB_','').replace('RUT_','')) for b,c in COL.items()]
fig.legend(handles=leg,loc='lower center',ncol=6)
fig.suptitle('Antistellar cap: center=antipode(arc180), radius=90-... , angle=longitude',y=.98)
plt.savefig('Transient/backside_reband_polar.png',dpi=90,bbox_inches='tight')
print('wrote Transient/backside_reband_polar.png')
