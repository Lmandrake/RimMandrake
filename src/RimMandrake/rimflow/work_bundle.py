#!/usr/bin/env python3
"""work_bundle.py: work bundles. All ready tickets of one system, worked by one run in one context, restarted fresh from
its state file until each member has an outcome. No model and no tokens of its own.

Item RIMMANDRAKE_BATCH_ONE_MODS_OPEN_WORK_INTO_ONE_RUN_PIPELINE_SPLITS_PER_TICKET. Design
design/specs/2026-11-24-work-bundles/design.md (section 7: the owner's four decisions); page boundary.md beside it;
selftest selftest_work_bundle.py.

    python3 src/RimMandrake/rimflow/work_bundle.py sort <home | Mod | ID...> [--dry]   the reality sort (design step 0)
    python3 src/RimMandrake/rimflow/work_bundle.py launch <home | Mod | ID...> --why "..."   (= ./pipe bundle ...) the
                                                  sort, then ONE bundle of the ready rest; one live bundle per system
    python3 src/RimMandrake/rimflow/work_bundle.py context            the worker's guard: GO ON | SAVE AND RESTART | UNMEASURED
    python3 src/RimMandrake/rimflow/work_bundle.py step <bundle> "<step>"   the worker's step, shown on the page
    python3 src/RimMandrake/rimflow/work_bundle.py live <bundle> --for "<what>" -- CMD   CMD on the first free game
                                                  (ArchBig, then ArchSmall) under game_lock run; else UNRUN, recorded

A system is a home of list_home.py (pipeline:<part>, game:<need>, machine:<name>), a mod (mod:<folder>), or item:<ID>
for a ticket with no home. The sort runs each open member's test on this clone's build: a green test closes the member
as already fixed, with that commit named; a member with no runnable test is listed `no test` and never closed.
"""
import argparse
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
        sys.path.insert(0, _p)

ITEM = "RIMMANDRAKE_BATCH_ONE_MODS_OPEN_WORK_INTO_ONE_RUN_PIPELINE_SPLITS_PER_TICKET"
UNIT = "rm-work-bundle"
CLOSED = ("done", "dropped", "superseded")
SCRIPT_RX = re.compile(r"python3\s+((?:design|src|skills|infrastructure)/[^\s'\"`]+?\.py)(?=[\s'\"`]|$)")
NO_TEST_RX = re.compile(r"acceptance test:\s*none\b", re.I)
# A named script added this long before its ticket's filing still counts as written with it: the filing rule drafts the
# test first and files minutes later in the same run. budget: danger=a script written for another purpose shortly
# before the ticket reads as its acceptance test; longest=UNMEASURED (the gap between writing a test and filing)
WRITTEN_WITH_SLACK_S = 6 * 3600
TEST_SECTIONS = re.compile(r"^## (?:verify|criteria|acceptance)[^\n]*\n(.*?)(?=^## |\Z)", re.M | re.S | re.I)
# Hang guard for one `rimflow close` (a publish retries a push): list_effect.CLOSE_TIMEOUT_S, the class=publish.
CLOSE_TIMEOUT_S = 21600  # budget: class=publish


def _one(s, n):
    s = " ".join(str(s or "").split())
    return s if len(s) <= n else s[: n - 1] + "…"


def _g(x, k, default=None):
    return x.get(k, default) if isinstance(x, dict) else getattr(x, k, default)


# ---- systems --------------------------------------------------------------------------------------------------------

def system_of(it, reading):
    """-> the system of one ticket: its mod (mod:<Mod>, mod_work's one rule), else its home, else item:<ID>. None when
    its mod work could not be read."""
    r = reading(it)
    if not isinstance(r, dict) or r.get("unreadable"):
        return None
    if r.get("mod"):
        return "mod:%s" % r["mod"]
    home = _g(it, "home")
    h = home.get("home") if isinstance(home, dict) else None
    if h and h != "unplaced":
        return h
    return "item:%s" % _g(it, "id")


def resolve(target, items, mods, reading):
    """-> (system, [open member ids], why). target: a home, a mod name (or mod:<Mod>), or a list of ids. Ids of two
    systems are refused (system None), and why names each id's system."""
    if isinstance(target, (list, tuple)) and len(target) == 1 and not re.match(r"^[A-Z][A-Z0-9_]{7,}$", target[0]):
        target = target[0]
    if isinstance(target, (list, tuple)):
        got, sy = [], {}
        for i in target:
            x = items.get(i)
            if x is None:
                return None, [], "%s is not an item of the ledger" % i
            if _g(x, "state") in CLOSED:
                return None, [], "%s is %s" % (i, _g(x, "state"))
            s = system_of(x, reading)
            if s is None:
                return None, [], "could not look which system %s belongs to" % i
            sy[i] = s
            got.append(i)
        if len(set(sy.values())) > 1:
            return None, [], "two systems are never in one bundle: " + "; ".join("%s is %s" % kv for kv in sy.items())
        return next(iter(sy.values())), got, "the named tickets"
    t = str(target)
    if not t.startswith(("mod:", "pipeline:", "game:", "machine:", "item:")):
        m = next((m for m in mods if m.lower() == t.lower()), None)
        if not m:
            return None, [], "%r is not a home (pipeline:<part>, game:<need>, machine:<name>), a mod or ticket ids" % t
        t = "mod:%s" % m
    ids = sorted(i for i, x in items.items() if _g(x, "state") not in CLOSED and system_of(x, reading) == t)
    return t, ids, "the open tickets of %s" % t


# ---- part 1: the reality sort ---------------------------------------------------------------------------------------

def test_of(it, prose, exists=None):
    """-> ("effect", check) | ("script", repo path) | None: the ticket's outcome check, else the first existing
    `python3 <repo path>.py` in its ## verify, ## criteria or ## acceptance prose."""
    if _g(it, "effect"):
        return "effect", _g(it, "effect")
    exists = exists or (lambda p: os.path.isfile(os.path.join(REPO, p)))
    secs = TEST_SECTIONS.findall(prose or "")
    if any(NO_TEST_RX.search(sec) for sec in secs):     # the absence is a decision: a script named there is no test
        return None
    for sec in secs:
        for p in SCRIPT_RX.findall(sec):
            if exists(p):
                return "script", p
    return None


