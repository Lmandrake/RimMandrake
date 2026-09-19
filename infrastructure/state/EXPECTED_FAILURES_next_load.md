# Decision strings — next load after the Caverns cut, 2026-09-18

Written BEFORE the game closes (rimworld-load-round §2/§3). Loads A and B of the
Caverns window are harvested (`CAVERNS_PARITY_BUILD_1` notes, 2026-09-18); this sheet
is the load that follows. Backup of the pre-cut list:
`infrastructure/state/modlists/ModsConfig_before_caverns_cut_2026-09-18.xml`.

## Load C — full list, `biomesteam.biomescaverns` OUT, `mandrake.rut.lanterndeeps` IN, 10 ArtOverride mods OUT (622 active, MEASURED)

Riding: the LanternDeeps assembly on the FULL list for the first time (it was only ever
proven on the 10-mod list — Load B never had it enabled), AND a rebuilt DLL
(`DEEP_ENTRANCE_BIOMES_SETTING_1`: entrance biomes are now a Mod Settings list). Core,
Polluted Lands and Fossils STAY (owner ruled Caverns only; Fossils kept on his word).

✅ **LanternDeeps DEPLOYED 2026-09-19 02:2x** (BENCH, during the other window's 29-mod
quicktest — the mod was not in that list, so its DLL was not locked): DLL + About + defs +
sound + 50 textures under the renamed paths, `--prune` removed the old plant folders,
VERIFIED in sync. `modcheck run LanternDeeps` still owed in a window of its own (it swaps
the list). ⚠️ The live list is the peer's 29-mod quicktest list; the FULL list to restore is
`Config/ModsConfig.xml.bak_pollutedlands_removal_20260919T021429Z` (622: Caverns out,
LanternDeeps in, 10 ArtOverrides out) or the peer's own 621 (Polluted Lands out as well) —
NOT `infrastructure/state/modlists/ModsConfig.FULL.PRECAPTURE.20260918_141403.xml`, which is
the pre-cut 630.

| item | string | baseline | means |
|---|---|---|---|
| entrance setting round-trips | Mod Settings → Lantern Deeps → "World generation: entrance biomes" shows 3 of N selected; `Player.log` has no `Scribe_Collections` error naming `entranceBiomes` | — | error ⇒ settings load shape wrong; entrances silently gate on nothing |
| the hum plays | enter a Deep, listen 30 s: steady low hum, periodic swell. If silent: `Player.log` lines naming `RUT_DeepHum` / `RUT_DeepChorus` / `Undercave_Ambience` / `VoidNode` | — | a "could not find clip" line ⇒ cross-pack clip path does not resolve; fall back to a Core clip |
| canonical save loads without Caverns | load `CANONICAL_ASHKARR_START_2026-09-12.rws`: count `Could not load reference` lines naming `BMT_` (expect dict-key skips), and 0 NREs on the mothballed colonists Nina Marsh / Kazuya Sexton (apparel stuff `BMT_MoonlessSilk` / `BMT_BatWool`) | never loaded this way | an NRE on apparel ⇒ scrub those 3 `<stuff>` (finding on `CANONICAL_SAVE_CAVERNS_SCRUB_1`) |
| rehomed override art | NOT in this load unless SWBestiary was redeployed (its plan carries Pass 21) — kroffa/puffmite still read maligoat/fleece spider until then; not a finding | — | — |

