# -*- coding: utf-8 -*-
"""prove_stat_and_room.py - the first live run of jawa/pawn_stats and jawa/room_get.

WHY THIS FILE EXISTS
====================
Both tools were written, built and deployed with the game DOWN (2026-08-26, seat
CHECK, deploy verified by bytes: sha256 b52b37cba71f4861...). Neither has ever
been called. A build that compiled is NOT a tool the bridge serves - RimBridge
discovers companions only at startup - so nothing about them is established
until this runs.

They exist because four queue rows had no instrument at all:

  LIVE_HALF_OF_LOAD_1  T1 T2 N1 N2   need ComfyTemperatureMin/Max on a live pawn
  TEMPLATE_ENGINE_ACCEPTANCE_1  1 2  need Room.Role and a room's temperature

WHAT IT CHECKS, IN THE ONLY ORDER THAT MAKES SENSE
==================================================
  1. CENSUS. Does the running game register the tools the deployed DLL contains?
     Everything below is meaningless until this passes. Expect 166 jawa/ tools.
  2. pawn_stats REFUSES a bad stat name instead of skipping it. This is checked
     BEFORE any real reading, because a tool that silently drops a stat reports
     an empty answer that reads exactly like "the pawn does not have it".
  3. pawn_stats on one pawn per xenotype -> the four temperature rows.
  3b. thing_stats on a HELD weapon -> value beside defBase, so a StatPart that
     moved the number is visible. STAT_ON_INSTANCE_TOOL_1.
  4. room_get on a built structure -> the two template rows.

USAGE
=====
    python.exe D:\\Luke\\dev\\Rimworld\\src\\RimMandrake\\bridgetools\\prove_stat_and_room.py
    ... --census        stop after check 1
    ... --rect X,Z,W,H  where a dwelling has been built, for check 4

SAFETY: read-only except for spawning pawns, which needs a map. Nothing is
destroyed and the game is never unpaused.
"""
import sys, json, io, argparse, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc

# 🔑 198 = the [Tool] names DECLARED IN SOURCE, counted by attribute, not by
# scanning the DLL for strings: build.py's tool_surface reads 200 because two
# tool names are MENTIONED in other tools' description prose ('jawa/anomaly_',
# 'jawa/revoke'). The live census counts what REGISTERED, so 198 is the number.
# ⚠️ This expects the 2026-08-26 down-window deploy (NEXT_RELOAD sec 25). Against a
# game still running the older DLL this reads 166 and says so, which is correct.
EXPECT_TOOLS = 198
NEW = ("jawa/pawn_stats", "jawa/room_get", "jawa/thing_stats")

# The genes measured off live instances on 2026-08-26. The stat must move in the
# direction the genes say; the exact numbers are what this run establishes.
XENOS = [
    ("RimMandrakeUgnaught", "no temperature gene at all"),
    ("RimMandrakeTwilek",   "no temperature gene at all"),
    ("RimMandrakeKelDor",   "no temperature gene at all"),
    ("Baseliner",           "the reference point"),
    ("MandrakeJawa",        "MinTemp_SmallDecrease + MaxTemp_SmallIncrease"),
    ("RimMandrakeChiss",    "MinTemp_LargeDecrease + MaxTemp_SmallDecrease"),
    ("RimMandrakeWookiee",  "Furskin + MinTemp_SmallDecrease + MaxTemp_SmallIncrease  <- N2, the stack"),
]

fails = []


