# BLUEDESERT_DESIGN_SITTING_1 — Blue Desert design sitting (bedazzle to full-mod status)

Picked 2026-09-24 as the next biome sitting. It was the runner-up at the
Nightside Ice pick (`57b28a3f7`), excluded only because 11 art jobs sat in the
pipe; the owner cleared that this session: *"Blue desert is still eligible."*
(typed). Those 11 jobs are still in `infrastructure/artpipe/pending/`
(chimeglobe ×2, glassfern ×3, palefloss ×3, dorrak/krissek dessicated, krissek
halo mote) — the sitting does not wait on them; 9 Blue Desert jobs are already
in `done/`.

Feeds `BLUEDESERT_RM_MOD_BUILD_1` (FOUNDRY), whose every step is OWED — this
sitting is the design input that item is waiting on. Precedent shape:
`SUMP_DESIGN_SITTING_1` → `WEEPING_STONES_DESIGN_SITTING_1` →
`NIGHTSIDE_ICE_DESIGN_SITTING_1` (all closed).

## Inputs — read before the sitting, do not re-invent

- `design/Jawa/worldbuilding/biomes/the_blue_desert.md` — the sheet; its
  `## Owed` list (line ~236) IS the agenda skeleton.
- `design/Jawa/worldbuilding/creatures/blue_desert_hydrocarbon_life.md` — the
  authored cast (`BLUE_DESERT_LIFE_AUTHORING_1` is CLOSED; the cast exists —
  vekkit, dorrak, krissek, chimeglobe, glassfern, palefloss…). A sitting that
  invents before it reads will re-invent.
- `design/Jawa/worldbuilding/biomes/rosters/the_blue_desert.json` — roster
  (fauna/flora/fish/evictions keys already present).
- `infrastructure/state/items/BLUEDESERT_RM_MOD_BUILD_1.md` §2 — the def as it
  stands (weather all zeroed to Clear 100, terrain Ice only, vanilla diseases).

## spec

Rule, with the owner at the bench, everything the sheet still owes so the
build item has complete design input:

1. **Weather/engine feasibility** — the Haze; ice-sand drift as accumulating
   weather (snow-depth mechanic reskinned); ice-fog range/accuracy defs.
2. **Remaining fauna/flora authoring** — Swallowers, Burners (halo VFX +
   detonation-on-death), Pickers; transparent fractal flora with the
   warm-detonation comp. Multi-homed rows judged here, per
   `BIOME_SPECIFIC_FAUNA_LAW_1` (per-biome sitting, not sweeping rules).
3. **Blue-ice** — mineable + item; water-taxonomy row as distilled-purity
   (`WATER_KINDS_TAXONOMY_1`).
4. **Quarry epochs** — which civilizations, in what order; alien script
   provenance; quarry injection templates (KCSG / dungeon-item method).
5. **Ship contribution row** (`BIOME_SHIP_CONTRIBUTIONS_1`) — what players
   take aboard from this biome.
6. Lobe-mosaic note: `HORRORWASTES_BIOME_DISSOLVE_1` tile work stays out of
   scope (painting is terminal, `BIOME_PAINT_ONCE_AT_THE_END_1`).

## verify

Every Owed bullet on the sheet either ruled (recorded on the sheet/rosters, by
card or typed word) or explicitly re-ticketed; rosters updated; sitting closed
with the commit hash of the applied rulings.

## criteria

`BLUEDESERT_RM_MOD_BUILD_1` can be claimed by FOUNDRY with no design question
left open — same bar Nightside Ice met ("design input COMPLETE").
