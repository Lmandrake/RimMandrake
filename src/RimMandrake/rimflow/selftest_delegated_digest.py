#!/usr/bin/env python3
"""selftest_delegated_digest.py — the daily digest of delegated calls (delegated_digest.py; DELEGATED_DIGEST_FIX_NEVER_WRITTEN,
DIGEST_BLIND_HARDEN_REASONS_SLIP_THROUGH; review gpt_review_digest_2026-10-27 findings 1-11).

  blind      an account id, an account name, a token figure, a cap, a cost, a key-shaped word and quota phrasing are
             planted in every field of every source (ledger event, judge verdict, Delegated commit, art mark incl. an
             unban's quoted words, art install, leftovers act); none reaches the page. The detector is first shown to
             see each planted value in the RAW records (a clean page means the digest dropped them).
  counts     records per source in the window; lease events, non-delegated events and out-of-window records are out;
             an item about accounts is withheld and counted
  malformed  a bad ledger time, a bad verdict file, a bad leftovers line and a bad commit are counted per source
  body       a `Delegated:` line in a commit BODY is a record, one per line
  window     consecutive digests never repeat a record; a second run the same date does nothing; a dry run never
             moves the state
  fail       a source that fails reads UNMEASURED and its records appear on the next digest that reads it
  identity   a verdict seen untracked (mtime) is not shown again once committed (a new git time)
  force      --force rebuilds a date with its own floor and its own records, never another digest's
  pending    a pending state entry whose page matches its sha256 is reconciled to complete
  refusals   --since without --dry-run, and a dry run into the production directory, are refused
  prelaunch  any failure under --pre-launch (bad argument, a raising build) exits 0 and writes the fixed FAILED page;
             the error goes to the errors log only; a later success removes the FAILED page
  real       a dry run over the real records completes, passes the detector, and sees >0 records (instrument sanity)
Writes only under a temp dir.
"""
import datetime as dt
import hashlib
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
          "acct-7f3e9", "54321", "LUKAS_93_WEEK_DRAIN", "sk-live-zz9", "weekly quota", "usage limit"]
# an independent detector (no code shared with contracts.blind): unit numbers, $ figures, big bare numbers
_UNIT = re.compile(r"(?<![A-Za-z0-9_])\$?\d+(?:[.,]\d+)*\s?(?:[kKM]|%|tokens?)(?![A-Za-z0-9])|\$\s?\d")
_BIG = re.compile(r"(?<![A-Za-z0-9_\-:./\\])\d{1,3}(?:,\d{3})+(?![\d])|(?<![A-Za-z0-9_\-:./\\])\d{5,}(?![A-Za-z0-9_\-:])")


def leaks(text):
    text = re.sub(r"\b(sha|git|event) [0-9a-f]{12}\b", r"\1", text)   # a labelled sha is not a figure
    found = [p for p in PLANTS if p.lower() in text.lower()]
    found += ["unit:" + m.group() for m in _UNIT.finditer(text)]
    found += ["big:" + m.group() for m in _BIG.finditer(text)]
    return found


T0 = dt.datetime(2026, 10, 27, 0, 0, tzinfo=dt.timezone.utc)
LEAK = "steven's account 93% of weekly quota, 45,000 tokens, $0.34 at 80k, usage limit, key sk-live-zz9 acct-7f3e9"


FULLS = ("abcdef1234567" + "8" * 27, "abcdef0123456789abcdef0123456789abcdef01", "ab" * 20)   # the commits git knows


def RESOLVE(cands):
    return {c: f for c in cands for f in FULLS if f.startswith(c)}


def _ids(hidden=()):
    from contracts import blind as BL
    return BL.Identity(frozenset({"PIPE_ELBOW_FIX_SEAM_JOGS", "BIOME_DECIDE_TWO_ROUTES", "A_ONE", "B_TWO", "C_THREE",
                                  "A_B"}), frozenset(hidden))


IDS = None   # set in main(), after the import path is in place


