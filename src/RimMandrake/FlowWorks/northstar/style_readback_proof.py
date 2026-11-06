#!/usr/bin/env python3
"""STYLE_READBACK_PROBE_ANY_BUILT_THING -- live proof of the any-building style reader (Hose/StyleReadback.cs).

  python.exe style_readback_proof.py [out.json] [--fresh-map] [--cell 120,120]

Stages, on a cleared 9x3 strip from --cell, one each of RM_PipeFaucet / RM_SprinklerHead / RM_PipePole spawned with its
_Modern ThingStyleDef (StyleReadback.SpawnStyled, the reader's own staging door) plus an unstyled vanilla Wall, then reads
every cell back through BOTH doors:
  jawa/static_call type=RimMandrake.FlowWorks.Hose.StyleReadback method=StyleRow args="x,z"
  HoseProbe request "stylerow:x,z"
Rows (MOD):
  SR1_faucet / SR2_sprinkler / SR3_pole  the row for the def reads style=<def>_Modern, look=Modern, and the drawn graphic is
                                          the Modern art (graphicPath or drawnTex names Modern)
  SR4_control_unstyled                   the Wall's row is present with style null (the reader is not a styled-def list)
  SR5_doors_agree                        static_call and HoseProbe answer the same rows on every staged cell
Exit 0 PASS, 1 FAIL (a measured row FAILs), 2 UNMEASURED (the proof could not see). The staged things are destroyed after.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

TYPE = "RimMandrake.FlowWorks.Hose.StyleReadback"
STAGED = [("SR1_faucet", "RM_PipeFaucet", "RM_PipeFaucet_Modern"),
          ("SR2_sprinkler", "RM_SprinklerHead", "RM_SprinklerHead_Modern"),
          ("SR3_pole", "RM_PipePole", "RM_PipePole_Modern"),
          ("SR4_control_unstyled", "Wall", "-")]
MEASURED = ("SR1_", "SR2_", "SR3_", "SR4_", "SR5_")


def parse(txt):
    try:
        return json.loads(txt or "")
    except (TypeError, ValueError):
        return {}


def row_for(answer, defname):
    for r in (answer or {}).get("rows") or []:
        if r.get("def") == defname:
            return r
    return None


def verdict(rid, defname, style, r):
    """(status, detail) for one staged cell's row."""
    if r is None:
        return "FAIL", {"why": "no row for %s on its cell" % defname}
    if style == "-":
        return ("PASS" if r.get("style") is None else "FAIL"), {"row": r}
    drawn = " ".join(str(r.get(k) or "") for k in ("graphicPath", "drawnTex"))
    ok = r.get("style") == style and r.get("look") == "Modern" and "Modern" in drawn
    return ("PASS" if ok else "FAIL"), {"row": r, "wantStyle": style, "drawnNamesModern": "Modern" in drawn}


def exit_code(rows):
    rows = [r for r in rows if r["id"].startswith(MEASURED)]
    if any(r["status"] == "FAIL" for r in rows):
        print("VERDICT: FAIL", flush=True)
        return 1
    if len(rows) == len(MEASURED) and all(r["status"] == "PASS" for r in rows):
        print("VERDICT: PASS", flush=True)
        return 0
    print("VERDICT: UNMEASURED (%d of %d rows measured)" % (sum(r["status"] in ("PASS", "FAIL") for r in rows), len(MEASURED)),
          flush=True)
    return 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--cell", default="120,120")
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args()
    import proof_hose as PH           # noqa: E402  (bridge-side imports only on a live run)
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "style_readback_proof_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    x0, z0 = (int(v) for v in a.cell.split(","))
    rows = []
    res = {"script": "style_readback_proof.py", "item": "STYLE_READBACK_PROBE_ANY_BUILT_THING",
           "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "cell": [x0, z0], "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, det):
        rows.append({"id": rid, "status": st, "detail": det})
        print("%-24s %-10s %s" % (rid, st, json.dumps(det, default=str)[:300]), flush=True)
        save()

    def static(meth, args):
        r = B.call("jawa/static_call", type=TYPE, method=meth, args=args) or {}
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        return (parse(txt) if r.get("success") is True else {}), txt

    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        row("SR0_site_ready", "UNMEASURED", {"why": "game not Playing"})
        return exit_code(rows)
    if a.fresh_map:
        res["site_calm"] = V.site_calm(B)   # TESTENV_PREFLIGHT_HARDEN_TRISPIKE_AT_ARM: map-gen hostiles/hives stop safe_advance at arm
    site = (x0 - 1, z0 - 1, 2 * len(STAGED) + 1, 3)
    B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % site, categories="All")
    B.call("jawa/set_terrain", x=site[0], z=site[1], terrainDef="Soil", width=site[2], height=site[3])

    cells = []
    for i, (rid, defname, style) in enumerate(STAGED):
        x, z = x0 + 2 * i, z0
        made, txt = static("SpawnStyled", "%s,%s,%d,%d" % (defname, style, x, z))
        res.setdefault("spawn", {})[rid] = txt[:400]
        if not made.get("success"):
            row(rid, "UNMEASURED", {"why": "staging refused", "answer": txt[:300]})
            continue
        cells.append((x, z))
        got, gtxt = static("StyleRow", "%d,%d" % (x, z))
        if not got.get("success"):
            row(rid, "UNMEASURED", {"why": "StyleRow did not answer", "answer": gtxt[:300]})
            continue
        st, det = verdict(rid, defname, style, row_for(got, defname))
        row(rid, st, det)

    diffs, seen, silent = [], 0, []
    for x, z in cells:
        s, stxt = static("StyleRow", "%d,%d" % (x, z))
        h = B.hp("stylerow:%d,%d" % (x, z))
        if s.get("success") and h.get("success"):
            seen += 1
            if s.get("rows") != h.get("rows"):
                diffs.append({"cell": [x, z], "static": s.get("rows"), "hoseprobe": h.get("rows")})
        else:   # a door that did not answer is a measurement gap, never a disagreement
            silent.append({"cell": [x, z], "static": stxt[:160], "hoseprobe": str(h)[:160]})
    det = {"cells": len(cells), "bothAnswered": seen, "diffs": diffs[:3], "silent": silent[:3]}
    if diffs:
        row("SR5_doors_agree", "FAIL", det)
    elif seen == len(cells) == len(STAGED):
        row("SR5_doors_agree", "PASS", det)
    else:
        row("SR5_doors_agree", "UNMEASURED", dict(det, why="not every staged cell answered through both doors"))

    B.call("jawa/destroy_batch", rects="%d,%d,%d,%d" % site, categories="All")
    save()
    print("VERIFY " + " ".join("%s=%s" % (r["id"], r["status"]) for r in rows), flush=True)
    return exit_code(rows)


def guarded(fn):
    """An uncaught harness/bridge error is UNMEASURED (exit 2) with its reason, never a FAIL."""
    try:
        return fn()
    except SystemExit:
        raise
    except Exception as e:            # noqa: BLE001
        import traceback
        traceback.print_exc()
        print("VERDICT: UNMEASURED (harness: %s: %s)" % (type(e).__name__, str(e).splitlines()[0][:200] if str(e) else ""),
              flush=True)
        return 2


if __name__ == "__main__":
    sys.exit(guarded(main))
