#!/usr/bin/env python3
"""Acceptance for RIMMANDRAKE_WRITE_REVIEW_BRIEF_CALIBRATE_ON_THIRTY_FIVE_CLAIMS.

The code-review brief of design/specs/2026-11-18-review-growth-cycle/01-design.md section 5.3 exists as a role file, the
refusal contract knows a `code_review` family, and that family is CALIBRATED on the labelled claims of 2026-11-18
(4 problems, 31 polish). Codex and GPT reviews of pipeline code do not wait for this (owner, card 2026-11-23;
standing_rulings.md, section "A boundary page before pipeline code"). Exit 0 = every check passes (expected: 4)."""
import json
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
import refusal_contract as RC  # noqa: E402

BRIEF = os.path.join(REPO, "src", "RimMandrake", "rimflow", "roles", "code_review.md")
FAILS = []


def check(name, ok, got=""):
    print("%s %s %s" % ("ok  " if ok else "FAIL", name, "" if ok else got))
    FAILS.append(name) if not ok else None


text = open(BRIEF, encoding="utf-8").read() if os.path.isfile(BRIEF) else ""
check("the brief exists: %s" % os.path.relpath(BRIEF, REPO), bool(text))
check("the brief names the page's parts and the two looks", all(w in text for w in ("ACCEPTS", "DOES NOT SURVIVE", "PROMISES",
                                                                                    "polish.md", "next_version.md")), "missing words")
row = RC.load_calibration()["families"].get("code_review") or {}
check("the refusal contract has a code_review family whose brief is that file",
      any(str(b).endswith("roles/code_review.md") for b in row.get("brief") or []), json.dumps(row)[:200])
check("the code_review family is CALIBRATED now", RC.status("code_review") == "CALIBRATED", RC.status("code_review") if row else "no family")
print("FAILED %d" % len(FAILS) if FAILS else "PASS code_review_brief_accept (4 checks)")
sys.exit(1 if FAILS else 0)