def ts(h):
    return (T0 + dt.timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ")


def tm(h):
    return T0 + dt.timedelta(hours=h)


def events():
    return [
        {"seat": "BENCH", "event": "close", "id": "PIPE_ELBOW_FIX_SEAM_JOGS", "sha": "abcdef1234567",
         "why": "delegated: art geometric correction — " + LEAK, "ts": ts(3), "account_id": "acct-7f3e9",
         "cost_usd": 0.3366},
        {"seat": "BENCH", "event": "note", "id": "PIPE_ELBOW_FIX_SEAM_JOGS", "text": LEAK,
         "why": "delegated: art geometric correction", "ts": ts(4)},
        {"seat": "BENCH", "event": "lease", "id": "PIPE_ELBOW_FIX_SEAM_JOGS", "why": "delegated: art", "ts": ts(4)},
        {"seat": "FOUNDRY", "event": "close", "id": "OPS_ACCOUNT_DRAIN_C01D", "sha": "1111111", "why": "delegated: scope",
         "ts": ts(5)},
        {"seat": "BENCH", "event": "file", "id": "BIOME_DECIDE_TWO_ROUTES", "title": "route B over LUKAS_93_WEEK_DRAIN",
         "why": "delegated: scope " + LEAK, "ts": ts(6), "tokens": 54321},
        {"seat": "OWNER", "event": "game", "state": "DOWN", "ranBy": "BENCH", "ts": ts(7),
         "why": "delegated: bridge idle — deploy [owner idle 33 min (need 20)] key sk-live-zz9"},
        {"seat": "BENCH", "event": "note", "id": "BIOME_DECIDE_TWO_ROUTES", "text": "x", "why": "not delegated",
         "ts": ts(8)},
        {"seat": "BENCH", "event": "note", "id": "steven_54321", "text": "x", "why": "delegated: scope", "ts": ts(9)},
        {"seat": "BENCH", "event": "note", "id": "X_Y", "why": "delegated: scope", "ts": "not a time"},   # malformed
        "not an event",                                                                                  # malformed
    ]


def verdicts(root):
    ddir = os.path.join(root, "infrastructure", "state", "delegated")
    os.makedirs(os.path.join(ddir, "2026-10-27"))
    recs = {"RM_Chittik_n__r1": {"subject": "RM_Chittik_n", "class": "art", "decision": "ACCEPT", "judge_model":
                                 {"opus": "claude-opus", "gpt": "x"}, "image_sha256": "ab" * 32, "note": LEAK},
            "RM_Leak_n__r1": {"subject": "steven_93pct", "class": "art " + LEAK, "decision": "keep, " + LEAK,
                              "judge_model": {"acct-7f3e9": 1}, "item": "LUKAS_93_WEEK_DRAIN"},
            "RM_Prose_n__r1": {"subject": "RM_Prose_n", "class": "scope", "verdict": {"decision": "the 54321 one"}}}
    for name, rec in recs.items():
        with open(os.path.join(ddir, "2026-10-27", name + ".json"), "w") as fh:
            json.dump(rec, fh)
    with open(os.path.join(ddir, "2026-10-27", "RM_Bad__r1.json"), "w") as fh:
        fh.write("{not json")                                                                            # malformed
    return ddir, recs


COMMITS = [("abcdef0123456789abcdef0123456789abcdef01", ts(10),
            "art: fix seams\n\nDelegated: art geometric correction " + LEAK + "\nDelegated: scope\nother line\n"),
           ("", "", "")]                                                                                 # malformed
ART = [{"type": "live", "id": "ev_1", "ts": ts(11), "why": "delegated: art marks", "reason": "archive",
        "sha": "cd" * 20, "rel": "Mods/X/Textures/a.png", "note": LEAK},
       {"type": "unban", "id": "ev_2", "ts": ts(11), "said": LEAK, "sha": "ef" * 20},
       {"type": "live", "id": "ev_3", "ts": ts(12), "why": "delegated: art-eval " + LEAK, "seat": "BENCH",
        "sha": "12" * 20, "rel": "Mods/X/Textures/steven_93.png"},
       {"type": "live", "id": "ev_4", "ts": ts(12), "why": "script:x"}]


def leftovers(root):
    p = os.path.join(root, "acts.jsonl")
    with open(p, "w") as fh:
        fh.write(json.dumps({"ts": ts(13), "kind": "save", "archive": "/mnt/d/ClaudeWork/backups/leftovers/a.zip",
                             "why": LEAK}) + "\n")
        fh.write(json.dumps({"ts": ts(13), "kind": LEAK, "archive": "C:\\Users\\steven\\54321.zip"}) + "\n")
        fh.write("{broken\n")                                                                            # malformed
    return p


def table(page):
    out = {}
    for line in page.splitlines():
        m = re.match(r"\| ([a-zA-Z ]+) \| ([^|]+) \| ([^|]+) \| (\d+) \| (\d+) \| (\d+) \| ([^|]+) \|$", line)
        if m:
            out[m.group(1)] = [c.strip() for c in m.groups()[1:]]
    return out


def lines(page):
    return [l for l in page.splitlines() if l.startswith("- ")]


def args(tmp, date, *extra, cut=None):
    a = ["--date", date, "--state", os.path.join(tmp, "state.json"), "--out-dir", os.path.join(tmp, "out"),
         "--errors", os.path.join(tmp, "errors.log")]
    if cut:
        a += ["--cut", cut]
    return a + list(extra)


def page_of(tmp, date, sub="out"):
    with open(os.path.join(tmp, sub, "delegated_digest_%s.md" % date)) as fh:
        return fh.read()


def test_blind_counts_body_malformed():
    with tempfile.TemporaryDirectory() as tmp:
        ddir, recs = verdicts(tmp)
        lp = leftovers(tmp)
        raw = json.dumps(events()) + json.dumps(recs) + json.dumps(COMMITS) + json.dumps(ART) + open(lp).read()
        missing = [p for p in PLANTS if p.lower() not in raw.lower()]
        check(not missing, "instrument: every planted value is in the RAW records (%s)" % missing)
        check(len(leaks(raw)) >= len(PLANTS), "instrument: the detector sees the raw plants (%d)" % len(leaks(raw)))
        reads = D.gather(events(), tmp, ddir, lp, added={}, commits=COMMITS, art_events=ART)
        cut = max(tm(20), dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1))   # verdict files carry mtime
        text, seen = D.build("2026-10-27", None, cut, reads, ids=_ids({"OPS_ACCOUNT_DRAIN_C01D"}),
                             resolve=RESOLVE)
        check(not leaks(text), "blind: no planted value reaches the page: %s" % leaks(text)[:6])
        tb = table(text)
        led = tb.get("ledger events")
        check(led and led[1] == "4" and led[2] == "2", "counts: ledger 4 records in window (lease, non-delegated, "
              "withheld out), 2 malformed: %s" % led)
        check(led and led[3] == "2", "counts: the OPS_ item and the steven_ item are withheld (%s)" % led)
        check("OPS_ACCOUNT" not in text and "BIOME_DECIDE_TWO_ROUTES" in text, "counts: withheld item never named")
        v = tb.get("judge verdict files")
        check(v and v[1:4] == ["2", "1", "1"], "malformed: verdict 2 records, 1 bad file, the steven_ subject "
              "withheld: %s" % v)
        c = tb.get("Delegated commits")
        check(c and c[1] == "2" and c[2] == "1", "body: 2 Delegated: lines of one commit body, 1 bad commit: %s" % c)
        m = tb.get("art mark acts")
        check(m and m[1] == "2", "marks: archive and unban are mark records (%s)" % m)
        ai = tb.get("delegated art installs")
        check(ai and ai[1] == "1", "art installs: the delegated live install only (%s)" % ai)
        lf = tb.get("leftover deletions")
        check(lf and lf[1] == "2" and lf[2] == "1", "malformed: leftovers 2 records, 1 bad line: %s" % lf)
        check("RM_Chittik" in text and "ACCEPT" in text and "opus+gpt" in text, "blind: closed fields still show")
        check("sha abcdef123456" in text and "git abcdef012345" in text,
              "sha: a ledger and a commit sha git resolves print, by their label")
        check("111111" not in text, "sha: a sha git does not know never prints")
        check(" OTHER" in text, "blind: a prose decision reads OTHER, never its words")
        held = sum(int(r[3]) for r in tb.values())
        check(sum(len(x) for x in seen.values()) == len(lines(text)) + held,
              "counts: every record in the window is seen (shown + %d withheld): %d vs %d" % (
                  held, sum(len(x) for x in seen.values()), len(lines(text))))


