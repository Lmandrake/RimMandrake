#!/usr/bin/env python3
"""delegated_digest.py — the daily digest of delegated calls, built by a program (delegation_policy.md §5).

No AI. Once a day, as the Conductor's pre-step (dispatcher_schedule.json `pre_launch`), this writes
`Transient/delegated_digest_<YYYY-MM-DD>.md`: every delegated call not yet in a digest, grouped by class, newest
first, with counts MEASURED from the records. The Conductor delivers it (conductor.md, scheduled check (d)); it never
assembles one by hand. Items DELEGATED_DIGEST_FIX_NEVER_WRITTEN, DIGEST_BLIND_HARDEN_REASONS_SLIP_THROUGH.

🔴 TOKEN-BLIND BY CONSTRUCTION (owner 2026-10-27: only Operations is token-aware; the Conductor reads this page).
The page is a contracts.blind.DigestPage, a CLOSED type: each reader below extracts only the RAW_FIELDS of its
source, contracts.blind.project_digest maps them into closed sets (policy class, decision, mark action, judge family,
seat) and checked identifiers (item id, subject, sha, evidence path under an allowed root), and render_digest writes
it from fixed templates behind a page guard that fails closed. No record text reaches the page: titles, notes, `why`
details, commit subjects and quoted words are never copied. A record whose item is about accounts is withheld and
counted; an unsafe subject or path is dropped and counted (BLINDVIEW_BUILD_CLOSED_TYPE_LEAKPROOF).

Sources (each read whole; the window is decided centrally, below):
  ledger       events whose `why` starts `delegated:` (rimflow model.read(), all shards); identity seat+ts+tsn+verb+id.
  verdict      infrastructure/state/delegated/<date>/*.json; t = the commit that added it (git) or its mtime while
               untracked; identity = the repo path, so a verdict seen untracked is not shown again once committed.
  commit       every `Delegated: <class> …` line of a commit message, subject or BODY (`git log --format=%B`);
               identity = sha + line number. A git failure reads UNMEASURED.
  marks        the art ledger's mark acts (live events under MARKS_WHY incl. ✕ deletes, ban, unban, ban_hit), read as
               records with an upper bound like every source (never marks_digest's prose); identity = event id.
  art_install  the art ledger's other `delegated:` live installs; identity = event id (else ts+sha+rel).
  leftovers    D:\\ClaudeWork\\backups\\leftovers\\acts.jsonl; identity = the line's sha1.

The window (review gpt_review_digest_2026-10-27 findings 2, 4-8): state at
D:\\ClaudeWork\\rimmandrake\\delegated_digest\\state.json (scratch, never the repo) holds, per digest date, its
floor, cut, completion and the identities each source contributed. A record is on today's page iff its identity is in
no OTHER complete digest and floor < t <= cut. A source that fails reads UNMEASURED and its records stay unseen, so
they appear on the next digest that can read it: a failed source never loses its backlog. A malformed record (bad
JSON, no readable time) is counted per source, never silently skipped. The floor is the state's global floor (a legacy
`last_cut`, else none) and never advances; --force rebuilds a date with that date's own floor, its own records
re-included. Completion is the state entry, never the file's existence: the entry is written pending (with the page's
sha256), then the page, then the entry is marked complete; a pending entry whose page matches its sha256 is
reconciled to complete on the next run. --dry-run writes elsewhere (never the production directory) and never moves
the state; only a dry run may take --since.

--pre-launch: a pre-step's non-zero exit stops the Conductor (role_launch.launch_argv), and a missing digest must not
cost the owner his Conductor: in this mode ANY failure (bad arguments, an import, the page guard) writes the fixed
text `delegated_digest_<date>.FAILED.md` beside the digest and exits 0. The error itself (which may hold record text)
goes only to D:\\ClaudeWork\\rimmandrake\\delegated_digest\\errors.log, which Operations reads. A successful run
removes that date's stale FAILED marker. The failure path uses the stdlib only.

Usage:
  python3 src/RimMandrake/rimflow/delegated_digest.py                  # build today's, record it in the state
  python3 src/RimMandrake/rimflow/delegated_digest.py --dry-run [--since 2026-10-26T00:00:00Z] [--out-dir DIR]
  python3 src/RimMandrake/rimflow/delegated_digest.py --force          # rebuild today's with its own floor
"""
import argparse
import datetime as dt
import glob
import hashlib
import json
import os
import subprocess
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(SRC))

