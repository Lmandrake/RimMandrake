#!/usr/bin/env python3
"""evidence_gate.py - the one evidence-record close predicate, run in SHADOW beside today's close gate
(RIMFLOW_BUILD_ONE_EVIDENCE_RECORD step 09b; redesign_final.md WP-09 / section 3.4, redesign.md section 2).

The question redesign.md section 2.2 says a Relentless close should ask: is there a green evidence record for this exact
sha whose exam is the frozen exam? `green()` answers it from one record (evidence.py, 09a). Green, as far as today's
record can carry it (section 2.1; breaks, hunks and holdouts have no entry kind yet, so they are not judged here):
    - the record verifies (an edited, cut or forged record is no evidence)
    - its newest box run (kind `run`) is green, exit 0, against the frozen exam (exam_hash = the contract's hash); a
      `skipped` run (an offbox / reach_ok contract the box cannot run by design) is not red: the Marker decides. An
      `unrunnable` run is not green and rejects (RULED, EVIDENCE_SHADOW_FIX_REPORT_NEVER_READS_ZERO): `skipped` is a route
      declared and vetted at contract time; `unrunnable` is a proof nobody could run and nobody declared, so the box
      measured nothing and the record holds only the Marker's word. The route for it is `relentless.py rebind`. When the
      gate accepts such a close the gate is the one that is wrong, and the row stays a real disagreement
    - its newest Marker verdict is PASS: WEAK, FAIL and UNMEASURED do not close ("a WEAK verdict cannot close"), and
      a WEAK the live narrow rule reads as PASS (relentless_wall.acted_weak) is still WEAK here
    - an empty-diff close (--no-code) closes only on a `no_code` exam (G15: empty-diff Judge closes are false closes)
    - an exam that declares a live clause closes done only with a live attestation (today: the line cli._live_gate has
      checked and accepted, never the raw --live text); without one the item is `built`, not done

SHADOW ONLY: cli.py calls `shadow()` for every close of an item the Relentless store holds, once the close is decided
(after `_close_gate` and `_live_gate`, so the gate's word is the whole close's and `live` is a checked line). It never refuses, never raises and never waits long (git calls time out at GIT_TIMEOUT_S); it
appends one row per close to <store>/evidence_shadow.jsonl - the gate's word, the predicate's word, `disagree`.
09c deletes the replaced guards one at a time once the corpus and SAMPLE closes of this log agree; until then nothing
here decides anything.

The reading 09c cites (EVIDENCE_SHADOW_FIX_REPORT_NEVER_READS_ZERO). The log is append-only and its first rows predate the
working writers, so `report` over the whole log can never read 0 again:
    - a declared window: `report --since <writer fix | sha | ISO time>` counts the closes at or after it and says how many
      it left out, and of what. A fix's time is its commit, so a process still on the old code can write after it: a
      window that starts too early overstates the disagreements and never hides one.
    - scope: each row records who closed (`closed_by`: relentless, owner, seat). The predicate speaks for a Relentless
      close; an owner-authority close (--owner-said, --by-card, --per-ruling, seat OWNER) overrides the gate on his word
      and has no verdict to find, so it is its own line, neither agreement nor disagreement. Rows older than the field
      read it from the ledger's close event; with no such event it is `unrecorded`, and such a close stays judged. A
      seat's hand close stays judged too: nothing but his authority takes a close out of scope.
    - rescore reads the finish receipts: a snapshot without items/*/receipts cannot see the wedge cohort, and its wedge
      rows read as unexplained `no run` (the 10 such rows of 2026-11-06 were all wedge; `cohort_rows` names each row).
    - neither reading crashes on what it cannot read (EVIDENCE_CLI_HARDEN_MALFORMED_ROWS_CRASH). A log line that is no
      close row is left out and counted aloud (`unreadable_rows`); a row that cannot be judged (git timed out, a broken
      state.json) is an unexplained disagreement by name; an index that is unreadable or holds nothing explains nothing,
      so it can only overstate the disagreements. A store, log or ledger that cannot be read at all is UNMEASURED, exit 2.

    python3 src/RimMandrake/rimflow/evidence_gate.py report [--since X] [--json]  the disagreement count toward the sample
    python3 src/RimMandrake/rimflow/evidence_gate.py rescore --snapshot DIR  replay a frozen store's shadow rows, exit 1 on
                                                                            any disagreement no cohort explains, or any
                                                                            row or index it could not read
    python3 src/RimMandrake/rimflow/evidence_gate.py corpus check          the false/valid close corpus, exit 1 on a miss
    python3 src/RimMandrake/rimflow/evidence_gate.py corpus build          rebuild it from the ledger + store (writes)

The corpus (evidence_gate_corpus.json) is built from REAL past Relentless closes. No evidence record existed before
09a, so each close's record is reconstructed from what the store kept for it: the Marker's verdict (check.verdict, or
the close audit's), the contract (exam hash, live clause), the close event (--no-code, --live). The box run is taken
as green because finish accepted it. False closes: every close whose deciding Marker word was WEAK (the store's done
WEAK items and close_audits.jsonl's narrow_weak draws) and every empty-diff `--no-code` Relentless close. Valid
closes: every code close whose Marker said PASS.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import evidence                                                 # noqa: E402

DEFAULT_ROOT = "/home/mandrake/rm/relentless"       # relentless.DEFAULT_ROOT, not imported: cli.py must stay light
SHADOW = "evidence_shadow.jsonl"
SAMPLE = 30                 # redesign_final.md: the shadow ends on a sample count, not on days
GIT_TIMEOUT_S = 5
CORPUS = os.path.join(HERE, "evidence_gate_corpus.json")
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
AUDITS = os.path.join(REPO, "infrastructure", "state", "close_audits.jsonl")
READ_INDEX = object()       # judge(): no first_at handed in, read the store's index
PRE_RECORD = "pre_record"   # a judge() cohort: the candidate predates every evidence row (see _pre_record)
SKIPPED = "skipped"         # relentless_boxrun: the contract measures outside the box (offbox adapters, reach_ok)
BOOKKEEPING = ("infrastructure/state/ledger/", "infrastructure/state/items/", "infrastructure/state/queue/",
               "infrastructure/state/code_review/")      # relentless.BOOKKEEPING, not imported (cli.py stays light)
WORK_DEPTH = 60             # commits naming the item read under the candidate (relentless.WORK_SHA_DEPTH)
RELENTLESS_WHY = "relentless"       # relentless.py closes with --why "relentless: blind check passed"
RELENTLESS_CLOSE = "relentless"     # closed_by: the supervisor's close (the words begin "relentless:", see closed_by)
OWNER_CLOSE = "owner"               # closed_by: his authority; out of the predicate's scope
SEAT_CLOSE = "seat"                 # closed_by: a seat's hand close, still judged
UNRECORDED = "unrecorded"           # closed_by: a row older than the field, and the ledger holds no close to read it from
WRITER_FIXES = {"marker_writer": "8e3e8ef4a5"}  # report --since: the Marker's receipts reach the record (+ 789b5d71a2)


def store_dir():
    return os.path.join(os.environ.get("RELENTLESS_ROOT") or DEFAULT_ROOT, "store")


def own_root(root):
    """Pure but for realpath. May a close on a throwaway ledger log to this RELENTLESS_ROOT? Only a root of its own: a
    worker's env holds the real one, and a selftest under it that closed a fixture named after a real item wrote that
    fixture's close into the real log (DEPLOY_GUARD_FIX_EXCLUDE_DIR_MISMATCH's rows, EVIDENCE_GATE_FIX_WORK_COMMIT_HIDES_PASS)."""
    return bool(root) and os.path.realpath(root) != os.path.realpath(DEFAULT_ROOT)


def exam_of(contract):
    """-> the exam as the predicate reads it: {hash, live, no_code}. hash is relentless_boxrun.contract_hash."""
    c = contract or {}
    return {"hash": hashlib.sha256(json.dumps(c, sort_keys=True).encode()).hexdigest(),
            "live": bool(c.get("live")), "no_code": bool(c.get("no_code"))}


def green(entries, exam, no_code=False, live=None, tampered=()):
    """Pure. entries: one record's entries in order (evidence.read). exam: exam_of(...) or None (not known: hash and
    clauses unchecked). no_code: the close names no work commit. live: the live attestation the close carries (a checked
    line) or None. tampered: evidence.verify's problems. -> (accepted, [reason]); every failing rule gives a reason."""
    why = []
    if tampered:
        why.append("tampered: the record does not verify (%s)" % "; ".join(tampered)[:200])
    runs = [e for e in entries if e.get("kind") == "run"]
    marks = [e for e in entries if e.get("kind") == "marker"]
    if not entries:
        why.append("no record: no evidence record at this sha")
    if not runs:
        why.append("no run: no box run on record")
    else:
        r = runs[-1]
        if r.get("verdict") == SKIPPED:
            pass        # an offbox / reach_ok contract: the box cannot run it by design, the Marker's adapters do
        elif r.get("verdict") != "green" or r.get("exit") != 0:
            why.append("run not green: newest box run is %s, exit %s" % (r.get("verdict"), r.get("exit")))
        if exam and r.get("exam_hash") != exam.get("hash"):
            why.append("exam drift: the run's exam %s is not the frozen exam %s"
                       % (str(r.get("exam_hash"))[:12], str(exam.get("hash"))[:12]))
    if not marks:
        why.append("no marker: no Marker verdict on record")
    elif marks[-1].get("verdict") != "PASS":
        why.append("marker %s: a %s verdict cannot close" % (marks[-1].get("verdict"), marks[-1].get("verdict")))
    if no_code and not (exam or {}).get("no_code"):
        why.append("empty diff: a --no-code close, and the exam is not a no_code exam")
    if (exam or {}).get("live") and not live:
        why.append("live owed: the exam declares a live clause and no attestation holds: built, not done")
    return (not why), why


