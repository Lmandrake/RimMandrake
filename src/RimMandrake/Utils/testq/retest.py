"""testq/retest.py -- what counts as a verdict at a code version (RETEST_RULE_ONCE_PER_CODE_VERSION).

Owner ruling by card 2026-10-31, "Retest only after a code change": an item is tested once per code version; a
harness-invalid run is repaired, never counted.

A CODE VERSION is modcheck's gate.code_version: the chain's runtime hash, the runtime hash of every mod composed with
it, its own code slice and its declared inputs. The harness is deliberately not in it: a harness change must not
retest what stood, and what it broke was never counted.

A row is the HARNESS's when it says the run did not measure (CAUSES). Such a chain has no verdict, unless a row FAILED:
a real FAIL stands whatever else broke. ingest records no verify for it and files one repair item per distinct cause;
the filler holds its chains while that item is open. A row owed a live check, or a map without the feature, is a
real GAP and so a verdict: nothing a rerun at the same code can change. A reader row with no result from its driver
("no <driver> result at the current mod hash") is the harness's: the driver, not the code, decides whether it reads.
"""
import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import invalid_class as IC  # noqa: E402

CAUSES = (("canary", r"canary red"),
          ("site_hold", r"could not hold the site quiet"),
          ("surprise", r"\bsurprise: |a surprise ended this chain"),
          ("selftest_not_run", r"SelfTest did not run"),
          ("absent_from_sheet", r"absent from the sheet"),
          ("run_aborted", r"\(run aborted"),
          # TESTQ_ROWS_MEASURE_THE_UNMEASURED_THIRD: a reader row whose driver left no result. testq runs every driver
          # (modcheck --drivers on), so no result means the driver failed, timed out or was skipped: 30 hose_live_rows
          # (proof_hose's offline gate red) and 13 sprinkler/thirst rows (bridge DeadlineError) were held as GAPs at
          # their code version and never re-run once the driver was repaired.
          ("driver_undelivered", r"\bno [\w .*-]+ result at the current mod hash"))
# A chain another chain's failure stopped (suite.py upstream_reason, cross-chain). NOT "an UNMEASURED component ended this
# chain earlier": that is the chain's OWN earlier row (suite.py, intra-chain), already judged by row_cause on that row.
# HARNESS_REPAIR_CAUSE_8135787B: matching it held flow_map_controls_six, pit_access_gear_ladders and
# suspension_bridges_and_covers -- each ended by its own real `live check owed`/`look owed` GAP -- under thirst's cause.
UPSTREAM = re.compile(r"upstream failed")
ORPHAN = "<no chain>"           # split_rows key: rows the sheet never reached carry no chain
NOT_A_FAULT = ("BLOCKED_SELECTION",)        # the selection was refused: no run happened
LANE_CAUSES = ("CANARY",)                   # testq.PAUSE_ON with an INVALID outcome: lane_finding has these
COMPANION_STALE = re.compile(r"companion (STALE|UNSTAMPED|MISSING) ")


def normal(text):
    """Text with what differs between two sightings of one cause taken out."""
    t = re.sub(r"\S*[\\/]\S*", "<path>", str(text or ""))
    t = re.sub(r"\b(?:0x)?[0-9a-fA-F]{8,}\b", "#", t)
    return re.sub(r"\s+", " ", re.sub(r"\d+(?:\.\d+)?", "#", t)).strip()


def row_cause(row):
    """-> the cause signature of a row that did not measure, or None."""
    if row.get("verdict") in ("PASS", "FAIL", "SKIP"):
        return None
    detail = str(row.get("detail") or "")
    for name, pat in CAUSES:
        if re.search(pat, detail):
            return "%s: %s" % (name, normal(detail)[:80])
    if row.get("validity") == "invalid":
        return "invalid_run: %s" % normal(detail)[:80]
    return None