DELEGATED_DIR = os.path.join(ROOT, "infrastructure", "state", "delegated")
OUT_DIR = os.path.join(ROOT, "Transient")
SCRATCH = "/mnt/d/ClaudeWork/rimmandrake/delegated_digest"
STATE = os.path.join(SCRATCH, "state.json")
DRY_DIR = os.path.join(SCRATCH, "dry")
ERRORS = os.path.join(SCRATCH, "errors.log")
LEFTOVERS = "/mnt/d/ClaudeWork/backups/leftovers/acts.jsonl"
STATE_SCHEMA = "rimflow.delegated-digest-state/2"
SKIP_VERBS = {"lease", "renew", "release"}    # lease bookkeeping a claim already shows
SOURCES = ("ledger", "verdict", "commit", "marks", "art_install", "leftovers")
FAILED_TEXT = ("# Delegated digest %s NOT BUILT\n\nThe program failed; the error is in Operations' log. The Conductor "
               "started anyway. The next digest carries every record this one would have.\n")


def utc(ts):
    """ISO text -> aware UTC datetime; a naive time is local (leftovers' acts.jsonl). None if unreadable."""
    if not ts or not isinstance(ts, str):
        return None
    try:
        d = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None
    if d.tzinfo is None:
        d = d.astimezone()
    return d.astimezone(dt.timezone.utc)


def iso(d):
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


def _h(*parts):
    return hashlib.sha1("\x1f".join(str(p) for p in parts).encode("utf-8")).hexdigest()


def _read(state="measured", fault="none"):
    """A source read: every record of all time as (identity, t, raw), plus its malformed count."""
    return {"state": state, "fault": fault, "malformed": 0, "items": []}


# ------------------------------------------------------------------------------------------------ sources -----
def ledger_read(events):
    """events: rimflow model.read()'s list, or None when the ledger could not be read (UNMEASURED)."""
    if events is None:
        return _read("unmeasured", "unreadable")
    r = _read()
    for ev in events:
        if not isinstance(ev, dict):
            r["malformed"] += 1
            continue
        why = ev.get("why")
        if not isinstance(why, str) or not why.startswith("delegated:") or ev.get("event") in SKIP_VERBS:
            continue
        t = utc(ev.get("ts"))
        if t is None:
            r["malformed"] += 1
            continue
        ident = "L" + _h(ev.get("seat"), ev.get("ts"), ev.get("tsn"), ev.get("event"), ev.get("id"))
        r["items"].append((ident, t, {"source": "ledger", "t": t, "why": why, "id": ev.get("id"),
                                      "event": ev.get("event"), "seat": ev.get("seat"), "ranBy": ev.get("ranBy"),
                                      "sha": ev.get("sha")}))
    return r


