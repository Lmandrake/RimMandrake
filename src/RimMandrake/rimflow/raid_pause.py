#!/usr/bin/env python3
"""raid_pause.py -- raid tests are paused until the test tools can hold a raid still (owner, 2026-11-23,
design/RimMandrake/standing_rulings.md §The cheapest test that decides the bar). The switch is raid_pause.json beside this
file; the bridge client, the Stage 6 reader, modcheck and the test lane read it here. Page:
design/specs/2026-11-23-raid-tests-paused/boundary.md. Tests: selftest_raid_pause.py.

    raid_pause.py show | census | lift --why "..." | pause --why "..." | allow ITEM --why "..." | disallow ITEM --why "..."
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SWITCH = os.path.join(HERE, "raid_pause.json")
WORD = "PAUSED: raid tests wait for the tools"
STANDS = "PASS stands"
FOR_ENV = "RM_RAID_FOR"      # the item whose work builds the raid tools; from WSL to python.exe pass it with WSLENV=RM_RAID_FOR
TAG = "stages_raid"
RULE = ("- The cheapest test that decides the bar is the test (owner, 2026-11-23; standing_rulings.md §The cheapest test that decides "
        "the bar). A dearer check or scene says in `cheaper_why` (its test-table entry) why a cheaper, faster, simpler test cannot "
        "decide the same bar. Write no scene that stages a raid (hostile pawns that attack by their own will) unless the mod's own "
        "function is about raiders; tag one that must with `stages_raid`. Raid tests are paused: nothing starts them, they hold "
        "no exit, and their bars stay open on the record.")
RAID_INCIDENT = re.compile(r"raid|siege|mechcluster", re.I)
RAID_JOB = re.compile(r"assault|siege|breach|sapper|stageThenAttack|kidnap", re.I)
DRY_BY_DEFAULT = {"jawa/fire_raid": True, "jawa/raid_shape_fire": True, "jawa/storyteller_fire": True,
                  "jawa/fire_incident": False}
ALWAYS = ("jawa/spawn_mech_cluster", "jawa/lord_assault_spawn")
NAMES = re.compile(r"jawa/(fire_raid|raid_shape_fire|lord_assault_spawn|spawn_mech_cluster)\b")


def switch(path=None):
    """-> {paused, why, allow, chains, unreadable}. A switch that cannot be read is a pause (unreadable says why)."""
    p = path or SWITCH
    try:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        if not isinstance(d, dict) or not isinstance(d.get("paused"), bool):
            raise ValueError("no true or false `paused`")
    except (OSError, ValueError) as e:
        return {"paused": True, "why": "the switch cannot be read", "allow": [], "chains": {},
                "unreadable": "%s: %s: %s" % (p, type(e).__name__, e)}
    allow, chains = d.get("allow"), d.get("chains")
    return {"paused": d["paused"], "why": str(d.get("why") or ""), "allow": allow if isinstance(allow, list) else [],
            "chains": chains if isinstance(chains, dict) else {}, "unreadable": None}


def paused(path=None):
    return switch(path)["paused"]


def _true(v):
    return v is True or str(v).strip().lower() in ("true", "1", "yes")


def raid_call(tool, params=None):
    """-> what this bridge call would stage, or None when it stages no raid."""
    p = params if isinstance(params, dict) else {}
    t = str(tool or "")
    if t in ALWAYS:
        return "%s: %s" % (t, "pawns under an assault lord" if "lord" in t else "a mech cluster")
    if t in DRY_BY_DEFAULT:
        dry = _true(p["dryRun"]) if "dryRun" in p else DRY_BY_DEFAULT[t]
        if dry:
            return None
        if t in ("jawa/fire_raid", "jawa/raid_shape_fire"):
            return "%s: a raid" % t
    if t in ("jawa/fire_incident", "jawa/storyteller_fire", "jawa/incident_schedule"):
        inc = str(p.get("incidentDef") or "")
        if RAID_INCIDENT.search(inc):
            return "%s: the incident %s" % (t, inc)
        if not inc and re.search(r"threat", str(p.get("category") or ""), re.I):
            return "%s: an incident of category %s" % (t, p.get("category"))
        return None
    if t == "jawa/lord_set_job" and RAID_JOB.search(str(p.get("lordJob") or "")):
        return "%s: %s" % (t, p.get("lordJob"))
    if "debug_action" in t and RAID_INCIDENT.search(json.dumps(p, default=str)):
        return "%s: a debug action that names a raid" % t
    if re.search(r"batch|sequence|run_until", t):
        m = NAMES.search(json.dumps(p, default=str))
        if m:
            return "%s carries %s" % (t, m.group(0))
    return None


def refuse_call(tool, params=None, path=None, env=None):
    """-> the refusal text of a raid call while the pause is on, or None."""
    what = raid_call(tool, params)
    if what is None:
        return None
    s = switch(path)
    if not s["paused"]:
        return None
    item = ((env if env is not None else os.environ).get(FOR_ENV) or "").strip()
    if item and item in s["allow"]:
        return None
    return ("%s. Refused: %s%s. No raid in a test: use the cheaper test of the bar (standing_rulings.md §The cheapest test "
            "that decides the bar), tag a scene that needs raiders `%s` in its test table, and record no verdict for this "
            "run. The work that builds the raid tools sets %s to its item (`raid_pause.py allow ITEM`)%s" % (
                WORD, what, "; %s=%s is not in the switch's allow list" % (FOR_ENV, item) if item else "", TAG, FOR_ENV,
                "; %s" % s["unreadable"] if s["unreadable"] else ""))


def stages(spec):
    """-> what this test of a table stages, or None."""
    v = (spec or {}).get(TAG) if isinstance(spec, dict) else None
    v = str(v).strip() if v not in (None, False, "", [], {}) else ""
    return v or None


def chain_paused(mod, chain, path=None):
    """-> what this modcheck chain stages while the pause is on, or None."""
    s = switch(path)
    return (s["chains"].get(mod) or {}).get(chain) if s["paused"] else None


# ---- the Stage 6 reading of the raid scenes --------------------------------------------------------------------------

def scenes(tt):
    """-> [(id, spec)]: the table's stage-6 in-game raid scenes, the pause on or off."""
    return [(k, t) for k, t in ((tt or {}).get("tests") or {}).items()
            if isinstance(t, dict) and str(t.get("kind", "")).startswith("live") and str(t.get("stage")) == "6" and stages(t)]


