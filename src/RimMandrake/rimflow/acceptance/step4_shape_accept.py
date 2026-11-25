#!/usr/bin/env python3
"""Acceptance for plan.md step 4 (the Shape stage of the Workshop Pipeline): the program around the Shape run. What a
Shape run writes is a model's work and is judged by the weekly audit; this script tests the exit rule.

Contract: a new module src/RimMandrake/rimflow/list_shape.py
  needs_shape_run(item) -> bool      item = {"effect": str or None, "route": dict or None, "parts": list or None}
  shaped(parts) -> {"shaped": bool, "unshaped": [part names], "weak": [part names]}
      part = {"name", "effect": str or None, "fooled_by": str or None, "route": None or {"who", "ask", "resumes"}}
      a part is shaped when it has an outcome check, or a route with all three of who, ask and resumes.
      "weak" names each part whose check has no "what would pass this check and leave the need unmet" line
      (fooled_by). Weak is a mark for the page and the audit. Weak never makes "shaped" False.
  ROUTES -> the allowed "who" values: "judge", "owner", "conductor", "review"
Expected when built: PASS 12/12.  Today: FAIL 0/12, because list_shape.py does not exist."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _harness as H  # noqa: E402

LS, why = H.load("list_shape")
R_OK = {"who": "owner", "ask": "pick one of two designs", "resumes": "his card answer"}


def ls():
    if LS is None:
        raise RuntimeError(why)
    return LS


def part(name="p1", effect="path-has:page.md::text", fooled_by="the text in an appendix while the old line stays", route=None):
    return {"name": name, "effect": effect, "fooled_by": fooled_by, "route": route}


H.check("an item filed with its check needs no Shape run (the fast path)",
        lambda: ls().needs_shape_run({"effect": "cmd:true", "route": None, "parts": None}) is False)
H.check("an item with no check, no route and no parts needs a Shape run",
        lambda: ls().needs_shape_run({"effect": None, "route": None, "parts": None}) is True)
H.check("an item already routed needs no Shape run",
        lambda: ls().needs_shape_run({"effect": None, "route": R_OK, "parts": None}) is False)
H.check("every part with a check: shaped", lambda: ls().shaped([part("a"), part("b")])["shaped"] is True)
H.check("a part with a full route and no check: shaped",
        lambda: ls().shaped([part("a"), part("b", effect=None, fooled_by=None, route=R_OK)])["shaped"] is True)
H.check("a part with neither is named, and the item is not shaped",
        lambda: ls().shaped([part("a"), part("b", effect=None, fooled_by=None)]) ["unshaped"] == ["b"]
        and ls().shaped([part("a"), part("b", effect=None, fooled_by=None)])["shaped"] is False)
H.check("a route that does not say what resumes the item is not a hand-over",
        lambda: ls().shaped([part("a", effect=None, fooled_by=None,
                                  route={"who": "conductor", "ask": "choose", "resumes": ""})])["unshaped"] == ["a"])
H.check("a route to nobody we know is not a hand-over",
        lambda: ls().shaped([part("a", effect=None, fooled_by=None,
                                  route={"who": "someone", "ask": "x", "resumes": "y"})])["shaped"] is False)
H.check("no parts at all is not shaped (an empty split is not a split)", lambda: ls().shaped([])["shaped"] is False)
H.check("a check with no 'what would fool this' line is marked weak",
        lambda: ls().shaped([part("a", fooled_by=None), part("b")])["weak"] == ["a"])
H.check("weak is a mark, never a stop", lambda: ls().shaped([part("a", fooled_by="")])["shaped"] is True)
H.check("the four routes are judge, owner, conductor and review",
        lambda: sorted(ls().ROUTES) == ["conductor", "judge", "owner", "review"])
H.done(12)
