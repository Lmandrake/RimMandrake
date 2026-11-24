#!/usr/bin/env python3
"""ingest.py - finished test-queue jobs become RUNNER ledger events (STEVEDESKTOP_RUNNER_WIRE_OWN_LEDGER_SEAT).

Plan: design/RimMandrake/test_orchestration_two_machines_2026-10-25.md item #5. The testq-tick service runs it after
every tick, from the dispatch clone (~/rm/dispatch), so the only writer of the RUNNER shard is that clone.

For each done/<job>.json not yet ingested, whose job names a rimflow item:
  outcome DONE      -> `rimflow verify ITEM --result pass|fail|partial --config steve-<profile>` (archmagi-<profile> from the backfill) as seat RUNNER
                       (fail: any FAIL row; pass: every row PASS; partial: otherwise), --sha the runner's commit,
                       --evidence the sheet on SteveDesktop plus the attempt id; then ONE finding per FAIL row,
                       --from that run, type UNTRIAGED (a human or seat decides MOD/SITE/HARNESS).
  any other outcome -> a note on the item (INVALID/REFUSED/INTERRUPTED measured nothing about the mod), once per
                       attempt; a refused note (item not on origin yet) is an error, retried like a verify.
  a harness fault   -> no verdict (owner ruling by card 2026-10-31, retest.py). A chain the harness stopped is left out of
                       the verify, so it never reads as a feature's partial, and each distinct cause files ONE repair
                       item, HARNESS_REPAIR_CAUSE_<HEX> (--for BENCH, needs offline; FOUNDRY is retired), or a
                       note on the open one. Self-healing causes note the filler host until three jobs in 24 h.
                       An INVALID job with no sheet does the same. The item is filed with its
                       template, items/<NAME>.md (repair_prose: job ids to re-run, classify first, pass = the same
                       job re-run yields a verdict, `retest.py passed`, forbidden fixes, a negative control), committed
                       with the shard; a run inside a known fault window is ENVIRONMENT and files nothing
                       (TESTQ_REPAIR_FIX_TICKETS_NAME_THEIR_PASS).
  no item, a FAIL   -> FILL_ITEM (STEVE_FILLER_MONITOR_FAIL_FINDINGS, a standing host) is verified from the job's rows
                       and gets one finding per FAIL row, so the filler's failures reach flow.untriaged_findings
                       (TESTQ_FILLER_DIAGNOSE_FAILS_NOBODY_HEARD: 35 FAIL rows in 18 such jobs had been dropped).
  no item           -> nothing on the ledger, unless job.row_items (submit --row-item ROW_OR_CHAIN=ITEM) maps rows to
                       items or TESTQ_HOST_ITEM names a standing host: then each item is verified from ITS rows only.
SteveDesktop's SIMD fault (fault_monitor.py) goes first, whatever the record says: a job that ran inside a fault window
is quarantined (its record leaves done/, its items get a note, an item job is re-queued), even if it was ingested before the
window was known; a job with no clean canary cycle read since it finished is held, not marked, and asked again next pass.
A repair item rests on its sightings (support(): the attempt in its spawn title plus each `seen again in testq ATT`
note); a quarantine marks that attempt's sighting invalid (`testq ATT quarantined:` on the item), and withdraw()
recomputes support: an open repair with no valid sighting left is dropped, its evidence and a reopen signature in the
reason; a mixed one is kept. Late discovery so ends where early discovery would (TESTQ_QUARANTINE_BUILD_WITHDRAW_UNSUPPORTED).
A lane-pausing outcome (testq.PAUSE_ON: a red canary, a refused runner pull) is also, item or not, a failed run of
the lane (verify STEVE_LANE_MONITOR_PAUSE_FINDINGS --config steve-lane) plus one finding from it,
STEVE_LANE_<CANARY_RED|SYNC_REFUSED>_<JOBHEX6> (design section 6: pause the lane, file a finding).
The done record gets "ingested" either way, except after an error (typically an item filed in a seat clone that
has not reached origin yet): that record is retried every TESTQ_INGEST_RETRY_S (600) and marked ingested with the
error only after TESTQ_INGEST_MAX_TRIES (6) tries (a crash or a timeout of the ingest spends none: tries_after). Idempotent: a verify already in the RUNNER shard for that attempt is
reused, never written twice. Then the shard is committed and pushed (TESTQ_INGEST_PUSH=0 skips the git step); a
pull --rebase that fails is aborted and stops that publication with the commit kept local, never pushed half-rebased;
any later ingest publishes RUNNER lines left uncommitted or commits left unpushed, even with nothing new to ingest.
"""
import contextlib
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.append(os.path.join(HERE, "..", "..", "rimflow"))
import failure_class as FC  # noqa: E402
import fault_monitor as FM  # noqa: E402
import invalid_class as IC  # noqa: E402
import own_cgroup  # noqa: E402  a ledger write outside a timed caller's memory limit
import retest as R  # noqa: E402
import schema as S  # noqa: E402
import testq as T  # noqa: E402
import visit_rows as VR  # noqa: E402

REPO = T.REPO
CLI = os.path.join(REPO, "src", "RimMandrake", "rimflow", "cli.py")
SHARD_REL = os.path.join("infrastructure", "state", "ledger", "events", "RUNNER.jsonl")
RETRY_S = int(os.environ.get("TESTQ_INGEST_RETRY_S", "600"))
MAX_TRIES = int(os.environ.get("TESTQ_INGEST_MAX_TRIES", "6"))


def shard_path():
    led = os.environ.get("RIMFLOW_LEDGER")       # rimflow's own redirect (selftests): shards sit beside it
    return os.path.join(os.path.dirname(led), "events", "RUNNER.jsonl") if led else os.path.join(REPO, SHARD_REL)


def rimflow(*args):
    env = dict(os.environ, RIMFLOW_SEAT="RUNNER", CLAUDE_PROJECT_DIR=REPO)
    r = own_cgroup.run([sys.executable, CLI] + list(args), env=env, capture_output=True, text=True, timeout=120)
    return r.returncode, (r.stdout + r.stderr).strip()


def tries_after(pend, error):
    """-> (the tries spent with this error, whether they are all spent). A crash or a timeout of the ingest itself spends
    none (failure_class.of_error): the record waits and is tried again, for its verdict would be lost with it."""
    tries = (pend or {}).get("tries", 0) + (1 if FC.of_error(error).counts else 0)
    return tries, tries >= MAX_TRIES


def verdict(res):
    counts = res.get("counts") or {}
    if counts.get("FAIL"):
        return "fail"
    return "pass" if counts and set(counts) == {"PASS"} else "partial"


def sheet_of(res):
    paths = [a["path"] for a in res.get("artifacts") or []]
    return next((p for p in paths if p.endswith(".html")), paths[0] if paths else "no sheet")