def _reads(evs=None, commit=None, verdict_added=None, tmp=None, ddir=None):
    return D.gather(evs if evs is not None else [], tmp, ddir or os.path.join(tmp, "none"),
                    os.path.join(tmp, "none.jsonl"), added=verdict_added or {},
                    commits=commit if commit is not None else [], art_events=[])


def test_window_fail_force_pending():
    with tempfile.TemporaryDirectory() as tmp:
        ev1 = [{"seat": "BENCH", "event": "close", "id": "A_ONE", "why": "delegated: scope", "ts": ts(1)}]
        ev2 = ev1 + [{"seat": "BENCH", "event": "close", "id": "B_TWO", "why": "delegated: scope", "ts": ts(25)}]
        cm = [("ab" * 20, ts(2), "x\n\nDelegated: scope")]
        # day 1: the commit source fails
        r1 = _reads(ev1, tmp=tmp)
        r1["commit"] = D._read("unmeasured", "git_failed")
        rc = D.main(args(tmp, "2026-10-27", cut=ts(20)), sources=(r1, IDS, RESOLVE))
        p1 = page_of(tmp, "2026-10-27")
        check(rc == 0 and "A_ONE" in p1 and "UNMEASURED git_failed" in p1, "fail: a failed source reads UNMEASURED")
        st = json.load(open(os.path.join(tmp, "state.json")))
        check(st["digests"]["2026-10-27"]["complete"] is True, "window: the state entry is complete after the run")
        # same date again: nothing done, page untouched
        rc = D.main(args(tmp, "2026-10-27", cut=ts(21)), sources=(_reads(ev2, cm, tmp=tmp), IDS, RESOLVE))
        check(page_of(tmp, "2026-10-27") == p1, "window: a second run the same date does nothing")
        # a dry run never moves the state
        before = open(os.path.join(tmp, "state.json")).read()
        D.main(args(tmp, "2026-10-28", "--dry-run", cut=ts(44)), sources=(_reads(ev2, cm, tmp=tmp), IDS, RESOLVE))
        check(open(os.path.join(tmp, "state.json")).read() == before, "window: a dry run never moves the state")
        # day 2: the commit source recovers; its day-1 record appears now, A_ONE never again
        D.main(args(tmp, "2026-10-28", cut=ts(44)), sources=(_reads(ev2, cm, tmp=tmp), IDS, RESOLVE))
        p2 = page_of(tmp, "2026-10-28")
        check("A_ONE" not in p2 and "B_TWO" in p2, "window: consecutive digests never repeat a record")
        check("git abababababab" in p2, "fail: the failed source's backlog appears on the next digest that reads it")
        # force day 1: its own floor, its own records, never day 2's
        D.main(args(tmp, "2026-10-27", "--force", cut=ts(45)), sources=(_reads(ev2, cm, tmp=tmp), IDS, RESOLVE))
        p1f = page_of(tmp, "2026-10-27")
        check("A_ONE" in p1f and "B_TWO" not in p1f and "abababababab" not in p1f,
              "force: a rebuild keeps its own records and never takes another digest's")
        st = json.load(open(os.path.join(tmp, "state.json")))
        check(st["digests"]["2026-10-27"]["floor"] is None, "force: the original floor is kept")
        # pending: entry written, page written, completion lost -> reconciled, not rebuilt
        e = st["digests"]["2026-10-28"]
        e["complete"] = False
        e["page_sha256"] = hashlib.sha256(open(os.path.join(tmp, "out", "delegated_digest_2026-10-28.md"),
                                              "rb").read()).hexdigest()
        json.dump(st, open(os.path.join(tmp, "state.json"), "w"))
        ev3 = ev2 + [{"seat": "BENCH", "event": "close", "id": "C_THREE", "why": "delegated: scope", "ts": ts(30)}]
        D.main(args(tmp, "2026-10-28", cut=ts(46)), sources=(_reads(ev3, cm, tmp=tmp), IDS, RESOLVE))
        st = json.load(open(os.path.join(tmp, "state.json")))
        check(st["digests"]["2026-10-28"]["complete"] is True and "C_THREE" not in page_of(tmp, "2026-10-28"),
              "pending: a page matching its recorded sha256 is reconciled to complete, not rebuilt")
        # pending with a page that does NOT match: rebuilt
        st["digests"]["2026-10-28"]["complete"] = False
        st["digests"]["2026-10-28"]["page_sha256"] = "0" * 64
        json.dump(st, open(os.path.join(tmp, "state.json"), "w"))
        D.main(args(tmp, "2026-10-28", cut=ts(46)), sources=(_reads(ev3, cm, tmp=tmp), IDS, RESOLVE))
        check("C_THREE" in page_of(tmp, "2026-10-28"), "pending: a page that does not match is rebuilt")
        # legacy state: last_cut becomes the floor
        json.dump({"last_cut": ts(26)}, open(os.path.join(tmp, "legacy.json"), "w"))
        st = D.load_state(os.path.join(tmp, "legacy.json"))
        check(st["floor"] == ts(26) and st["digests"] == {}, "legacy: last_cut becomes the global floor")


