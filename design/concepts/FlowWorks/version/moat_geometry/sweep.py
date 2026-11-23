"""Region map of the flagship moat (RIMMANDRAKE_DECIDE_MOAT_RAID_BAR_TEXT_SAYS_D4_SCENE_NEEDS_SIX). Writes sweep_result.md.

The mod's numbers (read in the code, 2026-11-23, tip 7606237d1a):
  swim square cost 60 + 13 (a person's walk) x the raider's own costX (RM_SwimMath.CostFactor; recorded live, median 1.55)
  a pawn pays a square's cost BEFORE it stands on it, so the time in a moat W wide is (W-1) swim squares + one walked step
  exhaustion: every 250 ticks, whoever is in the water then (RM_Swim.CheckTicks); 250 / (enduranceH x 2500) each time
  swims while the water is over 0.9 x 1.75 m = 1.575 m; may step in and out while the hole above the surface is <= 2 notches
  (RM_PitTrapMath.ClimbLimit, RM_SwimMath.SurfaceClimbDepth): a moat filled to its brim holds nobody; it holds once the level fell
  more than 1 m (whole notches), and a drained floor is a prison only from 3 m down (pitRoomMinDepthMetres)
  a step of exactly 2 notches is a slow climb: the 2-notch terrain's cost (45) x the slow factor (2) on top of the walked step, paid
  on the last water square (RM_PitTrapMath.StepCost); a brim-full moat has no such step
  water moves once per 250 ticks (pulseIntervalTicks); the level after each pulse is the kernel twin's (drain_model.py, checked to
  1 dL against the recorded live drain)
Raiders: 21 recorded runs (raiders.json): when each entered the water, its costX and enduranceH. Entry times come from 120- and
50-tick polls (uniform inside the poll); a raider never seen in the water before the watch ended enters at end + 0..360 ticks with
probability 0.7, else never (an assumption; the shares below move by a few points with it, the order of the regions does not)."""
import json, math, os, random, sys
import drain_model as D
HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = json.load(open(os.path.join(HERE, 'raiders.json')))
N = 4000
LATE_SWIM = 0.7                                       # a raider not seen in the water by the end of the watch still swims: share
IN = lambda p: 60 <= p[0] <= 71 and 60 <= p[1] <= 71              # noqa: E731
PLOT = lambda p: 62 <= p[0] <= 69 and 62 <= p[1] <= 69            # noqa: E731
ALL_SWIM = [s for r in RUNS for s in r['swim'].values() if s[0] == 'Swimmer' and s[2] > 0]


CLIMB_OUT = {0: 0, 1: 30, 2: 45 * 2}                   # ticks to leave a square whose surface is this many notches down


def raid(rng, W, free=0):
    """One raid: [(enter, leave, cost, enduranceH)] for a moat W wide; leave = the tick it stands on the far bank."""
    r = rng.choice(RUNS)
    end, out, bank = r['polls'][-1][0], [], []
    for pid in r['ids']:
        prev, lo, hi, b = r['polls'][0][0] - 120, None, None, None
        for t, ps in r['polls']:
            p = ps.get(pid)
            if p and b is None and p[1] >= 58:
                b = rng.uniform(prev, t)
            if p and IN(p):
                lo, hi = prev, t
                if PLOT(p):                         # already across a 2-wide moat at this poll: he entered at least a crossing ago
                    lo, hi = prev - 115, t - 115
                break
            prev = t
        bank.append(b if b is not None else end)
        s = r['swim'].get(pid)
        s = s if s and s[0] == 'Swimmer' and s[2] > 0 else rng.choice(ALL_SWIM)
        C = 73 * s[3]
        if lo is None:
            if rng.random() > LATE_SWIM:
                continue
            e = end + rng.uniform(0, 360)
        else:
            e = rng.uniform(lo, hi)
        out.append((e, e + (W - 1) * C + 13 * s[3] + CLIMB_OUT[free], C, s[2]))
    return out, min(bank)


def tired(rs, until):
    """Somebody stood in the water at a 250-tick check at or before `until`."""
    return any(math.floor(min(l, until) / 250) * 250 > e for e, l, C, h in rs)


def polls(start=4, step=120, n=25):
    return [start + step * (k + 1) for k in range(n)]


def wet(rs, t):
    return sum(1 for e, l, C, h in rs if e <= t < l)


