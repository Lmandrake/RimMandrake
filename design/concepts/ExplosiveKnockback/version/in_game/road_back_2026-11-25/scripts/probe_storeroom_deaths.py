"""probe_storeroom_deaths.py - class step for RIMMANDRAKE_CLASS_KNOCKBACK_SHELL_KILLS_COLONIST_TWO_OF_FIVE_RUNS (EXPLORED).

Question: in scene_storeroom_pit (25 Shell_HighExplosive set off by damage among five drafted colonists in flak), 2 of 7
runs on ArchBig (2026-11-25 05:14 and 05:29 PST) read a colonist dead 3 and 6 ticks after the blast. Is the killer the
vanilla blast (Bomb 50 on every cell of the ring: the staged scene is wrong to claim "kills nobody"), or our mod (the impact
hit at launch, or the 0.2.0 collision bruise that a colonist thrown into another colonist now gives both)?
What the answer changes: deaths with knockback OFF, or with impact damage off, are the vanilla blast's: the scene's staging
is wrong. Deaths only with our damage on point at the mod.

Arms, each N runs from the same fixture save, in this order: real (the settings as they are), impact_off
(impactDamageEnabled False: our Blunt hits are 0, the throw stays), knock_off (enabled False: vanilla only).
Each run: the scene's own staging; damage the bomb; 300 ticks; then for each of the five colonists: Dead, Downed, and the
dead one's corpse hediffs (def, part, severity; a missing part's last injury) read from the corpse in the site; and the
journal's launch / bruise / blocked lines that name a colonist (their impact amounts).

    python.exe design\\concepts\\ExplosiveKnockback\\version\\in_game\\road_back_2026-11-25\\scripts\\probe_storeroom_deaths.py [N] [ARMS] [GAME]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
import scene  # noqa: E402
from scene import cond as c  # noqa: E402

N = int(sys.argv[1]) if len(sys.argv) > 1 else 4
ARMS = sys.argv[2].split(",") if len(sys.argv) > 2 else ["real", "impact_off", "knock_off"]
GAME = sys.argv[3] if len(sys.argv) > 3 else "ArchSmall"
SAVE = "EK_SITTING_STATION1_STOREROOM_PIT_20261112"
SITE = (114, 117, 22, 15)
RADIUS, PEOPLE, GOODS, TICKS = 6.0, 5, 6, 300
SETTINGS = "RimMandrake.ExplosiveKnockback.RimMandrakeExplosiveKnockbackSettings"
JOURNAL = "RimMandrake.ExplosiveKnockback.RM_KnockbackJournal"
OUT = os.path.join(HERE, "..", "probe_storeroom_deaths.jsonl")

probe = scene.contract(
    claim="the storeroom-pit blast: which colonists die, and of what", kind="C",
    exposure=c.state("bomb", "positionInt") == "gone",
    success=[c.played(TICKS)], forbidden=[], end=TICKS, limit=TICKS + 100)


def far(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def cell(v):
    x, *_y, z = (int(n) for n in str(v).split(","))
    return x, z


def put(s, field, value):
    r = s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=field, value=value, driver=s.id) or {}
    if r.get("success") is not True or str(r.get("valueAfter")) != str(value):
        raise RuntimeError("SETTING_REFUSED %s=%s: %s" % (field, value, r))


def get(s, field):
    return (s.raw("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=field) or {}).get("value")


def hediffs(s, of, prefix):
    n = s.read(of, prefix + "health.hediffSet.hediffs._size")
    if n.state != "ok":
        return "unread: %s %s" % (n.state, n.detail)
    reads = []
    for i in range(int(n.v)):
        h = prefix + "health.hediffSet.hediffs[%d]." % i
        reads += [(of, h + "def.defName"), (of, h + "Part.def.defName"), (of, h + "severityInt"), (of, h + "lastInjury.defName")]
    vals = s.read_many(reads=reads) if reads else []
    out = []
    for i in range(0, len(vals), 4):
        out.append([vals[i + k].v if vals[i + k].state == "ok" else None for k in range(4)])
    return out


def one_run(arm, i):
    with scene.open(GAME, contract=probe, needs={"mods": ["ExplosiveKnockback", "FlowWorks"], "map": SAVE, "calm": "standard"}) as s:
        kinds = {v.of: v.v for v in s.read_many(rect=SITE, path="def.category") if v.state == "ok"}
        defs = {v.of: v.v for v in s.read_many(rect=SITE, path="def.defName") if v.state == "ok"}
        cells = {v.of: cell(v.v) for v in s.read_many(rect=SITE, path="positionInt") if v.state == "ok"}
        shells = sorted(t for t, d in defs.items() if str(d).startswith("Shell_"))
        bx, bz = cells[shells[0]]
        near = sorted((t for t in cells if t != shells[0] and far(cells[t], (bx, bz)) <= RADIUS), key=lambda t: far(cells[t], (bx, bz)))
        people = [t for t in near if kinds.get(t) == "Pawn" and defs.get(t) == "Human"][:PEOPLE]
        goods = [t for t in near if kinds.get(t) == "Item" and t not in shells][:GOODS]
        s.stage(cast={"bomb": dict(take=shells[0][6:]), "people": dict(take=[p[6:] for p in people]),
                      "goods": dict(take=[g[6:] for g in goods])})
        ids = {}
        for k in range(PEOPLE):
            n = s.read("people[%d]" % k, "thingIDNumber")
            ids[k] = int(float(n.v)) if n.state == "ok" else None
        jv = s.read("static:" + JOURNAL, "lines")
        mark = len(jv.v) if jv.state == "ok" and isinstance(jv.v, (list, tuple)) else 0
        fields = {"real": [], "impact_off": [("impactDamageEnabled", "False")], "knock_off": [("enabled", "False")]}[arm]
        prior = {f: get(s, f) for f, _ in fields}
        try:
            for f, v in fields:
                put(s, f, v)
            hp = s.read("bomb", "hitPointsInt")
            s.act.damage("bomb", (hp.v if hp.state == "ok" else 60) + 40, kind="Crush", name="bomb")
            s.run(until=probe.end, limit=probe.limit)
            row = {"arm": arm, "i": i, "people": {}}
            for k in range(PEOPLE):
                a = "people[%d]" % k
                d, dn, pos = s.read(a, "Dead"), s.read(a, "Downed"), s.read(a, "positionInt")
                row["people"][k] = {"id": ids[k], "dead": d.v if d.state == "ok" else d.state, "downed": dn.v if dn.state == "ok" else dn.state,
                                    "pos": pos.v if pos.state == "ok" else "%s %s" % (pos.state, pos.detail)}
            corpses = {}
            cdefs = {v.of: v.v for v in s.read_many(rect=SITE, path="def.defName") if v.state == "ok"}
            for of, dn in cdefs.items():
                if str(dn).startswith("Corpse_Human"):
                    IP = "innerContainer.innerList[0]."      # Corpse.InnerPawn is a property the reader refuses; the field holds it
                    try:
                        inner = s.read(of, IP + "thingIDNumber")
                        corpses[of] = {"inner": int(float(inner.v)) if inner.state == "ok" else "%s %s" % (inner.state, inner.detail),
                                       "hediffs": hediffs(s, of, IP)}
                    except scene.Refused as e:
                        corpses[of] = {"inner": "unread: %s" % e}
            row["corpses"] = corpses
            for k in range(PEOPLE):
                if row["people"][k]["dead"] not in (True, "True"):
                    row["people"][k]["hediffs"] = hediffs(s, "people[%d]" % k, "")
            jv = s.read("static:" + JOURNAL, "lines")
            lines = list(jv.v)[mark:] if jv.state == "ok" and isinstance(jv.v, (list, tuple)) else []
            want = set(str(x) for x in ids.values() if x is not None)
            recs = []
            for ln in lines:
                try:
                    r = json.loads(str(ln))
                except ValueError:
                    continue
                if str(r.get("thingId")) in want or str(r.get("otherId")) in want or str(r.get("pawnId")) in want:
                    if r.get("type") in ("launch", "bruise", "blocked", "land_on_pawn", "land", "redirect"):
                        recs.append({k: r.get(k) for k in ("type", "tick", "thingId", "cells", "stop", "impact", "otherImpact", "amount",
                                                           "otherAmount", "otherId", "hitOther", "pawnId")})
            row["journal"] = recs
        finally:
            for f, v in prior.items():
                if v is not None:
                    try:
                        put(s, f, str(v))
                    except RuntimeError as e:
                        print("WARN restore", e)
    deaths = [k for k, p in row["people"].items() if p["dead"] in (True, "True")]
    row["deaths"] = deaths
    with open(OUT, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, default=str) + "\n")
    print("%s run %d: deaths %s; corpses %s" % (arm, i, deaths, json.dumps(row["corpses"], default=str)[:900]))
    return row


tally = {}
for arm in ARMS:
    for i in range(N):
        try:
            r = one_run(arm, i)
            tally.setdefault(arm, []).append(len(r["deaths"]))
        except Exception as e:  # noqa: BLE001 - a probe: say what stopped the run, keep the others
            print("%s run %d: COULD NOT LOOK %s: %s" % (arm, i, type(e).__name__, e))
            tally.setdefault(arm, []).append(None)
print("TALLY", json.dumps(tally))
