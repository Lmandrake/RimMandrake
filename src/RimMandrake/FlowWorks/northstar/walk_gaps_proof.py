"""WALK GAPS live proof: the FlowWorks mechanisms the 2026-10-22 owner walk leans on that NO proof row covered (BENCH proof
author, 2026-10-22; inventory in Transient/pile_2026-10-22/proof_author.md). One row per (item, criterion); every row names both.

  python.exe src/RimMandrake/FlowWorks/northstar/walk_gaps_proof.py [out.json] [--origin X,Z] [--fresh-map] [--only a,b]
             [--level-ticks N]
  python3    src/RimMandrake/FlowWorks/northstar/walk_gaps_proof.py --mock [--mock-faults a,b] [--only a,b]
             every path offline against FakeBridge (a small world model, NOT the mod); every row is written SKIP with the
             verdict it would have reached kept under detail.mock (proves the script, never the game)

Run from the repo root with python.exe on the walk tier (fw_gss_sitting) or the minimal list; the bridge must be held.
Exit 0 = every row PASS; 1 = a FAIL; 2 = a row could not be measured. WRITTEN OFFLINE 2026-10-22: every row is OWED to its first
live run, and the plot geometry below carries UNVERIFIED LAYOUT GUESSES (named); a guess that is wrong reads UNMEASURED/SITE,
never FAIL.

Calls: JawaBench tools; RM_PromotionProofs ProofLadder / ProofPitTravel / ProofForcedFlyer; RM_NorthstarProofs.ProofTrap /
ProofLevelLink / ProofPumpPorts (fixer I, 2026-10-22); RM_LineProofs ProofSurface / ProofPitWater / ProofHoseRole / ProofHoseLine;
RM_FluidIdentityProof.ProofFillWithFluid; the hose probe verbs tank / filltank / net / lay. ProofTankSettle is NOT owed: storage
tanks do not level (owner ruling); the A3 perf rows live in pipe_levelling_perf_proof.py.

Rows (plot coords from --origin, default 40,40; site rect origin-(2,6) .. +64 x 66):
  COVER_DECON_DROPS_RIDER     PIT_COVER_BUILD_DECONSTRUCT_DROPS_TOO A2. Walk stop 3 has HIM deconstruct a gatehouse plank.
     scene A: pit x2..4 z2..4 dug 8 notches (4 m, a cover needs superdeep); RM_PitCover_PlankLattice on (2,3); a drafted
     colonist on it; a Deconstruct designation (jawa/designate_batch, the player's own order) and an undrafted colonist with
     Construction on, on the lip (0,3). PROVE the real deconstruct JOB (DestroyMode.Deconstruct), never destroy_batch (Vanish)
     nor damage (KillFinalize: lines_proof COVER_BREAK_DROPS_RIDER). EXPECT the cover gone, ProofTrap descents +1 for the
     rider and held=True. LIES: a rider the spawn put off the cover never rode it; a designation that never took; nobody did
     the job (cover still there at the bound: UNMEASURED/SITE, never FAIL).
  LADDER_RAISED_FROM_BELOW / LADDER_NO_LOWER_FROM_BELOW / LADDER_LOWERED_FROM_RIM / LADDER_RAISED_FROM_RIM
                              FLOWWORKS_RAIL_LADDER_BUILD_LOWER_FROM_ABOVE A4 (validation.py ladder_rails_live spells it).
     scene B: pit x10..12 z2..4 dug 6 (3 m); RM_Ladder on (10,3) rot 3 (West: its top square is (9,3) on the rim, as
     lines_proof scene H). Every other player colonist DRAFTED first (a drafted pawn takes no job), so "the only colonist in
     the pit" is true. (1) lowered, the pit colonist undrafted, order_raise -> raised within the bound. (2) order_lower with
     him still in the pit -> after the window it is STILL raised (no job from below). (3) a rim colonist spawned undrafted on
     (6,3) -> lowered within the bound. (4) order_raise with the rim colonist -> raised. LIES: a ladder raised by the staging
     write, not a pawn (only order_* is used after the first 'lower'); a pit colonist who cannot work at all makes (2) pass
     falsely -> (2) is scored only when (1) PASSed (the same pawn did a ladder job from below).
  TRAVEL_FLYER_FREE_ON_FLOOR / TRAVEL_PERSON_HELD_CONTROL / TRAVEL_MARKED_FREE / TRAVEL_THROWN_FLYER_UNHURT
                              FLOWWORKS_PIT_TRAVEL_BUILD_FLY_JUMP_FLOAT A4 (STATE reads only: no flight is watched, owner
                              2026-09-25). The jump-pack half of A4 is live_session.py B4_access_jump_pack_in_no_fall.
     scene C: pits x18..20 and x24..26, z2..4, dug 6 (3 m). A Duck (Core, MaxFlightTime 30) spawned on (19,3): ProofPitTravel
     reads canFly free=True held=False. The control, a colonist on (25,3): free=False held=True (the instrument can go red).
     A race tagged RM_PitTravelExtension (first that spawns of MARKED_RACES): jumps|floats, free, not held; none loaded on this
     tier = UNMEASURED/SITE. Thrown: a second Duck on the rim (16,3) and a colonist on the rim (23,3) each thrown
     (ProofForcedFlyer, PawnFlyer_Stun) into the pits; EXPECT the duck gains no hediff while the thrown colonist DOES (the
     can-fail control: a person still falls). Control unhurt -> the duck row is UNMEASURED/HARNESS (the read is blind).
  TANKS_APART_HOLD / TANKS_JOINED_ONE_LEVEL
                              walk stop 6 premise (card closes PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL and
                              WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES); no ledger criterion names it: the row id is the claim.
     scene D: scenario C7's three ground tanks (RM_LiquidTank, RM_LiquidTankTall, RM_UniversalCargoTank) on a pipe at z+2 with
     the same two-cell gap, filled to 10% / 40% / 80% of capacity (fresh water, Store mode as staged). (D1) 300 ticks apart:
     nothing moves. (D2) the gap piped (jawa/build_batch, what the walk's seat does), net:x,z reaches all three, 2500 ticks
     (the walk's one hour): EXPECT units move toward one fill fraction, total conserved to the unit. READ OF THE CODE 2026-10-22:
     RM_LiquidNetKernel.SettlePlan says "Store tanks only buffer" and RM_Levelling links only open HOSE ends, so this row is
     expected to go RED; the walk card must not be asked over a mechanism that does not exist.
  PONDS_DIFFERENT_LIQUIDS_NO_MIX
                              PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL A5. Runs BEFORE A4 (RM_Levelling.Moves is a process
                              static: read as a delta, with no other link alive).
  PONDS_HOSE_LEVEL           PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL A4.
     scenes E (z+20, the A4 rig) and F (z+40, the A5 rig), same shape (POND_RIG, checked offline by pond_rig_problems): two
     dug pools 3x3, 4 notches deep (equal floors, so equal dL per square = equal surface), pool 1 at x0..2 z-4..-2 and pool 2
     at x0..2 z8..10 (plot-local to the rig); hose reel 1 built West with its footprint at (10,2) and reel 2 at (10,4), both
     coupled by their East edges to ONE RM_UniversalPipe run x12 z2..5, so the two links are one network component with two
     open ends (the RM_Levelling link). RULED OUT 2026-10-22: two reels touching one RM_LiquidTank (the first layout guess) --
     a tank is a component MEMBER, not a conductor (RM_NetComponents.Build attaches a Tank end and never walks through it), so
     each reel was its own component with one port (Ports.Count < 2): three belt runs read linked=False, moves=0. Before any
     tick the coupling is read back (ProofLevelLink intakes>=1 and outflows>=1 on each reel = both ends on one component);
     not so = UNMEASURED/SITE. Reel 1 laid to the lip (3,-3) and set Intake, reel 2 to (3,9) and set Outflow. A5: pool 1 water F=4,
     pool 2 RM_Fluid_Chemfuel F=1; EXPECT RM_Levelling.Moves +0 over 1500 ticks, both pools' dL unchanged and a reel's inspect
     reads "different liquids never mix". A4: pool 1 water F=4, pool 2 water F=1; EXPECT Moves > 0, the per-square dL gap
     <= 100 dL (1 cm over a square metre) within --level-ticks, the total dL conserved within 1 %, and a reel read
     "Levelling: flowing" while it moved. LIES: a rig with no link (ProofLevelLink links=0 at every read) moves nothing and is
     UNMEASURED/SITE, never a PASS for A5; evaporation is not levelling (the total is read). The reel's levelling state and the
     counters (links = RM_Levelling.LastLinks, moves = RM_Levelling.Moves) are read through RM_NorthstarProofs.ProofLevelLink
     (no tank stands on the rig, so the probe's net verb has no origin); an old deploy without the hook reads the inspect line
     for the word but has no counters, so both rows are UNMEASURED/HARNESS there.
  PORTS_PIPE_AND_REEL_ON_SIDES
  PORTS_ONE_HOSE_PER_SIDE
  PORTS_CORNER_REFUSED       FLOWWORKS_PUMP_PORTS_REBUILD_ONE_PER_SIDE A4 (walk stop 5), read by RM_NorthstarProofs.ProofPumpPorts.
     scene G: an RM_LiquidPump at (52,4); a pipe on its West side (51,4) and (50,4); reel A built West with its body on the
     East side (footprint (53,4)); reels B (52,-1) and C (55,-1) both laid with their free ends to the South side (52,3) (not
     North: (52,5) is diagonal to the pipe, which a free end may pick); reel D (58,9) laid to the SE corner (53,3) (reels are
     2x2: A covers (53..54,4..5), so NE is taken).
     EXPECT W=pipe and E=reel:A:c (a pipe and a hose on two sides, both kept); S holds two
     free ends, exactly one coupled and it is the LOWER thing id (one hose per side); corner>=1 with cornerCoupled=0. The
     ledger A4 text predates the owner's 2026-10-20 correction (pipes join wherever adjacent and never take a port): its
     pipe-blocks-a-hose and diagonal-pipe-off clauses are not rows here. A lay refused (nothing on S) is UNMEASURED/SITE.

ANTI-GUESSING NOTES
- Counters (RM_Levelling.Moves / LastLinks, ProofTrap descents) are statics or per-pawn tallies: read before and after.
- A freshly spawned colonist may be incapable of Construction: set_work_priority reports readBack; refused = UNMEASURED/SITE.
- jawa/designate_batch adds the designation with no god-mode shortcut: the deconstruct is a real job (bounded by --job-ticks).
- The start colony's colonists are drafted for the whole run (they would otherwise take the ladder and deconstruct jobs).
"""
import argparse
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
UTILS = os.path.abspath(os.path.join(HERE, "..", "..", "Utils"))
if UTILS not in sys.path:
    sys.path.insert(0, UTILS)
