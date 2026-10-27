#!/usr/bin/env python3
"""isolated_evidence.py - the Arbiter's INDEPENDENT pre-step: re-run each done claim's checks in a private checkout
of its close sha, from a non-builder seat, with no AI (item EVIDENCE_TOOLS_WIRE_ISOLATED_CHECKOUT).

Why: since review AB2 (45eef6b97e6d) a run in a shared seat clone is never sha evidence (close_evidence.py, "origin.tree"):
a file can change and be restored mid-run. Making every pre-commit run pay an isolated checkout is the wrong price, so
the independent run belongs to the checker, not the builder: for each pending done claim (the latest `close` of an
item citing a sha), this makes a `close_evidence.make_isolated` checkout of that sha, runs the claim's selftests and
validators THERE, and the tools record close_evidence lines from that checkout under the runner seat (RIMFLOW_SEAT,
default DISPATCHER; RIMFLOW_ITEM = the item). The lines are then origin.tree "isolated", seat_from RIMFLOW_SEAT, and
count for arbiter_tiers G6 / G6_independent when the seat is not a maker of the claim.

What runs (deterministic, from the commit and the ledger only):
  * selftests  -- touched selftest*.py files; selftest files the item's close / verify / implemented / note text names
                  (run_selftests --only takes PATHS: a bare name resolves only when unique at the sha); and the sibling
                  `selftest_<stem>.py` of each touched `<stem>.py`. One `run_selftests.py --only ... --full` run.
  * validate_patch -- touched .xml under a Defs/ or Patches/ folder, with --defs over the install roots that exist
                  (DEFS_ROOTS_ENV, else the Steam RimWorld Data + Mods + workshop folders). No root -> not run: a
                  static run is a variant and never counts.
  * winbuild   -- touched .cs/.csproj are listed as OWED, never run here (a Windows build staged on D:).
Coverage (SELFTEST_EVIDENCE_FIX_COVERS_TESTS_ONLY): a selftest record covers its test files plus the sources the run
provably loaded (traced imports) or declares (evidence_covers.py). The plan's `predicted` / `uncovered` lists are a
static one-hop PREDICTION of that, for planning only; G6 reads what the run actually recorded.
The INSTRUMENTS are this clone's current run_selftests.py / validate_patch.py and close_evidence.py, never the copies
at the sha: a commit under test could change its own runner. The code under test is the checkout's.

Checkout cost, MEASURED 2026-10-27 on the bench clone (37,990 files, 3.67 GB working tree, objects shared):
ext4 (~/.seat-tmp) 12.6-14.7 s + 0.4 s delete; D: (drvfs) 312.4 s + 29.8 s delete. So checkouts go on ext4:
DEFAULT_ROOT, override with RM_ISOLATED_ROOT or --root. One checkout at a time (flock), deleted after each claim.

Scheduled as the Arbiter's first pre_launch step (`--run --seat DISPATCHER --since-cutoff --budget-s 900`, before
arbiter_tiers.py, dispatcher_schedule.json), so it runs only while the Arbiter is enabled. Dry run is the default: it
prints the plan and runs nothing. `--run` executes.

--since-cutoff (ARBITER_DECIDE_BACKLOG_NEVER_DRAINS): the claims are the closes at/after the Arbiter's cutoff stamp
(arbiter_pending.py), oldest first, with no day window; no stamp -> exit 2. --budget-s N
(ARBITER_MEASURE_PRELAUNCH_EVIDENCE_TIME): skip-and-carry. The oldest claim always runs; a later one starts only while
elapsed + --claim-reserve-s (default 180 = the measured worst claim, 171.1 s, rounded up) <= N; each tool's timeout is
what is left of N (at least 60 s, at most RUN_TIMEOUT). A claim cut by that timeout is journaled like any other (its
rc is "timeout", not evidence) so it never starves the queue; claims not started are CARRIED: written, oldest first, to
CARRIED (env RM_ISOLATED_CARRIED), rewritten on every --run (empty when none), and arbiter_tiers --since-cutoff leaves
them out of that batch. MEASURED 2026-10-27 (1 day of real closes, scratch store): per claim mean 22.3 s, p90 25.6,
max 171.1; 826 s for one day's 37 runnable claims.

    python3 src/RimMandrake/rimflow/isolated_evidence.py [--days 2] [--item ID] [--max N] [--json]      # plan only
    python3 src/RimMandrake/rimflow/isolated_evidence.py --run [--seat DISPATCHER] [--root DIR] [--again]

Journal (what was run, per item+sha, and the evidence lines it produced): JOURNAL. A claim already in the journal for
the same sha and plan is skipped unless --again. Exit: 0 done/planned, 2 UNMEASURED (ledger unreadable, no space,
lock held).
"""
import argparse, calendar, contextlib, datetime, fcntl, json, os, re, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import close_evidence as ce                                                # noqa: E402
import evidence_covers as EC                                               # noqa: E402

