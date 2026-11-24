#!/usr/bin/env python3
"""host_facts.py - what SteveDesktop's games have, read by program each half hour, kept with its age
(page design/specs/2026-11-24-ask-lane-after-host-facts/boundary.md; tests selftest_ask_lane.py; rm-host-facts.timer).

  read(path, now) -> {"age_s", "stale", "facts"}   no file, unreadable file, or older than MAX_AGE_S: stale, never facts
  lacks(need, facts, stale) -> [(kind, name, word)]  "absent" (looked, not there) or "could not look" (stale, or that part unread)
  need_of(mod, tier) -> what a lane job of MOD on TIER (None: the minimal list) asks of the host
  unmet(mod, tier) -> "kind name is absent; ..." for that job at the kept facts, or None
  collect(run) -> facts                              `run(cmd) -> stdout`; raises when the host cannot be read (nothing is written)
  logins_low(facts, days=3) -> [account]             logins with under `days` left (login_watch.py raises the alarm, not this)
CLI: host_facts.py refresh | show   (exit 0 read, 4 could not look)

It read C:\\ Steam and sjlewis's python through cmd.exe until 2026-11-24, and wrote 18 mods of an install that no lane
game uses: every tier mod would have read absent. The games are on D: (testcentre_env.sh), and WSL is the door.
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
# budget: danger=old facts of a host read as current; ends no work: the facts are read again
MAX_AGE_S = 2 * 3600
KINDS = ("mods", "saves", "python", "companion")
PART = {"companion": "companions"}      # the facts key of a kind that is not its own name
PYTHON = ("numpy", "lxml", "PIL")       # Windows python: each was missing once and its jobs measured nothing (RUNBOOK)

# Runs in SteveDesktop's WSL, whose ~/.bashrc sources testcentre_env.sh. A part that cannot be read is null, never empty.
PROBE = r"""
import glob, json, os, shutil, subprocess, xml.etree.ElementTree as ET
out = {"games": {}, "unread": []}
steam = os.environ["RM_STEAMAPPS"] + "/common/RimWorld"
b = os.environ["RM_INSTANCES_ROOT"] + "/b"
def ids(dirs):
    got = set()
    for d in dirs:
        for p in glob.glob(d + "/*/About/About.xml"):
            try:
                t = [e.text for e in ET.parse(p).getroot() if e.tag.lower() == "packageid"]
                got.add(t[0].strip().lower())
            except Exception as e:
                out["unread"].append("%s (%s)" % (p, type(e).__name__))
    return sorted(got)
for name, root, data, extra in (
        ("Steve1", steam, os.environ["RM_GAME_USERDATA"], [os.environ["RM_STEAMAPPS"] + "/workshop/content/294100"]),
        ("Steve2", b + "/game", b, [])):
    try:
        os.listdir(root + "/Mods")
        out["games"][name] = {"mods": ids([root + "/Mods", root + "/Data"] + extra),
                              "saves": sorted(f[:-4] for f in os.listdir(data + "/Saves") if f.endswith(".rws"))}
    except OSError as e:
        out["games"][name] = None
        out["unread"].append("%s: %s" % (name, e))
try:
    code = "import importlib.util as u,json;print(json.dumps({m: u.find_spec(m) is not None for m in %r}))" % (PYTHON,)
    r = subprocess.run(["python.exe", "-c", code], capture_output=True, text=True, timeout=60)
    out["python"] = json.loads(r.stdout.strip().splitlines()[-1])
except Exception as e:
    out["python"] = None
    out["unread"].append("Windows python: %s" % e)
