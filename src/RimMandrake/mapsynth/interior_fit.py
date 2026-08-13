"""
interior_fit.py  —  FULL-FIDELITY fit-check for the #15 Falcon Halo (hollow) hull.

Question this answers (the load-bearing evidence step before drawing any interior
skeleton): does each rim-embedded function pod (a radius-8 disk, ~197 tiles) PHYSICALLY
hold its real VFE-Factory machine set at true footprints, PLUS the logistics and thermal
hardware Factory_lore.md requires — input/output hoppers (1 tile each), a factory-floor
apron, a Factory Booster (3x1) and Factory Heatsink bank (2x2 each), and pawn/belt access?

Machine footprints, hopper counts, and the 9.9-tile booster/heatsink link radius are taken
verbatim from Factory_lore.md §3/§5 (sourced [S2A]-[S2E]). We do a real rectangle-pack into
the pod's inscribed clear region and report per-wing headroom. A pod that cannot hold its set
is a HULL problem (escalate), not a decoration problem.

Run:  python3 interior_fit.py
"""
import numpy as np, json, math
from ship_designs import COL, LABEL

g = np.load('design_15_falcon_halo_hollow.npy'); H, W = g.shape

# --- ring geometry (recovered from the build: cropped grid, center from G/K centroid) ---
ys, xs = np.where(np.isin(g, ['G', 'K']))
CX, CY = xs.mean(), ys.mean()

# --- machine sets per wing (Factory_lore.md §3; footprint = (dx,dy) in tiles, io = #hopper ports) ---
# Every factory machine needs Factory Floor beneath it (§1.1) and hoppers at each I/O port (§4.1).
# Hot wings additionally carry a Factory Booster (3x1) + Factory Heatsink bank (2x2 each).
MACHINES = {
    'A': [('Autofarmer', 3, 7, 1), ('Drill Platform', 3, 3, 1), ('Fishfarm', 3, 3, 1)],
    'B': [('Smelter', 3, 4, 4), ('Masonry Saw', 3, 3, 2), ('Mincer', 3, 3, 2),
          ('Crematorium', 3, 3, 1), ('Biofuel Refinery', 3, 4, 4)],
    'C': [('Conveyor Oven', 3, 5, 4), ('Cannery', 3, 5, 3), ('Distillery', 3, 3, 2)],
    'D': [('Autoloom', 3, 5, 3), ('Ammo Press', 3, 4, 3)],
    'E': [('Assembler', 5, 5, 5), ('Alloy Forge', 5, 5, 4), ('Neutro Synth', 5, 3, 3)],
    'F': [('Medicine Granulator', 5, 3, 4), ('Machining Bay', 5, 5, 4)],
    'R': [],  # habitat — furniture, handled as a density estimate not machine packing
}
HOT = {'B', 'E'}          # wings that must also fit booster + heatsink bank
BOOSTER = (3, 1)          # Factory Booster footprint (§5)
HEATSINK = (2, 2)         # Factory Heatsink footprint (§5)
N_HEATSINK_HOT = 4        # link up to 4 heatsinks on the hottest machine (§5)
N_BOOSTER_HOT = 1         # 1 booster reserved in the pod (surge; more can sit on the ring)

def pod_mask(code):
    return (g == code)

def inscribed_free(mask):
    """Return the pod's tile set as a boolean grid cropped to its bbox, plus bbox origin."""
    yy, xx = np.where(mask)
    y0, y1, x0, x1 = yy.min(), yy.max(), xx.min(), xx.max()
    sub = mask[y0:y1+1, x0:x1+1].copy()
    return sub, (int(x0), int(y0))

