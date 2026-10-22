# World remake: the mods to reinstate, and how

> 🔒 **PRESERVED FILE. Do not delete, cull or "tidy" it.** The owner asked for it to be kept for the day the world is remade.
> Correct a row that turns out wrong (CLAUDE.md: delete wrong content, don't supersede it), but keep the file.

Owner, 2026-10-21: *"Please make a careful note of the mods we would have to reinstate if we remade the world again and keep
that in a specially preserved file with instructions."*

**What a "remake" means here.** Re-creating Ash'karr from scratch: a new Create World pass at 21,872 tiles, then the paint
stamped back on with `w9_run.py`, then the start save (the procedure in
`design/RimMandrake/world_remake_2026-10-19/06_remake_runbook.md`). It is **not** a small repaint inside an existing world, and
it is **never** a different planet (CLAUDE.md: one hand-made world; no alternative planets). Players never do this; they
receive the save.

**Machine-readable copy:** `infrastructure/state/modlists/world_remake_reinstate.txt`
(`packageId<TAB>name<TAB>class<TAB>why`; 442 retired rows + 24 active-but-not-SHIP rows, `#` header lines).

**How this was established (FOUNDRY, 2026-10-21, offline; no game, no ModsConfig written).**
- Every retired row of `design/RimMandrake/mod_archive/ALL_ORIGINAL_MODS.tsv` (parsed with `csv`: 766 rows; 442 retired =
  222 earlier + 46 W1 + 118 W2 + 6 W3 + 50 W4; 324 active), checked against the five `*.RULED_2026-10-20.xml` profiles
  (parsed with ElementTree: PAINT 83, AUTHORING 171, DEV 117, TEST 152, SHIP 277) and `ModsConfig.FULL.LATEST.xml` (325).
- The decisive evidence is a **measured remake**: on 2026-10-20 a development world was created end to end (S2-S14) on
  **`ModsConfig.PAINT.RULED_2026-10-20.xml`** (83 mods): 21,872 tiles, TidallyLocked, every paint layer stamped, cold reload
  PASS (`06_remake_runbook.md` line 76 and gates G2, G12, G13, G15). Its paint bundle `world/paint_inputs_2026-10-20/`
  resolves with **0 unresolved names** against the PAINT def closure (`RESOLVER.md`). So: a retired mod that is not on PAINT and
  that no paint input names was not needed to make the world.
- Wave 4 (2026-10-20) then cut one PAINT mod, My Little Planet, as "world-creation only" — that is the one mod a remake
  needs back. Everything else is conditional on an owner choice and is listed with its condition.
- The original world (2026-08-21) was generated on a 578-mod list (`ModsConfig.FULL.20260821_WITH_factioncontrol.xml`).
  Its world-creation mods are each accounted for below (needed, still active, or retired with a cited reason).

## Counts

| class | retired mods | meaning |
|---|---:|---|
| **NEEDED-FOR-REMAKE** | **1** | must be back on the list before Create World |
| **MAYBE** | **7** | needed only if the owner chooses the stated option |
| **UNMEASURED** | **2** | a link exists by name only; nobody has measured whether the mod supplies it |
| NOT-NEEDED | 432 | 14 world-related ones are justified one by one below; the other 418 by the PAINT-run rule above |

Active mods (still installed, in `FULL.LATEST`) that are **not in SHIP** but are on PAINT/AUTHORING/DEV: **24** —
3 required for a remake, 11 optional authoring tools, 10 instruments. A further 24 active mods are in FULL only (no ruled
profile); none is a world-creation mod except Geological Landforms (see Traps).

---

## How to use this file — reinstating for a remake, step by step

Everything below happens **with the game DOWN** unless a step says otherwise. Read `06_remake_runbook.md` first; this file
only covers the mod list. Hold the bridge (`rimflow bridge take --for "world remake"`) for the whole sitting.

1. **Confirm the owner has ruled a remake.** `WORLD_REDRAFT.md` (owner 2026-08-21): *"Nobody schedules a remake to 'test'
   something."* Every remake spends the irreversible Configure Factions pass. No ruling, no remake.
2. **Decide the MAYBE rows with him first** (one question card): (a) carry Dungeon Pack's two hidden factions? (b) rings on?
   (c) original `The Salvation.rid` or the PAINT-clean one? Each "yes" adds that row's mods. Default = no.
3. **Base list = `infrastructure/state/modlists/ModsConfig.PAINT.RULED_2026-10-20.xml`** — the only list a remake has been
   measured on. It **already contains** the NEEDED mod (`oblitus.mylittleplanet`, position 30 of 83, after
   `zylle.morevanillabiomes`) and the three required active mods. Do not base a remake on SHIP (it lacks the
   bridge) or on FULL.LATEST (325 mods, includes Deep Orbit and every class-E mod; never measured for a remake).
   - If PAINT has since been edited and lost a row, re-insert it from the tables below (`<li>packageId</li>`, after the named
     predecessor), then parse back: `python3 -c "import xml.etree.ElementTree as E,sys;a=[l.text for l in E.parse(sys.argv[1]).find('activeMods')];print(len(a),len(set(a)))" <file>`
     (count and distinct count must match; never `grep -c '<li>'`).
   - For each MAYBE the owner said yes to: insert it into a **copy** of PAINT (e.g. `ModsConfig.PAINT.REMAKE_<date>.xml`),
     after its predecessor's position in FULL.LATEST order; for an ideo mod also add its active dependants listed under
     "Ideoligion mods that are active but not on PAINT" below. Parse back.
4. **Check every folder exists** before swapping: each row's `workshop_id` under
   `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\<id>` (all present 2026-10-21), and that its
   `About\About.xml` `<packageId>` matches (compare lowercased). A missing folder is a Steam resubscribe — the owner's
   action — and RimWorld silently drops an id it cannot find. Our own mods: `python3 src/RimMandrake/Utils/deploy_custom_mods.py`
   (plan; `--apply` only after reading it).
5. **Checkpoints, then install the list.** `python3 src/RimMandrake/Utils/remake/checkpoint.py make --ids C1,C2,C3`
   (Saves folder, live ModsConfig, mod settings). Then copy the chosen list file over the live
   `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Config\ModsConfig.xml` (game down; RimSort
   closed). `modset_builder.py` and `modlist_swap.py` have **no "install this file" mode** (`15_conductor_plan.md` line 53);
   an atomic copy is the route. Verify with gate G2's one-liner (`06_remake_runbook.md` line 88): count and sorted sha equal
   the file's.
6. **Cherry Picker:** `python3 src/RimMandrake/Utils/cherrypicker_swap.py --status` (gate G4). A reinstated Wave-4 mod's
   cut keys are in `infrastructure/state/cherrypicker/cp_wave4_keys_24.txt`; only matters if that mod is in the list.
7. **Launch, then set the planet before generating** (game UP): `python3 src/RimMandrake/Utils/remake/set_planet_type.py --check`
   (Alien Worlds must read TidallyLocked; with no settings file it silently makes a vanilla planet). Player.log must show
   PlanetPresetPrime `ready: coverage 1, subdivisions 7, MLP slider primed` — "ABSENT" means My Little Planet did not load:
   **stop**, do not generate.
8. **Run the runbook** S4-S15. Stamp from the bundle, never the record:
   `python.exe src/RimMandrake/Utils/w9_run.py --inputs world/paint_inputs_2026-10-20` (dry run), then `--apply`
   (or a newer `world/paint_inputs_<date>/` rebuilt by `python3 src/RimMandrake/Utils/paint_inputs_build.py`).
   `w9_run.py` refuses a world whose tile count is not 21,872.
9. **Verify:** tile count 21,872; `alienWorldsFrameworkPlanetType` = TidallyLocked in the save; roster per G15 and
   `python3 src/RimMandrake/Utils/banned_factions.py check-save <save>` PASS; the three censuses of G11
   (`save_class_census.py`, `save_def_census.py`, `save_adoption_check.py`); the owner's LOOK (G14).
10. **Afterwards:** restore the working list (checkpoint C2, game down). Record any mod you reinstated in the archive:
    `python3 src/RimMandrake/Utils/mod_archive.py add <packageId> --lifecycle ACTIVE-... --date <date> --doc design/RimMandrake/world_remake_reinstate_list.md --reason "..."`,
    then `python3 src/RimMandrake/Utils/mod_archive.py check`. Correct this file if anything here proved wrong.

**Do NOT:**
- edit the live `ModsConfig.xml` with the game up (the game rewrites it on exit; the edit is lost) or while RimSort is open;
- run `modcheck run <Mod>` during the sitting — it rewrites the live ModsConfig;
- stamp `world/ASHKARR_WORLDMAP_*.csv` (the frozen RECORD, w9_run's default inputs): it carries pre-port donor names
  (`AB_*`, `sw_*`, pre-rename biomes) that need retired mods, and an 08-23 road/mutator lineage;
- reinstate Alpha Biomes or any donor to make an old name resolve — port the name (`retired_mutators_port_map.json`);
- burn a generation "to test" (owner 2026-08-21), or build anything that could roll a second planet (owner 2026-08-18);
- `--restore-full` blind, or restore from an older `ModsConfig.FULL.*` (they predate the renames and the waves).

---

## 1. Retired mods a remake needs (NEEDED, MAYBE, UNMEASURED)

`predecessor` = where the mod sat in the last full list that held it (line number in that file) and the nearest earlier
entry still present in today's `ModsConfig.FULL.LATEST.xml`, which is where to insert it. In PAINT, insert after the same
neighbour if present, else in About.xml `loadAfter` order. `state` measured 2026-10-21.

| class | packageId | name | workshop_id | why (citation) | predecessor | state |
|---|---|---|---|---|---|---|
| NEEDED-FOR-REMAKE | `oblitus.mylittleplanet` | My Little Planet | 1117406550 | Planet SIZE. Ash'karr is 21,872 tiles = coverage 1.0 at subdivisions 7; the only route ever measured to that count is PlanetPresetPrime priming My Little Planet's slider (PlanetPresetPrime.cs:87-103: MLP's transpiler re-stamps its own default 10 every frame unless primed); 2026-10-20 dev remake on PAINT 83 got 21,872 tiles with 'MLP slider primed' (06_remake_runbook.md:58,76). Wave 4 cut it as world-creation-only and kept it on PAINT+AUTHORING for the final repaint (retirement_register_wave4_2026-10-20.md:38,142). Without MLP, PlanetPresetPrime sets vanilla subdivisions only: never run, UNMEASURED. | `ModsConfig.FULL.PRE_WAVE4_374.xml` line 162, after `snobi.mutatorworldicons`; insert after `snobi.mutatorworldicons` in today's FULL.LATEST | RETIRED-WAVE4; folder present; not in FULL.LATEST; on PAINT.RULED |
| MAYBE | `avius.prisonlabor` | Prison Labor | 1899474310 | Only if the remake loads the ORIGINAL player ideo `src/Jawa/ideoligion/The Salvation.rid` at S5 with every element intact: ritual prisoner interrogation [PL_Interrogation] (removed.md:33). The PAINT-clean variant needs none of it (06_remake_runbook.md:60). Cut in Wave 4. | `ModsConfig.FULL.PRE_WAVE4_374.xml` line 300, after `mehni.pickupandhaul`; insert after `mehni.pickupandhaul` in today's FULL.LATEST | RETIRED-WAVE4; folder present; not in FULL.LATEST |
| MAYBE | `lovelydovey.recreation.witheuterpe` | Intimacy - Socio Butterfly | 3630896210 | Only if the remake loads the ORIGINAL player ideo `src/Jawa/ideoligion/The Salvation.rid` at S5 with every element intact: precept divorce [SEX_Divorce_Accepted] (removed.md:52). The PAINT-clean variant needs none of it (06_remake_runbook.md:60). Cut in Wave 4. | `ModsConfig.FULL.PRE_WAVE4_374.xml` line 328, after `lovelydovey.sex.withrosaline`; insert after `lovelydovey.sex.withrosaline` in today's FULL.LATEST | RETIRED-WAVE4; folder present; not in FULL.LATEST |
| MAYBE | `mlie.dungeonpack` | Dungeon Pack (Continued) | 3765496911 | Only if the remade world must carry the 09-12 world's hidden factions TribalHostile and DP_GenericHostile (world/rescue_2026-10-19/ported/world_info.json factions). paint_inputs_remap.json factions_drop drops both PROVISIONAL ('mlie.dungeonpack not on PAINT; no settlement uses it'); world/paint_inputs_2026-10-20/README.md:36 says to reverse: remove from factions_drop and add the mod to PAINT. Cut in Wave 4 (register row 26). | `ModsConfig.FULL.PRE_WAVE4_374.xml` line 271, after `neronix17.retexture.charactereditor`; insert after `neronix17.retexture.charactereditor` in today's FULL.LATEST | RETIRED-WAVE4; folder present; not in FULL.LATEST |
| MAYBE | `mlie.preceptsandmemesritualsmodule` | Precepts and Memes - Rituals module (Continued) | 2894628849 | Only if the remake loads the ORIGINAL player ideo `src/Jawa/ideoligion/The Salvation.rid` at S5 with every element intact: ritual Wealthy Records [QuarterlyReport] (removed.md:19). The PAINT-clean variant needs none of it (06_remake_runbook.md:60). Cut in Wave 4. | `ModsConfig.FULL.PRE_WAVE4_374.xml` line 282, after `mandrake.rm.planetpresetprime`; insert after `mandrake.rm.planetpresetprime` in today's FULL.LATEST | RETIRED-WAVE4; folder present; not in FULL.LATEST |
| MAYBE | `rwnodetree.rwplanetatmosphere` | RW - Planet Atmosphere | 3272330410 | Planet rings / atmosphere on the world view. On the list when Ash'karr was first generated (ModsConfig.FULL.20260821_WITH_factioncontrol.xml). Owner 2026-10-20: 'I would also like to add back the Rings when we bring back the larger mod list' (infrastructure/state/modlists/README.md:45-48); already back in FULL.LATEST, not on PAINT/SHIP. Needed at the remake only if the owner wants the rings on during the globe LOOK (S9); whether it writes anything into a world save is UNMEASURED. | `ModsConfig.FULL.WAVE1_498_2026-10-19.xml` line 252, after `mandrake.rut.empirepursuit`; insert after `mandrake.rut.empirepursuit` in today's FULL.LATEST | RETIRED-WAVE2; folder present; in FULL.LATEST |
| MAYBE | `telardo.romanceontherim` | Romance On The Rim | 2654432921 | Only if the remake loads the ORIGINAL player ideo `src/Jawa/ideoligion/The Salvation.rid` at S5 with every element intact: ritual wedding ceremony [RotR_Precept_WeddingCeremony] (removed.md:34). The PAINT-clean variant needs none of it (06_remake_runbook.md:60). Cut in Wave 4. | `ModsConfig.FULL.PRE_WAVE4_374.xml` line 288, after `co.uk.epicguru.factionloadout`; insert after `co.uk.epicguru.factionloadout` in today's FULL.LATEST | RETIRED-WAVE4; folder present; not in FULL.LATEST |
| MAYBE | `thesepeople.ritualattachableoutcomes` | Custom Ritual Framework | 2561617361 | Only if the remake loads the ORIGINAL player ideo `src/Jawa/ideoligion/The Salvation.rid` at S5 with every element intact: ritual outcomes CallRain/GamblersPrayer + QuarterlyReport worker class (removed.md:19,22,25). The PAINT-clean variant needs none of it (06_remake_runbook.md:60). Cut in Wave 4. | `ModsConfig.FULL.PRE_WAVE4_374.xml` line 18, after `aoba.framework`; insert after `aoba.framework` in today's FULL.LATEST | RETIRED-WAVE4; folder present; not in FULL.LATEST |
| UNMEASURED | `kxp.ideosymbolsasideograms` | Ideology symbols as Ideograms | 3199358915 | The Salvation.rid names KxPDefaultStyleBase / KxPSpikeyE (removed.md:62), which 'resolves in no dump (dangling everywhere)'. The link from that name to this mod is by prefix only; whether reinstating it restores the reference is UNMEASURED. Matters only for the original .rid. | `ModsConfig.FULL.WAVE1_498_2026-10-19.xml` line 147, after `amegakull.scvrole`; insert after `amegakull.scvrole` in today's FULL.LATEST | RETIRED-WAVE2; folder present; not in FULL.LATEST |
| UNMEASURED | `sinnamon.moreritualrewards` | More Ritual Rewards | 2582489076 | The Salvation.rid names Sinnamon_Raincalling (removed.md:18), which 'resolves in no dump (dangling everywhere)'. The link from that name to this mod is by prefix only; whether reinstating it restores the reference is UNMEASURED. Matters only for the original .rid. | `ModsConfig.FULL.WAVE1_498_2026-10-19.xml` line 373, after `mandrake.rsw.cuisine`; insert after `mandrake.rsw.cuisine` in today's FULL.LATEST | RETIRED-WAVE2; folder present; not in FULL.LATEST |

`removed.md` = `src/Jawa/ideoligion/The Salvation (PAINT-clean).removed.md`. `register` =
`design/RimMandrake/retirement_register_wave4_2026-10-20.md`.

**Ideoligion mods that are active but not on PAINT** (needed beside the MAYBE ideo rows only if the original
`The Salvation.rid` is loaded; all in FULL.LATEST, per `removed.md`): `vanillaexpanded.vmemese`, `mlie.preceptsandmemes`,
`llunak.moreprecepts`, `toastyman.moreritualseats`, `vanillaexpanded.vgeneticse`, `divinederivative.romance`,
`oskarpotocki.vanillavehiclesexpanded`, `amegakull.scvrole`. On 2026-10-20 the original .rid loaded on PAINT with 246/251
refs resolving and PostLoadInit NREs from its off-PAINT rituals (06 G12); the PAINT-clean variant avoids them.

**ModsConfig-ready snippet** (the NEEDED row; parsed back with ElementTree: `['oblitus.mylittleplanet']`). PAINT.RULED
already holds it; this is for a list that lost it:

```xml
<activeMods>
  <li>oblitus.mylittleplanet</li>
</activeMods>
```

No full remake ModsConfig is shipped here on purpose: the base is the existing PAINT file, and the MAYBE rows are the
owner's choice at the sitting.

## 2. Retired world-creation mods that are NOT needed, and why

Each of these touched world creation or the original world's content; each is ruled out with a citation. The other 418
retired mods are NOT-NEEDED by the PAINT-run rule (header); their rows are in the `.txt`.

| packageId | name | workshop_id | lifecycle | why not needed (citation) |
|---|---|---|---|---|
| `boots.sensiblefactions` | Sensible Factions | 3531306011 | RETIRED-WAVE3 | On the 08-21 creation list (faction placer), but owner card 2026-10-19 row 6: 'If we don't need it, drop it permanently' (13_owner_rulings_2026-10-19.md:12; 11_ruled_keepcut.md:18); the 2026-10-20 remake roster passed G15 without it (06_remake_runbook.md:101). |
| `grimterra.worldmap` | GRimTerra World Map | 3546956014 | RETIRED-EARLIER | World-map texture cosmetics; cut by owner card 2026-10-10 (commit 9769149ae). No world data. |
| `iforgotmysocks.caravanadventures` | Caravan Adventures | 2558957509 | RETIRED-WAVE4 | Supplied CASacrilegHunters; owner 2026-10-20: 'We don't want those' (register:45); def banished in FactionSlate. |
| `mandrake.ashkarrlandmarkart` | UNKNOWN | - | RETIRED-EARLIER | Old id of `mandrake.rut.ashkarrlandmarkart` (rename 0fda62c94), which is active and on PAINT. |
| `mandrake.jawafactionslate` | UNKNOWN | - | RETIRED-EARLIER | Old id; renamed `mandrake.rut.factionslate` (0fda62c94) then folded into UtinniPatches (485380d4c); `mandrake.rut.patches` is on PAINT. |
| `mandrake.planetpresetprime` | UNKNOWN | - | RETIRED-EARLIER | Old id of `mandrake.rm.planetpresetprime` (rename 0fda62c94), which is active and on PAINT. |
| `mandrake.rut.factionslate` | UNKNOWN | - | RETIRED-EARLIER | Folded into UtinniPatches (485380d4c); `mandrake.rut.patches` is on PAINT. |
| `mlie.choosebiomecommonality` | Choose Biome Commonality | 2582875043 | RETIRED-EARLIER | Generation-time biome weights only; w9_run stage 1 overwrites the biome of all 21,872 tiles (02_world_pipeline.md:75; 2026-10-20 run stage 1 21,872 applied, 06_remake_runbook.md:76). Its slider keys in the save are inert (06 G10). |
| `noxilie.regrow.wmb.advancedbiomes` | ReGrowth 2 World Map Beautification for Advanced Biomes (Continued) | 3564679844 | RETIRED-EARLIER | World-map texture cosmetics for a donor biome set; retired with it. No world data. |
| `noxilie.regrow.wmb.alphabiomes` | ReGrowth 2 World Map Beautification for Alpha Biomes | 3564679302 | RETIRED-EARLIER | World-map texture cosmetics for a donor biome set; retired with it. No world data. |
| `noxilie.regrow.wmb.morevanillabiomes` | ReGrowth 2 World Map Beautification for More Vanilla Biomes | 3564679624 | RETIRED-EARLIER | World-map texture cosmetics for a donor biome set. No world data. |
| `sarg.alphabiomes` | Alpha Biomes | 1841354677 | RETIRED-EARLIER | Supplied the AB_ biomes/mutators/landmarks of the original world. All ported or defaulted in the paint bundle (retired_mutators_port_map.json; world/paint_inputs_2026-10-20/RESOLVER.md 0 unresolved). Owner: reproduce, then deprecate the donors. |
| `thereallemon.factioncontrol` | Faction Control (1.4-1.6) | 2882785581 | RETIRED-EARLIER | On the 08-21 creation list, removed the same day: owner 'I was wrong. We should remove the Faction Control mod.' (commit f1eb572fe). Faction counts come from the 1.6 Create World page + FactionSlate (06 G15). |
| `zal.worldmapenhanced` | World Map Enhanced (Continued) | 3599967849 | RETIRED-EARLIER | World-map texture cosmetics; cut by owner card 2026-10-10 (commit 9769149ae). No world data. |

## 3. Active mods that are not in SHIP but a remake uses

Still installed and in `FULL.LATEST`; they leave the player list at release (C04, dev tooling). For a remake they must be
in the list you install. **REQUIRED** ones are already on PAINT; **OPTIONAL** ones are AUTHORING tools to add to the PAINT
copy only if that step is wanted (each adds load time and was not on the measured run).

| class | packageId | name | workshop_id | ruled profiles | role in a remake | folder |
|---|---|---|---|---|---|---|
| ACTIVE-REENABLE-REQUIRED | `7f.alienworlds` | Alien Worlds Framework | 3626210061 | PAINT,AUTHORING | Tidal lock. Planet type TidallyLocked is set at generation (06_remake_runbook.md:58 Alien Worlds default-planet trap) and the mod patches the sun every session (register:33). On PAINT. | folder present |
| ACTIVE-REENABLE-REQUIRED | `7f.alienworlds.tidallylocked` | Alien Worlds - Tidally Locked | 3631364335 | PAINT,AUTHORING | The TidallyLocked planet type itself (register:33). On PAINT. | folder present |
| ACTIVE-REENABLE-REQUIRED | `brrainz.rimbridgeserver` | RimBridgeServer | 3727949765 | PAINT,AUTHORING,DEV | The bridge: w9_run.py stamps every layer through it (02_world_pipeline.md:75). On PAINT; never ships. | folder present |
| ACTIVE-REENABLE-OPTIONAL | `alleykat.persistentprecepts` | Persistent Precepts | 2944765939 | AUTHORING | Ideoligion editing aid for S5 (C04). | folder present |
| ACTIVE-REENABLE-OPTIONAL | `azravos.factioncustomizer` | Faction Customizer | 3336572602 | AUTHORING | Faction editor at Configure Factions (C04); its config is empty (TSV). | folder present |
| ACTIVE-REENABLE-OPTIONAL | `ferny.worldbuilder` | Worldbuilder | 3522102833 | AUTHORING | Not needed on the 2026-10-20 route (stage 6 used Core `Desert`, 06_remake_runbook.md:32-37). Needed only to restore `WB_MapLabelFeature` region labels (paint_inputs README:37) or the Worldbuilder preset route (`set_planet_subcount.py`). | folder present |
| ACTIVE-REENABLE-OPTIONAL | `funkyshit.mods.worldedit.alpha` | WorldEdit 2.0 | 3590928058 | AUTHORING | Hand-editing tiles in game (08_wave2_prep.md:181). | folder present |
| ACTIVE-REENABLE-OPTIONAL | `hali.modifylandingtile` | Modify Tiles at Game Start | 3667490447 | AUTHORING | Landing-tile editor at S10 (C04). | folder present |
| ACTIVE-REENABLE-OPTIONAL | `m00nl1ght.mappreview` | Map Preview | 2800857642 | AUTHORING | Landing preview at S10 (C04 authoring tool). | folder present |
| ACTIVE-REENABLE-OPTIONAL | `m00nl1ght.unofficialupdates.preparelanding` | Prepare Landing (Continued) | 3221125358 | AUTHORING | Tile picker at S10 (C04). | folder present |
| ACTIVE-REENABLE-OPTIONAL | `neronix17.retexture.charactereditor` | Character Editor Retextured | 2855844396 | AUTHORING | Goes with Character Editor. | folder present |
| ACTIVE-REENABLE-OPTIONAL | `plusblankplus.scenarioamenderfork` | Scenario Amender [1.6 Fixed] | 3761028060 | AUTHORING | Scenario edits on a live save (C04). | folder present |
| ACTIVE-REENABLE-OPTIONAL | `snobi.mutatorworldicons` | MutatorWorldIcons | 3551904193 | AUTHORING | Shows mutator icons on the globe for the S9 LOOK (C04). | folder present |
| ACTIVE-REENABLE-OPTIONAL | `void.charactereditor` | Character Editor | 1874644848 | AUTHORING | Pawn editing for founders/S11b (C04). | folder present |
| ACTIVE-NOT-FOR-REMAKE | `aleksey.betterstacktraces` | Better Stacktraces | 3541579129 | AUTHORING,DEV | Dev/test instrument or authoring aid; no role in world creation found (TSV reason: log instrument: proof_all.py parses its [Ref] lines). | folder present |
| ACTIVE-NOT-FOR-REMAKE | `co.uk.epicguru.factionloadout` | Rimsential - Total Control: Continued | 3063465133 | AUTHORING | Dev/test instrument or authoring aid; no role in world creation found (TSV reason: pawnkind-gear editor; prime suspect for apparel bypass (SpeciesStartingGear_Tuning.xml:37)). | folder present |
| ACTIVE-NOT-FOR-REMAKE | `co.uk.epicguru.whatsthatmod` | What's That Mod | 2258431182 | AUTHORING | Dev/test instrument or authoring aid; no role in world creation found (TSV reason: mod-source tooltip; manual dev aid only). | folder present |
| ACTIVE-NOT-FOR-REMAKE | `lordfelix.rimcontrol` | Rim Control | 3774299554 | AUTHORING | Dev/test instrument or authoring aid; no role in world creation found (TSV reason: owner-adopted tuning tool; its override config is EMPTY (MEASURED), so leaving loses nothing). | folder present |
| ACTIVE-NOT-FOR-REMAKE | `madeline.modmismatchformatter` | Better ModMismatch Window | 1872244972 | AUTHORING | Dev/test instrument or authoring aid; no role in world creation found (TSV reason: mismatch-dialog formatter; no consumer in our tooling). | folder present |
| ACTIVE-NOT-FOR-REMAKE | `mandrake.rm.loadtracer` | Load Tracer (local) | - | AUTHORING,DEV | Dev/test instrument or authoring aid; no role in world creation found (TSV reason: our load-stall diagnostic; not player content). | no workshop id (local/ours) |
| ACTIVE-NOT-FOR-REMAKE | `mandrake.rm.rimdefdump` | RimDefDump (local tooling) | - | AUTHORING,DEV | Dev/test instrument or authoring aid; no role in world creation found (TSV reason: our def-dump instrument; not player content). | no workshop id (local/ours) |
| ACTIVE-NOT-FOR-REMAKE | `mandrake.rut.birthhatchdemo` | RimMandrake: Utinni — Birth & Hatch Demo | - | AUTHORING | Dev/test instrument or authoring aid; no role in world creation found (TSV reason: our DEMONSTRATION mod (About.xml), not campaign content). | no workshop id (local/ours) |
| ACTIVE-NOT-FOR-REMAKE | `mlie.incidentdisabler` | Incident Disabler (Continued) | 3574116665 | AUTHORING,DEV | Dev/test instrument or authoring aid; no role in world creation found (TSV reason: evaluation aid: silences incidents in tests). | folder present |
| ACTIVE-NOT-FOR-REMAKE | `mlie.logafterdeferror` | Log After Def Error (Continued) | 3550944748 | AUTHORING,DEV | Dev/test instrument or authoring aid; no role in world creation found (TSV reason: log instrument: harvest_log.py parses its manifest). | folder present |

## 4. Traps

1. **Load order.** Insert after the predecessor named in section 1, never at the end: our mods are pinned last and must
   keep the final word (`modset_builder.py` ordering note; `rimworld-start-prep` skill). Line numbers are in
   `ModsConfig.FULL.PRE_WAVE4_374.xml` (Wave 4 rows) and `ModsConfig.FULL.WAVE1_498_2026-10-19.xml` (Wave 2 rows).
   `mandrake.rm.planetpresetprime` names My Little Planet in `loadAfter`, so MLP must sit before it.
2. **My Little Planet missing = a scrambled planet that reports success.** Without it, opening Create World at the
   defaults gives 119,904 tiles, and every row of the paint addresses different ground (PlanetPresetPrime About.xml).
   PlanetPresetPrime alone (vanilla subdivisions only) has **never been run**: UNMEASURED. `w9_run.py`'s 21,872 guard
   stops the stamp; check the Player.log line before generating.
3. **Alien Worlds default-planet trap.** With no Alien Worlds settings file, the planet type is `Default` (vanilla, not
   tidally locked) — MEASURED 2026-10-20 (`06_remake_runbook.md` line 58). Run `set_planet_type.py --check` after launch.
4. **SHIP now carries Alien Worlds** (owner 2026-10-21: "Obviously."; both ids added to `ModsConfig.SHIP.RULED_2026-10-20.xml`, now 279),
   so a world made on PAINT and played on SHIP keeps its tidal sun.
5. **Folders and ids.** All 10 retired rows in section 1 and all 24 active rows in section 3 had their workshop folder
   present on 2026-10-21. Wave 4 did not unsubscribe anything (register line 68). A future unsubscribe empties the folder
   and RimWorld drops the id **silently**; the archive keeps each mod's `About.xml` under
   `design/RimMandrake/mod_archive/about/<packageId>.xml` to identify it. Old `mandrake.*` ids (section 2) must never be
   re-added: they no longer exist.
6. **DLC.** All five expansions are prerequisites (CLAUDE.md). PAINT carries `ludeon.rimworld` plus royalty, ideology,
   biotech, anomaly, odyssey (MEASURED). Odyssey re-creates `TradersGuild` and `Salvagers` on every load; they are banished,
   never removed (register line 47).
7. **The world bakes things in.** Once generated: planet size and coverage, planet type, the faction roster (a faction
   absent at Configure Factions is absent unless `jawa/faction_create` adds it — measured working for
   `RUT_GreentideAntFaction`, 06 G15), ideoligions (classic vs. fixed, 06 S5), seed. A mod that only shapes generation
   (My Little Planet) can leave afterwards; a mod whose classes or defs the save names cannot (Alien Worlds, VFE Tribals,
   More Vanilla Biomes: register lines 33-36).
8. **The world-map CSVs are a RECORD.** `world/ASHKARR_WORLDMAP_*.csv` tells you the planet on its export date
   (2026-09-12 tiles; older links/mutators), not the planet now, and holds pre-port names. The stamp source is a
   `world/paint_inputs_<date>/` bundle rebuilt from the authoritative save and checked by its `RESOLVER.md`. If a newer
   bundle names a def from a mod not on the remake list, the resolver fails: **port the def, or add that mod here with a
   citation** — do not quietly reinstate.
9. **Geological Landforms** (`m00nl1ght.geologicallandforms`, active, in FULL only, on no ruled profile) shapes map
   generation, not the world; the rescue export has a landforms layer (`world/rescue_2026-10-19/ported/ASHKARR_WORLDMAP_landforms.csv`)
   that `w9_run.py` does not stamp (paint bundle README). Whether a remade world's maps need it for parity: UNMEASURED
   (`LANDFORMS_REPLICATE_OR_KEEP_EXPERIMENT`).
10. **Deep Orbit** (`broms.deeporbit`, active, SHIP) is needed to LOAD the old 09-12-family saves (`Orbit2` layer), not to
    make a world; the 2026-10-20 remake ran without it (06 G2).

## 5. What is UNMEASURED

- Whether vanilla 1.6 honours PlanetPresetPrime's subdivisions=7 without My Little Planet (would make MLP unnecessary).
- Whether `rwnodetree.rwplanetatmosphere` writes anything into a world save.
- Whether `sinnamon.moreritualrewards` / `kxp.ideosymbolsasideograms` supply the two dangling names in `The Salvation.rid`.
- Which mod supplied the unported `WildDantooinePlants` mutator (4 tiles; defaulted to `RSW_WildGalacticPlants`,
  PROVISIONAL in the paint bundle README) — no packageId is named in `retired_mutators_port_2026-10-19.md`.
- Reasons for the 222 RETIRED-EARLIER removals are per-period ledger entries, not per-mod rows (archive README); the 418
  generic NOT-NEEDED rows rest on the PAINT-run rule, not on a per-mod reading.
