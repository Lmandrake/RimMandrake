#!/usr/bin/env python3
"""modledger.py — one append-only ledger per mod; every other per-mod record is a view printed from it.

Spec: design/specs/2026-11-15-holder-pipeline-fusion.md §3.1-3.3 (his card answers at its top); plan:
design/plans/2026-11-15-holder-pipeline-fusion-build.md step 2; item RIMMANDRAKE_BUILD_MOD_LEDGER_HOLDERS_THREE_PILOTS_AT_ONCE.

Layout. `design/concepts/<Mod>/ledger/<WRITER>.jsonl`, one shard per producer: `DISPATCH`, `OWNER`, `STEWARD`,
`BACKFILL`, `HOLDER.<lease>` (each holder lease its own shard), `JUDGE.<run>` (each blind run its own shard, sealed by
the dispatcher when it ends). Views (generated, never edited) in `ledger/views/`; a text too long for one atomic line
lives whole in `ledger/text/<sha>.txt` and the event points at it.

Not a second ledger engine: the write is rimflow's (`model._dir_lock` + `model._append_locked`: flock, O_APPEND, the
PIPE_BUF bound), the merged read is `model.canonical_order`, and the per-shard append-only lint is
`ledger_lint.lint_blob` (MALFORMED, NO_NEWLINE, NOT_APPEND, DUP_DIFFERENT). What is new is per-mod: who may write which
kind, the holder's fencing token, sealed judge shards, the reducer, the packet and the views.

Every number comes from `modledger.json` (the 400k holder ceiling, the 15k packet budget, the lease idle minutes).

    modledger.py append --mod M --writer W --kind K --subject S [--text T] [--fix F] [--token N] [--run R] ...
    modledger.py grant  --mod M --lease L            DISPATCH: a new holder lease, the next fencing token
    modledger.py seal   --mod M --run R              DISPATCH: seal JUDGE.R (its hash recorded)
    modledger.py show   --mod M [SUBJECT]            events, one line each
    modledger.py state  --mod M                      the reduced state, JSON
    modledger.py packet --mod M [--budget N] [--strict]
    modledger.py views  --mod M                      regenerate the views (append does it by itself)
    modledger.py lint   [--mod M] [--base origin/main]   exit 0 clean, 1 findings, 2 could not run

Root: `--root`, else $RM_MODLEDGER_ROOT, else this repo. A process started as one writer sets
$RM_MODLEDGER_WRITER (the launcher does), and append refuses any other shard: a holder cannot write a judge's finding
or his answer. That is tamper-evidence plus the lint, not prevention: a shell can still write a file by hand, and the
lint is what catches it (spec §3.1, GPT objection 10).
"""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(os.path.dirname(HERE), "Utils"))
import model                                                     # noqa: E402  rimflow's shard writer and reader
import ledger_lint                                               # noqa: E402  the append-only shard lint

REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CONFIG_PATH = os.path.join(HERE, "modledger.json")
REDUCER_VERSION = 1
VIEWS = ("state.md", "history.md", "state.json")
WRITER_RE = re.compile(r"^(DISPATCH|OWNER|STEWARD|BACKFILL|(HOLDER|JUDGE)\.[A-Za-z0-9_-]{1,64})$")
MOD_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")
REQUIRED = ("id", "key", "ts", "mod", "version", "writer", "kind", "subject", "body")
AUTH_KEYS = ("owner_said", "by_card", "per_ruling", "why")
OWNER_AUTH = ("owner_said", "by_card", "per_ruling")
SPILL_HEAD = 300            # chars of a spilled body field kept on the line, before the pointer
_UNSET = object()


class ModLedgerError(Exception):
    """A refused append or an unusable ledger. The message says why and what would pass."""


_CFG = {}


def config(path=CONFIG_PATH):
    if path not in _CFG:
        with open(path, encoding="utf-8") as fh:
            _CFG[path] = json.load(fh)
    return _CFG[path]


def default_root():
    return os.environ.get("RM_MODLEDGER_ROOT") or REPO_ROOT


def _check_mod(mod):
    if not isinstance(mod, str) or not MOD_RE.match(mod):
        raise ModLedgerError("mod %r is not a concept folder name (letters, digits, _)" % (mod,))


def _check_writer(writer):
    if not isinstance(writer, str) or not WRITER_RE.match(writer):
        raise ModLedgerError("writer %r is not one of DISPATCH, OWNER, STEWARD, BACKFILL, HOLDER.<lease>, "
                             "JUDGE.<run>" % (writer,))


def ledger_dir(root, mod):
    _check_mod(mod)
    return os.path.join(root, "design", "concepts", mod, "ledger")


def views_dir(root, mod):
    return os.path.join(ledger_dir(root, mod), "views")


def shard_path(root, mod, writer):
    _check_writer(writer)
    return os.path.join(ledger_dir(root, mod), writer + ".jsonl")


def writer_class(writer):
    return writer.split(".", 1)[0]


def writer_suffix(writer):
    return writer.split(".", 1)[1] if "." in writer else None


def kind_allowed(writer, kind):
    kinds = config()["writers"].get(writer_class(writer), [])
    return "*" in kinds or kind in kinds


def tokens(text):
    """The spec's estimate: tokens = bytes / 4, rounded up."""
    return (len(text.encode("utf-8")) + 3) // 4


def _canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def derive_key(ev):
    fields = {k: ev.get(k) for k in ("kind", "subject", "version", "body", "evidence", "supersedes", "code_sha",
                                     "run", "token", "authority")}
    return hashlib.sha256(_canon(fields).encode("utf-8")).hexdigest()[:16]


def derive_id(writer, key):
    return "%s:%s" % (writer, hashlib.sha256(("%s\0%s" % (writer, key)).encode("utf-8")).hexdigest()[:16])


def _when(ev):
    """Order key inside the ledger: (ts, tsn), as rimflow orders its own events."""
    tsn = ev.get("tsn")
    return (str(ev.get("ts") or ""), tsn if isinstance(tsn, int) and not isinstance(tsn, bool) else 0)


