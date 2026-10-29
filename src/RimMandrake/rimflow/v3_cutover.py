#!/usr/bin/env python3
"""v3 cutover: BENCH's lane goes to FOUNDRY (V3_CUTOVER_MIGRATE_BENCH_LANE_TO_FOUNDRY).

Owner, 2026-10-28 17:00 PDT: "Once we switch over to Conductor + ispatch + Foundry, all bench
items get reassigned to Dispatch-> Foundry". Design of record: design/RimMandrake/rimflow_v3_2026-10-26.md
§2 — there is no BENCH seat in v3; the Conductor absorbs Bench and works only in live sessions with
him; FOUNDRY is the one autonomous builder.

    python3 src/RimMandrake/rimflow/v3_cutover.py plan
    python3 src/RimMandrake/rimflow/v3_cutover.py apply --owner-said "<his words>" [--why ..] [--commit]
    python3 src/RimMandrake/rimflow/v3_cutover.py revert (--owner-said "<his words>" | --why "..") [--commit]

Run it at the switch, when no BENCH window is working: classification reads the ledger once, so a lease a
BENCH window takes DURING the batch is not seen (a reassign revokes it).

RULE (printed by `plan`): every open BENCH-owned item is reassigned to FOUNDRY, EXCEPT
  keep  - it needs him live: needs=owner, or the next acceptance level owed is L4 (his in-person look);
        - the cutover item itself (BENCH runs it and closes it);
  defer - it is under a LIVE lease right now (a BENCH window is mid-work on it). `apply` is idempotent:
          run it again once the lease ends and the item moves.

`apply` writes, in order and only after every precondition passed (his words are an instruction, the
staged docs patch applies): one `reassign --to FOUNDRY` event per item through rimflow's own
check/stamp/append (seat OWNER, `ownerSaid` = his words), the FlowWorks/GSS lane seat flipped to
FOUNDRY (the lane file stays as data), the staged docs patch, and record.json naming everything it
did. `revert` reads record.json and undoes exactly that. Neither ever hand-edits the ledger.
"""
import argparse
import contextlib
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from rimflow import model  # noqa: E402
from rimflow import cli  # noqa: E402
from rimflow import priority  # noqa: E402

CUTOVER_ITEM = "V3_CUTOVER_MIGRATE_BENCH_LANE_TO_FOUNDRY"
FROM_SEAT, TO_SEAT = "BENCH", "FOUNDRY"
STATE_DIR = os.path.join(model.ROOT, "infrastructure", "state", "v3_cutover")
RULE = ("RULE: every open BENCH-owned item moves to FOUNDRY (v3 design §2: no BENCH seat; the Conductor "
        "keeps only live sessions with him). KEEP only what needs him live: needs=owner, or next "
        "acceptance level L4; plus %s itself. DEFER an item under a live lease (re-run apply after it "
        "ends)." % CUTOVER_ITEM)


class Paths(object):
    def __init__(self, lane=None, patch=None, record=None, repo=None):
        self.lane = lane or priority.FLOWWORKS_LANE_FILE
        self.patch = patch or os.path.join(STATE_DIR, "docs.patch")
        self.record = record or os.path.join(STATE_DIR, "record.json")
        self.repo = repo or model.ROOT


def classify(world, now):
    """-> {"move": [item], "keep": [(item, why)], "defer": [(item, why)]} over open BENCH items."""
    out = {"move": [], "keep": [], "defer": []}
    for it in sorted(world.items.values(), key=lambda i: i.id):
        if it.owner != FROM_SEAT or it.state not in model.OPEN_STATES:
            continue
        lvl = it.next_level() if it.state in ("built", "validated") else None
        if it.id == CUTOVER_ITEM:
            out["keep"].append((it, "the cutover item (BENCH runs it tonight)"))
        elif it.needs == "owner":
            out["keep"].append((it, "needs=owner (he must act, live)"))
        elif lvl == "L4":
            out["keep"].append((it, "next level L4 (his in-person acceptance)"))
        elif model.lease_status(it, now) == "live":
            out["defer"].append((it, "live lease until %s" % (it.lease or {}).get("expires")))
        else:
            out["move"].append(it)
    return out


def _git(args, cwd):
    return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)