def run_script(path, root):
    """-> (holds|fails|unmeasured, output) of `python3 <path>` with no arguments, from root."""
    import list_effect as LE     # one named script is run as an outcome check is, under the checks' own hang guard
    try:
        r = subprocess.run([sys.executable, path], cwd=root, capture_output=True, text=True, errors="replace",
                           timeout=LE.CMD_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return "unmeasured", "it ran past its %ds hang guard" % LE.CMD_TIMEOUT_S
    except OSError as e:
        return "unmeasured", "it could not start: %s" % e
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    if r.returncode in (0, 1):
        return ("holds" if r.returncode == 0 else "fails"), out
    return "unmeasured", "exit %d (only 0 holds and 1 fails)\n%s" % (r.returncode, out)


def _ts(iso):
    """-> the epoch of an ISO time; raises ValueError when it cannot be read (the caller says so)."""
    import datetime as dt
    return dt.datetime.fromisoformat(str(iso).replace("Z", "+00:00")).timestamp()


def added_at_git(path, root=REPO):
    """-> the epoch of the commit that first added `path`; raises when git cannot say (the caller says so)."""
    import time_budget as TB
    r = subprocess.run(["git", "-C", root, "log", "--diff-filter=A", "--format=%ct", "--", path], capture_output=True,
                       text=True, timeout=TB.CALL_S, stdin=subprocess.DEVNULL)
    ts = [int(x) for x in r.stdout.split()] if r.returncode == 0 else []
    if not ts:
        raise RuntimeError("git log names no commit that added %s (exit %d)" % (path, r.returncode))
    return min(ts)


def sort(ids, items, prose_of, run_effect, run_script_fn, root=REPO, exists=None, added_at=None):
    """-> one row per member: {id, test, verdict: holds|holds_unproven|fails|unmeasured|no_test, why}. Each test runs
    once. An outcome check was seen failing when it was attached (list_effect.attach_gate); a named script was not, so a
    green one counts only when it was added with or after its ticket (WRITTEN_WITH_SLACK_S), else holds_unproven."""
    added_at = added_at or (lambda p: added_at_git(p, root))
    import list_effect as LE
    rows = []
    for i in ids:
        it = items[i]
        t = test_of(it, prose_of(i), exists)
        if not t:
            rows.append({"id": i, "test": None, "verdict": "no_test",
                         "why": "no outcome check, and no existing python3 <repo path>.py in its ## verify, ## criteria or "
                                "## acceptance"})
            continue
        kind, what = t
        if kind == "effect":
            p = LE.parse(what)
            if p.get("kind") == "cmd" and LE.VACUOUS.match(p["cmd"]):
                rows.append({"id": i, "test": what, "verdict": "unmeasured",
                             "why": "the check %r is vacuous: it holds whatever the work" % what})
                continue
            verdict, out = run_effect(what, root)
        else:
            verdict, out = run_script_fn(what, root)
            if verdict == "holds":
                try:
                    filed, born, cause = _ts(_g(it, "created_at")), added_at(what), None
                except Exception as e:  # noqa: BLE001 - not dated: never proven, and the row says why
                    filed = born = None
                    cause = "could not be dated against the filing (%s: %s)" % (type(e).__name__, _one(e, 120))
                if cause or born < filed - WRITTEN_WITH_SLACK_S:
                    verdict = "holds_unproven"
                    out = ("it holds, but it %s, so it was never seen failing on this ticket: the worker classes it"
                           % (cause or "was there before the ticket was filed"))
            what = "python3 %s" % what
        rows.append({"id": i, "test": what, "verdict": verdict, "why": _one(out, 300) or "(no output)"})
    return rows


def close_member(iid, sha, evidence):
    """`rimflow close <iid> --no-code "already fixed: ... at <sha>" --evidence ...` as the pipeline's act. -> (rc, output).
    The build the test ran on is named in the text, not in --sha: that build is often a ledger-only commit, which
    `close --sha` refuses, and the commit that did the work is not known to the sort (list_effect.close_item's form)."""
    argv = [sys.executable, os.path.join(HERE, "cli.py"), "close", iid, "--no-code",
            "already fixed: its test holds on the build %s (work_bundle sort)" % sha, "--evidence", evidence,
            "--seat", "BENCH", "--why", "pipeline act (work_bundle sort): its test holds at %s, so it was already fixed"
            % sha, "--reason", "already fixed: its test holds at %s (work_bundle sort)" % sha, "--publish"]
    env = dict(os.environ, RM_ROLE_UNIT=os.environ.get("RM_ROLE_UNIT") or UNIT, RIMFLOW_SEAT="BENCH")
    try:
        r = subprocess.run(argv, cwd=REPO, env=env, capture_output=True, text=True, errors="replace",
                           timeout=CLOSE_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired) as e:
        return 99, "%s: %s" % (type(e).__name__, e)
    return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()


def sort_apply(rows, sha, closer=close_member, dry=False):
    """Close each `holds` row as already fixed at `sha`. -> rows with `act`."""
    out = []
    for r in rows:
        r = dict(r)
        if r["verdict"] == "holds":
            ev = "%s holds at %s (work_bundle sort): %s" % (r["test"], sha, _one(r.get("why"), 200))
            if dry:
                r["act"] = "would close as already fixed at %s" % sha
            else:
                rc, said = closer(r["id"], sha, ev)
                r["act"] = ("closed as already fixed at %s" % sha if rc in (0, 4) else
                            "close REFUSED (rc %s): %s" % (rc, _one(said, 300)))
                r["closed"] = rc in (0, 4)
        elif r["verdict"] == "holds_unproven":
            r["act"] = "kept: green, but never seen failing on this ticket"
        elif r["verdict"] == "no_test":
            r["act"] = "listed no test"
        elif r["verdict"] == "fails":
            r["act"] = "kept: its test fails"
        else:
            r["act"] = "kept: its test is unmeasured"
        out.append(r)
    return out


def build_sha(root=REPO):
    """-> (sha, None) when the clone stands level on origin/main with no tracked change, else (None, the fault and its
    repair): a close names a published commit, and a test run on local changes is not that commit's reading."""
    def git(*a):
        import time_budget as TB
        return subprocess.run(["git", "-C", root] + list(a), capture_output=True, text=True, timeout=TB.CALL_S,
                              stdin=subprocess.DEVNULL)
    head, main = git("rev-parse", "HEAD"), git("rev-parse", "origin/main")
    if head.returncode or main.returncode:
        return None, "could not read HEAD or origin/main in %s" % root
    dirty = git("status", "--porcelain", "--untracked-files=no").stdout.strip()
    if head.stdout.strip() != main.stdout.strip() or dirty:
        return None, ("the clone is not level with origin/main%s; run ./sync (or publish your changes), then sort again"
                      % (" and has tracked changes" if dirty else ""))
    return head.stdout.strip()[:10], None


# ---- part 2: the record and the launcher ----------------------------------------------------------------------------

ROLE = "src/RimMandrake/rimflow/roles/bundle_worker.md"
STATE_FILES = "infrastructure/bundles"
ENV = "RM_WORK_BUNDLE"
LIVE_STATES = ("launching", "live", "restarting")
REFUSED_HEAD = "REFUSED BY BUNDLE:"
REFUSED_HEADS = (REFUSED_HEAD, "BUNDLE REFUSED:")     # the role (roles/bundle_worker.md) writes the first


def store_dir(create=True):
    d = os.environ.get("RM_WORK_BUNDLE_DIR")
    if not d:
        import doorbell
        d = os.path.join(doorbell.state_dir(), "work_bundle")
    d = os.path.join(d, "bundles")
    if create:
        os.makedirs(d, exist_ok=True)
    return d


def store_path(bid):
    return os.path.join(store_dir(), bid + ".json")


def store_write(rec):
    p = store_path(rec["id"])
    with open(p + ".tmp", "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1, ensure_ascii=False, sort_keys=True)
    os.replace(p + ".tmp", p)
    return rec


def store_read(bid):
    """-> the record, or None when there is none; raises when it exists and cannot be read (could not look)."""
    p = store_path(bid)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def all_bundles():
    """-> {id: record} of every bundle in the store; raises when the store cannot be read."""
    d = store_dir()
    out = {}
    for n in sorted(os.listdir(d)):
        if n.endswith(".json"):
            with open(os.path.join(d, n), encoding="utf-8") as f:
                r = json.load(f)
            out[r["id"]] = r
    return out


def live_bundles(bundles=None):
    """-> {system: bundle id} of the bundles that are launching, live or restarting."""
    bundles = all_bundles() if bundles is None else bundles
    return {r["system"]: r["id"] for r in bundles.values() if r.get("state") in LIVE_STATES}


def bundle_id(system, now):
    slug = re.sub(r"[^A-Za-z0-9]+", "-", system).strip("-")
    return "WB-%s-%s" % (slug, time.strftime("%Y%m%d-%H%M%S", time.gmtime(now)))


def new_record(system, members, why, pipeline, now, launched_by=None):
    bid = bundle_id(system, now)
    return {"schema": 1, "id": bid, "system": system, "pipeline": pipeline, "members": list(members),
            "lead": members[0], "why": why, "at": now, "launched_by": launched_by or os.environ.get("RM_ROLE_UNIT") or "hand",
            "state": "launching", "step": "launched", "state_file": "%s/%s.md" % (STATE_FILES, bid), "units": [],
            "restarts": 0, "outcomes": {}}


def ready_split(ids, items, now, refused, held, leased):
    """-> ([ready ids], {left-out id: reason}). refused(id) -> the refusal text since its last other event or None;
    held(id) -> the owner's hold text or None; leased(item) -> True under another live lease."""
    ready, out = [], {}
    for i in ids:
        it = items[i]
        wu = _g(it, "wait_until")
        try:
            ahead = bool(wu) and _ts(wu) > now
        except ValueError:
            out[i] = "its wait date %r cannot be read" % wu
            continue
        why = (("it is under another live lease (%s)" % _g(it, "owner")) if leased(it) else
               ("it waits until %s: %s" % (wu, _g(it, "wait_reason") or "no reason given")) if ahead else
               ("it is blocked: %s" % (_g(it, "blocked_reason") or "no reason given")) if _g(it, "blocked") else
               refused(i) or held(i))
        if why:
            out[i] = why
        else:
            ready.append(i)
    return ready, out


def brief(rec, items, tests):
    """The bundle run's brief: the role, the members with their tests, the state file. No spend, cap or remainder."""
    rows = []
    for i in rec["members"]:
        t = tests.get(i)
        rows.append("- `%s` %s\n  test: %s" % (i, _one(_g(items.get(i), "title"), 160),
                                              t or "no test (step 1: class it; write its test if it is real)"))
    return """You are the worker of work bundle {bid}: all the ready tickets of one system, {system}, in one run.

Read your role first and follow it step by step: {role}

The bundle id is {bid}. Its state file is {sf}: read it first if it exists (a restart), and write it after each group.
Your first ticket is `{lead}`: claim it before anything else
(`python3 src/RimMandrake/rimflow/cli.py claim {lead} --seat BENCH --why "work bundle {bid}" --publish`).

The members ({n}), each with its own test and its own close:
{rows}

Why this bundle: {why}
""".format(bid=rec["id"], system=rec["system"], role=ROLE, sf=rec["state_file"], lead=rec["lead"], n=len(rec["members"]),
           rows="\n".join(rows), why=rec["why"])


def tests_text(ids, items, prose_of):
    out = {}
    for i in ids:
        t = test_of(items[i], prose_of(i))
        out[i] = None if not t else t[1] if t[0] == "effect" else "python3 %s" % t[1]
    return out


def launch_run(rec, text, model="opus", cap=None, seat="BENCH", mod=None, next_act_owner=None):
    """Start the bundle's first run: one detached helper on the lead, RM_WORK_BUNDLE in its env. -> (rc, out, unit)."""
    import time_budget as TB
    d = os.path.join(os.path.dirname(store_dir()), "briefs")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "%s.md" % rec["id"])
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    if cap is None:
        import list_dispatch as LD
        cap = LD.load_cfg()["%s_cap_usd" % model]     # the lane's per-run stop; no guessed number
    argv = [sys.executable, os.path.join(HERE, "detached_helper.py"), "launch", "--seat", seat, "--item", rec["lead"],
            "--brief-file", path, "--model", model, "--budget-usd", "%g" % cap, "--env", "%s=%s" % (ENV, rec["id"])]
    if mod:
        argv += ["--env", "RM_CONTROL_MOD=%s" % mod]
    if next_act_owner:
        argv += ["--next-act-owner", next_act_owner]
    r = subprocess.run(argv, capture_output=True, text=True, timeout=TB.LAUNCH_S, stdin=subprocess.DEVNULL)
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    m = re.search(r"^DETACHED (\S+)", r.stdout or "", re.M)
    return r.returncode, out, (m.group(1) if m and not r.returncode else None)


def _lock():
    import fcntl
    f = open(os.path.join(os.path.dirname(store_dir()), "launch.lock"), "w")
    fcntl.flock(f, fcntl.LOCK_EX)
    return f


def launch_bundle(system, members, items, why, pipeline, now=None, launcher=None, tests=None, launched_by=None):
    """One bundle for `system`: refused (2, why) while another bundle of it is live; else the record is written, then
    the run starts. -> (0, record) | (1, record with launch_failed) | (2, why)."""
    now = time.time() if now is None else now
    if not members:
        return 2, "%s has no ready member" % system
    lk = _lock()
    try:
        live = live_bundles()
        if system in live:
            return 2, "%s already has a live bundle, %s; one live bundle per system" % (system, live[system])
        rec = new_record(system, members, why, pipeline, now, launched_by)
        for old in all_bundles().values():      # a gated bundle of this system is the new one's to carry on
            if old.get("system") == system and old.get("state") == "gated":
                store_write(dict(old, state="replaced", replaced_by=rec["id"]))
        store_write(rec)
    finally:
        lk.close()
    text = brief(rec, items, tests or {i: _g(items.get(i), "effect") for i in members})
    rc, out, unit = (launcher or (lambda r, b: launch_run(r, b)))(rec, text)
    rec = store_read(rec["id"]) or rec
    if rc == 0 and unit:
        rec.update(state="live", units=[{"unit": unit, "at": now, "kind": "launch", "ended_before": 0}])
        store_write(rec)
        return 0, rec
    rec.update(state="launch_failed", launch_out=_one(out, 600) or "rc %s" % rc)
    store_write(rec)
    return 1, rec


def group(rows, launches, systems, live):
    """The lane's launch rows of one system become one bundle. -> (rows, launches). systems: {item: system}; live:
    {system: live bundle id}. Pure; edits the rows in place."""
    lead, keep = {}, []
    for r in rows:
        i = r["item"]
        if r.get("kind") == "shape" or i not in systems:
            if i in launches:
                keep.append(i)
            continue
        s = systems[i]
        if r["decision"] not in ("launch", "slots_full"):
            continue
        if s in live:
            r.update(decision="bundle_live", why="waits for the live bundle %s of %s; it joins the next one" % (live[s], s))
        elif r["decision"] == "launch" and s not in lead:
            if r.get("host"):
                r.pop("host")
                r.update(decision="slots_full", why="a work bundle runs on this machine only (its record and its restart "
                                                    "are here), and the lane's own slots are full")
                continue
            lead[s] = r
            r["bundle"] = {"system": s, "members": [i]}
            keep.append(i)
        elif s in lead:
            lead[s]["bundle"]["members"].append(i)
            r.update(decision="bundled", why="joins the bundle of %s that %s leads this tick" % (s, lead[s]["item"]))
    return rows, [i for i in launches if i in keep]


def overlay(runs, ids, bundles, live):
    """Fill runs[member] for the lane: "bundle" (its live bundle's id) and the units of every bundle it was in, under
    "live" or "ended" by live(unit), so the lane's own run count reads a bundle run as that member's run."""
    runs = dict(runs or {})
    want = set(ids)
    for b in bundles.values():
        for m in b.get("members") or []:
            if m not in want:
                continue
            r = runs.setdefault(m, {"live": [], "ended": []})
            r.setdefault("live", [])
            r.setdefault("ended", [])
            for u in b.get("units") or []:
                key = "live" if live(u["unit"]) else "ended"
                if u["unit"] not in r["live"] + r["ended"] and key == "ended":
                    r["ended"].append(u["unit"])
            if b.get("state") in LIVE_STATES:
                r["bundle"] = b["id"]
            elif b.get("state") == "gated" and (b.get("outcomes") or {}).get(m, {}).get("outcome", "open") == "open":
                r["bundle_resume"] = b["id"]      # a gate refused its restart: the lane owes it one more run
            if (b.get("outcomes") or {}).get(m, {}).get("outcome") == "refused":
                r["bundle_refused"] = {"id": b["id"], "why": b["outcomes"][m].get("why")}
    return runs


def refusals(events):
    """-> {id: the newest BUNDLE REFUSED: note's text} for each ticket whose refusal is newer than its last other
    event that is not a note (a re-home, an effect, a reopen starts it again). Pure over the ledger's events."""
    last_other, refused = {}, {}
    for e in events:
        i = e.get("id")
        try:
            t = _ts(e.get("ts"))
        except (TypeError, ValueError):
            continue        # an event with no readable time orders nothing; the refusal it may be is not read
        if not i:
            continue
        if e.get("event") == "note":
            if str(e.get("text") or "").strip().upper().startswith(REFUSED_HEADS):
                refused[i] = (t, str(e.get("text")).strip())
        elif t >= last_other.get(i, 0):
            last_other[i] = t
    return {i: txt for i, (t, txt) in refused.items() if t > last_other.get(i, 0)}


def member_held(it, reading, held):
    """-> why a member's own mod is held by the owner, or None; a mod that cannot be read is said, never "not held"."""
    r = reading(it)
    if not isinstance(r, dict) or r.get("unreadable"):
        return "could not look which mod it belongs to: %s" % (r.get("unreadable") if isinstance(r, dict) else r)
    return "HELD BY OWNER: %s" % r["mod"] if r.get("mod") and held(r["mod"]) else None


def mod_gate(mod):
    """-> why a bundle of `mod` may not launch now (the owner's hold, a `pipe off`: the readiness switch), or None."""
    import control as C
    import mod_owner_hold as MOH
    h = MOH.held(mod)
    if h:
        return "HELD BY OWNER: %s (%s)" % (mod, _one(h.get("said"), 120))
    why = C.blocked({"family": "detached", "mod": mod})
    return ("%s is off (%s); a mod's readiness list must read READY before it runs" % (mod, why)) if why else None


def cmd_launch(o):
    """The hand launch, `./pipe bundle <home | Mod | ID...> --why "..."`: the sort first, then one bundle of the
    ready rest."""
    import list_effect as LE
    import model as LM
    now = time.time()
    w = world()
    modset, reading = mod_reader()
    system, ids, why = resolve(o.target if len(o.target) > 1 else o.target[0], w.items, modset, reading)
    if not system:
        print("REFUSED: %s" % why)
        return 2
    mod = system.split(":", 1)[1] if system.startswith("mod:") else None
    if mod:
        no = mod_gate(mod)
        if no:
            print("REFUSED: %s" % no)
            return 2
    prose = prose_reader()
    sha, fault = build_sha()
    rows = sort_apply(sort(ids, w.items, prose, LE.run, run_script, root=REPO), sha or "HEAD", dry=bool(fault))
    for r in rows:
        if r["verdict"] in ("holds", "holds_unproven", "unmeasured"):
            print("sort: %-62s %s" % (r["id"], r["act"]))
    if fault:
        print("sort ran dry (%s): its green members stay in the bundle, for the worker to close" % fault)
    gone = set(r["id"] for r in rows if r.get("closed"))
    rest = [i for i in ids if i not in gone]
    ref = refusals(LM.read())
    import mod_owner_hold as MOH
    ready, out = ready_split(rest, w.items, now, refused=ref.get,
                             held=lambda i: None if mod else member_held(w.items[i], reading, MOH.held),
                             leased=lambda it: _g(it, "state") == "doing" and LM.lease_status(it, now) == "live")
    for i, y in sorted(out.items()):
        print("left out: %-60s %s" % (i, _one(y, 160)))
    if not ready:
        print("NO BUNDLE: %s has no ready member (%d closed by the sort, %d left out)" % (system, len(gone), len(out)))
        return 0 if gone else 2
    tests = tests_text(ready, w.items, prose)
    pipeline = "maturation" if mod else "workshop"
    rc, rec = launch_bundle(system, ready, w.items, o.why, pipeline, now=now, tests=tests,
                            launcher=lambda r, b: launch_run(r, b, mod=mod), launched_by="hand")
    if rc == 2:
        print("REFUSED: %s" % rec)
        return 2
    if rc:
        print("LAUNCH FAILED %s: %s" % (rec["id"], rec.get("launch_out")))
        return 1
    print("BUNDLE %s of %s launched: %s; %d member(s): %s" % (rec["id"], system, rec["units"][0]["unit"], len(ready),
                                                              ", ".join(ready)))
    return 0


# ---- part 3: the worker's context guard and its step ----------------------------------------------------------------

# The guard's line, a share of the window: past it the worker finishes its group, saves its state and restarts.
# budget: danger=a full context loses what the worker learned (design section 5: 480k after 18 tickets, measured
# budget: 2026-11-24); longest=UNMEASURED (the first bundles record their context per group)
SAVE_FRACTION = 0.5
WINDOW_RX = re.compile(r'"contextWindow"\s*:\s*([0-9]+)[^}]*?"canonicalModel"\s*:\s*"([^"]+)"')
# How many of the newest run result files are read for the window: each is a full result JSON. budget: danger=a scan
# budget: of every result file of a month reads hundreds of MB for one number; longest=UNMEASURED (one file holds it)
WINDOW_FILES_MOST = 40


def _session_model_tokens(transcript):
    """-> (context tokens of the last main-thread turn, its model) or (None, None)."""
    import detached_helper as DH
    tokens = DH.context_tokens(transcript) if os.path.isfile(transcript or "") else None
    model = None
    if tokens is not None:
        with open(transcript, encoding="utf-8", errors="replace") as f:
            for line in f:
                if '"model"' in line and '"isSidechain": true' not in line and '"isSidechain":true' not in line:
                    m = re.search(r'"model"\s*:\s*"([^"]+)"', line)
                    model = m.group(1) if m else model
    return tokens, model


def window_of(model, runs_dir):
    """-> (window tokens, None) from the newest run result files that name `model`, or (None, the cause)."""
    try:
        names = sorted((os.path.join(runs_dir, n) for n in os.listdir(runs_dir) if n.endswith((".out", ".out.json"))),
                       key=os.path.getmtime, reverse=True)[:WINDOW_FILES_MOST]
    except OSError as e:
        return None, "the run results in %s could not be listed (%s)" % (runs_dir, e)
    for p in names:
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                text = f.read()
        except OSError:
            continue
        for win, canon in WINDOW_RX.findall(text):
            if not model or canon == model or model.startswith(canon):
                return int(win), None
    return None, "no run result in %s names the window of %s" % (runs_dir, model or "this model")


def context_reading(transcript, runs_dir):
    """-> {tokens, window, model, verdict: GO ON | SAVE AND RESTART | UNMEASURED, why}."""
    tokens, model = _session_model_tokens(transcript)
    if tokens is None:
        return {"tokens": None, "window": None, "model": None, "verdict": "UNMEASURED",
                "why": "no main-thread usage in %s" % transcript}
    win, why = window_of(model, runs_dir)
    if win is None:
        return {"tokens": tokens, "window": None, "model": model, "verdict": "UNMEASURED", "why": why}
    over = tokens > win * SAVE_FRACTION
    return {"tokens": tokens, "window": win, "model": model, "verdict": "SAVE AND RESTART" if over else "GO ON",
            "why": "%d of %d tokens, the line is %d" % (tokens, win, int(win * SAVE_FRACTION))}


def cmd_context(o):
    import detached_helper as DH
    sid = o.session or os.environ.get("CLAUDE_CODE_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID")
    t = DH.find_transcript(sid) if sid else None
    r = context_reading(t or "", DH.runs_dir())
    print("%s: context %s of window %s (%s); %s" % (r["verdict"], r["tokens"], r["window"], r.get("model") or "-", r["why"]))
    return 0 if r["verdict"] != "UNMEASURED" else 5


def cmd_step(o):
    """The worker writes its step on the record (the page shows it). A missing bundle is said, never made up."""
    lk = _lock()
    try:
        rec = store_read(o.bundle)
        if not rec:
            print("NO BUNDLE %s in %s" % (o.bundle, store_dir()))
            return 2
        rec["step"] = _one(o.step, 200)
        rec["step_at"] = time.time()
        store_write(rec)
    finally:
        lk.close()
    print("STEP %s: %s" % (o.bundle, rec["step"]))
    return 0


# ---- part 4: outcomes, restart and the guard on progress ------------------------------------------------------------

HAND_KILL_RX = re.compile(r"^killed: (?!(?:signal|unknown)\b)")     # mark_killed writes its reason; a death reads signal
READ_MEMBERS = r"""
import json, os, sys
sys.path.insert(0, os.path.join("src", "RimMandrake", "rimflow"))
import model
evs = model.read()
items = model.replay(evs).items
out = {}
for i in sys.argv[1:]:
    x = items.get(i)
    out[i] = None if x is None else {"state": x.state, "wait_until": x.wait_until, "wait_ts": None, "refusal": None,
                                     "refusal_ts": None}
for e in evs:
    f = out.get(e.get("id"))
    if f is None:
        continue
    if e.get("event") == "wait":
        f["wait_ts"] = e.get("ts")
    elif e.get("event") == "note" and str(e.get("text") or "").strip().upper().startswith(("REFUSED BY BUNDLE:", "BUNDLE REFUSED:")):
        f["refusal"], f["refusal_ts"] = str(e.get("text")).strip(), e.get("ts")
print(json.dumps(out))
"""


def read_members(clone, ids):
    """-> {id: facts or None} as the run's clone folds its ledger (the run's own closes sit there first); raises when the
    ledger there cannot be read."""
    import time_budget as TB
    r = subprocess.run([sys.executable, "-c", READ_MEMBERS] + list(ids), cwd=clone, capture_output=True, text=True,
                       timeout=TB.RIMFLOW_S, stdin=subprocess.DEVNULL)
    if r.returncode:
        raise RuntimeError("the member read in %s exited %d: %s" % (clone, r.returncode, _one(r.stderr, 300)))
    return json.loads(r.stdout)


def _when(v):
    """-> epoch of an epoch or ISO value; raises ValueError when it cannot be read."""
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    return _ts(v)


def outcomes(rec, facts, now):
    """-> {member: {"outcome", "why"}}: fixed | already_fixed | dropped | refused | waits | open | unread. A refusal or
    wait counts only when written since the bundle began."""
    out, since = {}, rec.get("at") or 0
    for m in rec["members"]:
        f = (facts or {}).get(m)
        if not isinstance(f, dict):
            out[m] = {"outcome": "unread", "why": "its ledger state could not be read"}
            continue
        st = f.get("state")
        try:
            refused = bool(f.get("refusal")) and _when(f.get("refusal_ts")) >= since
            waits = bool(f.get("wait_until")) and _when(f["wait_until"]) > now and _when(f.get("wait_ts")) >= since
        except (TypeError, ValueError) as e:
            out[m] = {"outcome": "unread", "why": "a time on it could not be read (%s)" % e}
            continue
        if st == "done":
            out[m] = {"outcome": "already_fixed" if m in (rec.get("sort_closed") or []) else "fixed", "why": "closed done"}
        elif st in ("dropped", "superseded"):
            out[m] = {"outcome": "dropped", "why": "closed %s" % st}
        elif refused:
            out[m] = {"outcome": "refused", "why": f["refusal"]}
        elif waits:
            out[m] = {"outcome": "waits", "why": "a dated wait to %s" % f["wait_until"]}
        else:
            out[m] = {"outcome": "open", "why": "no close, refusal or wait since the bundle began"}
    return out


def plan_restart(rec, facts, run, now):
    """-> {act: end | restart | raise | none, why, target?, open, outcomes, ended_now}. Pure over its inputs."""
    o = outcomes(rec, facts, now)
    opened = [m for m in rec["members"] if o[m]["outcome"] == "open"]
    unread = [m for m in rec["members"] if o[m]["outcome"] == "unread"]
    ended = len(rec["members"]) - len(opened) - len(unread)
    base = {"open": opened, "outcomes": o, "ended_now": ended}
    if unread:
        return dict(base, act="raise", why="could not look at %s (%s); nothing is decided on a member it cannot read" % (
            ", ".join(unread), o[unread[0]]["why"]))
    if not opened:
        return dict(base, act="end", why="every member has an outcome: " + ", ".join(
            "%s %s" % (m, o[m]["outcome"]) for m in rec["members"]))
    res = str(run.get("result") or "")
    if HAND_KILL_RX.match(res):
        return dict(base, act="none", why="stopped by hand (%s): a stop is not restarted" % _one(res, 160))
    unit = next((u for u in rec.get("units") or [] if u.get("unit") == run.get("unit")), None)
    if unit and unit.get("kind") == "restart" and ended <= int(unit.get("ended_before") or 0):
        return dict(base, act="raise", why="restart %s of bundle %s ended no member (still open: %s); a restart that "
                                           "ends none is not restarted again" % (run.get("unit"), rec["id"], ", ".join(opened)))
    return dict(base, act="restart", target=opened[0], why="%d member(s) still open (%s)" % (len(opened), ", ".join(opened)))


def conductor_say(line, now=None):
    import detached_helper as DH
    DH.conductor_line(line, now or time.time(), head="WORK BUNDLE")


def note_end(bid, q, unit, now, say=None):
    """Write what a run's end decided on the record: outcomes, the unit's count, the state; each refusal and a raise
    reach the Conductor log once."""
    say = say or (lambda line: conductor_say(line, now))
    lk = _lock()
    try:
        rec = store_read(bid)
        if not rec:
            return None
        rec["outcomes"] = q.get("outcomes") or rec.get("outcomes") or {}
        rec["outcomes_at"] = now
        for u in rec.get("units") or []:
            if u.get("unit") == unit:
                u.update(ended_after=q.get("ended_now"), end_act=q["act"])
        rec["state"] = {"end": "ended", "raise": "raised", "restart": "restarting", "none": "stopped",
                        "gated": "gated"}[q["act"]]
        if q["act"] == "raise":
            rec["raised"] = {"at": now, "why": q["why"]}
        told = set(rec.get("told") or [])
        lines = []
        for m in rec["members"]:
            oc = rec["outcomes"].get(m) or {}
            if oc.get("outcome") == "refused" and m not in told:
                lines.append("work bundle %s (%s): %s refused: %s" % (bid, rec["system"], m, _one(oc.get("why"), 400)))
                told.add(m)
        if q["act"] == "raise" and "raise" not in told:
            lines.append("ALARM work bundle %s (%s) is not restarted: %s. Look at its state file %s; restart it by hand "
                         "with `./pipe bundle <ids> --why ...` or end it" % (bid, rec["system"], q["why"], rec["state_file"]))
            told.add("raise")
        if rec["state"] in ("ended", "stopped", "gated") and "end:%s" % rec["state"] not in told:
            lines.append("work bundle %s (%s) %s: %s" % (bid, rec["system"], rec["state"].upper(), _one(q["why"], 400)))
            told.add("end:%s" % rec["state"])
        rec["told"] = sorted(told)
        store_write(rec)
    finally:
        lk.close()
    for line in lines:
        try:
            say(line)
        except Exception as e:  # noqa: BLE001 - the record keeps the outcome; the line is said on stderr
            print("work_bundle: conductor line not written (%s): %s" % (e, line), file=sys.stderr)
    return rec


def note_restart(bid, unit, now, ended_before):
    lk = _lock()
    try:
        rec = store_read(bid)
        if not rec:
            return None
        rec["units"] = (rec.get("units") or []) + [{"unit": unit, "at": now, "kind": "restart", "ended_before": ended_before}]
        rec.update(state="live", restarts=int(rec.get("restarts") or 0) + 1)
        return store_write(rec)
    finally:
        lk.close()


def loc_plan(rec, facts, now, gates, base, gate_no):
    """left_open_continue.plan's bundle branch: the bundle's rule decides, LOC's gates still bind. -> a LOC plan."""
    bid = (rec.get("env") or {}).get(ENV)
    try:
        b = store_read(bid)
    except Exception as e:  # noqa: BLE001
        return dict(base, act="alarm", bundle=bid, why="work bundle %s: its record could not be read (%s)" % (bid, e))
    if not b:
        return dict(base, act="alarm", bundle=bid, why="work bundle %s has no record in %s" % (bid, store_dir()))
    q = plan_restart(b, facts, rec, now)
    out = dict(base, bundle=bid, bundle_plan=q, state_file=b["state_file"], open_lane=q["open"], kind="bundle")
    if q["act"] == "end":
        return dict(out, act="none", why=q["why"])
    if q["act"] == "none":
        return dict(out, act="none", why=q["why"])
    if q["act"] == "raise":
        return dict(out, act="alarm", why=q["why"])
    no = gate_no(rec, q["target"], gates)
    if no:
        return dict(out, act="none", why=no, bundle_plan=dict(q, act="gated", why=no))
    import left_open_continue as LOC
    return dict(out, act="continue", target=q["target"], capped=LOC.capped(rec), note=None, progress=[],
                n=int(rec.get("continue_n") or 0) + 1, why="work bundle %s: %s" % (bid, q["why"]))


def members_of_run(rec):
    """-> the bundle's members for a run record that carries RM_WORK_BUNDLE, or []."""
    bid = (rec.get("env") or {}).get(ENV)
    b = store_read(bid) if bid else None
    return list(b["members"]) if b else []


# ---- part 5: the live pass ------------------------------------------------------------------------------------------

GAMES = ("ArchBig", "ArchSmall")      # this machine's games; Steve1 and Steve2 go through the SteveDesktop test lane


def game_query(game):
    """-> (exit, line) of `game_lock.py query <game>`: 0 free, 75 held, 3 his hold, 2 could not look."""
    import time_budget as TB
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, "game_lock.py"), "query", game], capture_output=True,
                           text=True, timeout=TB.CALL_S, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as e:
        return 2, "%s: could not look (%s: %s)" % (game, type(e).__name__, e)
    return r.returncode, _one((r.stdout or "") + (r.stderr or ""), 300)


