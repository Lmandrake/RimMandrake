#!/usr/bin/env python3
"""selftest_unproven_adjudicate.py — TEXREGEN_UNPROVEN_ASK_THE_SHEETS, on a disposable git fixture.

Proves unproven_adjudicate.py's provenance instrument and verdict order, the parts that decided 563 pictures:
  - PngHistory finds the commit that first brought TODAY'S bytes in: across a pure move, across a COPY under a new
    name (rename detection calls that a fresh add — the trap behind the "retier" and "own it as RM_" commits), past a
    mechanical re-save listed in PASS_THROUGH, and NOT the path's first add when the picture was later replaced;
  - adjudicate_one's order: a dhash near-duplicate of our render wins, then a donor twin, then BYTES_RULES, then
    FILE_RULES; a sheet keep is evidence only; nothing matched is UNRESOLVED (never silently ours);
  - the dhash threshold catches a LANCZOS rescale of the same picture and not an unrelated one;
  - owner_picks (recorded as evidence, never a verdict) counts only the OWNER'S own keep decision on a row (never an
    agent prefill, never redo/cut), matched on the exact row stem, a Catch row apart from its animal; --check says no
    to a doc missing a roster row or a file verdict;
  - every hand-read rule names a known basis, every basis maps to one of the item's three verdicts, and the committed
    adjudication carries one of the three on every file and on every roster row, all held in the committed snapshot.
"""
from __future__ import annotations

import json
import random
import shutil
import subprocess
import sys
import tempfile
from io import BytesIO
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artledger as A               # noqa: E402
import unproven_adjudicate as U     # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def noise_png(seed, size=64):
    from PIL import Image
    rnd = random.Random(seed)
    im = Image.new("RGBA", (size, size))
    im.putdata([(rnd.randrange(256), rnd.randrange(256), rnd.randrange(256), 255) for _ in range(size * size)])
    # smooth blobs so dhash has structure (pure noise is not a picture)
    im = im.resize((8, 8), Image.BILINEAR).resize((size, size), Image.BICUBIC)
    b = BytesIO()
    im.save(b, "PNG")
    return b.getvalue(), im


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True).stdout.strip()


def commit(repo, msg):
    git(repo, "add", "-A")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", msg)
    return git(repo, "rev-parse", "HEAD")


