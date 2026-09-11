#!/usr/bin/env python3
"""artreg.py — the SOLE writer of `infrastructure/artpipe/registry.jsonl`.

Design: `design/RimMandrake/art_regen_registry_design.md` (owner-ruled
2026-09-11). Item: `infrastructure/state/items/ART_REGEN_REGISTRY_1.md`.

This is the tracking layer ABOVE `ART_PIPELINE_DAEMON_1`'s queue
(`pending/active/done/failed/`, `throughput.jsonl`) — it changes nothing
about that daemon's contract. `registry.jsonl` is an append-only event log;
every view (`status`, `render`) is DERIVED from replaying it, never
hand-edited. Callers write through this module — either its CLI, or (for
`fill_queue.py`/`artpiped.py`, which call this in-process to avoid a
subprocess spawn per job in a hot loop) its `record_*()` functions directly.
Either path ends up appending through the same `_append()` under the same
lock, so "one CLI owns every write" holds regardless of call shape.

**Identity** (design §1, not this script's call to redesign):
- A **target** is the thing that must exist: `<asset_key>/<facing>`, or bare
  `<asset_key>` when the job has no facing. Targets are never parsed back
  out of a job_id by guesswork at read time — every event that only knows a
  job_id (`generated`, `validated`) resolves its target by looking up the
  most recent `queued` event recorded for that job_id in the registry
  itself, unless the caller already knows it and passes `--target`.
- A **job** is one generation attempt against a target; job ids stay
  exactly as the daemon already knows them.
- **Iterations are counted from `queued` events** — one more than however
  many `queued` events already exist for this target — never parsed from a
  job-id suffix like `_v2`/`_r3`.

**Retry cap — resolving one numeric discrepancy honestly** rather than
guessing: the design's prose says "retry cap 3, then escalate ... rejected 3
full owner-verdict rounds ... parks", while the item's own verify checklist
tests "a 4th rejection on the same target parks it". Read together, "cap 3"
most sensibly means 3 retries are ALLOWED after a rejection (attempts 2, 3,
4 each get one more try) and parking fires only once a 4th rejection proves
the 3rd retry didn't fix it either — which is exactly the item's literal,
checkable test. `PARK_AFTER_REJECTIONS = 4` implements that reading; it is
one named constant, trivially moved if the owner meant literally 3.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import re
import sys
import time
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

REGISTRY_PATH = common.QUEUE_ROOT / "registry.jsonl"
REGISTRY_LOCK = common.QUEUE_ROOT / "registry.jsonl.lock"
ART_STATUS_JSON = common.QUEUE_ROOT / "art_status.json"
ART_STATUS_HTML = common.QUEUE_ROOT / "art_status.html"

WEEKLY_WINDOW_MINUTES = 10080  # the "secondary" codex meter window == 7 days
WEEKLY_BUDGET_USD = 20.0       # owner-ruled plan rate: 5% of the weekly window ≈ $1
PARK_AFTER_REJECTIONS = 4      # see module docstring — resolves design-vs-item wording

EVENT_TYPES = ("registered", "queued", "generated", "validated", "sheeted",
               "verdict", "committed", "deployed")

TERMINAL_STATES = ("committed", "deployed")


class RegError(ValueError):
    pass


# --------------------------------------------------------------------------
# storage: append-only, one lock for every read-compute-append cycle
# --------------------------------------------------------------------------

@contextmanager
def _locked():
    REGISTRY_LOCK.parent.mkdir(parents=True, exist_ok=True)
    fh = open(REGISTRY_LOCK, "a+")
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        fh.close()


def read_events(path: Path = REGISTRY_PATH) -> list[dict]:
    """Every event in file order. A line that fails to parse is skipped with
    a stderr warning, never silently dropped and never a crash — this is our
    OWN append-only log, but a torn write from a killed process is still
    possible and must not take the whole registry down."""
    if not path.is_file():
        return []
    events = []
    for i, line in enumerate(path.read_text().splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            print(f"artreg: WARNING {path}:{i}: unparseable line skipped ({exc})",
                  file=sys.stderr)
    return events


def _append(event: dict, path: Path = REGISTRY_PATH) -> dict:
    if event.get("event") not in EVENT_TYPES:
        raise RegError(f"unknown event type {event.get('event')!r}")
    event.setdefault("ts", time.time())
    event.setdefault("by", "unknown")
    common.append_jsonl(path, event)
    return event


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# --------------------------------------------------------------------------
# target <-> job resolution
# --------------------------------------------------------------------------

_VER_OR_RETRY_SUFFIX = re.compile(r"_(?:v|r)\d+$")


def derive_target(job_id: str, facing: str | None) -> str:
    """Backfill-only helper: reconstruct `<asset_key>/<facing>` from a bare
    job_id + its job file's own `facing` field (never guessed from the id
    alone when a `queued` event already names the real target)."""
    base = job_id
    if facing:
        suffix = f"_{facing}"
        if base.endswith(suffix):
            base = base[: -len(suffix)]
    # strip trailing _v<N> / _r<N> repeatedly — a job can carry both
    # ("..._v1_r2") and either order.
    while True:
        m = _VER_OR_RETRY_SUFFIX.search(base)
        if not m:
            break
        base = base[: m.start()]
    return f"{base}/{facing}" if facing else base


def resolve_target_for_job(job_id: str, events: list[dict] | None = None) -> str | None:
    """Most recent `queued` event's target for this job_id, or None."""
    events = events if events is not None else read_events()
    best = None
    for ev in events:
        if ev.get("event") == "queued" and ev.get("job_id") == job_id:
            if best is None or ev.get("ts", 0) >= best.get("ts", 0):
                best = ev
    return best.get("target") if best else None


