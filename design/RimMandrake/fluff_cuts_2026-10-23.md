# Fluff cuts, 2026-10-23: the veto digest

**Authority:** the owner's question card on `BIOME_MECHANICS_JUDGE_FLUFF_ON_TRIAL`: *"How do you want to rule on the rest? → I cut, you veto (Recommended)"*.
**Source of the opinions:** `design/RimMandrake/special_mechanics_review_2026-10-22.md`. Each "why" below is that row's own opinion.
**Before acting, every row was re-checked against the code.** Rows whose facts had gone stale were skipped and are listed at the end.

Nothing was deployed. Every cut can be restored from git:

- **Code and defs:** `git revert <sha>` undoes the whole commit. To restore one mechanic, use `git checkout <sha>^ -- <paths>` and then rebuild the mod with `python3 src/RimMandrake/Utils/winbuild.py <Mod>`.
- **Art:** it was retired through the art ledger, never deleted outright. Restore it with `python3 src/RimMandrake/Utils/art/art.py install <mod> <rel> <prev-sha> --by-card "…"`. The prev sha is listed per row.

**To veto,** name the block; it gets restored.

---

## Cut

### Pyrelands: furnace-herd world migration (`6693c0e4e`)
- **What:** the furnace herds that travelled between Pyrelands tiles on the world map. Removed:
  - the world object and the seeder;
  - the map-removal patch;
  - the world leg of the thermal-charge comp;
  - the settings `furnaceWorldMigrationEnabled` and `furnaceHerdCount`;
  - the WorldObjectDef.
- **What stays:** the beasts themselves, on their maps. `diag/save_world_check.py` now flags any herd left in a save; the canonical save holds 0.
- **Why:** "cut or table (candidate fluff)".
- **Restore:** `git revert 6693c0e4e`.

### Fever Wood: kurreth theft and the column camp quest (`db3c5416e`; the file deletions landed in `67633f878`)
- **What:** ants that stun thornbugs and carry them off alive, then a column camp quest. Removed `RM_KurrethTheft.cs`, `RM_KurrethColumn.cs`, the KurrethBound hediff, the theft JobDefs, the `RM_Quest_KurrethColumn` QuestScriptDef and the `RM_KurrethColumnCamp` SitePartDef.
- **Why:** "cut or ask: largest piece with no tie to the line, never run".
- ⚠️ **This row's opinion read "cut or ask". It was cut under "I cut, you veto", so veto here if you wanted to be asked.**
- **Restore:** `git checkout 67633f878^ -- src/RimMandrake/FeverWood` (take only the kurreth files), then revert the kurreth hunks of `db3c5416e`.

### Fever Wood: hive parasite chamber (`db3c5416e` and `67633f878`)
- **What:** a hungry glomvar that eats kurreth no one is watching. Removed `RM_CompHiveParasite.cs` and the comp on the race.
- **What stays:** the `RM_Glomvar` race and all its art. Two of its facings are owner-kept.
- **Why:** "cut or merge: flavour inside a feature the line omits".
- **Restore:** `git checkout 67633f878^ -- src/RimMandrake/FeverWood/Source/RM_CompHiveParasite.cs`, plus the race-comp hunk of `db3c5416e`.

### Fever Wood: natural placement scorer (`db3c5416e`)
- **What:** `RM_BiomeWorker_FeverWood` scoring. It is now a −100 stub, and the `naturalPlacementEnabled` setting is gone.
- **Why:** "cut: worldgen is out and the biome is hand-placed".
- **Restore:** the BiomeWorker hunk of `db3c5416e`.
- **Kept on second look:** the brathek tree-eating toggle was restored in `c8e160b7c`. The diet itself is vanilla behaviour; the toggle is its Mod Settings switch.

### Blue Desert: soundscape cut; vhaulk road and cold rack trimmed (`d5bfcd46e`)
- **Soundscape, cut:** `RM_BlueDesertSoundscape.cs`. **Why:** "cut or trim: pure audio at 361 lines".
- **Vhaulk road, trimmed:**
  - Removed: the pressed rime-road terrain (`RM_BlueDesertTerrain.xml`), the flora cropping, the frost and the booms.
  - Kept: the walk-off and its letters.
  - **Why:** "simplify: scenic; keep walk-off letter".
- **Cold rack, trimmed:** the meltwater drip is gone; the rack still keeps a room cold. **Why:** "consider trimming the meltwater drip".
- **Restore:** `git revert d5bfcd46e`.

### Cracked Lands: four cuts, map controls kept (`4e16f20fc`)
- **Fossil display slab and mount.** **Why:** "cut or merge: plain decoration". Art retired (prev shas below).
  - `RM_FossilDisplaySlab.png` prev `f9f746f8bd94`
  - `RM_FossilDisplayMount.png` prev `e983e2ef13d5`
