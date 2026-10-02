"""modcheck.jev_triage -- the guarded, SHADOW-MODE caller for Jev (see jev_questions.py).

Every public function returns a plain dict and never raises:
    {"status": "UNAVAILABLE"|"SHADOW"|"ACTED"|"ERROR", "verdict": <choice or None>, "answers": {...}, ...}
  UNAVAILABLE  no key / no package / network down: the harness is whole without Jev (same law as the in-game LLM).
  SHADOW       answered and logged; NOT acted on because a threshold in jev_questions is None (unmeasured).
  ACTED        every threshold needed is set and every guard agreed; the verdict is a ROUTING TAG only.
Answers are appended to Transient/modcheck/jev_shadow.jsonl so thresholds can be measured against them.

`ask` is injectable (tests pass a stub). Guards run in separate calls with only their named fields.
"""
import json
import os
import sys
import time

import jev_questions as Q

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_HERE))))
SHADOW_LOG = os.path.join(ROOT, "Transient", "modcheck", "jev_shadow.jsonl")


def _real_ask():
    """consultjev.ask from CONSULTJEV_PATH (default ~/dev/ConsultJev); (None, reason) if unusable."""
    path = os.environ.get("CONSULTJEV_PATH") or os.path.join(os.path.expanduser("~"), "dev", "ConsultJev")
    if path not in sys.path and os.path.isdir(path):
        sys.path.insert(0, path)
    try:
        from consultjev.client import ask, load_api_key
        load_api_key()
    except Exception as e:                                   # noqa: BLE001 - no package, no key, anything
        return None, "%s: %s" % (type(e).__name__, str(e)[:160])
    return ask, ""


def _log(row):
    try:
        os.makedirs(os.path.dirname(SHADOW_LOG), exist_ok=True)
        with open(SHADOW_LOG, "a") as f:
            f.write(json.dumps(row, default=str) + "\n")
    except OSError:
        pass


def _pick(state, fields):
    return dict((k, state[k]) for k in fields if k in state)


def _flatten(resp, ids):
    out = {}
    for qid in ids:
        a = resp[qid] if hasattr(resp, "__getitem__") else resp.answers[qid]
        out[qid] = {"type": a.type, "noul": a.noul, "choice": a.choice, "score": a.score,
                    "confidence": a.confidence, "probabilities": dict(a.probabilities or {})}
    return out


def _run(kind, state, ask=None, log=True, extra=None):
    """One verdict question (full state) + its guards (own calls, reduced states)."""
    if ask is None:
        ask, why = _real_ask()
        if ask is None:
            return {"status": "UNAVAILABLE", "kind": kind, "why": why, "verdict": None, "answers": {}}
    t0 = time.time()
    try:
        battery = Q.BATTERIES[kind]
        resp = ask(state, battery, model=Q.MODEL)
        answers = _flatten(resp, list(battery))
        for qid, q, fields in Q.GUARDS.get(kind, []):
            gresp = ask(_pick(state, fields), {qid: q}, model=Q.MODEL)
            answers.update(_flatten(gresp, [qid]))
    except Exception as e:                                   # noqa: BLE001 - never raise into a run
        return {"status": "ERROR", "kind": kind, "why": "%s: %s" % (type(e).__name__, str(e)[:200]),
                "verdict": None, "answers": {}}
    verdict = next(iter(answers.values()))["choice"] if answers else None
    out = {"status": "SHADOW", "kind": kind, "verdict": verdict, "answers": answers,
           "elapsed_ms": int((time.time() - t0) * 1000), "extra": extra or {}}
    if log:
        _log({"when": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "kind": kind, "state": state, "result": out})
    return out


def _gate_ok(ans, tgate):
    return tgate is not None and ans.get("confidence") is not None and ans["confidence"] >= tgate


# -------------------------------------------------------------------- public functions
def classify_def(def_type, def_name, label, description, ask=None, log=True):
    """Rank 1. ACTED only when T_GATE, T_DESCRIBED (and T_HURTS for the dangerous branch) are SET and agree."""
    r = _run("def_harm", {"def_type": def_type, "def_name": def_name, "label": label, "description": description},
             ask=ask, log=log)
    if r["status"] != "SHADOW":
        return r
    a = r["answers"]
    needed = (Q.T_GATE, Q.T_DESCRIBED)
    if any(t is None for t in needed):
        return r
    v = a["DEF_HARM"]["choice"]
    ok = (_gate_ok(a["DEF_HARM"], Q.T_GATE) and a["DEF_IS_DESCRIBED"]["noul"] is not None
          and a["DEF_IS_DESCRIBED"]["noul"] >= Q.T_DESCRIBED)
    if v == "injures_or_kills":
        ok = ok and Q.T_HURTS is not None and (a["DEF_HURTS_DIRECTLY"]["noul"] or 0) >= Q.T_HURTS
    r["status"] = "ACTED" if ok else "SHADOW"
    r["fail_safe"] = not ok          # disagreement => treat as SURPRISE-severity until a human labels it
    return r


