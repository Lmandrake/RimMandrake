# DROID_FACTION_LOADOUTS_1 — droids in every faction's hands

Packet **C1** of `design/Jawa/droids/DROID_UNIFIED_FRAMEWORK_DESIGN.md` (§5).
Governed by owner **ruling 2**, 2026-09-06 (§0 of that doc, verbatim) and by
§3.2's "who fields droids" table. Critical path: C4, C5, C6, C7 and D2-D4 all
name this packet as their predecessor.

## spec

Droids appear in the loadouts of factions that already exist. **No droid
FactionDef is created, anywhere** — that is ruling 2's first clause ("NO rogue
droid faction, ever") and it is this packet's hardest constraint.

## Built

### The six rows of §3.2 that are mine

| row | file | what landed |
|---|---|---|
| Galactic Empire (`Empire`) | `src/RimUtinni/UtinniPatches/Patches/GalacticEmpire.xml` | attack droids added to all three group `options` this file already replaces — common raid (commonality 100), rare raid (commonality 10) and Settlement. `Jawa_Empire_*` untouched, same three defNames at the same three weights. |
| Homestead Defense League (`OutlanderCivil`) | `src/RimUtinni/UtinniPatches/Patches/HomesteadDefenseLeague.xml` | four low-power Labour/Astromech kinds into the Combat, Peaceful and Settlement groups this file already hangs off `OutlanderFactionBase`; a protocol droid into its Trader `guards`. |
| Hutt Cartel | `src/RimUtinni/UtinniPatches/Defs/FactionDefs/JawaHuttCartel.xml` | two Heavy-family Colonist-tier kinds into Combat and Settlement; a protocol droid into Trader `guards`. |
| the Junkers | `src/RimUtinni/UtinniPatches/Defs/FactionDefs/JawaJunkers.xml` | `RSW_DW_Primitive_Junker` into Combat (weight 3) and Settlement (weight 2). |
| every trader kind | `JawaHuttCartel.xml`, `JawaTribes.xml`, `HomesteadDefenseLeague.xml`, `JawaDeepwaterCompact.xml`, `JawaWildsteamClan.xml`, `JawaAscendantHelix.xml` | a Protocol-family droid in each faction's Trader-group `guards`. **Presence only.** |
| Jawa Trade Moot (`Jawa_IndigenousTribes`) | `src/RimUtinni/UtinniPatches/Defs/TraderKindDefs/RUT_TradeMootDroids.xml` (new) + `JawaTribes.xml` | three TraderKindDefs appended to `caravanTraderKinds`/`baseTraderKinds`; droids in the Combat, Peaceful and Trader groups. |

Plus one line outside RimUtinni:
`src/RimStarWars/Droidworks/Defs/Races_Primitive.xml` — the Junker race's
`CompProperties_DroidDetonation` now carries `<damageDef>Flame</damageDef>`.
See "the Junker's fire" below.

### The numbers, and how they were chosen

Ruling 2 asks for a **minority** droid element everywhere except literally-droid
factions. `pawnGroupMaker` `options` weights are SELECTION weights, so a share of
*points* is `Σ(weight × combatPower)` per side, not a share of entries. Every
combatPower below was read off the live 600-mod def dump
(`captures/2026-09-08T19-25-50Z`, mod set byte-identical to `ModsConfig.xml`),
never off a doc — the Empire Grunt is **101**, not the 87 `GalacticEmpire.xml`'s
own header still records from 2026-08-21.

| faction | droid share of weighted points | ruled target |
|---|---|---|
| Empire, common raid | 405 / 1346.5 = **30.1 %** | 20-40 % |
| Empire, rare raid | ≤ 447.5 / 1389 = **≤ 32 %** (lower once the three Outer Rim specialists are counted) | 20-40 % |
| Empire, settlement | **30.1 %**, identical to the common raid | mirrors B40's own reason |
| Homestead | 290 / 2234 = **13 %** of points, but **30 % of picks** | "utility droids fighting badly" — seen, and useless |
| Hutt | 155 / 2154 = **7 %**; 2.5 of 19.5 weight ⇒ 0-2 per group | "0-2 Heavy kinds" |
| Junkers | 60 / 1293 = **4.6 %**; 3 of 20 weight ⇒ 1-2 per band of ten | "one or two" |
| Trade Moot | 190 / 1281 = **15 %** | "loves droids of all kinds" |

## Decisions recorded

