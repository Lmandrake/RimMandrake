"""
skeleton_15.py  —  systems/flow SKELETON for the #15 Falcon Halo (hollow) hull.

Approach (user 2026-08-07): lay the load-bearing skeleton FIRST — circulation
(ring maintenance corridor + rear causeway), pod entrances/isolation doors, the
booster/heatsink THERMAL SPINE in the hot wings, per-cell power switches, hot-wing
heat vents, and the SEVEN filtered belt-trunk classes (Factory_lore.md §1.1) routed
as arcs along the cargo/keel ring band. Machine interiors stay as labelled zones for
a later pass.

FULL mechanical fidelity (user 2026-08-07): the thermal spine is placed and then
HARD-VERIFIED against the real 9.9-tile Factory Booster/Heatsink link radius
(Factory_lore.md §5) — every hot machine must sit within 9.9 tiles of its linked
booster/heatsink or the build aborts. Belt trunks follow the 7 documented material
classes with distinct source->sink wings; finished goods deposit radially into the
adjacent G cargo band (the band IS the warehouse), not down a long shared trunk.

Emits skeleton_15.json (typed, tile-coordinate elements) for render_skeleton.py, and
prints a per-element report + the 9.9-tile verification.
"""
import numpy as np, json, math

g = np.load('design_15_falcon_halo_hollow.npy'); H, W = g.shape
# TRUE ring center = the T scrap-shrine, placed at the exact centre in the build
# (cx-2..cx+2, cy-2..cy+2). The G/K centroid is WRONG — the mandible arm's cargo
# tiles bias it upward — so derive the centre from T.
ty, tx = np.where(g == 'T'); CX, CY = float(tx.mean()), float(ty.mean())
ROUT, RIN, RMID = 40, 31, 35            # from the build; band 31..40, keel midline 35
LINK = 9.9                              # Factory Booster / Heatsink link radius (§5)

def centroid(code):
    yy, xx = np.where(g == code)
    return float(xx.mean()), float(yy.mean())

def ang(px, py):                        # degrees, matching the build's convention
    return math.degrees(math.atan2(py - CY, px - CX)) % 360

# --- region angular positions (for routing + entrance placement) -------------
POD = {}
for code in ['A', 'E', 'B', 'C', 'D', 'F', 'R']:
    px, py = centroid(code); POD[code] = dict(x=px, y=py, deg=ang(px, py))
CARD = {}
for code in ['S', 'U', 'W', 'M', 'T', 'H']:
    px, py = centroid(code); CARD[code] = dict(x=px, y=py, deg=ang(px, py))

elements = []       # each: dict(type=..., ...tile coords...)

# =====================================================================
# 1. RING MAINTENANCE CORRIDOR  — the utility spine on the keel midline.
#    A walkable lane following r=RMID all the way round (the "keel repaired
#    first" backbone). Drawn as a dense polyline of tile centres at r=RMID.
# =====================================================================
ring_pts = []
for deg in range(0, 360):
    a = math.radians(deg)
    x = int(round(CX + RMID * math.cos(a))); y = int(round(CY + RMID * math.sin(a)))
    if 0 <= x < W and 0 <= y < H and g[y, x] != '':
        ring_pts.append([x, y])
elements.append(dict(type='corridor', role='ring_spine', pts=ring_pts))

# rear causeway (already a '.' spoke in the hull): centre core -> ring, straight down
cause = [[int(round(CX)), y] for y in range(int(round(CY)), int(round(CY + RIN)) + 1)]
elements.append(dict(type='corridor', role='causeway', pts=cause))

# =====================================================================
# 2. POD ENTRANCES + ISOLATION DOORS  — one airlock where each pod's inner
#    edge meets the ring corridor (region entrance + per-cell isolation, §1.1
#    "one local switch per cell"). Door sits on the ring midline at the pod's
#    bearing; the power switch sits just inboard of it.
# =====================================================================
for code, p in POD.items():
    a = math.radians(p['deg'])
    dx, dy = math.cos(a), math.sin(a)
    door = [int(round(CX + RMID * dx)), int(round(CY + RMID * dy))]
    switch = [int(round(CX + (RMID - 2) * dx)), int(round(CY + (RMID - 2) * dy))]
    elements.append(dict(type='door', role='pod_airlock', wing=code, at=door))
    elements.append(dict(type='switch', role='cell_power', wing=code, at=switch))

# =====================================================================
# 3. THERMAL SPINE  — hot wings B, E get a Factory Booster (3x1) + heatsink
#    bank placed OUTBOARD (heat dumps to the hull edge / early-game gaps, §3
#    heat doctrine), then HARD-VERIFIED within 9.9 tiles of every hot machine.
# =====================================================================
def hot_machines(code):
    # machine centres from interior_fit placements (sub-local) + pod bbox origin
    fit = json.load(open('interior_fit_placements.json')).get(code, [])
    yy, xx = np.where(g == code); ox, oy = int(xx.min()), int(yy.min())
    out = []
    for (lab, x, y, w, h) in fit:
        if x < 0: continue
        if any(k in lab for k in ('Booster', 'Heatsink')): continue
        out.append((lab, ox + x + w/2.0, oy + y + h/2.0))
    return out