def _parse_ts(ts):
    return datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")


# ---- read -----------------------------------------------------------------------------------------------------------

def shard_names(root, mod):
    d = ledger_dir(root, mod)
    try:
        return sorted(n[:-len(".jsonl")] for n in os.listdir(d) if n.endswith(".jsonl"))
    except OSError:
        return []


def read(root, mod):
    """-> every event of the mod, merged across shards in canonical order (rimflow's), each carrying `_shard` and
    `_seq` (its line number in its shard: shards only grow, so the number never moves). Unparsable lines are skipped
    here; the lint reports them."""
    where = {}
    raw_events = []
    for shard in shard_names(root, mod):
        path = os.path.join(ledger_dir(root, mod), shard + ".jsonl")
        for seq, line in enumerate(model._read_lines(path), 1):
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            if not isinstance(ev, dict):
                continue
            k = model.event_key(ev)
            if k not in where:
                where[k] = (shard, seq)
                raw_events.append(ev)
    out = []
    for ev in model.canonical_order(raw_events):
        shard, seq = where[model.event_key(ev)]
        out.append(dict(ev, _shard=shard, _seq=seq))
    return out


def _clean(ev):
    return {k: v for k, v in ev.items() if not k.startswith("_")}


# ---- leases and seals -----------------------------------------------------------------------------------------------

def leases(events):
    """-> {lease: {token, granted, last, released}} plus the current (highest-token) lease, from DISPATCH grants and
    the holder's own activity."""
    by = {}
    current = None
    for ev in events:
        if ev.get("writer") == "DISPATCH" and ev.get("kind") == "lease.grant":
            b = ev.get("body") or {}
            lease, tok = b.get("lease"), b.get("token")
            if isinstance(lease, str) and isinstance(tok, int):
                by[lease] = {"lease": lease, "token": tok, "granted": _when(ev), "last": ev.get("ts"),
                             "released": False}
                if current is None or tok > by[current]["token"]:
                    current = lease
        elif ev.get("writer") == "DISPATCH" and ev.get("kind") == "lease.revoke":
            lease = (ev.get("body") or {}).get("lease")
            if lease in by:
                by[lease]["released"] = True
    for ev in events:
        if writer_class(ev.get("writer") or "") == "HOLDER" and not fenced(ev, by):
            lease = writer_suffix(ev["writer"])
            if ev.get("kind") == "lease.release":
                by[lease]["released"] = True
            if ev.get("ts") and ev["ts"] > (by[lease]["last"] or ""):
                by[lease]["last"] = ev["ts"]
    return by, current


def fenced(ev, by):
    """-> a reason string when a HOLDER event does not count (no token, a token never granted to its lease, or a
    newer lease granted before it was written), else None. The reducer ignores such events; the lint names them."""
    lease = writer_suffix(ev.get("writer") or "")
    tok = ev.get("token")
    g = by.get(lease)
    if not isinstance(tok, int) or isinstance(tok, bool):
        return "a HOLDER event carries no fencing token"
    if g is None or g["token"] != tok:
        return "token %r was never granted to lease %r" % (tok, lease)
    if _when(ev) < g["granted"]:
        return "written before its lease was granted"
    newer = [o for o in by.values() if o["token"] > tok and o["granted"] <= _when(ev)]
    if newer:
        n = max(newer, key=lambda o: o["token"])
        return "stale token %d: lease %r (token %d) was granted before it" % (tok, n["lease"], n["token"])
    return None


def seals(events):
    """-> {judge shard name: latest judge.sealed body}."""
    out = {}
    for ev in events:
        if ev.get("writer") == "DISPATCH" and ev.get("kind") == "judge.sealed":
            b = ev.get("body") or {}
            if isinstance(b.get("shard"), str):
                out[b["shard"]] = b
    return out


def _shard_bytes(root, mod, shard):
    try:
        with open(os.path.join(ledger_dir(root, mod), shard + ".jsonl"), "rb") as fh:
            return fh.read()
    except OSError:
        return b""


# ---- append ---------------------------------------------------------------------------------------------------------

def _lock(root, mod, what):
    """An exclusive lock per (ledger, purpose), kept outside the tree so git never sees it. The shard's own flock is
    taken by model._append_locked; this one makes check-then-append (idempotency, lease) one step."""
    tag = hashlib.sha256(("%s\0%s" % (os.path.abspath(ledger_dir(root, mod)), what)).encode()).hexdigest()[:20]
    fd = os.open(os.path.join("/tmp", "modledger-%s.lock" % tag), os.O_RDWR | os.O_CREAT, 0o644)
    fcntl.flock(fd, fcntl.LOCK_EX)
    return fd


def _unlock(fd):
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def _spill(root, mod, ev):
    """A body too large for one atomic line keeps every string field WHOLE in `ledger/text/<sha>.txt` (in git, beside
    the shards) and the field holds its head plus a pointer and the full length — the fulltext.fit format, with the
    side file inside the mod's ledger so every clone has it."""
    ev = dict(ev)
    body = dict(ev["body"])
    for k in sorted((k for k, v in body.items() if isinstance(v, str) and len(v) > SPILL_HEAD),
                    key=lambda k: -len(body[k].encode("utf-8"))):
        text = body[k]
        sha = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
        rel = "design/concepts/%s/ledger/text/%s.txt" % (mod, sha)
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
        head = text[:SPILL_HEAD]   # cut-ok: the whole text is kept at `rel`, and the pointer says so
        body[k] = "%s [+%d chars; whole text (%d chars): %s]" % (head, len(text) - len(head), len(text), rel)
        ev["body"] = body
        if len((_canon_line(ev)).encode("utf-8")) < model.PIPE_BUF:
            break
    return ev


def _canon_line(ev):
    return json.dumps(ev, separators=(",", ":"), ensure_ascii=False) + "\n"


