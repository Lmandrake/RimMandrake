"""Proof of LONGSHADE_JAWATOW_RECHECK_1: the Jawa clan tows the Long Shade's dead sandcrawler away.

    python3 src/RimMandrake/LongShade/prove_jawatow.py --offline
    python.exe "$(wslpath -w src/RimMandrake/LongShade/prove_jawatow.py)" --clause A1 < /dev/null    (A1..A4)

Exit 0 = the clause holds, 1 = it does not, 2 = UNMEASURED (no game, no RUT_Jawa_ faction or Utinni layer, no hull).

The live clauses share ONE scene (it costs ~15000 game ticks): the first clause asked runs it on a freshly generated
RM_LongShade map (tile 114480, size 200; the dead crawler is laid by the Crawler Road terminus, so up to 3 maps are tried)
and stores every reading in <tempdir>/rm_jawatow_scene.json; a later clause within 45 minutes reads that record.
Scene: Stage (drafted colonist inside the 25x9 hull, hostiles in it killed, loose items and corpses removed) -> run 300
ticks (the entry scan is every 250) -> CanFire disabled -> CanFire -> Fire -> run towTicks+300 -> Hull + log.
  A1  canFireNow (forced, fresh worker) is True with the colonist entered, no hostiles and no loose items in the hull
  A2  firing spawns a non-hostile group of a RUT_Jawa_* faction under LordJob_VisitColony (Peaceful group; Combat when
      the faction has no Peaceful maker) and the hull reads clanComing
  A3  after towTicks the hull reads towed, no faction-less non-rock building is left in the rect, and
      "[RM LongShade] Jawa return: hull towed" is in the log
  A4  with jawaReturnEnabled=false canFireNow is False (the same moment A1 reads True, so the switch is what decided)
Probe: RimMandrake.LongShade.RM_HullTowProof (Source/RM_HullTowProof.cs) through jawa/static_call.
--offline  the wiring and the verdict logic (no game): the probe is compiled into the csproj, the def names the
           worker, and judge() passes a good record and fails each clause on a record broken for that clause.
           (DLL freshness against its source is the .srchash's job, checked at landing.)
"""
import json
import os
import re
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PROBE = "RimMandrake.LongShade.RM_HullTowProof"
TILE, SIZE, TRIES = 114480, 200, 3
LOGLINE = "[RM LongShade] Jawa return: hull towed"
RECORD = os.path.join(tempfile.gettempdir(), "rm_jawatow_scene.json")
FRESH_S = 45 * 60
CLAUSES = ("A1", "A2", "A3", "A4")


def kv(line):
    """'HULL a=1 b=x,y' -> {'a': '1', 'b': 'x,y', '_head': 'HULL'}"""
    out = {"_head": (line or "").split(" ", 1)[0]}
    for m in re.finditer(r"(\w+)=(\S*)", line or ""):
        out[m.group(1)] = m.group(2)
    return out


def judge(rec):
    """{clause: (ok, why)} from a scene record. Pure; the selftest feeds it fakes."""
    out = {}
    st, h0 = kv(rec.get("staged_hull")), kv(rec.get("canfire"))
    off = kv(rec.get("canfire_disabled"))
    a1 = (st.get("entered") == "True" and st.get("hostiles") == "0" and st.get("items") == "0"
          and h0.get("_head") == "CANFIRE" and h0.get("forced") == "True")
    out["A1"] = (a1, "hull %s | %s" % (rec.get("staged_hull"), rec.get("canfire")))
    f = kv(rec.get("fired"))
    try:
        n = int(f.get("pawns", "0"))
    except ValueError:
        n = 0
    a2 = (f.get("_head") == "FIRED" and f.get("ok") == "True" and n >= 1 and f.get("faction", "").startswith("RUT_Jawa_")
          and f.get("factions") == "1" and f.get("hostile") == "False" and f.get("lords") == "LordJob_VisitColony"
          and f.get("clanComing") == "True")
    out["A2"] = (a2, rec.get("fired"))
    t = kv(rec.get("towed_hull"))
    a3 = t.get("towed") == "True" and t.get("buildings") == "0" and bool(rec.get("log_hit"))
    out["A3"] = (a3, "%s | log: %s" % (rec.get("towed_hull"), rec.get("log_hit") or "NOT FOUND"))
    a4 = off.get("_head") == "CANFIRE" and off.get("forced") == "False" and off.get("setting") == "False" and a1
    out["A4"] = (a4, "%s (enabled: %s)" % (rec.get("canfire_disabled"), rec.get("canfire")))
    return out