def recorded_run(item, attempt):
    """The run name of a verify already on the ledger for this attempt, or None. The shard is grepped first (cheap);
    only a hit pays for a replay, which is what numbers runs."""
    try:
        with open(shard_path(), encoding="utf-8") as f:
            if attempt not in f.read():
                return None
    except OSError:
        return None
    # the attempt must stand whole in the evidence: JOB.a1 is not JOB.a10
    pat = re.escape(attempt) + r"(?![\w.])"
    code = ("import os, re, sys; sys.path.insert(0, %r); import model\n"
            "model.EVENTS = os.environ.get('RIMFLOW_LEDGER') or model.EVENTS\n"
            "it = model.replay(model.read()).items.get(%r)\n"
            "print(next((r.name for r in (it.runs if it else []) if re.search(%r, r.evidence or '')), ''))"
            % (os.path.dirname(CLI), item, pat))
    r = subprocess.run([sys.executable, "-c", code], env=dict(os.environ, CLAUDE_PROJECT_DIR=REPO),
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:     # a failed lookup is not "no run": verifying anyway would record the attempt twice
        raise RuntimeError("replay for %s failed (exit %d): %s" % (item, r.returncode, (r.stderr or "").strip()[-160:]))
    return r.stdout.strip() or None


def filed(name, run):
    """True when the shard already holds finding NAME from RUN (an ingest that died before marking its record). Only
    the same run counts: a name is not unique, and another item's finding must never pass for this one's."""
    try:
        with open(shard_path(), encoding="utf-8") as f:
            for line in f:
                if '"%s"' % name in line:
                    try:
                        e = json.loads(line)
                    except ValueError:
                        continue
                    if e.get("event") == "finding" and e.get("name") == name and e.get("from") == run:
                        return True
    except OSError:
        pass
    return False


def finding_name(mod, row, job_id, salt=False, chain=None):
    """MOD_ROW_FAILS_JOBHEX6. When folding the row to A-Z0-9_ loses anything (a cut at 44, `foo-bar` vs `foo_bar`),
    6 hex of the raw mod/row keep two rows of one job from sharing a name (one would pass for the other's finding).
    `chain` (given only when one row id FAILs in two chains) joins the hashed text, so those two differ as well."""
    raw = "%s_%s" % (mod, row)
    full = re.sub(r"[^A-Z0-9]+", "_", raw.upper()).strip("_")
    base = full[:44]
    if salt or base != raw.upper():
        key = raw if chain is None else "%s\0%s" % (raw, chain)
        base = "%s_%s" % (base[:37].rstrip("_"), hashlib.sha1(key.encode("utf-8")).hexdigest()[:6].upper())
    return "%s_FAILS_%s" % (base, job_id[-6:].upper())


def finding_names(mod, job_id, fails):
    """-> one finding name per FAIL row in FAILS, distinct across them. FAILS is the whole job's FAIL rows (every item
    group's, in ingest_done's fixed order), so one row id FAILing in two items' chains never mints one name for both
    (job J20261112T144249Z-2ac601 gave three items one name and findings_fold refused the ledger,
    RIMMANDRAKE_UNJAM_FINDINGS_FOLD_THREE_ITEMS_ONE_NAME). Deterministic from the rows, so a resumed ingest finds the
    names it filed (filed())."""
    plain = [finding_name(mod, row["row"], job_id) for row in fails]
    taken, out = set(), []
    for row, name in zip(fails, plain):
        if plain.count(name) > 1:              # rows only case apart (foo / FOO): each gets its own hash
            twin = sum(1 for r in fails if r["row"] == row["row"]) > 1    # one row id in two chains: chain joins it
            chain = str(row.get("chain")) if twin else None
            name = finding_name(mod, row["row"], job_id, salt=True, chain=chain)
        k = 0
        while name in taken:                   # a salted name can hit another row's name: re-salt until distinct
            k += 1
            name = finding_name(mod, row["row"], job_id, salt=True, chain="%s#%d" % (row.get("chain"), k))
        taken.add(name)
        out.append(name)
    return out


LANE_ITEM = os.environ.get("TESTQ_LANE_ITEM", "STEVE_LANE_MONITOR_PAUSE_FINDINGS")
FILL_ITEM = os.environ.get("TESTQ_FILL_ITEM", "STEVE_FILLER_MONITOR_FAIL_FINDINGS")
LANE_TWIST = {("INVALID", "CANARY"): "CANARY_RED", ("REFUSED", "SYNC"): "SYNC_REFUSED"}


def lane_finding(job, res):
    """An outcome that paused the lane is a failed run of the lane itself: RUNNER may only verify/finding/note, so it
    records `verify LANE_ITEM --result fail --config steve-lane` and one finding from that run. Idempotent: the run
    is reused by attempt (recorded_run) and the finding by grepping the shard for its name."""
    key = (res["outcome"], res.get("cause"))
    if key not in T.PAUSE_ON:
        return None
    att = res["attempt"]
    name = "STEVE_LANE_%s_%s" % (LANE_TWIST.get(key, "PAUSED"), job["id"][-6:].upper())
    run = recorded_run(LANE_ITEM, att)
    if not run:
        rc, out = rimflow("verify", LANE_ITEM, "--result", "fail", "--config", "steve-lane",
                          "--evidence", "stevedesktop: testq %s %s/%s" % (att, key[0], key[1]),
                          "--sha", res.get("runner_sha") or job["source_sha"])
        m = re.search(r"(\S+/run-\d+@\S+) recorded", out)
        if rc != 0 or not m:
            return "lane run not recorded: " + out[-160:]
        run = m.group(1)
    if filed(name, run):
        return name
    rc, out = rimflow("finding", "--from", run, "--name", name, "--type", "UNTRIAGED", "--severity", "high",
                      "--why", "SteveDesktop lane paused: %s (testq %s: %s); it admits nothing until "
                      "`testq.py resume --reason`" % (T.PAUSE_ON[key], att, (res.get("note") or "")[:160]))
    return name if rc == 0 else "lane finding not recorded: %s: %s" % (name, out[-160:])


def note_once(item, needle, text):
    """Note ITEM unless the shard already holds a note on it whose text contains NEEDLE (an earlier try of this
    record) -> True when the note is on the ledger. A refused note (the item not on origin yet) is retried like a
    verify instead of being lost when the record is marked."""
    try:
        with open(shard_path(), encoding="utf-8") as f:
            for line in f:
                if needle in line:
                    e = json.loads(line)
                    if e.get("event") == "note" and e.get("id") == item and needle in (e.get("text") or ""):
                        return True
    except (OSError, ValueError):
        pass
    return rimflow("note", item, "--text", text)[0] == 0


_REPAIR_ITEMS = [None]      # the ledger's items, once per process; REPAIRED holds what this process has filed since
_REPAIRED = {}
_REPAIR_HISTORY = [None]    # indexed once per pass, only if a self-healing cause is seen
REPAIR_WINDOW_S = 24 * 3600
REPAIR_JOBS = 3


def spawned_for(base, att):
    """True when the shard already holds a repair spawned by ATT for this cause."""
    try:
        with open(shard_path(), encoding="utf-8") as f:
            return any(base in line and att in line and '"spawn"' in line for line in f)
    except OSError:
        return False


ITEMS_REL = os.path.join("infrastructure", "state", "items")
REPAIR_PREFIX = "HARNESS_REPAIR_"
#: the class a cause kind most likely belongs to; the builder confirms it before anything else (## classify)
CLASS_PRIOR = {"site_hold": "SITE", "surprise": "SITE", "selftest_not_run": "MOD", "canary": "ENVIRONMENT",
               # invalid_class's stable keys: a TEST fault is the mod's own test, a GAME fault the host or game
               "TEST": "MOD", "DELIVERY": "HARNESS", "GAME": "ENVIRONMENT"}


def items_dir():
    return os.environ.get("RIMFLOW_ITEMS") or os.path.join(REPO, ITEMS_REL)


def ledger_items():
    """-> the ledger's items now (id -> item with .state); one place, so a selftest can stand in for it."""
    import gaps
    return gaps.ledger()[2].items


def env_window(rec):
    """ENVIRONMENT is checked at filing, never left to the builder: -> (window or None, what was read). A run whose span
    overlaps a known SteveDesktop fault window is the host's; it files no repair (the gate quarantines and re-queues it)."""
    res = (rec or {}).get("result") or {}
    host = res.get("host", T.STEVE)
    if not T.on_steve(host):            # Steve1 and Steve2 share the machine and its fault windows
        return None, "host %s: SteveDesktop's fault windows do not apply" % host
    windows, state = FM.load()
    span = FM.job_span(rec)
    if span is None:
        return None, "UNCHECKED: the record states no time"
    w = FM.window_of(span, windows)
    if w:
        return w, "inside fault window %s" % w.get("id")
    return None, "%d known fault window(s) in fault_windows.json, none overlaps the run (%s .. %s)%s" % (
        len(windows), FM.stamp(span[0]), FM.stamp(span[1]),
        "" if state else "; UNCHECKED beyond that: the fault monitor has never run")


def rerun_line(job):
    """The testq.py submit line that re-runs JOB as it was (same mod, selector, purpose, items), at the fix's sha."""
    sel, out = job.get("selector") or {}, ["python3 src/RimMandrake/Utils/testq/testq.py submit", job["mod"]]
    for k in ("chains", "rows"):
        if sel.get(k):
            out += ["--%s" % k, ",".join(sel[k])]
    for it in sel.get("item") or []:
        out += ["--item", it]
    if sel.get("full"):
        out.append("--full")
    out += ["--purpose", job.get("purpose") or "fix", "--by BENCH --sha <the fix's published sha>"]
    if job.get("item"):
        out += ["--for-item", job["item"]]
    for k, v in sorted((job.get("row_items") or {}).items()):
        out += ["--row-item", "%s=%s" % (k, v)]
    if job.get("profile"):
        out += ["--profile", job["profile"]]
    return " ".join(out)


def test_author_lines(job, cause):
    """A TEST-class fault goes back to whoever wrote the test: -> prose lines naming the last commit to the mod's
    validation walk and validation.py (git records the commit, not the seat; the subject usually names the item or
    loop). [] for any other class, or when git cannot tell."""
    if IC.class_of_cause(cause) != IC.TEST:
        return []
    G = T._own_repeat_guard()  # never rimflow's repeat_guard.py, which shadows it once rimflow is on sys.path
    paths = [p for p in G.relevant(job.get("mod") or "", IC.TEST, REPO)
             if p.endswith(".md") or os.path.isdir(os.path.join(REPO, p)) and "/Utils/" not in p]
    out = G.git("log", "-1", "--format=%h %ad %s", "--date=short", "--", *paths) if paths else None
    if not out:
        return ["- the test's author: unknown (git log of %s read nothing)" % (", ".join(paths) or "no path")]
    return ["- the test was last written by commit %s (git log of %s): route the fix to that item or seat, not to "
            "the harness" % (out[:160], ", ".join(paths))]


def repair_prose(name, job, res, cause, env_read):
    """TESTQ_REPAIR_FIX_TICKETS_NAME_THEIR_PASS: what a repair item builds and how it passes, written at filing, so no
    builder invents what "fixed" means (the cheapest invention silences the check)."""
    att, kind = res["attempt"], cause.split(":")[0].strip()
    prior = CLASS_PRIOR.get(kind, "HARNESS")
    held = sorted(c for c, v in R.split_rows(res.get("rows") or [])[2].items() if v == cause) \
        if res.get("outcome") == "DONE" else []
    return "\n".join([
        "# %s" % name, "",
        "Filed by testq ingest.repair() (TESTQ_REPAIR_FIX_TICKETS_NAME_THEIR_PASS). A harness fault: the run measured "
        "nothing for what it held, so no verdict was recorded.", "",
        "## spec", "",
        "- cause signature: `%s`" % cause,
        "- job `%s`, attempt `%s`, mod %s, host %s, outcome %s/%s" % (
            job["id"], att, job["mod"], res.get("host", T.STEVE), res.get("outcome"), res.get("cause")),
        "- chains held without a verdict: %s" % (", ".join("`%s`" % c for c in held) or "the whole job (no sheet)"),
        "- runner note: %s" % (res.get("note") or "")[:300].replace("\n", " "),
        "- read the sighting: `python3 src/RimMandrake/Utils/testq/testq.py show %s`" % job["id"],
        ] + test_author_lines(job, cause) + [
        "- the filler will not run this selection again until a relevant path changes or this item closes "
        "(testq/repeat_guard.py)."][:1 if IC.class_of_cause(cause) in IC.OWNED else 0] + [
        "- later sightings land as `seen again in testq <attempt>` notes on this item: re-run those jobs too.", "",
        "## classify", "",
        "Decide the class FIRST, from the sighting, before changing any code. Prior from the cause kind `%s`: %s." % (
            kind, prior),
        "- ENVIRONMENT (the host: SIMD fault, reboot, disk) was checked at filing: %s. If the host still did it, "
        "drop this item with that evidence; never change the harness for a host fault." % env_read,
        "- MOD: the mod under test stopped the harness reading it. File a finding or item on the mod and supersede "
        "this one; the harness is not changed.",
        "- SITE: the test site (map, fixture, quiet hold, a surprise event) did it. Fix the staging, not the check.",
        "- HARNESS: the harness's own code. Fix it here.", "",
        "## verify", "",
        "Pass = the SAME job re-run yields a verdict. After the fix is published, queue it again:",
        "", "    %s" % rerun_line(job), "",
        "and when it finishes: `python3 src/RimMandrake/Utils/testq/retest.py passed <new job id> %s` exits 0 (the run "
        "is DONE, rows carry PASS/FAIL/SKIP, and none carries this cause). A FAIL verdict passes this item: a real "
        "FAIL is a verdict." % name, "",
        "## negative control", "",
        "`python3 src/RimMandrake/Utils/testq/retest.py passed %s %s` must exit 1 both before and after the fix: the "
        "original sighting still carries the cause. If it exits 0, the fix silenced the detector." % (job["id"], name), "",
        "## forbidden", "",
        "- heal: no retry, auto-restart or self-repair that turns the fault into a pass without removing its cause.",
        "- tolerance: no widened timeout, threshold or budget that lets the same fault through unseen.",
        "- drop the check: no removed row, chain, `retest.CAUSES` pattern or validity test; no row re-labelled to "
        "escape it.", "",
        "## criteria", "",
        "- the class is recorded on this item (note) with its evidence before the fix;",
        "- `retest.py passed <re-run job> %s` exits 0 on a job run at the fix's sha;" % name,
        "- the negative control above exits 1.", ""])


def write_repair_prose(name, text):
    """Write items/NAME.md once (a later sighting is a note, never a rewrite) -> the path, or None if it existed."""
    path = os.path.join(items_dir(), name + ".md")
    if os.path.exists(path):
        return None
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def self_healing(res, cause):
    return (R.stale_load(res) == "repaired" and cause.startswith("HARNESS: stale_load,")) or all(
        part.split(":", 1)[0] in ("site_hold", "surprise") for part in cause.split(" + "))


def repair_history():
    """Index readable self-healing sightings and keep failures to read separate from an empty history."""
    sightings, unread = {}, []
    windows, _ = FM.load()
    for name in sorted(os.listdir(T.q("done"))):
        if not name.endswith(".json"):
            continue
        rec = T.read_json(T.q("done", name))
        if not isinstance(rec, dict):
            unread.append(name)
            continue
        job, res = rec.get("job"), rec.get("result")
        if not isinstance(job, dict) or not isinstance(res, dict):
            unread.append(name)
            continue
        if S.is_checks(job) or S.is_proofs(job):
            continue
        causes = [cause for cause in R.causes_of(res) if self_healing(res, cause)]
        if not causes:
            continue
        at = IC.finished_of(rec)
        if at is None or not job.get("id"):
            unread.append(name)
            continue
        span = FM.job_span(rec)
        if span and T.on_steve(res.get("host", T.STEVE)) and FM.window_of(span, windows):
            continue
        for cause in causes:
            sightings.setdefault(cause, []).append((at, job["id"]))
    return sightings, unread


def repair(job, res, cause, rec=None):
    """One repair item per CAUSE: file it with its template (items/NAME.md), or note the open one -> None, or an error
    string (retried). A run inside a known fault window is ENVIRONMENT: never filed, never noted."""
    att, base = res["attempt"], R.repair_base(cause)
    if spawned_for(base, att):      # a retry of this attempt, even if its repair has closed since
        return None
    rec = rec or {"job": job, "result": res}
    w, env_read = env_window(rec)
    # RIMMANDRAKE_STOP_STEVEDESKTOP_INVALID_RUNS_REPEATING_UNFIXED: a broken test or delivery fault is code, never the
    # host's doing. Fault windows ran back to back from 2026-11-08 on, so this exemption filed no repair for 76
    # sightings and no hold ever formed: the filler re-ran the same selections into the same faults.
    if w and IC.class_of_cause(cause) in IC.OWNED:
        env_read = "inside fault window %s, but a %s fault is not the host's: filed" % (
            w.get("id"), IC.class_of_cause(cause))
    elif w:
        T.log("ingest %s: cause %s ran inside fault window %s: ENVIRONMENT, no repair filed" % (att, base, w.get("id")))
        return None
    if self_healing(res, cause):
        finished = IC.finished_of(rec)
        if finished is None:
            return "repair %s: could not look at the finish time" % att
        try:
            if _REPAIR_HISTORY[0] is None:
                _REPAIR_HISTORY[0] = repair_history()
            sightings, unread = _REPAIR_HISTORY[0]
        except OSError as e:
            return "repair %s: could not look at done jobs: %s" % (att, e)
        seen = {jid for at, jid in sightings.get(cause, ()) if finished - REPAIR_WINDOW_S <= at <= finished}
        seen.add(job["id"])
        if len(seen) < REPAIR_JOBS:
            if unread:
                return "repair %s: could not look at done job %s" % (att, unread[0])
            needle = "testq %s self-healing cause %s" % (att, base)
            if note_once(FILL_ITEM, needle, "%s (job %s, %d/%d distinct jobs in 24 h): %s"
                         % (needle, job["id"], len(seen), REPAIR_JOBS, cause)):
                return None
            return "repair %s: filler host note refused" % att
    try:
        if _REPAIR_ITEMS[0] is None:
            _REPAIR_ITEMS[0] = ledger_items()
    except Exception as e:  # noqa: BLE001 - retried like any record that could not be written
        return "repair %s: ledger unreadable: %s" % (base, e)
    if base in _REPAIRED:
        name, how = _REPAIRED[base], "note"
    else:
        name, how = R.repair_slot(_REPAIR_ITEMS[0], base)
    if how == "note":
        needle = "seen again in testq %s" % att
        return None if note_once(name, needle, "%s (job %s): %s" % (needle, job["id"], (res.get("note") or cause)[:160])) \
            else "repair note refused on %s" % name
    wrote = write_repair_prose(name, repair_prose(name, job, res, cause, env_read))
    cause_item = job.get("item") or next(iter(sorted((job.get("row_items") or {}).values())), None) or LANE_ITEM
    rc, out = rimflow("spawn", "--from", cause_item, "--for", "BENCH",      # FOUNDRY is retired (owner, 2026-11-02)
                      "--needs", "offline", "--name", name,
                      "--title", ("harness fault, no verdict (testq %s, %s): %s" % (att, job["mod"], cause))[:160])
    if rc != 0:
        # The template this call wrote goes with the refused spawn: left behind it sat untracked for days, and once
        # another clone filed the same item with fresh prose, every replay in this clone refused on the different
        # untracked file (incident publish-20261120063531, ~/rm/dispatch). The retry writes it again.
        if wrote:
            with contextlib.suppress(OSError):
                os.remove(wrote)
        return "repair %s not filed: %s" % (name, out[-160:])
    _REPAIRED[base] = name
    return None


def in_window(res):
    """-> " [inside machine-fault window F...]" for a result the fault tracker dated inside one, else "". It goes on every
    ledger line of the result: 157 verdicts of 2026-11 stood there with nothing that said so."""
    w = (res.get("fault_window") or {}).get("id")
    return " [inside machine-fault window %s]" % w if w else ""


def ingest_proofs(job, res):
    """An exact-tier job (profile tier:<name>): its rows are the live-proof clauses of its item, so the verdict is a RUNNER
    verify on that item and no finding. (Its old reader was retired 2026-11-18 and the verdict went nowhere.)"""
    item, att, res = job["item"], res["attempt"], dict(res, counts=S.count_verdicts(res.get("rows") or []))
    if res["outcome"] != "DONE":
        needle = "testq %s on SteveDesktop:" % att
        ok = note_once(item, needle, "%s %s/%s, no verdict recorded%s (%s)" % (
            needle, res["outcome"], res.get("cause"), in_window(res), (res.get("note") or "")[:160]))
        return {"note": True} if ok else {"error": "note refused on %s" % item}
    run = recorded_run(item, att)
    if not run:
        host = res.get("host") or "stevedesktop"
        look = ["--outcome", FC.LK.NO_LOOK] if verdict(res) == "partial" else []
        rc, out = rimflow("verify", item, "--result", verdict(res), "--config", config_for(host, item, "proofs"),
                          "--evidence", "%s: testq %s%s: %s" % (host, att, in_window(res), "; ".join(
                              "%s %s %s" % (r["row"], r["verdict"], (r.get("detail") or "")[:120]) for r in res.get("rows") or [])),
                          "--sha", res.get("runner_sha") or job["source_sha"], *look)
        m = re.search(r"(\S+/run-\d+@\S+) recorded", out)
        if rc != 0 or not m:
            return {"error": out[-300:]}
        run = m.group(1)
    return {"run": run, "result": verdict(res)}


def visit_row_paths(git):
    """-> the visits' rows.jsonl with lines not yet committed here (visit_rows.py wrote them): they travel in the shard's
    commit."""
    r = git("status", "--porcelain", "--untracked-files=all", "--", "design/concepts")
    if getattr(r, "returncode", 1) != 0:
        return []
    return sorted(p for p in (ln[3:].strip().strip('"') for ln in r.stdout.splitlines())
                  if re.match(r"^design/concepts/[^/]+/version/in_game/visit_\d+/rows\.jsonl$", p))


def ingest_one(rec):
    """The record's ledger events, after its rows in the in-game visit it was sent for (BENCH.visit: visit_rows.py)."""
    vr = VR.ingest(rec, REPO)
    out = ledger_one(rec)
    return dict(out, **{"visit": vr}) if vr else out


def ledger_one(rec):
    job, res = rec["job"], rec["result"]
    if rec.get("fault_window"):
        res = dict(res, fault_window=rec["fault_window"])
    if S.is_checks(job) and not job.get("item"):
        return {"skipped": "a checks job with no item: its verdicts are its visit's rows"}
    if S.is_proofs(job) or S.is_checks(job):
        return ingest_proofs(job, res)
    item, att = job.get("item"), res["attempt"]
    lane = lane_finding(job, res)
    if lane and lane.startswith("lane "):  # run or finding not recorded (host item not on origin yet): retried
        return {"error": lane}
    if res["outcome"] == "DONE":
        causes = R.split_rows(res.get("rows") or [])[2].values()
    else:
        causes = [c for c in [R.job_cause(res)] if c]
        if rec.get("repeat_stop") and not causes:       # one-ticket-for-one-cause (lane_stop.py)
            causes = ["repeat: " + rec["repeat_stop"]]
    for cause in sorted(set(causes)):       # before the no-item return: the filler's jobs name no item
        err = repair(job, res, cause, rec)
        if err:
            return {"error": err}
    # the standing host stands in only for a job with no item of its own (as in groups_of)
    host = None if item else os.environ.get("TESTQ_HOST_ITEM")
    if not item and not job.get("row_items") and not host:
        if not filler_fails(res):
            return dict({"skipped": "the job names no item"}, **({"lane_finding": lane} if lane else {}))
        host = FILL_ITEM        # a FAIL nobody would hear: the filler's host records it (TESTQ_FILLER_DIAGNOSE_FAILS_NOBODY_HEARD)
    items = sorted({i for i in [item, host] + list((job.get("row_items") or {}).values()) if i})
    failed = []
    if lane:
        for it in items:
            needle = "testq %s paused the SteveDesktop lane" % att
            if not note_once(it, needle, "%s; finding %s" % (needle, lane)):
                failed.append(it)
    if res["outcome"] != "DONE":
        for it in items:
            needle = "testq %s on SteveDesktop:" % att
            if not note_once(it, needle, "%s %s/%s, no verdict recorded%s (%s)"
                             % (needle, res["outcome"], res.get("cause"), in_window(res), (res.get("note") or "")[:160])):
                failed.append(it)
        if failed:
            return {"error": "note refused on %s" % ",".join(sorted(set(failed)))}
        return {"note": True}
    if failed:
        return {"error": "lane note refused on %s" % ",".join(sorted(set(failed)))}
    return ingest_done(job, res, item, host)


def filler_fails(res):
    """True when a DONE record holds a FAIL row the harness did not stop (a harness fault files its repair instead)."""
    return res["outcome"] == "DONE" and any(r.get("verdict") == "FAIL" for r in R.split_rows(res.get("rows") or [])[0])


def groups_of(job, res, host=None):
    """-> {item: [rows]}: each row goes to the item its row id (else its chain) maps to in job["row_items"], else to the
    job's item, else to HOST (FILL_ITEM for an item-less job with a FAIL row), else to TESTQ_HOST_ITEM (a standing host
    for item-less sweeps/filler; neither: such rows are dropped).
    A sheet's verdict is never recorded on an item whose rows it does not hold (TESTQ_INGEST_FIX_ONE_ITEM_MANY_ROWS)."""
    ri = job.get("row_items") or {}
    default = job.get("item") or host or os.environ.get("TESTQ_HOST_ITEM") or None
    out = {}
    for row in res.get("rows") or []:
        it = ri.get(row.get("row")) or ri.get(row.get("chain")) or default
        if it:
            out.setdefault(it, []).append(row)
    return out


def ingest_done(job, res, item, host=None):
    att = res["attempt"]
    kept, held, causes = R.split_rows(res.get("rows") or [])
    groups = groups_of(job, dict(res, rows=kept), host)
    held_on = sorted(i for i in groups_of(job, dict(res, rows=held), host) if i not in groups)
    if item and item not in groups and item not in held_on and not job.get("row_items"):
        groups[item] = []                      # unchanged: a job for an item with no rows still gets its verdict
    if not groups and not held_on:
        return {"skipped": "no row maps to an item"}
    order = [(it, row) for it, rows in sorted(groups.items()) for row in rows if row["verdict"] == "FAIL"]
    named = {}
    for (it, _), n in zip(order, finding_names(job["mod"], job["id"], [row for _, row in order])):
        named.setdefault(it, []).append(n)
    out, errs = {}, []
    for it in held_on:                          # nothing measured for this item: never a partial
        needle = "testq %s on SteveDesktop:" % att
        if note_once(it, needle, "%s harness fault, no verdict recorded (%s)"
                     % (needle, "; ".join(sorted(set(causes.values())))[:160])):
            out[it] = {"result": "harness", "note": True}
        else:
            errs.append("%s: note refused" % it)
    for it, rows in sorted(groups.items()):     # every group is tried: one item not on origin yet blocks no other
        r = ingest_group(job, res, it, dict(res, rows=rows, counts=T.S.count_verdicts(rows)), att, named.get(it, []))
        if "error" in r:
            errs.append("%s: %s" % (it, r["error"]) if len(groups) > 1 else r["error"])
        else:
            out[it] = r
    if errs:                                    # retried; the groups recorded here are reused (recorded_run)
        return dict({"error": " | ".join(errs)}, **({"groups": out} if out else {}))
    if len(out) == 1:
        return next(iter(out.values()))
    if not out:
        return {"skipped": "no row maps to an item"}
    return {"groups": out, "result": ",".join("%s=%s" % (i, o["result"]) for i, o in out.items())}


def config_for(host, item, profile):
    """The verify --config: steve-<profile> for either SteveDesktop game, <host>-<profile> else (archmagi-...)."""
    return "%s-%s" % ("steve" if T.on_steve(host) else host,
                      "filler" if item == FILL_ITEM else profile)   # testpilot_route.NOT_A_TEST


def ingest_group(job, res, item, gres, att, names=None):
    host = res.get("host") or "stevedesktop"         # the archmagi backfill runs the same worker (host "archmagi")
    config = config_for(host, item, job.get("profile", "targeted"))
    run = recorded_run(item, att)
    if not run:
        # a partial holds no FAIL row (verdict()): its non-pass is rows nobody measured, which no streak counts
        look = ["--outcome", FC.LK.NO_LOOK] if verdict(gres) == "partial" else []
        rc, out = rimflow("verify", item, "--result", verdict(gres), "--config", config,
                          "--evidence", "%s:%s (testq %s)%s" % (host, sheet_of(res), att, in_window(gres)),
                          "--sha", res.get("runner_sha") or job["source_sha"], *look)
        m = re.search(r"(\S+/run-\d+@\S+) recorded", out)
        if rc != 0 or not m:
            return {"error": out[-300:]}
        run = m.group(1)
    found = []
    fails = [row for row in gres.get("rows") or [] if row["verdict"] == "FAIL"]
    if names is None:                          # NAMES: this group's slice of the whole job's (ingest_done)
        names = finding_names(job["mod"], job["id"], fails)
    for row, name in zip(fails, names):
        if filed(name, run):                   # filed by an ingest that died before marking the record
            found.append(name)
            continue
        rc, out = rimflow("finding", "--from", run, "--name", name, "--type", "UNTRIAGED", "--severity", "medium",
                          "--why", "%s/%s FAIL on %s%s: %s" % (row.get("chain"), row["row"],
                                                             {"stevedesktop": "SteveDesktop", "stevedesktop.b":
                                                              "Steve2"}.get(host, host), in_window(gres),
                                                             (row.get("detail") or "")[:160]))
        if rc != 0:     # retried: the run is reused, findings already filed are found in the shard
            return {"error": "finding %s not recorded: %s" % (name, out[-120:])}
        found.append(name)
    return {"run": run, "result": verdict(gres), "findings": found}


def repairs_of(att):
    """-> the HARNESS_REPAIR_ items ATT's harness fault filed or noted (repair()), from the shard. A crash inside a fault
    window is the host's, not the harness's: J20261103T233438Z-aa0482 died of an access violation in ast.parse inside
    F20261103T195921Z and its repair item, never told, went on chasing it (MODCHECK_DIAGNOSE_EXIT_FIVE_NO_SHEET)."""
    names = set()
    try:
        with open(shard_path(), encoding="utf-8") as f:
            for line in f:
                if att not in line or "HARNESS_REPAIR_" not in line:
                    continue
                e = json.loads(line)
                if e.get("event") == "spawn" and att in str(e.get("title")):
                    names.add(e.get("name"))
                elif e.get("event") == "note" and "seen again in testq %s" % att in str(e.get("text")):
                    names.add(e.get("id"))
    except (OSError, ValueError):
        pass
    return sorted(n for n in names if n and n.startswith("HARNESS_REPAIR_"))


_ATT = r"([^\s:,()]+)"
_SPAWNED_BY = re.compile(r"\(testq %s, " % _ATT)
_SEEN = re.compile(r"seen again in testq %s" % _ATT)
_QUAR = re.compile(r"testq %s quarantined:" % _ATT)
_QUAR_WIN = re.compile(r"fault window (\S+)")


def support(names=None):
    """-> {repair name: {"sightings": {attempt: how}, "invalid": {attempt: window id}, "dropped": bool}} from the
    shard, for NAMES (default: every HARNESS_REPAIR_ item the shard speaks of). A sighting is the attempt that filed
    the item (its spawn title) or a later `seen again in testq ATT` note; a `testq ATT quarantined:` note on the item
    marks that sighting invalid. The shard is the record: it survives a restart and is the same on every reader."""
    out = {}

    def slot(n):
        return out.setdefault(n, {"sightings": {}, "invalid": {}, "dropped": False})
    try:
        with open(shard_path(), encoding="utf-8") as f:
            for line in f:
                if REPAIR_PREFIX not in line:
                    continue
                e = json.loads(line)
                ev, n = e.get("event"), e.get("name") if e.get("event") == "spawn" else e.get("id")
                if not n or not n.startswith(REPAIR_PREFIX) or (names is not None and n not in names):
                    continue
                if ev == "spawn":
                    m = _SPAWNED_BY.search(str(e.get("title")))
                    if m:
                        slot(n)["sightings"][m.group(1)] = "filed"
                elif ev == "note":
                    t = str(e.get("text"))
                    q, m = _QUAR.search(t), _SEEN.search(t)
                    if q:
                        w = _QUAR_WIN.search(t)
                        slot(n)["invalid"][q.group(1)] = w.group(1) if w else "?"
                    elif m:
                        slot(n)["sightings"].setdefault(m.group(1), "seen again")
                elif ev == "drop":
                    slot(n)["dropped"] = True
    except (OSError, ValueError):
        pass
    return out


def withdraw(names=None, terminal=("done", "dropped", "superseded")):
    """Recompute each repair's support and drop an open one no valid sighting holds up -> the names dropped. A repair
    whose filing sighting the shard does not hold (filed elsewhere) is never judged: unknown support is not zero."""
    dead = [(n, s) for n, s in sorted(support(names).items())
            if s["sightings"] and not s["dropped"] and not set(s["sightings"]) - set(s["invalid"])]
    if not dead:
        return []
    try:
        items = ledger_items()
    except Exception as e:  # noqa: BLE001 - the next pass that recomputes tries again
        T.log("ingest withdraw: ledger unreadable, nothing dropped: %s" % e)
        return []
    gone = []
    for n, s in dead:
        if n not in items or items[n].state in terminal:
            continue
        base = re.match(r"%sCAUSE_[0-9A-F]+" % REPAIR_PREFIX, n)
        base = base.group(0) if base else n
        reason = ("withdrawn by testq ingest (TESTQ_QUARANTINE_BUILD_WITHDRAW_UNSUPPORTED): every sighting it rested on "
                  "ran inside a SteveDesktop fault window, so no evidence of a harness defect remains: %s. Evidence kept: "
                  "`python3 src/RimMandrake/Utils/testq/testq.py show <attempt's job>` and fault_windows.json. Reopen "
                  "signature: cause %s; a sighting outside a fault window files the next generation of %s."
                  % (", ".join("%s in %s" % (a, s["invalid"][a]) for a in sorted(s["sightings"])), base, base))
        rc, out = rimflow("drop", n, "--reason", reason[:900],
                          "--why", "auto: support recomputed after a fault-window quarantine, no valid sighting left")
        if rc != 0:
            T.log("ingest withdraw %s refused, retried on the next quarantine: %s" % (n, out[-200:]))
            continue
        gone.append(n)
        T.log("ingest withdraw %s: no valid sighting (%s)" % (n, ", ".join(sorted(s["sightings"]))))
        if _REPAIRED.get(base) == n:        # a later sighting of the cause files anew, never notes the dropped one
            del _REPAIRED[base]
        _REPAIR_ITEMS[0] = None     # the cache may predate this item's filing: a stale one would re-file its name
    return gone


def quarantine_one(rec, window):
    """A result from inside a fault window: off done/, a note on each item it speaks for and on each repair item its
    harness fault filed, an item job queued again."""
    job, res, was = rec["job"], rec.get("result") or {}, rec.get("ingested") or {}
    att = res.get("attempt") or job["id"]
    items = sorted({i for i in [job.get("item")] + list((job.get("row_items") or {}).values())
                    + list((was.get("groups") or {}).keys()) if i})
    repairs = repairs_of(att)
    new = FM.rerun_job(rec)
    said = "its verdict %s must not be counted" % was["run"] if was.get("run") else \
        "its verdicts must not be counted" if was.get("groups") else "no verdict recorded"
    needle = "testq %s quarantined:" % att
    refused = []
    for it in items:
        if not note_once(it, needle, "%s ran inside Steve SIMD fault window %s (last clean %s, first bad %s); %s%s"
                         % (needle, window["id"], window["start"], window["first_bad"], said,
                            "; re-queued as %s" % new if new else "")):
            refused.append(it)
    for it in repairs:
        if not note_once(it, needle, "%s this sighting ran inside Steve SIMD fault window %s (last clean %s, first bad "
                         "%s): a host fault, not evidence of a harness defect; this sighting no longer supports the "
                         "item (withdrawn when none outside a window remains)"
                         % (needle, window["id"], window["start"], window["first_bad"])):
            refused.append(it)
    withdrawn = withdraw(repairs)
    items = items + repairs
    FM.quarantine_move(rec, window, {"items": items, "rerun": new, "note_refused": refused, "was_ingested": bool(was),
                                     "withdrawn": withdrawn})
    T.log("ingest %s -> quarantined in %s, rerun %s%s" % (job["id"], window["id"], new,
                                                         ", note refused on %s" % refused if refused else ""))


def fault_note(state):
    """One ledger line for each onset and alarm, on the fault's own item: the record of when it came, boot by boot."""
    host = os.environ.get("TESTQ_FAULT_ITEM", "STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO")
    for w in FM.load()[0]:
        needle = "Steve fault window %s:" % w["id"]
        note_once(host, needle, "%s first bad %s at uptime %.2f h, CPUs %s, last clean %s; cause evidence %s"
                  % (needle, w["first_bad"], w["onset_uptime_h"], w["first_cpus"], w["start"], w.get("snapshot")))
    for kind, text in (("alarm", state.get("alarm")), ("BLIND", state.get("blind"))):
        if text:
            needle = "Steve fault monitor %s %s %s:" % (kind, state.get("boot_iso"), text.split()[0])
            note_once(host, needle, "%s %s" % (needle, text))


FAULT_WOKE = "fault_woke.json"      # what already woke the fault's ticket: {"seen": [window ids], "driver": verdict}


def wake_fault_ticket():
    """The fault's own ticket sleeps with no date (a block that starts model.RUNNER_WAKES); a NEW fault window, or its audio
    driver loaded or enabled again, wakes it, once per return. The first run takes every window there is as old news.
    -> the cause it woke for, or None. A refused unblock (the ticket is awake, ended, or held by another block) is logged
    and not asked again for that cause."""
    path, old = T.q(FAULT_WOKE), T.read_json(T.q(FAULT_WOKE))
    ids = [w["id"] for w in FM.load()[0]]
    driver = (T.read_json(T.q("steve_audio_driver.json")) or {}).get("verdict")
    now_ = {"seen": ids, "driver": driver if driver in ("LOADED", "ENABLED") else None}
    if driver in (None, "UNMEASURED"):      # could not look: the last thing seen of the driver stands
        now_["driver"] = (old or {}).get("driver")
    if old == now_:
        return None
    cause = None
    if old is not None:
        new = [i for i in ids if i not in old["seen"]]
        if new:
            cause = "fault window %s" % new[-1]
        elif now_["driver"] and not old.get("driver"):
            cause = "audio driver %s is %s" % (FM.AUDIO_DRIVER, now_["driver"])
    if cause:
        host = os.environ.get("TESTQ_FAULT_ITEM", "STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO")
        rc, out = rimflow("unblock", host, "--reason", "the fault tracker saw the fault return: " + cause)
        T.log("fault ticket %s %s: %s%s" % (host, "woken" if rc == 0 else "NOT woken", cause,
                                            "" if rc == 0 else " (%s)" % out[-200:]))
    T.S.dump(now_, path)
    return cause


_HELD = []      # non-empty while this process holds the clone lock (main holds it across ingest + publish)


def repo_lock_path():
    return os.path.join(tempfile.gettempdir(), "testq-repo-%s.lock" % hashlib.sha1(
        os.path.realpath(REPO).encode("utf-8")).hexdigest()[:12])


@contextlib.contextmanager
def repo_lock(wait_s=0):
    """One lock per clone, across every queue/caller: the queue's ingest.lock does not stop a second queue (backfill)
    or the Dispatcher's publisher from rebasing/aborting while this one has appended uncommitted RUNNER lines
    (review r8). Yields True when held (re-entrant within the process), False when still busy after wait_s."""
    if _HELD:
        yield True
        return
    with open(repo_lock_path(), "w") as fh:
        end = time.time() + wait_s
        while True:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.time() >= end:
                    yield False
                    return
                time.sleep(1)
        _HELD.append(1)
        try:
            yield True
        finally:
            _HELD.pop()


def repair_prose_paths(git):
    """-> the repo-relative items/HARNESS_REPAIR_*.md that repair() wrote and the RUNNER shard spawned, not yet committed:
    they travel in the shard's commit (a template for an item the ledger never got stays behind, unpublished)."""
    r = git("status", "--porcelain", "--untracked-files=all", "--", ITEMS_REL)
    if getattr(r, "returncode", 1) != 0:
        return []
    spawned = set()
    try:
        with open(shard_path(), encoding="utf-8") as f:
            for line in f:
                if REPAIR_PREFIX in line and '"spawn"' in line:
                    with contextlib.suppress(ValueError):
                        e = json.loads(line)
                        if e.get("event") == "spawn":
                            spawned.add(e.get("name"))
    except OSError:
        return []
    out = []
    for line in r.stdout.splitlines():
        rel = line[3:].strip().strip('"')
        name = os.path.basename(rel)[:-3] if rel.endswith(".md") else None
        if name in spawned and os.path.dirname(rel) == ITEMS_REL.replace(os.sep, "/"):
            out.append(rel)
    return sorted(out)


def publish(n, shard_rel=SHARD_REL, message=None):
    """_publish under the clone lock (waits up to 120 s), after clearing a leftover rebase / stale index.lock
    (clear_leftovers); what it did leads the result."""
    with repo_lock(120) as got:
        if not got:
            return "publish stopped: another ingest/publish holds this clone (retried next time)"
        return _publish_locked(n, shard_rel, message)


def _publish_locked(n, shard_rel=SHARD_REL, message=None):
    def git(*a):
        return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True, timeout=300)
    pre = clear_leftovers(git)
    if pre and pre.startswith("publish stopped"):
        return pre
    out = _publish(n, shard_rel, message)
    return "%s; %s" % (pre, out) if pre else out


