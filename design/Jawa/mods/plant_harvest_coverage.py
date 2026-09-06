#!/usr/bin/env python3
r"""plant_harvest_coverage.py — what a plant cut actually costs, per biome.

WHY THIS EXISTS
---------------
`PLANT_CHERRYPICK_PASS_1` names the trap and then only half-guards it:

> From `skills/rimworld-content-moderation`: cutting the last item carrying a tag
> silently disarms every pawn kind whose tags all went to zero. **The plant equivalent
> is `harvestedThingDef`** — cut every plant that yields a resource and the resource
> leaves the biome, with nothing warning you.

`gen_plant_sheet.py` guards **WoodLog only**, in biomes over 100 tiles, at a floor of two
sources. That is the right idea applied to one resource out of thirty. This is the
general case, and it is the item's second criterion: *"the kept set checked for
`harvestedThingDef` coverage per biome."*

🔴 **THE CHECK IS PER BIOME, NEVER PLANET-WIDE.** A resource with nine suppliers across
Ash'karr can still have exactly one inside `AB_MycoticJungle`, and a colony does not
travel to another biome for wood. A planet-wide count answers a question nobody asked and
reads as safety.

⚠️ **This measures the SHIPPED roster, not a proposal.** Under the owner's keep-all
ruling nothing is cut, so today every number here is a *what it would cost*, not a
defect. That is the point: it is the decision aid the sheet was missing.

    python3 design/Jawa/mods/plant_harvest_coverage.py            # report to stdout
    python3 design/Jawa/mods/plant_harvest_coverage.py --md <out.md>
    python3 design/Jawa/mods/plant_harvest_coverage.py --against-decisions   # 🔴 run after EVERY cut

⭐ **`--against-decisions` is the one that earns its keep.** It re-derives coverage with the
owner's `cut` rows removed and names every resource that would leave a biome. Measured the
first time it ran, 2026-08-22, against his own four cuts: `Volcano` lost **all three** of its
wood sources and `AridShrubland` lost berries entirely. Neither was visible from the sheet,
because a row shows what one plant supplies, never what survives it.

⚠️ **A non-zero exit means a resource disappeared, not that the cut is wrong.** The owner may
well accept it; the tool's job is to make sure he is accepting it rather than missing it.
"""
from __future__ import annotations
import argparse, collections, csv, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CSV = os.path.join(ROOT, 'design', 'Jawa', 'mods', 'plant_cherrypick_candidates.csv')
TILES = os.path.join(ROOT, 'world', 'ASHKARR_WORLDMAP_tiles.csv')

# Biomes that are SUPPOSED to have no flora. Anything else with an empty roster is a
# finding, not a fact of nature.
PLANTLESS_BY_DESIGN = {'Ocean', 'Lake', 'SeaIce', 'IceSheet'}


