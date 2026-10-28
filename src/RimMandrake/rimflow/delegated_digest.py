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
it through the allowlist Page (contracts.blind_core.Page) behind a whole-page gate that fails closed. No record text
reaches the page: titles, notes, `why` details, commit subjects and quoted words are never copied; a sha or evidence
path shows only as an opaque handle E<n>, whose map is written to <state dir>/handles/<page sha256[:16]>.json for
Operations (and the owner), never beside the page. A record whose item is about accounts is withheld and
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
import hashlib
import json
import os
import re
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


def _list_json(ddir):
    """-> sorted <ddir>/<sub>/*.json paths, or None when any directory cannot be listed. glob swallows listing errors
    (an unlistable directory reads as empty); os.scandir raises them, so a blind spot is never a measured zero."""
    out = []
    try:
        with os.scandir(ddir) as it:
            subs = sorted(e.path for e in it if e.is_dir(follow_symlinks=False))
        for d in subs:
            with os.scandir(d) as it:
                out += [e.path for e in it if e.name.endswith(".json") and e.is_file(follow_symlinks=False)]
    except OSError:
        return None
    return sorted(out)


def verdict_read(root=ROOT, ddir=DELEGATED_DIR, added=None):
    if not os.path.isdir(ddir):
        return _read("unmeasured", "absent")
    rel_dir = os.path.relpath(ddir, root)
    r = _read()
    if added is None:
        added, ok = git_added_times(root, rel_dir)
        if not ok:
            r["fault"] = "git_failed"          # times fall back to mtime; identities (paths) are unaffected
    files = _list_json(ddir)
    if files is None:                          # a directory that cannot be listed is UNMEASURED, never zero records
        return _read("unmeasured", "unreadable")
    for f in files:
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
    if set(d) == {"last_cut"}:                       # the one legacy shape: a valid ISO cut, nothing else
        if not isinstance(d["last_cut"], str) or utc(d["last_cut"]) is None:
            raise ValueError("legacy state: last_cut is not an ISO time")
        return {"schema": STATE_SCHEMA, "floor": d["last_cut"], "digests": {}}
    if d.get("schema") != STATE_SCHEMA:
        raise ValueError("state schema %r is not %s" % (str(d.get("schema"))[:40], STATE_SCHEMA))
    _check_time(d.get("floor"), "floor", True)
    if not isinstance(d.get("digests"), dict):
        raise ValueError("state digests is not an object")
    for date, e in d["digests"].items():
        _check_entry(date, e)
    return d


ENTRY_REQUIRED = ("floor", "cut", "complete", "page_sha256", "seen", "sources")
ENTRY_OPTIONAL = ("out",)                # an entry written before `out` existed is checked at today's path only
SOURCE_STATES = ("measured", "unmeasured")


def _check_entry(date, e):
    """Every field of one digest entry, completely: a damaged entry raises, never half-loads (r1 MED: an unhashable
    seen element, a missing sources map that silently disabled the rebuild-loss check)."""
    dt.date.fromisoformat(date)
    if not isinstance(e, dict):
        raise ValueError("state entry %s is not an object" % date)
    missing = [k for k in ENTRY_REQUIRED if k not in e]
    extra = [k for k in e if k not in ENTRY_REQUIRED + ENTRY_OPTIONAL]
    if missing or extra:
        raise ValueError("state entry %s: missing %s, unknown %s" % (date, missing, extra))
    if not isinstance(e["complete"], bool):
        raise ValueError("state entry %s: complete is not a bool" % date)
    _check_time(e["floor"], "floor of %s" % date, True)
    _check_time(e["cut"], "cut of %s" % date, False)
    if not (isinstance(e["page_sha256"], str) and re.fullmatch(r"[0-9a-f]{64}", e["page_sha256"])):
        raise ValueError("state entry %s: page_sha256 is not 64 hex" % date)
    if "out" in e and not (isinstance(e["out"], str) and os.path.isabs(e["out"]) and e["out"].endswith(".md")):
        raise ValueError("state entry %s: out is not an absolute .md path" % date)
    src = e["sources"]
    if not (isinstance(src, dict) and set(src) == set(SOURCES) and all(v in SOURCE_STATES for v in src.values())):
        raise ValueError("state entry %s: sources must map every source to %s" % (date, "/".join(SOURCE_STATES)))
    seen = e["seen"]
    if not isinstance(seen, dict) or any(k not in SOURCES for k in seen):
        raise ValueError("state entry %s: seen is not a map of sources" % date)
    for ids in seen.values():
        if not isinstance(ids, list) or not all(isinstance(i, str) and i for i in ids):
            raise ValueError("state entry %s: seen holds a non-string identity" % date)


def _check_time(v, what, nullable):
    if v is None and nullable:
        return
    if not isinstance(v, str) or utc(v) is None:
        raise ValueError("state %s is not an ISO time" % what)


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


def _page_ok(path, sha):
    try:
        return bool(sha) and os.path.isfile(path) and _sha256(path) == sha
    except OSError:
        return False


def reconcile(st, date, out):
    """Every pending entry whose page exists with the sha256 it recorded is complete (a run died after writing the
    page). Each entry carries its page's path (`out`); an older entry without one is checked at `out` only when it
    is `date`'s. -> True when the state changed."""
    changed = False
    for d, e in st.get("digests", {}).items():
        if e.get("complete"):
            continue
        path = e.get("out") or (out if d == date else None)
        if path and _page_ok(path, e.get("page_sha256")):
            e["complete"] = True
            changed = True
    return changed


# -------------------------------------------------------------------------------------------------- build -----
def build(date, floor, cut, reads, seen_other=frozenset(), ids=None, resolve=None):
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
    page = BL.project_digest(date, floor, cut, raw, status, ids, resolve)
    return BL.render_digest(page), seen


