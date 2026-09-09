# rosters/ — the landed fauna/flora assignment, as data

One JSON per biome sheet (`<sheet>.json`, sheet = the biomes/*.md stem), plus `_global.json`
(planet-wide dispositions). Written by the BIOME_FAUNA_ASSIGNMENT_SITTING_1 pass
(owner rulings 2026-09-09, recorded in that item). These files are the SOURCE the
generators read; the XML patches are derived, never hand-edited. Review-sheet verdicts
from the owner amend THESE files, then regenerate.

## Per-biome JSON shape

```json
{
  "sheet": "desert",
  "defNames": ["Desert"],
  "tiles": 3932,
  "authored": "2026-09-09",
  "law_sources": ["desert.md", "_assignment_prep.md §2", "_freeze_rulings_2026-09-07.md R22"],
  "fauna": [
    {"def": "Bantha", "commonality": 0.8, "action": "keep|import|adjust-keep",
     "band": "huge-herd", "law": "herds wanted — a herd is a mobile shade structure",
     "note": "icon"}
  ],
  "evictions": [
    {"def": "Wraid", "reason": "ban 3 pursuit: predator + spd 5.0 (MEASURED)",
     "disposition": "adjust-keep-here | move:<defName-of-new-home-biome> | homeless-reserve | cut:<ruling ref>"}
  ],
  "stat_adjustments": [
    {"def": "Wraid", "field": "moveSpeed", "from": 5.0, "to": 4.4,
     "authority": "owner card 2026-09-09: SW staples adjust-and-keep"}
  ],
  "flora": [{"def": "AB_PlantX", "commonality": 0.5, "law": "..."}],
  "flora_purged": [{"def": "PlantSaguaroCactus", "reason": "Earth-nameable (owner card 2026-09-09)"}],
  "fish": {"ruling": "no fish — no standing water", "list": []},
  "new_defs": [
    {"name": "glass-nub light-pipe flora", "kind": "plant|creature",
     "mechanic_load": "none|C#: <what>", "from_sheet": "dune_sea §10"}
  ],
  "confidence": [{"claim": "Shyrack is a slow flier", "status": "UNMEASURED", "why": "register flies flag broken"}]
}
```

## Rules
- `commonality` is a DESIGN CHOICE; stats cited in `reason`/`law` lines carry
  MEASURED (from `creature_register_rows.json`) or UNMEASURED (by-name knowledge —
  the register's `flies` special is broken, life stages absent).
- Every fauna/evict row cites the sheet law it passed or failed. No bare verdicts.
- defNames are the LIVE ones (bare Mlie names, no RSW_ anticipation); verify each
  against the register / def dump before writing — a wrong-case defName no-ops silently.
- Injection layers (fall_line, wreck_fields, the_lantern_deeps) get files too; their
  `defNames` list the UNDERLYING defs they inject over and their entries are additions,
  not replacements.
- HorrorWastes gets no file (dissolving). ExtremeDesert = one merged file
  `dune_sea_deep_desert.json` (R22 strict intersection).
- `_global.json` holds: the ubiquity-25 dispositions, the Earth-five planet-wide
  evictions, the homeless reserve list, the Cherry Picker cut list (each cut cites its
  ruling), and the Grindterra homeless-by-default rule (Grindterra defs are `GRim*`;
  `GR_*` is Vanilla Genetics Expanded — chimeras, judged per sheet law normally).
