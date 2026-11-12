#!/usr/bin/env python3
"""Bookkeeping for the Claude Whittle loops (loop.sh): status page files, the shared claims table, and the shortlist a
round picks its one ticket from. Owner order 2026-11-11: two live FlowWorks loops (one per game) and offline loops on
Archmagi, one ticket at a time, never two loops on one item.

    wc.py status <WORKER> [--state S] [--item ID|-] [--round N] [--note TEXT] [--lane L --game G --unit U --machine M]
    wc.py log <WORKER> TEXT              one loop.log line, "YYYY-MM-DD HH:MM <text>" in local time (the contract)
    wc.py shortlist <WORKER> <fwlive|offline> [--n 12]
    wc.py claim <WORKER> <ID>            exit 3 when another loop holds it
    wc.py unclaim <WORKER> <ID>
    wc.py mine <WORKER>                  the ids the worker holds in the claims table, one per line
    wc.py lane-open <fwlive|offline>     count of open items the lane could take
    wc.py nonpass <ID>                   trailing run of non-pass results on the item
    wc.py tokens <claude json log>...    total tokens the logs report (input+output+cache), or 0
    wc.py diskfree                       free GB on the Windows drive that backs this WSL distro's ext4.vhdx; exit 4
                                         when under WC_MIN_FREE_GB (default 15): no new round, no new clone
    wc.py gate <WORKER> <LANE> <ID>...   PICK or SKIP with the reason, for each id (no model, no writes)
    wc.py setup <WORKER> <LANE> [--round N]   the whole SETUP phase without a model: release stale claims, take the
                                         first eligible item, claim it (table + ledger), write whittle/<dir>/, commit,
                                         publish. Last line PICKED <ID> <dir> whittle | NONE <reason>
    wc.py release <WORKER> <ID> --why T  give a claim back: ledger note + reassign to BENCH + unclaim, commit, publish
    wc.py wrapup <WORKER> <ID> --dir D --rc RC   the mechanical endings (ghost, closed already, BLOCKED, incomplete):
                                         last line RESULT ...; exit 5 = rc 0, a model must judge the close
    wc.py recent [--json]                ids whose round ended failed/released/parked in the last WC_RECENT_HOURS (12)
    wc.py admission [LANE] [--out F]     DRY RUN of the admission rules (below) over the lane's open items: a table of
                                         admitted / refused with the reason; default lane fwlive. No model, no writes
                                         but --out. (owner order 2026-11-12: "Yes to Whittle admission script and hard stops")
    wc.py limit <name>                   one value from limits.json (round_usd, broaden_usd, max_runs, poll_s)
    wc.py guard <W> <ID> --rd RD --dir D -- CMD...   run CMD (the Whittle run) under the hard stops: kills it at the
                                         round dollar cap (exit 90), at the post-DONE (broaden) cap (91), the moment the
                                         item closes in the ledger (92); else CMD's own exit code
    wc.py fingerprint <DIR>              what a run left behind (HEAD, tree, the Whittle dir): a rerun needs it to change
    wc.py rerun-ok <N> <RC> <FP0> <FP1> <DIR>   exit 0 when one more run is allowed (fewer than max_runs, new information)
    wc.py spend <ROUND_DIR> [--clone C]  per phase raw / weighted (cache reads at 0.1) / cost_usd; a killed Whittle run
                                         is read from its session transcripts. Writes <ROUND_DIR>/spend.json

THE GATE (owner order 2026-11-11 ~20:40 PST: "check the tickets deterministically first"). Before any model call an
item must: have a live items/<ID>.md on origin/main and in the clone; be ledger-open; not be held by another loop in the
claims table nor owned by a seat other than BENCH or this worker; fit the lane by needs (offline: needs=offline;
fwlive: a FlowWorks lane id with needs offline|bridge|game-up; never owner); not be blocked; not be routed to a Test
Pilot (testpilot_route.judge, or 3 non-pass runs in a row); not have ended failed|released|parked in a round in the
last WC_RECENT_HOURS. A thin item (no ## spec / ## verify / ## criteria) is NOT skipped (owner ruling 2026-08-22: a
missing field is not a rejection): it ranks after every full item and its STATEMENT.md names the gaps.

ADMISSION (owner order 2026-11-12, recommendation 1 of design/RimMandrake/agent_systems_assessment_2026-11-12.md;
supersedes the 2026-08-22 "a missing field is not a rejection" for the Whittle pick): after the checks above, a ticket
is refused, with a named reason, unless it has an items/<ID>.md; a done-line (ledger criteria, or content under
## criteria / ## verify); a named source path that exists in the repo; a proof route (a selftest or proof/validation
script it names that exists); is not an epic/parent/design (kind, open children, blocked); is not closed, doing or held;
and targets v1. See admit(). Hard stops (recommendation 2): limits.json, guard(), rerun_ok().

A candidate must have a live item file, infrastructure/state/items/<ID>.md (CLAUDE.md: that glob is the live set).
Ledger-open alone counts ~97 FlowWorks ghosts (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE).
While the backing drive is under the floor the lane has no candidates. On 2026-11-11 SteveDesktop C: filled, its
vhdx could not grow, and WSL went read-only.

Files live in /mnt/d/ClaudeWork/rimmandrake/whittle_claude (WC_HOME overrides): <WORKER>/worker.json, loop.log,
claims.json (under claims.lock), workers.json (the roster). On SteveDesktop WC_REMOTE=mandrake@archmagi-wsl: status, log,
claim and unclaim run on Archmagi's copy (REMOTE_WC) over ssh and the shortlist reads Archmagi's claims table, so every
loop on both machines shares one claims table and the WHITTLE_NOW page sees every worker. Every stamp carries a date and an offset: a time-only
stamp is what broke ARTISAN_NOW's dates."""
import argparse
import datetime as dt
import fcntl
import json
import os
import re
import shlex
import signal
import subprocess
import sys
from pathlib import Path

HOME = Path(os.environ.get("WC_HOME", "/mnt/d/ClaudeWork/rimmandrake/whittle_claude"))
REMOTE = os.environ.get("WC_REMOTE")          # user@host whose HOME holds the shared files
REMOTE_WC = "/mnt/d/ClaudeWork/rimmandrake/whittle_claude/tools/wc.py"
SSH = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "-o", "LogLevel=ERROR"]
REPO = Path(__file__).resolve().parents[2]
LIVE_NEEDS = ("bridge", "game-up")
NEVER_NEEDS = ("owner",)
MIN_FREE_GB = float(os.environ.get("WC_MIN_FREE_GB", "15"))
PS = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"


def ps_free():
    """PowerShell: this distro's BasePath (where ext4.vhdx lives; the default distro when WSL_DISTRO_NAME is not found),
    its long-path prefix stripped (checked on Archmagi 2026-11-11), -> "<drive letter> <free bytes>" """
    return ("$ProgressPreference='SilentlyContinue'; $k='HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Lxss';"
            " $n='%s'; $e=Get-ChildItem $k | ForEach-Object { Get-ItemProperty $_.PSPath } |"
            " Where-Object { $_.DistributionName -eq $n } | Select-Object -First 1;"
            " if (-not $e) { $g=(Get-ItemProperty $k).DefaultDistribution; $e=Get-ItemProperty \"$k\\$g\" };"
            " $b=$e.BasePath -replace '^\\\\\\\\\\?\\\\',''; $d=$b.Substring(0,1); \"$d \" + (Get-PSDrive $d).Free"
            % re.sub(r"[^A-Za-z0-9._-]", "", os.environ.get("WSL_DISTRO_NAME", "")))


def now():
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def wdir(worker):
    d = HOME / worker
    d.mkdir(parents=True, exist_ok=True)
    return d


def write_json(path, data):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def read_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def write_table(c):
    """the claims table, and a .bak of it beside, both written only from a table that was read whole"""
    write_json(HOME / "claims.json", c)
    write_json(HOME / "claims.json.bak", c)


def read_table():
    """the claims table, {} when there is none yet, None when it exists but cannot be read: a writer must never
    mistake an unreadable table for an empty one and overwrite every claim in it"""
    p = HOME / "claims.json"
    if not p.exists():
        return {}
    try:
        c = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return c if isinstance(c, dict) else None


class Locked:
    def __enter__(self):
        HOME.mkdir(parents=True, exist_ok=True)
        self.fh = open(HOME / "claims.lock", "w")
        fcntl.flock(self.fh, fcntl.LOCK_EX)
        return self

    def __exit__(self, *a):
        fcntl.flock(self.fh, fcntl.LOCK_UN)
        self.fh.close()


