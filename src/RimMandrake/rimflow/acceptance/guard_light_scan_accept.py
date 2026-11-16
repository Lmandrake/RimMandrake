#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_SCAN_SCENES_AGAINST_BARS_TOGGLE_NEVER_TOGGLED (spec:
design/specs/2026-11-15-cheap-guards-at-every-door.md, section "The light scan"). Written by the filing seat; the
builder does not edit it. This half spends no tokens: the model is a fake runner.

    python3 src/RimMandrake/rimflow/acceptance/guard_light_scan_accept.py       # exit 0 and "PASS 14/14" when built

THE CONTRACT IT FIXES: `src/RimMandrake/rimflow/light_scan.py`, one bounded question-list scan, reusable at any door.
  QUESTIONS            {list id: [{"q": id, "text": str}]}, loaded from light_scan_questions.json beside the module;
                       it holds the list "scene_asks_bar" (at least 2 questions).
  scan(list_id, subject, inputs, runner=subprocess.run, model="sonnet", max_input_chars=60000, max_usd=0.25)
      -> {"ran": bool, "ok": bool, "answers": [...], "refusals": [...], "did_not_run": str or None, "usd": float or None}
    inputs  {name: text}: the declared inputs and nothing else. The scan reads no file and has no tools.
    - total input over max_input_chars: did_not_run, the runner is NOT called (never a silent truncation), ok True.
    - model anything but "sonnet" or "opus": ValueError (Haiku is banned; this is a light scan, not a judge).
    - the runner is called once as runner(argv, input=prompt, capture_output=True, text=True, timeout=...), where argv
      starts with the `claude` CLI in print mode and carries "--model" (an alias or an ANTHROPIC_DEFAULT_*_MODEL value
      read from the environment, never a host or account name) and "--max-budget-usd" with max_usd; the prompt holds
      every question's text and every input under its name.
    - the model's stdout must be one JSON object {"answers": [{"q", "answer": "yes"|"no"|"cannot_tell", "evidence"}]}
      with exactly the list's question ids; anything else (not JSON, a missing or extra id, another answer word, a
      non-zero exit, a timeout): did_not_run, ok True. A scan that cannot be read never blocks.
    - each "no" becomes a refusal {"q", "evidence", "would_pass", "smallest_fix"} (all non-empty; a "no" whose evidence
      does not name one of the inputs "<name>:<line>" is did_not_run, not a refusal). "cannot_tell" refuses nothing.
    - ok is False only when there is at least one refusal.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RIMFLOW = os.path.dirname(HERE)
sys.path.insert(0, RIMFLOW)
RESULTS = []


def check(ok, what):
    RESULTS.append(bool(ok))
    print(("ok    " if ok else "FAIL  ") + what)


class Fake(object):
    def __init__(self, out, rc=0, boom=None):
        self.out, self.rc, self.boom, self.calls = out, rc, boom, []

    def __call__(self, argv, **kw):
        self.calls.append((argv, kw))
        if self.boom:
            raise self.boom

        class R(object):
            returncode = self.rc
            stdout = self.out if isinstance(self.out, str) else json.dumps(self.out)
            stderr = ""
        return R()


def main():
    try:
        import light_scan as LS
        qs = LS.QUESTIONS["scene_asks_bar"]
    except Exception as e:  # noqa: BLE001
        LS, qs = None, []
        print("FAIL  light_scan / its question list: %r" % (e,))
    ids = [q.get("q") for q in qs]
    check(len(ids) >= 2 and all(isinstance(q.get("text"), str) and q["text"].strip() for q in qs), "the scene_asks_bar list has at least two questions")
    inputs = {"bar": "The engine can be switched off and the water then stands still.",
              "scene": "def scene(B):\n    B.call('set', on=True)\n    return PASS\n"}

    def run(out, **kw):
        f = Fake(out, **{k: kw.pop(k) for k in ("rc", "boom") if k in kw})
        try:
            return LS.scan("scene_asks_bar", "Fix:bar", kw.pop("inputs", inputs), runner=f, **kw), f
        except Exception as e:  # noqa: BLE001
            return {"raised": repr(e)}, f
    yes = {"answers": [{"q": i, "answer": "yes", "evidence": "scene:2"} for i in ids]}
    r, f = run(yes)
    check(r.get("ran") is True and r.get("ok") is True and r.get("refusals") == [] and len(f.calls) == 1, "all yes: ok, one model call")
    argv, kw = (f.calls or [([], {})])[0]
    flat = " ".join(str(a) for a in argv)
    check("claude" in os.path.basename(str(argv[0] if argv else "")) and "--model" in argv and "--max-budget-usd" in argv
          and "0.25" in flat and "haiku" not in flat.lower(), "the call is the claude CLI with a model and the hard dollar cap")
    prompt = str(kw.get("input") or "") + flat
    check(all(q["text"] in prompt for q in qs) and inputs["bar"] in prompt and "B.call('set', on=True)" in prompt,
          "the prompt holds every question and every declared input")
    no = {"answers": [{"q": ids[0] if ids else "q", "answer": "no", "evidence": "scene:2 writes on=True and never off"}]
          + [{"q": i, "answer": "cannot_tell", "evidence": ""} for i in ids[1:]]}
    r, f = run(no)
    ref = (r.get("refusals") or [{}])[0]
    check(r.get("ok") is False and len(r.get("refusals") or []) == 1 and all(str(ref.get(k) or "").strip() for k in ("q", "evidence", "would_pass", "smallest_fix")),
          "a no is one refusal with evidence, would_pass and smallest_fix; cannot_tell refuses nothing")
    r, f = run(yes, inputs={"bar": "x" * 40000, "scene": "y" * 30000})
    check(r.get("ran") is False and r.get("ok") is True and r.get("did_not_run") and f.calls == [], "inputs over the cap: did not run, no call, no truncation")
    r, f = run("I think the scene is fine.")
    check(r.get("ok") is True and r.get("did_not_run") and not r.get("refusals"), "prose instead of JSON: did not run")
    r, f = run({"answers": yes["answers"][:-1]})
    check(r.get("ok") is True and r.get("did_not_run"), "a missing question id: did not run")
    r, f = run({"answers": yes["answers"] + [{"q": "made_up", "answer": "no", "evidence": "scene:1"}]})
    check(r.get("ok") is True and r.get("did_not_run"), "an extra question id: did not run")
    r, f = run({"answers": [dict(a, answer="probably") for a in yes["answers"]]})
    check(r.get("ok") is True and r.get("did_not_run"), "an answer outside yes/no/cannot_tell: did not run")
    r, f = run({"answers": [dict(a, answer="no", evidence="it just feels thin") for a in yes["answers"]]})
    check(r.get("ok") is True and r.get("did_not_run") and not r.get("refusals"), "a no that cites no input line is not a refusal")
    r, f = run(yes, rc=1)
    check(r.get("ok") is True and r.get("did_not_run"), "a non-zero exit: did not run")
    r, f = run(yes, boom=TimeoutError("slow"))
    check(r.get("ok") is True and r.get("did_not_run"), "a timeout: did not run")
    r, f = run(yes, model="haiku")
    check("ValueError" in str(r.get("raised")) and f.calls == [], "haiku is refused by name, before any call")
    n = sum(RESULTS)
    print("%s %d/%d" % ("PASS" if n == len(RESULTS) else "FAIL", n, len(RESULTS)))
    return 0 if n == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
