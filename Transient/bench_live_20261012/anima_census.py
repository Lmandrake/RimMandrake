"""ANIMA_TREE_FIX_TAKES_THE_SIDE_DOOR A1: fresh quicktest home map -> Plant_TreeAnima census; Base_Player genSteps; storyteller comps."""
import sys, json
sys.path.insert(0, 'src/RimMandrake/Utils'); import validation_core as VC
B = VC.Bridge(); out = {}
B.call('rimworld/go_to_main_menu')
r = B.call('rimworld/start_debug_game_ready', readiness='mapData', pauseIfNeeded=True, timeoutMs=280000)
out['start'] = {k: r.get(k) for k in ('success', 'message')}
ok, w = VC._wait_playing(B, leave_s=0); out['playing'] = ok
mi = B.call('jawa/map_info') or {}
out['map'] = {k: mi.get(k) for k in ('sizeX', 'sizeZ', 'mapBiome', 'tile', 'isPlayerHome')}
lt = B.call('jawa/list_things', defName='Plant_TreeAnima', limit=50) or {}
out['animaCensus'] = {'success': lt.get('success'), 'n': len(lt.get('things') or []), 'total': lt.get('totalCount', lt.get('count'))}
ctl = B.call('jawa/list_things', defName='Plant_TreeOak', limit=5) or {}
out['control_list_things_sees_trees'] = {'success': ctl.get('success'), 'n': len(ctl.get('things') or [])}
for typ, name, fields in (('MapGeneratorDef', 'Base_Player', 'genSteps'), ('StorytellerDef', 'Cassandra', 'comps')):
    try:
        g = B.call('jawa/get_defs', defs='%s/%s' % (typ, name), fields=fields)
        out[name] = json.dumps(g, default=str)[:1500]
    except Exception as ex:
        out[name] = 'ERR %s' % ex
print(json.dumps(out, indent=1, default=str))
json.dump(out, open('Transient/bench_live_20261012/anima_census.json', 'w'), indent=1, default=str)