def run_held(argv):
    """-> the exit of one live check held by game_lock run; 124 when it ran past its hang guard (the deploy class: a
    hung run holds the game it drives, like a hung deploy holds the game copy)."""
    import time_budget as TB
    try:
        return subprocess.run(argv, stdin=subprocess.DEVNULL, timeout=TB.DEPLOY_S).returncode
    except subprocess.TimeoutExpired:
        print("work_bundle live: the check ran past its %ds hang guard (time_budget deploy class)" % TB.DEPLOY_S,
              file=sys.stderr)
        return 124


def live_pass(bid, what, cmd, query=game_query, runner=None, now=None):
    """Run `cmd` on the first free game, held by `game_lock.py run` for its life; or run nothing and record UNRUN with
    the exact command and each game's answer. -> the check's exit, or 4 for UNRUN."""
    import shlex
    now = time.time() if now is None else now
    runner = runner or run_held
    answers, game = {}, None
    for g in GAMES:
        code, line = query(g)
        answers[g] = "exit %d: %s" % (code, line)
        if code == 0:
            game = g
            break
    text = " ".join(shlex.quote(c) for c in cmd)
    if game:
        rc = runner([sys.executable, os.path.join(HERE, "game_lock.py"), "run", game, "--for",
                     "work bundle %s: %s" % (bid, what), "--"] + list(cmd))
        row = {"at": now, "game": game, "for": what, "cmd": text, "rc": rc}
    else:
        rc = 4
        row = {"at": now, "unrun": True, "for": what, "cmd": text, "answers": answers}
    lk = _lock()
    try:
        rec = store_read(bid)
        if rec:
            rec["live_runs"] = (rec.get("live_runs") or []) + [row]
            store_write(rec)
    finally:
        lk.close()
    if game:
        print("LIVE %s on %s: exit %s | %s" % (bid, game, rc, text))
    else:
        print("UNRUN %s: no game is free; the command: %s | %s" % (bid, text, " | ".join(
            "%s %s" % kv for kv in answers.items())))
    return rc


