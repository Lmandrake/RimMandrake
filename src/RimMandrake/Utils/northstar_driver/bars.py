"""Bar runner. A BAR is one north-star line (a `## north star` must-show / cannot-show id,
or a hand-named trial bar). Two ways to bind evidence:

 1. `@bar("pit.must.3", mod="Pits")` functions in a plan module: `fn(t)` gets a Trial and
    returns a Verdict (or a bool / raises). Every action should go through `t.act()`, which
    forces a state read after the write.
 2. modcheck's Suite: `run_suite_bars()` runs validation.py's chains on the FastSession and
    rolls component verdicts up to bars through each component's `shows=`.

Verdict semantics (never blurred):
  PASS        evidence read back and it holds
  FAIL        evidence read back and it does NOT hold
  UNMEASURED  could not ask / could not prove (transport error, missing tool, no judge, no
              component claims the bar). NEVER a PASS, NEVER a FAIL.
A cannot-show bar inverts polarity only in what the fn asserts; the runner never flips.
Visual bars (visual=True) can only be PASS via a judge verdict supplied by the fn; with none
they are UNMEASURED with the screenshot path as evidence.
"""
import json
import os
import time
import traceback

from northstar_driver import PASS, FAIL, UNMEASURED

REGISTRY = {}     # bar id -> Bar


class Unmeasured(Exception):
    """Raise from a bar fn: could not ask / could not prove."""


class Verdict(object):
    def __init__(self, status, evidence=""):
        self.status, self.evidence = status, evidence


def passed(ev=""):
    return Verdict(PASS, ev)


def failed(ev=""):
    return Verdict(FAIL, ev)


def unmeasured(ev=""):
    return Verdict(UNMEASURED, ev)


class Bar(object):
    def __init__(self, id, fn, mod=None, visual=False, polarity="must", needs_tools=()):
        self.id, self.fn, self.mod, self.visual = id, fn, mod, visual
        self.polarity, self.needs_tools = polarity, tuple(needs_tools)


def bar(id, mod=None, visual=False, polarity="must", needs_tools=()):
    def deco(fn):
        REGISTRY[id] = Bar(id, fn, mod, visual, polarity, needs_tools)
        return fn
    return deco


class Trial(object):
    """What a bar fn is handed. Thin on purpose."""

    def __init__(self, session, anchor=(100, 100)):
        self.s, self.anchor, self.notes = session, anchor, []

    def call(self, tool, **p):
        return self.s.call(tool, **p)

    def read(self, tool, **p):
        return self.s.call(tool, **p)

    def act(self, what, do, read_back, expect=True):
        """Do a write, then PROVE it with an independent read. `read_back()` returns the
        observed value; the act fails loudly if it != expect (callable allowed). A write
        that reported success and changed nothing is the project's commonest trap."""
        do()
        got = read_back()
        ok = expect(got) if callable(expect) else got == expect
        if not ok:
            raise AssertionError("%s: wrote, but read-back says %r (expected %r) -- the call "
                                 "reported success and did not take" % (what, got, expect))
        self.notes.append("%s verified (%r)" % (what, got))
        return got

    def wait_ticks(self, n):
        return self.s_wait(n)

    def s_wait(self, n):
        # the mock advances per call; live uses rimworld/step_game_ticks if present
        if "rimworld/step_game_ticks" in self.s.tools:
            self.s.call("rimworld/step_game_ticks", ticks=n)
        return self


def run_bar(b, session, anchor=(100, 100)):
    t0 = time.perf_counter()
    t = Trial(session, anchor)
    missing = [x for x in b.needs_tools if x not in session.tools]
    if missing:
        return _row(b, UNMEASURED, "tool(s) absent from bridge census: %s" % missing, t0, t)
    try:
        v = b.fn(t)
        if isinstance(v, Verdict):
            st, ev = v.status, v.evidence
        elif v is True:
            st, ev = PASS, "fn returned True"
        elif v is False:
            st, ev = FAIL, "fn returned False"
        else:
            st, ev = UNMEASURED, "fn returned %r -- not a verdict" % (v,)
    except Unmeasured as ex:
        st, ev = UNMEASURED, str(ex)
    except AssertionError as ex:
        st, ev = FAIL, str(ex)
    except (ConnectionError, OSError, TimeoutError) as ex:
        st, ev = UNMEASURED, "transport: %s" % ex      # could not ask != FAIL
    except Exception as ex:
        # A bridge/tool error or script bug: we did not get an answer about the MOD.
        st, ev = UNMEASURED, "%s: %s | %s" % (type(ex).__name__, ex,
                                              traceback.format_exc().strip().splitlines()[-2][:120])
    if b.visual and st == PASS and "judge:" not in ev:
        st, ev = UNMEASURED, "visual bar: state evidence only, no judge verdict (%s)" % ev
    return _row(b, st, ev, t0, t)


def _row(b, st, ev, t0, t):
    return {"id": b.id, "status": st, "evidence": ev, "polarity": b.polarity,
            "visual": b.visual, "ms": round((time.perf_counter() - t0) * 1000, 3),
            "notes": t.notes}


def rollup_components(chains, declared_ids):
    """modcheck chain output -> {bar id: row} via each component's `shows`. A bar no component
    claims is UNMEASURED (unwired), which is exactly the floor modcheck refuses on."""
    claims = {}
    for ch in chains:
        for c in ch["components"]:
            for sid in c.get("shows", []):
                claims.setdefault(sid, []).append(c)
    rows = {}
    for bid in declared_ids:
        cs = claims.get(bid, [])
        if not cs:
            rows[bid] = {"id": bid, "status": UNMEASURED, "evidence": "no component claims shows=%s" % bid}
            continue
        vs = [str(c.get("verdict", "")) for c in cs]
        if any(v == "FAIL" for v in vs):
            st = FAIL
        elif all(v.startswith("PASS") for v in vs):
            st = PASS
        else:
            st = UNMEASURED
        rows[bid] = {"id": bid, "status": st,
                     "evidence": "; ".join("%s=%s" % (c.get("name"), c.get("verdict")) for c in cs)}
    return list(rows.values())


def summarize(rows):
    n = {PASS: 0, FAIL: 0, UNMEASURED: 0}
    for r in rows:
        n[r["status"]] += 1
    return n


def all_green(rows, expected_ids=None):
    """GREEN only if every EXPECTED bar is present and PASS. A bar the walk lists but the run
    never produced counts UNMEASURED -- absence is not a pass."""
    by = {r["id"]: r["status"] for r in rows}
    ids = list(expected_ids) if expected_ids is not None else list(by)
    return bool(ids) and all(by.get(i) == PASS for i in ids)


def write_results(path, doc):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=2)
    os.replace(tmp, path)
