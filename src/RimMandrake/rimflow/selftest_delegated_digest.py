#!/usr/bin/env python3
"""selftest_delegated_digest.py — the daily digest of delegated calls (delegated_digest.py, DELEGATED_DIGEST_FIX_NEVER_WRITTEN).

  blind     an account id, an account name, a token figure, a cap, a cost and an extra field are injected into every
            source (ledger event, judge verdict, art install, leftovers act, marks line); none reaches the page. The
            detector is first shown to see each planted value in the RAW records (a clean page means the digest
            dropped them, not that the detector is blind).
  counts    the counts are the records in the window, by class and by source; out-of-window and lease events are out
  window    --dry-run never moves the state; a real run does; a second run the same date does nothing
  zero      a window with no call says how many the sources see in all time (policy §5), never a bare zero
  prelaunch a raising build under --pre-launch exits 0 and writes the FAILED note; without it, it raises
  real      a dry run over the real records completes and its page passes the detector (instrument sanity: >0 ledger
            delegated events exist in all time)
Writes only under a temp dir.
"""
import datetime as dt
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import delegated_digest as D  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


# planted values: each must never appear on a page
PLANTS = ["OPS_ACCOUNT_DRAIN_C01D", "steven", "45,000 tokens", "93%", "80k", "$0.34", "cost_usd", "0.3366",
          "acct-7f3e9", "54321", "LUKAS_93_WEEK_DRAIN", "sk-live-zz9"]
# an independent detector (no code shared with blind_view): unit numbers, $ figures, big bare numbers
_UNIT = re.compile(r"(?<![A-Za-z0-9_])\$?\d+(?:[.,]\d+)*\s?(?:[kKM]|%|tokens?)(?![A-Za-z0-9])|\$\s?\d")
_BIG = re.compile(r"(?<![A-Za-z0-9_\-:./\\])\d{1,3}(?:,\d{3})+(?![\d])|(?<![A-Za-z0-9_\-:./\\])\d{5,}(?![A-Za-z0-9_\-:])")


def leaks(text):
    found = [p for p in PLANTS if p.lower() in text.lower()]
    found += ["unit:" + m.group() for m in _UNIT.finditer(text)]
    found += ["big:" + m.group() for m in _BIG.finditer(text)]
    return found


T0 = dt.datetime(2026, 10, 27, 0, 0, tzinfo=dt.timezone.utc)
SINCE = T0
CUT = T0 + dt.timedelta(hours=20)


