#!/usr/bin/env python3
"""Failing acceptance case for RIMMANDRAKE_KEEP_UNJUDGED_CHAINS_WHEN_ONLY_CHAIN_FILTERS (Codex, 2026-11-18, reviewing
judge_cli.py on RIMMANDRAKE_EMIT_REFUSAL_RECORDS_FROM_NORTHSTAR_FRAME_FAILS): `judge_cli.py <results> --only-chain A`
rewrites the results file in place with chain B's components deleted, and B's visual bars turn UNMEASURED ("no component
claim to judge") although B was never selected for judging. A mock judge stands in for `claude -p`: no model.
Run: python3 src/RimMandrake/Utils/northstar_driver/case_only_chain_keeps_other_chains.py   (exit 1 while the defect stands)"""
import json
import os
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
from northstar_driver import PASS                       # noqa: E402
from northstar_driver import judge_cli as J              # noqa: E402

PNG = (b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
       b"\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\xc9\xfe\x92\xef"
       b"\x00\x00\x00\x00IEND\xaeB`\x82")


def mock(model, timeout):
    def run(prompt_for, image):
        return True, json.dumps({"type": "result", "is_error": False, "result": json.dumps(
            {"verdict": "YES", "why": "shown", "look": "EXPECTED", "where": "", "first_noticed": "nothing"})})
    return run


def main():
    d = tempfile.mkdtemp()
    comps, bars, texts = [], [], {}
    for chain in ("A", "B"):
        p = os.path.join(d, chain + ".png")
        with open(p, "wb") as f:
            f.write(PNG)
        comps.append({"name": "c" + chain, "chain": chain, "shows": ["bar_" + chain], "screenshots": [p]})
        texts["bar_" + chain] = {"text": "the thing of %s is drawn" % chain, "polarity": "must"}
        bars.append({"id": "bar_" + chain, "visual": True, "status": PASS, "evidence": "state ok"})
    path = os.path.join(d, "results.json")
    with open(path, "w") as f:
        json.dump({"mod": "Mock", "components": comps, "bar_text": texts, "bars": bars, "expected": None}, f)
    J.claude_runner = mock
    J.main([path, "--only-chain", "A", "--no-records"])
    with open(path) as f:
        out = json.load(f)
    wrong = []
    if [c.get("chain") for c in out.get("components") or []] != ["A", "B"]:
        wrong.append("chain B's components were deleted from the saved file: %s" % [c.get("chain") for c in out["components"]])
    b = next((r for r in out.get("bars") or [] if r["id"] == "bar_B"), {})
    if b.get("status") != PASS or b.get("evidence") != "state ok":
        wrong.append("bar_B, never selected, was rewritten: %s / %s" % (b.get("status"), str(b.get("evidence"))[:80]))
    for w in wrong:
        print("WRONG", w)
    print("cases read 2; wrong %d; limit 0" % len(wrong))
    return 1 if wrong else 0


if __name__ == "__main__":
    sys.exit(main())
