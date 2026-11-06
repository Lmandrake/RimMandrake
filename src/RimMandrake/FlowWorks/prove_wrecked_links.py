#!/usr/bin/env python3
"""Live proof of WRECKED_LINKS_FIX_RUINS_SNUB_THEIR_PIPES. Windows python, a quicktest colony, FlowWorks + GimmeSomeSlack:

    python.exe src/RimMandrake/FlowWorks/prove_wrecked_links.py pipes     (A1, also takes the pump site's capture)
    python.exe src/RimMandrake/FlowWorks/prove_wrecked_links.py conduit   (A2)

pipes: RM_WreckedLinksProof.Sweep: a pipe beside each tagged ruin links as beside its repaired tier and not as alone, and the
ruin holds no net role and no power comp. conduit: RuinHookupProof.Sweep: a conduit end beside each tagged ruin hooks into it
in the cord snapshot, as into the repaired tier, and the ruin adds nothing to the power net. Everything staged is destroyed.
Exit 0 PASS, 1 FAIL, 2 UNMEASURED.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
import rimbridge_client as rb  # noqa: E402

PIPES = "RimMandrake.FlowWorks.Machinery.RM_WreckedLinksProof"
CORDS = "RimMandrake.GimmeSomeSlack.RuinHookupProof"
VERDICTS = {"pipes": "RUINLINKS", "conduit": "RUINHOOKS"}


def static(c, typ, method, args=""):
    r = c.call("jawa/static_call", {"type": typ, "method": method, "args": args}, check=False)
    return str(r.get("result") if isinstance(r, dict) else r)


def verdict(text, prefix):
    """The exit code a sweep's reply earns: only its own well-formed line is a verdict."""
    if text.startswith(prefix + " ok=True "):
        return 0
    if text.startswith(prefix + " ok=False "):
        return 1
    print("UNMEASURED: no verdict from the sweep: " + text[:200])
    return 2


def capture(c):
    """The pump test site's picture: evidence for a reader, never part of the verdict."""
    shown = static(c, PIPES, "Stage", "show")
    try:
        if not shown.startswith("SHOWN "):
            print("capture skipped: " + shown[:200])
            return
        x, z, w, h = (int(v) for v in shown.split()[1].split(","))
        r = c.call("rimworld/screenshot_cell_rect", {"x": x, "z": z, "width": w, "height": h, "paddingCells": 2}, check=False)
        print("capture: %s" % (r.get("path") or r.get("screenshotPath") if isinstance(r, dict) else r))
    finally:
        static(c, PIPES, "Stage", "clear")


def main(argv):
    what = argv[1] if len(argv) > 1 else ""
    if what not in VERDICTS:
        print("UNMEASURED: usage: prove_wrecked_links.py pipes|conduit")
        return 2
    h, p, t = rb.resolve_endpoint()
    c = rb.RimBridge(host=h, port=p, token=t, timeout=120)
    c.connect()
    text = static(c, PIPES if what == "pipes" else CORDS, "Sweep")
    print(text)
    if what == "pipes":
        capture(c)
    code = verdict(text, VERDICTS[what])
    print({0: "PASS", 1: "FAIL", 2: "UNMEASURED"}[code])
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