def _require_target(target: str | None, job_id: str | None,
                     events: list[dict]) -> str:
    if target:
        return target
    if job_id:
        resolved = resolve_target_for_job(job_id, events)
        if resolved:
            return resolved
        raise RegError(f"no 'queued' event found for job_id={job_id!r} — "
                        f"pass --target explicitly")
    raise RegError("need --target or a --job-id that resolves to one")


# --------------------------------------------------------------------------
# record_*() — the actual write API; the CLI subcommands are thin wrappers
# --------------------------------------------------------------------------

def record_registered(target: str, source: str, by: str = "unknown",
                       ts: float | None = None) -> dict:
    ev = {"event": "registered", "target": target, "source": source, "by": by}
    if ts is not None:
        ev["ts"] = ts
    return _append(ev)


def record_queued(target: str, job_id: str, notes: str = "", by: str = "unknown",
                   ts: float | None = None) -> dict:
    with _locked():
        events = read_events()
        iteration = 1 + sum(1 for e in events
                             if e.get("event") == "queued" and e.get("target") == target)
        ev = {"event": "queued", "target": target, "job_id": job_id,
              "iteration": iteration, "notes": notes, "by": by}
        if ts is not None:
            ev["ts"] = ts
        return _append(ev)


def record_generated(job_id: str, target: str | None = None,
                      elapsed_s: float | None = None, by: str = "unknown",
                      ts: float | None = None) -> dict:
    with _locked():
        events = read_events()
        target = _require_target(target, job_id, events)
        ev = {"event": "generated", "target": target, "job_id": job_id,
              "elapsed_s": elapsed_s, "by": by}
        if ts is not None:
            ev["ts"] = ts
        return _append(ev)


def record_validated(job_id: str, verdict: str, target: str | None = None,
                      by: str = "unknown", ts: float | None = None) -> dict:
    if verdict not in ("pass", "fail"):
        raise RegError("verdict must be 'pass' or 'fail'")
    with _locked():
        events = read_events()
        target = _require_target(target, job_id, events)
        ev = {"event": "validated", "target": target, "job_id": job_id,
              "verdict": verdict, "by": by}
        if ts is not None:
            ev["ts"] = ts
        return _append(ev)


def record_sheeted(target: str, sheet: str, by: str = "unknown") -> dict:
    return _append({"event": "sheeted", "target": target, "sheet": sheet, "by": by})


def record_verdict(target: str, result: str, notes: str = "",
                    as_target: str | None = None, job_id: str | None = None,
                    by: str = "unknown") -> list[dict]:
    """Returns the list of events actually written — 1 for accepted/rejected,
    3 for repurposed (design §1: closes `as_target`, re-registers `target`)."""
    if result not in ("accepted", "rejected", "repurposed"):
        raise RegError("result must be accepted|rejected|repurposed")
    if result == "repurposed" and not as_target:
        raise RegError("verdict repurposed needs --as-target")
    if result != "repurposed" and as_target:
        raise RegError("--as-target only makes sense with result=repurposed")

    with _locked():
        written = []
        ev = {"event": "verdict", "target": target, "result": result, "notes": notes,
              "by": by}
        if job_id:
            ev["job_id"] = job_id
        if as_target:
            ev["as_target"] = as_target
        written.append(_append(ev))

        if result == "rejected":
            events = read_events()
            n = sum(1 for e in events
                    if e.get("event") == "verdict" and e.get("target") == target
                    and e.get("result") == "rejected")
            if n >= PARK_AFTER_REJECTIONS:
                print(f"artreg: PARKED — {target!r} has been rejected {n} times "
                      f"(cap {PARK_AFTER_REJECTIONS}); needs a different approach, "
                      f"see `status --parked`", file=sys.stderr)

        if result == "repurposed":
            source_note = f"repurpose of {job_id}" if job_id else "repurpose (job id not given)"
            written.append(_append({
                "event": "verdict", "target": as_target, "result": "accepted",
                "notes": (f"accepted via repurpose from job {job_id!r}, originally "
                          f"intended for {target!r}" if job_id else
                          f"accepted via repurpose, originally intended for {target!r}"),
                "by": by,
            }))
            written.append(_append({
                "event": "registered", "target": target, "source": source_note, "by": by,
            }))
        return written


