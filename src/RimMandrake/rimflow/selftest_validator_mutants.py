#!/usr/bin/env python3
"""selftest_validator_mutants.py -- the two mutation streams of VALIDATOR_REPLAY_BUILD_GOOD_AND_BAD (spec
design/RimMandrake/test_tolerance_gpt_advice_2026-11-04.md, rank 5: "Mutate the product" / "Mutate the proof"), plus the
validator's own mutants:

  PRODUCT stream: a real proof (live_def_check.judge, the live tier's def proof) reads a world made from a product def;
    each product mutant (the comp dropped, the def renamed, a near-miss token, its mod not in the running load) must be
    seen for what it is: FAIL where the game answered no, UNMEASURED where it could not.
  PROOF stream: the same proof, damaged the ways a worker's proof gets damaged: an assertion removed, a threshold
    loosened, stale data substituted, a row skipped, an exception swallowed, PASS forced. The known-good / known-bad
    CONTROLS (validator_replay.controls) must expose every one, and must pass the real proof. A mutant that crashes is
    easy; the essential ones return a plausible green.
  VALIDATOR stream: the classifier and the supervisor's routing are themselves damaged (monkeypatched); the replay bank
    (validator_replay.py) must turn red on each, or the bank is not testing what it claims.
"""
import contextlib
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import live_def_check as C      # noqa: E402
import validator_replay as V    # noqa: E402

FAILS = []


def check(cond, what):
    print("%s %s" % ("ok  " if cond else "FAIL", what))
    if not cond:
        FAILS.append(what)


# ---- the product: one def as the game would report it ----

PRODUCT = {"defName": "RM_Chittik", "packageId": "mandrake.rm.therot",
           "comps": ["CompProperties_WoundLink", "CompProperties_Milkable"]}
CLAIMS = [("ThingDef/RM_Chittik", "CompProperties_WoundLink"), ("ThingDef/RM_Chittik", "CompProperties_Milkable")]
OWNERS = {"ThingDef/RM_Chittik": {"mandrake.rm.therot"}}


def world(product, running=("mandrake.rm.therot",), claims=CLAIMS):
    """-> the proof's inputs for a product: get_defs' reply, the owners and the running load."""
    found = product is not None and product.get("loaded", True) and bool(set(running) & {product["packageId"]})
    defs = []
    for key in sorted({k for k, _ in claims}):
        name = key.split("/", 1)[1]
        hit = found and product["defName"] == name
        defs.append({"requested": key, "found": hit,
                     "packageId": product["packageId"] if hit else None,
                     "fields": {"comps": [{"class": c} for c in product["comps"]]} if hit else None})
    return {"claims": claims, "reply": {"defs": defs}, "owners": OWNERS, "running": list(running)}


def mutate(**kw):
    return dict(PRODUCT, **kw)


# Known-good and known-bad worlds, each with the verdict a sound proof must give
WORLDS = [
    ("good: the product as built", world(PRODUCT), C.PASS),
    ("bad: the comp the criterion names is gone", world(mutate(comps=["CompProperties_Milkable"])), C.FAIL),
    ("bad: the second comp is gone (a later row)", world(mutate(comps=["CompProperties_WoundLink"])), C.FAIL),
    ("bad: a near-miss comp only (substring of nothing, superstring of the token)",
     world(mutate(comps=["CompProperties_WoundLinkLegacy", "CompProperties_Milkable"])), C.FAIL),
    ("bad: the def was renamed, its mod is loaded", world(mutate(defName="RM_ChittikOld")), C.FAIL),
    ("unreachable: its mod is not in the running load", world(PRODUCT, running=("ludeon.rimworld",)), C.UNMEASURED),
    ("unreachable: the reply is not a get_defs answer", dict(world(PRODUCT), reply={"error": "timeout"}), C.UNMEASURED),
    ("unreachable: no reply at all", dict(world(PRODUCT), reply=None), C.UNMEASURED),
]


def real(w):
    return C.judge(w["claims"], w["reply"], w["owners"], w["running"])[0]


# ---- the proof stream: damaged proofs ----

GOOD_REPLY = world(PRODUCT)["reply"]


def m_force_pass(w):
    return C.PASS


def m_no_token_assert(w):        # the assertion on the comp removed: only "it resolves" is checked
    return C.judge([(k, None) for k, _ in w["claims"]], w["reply"], w["owners"], w["running"])[0]


def m_loose_threshold(w):        # whole-value match loosened to a substring match
    if not isinstance(w["reply"], dict):
        return C.UNMEASURED
    blob = repr(w["reply"])
    if not any(d.get("found") for d in w["reply"].get("defs") or ()):
        return real(w)
    return C.PASS if all(t in blob for _, t in w["claims"]) else C.FAIL