def _publish(n, shard_rel=SHARD_REL, message=None):
    """Commit `shard_rel` alone, replay onto origin/main (dirty files carried), lint, push. Also the RimFlow v3
    Dispatcher's publisher for its DISPATCHER shard (rimflow/dispatcher.py passes its own shard and message)."""
    def git(*a):
        return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True, timeout=300)

    def git_index(*a):
        # repo_lock serializes publishers only: a `git status` index refresh or testq-tick's ExecStartPre pull in this
        # clone holds index.lock for a second, and an add then failed (RIMMANDRAKE_RETRY_STEWARD_LAUNCH_GIT_LOCK_
        # COUNTED_AS_SPENT, 2026-11-15 08:00 PST). Wait it out, a bounded number of times.
        for i in range(INDEX_LOCK_TRIES):
            r = git(*a)
            if r.returncode == 0 or "index.lock" not in (r.stderr or "") or i == INDEX_LOCK_TRIES - 1:
                return r
            time.sleep(INDEX_LOCK_WAIT_S)
    paths = [shard_rel] + (repair_prose_paths(git) + visit_row_paths(git) if shard_rel == SHARD_REL else [])
    a = git_index("add", "--", *paths)
    if a.returncode != 0:
        return "add failed (the lines stay in the working tree; the next ingest retries): " + a.stderr.strip()[-200:]
    if git("diff", "--cached", "--quiet", "--", *paths).returncode != 0:
        c = git_index("commit", "-q", "-m", message or "ledger: RUNNER ingest of %d testq job(s)" % n, "--", *paths)
        if c.returncode != 0:
            return "commit failed: " + c.stderr.strip()[-200:]
    p, note = None, ""
    for _ in range(3):
        # Never `pull --rebase`: it reads FETCH_HEAD, where a peer's fetch in this clone leaves a second line, and then
        # refuses with "Cannot rebase onto multiple branches" (8 stopped publishes by 2026-11-01). origin/main is one ref.
        r = git("fetch", "-q", "origin", "main")
        if r.returncode != 0:
            return "publish stopped: fetch failed, the commit stays local (the next ingest retries): " + \
                (r.stderr or r.stdout).strip()[-200:]
        # Never `git rebase` either: it refuses on ANY unstaged file, and this clone has several writers, each with a
        # live append in its own shard, so they blocked each other's publish and the clone sat ahead 7 / behind 49 for
        # 40 min (RIMMANDRAKE_UNJAM_DISPATCH_CLONE_TWO_WRITERS_BLOCK_EACH_REBASE, 2026-11-15). publish.py's replay is
        # the seats' own landing path: plumbing (no worktree), then a reset that carries dirty files and unions shards.
        head, why, stranded = replay_onto_origin()
        if why:
            return "publish stopped: the replay onto origin/main refused, the commit stays local (the next ingest " \
                "retries): " + why
        if stranded:
            note = "this clone's branch did not move (a dirty file overlaps origin's change): %s; " % stranded
        if git("merge-base", "--is-ancestor", head, "origin/main").returncode == 0:
            # nothing of this clone's left to push: linting it against origin would only read origin's newer lines as
            # removed (RIMMANDRAKE_UNSTICK_DISPATCH_CLONE_PUBLISH_LINT_REFUSES_HEAD: refused forever over d9d006f762)
            # ("; pushed": every caller reads that suffix as success, and all of this clone's work is on origin)
            return note + "nothing left to push, all of it is on origin/main; pushed"
        bad = lint_refusal(head)
        if bad:
            return "publish stopped: ledger_lint refuses HEAD, the commit stays local (the next ingest retries): " + bad
        p = git("push", "-q", "origin", "%s:refs/heads/main" % head)
        if p.returncode == 0:
            git("fetch", "-q", "origin", "main")
            return note + "pushed"
    return "push failed (the commit stays local; the next ingest retries): " + p.stderr.strip()[-200:]