def tile_counts() -> collections.Counter:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(TILES)), 'src', 'RimMandrake', 'Utils'))
    from verify_frozen import warn_if_stale
    warn_if_stale(TILES)
    c = collections.Counter()
    with open(TILES, encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            if r.get('biome'):
                c[r['biome']] += 1
    return c


def load_rows() -> list[dict]:
    with open(CSV, encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


def coverage(rows, tiles):
    """biome -> resource -> [defName, ...], over the biomes that exist on the planet."""
    cov = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        h = (r.get('harvestedThingDef') or '').strip()
        for b in (r.get('biomes') or '').split('|'):
            if b and b in tiles:
                cov[b]  # a biome with plants but no yields still deserves a row
                if h:
                    cov[b][h].append(r['defName'])
    return cov


def sole_sources(rows, tiles) -> dict[str, list[tuple[str, str]]]:
    """defName -> [(biome, resource), ...] where it is the ONLY supplier in that biome.

    🔑 This is the number that decides a cut. Everything else on the sheet is taste."""
    cov = coverage(rows, tiles)
    out = collections.defaultdict(list)
    for b, by_res in cov.items():
        for res, defs in by_res.items():
            if len(defs) == 1:
                out[defs[0]].append((b, res))
    return dict(out)


def load_decisions(path=None):
    """The owner's file. ⚠️ Returns (cut_set, provenance) and REFUSES a file that no page
    wrote — `savedBy` is stamped only by plant_review.html, never by a generator, so its
    absence means these are somebody's guesses rather than his decisions."""
    import json
    path = path or os.path.join(ROOT, 'design', 'Jawa', 'mods', 'plant_decisions.json')
    if not os.path.exists(path):
        return None, f"no decisions file at {path}"
    d = json.load(open(path, encoding='utf-8'))
    if not d.get('savedBy'):
        return None, ("REFUSED — this file carries no `savedBy`, so nothing proves the review "
                      "page ever wrote it. It may be a pre-fill wearing the owner's name.")
    cut = {k for k, v in (d.get('decisions') or {}).items() if v.get('decision') == 'cut'}
    return cut, f"{d['savedBy']} @ {d.get('savedAt')} · {d.get('decidedCount')}/{d.get('total')} touched"


def against_decisions(rows, tiles, cut) -> tuple[str, int]:
    """What the cut set actually costs, biome by biome. Returns (text, n_losses)."""
    before = coverage(rows, tiles)
    after = coverage([r for r in rows if r['defName'] not in cut], tiles)
    L, losses = [], 0
    A = L.append
    A(f"CUT SET: {len(cut)} plant(s) — " + ", ".join(f"`{c}`" for c in sorted(cut)))
    A("")
    for b in sorted(before, key=lambda x: -tiles[x]):
        lost = [(res, defs) for res, defs in before[b].items() if not after[b].get(res)]
        wb, wa = len(before[b].get('WoodLog', [])), len(after[b].get('WoodLog', []))
        pb = sum(1 for r in rows if b in (r.get('biomes') or '').split('|'))
        pa = sum(1 for r in rows if b in (r.get('biomes') or '').split('|') and r['defName'] not in cut)
        if not lost and wa == wb and pa == pb:
            continue
        A(f"### `{b}` — {tiles[b]:,} tiles")
        A("")
        A(f"plants {pb} → {pa} · wood sources {wb} → " + (f"🔴 **{wa}**" if wa == 0 else str(wa)))
        A("")
        for res, defs in lost:
            losses += 1
            A(f"- 🔴 **`{res}` leaves this biome entirely.** Its only source here was "
              + ", ".join(f"`{d}`" for d in defs) + ".")
        A("")
    if not losses:
        A("✅ No resource leaves any biome. Every cut plant has a survivor covering it.")
    return "\n".join(L) + "\n", losses


def report(rows, tiles) -> str:
    cov = coverage(rows, tiles)
    sole = sole_sources(rows, tiles)
    L: list[str] = []
    A = L.append
    A("# Plant harvest coverage on Ash'karr — what a cut would cost")
    A("")
    A("Generated by `design/Jawa/mods/plant_harvest_coverage.py` from")
    A("`plant_cherrypick_candidates.csv` × `world/ASHKARR_WORLDMAP_tiles.csv`.")
    A("Discharges the second criterion of `PLANT_CHERRYPICK_PASS_1`.")
    A("")
    cut, prov = load_decisions()
    if cut:
        A(f"🔪 **{len(cut)} plant(s) cut by the owner** — "
          + ", ".join(f"`{c}`" for c in sorted(cut)) + f".  <sub>{prov}</sub>")
        A("")
        A("The table below is the roster **before** those cuts, so it still reads as the full")
        A("supply picture. For what the cuts actually cost, run")
        A("`plant_harvest_coverage.py --against-decisions`.")
    else:
        A("⚠️ **Nothing is cut.** Every figure below is the *price* of a future cut, not a")
        A("present defect.")
    A("")

    missing = sorted(b for b in tiles if b not in cov and b not in PLANTLESS_BY_DESIGN)
    A(f"**{len(tiles)} biomes on the planet · {len(cov)} carry reachable plants · "
      f"{len(PLANTLESS_BY_DESIGN & set(tiles))} are plantless by design.**")
    A("")
    if missing:
        A("## 🔴 A biome with no reachable plant at all")
        A("")
        for b in missing:
            A(f"- **`{b}`** — {tiles[b]} tiles, and not one plant in the candidate list "
              f"reaches it. Nothing grows there in any season.")
        A("")

    A("## Per biome")
    A("")
    A("| biome | tiles | plants | resources | wood sources | fragile (sole-source) |")
    A("|---|---:|---:|---:|---:|---|")
    for b in sorted(cov, key=lambda x: -tiles[x]):
        by = cov[b]
        plants = sum(1 for r in rows if b in (r.get('biomes') or '').split('|'))
        wood = len(by.get('WoodLog', []))
        frag = sorted(res for res, ds in by.items() if len(ds) == 1)
        woodcell = ("🔴 **0**" if wood == 0 else ("⚠️ **1**" if wood == 1 else str(wood)))
        A(f"| `{b}` | {tiles[b]} | {plants} | {len(by)} | {woodcell} | "
          + (", ".join(f"`{x}`" for x in frag) if frag else "—") + " |")
    A("")

    nowood = [b for b in cov if not cov[b].get('WoodLog')]
    onewood = [b for b in cov if len(cov[b].get('WoodLog', [])) == 1]
    if nowood:
        A("## 🔴 Biomes with no wood at all — before any cut")
        A("")
        for b in sorted(nowood, key=lambda x: -tiles[x]):
            A(f"- **`{b}`** ({tiles[b]} tiles) — no plant here yields `WoodLog`. "
              f"A colony landing on it has no wood without hauling it in.")
        A("")
    if onewood:
        A("## ⚠️ Biomes hanging on ONE wood source")
        A("")
        A("Cut the named plant and the biome joins the list above.")
        A("")
        for b in sorted(onewood, key=lambda x: -tiles[x]):
            A(f"- **`{b}`** ({tiles[b]} tiles) — `{cov[b]['WoodLog'][0]}`, and nothing else.")
        A("")

    A("## The sole-source roster")
    A("")
    A(f"**{len(sole)} of {len(rows)} plants are the only supplier of some resource in some "
      f"biome.** Cutting one of these does not thin a biome; it deletes a resource from it.")
    A("")
    A("| plant | resource(s) | biome(s) |")
    A("|---|---|---|")
    for d, pairs in sorted(sole.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        res = sorted({r for _, r in pairs})
        bs = sorted({b for b, _ in pairs}, key=lambda x: -tiles[x])
        A(f"| `{d}` | " + ", ".join(f"`{x}`" for x in res) + " | "
          + ", ".join(f"`{b}`" for b in bs) + " |")
    A("")
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--md")
    ap.add_argument("--against-decisions", action="store_true",
                    help="re-derive coverage with the owner's cuts removed; exit 1 if a "
                         "resource leaves a biome")
    ap.add_argument("--decisions", help="path to the decisions file")
    args = ap.parse_args()
    rows, tiles = load_rows(), tile_counts()

    if args.against_decisions:
        cut, prov = load_decisions(args.decisions)
        if cut is None:
            print(f"UNMEASURED {prov}")
            return 2
        text, losses = against_decisions(rows, tiles, cut)
        print(f"decisions: {prov}")
        print()
        sys.stdout.write(text)
        if losses:
            print(f"\n🔴 {losses} resource(s) would leave a biome. Exit 1 — this is a "
                  f"finding for the owner, not a refusal.")
        return 1 if losses else 0
    text = report(rows, tiles)
    if args.md:
        open(args.md, "w", encoding="utf-8").write(text)
        sole = sole_sources(rows, tiles)
        cov = coverage(rows, tiles)
        print(f"wrote {args.md}")
        print(f"  {len(rows)} plants · {len(cov)} biomes with flora · "
              f"{len(sole)} sole-source plants · "
              f"{sum(1 for b in cov if not cov[b].get('WoodLog'))} biomes with no wood")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
