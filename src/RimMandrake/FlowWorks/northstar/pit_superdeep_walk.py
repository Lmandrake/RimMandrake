"""pit_superdeep_walk.py -- the ONE live walk that closes PIT_SUPERDEEP_COLLAPSE_1's remaining line (FOUNDRY reconcile
2026-10-23: "live v2 pit walk on the bridge (relative climb, prison ladder, sluice; flooded-pit swim-to-lip risk from
1e2dec39d) and child acceptance"), plus the rest of the item's rulings: the width rule, the "Jump into pit" gizmo, a cover
making involuntary falls possible, an enclosed pit becoming a prison only with a prisoner bed, capture and convert DOWN from
the lip. Every verdict is a deterministic state read (the pure v_* functions below, selftested); every station also gets a
zoomed, numbered, labelled capture and the run writes a numbered walkthrough map + index.html for the owner.

    python.exe src/RimMandrake/FlowWorks/northstar/pit_superdeep_walk.py --fresh-map
    python3    src/RimMandrake/FlowWorks/northstar/pit_superdeep_walk.py --mock          (offline: an in-script model game)

Options: --origin X,Z (default 120,180; site 62 x 20), --only S1,S9 (stations), --no-shots, --out-dir DIR,
--mock-fault NAME (mock only: make the model behave like an old/broken build; the selftest uses it).
Run live from the repo root with python.exe while holding the bridge, on a fresh quicktest map (--fresh-map makes one).
IDEMPOTENT: the site is reset first (ProofResetRect fills every dug cell back, prepare_site clears and reads back) and every
pawn left in the site rect by an earlier run is vanished; every setting this walk touches is read first and put back in
`finally` (RM_SwimSettings.swimEnduranceHours included). Output: D:\\ClaudeWork\\rimmandrake\\pit_walk\\<stamp>\\
(result.json, S*.png, walk_map.png, index.html). "Could not ask" is UNMEASURED, never FAIL (a refused call, a pawn that never
got onto its square, a site that did not read back).

Today's lessons honoured (2026-10-26): pitRescueLadderEnabled is held OFF for the whole walk (the rescue ladder auto-builds
into any pit holding a pawn and would free every stuck pawn); every pawn not acting in a station is vanished when the station
ends (fixture pawns fight each other); nothing waits on a pawn's digging (test pawns may have 0.1 mining): every pit is cut by
jawa/flowworks_excavation_drive.

Stations and rows (PROVE / EXPECT / LIES):
 S1 relative climb (owner 2026-10-12: a person climbs 2 levels; 3+ traps; gradual slopes never trap)
  PSW_climb_D3_person_trapped   ProofClimb pawn:<colonist> in a sheer D3 3x3 -> held+trapped True; a drafted order out
                                ends inside. LIES: a stale pocket grid (gen != built -> UNMEASURED); an order never taken.
  PSW_climb_D3_muffalo_free     the same pit, a wild muffalo (K 3): trapped False. LIES: a calf (age set to 8 y).
  PSW_climb_D2_rat_trapped      a 1x1 sheer D2, a rat (K 1): trapped True.
  PSW_climb_slope_never_traps   a D2 5x5 ring round a D4 3x3 core (a drained-pond stand-in): the colonist on the core is
                                trapped False and walks out. LIES: the ring dug to the wrong depth (dig_misses -> UNMEASURED).
 S2 width (owner Q4): PSW_width_trench   a 1-wide D4 trench: a hare is held, an ADULT muffalo (W 2) is not
                                (flowworks_pit_report held/requiredWidth). LIES: a muffalo read W 1 -> UNMEASURED.
 S3 prison ladder (a ladder is a prison door): PSW_ladder_prison_door   RM_Ladder on the west wall of a sheer D4 3x3 holding
                                a colonist: ProofLadder raise -> trapped True and the order out ends inside; ProofLadder lower
                                -> trapped False and the order out arrives. LIES: no ladder placed -> UNMEASURED SITE.
 S4 jump gizmo: PSW_jump_into_pit   JumpTargetFor(colonist on the lip) is a pit cell; RM_SuperdeepTrap.TryJumpInto (what the
                                gizmo calls) -> True, ProofTrap held True, descents +1, position in the pit. LIES: a jump
                                refused for geometry (JumpTargetFor Invalid -> UNMEASURED).
 S5 cover / forced entry:
  PSW_careless_walk_refused     a drafted colonist ordered onto an open ladderless D4 cell never stands on it and no
                                descent is counted (owner 2026-10-06 "can't fall in by careless pathing").
  PSW_cover_gives_way           a 2x2 RM_PitCover_WovenScrap deck (gives way under 40 kg) over a D4 2x2: a hostile shoved onto
                                it (ProofShove = forced displacement) -> within 300 ticks the deck is sprung, the hostile is
                                held and a descent is counted. LIES: the deck not laid (ProofCover covered False before ->
                                UNMEASURED SITE).
 S6 room -> prison: PSW_room_prison_only_with_bed   ProofRoom pit;far: split+pitRoom True, prison False with no bed; a Bed
                                owned for Prisoner in the pit (+ RM_PitRooms.RebuildAllMaps) -> prison True.
 S7 capture / convert down from the lip:
  PSW_capture_down_from_lip     an unarmed held pirate in the prison pit: ProofCaptureDown "VERDICT Allowed"; a drafted
                                colonist's RM_CaptureDown job (lip as targetB) -> prisoner True after 900 ticks and the warden
                                never ends in the pit.
  PSW_convert_down_from_lip     ProofLip <warden>;<pit centre>;PrisonerConvert -> serve True kind Interact lipInPit False
                                dist <= 6.
 S8 sluice / grate (SLUICE_GATE_REBUILD_LIFTS_UP_NOT_SIDEWAYS; flowDoorsSealedFromPitEnabled):
  PSW_sluice_shut_holds_all     a player-built RM_Sluice: RM_FlowDoorRules.ProofOpen SHUT for a hostile human, a muffalo, a
                                hare (a shut sluice opens for nobody walking at it).
  PSW_sluice_lifts_from_bank    ProofSetGate lift -> "lifted=True open=True"; lower -> "lifted=False".
  PSW_grate_seals_from_pit      a FACTIONLESS RM_SecurityGrateDoor on the lip of a sheer D4 pit: the held pirate below is
                                SHUT (vanilla would open a factionless door for anyone, so only the pit rule shuts it).
 S9 flooded sheer pit (P12 risk from 1e2dec39d: "a prisoner in a flooded sheer pit swims to the lip, cannot climb out, is
    warned before going under"):
  PSW_flood_swims_cannot_climb  a 4 m sheer 3x3 holding 2 m of water (surface 4 levels below the lip): the prisoner
                                swims (SwimsAt True, ProofSwim headUp True), ProofDrown exit False, ProofClimb trapped True.
  PSW_flood_warned_before_under swimEnduranceHours compressed to SWIM_ENDURANCE_FAST (the long-duration rule; restored and
                                read back): stepping WARN_STEP (30) ticks at a time, RM_Swim.ExhaustionOf crosses swimWarnAt while the
                                prisoner is alive, in the pit and headUp, and rimworld/list_messages gains "is tiring in deep
                                water" at that crossing. LIES: messages unreadable -> UNMEASURED; never reaching the warning
                                within the budget -> FAIL with the exhaustion trail.
  PSW_flood_near_brim_exit      the control: 4 m pit holding 3.5 m (surface 1 level below the lip), the prisoner on the
                                pit's west EDGE cell (BRIM_CTL) -> ProofDrown exit True, ProofClimb trapped False.
                                ProofDrown's exit is RM_Drowning.ExitInReach: the 4 cardinal neighbours only, so a pawn in
                                the 3x3 centre (round 4) has none and rightly reads False; the pocket-wide answer is ProofClimb.
 S10 child acceptance:
  PSW_child_pit_exposure        PIT_TEMPERATURE_SOFTENING_1: a colonist on an unroofed open D8 (4 m, S10_NOTCHES) pit floor
                                for 4 x 250 ticks has RM_PitExposure (jawa/pawn_get hediffs). A pit floor is a person
                                pocket at least pitRoomMinDepthMetres deep (3 m); a shallower staging is UNMEASURED/SITE.
  PSW_child_wall_art            EXCAVATION_WALL_ART_1: ProofWallFaces on S1's pit edge -> visible True, verts > 0 (the
                                picture is the owner's judgement; the capture is in the index).
Not covered (gaps, say so in the report): being BLASTED into a pit (an explosion's knockback; only a shove is driven), a full
recruit session from the lip, flight of any flyer (standing rule).

## anti-guessing notes (live round 4, 2026-10-26)
  - every spawned pawn is a declared clock-gate fixture and kept from every sweep (keep()): undeclared, its own arrival
    stopped safe_advance (hostile_arrival, declared=false) and site_recover's map-wide remove_intruders vanished S5/S7/S8's
    pirates, muffalo and hare before their rows read them. A row that lost its pawn names the refused call (couldNotAsk).
  - jawa/flowworks_pit_report lists only the pawns standing ON the queried cell: read each pawn at its own cell (pawn_get).
  - a capture path is shown relative to the repo only when it can be (show_path): python.exe raises on D: vs \\wsl.
  - RULED OUT: "RM_PitExposure never fires on an open floor" (MOD) -- RM_PitExposure.IsExposed needs RM_PitRooms.IsPitFloor,
    which needs the pit-room depth (3 m = 6 notches); round 4's S10 was dug 4 notches (2 m). S10 digs S10_NOTCHES and the
    mock exposes only at the room depth, so the old staging reads UNMEASURED/SITE, not a MOD fail.
  - RULED OUT: "a near-brim pit gives no exit" (MOD) -- ProofDrown's exit is cardinal-neighbour-only by design
    (RM_Drowning.ExitInReach); ProofClimb, the pocket-wide rule, said not trapped. The control stood in the 3x3 centre;
    it now stands on the edge (BRIM_CTL), and the mock's ProofDrown is cardinal-only so a centre control reads FAIL.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import climb_proof as CP  # noqa: E402  (pure helpers only: parse, state_verdict, walk_verdict, pit_pawn, dig_misses)

NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
PROMO = "RimMandrake.FlowWorks.RM_PromotionProofs"
TRAP = "RimMandrake.FlowWorks.RM_SuperdeepTrap"
DOORS = "RimMandrake.FlowWorks.RM_FlowDoorRules"
ROOMS = "RimMandrake.FlowWorks.RM_PitRooms"
FILLFX = "RimMandrake.FlowWorks.RM_PitFillEffects"
SWIMPOSE = "RimMandrake.FlowWorks.Swimming.RM_Patch_Pawn_SwimPose"
SWIM = "RimMandrake.FlowWorks.Swimming.RM_Swim"
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
# PIT_EXPOSURE_FIX_NO_HEDIFF_OPEN_FLOOR: RM_PitExposure needs a PIT FLOOR (RM_PitRooms.IsPitFloor: a person-band pocket dug
# at least pitRoomMinDepthMetres, ruled 3 m = 6 notches of 0.5 m; owner card PIT_ROOM_TUNE_TALL_FOLK_DIG_DEEPER). Round 4
# staged S10 at 4 notches (2 m), correctly no pit floor, and read the missing hediff as a MOD fail. 8 notches = 4 m.
S10_NOTCHES = 8
METRES_PER_NOTCH = 0.5
# PIT_FLOOD_FIX_NEAR_BRIM_NO_EXIT: ProofDrown's exit is RM_Drowning.ExitInReach, the pawn's own 4 CARDINAL neighbours
# (a step, not a swim). Round 4 stood the control in the CENTRE of the 3x3 near-brim pit, where every neighbour is
# 3.5 m water, so exit False was right. The control stands on the west EDGE, the lip one step away.
BRIM_PIT, BRIM_CTL = (10, 13), (10, 14)
S_SWIM = "RimMandrake.FlowWorks.Swimming.RM_SwimSettings"
SLUICE, GRATE, LADDER, WOVEN = "RM_Sluice", "RM_SecurityGrateDoor", "RM_Ladder", "RM_PitCover_WovenScrap"
SETTLE = 70                    # > RM_PocketGrid.RebuildMinTicks: every depth/ladder change is ticked this before a read
WAIT_OUT = 900
# PITWALK_FIX_SWIM_COMPRESSION_SKIPS_WARNING (HARNESS): RM_Swim checks every CheckTicks = 250. At 0.2 h (500 ticks) one check
# adds 0.5 exhaustion, so a swimmer went 0.5 -> 1.0 and the 70% warning landed AT exhaustion, head already under (round 5
# S9 FAIL). 1.0 h = 2500 ticks: 0.1 per check, the warning crossing reads with the head still up.
SWIM_ENDURANCE_FAST = 1.0      # hours (2500 ticks of swimming for a 1.0 endurance swimmer) for S9's warning row only
WARN_STEP = 50                 # ticks per read while waiting for the warning (the crossing is read within 2% of the pool)
WARN_BUDGET = 4000             # ticks of swimming allowed to reach the warning at the compressed endurance
WARN_TEXT = "is tiring in deep water"
SITE_W, SITE_H = 62, 20
FW_SETTINGS = {                # field -> value held for the walk (the old value is read first and restored in finally)
    "pitRescueLadderEnabled": False, "superdeepCapturesOwnFaction": True, "pitRelativeClimbEnabled": True,
    "ladderPrisonDoorEnabled": True, "rainFillsExcavationsEnabled": False, "flowDoorsSealedFromPitEnabled": True,
    "superdeepRoomsEnabled": True, "captureDownEnabled": True, "wardenFromLipEnabled": True, "pitExposureEnabled": True,
}

# station -> (title, rect relative to the origin (dx, dz, w, h), pits drawn on the walk map [(dx, dz, w, h, depth)])
STATIONS = {
    "S1": ("Relative climb: 3 levels trap a person, slopes never", (1, 1, 15, 7),
           [(2, 2, 3, 3, 3), (7, 3, 1, 1, 2), (10, 2, 5, 5, 2), (11, 3, 3, 3, 4)]),
    "S2": ("Width: a 1-wide trench holds a hare, not a muffalo", (16, 1, 5, 7), [(18, 2, 1, 5, 4)]),
    "S3": ("Prison ladder: raised strands, lowered frees", (21, 1, 6, 9), [(23, 2, 3, 3, 4)]),
    "S4": ("Jump into pit: the gizmo strands the jumper", (27, 1, 6, 6), [(29, 2, 3, 3, 4)]),
    "S5": ("Cover: careless walk refused, a shove through a cover falls", (33, 1, 8, 7),
           [(35, 2, 2, 2, 4), (39, 3, 1, 1, 4)]),
    "S6": ("Enclosed pit: a room, a prison only with a prisoner bed", (41, 1, 7, 7), [(44, 2, 3, 3, 6)]),
    "S7": ("Capture and convert DOWN from the lip", (41, 1, 7, 7), [(44, 2, 3, 3, 6)]),
    "S8": ("Sluice shut for all, lifted from the bank; grate seals the pit", (47, 1, 9, 9), [(51, 2, 3, 3, 4)]),
    "S9": ("Flooded sheer pit: swims, cannot climb out, warned; near-brim control exits", (1, 11, 14, 7),
           [(3, 13, 3, 3, 8), (10, 13, 3, 3, 8)]),
    "S10": ("Children: pit exposure; excavation wall art", (56, 1, 5, 5), [(57, 2, 3, 3, S10_NOTCHES)]),
}
ITEMS = {
    "PSW_child_pit_exposure": "PIT_TEMPERATURE_SOFTENING_1", "PSW_child_wall_art": "EXCAVATION_WALL_ART_1",
}
ITEM = "PIT_SUPERDEEP_COLLAPSE_1"


# ============================================================================ pure verdicts (selftest_pit_superdeep_walk.py)
def kv(txt):
    out = {}
    for tok in str(txt or "").replace("|", " ").split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            out[k] = v
    return out


def tbool(v):
    s = str(v).strip()
    return True if s == "True" else False if s == "False" else None


def fnum(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def worst(*sts):
    """Combine sub-verdicts: any UNMEASURED -> UNMEASURED (could not ask), else any FAIL -> FAIL, else PASS."""
    return "UNMEASURED" if "UNMEASURED" in sts else "FAIL" if "FAIL" in sts else "PASS"


def parse_xz(v):
    """'x,z' (or a {x, z} dict, or a pair) -> (int, int); anything else -> None."""
    try:
        if isinstance(v, dict):
            return int(v["x"]), int(v["z"])
        if isinstance(v, (list, tuple)):
            return int(v[0]), int(v[1])
        x, z = str(v).split(",")[:2]
        return int(x), int(z)
    except (KeyError, IndexError, TypeError, ValueError):
        return None


def in_rect(rect, xz):
    x0, z0, w, h = rect
    return xz is not None and xz[0] is not None and x0 <= xz[0] < x0 + w and z0 <= xz[1] < z0 + h


def v_width(hare_row, muff_row):
    """S2: the hare (W 1) is held in a 1-wide trench, the adult muffalo (W 2) is not."""
    if not hare_row or not muff_row:
        return "UNMEASURED", {"why": "pit_report did not list the pawn at its own cell", "hare": hare_row, "muffalo": muff_row}
    if muff_row.get("requiredWidth") != 2 or hare_row.get("requiredWidth") != 1:
        return "UNMEASURED", {"why": "fixture widths wrong (want hare W1, muffalo W2)",
                              "w": (hare_row.get("requiredWidth"), muff_row.get("requiredWidth"))}
    ok = hare_row.get("held") is True and muff_row.get("held") is False
    return ("PASS" if ok else "FAIL"), {"hareHeld": hare_row.get("held"), "muffaloHeld": muff_row.get("held")}


def v_ladder(lad_raised, climb_raised, walk_raised, lad_lowered, climb_lowered, walk_lowered):
    """S3: ProofLadder kv after raise / lower; ProofClimb kv; CP.walk_verdict results (status, det) of the order out."""
    if lad_raised.get("present") != "True" or lad_lowered.get("present") != "True":
        return "UNMEASURED", {"why": "no ladder on the wall", "raised": lad_raised, "lowered": lad_lowered}
    if lad_raised.get("raised") != "True" or lad_lowered.get("raised") != "False":
        return "UNMEASURED", {"why": "the ladder did not take the raise/lower", "raised": lad_raised, "lowered": lad_lowered}
    s1, d1 = CP.state_verdict(climb_raised, want_trapped=True)
    s2, d2 = CP.state_verdict(climb_lowered, want_trapped=False)
    st = worst(s1, s2, walk_raised[0], walk_lowered[0])
    return st, {"raised": {"climb": d1.get("mismatch"), "walk": walk_raised},
                "lowered": {"climb": d2.get("mismatch"), "walk": walk_lowered}}


def v_jump(target, ret, trap0, trap1, pit_rect):
    """S4: target = JumpTargetFor text "(x, 0, z)"; ret = TryJumpInto text; trap0/1 = ProofTrap kv before/after."""
    if not target or "-1000" in str(target) or not trap0 or not trap1:
        return "UNMEASURED", {"why": "no jump target or no trap read", "target": target, "trap0": trap0, "trap1": trap1}
    pos = parse_xz(trap1.get("pos"))
    d0, d1 = fnum(trap0.get("descents")), fnum(trap1.get("descents"))
    ok = tbool(ret) is True and trap1.get("held") == "True" and d0 is not None and d1 == d0 + 1 and in_rect(pit_rect, pos)
    return ("PASS" if ok else "FAIL"), {"ret": ret, "held": trap1.get("held"), "descents": (d0, d1), "pos": pos}


def v_careless(order_row, cell, desc0, desc1):
    """S5a: the drafted order onto an open ladderless D4 cell is refused: the pawn never stands on it, no descent."""
    if not order_row or order_row.get("orderAccepted") is not True or not (order_row.get("ticksElapsed") or 0) > 0:
        return "UNMEASURED", {"why": "order not accepted or the game never ticked", "order": order_row}
    pos = parse_xz(order_row.get("end") or order_row.get("position") or order_row.get("cell"))
    if pos is None or desc0 is None or desc1 is None:
        return "UNMEASURED", {"why": "no end position or descent count", "end": pos, "d": (desc0, desc1)}
    ok = pos != tuple(cell) and order_row.get("arrived") is not True and desc1 == desc0
    return ("PASS" if ok else "FAIL"), {"end": pos, "arrived": order_row.get("arrived"), "descents": (desc0, desc1)}


def v_cover_fall(cov0, cov1, trap0, trap1):
    """S5b: deck laid before (covered True, sprung False); after the shove: sprung, held, one more descent."""
    if cov0.get("covered") != "True" or cov0.get("sprung") != "False":
        return "UNMEASURED", {"why": "the deck was not laid intact before the shove", "cover0": cov0}
    if not trap0 or not trap1:
        return "UNMEASURED", {"why": "no ProofTrap read", "trap0": trap0, "trap1": trap1}
    d0, d1 = fnum(trap0.get("descents")), fnum(trap1.get("descents"))
    # PITWALK_FIX_SPRUNG_DECK_READS_ABSENT (HARNESS): Building_SpanDeck.Collapse DESTROYS the covers before anyone descends,
    # so after a real give-way ProofCover reads present=False sprung=False (round 5 S5 FAIL with held True, descents 0->1).
    # A deck that was laid intact and is gone after the shove is sprung; a deck still present must read sprung True.
    sprung = cov1.get("sprung") == "True" or cov1.get("present") == "False"
    ok = sprung and trap1.get("held") == "True" and d0 is not None and d1 is not None and d1 > d0
    return ("PASS" if ok else "FAIL"), {"sprung": cov1.get("sprung"), "present": cov1.get("present"),
                                        "held": trap1.get("held"), "descents": (d0, d1)}


def v_room(before, after, bed_id):
    """S6: ProofRoom kv with no bed (own room, not a prison) and with a prisoner bed (a prison)."""
    if "split" not in before or "prison" not in after:
        return "UNMEASURED", {"why": "ProofRoom unread", "before": before, "after": after}
    if not bed_id:
        return "UNMEASURED", {"why": "the bed was not built", "after": after}
    ok = (before.get("split") == "True" and before.get("pitRoom") == "True" and before.get("prison") == "False"
          and after.get("prison") == "True")
    return ("PASS" if ok else "FAIL"), {"before": before, "after": after}


def v_capture(v0, v1, warden_pos, pit_rect):
    """S7a: allowed before the job; a prisoner after it; the warden never ends in the pit."""
    if not str(v0).startswith("VERDICT") or "prisoner" not in v1:
        return "UNMEASURED", {"why": "ProofCaptureDown unread", "v0": v0, "v1": v1}
    if warden_pos is None or warden_pos[0] is None:
        return "UNMEASURED", {"why": "warden position unread"}
    ok = str(v0).startswith("VERDICT Allowed") and v1.get("prisoner") == "True" and not in_rect(pit_rect, warden_pos)
    return ("PASS" if ok else "FAIL"), {"v0": v0, "prisoner": v1.get("prisoner"), "warden": warden_pos}


def v_convert(k):
    """S7b: ProofLip PrisonerConvert on a pit prisoner is served from a lip cell."""
    if "serve" not in k:
        return "UNMEASURED", {"why": "ProofLip unread", "kv": k}
    ok = k.get("serve") == "True" and k.get("kind") == "Interact" and k.get("lipInPit") == "False" \
        and (fnum(k.get("dist")) or 99.0) <= 6.0
    return ("PASS" if ok else "FAIL"), {"kv": k}


def door_verdict(txt, pid):
    """OPEN / SHUT for pawn ThingID pid in a ProofOpen line ("DOOR ... | <pid> OPEN | <pid> SHUT"), else None."""
    for part in str(txt or "").split(" | ")[1:]:
        bits = part.split(" ")
        if pid and bits[0] == str(pid):
            return bits[1] if len(bits) > 1 else None
    return None


def v_sluice_shut(txt, pids):
    got = {p: door_verdict(txt, p) for p in pids if p}
    if len(got) != len(pids) or None in got.values():
        return "UNMEASURED", {"why": "a pawn is missing from the ProofOpen line", "txt": str(txt)[:200], "got": got}
    return ("PASS" if all(v == "SHUT" for v in got.values()) else "FAIL"), {"got": got}


def v_sluice_lift(up, down):
    if not str(up).startswith("DOOR") or not str(down).startswith("DOOR"):
        return "UNMEASURED", {"why": "ProofSetGate refused", "up": up, "down": down}
    ok = "lifted=True open=True" in up and "lifted=False" in down
    return ("PASS" if ok else "FAIL"), {"up": up, "down": down}


def v_grate(txt, pid, held):
    if held is not True:
        return "UNMEASURED", {"why": "the pirate below is not held (the row needs a held pawn)", "held": held}
    got = door_verdict(txt, pid)
    if got is None:
        return "UNMEASURED", {"why": "held pawn missing from ProofOpen", "txt": str(txt)[:200]}
    return ("PASS" if got == "SHUT" else "FAIL"), {"held": got}


def v_flood(swims, swim_kv, drown_kv, climb_kv):
    """S9a: the prisoner swims (head up), there is no exit in reach, the pocket traps it."""
    if swims is None or "exit" not in drown_kv or "headUp" not in swim_kv:
        return "UNMEASURED", {"why": "swim/drown read refused", "swims": swims, "swim": swim_kv, "drown": drown_kv}
    s, d = CP.state_verdict(climb_kv, want_trapped=True)
    ok = swims is True and swim_kv.get("headUp") == "True" and drown_kv.get("exit") == "False"
    return worst("PASS" if ok else "FAIL", s), {"swims": swims, "headUp": swim_kv.get("headUp"),
                                                "exit": drown_kv.get("exit"), "climb": d.get("mismatch")}


def v_warned(trail, warn_at, msgs_before, msgs_after, pit_rect):
    """S9b: trail = [(tick, exhaustion, (x, z), dead, headUp)] up to and including the warning crossing; msgs = lists of
    message strings (None = unreadable). PASS: exhaustion crossed warn_at while alive, in the pit, head up, and a new
    'is tiring in deep water' message appeared."""
    if msgs_before is None or msgs_after is None or warn_at is None:
        return "UNMEASURED", {"why": "messages or swimWarnAt unreadable"}
    if not trail:
        return "UNMEASURED", {"why": "no exhaustion read"}
    hit = [t for t in trail if t[1] is not None and t[1] >= warn_at]
    if not hit:
        return "FAIL", {"why": "never reached the warning in the budget", "trail": trail[-4:], "warnAt": warn_at}
    t = hit[0]
    new = sum(1 for m in msgs_after if WARN_TEXT in m) - sum(1 for m in msgs_before if WARN_TEXT in m)
    ok = (not t[3]) and in_rect(pit_rect, t[2]) and t[4] is True and new >= 1
    return ("PASS" if ok else "FAIL"), {"at": t, "warnAt": warn_at, "newWarnings": new, "trail": trail[-4:]}


def v_near_brim(drown_kv, climb_kv):
    if "exit" not in drown_kv:
        return "UNMEASURED", {"why": "ProofDrown unread", "drown": drown_kv}
    s, d = CP.state_verdict(climb_kv, want_trapped=False)
    return worst("PASS" if drown_kv.get("exit") == "True" else "FAIL", s), {"exit": drown_kv.get("exit"),
                                                                          "climb": d.get("mismatch")}


def v_exposure(pawn_row, room_min_m=None, notches=None):
    """S10: RM_PitExposure on a pit floor. A floor shallower than pitRoomMinDepthMetres is no pit floor by rule, so the
    row could not ask: UNMEASURED (the staging, not the mod)."""
    if room_min_m is not None and notches is not None and notches * METRES_PER_NOTCH < room_min_m:
        return "UNMEASURED", {"why": "S10 floor %.1f m is shallower than pitRoomMinDepthMetres %.1f m: no pit floor by rule"
                                     % (notches * METRES_PER_NOTCH, room_min_m)}
    if not pawn_row:
        return "UNMEASURED", {"why": "pawn_get found no pawn"}
    defs = [h.get("def") for h in pawn_row.get("hediffs") or []]
    return ("PASS" if "RM_PitExposure" in defs else "FAIL"), {"hediffs": defs[:8], "floorMetres":
                                                             None if notches is None else notches * METRES_PER_NOTCH}


def v_wallart(txt):
    k = kv(txt)
    if not str(txt).startswith("WALLS"):
        return "UNMEASURED", {"why": "ProofWallFaces refused", "txt": str(txt)[:160]}
    ok = k.get("visible") == "True" and (fnum(k.get("verts")) or 0) > 0
    return ("PASS" if ok else "FAIL"), {"kv": k}


def flat_strings(o):
    """Every string inside a bridge reply (list_messages' exact shape is not pinned; the text is what is judged)."""
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from flat_strings(v)
    elif isinstance(o, (list, tuple)):
        for v in o:
            yield from flat_strings(v)


# ============================================================================ the walk map (pure drawing; mock-tested)
def draw_walk_map(path, origin, stations, results):
    """A numbered, dense schematic of the whole site: every pit shaded by depth, every station's rect outlined, its number
    in a disc and a SPANNER (a bracket bar) drawn over the pit it is about, labelled with the station title and its rows'
    verdicts. Deterministic; drawn from the geometry, not from a screenshot."""
    from PIL import Image, ImageDraw
    import fw_walk_common as C
    cell = 32
    pad_top, pad = 120, 30
    W, H = SITE_W * cell + 2 * pad, SITE_H * cell + pad_top + 60 + len(stations) * 76
    im = Image.new("RGB", (W, H), (236, 230, 214))
    d = ImageDraw.Draw(im)
    ft, fl, fs = C._font(34, True), C._font(26, True), C._font(22)
    d.text((pad, 20), "%s walk map: site %d x %d at %d,%d (north up)" % (ITEM, SITE_W, SITE_H, origin[0], origin[1]),
           font=ft, fill=(20, 20, 20))

    def xy(dx, dz):        # site cell -> pixel (north up: larger z drawn higher)
        return pad + dx * cell, pad_top + (SITE_H - 1 - dz) * cell

    for dx in range(SITE_W + 1):
        d.line([xy(dx, SITE_H - 1)[0], pad_top, xy(dx, SITE_H - 1)[0], pad_top + SITE_H * cell], fill=(214, 206, 188))
    for dz in range(SITE_H + 1):
        d.line([pad, pad_top + dz * cell, pad + SITE_W * cell, pad_top + dz * cell], fill=(214, 206, 188))
    for sid, (title, rect, pits) in stations.items():
        for (px, pz, pw, ph, depth) in pits:
            shade = max(40, 200 - depth * 18)
            x0, y0 = xy(px, pz + ph - 1)
            d.rectangle([x0, y0, x0 + pw * cell, y0 + ph * cell], fill=(shade, shade - 20, shade - 40), outline=(60, 40, 20))
    legend_y = pad_top + SITE_H * cell + 40
    discs = {}
    for i, (sid, (title, rect, pits)) in enumerate(stations.items()):
        rx, rz, rw, rh = rect
        x0, y0 = xy(rx, rz + rh - 1)
        d.rectangle([x0, y0, x0 + rw * cell, y0 + rh * cell], outline=(0, 70, 140), width=3)
        px, pz, pw, ph, _ = pits[0]
        sx0, sy = xy(px, pz + ph - 1)
        sx1 = sx0 + pw * cell
        sy -= 10
        d.line([sx0, sy, sx1, sy], fill=(160, 0, 0), width=4)                 # the spanner over the pit
        d.line([sx0, sy, sx0, sy + 8], fill=(160, 0, 0), width=4)
        d.line([sx1, sy, sx1, sy + 8], fill=(160, 0, 0), width=4)
        cx, cy = (sx0 + sx1) // 2, sy - 22
        cx += 42 * discs.get(pits[0][:2], 0)                                 # two stations on one pit: side by side
        discs[pits[0][:2]] = discs.get(pits[0][:2], 0) + 1
        d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=(160, 0, 0))
        d.text((cx - 13 if len(sid) < 3 else cx - 17, cy - 13), sid[1:], font=fl, fill=(255, 255, 255))
        verdicts = " ".join("%s:%s" % (r["id"].replace("PSW_", ""), r["status"]) for r in results if r.get("station") == sid)
        d.text((pad, legend_y + i * 76), "%s  %s" % (sid, title), font=fl, fill=(20, 20, 20))
        d.text((pad + 60, legend_y + i * 76 + 34), verdicts or "(not run)", font=fs, fill=(20, 20, 20))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path)
    return path