def run(W, policy, hold_pulses, rng, free=0, left=0):
    """-> (held, tired before the sluice opens, tired by the time the level holds). policy:
    frozen  = the scene before this decision: two in the water, wait up to 300 ticks for one to tire, the moat drains in zero ticks
    live2/live1 = open at the first 60-tick look with two (one) in the water, the raid goes on while it drains
    bank = open when the first raider reaches the bank, the raid goes on while it drains"""
    rs, bank = raid(rng, W, free)
    if policy == 'frozen':
        t = next((t for t in polls() if wet(rs, t) >= 2), polls()[-1])
        for _ in range(6):
            if tired(rs, t):
                break
            t += 50
        return wet(rs, t), tired(rs, t), tired(rs, t)
    if policy == 'bank':
        t = math.ceil(bank / 60) * 60
    else:
        need = int(policy[-1])
        t = next((t for t in polls(step=60, n=50) if wet(rs, t) >= need), 3004)
    phase = rng.uniform(0, 250)                              # where the next flow pulse falls
    hold = t + phase + (hold_pulses - 1) * 250 + rng.uniform(0, 60)        # the dug-swim refresh runs every 60 ticks
    return wet(rs, hold), tired(rs, t), tired(rs, hold + 250)


def share(W, policy, hold, f, n=N, free=0):
    rng = random.Random(7)
    return sum(1 for _ in range(n) if f(run(W, policy, hold, rng, free))) / n


def hold_pulse(lv, notches):
    """First pulse after which a person cannot climb out: the hole above the water's whole notches is over 2 notches."""
    return next((k for k, w in enumerate(lv) if notches - int(w / 0.5 + 1e-9) > 2), None)


def dry_pulse(lv):
    return next((k for k, w in enumerate(lv) if w <= 0), None)


PITS = {'7x7 10 m, 1 sluice': (D.rect_pit(7, 7), 20, 1), '9x9 10 m, 1 sluice': (D.rect_pit(9, 9), 20, 1),
        '11x11 10 m, 1 sluice': (D.rect_pit(11, 11), 20, 1), '9x9 20 m, 1 sluice': (D.rect_pit(9, 9), 40, 1),
        '11x11 20 m, 1 sluice': (D.rect_pit(11, 11), 40, 1), '9x9 20 m, 3 sluices': (D.rect_pit(9, 9), 40, 3),
        '11x11 10 m, 3 sluices': (D.rect_pit(11, 11), 20, 3)}


