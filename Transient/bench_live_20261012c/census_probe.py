"""Why is RM_FE_Plant_EmberGrass rejected at the census probe cell (225,225)? Read the cell; retry with clearFirst."""
import sys, json
sys.path.insert(0, 'src/RimMandrake/Utils'); import validation_core as VC
B = VC.Bridge(); out = {}
def c(name, **kw):
    try: return B.call(name, **kw)
    except Exception as ex: return {'raised': str(ex)[:300]}
for x, z in ((225, 225), (200, 200)):
    k = '%d,%d' % (x, z)
    out['things_' + k] = c('jawa/list_things', rect='%d,%d,1,1' % (x, z), limit=10)
    out['terrain_' + k] = c('jawa/get_terrain', x=x, z=z) if True else None
    out['plain_' + k] = c('jawa/set_plants', ops='RM_FE_Plant_EmberGrass:%d,%d,1,1' % (x, z), growth=1.0)
    out['clearfirst_' + k] = c('jawa/set_plants', ops='RM_FE_Plant_EmberGrass:%d,%d,1,1' % (x, z), growth=1.0, clearFirst=True)
    out['after_' + k] = c('jawa/list_things', rect='%d,%d,1,1' % (x, z), limit=10)
print(json.dumps(out, indent=1, default=str)[:6000])