def split_rows(rows):
    """-> (kept, held, {chain or ORPHAN: cause}): the rows that may carry a verdict, those that may not, and why."""
    by, order = {}, []
    for r in rows or []:
        k = r.get("chain") or ORPHAN
        if k not in by:
            order.append(k)
        by.setdefault(k, []).append(r)
    causes = {}
    # the chains first, then ORPHAN: a row the sheet never reached whose planned_chain (the worker's, from modcheck's
    # EXPECTED_ROW_CHAINS) is a chain the harness stopped is that stop's consequence, held under the chain's cause, not
    # a second repair item for one event (HARNESS_REPAIR_CAUSE_AC81755A: a site hold before any component filed both)
    for k in [k for k in order if k != ORPHAN] + [k for k in order if k == ORPHAN]:
        if k == ORPHAN or not any(r.get("verdict") == "FAIL" for r in by[k]):
            kinds = {}          # every KIND of fault: closing the repair of one must not release the other
            for r in by[k]:
                c = row_cause(r)
                if c and not (k == ORPHAN and r.get("planned_chain") in causes):
                    kinds.setdefault(c.split(":")[0], c)
            if kinds:
                causes[k] = " + ".join(kinds.values())
    causes = {k: causes[k] for k in order if k in causes}      # first-seen order, as before
    if causes:          # a chain stopped by a harness chain's failure: not a verdict on it either
        first = next(iter(causes.values()))
        for k in order:
            if k not in causes and k != ORPHAN and not any(r.get("verdict") == "FAIL" for r in by[k]) \
                    and any(UPSTREAM.search(str(r.get("detail") or "")) for r in by[k]):
                causes[k] = first
    kept, held = [], []
    for k in order:
        if k == ORPHAN:
            for r in by[k]:
                (held if row_cause(r) else kept).append(r)
        else:
            (held if k in causes else kept).extend(by[k])
    return kept, held, causes


def companion_stale(res):
    """The worker refused this job at deploy for a companion not built from its sources: the lane's plumbing, which
    the stager (companion_stage.py) fixes by itself. The job ran nothing of its chains."""
    return (res or {}).get("outcome") == "INVALID" and res.get("cause") == "DEPLOY" \
        and bool(COMPANION_STALE.search(str(res.get("note") or "")))


# STEVE_LANE_UNSTICK_BRAKED_UNOWNED_8EB8: modcheck refused because the running load was not the list it composed. The
# worker names it (harness_cause); a result from before that carries only the clipped tail of load_gap's reasons.
STALE_LOAD = re.compile(r"the running load is not the composed list|loaded but not composed: |^stale_load\b")


#: MODCHECK_STALE_LOAD_FIX_UNINSTALLED_MOD: a composed mod with no folder on the host. Its own cause, never stale_load:
#: no restart loads it, and it repeats on every job until someone installs the mod there.
NOT_INSTALLED = "mod_not_installed"


def stale_load(res):
    """-> "repaired" when the result predates the worker's restart onto the composed list (no harness_cause: the
    worker that wrote it could not restart, the current one does), "unrepaired" when the current worker recorded the
    cause and still ended INVALID (it restarted and the load did not fit, or modcheck had restored FULL so no restart
    could help: both repeat, so neither may release a brake), else None."""
    res = res or {}
    if res.get("outcome") != "INVALID" or res.get("cause") != "HARNESS" or res.get("harness_cause") == NOT_INSTALLED:
        return None
    if res.get("harness_cause") != "stale_load" and not STALE_LOAD.search(str(res.get("note") or "")):
        return None
    return "unrepaired" if res.get("harness_cause") == "stale_load" or res.get("stale_load_bounced") else "repaired"


def job_cause(res):
    """-> the cause signature of a job that ended with no sheet to read, or None (DONE, a refusal, a paused lane, a
    stale companion: as a cause it filed a repair item that held every chain the job named, 59 of them, until someone
    closed it, while the stager had already fixed the fault)."""
    if (res or {}).get("outcome") != "INVALID" or res.get("cause") in NOT_A_FAULT + LANE_CAUSES or companion_stale(res):
        return None
    note = str(res.get("note") or "")
    if res.get("harness_cause") == NOT_INSTALLED:
        return "HARNESS: mod_not_installed, the composed list names a mod this host has not installed"
    if stale_load(res):         # its own repair item, not the catch-all "modcheck exit 1, no sheet" (4E52E202)
        return "HARNESS: stale_load, the running load is not the composed list%s" % (
            ", which the worker could not restart away" if stale_load(res) == "unrepaired" else "")
    # RIMMANDRAKE_STOP_STEVEDESKTOP_INVALID_RUNS_REPEATING_UNFIXED: a known fault files under ONE stable name. The note
    # is a log tail, so hashing its head split "the game would not start" into five items and merged five faults
    # into the catch-all below.
    known = IC.cause_key(res)
    if known:
        return known
    m = re.match(r"modcheck exit (\S+) and no sheet JSON", note)
    if m:
        err = re.search(r"\b[A-Z]\w*Error\b", note)
        return "%s: modcheck exit %s, no sheet%s" % (res.get("cause"), m.group(1), " (%s)" % err.group(0) if err else "")
    return "%s: %s" % (res.get("cause"), normal(note)[:80])


