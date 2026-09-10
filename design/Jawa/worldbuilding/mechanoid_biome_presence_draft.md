# Mechanoid & ancient-danger presence per biome — RULED

**RULED by the owner, 2026-09-10 morning batch** (`MECHANOID_BIOME_PRESENCE_REVIEW_1`,
`MORNING_RULING_BATCH_1` item 9): the table below is ratified as written, the axis-3
planet-wide doctrine is ratified, and both formerly-UNDECIDED rows are DENY.
Enforcement (the XML patches per the MECHANISM section) is FOUNDRY build work —
`MECH_PRESENCE_ENFORCEMENT_1`. Rows argued from each biome's sheet
(`design/Jawa/worldbuilding/biomes/*.md`, bindings per `_def_bindings_2026-09-09.md`).
Verified at drafting: `_freeze_matrix.csv` has no mechanoid column and
`_freeze_rulings_2026-09-07.md` no mechanoid ruling — this table is the first and now
authoritative data on the axis.

## The three axes

1. **AMBIENT** — mechanoid map presence / mech clusters as random storyteller events.
2. **ANCIENT** — ancient dangers / cryptosleep ruins placed at map generation.
3. **RAIDS** — mechanoid raid legality (random storyteller raids by `Faction.OfMechanoids`).

Verdicts: **ALLOW** / **DENY** / **RARE** (present but tuned sparse) / **RULED**
(owner already decided) / **UNDECIDED** (sheet gives no purchase; the decider is named).

## Planet-wide doctrine for axis 3 — RULED (owner, 2026-09-10)

