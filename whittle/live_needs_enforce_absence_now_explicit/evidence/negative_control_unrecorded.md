# Negative control: the 26 PASS-run additions with no recorded live list

Source: `replay_enforce.txt` (the `unrecorded live list:` lines) over
`src/RimMandrake/rimflow/fixtures/live_mods_replay.json`, whose 50 PASS cases are the last 50 PASS proofs before the
gate landed (2026-11-03T13:14Z .. 2026-11-05T19:26Z, frozen at the books and build sha of each run).

**What "addition" means here.** The gate adds a mod to the planned load. For a run that PASSED before the gate existed,
an addition matters only if that run passed WITHOUT the mod (then the proof did not need it: a false positive). So each
addition is checked against the live list the run passed on. `attach-loads` froze that list from Archmagi's ModsConfig
PRESWAP snapshots (`archmagi_preswap/`, mtimes in `archmagi_preswap/MTIMES.txt`). Each snapshot is the live list over
[its mtime, its stamp]. Recorded result: **24 additions on runs with a recorded list; the run already held all 24; 0 the
run did without.** For the other 26 the run's time falls between snapshots. `modlist_swap.snapshot` skips a list
identical to one already stored. 29 of the 37 transitions between snapshots leave a gap, and in 21 of those the list
after is not a superset of the list before (a swap, not an enable), so the list in a gap cannot be inferred and none is
guessed.

For those 26, what the PASS run itself shows (the scripts quoted are the versions frozen at the run's books sha in the
fixture, not HEAD):

| run (UTC) | item, clause | addition | shown held by the run? | why |
|---|---|---|---|---|
| 11-05 06:32 | HEAVY_TEXTURES_MEASURE_REAL_VRAM A2 | rwnodetree.rwplanetatmosphere, vesper.egihologramsandprojectors, zacharyfoster.mineralsframework, zacharyfoster.mineralsrock, fourtoo.glowingbush | **yes** (5) | `heavy_textures_vram.py:87,94-96`: exit 2 "not in the running load" for any wanted mod jawa/texture_memory does not see; the row is exit 0 |
| 11-04 13:26 | RSW_FACES_VERIFY_IN_GAME_BEFORE_SHIM A1 | nals.facialanimation | **yes** | `fa_faces_live.py:10,114-117`: exit 2 unless FA and the three RSW/RUT mods are in jawa/running_mods |
| 11-05 18:14 | PIT_ESCAPE_PROVE_LADDER_LEFT_DOWN A6 | FlowWorks | **yes** | `pit_rescue_live.py:53,141`: every row reads `RimMandrake.FlowWorks.RM_LadderParity` and fails UNMEASURED if the ladder is not read back; PASS needs FlowWorks' C# |
| 11-04 14:10 | CREEP_WEB_HARVEST_LIVE_1 A5 | RimMandrake.Biomes | **yes** | the Webwork harvest it measures is Webwork content, folded into RimMandrake.Biomes; no other mod holds it |
| 11-04 16:14, 15:46, 12:21; 11-03 22:04, 17:42 | MIASMA_WARDEN_MOTHER_ART_1, STILLSAND_GLASS_CHAIN_REMAINDER_1, CRACKEDLANDS_THREE_HEIGHT_FLORA_1, HORIZON_CARAVAN_VANILLA_REFUSES_1, GELATINOUSSLIME_KIT_ART_1 | RimMandrake.Biomes (folded) | **yes** (5) | each build is a folded source (Miasma, Stillsand, CrackedLands, Stillsand, GelatinousSlime) whose content loads only inside the composed RimMandrake.Biomes; the gate "adds" the composed mod the deploy already composes (`--compose biomes`) |
| 11-05 16:54 | HORRORS_RAIDING_FACTION_1 A3 | AshkarrWeatherSuite | **yes** | that version moves the LIVE PlanetGeometryDef (`probe(g, "Geometry", ...)`, lines 112-115), a def of mandrake.rut.weathersuite |
| 11-03 23:32 | HORRORS_RAIDING_FACTION_1 A3 | AshkarrWeatherSuite | **no, cannot tell** | that version reads the geometry XML from the repo (`GEOM`, line 35); clause A3 (dayside: no lair) can pass without the mod. The item's A2 clause needs it (census R1 repair), so it is not a wrong addition for the item, but this run does not show it was loaded |
| 11-05 16:54, 11-03 23:32 | HORRORS_RAIDING_FACTION_1 A3 | mandrake.rm.flowworks, mandrake.rm.luminouspigment (closure via mandrake.rm.biomes) | **cannot tell** (4) | transitive About.xml dependencies; the proof does not read them |
| 11-04 13:26 | RSW_FACES_VERIFY_IN_GAME_BEFORE_SHIM A1 | neronix17.toolbox, mandrake.rm.flowworks, mandrake.rm.luminouspigment (closure) | **cannot tell** (3) | as above |
| 11-04 01:56 | VANILLA_BEAST_EXCISION_1 C1 | mandrake.rm.flowworks, mandrake.rm.luminouspigment (closure) | **cannot tell** (2) | as above |
| 11-04 01:56 | SPECIES_TRAITS_OVER_APTITUDES_1 A1 | neronix17.toolbox (closure) | **cannot tell** | as above |
| 11-04 14:11 | BRONZIUM_DROP_1 B3 | neronix17.toolbox (closure) | **cannot tell** | as above |

**Totals over the 50 PASS proofs:** 50 additions. 24 were held per the recorded list, 14 more were held per the run's own
proof, 0 were shown absent, and 12 cannot be told (11 transitive-dependency closures, 1 HORRORS clause).

What the recorded lists say about the 11 closures (not proof for these runs): across the 38 recorded lists,
mandrake.rut.patches was active in 26 and never without flowworks and luminouspigment; mandrake.rsw.armoury was active in
14 and never without neronix17.toolbox; mandrake.rsw.starwarsraces was active in 9 and lacked toolbox once
(20261105_060525). mandrake.rm.biomes was active in 34 and lacked flowworks or luminouspigment in 4
(20261102_201833, 20261103_190745, 20261103_211213, 20261105_154438). So the immediate-dependency-only enable really did
leave broken loads, which is the defect the closure need fixes. No PASS run fell in those four intervals.

What would settle the 12: the running load of each of those runs. No record holds it: rows before landing carry no
mod list, logs hold none, and the snapshots skip repeated lists. Since this change, every admitted row carries its
running load (`env.running`: count, sha, the list under `<RELENTLESS_ROOT>/live/loads/`), so the next replay can check
every PASS run directly.
