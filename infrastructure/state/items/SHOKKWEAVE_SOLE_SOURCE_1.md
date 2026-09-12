# SHOKKWEAVE_SOLE_SOURCE_1 — Shokkweave economy (rename, trader strip, harvest routes)

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