def append(root, mod, writer, kind, subject, body=None, version=None, evidence=(), supersedes=None, code_sha=None,
           token=None, run=None, key=None, authority=None, ts=None, now=None, env_writer=_UNSET, views=True):
    """Validate and append one event to `writer`'s shard. -> (event id, created). An identical event already in the
    shard (same idempotency key) is not written again: (its id, False). Refusals raise ModLedgerError saying why."""
    _check_mod(mod)
    _check_writer(writer)
    if env_writer is _UNSET:
        env_writer = os.environ.get("RM_MODLEDGER_WRITER") or None
    if env_writer and env_writer != writer:
        raise ModLedgerError("this process writes as %s; it may not append to the %s shard (a holder never writes a "
                             "judge's finding or his words)" % (env_writer, writer))
    cls = writer_class(writer)
    if not kind_allowed(writer, kind):
        raise ModLedgerError("%s may not write %r (modledger.json writers.%s)%s"
                             % (writer, kind, cls, "; only a JUDGE turns a finding green"
                                if kind.startswith("finding.") else ""))
    if not isinstance(subject, str) or not subject.strip():
        raise ModLedgerError("an event needs a subject (a finding id, a bar, a question, 'stage', ...)")
    body = dict(body or {})
    evidence = list(evidence or [])
    authority = {k: v for k, v in (authority or {}).items() if v} or None
    if authority and set(authority) - set(AUTH_KEYS):
        raise ModLedgerError("authority keys are %s" % (AUTH_KEYS,))
    if kind == "finding.open":
        fix = body.get("proposed_fix")
        if not isinstance(fix, str) or len(fix.strip()) < config()["proposed_fix_min_chars"]:
            raise ModLedgerError("a finding.open must carry proposed_fix: the precise fix the finder would make "
                                 "(his card 2026-11-15: 'Anyone finding anything documents precisely how they would "
                                 "fix it but it goes back to the holder fully informed.'); pass --fix")
    if cls == "OWNER" and not (authority and any(authority.get(k) for k in OWNER_AUTH)):
        raise ModLedgerError("an OWNER event needs his authority: --owner-said, --by-card or --per-ruling")
    if kind == "decision" and not authority:
        raise ModLedgerError("a decision needs its provenance: --owner-said, --by-card, --per-ruling or --why")
    if cls == "BACKFILL" and not evidence:
        raise ModLedgerError("a BACKFILL event cites the old file it came from (--evidence)")
    if cls == "JUDGE":
        if run != writer_suffix(writer):
            raise ModLedgerError("a JUDGE.<run> shard is written by that run only: pass --run %s"
                                 % writer_suffix(writer))
    elif run is not None and not isinstance(run, str):
        raise ModLedgerError("run is a name")
    if cls == "HOLDER" and (not isinstance(token, int) or isinstance(token, bool)):
        raise ModLedgerError("a HOLDER event carries its lease's fencing token (--token)")
    if cls != "HOLDER" and token is not None:
        raise ModLedgerError("only HOLDER events carry a fencing token")
    lk = _lock(root, mod, "append")
    try:
        events = read(root, mod)
        if cls == "JUDGE" and writer in seals(events):
            raise ModLedgerError("%s is sealed (its run ended); a later judge writes its own shard" % writer)
        if cls == "HOLDER":
            by, current = leases(events)
            lease = writer_suffix(writer)
            g = by.get(lease)
            if g is None:
                raise ModLedgerError("lease %r was never granted (the dispatcher grants: modledger grant)" % lease)
            if g["token"] != token:
                raise ModLedgerError("token %d is not lease %r's token" % (token, lease))
            if current != lease:
                raise ModLedgerError("stale token %d: lease %r (token %d) has fenced lease %r; this run must stop"
                                     % (token, current, by[current]["token"], lease))
            if g["released"]:
                raise ModLedgerError("lease %r was released; ask the dispatcher for a new one" % lease)
            idle = config()["lease_idle_minutes"]
            nowts = now or model.now()
            if g["last"] and (_parse_ts(nowts) - _parse_ts(g["last"])).total_seconds() > idle * 60:
                raise ModLedgerError("lease %r lapsed: idle since %s, more than %d minutes (modledger.json "
                                     "lease_idle_minutes)" % (lease, g["last"], idle))
        if supersedes is not None and supersedes not in {e.get("id") for e in events}:
            raise ModLedgerError("supersedes %r: no event of this mod has that id" % (supersedes,))
        if version is None:
            version = reduce(events)["version"]
        if not isinstance(version, str) or not version:
            raise ModLedgerError("this ledger names no Design Version yet: pass --version")
        ev = {"ts": ts or model.now(), "tsn": time.time_ns(), "mod": mod, "version": version, "writer": writer,
              "run": run, "kind": kind, "subject": subject, "body": body, "evidence": evidence}
        for k, v in (("supersedes", supersedes), ("code_sha", code_sha), ("token", token), ("authority", authority)):
            if v is not None:
                ev[k] = v
        ev["key"] = key or derive_key(ev)
        ev["id"] = derive_id(writer, ev["key"])
        for e in events:
            if e.get("_shard") == writer and e.get("key") == ev["key"]:
                return e["id"], False
        if len(_canon_line(ev).encode("utf-8")) >= model.PIPE_BUF:
            ev = _spill(root, mod, ev)
        blob = _canon_line(ev).encode("utf-8")
        if len(blob) >= model.PIPE_BUF:
            raise ModLedgerError("event is %d bytes even with its body texts spilled; O_APPEND is atomic only below "
                                 "%d. Move the material into a file and cite it in --evidence"
                                 % (len(blob), model.PIPE_BUF))
        path = shard_path(root, mod, writer)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        dlock = model._dir_lock(os.path.dirname(path))
        try:
            model._append_locked(path, blob)
        finally:
            if dlock is not None:
                os.close(dlock)
    finally:
        _unlock(lk)
    if views:
        write_views(root, mod)
    return ev["id"], True


