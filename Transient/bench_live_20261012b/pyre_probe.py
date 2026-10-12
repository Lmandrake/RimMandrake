"""Diagnose two Pyrelands harness FAILs on the live anima0 site: plant census sanity probe; ground_ash_ladder refusal."""
import sys, json
sys.path.insert(0, 'src/RimMandrake/Utils'); import validation_core as VC
B = VC.Bridge(); out = {}
def c(name, **kw):
    try: return B.call(name, **kw)
    except Exception as ex: return {'raised': str(ex)[:300]}
out['map'] = {k: (c('jawa/map_info') or {}).get(k) for k in ('mapBiome', 'tile')}
# 1 sanity probe cell
for x, z in ((225, 225), (200, 200)):
    k = '%d,%d' % (x, z)
    out['cell_' + k] = json.dumps(c('jawa/get_cell_info', x=x, z=z), default=str)[:700]
    before = (c('jawa/list_things', group='Plant', limit=1) or {}).get('perDef', {}).get('Plant_Grass', 0)
    out['set_' + k] = json.dumps(c('jawa/set_plants', ops='Plant_Grass:%d,%d,1,1' % (x, z), growth=1.0), default=str)[:700]
    after = (c('jawa/list_things', group='Plant', limit=1) or {}).get('perDef', {}).get('Plant_Grass', 0)
    out['grass_' + k] = [before, after]
    c('jawa/set_plants', ops='CLEAR:%d,%d,1,1' % (x, z))
# 2 ladder rect
r = '50,180,20,20'
c('jawa/map_fire', action='extinguish', rect='0,0,250,250')
c('jawa/set_terrain', x=50, z=180, terrainDef='RM_FE_Ground_Soil', width=20, height=20, layer='top')
out['ladder_set_plants'] = json.dumps(c('jawa/set_plants', ops='RM_FE_Plant_EmberGrass:' + r, growth=1.0), default=str)[:900]
out['ladder_plants'] = (c('jawa/list_things', group='Plant', rect=r, limit=1) or {}).get('perDef')
out['ladder_terrain'] = json.dumps(c('jawa/terrain_census', rect=r), default=str)[:400]
out['weather'] = json.dumps(c('jawa/get_weather'), default=str)[:400]
f = c('jawa/map_fire', action='start', rect=r, fireSize=1.2) or {}
out['ladder_fire'] = {k: f.get(k) for k in ('firesStarted', 'cellsTried', 'note')}
c('jawa/map_fire', action='extinguish', rect='0,0,250,250')
print(json.dumps(out, indent=1, default=str))