import validation_core as V  # noqa: E402

LPROOF = "RimMandrake.FlowWorks.Machinery.RM_LineProofs"
PROMO = "RimMandrake.FlowWorks.RM_PromotionProofs"
NPROOF = "RimMandrake.FlowWorks.RM_NorthstarProofs"
FLUIDP = "RimMandrake.FlowWorks.RM_FluidIdentityProof"
COVER_DEF = "RM_PitCover_PlankLattice"
WATER_LIQ = "RM_Liquid_FreshWater"        # tank liquid (proof_hose.LIQUID_WATER)
WATER_FLUID = "RM_Fluid_Water"            # dug-cell fluid (scenario C7)
OIL_FLUID = "RM_Fluid_Chemfuel"           # dug-cell fluid (scenario C5)
FLYER_KIND = "Duck"                       # Core Races_Animal_ChickenGroup.xml: MaxFlightTime 30
MARKED_RACES = ["RM_Huldu", "RM_Sipper", "RSW_Tooke", "RSW_FrogDog", "RSW_SandLeaper", "RSW_CaveLemming", "RM_Bulloo",
                "RM_Drifter", "RM_Gawpsack", "RM_OcularJelly", "RM_Garsulix"]   # Patches/Canals/FlowWorks_PitTravel.xml
TANKS = [("RM_LiquidTank", 2, 0.10), ("RM_LiquidTankTall", 6, 0.40), ("RM_UniversalCargoTank", 10, 0.80)]
DL_PER_CM_SQUARE = 100                    # 1 cm over 1 m^2 = 10 L = 100 dL

ROW_IDS = ["COVER_DECON_DROPS_RIDER",
           "LADDER_RAISED_FROM_BELOW", "LADDER_NO_LOWER_FROM_BELOW", "LADDER_LOWERED_FROM_RIM", "LADDER_RAISED_FROM_RIM",
           "TRAVEL_FLYER_FREE_ON_FLOOR", "TRAVEL_PERSON_HELD_CONTROL", "TRAVEL_MARKED_FREE", "TRAVEL_THROWN_FLYER_UNHURT",
           "TANKS_APART_HOLD", "TANKS_JOINED_ONE_LEVEL",
           "PONDS_DIFFERENT_LIQUIDS_NO_MIX", "PONDS_HOSE_LEVEL",
           "PORTS_PIPE_AND_REEL_ON_SIDES", "PORTS_ONE_HOSE_PER_SIDE", "PORTS_CORNER_REFUSED"]
ROW_ITEM = {
    "COVER_DECON_DROPS_RIDER": ("PIT_COVER_BUILD_DECONSTRUCT_DROPS_TOO", "A2"),
    "LADDER_RAISED_FROM_BELOW": ("FLOWWORKS_RAIL_LADDER_BUILD_LOWER_FROM_ABOVE", "A4"),
    "LADDER_NO_LOWER_FROM_BELOW": ("FLOWWORKS_RAIL_LADDER_BUILD_LOWER_FROM_ABOVE", "A4"),
    "LADDER_LOWERED_FROM_RIM": ("FLOWWORKS_RAIL_LADDER_BUILD_LOWER_FROM_ABOVE", "A4"),
    "LADDER_RAISED_FROM_RIM": ("FLOWWORKS_RAIL_LADDER_BUILD_LOWER_FROM_ABOVE", "A4"),
    "TRAVEL_FLYER_FREE_ON_FLOOR": ("FLOWWORKS_PIT_TRAVEL_BUILD_FLY_JUMP_FLOAT", "A4"),
    "TRAVEL_PERSON_HELD_CONTROL": ("FLOWWORKS_PIT_TRAVEL_BUILD_FLY_JUMP_FLOAT", "A4"),
    "TRAVEL_MARKED_FREE": ("FLOWWORKS_PIT_TRAVEL_BUILD_FLY_JUMP_FLOAT", "A4"),
    "TRAVEL_THROWN_FLYER_UNHURT": ("FLOWWORKS_PIT_TRAVEL_BUILD_FLY_JUMP_FLOAT", "A4"),
    "TANKS_APART_HOLD": ("PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL", "walk-stop-6 premise (no ledger criterion)"),
    "TANKS_JOINED_ONE_LEVEL": ("PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL", "walk-stop-6 premise (no ledger criterion)"),
    "PONDS_DIFFERENT_LIQUIDS_NO_MIX": ("PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL", "A5"),
    "PONDS_HOSE_LEVEL": ("PIPE_LEVELLING_BUILD_WATER_FINDS_ITS_LEVEL", "A4"),
    "PORTS_PIPE_AND_REEL_ON_SIDES": ("FLOWWORKS_PUMP_PORTS_REBUILD_ONE_PER_SIDE", "A4"),
    "PORTS_ONE_HOSE_PER_SIDE": ("FLOWWORKS_PUMP_PORTS_REBUILD_ONE_PER_SIDE", "A4"),
    "PORTS_CORNER_REFUSED": ("FLOWWORKS_PUMP_PORTS_REBUILD_ONE_PER_SIDE", "A4"),
}
MISSING_HOOKS = {}   # ProofLevelLink / ProofPumpPorts built 2026-10-22 (fixer I); ProofTankSettle not owed (tanks do not level)


def parse(txt):
    kv = {}
    for tok in str(txt).split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            kv[k] = v
    return kv


def num(kv, k, default=None):
    try:
        return int(str(kv.get(k)).split("/")[0])
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------- pure verdicts (selftest_walk_gaps_proof.py proves them)
def decon_verdict(before, after, cover_left, rider):
    """(status, cls). before/after: ProofTrap kv. Cover still standing = nobody did the job (SITE)."""
    if cover_left is None or not before or not after:
        return "UNMEASURED", "HARNESS"
    if cover_left:
        return "UNMEASURED", "SITE"
    if before.get("held") != "False":
        return "UNMEASURED", "SITE"
    fell = (num(after, "descents") or 0) - (num(before, "descents") or 0)
    named = str(rider).replace("Thing_", "") in str(after.get("last"))
    return ("PASS" if fell >= 1 and after.get("held") == "True" and named else "FAIL"), "MOD"


def ladder_wait_verdict(reached, want):
    """reached: the ladder's last ProofLadder kv after the bound; want: raised True/False."""
    if not reached or reached.get("present") != "True":
        return "UNMEASURED", "SITE"
    return ("PASS" if reached.get("raised") == str(bool(want)) else "FAIL"), "MOD"


def travel_free_verdict(kv, want_free):
    """ProofPitTravel kv; want_free True for a flyer/marked race, False for the person control."""
    if not kv or kv.get("pawn") in (None, "none"):
        return "UNMEASURED", "SITE"
    if kv.get("setting") == "False":
        return "UNMEASURED", "SITE"
    ok = (kv.get("free") == "True" and kv.get("held") == "False") if want_free else (kv.get("free") == "False" and kv.get("held") == "True")
    return ("PASS" if ok else "FAIL"), "MOD"


def thrown_verdict(flyer_new, person_new, launched):
    """flyer_new / person_new: hediffs gained after the throw (lists, None = unread); launched: both throws accepted."""
    if not launched or flyer_new is None or person_new is None:
        return "UNMEASURED", "HARNESS"
    if not person_new:
        return "UNMEASURED", "HARNESS"         # the control did not fall: the read is blind, the flyer's 'unhurt' proves nothing
    # HARNESS (belt live 2026-10-22): RM_PitExposure is the pit's temperature exposure, gained by anything standing in a pit
    # (the thrown duck AND the person both got it): it is not a fall injury, so it does not count against the flyer
    hurt = [h for h in flyer_new if h != "RM_PitExposure"]
    return ("PASS" if not hurt else "FAIL"), "MOD"


def spread(fracs):
    return (max(fracs) - min(fracs)) if fracs else None