def reason_class(reason):
    """'marker WEAK: ...' -> 'marker WEAK'; the label before the colon is the class a report counts by."""
    return str(reason).split(":", 1)[0]


# ---------------------------------------------------------------- the shadow call

def _git(cwd, *a):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, timeout=GIT_TIMEOUT_S, stdin=subprocess.DEVNULL)
    return r.returncode, r.stdout.strip()


def _same_work(cwd, item, full, cand):
    """-> True when the candidate `cand` (a descendant of `full`) tested this item's work exactly as it stands at
    `full`: every path that differs between them outside the bookkeeping is a path no commit naming the item touched
    (another item's landing in between). A fix of this item after `full` - or anyone's edit of this item's files -
    differs, and the candidate's record does not speak for `full` (A broken, B fixed and passed: closing at A is not
    B's pass). Git that cannot say is False."""
    rc, out = _git(cwd, "diff", "--name-only", full, cand)
    if rc:
        return False
    changed = {p for p in out.splitlines() if p and not p.startswith(BOOKKEEPING)}
    if not changed:
        return True
    rc, out = _git(cwd, "log", "--format=%x01%s", "--name-only", "-F", "--grep=" + item, "-n", str(WORK_DEPTH), cand)
    if rc:
        return False
    name = re.compile(r"(?<![A-Z0-9_])%s(?![A-Z0-9_])" % re.escape(item))
    mine, keep = set(), False
    for line in out.splitlines():
        if line.startswith("\x01"):
            keep = bool(name.search(line[1:]))
        elif line and keep and not line.startswith(BOOKKEEPING):
            mine.add(line)
    return bool(mine) and not (changed & mine)