def status(a):
    p = wdir(a.worker) / "worker.json"
    w = read_json(p, {})
    w.setdefault("worker", a.worker)
    for k in ("unit", "machine", "lane", "game"):
        if getattr(a, k):
            w[k] = getattr(a, k)
    if a.item is not None:
        item = None if a.item in ("", "-") else a.item
        if item != w.get("item"):
            w["item_started_at"] = now() if item else None
        w["item"] = item
    if a.round is not None:
        w["round"] = a.round
    if a.state:
        w["state"] = a.state
    if a.note is not None:
        w["note"] = a.note.splitlines()[0][:300] if a.note else ""
    for k in ("unit", "machine", "lane", "game", "item", "item_started_at", "round", "state", "note"):
        w.setdefault(k, None)
    w["updated_at"] = now()
    write_json(p, w)
    with Locked():
        r = read_json(HOME / "workers.json", {"workers": []})
        names = [x["worker"] for x in r["workers"]]
        if a.worker not in names:
            r["workers"].append({"worker": a.worker, "dir": str(HOME / a.worker), "lane": w["lane"],
                                 "machine": w["machine"], "game": w["game"], "unit": w["unit"]})
        r["updated_at"] = now()
        write_json(HOME / "workers.json", r)


LOG_MAX = 5 * 1024 * 1024


def log_line(worker, text):
    if REMOTE:      # the one loop.log lives on Archmagi (see main(): "log" is forwarded there)
        subprocess.run(SSH + [REMOTE, "python3 %s log %s %s" % (REMOTE_WC, shlex.quote(worker), shlex.quote(text))],
                       capture_output=True, timeout=60)
        return
    log(argparse.Namespace(worker=worker, text=[text]))


