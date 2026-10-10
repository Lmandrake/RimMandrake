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

    # variant ticks (owner, by question card 2026-10-10): NEVER pre-ticked; a click never launders a machine-default
    # list into his; a tick exists only on a random-pool lane. Run under node; each check FAILS on the 10-06 code.
    import json, shutil, subprocess
    src = Path(S.__file__).read_text()
    node = shutil.which("node") or str(Path.home() / ".local/bin/node")
    if not Path(node).exists():
        check(False, "variant tick selftest needs node (UNMEASURED)")
    else:
        js = src[src.index("window.artOwnerVariants"):src.index("const _itemBody = it => {")]
        tog = src[src.index("window.artToggleVariant = (id, letter) => {"):src.index("window.artPick = (id, g, letter) => {")]
        it = {"id": "r", "graphics": [
            {"pool": True, "cols": [{"letter": "A", "kind": "artpipe", "faces": {"south": "a1"}},
                                    {"letter": "B", "kind": "artpipe", "faces": {"south": "b1"}},
                                    {"letter": "C", "kind": "artpipe", "faces": {"south": "c1"}, "noSelect": True}]},
            {"flip": True, "cols": [{"letter": "E", "kind": "artpipe", "faces": {"1_east": "e1"}}]}]}
        prog = ("const window={};const LETTER_ORDER='ABCDEFG';let frozen=false;const errs=[];const showErr=m=>errs.push(m);"
                "const queue=()=>{},patchRow=()=>{},paintCounts=()=>{},prefillOf=()=>'A';" + js + tog +
                "const it=" + json.dumps(it) + ";const byId=new Map([['r',it]]);const o={};"
                "o.none=window.artOwnerVariants({variants:['A','B'],variantsDefault:true});"
                "o.mine=window.artOwnerVariants({variants:['A']});"
                "const DEC={r:{decision:'A',variants:['A','B'],variantsDefault:true}};"
                "window.artToggleVariant('r','B');o.after=JSON.parse(JSON.stringify(DEC.r));"
                "window.artToggleVariant('r','E');o.flip=JSON.parse(JSON.stringify(DEC.r));o.errs=errs.slice();"
                "const r5={variants:['A','C']};window.artEnsureVariants(it,r5);o.r5=r5;"
                "const r6={variants:['A','C'],variantsDefault:true};window.artEnsureVariants(it,r6);o.r6=r6;"
                "console.log(JSON.stringify(o))")
        out = json.loads(subprocess.run([node, "-e", prog], capture_output=True, text=True, check=True).stdout)
        check(out["none"] == [] and out["mine"] == ["A"], "a machine-default variant list shows NO ticks; his list shows")
        check(out["after"]["variants"] == ["B"] and "variantsDefault" not in out["after"],
              "one click ticks only THAT set: the default list is not laundered into his (was [A,B] -> click B)")
        check(out["after"].get("legacyVariantsDefault") == ["A", "B"], "the dropped default list is kept aside as legacy, not lost")
        check(out["flip"]["variants"] == ["B"] and any("random pool" in e for e in out["errs"]),
              "a tick on a non-pool lane (flight frames) is refused with a reason")
        check(out["r5"]["variants"] == ["A"], "a placeholder letter is stripped from his explicit variants list on save")
        check(out["r6"]["variants"] == ["A", "C"] and out["r6"]["variantsDefault"],
              "a save never rewrites (materialises) a machine-default list")
        check("artDefaultVariants" not in src, "the pre-tick default (artDefaultVariants) is gone from the sheet")
    for frag in ("if (c.noSelect) return", "placeholder — not selectable", "artNoSelect(it).has(letter)",
                 "artNoSelect(it_).has(key)"):
        check(frag in src, f"sheet JS guards placeholders: {frag!r}")
    # the Python side: a circle set is noSelect; a set mixing a circle with real art is not
    from PIL import Image, ImageDraw
    import io
    im = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((14, 14, 114, 114), fill=(120, 80, 40, 255), outline=(10, 10, 10, 255), width=3)
    bio = io.BytesIO(); im.save(bio, "PNG")
    circ = bio.getvalue()
    S._GEO_CACHE.clear()
    S._GEO_CACHE.update({"circ": S.PD.placeholder_reason(circ) or "", "real": ""})
    check(bool(S.geo_placeholder({"south": "circ"})), "geo_placeholder flags a set that is all circle")
    check(not S.geo_placeholder({"south": "circ", "east": "real"}), "a set with one real picture is not a placeholder")
    check(not S.geo_placeholder({}), "an empty set is not judged")

    print(f"\n{'ALL PASS' if not FAILS else str(len(FAILS)) + ' FAIL'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
