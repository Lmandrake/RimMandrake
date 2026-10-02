"""Offline selftest for jev_triage/jev_questions with a STUB ask (no network, no key).

Checks the rules that make Jev safe here: shadow by default, guards blind and in their own calls, code
speaks first, Jev absent never breaks a run, and nothing can claim 'outside_event' without code seeing one.
Run: python3 selftest_jev.py
"""
import json
import os
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import jev_questions as Q    # noqa: E402
import jev_triage as J       # noqa: E402

_r = []


def check(name, cond, detail=""):
    _r.append(bool(cond))
    print("%s %s%s" % ("ok  " if cond else "FAIL", name, ("  -- " + detail) if (detail and not cond) else ""))


class A(object):
    def __init__(self, qid, typ, noul=None, choice=None, conf=None):
        self.question_id, self.type, self.noul, self.choice = qid, typ, noul, choice
        self.score, self.confidence, self.probabilities, self.legend = None, conf, {}, {}


class Stub(object):
    """Answers every question from `script`: qid -> (noul|choice, confidence). Records every call."""
    def __init__(self, script):
        self.script, self.calls = script, []

    def __call__(self, state, questions, model=None):
        self.calls.append((dict(state), list(questions)))
        out = {}
        for qid, q in questions.items():
            v, conf = self.script[qid]
            out[qid] = A(qid, q["type"], noul=v if q["type"] == "noul" else None,
                         choice=v if q["type"] == "choice" else None, conf=conf)
        return out