def _record_for(sd, item, sha, cand, no_code, cwd):
    """-> the sha whose record speaks for this close, or None. The close's own sha; else the store's candidate (where
    the Marker ran) when the close is --no-code, is that sha, or is a descendant that holds the same work for this item
    (relentless closes at the work commit under a bookkeeping candidate; `_same_work`)."""
    full = sha
    if sha and not evidence._SHA.match(sha):
        rc, out = _git(cwd, "rev-parse", "--verify", "-q", sha + "^{commit}")
        full = out if rc == 0 and out else sha
    if full and evidence._SHA.match(full) and os.path.exists(evidence.record_path(sd, item, full)):
        return full
    if cand and evidence._SHA.match(cand) and os.path.exists(evidence.record_path(sd, item, cand)):
        if no_code or full == cand:
            return cand
        if full and _git(cwd, "merge-base", "--is-ancestor", full, cand)[0] == 0 and _same_work(cwd, item, full, cand):
            return cand
    return None


def judge(sd, item, sha, no_code, live=None, cwd=None, first_at=READ_INDEX):
    """-> {record, accepted, reasons} for `item` closing at `sha`, or None when the store does not hold the item (not a
    Relentless close: the predicate does not speak for it). first_at: the store's first evidence row time, when the caller
    judging many rows has read it once (default: read it here)."""
    st = _load_state(sd, item)
    if st is None:
        return None
    cand = str(_candidate(st).get("sha") or "")
    rec = _record_for(sd, item, sha, cand, no_code, cwd or HERE)
    entries, bad = [], []
    if rec:     # one snapshot: the entries judged are the very lines that were verified
        entries, bad = evidence.read_verified(sd, item, rec)
    ok, why = green(entries, exam_of(st.get("contract")), bool(no_code), live, bad)
    out = {"record": rec, "accepted": ok, "reasons": why}
    if not any(e.get("kind") == "run" for e in entries) and _pre_record(sd, st, first_at):
        out["cohort"] = PRE_RECORD      # keyed on the run, not the record: the Marker's receipt may stand alone
    return out


def _index_rows(sd):
    """-> the store's index rows, or None when it cannot be read, however that shows (a line nested too deep for json is
    RecursionError, neither OSError nor ValueError)."""
    try:
        return evidence.index_rows(sd)
    except Exception:            # noqa: BLE001 - an index that will not read is the named reading, never a traceback
        return None


def _first_at(index):
    return min((str(e.get("at") or "") for e in index or ()), default=None) or None


def _iso(t):
    try:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(float(t)))
    except (TypeError, ValueError):
        return None


def _load_state(sd, item):
    """-> the item's state, None when it is missing, unreadable or no object."""
    try:
        with open(os.path.join(sd, "items", item, "state.json"), encoding="utf-8") as f:
            st = json.load(f)
    except (OSError, ValueError, RecursionError):
        return None
    return st if isinstance(st, dict) else None


def _candidate(st):
    c = st.get("candidate")
    return c if isinstance(c, dict) else {}


def _pre_record(sd, st, first_at=READ_INDEX):
    """The candidate finished before the store held any evidence row: no writer existed to record its box run, so its
    missing run says nothing about the predicate (the shadow's first day closed items finished days earlier)."""
    first = _first_at(_index_rows(sd)) if first_at is READ_INDEX else first_at
    at = _iso(_candidate(st).get("at"))
    return bool(first and at and at < first)


def closed_by(owner, why):
    """Pure. owner: the close carries his authority. why: the close's --why. The prefix, never `RELENTLESS_WHY in why`:
    a hand close may well mention "the relentless record"."""
    if owner:
        return OWNER_CLOSE
    return RELENTLESS_CLOSE if str(why or "").startswith(RELENTLESS_WHY + ":") else SEAT_CLOSE


def ledger_closes(events):
    """events: model.read(). -> {item: [(ts, sha, closed_by)] in ledger order}, for rows older than the `closed_by` field."""
    out = {}
    for e in events:
        if e.get("event") == "close":
            owner = e.get("seat") == "OWNER" or e.get("ownerSaid") or e.get("byCard") or e.get("perRuling")
            out.setdefault(e.get("id"), []).append((str(e.get("ts") or ""), str(e.get("sha") or ""),
                                                    closed_by(owner, e.get("why"))))
    return out


def closer(row, closes=None):
    """-> who closed this row: its own field, else the first ledger close of item@sha not older than the row (the row is
    written just before the event, so a refused attempt reads the close that followed it), else UNRECORDED."""
    if row.get("closed_by"):
        return row["closed_by"]
    sha, at = str(row.get("sha") or ""), str(row.get("at") or "")[:19]
    for ts, s, who in (closes or {}).get(row.get("item")) or ():
        if sha and s and s[:7] == sha[:7] and ts[:19] >= at:
            return who
    return UNRECORDED


