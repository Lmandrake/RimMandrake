"""density_sampler.py -- CHILL_DIVE_DENSITY_SAMPLER_1.

Offline simulation of what a Chill dive meets, mirroring GenStep_SeaFloorFauna (legacy one-of-each
vs the weighted draw). Reads the RM_TheChill wildAnimals roster as an XML ELEMENT (shorthand
<Def>commonality</Def>, never <li>). Needs no game. The live count of animals on a generated floor
is UNMEASURED here; modcheck component chill_dive_density_sampler reports it so.
Usage: python3 density_sampler.py [--n 20000] [--count 3] [--seed 1]
"""
import argparse, os, random, sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
BIOME_XML = os.path.join(HERE, "..", "TerminalBiomes", "Defs", "BiomeDefs", "RM_TheChill.xml")
COUNT_PER_DENSITY = 20.0


def load_roster(path=BIOME_XML, biome="RM_TheChill"):
    root = ET.parse(path).getroot()
    for b in root.iter("BiomeDef"):
        if b.findtext("defName") == biome:
            wa = b.find("wildAnimals")
            density = float(b.findtext("animalDensity") or 0)
            roster = {e.tag: float(e.text) for e in wa if e.text and e.text.strip()}
            return density, roster
    raise SystemExit("biome %s not found in %s" % (biome, path))


def legacy_draw(density, roster, rng):
    total = max(1, round(COUNT_PER_DENSITY * max(density, 0.05)))  # banker's rounding, as Mathf.RoundToInt
    out = []
    for k, c in roster.items():
        n = round(total * c)
        if n <= 0:
            n = 1 if rng.random() < c else 0
        out += [k] * n
    return out


def weighted_draw(roster, count, rng):
    kinds, w = list(roster), list(roster.values())
    return rng.choices(kinds, weights=w, k=count)


def summarize(name, draws, roster):
    n = len(draws)
    sizes = sorted(len(d) for d in draws)
    print("%s: mean %.2f animals (min %d, median %d, max %d)" % (name, sum(sizes) / n, sizes[0], sizes[n // 2], sizes[-1]))
    uniq = sum(len(set(d)) for d in draws) / n
    print("  mean distinct species %.2f of %d; P(any repeat) %.2f" % (uniq, len(roster), sum(len(set(d)) < len(d) for d in draws) / n))
    for k in sorted(roster, key=roster.get, reverse=True):
        print("  %-12s c=%.2f  appears in %5.1f%% of dives" % (k, roster[k], 100.0 * sum(k in d for d in draws) / n))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--count", type=int, default=3)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args(argv)
    density, roster = load_roster()
    if not roster:
        print("FAIL: empty roster (instrument cannot read it)"); return 2
    rng = random.Random(a.seed)
    print("roster %d species, animalDensity %s" % (len(roster), density))
    summarize("legacy one-of-each", [legacy_draw(density, roster, rng) for _ in range(a.n)], roster)
    summarize("weighted draw count=%d" % a.count, [weighted_draw(roster, a.count, rng) for _ in range(a.n)], roster)
    print("LIVE floor animal count: UNMEASURED (needs a generated Chill floor via the bridge)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
