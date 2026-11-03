#!/usr/bin/env python3
"""fauna_divergence_graph.py — the damage-vs-bodySize graph with the deliberate divergences labeled.

Reads the roster damage snapshot and the divergence manifest (FAUNA_LORE_DIVERSIFICATION_1),
checks the manifest, and draws one PNG: every rostered animal in grey at its ENGINE body size,
the Law 3 band (12-15 x bodySize) shaded, and each manifest row drawn at its RULED best hit
(red = terror, above the band; green = harmless, below it) with its defName beside it.

    python3 src/RimMandrake/Utils/fauna_divergence_graph.py [--out <png>] [--check-only]

The check (also run by selftest_fauna_lore_diversification.py) refuses a manifest whose row:
is missing a field; names a defName absent from the roster snapshot; sits INSIDE the band
(a divergence that does not diverge); points the wrong way for its direction; disagrees with
K_ruled x bodySize; has no reason; or names no ruling. Exit 0 clean, 1 on findings.

Inputs (repo-relative): design/Jawa/worldbuilding/data/fauna_lore_divergence_manifest.csv and
design/Jawa/worldbuilding/data/fauna_roster_damage_2026-11-02.csv. Provenance of both:
design/Jawa/worldbuilding/fauna_lore_divergence_2026-11-02/README.md.
"""
import argparse
import csv
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DATA = os.path.join(ROOT, "design", "Jawa", "worldbuilding", "data")
MANIFEST = os.path.join(DATA, "fauna_lore_divergence_manifest.csv")
ROSTER = os.path.join(DATA, "fauna_roster_damage_2026-11-02.csv")
DEFAULT_OUT = os.path.join(ROOT, "Transient", "fauna_lore_divergence", "damage_vs_bodysize.png")
K_LO, K_HI = 12.0, 15.0
FIELDS = ("defName", "direction", "bodySize", "band_lo", "band_hi", "current_best",
          "K_ruled", "ruled_best", "reason", "ruling")


def load(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def check(manifest, roster):
    """Return a list of finding strings; empty means the manifest is sound."""
    bad = []
    by_def = {r["defName"]: r for r in roster}
    if len(roster) < 300:  # sanity probe: the snapshot holds 666 rows; a short read is a broken file
        bad.append("roster snapshot has only %d rows (expected the full roster, 600+)" % len(roster))
    if not manifest:
        bad.append("manifest is empty")
    seen = set()
    for r in manifest:
        d = r.get("defName", "")
        missing = [k for k in FIELDS if not (r.get(k) or "").strip()]
        if missing:
            bad.append("%s: empty field(s) %s" % (d or "<row>", ",".join(missing)))
            continue
        if d in seen:
            bad.append("%s: duplicate row" % d)
        seen.add(d)
        if d not in by_def:
            bad.append("%s: not in the roster snapshot" % d)
            continue
        bs, k, best = float(r["bodySize"]), float(r["K_ruled"]), float(r["ruled_best"])
        if abs(bs - float(by_def[d]["bodySize"])) > 1e-6:
            bad.append("%s: bodySize %g != roster %s" % (d, bs, by_def[d]["bodySize"]))
        if abs(best - max(1.0, round(k * bs, 1))) > 0.051:
            bad.append("%s: ruled_best %g != K_ruled %g x bodySize %g" % (d, best, k, bs))
        if K_LO <= k <= K_HI:
            bad.append("%s: K_ruled %g sits inside the 12-15 band - not a divergence" % (d, k))
        if r["direction"] == "terror" and not k > K_HI:
            bad.append("%s: terror row with K %g not above the band" % (d, k))
        elif r["direction"] == "harmless" and not k < K_LO:
            bad.append("%s: harmless row with K %g not below the band" % (d, k))
        elif r["direction"] not in ("terror", "harmless"):
            bad.append("%s: direction %r is neither terror nor harmless" % (d, r["direction"]))
        if not r["ruling"].startswith("delegated: fauna lore divergence"):
            bad.append("%s: ruling %r does not name the delegated judge ruling" % (d, r["ruling"]))
    return bad


def draw(manifest, roster, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ruled = {r["defName"] for r in manifest}
    xs, ys = [], []
    for r in roster:
        if r["defName"] in ruled:
            continue
        bs, p = float(r["bodySize"] or 0), float(r["current_best"] or 0)
        if bs > 0 and p > 0:
            xs.append(bs)
            ys.append(p)
    fig, ax = plt.subplots(figsize=(13, 9), dpi=110)
    ax.set_xscale("log")
    ax.set_yscale("log")
    band_x = [0.03, 60]
    ax.fill_between(band_x, [K_LO * x for x in band_x], [K_HI * x for x in band_x],
                    color="#c9b458", alpha=0.35, label="Law 3 band: 12-15 x bodySize")
    ax.scatter(xs, ys, s=10, color="#9a9a9a", alpha=0.6,
               label="rest of roster, current best hit (pre-normalization)")
    for direction, colour, label in (("terror", "#c0392b", "deliberate TERROR (ruled)"),
                                     ("harmless", "#1e8449", "deliberate HARMLESS (ruled)")):
        rows = [r for r in manifest if r["direction"] == direction]
        ax.scatter([float(r["bodySize"]) for r in rows], [float(r["ruled_best"]) for r in rows],
                   s=46, color=colour, edgecolor="black", linewidth=0.5, zorder=3, label=label)
        at = {}  # twins (RM_/RSW_ tiers) share a point: one joined label, not two overprinted
        for r in rows:
            at.setdefault((float(r["bodySize"]), float(r["ruled_best"])), []).append(r["defName"])
        for (x, y), names in at.items():
            ax.annotate(" / ".join(names), (x, y),
                        xytext=(4, 3 if direction == "terror" else -9), textcoords="offset points",
                        fontsize=7, color=colour)
    ax.set_xlabel("bodySize (engine)")
    ax.set_ylabel("best melee hit (power)")
    ax.set_title("Fauna damage vs bodySize: %d deliberate divergences over a %d-animal roster "
                 "(FAUNA_LORE_DIVERSIFICATION_1)" % (len(manifest), len(roster)), fontsize=10)
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, which="both", alpha=0.2)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args()
    manifest, roster = load(MANIFEST), load(ROSTER)
    bad = check(manifest, roster)
    for b in bad:
        print("FINDING", b)
    if bad:
        return 1
    print("manifest OK: %d divergences (%d terror, %d harmless) over %d rostered animals"
          % (len(manifest), sum(r["direction"] == "terror" for r in manifest),
             sum(r["direction"] == "harmless" for r in manifest), len(roster)))
    if not a.check_only:
        draw(manifest, roster, a.out)
        print("wrote", a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