def grant(root, mod, lease, version=None, ts=None, views=True):
    """DISPATCH grants a holder lease with the next fencing token. -> the token. The new lease fences every older
    one at once: an older holder's next append is refused, and its later lines are ignored by the reducer."""
    if not re.match(r"^[A-Za-z0-9_-]{1,64}$", lease or ""):
        raise ModLedgerError("lease %r: letters, digits, _ and - only" % (lease,))
    lk = _lock(root, mod, "grant")
    try:
        by, _ = leases(read(root, mod))
        if lease in by:
            raise ModLedgerError("lease %r was already granted (token %d); a new run gets a new lease name"
                                 % (lease, by[lease]["token"]))
        tok = max([g["token"] for g in by.values()] + [0]) + 1
        append(root, mod, "DISPATCH", "lease.grant", "HOLDER/%s" % mod, body={"lease": lease, "token": tok},
               version=version, ts=ts, views=views)
    finally:
        _unlock(lk)
    return tok


def seal(root, mod, run, ts=None, views=True):
    """DISPATCH seals JUDGE.<run> when the run ends: its hash and line count, so a later edit is detectable."""
    shard = "JUDGE.%s" % run
    _check_writer(shard)
    data = _shard_bytes(root, mod, shard)
    eid, _ = append(root, mod, "DISPATCH", "judge.sealed", shard,
                    body={"shard": shard, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
                          "lines": data.count(b"\n")}, ts=ts, views=views)
    return eid


# ---- reduce ---------------------------------------------------------------------------------------------------------

def _text(ev):
    return (ev.get("body") or {}).get("text") or ""


def reduce(events):
    """-> the mod's state now, a pure function of its events. Superseded events and fenced HOLDER events (stale
    tokens) do not count; both are listed."""
    events = [e for e in events if isinstance(e, dict)]
    superseded = sorted({e["supersedes"] for e in events if isinstance(e.get("supersedes"), str)})
    by, current = leases(events)
    st = {"reducer": REDUCER_VERSION, "version": None, "stage": None, "exit_claims": [], "bars": {}, "findings": {},
          "causes": {}, "questions": {}, "answers": {}, "decisions": {}, "checkpoint": None, "session": None,
          "lease": None, "spend_usd": 0.0, "spend_tokens": 0, "tests": [], "notes": [], "superseded": superseded, "fenced": [],
          "events": len(events), "shards": sorted({e.get("_shard") or e.get("writer") for e in events})}
    sup = set(superseded)
    ceiling = config()["holder_context_ceiling_tokens"]
    opened_version = False
    for ev in events:
        if ev.get("id") in sup:
            continue
        w = ev.get("writer") or ""
        if writer_class(w) == "HOLDER":
            why = fenced(ev, by)
            if why:
                st["fenced"].append({"id": ev.get("id"), "why": why})
                continue
        k, s, b = ev.get("kind"), ev.get("subject"), ev.get("body") or {}
        when = ev.get("ts")
        if k == "version.open":
            st["version"] = b.get("version") or ev.get("version")
            opened_version = True
        elif ev.get("version") and not opened_version:
            st["version"] = ev["version"]
        elif k == "stage.enter":
            st["stage"] = b.get("stage")
        elif k == "stage.accepted":
            st["stage"] = b.get("to")
            st["exit_claims"] = []
        elif k == "stage.exit_claimed":
            st["exit_claims"].append({"by": w, "ts": when, "text": _text(ev), "evidence": ev.get("evidence")})
        elif k == "stage.rejected":
            st["exit_claims"] = [dict(c, rejected=_text(ev)) for c in st["exit_claims"]]
        elif k == "stage.exit_confirmed":
            st["exit_claims"] = [dict(c, confirmed_by=w) for c in st["exit_claims"]]
        elif k and k.startswith("bar."):
            bar = st["bars"].setdefault(s, {"verdict": None})
            bar.update({"status": k.split(".", 1)[1], "text": _text(ev) or bar.get("text"), "ts": when})
        elif k in ("test.run", "live.run"):
            st["tests"].append({"ts": when, "kind": k, "subject": s, "result": b.get("result"), "sha":
                                ev.get("code_sha"), "text": _text(ev), "by": w})
            if b.get("bar"):
                st["bars"].setdefault(b["bar"], {"verdict": None})["verdict"] = b.get("result")
        elif k == "finding.open":
            st["findings"][s] = {"status": "open", "text": _text(ev), "proposed_fix": b.get("proposed_fix"),
                                 "by": w, "ts": when, "claim": None}
        elif k and k.startswith("finding.") and s in st["findings"]:
            f = st["findings"][s]
            f["status"] = {"finding.claimed_fixed": "claimed_fixed", "finding.disputed": "disputed",
                           "finding.verified": "verified", "finding.reopened": "open"}.get(k, f["status"])
            f["ts"] = when
            if k in ("finding.claimed_fixed", "finding.disputed"):
                f["claim"] = _text(ev)
            if k == "finding.reopened" and _text(ev):
                f["text"] = "%s (reopened: %s)" % (f["text"], _text(ev))
        elif k == "cause.tried":
            st["causes"][s] = {"status": "tried", "text": _text(ev), "ts": when}
        elif k == "cause.refuted":
            st["causes"][s] = {"status": "refuted", "text": _text(ev), "ts": when, "code_sha": ev.get("code_sha"),
                               "depends_on": b.get("depends_on") or []}
        elif k == "cause.reopened":
            st["causes"][s] = {"status": "tried", "text": _text(ev), "ts": when}
        elif k == "question.ask":
            st["questions"][s] = {"status": "open", "text": _text(ev), "obvious": b.get("obvious"),
                                  "against": b.get("against"), "ts": when, "by": w}
        elif k == "question.answer":
            q = st["questions"].setdefault(s, {"text": b.get("question") or "", "ts": when})
            q.update({"status": "answered", "answer": _text(ev)})
            st["answers"][s] = {"question": q.get("text"), "answer": _text(ev), "ts": when,
                                "authority": ev.get("authority")}
        elif k == "question.withdrawn" and s in st["questions"]:
            st["questions"][s]["status"] = "withdrawn"
        elif k == "decision":
            st["decisions"][s] = {"text": _text(ev), "by": w, "ts": when, "authority": ev.get("authority")}
            auth = ev.get("authority") or {}
            if w == "OWNER" or auth.get("owner_said") or auth.get("by_card"):
                st["answers"]["decision:" + s] = {"question": None, "answer": _text(ev), "ts": when,
                                                  "authority": ev.get("authority")}
        elif k == "session.id":
            ctx = b.get("context_tokens")
            st["session"] = {"session_id": b.get("session_id"), "context_tokens": ctx, "ceiling": ceiling,
                             "rotate_due": isinstance(ctx, int) and ctx >= ceiling, "ts": when}
        elif k == "session.checkpoint":
            st["checkpoint"] = {"ts": when, "by": w, "done": b.get("done") or _text(ev), "next": b.get("next"),
                                "ruled_out": b.get("ruled_out")}
        elif k == "spend":
            usd = b.get("usd")
            if isinstance(usd, (int, float)) and not isinstance(usd, bool):
                st["spend_usd"] = round(st["spend_usd"] + usd, 4)
            if isinstance(b.get("tokens"), int) and not isinstance(b.get("tokens"), bool):
                st["spend_tokens"] += b["tokens"]
        elif k == "note":
            st["notes"].append({"ts": when, "by": w, "subject": s, "text": _text(ev)})
    if current:
        g = by[current]
        st["lease"] = {"lease": current, "token": g["token"], "last": g["last"], "released": g["released"]}
    return st