def repair_base(cause):
    """The repair item's name: the cause's, not a job's, so a second sighting finds the first."""
    return "HARNESS_REPAIR_CAUSE_%s" % hashlib.sha1(cause.encode("utf-8")).hexdigest()[:8].upper()


def _generations(items, base):
    """-> the names of BASE's repair items that exist: BASE, BASE_2, BASE_3 ..."""
    names = []
    while (base if not names else "%s_%d" % (base, len(names) + 1)) in (items or {}):
        names.append(base if not names else "%s_%d" % (base, len(names) + 1))
    return names


def repair_slot(items, base, terminal=("done", "dropped", "superseded")):
    """-> (name, "note") for an open repair of this cause, else (the next free name, "file"). A cause back after its
    repair closed is a new item: a closed item stays closed."""
    for name in _generations(items, base):
        if items[name].state not in terminal:
            return name, "note"
    gen = len(_generations(items, base)) + 1
    return (base if gen == 1 else "%s_%d" % (base, gen)), "file"


def repair_open(items, cause, terminal=("done", "dropped", "superseded")):
    """True while an item is open for CAUSE. No item yet (a run from before this rule, or ingest still to come) holds
    nothing: a hold nobody can see or release would be a silent stop."""
    return any(items[n].state not in terminal for n in _generations(items, repair_base(cause)))


def causes_of(res):
    """-> every cause signature RES carries: one per chain the harness stopped (DONE), or the job's own (no sheet)."""
    res = res or {}
    if res.get("outcome") == "DONE":
        return sorted(set(split_rows(res.get("rows") or [])[2].values()))
    return [c for c in [job_cause(res)] if c]


def repaired_by(res, name):
    """TESTQ_REPAIR_FIX_TICKETS_NAME_THEIR_PASS: does the result RES pass repair item NAME (a HARNESS_REPAIR_CAUSE_<HEX>,
    or its _N generation)? -> (ok, why). It passes only when the run measured (DONE, at least one row with a verdict) and
    no cause it carries is NAME's cause. So the sighting that filed NAME must FAIL this (the negative control): a fix
    that makes it pass silenced the detector instead of repairing the fault."""
    base = re.sub(r"_\d+$", "", name)
    res = res or {}
    hit = [c for c in causes_of(res) if repair_base(c) == base]
    if hit:
        return False, "still carries the cause: %s" % hit[0]
    if res.get("outcome") != "DONE":
        return False, "no sheet: outcome %s (%s)" % (res.get("outcome"), res.get("cause"))
    judged = [r for r in res.get("rows") or [] if r.get("verdict") in ("PASS", "FAIL", "SKIP")]
    if not judged:
        return False, "DONE, but no row carries a verdict"
    return True, "%d row(s) carry a verdict and none carries %s's cause" % (len(judged), base)


QUEUE_HOST = "archmagi"     # the dispatcher's machine: its queue dir is the only one that holds job records


def remote_record(job_id, qhome):
    """-> (record or None, a clause saying what was asked of whom). Off the dispatcher's machine the job is read from
    its queue over SSH (TESTQ_QUEUE_SSH, default mandrake@archmagi-wsl; set it empty to stay local). Read-only."""
    import json
    import os
    import shlex
    import socket
    import subprocess
    me = (os.environ.get("RM_HOST") or socket.gethostname()).strip().lower()
    target = os.environ.get("TESTQ_QUEUE_SSH", "mandrake@archmagi-wsl")
    if me == QUEUE_HOST or not target:
        return None, ""
    paths = " ".join(shlex.quote("%s/%s/%s.json" % (qhome, st, job_id)) for st in ("done", "running", "pending", "cancelled"))
    cmd = "for f in %s; do [ -f \"$f\" ] && exec cat \"$f\"; done; exit 3" % paths
    try:
        r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", "-o", "LogLevel=ERROR", target, cmd],
                           # budget: danger=a hung ssh holds the retest; never reached in the 14 days to 2026-11-24; no record
                           # budget: of its run
                           capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, ", nor could %s be asked (%s)" % (target, e)
    if r.returncode == 3:
        return None, " here or on %s" % target
    if r.returncode != 0:
        return None, ", and %s did not answer (ssh exit %d: %s)" % (target, r.returncode, r.stderr.strip()[-200:])
    try:
        return json.loads(r.stdout), ""
    except ValueError:
        return None, ", and %s returned an unreadable record" % target