| item | string | baseline | means |
|---|---|---|---|
| Caverns gone | mod roster in Player.log lacks `Biomes! Caverns`; `measure get BMT_CrystalCaverns` → UNMEASURED/absent | present | present ⇒ ModsConfig was rewritten by the mod menu or RimSort — re-apply the cut |
| LanternDeeps loads | `measure get RUT_LanternDeeps` → BiomeDef; NO `TypeLoadException` naming `RimMandrake.Utinni.LanternDeeps` | absent in Load B | absent ⇒ the mod is off again or its About.xml failed |
| Harmony patch attaches | NO Harmony error naming `Patch_PocketMapGrowthRate`; Harmony patch failures stay = 1 (HAR/Universal Pregnancy) | 1 | 2 ⇒ our patch collided on the full list |
| cave-fungus crash surface dead | NO `MapComponent_CaveFungus` / `Caveworld_Flora_Unleashed` in any stack | present before | present ⇒ Caverns is still loading |
| guarded refs stayed silent | `Could not resolve cross-reference` lines naming `BMT_` from OUR files (UtinniPatches, Doctrine, PawnFlavor, Armoury) = 0 — every BMT_ op there is Conditional/FindMod-guarded | 0 | >0 ⇒ an unguarded Caverns reference; name the file |
| Polluted Lands still whole | NO dependency warning for `biomesteam.biomespollutedlands` (its Core dependency is still active) | 0 | present ⇒ Core was removed by mistake |
| art-override mods | the 5 `mandrake.rut.*artoverride` mods load without error but now patch nothing — expected, NOT a finding (`CAVERNS_LOADAFTER_STRIP_1`) | — | — |
| EmptyAICore | `Could not resolve cross-reference ... EmptyAICore` still logs — KNOWN (`RUT_Ported_GravForge.xml`, finding on `CAVERNS_PARITY_BUILD_1`), not new | 1 | — |
| Deep generates on the full list | quicktest → enter the emergence entrance → map with biome `RUT_LanternDeeps` exists; `RUT_Lanternstone*` count > 0; 0 exceptions | Load A: 525 walls / 21 formations | exception ⇒ a full-list mod collides with the pocket-map patch — read the stack, it was clean on 10 mods |
| magenta is EXPECTED | pink textures on crystals/flora are NOT a finding (art in the one-sheet sitting) | — | do not file |
| Deep flora renamed (`DEEP_FLORA_RENAME_1`) | after the dump, `measure get` resolves all eleven: `RUT_DeepMycelium`, `RUT_ZivvitTaper`, `RUT_QuorrFern`, `RUT_OsskBramble`, `RUT_BrellikBulb`, `RUT_TwitchingPuffer`, `RUT_ThrakkCap`, `RUT_PrennaLace`, `RUT_VellokReed`, `RUT_KuvraSpout`, `RUT_NurrikGill`, plus item `RUT_PufferTendrils`; the old ten (`RUT_Gleamtip`, `RUT_Fungusfern`, `RUT_CrystaltipBrambles`, `RUT_YumBulbs`, `RUT_DeepDulcisPlant`, `RUT_Crystalcap`, `RUT_DeepGreyLady`, `RUT_DeepArpeau`, `RUT_LuminousSpout`, `RUT_DeepNuitae`) are ABSENT; `RUT_RawDulcis` is referenced by nothing in LanternDeeps (RotSporeKit dependency dropped) | old names present | a `Config error` or cross-reference line naming any old name ⇒ a missed reference in the rename; the puffer's three plant stages and the tendrils item render magenta until the four `twitchingpuffer_*_v1` jobs are wired — NOT a finding |

## Owed before this load, if they land in time
- `DEEP_DULCIS_DEDUP_1` / `DEEP_FLORA_RENAME_1` (FOUNDRY): `RUT_DeepRawDulcis` and
  `RUT_DeepDulcisPlant` ABSENT from the dump; `RUT_RawDulcis` present (RotSporeKit's, now
  unreferenced by LanternDeeps); `RUT_TwitchingPuffer` and `RUT_PufferTendrils` PRESENT and
  `RUT_LanternDeeps.foragedFood` resolves to the tendrils. If the rename is not deployed,
  the old ten defs still load — expected, not a finding.
- SWBestiary Pass 21 (other window): if committed + deployed, `RSW_Scavrat`, `RSW_Runyip`,
  `RSW_Scurrier` appear in the dump and the BiomeCast regen unblocks. If not, they stay absent
  and it is STILL not a regression.

## Not riding this load
- No Core / Polluted Lands cut (waits on `POLLUTED_LANDS_FLORA_PORT_1`). No Fossils cut, ever
  unless he says so again. No BiomeCast regen until the dump holds the Pass 21 kinds.

## Load D — full list 622 (Load C's 621 + `mandrake.rsw.gizkastowaway` back at 553), LanternDeeps darkness DLL rebuilt, defs dump ARMED (`all`)

Backup of the pre-reactivation list: `infrastructure/state/modlists/ModsConfig_before_gizka_reactivate_2026-09-19.xml`.

| item | string | baseline | means |
|---|---|---|---|
| gizka exonerated (`GIZKA_TRIBBLE_ADAPTATION_1`, `FULL_LIST_CANNOT_LOAD_GAME_1`) | load `CANONICAL_ASHKARR_START_2026-09-12.rws` with gizka ON: 0 lines `ReadingPolicyDatabase` / `GenerateStartingPolicies`; 0 `has null thingClass` | Load B (gizka ON, FlowWorks DLL stale): NRE every `new Game()`, `Config error in RM_LiquidTank: has null thingClass` | save reaches Playing ⇒ the NRE was `RM_LiquidTank`'s null thingClass (stale FlowWorks DLL), gizka stays ON and the item closes. NRE again ⇒ gizka really is the culprit; deactivate from the backup |
| darkness ambush fires (`LANTERN_DEEPS_INJECTION_1`) | on a Deep, 6 campfires around a drafted colonist, ≤ 8,000 stepped ticks: a new `RSW_BloodropMoth` on the map in `Manhunter`, 0 exceptions in `effects.logs` | Load C build: 16,500 ticks, nothing (glow capped at 0.5 under roof) | fires ⇒ item closes on live proof; silent ⇒ `lightExposure` never crosses 60 — read the component, not the light |
| defs dump lands | `DefDump/captures/` gains a fresh `defs` capture (not animals-only); `dump_request.txt` deleted after | Load C wrote an animals-only dump (request content `1`) | no capture ⇒ request content wrong again |
