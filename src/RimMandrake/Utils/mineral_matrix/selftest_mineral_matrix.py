#!/usr/bin/env python3
"""selftest_mineral_matrix.py -- gen_matrix.py rebuilds the matrix from the repo, and check_matrix.py catches a bad build.

1. gen_matrix.py --no-page into a temp folder: exit 0, all 8 outputs written.
2. check_matrix.py on that folder: exit 0.
3. Mutants check_matrix.py must refuse: a dropped audit row, an extra row, an unmarked extra, a src_def pointing at no
   file, a label differing from its def with no note, a planted "(Jawa)" in a far file.
"""
import csv, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
OUTS = ["biomes.csv", "draft_matrix.csv", "reasons.csv", "mineral_homes.csv", "inventory.csv", "reach_summary.csv",
        "column_changes.csv", "stats.json"]
fails = []


def check(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        fails.append(what)


def run(*args):
    return subprocess.run([PY, *args], capture_output=True, text=True, timeout=300)


def mutate_biomes(folder, fn):
    p = os.path.join(folder, "biomes.csv")
    rows = list(csv.DictReader(open(p, encoding="utf-8")))
    fields = list(rows[0])
    rows = fn(rows)
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)


def main():
    with tempfile.TemporaryDirectory() as t:
        good = os.path.join(t, "good")
        r = run(os.path.join(HERE, "gen_matrix.py"), "--out", good, "--no-page")
        check(r.returncode == 0, "gen_matrix.py --no-page exits 0" + ("" if r.returncode == 0 else ": " + r.stderr[-400:]))
        check(all(os.path.isfile(os.path.join(good, f)) for f in OUTS), "all 8 outputs written")
        r = run(os.path.join(HERE, "check_matrix.py"), good)
        check(r.returncode == 0, "check_matrix.py passes the real build" + ("" if r.returncode == 0 else ": " + r.stdout[-600:]))

        def one(name, fn, expect):
            d = os.path.join(t, name)
            shutil.copytree(good, d)
            fn(d)
            r = run(os.path.join(HERE, "check_matrix.py"), d)
            check(r.returncode != 0 and expect in r.stdout, "refuses: " + name)

        one("dropped_row", lambda d: mutate_biomes(d, lambda rs: [x for x in rs if x["biome"] != "RM_Webwork"]),
            "FAIL biomes.csv rows = audit list")
        one("extra_row", lambda d: mutate_biomes(d, lambda rs: rs + [dict(rs[0], biome="RUT_Desert")]),
            "FAIL biomes.csv rows = audit list")
        one("unmarked_extra", lambda d: mutate_biomes(d, lambda rs: [dict(x, mark="") if x["biome"] == "RM_LanternDeeps" else x for x in rs]),
            "FAIL the two extras are marked")
        one("bad_src", lambda d: mutate_biomes(d, lambda rs: [dict(x, src_def="src/Nope/Biome.xml") if x["biome"] == "RM_Abyss" else x for x in rs]),
            "FAIL every row's src_def")
        one("label_drift", lambda d: mutate_biomes(d, lambda rs: [dict(x, label="the Wrong", src_label="the Wrong") if x["biome"] == "RM_Wastes" else x for x in rs]),
            "FAIL every row's src_def")
        def plant(d):
            p = os.path.join(d, "reach_summary.csv")
            open(p, "a", encoding="utf-8").write("planted,the Rot (Jawa)\n")
        one("planted_jawa", plant, "FAIL no '(Jawa)' tag")
    print("selftest_mineral_matrix: %s" % ("FAIL %d" % len(fails) if fails else "OK"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