# ============================================================================ the mock game (--mock)
class FakePit(object):
    """A small model of the pit rules, good enough to drive every station offline: depths and fills per cell, pockets by
    the relative-climb rule (exit step = floor height above the highest neighbour outside the pocket, against K), the width
    rule, a ladder door, a woven deck that gives way, rooms/beds, doors, swim exhaustion with messages. `faults` makes it
    behave like an old or broken build (the selftest asserts that the matching row goes red)."""
    K = {"Colonist": 2, "Villager": 2, "Pirate": 2, "Rat": 1, "Hare": 1, "Muffalo": 3}
    W = {"Muffalo": 2}
    MASS = {"Rat": 0.5, "Hare": 3, "Muffalo": 150}

    def __init__(self, faults=()):
        self.faults = set(faults or ())
        self.tick = 0
        self.depth, self.fill = {}, {}
        self.pawns = {}
        self.n = 0
        self.things = {}
        self.ladders = {}           # cell -> raised
        self.covers = {}            # cell -> sprung
        self.descents = 0
        self.settings = {}
        self.messages = []
        self.prison_bed = False
        self.capture = {}
        self.kept = set()           # fixtures the walk declared (keep()); `keep_ignored` = the round-4 harness
        self.announced = set()      # hostile arrivals the governor has already seen
        self.swept = []

    # ---- model
    def _d(self, c):
        return self.depth.get(tuple(c), 0)

    def _pocket(self, c):
        d0 = self._d(c)
        seen, todo = {tuple(c)}, [tuple(c)]
        while todo:
            x, z = todo.pop()
            for n in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
                if n not in seen and self._d(n) == d0:
                    seen.add(n)
                    todo.append(n)
        return seen

    def _exit_step(self, c):
        pk = self._pocket(c)
        d0 = self._d(c) - (self.fill.get(tuple(c), 0) if self.fill.get(tuple(c), 0) >= 4 else 0)   # swimmers float up
        best = None
        for (x, z) in pk:
            for n in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
                if n not in pk:
                    step = d0 - self._d(n)
                    best = step if best is None else min(best, step)
        return best if best is not None else 0, pk

    def _climb_d(self, c):
        f = self.fill.get(tuple(c), 0)
        return self._d(c) - (f if f >= 4 else 0)                  # water lifts the climb to its surface

    def _step_exit(self, c):
        """RM_Drowning.ExitInReach: a CARDINAL neighbour within the climb step whose water is under a 1.75 m head."""
        x, z = c
        return any(abs(self._climb_d(c) - self._climb_d(n)) <= 2 and self.fill.get(n, 0) / 2.0 < 1.75 * 0.9
                   for n in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)))

    def _trapped(self, pid):
        p = self.pawns[pid]
        if self._d(p["cell"]) == 0 or self.covers.get(tuple(p["cell"])) is False:
            return False
        step, pk = self._exit_step(p["cell"])
        if any(self.ladders.get(c) is False for c in pk) and "ladder_ignored" not in self.faults:
            return False
        if "slope_traps" in self.faults and any(0 < self._d(n) < self._d(p["cell"]) for (x, z) in pk
                                                for n in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1))):
            return True                                           # an old build: a terraced pit traps like a sheer one
        if self.W.get(p["kind"], 1) == 2:
            xs, zs = {c[0] for c in pk}, {c[1] for c in pk}
            if min(len(xs), len(zs)) < 2:
                return False
        return step > self.K.get(p["kind"], 2)

    def _climb(self, pid):
        t = self._trapped(pid)
        p = self.pawns[pid]
        return ("CLIMB k=%d held=%s trapped=%s cell=%d,%d | POCKET k=%d comp=1 pocket=%s size=9 depth=%d gen=5 built=5 "
                "rebuilds=1" % (self.K.get(p["kind"], 2), t, t, p["cell"][0], p["cell"][1], self.K.get(p["kind"], 2), t,
                                self._d(p["cell"])))

    def _at(self, c):
        for pid, p in self.pawns.items():
            if tuple(p["cell"]) == tuple(c):
                return pid
        return None

    def _swim_tick(self, n):
        for pid, p in self.pawns.items():
            if self.fill.get(tuple(p["cell"]), 0) >= 4:
                before = p.get("ex", 0.0)
                hrs = float(self.settings.get(S_SWIM + ".swimEnduranceHours", 3.0))
                p["ex"] = min(1.0, before + n / (hrs * 2500.0))
                warn = float(self.settings.get(S_SWIM + ".swimWarnAt", 0.6))
                if before < warn <= p["ex"] and p.get("prisoner") and "no_warning" not in self.faults:
                    self.messages.append("Mock prisoner %s: about 12 minutes of swimming left before going under." % WARN_TEXT)

    def _governor(self):
        """validation_core.Bridge.ticks: a hostile arrival stops safe_advance; a declared fixture resumes, anything else
        goes to site_recover -> remove_intruders() on the WHOLE map (every hostile and factionless pawn not kept)."""
        kept = set() if "keep_ignored" in self.faults else self.kept
        live = {q: p for q, p in self.pawns.items() if not p.get("prisoner")}     # a prisoner is neither (round 4: S9)
        new = [pid for pid, p in live.items() if p["faction"] == "hostile" and pid not in self.announced]
        self.announced.update(new)
        if any(pid not in kept for pid in new):
            for pid in [q for q, p in live.items() if p["faction"] in ("hostile", "none") and q not in kept]:
                self.pawns.pop(pid)
                self.swept.append(pid)

    def ticks(self, n):
        self.tick += n
        self._governor()
        self._swim_tick(n)
        for c, sprung in list(self.covers.items()):
            pid = self._at(c)
            if pid and sprung is False and self.MASS.get(self.pawns[pid]["kind"], 60) > 40:
                self.covers[c] = True
                self.descents += 1
                self.pawns[pid]["descent"] = True
        for pid, (tick_due, target) in list(self.capture.items()):
            if self.tick >= tick_due and target in self.pawns:
                self.pawns[target]["prisoner"] = True
                del self.capture[pid]

    # ---- bridge
    def call(self, tool, **kw):
        if tool == "jawa/flowworks_excavation_drive":
            c = (int(kw["x"]), int(kw["z"]))
            self.depth[c] = self.depth.get(c, 0) + int(kw.get("deepenLevels") or 0)
            if int(kw.get("setFill", -1)) >= 0:
                self.fill[c] = int(kw["setFill"])
            return {"success": True, "depth": self.depth[c]}
        if tool == "jawa/spawn_pawn":
            self.n += 1
            pid = "Thing_Mock%d" % self.n
            kind = kw.get("kindDef")
            self.pawns[pid] = {"kind": kind, "cell": (int(kw["x"]), int(kw["z"])), "faction": kw.get("faction"),
                               "born": self.tick}
            return {"success": True, "pawns": [{"id": pid}]}
        if tool == "jawa/order_pawn":
            pid = kw["pawnId"]
            p = self.pawns.get(pid)
            if not p:
                return {"success": False}
            want = (int(kw["x"]), int(kw["z"]))
            self.ticks(int(kw.get("waitTicks") or 1))
            if want == tuple(p["cell"]):
                arrived = True
            elif self._d(want) >= 4 and self._d(p["cell"]) == 0 and self.ladders.get(want) is None:
                arrived = False                                   # RM_PitPathing refuses a ladderless open D4 cell
            elif self._trapped(pid):
                arrived = False
            else:
                p["cell"] = want
                arrived = True
            return {"success": True, "ticksElapsed": int(kw.get("waitTicks") or 1),
                    "pawns": [{"id": pid, "orderAccepted": True, "arrived": arrived,
                               "end": {"x": p["cell"][0], "z": p["cell"][1]}}]}
        if tool == "jawa/static_call":
            return {"success": True, "result": self._static(kw["type"], kw["method"], kw.get("args", ""))}
        if tool == "jawa/mod_settings_field":
            key = "%s.%s" % (kw["typeName"], kw["field"])
            if kw.get("action") == "set":
                self.settings[key] = kw.get("value")
            return {"success": True, "value": self.settings.get(key, {"swimWarnAt": "0.6", "swimEnduranceHours": "3",
                                                                   "pitRoomMinDepthMetres": "3"}.get(
                kw["field"], "True"))}
        if tool == "jawa/flowworks_pit_report":
            c = (int(kw["x"]), int(kw["z"]))
            rows = []
            for pid, p in self.pawns.items():
                if tuple(p["cell"]) == c:                         # the real tool: c.GetThingList(map), this cell only
                    t = self._trapped(pid)
                    rows.append({"id": pid, "held": t, "requiredWidth": self.W.get(p["kind"], 1), "spawned": True,
                                 "dead": False, "lipReachable": 0 if t else 3, "canReachMapEdge": not t})
            return {"success": True, "pawns": rows, "descentCount": self.descents}
        if tool in ("jawa/spawn_batch", "jawa/build_batch"):
            placed = 0
            for op in kw.get("ops", "").split(";"):
                name, rest = op.split(":")
                x, z = (int(v) for v in rest.split(",")[:2])
                self.things[(x, z)] = name
                placed += 1
                if name == LADDER:
                    self.ladders[(x, z)] = False
                if name.startswith("RM_PitCover_"):
                    self.covers[(x, z)] = False
            return {"success": True, "thingsPlaced": placed}
        if tool == "jawa/list_things":
            want = kw.get("defName")
            return {"success": True, "things": [{"id": "Thing_Bed1", "def": d} for d in self.things.values() if d == want]}
        if tool == "jawa/set_bed_owner_type":
            self.prison_bed = kw.get("ownerType") == "Prisoner"
            return {"success": True}
        if tool == "jawa/ordered_job":
            self.capture[kw["pawnId"]] = (self.tick + 300, kw.get("targetAId"))
            return {"success": True}
        if tool == "jawa/pawn_set_guest_status":
            self.pawns[kw["pawn"]]["prisoner"] = True
            return {"success": True}
        if tool == "jawa/pawn_force_incapacitate":
            self.pawns.pop(kw.get("pawn"), None)
            return {"success": True}
        if tool == "jawa/pawn_get":
            p = self.pawns.get(kw.get("pawn"))
            if not p:
                return {"success": True, "pawns": []}
            hd = []
            room_min = float(self.settings.get(S_FW + ".pitRoomMinDepthMetres", 3.0))
            if (self._d(p["cell"]) * METRES_PER_NOTCH >= room_min and self.tick - p["born"] >= 250
                    and "no_exposure" not in self.faults):
                hd.append({"def": "RM_PitExposure"})
            return {"success": True, "pawns": [{"id": kw["pawn"], "hediffs": hd, "dead": False,
                                                "position": {"x": p["cell"][0], "z": p["cell"][1]}}]}
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": [{"id": "Thing_MapCol1", "isPlayer": True, "x": 10, "z": 10}]}
        if tool == "rimworld/list_messages":
            return {"success": True, "messages": [{"text": m} for m in self.messages]}
        if tool == "rimworld/step_game_ticks":
            self.ticks(int(kw.get("ticks") or 1))
            return {"success": True}
        return {"success": True}

    def _static(self, typ, method, arg):
        a = str(arg or "")
        if method == "ProofResetRect":
            return "RESET cells=0 levels=0 rolled=0 left=0"
        if method == "ProofClimb":
            pid = a.split(":", 1)[1]
            return self._climb(pid) if pid in self.pawns else "REFUSED: no pawn"
        if method == "ProofLadder":
            x, z, op = a.split(",")
            c = (int(x), int(z))
            if c not in self.ladders:
                return "LADDER cell=%s present=False" % a
            if op in ("raise", "lower"):
                self.ladders[c] = op == "raise"
            return "LADDER cell=%d,%d present=True raised=%s inspect=Ladder" % (c[0], c[1], self.ladders[c])
        if method == "JumpTargetFor":
            p = self.pawns[a]
            for n in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                c = (p["cell"][0] + n[0], p["cell"][1] + n[1])
                if self._d(c) >= 4:
                    return "(%d, 0, %d)" % c
            return "(-1000, -1000, -1000)"
        if method == "TryJumpInto":
            pid, xz = a.split("|")
            c = tuple(int(v) for v in xz.split(","))
            if "jump_refused" in self.faults:
                return "False"
            self.pawns[pid]["cell"] = c
            self.descents += 1
            return "True"
        if method == "ProofTrap":
            p = self.pawns.get(a)
            if not p:
                return "REFUSED"
            held = self._trapped(a) or self._d(p["cell"]) >= 4
            return "TRAP descents=%d lastCell=none pos=%d,%d held=%s last=-" % (self.descents, p["cell"][0], p["cell"][1], held)
        if method == "ProofShove":
            pid, xz = a.split(";")
            if pid not in self.pawns:
                return "REFUSED: no spawned pawn %s" % pid               # RM_NorthstarProofs.ProofShove
            self.pawns[pid]["cell"] = tuple(int(v) for v in xz.split(","))
            return "SHOVE at=" + xz
        if method == "ProofCover":
            c = tuple(int(v) for v in a.split(","))
            if c not in self.covers:
                return "COVER present=False covered=False"
            return "COVER present=True covered=%s sprung=%s depth=%d" % (not self.covers[c], self.covers[c], self._d(c))
        if method == "ProofRoom":
            prison = self.prison_bed and "bed_ignored" not in self.faults
            return "ROOM split=True pitRoom=True proper=True edge=False prison=%s" % prison
        if method == "RebuildAllMaps":
            return ""
        if method == "ProofCaptureDown":
            p = self.pawns.get(a)
            if not p:
                return "REFUSED: no spawned pawn %s" % a                 # RM_NorthstarProofs.ProofCaptureDown
            return "VERDICT Allowed held=True prisoner=%s cell=%d,%d" % (bool(p.get("prisoner")), p["cell"][0], p["cell"][1])
        if method == "ProofLip":
            return "LIP serve=True kind=Interact lipInPit=False dist=1.4"
        if method == "ProofOpen":
            c = tuple(int(v) for v in a.split("|")[1].split(","))
            name = self.things.get(c, "none")
            parts = ["DOOR %s" % name]
            for pid, p in self.pawns.items():
                if max(abs(p["cell"][0] - c[0]), abs(p["cell"][1] - c[1])) <= 2:
                    opens = (name == SLUICE and "sluice_opens" in self.faults)
                    parts.append("%s %s" % (pid, "OPEN" if opens else "SHUT"))
            return " | ".join(parts)
        if method == "ProofSetGate":
            up = a.split("|")[2] == "true"
            return "DOOR %s lifted=%s open=%s" % (SLUICE, up, up)
        if method == "SwimsAt":
            pid, xz = a.split("|")
            return str(self.fill.get(tuple(int(v) for v in xz.split(",")), 0) >= 4)
        if method == "ProofSwim":
            c = tuple(int(v) for v in a.split(","))
            pid = self._at(c)
            if not pid:
                return "REFUSED: no pawn"
            return "SWIM %s class=Human exhaustion=%.3f headUp=True" % (pid, self.pawns[pid].get("ex", 0.0))
        if method == "ProofDrown":
            c = tuple(int(v) for v in a.split(","))
            pid = self._at(c)
            if not pid:
                return "REFUSED: no pawn"
            return "DROWN %s H=1.75 lying=False water=%.2f under=False headUp=True exit=%s perCheck=0" % (
                pid, self.fill.get(c, 0) / 2.0, self._step_exit(c))
        if method == "ExhaustionOf":
            if a not in self.pawns:
                return "REFUSED: no pawn"
            return "%.3f" % self.pawns[a].get("ex", 0.0)
        if method == "ProofWallFaces":
            return "WALLS visible=True verts=%d" % (0 if "no_walls" in self.faults else 96)
        return "REFUSED: mock has no %s" % method