thermal_report = {}
for code in ['B', 'E']:
    p = POD[code]
    a = math.radians(p['deg'])
    # place the bank just OUTBOARD of the pod centre, toward the rim
    bank_cx = p['x'] + 3*math.cos(a); bank_cy = p['y'] + 3*math.sin(a)
    booster = [int(round(bank_cx - 1)), int(round(bank_cy)), 3, 1]      # x,y,w,h
    sinks = [[int(round(bank_cx - 2)), int(round(bank_cy + 1)), 2, 2],
             [int(round(bank_cx + 1)), int(round(bank_cy + 1)), 2, 2]]
    elements.append(dict(type='booster', wing=code, rect=booster))
    for s in sinks:
        elements.append(dict(type='heatsink', wing=code, rect=s))
    # verify: every hot machine within LINK of the bank centre
    mx = [d for d in hot_machines(code)]
    worst = 0.0; worst_lab = None
    for lab, cx, cy in mx:
        dist = math.hypot(cx - bank_cx, cy - bank_cy)
        if dist > worst: worst, worst_lab = dist, lab
    thermal_report[code] = dict(bank=[round(bank_cx, 1), round(bank_cy, 1)],
                                worst_machine=worst_lab, worst_dist=round(worst, 2),
                                within_link=bool(worst <= LINK))
    # outboard heat vents (early gap-vent -> late louvre): 2 tiles at the rim
    for off in (-1, 1):
        vd = math.radians(p['deg'] + off*6)
        vx = int(round(CX + (ROUT-1)*math.cos(vd))); vy = int(round(CY + (ROUT-1)*math.sin(vd)))
        elements.append(dict(type='vent', wing=code, at=[vx, vy]))

# =====================================================================
# 4. BELT TRUNK CLASSES (Factory_lore.md §1.1) — seven FILTERED trunks, each an
#    arc of the cargo/keel band between its source and sink wings. Finished goods
#    (class 6) deposit radially into the adjacent G band, so it's modelled as short
#    radial stubs at each wing, not a long shared trunk.
# =====================================================================
def arc_pts(deg0, deg1, r):
    # short-way sweep deg0->deg1 along radius r
    d = (deg1 - deg0)
    if d > 180: d -= 360
    if d < -180: d += 360
    n = max(2, int(abs(d)) )
    pts = []
    for t in np.linspace(0, 1, n):
        a = math.radians(deg0 + d*t)
        x = int(round(CX + r*math.cos(a))); y = int(round(CY + r*math.sin(a)))
        if 0 <= x < W and 0 <= y < H: pts.append([x, y])
    return pts

TRUNKS = [
    (1, 'raw minerals + chunks', 'A', 'B', RMID-2),
    (2, 'organic + corpses',     'A', 'B', RMID-3),   # to B mincer/cremator/biofuel
    (3, 'food ingredients',      'A', 'C', RMID-1),
    (4, 'textile crops',         'A', 'D', RMID+0),
    (5, 'components + adv-mat',   'B', 'F', RMID+1),   # B metal -> E -> F (routes past E@60)
    (7, 'chemfuel',              'B', 'U', RMID+2),   # B biofuel -> fuel bunkerage -> thrusters
]
for cls, name, src, dst, r in TRUNKS:
    d0 = POD[src]['deg']; d1 = (POD[dst]['deg'] if dst in POD else CARD[dst]['deg'])
    elements.append(dict(type='belt', cls=cls, name=name, src=src, dst=dst,
                         pts=arc_pts(d0, d1, r)))
# class 6 finished-goods radial stubs (wing -> adjacent G band)
for code, p in POD.items():
    a = math.radians(p['deg'])
    stub = [[int(round(CX + rr*math.cos(a))), int(round(CY + rr*math.sin(a)))]
            for rr in (RIN+1, RMID)]
    elements.append(dict(type='belt', cls=6, name='finished goods', src=code, dst='G', pts=stub))

# =====================================================================
# report + emit
# =====================================================================
# ⚠️ VERIFY BEFORE WRITE. This used to json.dump() skeleton_15.json first and
# only assert allok afterward, so a design that FAILED the 9.9-tile link check
# still landed on disk with the bad layout -- the docstring's "or the build
# aborts" was false as written; only the process exit code caught it, and any
# caller that didn't check that (render_skeleton.py doesn't) would render a
# skeleton that violates the doctrine it claims to hard-verify. Compute and
# assert allok BEFORE the dump so a failing design never reaches the file.
from collections import Counter
cnt = Counter(e['type'] for e in elements)
allok = all(r['within_link'] for r in thermal_report.values())
if not allok:
    print("\nTHERMAL 9.9-tile link verification (Factory_lore §5):")
    for code, r in thermal_report.items():
        flag = 'OK' if r['within_link'] else '*** EXCEEDS 9.9 ***'
        print(f"  wing {code}: worst machine {r['worst_machine']} @ {r['worst_dist']} tiles  [{flag}]")
    assert allok, "thermal link radius exceeded — reposition bank"

json.dump(dict(center=[round(CX, 2), round(CY, 2)], rout=ROUT, rin=RIN, rmid=RMID,
               link=LINK, elements=elements, thermal=thermal_report),
          open('skeleton_15.json', 'w'), indent=1)

print("SKELETON #15  center", (round(CX,1), round(CY,1)))
print("elements:", dict(cnt))
print("\nTHERMAL 9.9-tile link verification (Factory_lore §5):")
for code, r in thermal_report.items():
    print(f"  wing {code}: worst machine {r['worst_machine']} @ {r['worst_dist']} tiles  [OK]")
print("\nBELT TRUNKS (7 filtered classes, §1.1):")
for cls, name, src, dst, r in TRUNKS:
    print(f"  {cls}. {name:<22} {src} -> {dst}")
print(f"  6. finished goods         each wing -> G (radial stubs)")
print("\nwrote skeleton_15.json   (thermal verification PASSED)")
