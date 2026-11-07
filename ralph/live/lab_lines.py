#!/usr/bin/env python3
"""Lines a laid colony draws at its own ends and doors, and how much slack it kept: compare one lay with another.

    python3 ralph/live/lab_lines.py LAID.json [WORLD.json]
"""
import json, math, sys
sys.path.insert(0, 'ralph/live')
import lab_doors as D
L = json.load(open(sys.argv[1]))
strands = [s for p in L['pieces'] for s in p['strands']]
own = {}
for s in strands:
    for q in (s[0], s[-1]):
        c = D.crossings((q[0], q[1]), 1.5, [s])[0]
        own[c] = own.get(c, 0) + 1
def ln(s):
    return sum(math.hypot(s[i][0] - s[i - 1][0], s[i][1] - s[i - 1][1]) for i in range(1, len(s)))
ratio = []
for s in strands:
    d = math.hypot(s[0][0] - s[-1][0], s[0][1] - s[-1][1])
    if d > 1.5:
        ratio.append(ln(s) / d)
ratio.sort()
print('strands', len(strands), 'end crossings', sorted(own.items()), 'median laid/straight %.2f' % ratio[len(ratio) // 2], 'p10 %.2f' % ratio[len(ratio) // 10])
if len(sys.argv) > 2:
    W = json.load(open(sys.argv[2]))
    print('doors', [(sum(D.crossings((a + .5, b + .5), 1.5, strands))) for a, b in W['doors']])