# ============================================================================ the walk
def default_out(stamp):
    base = r"D:\ClaudeWork\rimmandrake\pit_walk" if os.name == "nt" else "/mnt/d/ClaudeWork/rimmandrake/pit_walk"
    return os.path.join(base, stamp)


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--origin", default="120,180")
    ap.add_argument("--only", default="", help="comma list of stations, e.g. S1,S9")
    ap.add_argument("--no-shots", action="store_true")
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--mock-fault", default="", help="mock only: comma list of model faults")
    ap.add_argument("--out-dir", default=None)
    return ap.parse_args(argv)


def main(argv=None):
    a = parse_args(argv)
    stamp = time.strftime("%Y%m%dT%H%M%S") + ("_mock" if a.mock else "")
    out_dir = a.out_dir or default_out(stamp)
    import fw_walk_common as C
    w = C.make_walk(a, out_dir)
    if a.mock:
        w.B = FakePit([f for f in a.mock_fault.split(",") if f])
    B = w.B
    only = {s.strip() for s in a.only.split(",") if s.strip()}
    want = lambda s: not only or s in only        # noqa: E731
    out = os.path.join(out_dir, "result.json")
    rows, groups = [], []
    res = {"script": "pit_superdeep_walk.py", "item": ITEM, "mode": "mock" if a.mock else "live",
           "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a), "outDir": out_dir}
    could_not = []
    station = ["-"]

    def save():
        os.makedirs(out_dir, exist_ok=True)
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, det, cls="MOD"):
        if st == "FAIL" and could_not:          # a refused call in this row: could not ask
            st, cls = "UNMEASURED", "HARNESS"
        if st == "UNMEASURED" and could_not:    # say WHICH call could not ask (round 4 lost the reason on 5 rows)
            det = dict(det, couldNotAsk=list(could_not))
            cls = "HARNESS"
        if st == "UNMEASURED" and cls == "MOD":
            cls = "SITE" if "why" in det else "HARNESS"
        del could_not[:]
        rows.append({"id": rid, "station": station[0], "item": ITEMS.get(rid, ITEM), "status": st, "class": cls,
                     "detail": det})
        print("%-32s %-10s %-7s %s" % (rid, st, cls, json.dumps(det, default=str)[:260]), flush=True)
        save()

    def sc(typ, method, arg=""):
        r = B.call("jawa/static_call", type=typ, method=method, args=arg) or {}
        txt = str(r.get("result") if r.get("result") is not None else "")
        if not r.get("success") or txt.startswith("REFUSED"):
            could_not.append("%s(%s): %s" % (method, str(arg)[:30], (txt or str(r.get("message") or r.get("error")))[:80]))
            return None
        return txt

    def sget(typ, f):
        return (B.call("jawa/mod_settings_field", typeName=typ, action="get", field=f) or {}).get("value")

    def sset(typ, f, v):
        return B.call("jawa/mod_settings_field", typeName=typ, action="set", field=f, value=str(v))

    digs = []

    def dig(c, n, fill=-1):
        r = B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=n, setFill=fill) or {}
        digs.append((tuple(c), n, r))
        return r

    def pit(o, w_, h_, n, fill=-1):
        for i in range(w_):
            for j in range(h_):
                dig((o[0] + i, o[1] + j), n, fill)

    spawned = []

    def keep(pid, on=True):
        """PITWALK_FIX_FIVE_ROWS_NEVER_MEASURE: a pawn the walk spawned is a FIXTURE. Undeclared, its own arrival stopped
        safe_advance (hostile_arrival), site_recover ran remove_intruders() map-wide and vanished the station's pirates,
        muffalo and hare before their row read them (round 4: S5, S7, S8 x2 UNMEASURED). Declared to the clock gate (the
        arrival resumes) and kept from every sweep (KEEP_PAWNS of validation_core and of the modcheck helpers)."""
        if a.mock:
            (B.kept.add if on else B.kept.discard)(pid)
            return
        try:
            cg, H = w.V._clockgate(), w.V._helpers()
            if on:
                cg.declare_fixture(pid)
                w.V.KEEP_PAWNS.add(pid)
                H.KEEP_PAWNS.add(pid)
            else:
                cg.withdraw_fixture(pid)
                w.V.KEEP_PAWNS.discard(pid)
                H.KEEP_PAWNS.discard(pid)
        except Exception as ex:  # noqa: BLE001 - an undeclared fixture is swept: the row must say why it could not ask
            if on:
                could_not.append(("keep %s: %r" % (pid, ex))[:120])
            else:                                 # a failed withdraw is no reason the NEXT row could not ask
                w.say("  withdraw fixture %s failed: %r" % (pid, ex))

    def spawn(kind, c, faction="player"):
        r = B.call("jawa/spawn_pawn", kindDef=kind, x=c[0], z=c[1], faction=faction, count=1) or {}
        pid = ((r.get("pawns") or [{}])[0]).get("id")
        if not pid:
            could_not.append("spawn %s at %s failed" % (kind, c))
        else:
            spawned.append(pid)
            keep(pid)
        return pid

    def vanish(*pids):
        for pid in pids:
            if pid:
                B.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish")
                keep(pid, on=False)

    def cell_of(pid):
        """The pawn's current cell from pawn_get, or None."""
        pg = ((B.call("jawa/pawn_get", pawn=pid) or {}).get("pawns") or [{}])[0].get("position") or {}
        return (pg["x"], pg["z"]) if pg.get("x") is not None and pg.get("z") is not None else None

    def report_at(pid, fallback):
        """flowworks_pit_report lists only the pawns standing ON the queried cell (JawaBenchFlowWorksPulseTools.cs
        GetThingList), so a pawn is read at its own cell (round 4 S2 read P(18,4) with the hare at 18,2: both null)."""
        c = cell_of(pid) if pid else None
        if pid and c is None:
            could_not.append("pawn_get %s: no position" % pid)
        return CP.pit_pawn(report(c or fallback), pid)

    def order(pid, c, wait=WAIT_OUT):
        o = B.call("jawa/order_pawn", pawnId=pid, x=c[0], z=c[1], waitTicks=wait, draft=True, unpause=True) or {}
        for p in o.get("pawns") or []:
            if p.get("id") == pid:
                return dict(p, ticksElapsed=o.get("ticksElapsed"))
        return {}

    def climb(pid):
        return kv(sc(NSP, "ProofClimb", "pawn:%s" % pid) or "")

    def report(c):
        return B.call("jawa/flowworks_pit_report", x=c[0], z=c[1]) or {}

    shots = {}

    def shoot(sid, rect_rel, caption_lines):
        title, _, _ = STATIONS[sid]
        rect = (ox + rect_rel[0] - 2, oz + rect_rel[1] - 2, rect_rel[2] + 4, rect_rel[3] + 4)
        src = C.snap(w, "%s_raw" % sid, rect)
        if not src:
            return None
        dst = os.path.join(out_dir, "%s.png" % sid)
        verdicts = ["%s  %s" % (r["status"], r["id"]) for r in rows if r["station"] == sid]
        C.label_image(src, dst, "%s. %s" % (sid[1:], title), "station %s, cells %d,%d %dx%d" % ((sid,) + rect),
                      list(caption_lines) + verdicts)
        shots[sid] = os.path.basename(dst)
        return dst

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)          # noqa: E731
    R = lambda dx, dz, w_, h_: (ox + dx, oz + dz, w_, h_)  # noqa: E731
    site = (ox, oz, SITE_W, SITE_H)
    saved_fw, saved_swim = {}, {}
    if not a.mock:
        if a.fresh_map:
            B.call("rimworld/go_to_main_menu")
            B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
        ok, _ = w.V._wait_playing(B, leave_s=0)
    else:
        ok = True
    save()
    try:
        if not ok:
            row("PSW_site", "UNMEASURED", {"why": "not playing"}, "HARNESS")
            return 2
        if not a.mock:
            B.call("jawa/kill_hostiles")
            B.call("jawa/quiet_site", action="apply", clearThreats=True, proximityLetters=True)
            B.call("jawa/debug_settings", action="set", field="enableStoryteller", value=False)
            B.call("jawa/weather_set", weather="Clear")
            B.call("rimworld/set_god_mode", enabled=False)
        for f, v in FW_SETTINGS.items():
            saved_fw[f] = sget(S_FW, f)
            sset(S_FW, f, v)
        for f in ("swimEnduranceHours", "swimWarnAt"):
            saved_swim[f] = sget(S_SWIM, f)
        res["settingsBefore"] = {"fw": saved_fw, "swim": saved_swim}
        # idempotence: an earlier run's pawns in the site go (no corpse), its digs are filled back, the ground is re-laid
        res["mapColonists"], res["vanishedLeftovers"] = [], []
        for p in (B.call("jawa/list_pawns", limit=400) or {}).get("pawns") or []:
            if p.get("dead") or p.get("x") is None:
                continue
            if in_rect(site, (p.get("x"), p.get("z"))):
                vanish(p.get("id"))
                res["vanishedLeftovers"].append(p.get("id"))
            elif p.get("isPlayer"):
                B.call("jawa/order_pawn", pawnId=p.get("id"), x=p.get("x"), z=p.get("z"), waitTicks=1, draft=True)
                res["mapColonists"].append(p.get("id"))
        if not a.mock:
            # PITWALK_FIX_HUGE_TRUNK_BLOCKERS_IN_SITE (SITE/HARNESS): a fresh full-list quicktest map grew a giant over the
            # site (round 5: 8 RM_HugeTrunkBlocker, PSW_site UNMEASURED). Huge Things re-plans a blocker whose plant still
            # stands, so prepare_site alone cannot clear it; the giant goes first (validation_core.clear_huge_plants).
            res["hugePlantsCleared"] = w.V.clear_huge_plants(B)
        rr = sc(NSP, "ProofResetRect", "%d;%d;%d;%d" % site)
        left = CP.reset_left(rr or "")
        site_rows = []
        if left != 0 or (not a.mock and not w.V.prepare_site(B, site, site_rows, "PSW_site_ready")):
            row("PSW_site", "UNMEASURED", {"why": "site not ready / old digs not reset", "reset": rr, "site": site_rows[:2]},
                "SITE")
            return 2
        del could_not[:]

        # ---------------------------------------------------------------- digs (all stations; then one settle)
        pit(P(2, 2), 3, 3, 3)                                      # S1 sheer D3
        dig(P(7, 3), 2)                                            # S1 rat 1x1 D2
        for x in range(5):                                          # S1 drained-pond stand-in: D2 ring, D4 core
            for z in range(5):
                dig(P(10 + x, 2 + z), 4 if (1 <= x <= 3 and 1 <= z <= 3) else 2)
        for z in range(5):
            dig(P(18, 2 + z), 4)                                   # S2 1-wide trench
        pit(P(23, 2), 3, 3, 4)                                     # S3 ladder pit
        pit(P(29, 2), 3, 3, 4)                                     # S4 jump pit
        pit(P(35, 2), 2, 2, 4)                                     # S5 covered pit
        dig(P(39, 3), 4)                                           # S5 careless 1x1
        pit(P(44, 2), 3, 3, 6)                                     # S6/S7 prison pit
        pit(P(51, 2), 3, 3, 4)                                     # S8 grate pit
        pit(P(57, 2), 3, 3, S10_NOTCHES)                           # S10 exposure pit (a pit-room depth)
        pit(P(3, 13), 3, 3, 8, 4)                                  # S9 sheer 4 m, 2 m water
        pit(P(*BRIM_PIT), 3, 3, 8, 7)                              # S9 near-brim control: 3.5 m water
        bad = CP.dig_misses(digs)
        if bad:
            row("PSW_site_dug", "UNMEASURED", {"why": "%d drive(s) missed their depth" % len(bad), "misses": bad[:6]}, "SITE")
            return 2
        lad = B.call("jawa/spawn_batch", ops="%s:%d,%d" % ((LADDER,) + P(23, 3))) or {}
        B.ticks(SETTLE)

        # ---------------------------------------------------------------- S1 relative climb
        if want("S1"):
            station[0] = "S1"
            col = spawn("Colonist", P(3, 3))
            muff = spawn("Muffalo", P(4, 4), "none")
            if muff:
                B.call("jawa/set_pawn_age", pawn=muff, biologicalYears=8.0)
            rat = spawn("Rat", P(7, 3), "none")
            pond = spawn("Colonist", P(12, 4))
            B.ticks(2)
            st, det = CP.state_verdict(climb(col), want_held=True, want_trapped=True)
            sw, dw = CP.walk_verdict(order(col, P(3, 8)), R(2, 2, 3, 3), want_out=False)
            row("PSW_climb_D3_person_trapped", worst(st, sw), {"climb": det, "walk": dw})
            st, det = CP.state_verdict(climb(muff), want_trapped=False)
            row("PSW_climb_D3_muffalo_free", st, det)
            st, det = CP.state_verdict(climb(rat), want_held=True, want_trapped=True)
            row("PSW_climb_D2_rat_trapped", st, det)
            st, det = CP.state_verdict(climb(pond), want_trapped=False)
            sw, dw = CP.walk_verdict(order(pond, P(12, 9)), R(10, 2, 5, 5), want_out=True)
            row("PSW_climb_slope_never_traps", worst(st, sw), {"climb": det, "walk": dw})
            shoot("S1", STATIONS["S1"][1], ["left: sheer D3 3x3 (person trapped, muffalo free)", "middle: 1x1 D2 (rat)",
                                            "right: D2 ring round a D4 core (slope, person walks out)"])
            vanish(col, muff, rat, pond)

        # ---------------------------------------------------------------- S2 width
        if want("S2"):
            station[0] = "S2"
            hare = spawn("Hare", P(18, 2), "none")
            muff = spawn("Muffalo", P(18, 5), "none")
            if muff:
                B.call("jawa/set_pawn_age", pawn=muff, biologicalYears=8.0)
            B.ticks(SETTLE)
            st, det = v_width(report_at(hare, P(18, 2)), report_at(muff, P(18, 5)))
            row("PSW_width_trench", st, det)
            shoot("S2", STATIONS["S2"][1], ["a 1-wide D4 trench: the hare (south) is held, the adult muffalo is not"])
            vanish(hare, muff)

        # ---------------------------------------------------------------- S3 prison ladder
        if want("S3"):
            station[0] = "S3"
            col = spawn("Colonist", P(24, 3))
            lr = kv(sc(PROMO, "ProofLadder", "%d,%d,raise" % P(23, 3)) or "")
            B.ticks(SETTLE)
            cr = climb(col)
            wr = CP.walk_verdict(order(col, P(24, 8), wait=600), R(23, 2, 3, 3), want_out=False)
            ll = kv(sc(PROMO, "ProofLadder", "%d,%d,lower" % P(23, 3)) or "")
            B.ticks(SETTLE)
            cl = climb(col)
            wl = CP.walk_verdict(order(col, P(24, 8)), R(23, 2, 3, 3), want_out=True)
            st, det = v_ladder(lr, cr, wr, ll, cl, wl)
            row("PSW_ladder_prison_door", st, dict(det, spawnLadder={k: lad.get(k) for k in ("success", "thingsPlaced")}),
                "MOD" if lad.get("thingsPlaced") else "SITE")
            shoot("S3", STATIONS["S3"][1], ["RM_Ladder on the west wall; the colonist walked out once it was lowered"])
            vanish(col)

        # ---------------------------------------------------------------- S4 jump gizmo
        if want("S4"):
            station[0] = "S4"
            col = spawn("Colonist", P(28, 3))
            B.ticks(2)
            tgt = sc(TRAP, "JumpTargetFor", col or "") or ""
            t0 = kv(sc(NSP, "ProofTrap", col or "") or "")
            cell = P(29, 3)
            ret = sc(TRAP, "TryJumpInto", "%s|%d,%d" % ((col,) + cell))
            B.ticks(SETTLE)
            t1 = kv(sc(NSP, "ProofTrap", col or "") or "")
            st, det = v_jump(tgt, ret, t0, t1, R(29, 2, 3, 3))
            row("PSW_jump_into_pit", st, dict(det, target=tgt))
            shoot("S4", STATIONS["S4"][1], ["the colonist jumped from the west lip and is stranded in the D4 pit"])
            vanish(col)

        # ---------------------------------------------------------------- S5 cover / forced entry
        if want("S5"):
            station[0] = "S5"
            col = spawn("Colonist", P(39, 6))
            d0 = report(P(39, 3)).get("descentCount")
            o = order(col, P(39, 3), wait=600)
            d1 = report(P(39, 3)).get("descentCount")
            st, det = v_careless(o, P(39, 3), d0, d1)
            row("PSW_careless_walk_refused", st, det)
            sb = B.call("jawa/spawn_batch", ops=";".join("%s:%d,%d" % ((WOVEN,) + P(35 + i, 2 + j))
                                                        for i in range(2) for j in range(2))) or {}
            c0 = kv(sc(PROMO, "ProofCover", "%d,%d" % P(35, 2)) or "")
            pir = spawn("Pirate", P(34, 6), "hostile")
            if pir:
                B.call("jawa/pawn_gear", pawn=pir, action="clear")
            t0 = kv(sc(NSP, "ProofTrap", pir or "") or "")
            sc(NSP, "ProofShove", "%s;%d,%d" % ((pir,) + P(35, 2)))
            for _ in range(5):
                B.ticks(60)
                c1 = kv(sc(PROMO, "ProofCover", "%d,%d" % P(35, 2)) or "")
                if c1.get("sprung") == "True" or c1.get("present") == "False":
                    break
            B.ticks(SETTLE)
            t1 = kv(sc(NSP, "ProofTrap", pir or "") or "")
            st, det = v_cover_fall(c0, c1, t0, t1)
            row("PSW_cover_gives_way", st, dict(det, deck=sb.get("thingsPlaced")))
            shoot("S5", STATIONS["S5"][1], ["west: woven-scrap deck sprung under the shoved pirate",
                                            "east: the open 1x1 the drafted colonist refused to walk into"])
            vanish(col, pir)

        # ---------------------------------------------------------------- S6 room -> prison, S7 capture/convert down
        prison_rect = R(44, 2, 3, 3)
        centre, far, lip = P(45, 3), P(42, 6), P(43, 3)
        if want("S6") or want("S7"):
            station[0] = "S6"
            room = lambda: kv(sc(NSP, "ProofRoom", "%d,%d;%d,%d" % (centre + far)) or "")   # noqa: E731
            sc(ROOMS, "RebuildAllMaps", "")
            k0 = room()
            B.call("jawa/build_batch", ops="Bed:%d,%d,0" % P(46, 3), stuff="WoodLog", faction="player")
            beds = B.call("jawa/list_things", defName="Bed", rect="%d,%d,%d,%d" % prison_rect, limit=5) or {}
            bid = ((beds.get("things") or [{}])[0]).get("id")
            if bid:
                B.call("jawa/set_bed_owner_type", thing=bid, ownerType="Prisoner")
            sc(ROOMS, "RebuildAllMaps", "")
            k1 = room()
            st, det = v_room(k0, k1, bid)
            row("PSW_room_prison_only_with_bed", st, det)
            shoot("S6", STATIONS["S6"][1], ["a D6 3x3: its own room; a prisoner bed on the east side makes it a prison"])
        if want("S7"):
            station[0] = "S7"
            hid = spawn("Pirate", P(44, 3), "hostile")
            if hid:
                B.call("jawa/pawn_gear", pawn=hid, action="clear")      # unarmed: nothing shoots the warden
            col = spawn("Colonist", far)
            B.ticks(60)
            v0 = sc(NSP, "ProofCaptureDown", hid or "") or ""
            B.call("jawa/set_draft", pawnId=col, drafted=True)
            oj = B.call("jawa/ordered_job", pawnId=col, jobDef="RM_CaptureDown", targetAId=hid, targetBX=lip[0],
                        targetBZ=lip[1]) or {}
            # PITWALK_FIX_CAPTURE_ROW_BLIND (HARNESS): round 5 read prisoner False with no record of why; the order's reply
            # and a (tick, warden, held pawn, verdict) trail are kept so a FAIL names where the job stopped
            ctrail = []
            stop = None
            for k in range(15):
                try:
                    B.ticks(60)
                except Exception as ex:  # noqa: BLE001 - clockgate.GovernorStop: round 5 the warden was hurt at the lip
                    if type(ex).__name__ != "GovernorStop":
                        raise
                    stop = str(ex)[:240]
                wp = ((B.call("jawa/pawn_get", pawn=col) or {}).get("pawns") or [{}])[0].get("position") or {}
                hp = ((B.call("jawa/pawn_get", pawn=hid) or {}).get("pawns") or [{}])[0].get("position") or {}
                cv = sc(NSP, "ProofCaptureDown", hid or "") or ""
                ctrail.append(((k + 1) * 60, (wp.get("x"), wp.get("z")), (hp.get("x"), hp.get("z")), cv[:60]))
                if "prisoner=True" in cv or stop:
                    break
            res["s7"] = {"orderedJob": {k: oj.get(k) for k in ("success", "message", "error", "result") if k in oj},
                         "trail": ctrail, "governorStop": stop}
            v1 = kv(sc(NSP, "ProofCaptureDown", hid or "") or "")
            pg = ((B.call("jawa/pawn_get", pawn=col) or {}).get("pawns") or [{}])[0].get("position") or {}
            st, det = v_capture(v0, v1, (pg.get("x"), pg.get("z")), prison_rect)
            if stop:                                # a disturbance stopped the clock: the row could not finish asking
                st, det = "UNMEASURED", dict(det, why="governor stop during the capture: " + stop)
            if st != "PASS":
                det = dict(det, orderedJob=res["s7"]["orderedJob"], trail=ctrail[:3] + ctrail[-2:])
            row("PSW_capture_down_from_lip", st, det)
            st, det = v_convert(kv(sc(NSP, "ProofLip", "%s;%d,%d;PrisonerConvert" % ((col,) + centre)) or ""))
            row("PSW_convert_down_from_lip", st, det)
            shoot("S7", STATIONS["S7"][1], ["the warden on the west lip; the pirate below is now a prisoner"])
            vanish(hid, col)

        # ---------------------------------------------------------------- S8 sluice / grate
        if want("S8"):
            station[0] = "S8"
            sl, gr = P(49, 7), P(50, 3)
            B.call("jawa/build_batch", ops="%s:%d,%d" % ((SLUICE,) + sl), stuff="WoodLog", faction="player")
            B.call("jawa/spawn_batch", ops="%s:%d,%d" % ((GRATE,) + gr), stuff="Steel")   # factionless on purpose
            hum = spawn("Pirate", P(50, 6), "hostile")
            muf = spawn("Muffalo", P(48, 8), "none")
            hare = spawn("Hare", P(48, 6), "none")
            held = spawn("Pirate", P(51, 3), "hostile")
            for pid in (hum, held):
                if pid:
                    B.call("jawa/pawn_gear", pawn=pid, action="clear")
            B.ticks(SETTLE)
            txt = sc(DOORS, "ProofOpen", "current|%d,%d" % sl) or ""
            st, det = v_sluice_shut(txt, [hum, muf, hare])
            row("PSW_sluice_shut_holds_all", st, det)
            up = sc(DOORS, "ProofSetGate", "current|%d,%d|true" % sl) or ""
            down = sc(DOORS, "ProofSetGate", "current|%d,%d|false" % sl) or ""
            st, det = v_sluice_lift(up, down)
            row("PSW_sluice_lifts_from_bank", st, det)
            hp = report_at(held, P(51, 3)) or {}
            txt = sc(DOORS, "ProofOpen", "current|%d,%d" % gr) or ""
            st, det = v_grate(txt, held, hp.get("held"))
            row("PSW_grate_seals_from_pit", st, det)
            shoot("S8", STATIONS["S8"][1], ["south-west: the shut wooden sluice with a pirate, a muffalo and a hare at it",
                                            "the steel grate on the pit's west lip; the held pirate below cannot open it"])
            vanish(hum, muf, hare, held)

        # ---------------------------------------------------------------- S9 flooded sheer pit + near-brim control
        if want("S9"):
            station[0] = "S9"
            pc, cc = P(4, 14), P(*BRIM_CTL)
            pr = spawn("Villager", pc, "hostile")
            ctl = spawn("Villager", cc, "hostile")
            for pid in (pr, ctl):
                if pid:
                    B.call("jawa/pawn_gear", pawn=pid, action="clear")
                    B.call("jawa/pawn_set_guest_status", pawn=pid, guestStatus="Prisoner", hostFaction="PlayerColony")
            B.ticks(SETTLE)
            swims = tbool(sc(SWIMPOSE, "SwimsAt", "%s|%d,%d" % ((pr,) + pc)))
            st, det = v_flood(swims, kv(sc(SWIM, "ProofSwim", "%d,%d" % pc) or ""),
                              kv(sc(FILLFX, "ProofDrown", "%d,%d" % pc) or ""), climb(pr))
            row("PSW_flood_swims_cannot_climb", st, det)
            st, det = v_near_brim(kv(sc(FILLFX, "ProofDrown", "%d,%d" % cc) or ""), climb(ctl))
            row("PSW_flood_near_brim_exit", st, det)
            vanish(ctl)
            # the warning: endurance compressed (restored in finally), stepped WARN_STEP ticks at a time to the crossing
            warn_at = fnum(sget(S_SWIM, "swimWarnAt"))
            mb = B.call("rimworld/list_messages", limit=200) or {}
            msgs0 = list(flat_strings(mb)) if mb.get("success") is not False else None
            sset(S_SWIM, "swimEnduranceHours", SWIM_ENDURANCE_FAST)
            trail = []
            for k in range(WARN_BUDGET // WARN_STEP):
                B.ticks(WARN_STEP)
                ex = fnum(sc(SWIM, "ExhaustionOf", pr or ""))
                pg = ((B.call("jawa/pawn_get", pawn=pr) or {}).get("pawns") or [{}])[0]
                pos = pg.get("position") or {}
                xz = (pos.get("x"), pos.get("z"))
                head = tbool(kv(sc(SWIM, "ProofSwim", "%d,%d" % xz) or "").get("headUp")) if xz[0] is not None else None
                trail.append(((k + 1) * WARN_STEP, ex, xz, bool(pg.get("dead")), head))
                if ex is not None and warn_at is not None and ex >= warn_at:
                    break
            ma = B.call("rimworld/list_messages", limit=200) or {}
            msgs1 = list(flat_strings(ma)) if ma.get("success") is not False else None
            st, det = v_warned(trail, warn_at, msgs0, msgs1, R(3, 13, 3, 3))
            if saved_swim.get("swimEnduranceHours") is not None:
                sset(S_SWIM, "swimEnduranceHours", saved_swim["swimEnduranceHours"])
            row("PSW_flood_warned_before_under", st, det)
            shoot("S9", STATIONS["S9"][1], ["west: 4 m sheer pit, 2 m water: the prisoner swims at the wall, warned",
                                            "east: the near-brim control (3.5 m water) has an exit"])
            vanish(pr)

        # ---------------------------------------------------------------- S10 children
        if want("S10"):
            station[0] = "S10"
            col = spawn("Colonist", P(58, 3))
            B.call("jawa/order_pawn", pawnId=col, x=P(58, 3)[0], z=P(58, 3)[1], waitTicks=1, draft=True)
            B.ticks(4 * 250 + 10)
            pg = ((B.call("jawa/pawn_get", pawn=col) or {}).get("pawns") or [None])[0]
            st, det = v_exposure(pg, fnum(sget(S_FW, "pitRoomMinDepthMetres")), S10_NOTCHES)
            row("PSW_child_pit_exposure", st, det)
            st, det = v_wallart(sc(NSP, "ProofWallFaces", "%d,%d" % P(2, 3)) or "")
            row("PSW_child_wall_art", st, det)
            shoot("S10", STATIONS["S10"][1], ["a colonist on an open D%d pit floor (RM_PitExposure)" % S10_NOTCHES,
                                              "the excavation wall faces: judge the art on S1's capture too"])
            vanish(col)
    finally:
        for f, v in saved_fw.items():
            if v is not None:
                sset(S_FW, f, v)
        if saved_swim.get("swimEnduranceHours") is not None:
            sset(S_SWIM, "swimEnduranceHours", saved_swim["swimEnduranceHours"])
            res["swimEnduranceRestored"] = sget(S_SWIM, "swimEnduranceHours")
        if not a.mock:
            B.call("jawa/debug_settings", action="set", field="enableStoryteller", value=True)
        res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        res["summary"] = {s: sum(1 for r in rows if r["status"] == s) for s in ("PASS", "FAIL", "UNMEASURED")}
        try:
            if not a.no_shots or a.mock:
                src = C.snap(w, "overview_raw", site)
                if src:
                    C.label_image(src, os.path.join(out_dir, "overview.png"), "%s: the whole site" % ITEM,
                                  "numbers match the walk map", [])
            run_st = {k: v for k, v in STATIONS.items() if want(k)}
            res["walkMap"] = draw_walk_map(os.path.join(out_dir, "walk_map.png"), (ox, oz), run_st, rows)
            for sid, (title, rect, _) in run_st.items():
                groups.append({"id": sid, "title": "%s. %s" % (sid[1:], title),
                               "readings": [(r["status"], "%s: %s" % (r["id"], json.dumps(r["detail"], default=str)[:300]))
                                            for r in rows if r["station"] == sid],
                               "images": [(shots[sid], "%s capture" % sid)] if sid in shots else []})
            groups.insert(0, {"id": "map", "title": "Walk map", "images": [("walk_map.png", "numbered stations")]
                              + ([("overview.png", "the site in game")] if os.path.exists(os.path.join(out_dir, "overview.png"))
                                 else [])})
            res["index"] = C.write_index(os.path.join(out_dir, "index.html"), "%s live walk" % ITEM,
                                         "Every verdict is a state read; the pictures are for your eye.", groups,
                                         accumulate=False)
        except Exception as ex:  # noqa: BLE001  (the pictures never hide the rows)
            res["pictureError"] = repr(ex)
        save()
        print("result ->", out, res["summary"])
    return 0 if res["summary"].get("FAIL", 0) == 0 and res["summary"].get("UNMEASURED", 0) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
