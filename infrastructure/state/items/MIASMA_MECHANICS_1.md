# MIASMA_MECHANICS_1 — the Miasma C# kit

## spec — the C# kit

Per `design/Jawa/worldbuilding/biomes/the_miasma.md` (FROZEN,
`BIOME_FREEZE_FABLE_REVIEW_1`): the surge/salt-line system (fresh→brine map
axis, storm-driven movement, stranding pools) · fever-forged boon tables ·
miasma weather (exposure + the mangals' visible thriving) · warden-mother
set-piece placement.

**The engine mapping is drafted**:
`design/Jawa/worldbuilding/biomes/kits/miasma_kit_spec.md` (2026-09-11) — 6
mechanics (M1 gradient axis, M2 surge, M3 stranding pools, M4 miasma weather,
M5 fever-forged, M6 warden mothers), 2 ruled-comp reuses from
`ALPHA_MECHANICS_KIT_1`, 6 new RM_ classes (1 L, 3 M, 2 S), hard-ban
compliance table for the sheet's six 🔴 bans, build order, and 3 open owner
cards.

The governing rules from the sheet: the salt line moves with every surge and
**no map state is permanent**; the surge is storm-driven, **never scheduled**;
fever-forged boons are hediffs, **never genes** (the gene machine is the
Slime's); warden mothers are **placed set-pieces, never random spawns**.

## verify

- [ ] The 3 owner cards in the kit spec's "Open owner cards" section are ruled
      (card sitting; see also `KIT_SPECS_CARD_SITTING_1` for the sibling kits'
      batch).
- [ ] Every ❓ engine claim in the kit spec is re-checked against the live 1.6
      assembly before its C# is spent (the RimSage index is 1.5-era; in
      particular: Odyssey tide machinery, TerrainGrid under-grid API, hediff
      removal-reason seam, hive-anchor ThinkTree nodes).
- [ ] Build lands per the spec's build order, after `ALPHA_MECHANICS_KIT_1`;
      `LIQUID_TYPES_MOD_1` grades exist (or stub) before M1's terrain bands.
- [ ] A quicktest map in the biome shows: forced miasma weather with no rain
      reachable; the salt line drawn and moving during a surge; a pool with a
      stranded spawn after a recede; a placed warden that never leaves its
      anchor.

## criteria

- Every mechanic traces to a sheet section; no lore invented outside
  **INVENTED** tuning values.
- All six §6 hard bans hold in the shipped defs (linter-checkable where the
  sheet says so: no rain weather reachable, no scheduled-period field on the
  surge, no gene in any boon table, no medical trade good from this kit).
- Naming per `design/NAMING_SCHEME_PLAN.md`: mechanisms `RM_`, Miasma content
  `RUT_`; "Jawa" is lore text only.