def git_added_times(root, rel_dir):
    """-> ({repo-relative path: aware UTC datetime of the commit that added it}, ok). One git call."""
    try:
        p = subprocess.run(["git", "-C", root, "log", "--diff-filter=A", "--name-only", "--format=@%cI", "--",
                            rel_dir], capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return {}, False
    if p.returncode != 0:
        return {}, False
    out, cur = {}, None
    for line in p.stdout.splitlines():
        if line.startswith("@"):
            cur = utc(line[1:])
        elif line.strip() and cur is not None:
            out.setdefault(line.strip(), cur)     # newest first: an add after a delete keeps the newest add
    return out, True


def _decided(rec):
    for k in ("decision", "verdict", "overall", "final", "recommended_pick"):
        v = rec.get(k)
        if isinstance(v, str) and v.strip():
            return v
        if isinstance(v, dict):
            for kk in ("decision", "verdict", "pick"):
                if isinstance(v.get(kk), str):
                    return v[kk]
    return None


def verdict_read(root=ROOT, ddir=DELEGATED_DIR, added=None):
    if not os.path.isdir(ddir):
        return _read("unmeasured", "absent")
    rel_dir = os.path.relpath(ddir, root)
    r = _read()
    if added is None:
        added, ok = git_added_times(root, rel_dir)
        if not ok:
            r["fault"] = "git_failed"          # times fall back to mtime; identities (paths) are unaffected
    for f in sorted(glob.glob(os.path.join(ddir, "*", "*.json"))):
        rel = os.path.relpath(f, root).replace(os.sep, "/")
        t = added.get(rel)
        try:
            if t is None:
                t = dt.datetime.fromtimestamp(os.path.getmtime(f), dt.timezone.utc).replace(microsecond=0)
            with open(f, encoding="utf-8") as fh:
                raw = json.load(fh)
        except (OSError, ValueError):
            r["malformed"] += 1
            continue
        if not isinstance(raw, dict):
            r["malformed"] += 1
            continue
        jm = raw.get("judge_model")
        r["items"].append(("V" + rel, t, {
            "source": "verdict", "t": t, "rel": rel, "item": raw.get("item"),
            "subject": raw.get("subject") if isinstance(raw.get("subject"), str) else os.path.basename(f)[:-5],
            "class": raw.get("class") if isinstance(raw.get("class"), str) else None, "decision": _decided(raw),
            "judge_keys": list(jm) if isinstance(jm, dict) else [], "art": "image_sha256" in raw}))
    return r


def commit_read(root=ROOT, commits=None):
    """commits: [(sha, iso time, full message)] for the selftest, else git (whose failure reads UNMEASURED)."""
    if commits is None:
        try:
            p = subprocess.run(["git", "-C", root, "log", "--grep=^Delegated:", "--format=%H%x1f%cI%x1f%B%x1e"],
                               capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.SubprocessError):
            return _read("unmeasured", "git_failed")
        if p.returncode != 0:
            return _read("unmeasured", "git_failed")
        commits = []
        for chunk in p.stdout.split("\x1e"):
            parts = chunk.strip("\n").split("\x1f")
            if len(parts) == 3:
                commits.append(tuple(parts))
            elif chunk.strip():
                commits.append(("", "", ""))           # counted malformed below
    r = _read()
    for sha, ts, body in commits:
        t = utc(ts)
        if t is None or not sha:
            r["malformed"] += 1
            continue
        lines = [l for l in str(body).splitlines() if l.startswith("Delegated:")]
        for n, line in enumerate(lines):
            r["items"].append(("C%s:%d" % (sha, n), t, {"source": "commit", "t": t, "sha": sha,
                                                         "class": line[len("Delegated:"):].strip()}))
    return r


def _artledger():
    p = os.path.join(SRC, "Utils", "art")
    if p not in sys.path:
        sys.path.insert(0, p)
    import artledger  # noqa: E402
    return artledger


def art_reads(events=None, marks_why="delegated: art marks"):
    """-> (marks read, art_install read) from the art ledger's events (one load for both)."""
    if events is None:
        try:
            L = _artledger()
        except Exception:  # noqa: BLE001 — a broken source is reported, never fatal
            return _read("unmeasured", "import_failed"), _read("unmeasured", "import_failed")
        try:
            events, marks_why = L.cached_index().events, L.MARKS_WHY
        except Exception:  # noqa: BLE001
            return _read("unmeasured", "unreadable"), _read("unmeasured", "unreadable")
    marks, inst = _read(), _read()
    for e in events:
        if not isinstance(e, dict):
            marks["malformed"] += 1
            continue
        typ, why = e.get("type"), str(e.get("why") or "")
        is_mark = typ in ("ban", "unban", "ban_hit") or (typ == "live" and (
            why.startswith(marks_why) or e.get("reason") == "x-delete"))
        is_inst = not is_mark and typ == "live" and why.startswith("delegated:")
        if not (is_mark or is_inst):
            continue
        tgt = marks if is_mark else inst
        t = utc(e.get("ts"))
        if t is None:
            tgt["malformed"] += 1
            continue
        ident = "A" + (str(e["id"]) if e.get("id") else _h(e.get("ts"), e.get("sha"), e.get("rel"), typ))
        if is_mark:
            tgt["items"].append((ident, t, {"source": "marks", "t": t, "type": typ, "reason": e.get("reason"),
                                            "id": e.get("id"), "sha": e.get("sha"), "prev": e.get("prev"),
                                            "rel": e.get("rel")}))
        else:
            tgt["items"].append((ident, t, {"source": "art_install", "t": t, "why": why, "seat": e.get("seat"),
                                            "sha": e.get("sha"), "rel": e.get("rel")}))
    return marks, inst


def leftovers_read(path=LEFTOVERS):
    if not os.path.exists(path):
        return _read("unmeasured", "absent")
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return _read("unmeasured", "unreadable")
    r = _read()
    for line in lines:
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except ValueError:
            raw = None
        t = utc(raw.get("ts")) if isinstance(raw, dict) else None
        if t is None:
            r["malformed"] += 1
            continue
        r["items"].append(("F" + _h(line.strip()), t, {"source": "leftovers", "t": t, "kind": raw.get("kind"),
                                                       "archive": raw.get("archive")}))
    return r


def gather(events, root=ROOT, ddir=DELEGATED_DIR, leftovers=LEFTOVERS, added=None, commits=None, art_events=None):
    """Every source read; each injectable for the selftest. events None = the ledger did not read."""
    marks, inst = art_reads(art_events)
    return {"ledger": ledger_read(events), "verdict": verdict_read(root, ddir, added),
            "commit": commit_read(root, commits), "marks": marks, "art_install": inst,
            "leftovers": leftovers_read(leftovers)}


# -------------------------------------------------------------------------------------------------- state -----
def load_state(path):
    """-> the v2 state dict. A legacy {last_cut} becomes the global floor. An unreadable file raises: it is never
    treated as 'no digest yet', which would re-send all time."""
    if not os.path.exists(path):
        return {"schema": STATE_SCHEMA, "floor": None, "digests": {}}
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    if not isinstance(d, dict):
        raise ValueError("state is not an object")
    if d.get("schema") == STATE_SCHEMA:
        return d
    return {"schema": STATE_SCHEMA, "floor": d.get("last_cut"), "digests": {}}


def save_state(path, st):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(st, fh, sort_keys=True)
    os.replace(tmp, path)


def seen_elsewhere(st, date):
    """Identities in every COMPLETE digest other than `date`."""
    out = set()
    for d, e in st.get("digests", {}).items():
        if d != date and e.get("complete"):
            for ids in (e.get("seen") or {}).values():
                out.update(ids)
    return out


def _sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def reconcile(st, date, out):
    """A pending entry whose page exists with the sha256 it recorded is complete (the run died after writing the
    page). -> True when the state changed."""
    e = st.get("digests", {}).get(date)
    if e and not e.get("complete") and e.get("page_sha256") and os.path.exists(out) and \
            _sha256(out) == e["page_sha256"]:
        e["complete"] = True
        return True
    return False


# -------------------------------------------------------------------------------------------------- build -----
def build(date, floor, cut, reads, seen_other=frozenset(), hidden=frozenset()):
    """-> (page text, {source: [identities on the page]})."""
    from contracts import blind as BL
    raw, seen, status = [], {}, {}
    for s in SOURCES:
        r = reads.get(s) or _read("unmeasured", "error")
        status[s] = {"state": r["state"], "fault": r["fault"], "malformed": r["malformed"]}
        if r["state"] == "measured":
            status[s]["all_time"] = len(r["items"])
            if r["items"]:
                status[s]["newest"] = max(t for _i, t, _r in r["items"])
        seen[s] = []
        for ident, t, rec in r["items"]:
            if ident in seen_other or t > cut or (floor is not None and t <= floor):
                continue
            seen[s].append(ident)
            raw.append(rec)
    page = BL.project_digest(date, floor, cut, raw, status, hidden)
    return BL.render_digest(page), seen


def _load_ledger():
    """-> (events, hidden ids); (None, ()) when the ledger does not read (the ledger source is then UNMEASURED)."""
    try:
        from rimflow import model
        events = model.read()
        world = model.replay(events)
        import blind_view as BV
        return events, frozenset(BV.hidden_ids(world))
    except Exception:  # noqa: BLE001
        return None, frozenset()


def run(a, sources=None):
    """sources: the selftest's injected (reads, hidden); else every source is read here."""
    date = a.date or dt.date.today().isoformat()
    dt.date.fromisoformat(date)
    out_dir = a.out_dir or (DRY_DIR if a.dry_run else OUT_DIR)
    out = os.path.join(out_dir, "delegated_digest_%s.md" % date)
    if a.since and not a.dry_run:
        raise ValueError("--since moves the window by hand: only a --dry-run may take it")
    if a.dry_run and os.path.realpath(out_dir) == os.path.realpath(OUT_DIR):
        raise ValueError("a dry run never writes the production digest directory")
    for p in (SRC, HERE):
        if p not in sys.path:
            sys.path.insert(0, p)
    st = load_state(a.state)
    if not a.dry_run and reconcile(st, date, out):
        save_state(a.state, st)
    entry = st["digests"].get(date)
    if entry and entry.get("complete") and not a.force and not a.dry_run:
        print("delegated_digest: the %s digest is complete; one digest per day, nothing done" % date)
        return 0
    if a.since:
        floor = utc(a.since)
        if floor is None:
            raise ValueError("--since is not an ISO time")
    elif entry and a.force:
        floor = utc(entry.get("floor")) if entry.get("floor") else None
    else:
        floor = utc(st.get("floor")) if st.get("floor") else None
    cut = utc(a.cut) if a.cut else dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    if cut is None:
        raise ValueError("--cut is not an ISO time")
    if sources is None:
        events, hidden = _load_ledger()
        reads = gather(events)
    else:
        reads, hidden = sources
    text, seen = build(date, floor, cut, reads, seen_elsewhere(st, date), hidden)
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if not a.dry_run:
        st["digests"][date] = {"floor": iso(floor) if floor else None, "cut": iso(cut), "complete": False,
                               "page_sha256": sha, "seen": seen,
                               "sources": {s: reads[s]["state"] if s in reads else "unmeasured" for s in SOURCES}}
        save_state(a.state, st)                      # 1. pending, with the page's hash
    os.makedirs(out_dir, exist_ok=True)
    tmp = out + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    os.replace(tmp, out)                             # 2. the page
    if not a.dry_run:
        st["digests"][date]["complete"] = True
        save_state(a.state, st)                      # 3. complete
        failed = os.path.join(out_dir, "delegated_digest_%s.FAILED.md" % date)
        if os.path.exists(failed):
            os.remove(failed)
    n = sum(len(v) for v in seen.values())
    print("delegated_digest: wrote %s (%d record(s))%s" % (out, n, "; DRY RUN, state untouched" if a.dry_run else ""))
    return 0


def parser():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date", help="digest date YYYY-MM-DD (default: today, local)")
    ap.add_argument("--since", help="dry run only: an ISO floor instead of the state's")
    ap.add_argument("--cut", help=argparse.SUPPRESS)          # selftest: a fixed upper bound
    ap.add_argument("--out-dir", help="default Transient/ (a dry run: %s)" % DRY_DIR)
    ap.add_argument("--state", default=STATE)
    ap.add_argument("--errors", default=ERRORS, help=argparse.SUPPRESS)
    ap.add_argument("--dry-run", action="store_true", help="write the page elsewhere, never touch the state")
    ap.add_argument("--force", action="store_true", help="rebuild the date's digest with its own floor")
    ap.add_argument("--pre-launch", action="store_true", help="never exit non-zero (the Conductor's pre-step)")
    return ap


def _fail(a):
    """The failure path: stdlib only, fixed text on the page side, the error to Operations' log. Never raises."""
    date = getattr(a, "date", None) or dt.date.today().isoformat()
    try:
        dt.date.fromisoformat(date)
    except (TypeError, ValueError):
        date = dt.date.today().isoformat()
    out_dir = getattr(a, "out_dir", None) or OUT_DIR
    errors = getattr(a, "errors", None) or ERRORS
    try:
        os.makedirs(os.path.dirname(errors), exist_ok=True)
        with open(errors, "a", encoding="utf-8") as fh:
            fh.write("%s %s\n%s\n" % (iso(dt.datetime.now(dt.timezone.utc)), date, traceback.format_exc()))
    except Exception:  # noqa: BLE001
        pass
    try:
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "delegated_digest_%s.FAILED.md" % date), "w", encoding="utf-8") as fh:
            fh.write(FAILED_TEXT % date)
    except Exception:  # noqa: BLE001
        pass
    try:
        print("delegated_digest: FAILED; the Conductor starts anyway (the error is in Operations' log)",
              file=sys.stderr)
    except Exception:  # noqa: BLE001
        pass
    return 0


def _partial(argv):
    """The paths a bad command line still names (--date, --out-dir, --errors), so a refused argument fails on the
    page the caller asked for, never on the production page of a test. Never raises."""
    try:
        with open(os.devnull, "w") as null:
            err, sys.stderr = sys.stderr, null
            try:
                return parser().parse_known_args(argv)[0]
            finally:
                sys.stderr = err
    except BaseException:  # noqa: BLE001
        return None


def main(argv=None, sources=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    pre = "--pre-launch" in argv
    a = None
    try:
        a = parser().parse_args(argv)
        return run(a, sources)
    except SystemExit as e:
        if pre and e.code not in (0, None):
            return _fail(a if a is not None else _partial(argv))
        raise
    except Exception:  # noqa: BLE001
        if not pre:
            raise
        return _fail(a)


if __name__ == "__main__":
    sys.exit(main())