def patch_status(paths):
    """-> (ok_to_apply, "applies cleanly" | "already applied" | "DOES NOT APPLY: ..." | "no patch")."""
    if not os.path.exists(paths.patch):
        return True, "no patch"
    fwd = _git(["apply", "--check", paths.patch], paths.repo)
    if fwd.returncode == 0:
        return True, "applies cleanly"
    if _git(["apply", "--check", "-R", paths.patch], paths.repo).returncode == 0:
        return True, "already applied"
    return False, "DOES NOT APPLY: " + (fwd.stderr.strip().splitlines() or ["?"])[0]


def patch_files(paths):
    if not os.path.exists(paths.patch):
        return []
    return sorted({l[6:].strip() for l in open(paths.patch) if l.startswith("+++ b/")})


def read_record(paths):
    try:
        return json.load(open(paths.record))
    except (OSError, ValueError):
        return None


def lane_seat(paths):
    return json.load(open(paths.lane)).get("seat")


def _set_lane_seat(paths, seat):
    """Rewrite only the `seat` value, keeping the file's text (and every pattern) as it is."""
    text = open(paths.lane).read()
    new, n = re.subn(r'("seat"\s*:\s*)"[A-Z]+"', r'\1"%s"' % seat, text, count=1)
    if n != 1:
        raise SystemExit("refused: no \"seat\" field in %s" % paths.lane)
    with open(paths.lane, "w") as fh:
        fh.write(new)


def _world():
    return model.replay(model.read())


def plan_text(paths, now):
    w = _world()
    r = classify(w, now)
    ok, pst = patch_status(paths)
    rec = read_record(paths)
    lines = [RULE, "",
             "move %d   keep %d   defer %d   (open BENCH items %d)" % (
                 len(r["move"]), len(r["keep"]), len(r["defer"]),
                 len(r["move"]) + len(r["keep"]) + len(r["defer"])),
             "lane seat now: %s -> %s after apply" % (lane_seat(paths), TO_SEAT),
             "docs patch: %s (%s)" % (pst, ", ".join(patch_files(paths)) or "-"),
             "record: %s" % ((rec or {}).get("state") or "none (never applied)"), ""]
    for name in ("keep", "defer"):
        lines.append("== %s (%d)" % (name.upper(), len(r[name])))
        lines += ["  %-48s %-9s %s" % (i.id, i.state, why) for i, why in r[name]]
        lines.append("")
    lines.append("== MOVE to FOUNDRY (%d)" % len(r["move"]))
    lines += ["  %-48s %-9s %s%s" % (i.id, i.state, i.kind or "-", " BLOCKED" if i.blocked else "")
              for i in r["move"]]
    return "\n".join(lines) + "\n"


def _provenance(owner_said, why):
    model.OWNER_SAID = owner_said or ""
    model.AGENT_WHY = why or ""


def _reassign_all(ids, to, seat, reason, world):
    """One checked `reassign` per id, through rimflow's own writer path; world kept current."""
    done = []
    for iid in ids:
        ev = {"seat": seat, "event": "reassign", "id": iid, "to": to, "reason": reason, "ts": model.now()}
        model.check(ev, world)
        with contextlib.redirect_stderr(io.StringIO()):
            cli._stamp_owner_and_override(ev)
        model.append(ev)
        model._apply(ev, 0, world, False)
        done.append(iid)
    return done


def _note(seat, text):
    ev = {"seat": seat, "event": "note", "id": CUTOVER_ITEM, "text": text, "ts": model.now()}
    try:
        model.check(ev)
    except model.LedgerError:
        return                          # the item is not in this ledger (a test ledger): nothing to note on
    with contextlib.redirect_stderr(io.StringIO()):
        cli._stamp_owner_and_override(ev)
    model.append(ev)


def _write_record(paths, rec):
    os.makedirs(os.path.dirname(paths.record) or ".", exist_ok=True)
    with open(paths.record, "w") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)
        fh.write("\n")


def _said_ok(said):
    try:
        cli._check_owner_said(said)
    except SystemExit:
        return False
    return True


def _commit(paths, seat, msg):
    files = [model.shard_path(seat), paths.lane, paths.record] + [
        os.path.join(paths.repo, f) for f in patch_files(paths)]
    files = [f for f in files if os.path.exists(f)]
    r = _git(["add", "--"] + files, paths.repo)
    if r.returncode == 0:
        r = _git(["commit", "-m", msg, "--"] + files, paths.repo)
    sys.stdout.write(r.stdout + r.stderr)
    print("now: ./publish")
    return r.returncode