def replay_onto_origin():
    """publish.py's rebase() on REPO -> (sha to push, None, None) once the branch sits on origin/main with the dirty
    files carried; (replayed tip, None, why) when the replay is good but a dirty file overlaps origin's change, so
    only the branch waits (publish.Stranded: the work still lands); (None, why, None) when it refuses. Loaded by
    path: this module has its own `publish`. Its prints are kept out of the ingest log line."""
    import contextlib as _cl
    import importlib.util
    import io
    spec = importlib.util.spec_from_file_location("rm_publish_tool", os.path.join(HERE, "..", "publish.py"))
    pub = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pub)
    said = io.StringIO()
    try:
        with _cl.redirect_stdout(said):
            rebuilt = pub.rebase(REPO)
    except pub.Stranded as s:
        return s.tip, None, str(s).splitlines()[0][:200]
    except pub.Refuse as e:
        return None, str(e)[-300:], None
    except (subprocess.SubprocessError, OSError) as e:          # commit-tree's check=True, a git timeout
        return None, ("replay failed: %s %s" % (e, (getattr(e, "stderr", "") or "").strip()))[-300:], None
    if rebuilt:                                       # a committed DLL conflicted: only ./publish rebuilds those
        return None, "a committed DLL conflicted (%s); land it with ./publish" % ", ".join(sorted(rebuilt)), None
    return subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True,
                          timeout=60).stdout.strip(), None, None


