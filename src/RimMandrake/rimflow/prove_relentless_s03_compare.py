#!/usr/bin/env python3
"""RA_S03_WALL_MEASURE_DID_IT_HELP proof: every number the step 3 section of design/RimMandrake/relentless_TRUST_2026-11-01.md
states is recomputed from the seed results by relentless_trust.compare_report (arm S03 and arm wall, both against step 0).

The seed results (keys, per-case verdicts) live under RM_SEEDS_PRIVATE (default D:\\ClaudeWork\\rimmandrake\\relentless_agent\\seeds),
which the Marker's wall keeps dark on purpose: a copy in the tree would hand every later walled Marker the answer key. So this
runs where the seeds are (the supervisor, through an offbox adapter) and prints numbers and case ids only, never a key, a
reason or a transcript.

Exit 0: every claim holds. 1: a claim and the recomputation disagree (each printed FAIL). 2: UNMEASURED (seeds not readable)."""
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import relentless_trust as T  # noqa: E402

# Every row crosses the wall (relentless_seed_compare): a row may print a case id or a verdict, never the case's key class.

DOC = HERE.parents[2] / "design" / "RimMandrake" / "relentless_TRUST_2026-11-01.md"
HEAD = "## Step 3: the evaluation seeds behind the wall"
fails = []


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        fails.append(what)


def section():
    text = DOC.read_text(encoding="utf-8")
    i = text.find(HEAD)
    if i < 0:
        return None
    j = text.find("\n## ", i + len(HEAD))
    return text[i:j if j > 0 else None]


def table_rows(sec, first):
    """-> {first cell: [cells]} of the table whose header's first cell is `first`."""
    out, on = {}, False
    for ln in sec.splitlines():
        if not ln.startswith("|"):
            on = False
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if cells[0] == first:
            on = True
            continue
        if on and not set(cells[0]) <= set("-"):
            out[cells[0]] = cells[1:]
    return out