def cmd_live(o):
    cmd = list(o.cmd)
    if not cmd:
        print("REFUSED: no command after --; the form: work_bundle.py live <bundle> --for \"<what>\" -- <command>")
        return 2
    return live_pass(o.bundle, o.what, cmd)


# ---- part 7: the page -----------------------------------------------------------------------------------------------

PAGE_TITLE = "Work bundles (one run per system; work_bundle.py)"
SHOWN_STATES_NOT = ("ended", "replaced")


def _unit_live(u):
    import detached_helper as DH
    rec = DH.read_record(u)
    return rec is None or DH.live_status(rec) in ("launching", "running")    # unread counts live: never "dead" unseen


def page_rows(now, bundles=None, unit_live=None, reader=None):
    """-> {"state": ok | unmeasured, "cause"?, "rows": [{id, system, state, step, restarts, members: [(id, outcome)],
    since}]}: one row per bundle that is not ended."""
    unit_live = unit_live or _unit_live
    if bundles is None:
        try:
            bundles = (reader or all_bundles)()
        except Exception as e:  # noqa: BLE001 - could not look: said, never an empty block
            return {"state": "unmeasured", "cause": "the work-bundle store could not be read (%s: %s)" % (
                type(e).__name__, _one(e, 160)), "rows": []}
    rows = []
    for b in sorted(bundles.values(), key=lambda b: b.get("at") or 0):
        if b.get("state") in SHOWN_STATES_NOT:
            continue
        st = b.get("state")
        units = b.get("units") or []
        if st in LIVE_STATES and units and not unit_live(units[-1]["unit"]) and st != "restarting":
            st = "%s, dead, no finish (unit %s is gone and its end was never recorded; `work_bundle` cannot restart it)" % (
                st, units[-1]["unit"])
        oc = b.get("outcomes") or {}
        rows.append({"id": b["id"], "system": b.get("system"), "state": st, "step": b.get("step") or "-",
                     "restarts": int(b.get("restarts") or 0), "since": b.get("at"),
                     "members": [(m, (oc.get(m) or {}).get("outcome") or "no outcome yet") for m in b.get("members") or []],
                     "unit": units[-1]["unit"] if units else None, "raised": (b.get("raised") or {}).get("why")})
    return {"state": "ok", "rows": rows}


