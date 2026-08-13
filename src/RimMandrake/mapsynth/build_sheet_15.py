"""
build_sheet_15.py  —  PASS 2 for the #15 Falcon Halo (hollow) hull: turn the
verified skeleton + fit-check into a BUILDABLE machine build sheet.

PASS 1 (interior_fit.py) proved AREA feasibility with a shoulder-to-shoulder pack —
correct for "do the machines fit?" but not buildable: abutting machines leave no free
perimeter for hoppers and no walkable lane from the airlock. PASS 2 therefore RE-PACKS
each pod with a mandatory 1-tile working AISLE around every machine (Factory_lore.md
§1.1 access rule). The pods have large headroom (B 114, E 101 spare) so spacing is
affordable; this is where the fit-check's headroom gets spent.

Inputs:
  * interior_fit_summary.json     — each wing's pod bbox origin (x0,y0) + headroom.
  * skeleton_15.json              — pod airlock/door tiles (belt + pawn entry point).
Machine sets/footprints are mirrored from interior_fit.MACHINES (Factory_lore.md §3/§5).

⚠️ THE OUTPUT OF THIS FILE IS PINNED. `src/RimMandrake/Utils/rimbench/shipbuild.py` holds a
sha256 over `build_sheet_15.json`'s canonicalised elements (`330e6ff`) and
asserts it in its selftest, because regenerating this sheet moves five machines
-- Conveyor Oven, Cannery, Autoloom, Neutro Synth, Medicine Granulator -- and
silently changes their rotation flags.

**If you regenerate and BRIDGE's selftest goes red, that is the guard working.**
Re-verify the five non-square machines against the deck plan first. Updating
SHEET_SHA256 to make the test pass, without doing that, converts a deliberate
conversation back into the silent divergence the pin exists to prevent -- and it
must be updated in the SAME commit as the regenerated json.

`src/RimMandrake/Utils/rimbench/` is BRIDGE's; coordinate rather than editing it alone.

What PASS 2 adds on top of the skeleton (Factory_lore.md §1.1/§3/§4.1):
  1. MACHINE rects placed at global tile coords (origin + pod-local from the fit-check).
  2. FACTORY FLOOR apron  — the buildable floor beneath machines + the 1-tile working
     aisle around them, clipped to the pod disk (machines need Factory Floor under them).
  3. HOPPER faces         — `io` input/output hopper tiles per machine, placed on the
     machine's free perimeter, biased toward the pod airlock (where the belt trunk enters).
  4. BELT-TO-MACHINE stubs — a short spur from the pod airlock to the nearest machine
     hopper, so every cell's trunk actually reaches its first machine.

Emits build_sheet_15.json (typed, global tile coords) for render_build_sheet.py and
prints a per-wing report: machines placed, apron tiles, hoppers placed vs required.
No geometry is invented — every machine tile comes from the PASS 1 verified pack.
"""
import numpy as np, json, math
from collections import deque

g = np.load('design_15_falcon_halo_hollow.npy'); H, W = g.shape
summary     = json.load(open('interior_fit_summary.json'))
sk          = json.load(open('skeleton_15.json'))

# machine sets per wing: (name, w, h, io) — mirrors interior_fit.MACHINES (Factory_lore §3)
#
# ⚠️ w,h here is the DEF's own <size>, verified 2026-08-13 against VFE-Factory's
# ThingDefs. It is NOT the placed footprint: spaced_pack() below tries both
# orientations, so a machine may land rotated and the placed rect records which.
# Autofarmer was ('Autofarmer',3,7) — the transpose of the real def (7,3) — which
# made the sheet and the placement agree with each other and both disagree with
# the game. Caught by BRIDGE (7a5ab88); shipbuild's rotation check now reads the
# def sizes directly and treats this table only as a fallback.
# All 18 re-checked against the defs; Autofarmer was the only one wrong.
MACHINES = {
    'A': [('Autofarmer',7,3,1),('Drill Platform',3,3,1),('Fishfarm',3,3,1)],
    'B': [('Smelter',3,4,4),('Masonry Saw',3,3,2),('Mincer',3,3,2),
          ('Crematorium',3,3,1),('Biofuel Refinery',3,4,4)],
    'C': [('Conveyor Oven',3,5,4),('Cannery',3,5,3),('Distillery',3,3,2)],
    'D': [('Autoloom',3,5,3),('Ammo Press',3,4,3)],
    'E': [('Assembler',5,5,5),('Alloy Forge',5,5,4),('Neutro Synth',5,3,3)],
    'F': [('Medicine Granulator',5,3,4),('Machining Bay',5,5,4)],
}
HOT = {'B','E'}; BOOSTER=(3,1); HEATSINK=(2,2); N_HEATSINK=4; N_BOOSTER=1
IO = {nm: io for machs in MACHINES.values() for (nm,w,h,io) in machs}