try:
    out["free_gb"] = min(shutil.disk_usage(p).free // 2**30 for p in ("/", "/mnt/d"))
except OSError as e:
    out["free_gb"] = None
    out["unread"].append("disk: %s" % e)
print(json.dumps(out))
"""


def path_now():
    return os.path.join(os.environ.get("TESTQ_QUEUE", "/mnt/d/ClaudeWork/rimmandrake/testq"), "host_facts.json")


def read(path=None, now=None):
    now = time.time() if now is None else now
    try:
        with open(path or path_now(), encoding="utf-8") as f:
            d = json.load(f)
        at, facts = float(d["at"]), d["facts"]
    except (OSError, ValueError, KeyError, TypeError):
        return {"age_s": None, "stale": True, "facts": None}
    age = now - at
    stale = age > MAX_AGE_S or age < 0
    return {"age_s": age, "stale": stale, "facts": None if stale else facts}


def lacks(need, facts, stale):
    out = []
    for kind in KINDS:
        want = need.get(kind)
        if not want:
            continue
        want = [want] if isinstance(want, str) else list(want)
        have = facts.get(PART.get(kind, kind)) if isinstance(facts, dict) else None
        for name in want:
            if stale or have is None:
                out.append((kind, name, "could not look"))
                continue
            if not (have.get(name) is True if kind == "python" else name in have):
                out.append((kind, name, "could not look" if kind in (facts.get("partial") or ()) else "absent"))
    return out


def need_of(mod, tier=None, repo=None):
    """-> {"mods", "saves", "python"}: the mods of TIER that are not ours (ours are deployed by the job) with the lists'
    own three, the mod's registered site save, and the packages the live proofs import. ValueError: no such tier."""
    repo = repo or REPO
    utils = os.path.join(repo, "src", "RimMandrake", "Utils")
    for p in (utils, os.path.join(utils, "modcheck")):
        if p not in sys.path:
            sys.path.append(p)
    import modset_builder as MB
    import runner
    want = {MB.BRIDGE, MB.HARMONY, MB.CHERRY}
    if tier:
        td = MB.tier_def(tier, MB.scan() if MB.mods_tier_tokens(tier) else None)    # a mods__ name decodes on what is installed
        if td is None:
            raise ValueError("tier %s is no modset_builder.py tier" % tier)
        want |= {p.lower() for p in td["want"]}
    ours = {p.lower() for p in runner.src_mods_by_id(repo)}
    with open(os.path.join(utils, "modcheck", "test_site_saves.json"), encoding="utf-8") as f:
        site = (json.load(f).get(str(mod).lower()) or {}).get("save")
    return {"mods": sorted(want - ours), "saves": [site] if site else [], "python": list(PYTHON)}


def unmet(mod, tier=None, kept=None, need=None):
    """Why a lane job of MOD on TIER may not be sent at the kept facts, or None."""
    kept = kept or read()
    try:
        need = need_of(mod, tier) if need is None else need
    except Exception as e:  # noqa: BLE001 - a need that cannot be read is not a need of nothing
        return "could not look: what %s needs cannot be read (%s: %s)" % (mod, type(e).__name__, e)
    gone = lacks(need, kept["facts"], kept["stale"])
    if not gone:
        return None
    if kept["stale"]:
        return "could not look: the host facts are %s" % (
            "missing or unreadable" if kept["age_s"] is None else "%d min old" % (kept["age_s"] / 60))
    return "; ".join("%s %s is %s" % g if g[2] == "absent" else "could not look: %s %s" % g[:2] for g in gone)


def logins_low(facts, days=3):
    return sorted(a for a, s in ((facts or {}).get("logins") or {}).items() if s is not None and s < days * 86400)


def collect(run):
    """The host's facts. A mod or save counts as there when one lane game has it; `games` says which."""
    d = json.loads(run("PYTHON = %r\n" % (PYTHON,) + PROBE).strip().splitlines()[-1])
    games = d["games"]
    seen = [g for g in games.values() if g]
    for kind in ("mods", "saves"):
        d[kind] = sorted({x for g in seen for x in g[kind]}) if seen else None
    d["partial"] = []                   # a name not seen in a part that was not read whole is not `absent`
    if len(seen) < len(games):
        d["partial"] = ["mods", "saves"]
    elif any("About.xml" in u for u in d["unread"]):
        d["partial"] = ["mods"]
    return d


def _ssh(code):
    argv = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", os.environ.get("STEVE_WSL", "mandrake@stevedesktop-wsl"), "python3 -"]
    # budget: danger=a hung ssh holds the host facts; never reached in the 14 days to 2026-11-24; no record of its run
    r = subprocess.run(argv, input=code, capture_output=True, text=True, timeout=180)
    if r.returncode:
        raise OSError(r.stderr.strip()[-200:] or "ssh exit %d" % r.returncode)
    return r.stdout


def _companions():
    import companion_stage as CS
    got = CS.probe()
    return None if got is None else sorted({h for h in got.values() if len(h) == 64})


def _logins(now):
    rf = os.path.join(HERE, "..", "..", "rimflow")
    if rf not in sys.path:
        sys.path.append(rf)
    import login_watch as LW
    r = LW.host_login_deadlines("stevedesktop")
    return None if r is None else {a: None if v["deadline"] is None else int(v["deadline"] - now)
                                   for a, v in r.items() if not a.startswith("_")}


def refresh(path=None, run=None, now=None, companions=None, logins=None):
    path = path or path_now()
    now = time.time() if now is None else now
    facts = collect(run or _ssh)
    for key, fn in (("companions", companions or _companions), ("logins", logins or (lambda: _logins(now)))):
        try:
            facts[key] = fn()
        except Exception as e:  # noqa: BLE001 - one unread part is null and named; the others stand
            facts[key] = None
            facts["unread"].append("%s: %s: %s" % (key, type(e).__name__, e))
    tmp = path + ".tmp"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"at": now, "facts": facts}, f)
    os.replace(tmp, path)
    return facts


def line(f):
    n = lambda x: "UNMEASURED" if x is None else str(len(x))
    games = ", ".join("%s %s" % (g, "UNMEASURED" if v is None else "%d mods %d saves" % (len(v["mods"]), len(v["saves"])))
                      for g, v in sorted((f.get("games") or {}).items()))
    return "%s; python %s; companions %s; free %s GB; logins %s; unread: %s" % (
        games, json.dumps(f.get("python")), n(f.get("companions")), f.get("free_gb"), json.dumps(f.get("logins")),
        "; ".join(f.get("unread") or []) or "none")


def main(argv=None):
    cmd = (sys.argv[1:] if argv is None else argv or ["show"])
    cmd = cmd[0] if cmd else "show"
    try:
        if cmd == "refresh":
            f = refresh()
        else:
            r = read()
            if r["facts"] is None or r["stale"]:
                print("COULD NOT LOOK: host facts %s" % ("missing or unreadable" if r["age_s"] is None else "stale (%d s old)" % r["age_s"]))
                return 4
            f = r["facts"]
    except (OSError, ValueError, KeyError, IndexError, subprocess.SubprocessError) as e:
        print("COULD NOT LOOK: %s: %s" % (type(e).__name__, e))
        return 4
    print(line(f))
    low = logins_low(f)
    if low:
        print("LOW: login of %s has under 3 days left (login_watch.py raises the alarm)" % ", ".join(low))
    return 0


if __name__ == "__main__":
    sys.exit(main())
