#!/usr/bin/env python3
"""Selftest: w9_run.py --inputs DIR (G7, runbook §0.5) and the committed paint bundle.

Offline; no bridge, no def dump. Cases:
 1 default stamp paths are the frozen record world/ASHKARR_WORLDMAP_*.csv (unchanged default)
 2 set_inputs(DIR) rebinds all five layers to DIR, and nothing points back at world/
 3 probe: check_inputs on a bundle missing a layer FAILS, and main(--check-inputs) exits 13
 4 the committed bundle world/paint_inputs_2026-10-20 passes main(--inputs .. --check-inputs)
 5 inputs_feature_def reads the bundle's single label def (not WB_MapLabelFeature)
 6 bundle content holds the owner rulings: RUT_Umbra 2531 kept, RM_TheForge 44, RM_Pyrelands 222,
   and no frozen RUT_ twin left on any tile

    python3 src/RimMandrake/Utils/selftest_w9_inputs.py
"""
import collections, contextlib, csv, io, os, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w9_run  # noqa: E402

REPO = w9_run.REPO
BUNDLE = os.path.join(REPO, "world", "paint_inputs_2026-10-20")
fails = []


def ok(cond, name):
    print(("ok  " if cond else "FAIL"), name)
    if not cond:
        fails.append(name)


def quiet(fn, *a):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        return fn(*a)


def main():
    rec = os.path.join(REPO, "world")
    ok(all(os.path.dirname(p) == rec for p in (w9_run.TILES, w9_run.LINKS, w9_run.SETTS,
                                                w9_run.MUTS, w9_run.LMKS)), "1 default paths are world/ record")
    tmp = tempfile.mkdtemp(prefix="w9in_")
    try:
        p = w9_run.set_inputs(tmp)
        bound = (w9_run.TILES, w9_run.LINKS, w9_run.SETTS, w9_run.MUTS, w9_run.LMKS)
        ok(set(bound) == set(p.values()) and all(os.path.dirname(b) == os.path.abspath(tmp) for b in bound),
           "2 set_inputs rebinds all five layers")
        if os.path.isdir(BUNDLE):
            for k in w9_run.LAYERS[:-1]:  # every layer but landmarks
                shutil.copy(os.path.join(BUNDLE, "ASHKARR_WORLDMAP_%s.csv" % k), tmp)
        probs = quiet(w9_run.check_inputs, [])
        ok(any(x.startswith("landmarks: missing") for x in probs), "3a probe: missing layer is reported")
        ok(quiet(w9_run.main, ["--inputs", tmp, "--check-inputs"]) == 13, "3b probe: --check-inputs exits 13")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if not os.path.isdir(BUNDLE):
        print("SKIP 4-6: %s absent" % BUNDLE)
        return 1 if fails else 0
    ok(quiet(w9_run.main, ["--inputs", BUNDLE, "--check-inputs"]) == 0, "4 committed bundle passes --check-inputs")
    ok(w9_run.inputs_feature_def(BUNDLE) not in (None, "WB_MapLabelFeature"), "5 bundle names its own label def")
    with io.open(os.path.join(BUNDLE, "ASHKARR_WORLDMAP_tiles.csv"), encoding="utf-8") as fh:
        bc = collections.Counter(r["biome"] for r in csv.DictReader(fh))
    twins = {b for b in bc if b.startswith("RUT_") and b != "RUT_Umbra"}
    ok(bc["RUT_Umbra"] == 2531 and bc["RM_TheForge"] == 44 and bc["RM_Pyrelands"] == 222 and not twins
       and "ZBiome_Grasslands" not in bc,
       "6 owner rulings hold (Umbra %d, Forge %d, Pyrelands %d, twins left %s)"
       % (bc["RUT_Umbra"], bc["RM_TheForge"], bc["RM_Pyrelands"], sorted(twins)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
