"""Prove the raid criterion for all seven authored factions.

Run with WINDOWS python.exe - the bridge binds Windows loopback.

Discipline this script enforces, each rule bought by a retracted evidence table:
  * only ONE authored faction hostile at a time; every other returned to Neutral first
  * every row reads actual.substituted - a non-hostile target is silently swapped
  * the kinds are read off the MAP (jawa/list_pawns), never echoed from the request
  * windowsOpened / blockedByDialog from the new fire_raid is recorded on every row
"""
import sys, json, time, os
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rbc

OUT = r"D:\Luke\dev\Rimworld\Transient\raid_proof_2026_08_30\results.json"
GM = json.load(open(r"D:\Luke\dev\Rimworld\Transient\raid_proof_2026_08_30\groupmakers.json"))

TARGETS = [
    "Jawa_HuttCartel",
    "Jawa_FreeDroidEnclaves",
    "Jawa_WildsteamClan",
    "Jawa_DeepwaterCompact",
    "Jawa_GeonosianFoundryHive",
    "Jawa_AscendantHelix",
    "Jawa_Junkers",
]
CONTROL = "Pirate"          # extorted on every prior pass; the negative control
POINTS = 3000.0
MAX_TRIES = 3

host, port, token = rbc.resolve_endpoint()
S = rbc.RimBridge(host=host, port=port, token=token, timeout=600.0)
S.connect()


def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try:
            r = json.loads(r["content"][0]["text"])
        except Exception:
            pass
    return r


def log(*a):
    print(*a, flush=True)


