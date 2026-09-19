# ARMOURY_LEATHER_RATINGS_REGEN_STALE_1

Found while verifying ARMOURY_DECLARER_ATTRIBUTION_FLIP_1 (2026-09-08): a
fresh `gen_armour_patch.py` run against the current (post-naming-sprint,
post-dedupe-sprint) live dump does NOT match the committed
`src/RimStarWars/Armoury/Patches/Armour_Leather.xml` or `Armour_Ratings.xml`.

## finding
- `Armour_Leather.xml`: committed file has a `RSW_TelluroxShell` block (baseline
  hide leather profile) that a fresh regen does NOT produce — either the def
  no longer exists under that name (renamed again since?) or the generator's
  matching logic no longer finds it.
- `Armour_Ratings.xml`: a fresh regen produces a `guy762_Backpack_scorch`
  block (beskar tier) that is NOT in the committed file — either this def is
  new/newly-matched since the last regen, or the committed file is simply
  stale relative to it.
- `Armour_DamageCategories.xml`'s equivalent staleness was already fixed as
  part of ARMOURY_DECLARER_ATTRIBUTION_FLIP_1 (that one was definitely the
  declarer() nondeterminism). These two are a DIFFERENT, broader kind of
  drift — likely just "nobody re-ran the generator since the naming/dedupe
  sprints landed today" rather than a generator bug, but it needs verifying
  before blindly overwriting: a wholesale live-file replacement from a fresh
  regen risks pulling in unreviewed churn (see the 2026-09-08 lesson
  "patch-a-curated-artifact-never-reallocate" — diff to a temp path first,
  never regenerate in place blind).
- `Armour_Penetration.xml` was confirmed byte-identical to a fresh regen —
  not affected.

## verify
```
PROVE   a fresh gen_armour_patch.py --out <scratch> run's Armour_Leather.xml
        and Armour_Ratings.xml, diffed line-by-line against the committed
        versions, explained (why RSW_TelluroxShell dropped / why
        guy762_Backpack_scorch appeared) before either is overwritten
EXPECT  the diff is pure staleness (defs renamed/deduped, not a generator
        regression) - confirm by checking whether RSW_TelluroxShell and
        guy762_Backpack_scorch still resolve in the current def dump at all
LIES    diffing against a def dump that itself predates today's naming/dedupe
        sprints - re-check the dump's own fingerprint/capture timestamp first
```

## criteria
Done when both files are regenerated (or the drift is explained as
intentional and left alone) with the reason recorded, and `validate_patch.py
--live` + `xml.etree.ElementTree.parse()` both pass clean afterward.
