#!/usr/bin/env python3
"""selftest_sheet_letters.py — a per-biome sheet's column letters are STABLE across rebuilds.

Pure in-memory (no store, no ledger, no game). Proves the guarantees `art_sheet.py --biome` relies on so an
owner-ruled decisions file keeps resolving to the pictures he ruled on:
  * a set that is still found keeps its letter even when newer renders are listed first;
  * a genuinely new set takes the next letter never used on the row (append-only);
  * a vanished set's letter is never reused, including across a second rebuild (`reserved`);
  * a vanished set a decision still names is carried forward as a KEPT column with its exact pictures;
  * the ruled snapshot's letters win over a later rebuild's drift;
  * letter_mismatches checks only the letters a decision uses.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import art_sheet as S  # noqa: E402
import artledger as L  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def col(**faces):
    return {"kind": "artpipe", "faces": dict(faces), "label": "render x"}


def letters(cols):
    return {c["letter"]: c["faces"] for c in cols}


def main():
    a, b, c = {"south": "a1"}, {"south": "b1"}, {"south": "c1"}
    # first build: three sets lettered afresh
    cols = [col(**a), col(**b), col(**c)]
    S._assign_letters(cols, {})
    ruled = letters(cols)
    check(ruled == {"A": a, "B": b, "C": c}, "fresh row letters A, B, C")

    # rebuild: two NEW renders listed first, set A gone, B and C still found
    n1, n2 = {"south": "n1"}, {"south": "n2"}
    mem = S._merge_memory({"r": {"columns": ruled}}, {})["r"]
    cols2 = [col(**n1), col(**n2), col(**c), col(**b)]
    S._assign_letters(cols2, mem["columns"], mem["reserved"])
    got = letters(cols2)
    check(got.get("B") == b and got.get("C") == c, "surviving sets keep their letters though newer renders sort first")
    check(got.get("D") == n1 and got.get("E") == n2, "new sets take the next never-used letters (D, E)")
    check("A" not in got, "vanished set's letter A is not handed to a new set")

    # a decision names the vanished A: it is carried forward with its exact pictures
    kept = S._kept_cols(cols2, mem, {"A", "B"})
    check(len(kept) == 1 and kept[0]["letter"] == "A" and kept[0]["faces"] == a and kept[0]["kind"] == "kept",
          "a ruled letter whose set vanished comes back as a KEPT column with the same pictures")
    check(S._short(kept[0]).startswith("KEPT"), "KEPT column says so in its header")

    # second rebuild from the later snapshot alone: A stays reserved, never reused
    later = {"r": {"columns": got, "reserved": sorted(set(got) | set(mem["reserved"]))}}
    mem3 = S._merge_memory({}, later)["r"]
    cols3 = [col(south="n3"), col(**b)]
    S._assign_letters(cols3, mem3["columns"], mem3["reserved"])
    check(letters(cols3) == {"B": b, "F": {"south": "n3"}}, "reserved letters survive a second rebuild (new set is F, not A)")

    # the ruled snapshot wins over a later snapshot that drifted
    drift = {"r": {"columns": {"B": c, "C": b, "D": n1}}}
    mem4 = S._merge_memory({"r": {"columns": ruled}}, drift)["r"]
    check(mem4["columns"]["B"] == b and mem4["columns"]["C"] == c and mem4["columns"]["D"] == n1,
          "ruled letters win over a drifted later snapshot; its genuinely new sets are kept")

    # letter_mismatches: only used letters, only letters the ruled snapshot had
    dec = {"decisions": {"r": {"decision": "B", "variants": ["C"], "picks": {"g": "Z"}}, "q": {"decision": "redo"}}}
    now_ok = {"rows": {"r": {"columns": {"B": b, "C": c, "D": n1}}}}
    now_bad = {"rows": {"r": {"columns": {"B": c, "C": c}}}}
    rs = {"rows": {"r": {"columns": ruled}}}
    check(L.letter_mismatches(dec, rs, now_ok) == [], "unchanged used letters: no mismatch (unused A may vanish)")
    check(L.letter_mismatches(dec, rs, now_bad) == [("r", "B")], "a used letter naming other pictures is reported")
    check(L.decision_letters({"decision": "redo", "variants": ["B"], "picks": {"x": "C"}}) == {"B", "C"},
          "decision_letters ignores non-letter verdicts")

    # variant default (owner 2026-10-06): the page JS, run under node, defaults variants to every non-donor,
    # non-purged, non-purgedLive set; an explicit list (even empty) is never overwritten
    import json, shutil, subprocess
    src = Path(S.__file__).read_text()
    js = src[src.index("window.artDefaultVariants"):src.index("const _itemBody = it => {")]
    node = shutil.which("node") or str(Path.home() / ".local/bin/node")
    if not Path(node).exists():
        check(False, "variant default selftest needs node (UNMEASURED)")
    else:
        it = {"graphics": [{"cols": [
            {"letter": "A", "kind": "artpipe", "faces": {"south": "a1"}},
            {"letter": "B", "kind": "donor", "faces": {"south": "b1"}},
            {"letter": "C", "kind": "donor", "ours": True, "faces": {"south": "c1"}},
            {"letter": "D", "kind": "artpipe", "faces": {"south": "d1"}},
            {"letter": "E", "kind": "artpipe", "faces": {"south": "e1"}, "purgedLive": True}]}]}
        prog = ("const window={};const LETTER_ORDER='ABCDEFG';" + js +
                "const it=" + json.dumps(it) + ";const o={};"
                "const r1={purge:['d1']};window.artEnsureVariants(it,r1);o.r1=r1;"
                "const r2={variants:[]};window.artEnsureVariants(it,r2);o.r2=r2;"
                "const r3={variants:['A']};window.artEnsureVariants(it,r3);o.r3=r3;console.log(JSON.stringify(o))")
        out = json.loads(subprocess.run([node, "-e", prog], capture_output=True, text=True, check=True).stdout)
        check(out["r1"]["variants"] == ["A", "C"] and out["r1"].get("variantsDefault") is True,
              "default variants = ours, not donor original, not purged, not purgedLive; stored with variantsDefault")
        check(out["r2"]["variants"] == [] and "variantsDefault" not in out["r2"], "an explicit empty variants list is not overwritten")
        check(out["r3"]["variants"] == ["A"], "an explicit variants list is not overwritten")

    print(f"\n{'ALL PASS' if not FAILS else str(len(FAILS)) + ' FAIL'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