def record_committed(target: str, repo_path: str, sha: str, by: str = "unknown") -> dict:
    return _append({"event": "committed", "target": target, "repo_path": repo_path,
                     "sha": sha, "by": by})


def record_deployed(target: str, by: str = "unknown") -> dict:
    return _append({"event": "deployed", "target": target, "by": by})


# --------------------------------------------------------------------------
# derived state — one pass over a target's own events, in ts order
# --------------------------------------------------------------------------

def compute_target_states(events: list[dict]) -> dict[str, dict]:
    """target -> {state, iteration, rejected_count, job_ids, sources,
    last_ts, notes_history}. Pure function of the event list — this IS the
    view; nothing here is stored, everything is replayed."""
    by_target: dict[str, list[dict]] = {}
    for ev in events:
        t = ev.get("target")
        if t is None:
            continue
        by_target.setdefault(t, []).append(ev)

    out = {}
    for target, evs in by_target.items():
        evs = sorted(evs, key=lambda e: e.get("ts", 0))
        state = "unregistered"
        iteration = 0
        rejected_count = 0
        job_ids: list[str] = []
        sources: list[str] = []
        last_ts = None
        last_notes = None
        for ev in evs:
            last_ts = ev.get("ts", last_ts)
            kind = ev["event"]
            if kind == "registered":
                state = "registered"
                if ev.get("source"):
                    sources.append(ev["source"])
            elif kind == "queued":
                state = "queued"
                iteration = ev.get("iteration", iteration + 1)
                if ev.get("job_id"):
                    job_ids.append(ev["job_id"])
            elif kind == "generated":
                state = "generated"
            elif kind == "validated":
                # a daemon-internal fail just means "still needs another
                # attempt" — the next `queued` event (a fresh job_id, the
                # daemon's own unchanged internal retry) supersedes this;
                # it is never itself the owner-facing rejected-in-retry state.
                state = "awaiting_verdict" if ev.get("verdict") == "pass" else "generated"
            elif kind == "sheeted":
                state = "awaiting_verdict"
            elif kind == "verdict":
                result = ev.get("result")
                last_notes = ev.get("notes") or last_notes
                if result == "accepted":
                    state = "accepted"
                elif result == "rejected":
                    rejected_count += 1
                    state = ("parked_at_cap" if rejected_count >= PARK_AFTER_REJECTIONS
                              else "rejected_in_retry")
                elif result == "repurposed":
                    state = "repurposed"
            elif kind == "committed":
                state = "committed"
            elif kind == "deployed":
                state = "deployed"
        out[target] = {
            "state": state, "iteration": iteration, "rejected_count": rejected_count,
            "job_ids": job_ids, "sources": sources, "last_ts": last_ts,
            "last_notes": last_notes,
        }
    return out


# --------------------------------------------------------------------------
# spend — join onto throughput.jsonl by job_id (§2)
# --------------------------------------------------------------------------

def load_throughput(path: Path = common.DEFAULT_THROUGHPUT_LOG) -> dict[str, list[dict]]:
    """job_id -> list of completion rows (never the pre-flight `record:
    intent` marker rows, which carry no status/cost and would silently
    zero out a real job's join if included)."""
    if not path.is_file():
        return {}
    by_id: dict[str, list[dict]] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "status" not in row or "record" in row:
            continue
        jid = row.get("id")
        if jid:
            by_id.setdefault(jid, []).append(row)
    return by_id


def job_cost_usd(row: dict) -> tuple[float, bool]:
    """(dollars, fully_measured). `fully_measured` is False when a codex row
    has no usable meter pair — the dollar figure then only reflects
    `cost_usd` (usually 0 for codex) and must be reported UNMEASURED, not a
    silent undercount presented as a clean number."""
    dollars = 0.0
    measured = True
    mb, ma = row.get("meter_before"), row.get("meter_after")
    if row.get("channel") == "codex":
        pb = mb.get("secondary_used_percent") if isinstance(mb, dict) else None
        pa = ma.get("secondary_used_percent") if isinstance(ma, dict) else None
        if pb is not None and pa is not None:
            delta = max(0.0, pa - pb)  # clamp a window-reset wraparound to 0, not negative
            dollars += delta / 100.0 * WEEKLY_BUDGET_USD
        else:
            measured = False
    cost_usd = row.get("cost_usd")
    if cost_usd:  # Gemini's own reported cost — additive on top, never instead-of
        dollars += float(cost_usd)
    return dollars, measured


