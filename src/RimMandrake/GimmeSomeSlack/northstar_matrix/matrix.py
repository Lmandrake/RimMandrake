#!/usr/bin/env python3
"""Case matrix: a pairwise (strength-2) covering array over the Gimme Some Slack scene axes, plus its proof.

    python3 matrix.py                       # print the count, per-axis value usage and the pair proof
    python3 matrix.py --out <catalog.json>  # also write the catalog: every case with scene + oracle + plan
    python3 matrix.py --prove <catalog.json>   # re-prove pair coverage of a written catalog (exit 1 if any pair missing)

Every pair of values from any two axes appears in at least one case. The generator is a seeded greedy
(AETG-style: per new row, 60 candidate rows built value-by-value to cover the most uncovered pairs; keep the
best), so the set is deterministic; the lower bound is |topology| x |largest other axis| = 18 x 4 = 72.
"""
import argparse
import itertools
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE in sys.path:
    sys.path.remove(HERE)
sys.path.insert(0, HERE)   # front always: Utils/scenes (a package) must not shadow this directory's scenes.py
_m = sys.modules.get("scenes")
if _m is not None and os.path.dirname(os.path.abspath(getattr(_m, "__file__", "") or "")) != HERE:
    del sys.modules["scenes"]
import scenes as S  # noqa: E402

AXES = [
    ("topology", list(S.TOPOLOGY_ORDER)),
    ("tangle", ["tidy", "ropey", "ratsnest"]),
    ("style", ["jawa", "extcord", "cybertek", "starwars"]),
    ("density", [5, 20, 100, 400]),
    ("break", ["none", "live_gap", "dead_gap"]),
    ("aerial", ["none", "one_span", "chain_cut"]),
    ("hose", ["none", "flat", "plump"]),
]
SEED = 20261002
CANDIDATES = 60


def all_pairs(axes=AXES):
    out = set()
    for (i, (_, vi)), (j, (_, vj)) in itertools.combinations(list(enumerate(axes)), 2):
        for a in range(len(vi)):
            for b in range(len(vj)):
                out.add((i, a, j, b))
    return out


def pairs_of(row):
    return {(i, row[i], j, row[j]) for i, j in itertools.combinations(range(len(row)), 2)}


def covering(axes=AXES, seed=SEED, candidates=CANDIDATES):
    rng = random.Random(seed)
    unc = all_pairs(axes)
    rows = []
    use = [[0] * len(v) for _, v in axes]
    n = len(axes)
    while unc:
        best, best_gain = None, -1
        for _ in range(candidates):
            order = list(range(n))
            rng.shuffle(order)
            row = [None] * n
            for i in order:
                scored = []
                for a in range(len(axes[i][1])):
                    gain = sum(1 for j in range(n) if row[j] is not None and
                               ((i, a, j, row[j]) in unc if i < j else (j, row[j], i, a) in unc))
                    scored.append((-gain, use[i][a], rng.random(), a))
                row[i] = min(scored)[3]
            gain = len(pairs_of(row) & unc)
            if gain > best_gain:
                best, best_gain = row, gain
        rows.append(best)
        unc -= pairs_of(best)
        for i, a in enumerate(best):
            use[i][a] += 1
    return rows


def prove(cases, axes=AXES):
    """Every pair of axis values appears in some case. Returns (n_pairs, missing list)."""
    idx = [{v: k for k, v in enumerate(vals)} for _, vals in axes]
    have = set()
    for c in cases:
        row = [idx[i][c[name]] for i, (name, _) in enumerate(axes)]
        have |= pairs_of(row)
    need = all_pairs(axes)
    missing = sorted(need - have)
    named = [(axes[i][0], axes[i][1][a], axes[j][0], axes[j][1][b]) for i, a, j, b in missing]
    return len(need), named


def cases(axes=AXES):
    out = []
    for k, row in enumerate(covering(axes)):
        c = {name: axes[i][1][row[i]] for i, (name, _) in enumerate(axes)}
        c["case"] = "MC%03d_%s" % (k + 1, c["topology"])
        out.append(c)
    return out


def scene_for(case):
    return S.compose(case["topology"], case["density"], case["break"], case["aerial"], case["hose"], name=case["case"])


def build_catalog(origin=(150, 150)):
    import oracle as O
    import placer as P
    cs = cases()
    cat = []
    for c in cs:
        sc = scene_for(c)
        cat.append({"case": c, "scene": sc, "lint": S.lint(sc), "oracle": O.full(sc, c["tangle"]),
                    "plan": P.plan(sc, c, origin)})
    n, missing = prove(cs)
    return {"format": "mc_catalog/1", "generator": "src/RimMandrake/GimmeSomeSlack/northstar_matrix/matrix.py",
            "seed": SEED, "axes": [[a, v] for a, v in AXES], "count": len(cat), "pairs": n,
            "pairs_missing": missing, "cases": cat}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out")
    ap.add_argument("--prove")
    a = ap.parse_args(argv)
    if a.prove:
        cat = json.load(open(a.prove))
        n, missing = prove([c["case"] for c in cat["cases"]])
        print("%d cases, %d pairs required, %d missing" % (len(cat["cases"]), n, len(missing)))
        for m in missing[:20]:
            print("  MISSING", m)
        return 1 if missing else 0
    cs = cases()
    n, missing = prove(cs)
    print("cases: %d   (lower bound %d)   pairs required: %d   missing: %d" %
          (len(cs), max(len(v) for _, v in AXES) * sorted(len(v) for _, v in AXES)[-2], n, len(missing)))
    for i, (name, vals) in enumerate(AXES):
        cnt = {v: sum(1 for c in cs if c[name] == v) for v in vals}
        print("  %-9s %s" % (name, cnt))
    if a.out:
        cat = build_catalog()
        bad = [(c["case"]["case"], c["lint"]) for c in cat["cases"] if c["lint"]]
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w") as f:
            json.dump(cat, f, indent=1, default=list)
        print("wrote %s (%d cases, lint problems in %d)" % (a.out, cat["count"], len(bad)))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