# ---------------------------------------------------------------- offline
def _read(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as fh:
        return fh.read()


def _good():
    return {"staged_hull": "HULL biome=RM_LongShade hasHull=True center=1,2 rect=0,0,25,9 entered=True clanComing=False towed=False towTicks=15000 buildings=40 items=0 hostiles=0",
            "canfire": "CANFIRE forced=True unforced=False setting=True",
            "canfire_disabled": "CANFIRE forced=False unforced=False setting=False",
            "fired": "FIRED ok=True pawns=3 faction=RUT_Jawa_Kreetle factions=1 peacefulMaker=False hostile=False lords=LordJob_VisitColony clanComing=True",
            "towed_hull": "HULL biome=RM_LongShade hasHull=False center=1,2 rect=0,0,25,9 entered=True clanComing=False towed=True towTicks=15000 buildings=0 items=0 hostiles=0",
            "log_hit": LOGLINE + ", 40 buildings removed"}


def offline():
    bad = []
    proj = _read("src/RimMandrake/LongShade/Source/RM_LongShade.csproj")
    if '<Compile Include="RM_HullTowProof.cs" />' not in proj:
        bad.append("RM_HullTowProof.cs is not compiled by RM_LongShade.csproj")
    src = _read("src/RimMandrake/LongShade/Source/RM_HullTowProof.cs")
    for m in ("Hull", "Stage", "CanFire", "Fire"):
        if not re.search(r"public static string %s\(string \w+\)" % m, src):
            bad.append("RM_HullTowProof.%s(string) missing" % m)
    if "class IncidentWorker_RM_HullTow" not in _read("src/RimMandrake/LongShade/Source/RM_ShadeExtras.cs"):
        bad.append("IncidentWorker_RM_HullTow missing")
    if LOGLINE not in _read("src/RimMandrake/LongShade/Source/RM_ShadeExtras.cs"):
        bad.append("the tow log line is no longer %r" % LOGLINE)
    xml = _read("src/RimUtinni/UtinniPatches/Defs/IncidentDefs/RUT_JawaReturnTow.xml")
    if "<workerClass>RimMandrake.LongShade.IncidentWorker_RM_HullTow</workerClass>" not in xml or "<li>RUT_Jawa_</li>" not in xml:
        bad.append("RUT_JawaReturnTow no longer names the worker or the RUT_Jawa_ prefix")
    # verdict logic: a good record passes every clause; each break fails exactly its clause
    g = judge(_good())
    bad += ["judge fails %s on a good record: %s" % (c, w) for c, (ok, w) in g.items() if not ok]
    breaks = {"A1": ("canfire", "CANFIRE forced=False unforced=False setting=True"),
              "A2": ("fired", "FIRED ok=True pawns=3 faction=RUT_Jawa_Kreetle factions=1 peacefulMaker=False hostile=True lords=LordJob_AssaultColony clanComing=True"),
              "A3": ("log_hit", None),
              "A4": ("canfire_disabled", "CANFIRE forced=True unforced=False setting=False")}
    for c, (k, v) in breaks.items():
        rec = _good()
        rec[k] = v
        if judge(rec)[c][0]:
            bad.append("judge passes %s on a record broken for it (%s=%r)" % (c, k, v))
    rec = _good()
    rec["towed_hull"] = rec["towed_hull"].replace("buildings=0", "buildings=7")
    if judge(rec)["A3"][0]:
        bad.append("judge passes A3 with buildings left in the hull")
    for b in bad:
        print("FAIL " + b)
    print("%s offline: probe compiled, def wired, judge sees a pass and every clause's fail" % ("PASS" if not bad else "FAIL"))
    return 0 if not bad else 1


# ---------------------------------------------------------------- live
def _scene():
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
    from scenes import scenelib as S  # noqa: E402
    from await_lifecycle import await_lifecycle  # noqa: E402

    def static(method, arg=""):
        r = S.call("jawa/static_call", type=PROBE, method=method, args=arg)
        return str((r or {}).get("result", "")) if isinstance(r, dict) else str(r)

    lc = await_lifecycle(S.call, "map_ready", deadline_s=400, start=True)
    if not lc.ok:
        return {"started": time.time(), "unmeasured": "no playing map: " + lc.reason}
    back = (S.call("jawa/map_info") or {}).get("mapIndex", 0)
    rec = {"started": time.time()}
    probe = static("CanFire")
    if not probe.startswith("CANFIRE"):
        rec["unmeasured"] = "probe or IncidentDef RUT_JawaReturnTow absent (Utinni layer / new DLL not loaded): " + probe
        return rec
    mid = None
    try:
        for i in range(TRIES):
            mid = S.biome_map(TILE, "RM_LongShade", size=SIZE)
            hull = static("Hull")
            rec.setdefault("maps", []).append(hull)
            if "hasHull=True" in hull:
                break
            S.drop_map(mid, TILE, back)
            mid = None
        if mid is None:
            rec["unmeasured"] = "no generated RM_LongShade map laid the crawler hull in %d tries" % TRIES
            return rec
        rec["stage"] = static("Stage")
        S.run(300)
        rec["staged_hull"] = static("Hull")
        rec["canfire_disabled"] = static("CanFire", "disabled")
        rec["canfire"] = static("CanFire")
        S.call("jawa/drain_log", limit=2000)            # empty the window so the line below is this scene's
        rec["fired"] = static("Fire")
        tow = int(kv(rec["staged_hull"]).get("towTicks", "15000") or 15000)
        if "ok=True" in rec["fired"]:
            S.run(tow + 300)
        rec["towed_hull"] = static("Hull")
        logs = S.call("jawa/drain_log", limit=2000) or {}
        hits = [json.dumps(m) for m in (logs.get("messages") or []) if LOGLINE in json.dumps(m)]
        rec["log_hit"] = hits[0][:300] if hits else ""
    finally:
        if mid is not None:
            S.drop_map(mid, TILE, back)
    return rec


def live(clause):
    rec = None
    if os.path.isfile(RECORD):
        with open(RECORD, encoding="utf-8") as fh:
            old = json.load(fh)
        if time.time() - old.get("started", 0) < FRESH_S and not old.get("unmeasured"):
            rec = old
            print("scene record reused: %s" % RECORD)
    if rec is None:
        try:
            rec = _scene()
        except Exception as ex:   # no bridge, no game
            print("UNMEASURED: %r" % (ex,))
            return 2
        with open(RECORD, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, indent=1)
    if rec.get("unmeasured"):
        print("UNMEASURED: " + rec["unmeasured"])
        return 2
    ok, why = judge(rec)[clause]
    print("%s %s: %s" % ("PASS" if ok else "FAIL", clause, why))
    return 0 if ok else 1


def main(argv):
    if "--offline" in argv:
        return offline()
    if "--clause" in argv and argv[argv.index("--clause") + 1] in CLAUSES:
        return live(argv[argv.index("--clause") + 1])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