def _line(r):
    mem = ", ".join("`%s` %s" % (m, o) for m, o in r["members"])
    return "**%s** · %s · %s · step: %s · restarts: %d · run: %s%s · members: %s" % (
        r["id"], r["system"], r["state"], r["step"], r["restarts"], r["unit"] or "-",
        (" · raised: %s" % _one(r["raised"], 200)) if r.get("raised") else "", mem)


def page_md(page):
    out = ["## " + PAGE_TITLE, ""]
    if page["state"] != "ok":
        return out + ["- UNMEASURED: %s." % page["cause"], ""]
    return out + (["- " + _line(r) for r in page["rows"]] or ["- none (looked: the work-bundle store; no bundle is open)"]) + [""]


def page_html(page):
    import html
    def inline(s):
        s = html.escape(str(s), quote=False)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
        return re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    if page["state"] != "ok":
        items = ["UNMEASURED: %s." % page["cause"]]
    else:
        items = [_line(r) for r in page["rows"]] or ["none (looked: the work-bundle store; no bundle is open)"]
    return "<h2>%s</h2><ul>%s</ul>" % (html.escape(PAGE_TITLE), "".join("<li>%s</li>" % inline(x) for x in items))


# ---- reading the ledger ---------------------------------------------------------------------------------------------

def world():
    import list_effect as LE
    return LE._world()


