"""ground_ash_ladder: one burn left the whole 20x20 cohort on RM_FE_Ash_Deep. Re-lay soil, grass, one fire, and read the
cohort's terrain + fire count every 500 ticks for 8000 ticks: does one fire walk soil -> deep, and when?"""
import sys, json, collections, re
sys.path.insert(0, 'src/RimMandrake/Utils'); import validation_core as VC
B = VC.Bridge(); out = {'series': []}
def c(name, **kw):
    try: return B.call(name, **kw)
    except Exception as ex: return {'raised': str(ex)[:300]}
R = '50,180,20,20'
ring = ['46,176,28,4', '46,200,28,4', '46,180,4,20', '70,180,4,20']
c('jawa/set_terrain_batch', ops=';'.join('RM_FE_FirebreakLine:' + r for r in ring), layer='top')
c('jawa/set_plants', ops=';'.join('CLEAR:' + r for r in ring))
out['soil'] = (c('jawa/set_terrain', x=50, z=180, terrainDef='RM_FE_Ground_Soil', width=20, height=20, layer='top') or {}).get('message')
out['plant'] = (c('jawa/set_plants', ops='RM_FE_Plant_EmberGrass:' + R, growth=1.0) or {}).get('message')
def terr():
    r = c('jawa/get_terrain_batch', rects=R); n = collections.Counter()
    for op in (r.get('ops') or '').split(';'):
        m = re.match(r'([^:]+):\d+,\d+,(\d+),(\d+)', op)
        if m: n[m.group(1)] += int(m.group(2)) * int(m.group(3))
    return dict(n)
def fires():
    return ((c('jawa/list_things', defName='Fire', rect=R, limit=1) or {}).get('countMatched'))
out['fire'] = {k: v for k, v in (c('jawa/map_fire', action='start', rect=R, fireSize=1.2) or {}).items() if k in ('firesStarted', 'success')}
t0 = (c('jawa/map_info') or {}).get('ticksGame')
for i in range(16):
    c('rimworld/step_game_ticks', ticks=500, pauseFirst=True, timeoutMs=120000)
    out['series'].append({'t': 500 * (i + 1), 'terrain': terr(), 'fires': fires(),
                          'plants': sum(((c('jawa/list_things', group='Plant', rect=R, limit=1) or {}).get('perDef') or {}).values())})
    print(json.dumps(out['series'][-1]), flush=True)
c('jawa/map_fire', action='extinguish', rect=R)
print('RESULT ' + json.dumps(out))