def shadow(item, sha, no_code, gate_found, live=None, cwd=None, sd=None, out=None, by=None):
    """cli's call, once the close is decided. Logs the predicate beside the gate's own refusals (`gate_found`,
    [(kind, why)] - the live gate's included) and returns the row, or None. `live` is an attestation the live gate has
    CHECKED, never the raw --live text. `by` is closed_by()'s word; `disagree` stays the raw gate/predicate comparison and
    the report takes an owner close out of it. NEVER raises and never refuses: any failure is one stderr line and the
    close goes on."""
    t0 = time.time()
    out = out or sys.stderr      # resolved per call, so a redirected stderr is honoured
    try:
        sd = sd or store_dir()
        j = judge(sd, item, sha, no_code, live, cwd)
        if j is None:
            return None
        gate_ok = not gate_found
        row = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "item": item, "sha": sha,
               "no_code": bool(no_code), "record": j["record"], "gate": "accept" if gate_ok else "refuse",
               "gate_reasons": sorted({str(k) for k, _ in gate_found}), "predicate": "accept" if j["accepted"] else "reject",
               "reasons": j["reasons"], "disagree": gate_ok != j["accepted"], "ms": int((time.time() - t0) * 1000)}
        if by:
            row["closed_by"] = by
        if j.get("cohort"):
            row["cohort"] = j["cohort"]
        _append_row(os.path.join(sd, SHADOW), json.dumps(row, sort_keys=True))
        if row["disagree"] and by != OWNER_CLOSE:
            print("close: %s: evidence shadow DISAGREES (gate %s, record %s: %s). Shadow only: this changes nothing."
                  % (item, row["gate"], row["predicate"], "; ".join(reason_class(r) for r in j["reasons"]) or "green"),
                  file=out)
        return row
    except Exception as ex:      # noqa: BLE001 - a shadow must never refuse or break a close
        try:
            print("close: %s: evidence shadow failed (%s: %s); the close is unaffected" % (item, type(ex).__name__, ex),
                  file=out)
        except Exception:        # noqa: BLE001
            pass
        return None


def _append_row(path, line):
    """Append one JSON line. A torn last line (a crash mid-append, no newline) is closed off first, so this row starts
    a line of its own and rows() loses only the fragment, never the next whole observation."""
    with open(path, "ab+") as f:
        f.seek(0, os.SEEK_END)
        lead = b""
        if f.tell():
            f.seek(-1, os.SEEK_END)
            if f.read(1) != b"\n":
                lead = b"\n"
        f.write(lead + line.encode("utf-8") + b"\n")


# ---------------------------------------------------------------- the report

def _is_row(r):
    """What shadow() writes and report and rescore read: an object naming an item, with the gate's and the predicate's
    words and its time. A row missing a word has no comparison to count, so it must never read as agreement."""
    return isinstance(r, dict) and bool(r.get("item")) and isinstance(r["item"], str) \
        and isinstance(r.get("sha"), (str, type(None))) and bool(r.get("at")) and isinstance(r["at"], str) \
        and r.get("gate") in ("accept", "refuse") and r.get("predicate") in ("accept", "reject") \
        and isinstance(r.get("disagree"), bool) \
        and isinstance(r.get("reasons") or [], list) and isinstance(r.get("gate_reasons") or [], list)


def read_rows(sd=None):
    """-> ([close row], how many non-blank lines of the log are no close row); a line that is not text or JSON is one of
    those. No log yet is no rows; a log that cannot be read raises OSError: a part of a log is not a smaller log."""
    out, unreadable = [], 0
    try:
        with open(os.path.join(sd or store_dir(), SHADOW), "rb") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    r = json.loads(line.decode("utf-8"))
                except (ValueError, RecursionError):
                    r = None
                if _is_row(r):
                    out.append(r)
                else:
                    unreadable += 1
    except FileNotFoundError:
        pass
    return out, unreadable


def rows(sd=None):
    return read_rows(sd)[0]


def resolve_window(spec, cwd=None):
    """--since: a WRITER_FIXES name, a commit, or an ISO time. -> {since, named}. ValueError when it names nothing: a
    window that cannot be read must never quietly become the whole log."""
    spec = str(spec or "").strip()
    if re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", spec):
        return {"since": spec, "named": spec}
    sha = WRITER_FIXES.get(spec, spec)
    if not re.fullmatch(r"[0-9a-f]{7,40}", sha):
        raise ValueError("%r is no writer fix (%s), commit or YYYY-MM-DDTHH:MM:SSZ" % (spec, ", ".join(sorted(WRITER_FIXES))))
    try:
        rc, out = _git(cwd or REPO, "log", "-1", "--format=%ct %s", sha + "^{commit}")
    except (OSError, subprocess.SubprocessError) as ex:
        raise ValueError("git could not read commit %s (%s)" % (sha, ex)) from ex
    if rc or not out:
        raise ValueError("no commit %s in this clone" % sha)
    ct, _, subject = out.partition(" ")
    return {"since": _iso(ct), "named": "%s%s: %s" % (spec + " = " if spec != sha else "", sha, subject[:100])}


def _by_class(rs):
    by = {}
    for r in rs:
        for c in sorted({reason_class(x) for x in r.get("reasons") or []}) or ["green"]:
            k = "gate %s / record %s: %s" % (r.get("gate"), r.get("predicate"), c)
            by[k] = by.get(k, 0) + 1
    return dict(sorted(by.items(), key=lambda kv: -kv[1]))