def tanks_verdict(u0, u1, caps):
    """u0/u1 units per tank before and after the joined window. PASS: moved toward one fraction, total conserved."""
    if not u0 or not u1 or None in u0 or None in u1 or not caps or None in caps:
        return "UNMEASURED", "HARNESS", {}
    f0 = [u / float(c) for u, c in zip(u0, caps)]
    f1 = [u / float(c) for u, c in zip(u1, caps)]
    d = {"fractionsBefore": [round(x, 4) for x in f0], "fractionsAfter": [round(x, 4) for x in f1],
         "spreadBefore": round(spread(f0), 4), "spreadAfter": round(spread(f1), 4), "totalBefore": sum(u0), "totalAfter": sum(u1),
         "level": spread(f1) <= 0.02}
    if sum(u0) != sum(u1):
        return "FAIL", "MOD", dict(d, why="units not conserved")
    if u0 == u1:
        return "FAIL", "MOD", dict(d, why="nothing moved between joined Store tanks")
    return ("PASS" if spread(f1) < spread(f0) else "FAIL"), "MOD", d


def ponds_level_verdict(moves, dl0, dl1, cells, linked, flowing_seen):
    """moves: Moves delta; dl0/dl1: (pool1, pool2) dL before / at the end; cells per pool; linked: levelLinks ever > 0."""
    if None in (moves,) or not dl0 or not dl1 or None in dl0 or None in dl1 or not cells:
        return "UNMEASURED", "HARNESS"
    if not linked:
        return "UNMEASURED", "SITE"
    t0, t1 = sum(dl0), sum(dl1)
    gap = abs(dl1[0] - dl1[1]) / float(cells)
    if moves <= 0 or abs(t1 - t0) > 0.01 * max(t0, 1):
        return "FAIL", "MOD"
    if gap > DL_PER_CM_SQUARE:
        start_gap = abs(dl0[0] - dl0[1]) / float(cells)
        return ("UNMEASURED", "HARNESS") if gap < start_gap else ("FAIL", "MOD")   # moving but the window ended first
    return ("PASS" if flowing_seen else "FAIL"), "MOD"


def ponds_nomix_verdict(moves, dl0, dl1, linked, readout):
    if moves is None or not dl0 or not dl1 or None in dl0 or None in dl1:
        return "UNMEASURED", "HARNESS"
    if not linked:
        return "UNMEASURED", "SITE"
    ok = moves == 0 and tuple(dl0) == tuple(dl1) and ("DifferentLiquids" in (readout or "") or
                                                      "different liquids never mix" in (readout or ""))
    return ("PASS" if ok else "FAIL"), "MOD"


# The A4/A5 rig, plot-local to the rig (the caller adds the rig's z). Reels are footprint corners of a 2x2 built West
# (validation_core.reel_west); a pipe run joins their East edges.
POND_RIG = {"pools": [(0, -4), (0, 8)], "reels": [(10, 2), (10, 4)], "pipes": [(12, 2), (12, 3), (12, 4), (12, 5)], "tanks": [],
            "ends": [(3, -3), (3, 9)]}
# The layout the three 2026-10-22 belt runs used (linked=False, moves=0): kept so the selftest proves the checker refuses it.
TANK_RIG_20261022 = {"pools": [(0, -4), (0, 8)], "reels": [(10, 2), (10, 4)], "pipes": [], "tanks": [(12, 3)],
                     "ends": [(3, -3), (3, 9)]}
HOSE_REACH = 40 - 5        # HoseMath.DefaultMaxLength 40, less the ~4.4-cell straight lead-out


def _rect(c, w, h):
    return {(c[0] + i, c[1] + j) for i in range(w) for j in range(h)}


def _edge_nbrs(cells):
    """The cells edge-adjacent to a footprint, outside it (HosePortRule.Pick couples across a shared edge only)."""
    return {(x + dx, z + dz) for x, z in cells for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))} - set(cells)


def pond_rig_problems(lay):
    """[] when the rig's geometry makes ONE levelling link, else why not. A model of the C# rules read 2026-10-22, not the
    game: a reel couples to a pipe or tank across a shared edge (HosePorts.RawFind / HosePortRule.Pick); pipes conduct, 4-way
    (RM_NetComponents.Conducts), a tank does not (Build attaches it as a member); a link needs >= 2 open ends on one component
    (RM_Levelling.Tick); a free end beside a pipe/tank/reel couples to it and is no open port (HosePorts.FindAt); an end
    resolves the first dug square of the end and its 8 neighbours (RM_Levelling.Resolve)."""
    probs = []
    pools = [_rect(p, 3, 3) for p in lay["pools"]]
    reels = [_rect(r, 2, 2) for r in lay["reels"]]
    pipes = set(lay["pipes"])
    tanks = [_rect(t, 2, 2) for t in lay["tanks"]]
    solid = [("pipe", {p}) for p in pipes] + [("tank", t) for t in tanks] + [("reel", r) for r in reels]
    for i, (k, a) in enumerate(solid):
        for p in pools:
            if a & p:
                probs.append("%s %s stands in a pool" % (k, sorted(a)[0]))
        for k2, b in solid[i + 1:]:
            if a & b:
                probs.append("%s %s overlaps %s %s" % (k, sorted(a)[0], k2, sorted(b)[0]))
    comp, n = {}, 0                       # 4-connected pipe runs
    for p in sorted(pipes):
        if p in comp:
            continue
        n += 1
        todo = [p]
        while todo:
            q = todo.pop()
            if q in comp or q not in pipes:
                continue
            comp[q] = n
            todo += [(q[0] + 1, q[1]), (q[0] - 1, q[1]), (q[0], q[1] + 1), (q[0], q[1] - 1)]
    seen = []
    for r, fp in zip(lay["reels"], reels):
        nb = _edge_nbrs(fp)
        runs = {comp[c] for c in nb if c in comp}
        if any(nb & t for t in tanks):
            probs.append("reel %s touches a tank: a tank is a member, not a conductor (one port per component)" % (r,))
        if len(runs) != 1:
            probs.append("reel %s touches %d pipe runs (wants exactly 1)" % (r, len(runs)))
        seen.append(runs)
    if len(seen) == 2 and (len(seen[0]) != 1 or seen[0] != seen[1]):
        probs.append("the two reels are not on one pipe run: two components, one open end each")
    for k, (e, own) in enumerate(zip(lay["ends"], pools)):
        other = pools[1 - k] if len(pools) == 2 else set()
        near8 = {(e[0] + dx, e[1] + dz) for dx in (-1, 0, 1) for dz in (-1, 0, 1)}
        if e in own or e in other:
            probs.append("end %s lies in a pool (aim at the lip)" % (e,))
        if not (near8 & own):
            probs.append("end %s is not beside its pool" % (e,))
        if near8 & other:
            probs.append("end %s also reaches the other pool" % (e,))
        for kind, a in solid:
            if e in a or (_edge_nbrs({e}) & a):
                probs.append("end %s couples to a %s (no open port)" % (e, kind))
        r = lay["reels"][k]
        if ((e[0] - r[0]) ** 2 + (e[1] - r[1]) ** 2) ** 0.5 > HOSE_REACH:
            probs.append("end %s is beyond a shipped hose's reach from %s" % (e, r))
    return probs


def ports_parse(txt):
    """'PUMPPORTS N=a+b E=.. S=.. W=.. coupled=n corner=n cornerCoupled=n' -> ({side: [entry, ..]}, {k: int})."""
    sides, nums = {}, {}
    for tok in (txt or "").split()[1:]:
        k, _, v = tok.partition("=")
        if k in ("N", "E", "S", "W"):
            sides[k] = [] if v == "none" else v.split("+")
        elif v.lstrip("-").isdigit():
            nums[k] = int(v)
    return sides, nums


def ports_sides_verdict(sides):
    """W holds a pipe, E holds a coupled reel body: a pipe and a hose on two sides, both kept."""
    if not sides:
        return "UNMEASURED", "HARNESS"
    e = [x for x in sides.get("E", []) if x.startswith("reel:")]
    if "pipe" not in sides.get("W", []) or not e:
        return "UNMEASURED", "SITE"
    return ("PASS" if all(x.endswith(":c") for x in e) else "FAIL"), "MOD"


def ports_one_per_side_verdict(sides):
    """S holds two free ends: exactly one coupled, and it is the lower thing id."""
    if not sides:
        return "UNMEASURED", "HARNESS"
    n = [x.split(":") for x in sides.get("S", []) if x.startswith("free:")]
    if len(n) < 2:
        return "UNMEASURED", "SITE"
    kept = [int(i) for _k, i, c in n if c == "c"]
    low = min(int(i) for _k, i, _c in n)
    return ("PASS" if kept == [low] else "FAIL"), "MOD"