def route_failure(failure_message, surprises_during=(), ask=None, log=True):
    """Rank 2. `outside_event` is only ever asserted if CODE saw a surprise during the component; Jev alone
    may not claim it. The result is a routing TAG for a rimflow finding, never a PASS and never a verdict."""
    r = _run("fail_route", {"failure_message": failure_message, "surprises_during": list(surprises_during)},
             ask=ask, log=log, extra={"code_saw_surprise": bool(surprises_during)})
    if r["status"] != "SHADOW":
        return r
    a = r["answers"]
    v = a["FAIL_ROUTE"]["choice"]
    if any(t is None for t in (Q.T_GATE, Q.T_PARAM_OR_TYPE)):
        return r
    ok = _gate_ok(a["FAIL_ROUTE"], Q.T_GATE)
    if v == "outside_event":
        ok = ok and bool(surprises_during)
    if v == "harness_mistake":
        ok = ok and (a["MSG_NAMES_PARAM_OR_TYPE"]["noul"] or 0) >= Q.T_PARAM_OR_TYPE
    r["status"] = "ACTED" if ok else "SHADOW"
    return r


def lint_vacuous_test(test_intent, stimulus_summary, observed_assertion, ask=None, log=True):
    """GPT-review idea #1: needs NO game. A review flag only; it never turns anything into a PASS."""
    r = _run("vacuous", {"test_intent": test_intent, "stimulus_summary": stimulus_summary,
                         "observed_assertion": observed_assertion}, ask=ask, log=log)
    if r["status"] != "SHADOW" or any(t is None for t in (Q.T_GATE, Q.T_OBSERVED_READBACK)):
        return r
    a = r["answers"]
    flagged = a["VACUOUS_TEST"]["choice"] in ("setup_only", "tests_different_claim")
    r["flag"] = bool(flagged and _gate_ok(a["VACUOUS_TEST"], Q.T_GATE)
                     and (a["OBSERVED_IS_READBACK"]["noul"] or 1) <= Q.T_OBSERVED_READBACK)
    r["status"] = "ACTED"
    return r


def audit_exemption(test_intent, detector, exemption, phase, ask=None, log=True):
    r = _run("exemption", {"test_intent": test_intent, "detector": detector, "exemption": exemption, "phase": phase},
             ask=ask, log=log)
    return r


def classify_cause(pawn_record, test_actions=(), ask=None, log=True):
    """Rank 3. CODE FIRST: the hediff-to-cause table in detectors answers exactly when it yields one class;
    Jev is asked only when it yields none or several (honest 'unknown')."""
    try:
        import detectors as D
        classes = sorted({D.HEDIFF_CAUSE.get(h.get("def")) for h in pawn_record.get("new_hediffs", [])} - {None})
    except Exception:                                        # noqa: BLE001
        classes = []
    if len(classes) == 1:
        return {"status": "ACTED", "kind": "cause", "verdict": classes[0], "answers": {}, "source": "code_table"}
    state = dict(pawn_record)
    state["test_actions"] = list(test_actions)
    r = _run("cause", state, ask=ask, log=log, extra={"code_classes": classes})
    r["source"] = "jev"
    return r


def triage_summary(summary, ask=None):
    """Post-run shadow pass over a run_suite summary: route every FAIL component. Never raises; returns the
    list of results (also logged). Jev absent => one UNAVAILABLE entry, harmlessly."""
    out = []
    try:
        for ch in summary.get("chains", []):
            for c in ch.get("components", []):
                if c.get("verdict") == "FAIL":
                    sp = (c.get("surprises") or {}).get("hits") or []
                    out.append(dict(route_failure(c.get("detail", ""), [h.get("summary") for h in sp], ask=ask),
                                    component=c.get("name"), chain=ch.get("name")))
                    if out[-1]["status"] == "UNAVAILABLE":
                        break
            if out and out[-1]["status"] == "UNAVAILABLE":
                break
    except Exception as e:                                   # noqa: BLE001
        out.append({"status": "ERROR", "why": repr(e)})
    return out