def test_identity():
    with tempfile.TemporaryDirectory() as tmp:
        ddir, _recs = verdicts(tmp)
        r1 = D.gather([], tmp, ddir, os.path.join(tmp, "x"), added={}, commits=[], art_events=[])
        t1 = max(t for _i, t, _r in r1["verdict"]["items"])
        D.main(args(tmp, "2026-10-27", cut=D.iso(t1 + dt.timedelta(seconds=5))), sources=(r1, IDS, RESOLVE))
        check("RM_Chittik" in page_of(tmp, "2026-10-27"), "identity: an untracked verdict shows (mtime)")
        rel = os.path.relpath(os.path.join(ddir, "2026-10-27", "RM_Chittik_n__r1.json"), tmp).replace(os.sep, "/")
        later = t1 + dt.timedelta(hours=2)
        r2 = D.gather([], tmp, ddir, os.path.join(tmp, "x"), added={rel: later}, commits=[], art_events=[])
        D.main(args(tmp, "2026-10-28", cut=D.iso(later + dt.timedelta(hours=1))), sources=(r2, IDS, RESOLVE))
        check("RM_Chittik_n" not in page_of(tmp, "2026-10-28"),
              "identity: once committed (a new git time) it is not shown again")


def test_refusals_prelaunch():
    with tempfile.TemporaryDirectory() as tmp:
        try:
            D.main(args(tmp, "2026-10-27", "--since", ts(0)), sources=({}, IDS, RESOLVE))
            ok = False
        except ValueError:
            ok = True
        check(ok, "refusals: --since without --dry-run is refused")
        try:
            D.main(["--date", "2026-10-27", "--dry-run", "--out-dir", D.OUT_DIR, "--state",
                    os.path.join(tmp, "s.json")], sources=({}, IDS, RESOLVE))
            ok = False
        except ValueError:
            ok = True
        check(ok, "refusals: a dry run into the production directory is refused")
        failed = os.path.join(tmp, "out", "delegated_digest_2026-10-27.FAILED.md")
        rc = D.main(args(tmp, "2026-10-27", "--pre-launch", "--since", ts(0)), sources=({}, IDS, RESOLVE))
        txt = open(failed).read() if os.path.exists(failed) else ""
        check(rc == 0 and txt == D.FAILED_TEXT % "2026-10-27", "prelaunch: a refusal exits 0 with the fixed page")
        err = open(os.path.join(tmp, "errors.log")).read()
        check("ValueError" in err, "prelaunch: the error goes to the errors log")
        os.remove(failed)
        rc = D.main(args(tmp, "2026-10-27", "--pre-launch", "--bogus"), sources=({}, IDS, RESOLVE))
        check(rc == 0 and os.path.exists(failed), "prelaunch: a bad argument exits 0 with the fixed page")
        bad = {"ledger": {"state": "measured", "fault": "none", "malformed": 0,
                          "items": [("L1", tm(1), {"source": "ledger", "t": tm(1), "why": "delegated: scope",
                                                   "id": "A_B", "event": "close", "seat": "BENCH"})]}}
        orig = D.build

        def boom(*a, **k):
            raise RuntimeError("acct-7f3e9 45,000 tokens")
        D.build = boom
        try:
            rc = D.main(args(tmp, "2026-10-27", "--pre-launch", cut=ts(2)), sources=(bad, IDS, RESOLVE))
        finally:
            D.build = orig
        txt = open(failed).read()
        check(rc == 0 and not leaks(txt), "prelaunch: a raising build exits 0 and the page holds no error text")
        st = json.load(open(os.path.join(tmp, "state.json"))) if os.path.exists(os.path.join(tmp, "state.json")) else {}
        check(not (st.get("digests") or {}).get("2026-10-27", {}).get("complete"), "prelaunch: a failure is not complete")
        try:
            D.build = boom
            D.main(args(tmp, "2026-10-27", cut=ts(2)), sources=(bad, IDS, RESOLVE))
            ok = False
        except RuntimeError:
            ok = True
        finally:
            D.build = orig
        check(ok, "prelaunch: without --pre-launch the error raises")
        rc = D.main(args(tmp, "2026-10-27", "--pre-launch", cut=ts(2)), sources=(bad, IDS, RESOLVE))
        check(rc == 0 and not os.path.exists(failed) and "A_B" in page_of(tmp, "2026-10-27"),
              "prelaunch: a later success writes the digest and removes the stale FAILED page")


def test_real():
    with tempfile.TemporaryDirectory() as tmp:
        rc = D.main(["--dry-run", "--date", "2026-10-27", "--state", os.path.join(tmp, "s.json"), "--out-dir",
                     os.path.join(tmp, "dry")])
        p = page_of(tmp, "2026-10-27", "dry")
        tb = table(p)
        led = tb.get("ledger events")
        check(rc == 0 and led and led[0] == "measured" and int(led[5]) > 0,
              "real: the ledger is measured and sees >0 delegated events in all time (%s)" % led)
        check(not leaks(p), "real: the real page passes the detector: %s" % leaks(p)[:5])
        check(not os.path.exists(os.path.join(tmp, "s.json")), "real: a dry run writes no state")


def main():
    global IDS
    IDS = _ids()
    for t in (test_blind_counts_body_malformed, test_window_fail_force_pending, test_identity,
              test_refusals_prelaunch, test_real):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            check(False, "%s crashed: %s" % (t.__name__, e))
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
