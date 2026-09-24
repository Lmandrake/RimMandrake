# SHOKKWEAVE_SOLE_SOURCE_1 — Shokkweave economy (rename, trader strip, harvest routes)

## 2026-09-24 (FOUNDRY, sixth pass) — wake-up fix RE-PARSE confirmed live; full behavioral proof deferred, canonical map is mid-encounter

**Gap closed**: the 5th pass's open question — "does the running process have
the `wakeUpIfAnyTargetClose` fix, or does it still need a restart to re-parse
defs" — is answered **yes, restart happened, fix is live**. `jawa/get_defs`
with `deep: true` on `ThingDef/RUT_Webwork_Nest` (game UP, tile 17007,
`mandrake.rut.shokkweaveeconomy` loaded) reads the `CompProperties_WakeUpDormant`
block back with `wakeUpIfAnyTargetClose: true` and `wakeUpOnDamage: true` — the
2026-09-12 fix is genuinely parsed into the running process, not just sitting on
disk. This is a static def read, not a behavioral test, but it retires the
"needs a fresh restart" line from every prior pass.

**Full behavioral proof (wake-on-approach, no damage needed; butchery live
test) NOT attempted this pass, and the reason is new**: the currently-loaded
map is not a spare quicktest map, it is the **canonical Ash'karr campaign
save** (`jawa/map_info`: `mapParent` "Zeddo's Salvage Yard", tile 17007 — the
CANONICAL_ASHKARR_START colony). `jawa/list_pawns` shows 6 drafted colonists
(`job: Wait_Combat`) plus 3 live Mechanoids and 7 `RUT_Jawa_HuttCartel`
pawns on the same map — an encounter in progress, not an idle colony.
`step_game_ticks` advances simulation regardless of pause state (per this
skill's own §4b), so stepping the ~300+ ticks this test needs risks resolving
real combat on the one save this campaign cannot lose. Read-only calls only
were made; nothing was spawned, damaged, or advanced. The 2026-09-12 pass
solved this exact problem by repainting a *quicktest* map's tile to
`RUT_Webwork` — that route is unavailable here because this session is
connected to the canonical save, not a quicktest session; a dedicated
throwaway quicktest session is needed to finish this test (rimworld-debug-testing
skill), which is its own bridge cycle, not attempted this pass.

**Status unchanged**: `doing`, `needs owner` on the two build decisions (trader-
stock companion tool vs. accepting source proof; new colonist harvest-job for
the emergent-Shokk spawn half) — this pass only retired the restart question.
Bridge taken and released clean; no game state touched.

## 2026-09-18 (FOUNDRY, belt mode, subagent, fifth pass) — trader-stock proof completed by source (all 11 kinds), one gap reassessed as stale-blocker/still-open, half of the other gap found uncommitted and shipped

**Bridge check**: `rimflow bridge who` → held by BENCH (`rot wave: deploy +
restart cycle + live quicktest battery`, idle ~2 min at check time — genuinely
live, not stale). Did not take it. The prior pass's `wakeUpIfAnyTargetClose`
fix therefore stays exactly as it was left: deployed, unverified live (needs a
fresh restart to re-parse defs). **Still owed, needs bridge.**

**Gap 1 (11-trader-kind zero-stock proof) — no bridge tool built (unchanged),
but now backed by a COMPLETE source-verified mechanism proof across all 11
named kinds, not just the 5 previously reasoned about.** Pulled the freshest
live def dump (`captures/2026-09-18T05-05-13Z`, fingerprint-matched
packageId-for-packageId against the currently-loaded `ModsConfig.xml` at the
time BENCH's rot wave started — 634/634 match) and grepped
`defs/TraderKindDef.json` for `Hyperweave`: exactly **11** trader kinds hit,
confirming the item's own long-standing "11" figure directly for the first
time (previously only asserted, never re-derived from data this pass cycle).

- **5 `StockGenerator_SingleDef`** (`AM_AncientLogisticsSystem`,
  `guy762_BaseTraderKind_Czerka`, `guy762_TraderKind_Czerka`,
  `guy762_BaseTraderKind_HuttGalleon`, `guy762_TraderKind_HuttGalleon`).
  RimSage-read `StockGeneratorUtility.TryMakeForStockSingle` and
  `TradeabilityUtility.TraderCanSell()`: `TraderCanSell()` returns
  `tradeability == Tradeability.Buyable` (or `All`) — `Sellable` (Hyperweave's
  current value, live-confirmed) returns **false**. `TryMakeForStockSingle`
  hard-gates on this and returns `null` before ever making a Thing — so these
  5 kinds mechanically CANNOT ever add Shokkweave to stock, confirming the
  2026-09-11 pass's conclusion by source, not just by the expected config
  errors. **New finding, not previously documented**: that same gated branch
  also calls `Log.Error("Tried to make non-trader-sellable thing for trader
  stock: Hyperweave")` — not just the known one-time load `ConfigErrors()`
  line, but a **runtime** error logged every single time one of these 5
  traders regenerates stock (every visit/restock, not just once at load).
  Zero gameplay effect (stock is correctly always zero either way) but real,
  ongoing log spam. **Flagged, not fixed this pass**: a clean fix means
  removing the dead `<li>` outright via `PatchOperationRemove`, but the
  Czerka/HuttGalleon pairs' identical values across Base/non-Base defnames
  mean the `<li>` almost certainly lives on the *Base* def and is inherited
  (this item's own codebase has a standing lesson that `Remove` on an
  inheriting def's own XML matches nothing) — targeting it correctly needs
  reading the donor mod's actual XML to find which def truly owns it, not
  guessed from the post-merge JSON dump alone. Out of scope this pass.
- **6 `StockGenerator_Tag`** (`Base_Empire_Standard`, `Base_Outlander_Standard`,
  `Caravan_Outlander_Exotic`, `Orbital_Exotic` — all "Better Traders"; plus
  `DV_Base_Keshig_Standard`, `DV_Caravan_Keshig_Exotic` — "Det's Xenotypes -
  Keshig"). These were NEVER discussed in any prior pass — a genuinely new
  check. RimSage-read `StockGenerator_Tag.HandlesThingDef`:
  `return thingDef.tradeTags.Contains(tradeTag)` — Hyperweave's `tradeTags`
  is live-confirmed `[]` (empty, from the 2026-09-11 rename patch), so this
  returns **false** unconditionally, and `GenerateThings`' selection
  `.Where(HandlesThingDef(d) && ...)` never reaches these defs at all. Each
  of these 6 kinds also carries a `customCountRanges` override entry naming
  Hyperweave (200-400 / 100-400 / 80-240 / 100-400 / 50-200 / 40-120) — these
  are confirmed **dead configuration**: `RandomCountOf`'s count-range lookup
  is only ever consulted for a def that already survived the `Where` filter,
  which Hyperweave never does. No log spam on this branch (clean silent
  exclusion, unlike the 5 above).
- The 2 HuttGalleon kinds also carry a `StockGenerator_Category` (Textiles)
  that independently lists Hyperweave in its own `excludedThingDefs` — a
  donor-mod precaution, unrelated to and unaffected by our rename.

**Net**: all 11 named trader kinds are now proven, by direct RimSage source
read (never guessed) against the actual live-loaded stockGenerator
configuration of each, to be structurally incapable of ever stocking
Shokkweave. This is the strongest evidence gathered on this sub-item to
date — but it is still not the spec's own originally-envisioned empirical
N≥20-roll bridge test, because no bridge tool to force a specific
`TraderKindDef`'s stock generation exists yet (unchanged from every prior
pass). `needs owner`: whether this source-level proof is accepted as
sufficient, or the `rimbridge-companion` tool-build is still wanted.

**Gap 2 (border creep-web route) — its stated BLOCKER is stale; the real
remaining gap is different from how the last pass described it, and half of
it was already sitting unbuilt+uncommitted in this shared tree.**
`WEBWORK_KIT_BUILD_1` and `SHOKK_RSW_MOD_1` (the two items the 4th pass
named as this gap's blockers) are **both closed** (`rimflow show` — closed at
`421ee05d…` and `19fbedbfb` respectively) — so "blocks on FrontCreep needing
wiring which in turn needs SHOKK_RSW_MOD_1" is stale as a blocking reason;
both prerequisites now exist.

Found `src/RimUtinni/ShokkweaveEconomy/Patches/ShokkweaveCreepWebYield.xml`
sitting **untracked** in this shared worktree (`git status`: `??`), with a
matching uncommitted edit to `About/About.xml` — unclaimed by any pass note
in this file, evidently work from an earlier or concurrent session that
never got committed. Read it in full, independently re-derived its reasoning
from source before trusting it (per this campaign's own "read the mechanism,
don't trust the comment" doctrine), and it holds up:

- **The "yields Shokkweave" half is genuinely done and correct.** RimSage-read
  `GenLeaving.DoLeavingsFor`: `killedLeavings` returns immediately and does
  nothing under `DestroyMode.Vanish`/`QuestLogic` — it only ever fires under
  `KillFinalize` (and a few resource-refund modes). Combat-destroying
  `RUT_Webwork_Anchor`/`_Web`/`_Gutter` (their only destroy route today; no
  harvest job exists) uses `KillFinalize`, exactly matching the
  already-live-verified `RUT_Webwork_Nest`/`_SilkKnot` pattern. The patch
  adds `killedLeavings` (Anchor 3 / Web 2 / Gutter 5 Shokkweave, ❓INVENTED,
  matching the spec's "~2-5 per line-segment" range) to all three. Ran
  `validate_patch.py` against the fresh live dump + the actual `--defs`
  install roots: **0 errors**, all 3 xpaths match exactly 1 target each in
  `RUT_WebworkStructures.xml`.
- **The "spawns an emergent Shokk" half is genuinely NOT satisfiable by a
  patch, confirmed independently via source (not just trusting the file's
  own comment)**: `RSW_CompEmergentSpawnOnDestroy.PostDestroy`
  (`src/RimStarWars/Shokk/Source/RSW_CompEmergentSpawnOnDestroy.cs`) requires
  `mode == DestroyMode.Vanish` and explicitly returns on anything else —
  attaching that comp to these three Things (whose only destroy route is
  combat `KillFinalize`) would ship a comp that can structurally never fire.
  A genuine dedicated colonist harvest job (a `WorkGiver`/`JobDriver`/
  `DesignationDef` trio that walks a colonist to the structure, manually
  spawns the yield, and calls `Destroy(DestroyMode.Vanish)` instead of
  relying on `killedLeavings`) is required for the spawn-chance half, and
  does not exist anywhere in this codebase. **Correcting the record**:
  `WEBWORK_KIT_BUILD_1`'s closing note called this "this item's own patch to
  attach" — that undersold it; the yield half is a patch, the spawn half is
  new C# (a new colonist work type), not a patch. Not attempted this pass:
  it is a genuinely new gameplay mechanism with no live way to verify it this
  pass (bridge held by BENCH), and this campaign's own doctrine is explicit
  about silent ThinkTree/WorkGiver wiring failures — shipping one unverified
  is a landmine, not progress.

**Committed this pass**: the pre-existing `ShokkweaveCreepWebYield.xml` +
`About.xml` edit (re-verified, not blindly trusted), plus this note.
`needs owner`: whether the new colonist harvest-job build (spawn mechanism
half) is wanted now that nothing external blocks it, or waits.

**Butchery route: still never live-exercised, re-confirmed correct by
source a second time.** RimSage-read `Pawn.ButcherProducts` →
`Thing.ButcherProducts`: reads `def.butcherProducts` directly, vanilla-
standard, no trap (unlike the tradeability field this item already caught
once). `ShokkweaveButcherYield.xml` re-validated against the fresh live dump:
0 errors, its `PatchOperationFindMod`-gated xpath resolves correctly against
the current (minimal, 30-mod) load set exactly as expected. Never actually
butchered a Wyyyschokk corpse and read the output — lower risk than the
wake-up bug (plain vanilla field, not custom comp logic) but still open
under this item's own live-proof standard. Not attempted this pass (bridge
unavailable).

**Status**: leaving `doing`, `needs owner` — real gaps remain (bridge
reconfirmation of the wake-up fix; the trader-stock companion-tool decision;
the emergent-Shokk harvest-job build decision; butchery live proof), none of
them closeable offline this pass.

## 2026-09-12 (FOUNDRY, fourth pass) — web-cutting + nest raid LIVE-VERIFIED; one real bug found and fixed; item stays OPEN on two unrelated pre-existing gaps

`QUICKTEST_POSTSETUP_CRASH_1`'s fix made the whole session's map-crash problem
moot. Rather than fight `start_debug_game_ready` for a `RUT_Webwork` tile,
repainted the already-loaded quicktest map's own tile to `RUT_Webwork` (same
technique as `SHRINE_GUARDIAN_BIOME_GATE_1`) and regenerated it in place.
`jawa/map_info` confirmed `mapBiome: "RUT_Webwork"`.

**Web-cutting — FULLY LIVE-VERIFIED.** `jawa/list_things` found 21
`RUT_Webwork_SilkKnot` scattered on the fresh map. Destroyed one with
`jawa/damage` (Bomb, to 0 HP): the cell now holds `Hyperweave` (label
"Shokkweave", the rename confirmed live, not just on disk) at the exact
knot's position. Matches `Mineable.TrySpawnYield` firing on
`DestroyMode.KillFinalize`, per this item's own build note.

**Nest raid — scatter genstep confirmed structurally sound, comp chain
LIVE-VERIFIED via manual spawn, one real bug found and fixed.**
`RUT_WebworkNestScatter` (`jawa/get_defs`) loaded correctly (the
`MayRequire="mlie.starwarsanimalcollection"` gate passed — that donor mod is
active). It did not happen to scatter on this one map (density is
deliberately near-zero per this item's own build note: `coveredCellsPer10Cells
0~0.002` on a 62,500-cell map — expected ~0-12 covered cells, genuinely a
coin flip), which is not evidence against it: it shares the exact same
`GenStep_ScatterWebworkSilk` class that DID scatter 21 SilkKnots above.

So the comp chain was proven directly instead (rimbridge skill's own
"prefer testing the mechanism synthetically" guidance): spawned a
`RUT_Webwork_Nest` via `rimworld/spawn_thing`, spawned a colonist 2 cells
away, and stepped **2,640+ ticks** (10+ of the comp's own 250-tick check
intervals) — **no Wyyyschokk spawned.** Read
`RimWorld/CompProperties_WakeUpDormant.cs`: `wakeUpIfAnyTargetClose` defaults
**false**, and this def deliberately uses plain `thingClass=Building` (not
`Hive`'s own class, which is where vanilla's actual "wakes when unfogged/
approached" behavior lives) — so with the field unset, `TickRareWorker`'s
whole proximity-check branch was dead code. **This is why "wakes ... on
approach" (this item's own verify text) could never have fired.**

Confirmed empirically both ends: (a) 2,640 ticks of a colonist standing
2 cells away, dormant, no guardian; (b) damaging the SAME nest instead
(`wakeUpOnDamage` defaults true) woke it within 300 ticks — a Wyyyschokk
guardian spawned (`LordJob_DefendAndExpandHive`, confirmed via
`jawa/list_pawns`). Then killed the nest outright: exactly **60 Shokkweave**
dropped (`killedLeavings`), matching the def precisely.

**Fixed**: added `<wakeUpIfAnyTargetClose>true</wakeUpIfAnyTargetClose>` to
`RUT_Webwork_Nest`'s `CompProperties_WakeUpDormant` block in
`src/RimUtinni/ShokkweaveEconomy/Defs/ThingDefs_Buildings/ShokkweaveHarvestNodes.xml`
(full reasoning + evidence recorded inline in that file's comment). Default
`wakeUpTargetingParams` (`TargetingParameters.ForColonist()`) is exactly "a
colonist approaches" — no further field needed. Deployed
(`deploy_custom_mods.py --mod ShokkweaveEconomy --apply`, verified in sync).
**This ONE fix is unverified live** — defs are parsed once at process
startup, so the already-running game still has the old (broken) value in
memory; re-confirming it needs the next full restart. Everything else about
the nest mechanism (dormancy, wake-on-damage, guardian spawn, kill yield) IS
live-confirmed on the CURRENT process, and that logic path is unchanged by
this fix.

**Item stays OPEN — two gaps are genuinely unrelated to tonight's crash fix
and unchanged from the 2026-09-11/12 notes below:**
1. The 11-trader-kind zero-hyperweave-stock proof: still no bridge tool
   forces a specific `TraderKindDef`'s stock generation. Confirmed again
   this pass this is still true — building one is its own
   `rimbridge-companion` cycle, not attempted tonight (out of scope: the
   coordinator's ask was the two harvest routes, conditional on "if bridge
   tools allow" for the trader proof — they don't).
2. Border creep-web (4th route, owner-ruled-in 2026-09-11): still blocks on
   `RM_MapComponent_FrontCreep` needing Webwork-specific yield/spawn wiring
   from this item's own patch, which in turn needs `SHOKK_RSW_MOD_1`'s
   emergent-Shokk spawn hook. `FrontCreep` itself IS now live-verified
   (see `WEBWORK_KIT_BUILD_1`'s note this pass) — only the yield/Shokk-spawn
   attachment is missing, unchanged from before.

`needs owner` (whether to prioritize the trader-stock companion tool build,
and whether border creep-web waits on `SHOKK_RSW_MOD_1`) rather than `bridge`
— the bridge itself is no longer what's blocking this item.

## 2026-09-12 (FOUNDRY, later same night) — deploy confirmed; live web-cutting/nest-raid verify blocked on QUICKTEST_POSTSETUP_CRASH_1

`deploy_custom_mods.py --mod ShokkweaveEconomy` reports "in sync" — the
2026-09-12 build note's `needs=deploy` is resolved (carried over from
tonight's restart). The two remaining live proofs this item owes
(web-cutting scatter + mining yield; nest raid scatter + wake + guardian +
drop) both need a `RUT_Webwork`-biome map, which the currently-loaded
canonical colony map is not, and `start_debug_game_ready` (the only route
to a fresh biome-of-choice map) crashes the process reliably after this
session fixed two OTHER load-blocking bugs first — see
`QUICKTEST_POSTSETUP_CRASH_1` and `SHRINE_GUARDIAN_BIOME_GATE_1`'s sibling
note for the full chase. Not substituting the loaded real map (as
`BUILDING_THEFT_HAULER_1` did) because these two routes are gated on the
map's OWN biome (`GenStep_ScatterWebworkSilk`'s `map.Biome.defName ==
"RUT_Webwork"` check), not just "any map with a building."

The 11-trader-kind zero-stock proof and the quest-reward roll pass remain
unattempted for the same reason noted in the 2026-09-11 update (no bridge
tool forces a specific `TraderKindDef`'s stock generation yet) — unchanged
tonight.

`needs=bridge` stays accurate; unblocks once `QUICKTEST_POSTSETUP_CRASH_1`
is fixed or a minimal+target mod list swap gets a `RUT_Webwork` quicktest
map without it.

Queue line: rename hyperweave game-wide, strip it from EVERY trader stock
table (prove against live trader generation), add the three Webwork harvest
routes (web-cutting, butchery, nest raid).

## Ruled input — 2026-09-11 card sitting (the boundary question)

**Border-map creep-web YIELDS, with teeth.** Owner-verbatim: "(2) but it has
a small chance of SPAWNING an emergent Shokk to get you." Cutting creep-web
on a border map is a real in-biome harvest route — supersedes the webwork
kit's no-yield-variant placeholder — and each cut carries a small chance of
spawning an emergent Shokk. The spawn hook lands with `SHOKK_RSW_MOD_1`
(the Shokk is its own RSW-tier mod, same sitting); this item wires the
yield side. Does NOT change the other three harvest routes or the trader
strip.

## spec
(unchanged from the queue line; see `webwork_kit_spec.md` "Owner rulings"
item 4 and the sole-source constraints block for the boundary contract)

## verify
Live trader generation shows zero hyperweave/Shokkweave stock; border-map
creep-web cut yields Shokkweave and can spawn the emergent Shokk.

## 2026-09-11 update — build-order step 1 shipped, live proof PARTIAL

**Built** (`src/RimUtinni/ShokkweaveEconomy/`, deployed, enabled in
`ModsConfig.xml`): rename, tradeability strip, quest-reward tag strip,
`ExoticMisc` tag strip, stuff-commonality 0.1→0.05, Wyyyschokk butcher yield
(15). Every xpath confirmed matching live via `validate_patch.py --live`
before shipping (caught the `tradeability` field-doesn't-exist-in-XML trap:
`PatchOperationAdd`, not `Replace`). All 4 files reviewed and marked CLEAN.

**Live-confirmed this session** (`jawa/get_def` on `Hyperweave`, full
591-mod list, game UP): `label: "shokkweave"`, new `description` text,
`tradeability: "Sellable"`, `tradeTags: []` — all four read back correctly
from the RUNNING game, not just the XML on disk. Five expected "Hyperweave
tradeability doesn't allow traders to sell this thing" config errors also
appeared for exactly the five SingleDef trader kinds the spec predicted
(`AM_AncientLogisticsSystem`, `guy762_BaseTraderKind_Czerka`,
`guy762_TraderKind_Czerka`, `guy762_BaseTraderKind_HuttGalleon`,
`guy762_TraderKind_HuttGalleon`) — this is the mechanism working as
documented, not a bug.

**NOT done this session** (honest gap, not swept under anything): the
spec's own proof standard — bridge/dev-mode generation of all 11 named
trader kinds, N≥20 rolls each, asserting zero stock — was not run. No
bridge tool exists to generate a specific `TraderKindDef`'s stock list
directly (checked `rimbridge/run_lua`'s capability surface; it only
composes existing `jawa/`/`rimworld/` tools, none of which do this), and
building one is its own `rimbridge-companion` cycle, out of scope for
tonight. Also not attempted: quest-reward roll pass, live butchery spawn
test (relying on the def-state read + `validate_patch.py --live` instead),
and steps 3/4 (web-cutting/nest-raid/border-creep-web yields — block on
unbuilt roster ThingDefs, unchanged from the offline build note).

**Criteria status**: the mechanism is verified correct by direct live def
read and by RimSage source analysis of `TradeabilityUtility`/
`StockGeneratorUtility` (done during the build, see the patch file's own
comments) — but the item's own stated verify line ("live trader generation
shows zero stock") is not yet independently exercised end-to-end. Leaving
`doing`, not closing, until either that tool gets built or someone accepts
the def-state + source-analysis proof as sufficient.

## 2026-09-12 update — web-cutting + nest raid BUILT and offline-validated; needs=deploy

**Reclaimed** (stale-queue audit, FOUNDRY): 3 of 4 Webwork harvest routes were
still unbuilt (butchery shipped 2026-09-11; web-cutting, nest raid, and the
ruled-in border creep-web route were not). This pass builds the two of those
three that do not depend on other unbuilt items.

**Built** (`src/RimUtinni/ShokkweaveEconomy/`, new files this pass):
- `Defs/ThingDefs_Buildings/ShokkweaveHarvestNodes.xml` —
  `RUT_Webwork_SilkKnot` (web-cutting: a mineable silk vein, `ParentName="RockBase"`
  same shape as `MineableSteel`, `mineableThing=Hyperweave` `mineableYield=4`
  INVENTED — spec's own "~2-5 per line-segment" range) and `RUT_Webwork_Nest`
  (nest raid: `ParentName="BuildingNaturalBase"`, `MayRequire="mlie.starwarsanimalcollection"`,
  same comp combination vanilla `Hive` uses — `CompCanBeDormant` +
  `CompWakeUpDormant` + `CompProperties_SpawnerPawn` spawning a Wyyyschokk
  guardian on `LordJob_DefendAndExpandHive` — `killedLeavings` Hyperweave 60
  INVENTED, midpoint of the spec's own "~40-80" range).
- `Defs/MapGeneration/ShokkweaveHarvestScatter.xml` — two `GenStepDef`s
  scattering the above onto `RUT_Webwork` maps only (biome-gated in C#, not
  XML — see below); nest scatter wrapped `MayRequire` for the donor mod.
- `Source/GenStep_ScatterWebworkSilk.cs` + matching `.csproj` — a ~20-line
  `GenStep_ScatterGroup` subclass gating on `map.Biome.defName == "RUT_Webwork"`,
  copied verbatim from the established sibling pattern
  (`FungalSoilTrade/Source/GenStep_ScatterFungalGround.cs`, itself from
  LanternDeeps). **Compiled clean**: `dotnet.exe build -c Release` — 0
  warnings, 0 errors — DLL lands at
  `src/RimUtinni/ShokkweaveEconomy/Assemblies/RimMandrake.Utinni.ShokkweaveEconomy.dll`.
  This is the mod's FIRST assembly (previously XML-only).
- Two new `Patches/*_MapGenPatch.xml` files add both GenStepDefs to
  `MapCommonBase` (silk unconditional, matching the sibling `FungalSoilTrade`
  patch shape and warning; nest wrapped `PatchOperationFindMod`).
- `About/About.xml` description extended to name both new routes.

**Every def field/API RimSage- or vendor-source-verified, never guessed**:
`MineableSteel`'s raw XML (RockBase shape), `Mineable.cs` source (confirms
`TrySpawnYield` fires on the Mine job AND on `Destroy(DestroyMode.KillFinalize)`
— i.e. ordinary combat destruction of a mineable vein/lair yields too, same as
vanilla `MineableSteel`; this is NOT the kit's "web-cutting rings no yield"
guard, which is about the *separate*, still-unbuilt web/anchor decorative
Things, not these dedicated resource nodes — called out explicitly in-file),
`Hive`'s raw XML (comp combination + `killedLeavings` shape),
`CompProperties_SpawnerPawn`/`CompProperties_WakeUpDormant` C# source (field
names), `LordJob_DefendAndExpandHive` C# source (confirms its constructor
takes `SpawnedPawnParams`), `Wyyyschokk` PawnKindDef (vendor source,
`mlie.starwarsanimalcollection`, combatPower 600), `AB_FeraliskInfestedJungle`
defName (vendor source, Alpha Biomes) — biome gate instead uses `RUT_Webwork`
(our own biome def, confirmed live-loaded, since it replaces the donor per
`RUT_Webwork.xml`'s own header).

**Offline-validated**: all 5 new/changed XML files parse
(`xml.etree.ElementTree`); `validate_patch.py` against the LIVE 592-mod list
(`ModsConfig.FULL.LATEST.xml`, confirmed byte-identical to the running
`ModsConfig.xml` this session) — **0 errors** on both new Patches files (both
`MapCommonBase` xpaths match exactly 1, same target the two working sibling
patches already use) and on the two new Defs files (0 errors; one advisory
WARN on the Nest's reused `Hive` texPath — expected per the tool's own
caveat, game textures live in asset bundles invisible to a loose-file scan;
confirmed correct instead via RimSage `get_def_details Hive`, which reads
that exact texPath off the live vanilla def).

**NOT deployed this session, and NOT attemptable**: the game is UP on the
full 591/592-mod list and `ShokkweaveEconomy` is already active in it (XML
only, from the 2026-09-11 session) — per the standing FOUNDRY constraint
tonight, a brand-new DLL for an already-loaded mod does not deploy while the
game is running. `needs` set to `deploy`.

**Still owed** (unchanged in kind from the 2026-09-11 gap, now scoped
tighter):
1. Deploy (game-down window): `deploy_custom_mods.py --mod ShokkweaveEconomy`,
   md5-verify the new DLL landed, restart.
2. Live proof, all via bridge/quicktest (never a cold load), all still
   blocked on step 1:
   - the original 11-trader-kind zero-stock generation proof (N≥20 rolls
     each — no bridge tool exists yet to force a specific TraderKindDef's
     stock generation; still its own `rimbridge-companion` cycle per the
     2026-09-11 note),
   - the quest-reward roll pass,
   - web-cutting: spawn a quicktest RUT_Webwork map, confirm `RUT_Webwork_SilkKnot`
     scatters and mining it yields shokkweave,
   - nest raid: confirm `RUT_Webwork_Nest` scatters (rare/singular),
     starts dormant, wakes and spawns a Wyyyschokk guardian on approach, and
     killing/deconstructing it drops 60 shokkweave.
3. Border creep-web (4th, ruled-in route): NOT attempted. Genuinely blocks on
   `RM_MapComponent_FrontCreep` (WEBWORK_MECHANICS_1 mechanic #6, itself
   gated on `RM_Gas_Transmuting` content-wiring), which is unbuilt — no
   queue item currently drives that build. Flagging as a gap: nothing is
   presently filed to build the Webwork biome's own SenseWeb/FrontCreep/
   web-and-anchor content kit at all (only the six generic RM_ comps from
   `ALPHA_MECHANICS_KIT_1` are built); the kit spec and roster item exist in
   design/ but have no FOUNDRY build item of their own yet.
4. Balance pass on every INVENTED number in this item (butcher 15, silk
   knot yield 4, nest yield 60, HP figures, scatter densities, guardian
   points) — flagged, not ruled, throughout.