def prose_reader():
    import model as LM

    def read(iid):
        for d in (LM.ITEMS, getattr(LM, "CLOSED", os.path.join(LM.ITEMS, "closed"))):
            p = os.path.join(d, iid + ".md")
            if os.path.isfile(p):
                with open(p, encoding="utf-8", errors="replace") as f:
                    return f.read()
        return ""
    return read


def mod_reader():
    import mod_work as MW
    import model as LM
    modset = MW.mods()
    return modset, (lambda it: MW.reading(it, modset, LM.ITEMS))


# ---- the command ----------------------------------------------------------------------------------------------------

def cmd_sort(o):
    import list_effect as LE
    w = world()
    modset, reading = mod_reader()
    system, ids, why = resolve(o.target if len(o.target) > 1 else o.target[0], w.items, modset, reading)
    if not system:
        print("REFUSED: %s" % why)
        return 2
    sha, fault = build_sha()
    if fault and not o.dry:
        print("REFUSED (a fault of form; the repair): %s" % fault)
        return 3
    rows = sort(ids, w.items, prose_reader(), LE.run, run_script, root=REPO)
    rows = sort_apply(rows, sha or "HEAD", dry=o.dry)
    for r in rows:
        print("%-66s %-10s %s | %s" % (r["id"], r["verdict"], r["act"], _one(r.get("test") or "-", 90)))
    n = {}
    for r in rows:
        n[r["verdict"]] = n.get(r["verdict"], 0) + 1
    print("work_bundle sort%s %s: %d member(s); %s" % (" --dry" if o.dry else "", system, len(rows),
                                                       ", ".join("%s %d" % kv for kv in sorted(n.items()))))
    return 0


