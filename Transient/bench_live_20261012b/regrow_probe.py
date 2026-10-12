"""Why did the burned regrow cohort (16x16 at 182,182) hold 0 roster plants on day 7? Read terrain + whether EmberGrass is placeable."""
import sys, json
sys.path.insert(0, 'src/RimMandrake/Utils'); import validation_core as VC
B = VC.Bridge(); out = {}
def c(name, **kw):
    try: return B.call(name, **kw)
    except Exception as ex: return {'raised': str(ex)[:300]}
r = '182,182,16,16'
out['plants'] = (c('jawa/list_things', group='Plant', rect=r, limit=1) or {}).get('perDef')
out['filth'] = (c('jawa/list_things', group='Filth', rect=r, limit=1) or {}).get('perDef')
tools = [t for t in json.dumps(c('jawa/list_tools') or {}).split('"') if 'terrain' in t.lower()][:20]
out['terrain_tools'] = tools
for name, kw in (('jawa/get_terrain', dict(x=190, z=190)), ('jawa/terrain_at', dict(x=190, z=190)), ('jawa/read_terrain', dict(rect=r)), ('jawa/terrain_counts', dict(rect=r))):
    out[name] = json.dumps(c(name, **kw), default=str)[:500]
out['probe_plant_190'] = json.dumps(c('jawa/set_plants', ops='RM_FE_Plant_EmberGrass:190,190,1,1', growth=0.1), default=str)[:400]
print(json.dumps(out, indent=1, default=str))
