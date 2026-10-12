"""ground_ash_ladder cycle 2 refused: what terrain does the 50,180,20,20 cohort hold after burn 1, and is EmberGrass placeable on it?"""
import sys, json, collections
sys.path.insert(0, 'src/RimMandrake/Utils'); import validation_core as VC
B = VC.Bridge(); out = {}
def c(name, **kw):
    try: return B.call(name, **kw)
    except Exception as ex: return {'raised': str(ex)[:300]}
r = c('jawa/get_terrain_batch', rects='50,180,20,20')
ops = r.get('ops') if isinstance(r, dict) else None
out['terrain_raw_keys'] = list(r.keys()) if isinstance(r, dict) else r
out['ops_sample'] = (ops or [])[:3] if isinstance(ops, list) else str(ops)[:600]
out['things'] = {g: (c('jawa/list_things', group=g, rect='50,180,20,20', limit=1) or {}).get('perDef') for g in ('Plant', 'Filth', 'BuildingArtificial')}
out['fert'] = c('jawa/get_defs', defs='TerrainDef/RM_FE_Ash_Light,TerrainDef/RM_FE_Ash_Heavy,TerrainDef/RM_FE_Ash_Trace,TerrainDef/RM_FE_Ash_Deep', fields='fertility,burnedDef')
out['ember'] = c('jawa/get_defs', defs='ThingDef/RM_FE_Plant_EmberGrass', fields='plant', deep=True)
out['plant1'] = c('jawa/set_plants', ops='RM_FE_Plant_EmberGrass:60,190,1,1', growth=0.5)
print(json.dumps(out, default=str)[:9000])