CLONE = os.path.realpath(os.path.join(HERE, "..", "..", ".."))             # the runner's own clone (its instruments)
RUN_SELFTESTS = os.path.join(CLONE, "src", "RimMandrake", "Utils", "run_selftests.py")
VALIDATE_PATCH = os.path.join(CLONE, "skills", "rimworld-modding", "scripts", "validate_patch.py")
DEFAULT_ROOT = os.path.expanduser("~/.seat-tmp/isolated_evidence")         # ext4: 24x cheaper than D: (MEASURED)
DATA = "/mnt/d/ClaudeWork/rimmandrake/isolated_evidence"
JOURNAL_ENV = "RM_ISOLATED_JOURNAL"
DEFS_ROOTS_ENV = "RM_ISOLATED_DEFS_ROOTS"                                   # os.pathsep-separated
_STEAM = "/mnt/c/Program Files (x86)/Steam/steamapps"
DEFAULT_DEFS_ROOTS = (_STEAM + "/common/RimWorld/Data", _STEAM + "/common/RimWorld/Mods", _STEAM + "/workshop/content/294100")
RUNNER_SEATS = ("DISPATCHER", "RUNNER")      # no-AI seats; a builder seat's run is never independent of its own work
MIN_FREE = 12 * 1024 ** 3                    # a checkout is ~3.7 GB; leave room for the tests' own output
RUN_TIMEOUT = 1800
MIN_TOOL_TIMEOUT = 60
CLAIM_RESERVE_S = 180                        # the measured worst claim (171.1 s, validate_patch), rounded up
CARRIED_ENV = "RM_ISOLATED_CARRIED"
CLOCK = time.monotonic                       # tests replace it
SELFTEST_ROOTS = ("src/", ".claude/hooks/", "skills/", "infrastructure/dashboards/hub/", "infrastructure/stevedesktop/")
_CITE = re.compile(r"[A-Za-z0-9_./\\:-]*selftest[A-Za-z0-9_-]*\.py")


def carried_path():
    return os.environ.get(CARRIED_ENV) or os.path.join(DATA, "carried.json")


