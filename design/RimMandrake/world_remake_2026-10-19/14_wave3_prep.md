# World remake 14: Retirement Wave 3, prepared offline (2026-10-20)

FOUNDRY helper, offline, while the game was UP on the 380 list. No game, no bridge; the live `ModsConfig.xml` and Cherry
Picker file were only READ. **Not deployed; `FULL.LATEST` is NOT changed.**

Owner orders: *"we should get rid of the Fog of War. I think I'm done with it. It's ugly."* (card, 2026-10-19; supersedes the
Route B ruling that shipped Real Fog of War + CAI 5000 together; recorded as ruling 17 in `13_owner_rulings_2026-10-19.md`).
The other five come from the keep/cut sheet (`11_ruled_keepcut.md` §Wave 3) and card row 6 (Sensible Factions, *"drop it
permanently"*).

## 0. Counts

| list | mods | file (`infrastructure/state/modlists/` unless noted) |
|---|---:|---|
| base (= live ModsConfig = `FULL.LATEST`, parsed, equal) | 380 | `ModsConfig.FULL.LATEST.xml` |
| **Wave 3 drops** | **6** | `wave3_removed_6.txt` (packageId, name, why) |
| **new FULL** | **374** | `ModsConfig.FULL.WAVE3_374_2026-10-20.xml` (ET.parse 374, 0 dupes, 0 drops left, 6 `ludeon.*`) |
| DEV / TEST / AUTHORING / PAINT (RULED, regenerated in place) | 117 / 153 / 172 / 83 | unchanged: none of the six was in them |
| SHIP (RULED, regenerated in place) | 326 → **325** | `ModsConfig.SHIP.RULED_2026-10-20.xml` (Real FoW out; CAI 5000 + Prepatcher stay) |
| Cherry Picker SHIP keys | 1,747 → **1,747** | `infrastructure/state/cherrypicker/CherryPicker.SHIP.WAVE3_CANDIDATE.xml` (byte-identical: no SHIP key names a dropped def) |

The six (packageIds from the live list):

| packageId | name | why |
|---|---|---|
| `mlie.nwnrealfogofwar` | (NWN) Real Fog of War (Continued) | owner card 2026-10-19, ruling 17 |
| `gravtide.mod` | GravTide | keep/cut DROP |
| `deon.rimtek.core`, `deon.rimtek.digipal`, `deon.rimtek.docmate` | RimTek Core / DigiPal / DocMate | keep/cut DROP |
| `boots.sensiblefactions` | Sensible Factions | card row 6: drop permanently |

Closure on FULL and every RULED profile: **0 missing** (About.xml `modDependencies` incl. `v1.6` + `mod_facts.jsonl`
`class_ref`/`hard_dep`). **No retained mod hard-depends on a drop.** The only edge from a retained mod to a drop is
`mandrake.rut.researchretag`'s `forceLoadAfter` naming `mlie.nwnrealfogofwar` (order only; see step 6).

## 1. Closure in our src (instrument: `wave3_prep.py`, this folder)

Dropped defNames (the 380 capture `2026-10-20T03-35-54Z`, capture == list; defs whose every defining package is a drop, plus
the drops' own XML, minus anything Core/DLC or a retained mod also declares): **1,163** (GravTide 1,064, Real FoW 90,
DigiPal 5, DocMate 4; 0 collisions).

**The guard test is fixed** (Wave 2's 18 patch failures, `Transient/live_testing_2026-10-20a/RESULTS.md`, c674b7832): a
Conditional now counts as a guard only for a reference in its `<match>` branch, or when its xpath is a pure def-exists test
(`…[defName="X"]` with nothing after it); a FindMod only guards its `<match>` branch. Sanity probe: on
`StarWarsPatches/Patches/WeaponTags_Renormalise.xml` the new test reports 24 BS_ xpaths unguarded at `c674b7832^` and 0 at
`c674b7832` (the old test passed both).

| scan | result |
|---|---|
| src XML refs to a dropped def (active src mods) | **37: 36 guarded, 1 false hit** (`Inhabited/Defs/CastRosters/CastRoster_EMPIRE.xml`: the word "Inspector" in a `<label>`) |
| the 36 guarded | all ResearchRetag (`RUT_TechprintGating.xml` 24, `RUT_ResearchTabAssign.xml` 12) naming Real FoW's `CameraSecurity`, `CameraSecurityAdvanced`, `WatchTelescope`: 30 in a Conditional's `<match>`, 6 behind a def-exists Conditional |
| C# string literals naming a dropped def | **0** |
| `MayRequire` / FindMod / About `loadAfter` naming a drop | 0 / 0 / 0 (only the ResearchRetag `forceLoadAfter` above) |
| founders, `Gravship_v2_ring`, `Scenario_Utinni.xml` (8 files) | 0 dropped defNames |

**No src change is needed.** Things that assume Real FoW, checked by hand (grep: fog, FoW, RealFoW, CAI, rule56):
- `DivingInteraction/Source/Patch_RealFoWStaleHearing.cs`: `Prepare()` returns false when `RimWorldRealFoW.CompFieldOfViewWatcher`
  is absent, so Harmony skips it. The Mod Settings checkbox "Compatibility: Real Fog of War map-change fix" becomes a dead
  option (its own text says "Only matters if Real Fog of War is installed"). Cleanup, not a fix.
- `Webwork/Source/RM_WebworkProof.cs:213` `DesignatableAfterTicks`: steps ticks until Real FoW lets the designator accept;
  without it the first check accepts at tick 0.
- `GravshipLanding` (`rm.gravshiplanding`), `rm.visibility`, the bridge `set_fog` tool, Atlas/EggReckoning "unfogged" checks:
  vanilla fog only; nothing names Real FoW or CAI. `GRAVSHIP_LANDING_FOG_REVEAL_1` (closed) is vanilla `GenStep_Fog` and
  unaffected; its Real-FoW half disappears.
- GravTide: our sea BiomeDefs' "GRAVTIDE SUPPORT" blocks are vanilla fields (`terrainsByFertility`, `baseWeatherCommonalities`,
  `wildAnimalsCanWanderInto`): load-safe and still needed by any water map. The ship is the only way down (owner ruling,
  `RM_SeabedLayer`), so no GravTide arrival path is lost. `Armoury/Source/SelfTest/ArmouryFuzz.cs:587` names
  `MinesAutomated_RecipeDef_GravTide_CrossableRock_*` as strings in a pure-function table (no def lookup): stays green.
  Comments that call GravTide "active in the live list" (`RUT_TwilightFish_Niim.xml:21`, both copies) go stale at deploy.
- RimTek: only the ideo stamp (`src/Jawa/ideoligion/The Salvation.rid`, `MandrakeJawa.xtp`): the missing-mod notice is
  harmless; re-save the ideo under the new list (same caveat as `11_ruled_keepcut.md`).

## 2. Archive

`design/RimMandrake/mod_archive/ALL_ORIGINAL_MODS.tsv`: the six are `RETIRED-WAVE3` (2026-10-20, this doc, reason from
`wave3_removed_6.txt`); `krkr.rule56` (CAI 5000) reason corrected (it was "fog pair with Real FoW") and stays `ACTIVE-380`/SHIP.
`mod_archive.py check`: 766 rows, 0 missing. (`RETIRED-WAVE3` is set before deploy: the lists, not the archive, are the
deploy record.)

## 3. CAI 5000 (`krkr.rule56`) without Real FoW: RECOMMENDATION, owner's call

- **Does not depend on Real FoW.** About.xml hard deps: Harmony and Prepatcher (`zetrith.prepatcher`, which only CAI needs);
  `incompatibleWith` does not name Real FoW. So it stays on the Wave 3 list.
- **What it does for us now:** combat AI only (smarter cover, retreats, flanking for raiders and colonists). Its fog role
  is gone: `FogOfWar_DisableOnPlayerMap=True` (live settings) stripped *Real FoW's* fog on player maps, which no longer
  exists; CAI's **own** fog is OFF (`FogOfWar_Enabled=False`, `Config/Mod_3673768803_CombatAIMod.xml:13064`).
- **Nothing of ours depends on it**: no src XML/C# names it except ResearchRetag's `forceLoadAfter` (order) and
  `gen_creature_register.py`'s list of its comp classes to ignore.
- **Risks (07):** listed in 07 §4b only for fog (strips fog; blinded the gravship landing, which was really vanilla
  `GenStep_Fog` + Real FoW). Prepatcher's own risk (fatal when an add-on is orphaned) rides with it.
- 🔴 **Player-facing trap:** CAI's name is "Advanced AI + Fog Of War" and it ships its own fog layer. Our live settings turn
  it off, but **a player's fresh install gets CAI's code default, which is UNMEASURED** (`FogOfWar_Enabled` default not read).
  If the default is on, players see exactly the fog the owner just called ugly.
- **Recommendation:** keep CAI for its combat AI, and before ship either (a) measure the default and, if it is on, force
  `FogOfWar_Enabled=false` from a mod of ours (settings patch at startup), or (b) drop CAI + Prepatcher too if the combat AI
  is not something he wants to evaluate. Low cost either way: nothing depends on it.

## 4. Live deploy (exact steps; game DOWN, bridge held). Do NOT do while the game is up.

1. `rimflow bridge take --for "Wave 3 retirement deploy"`; `./game` must read down (close the game first; `./game --why "…" down`).
2. Back up: copy live `ModsConfig.xml` → `infrastructure/state/modlists/ModsConfig.LIVE_BACKUP_<date>_pre_wave3.xml`.
3. Mods: **nothing to deploy for Wave 3** (no src change). If anything under `src/` changed since, plan BOTH halves
   (lesson `20261020T024929Z-FOUNDRY-wave-list-deploy-must-plan-both.md`): `deploy_custom_mods.py --mod <M>` for flat mods
   **and** `deploy_custom_mods.py --compose biomes` (Baroque Biomes is composed; a `--mod` deploy of a biome folder does not
   reach it), plan, read, then `--apply`.
4. Mod list: copy `ModsConfig.FULL.WAVE3_374_2026-10-20.xml` over the live `ModsConfig.xml`; parse it back: 374, sha equal to
   the file. Then `cp ModsConfig.FULL.LATEST.xml ModsConfig.FULL.PRE_WAVE3_380.xml` and copy the 374 list to
   `ModsConfig.FULL.LATEST.xml` (only now).
5. Cherry Picker: **no change** (candidate == current SHIP, 1,747 keys). `cherrypicker_swap.py --status` must read 1,747.
6. Cold load (Steam). Read the FIRST exception in Player.log; compare with the 380 baseline (`Transient/live_testing_2026-10-20a/`,
   load #3: exceptions 3, patch failures 3 / ours 0, xref ours 0, config errors 14 / ours 1 Ummisk BodyDef). Any new patch
   failure naming CameraSecurity/WatchTelescope means a ResearchRetag guard is wrong. Arm a def dump; on it run
   `selftest_researchretag.py`, then remove `mlie.nwnrealfogofwar` from `src/RimUtinni/ResearchRetag/About/About.xml`
   `forceLoadAfter` and deploy ResearchRetag (the Wave 2 order: removing it before the dump turns
   `force_load_after_names_every_donor_owner` red).
7. In game, Mod Settings → CAI 5000: confirm "fog of war" is off (and for the record, note its default if a reset button shows it).
8. Release the bridge; commit the backup + FULL.LATEST + PRE_WAVE3 by explicit path; `./publish`.
Rollback: the backup from step 2.

UNMEASURED: save-borne residue of GravTide/RimTek/Real FoW things in the `_AREAFIX2` fixtures (`save_def_census.py` after
the load); CAI's shipped fog default; C# string defName references inside third-party DLLs; load time of the 374 list.

Work files: `Transient/wave3_prep_2026-10-20/` (dropped_defnames.json, src_guarded.json, src_unguarded.json).
Tools: `wave3_prep.py <ids> <workdir>`, then `wave3_lists.py <ids> <workdir>/cp_wave3_keys.txt <workdir>/roots.json`.