def spaced_pack(sub, rects):
    """Pack (label,w,h) rects into free tiles of `sub` (True=usable) leaving a 1-tile
    aisle around EACH machine: a rect is legal only if its footprint AND a 1-tile halo
    are all inside the pod and unoccupied. Machines still abut the aisle, not each other.
    Returns (placed[(label,x,y,w,h)], ok)."""
    hh, ww = sub.shape
    occ = ~sub
    placed = []; ok = True
    def fits(x,y,w,h):
        if x<1 or y<1 or x+w>ww-1 or y+h>hh-1: return False
        return not occ[y-1:y+h+1, x-1:x+w+1].any()   # footprint + 1-tile halo clear
    for label,w,h in sorted(rects, key=lambda r:-r[1]*r[2]):
        done=False
        # Orientation order is EXPLICIT and it is a packing convenience, not a
        # design intent. It used to read `{(w,h),(h,w)}` -- a set, so hash order
        # picked the winner and nothing chose it.
        #
        # ⚠️ It was reproducible, contrary to what I first claimed: BRIDGE measured
        # 5 interpreters x 5 PYTHONHASHSEEDs and got identical order every time,
        # because Python randomises hashing for str/bytes only, never for ints or
        # tuples of ints. The defect was never determinism -- it was that the code
        # read as though a rule existed when none did, so changing a machine's
        # dimensions could silently flip its orientation.
        #
        # Deliberately NOT "declared orientation first": the deck plan's intent and
        # the def's own size disagree for four machines (Autofarmer is def 7x3 and
        # drawn 3x7), so preferring the def would fight the plan. The packer does
        # not know the plan; it only knows fit. Which orientation actually landed
        # is recorded in the placed rect, and shipbuild flags def-vs-placement
        # transpositions as needsManualRotation -- that is where intent lives.
        #
        # 🔴 THIS CHANGE IS NOT A NO-OP, MEASURED: of the 9 non-square machines,
        # 5 sit in a DIFFERENT orientation in the committed build_sheet_15.json
        # than sorted() would choose -- Conveyor Oven, Cannery, Autoloom, Neutro
        # Synth and Medicine Granulator are all placed 5x3 where sorted() picks
        # 3x5. The old hash order was not even self-consistent as a rule: it took
        # the wider form for those five and the taller form for Autofarmer, which
        # is the clearest evidence that nothing chose it.
        #
        # So build_sheet_15.json PREDATES this rule and is authoritative until
        # someone regenerates deliberately. Regenerating WILL move those five and
        # that is intended cleanup, not a regression -- but it must be a decision,
        # re-checked against the deck plan and against shipbuild's rotation flags,
        # never a side effect of running this file to refresh something else.
        for (pw,ph) in sorted({(w,h),(h,w)}):
            if done: break
            for y in range(hh):
                for x in range(ww):
                    if fits(x,y,pw,ph):
                        occ[y:y+ph, x:x+pw]=True     # reserve footprint only (aisle shared)
                        placed.append((label,x,y,pw,ph)); done=True; break
                if done: break
        if not done:
            ok=False; placed.append((label+' [UNPLACED]',-1,-1,w,h))
    return placed, ok