**1 · The Junker's suicide mechanic: REUSED, not rebuilt.** §3.2 asks for a
"`MentalState` charge-and-detonate". `CompDroidDetonation` already fires on death
for any race with `energyDensity > 0` and stored charge, scaling with both, and
`RSW_DW_Race_Primitive_Junker` already carries `energyDensity 3` +
`deliberateDenyModule true` from B9. Ruling 2's actual words are *"able to blow
themselves up against the enemy or their structures"*, and in a raid the thing
that kills a Junker droid **is** the colony — so the death path delivers the
ruling. A proactive walk-up-and-self-destruct behaviour is a genuinely different
mechanism (new `MentalStateDef` + `JobGiver` + a self-kill route) and is **NOT
built and NOT claimed here**; it is filed as `DROID_SUICIDE_CHARGE_STATE_1`.

**2 · The Junker's fire: the explosion, not a weapon.** No flamethrower is
equippable. The only droid flamethrower in the live 600-mod set is
`guy762_DroidWeapon_flamethrower` — which is **Apparel** (`thingClass
RimWorld.Apparel`), belongs to `guy762.mm.kotorcore` (a mod §2's R4 retires), and
was already excluded from the B2 module absorption for requiring MVCF, a
framework Droidworks does not ship
(`Absorbed_KotorDroidModules_EXCLUDED_manifest.txt:24`). Nothing else in 600 mods
fits. Rather than invent a defName or wire a doomed donor dependency, the
detonation's `damageDef` was set to vanilla `Flame` — the same DamageDef vanilla's
own molotov explosion uses — on that one race and nowhere else. The droid now
spews fire when it goes, which is the visible half of the ruling.

**3 · Trade Moot stock: a stock generator of our own, after the first attempt
failed live.** §3.2 names `StockGenerator_Colonists`; that is an example, and
every off-the-shelf route measured against the live 600-mod set fails:

- `StockGenerator_Colonists` — 17 uses, **all** `guy762.mm.kotorcore` (R4 retires
  it). There is no vanilla class of this name.
- `StockGenerator_Automatons` — 9 uses. Its real name is
  **`Asimov.StockGenerator_Automatons`** and the donor's own
  `TraderKinds_Base.xml:83` gates it on `Neronix17.OuterRim.DroidDepot`, **not**
  on Outer Rim Core — so §2's **R3 kills it**, before D4 has even run.
- vanilla `StockGenerator_Slaves` — unusable and **silently** so:
  `StockGenerator_Slaves.cs` lines 20-35 yield nothing unless every ideo of the
  trading faction returns `IdeoApprovesOfSlavery()`, and the Moot's fixed ideo is
  The Salvation.

🔴 **The first build of this packet shipped `Class="StockGenerator_Automatons"`
without the `Asimov.` namespace, and the 20:26 full-list load caught it**: two
`Could not find type named StockGenerator_Automatons`, both TraderKindDefs
discarded, and then two dangling `caravanTraderKinds`/`baseTraderKinds`
cross-references — because a faction's `<li>` survives a def that does not. The
short `$type` in a def *dump* is not the `Class=` string a loader wants. That is
the whole reason this packet took a second load.

⇒ **`RimMandrake.StarWars.Droidworks.StockGenerator_DWDroids`**, new, ~40 lines
(`src/RimStarWars/Droidworks/Source/Droidworks/StockGenerator_DWDroids.cs`). It
outlives R1-R4, has no slavery gate (a droid is property, not a person), and its
`HandlesThingDef` keys on `RSW_DW_FleshType_Droid` — so the Moot **buys any
Droidworks droid the player brings**, not only the models it is selling today.
That is ruling 2's "buys" half, and with a third-party class it was unprovable.

🔴 **The DLL and `RUT_TradeMootDroids.xml` ship together or not at all.** An
assembly can only be replaced while the game is CLOSED; deploying the XML against
an older DLL reproduces the discard exactly.

**4 · Protocol droids are presence, not price.** The mechanical trade advantage
is C4 (`DROID_PROTOCOL_TRADE_ADVANTAGE_1`) and is not touched. `guards` is the
only node `PawnGroupKindWorker_Trader` reads a companion out of (it fills a Trader
group from `traders`, `carriers` and `guards`, and never reads `options`), so the
droid is listed as a guard whether or not it can fight. Presence is **by weight,
therefore probabilistic** — which is the ruled behaviour, not a shortfall: ruling
2 also says it is *"dangerous not to"* have one, and that requires that some
parties arrive without. C4 owns the absent case as its penalty branch.

**5 · Bought droids arrive UNBOLTED.** `RSW_DW_RestrainingBolt` on its own is
half a mechanism: `RSW_DW_BoltResentment` is seeded by the two *application*
routes (`Recipe_InstallRestrainingBolt.ApplyOnPawn` / `JobDriver_DWClampBolt`),
never by a hediff merely appearing on a pawn. A droid bolted by a stock generator
would carry a bolt that never earns resentment and never rebels when freed —
half a mechanism wearing the whole one's face. Selling bolted droids is a good
idea and belongs with B5's payoff, seeded properly.

**6 · Droid entries use the Colonist/Good builds, never the "Bad" ones**, on the
markets and on the low-threat factions. Droidworks ships a raider-grade `*Bad_*`
variant of the same chassis at 125-500 combatPower; those are the Empire's, and
putting one on a Moot counter would hand the player an HK-50 for silver.

## Explicitly NOT built — other items own these

| §3.2 row | owner |
|---|---|
| protocol-droid **price mechanic** | C4 `DROID_PROTOCOL_TRADE_ADVANTAGE_1` |
| Free Droid Enclaves (membership, territory-only hostility) | C2 (closed) + C3 `DROID_FDE_GOODWILL_CAP_1`. **`JawaFreeDroidEnclaves.xml` was not touched at all.** |
| wild droids (crashed, gone crazy) | E4 `DROIDWORKS_WILD_DROIDS_1` |
| Hutt captives in the torture chambers | C6 `DROID_HUTT_CAPTIVES_1` |
| the Junker's proactive charge-and-detonate | new: `DROID_SUICIDE_CHARGE_STATE_1` |

Two more, decided rather than overlooked:

- **The Empire's Trader group is untouched**, as `GalacticEmpire.xml` has ruled
  since 2026-08-14. The Empire is a permanent enemy and never trades with the
  player, so a protocol droid there would be scenery nobody sees.
- **The Deep Desert Tribes (`TribeCivil`) get no protocol droid.** They are a
  neolithic tribal reskin; ruling 2's "many traders" does not read as "all
  traders", and a protocol droid on a stone-age caravan is a lore break, not a
  gap. Recorded so nobody files it as an omission.
- **"Occasional Sith" is not built.** It is in §3.2's Empire *description* cell,
  not its mechanism cell, and no Sith PawnKindDef was verified to exist in the
  live set. Out of scope for a droid packet; not claimed.

## verify

**Offline — clean.**

- `xml.etree` parses all 10 touched/created files.
- `validate_patch.py` against the live 600-mod set + `--defnames` from the
  2026-09-08T19:25:50Z capture: **0 errors, 0 warnings** on both PatchOperation
  files (`GalacticEmpire.xml`, `HomesteadDefenseLeague.xml`).
- Every defName referenced by this packet checked against the same capture:
  **32 of 33 MEASURED present**. The one absent is `RSW_DW_Primitive_Junker` —
  built by B9 and deployed to the game folder at 12:37 local, seven minutes
  *after* that 19:25:50Z capture, so it is absent from the capture and present on
  disk. Not a typo; a timestamp.
- **No FactionDef was created.** The only new def file in this packet is
  `RUT_TradeMootDroids.xml`, which contains three `TraderKindDef`s and nothing
  else. `grep -c "<FactionDef" src/RimUtinni/UtinniPatches/Defs/TraderKindDefs/`
  is 0, and the eight campaign FactionDefs are the same eight as before.

**Live — MEASURED on a full 600-mod cold load, 2026-09-08 21:31.**

Two loads were spent, because the first one caught a real defect (see decision 3).

| claim | how it was measured | result |
|---|---|---|
| nothing my XML added breaks the load | `harvest_log.py` on the second run's Player.log | DEFS DISCARDED **0** = baseline · cross-reference (def loader) **0** = baseline · dead mods 0 · Harmony failures 1 = baseline · patch ops failed 5 = baseline |
| no NEW ConfigError is mine | `--show configerror`, grepped for every name this packet creates | **0 hits.** The 25-vs-17 RED is unchanged between run 1 and run 2 and is `RSW_FE_*` (fire ecology), `RSW_DW_Module_DroidArmor*` (B2), `RUT_ComplexStructures` and five others. None of it is C1's. |
| the droids are in the resolved rosters | `jawa/get_defs` on the live game, `pawnGroupMakers` with `deep:true` | `Empire` **6** droid kinds · `OutlanderCivil` **5** · `Jawa_HuttCartel` **3** · `Jawa_Junkers` **1** (`RSW_DW_Primitive_Junker`, which also proves B9's kind is live and the entry is not dangling) · `Jawa_IndigenousTribes` **4** |
| the Trade Moot's markets exist and hold droids | `jawa/get_defs` on all three TraderKindDefs | **4 of 4 resolved**, `notFound: []`. `RUT_Caravan_TradeMoot_Droids` carries two instantiated `StockGenerator_DWDroids` with their `pawnKinds` (9 and 2) and countRanges (2~5, 0~1) intact — which is also the proof the new DLL loaded and the type resolved. `Jawa_IndigenousTribes` lists all three in its trader-kind lists. |
| the Junker spews fire | `jawa/get_def RSW_DW_Race_Primitive_Junker` | `CompProperties_DroidDetonation` present with `damageDef: 'Flame'`, `baseRadius: 3.9` |
| **no droid FactionDef exists anywhere** | `measure count FactionDef` + a `FactionDef` census by packageId, on the fresh 600-mod capture `2026-09-08T20-26-42Z` | **85 FactionDefs**, identical to the pre-change 19:25:50Z capture. Ours are the same **8** `Jawa_*` as before. **Droidworks ships zero FactionDefs.** |

🔴 **NOT proven, and not claimed: a raid actually rolling a droid at runtime.**
The packet's verify line says "each faction raid/caravan on quicktest shows the
droids", and the quicktest could not be reached: `rimworld/start_debug_game_ready`
**crashed RimWorld outright** on the 600-mod list — the third reproduction of
`NINEFOLD_DEBUG_GAME_READY_CRASH_1`, and this run's tail names a culprit that item
did not have. The stack is
`Caveworld_Flora_Unleashed.MapComponent_CaveFungus.MapGenerated →
TrySpawnNewMyceliumAtRandomPosition → Mycelium.SpawnNewMyceliumAt →
Verse.GenSpawn.Spawn`, dying inside `GenSpawn.Spawn` under six third-party
patches. Nothing to do with this packet; noted on that item with the log.

What that leaves unobserved is one step: whether a weighted `options` dictionary
picks an entry at real point budgets. That is stock engine behaviour on
non-trivial weights (the smallest share here is 3 of 20), and every input to it is
measured above — but it is an inference, not an observation, and the next session
that has a live map should fire one raid per faction and look. Logs kept:
`Transient/Player_log_C1_run1_automatons_discarded_2026-09-08.log` (the defect) and
`Transient/Player_log_C1_run2_clean_then_quicktest_crash_2026-09-08.log` (the fix).

## Assumptions

1. Every def this packet references carries `MayRequire="mandrake.rsw.droidworks"`
   — on `<li>` entries inside `options`/`guards` (this codebase's own precedent:
   `GalacticEmpire.xml`'s `OuterRim_ImpRangeTrooper`), and on the **root element**
   of each new `TraderKindDef` with the identical string on the faction's own
   `<li>`. Root-element `MayRequire` and comma-separated `MayRequire` were both
   read out of engine source (`LoadedModManager.ParseAndProcessXML` lines 393-402,
   `ModsConfig.AreAllActive`), not assumed. The single comma-separated gate that
   was in the first build is gone with the third-party class it protected.
2. `StockGenerator_DWDroids.GenerateThings` generates stock with `faction: null`
   — stock is nobody's until it is bought, and `TradeUtility` hands the bought
   pawn to the player either way. The alternative (the trader's own faction) would
   make every unsold droid a member of a faction the player may be at war with.
3. The Homestead droids hang off the **abstract** `OutlanderFactionBase` along
   with their four host commonality-5 group makers, so they reach every Outlander
   descendant that rolls one of those groups, not `OutlanderCivil` alone. That is
   the same accepted blast radius `OUTLANDER_GROUPMAKER_PATCH_1` already carries.
4. Droidworks-generated kinds ship with no `weaponTags`/`weaponMoney` by that
   generator's own convention, so every droid here arrives bare-handed. For the
   Homestead that IS the design ("fighting badly"); elsewhere it is the platform's
   standing shape, not a defect of this packet. §3.2's "Primitive-tier weapons"
   cell could not be honoured — the Primitive tier fabricates frames, parts and
   modules, not weapons.