def ports_corner_verdict(nums):
    if "corner" not in nums or "cornerCoupled" not in nums:
        return "UNMEASURED", "HARNESS"
    if nums["corner"] < 1:
        return "UNMEASURED", "SITE"
    return ("PASS" if nums["cornerCoupled"] == 0 else "FAIL"), "MOD"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="40,40")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--only", default="", help="comma list of rows: " + ",".join(ROW_IDS))
    ap.add_argument("--job-ticks", type=int, default=3000, help="bound on a colonist job (deconstruct, ladder)")
    ap.add_argument("--level-ticks", type=int, default=6000, help="bound on the hose-levelling window")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--mock-faults", default="", help="comma list: " + ",".join(FakeBridge.FAULTS))
    a = ap.parse_args(argv)
    only = [x.strip().upper() for x in a.only.split(",") if x.strip()] or list(ROW_IDS)
    if set(only) - set(ROW_IDS):
        ap.error("unknown --only row(s) %s" % ",".join(sorted(set(only) - set(ROW_IDS))))
    faults = [f for f in a.mock_faults.split(",") if f]
    if set(faults) - set(FakeBridge.FAULTS):
        ap.error("unknown --mock-faults %s" % ",".join(sorted(set(faults) - set(FakeBridge.FAULTS))))
    if a.mock:
        raw = FakeBridge(faults)
    else:
        import proof_hose as PH          # noqa: E402  (bridge-side imports only on a live run)
        raw = PH.PB()
    B = V.guard(raw)
    out = a.out or (os.path.join(tempfile.gettempdir(), "walk_gaps_mock_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
                    if a.mock else os.path.join(HERE, "walk_gaps_result_%s.json" % time.strftime("%Y%m%dT%H%M%S")))
    rows = []
    res = {"script": "walk_gaps_proof.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a),
           "missingHooks": MISSING_HOOKS}
    if a.mock:
        res["mode"] = "mock"
    else:
        import driver_stamp
        driver_stamp.stamp(res, raw.call)

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        try:
            os.replace(out + ".tmp", out)
        except OSError:
            with open(out, "w", encoding="utf-8") as f:
                json.dump(res, f, indent=1, default=str)

    def row(rid, st, det, cls="MOD"):
        st, cls, det = V.PRE.judge(st, cls, det)
        if st == "FAIL" and cls != "MOD":
            st = "UNMEASURED"
        if a.mock:
            det = dict(det, mock=st)
            st = "SKIP"
        item, crit = ROW_ITEM[rid]
        rows.append({"id": rid, "status": st, "class": cls, "item": item, "criterion": crit, "detail": det})
        print("%-30s %-10s %-8s %s" % (rid, st, cls, json.dumps(det, default=str)[:300]), flush=True)
        save()

    def static(ty, method, arg, answer=False):
        r = B.call("jawa/static_call", type=ty, method=method, args=arg, _answer=answer) or {}
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        ok = r.get("success") is True and not txt.startswith("REFUSED")
        if not answer:
            V.require(ok, "%s answered" % method, txt[:200], cls="HARNESS")
        return (parse(txt) if ok else {}), txt

    def ticks(n):
        r = B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40)) or {}
        V.require(r.get("success") is not False, "the clock moved %d ticks" % n, r, cls="HARNESS")
        return r.get("success") is not False

    def poll(fn, bound, step=50):
        waited, v = 0, fn()
        while not v and waited < bound:
            if not ticks(step):
                return v, waited
            waited += step
            v = fn()
        return v, waited

    def dig(c, n, fill=-1):
        return B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=n, setFill=fill) or {}

    def pit(x0, z0, w, h, n):
        for x in range(x0, x0 + w):
            for z in range(z0, z0 + h):
                r = dig(P(x, z), n)
                V.require(r.get("depth", n) == n, "dug (%d,%d) to %d" % (x, z, n), r)

    def build(*ops):
        return B.call("jawa/build_batch", ops=";".join(o for o in ops if o), faction="player", wipeExisting=False) or {}

    def spawn(c, kind="Colonist", faction="player", answer=False):
        r = B.call("jawa/spawn_pawn", kindDef=kind, x=c[0], z=c[1], faction=faction, count=1, _answer=answer) or {}
        return ((r.get("pawns") or [{}])[0]).get("id")

    def draft(pid, on):
        return B.call("jawa/set_draft", pawnId=pid, drafted=on) or {}

    def health(pid):
        for p in (B.call("jawa/list_pawns", limit=500, includeHealth=True) or {}).get("pawns") or []:
            if str(p.get("id")).replace("Thing_", "") == str(pid).replace("Thing_", ""):
                return [h.get("def") for h in ((p.get("health") or {}).get("hediffs") or []) if isinstance(h, dict)]
        return None

    def trap(pid):
        return static(NPROOF, "ProofTrap", pid)

    def ladder(c, op="read"):
        return static(PROMO, "ProofLadder", "%d,%d,%s" % (c[0], c[1], op))

    def travel(c):
        return static(PROMO, "ProofPitTravel", "%d,%d" % c)

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)        # noqa: E731
    xz = lambda c: "%d,%d" % c                   # noqa: E731

    # ------------------------------------------------------------------ preflight
    if a.fresh_map and not a.mock:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok = True if a.mock else V._wait_playing(B, leave_s=0)[0]
    if not ok:
        for rid in only:
            row(rid, "UNMEASURED", {"why": "no game in Playing"}, cls="HARNESS")
        return 2
    probe = B.call("jawa/static_call", type=PROMO, method="ProofPitTravel", args="0,0", _answer=True) or {}
    if probe.get("success") is not True:
        for rid in only:
            row(rid, "UNMEASURED", {"why": "%s not in the loaded FlowWorks: %s" % (PROMO, str(probe)[:160])}, cls="HARNESS")
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        save()
        return 2
    if not a.mock:
        rect = (max(ox - 2, 1), max(oz - 6, 1), 64, 66)
        res["site_calm"] = V.site_calm(B)
        B.call("jawa/kill_hostiles")
        site_rows = []
        with V.scope("site"):
            V.prepare_site(B, rect, site_rows, "walk_gaps_site")
        bad = [r for r in site_rows if r.get("status") not in (None, "PASS")]
        if bad:
            for rid in only:
                row(rid, "UNMEASURED", {"why": "site not prepared", "rect": rect, "site": bad[:3]}, cls="SITE")
            return 2
    # the start colony drafted for the whole run: a drafted pawn takes no job (the ladder rows need 'the only colonist')
    start = [p.get("id") for p in (B.call("jawa/list_pawns", faction="player", limit=200) or {}).get("pawns") or []
             if not p.get("dead") and (p.get("kind") or "") not in ("", None) and "Colonist" in str(p.get("kind"))]
    res["startColonistsDrafted"] = [(pid, (B.call("jawa/set_draft", pawnId=pid, drafted=True, _answer=True) or {}).get("success"))
                                    for pid in start]

    ctx = dict(a=a, B=B, P=P, xz=xz, row=row, static=static, ticks=ticks, poll=poll, dig=dig, pit=pit, build=build,
               spawn=spawn, draft=draft, health=health, trap=trap, ladder=ladder, travel=travel, res=res, only=only)
    for name, fn in SCENES:
        mine = [r for r in SCENE_ROWS[name] if r in only]
        if mine:
            print("== scene %s (%s)" % (name, ",".join(mine)), flush=True)
            with V.scope(name):
                fn(ctx, mine)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    if a.mock:
        bad = [r["id"] for r in rows if r["detail"].get("mock") != "PASS"]
        print("MOCK: walk gaps: %d rows, mock verdicts not PASS: %s -> %s" % (len(rows), bad or "none", out))
        return 1 if any(r["detail"].get("mock") == "FAIL" for r in rows) else (2 if bad else 0)
    fails = [r for r in rows if r["status"] == "FAIL"]
    unm = [r for r in rows if r["status"] != "PASS"]
    print("walk gaps: %d rows, %d FAIL, %d not PASS -> %s" % (len(rows), len(fails), len(unm), out))
    return 1 if fails else (2 if unm else 0)


# ====================================================================== scenes
def scene_cover(ctx, mine):
    B, P, row, static = ctx["B"], ctx["P"], ctx["row"], ctx["static"]
    ctx["pit"](2, 2, 3, 3, 8)
    cov = P(2, 3)
    ctx["build"]("%s:%d,%d" % ((COVER_DEF,) + cov))
    ks, ts = static(LPROOF, "ProofSurface", ctx["xz"](cov))
    V.require(ks.get("s") == "Cover", "an intact pit cover on (2,3)", ts)
    rider = ctx["spawn"](cov)
    ctx["draft"](rider, True)
    worker = ctx["spawn"](P(0, 3))
    wp = B.call("jawa/set_work_priority", pawnId=worker, workType="Construction", priority=1, _answer=True) or {}
    V.require(wp.get("success") is True and wp.get("readBack") not in (0, None), "the worker may construct", wp, cls="SITE")
    ctx["ticks"](10)
    k0, t0 = ctx["trap"](rider)
    V.require(k0.get("pos") == ctx["xz"](cov), "the rider stands on the cover", t0)
    des = B.call("jawa/designate_batch", action="add", designation="Deconstruct", rect="%d,%d,1,1" % cov) or {}
    V.require((des.get("added") or 0) + (des.get("alreadyPresent") or 0) >= 1, "the Deconstruct designation took", des)

    def gone():
        lt = B.call("jawa/list_things", defName=COVER_DEF, rect="%d,%d,1,1" % cov, limit=1, _answer=True) or {}
        return lt.get("success") is not False and not (lt.get("things") or [])
    done, waited = ctx["poll"](gone, ctx["a"].job_ticks)
    ctx["ticks"](5)
    k1, t1 = ctx["trap"](rider)
    st, cls = decon_verdict(k0, k1, (not done), rider)
    row("COVER_DECON_DROPS_RIDER", st, {"before": t0, "after": t1, "designation": des, "jobTicks": waited,
                                         "workPriority": wp}, cls=cls)
    ctx["draft"](worker, True)          # out of the ladder rows: a free colonist on the surface would take their jobs


