#!/usr/bin/env python3
"""FAUNA_LORE_DIVERSIFICATION_1: the divergence manifest is sound and the graph regenerates.

1. The committed manifest passes fauna_divergence_graph.check (every row off the 12-15 band in
   its stated direction, ruled_best = K x bodySize, a reason, the delegated-judge ruling, a
   defName present in the roster snapshot).
2. Every manifest row traces to an accept/adjust verdict in the committed judge record, with the
   same K; no rejected row slipped in.
3. Planted faults are caught (in-band K, wrong direction, unknown defName, missing ruling) —
   the checker can see.
4. The graph draws to a temp PNG of plausible size.
"""
import csv
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fauna_divergence_graph as g  # noqa: E402

VERDICT = os.path.join(g.ROOT, "design", "Jawa", "worldbuilding", "fauna_lore_divergence_2026-11-02",
                       "judge_verdict.md")


def main():
    fails = []
    manifest, roster = g.load(g.MANIFEST), g.load(g.ROSTER)
    bad = g.check(manifest, roster)
    fails += ["manifest: " + b for b in bad]
    if len(manifest) < 10:
        fails.append("manifest has only %d rows" % len(manifest))

    text = open(VERDICT, encoding="utf-8").read()
    body = text.split("```csv", 1)[1].split("```", 1)[0].strip()
    verdict = {r["defName"]: r for r in csv.DictReader(io.StringIO(body))}
    if len(verdict) < 30:
        fails.append("judge verdict parsed only %d rows" % len(verdict))
    for r in manifest:
        v = verdict.get(r["defName"])
        if not v:
            fails.append("%s: no judge verdict" % r["defName"])
        elif v["verdict"] not in ("accept", "adjust"):
            fails.append("%s: judge said %s" % (r["defName"], v["verdict"]))
        elif abs(float(v["K_final"]) - float(r["K_ruled"])) > 1e-6:
            fails.append("%s: K %s != judge K_final %s" % (r["defName"], r["K_ruled"], v["K_final"]))
    endorsed = {d for d, v in verdict.items() if v["verdict"] in ("accept", "adjust")}
    missing = endorsed - {r["defName"] for r in manifest}
    if missing:
        fails.append("endorsed by the judge but absent from the manifest: %s" % sorted(missing))

    base = dict(manifest[0])
    plants = {
        "in-band K": dict(base, K_ruled="13", ruled_best=str(round(13 * float(base["bodySize"]), 1))),
        "wrong direction": dict(base, direction="harmless" if base["direction"] == "terror" else "terror"),
        "unknown defName": dict(base, defName="RM_NoSuchBeast"),
        "missing ruling": dict(base, ruling="my own idea"),
    }
    for name, row in plants.items():
        if not g.check([row], roster):
            fails.append("planted fault not caught: " + name)

    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "g.png")
        g.draw(manifest, roster, out)
        size = os.path.getsize(out) if os.path.exists(out) else 0
        if size < 20000:
            fails.append("graph PNG missing or tiny (%d bytes)" % size)

    for f in fails:
        print("FAIL", f)
    if fails:
        return 1
    print("PASS: %d divergences, all judge-endorsed, off-band, graph regenerates; 4 planted faults caught"
          % len(manifest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