def ts(h):
    return (T0 + dt.timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ")


EVENTS = [
    {"seat": "BENCH", "event": "close", "id": "PIPE_ELBOW_FIX_SEAM_JOGS", "sha": "abcdef1234567",
     "why": "delegated: art geometric correction — seams moved 2px; steven's account 93% of week cap, 45,000 tokens",
     "ts": ts(3), "account_id": "acct-7f3e9", "cost_usd": 0.3366},
    {"seat": "BENCH", "event": "note", "id": "PIPE_ELBOW_FIX_SEAM_JOGS", "text": "judge KEEP; run cost $0.34 at 80k",
     "why": "delegated: art geometric correction", "ts": ts(4)},
    {"seat": "BENCH", "event": "lease", "id": "PIPE_ELBOW_FIX_SEAM_JOGS", "why": "delegated: art geometric correction",
     "ts": ts(4)},
    {"seat": "FOUNDRY", "event": "close", "id": "OPS_ACCOUNT_DRAIN_C01D", "sha": "1111111", "why": "delegated: scope",
     "ts": ts(5)},
    {"seat": "BENCH", "event": "file", "id": "BIOME_DECIDE_TWO_ROUTES", "title": "pick route B over LUKAS_93_WEEK_DRAIN",
     "why": "delegated: scope", "ts": ts(6), "tokens": 54321},
    {"seat": "OWNER", "event": "game", "state": "DOWN", "ranBy": "BENCH", "ts": ts(7),
     "why": "delegated: bridge idle — deploy [owner idle 33 min (need 20)] key sk-live-zz9"},
    {"seat": "BENCH", "event": "bridge", "state": "taken", "why": "delegated: bridge idle (owner idle 50 min)",
     "idleProbe": "state=MEASURED idle_seconds=3022", "purpose": "r12", "ts": ts(7)},
    {"seat": "BENCH", "event": "note", "id": "BIOME_DECIDE_TWO_ROUTES", "text": "x", "why": "delegated: scope",
     "ts": ts(-30)},                                                   # before the window
    {"seat": "BENCH", "event": "note", "id": "BIOME_DECIDE_TWO_ROUTES", "text": "x", "why": "not delegated",
     "ts": ts(8)},
]
ART_EVENTS = [
    {"type": "live", "ts": "2026-10-27T05:00:00-0700", "seat": "FOUNDRY", "mod": "src/RimMandrake/LeaningScrub",
     "rel": "Things/RM_Shirrel_north.png", "sha": "262180890bc9f3", "cost_usd": 0.3366,
     "why": "delegated: art infrastructure/state/delegated/2026-10-27/RM_Shirrel.json"},
    {"type": "live", "ts": "2026-10-27T05:00:00-0700", "why": "delegated: art marks", "mod": "m", "rel": "r"},
]
MARKS = ["art marks | installed over an older keep 0123456789ab at M/r.png | mark: sheet s row 3 at 2026-10-27 "
         "| steven 45,000 tokens"]


def make_world(tmp, untracked_time):
    ddir = os.path.join(tmp, "infrastructure", "state", "delegated", "2026-10-27")
    os.makedirs(ddir)
    art = {"subject": "RM_Shirrel", "decision": "ACCEPT", "image_sha256": {"a": "b"}, "reasons": ["steven 93%"],
           "judge_model": {"opus": [{"cost_usd": 0.3366, "account": "acct-7f3e9"}], "steven": [{}]},
           "tokens_used": 54321}
    other = {"item": "BIOME_DECIDE_TWO_ROUTES", "class": "design", "verdict": "KEEP route B (cap 80k)",
             "judge_model": {"gpt": [{}]}, "account": "acct-7f3e9"}
    hidden = {"item": "OPS_ACCOUNT_DRAIN_C01D", "decision": "x"}
    for name, rec in (("RM_Shirrel.json", art), ("BIOME.json", other), ("OPS.json", hidden)):
        p = os.path.join(ddir, name)
        json.dump(rec, open(p, "w"))
        os.utime(p, (untracked_time, untracked_time))
    left = os.path.join(tmp, "acts.jsonl")
    with open(left, "w") as f:
        f.write(json.dumps({"ts": ts(9).replace("Z", "+00:00"), "kind": "save", "path": "/mnt/c/x/old.rws",
                            "size": 28686221, "archive": "/mnt/d/ClaudeWork/backups/leftovers/a.tar.gz",
                            "verify": "ok", "evidence": ["steven 45,000 tokens"]}) + "\n")
    return os.path.join(tmp, "infrastructure", "state", "delegated"), left


def build(tmp, ddir, left, since=SINCE, cut=CUT, events=EVENTS, marks=MARKS, art=ART_EVENTS):
    return D.build("2026-10-27", since, cut, events, root=tmp, ddir=ddir, leftovers=left, world=None, added={},
                   marks_lines=marks, art_events=art, commits=False)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        mid = (T0 + dt.timedelta(hours=2)).timestamp()
        ddir, left = make_world(tmp, mid)
        raw = json.dumps(EVENTS) + json.dumps(ART_EVENTS) + json.dumps(MARKS) + open(left).read() + "".join(
            open(os.path.join(ddir, "2026-10-27", n)).read() for n in os.listdir(os.path.join(ddir, "2026-10-27")))
        missing = [p for p in PLANTS if p.lower() not in raw.lower()]
        check(not missing, "instrument: every planted value is in the RAW records (missing %s)" % missing)
        check(bool(leaks(raw)), "instrument: the detector finds leaks in the raw records")

        page = build(tmp, ddir, left)
        lk = leaks(page)
        check(not lk, "blind: no planted account/token/cost value on the page (found %s)" % lk)
        check("OPS_ACCOUNT_DRAIN" not in page and "2 record(s) about accounts withheld" in page,
              "blind: an item about accounts is counted, never named")
        check("judge_model" not in page and "steven" not in page.lower() and "(opus;" in page,
              "blind: the judge is a model family from the closed set, nothing else of judge_model")

        # counts: ledger in window = close+note (art geometric correction), file (scope), game+bridge (bridge idle)
        check("5 ledger event(s), 2 judge verdict file(s), 0 `Delegated:` commit(s), 1 art-mark act(s), "
              "1 delegated art install(s), 1 leftover deletion(s)" in page,
              "counts: lease, out-of-window, non-delegated and withheld records are out")
        check("**10 delegated call record(s)**" in page, "counts: the total is the sum of the sources")
        check("| art geometric correction | 2 | 1 |" in page and "| bridge idle | 2 | 0 |" in page
              and "| scope | 1 | 1 |" in page and "| design | 1 | 1 |" in page,
              "counts: per class records and items, measured")
        check("seams moved 2px" in page and "game DOWN" in page and "idle_seconds=3022" in page,
              "content: the decision text and the bridge-idle probe reading pass")
        check("D:\\ClaudeWork\\backups\\leftovers\\a.tar.gz" in page, "content: a leftover line carries its archive")

        later = build(tmp, ddir, left, since=T0 + dt.timedelta(hours=10), cut=CUT + dt.timedelta(hours=1),
                      marks=[], art=[])
        check("**0 delegated call record(s)**" in later and "sources see 6 delegated ledger event(s) and 2 verdict"
              in later, "zero: an empty window reports what the instrument sees in all time")

        # classes
        for why, want in (("delegated: delegated: art judgement", ("art judgement", "art")),
                          ("delegated: art marks", ("art marks", "art marks")),
                          ("delegated: bridge idle (owner idle 50 min)", ("bridge idle", "bridge idle")),
                          ("delegated: art-eval/ledger housekeeping", ("art-eval/ledger housekeeping", "art")),
                          ("delegated: fix", ("fix", None)),
                          ("delegated: design — per-biome giant", ("design", "design")),
                          ("delegated: designer call", ("designer call", None))):
            check(D.class_of(why) == want, "class_of(%r) -> %r" % (why, D.class_of(why)))

        # main(): state, once per date, pre-launch
        out, st = os.path.join(tmp, "out"), os.path.join(tmp, "st", "state.json")
        orig_build, orig_load = D.build, D.B._load
        D.B._load = lambda: (EVENTS, None)
        D.build = lambda date, since, cut, evs, world=None: orig_build(
            date, since, cut, EVENTS, root=tmp, ddir=ddir, leftovers=left, world=None, added={}, marks_lines=MARKS,
            art_events=ART_EVENTS, commits=False)
        try:
            D.main(["--date", "2026-10-27", "--out-dir", out, "--state", st, "--dry-run"])
            check(os.path.exists(os.path.join(out, "delegated_digest_2026-10-27.md")) and not os.path.exists(st),
                  "window: --dry-run writes the page and never moves the state")
            os.remove(os.path.join(out, "delegated_digest_2026-10-27.md"))
            D.main(["--date", "2026-10-27", "--out-dir", out, "--state", st])
            cut1 = D.load_state(st)
            check(cut1 is not None, "window: a real run records its cut")
            m1 = os.path.getmtime(os.path.join(out, "delegated_digest_2026-10-27.md"))
            D.main(["--date", "2026-10-27", "--out-dir", out, "--state", st])
            check(os.path.getmtime(os.path.join(out, "delegated_digest_2026-10-27.md")) == m1 and D.load_state(st) == cut1,
                  "window: one digest per date, a second run does nothing")

            def boom(*a, **k):
                raise RuntimeError("ledger torn near steven 45,000 tokens")
            D.build = boom
            rc = D.main(["--date", "2026-10-28", "--out-dir", out, "--state", st, "--pre-launch"])
            fail = os.path.join(out, "delegated_digest_2026-10-28.FAILED.md")
            check(rc == 0 and os.path.exists(fail) and not leaks(open(fail).read()),
                  "prelaunch: a failing build exits 0, writes a blind FAILED note")
            try:
                D.main(["--date", "2026-10-29", "--out-dir", out, "--state", st])
                check(False, "without --pre-launch a failing build raises")
            except RuntimeError:
                check(True, "without --pre-launch a failing build raises")
        finally:
            D.build, D.B._load = orig_build, orig_load

    # real records, dry run
    with tempfile.TemporaryDirectory() as tmp:
        evs, world = D.B._load()
        n_all = sum(1 for e in evs if str(e.get("why") or "").startswith("delegated:"))
        check(n_all > 0, "real: the ledger holds delegated events (%d) — the instrument can see" % n_all)
        cut = dt.datetime.now(dt.timezone.utc)
        page = D.build("real", cut - dt.timedelta(days=2), cut, evs, world=world)
        lk = [x for x in leaks(page) if not x.startswith("big:")] + [x for x in leaks(page) if x.startswith("big:")
                                                                    and not re.fullmatch(r"big:\d{5,}", x)]
        check(not lk, "real: a 2-day dry run over the real records has no unit/$ figure (found %s)" % lk[:5])
        m = re.search(r"\*\*(\d+) delegated call record", page)
        check(bool(m), "real: the page states a measured total (%s)" % (m.group(1) if m else None))

    print("\n%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
