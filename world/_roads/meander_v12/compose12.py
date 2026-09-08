"""Emit the candidate import CSV: ancient edges verbatim + rerouted runs classified.

classify() is compose.py's, verbatim, against CURRENT tiles/comfort.
NOT APPLIED - see REPORT.md.
"""
import sys, os, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
from field12 import build

DAY, DUSK, NIGHT = 'StoneRoad', 'DirtRoad', 'DirtPath'
PRIORITY = {'DirtPath': 10, 'DirtRoad': 20, 'StoneRoad': 30,
            'AncientAsphaltRoad': 40, 'AncientAsphaltHighway': 50}

F = build()
tiles, C = F['tiles'], F['comfort']
runs = json.load(open(os.path.join(HERE, 'rerouted_v12.json')))
anc = {tuple(int(x) for x in k.split(',')): v
       for k, v in json.load(open(os.path.join(HERE, 'ancient_edges.json'))).items()}


def classify(p):
    cf = sum(C[t] for t in p) / len(p)
    tm = sum(tiles[t]['tmax'] for t in p) / len(p)
    if cf >= 0.40 or tm <= 20.0:
        return DAY
    if cf < 0.16 and tm >= 45.0:
        return NIGHT
    return DUSK


edges = dict(anc)                      # ancient carried verbatim, and it wins
dropped_cold = 0
for r in runs:
    p = r['new']
    d = classify(p)
    for i in range(len(p) - 1):
        a, b = p[i], p[i + 1]
        k = (a, b) if a < b else (b, a)
        if tiles[a]['temp'] < -10.0 and tiles[b]['temp'] < -10.0:
            dropped_cold += 1
            continue
        if k in anc:
            continue
        if k not in edges or PRIORITY[d] > PRIORITY[edges[k]]:
            edges[k] = d

out = os.path.join(HERE, 'roads_import.csv')
with open(out, 'w', newline='') as fh:
    fh.write('kind,a,b,def\n')
    for (a, b), d in sorted(edges.items()):
        fh.write('road,%d,%d,%s\n' % (a, b, d))
cnt = collections.Counter(edges.values())
print('edges %d  (%s)  cold-dropped %d' % (len(edges), dict(cnt), dropped_cold))
print('wrote', out)