def note(ok, label, detail=""):
    print("  %-4s %-46s %s" % ("PASS" if ok else "FAIL", label, detail))
    if not ok:
        fails.append(label)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--census", action="store_true", help="stop after the tool census")
    ap.add_argument("--rect", default=None, help="'x,z,w,h' of a built structure for room_get")
    ap.add_argument("--x", type=int, default=120)
    ap.add_argument("--z", type=int, default=120)
    a = ap.parse_args(argv)

    h, p, t = rc.resolve_endpoint()
    b = rc.RimBridge(host=h, port=p, token=t, timeout=90)
    b.connect()

    def call(m, args=None):
        try:
            r = b.call(m, args or {})
            r.pop("operation", None)
            return r
        except Exception as ex:
            return {"success": False, "EXC": str(ex)}

    # ---- 1. census -------------------------------------------------------
    print("\n1. CENSUS - what the RUNNING GAME registered")
    names = sorted(x.get("name") for x in b.list_tools())
    jawa = [n for n in names if n.startswith("jawa/")]
    note(len(jawa) == EXPECT_TOOLS,
         "jawa/ tools registered",
         "%d (expected %d)%s" % (len(jawa), EXPECT_TOOLS,
                                 "" if len(jawa) == EXPECT_TOOLS
                                 else "  <- the DLL in the game is not the one that was deployed"))
    for n in NEW:
        note(n in names, "registered: " + n,
             "" if n in names else "absent from the LIVE list - it does not exist yet")
    if a.census or any(n not in names for n in NEW):
        return done()

    # ---- 2. it must REFUSE a bad stat name --------------------------------
    print("\n2. pawn_stats REFUSES an unresolvable stat rather than skipping it")
    ps = call("jawa/list_pawns", {"limit": 999}).get("pawns") or []
    if not ps:
        note(False, "a pawn to read", "no pawns on the map - load a map with pawns first")
        return done()
    subject = ps[0]["id"]
    r = call("jawa/pawn_stats", {"pawn": subject, "stats": "ComfortableTemperatureMin"})
    # ComfortableTemperatureMin does NOT exist - the real names are ComfyTemperature*.
    # A tool that returns success here has silently dropped the question.
    note(r.get("success") is False and r.get("details", {}).get("refused"),
         "a bogus stat name fails loudly",
         (r.get("message") or "")[:70])
    sug = ((r.get("details") or {}).get("refused") or [{}])[0].get("suggestions") or []
    note(any("Comfy" in s for s in sug), "and suggests the real name", str(sug[:3]))

    # ---- 3. the four temperature rows -------------------------------------
    print("\n3. ComfyTemperatureMin/Max per xenotype  (T1 T2 N1 N2)")
    rows = []
    for i, (xn, why) in enumerate(XENOS):
        sp = call("jawa/spawn_pawn", {"kindDef": "Colonist", "x": a.x + i * 2, "z": a.z,
                                      "faction": "none", "count": 1, "xenotype": xn})
        got = (sp.get("pawns") or [])
        if not got:
            note(False, "spawn " + xn, (sp.get("message") or "")[:60])
            continue
        pid = got[0]["id"]
        r = call("jawa/pawn_stats",
                 {"pawn": pid, "stats": "ComfyTemperatureMin,ComfyTemperatureMax"})
        vals = {s["defName"]: s["value"] for s in (r.get("stats") or [])}
        lo, hi = vals.get("ComfyTemperatureMin"), vals.get("ComfyTemperatureMax")
        ok = lo is not None and hi is not None
        rows.append((xn, lo, hi, why))
        note(ok, "read " + xn, "%s ... %s   [%s]" % (lo, hi, why))
    print("\n   the table these four rows are graded on:")
    for xn, lo, hi, why in rows:
        print("     %-24s %8s ... %-8s  %s" % (xn, lo, hi, why))
    print("   \u26d4 T2 and N1 are BOTH UNGRADED until the owner rules. He said, 2026-08-26:")
    print("      \"Measure it, then ask again\" - so this table goes back to him, it is not a verdict.")
    print("      T2 says the Jawa should read -40...+65, N1 says -50...+55, for the same stat.")
    print("      The genes say N1. Picking the criterion after looking is not a test.")


    # ---- 3b. thing_stats: the same rule, for ITEMS -------------------------
    # STAT_ON_INSTANCE_TOOL_1. Runs before the room block on purpose: that one
    # returns early without --rect, and this must not be skipped by an argument
    # that has nothing to do with it.
    print("\n3b. thing_stats  (STAT_ON_INSTANCE_TOOL_1 - the instance, beside the def)")
    armed = None
    for q in ps[:40]:
        g = call("jawa/pawn_get", {"pawn": q["id"]})
        eq = g.get("equipment") or []
        if eq:
            armed = (q["id"], eq[0].get("def"))
            break
    if armed is None:
        note(False, "an armed pawn to read",
             "no pawn on this map is holding anything - UNMEASURED, not a pass")
    else:
        pid, wdef = armed
        r = call("jawa/thing_stats", {"pawn": pid, "slot": "equipment",
                                      "stats": "MeleeWeapon_AverageDPS,ArmorPenetrationSharp,Mass"})
        things = r.get("things") or []
        st = (things[0].get("stats") if things else []) or []
        note(r.get("success") is True and bool(st), "read a HELD weapon's stats",
             "%s on %s" % (wdef, pid))
        note(bool(st) and all("defBase" in x for x in st),
             "defBase reported beside every value",
             "without it, 'a StatPart moved this' cannot be seen at all")
        for x in st:
            print("     %-26s value %-10s defBase %-10s moved=%s  parts=%s"
                  % (x.get("defName"), x.get("value"), x.get("defBase"),
                     x.get("movedFromDef"), (x.get("statParts") or [])[:2]))
        # A stat that does not exist must be REFUSED BY NAME, never reported as 0.
        bad = call("jawa/thing_stats", {"pawn": pid, "slot": "equipment",
                                        "stats": "ArmourPenetrationSharp"})
        ref = ((bad.get("details") or {}).get("refused")) or bad.get("refused") or []
        note(bad.get("success") is False and bool(ref),
             "a bogus stat name fails loudly", (bad.get("message") or "")[:70])
        note(any("ArmourPenetrationSharp" == (x.get("stat") or "") for x in ref),
             "and the refusal NAMES the stat asked for", str([x.get("stat") for x in ref][:3]))
        print("   \u26a0 The ground-vs-held comparison this tool exists for is TWO calls:")
        print("      jawa/spawn_batch a second copy, then jawa/thing_stats {thing: '<groundId>,<heldId>'}")
        print("      One answer, both rows, defBase beside each. That is LIGHTSABER_AP_FROM_HAND_1.")

    # ---- 4. rooms ---------------------------------------------------------
    print("\n4. room_get  (TEMPLATE_ENGINE_ACCEPTANCE_1 criteria 1 and 2)")
    if not a.rect:
        print("   skipped - pass --rect x,z,w,h where a dwelling has been built.")
        print("   Build one first:  rimplace calls dwelling --rect <x>,<z>,18,10 --rooms 3 --occupants 4")
        print("   \u26a0 translate rect -> ops until TEMPLATE_RECT_PARAM_NOT_ACCEPTED_1 is fixed.")
        return done()
    r = call("jawa/room_get", {"rect": a.rect})
    rooms = r.get("rooms") or []
    note(r.get("success") is True, "room_get answered", (r.get("message") or "")[:70])
    roles = [q.get("role") for q in rooms]
    print("   roles: %s" % roles)
    print("   temps: %s" % [round(q.get("temperature", 0), 1) for q in rooms])
    want = {"Bedroom", "Barracks", "DiningRoom", "Storeroom"}
    note(len(rooms) >= 3, "criterion 1: at least three rooms", "%d found" % len(rooms))
    note(any(x in want for x in roles if x),
         "criterion 1: the game calls them house rooms",
         "matched %s" % sorted(set(roles) & want))
    hot = [q for q in rooms if q.get("temperature", 0) > 32.0 and not q.get("isOutdoors")]
    note(not hot, "criterion 2: every indoor room <= 32 C",
         "over: %s" % [(q["id"], round(q["temperature"], 1)) for q in hot])
    return done()


def done():
    print("\n" + ("ALL CHECKS PASSED" if not fails
                  else "%d FAILED: %s" % (len(fails), ", ".join(fails))))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
