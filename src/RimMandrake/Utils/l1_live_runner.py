#!/usr/bin/env python3
"""Run the L1 manifest's def reads against the LIVE bridge (python.exe only; WSL cannot reach the bridge).

Usage (Windows python, cwd holds rimbridge_client.py + the manifest json):
    python.exe l1_live_runner.py l1.json l1_results.json
Per criterion: ONE jawa/get_defs call (`defs` = ';'-joined "DefType/DefName" STRING). Verdicts come only from the
tool's own success / foundCount / notFound fields. A failed ask is UNMEASURED, never ABSENT.
"""
import json, sys
import rimbridge_client as rbc

def main(src, dst):
    man = json.load(open(src))
    host, port, token = rbc.discover_from_log()
    out = []
    with rbc.RimBridge(host, port, token) as rb:
        # sanity probe: a def that must exist, and one that must not
        p = rb.call("jawa/get_defs", {"defs": "ThingDef/Steel;ThingDef/ZZ_NoSuchDef_Probe", "fields": "defName"}, check=False)
        print("PROBE", json.dumps(p)[:400])
        for e in man:
            if not e.get("defs"):
                continue
            try:
                r = rb.call("jawa/get_defs", {"defs": ";".join(e["defs"]), "fields": "defName", "limit": 500}, check=False)
            except Exception as ex:  # noqa
                r = {"success": False, "exception": str(ex)[:300]}
            row = {"item": e["item"], "criterion": e["criterion"], "asked": len(e["defs"]), "success": r.get("success"),
                   "foundCount": r.get("foundCount"), "notFound": r.get("notFound"), "message": (r.get("message") or "")[:200]}
            out.append(row)
            print(row["item"], row["criterion"], row["asked"], row["success"], row["foundCount"], (row["notFound"] or [])[:6])
    json.dump(out, open(dst, "w"), indent=1)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