def scene_ladder(ctx, mine):
    P, row = ctx["P"], ctx["row"]
    ctx["pit"](10, 2, 3, 3, 6)
    lad = P(10, 3)
    ctx["build"]("RM_Ladder:%d,%d,3" % lad)
    ctx["ticks"](2)
    k, t = ctx["ladder"](lad, "lower")
    V.require(k.get("present") == "True" and k.get("raised") == "False", "the ladder stands lowered", t)
    V.require(k.get("top") == ctx["xz"](P(9, 3)), "its top square is the rim (9,3)", t)
    below = ctx["spawn"](P(11, 3))
    ctx["ticks"](5)
    # HARNESS (belt live 2026-10-22): the first run's 'pit colonist' read pos=97,41 -- not in this pit at all, so (1) measured
    # nothing. The row needs him ON the pit floor before the order.
    kb0, tb0 = ctx["trap"](below)
    V.require(kb0.get("pos") == ctx["xz"](P(11, 3)), "the pit colonist stands in the ladder's pit", tb0, cls="SITE")
    bound = ctx["a"].job_ticks

    def reads(want):
        def f():
            kv, _ = ctx["ladder"](lad)
            return kv if kv.get("raised") == str(want) else None
        return f
    # (1) raised from below
    ctx["ladder"](lad, "order_raise")
    got, w1 = ctx["poll"](reads(True), bound)
    k1, t1 = ctx["ladder"](lad)
    s1, c1 = ladder_wait_verdict(k1, True)
    tb, tbt = ctx["trap"](below)
    row("LADDER_RAISED_FROM_BELOW", s1, {"ladder": t1, "ticks": w1, "pitColonist": tbt}, cls=c1)
    # (2) no lower from below (scored only if (1) PASSed: the same pawn does ladder jobs)
    ctx["ladder"](lad, "order_lower")
    ctx["ticks"](min(bound, 1500))
    k2, t2 = ctx["ladder"](lad)
    s2, c2 = ladder_wait_verdict(k2, True)
    if s1 != "PASS":                    # the ladder never went up: 'stays raised' cannot be asked
        s2, c2 = "UNMEASURED", "SITE"
    row("LADDER_NO_LOWER_FROM_BELOW", s2, {"ladder": t2, "ordered": k2.get("ordered"), "want": k2.get("want"),
                                           "gate": "scored only after LADDER_RAISED_FROM_BELOW PASS", "first": s1}, cls=c2)
    # (3) a rim colonist lowers it (the pending order)
    rim = ctx["spawn"](P(6, 3))
    got, w3 = ctx["poll"](reads(False), bound)
    k3, t3 = ctx["ladder"](lad)
    s3, c3 = ladder_wait_verdict(k3, False)
    row("LADDER_LOWERED_FROM_RIM", s3, {"ladder": t3, "ticks": w3, "rimColonist": ctx["trap"](rim)[1]}, cls=c3)
    # (4) raised from the rim
    ctx["draft"](below, True)           # the pit colonist may climb out now; keep the rim colonist the only free one
    ctx["ladder"](lad, "order_raise")
    got, w4 = ctx["poll"](reads(True), bound)
    k4, t4 = ctx["ladder"](lad)
    s4, c4 = ladder_wait_verdict(k4, True)
    row("LADDER_RAISED_FROM_RIM", s4, {"ladder": t4, "ticks": w4, "rimColonist": ctx["trap"](rim)[1]}, cls=c4)


def scene_travel(ctx, mine):
    B, P, row = ctx["B"], ctx["P"], ctx["row"]
    ctx["pit"](18, 2, 3, 3, 6)
    ctx["pit"](24, 2, 3, 3, 6)
    # HARNESS (belt live 2026-10-22): 'held' is the superdeep trap's capture, which takes the player's own pawns only with
    # superdeepCapturesOwnFaction ON (climb_proof sets it for its run): the colonist control read held=False twice. On for
    # this scene, restored after.
    S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
    own0 = (B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field="superdeepCapturesOwnFaction") or {}).get("value")
    B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field="superdeepCapturesOwnFaction", value="True")
    try:
        person = ctx["spawn"](P(25, 3))
        ctx["draft"](person, True)
        # the pocket grid rebuilds on its own cadence (climb_proof waits SETTLE): 70 ticks before the person's read
        ctx["ticks"](70)
        kp, tp = ctx["travel"](P(25, 3))
    finally:
        if own0 is not None:
            B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field="superdeepCapturesOwnFaction", value=str(own0))
    # the duck is read 2 ticks after it lands (a free flyer walks out of the pit: at 70 ticks it was gone, pawn=none)
    duck = ctx["spawn"](P(19, 3), kind=FLYER_KIND, faction="none")
    ctx["ticks"](2)
    kd, td = ctx["travel"](P(19, 3))
    s, c = travel_free_verdict(kd, True)
    row("TRAVEL_FLYER_FREE_ON_FLOOR", s, {"read": td, "kind": FLYER_KIND, "canFly": kd.get("canFly")}, cls=c)
    s, c = travel_free_verdict(kp, False)
    row("TRAVEL_PERSON_HELD_CONTROL", s, {"read": tp}, cls=c)
    # a marked race: the first that spawns on this tier
    tried, km, tm, race = [], {}, "", None
    if "TRAVEL_MARKED_FREE" in mine:
        for r in MARKED_RACES:
            pid = ctx["spawn"](P(20, 4), kind=r, faction="none", answer=True)
            tried.append((r, bool(pid)))
            if pid:
                race = r
                ctx["ticks"](2)
                km, tm = ctx["travel"](P(20, 4))
                break
        if race is None:
            row("TRAVEL_MARKED_FREE", "UNMEASURED", {"why": "no RM_PitTravelExtension race is loaded on this tier", "tried": tried},
                cls="SITE")
        else:
            s, c = travel_free_verdict(km, True)
            if s == "PASS" and not (km.get("jumps") == "True" or km.get("floats") == "True"):
                s, c = "FAIL", "MOD"              # free, but not by the mark: the patch did not land on the race
            row("TRAVEL_MARKED_FREE", s, {"race": race, "read": tm, "tried": tried}, cls=c)
    # thrown: a duck and a person from the rims into the pits
    duck2 = ctx["spawn"](P(16, 3), kind=FLYER_KIND, faction="none")
    rimp = ctx["spawn"](P(23, 3))
    ctx["draft"](rimp, True)
    ctx["ticks"](2)
    h0d, h0p = ctx["health"](duck2), ctx["health"](rimp)
    bare = lambda pid: str(pid).replace("Thing_", "")       # noqa: E731  (ProofForcedFlyer matches Thing.ThingID)
    fd, tfd = ctx["static"](PROMO, "ProofForcedFlyer", "%s,%d,%d" % ((bare(duck2),) + P(19, 2)))
    fp, tfp = ctx["static"](PROMO, "ProofForcedFlyer", "%s,%d,%d" % ((bare(rimp),) + P(25, 2)))
    ctx["ticks"](240)
    h1d, h1p = ctx["health"](duck2), ctx["health"](rimp)
    new_d = None if h0d is None or h1d is None else [h for h in h1d if h not in h0d or h1d.count(h) > h0d.count(h)]
    new_p = None if h0p is None or h1p is None else [h for h in h1p if h not in h0p or h1p.count(h) > h0p.count(h)]
    s, c = thrown_verdict(new_d, new_p, fd.get("launched") == "True" and fp.get("launched") == "True")
    row("TRAVEL_THROWN_FLYER_UNHURT", s, {"duck": tfd, "person": tfp, "duckNew": new_d, "personNew": new_p,
                                          "control": "the thrown colonist must gain a hediff, else the read is blind"}, cls=c)
    for pid in (duck, person, duck2, rimp):
        if pid:
            B.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish", _answer=True)


def scene_tanks(ctx, mine):
    B, P, row = ctx["B"], ctx["P"], ctx["row"]
    bx, bz = 30, 10
    roots = [P(bx + dx, bz) for _d, dx, _f in TANKS]
    pipes = [P(bx + x, bz + 2) for x in (1, 2, 3, 6, 7, 8, 9, 10, 11)]
    gap = [P(bx + 4, bz + 2), P(bx + 5, bz + 2)]
    ctx["build"](*(["%s:%d,%d" % ((d,) + r) for (d, _dx, _f), r in zip(TANKS, roots)] +
                   ["RM_UniversalPipe:%d,%d" % c for c in pipes]))
    ctx["ticks"](2)
    caps = []
    for (d, _dx, frac), r in zip(TANKS, roots):
        t = B.hp("tank:%d,%d" % r)
        cap = t.get("capacity")
        caps.append(cap)
        if cap:
            B.hp("filltank:%d,%d=%s,%d" % (r + (WATER_LIQ, int(cap * frac))))

    def units():
        return [B.hp("tank:%d,%d" % r).get("units") for r in roots]
    u_a = units()
    ctx["ticks"](300)
    u_b = units()
    if "TANKS_APART_HOLD" in mine:
        st = "UNMEASURED" if None in u_a or None in u_b else ("PASS" if u_a == u_b else "FAIL")
        row("TANKS_APART_HOLD", st, {"units": [u_a, u_b], "capacity": caps},
            cls="MOD" if st != "UNMEASURED" else "HARNESS")
    ctx["build"](*["RM_UniversalPipe:%d,%d" % c for c in gap])
    ctx["ticks"](2)
    net = B.hp("net:%d,%d" % roots[0])
    reach = sorted(tuple(t.get("tank") or ()) for t in net.get("tanks") or [])
    # HARNESS (belt live 2026-10-22): net:x,z lists the OTHER tanks (the origin is "origin"), so all three = 2 listed
    V.require(len(reach) >= 2, "the piped net reaches all three tanks", net)
    u0 = units()
    ctx["ticks"](2500)
    u1 = units()
    st, cls, d = tanks_verdict(u0, u1, caps)
    row("TANKS_JOINED_ONE_LEVEL", st, dict(d, units=[u0, u1], capacity=caps, netReach=reach,
                                           settles=[net.get("settles"), B.hp("net:%d,%d" % roots[0]).get("settles")]), cls=cls)