def m_stale_data(w):             # a reply captured on an earlier, good session is read instead of this one's
    return C.judge(w["claims"], GOOD_REPLY, w["owners"], w["running"])[0]


def m_skip_row(w):               # only the first claim is judged
    return C.judge(w["claims"][:1], w["reply"], w["owners"], w["running"])[0]


def m_swallow(w):                # an exception (or an UNMEASURED) is swallowed into a pass
    try:
        code = real(w)
        if code == C.UNMEASURED:
            raise ValueError("could not measure")
        return code
    except Exception:            # noqa: BLE001  the mutant's whole point
        return C.PASS


def m_crash(w):
    raise KeyError("rows")


MUTANTS = [m_force_pass, m_no_token_assert, m_loose_threshold, m_stale_data, m_skip_row, m_swallow, m_crash]


def t_controls_pass_the_real_proof():
    bad = V.controls(real, WORLDS)
    check(not bad, "the real proof passes every known-good and known-bad control%s" % (": %s" % bad if bad else ""))


def t_product_stream():
    """Each product mutant is seen by the real proof: FAIL where the game answered no, UNMEASURED where it could not."""
    for name, w, want in WORLDS:
        check(real(w) == want, "product %s -> %s" % (name, {0: "PASS", 1: "FAIL", 2: "UNMEASURED"}[want]))


def t_proof_stream():
    for m in MUTANTS:
        exposed = V.controls(m, WORLDS)
        check(bool(exposed), "proof mutant %s is exposed by the controls: %s" % (m.__name__, exposed[:1]))
    green = [m.__name__ for m in MUTANTS if V.controls(m, WORLDS[:1]) == []]
    check({"m_force_pass", "m_stale_data", "m_skip_row", "m_no_token_assert"} <= set(green),
          "the essential mutants return a plausible green on the good world (so only a bad-world control finds them)")


def t_controls_need_a_bad_world():
    """A control set of good worlds only is no control: it passes the forced-PASS proof."""
    check(V.controls(m_force_pass, [w for w in WORLDS if w[2] == C.PASS]) == [],
          "good worlds alone pass a forced PASS (why the bank keeps bad worlds)")
    check(V.controls_refusal([w for w in WORLDS if w[2] == C.PASS]) is not None,
          "controls_refusal refuses a set with no known-bad world")
    check(V.controls_refusal(WORLDS) is None, "and accepts one with good, bad and unreachable worlds")


# ---- the validator stream: the classifier and the routing damaged; the bank must notice ----

def _bank_red():
    bank = V.load()
    red = []
    for c in bank["cases"]:
        try:
            got = V.measure(c)
        except Exception as e:      # noqa: BLE001  a mutant that breaks the rig is caught too
            red.append("%s: %s" % (c["id"], type(e).__name__))
            continue
        red.extend(V.judge(c, got))
    return red


@contextlib.contextmanager
def patched(mod, name, value):
    old = getattr(mod, name)
    setattr(mod, name, value)
    try:
        yield
    finally:
        setattr(mod, name, old)


def t_validator_stream():
    import re
    import relentless as R
    import relentless_live as L
    import relentless_wall as W
    never = re.compile(r"(?!x)x")
    mutants = [
        ("an observed MOD FAIL row is no longer read", L, "MOD_ROW", never),
        ("a harness fault is no longer recognised", L, "EXIT1_HARNESS", never),
        ("an exit 1 that could not ask is a FAIL again", L, "could_not_ask", lambda path: None),
        ("the checker's blindness is no longer read", W, "blind_reason", lambda reasons: None),
        ("a stale build is run anyway", L, "stale_build", lambda fx, sha: (None, [])),
        ("an UNMEASURED check sends work back", R, "unmeasured",
         lambda store, st, said, blind, r, now: R.fail(store, st, "blind_fail", said, r, now)),
    ]
    sys.modules.setdefault("relentless", R)
    with contextlib.redirect_stdout(io.StringIO()):
        base = _bank_red()
    check(base == [], "the unmutated bank is green: %s" % base[:2])
    for what, mod, name, value in mutants:
        with patched(mod, name, value):
            red = _bank_red()
        check(bool(red), "validator mutant killed by the bank: %s (%s)" % (what, red[:1]))


def main():
    for t in (t_controls_pass_the_real_proof, t_product_stream, t_proof_stream, t_controls_need_a_bad_world,
              t_validator_stream):
        t()
    print("RESULT %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