def main():
    J.SHADOW_LOG = os.path.join(tempfile.mkdtemp(prefix="np_jev_"), "shadow.jsonl")
    save = dict((k, getattr(Q, k)) for k in dir(Q) if k.startswith("T_"))

    # every threshold ships UNMEASURED
    check("every shipped threshold is None (UNMEASURED)", all(v is None for v in save.values()), str(save))

    # --- Jev absent never breaks anything
    J._real_ask = lambda: (None, "no key")
    r = J.route_failure("x")
    check("no key => UNAVAILABLE, no exception, nothing logged", r["status"] == "UNAVAILABLE" and not os.path.exists(J.SHADOW_LOG))

    # --- shadow by default
    script = {"FAIL_ROUTE": ("harness_mistake", 0.99), "MSG_NAMES_PARAM_OR_TYPE": (0.97, None)}
    s = Stub(script)
    r = J.route_failure("severity ratio 4.17x ... type '700' vs 700.0", ["Raid: X"], ask=s)
    check("answers with every threshold None are SHADOW (acted on nothing)", r["status"] == "SHADOW" and r["verdict"] == "harness_mistake")
    check("the answer was logged for later threshold measurement",
          os.path.exists(J.SHADOW_LOG) and json.loads(open(J.SHADOW_LOG).readline())["kind"] == "fail_route")

    # --- guards are BLIND and in their own call
    check("two calls were made: verdict then guard", len(s.calls) == 2)
    check("the guard call saw ONLY failure_message (not surprises_during)", s.calls[1][0] == {"failure_message": "severity ratio 4.17x ... type '700' vs 700.0"}, str(s.calls[1][0]))
    check("the verdict call did not contain the guard question", "MSG_NAMES_PARAM_OR_TYPE" not in s.calls[0][1])
    s = Stub({"DEF_HARM": ("harmless", 0.9), "DEF_IS_DESCRIBED": (0.9, None), "DEF_HURTS_DIRECTLY": (0.1, None)})
    J.classify_def("HediffDef", "X", "X", "Quietly plays a flute.", ask=s, log=False)
    check("def guards see only `description`", all(set(c[0]) == {"description"} for c in s.calls[1:]) and len(s.calls) == 3)

    # --- with thresholds SET the combination rules apply
    Q.T_GATE, Q.T_PARAM_OR_TYPE = 0.5, 0.5
    r = J.route_failure("fire on the map", [], ask=Stub({"FAIL_ROUTE": ("outside_event", 0.99), "MSG_NAMES_PARAM_OR_TYPE": (0.1, None)}), log=False)
    check("Jev alone may NOT claim outside_event (no code-side surprise) -> not ACTED", r["status"] == "SHADOW", r["status"])
    r = J.route_failure("fire on the map", ["13 fires"], ask=Stub({"FAIL_ROUTE": ("outside_event", 0.99), "MSG_NAMES_PARAM_OR_TYPE": (0.1, None)}), log=False)
    check("with a code-side surprise outside_event is ACTED", r["status"] == "ACTED")
    r = J.route_failure("x", [], ask=Stub({"FAIL_ROUTE": ("harness_mistake", 0.99), "MSG_NAMES_PARAM_OR_TYPE": (0.1, None)}), log=False)
    check("harness_mistake needs its guard: a weak guard => not ACTED", r["status"] == "SHADOW")
    r = J.route_failure("x", [], ask=Stub({"FAIL_ROUTE": ("harness_mistake", 0.3), "MSG_NAMES_PARAM_OR_TYPE": (0.9, None)}), log=False)
    check("a confident-sounding but sub-gate verdict is not ACTED (confidence is a gate)", r["status"] == "SHADOW")
    for k, v in save.items():
        setattr(Q, k, v)

    # --- code speaks first
    s = Stub({"CAUSE": ("fire", 0.9), "GUARD_HEDIFF_IS_INJURY": (0.9, None), "GUARD_THREAT_PRESENT": (0.1, None)})
    r = J.classify_cause({"new_hediffs": [{"def": "Burn"}]}, ask=s, log=False)
    check("one hediff class from the code table answers without calling Jev", r["verdict"] == "fire" and r["source"] == "code_table" and not s.calls)
    r = J.classify_cause({"new_hediffs": [{"def": "Burn"}, {"def": "Bite"}]}, ask=s, log=False)
    check("two classes (or none) go to Jev", r["source"] == "jev" and len(s.calls) == 3, str(len(s.calls)))

    # --- failures never raise
    def boom(*a, **k):
        raise RuntimeError("network down")
    r = J.lint_vacuous_test("a", "b", "c", ask=boom, log=False)
    check("a failing ask yields ERROR, never an exception", r["status"] == "ERROR")

    # --- the lint flags a vacuous assertion only when measured thresholds exist
    Q.T_GATE, Q.T_OBSERVED_READBACK = 0.5, 0.5
    r = J.lint_vacuous_test("droid detonates", "spawn droid, damage it", "damage call returned success",
                            ask=Stub({"VACUOUS_TEST": ("setup_only", 0.9), "OBSERVED_IS_READBACK": (0.1, None)}), log=False)
    check("a setup_only verdict with a 'not a read-back' guard is flagged", r.get("flag") is True)
    r = J.lint_vacuous_test("droid detonates", "spawn droid, damage it", "explosion row present after",
                            ask=Stub({"VACUOUS_TEST": ("setup_only", 0.9), "OBSERVED_IS_READBACK": (0.95, None)}), log=False)
    check("control: the guard says it IS a read-back => not flagged", r.get("flag") is False)
    for k, v in save.items():
        setattr(Q, k, v)

    # --- post-run triage only touches FAIL components and stops at UNAVAILABLE
    summ = {"chains": [{"name": "c", "components": [
        {"name": "a", "verdict": "PASS", "detail": ""}, {"name": "b", "verdict": "FAIL", "detail": "boom"},
        {"name": "c", "verdict": "FAIL", "detail": "boom2"}]}]}
    s = Stub({"FAIL_ROUTE": ("mod_behaviour", 0.9), "MSG_NAMES_PARAM_OR_TYPE": (0.1, None)})
    out = J.triage_summary(summ, ask=s)
    check("triage routes exactly the FAIL components", [o["component"] for o in out] == ["b", "c"])
    J._real_ask = lambda: (None, "no key")
    out = J.triage_summary(summ)
    check("with Jev unavailable triage returns one UNAVAILABLE and stops", len(out) == 1 and out[0]["status"] == "UNAVAILABLE")

    n = sum(_r)
    print("\n%d/%d passed" % (n, len(_r)))
    return 0 if n == len(_r) else 1


if __name__ == "__main__":
    sys.exit(main())