def passed_since(recs, mod, chain, since, item):
    """-> (job id or None, why): the first done record of MOD whose selector names CHAIN, submitted at or after SINCE
    (ISO, compared as text: testq stamps are all `YYYY-MM-DDTHH:MM:SSZ`), whose result passes repair ITEM. The item's
    "re-run the same job" pass, for an outcome check that cannot know the re-run's job id when it is written."""
    seen = 0
    for rec in sorted(recs or [], key=lambda r: str(((r or {}).get("job") or {}).get("submitted") or "")):
        job = (rec or {}).get("job") or {}
        if job.get("mod") != mod or chain not in ((job.get("selector") or {}).get("chains") or []) \
                or str(job.get("submitted") or "") < since:
            continue
        seen += 1
        ok, why = repaired_by(rec.get("result"), item)
        if ok:
            return job.get("id"), why
    return None, "%d done %s job(s) naming %s since %s, none passes %s" % (seen, mod, chain, since, item)


def main(argv=None):
    """`retest.py passed <job-id|record.json> <REPAIR_ITEM>`: exit 0 when that job's result passes the repair item, 1
    when it does not, 2 when there is no finished record to read. `retest.py passed-since <MOD> <CHAIN> <ISO>
    <REPAIR_ITEM>`: exit 0 when a done job of that mod and chain, submitted since then, passes; 1 when none does; 2
    when the queue cannot be read here."""
    import argparse
    import glob
    import json
    import os
    import sys
    ap = argparse.ArgumentParser(prog="retest.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("passed", help="does a finished job's result pass a HARNESS_REPAIR_CAUSE_ item?")
    p.add_argument("job", help="a testq job id (looked up in the queue) or a path to its done record")
    p.add_argument("item")
    ps = sub.add_parser("passed-since", help="does any done job of MOD naming CHAIN since ISO pass the item?")
    for n in ("mod", "chain", "since", "item"):
        ps.add_argument(n)
    a = ap.parse_args(argv)
    if a.cmd == "passed-since":
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import testq as T
        done = os.path.join(T.QHOME, "done")
        if not os.path.isdir(done):
            print("UNMEASURED: no done queue at %s on this host" % done)
            return 2
        recs = []
        for f in glob.glob(os.path.join(done, "*.json")):
            try:
                with open(f, encoding="utf-8") as fh:
                    recs.append(json.load(fh))
            except (OSError, ValueError):
                continue        # a record mid-write: the next check reads it
        jid, why = passed_since(recs, a.mod, a.chain, a.since, a.item)
        print("%s: %s" % ("PASS %s" % jid if jid else "FAIL", why))
        return 0 if jid else 1
    rec = None
    if os.path.isfile(a.job):
        try:
            with open(a.job, encoding="utf-8") as f:
                rec = json.load(f)
        except (OSError, ValueError) as e:
            print("UNMEASURED: cannot read the record %s (%s)" % (a.job, e))
            return 2
    else:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import testq as T
        st = T.where(a.job)
        if st:
            rec = T.read_json(T.q(st, a.job + ".json"))
        else:
            # The queue is the dispatcher's (Archmagi): on SteveDesktop the local queue dir is empty, and the item's
            # verify command crashed into "expected str ... not NoneType" there (HARNESS_REPAIR_CAUSE_17704C88).
            rec, where_ = remote_record(a.job, T.QHOME)
            if rec is None:
                print("UNMEASURED: %s is in no queue state under %s%s" % (a.job, T.QHOME, where_))
                return 2
        if rec is None:
            print("UNMEASURED: the record of %s under %s is unreadable" % (a.job, T.QHOME))
            return 2
    res = rec.get("result")
    if not res:
        print("UNMEASURED: %s has no result yet" % a.job)
        return 2
    ok, why = repaired_by(res, a.item)
    print("%s: %s %s" % ("PASS" if ok else "FAIL", a.job, why))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