STALE_LOCK_S = 300
INDEX_LOCK_TRIES, INDEX_LOCK_WAIT_S = 6, 2     # an add/commit waits up to ~10 s on another git's index.lock
FRESH_LOCK_WAIT_S = 10      # clear_leftovers waits as long for a fresh index.lock to go before it stops the publish


def git_targets_repo(argv, env, cwd, root):
    """True when a git command line (argv list of str, env dict, its cwd or None) works on the clone at `root`: its cwd,
    a -C, --git-dir/--work-tree (either spelling) or GIT_DIR/GIT_WORK_TREE resolve to root or inside it. A git run from
    elsewhere with --git-dir still holds this clone's index.lock, so the cwd alone cannot tell."""
    def inside(path, base):
        path = os.path.realpath(os.path.join(base or "/", path))
        return path == root or path.startswith(root + os.sep)
    cands, here = [], cwd
    if cwd:
        cands.append(cwd)
    args, k = argv[1:], 0
    while k < len(args):
        a = args[k]
        if a == "-C" and k + 1 < len(args):
            here = os.path.join(here or "/", args[k + 1])
            cands.append(here)
            k += 1
        elif a in ("--git-dir", "--work-tree") and k + 1 < len(args):
            cands.append(os.path.join(here or "/", args[k + 1]))   # relative to the -C in force at this point
            k += 1
        elif a.startswith(("--git-dir=", "--work-tree=")):
            cands.append(os.path.join(here or "/", a.split("=", 1)[1]))
        elif a in ("-c", "--namespace", "--super-prefix", "--config-env") and k + 1 < len(args):
            k += 1                                 # a global option taking a separate value: not the subcommand
        elif not a.startswith("-"):
            break                                  # the subcommand: global options end here
        k += 1
    for key in ("GIT_DIR", "GIT_WORK_TREE"):
        if env.get(key):
            cands.append(os.path.join(cwd or "/", env[key]))   # env paths are relative to the cwd, not to -C
    return any(inside(c, None) for c in cands)