def target_spend(job_ids: list[str], throughput: dict[str, list[dict]]) -> dict:
    total = 0.0
    any_row = False
    fully_measured = True
    for jid in job_ids:
        for row in throughput.get(jid, []):
            any_row = True
            d, m = job_cost_usd(row)
            total += d
            fully_measured = fully_measured and m
    # `status` only tracks whether any spend row was found at all — a target
    # with a partially-measured row still reports "MEASURED" (the dollar
    # figure just becomes a floor, not the true total; see `note` below).
    status = "MEASURED" if any_row else "UNMEASURED"
    # any_row-but-not-fully_measured still reports the partial dollar figure,
    # tagged so the reader knows it may be a floor, not the true total.
    note = None if fully_measured or not any_row else \
        "partial: one or more codex rows had no usable meter pair"
    return {"usd": round(total, 4), "status": status, "note": note,
            "pct_weekly_window": round(total / WEEKLY_BUDGET_USD * 100, 2)}


# --------------------------------------------------------------------------
# backfill (§5) — seed from throughput.jsonl + done/failed manifests
# --------------------------------------------------------------------------

def _parse_iso_ts(s: str | None) -> float | None:
    """Job files stamp `created` as `%Y-%m-%dT%H:%M:%SZ` (UTC) — parsed with
    calendar.timegm, never time.mktime, so this doesn't silently shift by the
    host's local timezone offset."""
    if not s:
        return None
    try:
        import calendar
        return float(calendar.timegm(time.strptime(s, "%Y-%m-%dT%H:%M:%SZ")))
    except (ValueError, OverflowError):
        return None


def backfill(done_dir: Path = common.DEFAULT_DONE, failed_dir: Path = common.DEFAULT_FAILED,
             by: str = "backfill", dry_run: bool = False) -> dict:
    """Seeds registered+queued+generated+validated for every job manifest
    already sitting in done/ or failed/, tagged `source: backfill`. Honest
    about what it can and cannot know: a manifest only proves the DAEMON's
    own verdict (did it produce a validator-clean image), never an owner
    accept/reject — so backfill never fabricates `verdict`/`committed`
    events. Counts returned are MEASURED (this function counted the files
    itself, on this call, against the real directories passed in)."""
    manifests = []
    for d in (done_dir, failed_dir):
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.manifest.json")):
            job_path = d / (p.name[: -len(".manifest.json")] + ".json")
            if not job_path.is_file():
                continue
            manifests.append((job_path, p))

    existing = read_events()
    already_registered = {e["target"] for e in existing if e.get("event") == "registered"}
    already_queued_jobs = {e.get("job_id") for e in existing if e.get("event") == "queued"}

    targets_added, queued_added, generated_added, validated_added = 0, 0, 0, 0
    errors = []

    # Oldest first, by the job file's own `created` field where present, so
    # iteration numbers come out in a sane order.
    def _created_key(item):
        job_path, _m = item
        try:
            job = json.loads(job_path.read_text())
            return job.get("created") or ""
        except (OSError, ValueError):
            return ""

    for job_path, manifest_path in sorted(manifests, key=_created_key):
        try:
            job = json.loads(job_path.read_text())
            manifest = json.loads(manifest_path.read_text())
        except (OSError, ValueError) as exc:
            errors.append(f"{job_path}: {exc}")
            continue

        job_id = job.get("id", job_path.stem)
        if job_id in already_queued_jobs:
            continue  # already seeded (or genuinely live-registered) — never duplicate
        facing = job.get("facing")
        target = derive_target(job_id, facing)

        # already_registered/already_queued_jobs are updated identically in
        # both branches — dry-run must simulate the SAME dedup the real run
        # would apply (two manifests sharing a target, e.g. retries), or its
        # preview counts lie about what --apply will actually do.
        new_target = target not in already_registered
        already_registered.add(target)
        already_queued_jobs.add(job_id)
        if new_target:
            targets_added += 1
        queued_added += 1

        if dry_run:
            continue

        # Real historical time, not "now" — the job file's own `created`
        # stamp — so a burn-up chart or velocity projection built over
        # backfilled history isn't flattened onto the single moment this
        # command happened to run. Falls back to "now" only when a job file
        # predates the `created` field or is unparseable; generated/validated
        # get a monotonically later synthetic tick so they never precede
        # their own queued event.
        hist_ts = _parse_iso_ts(job.get("created")) or time.time()

        if new_target:
            record_registered(target, source="backfill", by=by, ts=hist_ts)
        record_queued(target, job_id, notes="", by=by, ts=hist_ts)

        elapsed_s = manifest.get("elapsed_s")
        record_generated(job_id, target=target, elapsed_s=elapsed_s, by=by,
                          ts=hist_ts + 1)
        generated_added += 1

        verdict = "pass" if manifest.get("status") == "ok" else "fail"
        record_validated(job_id, verdict, target=target, by=by,
                          ts=hist_ts + 1 + (elapsed_s or 1))
        validated_added += 1

    if dry_run:
        # apply always pairs exactly one generated+validated event with every
        # queued event — trivially knowable without writing anything.
        generated_added = validated_added = queued_added

    return {
        "manifests_scanned": {"value": len(manifests), "status": "MEASURED"},
        "targets_registered": {"value": targets_added, "status": "MEASURED"},
        "queued_events": {"value": queued_added, "status": "MEASURED"},
        "generated_events": {"value": generated_added, "status": "MEASURED"},
        "validated_events": {"value": validated_added, "status": "MEASURED"},
        "errors": errors,
        "dry_run": dry_run,
    }


