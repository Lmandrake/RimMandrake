# RETIREMENT WAVE 1: the authoritative definition

Owner order, card answer 2026-10-10: **"Start, prerequisites first"** (`OWNER_RULINGS.md`, row "Retirement wave 1").
This file is the single definition of the wave: which packageIds leave, in what order, behind which gates, and
what each step needs (game DOWN, game UP with the bridge, or a cold load). It replaces the 22-mod table that
`ACTIONS_NOW.md` carried under the same heading. The bridge-session commands are in
`RETIREMENT_WAVE_1_RUN_SHEET.md`. Offline evidence (2026-10-10, FOUNDRY, no bridge, no game):
`Transient/foundry_wave1_save_census_20261010.md` (save census), `Transient/foundry_wave1_lint_20261010.md`
(candidate lists, effective-def lint, reduced-tree reference scan), `Transient/foundry_retire_wave1_20261010.md`
(progress log).

## 1. What leaves

Positions are 0-based indexes in `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` (551 active).

| group (ruling) | packageIds (position) | n |
|---|---|---:|
| already ruled, list regressions (ACTIONS_NOW §A) | `gravenwitch.vsrexamined` (354), `jellypowered.survivaltools` (300), `leo.raidprotectionfee` (245), `mlie.beastsoftherim` (61) | 4 |
| C02 sandworm | `chezhou.creature.sandworm` (480), `chezhou.chezhoulib.lib` (455) | 2 |
| C07 crew growth | `sl4vp0wer.weareunited` (363), `mlie.syrmoreslaves` (38) | 2 |
| C08 skill ladders | `sarg.alphaskills` (453), `vanillaexpanded.skills` (450) | 2 |
| C09 event layers | `mlie.largefactionbases` (187), `mlie.storytellerenhanced` (295), `font.rimesis` (462) | 3 |
| C10 convenience nine | `groovytaco.beltextractors` (385), `reel.turretpipeline` (251), `erdelf.minifyeverything` (209), `clown.dedicatedturrets` (105), `neronix17.shieldgenerators` (484), `juanlopez2008.lightsout` (192), `hmc.wall.furniture` (26), `kyzy.shipwallenhanced` (432), `arcjc007.wallstuff` (430) | 9 |
| C13 industry (later card: retire now) | `thumb.bettercremation` (94) | 1 |
| C15 old donors (`mod_deepdive_oldwhy_removal.md`) | `vanillaexpanded.vwe` (356), `vanillaquestsexpanded.ancients` (346), `sarg.alphamechs` (51), `milkwater.destinymod` (108), `aoba.warcasket` (470) | 5 |
| C19 off-tone cut-now (`mod_deepdive_offtone.md`) | `flangopink.metalpipe` (204), `flangopink.metalpipehorseshoe` (205), `kshtantrumsounds.mod` (58), `bonible.medievalmeleesounds` (201, the "Monty Python" clangs), `armoredampharos.fancyrats` (40), `tyrannidae.fancyratsplus` (136), `van.dacrypts` (101), `aqued.dredgeaberrations` (56; absorb is a design note, the cut does not wait) | 8 |
| C19 list hygiene | `vlvop.tormentmaster.expansion` (305): ruled "not installed, simply dropped from the list" | 1 |
| **total unticked** | | **37** |
| swap (`PYRINTH_MIGRATE_LIST_NEVER_SWAPPED`) | `det.epochspyrinth` (130) out, `mandrake.rm.pyrinth` in at the same index (deployed; keeps the donor's `DV_*` defNames) | +1 / -1 |
| C22 shells, **conditional (W4b)** | `meteores.ancienturbanruinsalldeconstructible.aurad` (435), `meteores.ancienturbanruinsvanillaloot.aurvl` (454), `redmattis.bigsmall` (486). `xmb.ancienturbanruins.mo` (382) is held: not save-safe (conflict 5) | 3 |

Result: `ModsConfig.WAVE1_CANDIDATE.xml` (514 active) and `ModsConfig.WAVE1_CANDIDATE_PLUS_SHELLS.xml` (511),
both in `infrastructure/state/modlists/`, plus `manifest.WAVE1.json`. Neither is the live list.

**Also in this wave, not an untick:**
- Bones (`sihv.rombonesport`) stays loaded; its `Make_ChemfuelFromBone` and `MakeBonePlasteel` recipes are cut by a
  FindMod-guarded patch (owner card 2026-10-10), and every `BoneAmount` write of ours is now guarded on Bones.
  `MakeBonePlastic` is not cut (unjudged). The lean port is a separate build (`BONES_LEAN_PORT_BUILD_TREELESS_WORLD`).
- Better Infestations stays loaded; its own `BI_SwarmingHorde` and `BI_InsectRaid` events are silenced (C09).
- Cherry Picker: the repo SHIP profile goes live minus the 140 keys whose defs leave (§3 W2).

**Conflicts resolved explicitly.**
1. *ACTIONS_NOW said 22 mods; the owner's order names more.* The wave is the union of every ruling that says
   "now": the 22, plus Better Cremation (card after C13), the five C15 donors (C15 typed "remove them all" and the
   deep dive found the order and the bites), the eight C19 cut-now/absorb-then-cut-now mods, the Torment Master
   list entry and the Pyrinth swap.
2. *Registry verdicts that disagree.* `sarg.alphamechs` reads KEEP and VWE/Ancients/Warcasket read PHASE-OUT in
   `MASTER_REGISTRY.jsonl`; C15 overrides them (the deep dive §4 shows the KEEP rested on misreading the 2026-08-15
   "we are keeping the mechanoids" ruling, which the Core/Biotech/Odyssey mechanoids still satisfy). The registry
   rows are corrected when the wave lands (§3 W6), not before.
3. *Dredge "absorb-then-cut".* The absorb is only a design note (`RARE_CATCH_DESIGN_PERMANENT_BUFF_EATING`), so
   the cut is in this wave (`mod_deepdive_offtone.md`).
4. *Medieval Flavour.* `shavius.medieval.flavour` is ELIMINATE in the registry (a shell under the C22 doctrine), so
   its Cherry Picker cuts are not maintained for the long term and are **not hand-restored**. The mod is not named by
   any wave ruling, so it stays this wave. The save census found its only state: one living MOTHBALLED world pawn,
   Rebecca Rock (`Human933`, Ascendant Helix), with adulthood `SH_MED_MedievalAlchemist` (which is not itself a cut).
   Its 26 backstory cuts ride along in the SHIP profile until it leaves; it is the cheapest candidate for wave 2.
5. *Shells (C22: "may be uninstalled after the save check").* The census splits them: `meteores.ancienturbanruinsalldeconstructible.aurad`,
   `meteores.ancienturbanruinsvanillaloot.aurvl` (patch-only, CLEAN) and `redmattis.bigsmall` (6 faction defs in an
   `ignoredFactions` list and filter rows only) are save-safe and are admitted as the conditional step W4b.
   `xmb.ancienturbanruins.mo` is **NOT** save-safe: a placed `AM_DamagedEmptyShelves` at (140,0,114), a live faction
   `AM_EnemyPirate` "The Ash Crushers" (`Faction_18`, 25 relation rows), 3 relic precepts, 56 drug-policy rows, two
   component classes and ~1,230 of the first-load errors. It stays; its excision is its own item for wave 2.
6. *Torment Master.* Not installed (no `About.xml` with `vlvop.tormentmaster.expansion` in either root, 2026-10-10;
   the probe `erdelf.minifyeverything` was found). Only the list entry goes.

## 2. Held back (NOT in this wave)

Yayo's Combat 3 and Stronger Quality Scaling (deep analysis running); every face mod (C16 keep); Ideology Virtues
(`dimonsever000.ideologyvirtues`: 41 live precepts, waits for the virtue judgement and a save probe); the world
generators (C05: `GENERATOR_MODS_PROVE_INERT_AFTER_CREATION`) and Geological Landforms / Biome Transitions (C06
experiments); Oracle / RimAI (C23 study); RimTek Core, DocMate, DigiPal (C21: only once our replacements exist);
Faction Raid Cooldown and More Faction Interaction (event-wisdom study); `van.beasts` (troll line: Cherry Picker at
the biome sitting; `RM_Uttaqar`'s baby texture still uses it); Bones itself; every C01/C03 PHASE-OUT donor;
`mandrake.rm.strandedquest` (owner: not retired).

## 3. Steps

The removals are independent (the deep dives' lint deltas are disjoint), so the whole wave spends **one cold load**.
Everything before W5 is offline or game-DOWN work; the order below is also the bisection order if that load
surprises. Each step is its own commit. State column: **DOWN** = game not running (DLLs and Config files are only
written then), **OFFLINE** = no game needed, **COLD** = the one cold load, **UP** = game running, bridge held.

| step | what | state | prerequisite | offline test before it | acceptance |
|---|---|---|---|---|---|
| W0 | Back up the live `ModsConfig.xml`, `ModsConfig.FULL.LATEST.xml` (as `ModsConfig.FULL.PRE_WAVE1.xml`, committed), `manifest.FULL.json`, the Cherry Picker config, the canonical save; stat the Saves folder | DOWN | bridge free or ours; `./game` says NOT RUNNING | — | each backup exists, sizes logged |
| W1 | Deploy the offline fixes (§5): Armoury, StarWarsPatches, ResearchRetag, UtinniPatches, Doctrine, GreentideRaidAnt, LuminousPigment | DOWN | fixes on origin/main; clone level with origin for those paths | `validate_patch.py` per changed patch (done); `effective_def_lint.py` on the candidate with `packageId=folder` overrides to the fixed sources: 0 crash, `failed_ops` only the baseline Rakata rows | deploy plan shows only the intended files; `--apply` verify passes |
| W2 | Cherry Picker: `CherryPicker.SHIP.WAVE1_CANDIDATE.xml` becomes the SHIP profile, then `cherrypicker_swap.py --ship --apply` | DOWN | W0 | candidate parses; 2,177 keys = SHIP 2,317 minus the 140 whose defs leave (dump 2026-10-04); 0 keys added | swap prints its PRESWAP backup; live key count 2,177 |
| W3 | `wave1_save_preedit.py` writes an edited COPY of the canonical save: removes the 11 minified walls (0 references elsewhere), the dead `futureQuests` rows `VQE_AncientLabComplex` and `VQE_Cryptoforge_Chapter1`, and maps 198 VSE/Alpha Skills passions to vanilla, puts the 5 VWE relic precepts on the approved KotOR uniques (§6) | OFFLINE | W0 | done on a scratch copy 2026-10-14: OK, delta 16,868 bytes, relics 5 -> 0 on VWE, a re-run is byte-identical; refuses if the counts moved | output OK line; canonical file md5 unchanged |
| W4 | Promote `ModsConfig.WAVE1_CANDIDATE.xml` to `ModsConfig.FULL.LATEST.xml`, regenerate `manifest.FULL.json`, `modlist_swap.py --restore --apply` | DOWN | W1-W3 | `effective_def_lint.py` on the candidate (§4 of the lint report); `modmanifest.py diff` shows exactly the 37 ids + the Pyrinth swap | `modmanifest.py check` exits 0 |
| W4b | (conditional) use `..._PLUS_SHELLS` instead: also drops the two `meteores` AUR patches and `redmattis.bigsmall` | DOWN | census CLEAN/NOISE-ONLY for all three (met) | lint on the PLUS_SHELLS list: no new crash class | as W4 |
| W5 | ONE cold load; load the edited save; acceptance (§7) | COLD, then UP | bridge taken; W4 | `preflight_bridge.py --tier wave1 --deep` GREEN | first exception is not ours; expected-error classes only (§7); the acceptance list passes |
| W6 | Re-save under a NEW name; second load: 0 `Could not load reference` lines for wave mods; owner decides whether it becomes `canon.yml` `planet.start_savegame`; records: registry rows of the 37 (and the 3 shells) to RETIRED, `RETIREMENT_CHECKLIST.md` Beasts step 4, `assemble.py`, `merge_checks.py`, `run_selftests.py` | UP, then OFFLINE | W5 passed | — | records show the ids gone; selftests green |

### Per-mod gates (census and src references)

"src refs" are our references that survive in the reduced tree, from `Transient/foundry_wave1_lint_20261010.md`;
"save" is the census verdict. Every row's gate is met unless the last column says otherwise.

Our C# was searched separately (`git grep` over `src/**/*.cs|csproj` for each mod's namespace or type stem; probe
`Verse` 2,032 files): **0 type references** to any wave mod; the only hits are comments and bridge help strings
(`Leo.RaidProtectionFee` in JawaBench, "SandWorm" in a LongHunger comment, ShipShields' own `ShieldGen` types).
No remaining active mod hard-depends on a removed id (About `modDependencies`, both roots); only `loadAfter`s remain.

| packageId | our src refs (after the §5 fixes) | save (census) | gate |
|---|---|---|---|
| `gravenwitch.vsrexamined`, `jellypowered.survivaltools` | none; `STAT_NORM_WAVE3_RETIRE_1` counter-patches are guarded | VSR CLEAN; ST: 3 scenario parts, 1 lost component, rows | met (scenario parts drop with a warning) |
| `leo.raidprotectionfee` | none (JawaBench help text only) | 1 lost world component | met; acceptance §7.3 |
| `mlie.beastsoftherim` | none | 15 `Leather_*` apparel on world pawns, auto-slaughter rows | met (default stuff on load) |
| `det.epochspyrinth` -> `mandrake.rm.pyrinth` | `mandrake.rm.biomes` patches match the absorber's verbatim `DV_*` names | every donor `DV_*` def is also defined by the absorber: 0 real loss | met; absorber deployed |
| `chezhou.creature.sandworm`, `chezhou.chezhoulib.lib` | none (`mandrake.rut.longhunger`: comments only) | 18 lost component classes, rows | met |
| `sl4vp0wer.weareunited`, `mlie.syrmoreslaves` | none | CLEAN | met; C07 study notes are a separate item, not a load gate |
| `sarg.alphaskills`, `vanillaexpanded.skills` | none (`VSE_` names absent from biomes/graffiti) | 198 custom passions on 99 pawns (6 colonists), 151 AS hediffs | met by W3's passion map (§6) |
| `mlie.largefactionbases`, `mlie.storytellerenhanced`, `font.rimesis` | none | rows; Rimesis 1 lost world component | met |
| the convenience nine | pruned (`56958bf60`, `edd1ba89a`, `1cd5b165b`) | 0 placed things; **11 minified walls** (Minify); 2 lost components | met by W3 (walls removed from the copy) |
| `thumb.bettercremation` | none | CLEAN | met; vanilla cremation until `SALVAGE_YIELD_UNIFY_THREE_RULES_TODAY` |
| `vanillaexpanded.vwe` | `WeaponTags_Renormalise` block removed (`b2e398638`); ResearchRetag rows Conditional (inert) | 5 relic precepts | met; W3 repairs the relics (§6) |
| `vanillaquestsexpanded.ancients` | 5 files, all FindMod/Conditional except 2 Rakata backstories (string category, now unreachable) | `futureQuests` row, 1 `ignoredFactions` row | met by W3 (row removed) |
| `sarg.alphamechs` | six failing ops removed (`b2e398638`); RimAI prerequisite restored (`1cd5b165b`) | 2 Big and Small cache rows (third-party, UNMEASURED) | met; watch the log for Big and Small |
| `milkwater.destinymod`, `aoba.warcasket` | none / generated FindMod rows (inert) | drug-policy rows, 1 lost map component; 1 Tyrant on a dead pawn | met |
| off-tone eight | roster comment (`a1fd89e47`), FancyRats evictions (`8150cb9b5`), Crypts retag rows (`1cd5b165b`) | 2 pipes on dead pawns; rows | met |
| shells (W4b) | none in our src for the three admitted | CLEAN / NOISE-ONLY | met; `xmb.ancienturbanruins.mo` held |

**Effective-def lint (offline, 2026-10-10, `effective_def_lint.py` under `python.exe`, with `packageId=folder`
overrides pointing at the fixed sources of the seven changed mods):** both candidates are **crash-class 0**;
every check passes except `failed_ops`, which reports only the **2 pre-existing** `AncientsAreRakata.xml` rows
(baseline FULL.LATEST has 3; the third, `VQEPatients_AreRakata.xml`, stops firing). `costlist_resolve_check.py`:
1 miss, vanilla `Meat_Human` in CannibalPlatter, same as baseline. Before the fixes the candidate showed the six
Alpha Mechs `failed_ops`; they are gone.

## 4. Rollback

At any point before W6 the old state is three files and a list:
1. `cp infrastructure/state/modlists/ModsConfig.FULL.PRE_WAVE1.xml infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`
   (commit), game down, `modlist_swap.py --restore --apply`.
2. Cherry Picker: `cherrypicker_swap.py` restores from its PRESWAP backup (or `git revert` the SHIP commit and swap again).
3. Save: nothing to undo; the canonical save is never edited in place (W3 writes a copy, W6 saves under a new name).
4. Deployed fixes are load-safe with the wave mods still present (every new op is FindMod-guarded or deletes rows
   that only named the removed mods), so they stay; `deploy_custom_mods.py --apply --mod <M>` from the pre-wave
   commit restores one if it misbehaves.
Bisection if W5 shows an unexplained error: restore FULL.PRE_WAVE1, then re-remove in this order, one load each:
the CLEAN/code-only mods; the off-tone eight; the convenience nine; C07/C08/C09; Destiny + WarCasket; VWE; Ancients;
Alpha Mechs (Harmony-heavy, most referenced) last.

## 5. Offline fixes made for the wave (published 2026-10-10, not yet deployed)

Each fix is in the generator (or its input), never a counter-patch. Verification was offline: XML parse,
`validate_patch.py` (with `--defs` where noted), generator selftests where they exist, and the effective-def lint.

| sha | fix | why the wave needs it |
|---|---|---|
| `b2e398638` | `weapon_tag_audit.py` drops `AM_`/`VWE_` rows (`RETIRED_DEF_PREFIXES`); `WeaponTags_Renormalise.xml` loses the six Alpha Mechs Conditional-with-nomatch ops and the VWE FindMod block | the six ops would log red `Patch operation ... failed` errors the moment Alpha Mechs goes |
| `1cd5b165b` | ResearchRetag: the RimAI row keeps RimAI's own `RimAI_AI_Level3` (was replaced by `AM_Cryptoharmonization`); `build_retag_patches.py` skips retired source mods; Crypts ×2, `DedicatedDefenceSystems`, `ShieldGen_*` rows and five loadAfters removed | otherwise `RimAI_Subspace_Gravitic_Penetration` becomes a root project with zero prerequisites plus a cross-reference error |
| `a1fd89e47` | `gen_pawnkind_roster.py`: the Jawa roster comment names Core `MeleeWeapon_Club` / `GS_Gaffi`, not the metal pipe | the comment would be false once Metal Pipe goes |
| `bd5db3e5f` | `gen_megafauna_yield.py` and the two OwnedPorts files: every `BoneAmount` write sits under a Bones FindMod; `RUT_Race_GreentideAnt.xml` `MayRequire="sihv.rombonesPort"` | hygiene owed before Bones' own exit (up to 374 cross-reference errors and null stat entries) |
| `dec8ef9de` | `UtinniPatches/Patches/Bones_CutFuelAndPlasteelRecipes.xml`: removes `Make_ChemfuelFromBone` and `MakeBonePlasteel` and their BiofuelRefinery entries (FindMod; `validate_patch.py --defs` 0 errors, all 4 targets resolve) | owner card 2026-10-10 |
| `9ac8f0cad` | `UtinniPatches/Patches/BetterInfestations_SilenceOwnEvents.xml`: `baseChance` 0 on `BI_SwarmingHorde`, `BI_InsectRaid` | C09 |
| `8150cb9b5` | FancyRats: the 2 eviction ops and the loadAfter removed | inert after the cut; no live text may point at a gone mod |
| `56958bf60`, `edd1ba89a` | convenience prune: HMC rows (`gen_armoury_patch.py` `RETIRED_DONORS`), Dedicated rows (`gen_turret_doctrine.py`), two Armoury loadAfters; `DeepfireLightsOutCompat.cs` and its csproj entry, debug action, spec rows and walk line; LuminousPigment DLL + `.srchash` rebuilt | `convenience_replacements.md` §3 |
| `5c7d7387e`, `3b3d1bca2`, `f6859bcfd` | `src/RimMandrake/Utils/modaudit/wave1_save_preedit.py` (W3; `f6859bcfd` adds the relic repair and `selftest_wave1_save_preedit.py`) | the save repairs, without a second cold load |
| `67153b072` (earlier, FOUNDRY) | durasteel catch-all in both Armoury convert patches | **without it FULL.LATEST itself NREs in MinifyEverything at load** (`FULL_LIST_LOAD_DIAGNOSE_MINIFY_SAYS_NO`); deploy it in W1 regardless |

Known drift, recorded so nobody is surprised: three generated outputs were edited to match what their generator
now emits because the generator could not be re-run offline today (`weapon_tag_audit.py` refuses on a dump/list
mismatch; `build_retag_patches.py`'s pinned capture `2026-09-04T02-23-44Z` is gone; `MegafaunaYield.xml` was pruned
in place, 37 of 38 regenerated blocks matched, the 38th, Boomalope, exists only in the newer dump). And
`JawaFactionRoster.xml` on origin carries `MayRequire` guards its generator does not emit: a regen would strip them.

## 6. Save decisions taken offline (FOUNDRY defaults; the owner may override before W3)

- **Passions.** Skills stay vanilla (C08), and vanilla scribes `Passion` as an enum (`SkillRecord.ExposeData`,
  default `None`), so every `VSE_*`/`AS_*` value would silently fall to None on 99 pawns, 6 of them colonists
  (Wim Ateeka, Griz Utinn, Yeku, Tobb Nkik, Nekko Vok, Sekki Vosh). W3 maps them instead: `VSE_Critical`,
  `VSE_Natural`, `AS_PsychicPassion_Major`, `AS_BlindPassion_Sublime` -> Major; `VSE_Apathy`, `AS_DuncePassion` ->
  None; every other conditional Alpha Skills passion -> Minor (table in the script). The 151 `AS_*` hediffs are
  left to drop on load (null-def hediffs are removed).
- **Relics.** The 5 VWE relic precepts would re-roll to a random relic on load (`Precept_ThingDef.ExposeData`, one
  error each), so W3's fourth repair (`RELIC_MAP` in the script) rewrites their `<thingDef>` to the KotOR uniques the
  owner approved by card 2026-10-14 ("Approve all five"; `design/RimMandrake/relic_replacements_proposal.md`):
  Hexlink (Astropolitan) -> `guy762_disrifle_baragwin`, Loccorpus (the Contract) -> `guy762_brifle_jurgan`, Animal
  Blaster (the Green Oath) -> `guy762_bowcaster_zaalbar` (all three were `VWE_Gun_ChargeLMG_Unique`); Strong Rifle
  (the Ascendant Genome) -> `guy762_carbine_hogra`, Rifle of Self (the Balance) -> `guy762_hvypistol_nadd` (both
  `VWE_Gun_MarksmanRifle`). All five are `mandrake.rsw.armoury` (in the save and the candidate list), `relicChance`
  3, not made from stuff. Measured on the canonical save 2026-10-14: no placed relic Thing (`generatedRelic` null),
  zero references to the five `Precept_<ID>` load IDs; the VWE names left in CaravanAdventures filters and VTE price
  history are not relics and stay in the logged noise. Keyed on precept ID, name and old def (`Rifle of Self` is also
  precept 2590, which stays). Idempotent; refuses if the five moved.
- **Accepted as logged noise** (engine or third-party drops, no step): Survival Tools' 3 scenario parts
  (`Scenario.ExposeData` removes null parts with one warning), Beasts of the Rim's 15 `Leather_*` apparel on
  non-player world pawns (`Thing.ExposeData` resets missing stuff to the default stuff with an error), the Warcasket
  Tyrant and the two metal pipes on dead world pawns, 25 lost component classes, research keys, filters, price
  history, work priorities, auto-slaughter rows, Big and Small's two cached Alpha Mechs originals (UNMEASURED,
  third-party).

## 7. W5 acceptance and the expected log

Expected on the first load of the edited save (`Transient/foundry_wave1_save_census_20261010.md`, classified by
message, not counted): `Dialog_ModMismatch` listing the retired ids; roughly **2,000-3,000** logged messages, mostly
`Could not load reference to ... named ...` (one per surviving occurrence in filters, price history, work priorities,
research keys, drug policies, apparel stuff, hediffs) and `Null key while loading dictionary` (def-keyed rows);
about 25 `Could not find class` (lost game/world/map components of Sandworm, ChezhouLib, Raid Fee, Rimesis, Ship
Wall, Survival Tools, Destiny); `Some DrugPolicyEntries were null
after loading`; auto-slaughter warnings; `Some scenario parts were null or invalid after loading`; one `is made from
stuff but has no stuff set` per Beasts-leather apparel (15). The census estimated 3,300-4,300 with Ancient Urban
Ruins removed and passions unmapped; holding AUR removes ~1,230 and W3's passion map removes ~260. All of it is
far below the 10,000-message stop and one re-save clears it. **Anything else is new and stops the wave.**
(The C15 deep dive's "~900-1,100 errors" is the five old donors alone; it is a subset of this.)

Acceptance (each fails while its defect remains):
1. Main menu reached; no `Resetting mods config`; the first exception in `Player.log` is not one of ours and not new.
2. The edited save loads behind the expected `Dialog_ModMismatch`; the founders and the ship are intact
   (`rimworld/list_colonists`: the six colonists, passions now vanilla per §6).
3. `jawa/harmony_patches` lists no `RaidEnemy` prefix owned by `leo.raidprotectionfee`, **and** `jawa/fire_raid` actually
   produces a raid (A4: a missing package is not proof).
4. `jawa/running_mods` equals `manifest.WAVE1.json` (no wave id loaded, `mandrake.rm.pyrinth` loaded).
5. Bones: `Make_ChemfuelFromBone` and `MakeBonePlasteel` absent from the BiofuelRefinery bill list; `MakeBonePlastic` present.
6. Facial Animation on RSW_ xenotypes (owner: "check in game first, then fix"): spawn 2 Jawa and one pawn of each
   other RSW_ humanlike xenotype, verify each pawn's ACTUAL kind/xenotype (a spawn tool can substitute), close
   screenshots into `Transient/`, read face state, propose the shim from the log. Ticket
   `RSW_FACES_VERIFY_IN_GAME_BEFORE_SHIM`.
7. Health (C24): record private bytes / managed memory and TPS over ~1,000 warmed ticks beside the load time and the
   distinct-error count (`measure count-errors`), as the first row of `HEALTH_CHECK_MONITOR_MEMORY_TPS_OVER_TIME`.

## 8. Tickets (filed 2026-10-10, all `--for FOUNDRY`)

| ticket | needs | step |
|---|---|---|
| `WAVE1_FIXES_DEPLOY_BEFORE_THE_CUT` | deploy | W0-W1 |
| `CHERRY_PICKER_RESTORE_FROM_SHIP_PROFILE` | deploy | W2 |
| `WAVE1_MODLIST_RETIRE_37_IN_ONE_LOAD` | bridge | W3-W6 |
| `SAVE_RELIC_PRECEPTS_REPAIR_VWE_NULLS` | offline | built into W3 (owner approved 2026-10-14) |
| `RSW_FACES_VERIFY_IN_GAME_BEFORE_SHIM` | bridge | W5 acceptance 6 |
| `HEALTH_CHECK_MONITOR_MEMORY_TPS_OVER_TIME` | game-up | W5 acceptance 7, then standing (C24) |
| `REMAKE_CARRYOVER_VERIFY_SIX_ITEMS_ONLY` | offline | C25, independent |
| `BONES_LEAN_PORT_BUILD_TREELESS_WORLD` | offline | after the wave |
| `SALVAGE_YIELD_UNIFY_THREE_RULES_TODAY` | offline | replaces Better Cremation's behaviour |
| `SALVAGE_MINIFY_DESIGN_HAULER_OR_SCRAP` | offline | after Minify Everything goes (`convenience_replacements.md` §1.3 e) |

Wave 2 candidates found on the way (not filed): `shavius.medieval.flavour` (one mothballed world pawn),
`xmb.ancienturbanruins.mo` (needs the excision listed in conflict 5), Ideology Virtues after its probe.
