#!/usr/bin/env python3
"""relentless_incident.py — one record per shared instrument fault (INSTRUMENT_INCIDENT_BUILD_NO_STRIKES).

Spec: design/RimMandrake/test_tolerance_gpt_advice_2026-11-04.md, "Repair the instrument as tracked work". A broken
site, harness or checker fails every item that leans on it; before this each of them earned strikes and a new builder
(LEANINGSCRUB_STALL_SHARED_MOVE_1 and TITANIC_BODYSIZE_TEST_RACE_1 both changed code against one broken live harness).
Now the fault is ONE incident, keyed by its repair item:

  component   what is broken (a tool, the bridge, the checker's box, a staged site) and its version when known
  repro       the evidence that shows it is the instrument, not the work
  items       {item: {sha, since, released_at}}: every parent waiting on it, each with the candidate it keeps
  repair      the ledger item that repairs it (the parents' ledger block points there)
  fixtures    {good, bad}: a command the instrument must PASS (exit 0 and a `FIXTURE_VERDICT: PASS` line) and one it must
              FAIL (a non-zero exit it chose and `FIXTURE_VERDICT: FAIL`: a timeout, 126/127, a signal or no verdict is a
              fixture that could not measure) before any candidate is released; both
              run by the supervisor, never by a worker. No fixtures, no candidate released.
  checks      each fixture run: when, exits, tails

Release is an evidence event, never a clock: the repair item's ledger block stops holding (it closed) AND the fixtures
pass. A fixture that refuses keeps every parent waiting and is journaled as an alarm; nothing retries it on a timer.
Store logic here; check() takes the store lock itself, link() and released() run under the caller's.

A fixture that cannot print the verdict line can never release its parents (REPAIR_FIXTURES_ENFORCE_VERDICT_AT_FILING),
so lint() reads each command before it is trusted: at attribution a pair that names nothing able to print it is refused,
one whose named script does not print it YET is linked and flagged to Operations (alarm kind NO_VERDICT, a note on the
repair item: its close owes the line); `finish` on the repair item refuses while the lint still fails; a release run
that printed no verdict alarms the same kind. The lint is a static read, never the release gate: check() still runs.
"""
import json
import os
import re
import shlex

FILE = "instrument_incidents.json"     # relentless_breakers owns incidents.json (capability signatures)
OPEN, RELEASED, REFUSED = "open", "released", "fixture_refused"


def _path(store):
    return store.p(FILE)


