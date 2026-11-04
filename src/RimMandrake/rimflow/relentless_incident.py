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
  fixtures    {good, bad}: a command the instrument must PASS (exit 0) and one it must FAIL (exit non-zero) before any
              parent is released; both run by the supervisor, never by a worker
  checks      each fixture run: when, exits, tails

Release is an evidence event, never a clock: the repair item's ledger block stops holding (it closed) AND the fixtures
pass. A fixture that refuses keeps every parent waiting and is journaled as an alarm; nothing retries it on a timer.
Pure store logic here; relentless_attrib calls it under the store lock.
"""
import json
import os

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


def needs_fixtures(inc):
    return bool(inc and (inc.get("fixtures") or {}).get("good") and (inc.get("fixtures") or {}).get("bad"))


def check(store, repair, run, now, event):
    """Run the release fixtures once for this evidence `event` (the repair's closing): run(cmd) -> (exit, tail).
    -> (ok, why). The result is kept per event, so every parent of the incident reads the same run and no tick reruns
    it; a refusal stands until a new event (the repair reopened and closed again, or a person re-files it)."""
    incs = load(store)
    inc = incs.get(repair)
    if inc is None:
        return False, "no incident for %s" % repair
    done = [c for c in inc.get("checks") or [] if c.get("event") == event]
    if done:
        c = done[-1]
        return c["ok"], c["why"]
    fx = inc.get("fixtures") or {}
    if not needs_fixtures(inc):
        ok, why = True, "no fixtures recorded: released on the repair's close alone"
        good = bad = None
    else:
        good, bad = run(fx["good"]), run(fx["bad"])
        ok = good[0] == 0 and bad[0] not in (0, None)
        why = ("fixtures hold: good exit 0, bad exit %s" % bad[0] if ok else
               "fixtures refuse the repair: good exit %s (wants 0): %s | bad exit %s (wants non-zero): %s"
               % (good[0], (good[1] or "")[-200:], bad[0], (bad[1] or "")[-200:]))
    inc.setdefault("checks", []).append({"event": event, "at": now, "ok": ok, "why": why[:800],
                                         "good": good and good[0], "bad": bad and bad[0]})
    inc["checks"] = inc["checks"][-20:]
    inc["status"] = OPEN if ok else REFUSED
    save(store, incs)
    return ok, why


def released(store, repair, item, now):
    """One parent left the incident; the last one out releases it."""
    incs = load(store)
    inc = incs.get(repair)
    if not inc or item not in inc["items"]:
        return
    inc["items"][item]["released_at"] = now
    if all(v.get("released_at") for v in inc["items"].values()):
        inc["status"], inc["released_at"] = RELEASED, now
    save(store, incs)