def read_scenes(root, mod, n, tt, path=None):
    """-> {id: {read, why, bars, last, open}}: what each raid scene reads after visit n. `read` is STANDS, or WORD while the
    pause is on, or None (the pause is off and no pass stands: the exit reads the scene)."""
    sc = scenes(tt)
    if not sc:
        return {}
    import build_match as BM
    import live_kinds as LK
    on, out, rel, runs, last, bad = paused(path), {}, {}, {}, {}, None
    try:
        last, runs = BM.carried_rows(root, mod, n), BM.check_runs(root, mod, n)
        rel = BM.RR.relate(root, mod, dict(sc), {t: r for t, r in last.items() if t in dict(sc)})["rows"]
    except Exception as e:      # noqa: BLE001  unread relates nothing: no pass stands, and the cause is named
        bad = "%s: %s" % (type(e).__name__, e)
    for t, spec in sc:
        r = last.get(t)
        k = LK.reading(spec, runs.get(t)) if r else None
        v = None if r is None else str(r.get("verdict")).upper()
        if bad:
            why = "its rows or the change relation could not be read (%s)" % bad
        elif r is None:
            why = "it has no row"
        elif v != "PASS" or (k is not None and not (k["passes"] and k["count"] in (None, "pass"))):
            why = "its last row reads %s%s" % (v, "; " + "; ".join(k["why"]) if k and k["why"] else "")
        elif "mod_fix" not in r and ((k is not None and k["mod"]) or any(
                LK.norm(old.get("verdict")) == "FAIL" and LK.norm(old.get("class")) == "MOD"
                and LK.same_build(old, r) and LK.outcome(old, spec)[0] is None and not LK.spoiled(old)
                for _, old in runs.get(t, ()))):
            why = "an earlier run on that build is a MOD FAILURE"
        elif (rel.get(t) or {}).get("state") != "untouched":
            why = "the change since its PASS touches what it reads (%s)" % ((rel.get(t) or {}).get("why") or "not read")
        else:
            why = None
        out[t] = {"read": STANDS if why is None else WORD if on else None, "why": why, "stages": stages(spec), "open": why is not None,
                  "bars": [b.get("id") for b in (tt or {}).get("bars") or [] if isinstance(b, dict) and t in (b.get("decides") or [])],
                  "last": None if r is None else {"verdict": v, "visit": r.get("_visit"), "mod_sha": r.get("mod_sha")}}
    return out


def open_bars(readings):
    """-> {bar: [scene]}: the bars that a raid scene with no standing pass decides."""
    out = {}
    for t, x in (readings or {}).items():
        for b in x["bars"] if x["open"] else ():
            out.setdefault(b, []).append(t)
    return out


def said(readings):
    """-> one line for a page or a reason: the paused scenes and their open bars, or ''."""
    p = sorted(t for t, x in (readings or {}).items() if x["read"] == WORD)
    return "%s: %s; open bars: %s" % (WORD, ", ".join(p), ", ".join(sorted(open_bars(readings))) or "none") if p else ""


# ---- the census ------------------------------------------------------------------------------------------------------