# airlock (belt/pawn entry) per wing, from the skeleton
DOOR = {e['wing']: tuple(e['at']) for e in sk['elements']
        if e['type'] == 'door' and 'wing' in e}
LINK = sk.get('link', 9.9)                      # Factory Booster/Heatsink link radius §5
# thermal bank centers per hot wing, from the already-9.9-verified skeleton
BANK = {code: (r['bank'][0], r['bank'][1]) for code, r in sk['thermal'].items()}

def pod_mask(code):
    return (g == code)

elements = []          # typed, GLOBAL tile coords
report = {}

for code, machs in MACHINES.items():
    ox, oy = summary[code]['origin']
    mask = pod_mask(code)                       # global pod tiles
    sub = mask[oy:oy+ (np.where(mask)[0].max()-oy)+1,
               ox:ox+ (np.where(mask)[1].max()-ox)+1].copy()
    # pack ONLY the machines with aisle spacing INSIDE the pod. The thermal bank
    # (booster + 4 heatsinks) sits OUTBOARD per Factory_lore §5 and comes from the
    # skeleton (already 9.9-verified); it is re-checked below against the new centers.
    rects = [(nm, w, h) for (nm, w, h, io) in machs]
    placed, ok = spaced_pack(sub, rects)
    if not ok:
        print(f"  !! wing {code}: a rect went UNPLACED even with aisle spacing")
    occ  = np.zeros((H, W), bool)               # machine-occupied (global)
    machine_rects = []
    for (lab, x, y, w, h) in placed:
        if x < 0:
            continue
        base = lab.split('[')[0].strip()
        gx, gy = ox + x, oy + y
        occ[gy:gy+h, gx:gx+w] = True
        if any(k in base for k in ('Booster', 'Heatsink')):
            kind = 'booster' if 'Booster' in base else 'heatsink'
            elements.append(dict(type=kind, wing=code, rect=[gx, gy, w, h]))
            continue
        elements.append(dict(type='machine', wing=code, name=base, rect=[gx, gy, w, h]))
        machine_rects.append((base, gx, gy, w, h))

    # ---- 2. factory-floor apron: machine tiles + 1-tile aisle, clipped to pod disk ----
    apron = occ.copy()
    ys, xs = np.where(occ)
    for yy, xx in zip(ys, xs):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                ny, nx = yy+dy, xx+dx
                if 0 <= ny < H and 0 <= nx < W and mask[ny, nx]:
                    apron[ny, nx] = True
    apron_tiles = [[int(x), int(y)] for y, x in zip(*np.where(apron))]
    elements.append(dict(type='apron', wing=code, tiles=apron_tiles))

    # ---- 3. hopper faces: `io` tiles on each machine's free perimeter, biased to door ----
    door = DOOR.get(code)
    hoppers_placed = 0; hoppers_needed = 0
    taken = occ.copy()                          # can't put a hopper on another machine
    for (base, gx, gy, w, h) in machine_rects:
        need = IO.get(base, 1); hoppers_needed += need
        # candidate perimeter tiles: pod tiles orthogonally adjacent to this machine
        cand = []
        for yy in range(gy-1, gy+h+1):
            for xx in range(gx-1, gx+w+1):
                on_edge = (yy in (gy-1, gy+h) or xx in (gx-1, gx+w))
                inside_col = gx <= xx < gx+w; inside_row = gy <= yy < gy+h
                ortho = (on_edge and (inside_col or inside_row))
                if not ortho: continue
                if not (0 <= yy < H and 0 <= xx < W): continue
                if mask[yy, xx] and not taken[yy, xx]:
                    cand.append((xx, yy))
        # bias toward the airlock so hoppers meet the incoming belt trunk
        if door:
            cand.sort(key=lambda p: (p[0]-door[0])**2 + (p[1]-door[1])**2)
        for (xx, yy) in cand[:need]:
            taken[yy, xx] = True; hoppers_placed += 1
            elements.append(dict(type='hopper', wing=code, machine=base, at=[int(xx), int(yy)]))

    # ---- 4. belt-to-machine stub: airlock -> nearest machine hopper (BFS over pod tiles) ----
    stub = []
    if door and machine_rects:
        walk = mask & ~occ                      # walkable pod tiles (not under a machine)
        # nearest hopper tile to the door
        hops = [tuple(e['at']) for e in elements
                if e['type'] == 'hopper' and e['wing'] == code]
        if hops:
            target = min(hops, key=lambda p: (p[0]-door[0])**2 + (p[1]-door[1])**2)
            # BFS door -> target through walkable tiles
            start = (door[0], door[1])
            prev = {start: None}; q = deque([start]); found = False
            while q:
                cx, cy = q.popleft()
                if (cx, cy) == target: found = True; break
                for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    nx, ny = cx+dx, cy+dy
                    if (nx, ny) in prev: continue
                    if not (0 <= nx < W and 0 <= ny < H): continue
                    if (nx, ny) == target or (walk[ny, nx]):
                        prev[(nx, ny)] = (cx, cy); q.append((nx, ny))
            if found:
                node = target
                while node is not None:
                    stub.append([int(node[0]), int(node[1])]); node = prev[node]
                stub.reverse()
        elements.append(dict(type='belt_stub', wing=code, pts=stub))

    # ---- 5. thermal spine (hot wings): carry the skeleton's outboard bank + RE-VERIFY
    #         the 9.9-tile link against the NEW aisle-spaced machine centers (§5) ----
    thermal = None
    if code in HOT and code in BANK:
        bx, by = BANK[code]
        elements.append(dict(type='booster', wing=code, rect=[int(round(bx-1)), int(round(by)), 3, 1]))
        for k, (dx, dy) in enumerate([(-2,1),(1,1),(-2,-2),(1,-2)]):
            elements.append(dict(type='heatsink', wing=code,
                                 rect=[int(round(bx+dx)), int(round(by+dy)), 2, 2]))
        worst = 0.0; worst_lab = None
        for (base, gx, gy, w, h) in machine_rects:
            cx, cy = gx + w/2.0, gy + h/2.0
            dist = math.hypot(cx - bx, cy - by)
            if dist > worst: worst, worst_lab = dist, base
        thermal = dict(bank=[round(bx,1), round(by,1)], worst_machine=worst_lab,
                       worst_dist=round(worst,2), within_link=bool(worst <= LINK))

    report[code] = dict(machines=len(machine_rects), apron=len(apron_tiles),
                        hoppers_placed=hoppers_placed, hoppers_needed=hoppers_needed,
                        stub_len=len(stub), thermal=thermal)