def summary(rs, window=None, closes=None):
    """Pure. -> the shadow's count, one close per (item, sha) - the last attempt stands (a refused close retried).
    window: resolve_window(...) or None (every row). closes: ledger_closes(...), for rows older than `closed_by`."""
    last = {}
    for r in rs:
        last[(r.get("item"), r.get("sha"))] = r
    since = (window or {}).get("since")
    before = [r for r in last.values() if since and str(r.get("at") or "") < since]
    closes_in = [r for r in last.values() if not since or str(r.get("at") or "") >= since]
    owner = [r for r in closes_in if closer(r, closes) == OWNER_CLOSE]
    judged = [r for r in closes_in if closer(r, closes) != OWNER_CLOSE]
    pre = [r for r in judged if r.get("disagree") and r.get("cohort") == PRE_RECORD]
    dis = [r for r in judged if r.get("disagree") and r.get("cohort") != PRE_RECORD]
    out_dis = [r for r in before if r.get("disagree") and r.get("cohort") != PRE_RECORD and closer(r, closes) != OWNER_CLOSE]
    return {"closes": len(closes_in), "attempts": len(rs), "agree": len(judged) - len(dis) - len(pre), "disagree": len(dis),
            "pre_record": len(pre), "owner": len(owner), "owner_items": sorted({r.get("item") for r in owner})[:20],
            "unrecorded": sum(closer(r, closes) == UNRECORDED for r in judged),
            "judged": len(judged) - len(pre), "window": window,
            "left_out": {"closes": len(before), "disagree": len(out_dis), "by_class": _by_class(out_dis)},
            "gate_accept_record_reject": sum(r.get("gate") == "accept" and r.get("predicate") == "reject" for r in dis),
            "gate_refuse_record_accept": sum(r.get("gate") == "refuse" and r.get("predicate") == "accept" for r in dis),
            "by_class": _by_class(dis), "sample": SAMPLE,
            "sample_met": len(judged) - len(pre) >= SAMPLE, "items": sorted({r.get("item") for r in dis})[:20]}


def report_lines(s):
    judged = s["judged"]
    out = ["evidence shadow: %d closes (%d attempts), %d agree, %d DISAGREE, %d pre-record (finished before any "
           "evidence writer; not counted as disagreements), %d owner-authority - %s"
           % (s["closes"], s["attempts"], s["agree"], s["disagree"], s["pre_record"], s["owner"],
              "sample met (%d judged >= %d)" % (judged, s["sample"]) if s["sample_met"]
              else "UNDER SAMPLE: %d of %d judged closes" % (judged, s["sample"]))]
    w, lo = s.get("window"), s["left_out"]
    if w:
        out.append("  window: closes at or after %s (%s)" % (w["since"], w["named"]))
        out.append("  left out: %d closes before the window, %d of them disagreeing: older than the fix the window names"
                   % (lo["closes"], lo["disagree"]))
        out += ["  %4d  left out: %s" % (n, k) for k, n in lo["by_class"].items()]
    else:
        out.append("  window: none declared, the whole log counts, rows older than the working writers included "
                   "(--since names one: %s, a commit, or an ISO time)" % ", ".join(sorted(WRITER_FIXES)))
    if s["owner"]:
        out.append("  owner-authority: %d closes out of the predicate's scope, neither agreement nor disagreement: %s"
                   % (s["owner"], ", ".join(s["owner_items"])))
    if s["unrecorded"]:
        out.append("  closer unrecorded: %d closes with no closed_by and no ledger close to read it from; still judged"
                   % s["unrecorded"])
    if s.get("unreadable_rows"):
        out.append("  unreadable: %d lines of the log are no close row (torn, or no object naming an item); not counted"
                   % s["unreadable_rows"])
    out += ["  %4d  %s" % (n, k) for k, n in s["by_class"].items()]
    return out


# ---------------------------------------------------------------- the rescore

WEDGE = "wedge"     # a rescore cohort: the run receipt was refused while a pre-seal writer's tail read as tampering
VERDICT_GONE = "verdict_gone"   # the snapshot's state no longer holds the Marker word (retired/redone): nothing to replay
STATE_MOVED = "state_moved"     # the snapshot's candidate is newer than the close and no evidence row predates the close:
                                # the closed candidate cannot be rebuilt from the snapshot
NOT_JUDGED = {"guard"}          # gate refusals with no record entry kind yet (module doc: breaks/holdouts not judged)


def _state(sd, item):
    return _load_state(sd, item) or {}


def _item_ids(sd):
    try:
        return sorted(os.listdir(os.path.join(sd, "items")))
    except OSError:
        return []


def _readable(fn, sd, otherwise):
    try:
        return fn(sd)
    except Exception:            # noqa: BLE001 - evidence.py on an index too odd to read (HEAD n past a row without hash)
        return otherwise


def _receipt_wedged(sd, item, sha, before=None):
    """True when the NEWEST finish receipt for item@sha (written at or before `before`, the shadow row's ISO time) says
    its box run was green but the run receipt's append was refused as tampering (boxrun.evidence_error TamperError):
    the HEAD-lag wedge, read from the receipt itself. _wedge_from reads the index tail, which a later seal repairs, so
    after the repair only the receipt still shows the refusal. A receipt sha must be a full commit id; the row's sha a
    prefix of at least 7 hex digits of it."""
    sha = str(sha or "").lower()
    if not re.fullmatch(r"[0-9a-f]{7,40}", sha):
        return False
    d = os.path.join(sd, "items", item, "receipts")
    try:
        names = os.listdir(d)
    except OSError:
        return False
    best = None
    for n in names:
        try:
            with open(os.path.join(d, n), encoding="utf-8") as f:
                rec = json.load(f)
        except (OSError, ValueError):
            continue
        if not isinstance(rec, dict):
            continue
        rs, at = str(rec.get("sha") or "").lower(), str(rec.get("at") or "")
        if not re.fullmatch(r"[0-9a-f]{40}", rs) or not rs.startswith(sha) or (before and at and at > str(before)):
            continue
        g = rec.get("gen") if isinstance(rec.get("gen"), int) else -1
        if best is None or (g, at) > best[0]:
            best = ((g, at), rec)
    if best is None:
        return False
    box = best[1].get("boxrun")
    return isinstance(box, dict) and box.get("verdict") == "green" \
        and str(box.get("evidence_error") or "").startswith("TamperError")


