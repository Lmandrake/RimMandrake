# MECHANOID_BIOME_PRESENCE_REVIEW_1 — which biomes contain mechanoids and ancient dangers

Owner, 2026-09-06 (propane lakes sitting): *"The presence of Mechanoids and ancient
dangers here return suddenly (we should do a review of which biomes even contain them...
not all of them should!)"*

## spec
- Inventory, per biome, everything mechanoid-class and ancient-danger-class that can
  currently spawn or sit there: raid/incident sources (mechanoid raids, clusters,
  ancient dangers/complexes, Anomaly if `ANOMALY_EXCEPTION_ACCESS_1` allows), map
  generation (ancient shrines, mech clusters), Inhabited injections, faction bases.
  Read defs and the injection specs; never guess.
- Propose the ALLOWED map: the two magnetic poles get them by ruling — the Rust
  Cathedral (`AB_MechanoidIntrusion`, substellar) and the antistellar propane lakes
  around the ancient war lab; the Assailant remnants line is separate (the Horrors are
  not mechanoids). Everything else is a case to argue, biome by biome, to the owner.
- Add rows for the Lantern Deeps (`the_lantern_deeps.md`): the Shard-minds animating dead
  droids/suits, the mindstone's droid race, and the mechanoid production facility
  (`MECHANOID_ORIGIN_CANON_1`) — "ancient dangers" by the owner's own hand.
- Output as DATA (biome × source × allowed/denied), fed into the freeze review
  (`BIOME_FREEZE_FABLE_REVIEW_1`) as a column.

## verify
The table exists; the owner has ruled each denied row; the storyteller/incident
restrictions needed to enforce it are listed with defNames.

## 2026-09-09: DRAFT table built (BENCH, owner AFK) — awaiting his ruling
`design/Jawa/worldbuilding/mechanoid_biome_presence_draft.md` (`d927f4b7`): per-biome
AMBIENT/ANCIENT/RAIDS verdicts argued from the sheets; the two poles marked RULED;
two UNDECIDED (AridShrubland ancients, FeverWood pools). Carries one doctrine
proposal needing his word: random mech RAIDS deny planet-wide — mech violence is
provoked/scripted only (consistent with both poles). Mechanism notes verified via
source where possible; per-biome raid gating would need Harmony, planet-wide is XML.

**Fed 2026-09-11 (legends sitting)**: surface Sentinels are SPARSE lost units
— self-repairing, slowly devolving, never replenished; the factory trickle
feeds secret caches + Cathedral vaults only. Density and encounter framing per
`design/Jawa/worldbuilding/mindstone_arc_legends.md` §Canon corrections.
