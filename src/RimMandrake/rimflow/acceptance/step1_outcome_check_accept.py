#!/usr/bin/env python3
"""Acceptance for plan.md step 1: an outcome check on a list item, run by a program.

Contract: a new module src/RimMandrake/rimflow/list_effect.py, and `rimflow file --effect`.
  parse(text) -> {"kind": "path-has"|"path-lacks"|"cmd", ...} or {"kind": "unreadable", "why": str}; never raises.
      forms: "path-has:<repo path>::<text>", "path-lacks:<repo path>::<text>", "cmd:<shell command>"
  holds(text, root) -> "holds" | "fails" | "unmeasured"   (could-not-look is never "holds" and never "fails")
  decide(item, verdict) -> "close" | "work" | "blind" | "no_effect" | "closed"
      item = {"state": "open"|"doing"|"done"|..., "effect": str or None}
Expected when built: PASS 15/15.  Today: FAIL 0/15, because list_effect.py does not exist."""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _harness as H  # noqa: E402

LE, why = H.load("list_effect")
ROOT = tempfile.mkdtemp(prefix="outcome_check_")
with open(os.path.join(ROOT, "page.md"), "w", encoding="utf-8") as f:
    f.write("The plan runs to 2026-11-29.\nrulings A11 (open question)\n")


def need():
    if LE is None:
        raise RuntimeError(why)
    return LE


H.check("parse reads path-has", lambda: need().parse("path-has:page.md::2026-11-29")["kind"] == "path-has")
H.check("parse reads cmd", lambda: need().parse("cmd:true")["kind"] == "cmd")
H.check("parse of an unknown form is unreadable with a reason, not an exception",
        lambda: need().parse("looks-done")["kind"] == "unreadable" and need().parse("looks-done")["why"])
H.check("parse of empty text is unreadable", lambda: need().parse("")["kind"] == "unreadable")
H.check("path-has holds when the page holds the text", lambda: need().holds("path-has:page.md::2026-11-29", ROOT) == "holds")
H.check("path-has fails when the page lacks the text", lambda: need().holds("path-has:page.md::2026-12-25", ROOT) == "fails")
H.check("path-has on a missing page fails (the text is not there)",
        lambda: need().holds("path-has:absent.md::x", ROOT) == "fails")
H.check("path-lacks fails while the stale text is still there",
        lambda: need().holds("path-lacks:page.md::(open question)", ROOT) == "fails")
H.check("path-lacks on a missing page is unmeasured, never holds",
        lambda: need().holds("path-lacks:absent.md::x", ROOT) == "unmeasured")
H.check("cmd holds on exit 0 and fails on exit 1",
        lambda: need().holds("cmd:true", ROOT) == "holds" and need().holds("cmd:false", ROOT) == "fails")
H.check("a command that cannot run is unmeasured",
        lambda: need().holds("cmd:/no/such/program-xyz", ROOT) == "unmeasured")
H.check("an unreadable check is unmeasured", lambda: need().holds("looks-done", ROOT) == "unmeasured")
H.check("decide: holds closes, fails is work, unmeasured is blind",
        lambda: [need().decide({"state": "open", "effect": "cmd:true"}, v) for v in ("holds", "fails", "unmeasured")]
        == ["close", "work", "blind"])
H.check("decide: an item with no check is never closed or worked by the program; a closed item stays closed",
        lambda: need().decide({"state": "open", "effect": None}, "holds") == "no_effect"
        and need().decide({"state": "done", "effect": "cmd:true"}, "fails") == "closed")
H.check("rimflow file takes --effect",
        lambda: "--effect" in subprocess.run([sys.executable, os.path.join(H.RIMFLOW, "cli.py"), "file", "--help"],
                                             capture_output=True, text=True, timeout=60).stdout)
H.done(15)