def _wedge_from(sd):
    """-> the `at` of the first index row past HEAD that a pre-seal writer left (unsealed), or None. From then on the
    unfixed evidence.py refused every append, so a finish after it has no record through no fault of its own."""
    h, _ = evidence._head(sd)
    if not h or not isinstance(h.get("n"), int):
        return None
    ents = [e for _, e in evidence._index(sd) if e]
    tail = [e for e in ents[h["n"]:] if not e.get("sealed")]
    return min((str(e.get("at") or "") for e in tail), default=None) or None


def rescore(snapshot, cwd=None, closes=None):
    """Replay a frozen store's shadow rows with today's writers and predicate, on a COPY (the snapshot is never written):
    every Marker verdict the store held (check.verdict on its candidate) is appended as relentless.marker_receipt now
    does at verdict time, then each row is judged again. -> (report dict, [unexplained disagreement]). A disagreement
    is explained only by a cohort the record cannot help: pre_record (finished before any evidence row) or wedge (its
    receipt was refused by the HEAD-lag bug: from the index tail, or from the finish receipt's own evidence_error). An
    owner-authority row (closer(); closes = ledger_closes(...)) is out of scope, not replayed: its own cohort, never
    verdict_gone, for no verdict ever existed."""
    import shutil
    import tempfile
    src = os.path.join(snapshot, "store")
    if not os.path.isdir(src):
        raise ValueError("%s holds no store/ dir" % snapshot)
    shadow_rows, unreadable = read_rows(src)
    wedge = _readable(_wedge_from, src, None)       # no tail to read: no row is wedge, so none is explained by it
    tmp = tempfile.mkdtemp(prefix="evidence_rescore_")
    try:
        sd = os.path.join(tmp, "store")
        shutil.copytree(src, sd)
        for root, dirs, files in os.walk(sd):          # the copy keeps the snapshot's 0444: an append needs to write
            for n in dirs + files:
                os.chmod(os.path.join(root, n), 0o755 if n in dirs else 0o644)
        markers, failed = 0, []
        for iid in _item_ids(sd):
            st = _state(sd, iid)
            chk, cand = st.get("check"), str(_candidate(st).get("sha") or "")
            if not isinstance(chk, dict) or not chk.get("verdict") or not evidence._SHA.match(cand):
                continue
            try:
                if evidence.append_marker(sd, iid, cand, chk["verdict"], defects=chk.get("defects") or [],
                                          session=chk.get("session"), reasons=chk.get("reasons") or "",
                                          nonce=chk.get("nonce") or evidence._harvest_nonce(chk)):
                    markers += 1
            except Exception as ex:      # noqa: BLE001 - one item's odd state is a named failure, never the whole reading
                failed.append("%s: %s" % (iid, str(ex)[:160]))
        before, after, unexplained, cohorts, named = {}, {}, [], {}, {}
        # Once, from the frozen source: the copy's index now opens with the markers just stamped, so a store with no
        # index would read every old candidate as pre_record. An index that holds nothing, like an unreadable one, is None
        # and explains no row: a missing file must not read as "no evidence row predates this close".
        src_index = _index_rows(src) or None
        first_at = _first_at(src_index)
        for r in shadow_rows:
            if closer(r, closes) == OWNER_CLOSE:
                cohorts[OWNER_CLOSE] = cohorts.get(OWNER_CLOSE, 0) + 1
                named.setdefault(OWNER_CLOSE, []).append("%s@%s" % (r["item"], str(r.get("sha"))[:10]))
                continue
            live = None if any(str(x).startswith("live owed") for x in r.get("reasons") or []) else "replayed"
            try:
                j = judge(sd, r["item"], r.get("sha"), r.get("no_code"), live, cwd or HERE, first_at)
            except Exception as ex:      # noqa: BLE001 - git timed out, a state too odd to read: this row, by name
                unexplained.append("%s@%s: could not be judged (%s: %s)" % (r["item"], str(r.get("sha"))[:10],
                                                                           type(ex).__name__, str(ex)[:160]))
                continue
            if j is None:
                unexplained.append("%s@%s: the snapshot does not hold the item" % (r["item"], str(r.get("sha"))[:10]))
                continue
            for c in sorted({reason_class(x) for x in r.get("reasons") or []}) or ["green"]:
                before[c] = before.get(c, 0) + 1
            for c in sorted({reason_class(x) for x in j["reasons"]}) or ["green"]:
                after[c] = after.get(c, 0) + 1
            if (r.get("gate") == "accept") == j["accepted"]:
                cohorts["agree"] = cohorts.get("agree", 0) + 1
                continue
            cohort = j.get("cohort")
            norun = any(str(x).startswith("no run") for x in j["reasons"])
            st = _state(sd, r["item"])
            if not cohort and norun and ((wedge and str(r.get("at") or "") >= wedge)
                                         or _receipt_wedged(src, r["item"], r.get("sha"), r.get("at"))):
                cohort = WEDGE
            elif not cohort and any(str(x).startswith("no marker") for x in j["reasons"]) and not (st.get("check") or {}):
                cohort = VERDICT_GONE
            elif not cohort and norun and src_index is not None \
                    and (_iso(_candidate(st).get("at")) or "") > str(r.get("at") or "") \
                    and not any(e.get("item") == r["item"] and str(e.get("at") or "") <= str(r.get("at") or "")
                                for e in src_index):
                cohort = STATE_MOVED
            elif not cohort and j["accepted"] and r.get("gate_reasons") and {str(x) for x in r["gate_reasons"]} <= NOT_JUDGED:
                cohort = "not_judged:" + ",".join(str(x) for x in r["gate_reasons"])
            if cohort:
                cohorts[cohort] = cohorts.get(cohort, 0) + 1
                named.setdefault(cohort, []).append("%s@%s" % (r["item"], str(r.get("sha"))[:10]))
            else:
                unexplained.append("%s@%s gate %s, predicate %s: %s" % (r["item"], str(r.get("sha"))[:10], r.get("gate"),
                                   "accept" if j["accepted"] else "reject", "; ".join(j["reasons"])[:240]))
        rep = {"rows": len(shadow_rows), "unreadable_rows": unreadable, "index_readable": src_index is not None,
               "rows_are": "every attempt (report counts the last per item+sha)", "markers_appended": markers, "marker_failures": failed, "wedge_from": wedge,
               "reasons_before": before, "reasons_after": after, "outcome": cohorts, "cohort_rows": named, "unexplained": len(unexplained),
               "receipts_held": sum(os.path.isdir(os.path.join(src, "items", i, "receipts"))
                                    for i in _item_ids(src)),
               "index_verifies": _readable(evidence.verify_index, sd, None) == []}
        blind = ["%d lines of the log are no close row (torn, or no object naming an item): not replayed, any may be a "
                 "disagreement" % unreadable] if unreadable else []
        if src_index is None:
            blind.append("the snapshot's index could not be read or holds nothing: it explains no row, and no reading stands")
        return rep, unexplained + ["marker receipt failed: " + x for x in failed] + blind
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- the corpus

