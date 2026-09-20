# The Rot — card vs shipped reconciliation — 2026-09-20

Card: `design/Jawa/worldbuilding/biomes/the_rot.md` (FROZEN, read-only).
Shipped: `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_TheRot.xml`,
`src/RimUtinni/RotSporeKit/`, `src/RimUtinni/UtinniPatches/Patches/RotSpecies_NamesAndSizes.xml`.
Ground truth inherited from `Transient/biome_owed_audit_20260920/deeps_organic.md` (the_rot.md section).

## 1. Roster (flora/fauna)

- **Flora: IN SYNC.** `RUT_TheRot.xml` `<wildPlants>` has 32 entries; `rosters/the_rot.json`
  `"flora"` array has 32. All 12 AlphaBiomes donor species + all 20 `RUT_`-raided
  Fungal Forest species (nuitae/wrinklecap/nogtyl/arpeau/dewshrooms/fruiting bodies/
  pusmelon/rustpuff/sagecrust/flakespire/bleeding tooth/crimson cap/violet wimple/
  grey lady/shinecap/brightbell/mortal morel/skulltop/blastpod/AgariluxPrime) are wired.
  CONFIRMED.
- **Fauna: MAJOR DRIFT, CONFIRMED.** `rosters/the_rot.json` `"fauna"` array (the ruled
  admission list, directly citing the card's own §7b "keep the strange" language) has
  **28 species**. `RUT_TheRot.xml` `<wildAnimals>` wires only **10** (8 as of yesterday
  + `AA_AngelMoth`/`Snoruuk` added today per `ECOSYSTEM_PYRAMID_LAW_1`). Ruled-but-unwired:
  `BMT_ChemSnail`, `BMT_GlowBat`, `BMT_Pillbug`, `BMT_GiantSlug`, `BMT_GiantSnail`,
  `BMT_BovineBeetle`, `BMT_CaveSpider`, `ShiroTrap`, `BMT_ColonyPustuleHornetQueen`,
  `BMT_PustuleHornetQueen`, `BMT_PustuleHornetSpawned`, `BMT_ColonyPustuleHornet`,
  `BMT_PustuleHornet`, `AA_AnimaColossus`, `BMT_SmogMoth`, `BMT_Thrumbungus`,
  `BMT_Yooka`, `MA_Sporemole` — 18 species. (`BMT_FungalWeevil`/`BMT_FungalMantis` in
  the roster ARE covered, just under swapped defNames `RSW_FungalWeevil`/`RSW_FungalMantis`
  from the SWBestiary import — not a gap.) The card's own text ("keep the strange — glow
  bats, cave spider, bovine beetle, chem snail, pillbug, silk moths... giant slugs/snails")
  names exactly the missing set. **Believe the roster JSON/card over the shipped def** — the
  JSON is the def's own cited wiring source and nothing suggests a deliberate cut.
- **Inkcap substitution, CONFIRMED but incomplete.** Card names "inkcap (fiber, no light)"
  as ingested; no `BMT_Inkcap` exists in the donor. `RotSporeKit_Flora.xml` documents the
  resolution as `RUT_MoonlessStripesPlant` ("moonless stripes") — a reasoned substitution,
  not a gap in judgment — but that def is **not present** in `RUT_TheRot.xml`'s
  `<wildAnimals>`/`<wildPlants>` either. Minor, CONFIRMED.
- Donor vanilla zoo (rat/boar/alpaca/cassowary/chinchilla/raccoon/cobra/warg): confirmed
  absent from `<wildAnimals>` — eviction ban honored. CONFIRMED.

## 2. Names

- **The flagged suspects are REFUTED.** `RUT_NuitaeMarsh`, `RUT_WrinklecapMarsh`,
  `RUT_GreenArpeau`, `RUT_NogtylMarsh`, `RUT_MortalMorelPlantGrowable` all carry the same
  ruled campaign labels as their base defs (`nissik gill`, `rukka cap`, `churrun mast`,
  `brommok timber`, `vennik salve` respectively) — verified directly via
  `xml.etree.ElementTree` over `RUT_RotSporeKit_Flora.xml`. CONFIRMED: the marsh/growable
  siblings do NOT carry stale labels.
- **The 19 donor `AB_`/`AA_` renames are wired via a real patch**,
  `src/RimUtinni/UtinniPatches/Patches/RotSpecies_NamesAndSizes.xml` (668 lines,
  `ROT_FLORA_FAUNA_VERDICTS_1`): each donor def gets `PatchOperationConditional` label +
  description + `visualSizeRange`/`drawSize` replacement, matching
  `rot_flora_fauna_names.md`'s ruled widths, plus `texPath` overrides for the art that has
  landed (11 flora + 5 fauna body-stage overrides, plus a v3 landing for AgariluxPrime and
  RecurvedStropharia). CONFIRMED IN SYNC for all 19.
- **Gap: today's roster additions are unnamed.** `AA_AngelMoth` and `Snoruuk`, added to
  `<wildAnimals>` today per `ECOSYSTEM_PYRAMID_LAW_1`, are not in
  `rot_flora_fauna_names.md`'s 48-row ruling table and carry no rename patch — they ship
  under their raw donor/import labels ("angel moth", "Snoruuk"). Small, CONFIRMED, and
  likely just not-yet-done rather than a disagreement.
- `rot_flora_fauna_names.md` itself is marked **DRAFT — applied provisionally**, "his to
  overrule in the morning" (written 2026-09-19) — the names are live in the patch but the
  naming doc's own status line is stale; nothing found suggesting he overruled any of it.

## 3. Mechanics

Per-mechanic status (built / partial / absent), refining the inherited audit where a direct
check changed the answer:

| Mechanic (card §) | Status | Where |
|---|---|---|
| Heat-generating gene / metabolic warmth | BUILT | `RUT_Gene_Furnaceblood` (`RUT_RotSporeKit_Furnaceblood.xml`), `RM_WarmGroundExtension` on the biome def itself |
| Heat-pushing produce comp (grown furnace) | BUILT | `RUT_GrownFurnace`, same `ROT_WARM_MAT_1` |
| Sheen weather + compatibility hediff/exposure ladder | BUILT | `RUT_SheenFall/Storm/Mist` WeatherDefs, `RUT_SheenExposureLock` condition, `RUT_HediffComp_SheenExposure.cs`, wired live in `RUT_TheRot.xml`'s `baseWeatherCommonalities`/`biomeMapConditions` |
| Live-item viability clock (dies refrigerated, dies delayed) | BUILT | `RM_Patch_LivePrepViability.cs` + `RUT_RotSporeKit_LivePreparations.xml` (`CompTemperatureRuinable`+`CompLifespan`) |
| Instant composting / rot clock (item decay) | PARTIAL | `RM_AcceleratedRotExtension` modExtension is on the biome def (item/corpse rot multiplier), but no map-wide "rot-rate" GameConditionDef exists — the sheet's §3 "everything decays much faster" reads as built for items, not as an ambient condition |
| Guardian repertoire per tea species | **PARTIAL, CORRECTING THE INHERITED AUDIT.** `RUT_RotSporeKit_GuardianGroves.xml` (233 lines, `ROT_GUARDIAN_GROVES_1`) defends 4 named tea-source mushrooms with distinct mechanisms: `RUT_AgelessCap` (gas-emitter, spore cloud), `RUT_RegenerantVeil` (plant-alarm comp, wakes fauna via manhunter), `RUT_EuphoricCrown` (undefended directly, protected by its own `RUT_FalseFruit` lure/trap). The inherited audit called this UNFILED/UNCERTAIN — it is actually built for the four §7-named species, just not filed as a rimflow item under an obviously-searchable name. |
| Symbiont parasites (3 ratified pairs) | LIKELY BUILT, not independently verified this pass | `RUT_RotSporeKit_SheenHediffs.xml`/`LivePrepHediffs.xml` exist and are substantial; did not line-check the exact 3 pairs against the card |
| Health-sharing comp (2 variants: true wound-split, tend-aura) | ABSENT | confirmed no `CompHealthShare`/`SharedHealth`-style C# anywhere in `src/RimUtinni` or `src/RimMandrake` |
| Pale tree / anima reskin, Light-side psycast | BUILT (art + def), restricted-power audit explicitly DECLINED | `RUT_PaleTree.xml` full field-for-field build; its own XML comment records the psycast-whitelist audit as declined-not-owed ("needs C#, not built") — not a drift, a ruled-out non-goal |
| Milk ponds as terrain | **ABSENT — CONFIRMED, biggest terrain gap.** No `RUT_MilkPond`-style TerrainDef anywhere; named in the card (§1, §3, §7), the mushroom-bridge flora comments ("built OVER the milk ponds"), and two closed design items (`WATER_KINDS_TAXONOMY_1`, `FISH_BY_BIOME_1`) that classify it only in prose |
| Wildsteam sacred-grove wiring into `FACTION_SPEC.md` | ABSENT | zero mentions of the Rot/pale tree/sacred grove in `FACTION_SPEC.md` (611 lines) |

## 4. Terrain / weather

- **Terrain: `AB_MycoticGrass`/`AB_MycoticSoilRich` only** (donor's own two fertility-banded
  terrains) — matches the card's ground description loosely but the card's one explicitly
  *named* terrain, the milk ponds, has no def at all (see §3 above). No other named terrain
  in the card (no second terrain type called out by name) is missing beyond that.
- **Weather: IN SYNC.** `RUT_SheenFall`/`RUT_SheenStorm`/`RUT_SheenMist` replace the donor's
  water-rain weathers in `<baseWeatherCommonalities>`, closing hard ban 3 ("no water rain,
  ever / R-H1"). `Clear` and `DryThunderstorm` are the only non-Sheen entries — no vanilla
  rain weather present. CONFIRMED compliant.
- **Spore events** (card §4b, "the biggest fungi vent suffocation clouds"): present as a
  *per-plant* mechanic (AgariluxPrime's `CompProperties_GasProducer`, Skulltop's gas
  producer, the Guardian Groves gas emitter) rather than a standalone weather/game-condition
  event. Reads as satisfied in spirit, not as a literal second WeatherDef/GameConditionDef.

## Verdict

**Partially in sync — flora, names, and most named mechanics/weather match; fauna roster and
milk-pond terrain are the two real gaps.** The card and its supporting ruled documents
(`rosters/the_rot.json`, `rot_flora_fauna_names.md`) agree with each other; the drift is
between those ruled documents and what actually got wired into the live `BiomeDef`/patches.

## DRIFT rows (worst first)

1. **Roster (fauna)** — card/roster JSON name 28 admitted species ("keep the strange": glow
   bats, cave spider, bovine beetle, chem snail, pillbug, giant slugs/snails, plus 10 more
   from a later "round2 move mapping" pass) — ships with only 10 in `<wildAnimals>` — the
   roster JSON is right, the live def is 18 species short. CONFIRMED.
2. **Terrain** — card names milk ponds as the biome's only surface water, referenced in 4+
   places including built mushroom-bridge flora — no `RUT_MilkPond`-style TerrainDef exists
   anywhere — the card is right, nothing built it. CONFIRMED (inherited + re-verified).
3. **Mechanics (guardian repertoire)** — inherited audit called this UNFILED/UNCERTAIN — a
   direct read of `RUT_RotSporeKit_GuardianGroves.xml` shows 4 tea species already defended
   with distinct mechanisms — the audit undercounted; the build is right, the audit's UNFILED
   call was wrong. CONFIRMED (correction).
4. **Mechanics (health-sharing)** — card describes two variants (true wound-split, tend-aura)
   as "always true" biology — zero C# implementation found anywhere. The card is right that
   this is core biology; nothing built it. CONFIRMED.
5. **Mechanics (rot-rate map condition)** — card's "instant composting as a service" reads
   as ambient/map-wide; only a per-item/corpse rot multiplier exists (`RM_AcceleratedRotExtension`),
   no GameConditionDef. Partial credit — the item decay clock is real, the ambient framing
   isn't. CONFIRMED.
6. **Names** — today's two roster additions (`AA_AngelMoth`, `Snoruuk`) ship unrenamed,
   unlike every other resident species. Minor, likely just sequencing (added same day as this
   audit), not a real disagreement. CONFIRMED.
7. **Roster (inkcap)** — card names "inkcap"; resolved in design docs as `RUT_MoonlessStripesPlant`
   but that def isn't actually in the biome's wildPlants table either. Minor. CONFIRMED.
8. **Wildsteam/faction wiring** — card names the sacred-grove relationship as owed into
   `FACTION_SPEC.md`; confirmed absent, matches the card's own "Owed" line (not a
   disagreement — the card already says this is owed). Listed for completeness, not drift.

## Card lines stale because the work is DONE (inherited from the ground-truth audit, re-confirmed)

- Owed bullet 1 (heat-generating gene) — done, `ROT_WARM_MAT_1` closed.
- Owed bullet on live-item viability clock — done, `ROT_LIVE_PREPARATIONS_1` closed.
- Owed bullet on heat-pushing produce comp — done, same item.
- Owed bullet on Sheen weather + compatibility hediff — done, `RUT_RotSporeKit_SheenWeathers.xml`/`SheenHediffs.xml` shipped and wired live.
- Owed bullet on guardian repertoire per tea species — **now also correctable**: 4 of the
  named tea species have a built, distinct defense mechanism (`ROT_GUARDIAN_GROVES_1`); only
  the wider menu (hybrid defenders summoned network-wide, mat itself grasping) beyond those
  four remains open.

## UNKNOWN

- Whether the 3 ratified symbiont-parasite pairs (accelerated healing/metabolism,
  sleep-abolished/psychotic, Sheen-immunity/sun-intolerance) are individually hediff-complete
  — substantial hediff files exist but were not line-checked against the card's exact pairs.
- Whether the "round2 move mapping" fauna additions in `rosters/the_rot.json` (ShiroTrap,
  PustuleHornet family, AnimaColossus, SmogMoth, Thrumbungus, Yooka, Sporemole) are a fresh,
  still-in-flight ruling versus an older one that was deliberately not wired — no item name
  or date beyond "owner review 2026-09" was found to disambiguate.
- Whether the gourmet line / local genepacks / grown-heaters "uniquely available" bullets
  (§7) have any dedicated implementation beyond the generic mechanics already covered above —
  out of the four bounded axes, not chased further.