def main():
    out = ['# Flagship moat: region map (sweep.py)', '']
    p = out.append
    p('## Depth and water level (the mod\'s rules, no simulation)')
    p('')
    p('| dug | water | raiders enter | swim and tire | holds while draining | drained floor is a prison |')
    p('|---|---|---|---|---|---|')
    for notches in (2, 3, 4, 5, 6, 7, 8, 10):
        for wn in (notches, notches - 1, notches - 2, notches - 3):
            if wn < 3:
                continue
            w = wn * 0.5
            s = notches - wn
            enter = s <= 2
            p('| %.1f m | %.1f m%s | %s | %s | %s | %s |' % (notches * .5, w, ' (brim)' if s == 0 else '', 'yes' if enter else '**no**: %.1f m of wall' % (s * .5),
              'yes' if enter and w >= 2 else 'no', ('yes, once it fell more than %.1f m' % ((2 - s) * .5) if s < 2 else 'yes, at the first fall') if notches > 2 and enter else '-', 'yes' if notches >= 6 else '**no** (under 3 m)'))
    p('')
    p('## Width: time in the water and the exhaustion check')
    p('')
    p('| wide | in the water, ticks (fast / median / slow raider) | share of raiders a 250-tick check catches |')
    p('|---|---|---|')
    xs = sorted(s[3] for s in ALL_SWIM)
    for W in range(1, 9):
        dw = lambda x: (W - 1) * 73 * x + 13 * x            # noqa: E731
        p('| %d | %d / %d / %d | %d%% |' % (W, dw(xs[len(xs) // 20]), dw(xs[len(xs) // 2]), dw(xs[-len(xs) // 20]), 100 * sum(min(1, dw(x) / 250) for x in xs) / len(xs)))
    p('')
    p('## Drain, by the kernel: pulses (250 ticks) until it holds a person / until dry. `-` = the pit is too small, it never empties')
    p('')
    p('| moat (plot 8x8) | ' + ' | '.join(PITS) + ' |')
    p('|---|' + '---|' * len(PITS))
    H = {}
    for notches in (6, 8):
        for W in range(1, 9):
            row = []
            for name, (pit, pn, sl) in PITS.items():
                lv = D.levels(W, 8, notches, pit, pn, sl, max_pulses=40)
                H[(notches, W, name)] = (hold_pulse(lv, notches), dry_pulse(lv))
                row.append('%s / %s' % tuple('-' if x is None else x for x in H[(notches, W, name)]))
            p('| %d wide, %.0f m | %s |' % (W, notches * .5, ' | '.join(row)))
    p('')
    p('## The scene before the decision (moat drains in zero game time), model against the 21 recorded runs')
    p('')
    p('| wide | a raider tired | two or more held | both |')
    p('|---|---|---|---|')
    rec = (sum(r['tired'] > 0 for r in RUNS), sum((r['held'] or 0) >= 2 for r in RUNS), sum(r['tired'] > 0 and (r['held'] or 0) >= 2 for r in RUNS))
    p('| 2, recorded | %d/21 = %d%% | %d/21 = %d%% | %d/21 = %d%% |' % sum(((x, 100 * x / 21) for x in rec), ()))
    for W in range(1, 9):
        p('| %d | %d%% | %d%% | %d%% |' % (W, 100 * share(W, 'frozen', 0, lambda r: r[1]), 100 * share(W, 'frozen', 0, lambda r: r[0] >= 2), 100 * share(W, 'frozen', 0, lambda r: r[1] and r[0] >= 2)))
    p('')
    p('## Played in game time: share of raids with two or more held AND a raider tired, by width and by how many pulses the drain needs to hold')
    for pol, words in (('bank', 'sluice opened when the first raider reaches the bank'), ('live1', 'opened when the first raider is in the water'),
                       ('live2', 'opened when two are in the water')):
        p('')
        p('### %s' % words)
        p('')
        p('| wide | ' + ' | '.join('%d pulses' % k for k in range(1, 9)) + ' |')
        p('|---|' + '---|' * 8)
        for W in range(1, 9):
            p('| %d | ' % W + ' | '.join('%d%%' % (100 * share(W, pol, k, lambda r: r[0] >= 2 and r[2], 1500)) for k in range(1, 9)) + ' |')
    p('')
    p('## Freeboard: a moat dug 4 m whose water stands 0, 0.5, 0.75 or 1 m below the lip (pit 11x11, 10 m, 1 sluice; plot 8x8)')
    p('')
    p('Pulses until it holds / until dry, then the share of raids with two or more held and a raider tired when the sluice opens with two in the water.')
    p('')
    frees = ((4.0, 0), (3.5, 1), (3.25, 2), (3.1, 2), (3.0, 2))
    p('| wide | ' + ' | '.join('%.2f m of water' % w for w, _ in frees) + ' |')
    p('|---|' + '---|' * len(frees))
    for W in range(1, 9):
        row = []
        for w, fr in frees:
            lv = D.levels(W, 8, 8, D.rect_pit(11, 11), 20, 1, max_pulses=40, water=w)
            h, dr = hold_pulse(lv[1:], 8), dry_pulse(lv)
            h = None if h is None else h + 1
            row.append('%s / %s: **%s**' % (h or '-', dr or '-', '-' if h is None else '%d%%' % (100 * share(W, 'live2', h, lambda r: r[0] >= 2 and r[2], 3000, fr))))
        p('| %d | ' % W + ' | '.join(row) + ' |')
    p('')
    p('## The pick (4 wide, dug 4 m, 3 m of water, 7x7 pit 20 m, one sluice) under worse assumptions')
    p('')
    global LATE_SWIM
    lv = D.levels(4, 8, 8, D.rect_pit(7, 7), 40, 1, water=3.0)
    h = hold_pulse(lv[1:], 8) + 1
    p('Level after each pulse, m: %s; holds after pulse %d, dry after pulse %d (%d ticks).' % (', '.join('%.2f' % x for x in lv), h, dry_pulse(lv), 250 * dry_pulse(lv)))
    p('')
    both = lambda r: r[0] >= 2 and r[2]                          # noqa: E731
    p('| assumption | two or more held and a raider tired |')
    p('|---|---|')
    p('| as the map | %d%% |' % (100 * share(4, 'live2', h, both, N, 2)))
    p('| no climb cost at the rim | %d%% |' % (100 * share(4, 'live2', h, both, N, 0)))
    p('| the player opens one pulse late | %d%% |' % (100 * share(4, 'live2', h + 1, both, N, 2)))
    LATE_SWIM = 0.3
    p('| only 3 in 10 of the raiders not yet in the water ever swim | %d%% |' % (100 * share(4, 'live2', h, both, N, 2)))
    LATE_SWIM = 0.7
    p('| 3 wide, else as the pick | %d%% |' % (100 * share(3, 'live2', h, both, N, 2)))
    p('')
    p('## Where the limits cross (which widths the rest of the mod can serve)')
    p('')
    p('| wide | timber leaf (4 at most) | steel leaf (8 at most, needs power) | farthest moat square from the inner rim (capture reach 6) |')
    p('|---|---|---|---|')
    for W in range(1, 9):
        p('| %d | %s | %s | %.1f %s |' % (W, 'yes' if W <= 4 else '**no**', 'yes', W * 2 ** .5, 'yes' if W * 2 ** .5 <= 6 else '**no, at the corners**'))
    open(os.path.join(HERE, 'sweep_result.md'), 'w').write('\n'.join(out) + '\n')
    print('\n'.join(out))


if __name__ == '__main__':
    main()