**Random mechanoid raids: DENY everywhere.** The Scarlands sheet states the law of the
planet's machines: the Forgotten Sentinels *"defend, never raid, never pursue... never
explain."* The Rust Cathedral's own sheet agrees — its sanctioned mechanoid violence is
*provoked movement* (deep-drilling → "massive mechanoid movement"), never a storyteller
rolling a raid. Under this doctrine mechanoid violence reaches the player only as
scripted/provoked response: Cathedral trespass, war-lab breach, Deeps mining, Forge-tower
or Scald-tower assault. This is also the cheap doctrine to enforce (see MECHANISM: a
planet-wide DENY is XML; per-biome mixed legality needs C#). Every RAIDS cell below
assumes it. Ratified 2026-09-10 — no biome keeps vanilla-style random mech raids, so
axis-3 enforcement is the XML-only route (zero the mechanoid FactionDef's
raid-commonality curve; confirm the exact field name on the def before patching).

## The table

| def (tiles) | sheet | AMBIENT | ANCIENT | RAIDS | argument (from the sheet's identity) |
|---|---|---|---|---|---|
| `AB_MechanoidIntrusion` (236) | the_rust_cathedral | **RULED ALLOW** | **RULED ALLOW** | **RULED** (provoked only) | Pole by ruling: "the densest mechanoid ground on the planet"; even here raids are retaliation (deep-drill → massive movement), not storyteller rolls. |
| `AB_PropaneLakes` (2531) | the_propane_lakes | **RULED ALLOW** (near Impact Site) | **RULED ALLOW** (the lab IS the danger) | **RULED** (guardian response) | Pole by ruling (`ANCIENT_WAR_LAB_1`): "lab guardians — mechanoids and ancient dangers, the last watch," injected as you near the Impact Site; ban #8 keeps Assailants as study subjects, never residents. |
| `RUT_PropaneLake` (57) | the_propane_lakes | **RULED-adjacent** | **RULED-adjacent** | **RULED-adjacent** | Same sheet, same province — rides the pole ruling, not argued separately. |
| Scarlands (90) | the_scarlands | **ALLOW** | **ALLOW — opened only** | DENY | The last stand: Forgotten Sentinels are resident emplaced defenders; but the sheet says the vaults are "all already opened and destroyed" — so ruined/opened dangers yes, intact sealed cryptosleep no; and Sentinels "defend, never raid, never pursue." |
| the Forge: `AB_PyroclasticConflagration` (31) + `LavaField` (8) + `Volcano` (5) | the_forge | **ALLOW — native only** | **ALLOW — towers only** | RARE (provoked tower defense) | Cathedral's legacy smeltery: "old mechanoid-type machines... doing something unrevealed" and tender-garrisoned tower dungeons ARE the biome; but a vanilla cluster dropping from orbit dilutes "the only unstolen fire" — its machines are ancient and local, never arrivals. |
| `RUT_TheScald` (312) | the_scald | **ALLOW — tower only** | **ALLOW — tower only** | DENY (tower defends itself) | The boiler's machine content is entirely the dark tower (`SCALD_DARK_TOWER_1`, Rakatan high command, "fiercely defended") — site-scoped; the open pan holds only dead wrecks in the shallows, salvage priced in burns. |
| Wasteland (1126) | wasteland | RARE (dormant) | **ALLOW** | DENY | Rakatan-vs-Assailant war ground with "no outlet": buried arsenals, trench systems, warcasket sarcophagi ARE ancient dangers; a dormant machine priced in dose fits, a live roaming one breaks the law that danger here is environmental, never creature-shaped. Sheet's own bans (no anomaly entities, no bioweapon fauna) stand. |
| `AB_TarPits` (42) | the_sump | DENY | **ALLOW** | DENY | "The trap that remembers": the sheet already weights "sunken machines, sealed casings" and era booby-traps ("MORE likely than either") into dig tables — buried dangers are canon; nothing in the tar is active until dug. |
| `ZBiome_DesertOasis` (223) | weeping_stones | DENY | **ALLOW** (relic-tech, guardian-light) | DENY | The sheet already ships ancient structures — relic vane arrays, cistern shafts, an `AncientUplink` landmark loadout, "a dry ring around a silent machine"; but the water is truce-bound and its machines are dead — no active mechanoids, no violence. |
| `ZBiome_Badlands` (985) | the_cracked_lands | DENY | **ALLOW** | DENY | Floods "tear open ruins, wash buried tech from the banks" — mapgen ruins are the pre-flood state of the biome's own salvage engine; no machine residents, only road traffic. |
| Desert (3932) | desert | RARE (dormant, in shade) | **ALLOW** | DENY | "The shade is the dig site" — middens of "bones, debris and wreckage" admit buried ruins and the odd dormant machine as salvage; but this is the calm home biome of the sprint economy, so sparse and dead, never a front. |
| `ExtremeDesert` (3172) | dune_sea + deep_desert | DENY | RARE (sealed, buried) | DENY | The emptiness law: "time does not pass," and dayside wreckage is "sealed, dry, uncorroded," revealed only by dune migration — a rare intact sealed vault fits perfectly; a smoking crashed cluster is exactly the clutter the emptiness resists. (Deep-desert note: "a droid is invisible to the food web" is a player/Jawa mechanic, not a mechanoid-presence argument.) |
| `BiomeGRimond` (1029) | the_blue_desert | DENY | RARE (ice quarries) | DENY | The ice's war content is deliberately Horror-class spore forms, injected not resident — and Horrors are not mechanoids (item's own line); the ancient ice quarries with layered warning scripts give mild purchase for sealed ancient structures, nothing more. |
| `PoisonForest` (557) | poison_forest | DENY | RARE (mundane, guardian-free) | DENY | Chemistry biome; its ruins are capped wellheads, sealed shelters, corroded leavings of unnamed scavengers — small sealed structures fit, but the sheet keeps them mundane-industrial: no mech guardians inside. |
| `BiomeCypreJungle` (235) | the_greentide | DENY | RARE (river graves) | DENY | "Water is the only argument" — the free-for-all is biological; the salt-pan "river graves" give mild purchase for washed-down wreck deposits (the sheet sites Free Droid enclaves on them — faction content, not mechanoids). |
| `AB_MycoticJungle` (2258) | the_rot | DENY | DENY | DENY | "Nature won here": the Rot composted the war itself; its ruins-analogue is the digestion site, a biological mechanic already its own — a steel box full of sleepers contradicts the gut of the planet. |
| `AB_GelatinousSuperorganism` (96) | the_slime | DENY | DENY | DENY | The living registry reads everything that touches it — machines are the one thing it cannot read and has no use for; the item's own instinct ("a living genetic database arguably repels machines") holds; even the Helix lost interest. |
| `AB_OcularForest` (179) | the_contagion | DENY | DENY | DENY | "The weapon at open throttle" — this is the biological pole; the sheet rules "Assailant arsenal, never Wasteland content," and the Cathedral's hatred of it is "ideological... not adjacency" — explicitly not a physical front, so no machines here at all. |
| `AB_FeraliskInfestedJungle` (161) | the_webwork | DENY | DENY | DENY | Sheet-explicit: the Wyyyschokk "HATE droids and preferentially destroy them" — "the one terrain where a droid force is a liability"; an intact machine cache under the loom would have been cracked centuries ago. |
| `AB_MiasmicMangrove` (93) | the_miasma | DENY | DENY | DENY | The lifeboat at the drain: what washes in is "sterilized war-mulch" — biology, not hardware; its war legacy is engineered disease (§GM), which is precisely not a machine register. |
| `ZBiome_Grasslands` (222) | the_pyrelands | DENY | DENY | DENY | The Rakatan legacy here is genetic and alive — an engineered crop still burning 25,000 years on; nothing of theirs is buried steel, and the standing burn keeps no ruins. |
| `RUT_NightsideIce` (1506) | nightside_ice | DENY (sheet-explicit) | DENY (calving is the channel) | DENY | The sheet already defers: mech clusters/psychic drone are "not here by default — the propane country and the Deeps." Its war debris ("the terramanufacture's collapsing machine, the war's cocoons") arrives by glacial calving — the biome's own delivery mechanic, not mapgen scatter. |
| `AB_RockyCrags` (1170) | forsaken_crags | DENY | DENY | DENY | The Dark's register is Cryptid-only ("the Forsakens never appear"); its ruins are wind-farms and seep-works, fugitive infrastructure — machine dangers would floodlight a biome built on dread. |
| `AridShrubland` (665) | arid_shrubland | DENY | **DENY** (ruled 2026-09-10) | DENY | "The hush" gives machines nothing — concealment favours living ambushers. Owner ruled ANCIENT DENY: the hush belt is deliberately clean ground between the desert and the shade, not dig-site country. |
| `COMIGO_GreaterSwamp_Tropical` (43) | the_fever_wood | DENY | **DENY** (ruled 2026-09-10) | DENY | The giant stillness has no machine mention at all. Owner ruled ANCIENT DENY: the trees drank the history along with the chaos — the black still pools hide nothing pre-war. |
| `RUT_TwilightSea` (479) | terminator_sea + the_twilight_deep | DENY | DENY | DENY | The last ordinary sea — purely biological, Compact-held below; the engine already refuses shrine scatter in water biomes (see MECHANISM), so DENY costs nothing. Sea-bottom content is deferred to the diving mods. |
| `RUT_GreySea` (429) | terminator_sea + the_grey_deep | DENY | DENY | DENY | The statuary's encased soldiers and ruined vehicles are a PRESERVATION register (third of the tar/scar/brine triptych), meant to be seen, not to wake — an ancient danger that fights back would break the stillness that is the sheet's whole point. |

## Injection layers (not painted defs — rows required by the item spec)

| layer | class | verdict | argument |
|---|---|---|---|
| The Lantern Deeps — Shard-minds animating dead droids/suits | ancient-danger-class | **ALLOW (owner's own hand)** | `the_lantern_deeps.md` §8 / `MECHANOID_ORIGIN_CANON_1`: the Shard-minds ARE the Deeps' danger; nightside_ice's own sheet points mech clusters here ("the propane country and the Deeps"). |
| The Lantern Deeps — mindstone droid race | faction/race, not a spawn | **RULED-adjacent** | The "wild cousins" — potential allies against "the insane enslaved one"; presence is narrative (dialogue, quests), never an ambient-spawn axis. Rides `MECHANOID_ORIGIN_CANON_1`. |
| The Lantern Deeps — mechanoid production facility | site/dungeon | **RULED-adjacent** | Working-or-slumbering restocker of the Forgotten Sentries; a site with a restore-or-not choice, not a mapgen scatter. Rides `MECHANOID_ORIGIN_CANON_1`. |
| Fall Line (wreck deposition on desert) | injection on Desert | DENY mechanoids; its own wreck content ALLOW | `fall_line.md`: fresh orbital wreckage, feral (memwiped) droids, an `AncientGarrison` vault candidate — mundane machine salvage, Empire salvage-rights ground; explicitly not Cathedral or war-lab territory. |
| Wreck fields (superseded by fall_line) | dead proposal | DENY (its own hard ban) | "No mechanoids, no active machines, no functioning AI... If a wreck fights back, it is Cathedral content and belongs at θ 0." |
| Assailant weapon remnants (Horrors) | separate axis by ruling | out of scope here | The item's own line: "the Horrors are not mechanoids." Raid-only faction, no settlements — ruled on its own sheet. |

## UNDECIDED list — empty (all three resolved by the owner, 2026-09-10)

- `AridShrubland` ANCIENT → DENY (clean ground). `COMIGO_GreaterSwamp_Tropical`
  ANCIENT → DENY (the pools remember nothing). Axis-3 doctrine → ratified.

## MECHANISM sketch — how each axis is actually enforced

Verified against RimWorld 1.6 source/defs via `mcp__rimsage__` (source reads, not memory)
by a dedicated verification pass, 2026-09-09. Everything below is from actual
`read_csharp_symbol`/`get_def_details` output unless marked UNVERIFIED.

**Axis 1 — mech clusters: XML.** `IncidentDef` carries real
`allowedBiomes`/`disallowedBiomes` fields (verified in `IncidentDef.cs`), applied
generically upstream in storyteller target-filtering; the shipped `MechCluster`
IncidentDef just doesn't set them, and `IncidentWorker_MechCluster.CanFireNowSub`
checks only Royalty + `Faction.OfMechanoids` (read in full — no biome check). A
PatchOperation adding `<disallowedBiomes>`/`<allowedBiomes>` to `MechCluster` enforces
the whole column. "RARE" (reduced-but-nonzero frequency per biome) is finer than
on/off and would need a Harmony patch on `CanFireNowSub` — or accept ALLOW/DENY only.

**Axis 2 — ancient dangers at mapgen: XML.** `GenStep_ScatterShrines` is registered
inline in `BasePlayerMapGenerator.xml` (fires on every player-home map; 75% skip on
non-starting maps; `allowInWaterBiome=false` already excludes the two seas). The
per-biome hook is `BiomeDef.preventGenSteps` / `BiomeDef.extraGenSteps` (verified
fields; live vanilla usage in `Glowforest.xml`, `GlacialPlain.xml`). DENY = add the
shrine/ruin GenStepDefs to that biome's `preventGenSteps`; RARE = prevent the stock
genstep and add a cloned GenStepDef with a lower `countPer10kCellsRange` via
`extraGenSteps`. Odyssey's `TileMutatorDef` adds a per-TILE layer with its own
`extraGenSteps`/`preventGenSteps` + `biomeWhitelist`/`biomeBlacklist` — the right
tool for site-scoped rows (the Scald tower, the Forge towers, the Impact Site).
No C# needed. ⚠️ Contents trap: vanilla ancient shrines can wake with mechanoid
guardians inside — a biome ruled ANCIENT-ALLOW but AMBIENT-DENY needs its shrine
contents curated (exact vanilla contents table UNVERIFIED — check the shrine symbol
resolvers before building).

**Axis 3 — mechanoid raid legality: C# for per-biome, XML for planet-wide.** The
raid-faction chain (`IncidentWorker_RaidEnemy.TryResolveRaidFaction` →
`PawnGroupMakerUtility.TryGetRandomFactionForCombatPawnGroupWeighted` →
`FactionCanBeGroupSource`) was read end-to-end: it checks temperature range, world
LAYER white/blacklists (orbit/space — not biome), `earliestRaidDays`, and weights by
`f.def.RaidCommonalityFromPoints(points)` — **no BiomeDef reference anywhere**.
Per-biome mixed legality therefore needs a Harmony patch on `FactionCanBeGroupSource`
(add a check on `((Map)parms.target).Biome`). BUT under the proposed planet-wide
doctrine no biome filter is needed: zeroing the mechanoid FactionDef's
raid-commonality curve kills random mech raids globally in XML alone (the weighting
call is verified; the exact XML field name for the curve is UNVERIFIED — confirm on
the FactionDef before patching), leaving scripted/provoked mechanoid violence
(quests, site defense, retaliation events) untouched. `RaidStrategyWorker` also
honours `TileMutatorDef.blacklistedRaidStrategies` (verified, `RaidStrategyWorker.cs:70`)
— a strategy filter, useful for site tiles, not a faction ban.

**Per-axis cost summary**: AMBIENT = XML patch on one IncidentDef; ANCIENT = XML
patches on BiomeDefs (+ TileMutators for site rows); RAIDS = XML if the planet-wide
doctrine is accepted, Harmony C# if any biome keeps random mech raids while others
deny them.