def _pond_rig(ctx, base_dz, fluid2, fill2):
    """One rig at plot z+base_dz (POND_RIG): two 3x3 pools 4 notches deep, two West reels on one pipe run, hoses to the lips."""
    B, P, static, xz = ctx["B"], ctx["P"], ctx["static"], ctx["xz"]
    lay = POND_RIG                               # module-level so the selftest can plant the old layout
    o = lambda x, z: P(x, z + base_dz)           # noqa: E731
    probs = pond_rig_problems(lay)
    V.require(not probs, "the rig geometry makes one levelling link (pond_rig_problems)", probs, cls="SITE")
    for (px, pz), (fl, f) in zip(lay["pools"], [(WATER_FLUID, 4), (fluid2, fill2)]):
        for i in range(3):
            for j in range(3):
                ctx["dig"](o(px + i, pz + j), 4)
                static(FLUIDP, "ProofFillWithFluid", "%d,%d,%d,%s" % (o(px + i, pz + j) + (f, fl)))
    r1, r2 = (o(*r) for r in lay["reels"])
    ctx["build"](*(["RM_UniversalPipe:%d,%d" % o(*c) for c in lay["pipes"]] + ["RM_LiquidTank:%d,%d" % o(*t) for t in lay["tanks"]]
                   + [V.reel_west(r1), V.reel_west(r2)]))
    ctx["ticks"](2)
    for r, e in zip((r1, r2), lay["ends"]):
        B.hp("lay:%d,%d,%d,%d" % (r + o(*e)), answer=True)
    for r, role in ((r1, "Intake"), (r2, "Outflow")):
        kh, th = static(LPROOF, "ProofHoseLine", xz(r))
        V.require(kh.get("laid") == "True", "hose %s laid" % xz(r), th)
        static(LPROOF, "ProofHoseRole", "%s;%s" % (xz(r), role))
    ctx["ticks"](2)                              # the hose-link index re-reads the roles on a later tick
    rig = dict(reels=(r1, r2), rects=["%d,%d,3,3" % o(px, pz) for px, pz in lay["pools"]], problems=probs)
    # the coupling read back before any levelling window: both open ends on one component, seen from each reel
    _dl, _m, _l, _r, coup = _pond_reads(ctx, rig)
    rig["coupling"] = coup
    if all(c is not None for c in coup):
        V.require(all(i >= 1 and u >= 1 for i, u in coup), "both open ends on one network component (intakes, outflows per reel)",
                  coup, cls="SITE")
    return rig


def _pond_reads(ctx, rig):
    """-> (dl per pool, Moves, LastLinks, readout, [(intakes, outflows) or None per reel]). Counters come from ProofLevelLink
    only (None on an old deploy without it: the verdicts then read UNMEASURED/HARNESS)."""
    B, static = ctx["B"], ctx["static"]
    dl = [num(static(LPROOF, "ProofPitWater", r)[0], "dl") for r in rig["rects"]]
    readout, moves, links, coup = "", None, None, []
    for r in rig["reels"]:
        kl, tl = static(NPROOF, "ProofLevelLink", "%d,%d" % r, answer=True)
        if kl.get("state"):
            # the enum word first (the verdicts read it), then why a rig may make no link
            readout += " | %s(in=%s out=%s on=%s)" % (kl["state"], kl.get("intakes"), kl.get("outflows"), kl.get("on"))
            moves, links = num(kl, "moves"), num(kl, "links")
            i, u = num(kl, "intakes"), num(kl, "outflows")
            coup.append(None if i is None or u is None else (i, u))
            continue
        coup.append(None)
        lt = B.call("jawa/list_things", defName="RM_HoseReel", rect="%d,%d,2,1" % r, limit=1, _answer=True) or {}
        rid = ((lt.get("things") or [{}])[0]).get("id")
        if rid:
            ins = B.call("jawa/inspect_string", thingIds=str(rid), _answer=True) or {}
            readout += " | " + " | ".join(ln for t in (ins.get("things") or []) for ln in (t.get("inspect") or []) if "Levelling" in ln)
    return dl, moves, links, readout, coup


def scene_ponds(ctx, mine):
    row = ctx["row"]
    if "PONDS_DIFFERENT_LIQUIDS_NO_MIX" in mine:
        rig = _pond_rig(ctx, 40, OIL_FLUID, 1)
        dl0, m0, _l0, _r0, _c0 = _pond_reads(ctx, rig)
        linked, readout, dl1, m1 = False, "", dl0, m0
        for _ in range(6):
            ctx["ticks"](250)
            dl1, m1, l1, r1, _c1 = _pond_reads(ctx, rig)
            linked = linked or bool(l1)
            readout = r1 or readout
        moves = None if m0 is None or m1 is None else m1 - m0
        st, cls = ponds_nomix_verdict(moves, dl0, dl1, linked, readout)
        row("PONDS_DIFFERENT_LIQUIDS_NO_MIX", st, {"dl": [dl0, dl1], "moves": moves, "linked": linked, "readout": readout,
                                                   "coupling": rig["coupling"], "rigProblems": rig["problems"]}, cls=cls)
        # retire the A5 rig's hoses so its link cannot move anything during A4 (it moves nothing by design; the cap is belt-and-braces)
        for r in rig["reels"]:
            ctx["static"](LPROOF, "ProofHoseRole", "%s;Capped" % ctx["xz"](r), answer=True)
    if "PONDS_HOSE_LEVEL" in mine:
        rig = _pond_rig(ctx, 20, WATER_FLUID, 1)
        dl0, m0, _l, _r, _c = _pond_reads(ctx, rig)
        linked, flowing, trail, waited = False, False, [], 0
        dl1, m1 = dl0, m0
        while waited < ctx["a"].level_ticks:
            if not ctx["ticks"](250):
                break
            waited += 250
            dl1, m1, l1, r1, _c1 = _pond_reads(ctx, rig)
            linked = linked or bool(l1)
            flowing = flowing or "Flowing" in (r1 or "") or "flowing" in (r1 or "")
            trail.append((waited, dl1, m1))
            if None not in dl1 and abs(dl1[0] - dl1[1]) / 9.0 <= DL_PER_CM_SQUARE:
                break
        moves = None if m0 is None or m1 is None else m1 - m0
        st, cls = ponds_level_verdict(moves, dl0, dl1, 9, linked, flowing)
        row("PONDS_HOSE_LEVEL", st, {"dl": [dl0, dl1], "moves": moves, "linked": linked, "flowingSeen": flowing,
                                     "ticks": waited, "trail": trail[-6:], "coupling": rig["coupling"],
                                     "rigProblems": rig["problems"]}, cls=cls)


def scene_ports(ctx, mine):
    B, P, row, static, xz = ctx["B"], ctx["P"], ctx["row"], ctx["static"], ctx["xz"]
    pump = P(52, 4)
    ra, rb, rc, rd = P(53, 4), P(52, -1), P(55, -1), P(58, 9)
    ctx["build"]("RM_LiquidPump:%d,%d" % pump, "RM_UniversalPipe:%d,%d" % P(51, 4), "RM_UniversalPipe:%d,%d" % P(50, 4),
                 V.reel_west(ra), V.reel_west(rb), V.reel_west(rc), V.reel_west(rd))
    ctx["ticks"](2)
    lays = {}
    for r, to in ((rb, P(52, 3)), (rc, P(52, 3)), (rd, P(53, 3))):
        lays[xz(r)] = B.hp("lay:%d,%d,%d,%d" % (r + to), answer=True)
    ctx["ticks"](2)
    _k, txt = static(NPROOF, "ProofPumpPorts", xz(pump), answer=True)
    sides, nums = ports_parse(txt) if txt.startswith("PUMPPORTS") else ({}, {})
    det = {"ports": txt[:300], "lays": {k: (v or {}).get("success") for k, v in lays.items()}}
    if "PORTS_PIPE_AND_REEL_ON_SIDES" in mine:
        st, cls = ports_sides_verdict(sides)
        row("PORTS_PIPE_AND_REEL_ON_SIDES", st, det, cls=cls)
    if "PORTS_ONE_HOSE_PER_SIDE" in mine:
        st, cls = ports_one_per_side_verdict(sides)
        row("PORTS_ONE_HOSE_PER_SIDE", st, det, cls=cls)
    if "PORTS_CORNER_REFUSED" in mine:
        st, cls = ports_corner_verdict(nums)
        row("PORTS_CORNER_REFUSED", st, det, cls=cls)


SCENES = [("cover", scene_cover), ("ladder", scene_ladder), ("travel", scene_travel), ("tanks", scene_tanks),
          ("ponds", scene_ponds), ("ports", scene_ports)]
SCENE_ROWS = {"cover": ["COVER_DECON_DROPS_RIDER"],
              "ladder": ["LADDER_RAISED_FROM_BELOW", "LADDER_NO_LOWER_FROM_BELOW", "LADDER_LOWERED_FROM_RIM", "LADDER_RAISED_FROM_RIM"],
              "travel": ["TRAVEL_FLYER_FREE_ON_FLOOR", "TRAVEL_PERSON_HELD_CONTROL", "TRAVEL_MARKED_FREE", "TRAVEL_THROWN_FLYER_UNHURT"],
              "tanks": ["TANKS_APART_HOLD", "TANKS_JOINED_ONE_LEVEL"],
              "ponds": ["PONDS_DIFFERENT_LIQUIDS_NO_MIX", "PONDS_HOSE_LEVEL"],
              "ports": ["PORTS_PIPE_AND_REEL_ON_SIDES", "PORTS_ONE_HOSE_PER_SIDE", "PORTS_CORNER_REFUSED"]}