def census(root=REPO):
    """-> (tagged [(mod, test, stages, bars, last verdict)], scripts {path: [line numbers]}, unread [path])."""
    import glob
    tagged, scripts, unread = [], {}, []
    for p in sorted(glob.glob(os.path.join(root, "design", "concepts", "*", "version", "test_table.json"))):
        mod = p.split(os.sep)[-3]
        try:
            with open(p, encoding="utf-8") as f:
                tt = json.load(f)
        except (OSError, ValueError):
            unread.append(p)
            continue
        for t, spec in scenes(tt):
            last = None
            for q in sorted(glob.glob(os.path.join(os.path.dirname(p), "in_game", "visit_*", "rows.jsonl")),
                            key=lambda x: int(re.search(r"visit_(\d+)", x).group(1))):
                try:
                    with open(q, encoding="utf-8") as f:
                        for ln in f:
                            r = json.loads(ln) if ln.strip() else {}
                            if r.get("test") == t:
                                last = "%s (visit %s)" % (r.get("verdict"), re.search(r"visit_(\d+)", q).group(1))
                except (OSError, ValueError):
                    unread.append(q)
            tagged.append((mod, t, stages(spec), [b.get("id") for b in tt.get("bars") or [] if t in (b.get("decides") or [])], last))
    call = re.compile(r"jawa/(fire_raid|raid_shape_fire|lord_assault_spawn|spawn_mech_cluster)\b|incidentDef\s*=\s*[\"']\w*Raid\w*[\"']")
    for base, _, names in os.walk(os.path.join(root, "src")):
        for n in names:
            if not n.endswith(".py") or n.startswith("selftest") or n in ("raid_pause.py", "rimbridge_client.py"):
                continue
            q = os.path.join(base, n)
            try:
                with open(q, encoding="utf-8", errors="replace") as f:
                    hit = [i for i, ln in enumerate(f, 1) if call.search(ln)]
            except OSError:
                unread.append(q)
                continue
            if hit:
                scripts[os.path.relpath(q, root)] = hit
    return tagged, scripts, unread


# ---- the commands ----------------------------------------------------------------------------------------------------

def main(argv=None, root=REPO, runner=subprocess.run, env=None, path=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show")
    sub.add_parser("census")
    for c in ("lift", "pause", "allow", "disallow"):
        x = sub.add_parser(c)
        if c in ("allow", "disallow"):
            x.add_argument("item")
        x.add_argument("--why", required=True)
    a = ap.parse_args(argv)
    p = path or SWITCH
    if a.cmd == "show":
        s = switch(p)
        print("%s%s; allowed: %s; %s" % ("PAUSED" if s["paused"] else "LIFTED", " (%s)" % s["unreadable"] if s["unreadable"] else "",
                                         ", ".join(s["allow"]) or "none", s["why"]))
        return 0
    if a.cmd == "census":
        tagged, scripts, unread = census(root)
        for m, t, what, bars, last in tagged:
            print("%s %s | %s | bars %s | last %s" % (m, t, what, ", ".join(bars) or "none", last or "no row"))
        for q, ln in sorted(scripts.items()):
            print("%s:%s" % (q, ",".join(str(i) for i in ln[:8])))
        for q in unread:
            print("UNREAD %s" % q)
        return 3 if unread else 0
    e = env if env is not None else os.environ
    if e.get("RM_ROLE_UNIT"):
        print("REFUSED: the switch is the Conductor's act (or his); a role run does not move it. Nothing was written")
        return 2
    if not a.why.strip():
        print("REFUSED: --why is empty; nothing was written")
        return 2
    try:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        assert isinstance(d, dict)
    except (OSError, ValueError, AssertionError):
        d = {"allow": [], "chains": {}}
    if a.cmd in ("lift", "pause"):
        d["paused"], d["why"] = a.cmd == "pause", a.why.strip()
    else:
        d.setdefault("paused", True)
        have = [i for i in d.get("allow") or [] if i != a.item]
        d["allow"] = have + [a.item] if a.cmd == "allow" else have
        d["allow_why"] = dict(d.get("allow_why") or {}, **{a.item: "%s: %s" % (a.cmd, a.why.strip())})
    with open(p + ".tmp", "w", encoding="utf-8") as f:
        f.write(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
    os.replace(p + ".tmp", p)
    r = runner([os.path.join(root, "publish"), "-m", "raid tests: %s%s" % (a.cmd, " " + a.item if hasattr(a, "item") else ""),
                os.path.relpath(p, root)], cwd=root, capture_output=True, text=True)
    out = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()[-1:]
    print("%s written; %s" % (a.cmd, "".join(out)))
    return 0 if r.returncode == 0 else 4


if __name__ == "__main__":
    sys.exit(main())