# --------------------------------------------------------------------------
# fingerprint — content-based, per this repo's currency doctrine
# --------------------------------------------------------------------------

def fingerprint_file(path: Path) -> dict:
    if not path.is_file():
        return {"path": str(path), "exists": False}
    data = path.read_bytes()
    return {
        "path": str(path.relative_to(common.REPO_ROOT)),
        "exists": True,
        "sha256_12": hashlib.sha256(data).hexdigest()[:12],
        "bytes": len(data),
        "lines": data.count(b"\n"),
    }


# --------------------------------------------------------------------------
# status / render
# --------------------------------------------------------------------------

STATE_ORDER = ("registered", "queued", "generated", "awaiting_verdict", "accepted",
               "rejected_in_retry", "parked_at_cap", "repurposed", "committed",
               "deployed", "unregistered")


def build_status(target_filter: str | None = None) -> dict:
    events = read_events()
    states = compute_target_states(events)
    if target_filter:
        states = {t: v for t, v in states.items() if t == target_filter}
    throughput = load_throughput()

    counts = {s: 0 for s in STATE_ORDER}
    for v in states.values():
        counts[v["state"]] = counts.get(v["state"], 0) + 1

    parked = [{"target": t, "rejected_count": v["rejected_count"],
               "last_notes": v["last_notes"]}
              for t, v in states.items() if v["state"] == "parked_at_cap"]

    hist: dict[int, int] = {}
    for v in states.values():
        if v["iteration"]:
            hist[v["iteration"]] = hist.get(v["iteration"], 0) + 1

    per_target = {}
    total_usd, total_measured_any = 0.0, False
    accepted_or_committed = 0
    for t, v in states.items():
        spend = target_spend(v["job_ids"], throughput)
        per_target[t] = {**v, "spend": spend}
        if spend["status"] == "MEASURED":
            total_usd += spend["usd"]
            total_measured_any = True
        if v["state"] in ("accepted", "committed", "deployed"):
            accepted_or_committed += 1

    cost_per_accepted = None
    if accepted_or_committed:
        cost_per_accepted = round(total_usd / accepted_or_committed, 4)

    return {
        "generatedAt": _now_iso(),
        "sourceFingerprint": fingerprint_file(REGISTRY_PATH),
        "throughputFingerprint": fingerprint_file(common.DEFAULT_THROUGHPUT_LOG),
        "targetCount": len(states),
        "stateCounts": counts,
        "iterationsHistogram": hist,
        "parked": parked,
        "spend": {
            "totalUsd": round(total_usd, 4),
            "status": "MEASURED" if total_measured_any else "UNMEASURED",
            "pctWeeklyWindow": round(total_usd / WEEKLY_BUDGET_USD * 100, 2),
            "costPerAcceptedUsd": cost_per_accepted,
            "acceptedOrCommittedCount": accepted_or_committed,
        },
        "perTarget": per_target,
    }