def corpus_entries(row):
    """A corpus row -> the record entries it stands for (see the module doc: reconstructed from the store)."""
    return [{"kind": "run", "n": 0, "verdict": "green", "exit": 0, "exam_hash": row["exam_hash"]},
            {"kind": "marker", "n": 1, "verdict": row["marker"]}]


def corpus_judge(row):
    exam = {"hash": row["exam_hash"], "live": row["live_declared"], "no_code": bool(row.get("no_code_exam"))}
    return green(corpus_entries(row), exam, row["no_code"], row["live"] or None)


def check_corpus(corpus):
    """-> (problems, counts). A false close the predicate accepts, or a valid close it rejects, is a problem."""
    bad, n = [], {"false": 0, "valid": 0, "false_rejected": 0, "valid_accepted": 0}
    for r in corpus["closes"]:
        ok, why = corpus_judge(r)
        n[r["class"]] += 1
        if r["class"] == "false" and not ok:
            n["false_rejected"] += 1
        elif r["class"] == "valid" and ok:
            n["valid_accepted"] += 1
        else:
            bad.append("%s close %s@%s (%s): predicate %s %s" % (r["class"], r["item"], r["sha"][:10], r["kind"],
                                                                "accepts" if ok else "rejects", "; ".join(why)))
    return bad, n


def build_corpus(events, sd, audits):
    """events: model.read(). -> the corpus dict. One row per item: its last Relentless close."""
    last = {}
    for e in events:
        if e.get("event") == "close" and RELENTLESS_WHY in str(e.get("why", "")):
            if e["id"] not in last or str(e.get("ts")) >= str(last[e["id"]].get("ts")):
                last[e["id"]] = e
    out, seen = [], set()
    for iid, e in sorted(last.items()):
        try:
            with open(os.path.join(sd, "items", iid, "state.json"), encoding="utf-8") as f:
                st = json.load(f)
        except (OSError, ValueError):
            continue
        cand = str((st.get("candidate") or {}).get("sha") or "")
        work = "(work at" in str(e.get("reason", ""))
        if st.get("status") != "done" or not cand or not (cand.startswith(e["sha"]) or work or e.get("noCode")):
            continue            # the store's state is no longer the one this close was decided on
        word = (st.get("check") or {}).get("verdict")
        if word not in ("PASS", "WEAK"):
            continue
        ex = exam_of(st.get("contract"))
        row = {"item": iid, "sha": e["sha"], "ts": e.get("ts"), "marker": word, "no_code": bool(e.get("noCode")),
               "live_declared": ex["live"], "live": bool(e.get("live")), "exam_hash": ex["hash"][:16]}
        if ex["no_code"]:
            row["no_code_exam"] = True
        if word == "PASS" and e.get("noCode") and ex["no_code"]:
            row.update(cls="valid", kind="no_code exam close")
        elif e.get("noCode"):
            row.update(cls="false", kind="empty-diff --no-code close")
        elif word == "WEAK":
            row.update(cls="false", kind="WEAK close (store)")
        else:
            row.update(cls="valid", kind="PASS code close")
        row["class"] = row.pop("cls")
        out.append(row)
        seen.add(iid)
    for a in audits:
        if a.get("kind") == "draw" and a.get("stratum") == "narrow_weak" and a.get("verdict") == "WEAK" \
                and a["item"] not in seen:
            st = {}
            try:
                with open(os.path.join(sd, "items", a["item"], "state.json"), encoding="utf-8") as f:
                    st = json.load(f)
            except (OSError, ValueError):
                pass
            ex = exam_of(st.get("contract"))
            out.append({"item": a["item"], "sha": a["sha"], "ts": a.get("closed_at"), "marker": "WEAK", "no_code": False,
                        "live_declared": ex["live"], "live": ex["live"], "exam_hash": ex["hash"][:16],
                        "class": "false", "kind": "WEAK close (close_audits narrow_weak)"})
            seen.add(a["item"])
    return {"built": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "closes": out,
            "how": "evidence_gate.py corpus build: real Relentless closes, records reconstructed from the store (module doc)"}


