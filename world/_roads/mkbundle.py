"""Write a worldview-readable CSV bundle from the live harvest + a road graph."""
import sys, json, csv, shutil, os, collections
sys.path.insert(0, '/mnt/d/Luke/dev/Rimworld/world/_roads')
from rcommon import *

def write(stem, roadG=None, riverG=None):
    tiles, nb, roads, rivers, setts, objs = load()
    if roadG is None: roadG = roads
    if riverG is None: riverG = rivers
    # tiles.csv: worldview's bundle reader wants the AUTHORED header names
    src = R + 'base_tiles.csv'
    rdr = list(csv.DictReader(open(src)))
    with open(stem + '_tiles.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=rdr[0].keys()); w.writeheader(); w.writerows(rdr)
    shutil.copy(R + 'base_provenance.json', stem + '_provenance.json')
    json.dump({"planet": "Ash'karr", "startingTile": None,
               "source": "live bridge harvest, road pass"},
              open(stem + '_meta.json', 'w'), indent=1)
    with open(stem + '_links.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['kind', 'a', 'b', 'def'])
        for kind, g in (('river', riverG), ('road', roadG)):
            seen = set()
            for a, d in g.items():
                for b, df in d.items():
                    k = (min(a, b), max(a, b))
                    if k in seen: continue
                    seen.add(k); w.writerow([kind, a, b, df])
    with open(stem + '_settlements.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['id', 'faction_def', 'faction', 'name', 'tile', 'why'])
        for o in setts:
            w.writerow([o['id'], o['faction'] or '', o['factionName'] or '',
                        o['name'] or o['label'], o['tile'], ''])
    lm = json.load(open(R + '_landmarks.json'))
    with open(stem + '_landmarks.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['tile', 'landmark', 'why', 'name', 'label'])
        for l in lm.get('landmarks', []):
            w.writerow([l['tile'], l.get('def'), '', l.get('name') or '', l.get('label') or ''])
    print('wrote', stem)

if __name__ == '__main__':
    write(sys.argv[1] if len(sys.argv) > 1 else R + 'before')
