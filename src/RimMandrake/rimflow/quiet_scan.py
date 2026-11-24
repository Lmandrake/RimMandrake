#!/usr/bin/env python3
"""quiet_scan.py: the standing scan of quiet files. No model, no tokens of its own.

Item RIMMANDRAKE_BUILD_STANDING_SCAN_OF_QUIET_FILES_ON_SONNET, the owner's card of 2026-11-19 5:54 PM PST
(standing_rulings.md §Code is clean when its promises are tested). Page design/specs/2026-11-24-quiet-scan/boundary.md;
selftest selftest_quiet_scan.py; acceptance acceptance/quiet_scan_running_accept.py; brief roles/quiet_scan.md.

    python3 src/RimMandrake/rimflow/quiet_scan.py tick [--apply] [--hand "<why>"]   one pass; acts only with --apply.
                                        --hand (the Conductor's, or a proof): one file now, beside a live mod step
    python3 src/RimMandrake/rimflow/quiet_scan.py status                 the last reading and the counts
    python3 src/RimMandrake/rimflow/quiet_scan.py candidates [-n N]      the next files, in order
    python3 src/RimMandrake/rimflow/quiet_scan.py clear --why "..."      lift a stop
  the scan run's own two:
    python3 src/RimMandrake/rimflow/quiet_scan.py next                   prints `READ <path>`, `YIELD <why>` or `DONE <why>`
    python3 src/RimMandrake/rimflow/quiet_scan.py end <path> --outcome clean|flagged|noted [--reason "..."]

One decision per tick: disabled | off | pipeline_paused | stopped | live (a scan run is live) | blind (could not look) |
yields (a mod step is live or about to start) | system_wait | account_hold | pool_full | none_left | launch.
The tick runs on rm-quiet-scan.timer from the dispatch clone. State: <RM_DISPATCHER_STATE>/quiet_scan (RM_QUIET_SCAN_DIR
overrides): state.json, reading.json, ticks.jsonl, picks.jsonl, answers.jsonl, ends.jsonl.
"""
import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if _p not in sys.path:
        sys.path.append(_p)

FAMILY = "quiet_scan"
CFG_PATH = os.path.join(HERE, "quiet_scan.json")
CFG_REL = os.path.relpath(CFG_PATH, REPO)
ROLE = os.path.join(HERE, "roles", "quiet_scan.md")
# The closed item each scan run is launched on: a detached run needs one on the ledger, and a closed one asks no close of it.
RUN_ITEM = "RIMMANDRAKE_RESTART_QUIET_FILE_SCAN_3580_NEVER_READ"
EXTS = (".cs", ".xml", ".py")
# A mod decision under which a mod step is live, or starts as soon as it can (maturation_dispatch's decision words).
BUSY = ("live", "launch", "launched", "launch_wait", "launch_retry", "slots_full", "ready", "repairing", "settling")
# A test program inside a mod: the game never loads it, so it is not mod content.
MOD_TEST = re.compile(r"/[^/]*(SelfTest|Fuzz|Tests?)[^/]*(/|\.cs$)|/(selftest|northstar)")
OUTCOMES = ("clean", "flagged", "noted")
PAC = dt.timezone(dt.timedelta(hours=-8), "PST")
# Hang guards (the class of call_deadline_lint.py), far above a real run: the week's `git log` took 6 s (2026-11-24).
GIT_TIMEOUT_S = 300
LAUNCH_TIMEOUT_S = 10800  # budget: class=launch
REC = "infrastructure/state/code_review"


class Blind(Exception):
    """Could not look. Never "none"."""