def write_carried(rows, budget_s, path=None):
    """Atomic: the list arbiter_tiers --since-cutoff reads is never half-written."""
    path = path or carried_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = "%s.%d.tmp" % (path, os.getpid())
    with open(tmp, "w") as f:
        json.dump({"generated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                   "budget_s": budget_s, "carried": rows}, f, indent=1)
    os.replace(tmp, path)


def journal_path():
    return os.environ.get(JOURNAL_ENV) or os.path.join(DATA, "journal.jsonl")


def _repos():
    from rimflow import arbiter_tiers as at
    return at.REPOS


def _git(repo, *args, timeout=60):
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout


def resolve(sha, repos):
    """(repo, full sha) of the first clone holding the commit, or (None, None)."""
    for repo in repos:
        try:
            rc, out = _git(repo, "rev-parse", "--verify", "--quiet", "%s^{commit}" % sha, timeout=30)
        except (OSError, subprocess.SubprocessError):
            continue
        if rc == 0 and re.fullmatch(r"[0-9a-f]{40}", out.strip()):
            return repo, out.strip()
    return None, None


def touched(repo, full):
    """{path: status letter} the commit touches (first-parent diff, no renames: a rename is D + A)."""
    rc, out = _git(repo, "diff-tree", "--no-commit-id", "--name-status", "--no-renames", "-r", "--root", full)
    if rc != 0:
        raise RuntimeError("git diff-tree %s failed in %s" % (full[:12], repo))
    files = {}
    for line in out.splitlines():
        if "\t" in line:
            st, p = line.split("\t", 1)
            files[p] = st[:1]
    return files


def tree_files(repo, full):
    rc, out = _git(repo, "ls-tree", "-r", "--name-only", full, timeout=120)
    if rc != 0:
        raise RuntimeError("git ls-tree %s failed in %s" % (full[:12], repo))
    return out.splitlines()


def _is_selftest(p):
    b = p.rsplit("/", 1)[-1]
    return b.startswith("selftest") and b.endswith(".py") and p.startswith(SELFTEST_ROOTS)


def done_claims(events, since):
    """The pending done claims: per item, its latest `close` at/after `since` that cites a sha (not HEAD/PENDING).
    -> [{item, sha, close, events}] oldest first."""
    by, last = {}, {}
    for e in events:
        if e.get("id"):
            by.setdefault(e["id"], []).append(e)
            if e.get("event") == "close":
                last[e["id"]] = e
    out = []
    for item, c in last.items():
        sha = str(c.get("sha") or "").strip()
        if not re.fullmatch(r"[0-9a-fA-F]{7,40}", sha):
            continue
        t = _epoch(c.get("ts"))
        if t is None or t < since:
            continue
        out.append({"item": item, "sha": sha.lower(), "close": c, "events": by[item]})
    return sorted(out, key=lambda d: d["close"]["ts"])


def _epoch(ts):
    try:
        return calendar.timegm(time.strptime(str(ts)[:19], "%Y-%m-%dT%H:%M:%S"))
    except (TypeError, ValueError):
        return None


def claim_text(evs, close):
    """The words the claim's own record uses up to its close: close reason/why, verify evidence, implemented and note
    text. Only these name tests; nothing is guessed from prose elsewhere."""
    parts = []
    for e in evs:
        if e.get("ts", "") > close.get("ts", ""):
            continue
        if e.get("event") in ("close", "verify", "implemented", "note"):
            for k in ("reason", "why", "evidence", "text", "criteria"):
                v = e.get(k)
                parts.append(json.dumps(v) if isinstance(v, (list, dict)) else str(v or ""))
    return "\n".join(parts)


def cited_selftests(text, selftests):
    """Selftest paths (at the sha) the text names. A token with a directory resolves by path suffix; a bare name only
    when exactly one selftest at the sha has it (else it is reported ambiguous, never guessed)."""
    found, ambiguous = set(), set()
    by_base = {}
    for p in selftests:
        by_base.setdefault(p.rsplit("/", 1)[-1], []).append(p)
    for tok in _CITE.findall(text or ""):
        t = tok.replace("\\", "/")
        base = t.rsplit("/", 1)[-1]
        cands = by_base.get(base, [])
        if "/" in t:
            hit = [p for p in cands if t == p or t.endswith("/" + p)]
            if hit:
                found.update(hit)
                continue
        if len(cands) == 1:
            found.add(cands[0])
        elif len(cands) > 1:
            ambiguous.add(base)
    return found, ambiguous


def defs_roots():
    env = os.environ.get(DEFS_ROOTS_ENV)
    roots = [r for r in env.split(os.pathsep)] if env is not None else list(DEFAULT_DEFS_ROOTS)
    return [r for r in roots if r and os.path.isdir(r)]


def plan_claim(claim, repos, roots=None):
    """Pure but for git: what to run for one claim. -> dict with repo, full, selftests, validate, owed, skip."""
    p = {"item": claim["item"], "sha": claim["sha"], "close_ts": claim["close"].get("ts"),
         "close_seat": claim["close"].get("seat"), "repo": None, "full": None, "selftests": [], "validate": [],
         "defs": [], "owed": [], "notes": [], "predicted": [], "uncovered": [], "skip": None}
    repo, full = resolve(claim["sha"], repos)
    if not full:
        p["skip"] = "sha does not resolve in %s" % ", ".join(repos)
        return p
    p["repo"], p["full"] = repo, full
    files = touched(repo, full)
    live = sorted(f for f, st in files.items() if st != "D")
    tree = set(tree_files(repo, full))
    selftests = sorted(f for f in tree if _is_selftest(f))
    run = {f for f in live if _is_selftest(f)}
    cited, amb = cited_selftests(claim_text(claim["events"], claim["close"]), selftests)
    run |= cited
    for f in live:
        if f.endswith(".py") and not _is_selftest(f):
            d, b = (f.rsplit("/", 1) if "/" in f else ("", f))
            sib = (d + "/" if d else "") + "selftest_" + b
            if sib in tree:
                run.add(sib)
    p["selftests"] = sorted(run)
    if amb:
        p["notes"].append("ambiguous selftest name(s), not run: %s" % ", ".join(sorted(amb)))
    xml = [f for f in live if f.lower().endswith(".xml") and re.search(r"(^|/)(Defs|Patches)/", f)]
    roots = defs_roots() if roots is None else roots
    if xml and roots:
        p["validate"], p["defs"] = xml, list(roots)
    elif xml:
        p["owed"].append("validate_patch on %d xml file(s): no --defs root exists (a static run never counts)" % len(xml))
    cs = [f for f in live if f.endswith((".cs", ".csproj"))]
    if cs:
        p["owed"].append("winbuild for %d C# file(s): not run by this pre-step" % len(cs))
    # Sources the selected selftests are PREDICTED to cover (evidence_covers: static one-hop imports at the sha +
    # selftest_cache.DECLS csproj compile items). A prediction only: the record covers what the run's trace shows.
    def read_at(rel):
        rc, out = _git(repo, "show", "%s:%s" % (full, rel))
        return out if rc == 0 else None
    pred = set()
    for t in p["selftests"]:
        pred |= EC.predict(t, read_at, tree) | EC.declared(t, repo)
    by_pred = sorted(f for f in live if f in pred and f not in run and f not in p["validate"])
    uncovered = [f for f in live if f not in run and f not in p["validate"] and f not in pred]
    p["predicted"], p["uncovered"] = by_pred, uncovered
    if uncovered:
        p["notes"].append("%d touched path(s) no selftest here is predicted to load or declares, and no validator "
                          "covers" % len(uncovered))
    if not p["selftests"] and not p["validate"]:
        p["skip"] = "nothing to run: no selftest or validator names this claim"
    return p


def plan_key(p):
    return json.dumps([p["full"], p["selftests"], p["validate"], p["defs"]])


def read_journal(path=None):
    out = {}
    try:
        with open(path or journal_path(), encoding="utf-8") as f:
            for line in f:
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                out[(d.get("item"), d.get("key"))] = d
    except FileNotFoundError:
        pass
    return out


def child_env(seat, item):
    """The tools' environment: the runner seat and the item, as whoami() reads them. RM_SELFTEST_NESTED is dropped
    (this IS an outer run, so its records are written); the session ids stay, so a run started from the builder's own
    session is still visible to G6_independent as that session."""
    env = dict(os.environ)
    for k in ("RM_SELFTEST_NESTED", "RM_SELFTEST_REPO_ROOT", "AGENT_SEAT"):
        env.pop(k, None)
    env.update(RIMFLOW_SEAT=seat, RIMFLOW_ITEM=item, PYTHONDONTWRITEBYTECODE="1")
    return env


def run_claim(p, seat, root, runner=subprocess.run, out_dir=None, timeout=None):
    """Make the checkout, run the plan in it, read back what was recorded, delete the checkout. -> journal row.
    timeout: the batch budget left (None = RUN_TIMEOUT); each tool gets what is left of it when it starts."""
    deadline = None if timeout is None else time.time() + timeout
    t0 = time.time()
    co, full, td = ce.make_isolated(p["repo"], p["full"], root=root)
    row = {"item": p["item"], "sha": full, "key": plan_key(p), "seat": seat, "checkout_s": round(time.time() - t0, 1),
           "runs": [], "records": []}
    try:
        env = child_env(seat, p["item"])
        cmds = []
        if p["selftests"]:
            cmds.append(("selftest", [sys.executable, RUN_SELFTESTS, "--full", "--only"] +
                         [os.path.join(co, f) for f in p["selftests"]]))
        if p["validate"]:
            cmd = [sys.executable, VALIDATE_PATCH] + [os.path.join(co, f) for f in p["validate"]]
            for r in p["defs"]:
                cmd += ["--defs", r]
            cmds.append(("validate_patch", cmd))
        for tool, cmd in cmds:
            t1 = time.time()
            tmo = RUN_TIMEOUT if deadline is None else int(min(RUN_TIMEOUT, max(MIN_TOOL_TIMEOUT, deadline - t1)))
            try:
                r = runner(cmd, cwd=co, env=env, capture_output=True, text=True, timeout=tmo)
                rc, tail = r.returncode, ((r.stdout or "") + (r.stderr or ""))[-1500:]
            except subprocess.TimeoutExpired:
                rc, tail = "timeout", ""
            row["runs"].append({"tool": tool, "rc": rc, "secs": round(time.time() - t1, 1), "tail": tail})
        recs = [r for r in ce.lookup(sha=full, item=p["item"], days=2, include_dirty=True)
                if os.path.realpath(str(r.get("clone") or "")) == co]
        row["records"] = [{"tool": r.get("tool"), "result": r.get("result"), "seat": r.get("seat"),
                           "tree": (r.get("origin") or {}).get("tree"), "dirty": r.get("dirty"),
                           "evidence": ce.counts_as_evidence(r), "covers": len(r.get("covers") or [])} for r in recs]
    finally:
        shutil.rmtree(td, ignore_errors=True)
    row["total_s"] = round(time.time() - t0, 1)
    row["ts"] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    return row


@contextlib.contextmanager
def _lock(root):
    os.makedirs(root, exist_ok=True)
    fd = os.open(os.path.join(root, ".lock"), os.O_WRONLY | os.O_CREAT, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(fd)
        raise RuntimeError("another isolated_evidence run holds %s/.lock" % root)
    try:
        yield
    finally:
        os.close(fd)


def _append(path, row):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    ce._append(__import__("pathlib").Path(path), (json.dumps(row, sort_keys=True) + "\n").encode("utf-8"))


def main(argv=None, events=None, repos=None):
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.add_argument("--days", type=float, default=2, help="closes in the last N days (default 2)")
    a.add_argument("--item", action="append", help="only this item (repeatable)")
    a.add_argument("--max", type=int, default=0, help="at most N claims run (0 = all)")
    a.add_argument("--run", action="store_true", help="execute (default: dry run, print the plan only)")
    a.add_argument("--seat", default="DISPATCHER", choices=RUNNER_SEATS)
    a.add_argument("--root", default=os.environ.get(ce.ISOLATED_ROOT_ENV) or DEFAULT_ROOT)
    a.add_argument("--again", action="store_true", help="re-run claims the journal already has for the same plan")
    a.add_argument("--now", help="ISO UTC, for --days (tests)")
    a.add_argument("--since-cutoff", action="store_true",
                   help="claims closed at/after the Arbiter's cutoff stamp, no day window (exit 2 when unstamped)")
    a.add_argument("--budget-s", type=float, default=0, help="skip-and-carry wall budget for --run (0 = none)")
    a.add_argument("--claim-reserve-s", type=float, default=CLAIM_RESERVE_S,
                   help="a claim after the first starts only while elapsed + this <= the budget")
    a.add_argument("--json", action="store_true")
    a = a.parse_args(argv)
    now = _epoch(a.now) if a.now else time.time()
    repos = repos or _repos()
    try:
        if events is None:
            from rimflow import model
            events = model.read()
        if not events:
            raise ValueError("ledger read returned no events")
    except Exception as ex:  # noqa: BLE001
        print("UNMEASURED: ledger unreadable (%s)" % ex, file=sys.stderr)
        return 2
    since = now - 86400 * a.days
    if a.since_cutoff:
        from rimflow import arbiter_pending as PW
        try:
            since = PW.read_cutoff()
        except ValueError as ex:
            since, why = None, str(ex)
        else:
            why = "no Arbiter cutoff stamp at %s (arbiter_pending.py stamp)" % PW.cutoff_path()
        if since is None:
            print("UNMEASURED: %s" % why, file=sys.stderr)
            return 2
    claims = [c for c in done_claims(events, since) if not a.item or c["item"] in a.item]
    done = read_journal()
    plans = []
    for c in claims:
        try:
            p = plan_claim(c, repos)
        except Exception as ex:  # noqa: BLE001 -- one bad claim never stops the batch
            p = {"item": c["item"], "sha": c["sha"], "skip": "UNMEASURED: %s" % ex}
        if not p.get("skip") and (p["item"], plan_key(p)) in done and not a.again:
            p["skip"] = "already run (journal %s)" % done[(p["item"], plan_key(p))].get("ts")
        if not p.get("skip"):
            from rimflow import arbiter_tiers as at
            if a.seat in at.maker_seats(c["events"], c["close"]):
                p["skip"] = "seat %s built or closed this claim: its run would not be independent" % a.seat
        plans.append(p)
    todo = [p for p in plans if not p.get("skip")]
    held = []
    if a.max:
        todo, held = todo[:a.max], todo[a.max:]
    if a.json:
        print(json.dumps({"run": a.run, "root": a.root, "plans": plans}, indent=1, default=str))
    else:
        for p in plans:
            print("%-8s %-48s %s  %s" % ("SKIP" if p.get("skip") else ("RUN" if a.run else "PLAN"), p["item"][:48],
                                        p["sha"][:12], p.get("skip") or "selftests %d, validate %d%s" % (
                                            len(p["selftests"]), len(p["validate"]),
                                            ("; owed: " + "; ".join(p["owed"])) if p["owed"] else "")))
        print("%d claim(s), %d to run%s" % (len(plans), len(todo), "" if a.run else " (dry run: pass --run)"))
    if not a.run:
        return 0
    carried = [{"item": p["item"], "sha": p.get("full") or p["sha"], "close_ts": p.get("close_ts")} for p in held]
    if not todo:
        write_carried(carried, a.budget_s)
        return 0
    try:
        with _lock(a.root):
            free = shutil.disk_usage(a.root).free
            if free < MIN_FREE:
                print("UNMEASURED: %.1f GB free under %s, need %.0f" % (free / 1024 ** 3, a.root, MIN_FREE / 1024 ** 3),
                      file=sys.stderr)
                return 2
            t0 = CLOCK()
            for n, p in enumerate(todo):
                left = (a.budget_s - (CLOCK() - t0)) if a.budget_s else None
                if left is not None and n and left < a.claim_reserve_s:
                    carried.append({"item": p["item"], "sha": p.get("full") or p["sha"], "close_ts": p.get("close_ts")})
                    print("CARRIED  %-48s %s  %.0f s of %.0f left < reserve %.0f: first in line next batch" % (
                        p["item"][:48], (p.get("full") or p["sha"])[:12], left, a.budget_s, a.claim_reserve_s))
                    continue
                try:
                    row = run_claim(p, a.seat, a.root, timeout=None if left is None else max(left, 0))
                except Exception as ex:  # noqa: BLE001
                    row = {"item": p["item"], "sha": p.get("full"), "key": plan_key(p), "seat": a.seat,
                           "error": "%s: %s" % (type(ex).__name__, ex),
                           "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
                _append(journal_path(), row)
                print("DONE     %-48s %s  checkout %ss total %ss  records %s%s" % (
                    p["item"][:48], (row.get("sha") or "")[:12], row.get("checkout_s"), row.get("total_s"),
                    ", ".join("%s %s%s" % (r["tool"], r["result"], "" if r["evidence"] else " (not evidence)")
                              for r in row.get("records") or []) or "none",
                    ("  ERROR " + row["error"]) if row.get("error") else ""))
            carried.sort(key=lambda c: (c["close_ts"] or "", c["item"]))
            write_carried(carried, a.budget_s)
    except RuntimeError as ex:
        print("UNMEASURED: %s" % ex, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