def _merge_record(rec, **kw):
    rec = dict(rec or {})
    rec.update(kw)
    return rec


def apply(paths, owner_said, why, now, commit=False):
    """Every precondition first; then the record is written as a JOURNAL before any other write (state
    "applying", the lane seat and docs state it found), extended with each id as it moves, and set "applied"
    last — so a failure part-way leaves revert everything it needs, and a re-run resumes from it."""
    if not owner_said or not _said_ok(owner_said):
        print("refused: apply needs --owner-said quoting his INSTRUCTION (not a question)", file=sys.stderr)
        return 2
    ok, pst = patch_status(paths)
    if not ok:
        print("refused before any write: docs patch %s" % pst, file=sys.stderr)
        return 3
    prior = read_record(paths) or {}
    if prior.get("state") not in (None, "applying", "applied", "reverted"):
        print("refused: record state %r" % prior.get("state"), file=sys.stderr)
        return 2
    resuming = prior.get("state") in ("applying", "applied")
    w = _world()
    r = classify(w, now)
    ids = [i.id for i in r["move"]]
    lane_now = lane_seat(paths)
    if resuming and not ids and lane_now == TO_SEAT and pst != "applies cleanly" and prior["state"] == "applied":
        print("nothing to do: cutover already applied; move 0, keep %d, defer %d" % (len(r["keep"]), len(r["defer"])))
        return _commit(paths, "OWNER", "v3 cutover: record (%s)" % CUTOVER_ITEM) if commit else 0
    rec = _merge_record(
        prior if resuming else {}, state="applying", item=CUTOVER_ITEM, ownerSaid=owner_said, why=why or "",
        moved=list(prior.get("moved", [])) if resuming else [],
        lane_seat_before=prior.get("lane_seat_before", lane_now) if resuming else lane_now,
        docs_patched_by_cutover=bool(prior.get("docs_patched_by_cutover")) if resuming else False,
        docs_patch=os.path.relpath(paths.patch, paths.repo), docs_files=patch_files(paths),
        kept=[i.id for i, _ in r["keep"]], deferred=[i.id for i, _ in r["defer"]])
    _write_record(paths, rec)
    moved = []
    _provenance(owner_said, why)
    try:
        for iid in ids:
            _reassign_all([iid], TO_SEAT, "OWNER", "v3 cutover: BENCH lane -> FOUNDRY", w)
            moved.append(iid)
    finally:
        _provenance("", "")
        rec["moved"] = sorted(set(rec["moved"]) | set(moved))
        _write_record(paths, rec)
    w2 = _world()
    wrong = [i for i in moved if w2.items[i].owner != TO_SEAT]
    if wrong:
        print("FAILED: %d item(s) not owned by FOUNDRY after reassign: %s" % (len(wrong), wrong[:5]), file=sys.stderr)
        return 4
    if lane_now != TO_SEAT:
        _set_lane_seat(paths, TO_SEAT)
    if pst == "applies cleanly":
        res = _git(["apply", paths.patch], paths.repo)
        if res.returncode != 0:
            print("FAILED applying docs patch after the ledger moved (record stays 'applying'; fix and re-run): %s"
                  % res.stderr, file=sys.stderr)
            return 5
        rec["docs_patched_by_cutover"] = True
    rec.update(state="applied", applied_at=model.now(),
               runs=rec.get("runs", []) + [{"at": model.now(), "moved": len(moved)}])
    _write_record(paths, rec)
    _provenance(owner_said, why)
    try:
        _note("OWNER", "v3 cutover applied: moved %d BENCH items to FOUNDRY (keep %d, defer %d); lane seat "
              "FOUNDRY; docs patch %s. Record: infrastructure/state/v3_cutover/record.json" % (
                  len(moved), len(r["keep"]), len(r["defer"]), "landed" if pst == "applies cleanly" else pst))
    finally:
        _provenance("", "")
    print("applied: moved %d, keep %d, defer %d; lane seat %s -> %s; docs patch %s" % (
        len(moved), len(r["keep"]), len(r["defer"]), lane_now, TO_SEAT,
        "landed" if pst == "applies cleanly" else pst))
    if r["defer"]:
        print("deferred (re-run apply when their lease ends): " + ", ".join(i.id for i, _ in r["defer"]))
    if commit:
        return _commit(paths, "OWNER", "v3 cutover: BENCH lane -> FOUNDRY (%s)\n\nmoved %d items; record "
                       "infrastructure/state/v3_cutover/record.json" % (CUTOVER_ITEM, len(moved)))
    print("not committed: re-run with --commit, or commit the OWNER shard, lane file, record and docs by "
          "explicit path; then ./publish")
    return 0