def parse(argv=None):
    """-> the parsed command line. `live`'s command is everything after the first `--`, split off before argparse
    (argparse.REMAINDER after a positional swallowed --for; measured 2026-11-25)."""
    argv = list(sys.argv[1:] if argv is None else argv)
    rest = []
    if argv[:1] == ["live"] and "--" in argv:
        k = argv.index("--")
        argv, rest = argv[:k], argv[k + 1:]
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sort", help="the reality sort: run each member's test, close the green ones as already fixed")
    s.add_argument("target", nargs="+", help="a home (pipeline:ledger), a mod (FlowWorks) or ticket ids of one system")
    s.add_argument("--dry", action="store_true", help="print what it would close; write nothing")
    s = sub.add_parser("launch", help="the hand launch (./pipe bundle): the sort, then one bundle of the ready rest")
    s.add_argument("target", nargs="+", help="a home, a mod or ticket ids of one system")
    s.add_argument("--why", required=True)
    s = sub.add_parser("context", help="the worker's guard: its context against half of its window")
    s.add_argument("--session", help="a session id (default: this session, CLAUDE_CODE_SESSION_ID)")
    s = sub.add_parser("step", help="the worker writes the step it is on, for the page")
    s.add_argument("bundle")
    s.add_argument("step")
    s = sub.add_parser("live", help="the live pass: one check on the first free game, or UNRUN with its command")
    s.add_argument("bundle")
    s.add_argument("--for", dest="what", required=True)
    o = ap.parse_args(argv)
    if o.cmd == "live":
        o.cmd = rest
        o.verb = "live"
    else:
        o.verb = o.cmd
    return o


def main(argv=None):
    o = parse(argv)
    return {"sort": cmd_sort, "launch": cmd_launch, "context": cmd_context, "step": cmd_step, "live": cmd_live}[o.verb](o)


if __name__ == "__main__":
    sys.exit(main())
