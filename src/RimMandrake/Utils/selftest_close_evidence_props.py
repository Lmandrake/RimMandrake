#!/usr/bin/env python3
"""Property tests (Hypothesis) for close_evidence's record reading: _top_level, lookup and summarize.

Generated day files of sealed v4 records -- several tools, shared paths, timestamps drawn from three seconds so
same-second ties are common -- are written to a temp evidence folder under a temp key (never the user's), then:
  T1 _top_level on any prefix of a JSON object returns the true top-level string or None, never a wrong value;
     a value only nested (inside detail) is never returned; a key present twice at the top level gives None.
  L1 replaying lines (the same bytes again, anywhere later) changes nothing lookup returns.
  L2 torn copies of this sha's lines add exactly ONE UNMEASURED close_evidence marker, leave every real hit as it
     was, and so never improve a tool's summary; torn lines of ANOTHER sha whose route survived add nothing.
  S1 summarize: for one tool and path, the latest second decides, and within it the line written last.
  S2 appending a FAIL for a tool never improves any tool's summary, and makes that tool FAIL when it is the latest.
Deterministic (derandomize, no example database). Needs hypothesis (infrastructure/stevedesktop/
mutation_requirements.txt). MUTANTS_HUNT_ON_IDLE_STEVE.
"""
import datetime
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import close_evidence as CE  # noqa: E402
try:
    from hypothesis import given, settings, strategies as st, HealthCheck  # noqa: E402
except ImportError:                    # pinned in infrastructure/stevedesktop/mutation_requirements.txt
    print("hypothesis is not installed: UNMEASURED, not a pass or a fail")
    sys.exit(0)

SET = settings(max_examples=150, derandomize=True, database=None, deadline=None,
               suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture])
FAILS = []
SHA = "a" * 40
OTHER = "b" * 40
TOOLS = ("selftest", "validate_patch", "winbuild")
PATHS = ("src/x.py", "src/y.py")
SECS = ("2026-10-27T10:00:00+00:00", "2026-10-27T10:00:01+00:00", "2026-10-27T10:00:02+00:00")
ORDER = ("FAIL", "UNMEASURED", "PASS").index
KEYDIR = tempfile.mkdtemp(prefix="ce_props_key_")
KEYFILE = os.path.join(KEYDIR, "close_evidence.key")
with open(KEYFILE, "w") as fh:
    fh.write("k" * 64)
os.environ[CE.KEY_ENV] = KEYFILE
KEY = CE._key()


def check(cond, msg):
    print(("ok    " if cond else "FAIL  ") + msg)
    if not cond:
        FAILS.append(msg)


def rec(i, sha, tool, path, ts, result):
    r = {"v": CE.V, "ts": ts, "nonce": "%032x" % i, "tool": tool, "clone": "/c", "sha": sha, "dirty": False,
         "dirty_n": 0, "dirty_paths": [], "start": {"sha": sha, "dirty": False, "dirty_n": 0}, "paths": [path],
         "covers": [path], "result": result, "item": None, "seat": "BENCH", "who": {},
         "origin": {"via": "inproc", "start": "snapshot", "end": "git", "tree": "isolated"},
         "live_only": False, "variant": None, "detail": {"note": "nested", "sha": OTHER}}
    return CE.seal(r, KEY)


one = st.tuples(st.sampled_from(TOOLS), st.sampled_from(PATHS), st.sampled_from(SECS),
                st.sampled_from(CE.RESULTS), st.booleans())
records = st.lists(one, min_size=1, max_size=12).map(
    lambda xs: [rec(i, SHA if ours else OTHER, t, p, ts, r) for i, (t, p, ts, r, ours) in enumerate(xs)])


def line(r):
    return json.dumps(r) + "\n"


def lookup_of(lines):
    with tempfile.TemporaryDirectory(prefix="ce_props_") as td:
        today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
        Path(td, today + ".jsonl").write_text("".join(lines), encoding="utf-8")
        return CE.lookup(sha=SHA, folder=td, days=2)


def strip(hits):
    return [h.get("mac") or ("MARKER", h["result"], h["tool"]) for h in hits]


@SET
@given(st.dictionaries(st.sampled_from(["sha", "tool", "route", "x", "y"]),
                       st.one_of(st.text(max_size=8), st.integers(), st.none(),
                                 st.dictionaries(st.sampled_from(["sha", "tool"]), st.text(max_size=8), max_size=2)),
                       max_size=5),
       st.sampled_from(["sha", "tool", "route"]), st.integers(0, 400))
def t1(d, key, cut):
    text = json.dumps(d)
    truth = d.get(key) if isinstance(d.get(key), str) else None
    got = CE._top_level(text, key)
    assert got == truth, ("full", text, key, got)
    got = CE._top_level(text[:cut], key)
    assert got is None or got == truth, ("prefix", text[:cut], key, got, truth)