rec = {"startedUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "rows": [], "notes": []}

# ---------------------------------------------------------------- 0. map
log("== starting quicktest map")
r = call("rimworld/start_debug_game_ready", timeoutMs=280000,
         readiness="mapData", pauseIfNeeded=True)
log("   ", json.dumps(r)[:300])
for _ in range(180):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing":
        break
    time.sleep(1)
log("   programState:", st.get("programState"))

info = call("rimworld/get_game_info")
rec["gameInfo"] = {k: info.get(k) for k in ("modCount", "ticksGame", "mapCount", "gameVersion")}
log("   gameInfo:", json.dumps(rec["gameInfo"]))

# ---------------------------------------------------------------- 0b. tool surface
try:
    names = [t.get("name", t) if isinstance(t, dict) else t for t in S.list_tools()]
except Exception as e:
    names = []
    rec["notes"].append("list_tools failed: %r" % (e,))
rec["toolCount"] = len(names)
rec["jawaCount"] = len([n for n in names if str(n).startswith("jawa/")])
log("   tools:", rec["toolCount"], "jawa/:", rec["jawaCount"])

# ---------------------------------------------------------------- 1. factions present
fl = call("jawa/list_factions", limit=500)
facs = {f["defName"]: f for f in fl.get("factions", [])}
rec["factionsPresent"] = {t: (t in facs) for t in TARGETS}
rec["settlementCounts"] = {t: facs.get(t, {}).get("settlementCount") for t in TARGETS}
log("   present:", json.dumps(rec["factionsPresent"]))
log("   settlements:", json.dumps(rec["settlementCounts"]))

ALL_JAWA = [d for d in facs if d.startswith("Jawa_")]


def neutralise_all(except_def=None):
    """Exactly one authored faction hostile at a time."""
    for d in ALL_JAWA:
        if d == except_def:
            continue
        call("jawa/faction_relations_set", faction=d, other="Player",
             kind="Neutral", goodwill=0, both=True)


def pawn_kinds(fdef):
    p = call("jawa/list_pawns", faction=fdef, limit=500)
    hist = {}
    for row in p.get("pawns", []):
        k = row.get("kind")
        hist[k] = hist.get(k, 0) + 1
    return hist, p.get("pawns", [])


def fire(fdef, tries=MAX_TRIES):
    attempts = []
    for n in range(tries):
        before_hist, _ = pawn_kinds(fdef)
        r = call("jawa/fire_raid", points=POINTS, faction=fdef,
                 strategy="ImmediateAttack", arrivalMode="EdgeWalkIn", dryRun=False)
        after_hist, after_pawns = pawn_kinds(fdef)
        gained = {}
        for k, v in after_hist.items():
            d = v - before_hist.get(k, 0)
            if d > 0:
                gained[k] = d
        attempts.append({
            "try": n + 1,
            "executed": r.get("executed"),
            "success": r.get("success"),
            "blockedByDialog": r.get("blockedByDialog"),
            "windowsOpened": r.get("windowsOpened"),
            "actual": r.get("actual"),
            "arrived": r.get("arrived"),
            "pawnsArrivedTotal": r.get("pawnsArrivedTotal"),
            "note": (r.get("note") or "")[:400],
            "kindsGainedOnMap": gained,
        })
        if gained:
            break
    return attempts


# ---------------------------------------------------------------- 2. control
log("\n== CONTROL:", CONTROL, "(extorted on every prior pass)")
neutralise_all()
call("jawa/faction_relations_set", faction=CONTROL, other="Player",
     kind="Hostile", goodwill=-100, both=True)
ctrl = fire(CONTROL, tries=2)
rec["control"] = {"faction": CONTROL, "attempts": ctrl}
log("   ", json.dumps(ctrl[-1])[:600])

# ---------------------------------------------------------------- 3. the seven
for t in TARGETS:
    log("\n==", t)
    if t not in facs:
        rec["rows"].append({"faction": t, "verdict": "ABSENT FROM WORLD"})
        continue
    neutralise_all(except_def=t)
    # 🔴 jawa/set_faction_relation CANNOT make these factions hostile: it reports
    # "READ-BACK DOES NOT MATCH THE REQUEST - the engine overrode it", moving
    # goodwill to -100 while the kind stays Neutral. jawa/faction_relations_set
    # writes BOTH stored records and calls Notify_RelationKindChanged, which is
    # what actually sticks. Measured this session.
    rel = call("jawa/faction_relations_set", faction=t, other="Player",
               kind="Hostile", goodwill=-100, both=True)
    fl2 = call("jawa/list_factions", defName=t)
    hostile = (fl2.get("factions") or [{}])[0].get("hostile")
    log("   hostile:", hostile, "| setter success:", rel.get("success"))
    if not hostile:
        rec["rows"].append({"faction": t, "verdict": "COULD NOT MAKE HOSTILE",
                            "setter": rel.get("message")})
        log("   SKIPPED - not hostile, a firing here would be substituted")
        continue

    attempts = fire(t)
    last = attempts[-1]
    hist, pawns = pawn_kinds(t)

    expected = set(GM.get(t, {}).get("groups", {}).get("Combat", []))
    got = set(last["kindsGainedOnMap"].keys())
    foreign = sorted(got - expected)

    # anything that arrived under a DIFFERENT faction during the firing
    other_arrivals = [a for a in (last.get("arrived") or [])
                      if a.get("faction") != t]

    row = {
        "faction": t,
        "hostileAtFiring": hostile,
        "raidsForbidden": GM.get(t, {}).get("raidsForbidden"),
        "expectedCombatKinds": sorted(expected),
        "kindsGainedOnMap": last["kindsGainedOnMap"],
        "foreignKinds": foreign,
        "substituted": (last.get("actual") or {}).get("substituted"),
        "actualFaction": (last.get("actual") or {}).get("faction"),
        "blockedByDialog": last.get("blockedByDialog"),
        "windowsOpened": last.get("windowsOpened"),
        "pawnsArrivedTotal": last.get("pawnsArrivedTotal"),
        "otherFactionArrivals": other_arrivals,
        "triesUsed": len(attempts),
        "attempts": attempts,
    }
    total = sum(last["kindsGainedOnMap"].values())
    if total > 0 and not row["substituted"] and not foreign:
        row["verdict"] = "PASS - raided as itself, own kinds only"
    elif total > 0 and not row["substituted"]:
        row["verdict"] = "PASS WITH FOREIGN KINDS: " + ",".join(foreign)
    elif row["substituted"]:
        row["verdict"] = "INVALID - substituted to " + str(row["actualFaction"])
    else:
        row["verdict"] = "NO ARRIVALS in %d tries" % len(attempts)
    rec["rows"].append(row)
    log("   VERDICT:", row["verdict"], "|", json.dumps(last["kindsGainedOnMap"]))

    # Pawns are left on the PAUSED map on purpose - every count is a per-faction
    # before/after diff, so leftovers cannot contaminate the next faction's row,
    # and a mass kill is a write nobody needs.
    call("jawa/faction_relations_set", faction=t, other="Player",
         kind="Neutral", goodwill=0, both=True)
    log("   relation restored to Neutral")

# ---------------------------------------------------------------- 4. restore
log("\n== restoring relations")
neutralise_all()
rec["finalFactions"] = [
    {k: f.get(k) for k in ("defName", "hostile", "goodwill")}
    for f in call("jawa/list_factions", limit=500).get("factions", [])
    if f.get("defName", "").startswith("Jawa_")
]

json.dump(rec, open(OUT, "w"), indent=1)
log("\nwritten:", OUT)
for r0 in rec["rows"]:
    log("%-32s %s" % (r0["faction"], r0.get("verdict")))