def main():
    tmp = Path(tempfile.mkdtemp(prefix="unproven_adj_"))
    git(tmp, "init", "-q", "-b", "main")
    a, _ = noise_png(1)
    b, _ = noise_png(2)
    c, _ = noise_png(3)
    (tmp / "old").mkdir()
    (tmp / "old/A.png").write_bytes(a)
    (tmp / "old/R.png").write_bytes(b)
    c_src = commit(tmp, "donor port: art copied from the workshop")
    git(tmp, "mv", "old/A.png", "old/Moved.png")
    c_move = commit(tmp, "pure move")
    (tmp / "new").mkdir()
    (tmp / "new/Copy.png").write_bytes(a)                          # a copy under a new name: a fresh add to git
    c_copy = commit(tmp, "own it as RM_ (copy)")
    (tmp / "old/R.png").write_bytes(c)                             # the picture REPLACED after its first add
    c_redo = commit(tmp, "redraw R")
    _, im_c = noise_png(3)
    halo = BytesIO()
    im_c.save(halo, "PNG", compress_level=1)
    (tmp / "old/R.png").write_bytes(halo.getvalue())               # a mechanical re-save of the redrawn picture
    c_halo = commit(tmp, "zero the halo")

    real_repo, real_pass = U.REPO, dict(U.PASS_THROUGH)
    try:
        U.REPO = tmp
        U.PASS_THROUGH[c_halo[:10]] = "fixture halo pass"
        H = U.PngHistory()
        check(H.bytes_commit("old/Moved.png").startswith(c_src), "a pure move traces to the commit that added the bytes")
        check(H.bytes_commit("new/Copy.png").startswith(c_src),
              "a COPY under a new name traces to the source's commit, not the copying commit")
        check(H.bytes_commit("old/R.png").startswith(c_redo),
              "a re-save in PASS_THROUGH is looked past, landing on the redraw — not the path's first add")
        del U.PASS_THROUGH[c_halo[:10]]
        check(H.bytes_commit("old/R.png").startswith(c_halo), "without the PASS_THROUGH entry the re-save itself is the source")
        check(H.bytes_commit("nope.png") == "", "an untracked path has no bytes commit (never a guess)")
        check(c_move and c_copy, "fixture commits exist")

        # verdict order on a fake neighbour pool: (dhash d, kind, loc, sha, mad) — mad None = not pixel-confirmed
        class NB:
            def __init__(self, ours=None, donor=None):
                self.o, self.d = ours, donor

            def nearest(self, ph, kinds, raw=None):
                return self.o if kinds == U.OURS else self.d

        class Hist:
            def __init__(self, line):
                self.line = line

            def bytes_commit(self, rel):
                return self.line

            def commits(self, rel):
                return [self.line]

        p = tmp / "new/Copy.png"
        rule_sha = next(iter(U.BYTES_RULES))
        none = Hist("0000000000 x")
        near_both = NB((3, "artpipe", "r", "s", 0.2), (2, "donor", "d", "s", 0.1))
        v, w, _e = U.adjudicate_one("RM_X", p, "s", near_both, {}, Hist(rule_sha))
        check(v == U.BYTES_RULES[rule_sha][0] and rule_sha in w,
              "the commit that brought THESE bytes in outranks any similarity match")
        v, _w, _e = U.adjudicate_one("RM_X", p, "s", near_both, {}, none)
        check(v == "STAND_IN", "no rule: a closer confirmed donor twin beats a farther render of ours")
        v, _w, _e = U.adjudicate_one("RM_X", p, "s", NB((3, "artpipe", "r", "s", 0.2), (9, "donor", "d", "s", 0.3)), {}, none)
        check(v == "OURS_RESAVED", "no rule: a closer confirmed render of ours wins")
        unconf = NB((1, "artpipe", "r", "s", None), (1, "donor", "d", "s", None))
        pick = {"copyxyz": [("Transient/s.decisions.json", "RM_Copyxyz", "a", "2026-10-01T00:00:00Z")]}
        v, _w, e = U.adjudicate_one("RM_Copyxyz", p, "s", unconf, pick, none)
        check(v == "UNRESOLVED" and e["sheet_keeps"] and e["sheet_keeps"][0][2] == "RM_Copyxyz",
              "a dhash hit without pixel confirmation is no match; the owner's keep on a sheet row is recorded as "
              "evidence, never a verdict (a kept letter does not name these bytes)")
        v, _w, _e = U.adjudicate_one("RM_Zzzzz", p, "s", unconf, {}, none)
        check(v == "UNRESOLVED", "nothing matched is UNRESOLVED, never silently ours")

        # the pixel confirm itself: same dhash bucket, different pixels -> rejected; a rescale -> accepted
        from PIL import Image
        _, big = noise_png(21, 128)
        o = BytesIO(); big.save(o, "PNG")
        half = BytesIO(); big.resize((64, 64), Image.LANCZOS).save(half, "PNG")
        inv = BytesIO(); Image.eval(big.convert("RGB"), lambda x: min(255, x + 40)).convert("RGBA").save(inv, "PNG")
        store = {"half": half.getvalue(), "bright": inv.getvalue()}
        ph = A.dhash(o.getvalue())[0]

        class FakeIdx:
            variants = {"bright": [{"ph": ph, "kind": "artpipe", "loc": "x/bright.png"}],
                        "half": [{"ph": ph, "kind": "artpipe", "loc": "x/half.png"}],   # same bucket: pixels decide
                        "src": [{"ph": ph, "kind": "artpipe", "loc": "_artsrc/job/src.png"}]}
        real_get = A.store_get
        try:
            A.store_get = lambda sha: store[sha]
            nb = U.Neighbours(FakeIdx())
            check(all("_artsrc/" not in loc for _h, _k, loc, _s in nb.pool), "_artsrc job inputs are not in the pool")
            dk = U.Neighbours.kind_of
            check(dk({"kind": "install", "provenance": {}}, "src/X/Textures/swanimals/BiomesTeam/a.png") == "donor"
                  and dk({"kind": "install", "provenance": {"item": "J"}}, "src/X/Textures/swanimals/BiomesTeam/a.png")
                  == "install" and dk({"kind": "install"}, "src/X/Textures/Things/a.png") == "install",
                  "a provenance-less install under the donor port's folder counts as donor, any other install as ours")
            hit = nb.nearest(ph, U.OURS, o.getvalue())
            check(hit and hit[3] == "half" and hit[4] is not None and hit[4] <= U.MAD_MAX,
                  f"the brightened twin (dhash-identical) is rejected by pixels and the rescale accepted ({hit})")
        finally:
            A.store_get = real_get
    finally:
        U.REPO, U.PASS_THROUGH = real_repo, real_pass

    # threshold: a rescale of the same picture is under it, a stranger is not
    from PIL import Image
    _, im = noise_png(11, 256)
    s = BytesIO()
    im.resize((128, 128), Image.LANCZOS).save(s, "PNG")
    o = BytesIO()
    im.save(o, "PNG")
    d_same = A.hamming(A.dhash(o.getvalue())[0], A.dhash(s.getvalue())[0])
    d_other = A.hamming(A.dhash(o.getvalue())[0], A.dhash(noise_png(12, 256)[0])[0])
    check(d_same <= U.DHASH_MAX, f"a 1/2 LANCZOS rescale is within DHASH_MAX ({d_same})")
    check(d_other > U.DHASH_MAX, f"an unrelated picture is beyond DHASH_MAX ({d_other})")

    check(all(v in U.BASES and v != "UNRESOLVED" and why for v, why in
              list(U.BYTES_RULES.values()) + list(U.FILE_RULES.values())), "every hand-read rule names a real basis")
    check(set(U.VERDICTS) == {"OWNER_PICKED", "HAND_MADE", "STAND_IN"}, "the verdict set is the item's three classes")
    check(all(U.CLASS_OF[b] in U.VERDICTS for b in U.BASES if b != "UNRESOLVED") and U.CLASS_OF["UNRESOLVED"] is None,
          "every basis maps to one of the three; UNRESOLVED maps to none (so --check refuses it)")
    check(U.row_verdict({"OWNER_PICKED", "STAND_IN"}) == "STAND_IN" and U.row_verdict({"OWNER_PICKED", "HAND_MADE"})
          == "HAND_MADE" and U.row_verdict(set()) is None, "a mixed roster row takes STAND_IN, then HAND_MADE; none is none")

    # owner_picks: only the OWNER'S decision counts (decidedAt / overriding the prefill), only a keep, exact row stem
    dtmp = Path(tempfile.mkdtemp(prefix="unproven_dec_"))
    (dtmp / "Transient/x").mkdir(parents=True)
    (dtmp / "Transient/x/s.decisions.json").write_text(json.dumps({"decisions": {
        "RM_Prefillonly": {"decision": "A", "prefill": "A", "at": "t"},           # agent's seeded letter, never clicked
        "RM_Clicked": {"decision": "b", "prefill": "A", "at": "t", "decidedAt": "t1"},
        "RM_Overrode": {"decision": "C", "prefill": "A", "at": "t"},               # differs from the prefill: his
        "RM_Redone": {"decision": "redo", "prefill": "A", "decidedAt": "t2"},     # his, but not a keep
        "RM_ClickedCatch": {"decision": "a", "decidedAt": "t3"},                   # the catch icon, not the animal
        "swanimals/Pathy/Pathy_f": {"decision": "a", "decidedAt": "t4"}}}))
    real_repo = U.REPO
    try:
        U.REPO = dtmp
        pk = U.owner_picks()
    finally:
        U.REPO = real_repo
    check(set(pk) == {"clicked", "overrode", "clickedcatch", "pathy"} and pk["clicked"][0][2:] == ("b", "t1"),
          f"owner_picks keeps only his own keep decisions, prefill-only and redo dropped, Catch kept apart ({sorted(pk)})")
    check("clicked" in U.stems_for("RM_Clicked", Path("Clicked_south.png"))
          and "clickedcatch" not in U.stems_for("RM_Clicked", Path("Clicked_south.png")),
          "an animal's stems never reach its Catch row")
    shutil.rmtree(dtmp, ignore_errors=True)

    # roster_snapshot: every census row, body textures first, only live ones
    body = lambda m, r: {"res": r, "role": "body", "live": {"mod": m, "faces": {}}}  # noqa: E731
    census = {"biome_order": ["B"], "biomes": {"B": {"rows": [{"key": "k1", "art": {"resources": [body("src/M", "T/a"),
                                                                             {"res": "T/m", "role": "mask"}]}},
                                         {"key": "k2", "art": {"resources": [{"res": "T/b", "live": {"mod": "src/N"}}]}},
                                         {"key": "k3", "art": {"resources": [body("src/M", "T/c")]}}]}}}
    sp = [(r["biome"], r["def"], r["bodies"]) for r in U.roster_snapshot(census)]
    check(sp == [("B", "k1", [["src/M", "T/a"]]), ("B", "k2", [["src/N", "T/b"]]), ("B", "k3", [["src/M", "T/c"]])],
          f"roster_snapshot keeps every row, body textures first, live ones only ({sp})")

    doc = json.load(open(U.OUT_JSON))
    check(doc["files"] and all(r["verdict"] in U.VERDICTS and U.CLASS_OF[r["basis"]] == r["verdict"] and r["why"]
                               for r in doc["files"]),
          f"the committed adjudication has one of the three verdicts, its basis and a reason on all {len(doc['files'])} files")
    check(doc["roster"] and all(r["verdict"] in U.VERDICTS and r["bodies"] for r in doc["roster"]),
          f"every committed roster row ({len(doc['roster'])}) has one of the three verdicts and its body textures")
    snap = json.load(open(U.ROSTER_SNAP))["rows"]
    check(len(snap) > 500 and {(r["biome"], r["def"]) for r in doc["roster"]} <= {(r["biome"], r["def"]) for r in snap},
          f"the committed roster snapshot ({len(snap)} census rows) holds every adjudicated roster row; --check "
          "re-classifies all of them now")
    check(all(r["why"].startswith("bytes from ") or r["file"] in U.FILE_RULES
              for r in doc["files"] if r["verdict"] == "OWNER_PICKED"),
          "every OWNER_PICKED rests on a hand-read bytes commit or file look, never on a sheet row or stem")

    # --check itself fails on a doc missing a roster row or a file verdict (it must be able to say no)
    real_out = U.OUT_JSON
    for label, mut in (("a roster row", lambda x: x["roster"].pop(0)), ("a file verdict", lambda x: x["files"].pop(0))):
        bad = json.loads(json.dumps(doc))
        mut(bad)
        t = Path(tempfile.mkdtemp(prefix="unproven_neg_")) / "adj.json"
        t.write_text(json.dumps(bad))
        try:
            U.OUT_JSON = t
            rc = U.check()
        finally:
            U.OUT_JSON = real_out
            shutil.rmtree(t.parent, ignore_errors=True)
        check(rc == 1, f"--check refuses the committed adjudication with {label} removed (rc {rc})")

    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{'ALL PASS' if not FAILS else str(len(FAILS)) + ' FAIL'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