def load_cfg(path=CFG_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def sdir(create=True):
    d = os.environ.get("RM_QUIET_SCAN_DIR")
    if not d:
        import doorbell
        d = os.path.join(doorbell.state_dir(), "quiet_scan")
    if create:
        os.makedirs(d, exist_ok=True)
    return d


def _state():
    """-> the state; {} when there is none yet. A state that exists and cannot be read raises."""
    p = os.path.join(sdir(create=False), "state.json")
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _write(name, obj):
    p = os.path.join(sdir(), name)
    with open(p + ".tmp", "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
    os.replace(p + ".tmp", p)


def _rows(name):
    """-> the rows of one book; [] when there is none yet. A row that cannot be parsed raises: a lost row is a repeat read."""
    p = os.path.join(sdir(create=False), name)
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _append(name, row):
    with open(os.path.join(sdir(), name), "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def picks():
    return _rows("picks.jsonl")


def ends():
    return _rows("ends.jsonl")


def answers():
    """Each YIELD or DONE that `next` gave a run: the proof that a run with no pick asked."""
    return _rows("answers.jsonl")


def pac(t):
    return dt.datetime.fromtimestamp(t, PAC).strftime("%Y-%m-%d %I:%M %p %Z").replace(" 0", " ")


def sha256(path):
    """-> the hex digest. A file that is absent or cannot be read raises Blind."""
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError as e:
        raise Blind("%s: %s" % (path, e))


def git(root, *args):
    try:
        r = subprocess.run(["git", "-C", root] + list(args), capture_output=True, text=True, errors="replace",
                           timeout=GIT_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise Blind("git %s: %s" % (args[0], e))
    if r.returncode:
        raise Blind("git %s exit %d: %s" % (args[0], r.returncode, " ".join((r.stderr or "").split())[:200]))
    return r.stdout


# ---- what is true now -----------------------------------------------------------------------------------------------

def changed_since(root, days, now):
    """-> the paths that a commit on origin/main touched in the last `days` days. A shallow clone's history ends early, so
    it is no answer: Blind."""
    if git(root, "rev-parse", "--is-shallow-repository").strip() != "false":
        raise Blind("%s is a shallow clone: its history cannot say what is quiet" % root)
    since = dt.datetime.fromtimestamp(now - days * 86400, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = git(root, "log", "--since-as-filter=" + since, "-m", "-z", "--name-only", "--format=", "origin/main")
    return set(p.strip("\n") for p in out.split("\0") if p.strip("\n"))


def last_commit(root, path):
    """-> the epoch of the last commit on origin/main that touched `path`."""
    out = git(root, "log", "-1", "--format=%ct", "origin/main", "--", ":(literal)" + path).strip()
    if not out:
        raise Blind("no commit on origin/main touches %s" % path)
    return int(out)


def landed_cfg(root):
    """The settings on origin/main: the run's own clone was taken before it started and misses a later `enabled: false`."""
    try:
        return json.loads(git(root, "show", "origin/main:" + CFG_REL))
    except ValueError as e:
        raise Blind("quiet_scan.json on origin/main: %s" % e)


def mod_dirs(root, tracked):
    """-> {src/<tier>/<Mod>: Mod} of the folders that hold About/About.xml."""
    out = {}
    for p in tracked:
        m = re.match(r"(src/[^/]+/([^/]+))/About/About\.xml$", p)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def _flags():
    import code_review_status as CRS
    return CRS.flags()


def _records():
    import code_review_status as CRS
    return CRS.load()


def _holds():
    import mod_owner_hold as MOH
    return dict((m, MOH.status(h)) for m, h in MOH.load().items())


def gather_files(root, days, now, readers=None):
    """-> the facts `candidates` orders. Raises Blind when any of them cannot be read."""
    got = {}
    for k, fn in (("flags", _flags), ("records", _records), ("holds", _holds)):
        try:
            got[k] = (readers or {}).get(k, fn)()
        except Exception as e:  # noqa: BLE001 - unreadable flags, records or holds are never "none"
            raise Blind("%s: %s: %s" % (k, type(e).__name__, e))
    tracked = [p for p in git(root, "ls-files", "-z", "--", "src").split("\0") if p.endswith(EXTS)]
    ended = {}
    for e in ends():
        ended.setdefault(e["path"], set()).add(e.get("sha256"))
    over = set((e["run"], e["path"]) for e in ends())
    tries = {}
    for p in picks():
        if (p["run"], p["path"]) not in over:       # picked and released: only a system death leaves that
            tries[p["path"]] = tries.get(p["path"], 0) + 1
    clean, done = set(), set()
    for p in tracked:
        ent = got["records"].get(p)
        if not (ent and ent.get("hash")) and p not in ended:
            continue
        h = sha256(os.path.join(root, p))
        if ent and ent.get("hash") == h and ent.get("status") != "dirty":
            clean.add(p)
        if h in ended.get(p, ()):
            done.add(p)
    return {"tracked": tracked, "mods": mod_dirs(root, tracked), "changed": changed_since(root, days, now), "clean": clean,
            "recorded": set(got["records"]), "flagged": set(got["flags"]), "ended": done, "held": got["holds"],
            "picked": tries}


def mod_of(path, mods):
    return mods.get("/".join(path.split("/")[:3]))


def candidates(f):
    """-> the files owed a read, in order: the mods' C#, the mods' XML, the rest (tools, test programs); in each, a file never read first. A file
    that a run picked and left unread (a system death) goes behind every file picked fewer times, so one file that kills
    its runs never holds the queue."""
    skip = f["changed"] | f["clean"] | f["flagged"] | f["ended"]
    out = []
    for p in f["tracked"]:
        mod = mod_of(p, f["mods"])
        if p in skip or (mod and mod in f["held"]):
            continue
        tier = 2 if not mod or p.endswith(".py") or MOD_TEST.search(p) else 0 if p.endswith(".cs") else 1
        out.append((f.get("picked", {}).get(p, 0), tier, p in f["recorded"], p))
    return [x[-1] for x in sorted(out)]


def mod_step(reading, live_records, now, max_age):
    """-> (why a mod step needs the machine or None, why it could not be read or None)."""
    for rec in live_records:
        mod = (rec.get("env") or {}).get("RM_CONTROL_MOD")
        if mod and mod != "none":
            return "%s: %s is live" % (mod, rec.get("unit")), None
    at = reading.get("at") if isinstance(reading, dict) else None
    mods = reading.get("mods") if isinstance(reading, dict) else None
    if not isinstance(at, (int, float)) or not isinstance(mods, dict):
        return None, "the mod pipeline's reading could not be read"
    if now - at > max_age:
        return None, "the mod pipeline's reading is %d s old" % (now - at)
    for mod, row in sorted(mods.items()):
        if row.get("decision") in BUSY or row.get("live"):
            return "%s: %s (%s)" % (mod, row.get("decision"), " ".join(str(row.get("why") or "").split())[:120]), None
    return None, None


def _live_records():
    import detached_helper as DH
    return [r for r in DH.all_records() if r.get("status") in ("launching", "running")
            and DH.live_status(r) in ("launching", "running")]


def _mod_reading():
    import doorbell
    d = os.environ.get("RM_MATURATION_DISPATCH_DIR") or os.path.join(doorbell.state_dir(), "maturation")
    with open(os.path.join(d, "reading.json"), encoding="utf-8") as f:
        return json.load(f)


def _run(unit):
    """-> {unit: {live, counts, result}} of the scan's run, or {} when its record cannot be seen."""
    import detached_helper as DH
    import failure_class as FC
    rec = DH.read_record(unit) if unit else None
    if not rec:
        return {}
    if DH.live_status(rec) in ("launching", "running"):
        return {unit: {"live": True}}
    fc = FC.of_run(rec)
    return {unit: {"live": False, "counts": fc.counts, "result": "%s (%s)" % (rec.get("result") or rec.get("status"), fc.word)}}


def gather(cfg, st, now, root=REPO):
    """-> the facts of one decision. What could not be looked at is `blind`, named."""
    f = {"files": None, "busy": None, "off": None, "paused": None, "pool": None, "runs": {}, "blind": None}
    blind = []
    try:
        import control as C
        for fam in (FAMILY, "detached"):
            f["off"] = f["off"] or C.blocked({"family": fam, "item": RUN_ITEM, "mod": None})
    except Exception as e:  # noqa: BLE001
        blind.append("the control store: %s: %s" % (type(e).__name__, e))
    try:
        import pipeline_pause as PP
        f["paused"] = PP.blocks(None, now)
    except Exception as e:  # noqa: BLE001
        blind.append("the pause store: %s: %s" % (type(e).__name__, e))
    try:
        f["runs"] = _run((st.get("run") or {}).get("unit"))
        f["busy"], why = mod_step(_mod_reading(), _live_records(), now, cfg["reading_max_age_s"])
        if why:
            blind.append(why)
    except Exception as e:  # noqa: BLE001
        blind.append("the mod pipeline's reading: %s: %s" % (type(e).__name__, e))
    try:
        import detached_helper as DH
        import scratch_clone as SC
        dest = SC.pool_root() / (RUN_ITEM + ".det")
        f["pool"] = None if os.path.isdir(os.path.join(DH.pool_root(), "clones", RUN_ITEM + ".det")) else SC.pool_admit(dest)
    except Exception as e:  # noqa: BLE001
        blind.append("the clone pool: %s: %s" % (type(e).__name__, e))
    try:
        git(root, "fetch", "-q", "origin", "main")
        f["files"] = gather_files(root, cfg["quiet_days"], now)
    except Blind as e:
        blind.append(str(e))
    f["blind"] = "; ".join(blind) or None
    return f


def account_gate():
    import list_dispatch as LD
    return LD.account_gate()


# ---- the decision ---------------------------------------------------------------------------------------------------

def decide(cfg, st, facts, now, account=(True, ""), hand=None):
    """-> {decision, why, left?, next?, need?}. Pure."""
    def row(d, why, **kw):
        return dict({"decision": d, "why": why}, **kw)
    run = st.get("run")
    if not cfg.get("enabled"):
        return row("disabled", "quiet_scan.json has enabled: false")
    if facts["off"]:
        return row("off", facts["off"])
    if facts["paused"]:
        return row("pipeline_paused", facts["paused"])
    if st.get("stopped"):
        return row("stopped", st["stopped"], need=None if st.get("told") else (
            "the standing scan reads no more quiet files | not recovered: %s | smallest act: read that run's note on %s, fix "
            "the brief or the tool, then `quiet_scan.py clear --why ...`" % (st["stopped"], RUN_ITEM)))
    if run:
        r = (facts["runs"] or {}).get(run["unit"])
        if r is None:
            return row("blind", "the record of the scan run %s cannot be seen" % run["unit"])
        return row("live", "%s is live" % run["unit"])
    if facts["blind"]:
        return row("blind", facts["blind"])
    if facts["busy"] and not hand:
        return row("yields", "a mod step needs the machine: " + facts["busy"])
    if now < (st.get("wait_until") or 0):
        return row("system_wait", "the last run or launch did not count (%s); the next one from %s" % (
            st.get("wait_why"), pac(st["wait_until"])))
    left = candidates(facts["files"])
    if not left:
        return row("none_left", "no quiet file is owed a read", left=0)
    if not account[0]:
        return row("account_hold", account[1], left=len(left))
    if facts["pool"]:
        return row("pool_full", facts["pool"], left=len(left))
    return row("launch", "%d quiet files are owed a read; the first is %s" % (len(left), left[0]), left=len(left), next=left[0])


def next_word(cfg, st, facts, unit, mine, now):
    """-> ("READ", path) | ("YIELD", why) | ("DONE", why) for the scan run `unit` that has picked `mine`. Pure."""
    run = st.get("run") or {}
    if run.get("unit") != unit:
        return "YIELD", "%s is not the scan's live run (%s)" % (unit, run.get("unit") or "none")
    if not cfg.get("enabled"):
        return "YIELD", "quiet_scan.json has enabled: false"
    for k in ("off", "paused", "blind"):
        if facts[k]:
            return "YIELD", facts[k]
    if len(mine) >= (1 if run.get("hand") else cfg["files_per_run"]):
        return "DONE", "this run has read its %d" % len(mine)
    if facts["busy"] and not run.get("hand"):
        return "YIELD", "a mod step needs the machine: " + facts["busy"]
    left = [p for p in candidates(facts["files"]) if p not in mine]
    return ("READ", left[0]) if left else ("DONE", "no quiet file is owed a read")


# ---- the acts -------------------------------------------------------------------------------------------------------

def record_pick(unit, path, root, now):
    lc = last_commit(root, path)
    _append("picks.jsonl", {"at": now, "run": unit, "path": path, "last_commit": lc,
                            "sha256": sha256(os.path.join(root, path))})


def record_answer(unit, word, why, now):
    _append("answers.jsonl", {"at": now, "run": unit, "word": word, "why": why})


def look_at(root, path):
    """-> {record, flag, landed} of `path` in the review record of `root`. landed: the file's bytes and every record line
    that names it are on origin/main."""
    import code_review_status as CRS
    ent = CRS.load().get(path)
    state = CRS.clean_state(path, ent)[0]
    git(root, "fetch", "-q", "origin", "main")
    landed = True
    for d in (REC, REC + "/flags"):
        for n in sorted(os.listdir(os.path.join(root, d))):
            if not n.endswith(".jsonl"):
                continue
            with open(os.path.join(root, d, n), encoding="utf-8") as f:
                here = [x.rstrip("\n") for x in f if '"%s"' % path in x]
            if not here:
                continue
            try:
                there = set(git(root, "show", "origin/main:%s/%s" % (d, n)).split("\n"))
            except Blind:       # a shard origin/main does not hold yet
                there = set()
            landed = landed and all(x in there for x in here)
    blob = git(root, "hash-object", "--", path).strip()
    landed = landed and blob == git(root, "rev-parse", "origin/main:" + path).strip()
    return {"record": state, "flag": path in CRS.flags(), "landed": landed}


def end(path, unit, outcome, reason, root, now, look=look_at):
    """-> (exit code, text). 2 refuses and names the repair; nothing is recorded then."""
    if outcome not in OUTCOMES:
        return 2, "refused: --outcome is one of %s" % ", ".join(OUTCOMES)
    if not any(p["run"] == unit and p["path"] == path for p in picks()):
        return 2, "refused: %s was not picked by %s; end only a path that `quiet_scan.py next` gave you" % (path, unit)
    if outcome == "noted" and not (reason or "").strip():
        return 2, "refused: a noted file carries --reason \"<why it ends with no clean mark and no flag>\""
    if outcome != "noted":
        st = look(root, path)
        if outcome == "clean" and st["record"] != "CLEAN":
            return 2, ("refused: the review record does not read %s CLEAN. Run `python3 src/RimMandrake/Utils/"
                       "code_review_status.py mark-clean %s`, then `end` again" % (path, path))
        if outcome == "flagged" and not st["flag"]:
            return 2, ("refused: %s is not FLAGGED. Run `python3 src/RimMandrake/Utils/code_review_status.py flag %s "
                       "--why \"<what the second read found and fixed>\"`, then `end` again" % (path, path))
        if not st["landed"]:
            return 2, ("refused: the file or its review record is not on origin/main yet. Run `./publish -m \"%s: <what>\" %s "
                       "infrastructure/state/code_review/<SEAT>.jsonl` (and flags/<SEAT>.jsonl for a flag), then `end` "
                       "again" % (RUN_ITEM, path))
    _append("ends.jsonl", {"at": now, "run": unit, "path": path, "outcome": outcome, "reason": reason or None,
                           "sha256": sha256(os.path.join(root, path))})
    return 0, "%s ends %s" % (path, outcome)


# budget: danger=a launch is sent again every tick into the same refusal (the night of 2026-11-20); ends no work: a wait before
# budget: the next try
def harvest(st, runs, now, wait_s=3600):
    """The scan run that ended: its files with no outcome are noted with its end, or released when its end does not count."""
    run = st.get("run")
    r = (runs or {}).get(run["unit"]) if run else None
    if not run or r is None or r.get("live"):
        return
    unit = run["unit"]
    mine = [p for p in picks() if p["run"] == unit]
    ended = set(e["path"] for e in ends() if e["run"] == unit)
    st["run"], st["last_run"] = None, {"unit": unit, "result": r.get("result"), "picked": len(mine), "ended": len(ended),
                                       "at": now}
    if not r.get("counts") and not str(r.get("result") or "").startswith("success"):
        st.update(wait_until=now + wait_s, wait_why="%s: %s" % (unit, r.get("result")))
        return
    for p in mine:
        if p["path"] not in ended:
            _append("ends.jsonl", {"at": now, "run": unit, "path": p["path"], "outcome": "noted", "by_program": True,
                                   "reason": "run %s ended (%s) with no outcome for this file" % (unit, r.get("result")),
                                   "sha256": p["sha256"]})
    if mine and not ended:
        st.update(stopped="run %s ended (%s) and gave no outcome for any of its %d files" % (
            unit, r.get("result"), len(mine)), told=None)
    elif not mine:
        said = [a for a in answers() if a["run"] == unit]
        if said:        # told to yield before its first file: the next launch waits, so a yield in its clone is no loop
            st.update(wait_until=now + wait_s, wait_why="%s was told %s: %s" % (unit, said[-1]["word"], said[-1]["why"]))
        else:
            st.update(stopped="run %s ended (%s) and never asked for a file" % (unit, r.get("result")), told=None)


def clear(st, why, now):
    st.update(stopped=None, told=None, cleared={"at": now, "why": why})


def say_need(d, st, now, need=None):
    """The stop, once, as a Needs Conductor line."""
    if not d.get("need"):
        return
    try:
        (need or conductor_need)(d["need"], now)
        st["told"] = now
    except Exception as e:  # noqa: BLE001 - the line stays owed and is said on the reading
        d["need_failed"] = "%s: %s" % (type(e).__name__, e)


def conductor_need(text, now, path=None):
    """One Needs Conductor line in the Conductor log (the guards red_dispatch.conductor_need uses)."""
    import detached_helper as DH
    import doorbell
    import conductor_log_guard
    path = path or DH.conductor_log_path()
    if (os.path.abspath(path) == os.path.abspath(DH.REAL_LOG)
            and os.environ.get("RM_DISPATCHER_STATE", doorbell.DEFAULT_STATE) != doorbell.DEFAULT_STATE):
        raise RuntimeError("refusing to write the REAL conductor log from a test process: " + path)
    conductor_log_guard.refuse_if_test(path)
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n%s — NEEDS CONDUCTOR (quiet_scan): %s\n" % (DH.iso(now), text))


def brief_text():
    with open(ROLE, encoding="utf-8") as f:
        return f.read()


def launch_argv(cfg, brief):
    return [sys.executable, os.path.join(HERE, "detached_helper.py"), "launch", "--seat", cfg["seat"], "--item", RUN_ITEM,
            "--brief-file", brief, "--model", "sonnet", "--budget-usd", "%g" % cfg["sonnet_cap_usd"],
            "--next-act-owner", FAMILY]


def launch(cfg):
    try:
        r = subprocess.run(launch_argv(cfg, ROLE), capture_output=True, text=True, timeout=LAUNCH_TIMEOUT_S,
                           stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired) as e:
        return 99, "%s: %s" % (type(e).__name__, e), None
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    m = re.search(r"^DETACHED (\S+)", r.stdout or "", re.M)
    return r.returncode, out, (m.group(1) if m and not r.returncode else None)


def tick(cfg, apply, fx=None, now=None, hand=None):
    fx = fx or {}
    now = time.time() if now is None else now
    lock = None
    if apply:
        lock = open(os.path.join(sdir(), "tick.lock"), "w")
        fcntl.flock(lock, fcntl.LOCK_EX)
    try:
        st = _state()
        facts = fx.get("facts", gather)(cfg, st, now)
        if apply:
            harvest(st, facts["runs"], now, cfg["system_wait_s"])
            _write("state.json", st)        # the harvest stands even if the launch below dies
        account = fx.get("account", account_gate)()
        d = decide(cfg, st, facts, now, account, hand)
        if not apply:
            if d["decision"] == "launch":
                d["decision"] = "would_launch"
            d.pop("need", None)
            return dict(d, at=now)
        say_need(d, st, now, fx.get("need"))
        if d["decision"] == "launch":
            rc, text, unit = fx.get("launch", launch)(cfg)
            if rc == 0 and unit:
                st["run"] = {"unit": unit, "at": now, "hand": hand}
                d.update(decision="launched", unit=unit)
            else:
                why = " ".join((text or "rc %s" % rc).split())[:400]
                st.update(wait_until=now + cfg["system_wait_s"], wait_why="never started: " + why)
                d.update(decision="launch_failed", why=why)
        rd = dict(d, schema=1, at=now, at_pac=pac(now), ended=len(ends()), last_run=st.get("last_run"))
        _write("state.json", st)
        _write("reading.json", rd)
        _append("ticks.jsonl", {"at": now, "decision": d["decision"], "unit": d.get("unit")})
        return rd
    finally:
        if lock:
            lock.close()


def main(argv=None):
    ap = argparse.ArgumentParser(description="the standing scan of quiet files")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("tick")
    a.add_argument("--apply", action="store_true")
    a.add_argument("--hand", metavar="WHY", help="one file now, beside a live mod step")
    sub.add_parser("status")
    a = sub.add_parser("candidates")
    a.add_argument("-n", type=int, default=10)
    a = sub.add_parser("clear")
    a.add_argument("--why", required=True)
    a = sub.add_parser("next")
    a.add_argument("--run", default=os.environ.get("RM_DETACHED_UNIT"))
    a = sub.add_parser("end")
    a.add_argument("path")
    a.add_argument("--run", default=os.environ.get("RM_DETACHED_UNIT"))
    a.add_argument("--outcome", required=True)
    a.add_argument("--reason")
    args = ap.parse_args(argv)
    cfg, now = load_cfg(), time.time()
    if args.cmd == "tick":
        d = tick(cfg, args.apply, hand=args.hand, now=now)
        print("%s: %s" % (d["decision"], d["why"]))
        return 0
    if args.cmd == "status":
        try:
            with open(os.path.join(sdir(create=False), "reading.json"), encoding="utf-8") as f:
                rd = json.load(f)
        except FileNotFoundError:
            print("UNMEASURED: no reading yet")
            return 3
        print("%s: %s (%s)" % (rd["decision"], rd["why"], rd["at_pac"]))
        count = {}
        for e in ends():
            count[e["outcome"]] = count.get(e["outcome"], 0) + 1
        print("ended: " + (", ".join("%d %s" % (n, k) for k, n in sorted(count.items())) or "0"))
        return 0
    if args.cmd == "candidates":
        try:
            left = candidates(gather_files(REPO, cfg["quiet_days"], now))
        except Blind as e:
            print("COULD NOT LOOK: %s" % e)
            return 3
        print("%d quiet files are owed a read" % len(left))
        print("\n".join(left[:args.n]))
        return 0
    if args.cmd == "clear":
        with open(os.path.join(sdir(), "tick.lock"), "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            st = _state()
            clear(st, args.why, now)
            _write("state.json", st)
        print("cleared")
        return 0
    if not args.run:
        print("refused: no run: `next` and `end` are the scan run's own (RM_DETACHED_UNIT, or --run <unit>)")
        return 2
    if args.cmd == "next":
        st = _state()
        mine = [p["path"] for p in picks() if p["run"] == args.run]
        open_ = [p for p in mine if p not in set(e["path"] for e in ends() if e["run"] == args.run)]
        if open_:
            print("READ %s" % open_[0])     # its last pick has no outcome yet: the same file, never a second one
            return 0
        try:
            facts = gather(cfg, st, now)        # fetches
            word, what = next_word(landed_cfg(REPO), st, facts, args.run, mine, now)
            if word == "READ":
                record_pick(args.run, what, REPO, now)
        except Blind as e:
            word, what = "YIELD", str(e)
        if word != "READ":
            record_answer(args.run, word, what, now)
        print("%s %s" % (word, what))
        return 0
    try:
        rc, said = end(args.path, args.run, args.outcome, args.reason, REPO, now)
    except Blind as e:
        rc, said = 3, "COULD NOT LOOK: %s; nothing recorded, run the same command again" % e
    print(said)
    return rc


if __name__ == "__main__":
    sys.exit(main())