def git_procs_in_repo():
    """pids of live git processes working on REPO (a /proc scan: cwd, -C, --git-dir/--work-tree, GIT_DIR; the lock
    holder is one of these)."""
    found = []
    try:
        pids = [p for p in os.listdir("/proc") if p.isdigit()]
    except OSError:
        return found
    root = os.path.realpath(REPO)
    for pid in pids:
        try:
            with open("/proc/%s/cmdline" % pid, "rb") as f:
                argv = [x.decode("utf-8", "replace") for x in f.read().split(b"\0") if x]
            if not argv or os.path.basename(argv[0]) != "git" or int(pid) == os.getpid():
                continue
        except (OSError, ValueError):
            continue
        try:
            cwd = os.path.realpath(os.readlink("/proc/%s/cwd" % pid))
        except OSError:
            cwd = None
        try:
            with open("/proc/%s/environ" % pid, "rb") as f:
                env = dict(x.decode("utf-8", "replace").split("=", 1) for x in f.read().split(b"\0") if b"=" in x)
        except OSError:
            env = {}
        if git_targets_repo(argv, env, cwd, root):
            found.append(int(pid))
    return found


def clear_leftovers(git, now=None, procs=git_procs_in_repo):
    """Before publish touches the index: (1) a rebase a killed publish left half done is aborted, or the next commit
    lands on a detached HEAD that `rebase --abort` then drops (review S, F2); (2) a stale .git/index.lock (older than
    STALE_LOCK_S, no live git process in the clone) is removed, one still held by a git process stops the publish
    (review S, F3). -> None, or a message: "publish stopped: ..." stops, anything else is a log of what was done
    (callers prefix it to their result)."""
    gd = git("rev-parse", "--git-dir").stdout.strip()
    gd = gd if os.path.isabs(gd) else os.path.join(REPO, gd)
    notes = []
    lock = os.path.join(gd, "index.lock")
    if os.path.exists(lock) and now is None:       # an injected now is a simulated clock: no real wait
        # an unlocked reader (`git status` refreshing the index, testq-tick's ExecStartPre pull) holds it for under a
        # second: wait it out as the add does, or the publish stops on it (RIMMANDRAKE_RETRY_JUDGE_LAUNCH_GIT_LOCK_SPENT_
        # THE_CYCLE, measured 2026-11-15)
        t0 = time.time()
        while os.path.exists(lock) and time.time() - t0 < FRESH_LOCK_WAIT_S:
            try:
                if time.time() - os.path.getmtime(lock) >= STALE_LOCK_S:
                    break
            except OSError:
                break
            time.sleep(0.25)
        if not os.path.exists(lock):
            notes.append("waited %.1f s for another git's index.lock" % (time.time() - t0))
    if os.path.exists(lock):
        try:
            age = (now if now is not None else time.time()) - os.path.getmtime(lock)
        except OSError:
            age = 0
        if age >= STALE_LOCK_S:
            live = procs()
            if live:
                return "publish stopped: index.lock is %d s old and git process(es) %s hold the clone" % (age, live)
            try:
                os.remove(lock)
                notes.append("removed stale index.lock (%d s old, no live git process)" % age)
            except OSError as e:
                return "publish stopped: stale index.lock (%d s old) could not be removed: %s" % (age, e)
        else:
            return "publish stopped: index.lock present (%d s old, under %d s: another git may be running)" % (
                age, STALE_LOCK_S)
    if any(os.path.isdir(os.path.join(gd, d)) for d in ("rebase-merge", "rebase-apply")):
        r = git("rebase", "--abort")
        notes.append("aborted a leftover rebase (exit %d)" % r.returncode)
        if r.returncode != 0:
            return "publish stopped: leftover rebase could not be aborted: " + (r.stderr or r.stdout).strip()[-200:]
    return "; ".join(notes) or None