- **Zennaq lightning pull** (the setting and the flora code; the plant's description was edited). **Why:** "cut: nothing in the owner line".
- **Peakstorm dust reversal** (`RM_WeatherOverlay_PeakstormDust.cs`, `RM_DustKernel.cs`). The weather and the flood pull stay. **Why:** "keep the weather and the flood pull; cut the dust-reversal".
- **Recede migrant fliers.** The irqit carpet stays. **Why:** "the migrant flyers add the most test burden … for a flavor beat".
- **Restore:** `git revert 4e16f20fc`.

### Long Shade: the smoke calendar's ash act (`0d2d197ad`)
- **What:** after the haze came an ash growth pulse and a sand-lock. Removed `RM_SmokeCalendar.cs` and its conditions. The haze itself stays, as a plain GameCondition.
- **Why:** "cut: nothing about shade or crossing".
- **Leftover:** the inert reader code is filed as `ASHPULSE_READERS_PRUNE_NOBODY_LEFT`.
- **Restore:** `git revert 0d2d197ad`.

### Gelatinous Slime: two flavour hooks (`13b42445c`)
- **What:** the "Entry recorded" mote and the read-mark smears (`flavorEntryRecorded`, `flavorReadMarks`). The Slime-marked opinion stays.
- **Why:** "keep the opinion, the smear/mote flavour i[s fluff]".
- **Restore:** `git revert 13b42445c`.

### The Forge: floatstone keelwork (`061f5d693`)
- **What:** removed the following:
  - the keel brace ThingDef and its engine-link patch;
  - `RM_ForgeKeelwork.cs`;
  - the settings `keelworkEnabled` and `keelRingEnabled`;
  - the launch-ring sound.
- **Art:** `RM_FloatstoneKeelBrace.png` retired, prev `12d97c9f9fff`.
- **Why:** "simplify or cut: small effect; the only ship hook".
- **Restore:** `git revert 061f5d693`.

### Leaning Scrub: sweetline bark-wardens (`86b7eaaa9`)
- **What:** the guardian roost, its rage, the `RM_Barkwarden` race and five settings. The sweetline tree, its wool and the scratching tree all stay.
- **Art retired:** six `RM_Barkwarden_*` pngs, three per folder.
  - `Animal/RM_Barkwarden`: east `15476dc2033c`, north `f7621c981f8a`, south `4f1ebf4090b1`
  - `Animal/Cougar/RM_Barkwarden`: east `efbba0e12ac9`, north `aa95aea44e87`, south `f798ba1577df`
- **Why:** "simplify: 840 lines of guardians for one rare tree; keep tree, wool and scr[atching]".
- **Restore:** `git revert 86b7eaaa9`.

### Warscar: the tetchik jar (`d28a529cf`)
- **What:** removed:
  - the captured tetchik, the jar and its recipe;
  - the JarCaravans caravan warning;
  - `choirJarWarnings`.
- **What stays:** the Geiger choir's tick and its silence. The jar png is owner-kept, so it was left in place.
- **Why:** "the jar-and-caravan-warning is fluff-adjacent".
- **Restore:** `git revert d28a529cf`.

### Stillsand: five cuts (`36240c2d5`)
- **Dust devils** (`RM_DustDevil.cs`, the ThingDef and the IncidentDef).
  - **Art:** `RM_DustDevil.png` retired, prev `4795b23b0c3c`.
  - **Why:** "cut: no decision, nothing left behind".
- **Gale abrasion and static** (structure wear, roof-edge damage, stuns, building static, and two settings).
  - The gale, carry-and-return, emergence and seeding stay.
  - **Why:** "keep gale and carry-off, cut or trim static/abrasion toggles".
- **Cave drip** (the sound def and `CaveDrip.wav`).
  - **Why:** "keep preservation; drip and wall mark are dressing".
- **Tribal mark on a taken cave.**
  - **Art:** `RM_StillsandTribalMark.png` retired, prev `2758abc10f23`.
  - **Why:** the same row as the drip.
- **Skeleton dune burial** (`RM_SkeletonBurialLogic.cs` and the burial code on the skeleton).
  - The skeletons, bone harps, corpse-to-skeleton, tracks and dune eraser all stay.
  - **Why:** "keep skeletons as landmarks; the burial … tracking is heavy for a read-only effect".
- **Restore:** `git revert 36240c2d5`.

## Simplified

- **Rust Cathedral (`a8b17de93`):** the 20 stage-keyed commentary pools now default to OFF (`stageKeyedCommentaryEnabled`). The pools are kept. **Why:** "hold the 20 stage pools until the arc is decided". **Restore:** flip the default back.
- **Wasteland (`523cb4e45`):** the dead `brineDepositsEnabled` toggle is deleted. **Why:** "fix the dead toggle … or delete the toggle".
- **Terminal Biomes (`56e4207b6`):** the inert `twilightChainAvailability` setting is deleted. **Why:** "wire or delete inert settings".

## Queue items dropped (by card)

| Item | Reason |
|---|---|
| `FURNACE_HERD_DIAGNOSE_ARRIVES_NEVER_LEAVES` | Mechanic cut |
| `KURRETH_LOSS_FINALIZE_1` | Mechanic cut |
| `KURRETH_THEFT_PER_COLUMN_1` | Mechanic cut |
| `DUST_DEVIL_ITEM_LOSS_FIX_1` | Mechanic cut |
| `FORGE_KEELWORK_REMAINDER_1` | Mechanic cut |
| `SCRUB_WARDEN_FIX_TAMED_BOSS_STILL_REIGNS` | Mechanic cut |
| `WEBWORK_EGG_BROKER_CHANNEL_1` | Row W13: "cut — v2, and W2 already sells eggs" |
| `RUSTCATHEDRAL_LIVINGBOLT_WALL_FLIT_1` | Row #6: "do not build a wall-movement system" |

These items got notes instead of being dropped:

- `STILLSAND_DUNE_GALE_LIVE_1`
- `STILLSAND_CAVE_AS_PLACE_1`
- `STILLSAND_SKELETONS_REMAINDER_1`
- `CATHEDRAL_STAGE_COMMENTARY_POOLS_1`
- `BLUEDESERT_MECHANICS_BUILD_1`
- `BIOME_MECHANICS_JUDGE_FLUFF_ON_TRIAL`

## North-star text corrected, offered for validation

- `design/validation_walks/RimMandrake/BlueDesert.md` named the pressed rime road (cut above) in three places: the status hint, the def list in `## must be true`, and the visual question "does the rime road read as pressed ice" in `## north star`. All three were removed on 2026-11-02 (`FLUFF_ASKS_DECIDE_EIGHT_UNDER_VETO`). The north star was `DRAFT` with no validated hash, so no validation was broken. **It is offered to him for validation as it now reads:** his experience line and two visual questions, the krissek's halo as blue fire and the flora as transparent.

## Decided 2026-11-02 under "I cut, you veto" (the eight rows that asked him)

These rows were decided by the agent under his card rather than asked (`FLUFF_ASKS_DECIDE_EIGHT_UNDER_VETO`). **To veto,** name the row.

### Cut

- **Lantern Deeps #12, the blinker's flash** (`3f4593400`). **What:** removed the flash-and-dazzle comp (`RM_CompFlashOnHurt`), the `RM_BlinkerFlare` light, the `RM_BlinkerDazzled` hediff, the `blinkerFlashEnabled` setting, the `ProofBlinker` proof and its validation component. **What stays:** the blinker itself, as a plain animal with its art and roster weight; the slick and the knocker. **Why:** the row's opinion was "keep knocker, ask on slick and blinker", and the blinker "barely" changes a player decision. **Restore:** `git revert 3f4593400`, then rebuild with `python3 src/RimMandrake/Utils/winbuild.py LanternDeeps`.
- **Miasma #M12, the mangal pollination gate** (`66fc3c2b1`). **What:** removed the `RM_PollinationGateExtension` from `RM_Thessamor` and `RM_Quennath`, the shared `RM_PollinationGatePatch` and extension class in EnvironmentalHazards, and both settings that switched it (`pollinationGateEnabled` in Miasma and in EnvironmentalHazards). **What stays:** the plant predators eating scuttlers, the karrobel composting into delta loam, and the fever swarm. **Why:** the row's own reason, "ecology gates that are invisible to the player". Of the three, the gate is the one a player cannot see; the other two leave things he can see. **Restore:** `git revert 66fc3c2b1`, then rebuild EnvironmentalHazards and Miasma.

### Kept

- **Abyss #6, Etchfall.** It is the biome's one pressure that changes what you build ("roof everything"), the etchcap fungus and tholin chemfuel depend on it, and it is the "staying too long wears at you" half of his line.
- **Fever Wood #10 and #11, the kurreth hive and its sealing.** The hive is the map's one "how deep do I go" place, and items 6, 12 and 13 depend on it. The sealing is 117 lines and makes a retreat-route decision inside it. With the kurreth theft and the column camp already cut, the hive is what is left of the kurreth.
- **Lantern Deeps #12, the slick.** A fuel trail that a spark runs like a fuse is a real decision: keep fire away from where slicks walk. Its live check is still red (`slick_lays_fuel` FAIL, 2026-10-05). That is owed proof, not a reason to cut it.
- **Miasma #M6, warden mother succession.** His line is "a nursery … every surge brings orphans", and her young succeeding her is that nursery's long game. M4 (mother's price, "the clearest decision in the biome") voids succession, so cutting M6 would hollow M4.
- **The Rot #R3, swallowed ship core.** He already engaged with it: his card of 2026-10-22 on its campaign tiles was "wait for the paint". It is the "generous" half of his line, because it gives you sites.
- **Wasteland #7, gripper theft.** Built and proven (the gripper chain passed 7 of 7 on 2026-10-08), with no live check owed. Cutting it saves no test burden.

### Moved out of scope

- **Wasteland #11, Throat Cask.** It stays as built, but it is no longer counted as Wasteland content. It ships in the RimUtinni companion `src/RimUtinni/WasteRun` as campaign content, and the Wasteland walk does not cite it. **Correction:** this digest said `STENCHLANDS_THROAT_CASK_1` awaited him. That was wrong: the item is done, closed at `f6a8a6016`.

## Rites, already v2 per `design/RimMandrake/v2_nine_rituals.md` (left untouched)

- Nightside Ice #10 (Cold Ledger)
- Warscar #17 (Open Boast)
- Weeping Stones #11 (Refused Toll)
- Webwork W12 (Felled Noon)
- Pyrelands #15 (shovel; its only consumer is a rite)

## Skipped: the row was stale or wrong, or a standing ruling covers it

- **Greentide #12, stench grenade:** the row says "depends on none", which is wrong. The grenade is the only caller of `RM_ReactionSuppression` and is the ruled one tool for the biome's animals.
- **Greentide #13, canopy swarm:** stale. The Krannock is now rostered.
- **Cross-biome settings (Greentide #3, Warscar #18, F7 `crossBiome*`):** standing ruling (owner 2026-10-15): existing cross-biome switches stay, off and labelled.
- **Cracked Lands #14, map controls:** the FlowWorks review map uses them (`PlaceFloodTrigger`).
- **Gelatinous Slime #12, pit solvent:** stale. The ambrosyx source plant is now built.
- **Gelatinous Slime #15 (fubbum), Fever Wood #16 (brathek), Leaning Scrub #7 (vissler arm):** the behaviour is vanilla. The only code is its Mod Settings switch, which the settings rule keeps. Dwommo flight stays under the flyers-fly ruling.
- **Long Shade #14, heat soundscape:** the opinion was "cut or leave as is", and it was left. The code is the shared CreatureBehaviors `RM_HeatSoundscape.cs`, and the lit/shade bed was the owner's card note.
- **Rust Cathedral #15, overhead-sun heat:** the Direct Sun unification retires it for every biome at once. The strays are kept.
- **Rust Cathedral #16, roach:** a no-op; there was no mechanic work open.
- **Stillsand #16, Sun-Debt water ledger:** Utinni's `RUT_TheReturn` uses it, and a peer was mid-edit.
- **Stillsand #3, track eraser:** it is the Stillsand half of the shared footprint grid.
- **Sump S4, capstan merge (and S13 with it):** the capstan is the research prerequisite of the salvage winch, so the merge is a redesign.
- **Wasteland #13, wreck set:** already the generic Wreckage scatter.
- **Webwork W3, egg bounty:** S6 ruling 2 keeps the legal bounty separate from the black market.
- **Webwork W11, webfall:** the row is wrong that it has no play effect (it gives accuracy ×0.85), and the owner said *"Webfall weather is cool."*
- **Weeping Stones #7, dewsilk:** it is the biome's signature trade good, per the ruled sheet.
- **Every other "simplify" row with no concrete target** (e.g. "consider trimming", "finish rendering or stop") was skipped.

## Loose ends

- **Owner-kept art left in place:** `RM_Glomvar` (two facings are kept; east was retired by mistake and reinstalled) and the tetchik jar png.
- **Code not yet reviewed clean** (`code_review_status.py check`):
  - large files: `RM_WarscarMod.cs`, `RM_TerminalBiomesMod.cs`, `RM_DuneGale.cs`, `RM_GiantSkeletons.cs`, `RM_PreciousCaves.cs`, `RM_StillsandMod.cs`, the Fever Wood ant-hive GenStep;
  - each touched mod's `validation.py`, selftest and fuzz files.
- **A pre-existing failure, not caused by these cuts:** the Scarlands validation static check fails on the texture `RM_GlowerCrust_a`.
