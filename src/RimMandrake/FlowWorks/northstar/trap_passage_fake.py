"""The shared fake ground of selftest_pit_trap_raid_scene and selftest_fetch_scene: what the live game showed on
2026-11-21 (game b, Test Pilot sitting RIMMANDRAKE_STAGE_FLOWWORKS_PIT_TRAP_RAID_NONE_FELL), held to these facts:
  - a raid arrives STRUNG OUT (each raider SPACING squares behind the one before), never abreast;
  - a plank deck is one span: a lone raider walks over a lid and it holds; when two stand on lids at the same time the
    whole deck gives way and everyone on it falls and is held (need = 1 models a raid of which one falls);
  - a wall stops a raider, who sidesteps to the nearest gap; an open pit square stops him too, and he sidesteps to the
    nearest ground beside it (or walks in and is held, mod 'falls_open').
A fake proves the scene's logic, never the game."""
SPACING = 3


def spawn_raid(g, cx, cz, n):
    for i in range(n):
        g['n'] += 1
        g['hostile']['Human%d' % (500 + g['n'])] = {'x': cx - 2 + i % 5, 'z': cz - SPACING * i, 'held': False}


def build(g, ops, contract):
    """jawa/build_batch ops: Wall:x,z stands; an RM_PitCover lid lies on a square dug 4 m whose dug squares end in ground
    within 2 squares on both sides, across x or across z (the deck rests on two banks)."""
    for op in ops.split(';'):
        d, xz = op.split(':')
        c = tuple(int(v) for v in xz.split(',')[:2])
        if d == 'Wall':
            g.setdefault('walls', set()).add(c)
            continue
        banks = [all(any((c[0] + s * k * ax, c[1] + s * k * (1 - ax)) not in g['dug'] for k in (1, 2)) for s in (-1, 1))
                 for ax in (1, 0)]                                  # across x, across z
        # live game b 2026-11-21: lids read covered on a 3 m pit (6 levels), the fetch scene's depth
        if d.startswith('RM_PitCover') and g['dug'].get(c, 0) >= 6 and any(banks):
            g['covers'][c] = True
        else:
            contract.append('cover refused at %s (banks %s)' % (c, banks))


def _free(g, x, z):
    return (x, z) not in g.get('walls', ()) and ((x, z) not in g['dug'] or g['covers'].get((x, z)))


def walk(g, step, top, falls_open=False, nofall=False, need=2):
    """Every free raider walks `step` squares north (to z = top at most), then the deck takes its load. -> fell now?"""
    for _hid, h in sorted(g['hostile'].items()):
        if h['held']:
            continue
        for _ in range(step):
            if h['z'] >= top:
                break
            x, z = h['x'], h['z'] + 1
            if (x, z) in g.get('walls', ()):                       # the wall: sidestep to the nearest gap
                ways = [q for q in range(x - 40, x + 41) if (q, z) not in g['walls']]
                if not ways:
                    break
                x = min(ways, key=lambda q: abs(q - x))
            if (x, z) in g['dug'] and not g['covers'].get((x, z)):  # an open pit square
                if falls_open:
                    h['x'], h['z'], h['held'] = x, z, True
                    break
                ways = [q for q in range(x - 6, x + 7) if _free(g, q, z) and (q, z) not in g['dug']]
                if not ways:
                    break                                           # no ground beside it: he stops at the lip
                x = min(ways, key=lambda q: abs(q - x))
            h['x'], h['z'] = x, z
    on = [h for h in g['hostile'].values() if not h['held'] and g['covers'].get((h['x'], h['z']))]
    if len(on) >= need and not nofall:
        for h in on:
            h['held'] = True
        for c in g['covers']:
            g['covers'][c] = False                                  # the deck gives way whole
        return True
    return False