def lint_refusal(rev="HEAD"):
    """ledger_lint on `rev` (HEAD, or the replayed tip when the branch could not move) vs origin/main, as the pre-push hook runs it (the dispatch clone has no hooks:
    TESTQ_DISPATCH_PUSH_ENFORCE_LINT) -> None when clean, else why not to push. A lint that cannot run or crashes
    refuses too: this pusher is unattended, so it never pushes unlinted."""
    script = os.path.join(REPO, "src", "RimMandrake", "Utils", "ledger_lint.py")
    if not os.path.isfile(script):                   # a sparse clone without it: lint with this checkout's copy
        script = os.path.join(HERE, "..", "ledger_lint.py")
    try:
        r = subprocess.run([sys.executable, script, "--rev", rev, "--root", REPO, "--base", "origin/main"],
                           capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as e:
        return "ledger_lint could not run: %s" % e
    out = (r.stdout or "") + (r.stderr or "")
    finished = re.search(r"^ledger_lint: \d+ findings? over ", out, re.M)
    if r.returncode == 0 and finished:
        return None
    lines = [ln.strip() for ln in out.splitlines() if ln.strip() and not ln.startswith("note:")]
    return ("exit %d: " % r.returncode) + " | ".join(lines[-4:])[-300:]


def unpublished(shard_rel=SHARD_REL):
    """True when an earlier ingest left work behind: RUNNER lines not committed (a publish that died or failed
    before its commit; the done records are already marked, so n is 0 from then on) or commits not pushed."""
    def git(*a):
        return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True, timeout=60).stdout.strip()
    return bool(git("status", "--porcelain", "--", shard_rel)) \
        or (shard_rel == SHARD_REL and bool(repair_prose_paths(lambda *a: subprocess.run(
            ["git", "-C", REPO] + list(a), capture_output=True, text=True, timeout=60)))) \
        or (shard_rel == SHARD_REL and bool(visit_row_paths(lambda *a: subprocess.run(
            ["git", "-C", REPO] + list(a), capture_output=True, text=True, timeout=60)))) \
        or git("rev-list", "--count", "origin/main..HEAD") \
        not in ("", "0")


