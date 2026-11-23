#!/usr/bin/env python3
"""Pit melee reach = the climb criterion: the whole space, body size x step depth x direction, before and beside the C#.

Reads the climb band edges from RM_PitTrapMath.cs (never a copy). Usage: python3 sweep.py > table.txt; exit 1 on a region
that breaks the owner's ruling (RIMMANDRAKE_ENACT_PIT_MELEE_REACH_EQUALS_CLIMB_SIZE_DECIDES, 2026-11-23).
"""
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[4] / 'src/RimMandrake/FlowWorks/Source/RM_PitTrapMath.cs'
EDGES = [float(x) for x in re.search(r'ClimbBandEdges = \{([^}]*)\}', SRC.read_text(encoding='utf-8')).group(1).replace('f', '').split(',')]
BODIES = [('rat', .2), ('child', .5), ('cat/dog edge', .74), ('person edge', .75), ('person', 1.0), ('warg', 1.4), ('person edge', 1.64),
          ('large edge', 1.65), ('muffalo', 2.4), ('large edge', 2.99), ('huge edge', 3.0), ('thrumbo', 4.0), ('titan', 25.0)]
STEPS = range(0, 17)          # 0..8 m in half-metre notches


def k_of(b):
    return 1 + sum(b >= e for e in EDGES)


def reaches(b, step):
    return step <= k_of(b)    # RM_PitTrapMath.StepAllowed: |from - to| <= K, the same up and down


print('edges %s; a cell: U = strikes up out of the pit, D = strikes down into it, . = neither' % EDGES)
print('%-14s %5s %2s  ' % ('body', 'size', 'K') + ' '.join('%4.1f' % (s * .5) for s in STEPS) + '  (m)')
bad = []
for name, b in BODIES:
    row = ['UD' if reaches(b, s) else '.' for s in STEPS]
    print('%-14s %5.2f %2d  ' % (name, b, k_of(b)) + ' '.join('%4s' % c for c in row))
    if row != sorted(row, key=lambda c: c == '.'):
        bad.append('%s: reach returns at a deeper step' % name)
print('\npairs (attacker below / target above, or the other way round): two-way = either strikes, one-way = only the larger, none')
print('%-30s ' % 'pair' + ' '.join('%4.1f' % (s * .5) for s in STEPS))
for i, (an, a) in enumerate(BODIES):
    for bn, b in BODIES[i:]:
        cells = []
        for s in STEPS:
            ra, rb = reaches(a, s), reaches(b, s)
            if ra and not rb:
                bad.append('%s reaches %s at %.1f m, which cannot reach back though larger' % (an, bn, s * .5))
            if a == b and ra != rb:
                bad.append('same size one-way: %s' % an)
            cells.append('two' if ra and rb else 'one' if rb else '.')
        if (an, bn) in (('person', 'person'), ('rat', 'person'), ('person', 'muffalo'), ('person', 'thrumbo'), ('rat', 'thrumbo'), ('muffalo', 'thrumbo')):
            print('%-30s ' % (an + ' / ' + bn) + ' '.join('%4s' % c for c in cells))
print('\nregions: ' + ('; '.join(bad) if bad else 'every one sensible: reach never returns deeper, a larger body never reaches less, same sizes are always two-way or neither, one-way only to the larger'))
sys.exit(1 if bad else 0)