def revert(paths, owner_said, why, now, commit=False):
    """Undo from the record. Preflight (record, words, docs reversible) before any write; items still under a
    live lease stay listed as `revert_pending` (state "reverting") so a later revert finishes them."""
    rec = read_record(paths)
    if not rec or rec.get("state") not in ("applied", "applying", "reverting"):
        print("refused: no applied cutover in %s" % paths.record, file=sys.stderr)
        return 2
    if owner_said and not _said_ok(owner_said):
        print("refused: --owner-said must quote an instruction", file=sys.stderr)
        return 2
    if not owner_said and not why:
        print("refused: revert needs --owner-said or --why", file=sys.stderr)
        return 2
    ok, pst = patch_status(paths)
    undo_docs = bool(rec.get("docs_patched_by_cutover")) and pst != "applies cleanly"
    if undo_docs and pst != "already applied":
        print("refused before any write: the docs patch cannot be reversed (%s); fix the docs first" % pst,
              file=sys.stderr)
        return 3
    seat = "OWNER" if owner_said else FROM_SEAT
    w = _world()
    back, skipped = [], []
    todo = rec.get("revert_pending") if rec.get("state") == "reverting" else rec.get("moved", [])
    for iid in todo or []:
        it = w.items.get(iid)
        if it is None or it.owner != TO_SEAT or it.state not in model.OPEN_STATES:
            continue
        (skipped if model.lease_status(it, now) == "live" else back).append(iid)
    rec.update(state="reverting", revert_pending=sorted(set(back) | set(skipped)))
    _write_record(paths, rec)
    done = []
    _provenance(owner_said, why)
    try:
        for iid in back:
            _reassign_all([iid], FROM_SEAT, seat, "v3 cutover reverted", w)
            done.append(iid)
    finally:
        _provenance("", "")
        rec["revert_pending"] = sorted(set(rec["revert_pending"]) - set(done))
        rec["reverted_back"] = sorted(set(rec.get("reverted_back", [])) | set(done))
        _write_record(paths, rec)
    lane_before = rec.get("lane_seat_before") or FROM_SEAT
    if lane_seat(paths) != lane_before:
        _set_lane_seat(paths, lane_before)
    if undo_docs:
        res = _git(["apply", "-R", paths.patch], paths.repo)
        if res.returncode != 0:
            print("FAILED reversing docs patch: %s" % res.stderr, file=sys.stderr)
            return 5
        rec["docs_patched_by_cutover"] = False
    rec.update(state="reverting" if rec["revert_pending"] else "reverted", reverted_at=model.now(),
               revert_said=owner_said or "", revert_why=why or "")
    _write_record(paths, rec)
    print("revert: %d item(s) back to BENCH; %d still pending (live lease: %s; run revert again later); lane "
          "seat %s; docs %s" % (len(done), len(rec["revert_pending"]), ", ".join(rec["revert_pending"]) or "-",
                                lane_before, "restored" if undo_docs else "untouched (not patched by the cutover)"))
    if commit:
        return _commit(paths, seat, "v3 cutover reverted (%s)" % CUTOVER_ITEM)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--out")
    for name in ("apply", "revert"):
        s = sub.add_parser(name)
        s.add_argument("--owner-said")
        s.add_argument("--why")
        s.add_argument("--commit", action="store_true")
    a = ap.parse_args(argv)
    cli._bind_paths()
    paths, now = Paths(), model.epoch_now()
    if a.cmd == "plan":
        txt = plan_text(paths, now)
        if a.out:
            with open(a.out, "w") as fh:
                fh.write(txt)
        sys.stdout.write(txt if not a.out else txt.split("\n== KEEP")[0] + "\n(full list: %s)\n" % a.out)
        return 0
    if a.cmd == "apply":
        return apply(paths, a.owner_said, a.why, now, commit=a.commit)
    return revert(paths, a.owner_said, a.why, now, commit=a.commit)


if __name__ == "__main__":
    sys.exit(main())