def print_status(st: dict, verbose: bool = False) -> None:
    print(f"=== ART REGISTRY STATUS ({st['generatedAt']}) ===")
    print(f"targets: {st['targetCount']}")
    print("by state: " + " ".join(f"{k}={v}" for k, v in st["stateCounts"].items() if v))
    if st["iterationsHistogram"]:
        hist = ", ".join(f"{k}:{v}" for k, v in sorted(st["iterationsHistogram"].items()))
        print(f"iterations histogram: {hist}")
    sp = st["spend"]
    note = "" if sp["status"] == "MEASURED" or sp["totalUsd"] == 0 else " (UNMEASURED)"
    print(f"spend: ${sp['totalUsd']:.4f}{note} = {sp['pctWeeklyWindow']}% of "
          f"${WEEKLY_BUDGET_USD:.0f} weekly window [{sp['status']}]")
    if sp["costPerAcceptedUsd"] is not None:
        print(f"cost per accepted image: ${sp['costPerAcceptedUsd']:.4f} "
              f"({sp['acceptedOrCommittedCount']} accepted/committed) [MEASURED]")
    else:
        print("cost per accepted image: UNMEASURED (no accepted/committed targets yet)")
    if st["parked"]:
        print(f"PARKED / escalation list ({len(st['parked'])}):")
        for p in st["parked"]:
            print(f"  - {p['target']}  rejected={p['rejected_count']}x  "
                  f"notes={p['last_notes']!r}")
    if verbose:
        print("per-target:")
        for t, v in sorted(st["perTarget"].items()):
            print(f"  {t:40s} state={v['state']:18s} iter={v['iteration']} "
                  f"rejected={v['rejected_count']} spend=${v['spend']['usd']:.4f}"
                  f"[{v['spend']['status']}]")


# --------------------------------------------------------------------------
# render — burn-up + histogram + parked list + projection, HTML + JSON
# --------------------------------------------------------------------------

def _svg_burnup(events: list[dict], width=760, height=280) -> str:
    reg_events = sorted([e for e in events if e.get("event") == "registered"],
                         key=lambda e: e.get("ts", 0))
    com_events = sorted([e for e in events if e.get("event") == "committed"],
                         key=lambda e: e.get("ts", 0))
    if not reg_events:
        return "<p>no registered events yet — nothing to chart</p>"

    all_ts = [e.get("ts", 0) for e in reg_events + com_events]
    t0, t1 = min(all_ts), max(all_ts)
    span = max(t1 - t0, 1.0)

    def x_of(ts):
        return 50 + (ts - t0) / span * (width - 90)

    scope_pts, seen_targets = [], set()
    cum = 0
    for e in reg_events:
        # a target re-registered (repurpose reopen) still only counts once
        # toward SCOPE — it was already part of the scope, just reopened.
        if e["target"] not in seen_targets:
            seen_targets.add(e["target"])
            cum += 1
        scope_pts.append((e.get("ts", 0), cum, e.get("source", "")))

    committed_targets = set()
    committed_pts = []
    cum_c = 0
    for e in com_events:
        if e["target"] not in committed_targets:
            committed_targets.add(e["target"])
            cum_c += 1
        committed_pts.append((e.get("ts", 0), cum_c))

    max_y = max([p[1] for p in scope_pts] + [p[1] for p in committed_pts] + [1])

    def y_of(v):
        return height - 40 - (v / max_y) * (height - 70)

    def path_of(pts):
        if not pts:
            return ""
        d = f"M {x_of(t0):.1f} {y_of(0):.1f}"
        prev_v = 0
        for ts, v, *_ in pts:
            d += f" L {x_of(ts):.1f} {y_of(prev_v):.1f} L {x_of(ts):.1f} {y_of(v):.1f}"
            prev_v = v
        d += f" L {x_of(t1):.1f} {y_of(prev_v):.1f}"
        return d

    labels = []
    for ts, v, source in scope_pts:
        if source:
            labels.append(
                f'<text x="{x_of(ts):.1f}" y="{y_of(v) - 6:.1f}" font-size="9" '
                f'fill="#d8c3a5" text-anchor="middle">{_esc(source)[:22]}</text>')

    svg = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
           f'style="background:#241a12;border-radius:8px">']
    svg.append(f'<line x1="50" y1="{height-40}" x2="{width-40}" y2="{height-40}" '
               f'stroke="#7a624a"/>')
    svg.append(f'<line x1="50" y1="20" x2="50" y2="{height-40}" stroke="#7a624a"/>')
    svg.append(f'<text x="10" y="20" font-size="10" fill="#d8c3a5">{max_y}</text>')
    svg.append(f'<text x="10" y="{height-40}" font-size="10" fill="#d8c3a5">0</text>')
    svg.append(f'<path d="{path_of(scope_pts)}" fill="none" stroke="#e8a33d" stroke-width="2"/>')
    if committed_pts:
        svg.append(f'<path d="{path_of(committed_pts)}" fill="none" stroke="#5fb87a" '
                   f'stroke-width="2"/>')
    svg.extend(labels)
    svg.append(f'<text x="{width-190}" y="20" font-size="11" fill="#e8a33d">'
               f'─ scope (registered)</text>')
    svg.append(f'<text x="{width-190}" y="36" font-size="11" fill="#5fb87a">'
               f'─ committed (done)</text>')
    svg.append("</svg>")
    return "\n".join(svg)


