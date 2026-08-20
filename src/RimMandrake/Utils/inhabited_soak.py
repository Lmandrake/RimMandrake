"""inhabited_soak.py - the Inhabited architecture gate, driven and diffed.

    python.exe src/RimMandrake/Utils/inhabited_soak.py --setup
    ... save, quit to desktop, relaunch, reload the save ...
    python.exe src/RimMandrake/Utils/inhabited_soak.py --verify

🔴 WINDOWS `python.exe`.

WHAT IS ACTUALLY BEING TESTED. `Inhabited` holds a place's cast as real `Pawn` objects in
a `ThingOwner<Pawn>` on a `WorldObject`, off-map, between visits. `Caravan` is the shipped
model for that shape and it is designed to be TRANSIENT; this uses it for something
PERMANENT, and vanilla never stress-tests that. BUILD found and fixed two of the three ways
it could fail before handing it over (`ShouldTickContents => false`, and staying out of
`WorldPawns` by using `LookMode.Deep`). What is left is whether a deep-held, deliberately
un-ticked pawn comes back WHOLE after a real save/load.

🔑 THE BASELINE CANNOT BE RECONSTRUCTED AFTER THE QUIT. `--setup` writes it to a file for
exactly that reason. A baseline that lives in a terminal is destroyed by the thing being
tested.

WHAT COUNTS AS PASSING: not "the pawns are still there". Three specific things survive -
a Sibling relation to a free colonist, a missing eye, and the Abrasive trait - because
those are the fields that a shallow re-serialisation would quietly drop while leaving a
plausible-looking pawn behind.
"""
import argparse
import io
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rimbridge_client import RimBridge, resolve_endpoint

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
BASELINE = os.path.join(REPO, "infrastructure", "output", "inhabited_soak_baseline.json")
CAT = "Inhabited"


def find_action(rb, label):
    """Read the leaf path; never construct one. Some nodes key on a tab character."""
    for root in ("Actions",):
        r = rb.call("rimworld/list_debug_action_children", {"path": root})
        if not r.get("success"):
            raise RuntimeError("debug tree will not enumerate (%s) - the game may be a zombie"
                               % str(r.get("message"))[:100])
        for c in r.get("children") or []:
            if (c.get("label") or "") == CAT or CAT.lower() in (c.get("path") or "").lower():
                sub = rb.call("rimworld/list_debug_action_children", {"path": c.get("path")})
                for leaf in sub.get("children") or []:
                    if label.lower() in (leaf.get("label") or "").lower():
                        return leaf.get("path")
    return None


def run(rb, label):
    path = find_action(rb, label)
    if not path:
        raise RuntimeError("no debug action matching %r under category %r" % (label, CAT))
    r = rb.call("rimworld/execute_debug_action", {"path": path})
    logs = [str(x.get("message") if isinstance(x, dict) else x)
            for x in ((r.get("effects") or {}).get("logs") or [])]
    return r, logs


def capture_report(logs):
    """The action reports through Log.Message; keep the Inhabited lines in order."""
    return [l for l in logs if "[Inhabited]" in l or "Inhabited" in l]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--setup", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--baseline", default=BASELINE)
    a = ap.parse_args()
    if not (a.setup or a.verify):
        ap.error("pass --setup or --verify")

    host, port, token = resolve_endpoint()
    if not token:
        print("No bridge token - is the game running?")
        return 2

    with RimBridge(host, port, token) as rb:
        gi = rb.call("rimworld/get_game_info", {})
        if gi.get("status") != "game_loaded":
            print("no game loaded (status %s)" % gi.get("status"))
            return 2

        if a.setup:
            steps = []
            for label in ("Create place at current tile", "Stuff roster", "Report roster"):
                r, logs = run(rb, label)
                steps.append({"step": label, "success": r.get("success"), "logs": logs})
                print("- %-32s success=%s  %d log line(s)" % (label, r.get("success"), len(logs)))
                for l in capture_report(logs)[:6]:
                    print("    %s" % l[:160])
            data = {"capturedUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "ticksGame": gi.get("ticksGame"), "steps": steps,
                    "report": capture_report(steps[-1]["logs"])}
            d = os.path.dirname(a.baseline)
            if d and not os.path.isdir(d):
                os.makedirs(d)
            with io.open(a.baseline, "w", encoding="utf-8") as fh:
                fh.write(json.dumps(data, ensure_ascii=False, indent=1))
            print("\nBASELINE -> %s" % a.baseline)
            print("🔴 Now SAVE, then quit to desktop. The baseline above is the only copy.")
            return 0

        # ---- verify ---------------------------------------------------------
        if not os.path.exists(a.baseline):
            print("no baseline at %s - run --setup before the quit, not after" % a.baseline)
            return 2
        base = json.load(io.open(a.baseline, encoding="utf-8"))
        r, logs = run(rb, "Report roster")
        now = capture_report(logs)
        was = base.get("report") or []
        print("baseline captured %s, %d line(s); now %d line(s)" % (base.get("capturedUtc"), len(was), len(now)))

        same = (was == now)
        print("\nIDENTICAL: %s" % ("✅ yes" if same else "❌ no"))
        if not same:
            for i in range(max(len(was), len(now))):
                b = was[i] if i < len(was) else "(absent)"
                n = now[i] if i < len(now) else "(absent)"
                if b != n:
                    print("  line %d\n    was: %s\n    now: %s" % (i, b[:180], n[:180]))

        # The three fields that a shallow re-serialisation drops while leaving a
        # plausible pawn behind. Checked by name, not by counting lines.
        joined = "\n".join(now)
        for probe, why in (("Sibling", "the cross-reference to a free colonist"),
                           ("eye", "the missing-eye hediff"),
                           ("Abrasive", "the trait")):
            hit = re.search(probe, joined, re.I) is not None
            print("  %s %-10s %s" % ("✅" if hit else "🔴", probe, why))
        return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