def write_corpus(path, corpus):
    """Write beside the old corpus, then replace it in one rename: an interrupted rebuild leaves the old one whole."""
    tmp = "%s.tmp.%d" % (path, os.getpid())
    try:
        with open(tmp, "w", encoding="utf-8") as f:       # one close per line: a diff of a rebuild reads per close
            f.write('{"built": %s, "how": %s, "closes": [\n' % (json.dumps(corpus["built"]), json.dumps(corpus["how"])))
            f.write(",\n".join(json.dumps(r, sort_keys=True, separators=(",", ":")) for r in corpus["closes"]))
            f.write("\n]}\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _closes_for(rs):
    """The ledger's closes, read only when a row is older than `closed_by`. This repo's ledger answers for any snapshot."""
    if all(r.get("closed_by") for r in rs):
        return None
    sys.path.insert(0, os.path.dirname(HERE))
    try:
        from rimflow import model
        return ledger_closes(model.read())
    except Exception as ex:      # noqa: BLE001 - LedgerError is a bare Exception: who closed these rows is unknown
        raise ValueError("the ledger cannot say who closed the older rows (%s: %s)" % (type(ex).__name__, ex)) from ex


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--store-dir", help="the Relentless store dir (default: $RELENTLESS_ROOT/store)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("report", help="the shadow's disagreement count toward the sample")
    r.add_argument("--json", action="store_true")
    r.add_argument("--since", help="count closes at or after this: a writer fix (%s), a commit, or an ISO time"
                                   % ", ".join(sorted(WRITER_FIXES)))
    rs = sub.add_parser("rescore", help="replay a frozen store snapshot's shadow rows with today's writers + predicate")
    rs.add_argument("--snapshot", required=True, help="a dir holding store/ (evidence/, items/*/state.json, %s)" % SHADOW)
    rs.add_argument("--min-rows", type=int, default=70, help="fewer rows than this is an instrument that cannot see")
    c = sub.add_parser("corpus", help="check (default) or rebuild the false/valid close corpus")
    c.add_argument("what", nargs="?", choices=("check", "build"), default="check")
    c.add_argument("--path", default=CORPUS)
    a = ap.parse_args(argv)
    sd = a.store_dir or store_dir()
    if a.cmd == "report":
        try:
            window = resolve_window(a.since) if a.since is not None else None
        except ValueError as ex:
            print("UNMEASURED: --since: %s" % ex)
            return 2
        try:
            if not os.path.isdir(sd):
                raise ValueError("no store at %s" % sd)
            rs, unreadable = read_rows(sd)
            s = summary(rs, window, _closes_for(rs))
        except Exception as ex:  # noqa: BLE001 - whatever a store holds, this instrument says it could not read, by name
            print("UNMEASURED: report: %s: %s" % (type(ex).__name__, ex))
            return 2
        s["unreadable_rows"] = unreadable
        print(json.dumps(s, indent=1, sort_keys=True) if a.json else "\n".join(report_lines(s)))
        return 0
    if a.cmd == "rescore":
        try:
            rep, bad = rescore(a.snapshot, closes=_closes_for(rows(os.path.join(a.snapshot, "store"))))
        except Exception as ex:  # noqa: BLE001 - whatever a store holds, this instrument says it could not read, by name
            print("UNMEASURED: rescore: %s: %s" % (type(ex).__name__, ex))
            return 2
        print(json.dumps(rep, indent=1, sort_keys=True))
        for b in bad[:40]:
            print("UNEXPLAINED " + b)
        blind = rep["rows"] < a.min_rows
        print("evidence rescore: %d rows; %s" % (rep["rows"], "BLIND: under %d rows" % a.min_rows if blind else
              "%d unexplained" % len(bad) if bad else "every disagreement explained"))
        if not rep["receipts_held"]:
            print("evidence rescore: the snapshot holds no items/*/receipts: the wedge cohort cannot be read from it")
        return 1 if bad or blind or not rep["index_verifies"] else 0
    if a.what == "build":
        sys.path.insert(0, os.path.dirname(HERE))
        from rimflow import model
        audits = []
        if os.path.exists(AUDITS):
            with open(AUDITS, encoding="utf-8") as f:
                audits = [json.loads(x) for x in f if x.strip()]
        write_corpus(a.path, build_corpus(model.read(), sd, audits))
    with open(a.path, encoding="utf-8") as f:
        corpus = json.load(f)
    bad, n = check_corpus(corpus)
    for b in bad[:20]:
        print("MISS " + b)
    print("evidence corpus: %d false closes, %d rejected; %d valid closes, %d accepted - %s"
          % (n["false"], n["false_rejected"], n["valid"], n["valid_accepted"], "MISSES %d" % len(bad) if bad else "OK"))
    return 1 if bad or not n["false"] or not n["valid"] else 0


if __name__ == "__main__":
    sys.exit(main())