def load(store):
    try:
        with open(_path(store), encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save(store, incs):
    tmp = _path(store) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(incs, f, indent=1, sort_keys=True)
    os.replace(tmp, _path(store))


def get(store, repair):
    return load(store).get(repair)


def link(store, repair, item, sha, now, component=None, repro=None, fixtures=None, targets=(), waits=True):
    """Under the store lock. Opens the incident for `repair` or joins it: a second item on the same repair is the same
    fault, not a new one. Fixtures given later fill in, never replace ones already set (the first diagnosis that named
    them stands; a different pair is a different fault and wants its own repair item). -> the incident."""
    incs = load(store)
    inc = incs.get(repair)
    if inc is None or inc.get("status") == RELEASED:
        inc = {"repair": repair, "component": None, "repro": [], "items": {}, "fixtures": {}, "checks": [],
               "targets": [], "status": OPEN, "opened_at": now, "released_at": None}
        incs[repair] = inc
    if component and not inc.get("component"):
        inc["component"] = component[:300]
    if repro:
        inc["repro"] = (inc.get("repro") or []) + [{"item": item, "at": now, "evidence": repro[:1200]}]
        inc["repro"] = inc["repro"][-12:]
    for k, v in (fixtures or {}).items():
        if v and not inc["fixtures"].get(k):
            inc["fixtures"][k] = v[:600]
    inc["targets"] = sorted(set(inc.get("targets") or []) | set(targets or ()))
    # a mixed diagnosis (PRODUCT too) sends the item to its builder: it is recorded as affected, not as waiting
    inc["items"][item] = {"sha": sha, "since": now, "released_at": None if waits else now, "waits": bool(waits)}
    save(store, incs)
    return inc


NO_VERDICT = "instrument_fixture_no_verdict"      # the alarm kind Operations' told ledger reads
VERDICT_WORD = "FIXTURE_VERDICT"
LINT_OK, LINT_PENDING, LINT_NEVER = "ok", "pending", "never"
_SCRIPT_EXT = (".py", ".sh", ".bash", ".pl", ".js", ".ps1", ".rb")


def _paths(cmd):
    """The tokens of `cmd` that name a file: a path separator or a script extension (`--x=a/b.py` gives a/b.py)."""
    try:
        toks = shlex.split(cmd or "", posix=True)
    except ValueError:
        toks = (cmd or "").split()
    out = []
    for t in toks:
        t = t.split("=", 1)[1] if t.startswith("-") and "=" in t else t
        t = t.strip(";|&()<>")
        if t and not t.startswith("-") and ("/" in t or t.lower().endswith(_SCRIPT_EXT)) and "://" not in t:
            out.append(t)
    return out


def lint(cmd, root):
    """A static read of one fixture command. -> (LINT_OK|LINT_PENDING|LINT_NEVER, why).
    ok       the command text carries FIXTURE_VERDICT, or a file it names (under `root`, the tree it runs in) does
    pending  it names a script that does not exist yet, or exists without the word: the repair owes the line
    never    it names no file and its text has no verdict: nothing it runs can ever print the line"""
    cmd = cmd or ""
    if VERDICT_WORD in cmd:
        return LINT_OK, "the command prints %s itself" % VERDICT_WORD
    named = _paths(cmd)
    if not named:
        return LINT_NEVER, ("%r names no script and does not print %s: it can never give a verdict, so it can never "
                            "release a parent" % (cmd[:200], VERDICT_WORD))
    missing, silent = [], []
    for n in named:
        f = n if os.path.isabs(n) else os.path.join(root or ".", n)
        if not os.path.isfile(f):
            missing.append(n)
            continue
        try:
            with open(f, encoding="utf-8", errors="replace") as h:
                if VERDICT_WORD in h.read(2_000_000):
                    return LINT_OK, "%s prints %s" % (n, VERDICT_WORD)
        except OSError:
            missing.append(n)
            continue
        silent.append(n)
    return LINT_PENDING, ("%r does not print %s yet (%s): its repair must make it print `%s: PASS|FAIL` or its close "
                          "releases nothing" % (cmd[:200], VERDICT_WORD, "; ".join(
                              ["%s absent" % m for m in missing] + ["%s has no verdict line" % x for x in silent]),
                              VERDICT_WORD))


def lint_pair(fixtures, root):
    """{good, bad} -> (worst state, [why per fixture that is not ok]); (LINT_OK, []) when both pass or none is given."""
    worst, whys = LINT_OK, []
    for k in ("good", "bad"):
        v = (fixtures or {}).get(k)
        if not v:
            continue
        state, why = lint(v, root)
        if state != LINT_OK:
            whys.append("%s: %s" % (k, why))
            worst = LINT_NEVER if LINT_NEVER in (state, worst) else LINT_PENDING
    return worst, whys


def owed_by(store, item, root):
    """`finish` on `item`: why the close must wait, when `item` repairs an incident that still has parents waiting and
    whose fixtures do not print the verdict line in `root` (the worker's tree); None when nothing is owed."""
    inc = get(store, item)
    if not inc or inc.get("status") == RELEASED or not needs_fixtures(inc):
        return None
    if not any(v.get("waits", True) and not v.get("released_at") for v in (inc.get("items") or {}).values()):
        return None
    state, whys = lint_pair(inc["fixtures"], root)
    if state == LINT_OK:
        return None
    return ("%s repairs an instrument incident whose release fixtures cannot give a verdict, so closing it would release "
            "none of its waiting parents (%s): make them print `%s: PASS` (good, exit 0) and `%s: FAIL` (bad, a "
            "non-zero exit), commit that, then finish. %s" % (item, ", ".join(sorted(inc["items"])), VERDICT_WORD,
                                                             VERDICT_WORD, " | ".join(whys)))[:1500]


def no_verdict_at(store, repair, event):
    """True when a release run of `repair` for this evidence `event` had a fixture that printed no verdict line (a
    snag parent's cached no-run row on the same event does not hide it)."""
    return any(c.get("event") == event and c.get("no_verdict") for c in (get(store, repair) or {}).get("checks") or [])


def needs_fixtures(inc):
    return bool(inc and (inc.get("fixtures") or {}).get("good") and (inc.get("fixtures") or {}).get("bad"))


def ran(code):
    """An exit a fixture can be judged by: the command ran and chose it. None (timeout, no exit), 126/127 (not
    executable, not found) and signal deaths (negative, >= 128) say the fixture could not run, which is no evidence."""
    return isinstance(code, int) and 0 <= code < 126


def verdict(tail):
    """The instrument's own word, the last `FIXTURE_VERDICT: PASS|FAIL` line of the output; None when it printed none.
    An exit alone cannot tell a measured FAIL from a setup that died (`python3 /missing.py` exits 2), so a fixture that
    gives no verdict measured nothing and releases nothing."""
    words = re.findall(r"^\s*FIXTURE_VERDICT:\s*(PASS|FAIL)\s*$", tail or "", re.M)
    return words[-1] if words else None


def _cached(inc, key):
    done = [c for c in inc.get("checks") or [] if c.get("key") == key]
    return (done[-1]["ok"], done[-1]["why"]) if done else None


def check(store, repair, run, now, event, need_fixtures=True):
    """Run the release fixtures once for this evidence `event` (the repair's closing): run(cmd) -> (exit, tail).
    -> (ok, why). Takes the store lock itself (never call it under the lock): the fixtures run OUTSIDE the lock and the
    result is merged back under it, fenced on the fixtures it ran, so a parent linked meanwhile is never lost.
    The result is kept per (event, fixtures, need), so every parent reads the same run and no tick reruns it; a
    refusal stands until new evidence (the repair closes again, or new fixtures are attributed).
    `need_fixtures`: a validation parent (it holds a candidate) is released only by fixtures that ran and held; a
    worker's snag (no candidate, it resumes as a fresh lease) may go on the repair's close alone."""
    with store.lock():
        inc = load(store).get(repair)
        if inc is None:
            return False, "no incident for %s" % repair
        fx = dict(inc.get("fixtures") or {})
        key = [event, fx.get("good"), fx.get("bad"), bool(need_fixtures)]
        hit = _cached(inc, key)
    if hit:
        return hit
    good = bad = None
    if not needs_fixtures({"fixtures": fx}):
        ok = not need_fixtures
        why = ("no fixtures recorded: a worker's snag resumes on the repair's close" if ok else
               "no fixtures recorded: nothing shows the repaired instrument works, so no candidate is released; "
               "attribute it again with --fixture-good and --fixture-bad")
    else:
        good, bad = run(fx["good"]), run(fx["bad"])
        ok = (good[0] == 0 and verdict(good[1]) == "PASS" and
              ran(bad[0]) and bad[0] != 0 and verdict(bad[1]) == "FAIL")
        why = ("fixtures hold: good exit 0 PASS, bad exit %s FAIL" % bad[0] if ok else
               "fixtures refuse the repair: good exit %s verdict %s (wants 0 PASS): %s | bad exit %s verdict %s (wants a "
               "non-zero exit it chose, not a timeout, 126/127 or a signal, and FAIL): %s"
               % (good[0], verdict(good[1]), (good[1] or "")[-200:], bad[0], verdict(bad[1]), (bad[1] or "")[-200:]))
    with store.lock():
        incs = load(store)
        inc = incs.get(repair)
        if inc is None:
            return False, "the incident %s vanished while its fixtures ran" % repair
        hit = _cached(inc, key)
        if hit:
            return hit                          # another sweep recorded this event first: one result per event
        if dict(inc.get("fixtures") or {}) != fx:
            return False, "the fixtures changed while they ran: the next sweep runs the new ones"
        inc.setdefault("checks", []).append({"key": key, "event": event, "at": now, "ok": ok, "why": why[:800],
                                             "good": good and good[0], "bad": bad and bad[0],
                                             "no_verdict": bool(good and bad and (verdict(good[1]) is None or
                                                                                  verdict(bad[1]) is None))})
        inc["checks"] = inc["checks"][-20:]
        inc["status"] = OPEN if ok else REFUSED
        save(store, incs)
    return ok, why


def released(store, repair, item, now):
    """Under the store lock. One parent left the incident; the last one out releases it."""
    incs = load(store)
    inc = incs.get(repair)
    if not inc or item not in inc["items"]:
        return
    inc["items"][item]["released_at"] = now
    if all(v.get("released_at") for v in inc["items"].values()):
        inc["status"], inc["released_at"] = RELEASED, now
    save(store, incs)