def rebase_left(clear=True):
    """A publish killed mid-rebase leaves the shard in the rebase's tree; lines ingested into it would be thrown away by
    the `rebase --abort` publish runs, with their records already marked. So leftovers are cleared BEFORE ingesting,
    and while a rebase is still there nothing is ingested (-> True)."""
    def git(*a):
        return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True, timeout=300)
    pre = clear_leftovers(git) if clear else None     # publication off: look, never touch
    if pre:
        T.log("ingest pre-clear: %s" % pre)
    gd = git("rev-parse", "--git-dir").stdout.strip()
    gd = gd if os.path.isabs(gd) else os.path.join(REPO, gd)
    if any(os.path.isdir(os.path.join(gd, d)) for d in ("rebase-merge", "rebase-apply")):
        T.log("ingest skipped: a rebase is still in progress in %s" % REPO)
        return True
    return False


def main():
    T.ensure_dirs()
    with open(T.q("ingest.lock"), "w") as lk:
        try:
            fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("ingest already running")
            return 0
        with repo_lock(0) as got:
            if not got:
                T.log("ingest skipped: another ingest/publish holds this clone")
                return 0
            return _ingest_locked()


def _ingest_locked():
    _REPAIR_HISTORY[0] = None
    if True:
        push = os.environ.get("TESTQ_INGEST_PUSH", "1") != "0"
        if rebase_left(clear=push):
            return 0
        n = 0
        windows, fstate = FM.load()
        for path in sorted(os.listdir(T.q("done"))):
            rec = T.read_json(T.q("done", path))
            if not rec or not path.endswith(".json"):
                continue
            try:
                verdict_of_gate, why = FM.gate(rec, windows, fstate)
                if verdict_of_gate == "quarantine":
                    quarantine_one(rec, why)
                    n += 1
                    continue
            except Exception as ex:     # noqa: BLE001 - as below; an unjudged record waits, it is never counted
                T.log("ingest %s: fault gate failed, held: %s: %s" % (rec.get("job", {}).get("id"), type(ex).__name__, ex))
                continue
            if verdict_of_gate == "count" and str(why or "").startswith("advisory: ") \
                    and (rec.get("fault_window") or {}).get("id") != why[10:]:
                rec["fault_window"] = {"id": why[10:], "mode": "advisory", "at": T.S.utcnow()}
                T.S.dump(rec, T.q("done", path))
            if "ingested" in rec or verdict_of_gate == "hold":
                continue
            pend = rec.get("ingest_pending") or {}
            if pend and time.time() - pend.get("last", 0) < RETRY_S:
                continue
            try:
                out = ingest_one(rec)
            except Exception as ex:     # noqa: BLE001 - one bad record (a rimflow timeout) must not stop the rest
                out = {"error": "crash: %s: %s" % (type(ex).__name__, ex)}
            tries, spent = tries_after(pend, out.get("error"))
            if "error" in out and not spent:
                rec["ingest_pending"] = {"tries": tries, "last": time.time(), "error": out["error"]}
                T.S.dump(rec, T.q("done", path))
                T.log("ingest %s: try %d of %d failed, retried in %d s: %s"
                      % (rec["job"]["id"], tries, MAX_TRIES, RETRY_S, out["error"][-200:]))
                continue
            rec.pop("ingest_pending", None)
            rec["ingested"] = dict(out, at=T.S.utcnow())
            T.S.dump(rec, T.q("done", path))
            T.log("ingest %s -> %s" % (rec["job"]["id"], json.dumps(out)[:300]))
            n += 1
        if fstate:
            fault_note(fstate)
            n += bool(wake_fault_ticket())
        if n:
            withdraw()      # a drop refused earlier is tried again whenever the pass did anything
        if push and (n or unpublished()):
            T.log("ingest git: %s" % publish(n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