json.dump(dict(elements=elements, report=report), open('build_sheet_15.json', 'w'))

print("BUILD SHEET #15  (PASS 2 — machines + floor + hoppers + belt stubs)\n")
print(f"{'Wing':<5}{'machines':>9}{'apron':>7}{'hoppers':>16}{'stub':>6}")
print('-'*45)
allhop = True
for code, r in report.items():
    hop = f"{r['hoppers_placed']}/{r['hoppers_needed']}"
    allhop &= (r['hoppers_placed'] == r['hoppers_needed'])
    print(f"{code:<5}{r['machines']:>9}{r['apron']:>7}{hop:>16}{r['stub_len']:>6}")
print(f"\nall hoppers placed on-floor: {allhop}")

print("\nTHERMAL 9.9-tile RE-VERIFY vs aisle-spaced machine centers (Factory_lore §5):")
allok = True
for code, r in report.items():
    t = r.get('thermal')
    if not t: continue
    flag = 'OK' if t['within_link'] else '*** EXCEEDS 9.9 ***'
    allok &= t['within_link']
    print(f"  wing {code}: worst {t['worst_machine']} @ {t['worst_dist']} tiles  [{flag}]")
assert allhop, "not all hoppers landed on the pod floor — re-pack"
assert allok, "thermal link radius exceeded after re-pack — reposition bank"
print("\nwrote build_sheet_15.json   (hoppers + thermal PASSED)")