def _svg_hist(hist: dict[int, int], width=380, height=200) -> str:
    if not hist:
        return "<p>no iterations recorded yet</p>"
    items = sorted(hist.items())
    max_v = max(v for _, v in items)
    bar_w = (width - 60) / max(len(items), 1)
    svg = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
           f'style="background:#241a12;border-radius:8px">']
    for i, (k, v) in enumerate(items):
        h = (v / max_v) * (height - 50)
        x = 40 + i * bar_w
        y = height - 30 - h
        svg.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w*0.7:.1f}" height="{h:.1f}" '
                   f'fill="#e8a33d"/>')
        svg.append(f'<text x="{x + bar_w*0.35:.1f}" y="{height-14}" font-size="10" '
                   f'fill="#d8c3a5" text-anchor="middle">{k}</text>')
        svg.append(f'<text x="{x + bar_w*0.35:.1f}" y="{y-4:.1f}" font-size="10" '
                   f'fill="#d8c3a5" text-anchor="middle">{v}</text>')
    svg.append("</svg>")
    return "\n".join(svg)


def _esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def compute_projection(events: list[dict], st: dict) -> dict:
    reg_events = [e for e in events if e.get("event") == "registered"]
    com_events = [e for e in events if e.get("event") == "committed"]
    if not reg_events:
        return {"status": "UNMEASURED", "note": "no registered events"}
    t0 = min(e.get("ts", 0) for e in reg_events)
    now = time.time()
    days = max((now - t0) / 86400.0, 1e-6)
    committed_targets = {e["target"] for e in com_events}
    velocity = len(committed_targets) / days  # targets committed per day
    total_targets = st["targetCount"]
    remaining = max(total_targets - len(committed_targets), 0)
    if velocity <= 0 or len(committed_targets) == 0:
        return {"status": "UNMEASURED",
                "note": "no committed targets yet — no velocity to project from",
                "remaining": remaining, "totalTargets": total_targets}
    days_to_finish = remaining / velocity
    return {"status": "MEASURED", "velocityPerDay": round(velocity, 3),
            "remaining": remaining, "totalTargets": total_targets,
            "committed": len(committed_targets),
            "daysToFinishCurrentScope": round(days_to_finish, 1),
            "measuredOverDays": round(days, 2)}


def render(out_html: Path = ART_STATUS_HTML, out_json: Path = ART_STATUS_JSON) -> dict:
    events = read_events()
    st = build_status()
    projection = compute_projection(events, st)
    payload = {**st, "projection": projection}

    common.atomic_write_json(out_json, payload)

    parked_rows = "".join(
        f"<tr><td>{_esc(p['target'])}</td><td>{p['rejected_count']}</td>"
        f"<td>{_esc(p['last_notes'] or '')}</td></tr>" for p in st["parked"]) or \
        "<tr><td colspan=3>none</td></tr>"

    proj_line = ("UNMEASURED — " + projection.get("note", "")) if projection["status"] == "UNMEASURED" \
        else (f"MEASURED: {projection['velocityPerDay']} targets/day over "
              f"{projection['measuredOverDays']}d → {projection['remaining']} remaining "
              f"of {projection['totalTargets']} ≈ {projection['daysToFinishCurrentScope']} "
              f"days to finish CURRENT scope")

    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Art Regen Registry Status</title>
<style>
body{{background:#1b130d;color:#e8dcc8;font-family:system-ui,sans-serif;padding:24px;
      max-width:900px;margin:auto}}