# ====================================================================== offline stand-in
class FakeBridge(object):
    """A small world model answering in the live tools' shapes (and the proofs' line formats). It knows nothing about the
    game: a mock verdict proves the script's control flow and its MOD/SITE/HARNESS split only. Faults, one wrong thing each:
      no_proofs        RM_PromotionProofs missing (old deploy)          -> every row UNMEASURED/HARNESS
      no_worker        nobody takes the deconstruct job                 -> COVER_DECON_DROPS_RIDER UNMEASURED/SITE
      decon_no_fall    MOD: a deconstructed cover leaves its rider       -> COVER_DECON_DROPS_RIDER FAIL
      ladder_idle      MOD: nobody raises from below                     -> LADDER_RAISED_FROM_BELOW FAIL, (2) UNMEASURED/SITE
      lower_below      MOD: lowered from the pit                         -> LADDER_NO_LOWER_FROM_BELOW FAIL
      flyer_held       MOD: a flyer on the floor is held                 -> TRAVEL_FLYER_FREE_ON_FLOOR FAIL
      person_free      the instrument cannot tell (person free too)      -> TRAVEL_PERSON_HELD_CONTROL FAIL
      no_marked        no marked race on this tier                       -> TRAVEL_MARKED_FREE UNMEASURED/SITE
      thrown_hurt      MOD: a thrown duck takes the fall                 -> TRAVEL_THROWN_FLYER_UNHURT FAIL
      blind_health     a thrown person reads unhurt (blind read)          -> TRAVEL_THROWN_FLYER_UNHURT UNMEASURED/HARNESS
      store_only       MOD (the code read 2026-10-22): joined Store tanks never level -> TANKS_JOINED_ONE_LEVEL FAIL
      no_link          coupled, yet the mod makes no levelling link      -> PONDS_* UNMEASURED/SITE
      pipe_gap         a rig pipe never built: two components, one end each -> PONDS_* UNMEASURED/SITE (the coupling read)
      mixes            MOD: water and chemfuel exchange                  -> PONDS_DIFFERENT_LIQUIDS_NO_MIX FAIL
      no_level         MOD: two water pools never level                  -> PONDS_HOSE_LEVEL FAIL
      no_levellink     ProofLevelLink missing (old deploy)               -> no counters: PONDS_* UNMEASURED/HARNESS
      port_shared      MOD: both free ends couple on one side            -> PORTS_ONE_HOSE_PER_SIDE FAIL
      corner_couples   MOD: a hose end on a corner couples               -> PORTS_CORNER_REFUSED FAIL
      no_lay           the hose lays are refused                         -> PORTS_ONE_HOSE_PER_SIDE, PORTS_CORNER_REFUSED UNMEASURED/SITE"""
    FAULTS = ("no_proofs", "no_worker", "decon_no_fall", "ladder_idle", "lower_below", "flyer_held", "person_free", "no_marked",
              "thrown_hurt", "blind_health", "store_only", "no_link", "pipe_gap", "mixes", "no_level", "no_levellink", "port_shared",
              "corner_couples", "no_lay")

    def __init__(self, faults=()):
        self.f = set(faults)
        self.nid = 100
        self.dug = {}
        self.covers = set()
        self.desig = set()
        self.pawns = {}            # id -> dict(x, z, kind, drafted, hediffs, descents, held, last)
        self.ladders = {}          # cell -> dict(raised, want, ordered)
        self.tanks = {}            # root -> [units, cap]
        self.pipes = set()
        self.cells = {}            # dug cell -> (dl, fluid)
        self.reels = {}            # root -> dict(laid, role, to)
        self.moves = 0
        self.links = 0
        self.pumps = set()

    # ---- helpers
    def _pawn_at(self, c):
        for pid, p in self.pawns.items():
            if (p["x"], p["z"]) == c:
                return pid, p
        return None, None

    def _person(self, p):
        return p["kind"] == "Colonist"

    def _free_colonists(self):
        return [p for p in self.pawns.values() if self._person(p) and not p["drafted"]]

    def _tick(self, n):
        # deconstruct jobs
        for c in list(self.desig):
            if "no_worker" not in self.f and self._free_colonists():
                self.desig.discard(c)
                self.covers.discard(c)
                pid, p = self._pawn_at(c)
                if p is not None and "decon_no_fall" not in self.f:
                    p["descents"] += 1
                    p["held"] = True
                    p["last"] = "%s@%d,%d" % (pid, c[0], c[1])
        # ladder orders
        for c, L in self.ladders.items():
            if not L["ordered"]:
                continue
            free = self._free_colonists()
            below = [p for p in free if self.dug.get((p["x"], p["z"]))]
            above = [p for p in free if not self.dug.get((p["x"], p["z"]))]
            if L["want"] and (above or (below and "ladder_idle" not in self.f)):
                L.update(raised=True, ordered=False)
            elif not L["want"] and (above or (below and "lower_below" in self.f)):
                L.update(raised=False, ordered=False)
        # tanks: joined when the gap is piped (a pipe count model)
        roots = sorted(self.tanks)
        if len(roots) >= 3 and len(self.pipes) >= 11 and "store_only" not in self.f:
            tot = sum(u for u, _ in self.tanks.values())
            capt = sum(c for _, c in self.tanks.values())
            for r in roots:
                u, c = self.tanks[r]
                tgt = tot * c // capt
                self.tanks[r][0] = u + (tgt - u) * min(n, 2500) // 2500
            drift = tot - sum(u for u, _ in self.tanks.values())
            self.tanks[roots[0]][0] += drift
        # levelling between the open ends on one network component (pipe runs conduct; a tank does not)
        rigs = {}
        for r, h in self.reels.items():
            if h["laid"] and h["role"] in ("Intake", "Outflow"):
                rigs.setdefault(self._component(r), []).append(h)
        self.links = 0
        for rig, ends in rigs.items():
            if len(ends) < 2 or "no_link" in self.f:
                continue
            self.links += 1
            a_cells, b_cells = ends[0]["pool"], ends[1]["pool"]
            fa = {self.cells[c][1] for c in a_cells}
            fb = {self.cells[c][1] for c in b_cells}
            if fa != fb and "mixes" not in self.f:
                ends[0]["state"] = ends[1]["state"] = "stopped, different liquids never mix"
                continue
            if "no_level" in self.f:
                continue
            sa, sb = sum(self.cells[c][0] for c in a_cells), sum(self.cells[c][0] for c in b_cells)
            if sa == sb:
                ends[0]["state"] = ends[1]["state"] = "level"
                continue
            step = min(abs(sa - sb) // 2, 20000 * max(1, n // 250))
            hi, lo = (a_cells, b_cells) if sa > sb else (b_cells, a_cells)
            for c in hi:
                self.cells[c] = (self.cells[c][0] - step // 9, self.cells[c][1])
            for c in lo:
                self.cells[c] = (self.cells[c][0] + step // 9, self.cells[c][1])
            self.moves += 1
            ends[0]["state"] = ends[1]["state"] = "flowing (no pump; the higher water runs to the lower)"

    def _component(self, root):
        """The pipe run a reel's East/West/North/South edge touches (RM_NetComponents: pipes conduct, a tank is a member, so a
        reel touching only a tank is a component of its own). Pure geometry over self.pipes."""
        fp = _rect(root, 2, 2)
        seed = sorted(c for c in _edge_nbrs(fp) if c in self.pipes)
        if not seed:
            return ("alone", root)
        run, todo = set(), [seed[0]]
        while todo:
            q = todo.pop()
            if q in run or q not in self.pipes:
                continue
            run.add(q)
            todo += [(q[0] + 1, q[1]), (q[0] - 1, q[1]), (q[0], q[1] + 1), (q[0], q[1] - 1)]
        return ("run", min(run))

    def static(self, ty, m, arg):
        def cell(s):
            p = s.split(",")
            return (int(p[0]), int(p[1]))
        if m == "ProofPitTravel":
            c = cell(arg)
            pid, p = self._pawn_at(c)
            if p is None:
                return "PITTRAVEL cell=%d,%d pawn=none" % c
            fly = p["kind"] == FLYER_KIND
            marked = p["kind"] in MARKED_RACES
            free = (fly and "flyer_held" not in self.f) or marked or (self._person(p) and "person_free" in self.f)
            held = bool(self.dug.get(c)) and not free
            return "PITTRAVEL cell=%d,%d pawn=%s canFly=%s jumps=%s floats=False free=%s held=%s flying=False setting=True" % (
                c[0], c[1], p["kind"], fly, marked, free, held)
        if m == "ProofLadder":
            p = arg.split(",")
            c, op = (int(p[0]), int(p[1])), (p[2] if len(p) > 2 else "read")
            L = self.ladders.get(c)
            if L is None:
                return "LADDER cell=%d,%d present=False raised=None inspect=none" % c
            if op in ("raise", "lower"):
                L["raised"] = op == "raise"
            elif op in ("order_raise", "order_lower"):
                L.update(want=op == "order_raise", ordered=True)
            return "LADDER cell=%d,%d present=True raised=%s want=%s ordered=%s top=%d,%d inspect=x" % (
                c[0], c[1], L["raised"], L["want"], L["ordered"], c[0] - 1, c[1])
        if m == "ProofTrap":
            p = self.pawns.get(arg)
            if p is None:
                return "REFUSED: no pawn"
            return "TRAP descents=%d lastCell=none pos=%d,%d held=%s last=%s" % (p["descents"], p["x"], p["z"], p["held"], p["last"])
        if m == "ProofForcedFlyer":
            pid, x, z = arg.split(",")
            p = self.pawns.get(pid) or self.pawns.get("Thing_" + pid)
            p["x"], p["z"] = int(x), int(z)
            hurt = (self._person(p) and "blind_health" not in self.f) or (p["kind"] == FLYER_KIND and "thrown_hurt" in self.f)
            if hurt:
                p["hediffs"].append("Bruise")
            return "FLYER id=%s to=%s,%s depth=6 launched=True def=PawnFlyer_Stun" % (pid, x, z)
        if m == "ProofSurface":
            return "SURFACE s=%s" % ("Cover" if cell(arg) in self.covers else "SolidGround")
        if m == "ProofFillWithFluid":
            x, z, f, fl = arg.split(",")
            self.cells[(int(x), int(z))] = (int(f) * 5000, fl)
            return "FILLED"
        if m == "ProofPitWater":
            x, z, w, h = (int(v) for v in arg.split(","))
            dl = sum(self.cells.get((x + i, z + j), (0, None))[0] for i in range(w) for j in range(h))
            return "PITWATER dl=%d wet=9 cells=%d" % (dl, w * h)
        if m == "ProofHoseLine":
            r = self.reels.get(cell(arg))
            return "HOSELINE laid=%s" % (bool(r and r["laid"]))
        if m == "ProofLevelLink":
            if "no_levellink" in self.f:
                return "REFUSED: unknown " + m
            h = self.reels.get(cell(arg))
            if h is None:
                return "REFUSED: no hose reel at " + arg
            words = {"stopped, different liquids never mix": "DifferentLiquids", "level": "Level",
                     "flowing (no pump; the higher water runs to the lower)": "Flowing"}
            root = cell(arg)
            mine = self._component(root)
            ends = [g for r, g in self.reels.items() if g["laid"] and self._component(r) == mine]
            return "LEVELLINK reel=%d state=%s role=%s laid=%s intakes=%d outflows=%d on=True cycles=1 links=%d moves=%d movedDl=0" % (
                h["id"], words.get(h.get("state"), "None"), h["role"], h["laid"], sum(g["role"] == "Intake" for g in ends),
                sum(g["role"] == "Outflow" for g in ends), self.links, self.moves)
        if m == "ProofPumpPorts":
            pc = cell(arg)
            if pc not in self.pumps:
                return "REFUSED: no RM_LiquidPump at %d,%d" % pc
            off = {(0, 1): "N", (1, 0): "E", (0, -1): "S", (-1, 0): "W"}
            sides = {k: [] for k in "NESW"}
            corner = corner_c = coupled = 0
            for p in self.pipes:
                s = off.get((p[0] - pc[0], p[1] - pc[1]))
                if s:
                    sides[s].append("pipe")
            ends = {}
            for root, h in sorted(self.reels.items(), key=lambda kv: kv[1]["id"]):
                for c in (root, (root[0] + 1, root[1]), (root[0], root[1] + 1), (root[0] + 1, root[1] + 1)):
                    s = off.get((c[0] - pc[0], c[1] - pc[1]))
                    if s:
                        sides[s].append("reel:%d:c" % h["id"])
                        coupled += 1
                if h["laid"] and h["to"] and max(abs(h["to"][0] - pc[0]), abs(h["to"][1] - pc[1])) == 1:
                    s = off.get((h["to"][0] - pc[0], h["to"][1] - pc[1]))
                    if s:
                        ok = s not in ends or "port_shared" in self.f
                        ends.setdefault(s, h["id"])
                        sides[s].append("free:%d:%s" % (h["id"], "c" if ok else "r"))
                        coupled += ok
                    else:
                        corner += 1
                        corner_c += "corner_couples" in self.f
            return "PUMPPORTS " + " ".join("%s=%s" % (k, "+".join(v) or "none") for k, v in sides.items()) + \
                " coupled=%d corner=%d cornerCoupled=%d" % (coupled, corner, corner_c)
        if m == "ProofHoseRole":
            c, role = arg.split(";")
            self.reels[cell(c)]["role"] = role
            return "ROLE role=" + role
        return "REFUSED: unknown " + m

    def hp(self, cmd, wait_s=20.0):
        verb, _, arg = cmd.partition(":")
        if verb == "tank":
            r = tuple(int(v) for v in arg.split(","))
            t = self.tanks.get(r)
            return {"success": True, "units": t[0], "capacity": t[1]} if t else {"success": False, "error": "no tank there"}
        if verb == "filltank":
            r = tuple(int(v) for v in arg.split("=")[0].split(","))
            self.tanks[r][0] = int(arg.split("=")[1].split(",")[1])
            return {"success": True}
        if verb == "net":
            r = tuple(int(v) for v in arg.split(","))
            tanks = [{"tank": list(t)} for t in sorted(self.tanks)] if len(self.pipes) >= 11 or r not in self.tanks else [{"tank": list(r)}]
            return {"success": True, "tanks": tanks, "levelMoves": self.moves, "levelLinks": self.links, "settles": 0}
        if verb == "lay":
            rx, rz, x, z = (int(v) for v in arg.split(","))
            if "no_lay" in self.f and rz % 10 == 9:
                return {"success": False, "reason": "mock: lay refused"}
            h = self.reels[(rx, rz)]
            h.update(laid=True, to=(x, z))
            px, pz = x - 3, z - 1
            # the pool whose east lip the end touches: 3x3 at (to.x-3 .. to.x-1, to.z-1 .. to.z+1)
            h["pool"] = [(px + i, pz + j) for i in range(3) for j in range(3)]
            return {"success": True, "layOk": True}
        return {"success": True}

    def call(self, tool, **kw):
        if tool == "jawa/static_call":
            if kw.get("type") == PROMO and "no_proofs" in self.f:
                return {"success": False, "error": "Type not found"}
            return {"success": True, "result": self.static(kw.get("type"), kw.get("method"), kw.get("args") or "")}
        if tool == "rimworld/step_game_ticks":
            n = int(kw.get("ticks") or 0)
            self._tick(n)
            return {"success": True}
        if tool == "jawa/flowworks_excavation_drive":
            c = (kw["x"], kw["z"])
            self.dug[c] = self.dug.get(c, 0) + int(kw.get("deepenLevels") or 0)
            return {"success": True, "depth": self.dug[c]}
        if tool == "jawa/build_batch":
            for op in [o for o in str(kw.get("ops") or "").split(";") if o]:
                d, _, rest = op.partition(":")
                p = rest.split(",")
                c = (int(p[0]), int(p[1]))
                if d == COVER_DEF:
                    self.covers.add(c)
                elif d == "RM_Ladder":
                    self.ladders[c] = dict(raised=False, want=False, ordered=False)
                elif d in ("RM_LiquidTank", "RM_LiquidTankTall", "RM_UniversalCargoTank"):
                    self.tanks[c] = [0, {"RM_LiquidTank": 160000, "RM_LiquidTankTall": 320000}.get(d, 640000)]
                elif d == "RM_UniversalPipe":
                    if "pipe_gap" in self.f and c[0] == 52 and c[1] % 20 == 4:
                        continue            # the rig's third pipe never built: the run is cut in two
                    self.pipes.add(c)
                elif d == "RM_HoseReel":
                    root = (c[0] - 1, c[1]) if len(p) > 2 and int(p[2]) % 4 == 3 else c
                    self.nid += 1
                    self.reels[root] = dict(laid=False, role="Capped", to=None, state=None, id=self.nid)
                elif d == "RM_LiquidPump":
                    self.pumps.add(c)
            return {"success": True}
        if tool == "jawa/spawn_pawn":
            kind = kw.get("kindDef")
            if kind in MARKED_RACES and ("no_marked" in self.f or kind != MARKED_RACES[2]):
                return {"success": False, "error": "no PawnKindDef " + kind}
            self.nid += 1
            pid = "Thing_P%d" % self.nid
            self.pawns[pid] = dict(x=kw["x"], z=kw["z"], kind=kind, drafted=False, hediffs=[], descents=0, held=False, last="none")
            return {"success": True, "pawns": [{"id": pid}]}
        if tool == "jawa/set_draft":
            p = self.pawns.get(kw.get("pawnId"))
            if p is None:
                return {"success": False, "error": "no pawn"}
            p["drafted"] = bool(kw.get("drafted"))
            return {"success": True}
        if tool == "jawa/set_work_priority":
            return {"success": True, "readBack": 1, "manualPrioritiesOn": True}
        if tool == "jawa/designate_batch":
            x, z = (int(v) for v in str(kw.get("rect")).split(",")[:2])
            self.desig.add((x, z))
            return {"success": True, "added": 1}
        if tool == "jawa/list_things":
            x, z = (int(v) for v in str(kw.get("rect")).split(",")[:2])
            if kw.get("defName") == COVER_DEF:
                return {"success": True, "things": [{"id": "Cover"}] if (x, z) in self.covers else []}
            if kw.get("defName") == "RM_HoseReel":
                return {"success": True, "things": [{"id": "Reel%d_%d" % (x, z)}] if (x, z) in self.reels else []}
            return {"success": True, "things": []}
        if tool == "jawa/inspect_string":
            rid = str(kw.get("thingIds"))
            x, z = (int(v) for v in rid[4:].split("_"))
            st = self.reels[(x, z)].get("state")
            return {"success": True, "things": [{"inspect": ["Levelling: " + st + "."] if st else []}]}
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": [dict(id=i, kind=p["kind"], health={"hediffs": [{"def": h} for h in p["hediffs"]]})
                                               for i, p in self.pawns.items()]}
        return {"success": True}


if __name__ == "__main__":
    sys.exit(main())