def _load_ledger():
    """-> (events, blind.Identity); (None, None) when the ledger or its identity does not read: the ledger source
    is then UNMEASURED and every identity-bearing record is withheld (fail closed, never 'nothing hidden')."""
    try:
        from rimflow import model
        events = model.read()
        world = model.replay(events)
        import blind_view as BV
        from contracts import blind as BL
        return events, BL.Identity(frozenset(BV.known_ids(world)), frozenset(BV.hidden_ids(world)))
    except Exception:  # noqa: BLE001
        return None, None


def _dest(a):
    """-> the page directory for this run, shared by the success and the failure path: a dry run never resolves to
    the production directory."""
    dry = bool(getattr(a, "dry_run", False))
    out_dir = getattr(a, "out_dir", None) or (DRY_DIR if dry else OUT_DIR)
    if dry and os.path.realpath(out_dir) == os.path.realpath(OUT_DIR):
        return DRY_DIR, True
    return out_dir, False


def handles_dir(a, out_dir):
    """Where a digest's handle map goes: <state dir>/handles (Operations' scratch, beside errors.log); a dry run's
    under its own out dir (never the production scratch)."""
    if getattr(a, "dry_run", False):
        return os.path.join(out_dir, "handles")
    return os.path.join(os.path.dirname(os.path.abspath(a.state)), "handles")


def run(a, sources=None):
    """sources: the selftest's injected (reads, Identity, resolver); else every source is read here."""
    date = a.date or dt.date.today().isoformat()
    dt.date.fromisoformat(date)
    out_dir, refused = _dest(a)
    out = os.path.join(out_dir, "delegated_digest_%s.md" % date)
    if a.since and not a.dry_run:
        raise ValueError("--since moves the window by hand: only a --dry-run may take it")
    if refused:
        raise ValueError("a dry run never writes the production digest directory")
    for p in (SRC, HERE):
        if p not in sys.path:
            sys.path.insert(0, p)
    st = load_state(a.state)
    if not a.dry_run and reconcile(st, date, out):
        save_state(a.state, st)
    entry = st["digests"].get(date)
    if entry and entry.get("complete") and not a.force and not a.dry_run:
        failed = os.path.join(out_dir, "delegated_digest_%s.FAILED.md" % date)
        if _page_ok(entry.get("out") or out, entry.get("page_sha256")):
            if os.path.exists(failed):
                os.remove(failed)
            print("delegated_digest: the %s digest is complete; one digest per day, nothing done" % date)
            return 0
        print("delegated_digest: the %s digest is recorded complete but its page is missing or changed; "
              "rebuilding it" % date)
    rebuild = bool(entry) and (a.force or entry.get("complete"))
    if a.since:
        floor = utc(a.since)
        if floor is None:
            raise ValueError("--since is not an ISO time")
    elif rebuild:
        floor = utc(entry.get("floor")) if entry.get("floor") else None
    else:
        floor = utc(st.get("floor")) if st.get("floor") else None
    cut = utc(a.cut) if a.cut else dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    if cut is None:
        raise ValueError("--cut is not an ISO time")
    if sources is None:
        events, ids = _load_ledger()
        reads = gather(events)
        from contracts import blind_core as C
        resolve = C.git_resolver(ROOT)
    elif len(sources) == 2:                          # (reads, Identity): no resolver, so every sha is withheld
        (reads, ids), resolve = sources, None
    else:
        reads, ids, resolve = sources
    states = {s: reads[s]["state"] if s in reads else "unmeasured" for s in SOURCES}
    if rebuild and not a.dry_run:
        lost = [s for s, was in (entry.get("sources") or {}).items()
                if was == "measured" and states.get(s) != "measured"]
        if lost:
            raise RuntimeError("refusing to rebuild the %s digest: %s read before and is UNMEASURED now, so its "
                               "records would leave the page and its identities the state" % (date, ", ".join(lost)))
    text, seen = build(date, floor, cut, reads, seen_elsewhere(st, date), ids, resolve)
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if not a.dry_run:
        st["digests"][date] = {"floor": iso(floor) if floor else None, "cut": iso(cut), "complete": False,
                               "page_sha256": sha, "seen": seen, "out": os.path.abspath(out),
                               "sources": {s: reads[s]["state"] if s in reads else "unmeasured" for s in SOURCES}}
        save_state(a.state, st)                      # 1. pending, with the page's hash
    os.makedirs(out_dir, exist_ok=True)
    from contracts import blind_core as C
    # the page shows each sha and evidence path only as a handle E<n>; the map goes where Operations reads it (the
    # state's directory, never the page's), keyed by the page's sha256, BEFORE the page exists
    C.store_handles(text, getattr(text, "handles", {}), handles_dir(a, out_dir))
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
    try:
        out_dir = _dest(a)[0]
    except Exception:  # noqa: BLE001
        out_dir = DRY_DIR
    errors = _errors_path(a, out_dir)
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


def _errors_path(a, out_dir):
    """--errors, unless it could land where a blind role reads (a .md file, the page directory, the production or
    the dry-run digest directory): then Operations' fixed log. Never raises."""
    try:
        e = getattr(a, "errors", None)
        if not e:
            return ERRORS
        real = os.path.realpath(e)
        if real.lower().endswith((".md", ".markdown", ".html", ".txt")):
            return ERRORS
        for d in (out_dir, OUT_DIR, DRY_DIR):
            r = os.path.realpath(d)
            if real == r or real.startswith(r.rstrip(os.sep) + os.sep):
                return ERRORS
        return e
    except Exception:  # noqa: BLE001
        return ERRORS


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