h1,h2{{color:#e8a33d}}
table{{border-collapse:collapse;width:100%;margin:8px 0}}
td,th{{border:1px solid #4a3a2a;padding:4px 8px;text-align:left;font-size:13px}}
.fresh{{color:#9a8770;font-size:12px}}
.row{{display:flex;gap:24px;flex-wrap:wrap}}
</style></head><body>
<h1>Art Regen Registry</h1>
<p class="fresh">generatedAt {st['generatedAt']} — source registry {st['sourceFingerprint'].get('sha256_12','?')}
 ({st['sourceFingerprint'].get('lines','?')} lines) — throughput
 {st['throughputFingerprint'].get('sha256_12','?')} ({st['throughputFingerprint'].get('lines','?')} lines)</p>

<h2>Burn-up (scope vs committed)</h2>
{_svg_burnup(events)}

<h2>State counts</h2>
<table><tr>{"".join(f"<th>{k}</th>" for k, v in st['stateCounts'].items() if v)}</tr>
<tr>{"".join(f"<td>{v}</td>" for k, v in st['stateCounts'].items() if v)}</tr></table>

<div class="row">
<div><h2>Iterations histogram</h2>{_svg_hist(st['iterationsHistogram'])}</div>
<div><h2>Spend</h2>
<p>${st['spend']['totalUsd']:.4f} [{st['spend']['status']}] =
 {st['spend']['pctWeeklyWindow']}% of ${WEEKLY_BUDGET_USD:.0f} weekly window</p>
<p>cost / accepted image: {"$%.4f" % st['spend']['costPerAcceptedUsd'] if st['spend']['costPerAcceptedUsd'] is not None else "UNMEASURED"}</p>
</div>
</div>

<h2>Parked / escalation list (rejected ≥ {PARK_AFTER_REJECTIONS}x)</h2>
<table><tr><th>target</th><th>rejected</th><th>last notes</th></tr>{parked_rows}</table>

<h2>Projection</h2>
<p>{_esc(proj_line)}</p>
</body></html>"""
    out_html.write_text(html)
    return {"html": str(out_html), "json": str(out_json), "payload": payload}


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _add_common(ap):
    ap.add_argument("--by", default="unknown", help="seat/script identity recording this event")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("register"); _add_common(p)
    p.add_argument("--target", required=True)
    p.add_argument("--source", required=True)

    p = sub.add_parser("queued"); _add_common(p)
    p.add_argument("--target", required=True)
    p.add_argument("--job-id", required=True)
    p.add_argument("--notes", default="")

    p = sub.add_parser("generated"); _add_common(p)
    p.add_argument("--job-id", required=True)
    p.add_argument("--target")
    p.add_argument("--elapsed-s", type=float)

    p = sub.add_parser("validated"); _add_common(p)
    p.add_argument("--job-id", required=True)
    p.add_argument("--target")
    p.add_argument("--verdict", required=True, choices=("pass", "fail"))

    p = sub.add_parser("sheeted"); _add_common(p)
    p.add_argument("--target", required=True)
    p.add_argument("--sheet", required=True)

    p = sub.add_parser("verdict"); _add_common(p)
    p.add_argument("--target", required=True)
    p.add_argument("--result", required=True, choices=("accepted", "rejected", "repurposed"))
    p.add_argument("--notes", default="")
    p.add_argument("--as-target")
    p.add_argument("--job-id")

    p = sub.add_parser("committed"); _add_common(p)
    p.add_argument("--target", required=True)
    p.add_argument("--repo-path", required=True)
    p.add_argument("--sha", required=True)

    p = sub.add_parser("deployed"); _add_common(p)
    p.add_argument("--target", required=True)

    p = sub.add_parser("backfill")
    p.add_argument("--done-dir", type=Path, default=common.DEFAULT_DONE)
    p.add_argument("--failed-dir", type=Path, default=common.DEFAULT_FAILED)
    p.add_argument("--by", default="backfill")
    p.add_argument("--dry-run", action="store_true")

    p = sub.add_parser("render")
    p.add_argument("--out-html", type=Path, default=ART_STATUS_HTML)
    p.add_argument("--out-json", type=Path, default=ART_STATUS_JSON)

    p = sub.add_parser("status")
    p.add_argument("--target")
    p.add_argument("--json", action="store_true")
    p.add_argument("-v", "--verbose", action="store_true")

    args = ap.parse_args(argv)

    try:
        if args.cmd == "register":
            ev = record_registered(args.target, args.source, by=args.by)
            print(json.dumps(ev))
        elif args.cmd == "queued":
            ev = record_queued(args.target, args.job_id, notes=args.notes, by=args.by)
            print(json.dumps(ev))
        elif args.cmd == "generated":
            ev = record_generated(args.job_id, target=args.target,
                                   elapsed_s=args.elapsed_s, by=args.by)
            print(json.dumps(ev))
        elif args.cmd == "validated":
            ev = record_validated(args.job_id, args.verdict, target=args.target, by=args.by)
            print(json.dumps(ev))
        elif args.cmd == "sheeted":
            ev = record_sheeted(args.target, args.sheet, by=args.by)
            print(json.dumps(ev))
        elif args.cmd == "verdict":
            evs = record_verdict(args.target, args.result, notes=args.notes,
                                  as_target=args.as_target, job_id=args.job_id, by=args.by)
            for e in evs:
                print(json.dumps(e))
        elif args.cmd == "committed":
            ev = record_committed(args.target, args.repo_path, args.sha, by=args.by)
            print(json.dumps(ev))
        elif args.cmd == "deployed":
            ev = record_deployed(args.target, by=args.by)
            print(json.dumps(ev))
        elif args.cmd == "backfill":
            result = backfill(args.done_dir, args.failed_dir, by=args.by, dry_run=args.dry_run)
            print(json.dumps(result, indent=2))
            if result["errors"]:
                return 1
        elif args.cmd == "render":
            result = render(args.out_html, args.out_json)
            print(f"wrote {result['html']}")
            print(f"wrote {result['json']}")
        elif args.cmd == "status":
            st = build_status(args.target)
            if args.json:
                print(json.dumps(st, indent=2))
            else:
                print_status(st, verbose=args.verbose)
    except RegError as exc:
        print(f"artreg: ERROR {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