# ---- packet ---------------------------------------------------------------------------------------------------------

def _one(text, where=None):
    """One line. With `where` (the command that prints the whole event), a text past the configured packet_line_chars
    is clipped with fulltext.clip, which says it is cut and where the rest is; the ledger keeps it whole."""
    t = " ".join(str(text or "").split())
    if where:
        try:
            from . import fulltext
        except ImportError:
            import fulltext  # noqa: E402
        t = fulltext.clip(t, config()["packet_line_chars"], where)
    return t


def packet_from(mod, events, budget=None):
    """-> (text, info). The bounded read a holder starts from (spec §3.3). Never dropped: the open findings with
    their proposed fixes, the refuted causes, his answers, the open questions, the bars, the holder's last checkpoint.
    Dropped oldest-first when over budget: closed findings, other decisions, causes tried, tests, notes. Ends with
    what it left out."""
    budget = budget or config()["packet_budget_tokens"]
    st = reduce(events)

    def cl(text, subject):
        return _one(text, "modledger.py show --mod %s %s" % (mod, subject))

    keep = ["# %s — mod ledger packet" % mod,
            "version %s · stage %s · %d events in %d shards · reducer %d"
            % (st["version"] or "unknown", st["stage"] if st["stage"] is not None else "unknown", st["events"],
               len(st["shards"]), REDUCER_VERSION)]
    if not events:
        keep.append("This mod's ledger holds no events yet (no events).")
    if st["lease"]:
        L = st["lease"]
        keep.append("holder lease %s, token %d, last active %s%s" % (L["lease"], L["token"], L["last"],
                                                                    ", released" if L["released"] else ""))
    if st["session"]:
        S = st["session"]
        keep.append("holder session %s, context %s of ceiling %d%s" % (S["session_id"], S["context_tokens"],
                                                                      S["ceiling"], " — ROTATE DUE" if
                                                                      S["rotate_due"] else ""))
    for c in st["exit_claims"]:
        keep.append("exit claimed by %s at %s: %s%s" % (c["by"], c["ts"], cl(c["text"], "stage"),
                                                        " (confirmed by %s)" % c["confirmed_by"]
                                                        if c.get("confirmed_by") else ""))
    if st["checkpoint"]:
        C = st["checkpoint"]
        keep += ["", "## Last checkpoint (%s, %s)" % (C["by"], C["ts"]), "- done: " + cl(C["done"], "checkpoint"),
                 "- next: " + cl(C["next"], "checkpoint"), "- ruled out: " + cl(C["ruled_out"], "checkpoint")]
    opened = sorted(((k, f) for k, f in st["findings"].items() if f["status"] != "verified"), key=lambda t: t[1]["ts"])
    keep += ["", "## Open findings (%d)" % len(opened)]
    for k, f in opened:
        keep.append("- %s [%s] by %s, %s: %s" % (k, f["status"], f["by"], f["ts"], cl(f["text"], k)))
        keep.append("  proposed fix: " + cl(f["proposed_fix"], k))
        if f.get("claim"):
            keep.append("  holder: " + cl(f["claim"], k))
    refuted = sorted(((k, c) for k, c in st["causes"].items() if c["status"] == "refuted"), key=lambda t: t[1]["ts"])
    keep += ["", "## Causes refuted (%d) — do not chase these again" % len(refuted)]
    for k, c in refuted:
        on = ", ".join(x for x in [("on %s" % c["code_sha"]) if c.get("code_sha") else "",
                                    ("depends on %s" % ", ".join(c["depends_on"])) if c.get("depends_on") else ""] if x)
        keep.append("- %s: %s%s" % (k, cl(c["text"], k), (" (%s)" % on) if on else ""))
    keep += ["", "## His answers (%d)" % len(st["answers"])]
    for k, a in sorted(st["answers"].items(), key=lambda t: t[1]["ts"]):
        keep.append("- %s%s: %s" % (k, (" (Q: %s)" % cl(a["question"], k)) if a.get("question") else "",
                                    cl(a["answer"], k)))
    openq = [(k, q) for k, q in st["questions"].items() if q.get("status") == "open"]
    keep += ["", "## Open questions (%d)" % len(openq)]
    for k, q in openq:
        keep.append("- %s: %s (obvious answer: %s; against it: %s)" % (k, cl(q["text"], k), cl(q.get("obvious"), k),
                                                                      cl(q.get("against"), k)))
    keep += ["", "## Bars (%d)" % len(st["bars"])]
    for k, b in sorted(st["bars"].items()):
        keep.append("- %s [%s] verdict %s%s" % (k, b.get("status") or "?", b.get("verdict") or "none",
                                               (": " + cl(b["text"], k)) if b.get("text") else ""))
    keep.append("")
    keep.append("spend recorded: USD %.2f, %d tokens" % (st["spend_usd"], st["spend_tokens"]))
    # droppable material: (ts, group, line)
    drop = []
    for k, f in st["findings"].items():
        if f["status"] == "verified":
            drop.append((f["ts"], "closed findings", "- %s [verified] by %s: %s — fix was: %s"
                         % (k, f["by"], cl(f["text"], k), cl(f["proposed_fix"], k))))
    for k, d in st["decisions"].items():
        if d["by"] != "OWNER":
            drop.append((d["ts"], "decisions", "- %s (%s, %s): %s" % (k, d["by"], d["ts"], cl(d["text"], k))))
    for k, c in st["causes"].items():
        if c["status"] == "tried":
            drop.append((c["ts"], "causes tried", "- %s: %s" % (k, cl(c["text"], k))))
    for t in st["tests"]:
        drop.append((t["ts"], "tests", "- %s %s %s: %s %s" % (t["ts"], t["kind"], t["subject"], t["result"],
                                                              cl(t["text"], t["subject"]))))
    for n in st["notes"]:
        drop.append((n["ts"], "notes", "- %s %s %s: %s" % (n["ts"], n["by"], n["subject"], cl(n["text"], n["subject"]))))
    drop.sort(key=lambda t: (t[0] or "", t[1], t[2]))
    groups = ("decisions", "closed findings", "causes tried", "tests", "notes")

    def render(k):
        kept, gone = drop[k:], {}
        for _, g, _l in drop[:k]:
            gone[g] = gone.get(g, 0) + 1
        out = list(keep)
        for g in groups:
            lines = [l for _, gg, l in kept if gg == g]
            if lines:
                out += ["", "## %s (%d%s)" % (g[0].upper() + g[1:], len(lines),
                                              ", %d older left out" % gone[g] if gone.get(g) else "")] + lines
        out += ["", "## Left out"]
        for g in groups:
            if gone.get(g):
                out.append("- %s: %d, oldest first (`modledger.py show --mod %s <subject>`)" % (g, gone[g], mod))
        if st["superseded"] or st["fenced"]:
            out.append("- superseded events: %d; fenced holder events (stale tokens): %d"
                       % (len(st["superseded"]), len(st["fenced"])))
        out.append("- the full history: %d events (views/history.md; never read whole)" % len(events))
        return "\n".join(out) + "\n", gone

    lo, hi = 0, len(drop)
    text, gone = render(0)
    if tokens(text) > budget:
        while lo < hi:                       # the fewest dropped lines that fit
            mid = (lo + hi) // 2
            if tokens(render(mid)[0]) <= budget:
                hi = mid
            else:
                lo = mid + 1
        text, gone = render(lo)
    over = tokens(text) > budget
    if over:
        text = ("OVER BUDGET: %d tokens > %d, and nothing droppable is left (open findings, refuted causes, his "
                "answers, open questions and bars are never dropped)\n" % (tokens(text), budget)) + text
    return text, {"tokens": tokens(text), "budget": budget, "dropped": gone, "over_budget": over,
                  "events": len(events)}