def t1_duplicate():
    t = '{"sha": "%s", "detail": {"sha": "%s"}, "sha": "%s"}' % (SHA, OTHER, SHA)
    n = '{"tool": "x", "detail": {"sha": "%s"}}' % OTHER
    assert CE._top_level(t, "sha") is None, "duplicate top-level key read as a value"
    assert CE._top_level(n, "sha") is None, "nested-only sha read as top-level"


@SET
@given(records, st.lists(st.integers(0, 50), max_size=4))
def l1(rs, picks):
    lines = [line(r) for r in rs]
    replayed = list(lines)
    for p in picks:                            # a replay is the same bytes again somewhere AFTER the original
        src = lines[p % len(lines)]
        first = replayed.index(src)
        replayed.insert(first + 1 + p % (len(replayed) - first), src)
    assert strip(lookup_of(lines)) == strip(lookup_of(replayed)), "a replayed line changed lookup"


@SET
@given(records, st.lists(st.tuples(st.integers(0, 50), st.floats(0.05, 0.95)), min_size=1, max_size=3))
def l2(rs, tears):
    lines = [line(r) for r in rs]
    clean = lookup_of(lines)
    torn, ours, others = list(lines), 0, 0
    for idx, frac in tears:
        r = rs[idx % len(rs)]
        full = json.dumps(r)
        if r["sha"] == SHA:
            torn.append(full[:max(1, int(len(full) * frac))] + "\n")
            ours += 1
        else:                                  # keep the route intact: cut only inside the trailing mac
            torn.append(full[:full.index('"mac"') + 12] + "\n")
            others += 1
    got = lookup_of(torn)
    markers = [h for h in got if "mac" not in h]
    real = [h for h in got if "mac" in h]
    assert strip(real) == strip(clean), "a torn line changed the real hits"
    assert len(markers) == (1 if ours else 0), ("markers", len(markers), ours, others)
    if markers:
        assert markers[0]["result"] == "UNMEASURED" and markers[0]["tool"] == "close_evidence"
    s0, s1 = CE.summarize(clean), CE.summarize(got)
    for k, v in s0.items():
        assert ORDER(s1[k]) <= ORDER(v), ("summary improved", k, v, s1[k])


@SET
@given(records)
def s1(rs):
    ours = lookup_of([line(r) for r in rs])
    summ = CE.summarize(ours)
    for tool in TOOLS:
        rt = [r for r in ours if r["tool"] == tool]
        if not rt:
            assert tool not in summ
            continue
        want = None
        for p in PATHS:
            on = [r for r in rt if p in r["paths"]]
            if not on:
                continue
            top = max(r["ts"] for r in on)
            res = [r for r in on if r["ts"] == top][-1]["result"]          # same second: the line written last
            want = res if want is None else min(want, res, key=ORDER)
        assert summ[tool] == want, (tool, summ[tool], want, [(r["ts"], r["paths"], r["result"]) for r in rt])


@SET
@given(records, st.sampled_from(TOOLS), st.sampled_from(PATHS), st.sampled_from(SECS))
def s2(rs, tool, path, ts):
    lines = [line(r) for r in rs]
    before = CE.summarize(lookup_of(lines))
    after = CE.summarize(lookup_of(lines + [line(rec(999, SHA, tool, path, ts, "FAIL"))]))
    for k, v in before.items():
        assert ORDER(after[k]) <= ORDER(v), ("FAIL improved", k, v, after[k])
    if ts == max(SECS):
        assert after[tool] == "FAIL", (tool, after[tool])


def run(fn, label):
    try:
        fn()
        check(True, label)
    except AssertionError as e:
        check(False, "%s -- falsified: %s" % (label, str(e)[:400]))


def main():
    run(t1, "T1 _top_level on any prefix: the true top-level string or None, never another value")
    run(t1_duplicate, "T1 duplicate top-level key and nested-only key both read as None")
    run(l1, "L1 replayed lines never change lookup")
    run(l2, "L2 torn lines of this sha add exactly one UNMEASURED marker; routed torn lines of another add none")
    run(s1, "S1 summarize: the latest second decides, same-second ties go to the line written last")
    run(s2, "S2 appending a FAIL never improves a summary; at the latest second it makes that tool FAIL")
    # sanity probe: the instrument can see -- a hand-made FAIL beside a PASS really reads FAIL
    probe = lookup_of([line(rec(1, SHA, "selftest", "src/x.py", SECS[0], "PASS")),
                       line(rec(2, SHA, "selftest", "src/x.py", SECS[0], "FAIL"))])
    check(len(probe) == 2 and CE.summarize(probe) == {"selftest": "FAIL"},
          "probe: two sealed same-second lines reach lookup and the later FAIL decides (%d hits)" % len(probe))
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