def pack(sub, rects):
    """Greedy shelf/skyline pack of (w,h) rects into the free tiles of `sub`
    (True = usable). Rects may rotate 90deg. Returns (placed_list, ok, occ_grid).
    placed_list: (label, x, y, w, h) in sub-local coords. Honors the disk boundary:
    a rect is legal only if ALL its tiles are True (inside the pod)."""
    hh, ww = sub.shape
    occ = ~sub                      # occupied = outside-pod OR already placed
    placed = []
    def fits(x, y, w, h):
        if x < 0 or y < 0 or x+w > ww or y+h > hh: return False
        return not occ[y:y+h, x:x+w].any()
    def put(x, y, w, h):
        occ[y:y+h, x:x+w] = True
    ok = True
    # place largest-area first (assembler/forge before small saws) for a tight core
    for item in sorted(rects, key=lambda r: -r[1]*r[2]):
        label, w, h = item
        done = False
        for (pw, ph) in ({(w, h), (h, w)}):     # try both orientations
            if done: break
            for y in range(hh):
                for x in range(ww):
                    if fits(x, y, pw, ph):
                        put(x, y, pw, ph); placed.append((label, x, y, pw, ph)); done = True; break
                if done: break
        if not done:
            ok = False; placed.append((label+' [UNPLACED]', -1, -1, w, h))
    return placed, ok, occ

print(f"#15 ring center ~({CX:.0f},{CY:.0f})   grid {H}x{W}   total {int((g!='').sum())} tiles\n")
print(f"{'Wing':<4}{'label':<22}{'pod':>5}{'machineTiles':>13}{'w/hoppers':>11}{'w/thermal':>11}{'PACK':>7}{'headroom':>10}")
print('-'*84)

summary = {}
for code, machs in MACHINES.items():
    mask = pod_mask(code)
    n_pod = int(mask.sum())
    if code == 'R':
        # habitat: estimate at ~2.0 tiles/colonist for a 5-founder crew + shared rooms
        summary[code] = dict(pod=int(n_pod), note='habitat (furniture density, not machine-packed)')
        print(f"{code:<4}{LABEL[code]:<22}{n_pod:>5}{'—':>13}{'—':>11}{'—':>11}{'n/a':>7}{n_pod:>10}")
        continue
    # raw machine tiles
    m_tiles = sum(w*h for _, w, h, _ in machs)
    # + hoppers: 1 tile per I/O port
    hop = sum(io for *_, io in machs)
    w_hop = m_tiles + hop
    # + thermal for hot wings
    thermal = 0
    rects = [(nm, w, h) for (nm, w, h, io) in machs]
    if code in HOT:
        thermal = BOOSTER[0]*BOOSTER[1]*N_BOOSTER_HOT + HEATSINK[0]*HEATSINK[1]*N_HEATSINK_HOT
        for i in range(N_BOOSTER_HOT): rects.append((f'Booster{i+1}', *BOOSTER))
        for i in range(N_HEATSINK_HOT): rects.append((f'Heatsink{i+1}', *HEATSINK))
    w_therm = w_hop + thermal
    # real geometric pack (machines + thermal blocks; hoppers are 1-tile, packed loosely after)
    sub, origin = inscribed_free(mask)
    placed, ok, occ = pack(sub, rects)
    placed = [(lab, int(x), int(y), int(w), int(h)) for (lab, x, y, w, h) in placed]
    # after big rects, do hoppers fit in leftover free tiles?
    free_after = int((~occ).sum())
    hop_ok = free_after >= hop
    packok = 'YES' if (ok and hop_ok) else ('tight' if ok else 'NO')
    headroom = n_pod - w_therm
    summary[code] = dict(pod=int(n_pod), machine_tiles=int(m_tiles), with_hoppers=int(w_hop),
                         with_thermal=int(w_therm), headroom=int(headroom),
                         pack_ok=bool(ok), hoppers_fit=bool(hop_ok),
                         placed=placed, origin=list(origin))
    print(f"{code:<4}{LABEL[code]:<22}{n_pod:>5}{m_tiles:>13}{w_hop:>11}{w_therm:>11}{packok:>7}{headroom:>10}")

json.dump({k: {kk: vv for kk, vv in v.items() if kk != 'placed'} for k, v in summary.items()},
          open('interior_fit_summary.json', 'w'), indent=1)
# stash placements for the skeleton renderer
json.dump({k: v.get('placed', []) for k, v in summary.items() if 'placed' in v},
          open('interior_fit_placements.json', 'w'))
print("\nwrote interior_fit_summary.json + interior_fit_placements.json")