def packet(root, mod, budget=None):
    return packet_from(mod, read(root, mod), budget)


# ---- views ----------------------------------------------------------------------------------------------------------

def _offsets(root, mod):
    return {s: len(_shard_bytes(root, mod, s)) for s in shard_names(root, mod)}


def _header(mod, offsets, body):
    return ("<!-- modledger view, generated: never edit (python3 src/RimMandrake/rimflow/modledger.py views --mod %s)"
            " reducer=%d shards=%s body_sha256=%s -->\n"
            % (mod, REDUCER_VERSION, _canon(offsets), hashlib.sha256(body.encode("utf-8")).hexdigest()))


def render_views(root, mod):
    """-> {view name: full text}. A pure function of the shards: no clock, no git."""
    events = read(root, mod)
    offs = _offsets(root, mod)
    state_md = packet_from(mod, events)[0]
    hist = ["# %s — mod ledger history (%d events, merged across shards)" % (mod, len(events)), ""]
    for e in events:
        hist.append("- %s %s#%d %s %s v%s: %s" % (e.get("ts"), e["_shard"], e["_seq"], e.get("kind"),
                                                  e.get("subject"), e.get("version"), _one(_text(e))))
    hist_md = "\n".join(hist) + "\n"
    st = reduce(events)
    sj = json.dumps(st, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    return {"state.md": _header(mod, offs, state_md) + state_md,
            "history.md": _header(mod, offs, hist_md) + hist_md,
            "state.json": json.dumps({"_view": {"reducer": REDUCER_VERSION, "shards": offs,
                                                "body_sha256": hashlib.sha256(sj.encode("utf-8")).hexdigest()},
                                      "state": st}, indent=1, sort_keys=True, ensure_ascii=False) + "\n"}


def write_views(root, mod):
    """Regenerate every view under one lock, reading the shards inside it (so the last writer saw every append)."""
    if not shard_names(root, mod):
        return []
    lk = _lock(root, mod, "views")
    try:
        d = views_dir(root, mod)
        os.makedirs(d, exist_ok=True)
        out = []
        for name, text in render_views(root, mod).items():
            p = os.path.join(d, name)
            tmp = p + ".tmp%d" % os.getpid()
            with open(tmp, "w", encoding="utf-8") as fh:
                fh.write(text)
            os.replace(tmp, p)
            out.append(p)
        return out
    finally:
        _unlock(lk)


def _view_meta(name, text):
    """-> (recorded meta, body as written) or (None, None) when the view's header is unreadable."""
    try:
        if name.endswith(".json"):
            obj = json.loads(text)
            body = json.dumps(obj["state"], indent=1, sort_keys=True, ensure_ascii=False) + "\n"
            return obj["_view"], body
        first, body = text.split("\n", 1)
        m = re.search(r"reducer=(\d+) shards=(\{.*?\}) body_sha256=([0-9a-f]{64})", first)
        return {"reducer": int(m.group(1)), "shards": json.loads(m.group(2)), "body_sha256": m.group(3)}, body
    except (ValueError, KeyError, AttributeError, TypeError):
        return None, None


# ---- lint -----------------------------------------------------------------------------------------------------------

def mods_with_ledgers(root):
    base = os.path.join(root, "design", "concepts")
    try:
        names = sorted(os.listdir(base))
    except OSError:
        return []
    return [n for n in names if MOD_RE.match(n) and os.path.isdir(os.path.join(base, n, "ledger"))]


def lint(root, mod=None, base="origin/main"):
    """-> (findings [(code, path, line, detail)], notes). The worktree against `base` (None/'' = no base: the
    append-only checks are UNMEASURED and said so)."""
    notes = []
    have_base = bool(base) and ledger_lint.ref_exists(root, base)
    if base and not have_base:
        notes.append("no base ref %r — NOT_APPEND checks UNMEASURED, structure only" % base)
    if not base:
        notes.append("no base given — NOT_APPEND checks UNMEASURED, structure only")
    out = []
    for m in ([mod] if mod else mods_with_ledgers(root)):
        out += _lint_mod(root, m, base if have_base else None)
    return out, notes


def _lint_mod(root, mod, base):
    out = []
    d = ledger_dir(root, mod)
    rel_d = os.path.relpath(d, root)
    names = shard_names(root, mod)
    if base:
        r = ledger_lint._git(root, "ls-tree", "--name-only", base, rel_d + "/")
        names = sorted(set(names) | {os.path.basename(p)[:-len(".jsonl")] for p in r.stdout.decode().splitlines()
                                     if p.endswith(".jsonl")})
    for shard in names:
        rel = "%s/%s.jsonl" % (rel_d, shard)
        data = _shard_bytes(root, mod, shard) if os.path.exists(os.path.join(root, rel)) else None
        out += ledger_lint.lint_blob(rel, data, ledger_lint.blob_at(root, base, rel) if base else None)
        if not WRITER_RE.match(shard):
            out.append(("BAD_SHARD_NAME", rel, 0, "a shard is named for its writer: DISPATCH, OWNER, STEWARD, "
                        "BACKFILL, HOLDER.<lease>, JUDGE.<run>"))
    events = read(root, mod)
    by, _ = leases(events)
    ids = {e.get("id") for e in events}
    keys = {}
    for e in events:
        rel = "%s/%s.jsonl" % (rel_d, e["_shard"])
        missing = [k for k in REQUIRED if k not in e]
        if missing:
            out.append(("MISSING_FIELD", rel, e["_seq"], "missing %s" % ", ".join(missing)))
            continue
        w = e["writer"]
        if w != e["_shard"]:
            out.append(("WRONG_SHARD", rel, e["_seq"], "an event written by %s sits in the %s shard (a writer "
                        "appends only to its own)" % (w, e["_shard"])))
        if e["mod"] != mod:
            out.append(("WRONG_MOD", rel, e["_seq"], "event names mod %r" % e["mod"]))
        if WRITER_RE.match(e["_shard"]) and not kind_allowed(e["_shard"], e["kind"]):
            out.append(("KIND_NOT_ALLOWED", rel, e["_seq"], "%s may not write %r" % (e["_shard"], e["kind"])))
        if e["id"] != derive_id(w, e["key"]):
            out.append(("ID_MISMATCH", rel, e["_seq"], "id is not derived from writer and key"))
        k = (e["_shard"], e["key"])
        if k in keys and keys[k] != model.event_key(_clean(e)):
            out.append(("DUP_KEY", rel, e["_seq"], "two different events share the idempotency key %s" % e["key"]))
        keys.setdefault(k, model.event_key(_clean(e)))
        if e["kind"] == "finding.open":
            fix = (e.get("body") or {}).get("proposed_fix")
            if not isinstance(fix, str) or len(fix.strip()) < config()["proposed_fix_min_chars"]:
                out.append(("NO_PROPOSED_FIX", rel, e["_seq"], "a finding carries the precise fix its finder would "
                            "make"))
        cls = writer_class(e["_shard"])
        if cls == "HOLDER" and w == e["_shard"]:
            why = fenced(e, by)
            if why:
                out.append(("STALE_TOKEN", rel, e["_seq"], why))
        if cls == "JUDGE" and e.get("run") != writer_suffix(e["_shard"]):
            out.append(("WRONG_SHARD", rel, e["_seq"], "a JUDGE.<run> shard holds that run's events only"))
        if cls == "OWNER" and not any((e.get("authority") or {}).get(a) for a in OWNER_AUTH):
            out.append(("NO_AUTHORITY", rel, e["_seq"], "an OWNER event carries his words, card or ruling"))
        if cls == "BACKFILL" and not e.get("evidence"):
            out.append(("NO_EVIDENCE", rel, e["_seq"], "a BACKFILL event cites the old file it came from"))
        if e.get("supersedes") and e["supersedes"] not in ids:
            out.append(("BAD_SUPERSEDES", rel, e["_seq"], "supersedes an id this ledger does not hold"))
    for shard, s in seals(events).items():
        data = _shard_bytes(root, mod, shard)
        if hashlib.sha256(data).hexdigest() != s.get("sha256"):
            out.append(("SEALED_CHANGED", "%s/%s.jsonl" % (rel_d, shard), 0, "the judge shard changed after its "
                        "seal (%d bytes sealed, %d now)" % (s.get("bytes", -1), len(data))))
    if names:
        out += _lint_views(root, mod)
    return out


def _lint_views(root, mod):
    out = []
    want = render_views(root, mod)
    vd = views_dir(root, mod)
    for name, text in want.items():
        p = os.path.join(vd, name)
        rel = os.path.relpath(p, root)
        try:
            with open(p, encoding="utf-8") as fh:
                have = fh.read()
        except OSError:
            out.append(("VIEW_MISSING", rel, 0, "regenerate: modledger.py views --mod %s" % mod))
            continue
        if have == text:
            continue
        meta, body = _view_meta(name, have)
        if meta is None or hashlib.sha256(body.encode("utf-8")).hexdigest() != meta.get("body_sha256"):
            out.append(("VIEW_EDITED", rel, 0, "the view was edited by hand; a view is printed from the ledger, "
                        "never written. Append the fact as an event, then: modledger.py views --mod %s" % mod))
        else:
            out.append(("VIEW_STALE", rel, 0, "built from shards %s (reducer %s), the ledger is now %s (reducer %d):"
                        " modledger.py views --mod %s" % (_canon(meta.get("shards")), meta.get("reducer"),
                                                          _canon(_offsets(root, mod)), REDUCER_VERSION, mod)))
    return out


# ---- CLI ------------------------------------------------------------------------------------------------------------

def _line(e):
    t = _one(_text(e))
    fix = (e.get("body") or {}).get("proposed_fix")
    return "%s %s#%d %s %s v%s%s: %s%s" % (e.get("ts"), e["_shard"], e["_seq"], e.get("kind"), e.get("subject"),
                                           e.get("version"), (" supersedes %s" % e["supersedes"])
                                           if e.get("supersedes") else "", t,
                                           (" — proposed fix: " + _one(fix)) if fix else "")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=None)
    sub = ap.add_subparsers(dest="verb", required=True)
    a = sub.add_parser("append")
    a.add_argument("--mod", required=True)
    a.add_argument("--writer", required=True)
    a.add_argument("--kind", required=True)
    a.add_argument("--subject", required=True)
    a.add_argument("--version")
    a.add_argument("--text")
    a.add_argument("--fix", help="the precise fix the finder would make (finding.open)")
    a.add_argument("--body", help="a JSON object merged into the body")
    a.add_argument("--evidence", action="append", default=[])
    a.add_argument("--supersedes")
    a.add_argument("--code-sha")
    a.add_argument("--token", type=int)
    a.add_argument("--run")
    a.add_argument("--key")
    for k in AUTH_KEYS:
        a.add_argument("--" + k.replace("_", "-"))
    a.add_argument("--no-views", action="store_true")
    g = sub.add_parser("grant")
    g.add_argument("--mod", required=True)
    g.add_argument("--lease", required=True)
    g.add_argument("--version")
    s = sub.add_parser("seal")
    s.add_argument("--mod", required=True)
    s.add_argument("--run", required=True)
    sh = sub.add_parser("show")
    sh.add_argument("--mod", required=True)
    sh.add_argument("subject", nargs="?")
    sh.add_argument("--kind")
    stp = sub.add_parser("state")
    stp.add_argument("--mod", required=True)
    p = sub.add_parser("packet")
    p.add_argument("--mod", required=True)
    p.add_argument("--budget", type=int)
    p.add_argument("--strict", action="store_true", help="exit 1 on an empty ledger or a packet over budget")
    v = sub.add_parser("views")
    v.add_argument("--mod", required=True)
    li = sub.add_parser("lint")
    li.add_argument("--mod")
    li.add_argument("--base", default="origin/main", help="'' for none")
    o = ap.parse_args(argv)
    root = o.root or default_root()
    try:
        if o.verb == "append":
            body = json.loads(o.body) if o.body else {}
            if not isinstance(body, dict):
                raise ModLedgerError("--body is a JSON object")
            if o.text is not None:
                body["text"] = o.text
            if o.fix is not None:
                body["proposed_fix"] = o.fix
            auth = {k: getattr(o, k) for k in AUTH_KEYS if getattr(o, k)}
            eid, created = append(root, o.mod, o.writer, o.kind, o.subject, body=body, version=o.version,
                                  evidence=o.evidence, supersedes=o.supersedes, code_sha=o.code_sha, token=o.token,
                                  run=o.run, key=o.key, authority=auth or None, views=not o.no_views)
            print(("APPENDED " if created else "ALREADY ") + eid)
        elif o.verb == "grant":
            print("TOKEN %d" % grant(root, o.mod, o.lease, version=o.version))
        elif o.verb == "seal":
            print("SEALED " + seal(root, o.mod, o.run))
        elif o.verb == "show":
            evs = [e for e in read(root, o.mod) if (not o.subject or e.get("subject") == o.subject)
                   and (not o.kind or e.get("kind") == o.kind)]
            for e in evs:
                print(_line(e))
            print("%d event%s" % (len(evs), "" if len(evs) == 1 else "s"))
        elif o.verb == "state":
            print(json.dumps(reduce(read(root, o.mod)), indent=1, sort_keys=True, ensure_ascii=False))
        elif o.verb == "packet":
            text, info = packet(root, o.mod, o.budget)
            sys.stdout.write(text)
            print("packet: %d tokens of budget %d; %d events; left out %s"
                  % (info["tokens"], info["budget"], info["events"], _canon(info["dropped"]) if info["dropped"]
                     else "nothing but the full history"), file=sys.stderr)
            if o.strict and (info["events"] == 0 or info["over_budget"]):
                return 1
        elif o.verb == "views":
            for pth in write_views(root, o.mod):
                print("wrote " + os.path.relpath(pth, root))
        elif o.verb == "lint":
            findings, notes = lint(root, o.mod, o.base or None)
            for n in notes:
                print("note: " + n)
            for code, path, ln, detail in findings:
                print("%s %s:%s %s" % (code, path, ln, detail))
            print("modledger lint: %d finding%s" % (len(findings), "" if len(findings) == 1 else "s"))
            return 1 if findings else 0
    except ModLedgerError as e:
        print("REFUSED: %s" % e)
        return 1
    except Exception as e:                       # noqa: BLE001 — say so, exit 2
        print("modledger: could not run: %s: %s" % (type(e).__name__, e))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