def main():
    priv = Path(os.environ.get("RM_SEEDS_PRIVATE") or T.PRIVATE)
    if not (priv / "keys" / "E1.json").is_file() or not (priv / "results_S03").is_dir():
        print("UNMEASURED: seed results not readable at %s (keys/E1.json, results_S03/)" % priv)
        return 2
    sec = section()
    check(sec is not None, "the TRUST doc has a step 3 section")
    if sec is None:
        return 1
    keys = json.loads((priv / "keys" / "E1.json").read_text(encoding="utf-8"))
    cls_of = {k["item"]: k["cls"] for k in keys}
    x, text = T.compare_report(priv, "E1", "S03")
    w, _ = T.compare_report(priv, "E1", "wall")
    print("E1 keys %d; step 0 runs %d, S03 runs %d, wall runs %d" % (len(keys), x["runs"][0], x["runs"][1], w["runs"][1]))

    # 1. the class table, cell for cell, against the code's own render
    doc = table_rows(sec, "Class")
    got = table_rows(text, "Class")
    check(set(doc) == set(T.CLASSES + ("control",)), "class table names every class: %s" % sorted(doc))
    for cls in T.CLASSES + ("control",):
        check(doc.get(cls) == got.get(cls), "class %s: doc %s == recomputed %s" % (cls, doc.get(cls), got.get(cls)))

    # 2. the measure table
    m = table_rows(sec, "Measure")
    n0, n1 = x["runs"]
    v0, v1 = n0 - len(x["base"]["lost"]), n1 - len(x["arm"]["lost"])
    check(m.get("Runs with a verdict") == ["%d of %d" % (v0, n0), "%d of %d" % (v1, n1)],
          "runs with a verdict %s == %d of %d, %d of %d" % (m.get("Runs with a verdict"), v0, n0, v1, n1))
    (r0, u0), (r1, u1) = x["contam_base"], x["contam_arm"]
    check(m.get("Contaminated (a real read of the books or a seat clone)") == [str(len(r0)), str(len(r1))],
          "real reads %s == %d, %d" % (m.get("Contaminated (a real read of the books or a seat clone)"), len(r0), len(r1)))
    check(m.get("Unscanned, lost") == ["%d, %d" % (len(u0), len(x["base"]["lost"])), "%d, %d" % (len(u1), len(x["arm"]["lost"]))],
          "unscanned, lost %s" % m.get("Unscanned, lost"))
    st = ["%.0f / %dk" % (s, round(t / 1000.0)) for s, t in zip(x["secs"], x["tokens"])]
    check(m.get("Median seconds / tokens") == st, "median seconds / tokens %s == %s" % (m.get("Median seconds / tokens"), st))
    check(x["walled_arm"] == n1 and x["walled_base"] == 0, "every S03 run walled (%d of %d), no step 0 run walled (%d)"
          % (x["walled_arm"], n1, x["walled_base"]))

    # 3. the prose claims
    f0, f1 = x["fingerprints"]
    check(len(f0) == 1 and len(f1) == 1 and ("`%s` → `%s`" % (f0[0], f1[0])) in sec,
          "Marker fingerprints %s -> %s named in the doc" % (f0, f1))
    check(("36 of 36 runs gave a verdict" in sec) == (v1 == n1 == 36) and ("At step 0, %d of %d did" % (len(r0), n0)) in sec
          and len(r1) == 0, "in short: %d of %d verdicts behind the wall, none read; step 0 %d of %d read" % (v1, n1, len(r0), n0))
    red = [c for c in ("all_red", "hunk_red")]
    k0 = sum(x["base"]["classes"][c]["caught"] for c in red)
    k1 = sum(x["arm"]["classes"][c]["caught"] for c in red)
    nn0 = sum(x["base"]["classes"][c]["n"] for c in red)
    nn1 = sum(x["arm"]["classes"][c]["n"] for c in red)
    check(k0 == nn0 == k1 == nn1 and ("%d of %d both times" % (k1, nn1)) in sec, "red proofs caught %d/%d then %d/%d" % (k0, nn0, k1, nn1))
    fl = {i: (c, a, b) for i, c, a, b in x["flips"]}
    check(fl.get("SD_FB1AFAA887FD") == ("hunk_green", "FAIL", "PASS") and "SD_FB1AFAA887FD went from FAIL to PASS" in sec,
          "flip SD_FB1AFAA887FD %s" % ("%s>%s" % fl["SD_FB1AFAA887FD"][1:] if "SD_FB1AFAA887FD" in fl else None,))
    cb, ca = x["base"]["control"], x["arm"]["control"]
    check(("from %d of %d to %d of %d" % (cb["false_fail"], cb["n"], ca["false_fail"], ca["n"])) in sec,
          "control false fails %d of %d -> %d of %d" % (cb["false_fail"], cb["n"], ca["false_fail"], ca["n"]))

    # 4. the same-Marker wall arm
    wf = w["fingerprints"]
    npair = sum(sum(p.values()) for p in w["pairs"].values())
    (wr, wu) = w["contam_arm"]
    wc = w["arm"]["control"]
    check(wf[0] == wf[1] == [f0[0]], "wall arm ran step 0's Marker %s" % (wf,))
    check(("holds %d of these cases" % w["runs"][1]) in sec, "wall arm holds %d cases" % w["runs"][1])
    check(npair == 9 and "Nine of them can be paired" in sec and "changed none of those 9" in sec and not w["flips"],
          "wall arm: %d pairs, flips %s" % (npair, ["%s %s>%s" % (i, a, b) for i, _c, a, b in w["flips"]]))
    hg = w["pairs"].get("hunk_green", {}); es = w["pairs"].get("escaped", {}); co = w["pairs"].get("control", {})
    check(hg == {"FAIL>FAIL": 4} and es == {"FAIL>FAIL": 1} and co == {"FAIL>FAIL": 2, "PASS>PASS": 2},
          "wall pairs: 4 hunk_green FAIL, 1 escaped FAIL, 2 control FAIL, 2 control PASS (got %s %s %s)" % (hg, es, co))
    check(len(wr) == 0 and ("but %d of them were `unscanned`" % len(wu)) in sec
          and ("only %d clean reads" % (w["runs"][1] - len(wu))) in sec, "wall arm: real reads %d, unscanned %d" % (len(wr), len(wu)))
    check(("still had %d of %d" % (wc["false_fail"], wc["n"])) in sec, "wall arm control false fails %d of %d" % (wc["false_fail"], wc["n"]))

    # 5. the six step-0 reads, back in the count
    arm = {r["item"]: r.get("verdict") for r in T._load_results(priv, keys, "results_S03")}
    seeds = sorted(arm.get(i) for i in r0 if cls_of.get(i) != "control")
    ctrls = sorted(arm.get(i) for i in r0 if cls_of.get(i) == "control")
    check(seeds == ["FAIL", "FAIL", "WEAK", "WEAK"] and "their four seeds read 2 FAIL and 2 WEAK" in sec,
          "step-0 read seeds behind the wall: %s" % seeds)
    check(ctrls == ["PASS", "WEAK"] and "Their two controls read 1 PASS and 1 WEAK" in sec, "step-0 read controls: %s" % ctrls)

    print("RESULT %s: %d failed" % ("PASS" if not fails else "FAIL", len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