def log(a):
    p = wdir(a.worker) / "loop.log"
    try:
        if p.stat().st_size > LOG_MAX:      # one old generation kept; whittle_now reads the current one
            os.replace(p, p.with_name("loop.log.1"))
    except OSError:
        pass
    with open(p, "a", encoding="utf-8") as fh:
        fh.write("%s %s\n" % (dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M"), " ".join(a.text)))


def rimflow_mods():
    sys.path.insert(0, str(REPO / "src/RimMandrake/rimflow"))
    import cli
    import model
    import testpilot_route
    return cli, model, testpilot_route


_LOADED = {}


def loaded():
    """(events, world) of the clone's ledger, once per process."""
    if "w" not in _LOADED:
        cli = rimflow_mods()[0]
        _LOADED["evs"], _LOADED["w"] = cli.load()
    return _LOADED["evs"], _LOADED["w"]


def world():
    return loaded()[1]


def lane_patterns():
    d = json.loads((REPO / "infrastructure/state/flowworks_lane.json").read_text(encoding="utf-8"))
    return [re.compile(p) for p in d["id_patterns"]]


def nonpass_of(v):
    n = 0
    for r in reversed(v.runs or []):
        if str(getattr(r, "result", "")).lower() == "pass":
            break
        n += 1
    return n


def shared_claims():
    if not REMOTE:
        return read_json(HOME / "claims.json", {})
    r = subprocess.run(SSH + [REMOTE, "cat %s" % shlex.quote(str(HOME / "claims.json"))], capture_output=True, text=True,
                       timeout=60)
    if r.returncode != 0:
        raise SystemExit("cannot read the shared claims table on %s: %s" % (REMOTE, r.stderr.strip()[:200]))
    try:
        return json.loads(r.stdout or "{}")
    except ValueError:
        return {}


def backing_free():
    """(drive, free GB) of the Windows drive holding this distro's vhdx, or (None, None) when it cannot be read."""
    try:
        r = subprocess.run([PS, "-NoProfile", "-Command", ps_free()], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None, None
    m = re.fullmatch(r"([A-Z]) (\d+)", r.stdout.strip()) if r.returncode == 0 else None
    return (m.group(1), int(m.group(2)) / 1e9) if m else (None, None)


UNKNOWN_LOOKS = 3   # a loop fails closed after this many unreadable looks in a row; anything else at the first


def disk_unknown():
    """an unreadable backing drive: '' while a loop may still go on, else why it must not. Counted per loop in
    $WC_DIR/disk_unknown (reset by any good read); outside a loop (install.sh, steve.sh) it fails closed at once."""
    if not os.environ.get("WC_DIR"):
        return "the backing drive's free space could not be read"
    f = Path(os.environ["WC_DIR"]) / "disk_unknown"
    try:
        n = int(f.read_text().strip() or 0) + 1
    except (OSError, ValueError):
        n = 1
    try:
        f.write_text("%d\n" % n)
    except OSError:
        return "the backing drive's free space could not be read, and neither could %s" % f
    return "" if n < UNKNOWN_LOOKS else "the backing drive's free space could not be read %d looks in a row" % n


def disk_seen():
    if os.environ.get("WC_DIR"):
        try:
            (Path(os.environ["WC_DIR"]) / "disk_unknown").unlink()
        except OSError:
            pass


def disk_low():
    drive, gb = backing_free()
    if gb is None:
        return disk_unknown() or None
    disk_seen()
    if gb < MIN_FREE_GB:
        return "%s: free %.1f GB < %.0f GB floor (the vhdx backing this WSL)" % (drive, gb, MIN_FREE_GB)
    return None


def diskfree(a):
    drive, gb = backing_free()
    if gb is None:
        why = disk_unknown()
        print("unknown (could not read the backing drive)%s" % ((": " + why + ", refused") if why else ", tolerated"))
        return 4 if why else 0
    disk_seen()
    print("%s: %.1f GB free (floor %.0f GB)" % (drive, gb, MIN_FREE_GB))
    return 4 if gb < MIN_FREE_GB else 0


NOTICE = Path(os.environ.get("RM_SWITCH_PLAN_DIR") or "/mnt/d/ClaudeWork/rimmandrake/switching_plan") / "notice.json"


def notice_state():
    """-> (rc, text) of the account switcher's notice here: 0 a hard stop (text the reason), 1 no stop or no notice
    written yet, 2 it cannot be read"""
    if not NOTICE.exists():
        return 1, "no notice at %s" % NOTICE
    try:
        d = json.loads(NOTICE.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return 2, "unreadable %s: %s" % (NOTICE, e)
    if not isinstance(d, dict):
        return 2, "unreadable %s: not an object" % NOTICE
    if d.get("state") != "stop":
        return 1, "no stop (state %s)" % d.get("state")
    return 0, "hard stop by the account switcher at %s, until %s" % (d.get("since") or d.get("at") or "an unmeasured time",
                                                                    d.get("reset_at") or "the next account reset")


def stop_reason():
    """None while new work may start; else why not: a hard stop, or a notice that cannot be read (fail safe). On
    SteveDesktop (WC_REMOTE) the notice is Archmagi's, read over ssh: an old loop's shortlist gets this too"""
    if not REMOTE:
        rc, text = notice_state()
    else:
        try:
            r = subprocess.run(SSH + [REMOTE, "python3 %s hardstop" % shlex.quote(REMOTE_WC)], capture_output=True,
                               text=True, timeout=60)
            rc, text = (r.returncode if r.returncode in (0, 1) else 2), (r.stdout or r.stderr).strip()
        except (OSError, subprocess.SubprocessError) as e:
            rc, text = 2, "ssh %s: %s" % (REMOTE, e)
    if rc == 1:
        return None
    return text if rc == 0 else "the account switcher's notice cannot be read (%s): fail safe" % text[:200]


def hardstop(a):
    """the account switcher's notice (on Archmagi's D:; SteveDesktop asks Archmagi's copy over ssh). exit 0: hard stop,
    the reason printed; 1: no stop (or no notice written yet); 2: it cannot be read, and a loop starts nothing new"""
    rc, text = notice_state()
    print(text)
    return rc


def live_file(item_id):
    return (REPO / "infrastructure/state/items" / (item_id + ".md")).exists()


def origin_live_ids():
    """ids with an items/<ID>.md on origin/main (the loop's ./sync fetched it), or None when git cannot say."""
    try:
        r = subprocess.run(["git", "-C", str(REPO), "ls-tree", "--name-only", "origin/main", "infrastructure/state/items/"],
                           capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    return {Path(x).name[:-3] for x in r.stdout.split() if x.endswith(".md")}


END_LINE = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d) round \d+ end: (\S+) (\w+)")
BAD_ENDS = ("failed", "released", "parked")
RECENT_HOURS = float(os.environ.get("WC_RECENT_HOURS", "12"))


def recent_local(hours=None):
    """{id: "<ending> by <worker> at <stamp>"} for rounds that ended failed|released|parked within the window."""
    hours = RECENT_HOURS if hours is None else hours
    edge = dt.datetime.now() - dt.timedelta(hours=hours)
    out = {}
    for f in sorted(HOME.glob("*/loop.log")):
        try:
            lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line in lines:
            m = END_LINE.match(line)
            if not m or m[3] not in BAD_ENDS:
                continue
            try:
                when = dt.datetime.strptime(m[1], "%Y-%m-%d %H:%M")
            except ValueError:
                continue
            if when >= edge:
                out[m[2]] = "%s by %s at %s" % (m[3], f.parent.name, m[1])
    return out


def recent_ends():
    if not REMOTE:
        return recent_local()
    try:
        r = subprocess.run(SSH + [REMOTE, "python3 %s recent --json" % REMOTE_WC], capture_output=True, text=True,
                           timeout=60)
        return json.loads(r.stdout) if r.returncode == 0 else {}
    except (OSError, ValueError, subprocess.SubprocessError):
        return {}


# --- ticket admission (no model) --------------------------------------------------------------------------------------
LIMITS_FILE = Path(__file__).resolve().parent / "limits.json"
LIMIT_DEFAULTS = {"round_usd": 20.0, "broaden_usd": 3.0, "max_runs": 2, "poll_s": 60}
EPIC_KINDS = ("epic", "design", "decision", "decide", "spike", "system", "finding", "card", "review", "innovation")
PROOF_NAME = re.compile(r"(selftest|proof|validation)", re.I)   # not validate_patch.py and the like: tools, not a proof
TOKEN = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_./\-]*")
_REPO_FILES = {}


def limit(name):
    """one hard-stop value: env WC_LIMIT_<NAME> over limits.json over LIMIT_DEFAULTS"""
    env = os.environ.get("WC_LIMIT_" + name.upper())
    if env:
        return type(LIMIT_DEFAULTS[name])(float(env))
    try:
        d = json.loads(LIMITS_FILE.read_text(encoding="utf-8"))
        if name in d:
            return type(LIMIT_DEFAULTS[name])(d[name])
    except (OSError, ValueError):
        pass
    return LIMIT_DEFAULTS[name]


def repo_files():
    """-> (tracked paths, {path suffix after a '/': [full paths]}, directories); built once per process"""
    if "f" not in _REPO_FILES:
        rc, out = sh(["git", "ls-files"], timeout=120)
        files = set(out.splitlines()) if rc == 0 else set()
        suf, dirs = {}, set()
        for f in files:
            parts = f.split("/")
            for i in range(len(parts)):
                suf.setdefault("/".join(parts[i:]), []).append(f)
            for i in range(1, len(parts)):
                dirs.add("/".join(parts[:i]))
        _REPO_FILES["f"] = (files, suf, dirs)
    return _REPO_FILES["f"]


def clean_token(t):
    return t.rstrip(".,:;-")


def source_paths(text, index=None):
    """paths under src/ that the text names and that exist: a token with a slash, or a unique bare .cs/.xml/.py name"""
    files, suf, dirs = index or repo_files()
    found = []
    for raw in TOKEN.findall(text):
        t = clean_token(raw)
        if t in found:
            continue
        if "/" in t:
            hits = [t] if (t in files or t in dirs) else suf.get(t, [])
            hits = hits + [h for h in suf.get(t, []) if h not in hits]
        elif re.search(r"\.(cs|xml|py)$", t):
            hits = [h for h in suf.get(t, []) if h.startswith("src/")]
            hits = hits if len(hits) == 1 else []
        else:
            hits = []
        if any(h.startswith("src/") for h in hits):
            found.append(t)
    return found


def proof_routes(text, index=None):
    """selftests and proof/validation scripts the text names that exist on disk"""
    files, suf, _ = index or repo_files()
    found = set()
    for raw in TOKEN.findall(text):
        t = clean_token(raw)
        base = t.rsplit("/", 1)[-1]
        base = base if base.endswith(".py") else base + ".py"
        if re.fullmatch(r"(selftest|test)_\w+\.py", base) and base in suf:
            found.add(base)
        elif t.endswith(".py") and PROOF_NAME.search(t.rsplit("/", 1)[-1]) and (t in files or t in suf):
            found.add(t)
    for m in re.finditer(r"--only\s+([\w,]+)", text):
        found.update(n for n in m[1].split(",") if ("selftest_%s.py" % n) in suf or ("%s.py" % n) in suf)
    return sorted(found)


def done_line(v, text):
    for c in getattr(v, "criteria", None) or []:
        if oneline(c.get("text") if isinstance(c, dict) else c):
            return True
    for sec in ("criteria", "verify"):
        body = re.sub(r"(?i)\b(tbd|todo|n/a|none)\b", "", section(text, sec))
        if re.search(r"[A-Za-z]{3,}", body):
            return True
    return False


def open_children(v_id, items):
    """open items that wait on, or were caused by, this one"""
    return sorted(x.id for x in items if x.open and x.id != v_id and (
        getattr(x, "caused_by", None) == v_id or getattr(x, "blocked_on", None) == v_id))


def admit(v, ctx, worker=None):
    """-> [reason, ...]: every admission rule the ticket fails; empty when it is admitted. No model."""
    text = ctx.text(v.id)
    if not text.strip():
        return ["no item file: infrastructure/state/items/%s.md is missing" % v.id]
    why = []
    if not done_line(v, text):
        why.append("no done-line: no ledger criteria and nothing under ## criteria or ## verify")
    if not source_paths(text, ctx.index):
        why.append("no named mod/source path: no existing src/ path in the item file")
    if not proof_routes(text, ctx.index):
        why.append("no proof route: names no existing selftest or proof/validation script")
    kind = str(getattr(v, "kind", "") or "").lower()
    if kind in EPIC_KINDS or re.search(r"\bepic\b", str(getattr(v, "title", "") or ""), re.I):
        why.append("epic/design: kind=%s" % (kind or "?"))
    if getattr(v, "blocked", False):
        why.append("epic/parent: BLOCKED")
    kids = ctx.children(v.id) if ctx.children else []
    if kids:
        why.append("epic/parent: %d open children (%s)" % (len(kids), ", ".join(kids[:3])))
    if not getattr(v, "open", True):
        why.append("closed in the ledger")
    elif getattr(v, "state", "") == "doing" and getattr(v, "owner", "BENCH") not in ("BENCH", worker):
        why.append("doing: held by seat %s" % v.owner)
    elif getattr(v, "held", None):
        why.append("held in the ledger")
    if getattr(v, "target", None) != "v1":
        why.append("target=%s, not v1" % getattr(v, "target", None))
    return why


class Ctx:
    """What the gate reads besides the item. Built from the real clone by Ctx.real(); a selftest builds one by hand."""

    def __init__(self, pats=(), claims=None, origin=None, recent=None, live=live_file, pilot=None, missing=None,
                 admission=False, text=None, index=None, children=None):
        self.pats, self.claims, self.origin, self.recent = list(pats), claims or {}, origin, recent or {}
        self.admission, self.text, self.index, self.children = admission, text or item_text, index, children
        self.live, self.pilot, self.missing = live, pilot or (lambda v: None), missing or (lambda v: [])

    @classmethod
    def real(cls):
        evs, _ = loaded()
        _, model, tpr = rimflow_mods()
        items = list(world().items.values())
        return cls(pats=lane_patterns(), claims=shared_claims(), origin=origin_live_ids(), recent=recent_ends(),
                   pilot=lambda v: tpr.judge(v, evs), missing=model._missing, admission=True, index=repo_files(),
                   children=lambda i: open_children(i, items))


def gate(v, worker, lane, ctx):
    """-> (ok, reason, rank) for one ledger item. ok False: the reason says why it is skipped. Pure but for ctx."""
    if v is None:
        return False, "ghost: not in the ledger", None
    if not ctx.live(v.id) or (ctx.origin is not None and v.id not in ctx.origin):
        return False, "ghost: no infrastructure/state/items/%s.md on origin/main" % v.id, None
    if not v.open:
        return False, "closed: state=%s" % v.state, None
    held = ctx.claims.get(v.id)
    if held and held.get("worker") != worker:
        return False, "claimed by %s since %s" % (held.get("worker"), held.get("at")), None
    if v.owner not in ("BENCH", worker):
        return False, "owned by seat %s" % v.owner, None
    if v.needs in NEVER_NEEDS:
        return False, "needs=%s" % v.needs, None
    fw = any(p.search(v.id) for p in ctx.pats)
    live = v.needs in LIVE_NEEDS
    if lane == "fwlive":
        if not fw:
            return False, "lane: not a FlowWorks lane id", None
        if v.needs not in ("offline",) + LIVE_NEEDS:
            return False, "lane: needs=%s does not fit fwlive" % v.needs, None
        # the blockage: built or validated work that only lacks its live proof first, then other live, then offline
        rank = 0 if live and v.state in ("built", "validated") else 1 if live else 2
    else:
        if v.needs != "offline":
            return False, "lane: needs=%s is not offline" % v.needs, None
        # FlowWorks offline items belong to the live loops first; an offline loop takes them last
        rank = (0 if v.state == "ready" else 1) + (2 if fw else 0)
    if v.blocked:
        return False, "blocked: %s" % str(v.blocked_reason or "no reason given")[:120], None
    tp = ctx.pilot(v)
    if tp:
        return False, "Test Pilot: %s" % tp.get("why", tp.get("kind")), None
    if nonpass_of(v) >= 3:
        return False, "Test Pilot: %d non-pass runs in a row" % nonpass_of(v), None
    if v.id in ctx.recent:
        return False, "recent round: %s (within %g h)" % (ctx.recent[v.id], RECENT_HOURS), None
    if ctx.admission:
        refused = admit(v, ctx, worker)
        if refused:
            return False, "admission: " + "; ".join(refused), None
    gaps = ctx.missing(v)
    if gaps:
        return True, "eligible, thin (no ## %s): ranked last" % ", ## ".join(gaps), rank + 10
    return True, "eligible", rank


def candidates(worker, lane, ctx=None, why=None):
    """eligible items, ranked: [(rank, -criteria, item, reason)]. why: a list that gets (id, reason) of every skip."""
    if disk_low():
        return []
    ctx = ctx or Ctx.real()
    out = []
    for v in world().items.values():
        if not v.open:
            continue     # closed items are the bulk of the ledger: skipped without a line
        ok, reason, rank = gate(v, worker, lane, ctx)
        if ok:
            out.append((rank, -(len(v.criteria or [])), v, reason))
        elif why is not None:
            why.append((v.id, reason))
    out.sort(key=lambda t: (t[0], t[1], len(t[2].runs or []), t[2].id))
    return out


def gate_cmd(a):
    ctx, w = Ctx.real(), world()
    for i in a.ids:
        ok, reason, rank = gate(w.items.get(i), a.worker, a.lane, ctx)
        print("%s %s: %s%s" % ("PICK" if ok else "SKIP", i, reason, "" if rank is None else " (rank %d)" % rank))


def skip_summary(why):
    kinds = {}
    for _, r in why:
        k = re.sub(r" since .*", "", r.split(":")[0])
        kinds[k] = kinds.get(k, 0) + 1
    return ", ".join("%d %s" % (n, k) for k, n in sorted(kinds.items(), key=lambda t: -t[1]))


def shortlist(a):
    low = disk_low()
    if low:
        print("# NO CANDIDATES: disk guard: %s. Answer NONE." % low)
        return
    why = []
    rows = candidates(a.worker, a.lane, why=why)
    if a.why:
        for i, r in why:
            print("SKIP %s: %s" % (i, r))
    for rank, _, v, reason in rows[:a.n]:
        print("%s | state=%s needs=%s owner=%s runs=%d | %s | %s" % (
            v.id, v.state, v.needs, v.owner, len(v.runs or []), reason, (v.title or "")[:120]))
    print("# %d eligible in lane %s for %s at %s; skipped open: %s" % (len(rows), a.lane, a.worker, now(),
                                                                       skip_summary(why) or "none"))
    # the loops started before this gate run setup.md through a model: do the pick here, and hand the model one line
    if os.environ.get("WC_DIR") and os.environ.get("WC_LOOP") != "2" and not a.no_pick:
        r = setup_run(a.worker, a.lane, None, rows=rows, quiet=True)
        print("PRE-PICKED: %s" % r)


def lane_open(a):
    print(len(candidates("-", a.lane)))


def claim(a):
    with Locked():
        c = read_table()
        if c is None:
            print("REFUSED: %s is unreadable; not overwriting it" % (HOME / "claims.json"))
            return 4
        held = c.get(a.id)
        if held and held.get("worker") != a.worker:
            print("REFUSED: %s is claimed by %s since %s" % (a.id, held["worker"], held.get("at")))
            return 3
        mine = [k for k, x in c.items() if x.get("worker") == a.worker and k != a.id]
        if mine:
            print("REFUSED: %s already holds %s; one ticket at a time (unclaim it first)" % (a.worker, ", ".join(mine)))
            return 3
        c[a.id] = {"worker": a.worker, "at": now()}
        write_table(c)
    print("CLAIMED %s for %s" % (a.id, a.worker))
    return 0


def unclaim(a):
    with Locked():
        c = read_table()
        if c is None:
            print("REFUSED: %s is unreadable; not overwriting it" % (HOME / "claims.json"))
            return 4
        if c.get(a.id, {}).get("worker") == a.worker:
            del c[a.id]
            write_table(c)
            print("UNCLAIMED %s" % a.id)
        else:
            print("not held by %s: %s" % (a.worker, a.id))
    return 0


def mine(a):
    for k, x in read_json(HOME / "claims.json", {}).items():
        if x.get("worker") == a.worker:
            print(k)


def nonpass(a):
    v = world().items.get(a.id)
    print(nonpass_of(v) if v else "unknown item")


def tokens(a):
    total = 0
    for p in a.logs:
        for line in Path(p).read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                d = json.loads(line)
            except ValueError:
                continue
            u = d.get("usage") if isinstance(d, dict) and d.get("type") == "result" else None
            if u:
                total += sum(int(u.get(k) or 0) for k in ("input_tokens", "output_tokens",
                             "cache_creation_input_tokens", "cache_read_input_tokens"))
    print(total)


RULING = "CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM"
SHARD = "infrastructure/state/ledger/events/%s.jsonl"
OWNER_SHARD = "infrastructure/state/ledger/events/OWNER.jsonl"
_SAY = []


def say(text):
    """a line for the phase log (stderr, and $WC_DIR/script.log): the script's own record of what it did and why"""
    line = "%s %s" % (now(), text)
    _SAY.append(line)
    print(line, file=sys.stderr)
    if os.environ.get("WC_DIR"):
        try:
            with open(Path(os.environ["WC_DIR"]) / "script.log", "a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        except OSError:
            pass


def sh(cmd, timeout=300):
    """run in the clone; -> (rc, combined output). Never raises."""
    try:
        r = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()
    except (OSError, subprocess.SubprocessError) as e:
        return 99, str(e)


def rimflow(worker, *args):
    env_seat = os.environ.get("RIMFLOW_SEAT")
    os.environ["RIMFLOW_SEAT"] = worker
    try:
        rc, out = sh([sys.executable, str(REPO / "src/RimMandrake/rimflow/cli.py")] + list(args))
    finally:
        if env_seat is None:
            os.environ.pop("RIMFLOW_SEAT", None)
        else:
            os.environ["RIMFLOW_SEAT"] = env_seat
    say("rimflow %s -> rc %d %s" % (" ".join(args[:2]), rc, out.splitlines()[-1][:160] if out else ""))
    return rc, out


def land(worker, paths, subject):
    """commit the given paths (only those) and ./publish; -> the published sha or 'none'"""
    paths = [p for p in paths if (REPO / p).exists()]
    if paths:
        sh(["git", "add", "--"] + paths)
        rc, _ = sh(["git", "diff", "--cached", "--quiet", "--"] + paths)
        if rc == 1:
            rc, out = sh(["git", "commit", "-q", "-m", "%s\n\nwc.py (scripted, no model) for %s" % (subject, worker),
                          "--"] + paths)
            say("commit %s -> rc %d %s" % (subject[:60], rc, out[-160:]))
    rc, out = sh(["./publish"], timeout=420)
    if rc != 0:
        say("./publish failed rc %d: %s" % (rc, out[-200:]))
        return "none"
    rc, sha = sh(["git", "rev-parse", "--short=10", "HEAD"])
    return sha if rc == 0 else "none"


def table_claim(worker, item_id):
    with Locked():
        c = read_table()
        if c is None:
            return False
        held = c.get(item_id)
        if held and held.get("worker") != worker:
            return False
        c[item_id] = {"worker": worker, "at": now()}
        write_table(c)
    return True


def table_call(cmd, worker, item_id):
    """claim/unclaim in the shared table: here, or on Archmagi's copy from SteveDesktop. -> rc"""
    if REMOTE:
        r = subprocess.run(SSH + [REMOTE, "python3 %s %s %s %s" % (REMOTE_WC, cmd, shlex.quote(worker),
                                                                      shlex.quote(item_id))],
                           capture_output=True, text=True, timeout=120)
        return r.returncode
    if cmd == "claim":
        return 0 if table_claim(worker, item_id) else 3
    with Locked():
        c = read_table()
        if c is None:
            return 4
        if c.get(item_id, {}).get("worker") == worker:
            del c[item_id]
            write_table(c)
    return 0


def mine_ids(worker):
    return [k for k, x in shared_claims().items() if x.get("worker") == worker]


def oneline(text, n=400):
    return re.sub(r"\s+", " ", str(text or "")).strip()[:n]


def item_text(item_id):
    try:
        return (REPO / "infrastructure/state/items" / (item_id + ".md")).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def section(text, name):
    m = re.search(r"^##\s+%s\s*$(.*?)(?=^##\s|\Z)" % re.escape(name), text, re.M | re.S | re.I)
    return m.group(1).strip() if m else ""


def statement_md(v, gaps):
    crit = [c for c in (v.criteria or []) if oneline(c.get("text"))]
    lines = ["# %s: done statement" % v.id, "",
             "Item title: %s" % oneline(v.title, 300),
             "Written by wc.py setup (no model) from the ledger criteria and `infrastructure/state/items/%s.md`; the "
             "item file's spec and verify sections are the owner's words where it has them." % v.id]
    if gaps:
        lines.append("The item file is thin (it has no ## %s section). Read the ledger history (`rimflow show %s`) for "
                     "what is meant, and write what you find into NOTES.md; do not invent scope." % (
                         ", ## ".join(gaps), v.id))
    lines.append("")
    if crit:
        for c in crit:
            lines.append("- **%s (%s):** %s" % (c.get("id") or "A?", c.get("level") or "L?", oneline(c.get("text"))))
    else:
        found = [oneline(x[1:]) for x in section(item_text(v.id), "criteria").splitlines() if x.strip()[:1] in "-*"]
        for f in found or ["%s is done as `infrastructure/state/items/%s.md` says, shown by fresh evidence." % (
                oneline(v.title, 200), v.id)]:
            lines.append("- %s" % f)
    return "\n".join(lines) + "\n"


def notes_md(v, worker, evs):
    lines = ["# Notes (newest first)", "", "## %s setup (%s, wc.py, no model)" % (now()[:10], worker),
             "- Ledger: state=%s needs=%s owner=%s; %d runs, non-pass tail %d." % (
                 v.state, v.needs, v.owner, len(v.runs or []), nonpass_of(v)),
             "- The item file: `infrastructure/state/items/%s.md`; the full record: `rimflow show %s`." % (v.id, v.id)]
    for r in list(v.runs or [])[-5:][::-1]:
        lines.append("- run %s %s %s sha %s evidence `%s`" % (str(getattr(r, "ts", ""))[:16], getattr(r, "config", ""),
                     getattr(r, "result", ""), str(getattr(r, "sha", "") or "")[:10], getattr(r, "evidence", "")))
    notes = [evs[i] for i in (v.history or []) if i < len(evs) and evs[i].get("event") == "note"][-5:]
    for e in notes[::-1]:
        lines.append("- note %s %s: %s" % (str(e.get("ts", ""))[:16], e.get("seat", ""), oneline(e.get("text"), 300)))
    return "\n".join(lines) + "\n"


def prompt_md(v, d, lane):
    t = (Path(os.environ.get("WC_TEMPLATE", str(Path.home() / "dev/MandrakeWorkflows/whittle/template"))) /
         "PROMPT.md").read_text(encoding="utf-8")
    t = re.sub(r"\A\s*<!--.*?-->\s*", "", t, flags=re.S)
    verify = oneline(section(item_text(v.id), "verify"), 300)
    see = ("its proof script or a bridge session on your lane's game only (the lane file says which, and how to hold "
           "the bridge), in-game screenshots through the bridge that you then Read (lane file: how, and modal dialogs)" if lane == "fwlive" else
           "the offline check the item names (a selftest, a validator, a build), and its output")
    fills = ["`%s` (%s)" % (v.id, oneline(v.title, 200)),
             "built so every bullet in its STATEMENT.md is true in ordinary use, shown by fresh evidence",
             "%s%s" % (see, ("; the item's verify section says: " + verify) if verify else ""),
             "the item's verify section in `infrastructure/state/items/%s.md`, and `python3 "
             "src/RimMandrake/Utils/run_selftests.py --only <tests>` as the fast check" % v.id,
             "`rimflow show %s` (runs, notes, evidence paths), and the run notes in NOTES.md" % v.id,
             "the `chatgpt-consult` skill",
             "other lanes' games, the owner's mod list on his campaign, anything outside this item"]
    it = iter(fills)
    t = re.sub(r"<[^<>]+>", lambda m: next(it, "(see the item file)"), t)
    t = re.sub(r"You are on your own\s+branch; a bad result is thrown away, so try things\.",
               "Work lands on main through ./publish: commit what works, keep experiments in scratch.", t)
    return t.replace("whittle/", d + "/")


def setup_run(worker, lane, rnd, rows=None, quiet=False):
    """the SETUP phase without a model. -> 'PICKED <ID> <dir> whittle' | 'NONE <reason>'"""
    low = disk_low()
    if low:
        return "NONE disk guard: %s" % low
    stop = stop_reason()
    if stop:
        return "NONE hard stop: %s" % stop
    evs, w = loaded()
    ctx = Ctx.real()
    for held in mine_ids(worker):       # a claim left from an earlier round or try: keep it only while it passes
        ok, reason, _ = gate(w.items.get(held), worker, lane, ctx)
        if not ok:
            say("stale claim %s fails the gate (%s): releasing it" % (held, reason))
            release_run(worker, held, "stale claim at round start: %s" % reason)
    if rows is None:
        why = []
        rows = candidates(worker, lane, ctx, why)
        refused = [(i, r) for i, r in why if r.startswith("admission: ")]
        for i, r in refused[:40]:      # the named reason in the worker's loop.log; the ticket is skipped, not claimed
            log_line(worker, "admission refused %s: %s" % (i, r[len("admission: "):]))
        if refused:
            log_line(worker, "admission refused %d tickets this round%s" % (
                len(refused), "" if len(refused) <= 40 else " (first 40 listed; wc.py admission prints all)"))
    held = mine_ids(worker)
    order = [w.items[i] for i in held if i in w.items] + [r[2] for r in rows if r[2].id not in held]
    for v in order[:15]:
        ok, reason, _ = gate(v, worker, lane, ctx)
        if not ok:
            continue
        if table_call("claim", worker, v.id) != 0:
            say("%s: another loop claimed it first" % v.id)
            continue
        if v.owner != worker:
            if v.owner == "BENCH":
                rimflow(worker, "reassign", v.id, "--to", worker, "--per-ruling", RULING)
            rimflow(worker, "claim", v.id)
            _LOADED.clear()
            evs, w = loaded()
            if w.items[v.id].owner != worker:
                say("%s: the ledger claim did not take (owner %s): next" % (v.id, w.items[v.id].owner))
                table_call("unclaim", worker, v.id)
                continue
            v = w.items[v.id]
        d = "whittle/" + v.id.lower()
        wd = REPO / d
        wd.mkdir(parents=True, exist_ok=True)
        gaps = ctx.missing(v)
        files = {"STATEMENT.md": statement_md(v, gaps), "NOTES.md": notes_md(v, worker, evs), "MODE": "whittle\n",
                 "PROMPT.md": prompt_md(v, d, lane)}
        for name, body in files.items():
            if not (wd / name).exists() or not (wd / name).read_text(encoding="utf-8").strip():
                (wd / name).write_text(body, encoding="utf-8")
        sha = land(worker, [d, SHARD % worker, OWNER_SHARD], "whittle setup: %s takes %s" % (worker, v.id))
        _LOADED.clear()                 # the landing rebased onto origin: someone may have closed it meanwhile
        evs, w = loaded()
        now_v, live = w.items.get(v.id), origin_live_ids()
        if now_v is None or not now_v.open or (live is not None and v.id not in live):
            say("%s: closed or deleted upstream while it was being claimed: releasing it, next" % v.id)
            release_run(worker, v.id, "closed or deleted upstream during setup")
            continue
        say("picked %s (%s), whittle dir %s, published %s" % (v.id, reason, d, sha))
        if os.environ.get("WC_DIR"):
            with open(Path(os.environ["WC_DIR"]) / "progress.md", "a", encoding="utf-8") as fh:
                fh.write("%s round %s picked %s by wc.py (no model): %s; mode whittle%s\n" % (
                    now(), rnd or "?", v.id, reason, "; thin, STATEMENT names the gaps" if gaps else ""))
        return "PICKED %s %s whittle" % (v.id, v.id.lower())
    return "NONE no eligible item in lane %s (%d ranked)" % (lane, len(rows))


def setup(a):
    print(setup_run(a.worker, a.lane, a.round))


def release_run(worker, item_id, why):
    """the scripted release: note, give the item back to BENCH, unclaim the table, commit and publish. -> sha"""
    _, w = loaded()
    v = w.items.get(item_id)
    if v is not None:
        rimflow(worker, "note", item_id, "--text", "Claude Whittle %s released this claim: %s" % (worker, why),
                "--why", "wc.py scripted release (no model)")
        if v.open and v.owner == worker:
            rimflow(worker, "reassign", item_id, "--to", "BENCH", "--per-ruling", RULING)
    table_call("unclaim", worker, item_id)
    _LOADED.clear()
    return land(worker, [SHARD % worker, OWNER_SHARD], "whittle release: %s gives back %s" % (worker, item_id))


def release(a):
    print("RELEASED %s sha=%s" % (a.id, release_run(a.worker, a.id, a.why)))


def wrapup_run(worker, item_id, d, rc, rnd=None):
    """the mechanical endings. -> 'RESULT <ID> <ending> sha=<sha>', or None when a model must judge (rc 0)"""
    _, w = loaded()
    v = w.items.get(item_id)
    wd = REPO / d
    rd = (Path(os.environ["WC_DIR"]) / "rounds" / str(rnd)) if rnd and os.environ.get("WC_DIR") else rnd
    tail = "the work so far is in %s%s" % (d, (" and %s" % rd) if rd else "")
    if v is not None and not v.open:
        # the ledger decides the ending, read first: a closer (or `rimflow verify`) may already have moved the item to
        # done, which also removes its live file, so the ghost test below would call a win "released"
        table_call("unclaim", worker, item_id)
        sha = land(worker, [d, SHARD % worker, OWNER_SHARD], "whittle wrap-up: %s %s" % (item_id, v.state))
        end = "closed" if v.state == "done" else "dropped"
        return "RESULT %s %s sha=%s" % (item_id, end, v.closed_sha[:10] if v.closed_sha else sha)
    if rc == "ghost" or v is None or not live_file(item_id):
        sha = release_run(worker, item_id, "no live item file (ledger ghost); nothing was built")
        return "RESULT %s released sha=%s" % (item_id, sha)
    if v.owner != worker and item_id not in mine_ids(worker):
        # a replayed wrap-up (killed after it gave the item back): it is someone else's now, so touch nothing
        say("%s is no longer %s's (owner %s, not in its claims): this wrap-up already ran" % (item_id, worker, v.owner))
        return "RESULT %s released sha=none" % item_id
    if str(rc) == "0":
        return None
    if str(rc) == "capped":     # a hard stop (guard_run exit 90/91): PARK it for the owner, claim and bridge released by the loop
        g = read_json(Path(os.environ["WC_DIR"]) / "rounds" / str(rnd) / "guard.json", {}) if rnd and os.environ.get(
            "WC_DIR") else {}
        why = "parked by a hard stop: %s (spent about $%s); %s. Decide: resize or split it, or raise the cap in " \
              "infrastructure/whittle_claude/limits.json" % (g.get("stop") or "a cost cap", g.get("cost", "?"), tail)
        if os.environ.get("WC_DIR"):
            with open(Path(os.environ["WC_DIR"]) / "OWNER_QUESTIONS.md", "a", encoding="utf-8") as fh:
                fh.write("\n## %s %s (%s)\n%s\n" % (now(), item_id, worker, why))
        rimflow(worker, "note", item_id, "--text", "Claude Whittle %s round %s: %s" % (worker, rnd or "?", why),
                "--why", "wc.py hard stop (no model)")
        if v.owner == worker:
            rimflow(worker, "reassign", item_id, "--to", "BENCH", "--per-ruling", RULING)
        table_call("unclaim", worker, item_id)
        sha = land(worker, [d, SHARD % worker, OWNER_SHARD], "whittle wrap-up: %s parked by a hard stop" % item_id)
        return "RESULT %s parked sha=%s" % (item_id, sha)
    blocked = ""
    if (wd / "BLOCKED.md").exists():
        blocked = oneline((wd / "BLOCKED.md").read_text(encoding="utf-8", errors="replace"), 300)
    if str(rc) == "2" and re.search(r"\bowner\b|OWNER_QUESTIONS", blocked, re.I):
        end = "parked"
        if os.environ.get("WC_DIR"):
            with open(Path(os.environ["WC_DIR"]) / "OWNER_QUESTIONS.md", "a", encoding="utf-8") as fh:
                fh.write("\n## %s %s (%s)\n%s\n" % (now(), item_id, worker, blocked))
        why = "parked on an owner question: %s; %s" % (blocked, tail)
    else:
        end = "failed"
        n = nonpass_of(v)
        why = "unfinished (Whittle exit %s%s); %s%s" % (rc, (", BLOCKED: " + blocked) if blocked else "", tail,
                                                       "; 3 non-pass runs in a row: it needs a Test Pilot (rimflow "
                                                       "pilot %s)" % item_id if n >= 3 else "")
    rimflow(worker, "note", item_id, "--text", "Claude Whittle %s round %s: %s" % (worker, rnd or "?", why),
            "--why", "wc.py scripted wrap-up (no model)")
    if v.owner == worker:
        rimflow(worker, "reassign", item_id, "--to", "BENCH", "--per-ruling", RULING)
    table_call("unclaim", worker, item_id)
    rc2, dirty = sh(["git", "status", "--porcelain", "--untracked-files=all"])
    left = [x[3:] for x in dirty.splitlines() if x[3:] and not x[3:].startswith(d)]
    if left and os.environ.get("WC_DIR"):
        with open(Path(os.environ["WC_DIR"]) / "progress.md", "a", encoding="utf-8") as fh:
            fh.write("%s %s %s: uncommitted, left for a person: %s\n" % (now(), item_id, end, " ".join(left[:20])))
    sha = land(worker, [d, SHARD % worker, OWNER_SHARD], "whittle wrap-up: %s %s" % (item_id, end))
    return "RESULT %s %s sha=%s" % (item_id, end, sha)


def wrapup(a):
    r = wrapup_run(a.worker, a.id, a.dir, a.rc, a.round)
    if r is None:
        print("MODEL: Whittle exit 0: a model must check DONE.md and the judge and close")
        return 5
    print(r)
    return 0


def recent(a):
    r = recent_local(a.hours)
    if a.json:
        print(json.dumps(r))
    else:
        for k, x in sorted(r.items()):
            print("%s %s" % (k, x))


# per million tokens: input, output, cache write (1 h), cache read; fitted to the CLI's own costUSD on 2026-11-11 rounds,
# used only where a log carries no costUSD (a killed run read from its transcript)
PRICE = {"opus": (4.0, 20.0, 8.0, 0.2), "sonnet": (2.0, 10.0, 4.0, 0.1), "haiku": (1.0, 5.0, 2.0, 0.1)}


def priced(model, i, o, cc, cr):
    p = next((v for k, v in PRICE.items() if k in str(model)), PRICE["opus"])
    return (i * p[0] + o * p[1] + cc * p[2] + cr * p[3]) / 1e6


def blank():
    return {"input": 0, "output": 0, "cache_write": 0, "cache_read": 0, "cost_usd": 0.0, "turns": 0, "source": []}


def add(acc, i, o, cc, cr, cost, turns=0):
    acc["input"] += i
    acc["output"] += o
    acc["cache_write"] += cc
    acc["cache_read"] += cr
    acc["cost_usd"] += cost
    acc["turns"] += turns


def finish(acc):
    acc["raw"] = acc["input"] + acc["output"] + acc["cache_write"] + acc["cache_read"]
    acc["weighted"] = int(acc["input"] + acc["output"] + acc["cache_write"] + 0.1 * acc["cache_read"])
    acc["cost_usd"] = round(acc["cost_usd"], 4)
    return acc


def result_usage(path, acc):
    """add the result lines of a `claude -p --output-format json` log; -> the session ids seen (None: no result line)"""
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    docs = []
    for line in text.splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if isinstance(d, dict):
            docs.append(d)
        elif isinstance(d, list):
            docs.extend(x for x in d if isinstance(x, dict))
    sessions = set()
    for d in docs:
        if d.get("type") != "result":
            continue
        sessions.add(d.get("session_id"))
        mu = d.get("modelUsage") or {}
        if mu:
            for m, u in mu.items():
                add(acc, int(u.get("inputTokens") or 0), int(u.get("outputTokens") or 0),
                    int(u.get("cacheCreationInputTokens") or 0), int(u.get("cacheReadInputTokens") or 0),
                    float(u.get("costUSD") or 0))
        else:
            u = d.get("usage") or {}
            i, o = int(u.get("input_tokens") or 0), int(u.get("output_tokens") or 0)
            cc, cr = int(u.get("cache_creation_input_tokens") or 0), int(u.get("cache_read_input_tokens") or 0)
            add(acc, i, o, cc, cr, float(d.get("total_cost_usd") or priced("opus", i, o, cc, cr)))
        acc["turns"] += int(d.get("num_turns") or 0)
    if sessions:
        acc["source"].append(str(path))
    return sessions or None


def stamp_of(ts):
    try:
        return dt.datetime.fromisoformat(str(ts).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def transcript_usage(clone, t0, t1, skip, acc):
    """add every assistant message the clone's Claude sessions wrote between t0 and t1 (epoch s), deduped by message
    id, sessions in skip left out: the spend of a run that was killed before it printed its result"""
    proj = Path.home() / ".claude/projects" / re.sub(r"[^A-Za-z0-9]", "-", str(clone))
    seen = {}
    for f in proj.rglob("*.jsonl") if proj.is_dir() else ():
        try:
            if f.stat().st_mtime < t0:
                continue
            fh = open(f, encoding="utf-8", errors="replace")
        except OSError:
            continue
        with fh:
            for line in fh:
                if '"assistant"' not in line:
                    continue
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if d.get("type") != "assistant" or d.get("sessionId") in skip:
                    continue
                t = stamp_of(d.get("timestamp"))
                m = d.get("message") or {}
                if t is None or not (t0 <= t <= t1) or not m.get("usage"):
                    continue
                seen[m.get("id") or d.get("uuid")] = (m.get("model"), m["usage"], d.get("sessionId"))
    sessions = set()
    for model, u, sid in seen.values():
        i, o = int(u.get("input_tokens") or 0), int(u.get("output_tokens") or 0)
        cc, cr = int(u.get("cache_creation_input_tokens") or 0), int(u.get("cache_read_input_tokens") or 0)
        add(acc, i, o, cc, cr, priced(model, i, o, cc, cr), 1)
        sessions.add(sid)
    if seen:
        acc["source"].append("transcripts %s (%d sessions, %d messages)" % (proj, len(sessions), len(seen)))
    return sessions


def mtime(p):
    try:
        return Path(p).stat().st_mtime
    except OSError:
        return None


def spend_of(rd, clone):
    rd = Path(rd)
    out, skip = {}, set()
    for phase in ("setup", "wrapup"):
        acc = blank()
        skip |= result_usage(rd / ("%s.json" % phase), acc) or set()
        out[phase] = finish(acc)
    acc = blank()
    t_prev = mtime(rd / "setup.json") or mtime(rd)
    for n in range(1, 10):
        log_, outp = rd / ("whittle.%d.log" % n), rd / ("whittle.%d.out" % n)
        if not log_.exists() and not outp.exists():
            break
        if result_usage(log_, acc) is None:
            t0 = float((rd / ("whittle.%d.t0" % n)).read_text()) if (rd / ("whittle.%d.t0" % n)).exists() else t_prev
            # an empty .out was only created, never written (the run was killed): its end is when the wrapup began
            ends = [mtime(rd / "wrapup.json.err"), mtime(rd / "wrapup.json"), dt.datetime.now().timestamp()]
            if outp.exists() and outp.stat().st_size:
                ends.insert(0, mtime(outp))
            t1 = (float((rd / ("whittle.%d.t1" % n)).read_text()) if (rd / ("whittle.%d.t1" % n)).exists()
                  else next(e for e in ends if e))
            if t0:
                transcript_usage(clone, t0, t1, skip, acc)
        t_prev = mtime(outp) or t_prev
    out["whittle"] = finish(acc)
    tot = blank()
    for k in ("setup", "whittle", "wrapup"):
        add(tot, *(out[k][x] for x in ("input", "output", "cache_write", "cache_read", "cost_usd", "turns")))
    out["total"] = finish(tot)
    return out


def admission_table(worker, lane, ctx=None):
    """-> (rows, text): every open ledger item the lane could ever take, with the gate verdict and every admission rule it
    fails (standalone, so a ticket another gate rule stops first still shows what admission says)"""
    ctx = ctx or Ctx.real()
    w = world()
    fw = lane == "fwlive"
    rows = []
    for v in sorted(w.items.values(), key=lambda x: x.id):
        if not v.open or (fw and not any(p.search(v.id) for p in ctx.pats)):
            continue
        ok, reason, _ = gate(v, worker, lane, ctx)
        fails = admit(v, ctx, worker)
        rows.append((v.id, ok, reason, fails, v))
    adm = [r for r in rows if not r[3]]
    gated = [r for r in rows if r[1]]
    kinds = {}
    for r in rows:
        for f in r[3]:
            k = f.split(":")[0]
            kinds[k] = kinds.get(k, 0) + 1
    lines = ["# Whittle ticket admission, dry run (%s, lane %s)" % (now(), lane), "",
             "Written by `wc.py admission` (no model, no writes but this file). Rules: infrastructure/whittle_claude/wc.py "
             "admit(). Owner order 2026-11-12: \"Yes to Whittle admission script and hard stops.\"", "",
             "- open ledger items in the lane: **%d**" % len(rows),
             "- pass every admission rule: **%d**" % len(adm),
             "- pass the whole gate (admission + lane, claims, blocks, recent rounds), i.e. would be picked: **%d**" % len(gated),
             "- refused by admission: **%d**" % (len(rows) - len(adm)), "",
             "Admission refusals by rule (a ticket can fail several):", ""]
    lines += ["- %d x %s" % (n, k) for k, n in sorted(kinds.items(), key=lambda t: -t[1])]
    lines += ["", "| ticket | picked | admission | gate says |", "|---|---|---|---|"]
    for i, ok, reason, fails, v in sorted(rows, key=lambda r: (not r[1], bool(r[3]), r[0])):
        lines.append("| %s | %s | %s | %s |" % (i, "YES" if ok else "no", "admitted" if not fails else
                                                  "REFUSED: " + "; ".join(fails), reason.replace("|", "/")[:150]))
    return rows, "\n".join(lines) + "\n"


def admission(a):
    worker = a.worker or "CLAUDE_ARCHMAGI_FWLIVE"
    rows, text = admission_table(worker, a.lane)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(text, encoding="utf-8")
    print("\n".join(text.splitlines()[:16] if a.out else text.splitlines()))
    if a.out:
        print("table: %s" % a.out)


# --- hard stops (owner order 2026-11-12, recommendation 2) -----------------------------------------------------------
def live_cost(clone, t0):
    """dollars the clone's Claude sessions have spent since t0 (epoch s), priced from the growing session transcripts
    (PRICE below). The CLI only prints its own cost_usd at the end of a run, so this is the mid-round feed."""
    acc = blank()
    transcript_usage(clone, t0, dt.datetime.now().timestamp() + 5, set(), acc)
    return acc["cost_usd"]


def ledger_closed(item_id):
    _LOADED.clear()
    v = world().items.get(item_id)
    return v is not None and not v.open


def guard_run(cmd, cost_feed, closed_feed, broaden_feed, cap, broaden_cap, poll, note=None, sleep_grace=30,
              popen=subprocess.Popen):
    """run cmd under the hard stops, polling every `poll` s: -> its exit code, or 90 (the round's dollar cap), 91 (the
    broaden/judge window's cap: dollars spent since broaden_feed() first said True), 92 (the item closed in the ledger).
    cost_feed() -> dollars so far this round; closed_feed(), broaden_feed() -> bool. note(dict) gets every reading."""
    p = popen(cmd, start_new_session=True)
    base = None
    why = None
    while True:
        try:
            return p.wait(timeout=poll) if why is None else p.wait()
        except subprocess.TimeoutExpired:
            pass
        cost = cost_feed()
        if base is None and broaden_feed():
            base = cost
        if cost >= cap:
            why = (90, "the round reached $%.2f of the $%.2f cap" % (cost, cap))
        elif base is not None and cost - base >= broaden_cap:
            why = (91, "$%.2f spent since the judge/broaden stage began (cap $%.2f)" % (cost - base, broaden_cap))
        elif closed_feed():
            why = (92, "the item closed in the ledger: the round ends here")
        if note:
            note({"cost": round(cost, 2), "cap": cap, "broaden_base": base, "stop": why[1] if why else None})
        if why:
            for sig in (signal.SIGTERM, signal.SIGKILL):
                try:
                    os.killpg(p.pid, sig)
                except OSError:
                    pass
                try:
                    p.wait(timeout=sleep_grace if sig == signal.SIGTERM else 10)
                    break
                except subprocess.TimeoutExpired:
                    continue
            return why[0]


def guard(a):
    cmd = a.run[1:] if a.run and a.run[0] == "--" else a.run
    rd, clone = Path(a.rd), a.clone or REPO
    t0f = rd / "round.t0"
    if not t0f.exists():
        t0f.write_text("%d" % int(dt.datetime.now().timestamp()))
    t0 = float(t0f.read_text())
    started = dt.datetime.now().timestamp()
    wd = REPO / a.dir

    def broaden():
        for n in ("BROADEN.md", "JUDGE.md"):
            f = wd / n
            if f.exists() and f.stat().st_size > 20 and f.stat().st_mtime >= started:
                return True
        return False

    def note(d):
        write_json(rd / "guard.json", dict(d, at=now(), item=a.id))

    rc = guard_run(cmd, lambda: live_cost(clone, t0), lambda: ledger_closed(a.id), broaden, limit("round_usd"),
                   limit("broaden_usd"), limit("poll_s"), note)
    return rc


def rerun_ok_cmd(a):
    blocked = (REPO / a.dir / "BLOCKED.md").exists() and (REPO / a.dir / "BLOCKED.md").stat().st_size > 0
    ok, why = rerun_ok(int(a.n), a.rc, a.fp0, a.fp1, blocked)
    print(("RERUN " if ok else "NO-RERUN ") + why)
    return 0 if ok else 1


def fingerprint_of(d):
    import hashlib
    h = hashlib.sha1()
    rc, head = sh(["git", "rev-parse", "HEAD"])
    rc, st = sh(["git", "status", "--porcelain", "--untracked-files=all"])
    h.update((head + "\n" + st).encode())
    for line in st.splitlines():
        f = REPO / line[3:].strip().split(" -> ")[-1]
        try:
            h.update(("%s %d %d" % (f, f.stat().st_size, f.stat().st_mtime_ns)).encode())
        except OSError:
            pass
    return h.hexdigest()[:16]


def rerun_ok(n_done, rc, fp0, fp1, blocked, max_runs=None):
    """-> (ok, reason): may the failed run n_done be run again? At most max_runs runs, never after a cap or a close,
    never after BLOCKED, and only when the run left something new behind (fingerprint changed)."""
    max_runs = limit("max_runs") if max_runs is None else max_runs
    if str(rc) in ("90", "91", "92"):
        return False, "exit %s is a hard stop, not a failure" % rc
    if n_done >= max_runs:
        return False, "run %d of %d done: no more reruns" % (n_done, max_runs)
    if blocked:
        return False, "BLOCKED.md names a blocker: a rerun has no new information"
    if fp0 == fp1:
        return False, "the run left nothing new (same commit, tree and Whittle files): no new information"
    return True, "rerun %d of %d: the run changed the tree" % (n_done + 1, max_runs)


def human(n):
    return "%.2fM" % (n / 1e6) if n >= 1e6 else "%dk" % round(n / 1e3)


def spend(a):
    s = spend_of(a.rd, a.clone or REPO)
    write_json(Path(a.rd) / "spend.json", s)
    print("; ".join("%s %s raw / %s weighted / $%.2f" % (k, human(s[k]["raw"]), human(s[k]["weighted"]),
                                                          s[k]["cost_usd"]) for k in ("setup", "whittle", "wrapup",
                                                                                       "total")))
    # the loop's round end line takes this one (whittle_now reads its keys; tokens= stays the raw sum it always was)
    print("tokens=%d weighted=%d cost_usd=%.2f setup_usd=%.2f whittle_usd=%.2f wrapup_usd=%.2f" % (
        s["total"]["raw"], s["total"]["weighted"], s["total"]["cost_usd"], s["setup"]["cost_usd"],
        s["whittle"]["cost_usd"], s["wrapup"]["cost_usd"]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status")
    s.add_argument("worker")
    for k in ("state", "item", "note", "lane", "game", "unit", "machine"):
        s.add_argument("--" + k)
    s.add_argument("--round", type=int)
    s = sub.add_parser("log")
    s.add_argument("worker")
    s.add_argument("text", nargs="+")
    s = sub.add_parser("shortlist")
    s.add_argument("worker")
    s.add_argument("lane", choices=("fwlive", "offline"))
    s.add_argument("--n", type=int, default=12)
    s.add_argument("--why", action="store_true", help="print every skipped open item with its reason")
    s.add_argument("--no-pick", action="store_true", help="never do the pick here, even inside an old loop")
    s = sub.add_parser("gate")
    s.add_argument("worker")
    s.add_argument("lane", choices=("fwlive", "offline"))
    s.add_argument("ids", nargs="+")
    s = sub.add_parser("setup")
    s.add_argument("worker")
    s.add_argument("lane", choices=("fwlive", "offline"))
    s.add_argument("--round")
    s = sub.add_parser("release")
    s.add_argument("worker")
    s.add_argument("id")
    s.add_argument("--why", required=True)
    s = sub.add_parser("wrapup")
    s.add_argument("worker")
    s.add_argument("id")
    s.add_argument("--dir", required=True)
    s.add_argument("--rc", required=True)
    s.add_argument("--round")
    s = sub.add_parser("recent")
    s.add_argument("--hours", type=float)
    s.add_argument("--json", action="store_true")
    s = sub.add_parser("spend")
    s.add_argument("rd")
    s.add_argument("--clone")
    s = sub.add_parser("lane-open")
    s.add_argument("lane", choices=("fwlive", "offline"))
    for name in ("claim", "unclaim"):
        s = sub.add_parser(name)
        s.add_argument("worker")
        s.add_argument("id")
    s = sub.add_parser("mine")
    s.add_argument("worker")
    s = sub.add_parser("nonpass")
    s.add_argument("id")
    s = sub.add_parser("admission")
    s.add_argument("lane", nargs="?", default="fwlive")
    s.add_argument("--worker")
    s.add_argument("--out")
    s = sub.add_parser("limit")
    s.add_argument("name")
    s = sub.add_parser("guard")
    s.add_argument("worker")
    s.add_argument("id")
    s.add_argument("--rd", required=True)
    s.add_argument("--dir", required=True)
    s.add_argument("--clone")
    s.add_argument("run", nargs=argparse.REMAINDER)
    s = sub.add_parser("fingerprint")
    s.add_argument("dir")
    s = sub.add_parser("rerun-ok")
    for x in ("n", "rc", "fp0", "fp1", "dir"):
        s.add_argument(x)
    sub.add_parser("diskfree")
    sub.add_parser("hardstop")
    s = sub.add_parser("tokens")
    s.add_argument("logs", nargs="+")
    a = ap.parse_args(argv)
    if REMOTE and a.cmd in ("status", "log", "claim", "unclaim", "mine", "hardstop"):
        args = sys.argv[1:] if argv is None else argv
        try:
            r = subprocess.run(SSH + [REMOTE, "python3 %s %s" % (REMOTE_WC, shlex.join(args))], timeout=120)
        except (OSError, subprocess.SubprocessError) as e:
            print("could not reach %s: %s" % (REMOTE, e))
            return 2 if a.cmd == "hardstop" else 1
        # ssh's own failure (255) is never "no stop"
        return 2 if a.cmd == "hardstop" and r.returncode not in (0, 1) else r.returncode
    fn = {"status": status, "log": log, "shortlist": shortlist, "lane-open": lane_open, "claim": claim,
          "unclaim": unclaim, "mine": mine, "diskfree": diskfree, "hardstop": hardstop, "nonpass": nonpass, "tokens": tokens,
          "gate": gate_cmd, "setup": setup, "release": release, "wrapup": wrapup, "recent": recent,
          "spend": spend, "admission": admission, "guard": guard, "limit": lambda a: print(limit(a.name)),
          "fingerprint": lambda a: print(fingerprint_of(a.dir)), "rerun-ok": rerun_ok_cmd}[a.cmd]
    return fn(a) or 0


if __name__ == "__main__":
    sys.exit(main())
