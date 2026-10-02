# BENCH_REBOOT_HANDOFF_202610022308 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610021935`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
All twelve grandfathered bedazzle scoring sittings are closed (Weeping Stones, Gelatinous Slime, Miasma today), each ticketed out to FOUNDRY in the same §8 shape. Track (a) of `BEDAZZLE_TOP_SHAPE_PROGRAM_1` is done; the owner's next ordered step, the Northstar pilot, is filed, its offline half landed, and its live run sits with FOUNDRY.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
1. **Three owner rulings override older rules, recorded as exceptions:** the Slime chunk bomb beats sheet ban 7 (no re-arming); the Joining Water rite's injury-spreading is a power, against "cohesion, never a power". Both by card, 14:44 PDT.
2. **Gods at cap now:** Mob'Unloo (Refused Toll), Oomo (Joining Water; "Pomp" was Oomo), Rekko (Recall of the Written-Off), plus Ohm, Ozzik, Zizzik. Open slots: Ishko, Sh'kaar, Ta'Baa.
3. **Selftests 119/120:** `selftest_tool_metadata.py` says the built JawaBench DLL lacks four FlowWorks tools present in source; likely FOUNDRY mid-build, not BENCH work.
4. **Uncommitted `src/RimMandrake/Utils/modset_builder.py` edit seen mid-session** was the Northstar helper's, since committed in `a27a59c5d`.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `NORTHSTAR_ISHKO_PILOT_1` — steps 1-4 done (mock GREEN 8/8, driver records runs), reassigned to FOUNDRY; NEXT: when FOUNDRY's FlowWorks bridge work ends, run `python3 src/RimMandrake/Utils/northstar_driver/live_session.py --mod IshkoDarkLandmarks --tier ishko --plan src/RimUtinni/IshkoDarkLandmarks/northstar_plan.py --deploy-mod IshkoDarkLandmarks --deploy-mod AshkarrLandmarkArt`.
- `GIT_WORKFLOW_MIGRATION_1` — waiting on its date; NEXT: on 2026-10-05 measure manual rebases/day and Claude writes to D:\ for 3 days, record in the plan §4, close it.
- `LONGSHADE_BEDAZZLE_CONTENT_1` — 8 revision art jobs queued; NEXT: when `RM_Maidenbloom_b`/`RM_Tazzok_b`/`RM_Shadespire_b`/`RM_Skarrok_b` render, build him a review sheet.
- `BEDAZZLE_TOP_SHAPE_PROGRAM_1` — track (a) done; NEXT: read the program item for its next track and ask the owner which to start.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A gpt_consult with no live process may have finished; check its output file before calling it dead. (filed: lessons)
- Long option descriptions (~600 chars) in a 4-question card got rejected; under ~350 rendered. (filed: lessons)
- `live_session.py` refuses unless FOUNDRY holds the bridge. (filed: lessons)

## Closed since the last handoff (4)

- `WEEPINGSTONES_SCORING_SITTING_1` — 1fa92efa3
- `GELATINOUSSLIME_SCORING_SITTING_1` — f214b5385
- `MIASMA_SCORING_SITTING_1` — 4d426ea50
- `NORTHSTAR_DRIVER_RECORD_STATUS_1` — 1f39992ed

## Filed and still open (38) — the next seat's queue

- `WEEPINGSTONES_MURRIN_CATCH_WIRING_1` — Weeping Stones: murrin catchable (floor resident + RM_MurrinCatch in fishTypes); dead FISH_BY_BIOME_1 citations out
- `WEEPINGSTONES_TRUCE_HUNT_SUPPRESSION_1` — Water truce suppression half: predators never start a hunt within the truce radius
- `WEEPINGSTONES_DEWSILK_COCOON_1` — Weeping Stones: dewsilk from mirrik cocoons (cocoon item, tamed-swarm harvest, cloth)
- `WEEPINGSTONES_HEAT_WINDHOUR_TEXT_1` — Weeping Stones: heat kind by sun angle from latitude; rewrite the 12 dead wind-hour sentences
- `WEEPINGSTONES_OASIS_MUTATOR_FLORA_1` — Weeping Stones: register RM_/RUT_ with the Oasis mutator; Earth palms (date palm) out of our oases
- `WEEPINGSTONES_SETTINGS_SLIDERS_1` — Weeping Stones Mod Settings sliders: truce radius, vhorrin odds, vizhik escape chance
- `WEEPINGSTONES_WALKING_CONDENSER_1` — Weeping Stones giant: the walking condenser (oldest gorrask carries a running machine; a pool and truce where it settles)
- `WEEPINGSTONES_CONDENSER_QUESTS_1` — Walking condenser quests: Hutt capture for the Arena, or Moisture Farmers keep it free vs Blackstar fame hunters
- `WEEPINGSTONES_REFUSED_TOLL_RITE_1` — The Refused Toll, for Mob'Unloo: draw at an Imperial metering station and walk away unpaid
- `GELATINOUSSLIME_GAPPO_FAMILY_1` — Slime: the gappo family (grazer moved to RM_ with its v2 art, plus lesser and greater gappo); RUT_SlimeGrazer out
- `GELATINOUSSLIME_DWOMMO_FLIER_1` — Slime: the dwommo, a gas-float flier (real flight), the flying aristocracy
- `GELATINOUSSLIME_GLURRO_SALVE_1` — Slime: the glurro, iron-crusted grazer milked and rendered for a slime-resistance salve
- `GELATINOUSSLIME_FUBBUM_HUNTER_1` — Slime: the fubbum, the one hunter of the gelatid herds
- `GELATINOUSSLIME_KIT_ART_1` — Slime: real art for the whole free kit, replacing the vanilla tortoise/grass/bush/dandelion stand-ins
- `GELATINOUSSLIME_RAIN_STRIP_1` — Slime: campaign strips vanilla Rain/FoggyRain from RM_GelatinousSlime and the twin (ban 2); shrine denial retargeted
- `GELATINOUSSLIME_GENE_TEXT_TIER_1` — Slime: move the Star Wars A/B gene lists (57 genes, 19 canon strings) from the free mod to Utinni
- `GELATINOUSSLIME_SETTINGS_SWITCHES_1` — Slime Mod Settings: on/off and a slider for slimification, farm conversion, the visitors
- `GELATINOUSSLIME_PIT_SOLVENT_1` — Slime pit as a solvent: renders toxic or indigestible food safe (Rot's finest in the campaign)
- `GELATINOUSSLIME_FARM_RUINS_1` — Slime: ruined farms sinking into slime-grass (map genstep)
- `GELATINOUSSLIME_TITAN_CHUNK_BOMB_1` — Slime giant: a chunk of the titanoslime is a terrible thrown bioweapon
- `GELATINOUSSLIME_VAULT_SEAL_BREACH_1` — A titanoslime chunk opens a Forsaken vault blocked by an Assailant seal (seal does not exist yet; owner to confirm)
- `GELATINOUSSLIME_ARCHIVE_RESURRECTION_1` — Slime: resurrect someone as of the last time they touched the slime (Ascendant Ladder tech; are they the same?)
- `GELATINOUSSLIME_JOINING_WATER_RITE_1` — The Joining Water rite: join hands holding slime, one person's permanent hediffs spread weak over several (god: Pomp, unresolved)
- `MIASMA_FREE_SALT_CRUST_1` — Miasma free tier: its own salt crust so the salt line paints without the campaign
- `MIASMA_SWARM_COMPOSTER_PORT_1` — Miasma: port the fever swarm, karrobel and delta loam to RM_, and the pollination gate into the free mod
- `MIASMA_FREE_NURSERY_YOUNG_1` — Miasma free nursery: young of crimson opee, thornback colo, shale gorger, reefback
- `MIASMA_AMBUSH_FROG_REMAKE_1` — Miasma: the giant ambush frog remade as ours (new name, alienized art)
- `MIASMA_ROUND2_IMPORTS_1` — Miasma campaign cast: round-2 imports as races (bogwing flier, blarth, blixus, marsh haunt); sando adult held
- `MIASMA_WARDEN_MOTHER_ART_1` — Warden mother art, with an aged variant for her last season
- `MIASMA_YOUNG_CALL_1` — Miasma: the stranded young's cry, and the warden mother lumbering toward it
- `MIASMA_ATTAR_STILL_1` — Miasma: the attar (beauty oil) from delta silt and salt; glaze and balm, never medicine
- `MIASMA_FLOTSAM_YARD_1` — Miasma: the flotsam beach, river goods washed into the roots after each surge
- `MIASMA_SETTINGS_SWITCHES_1` — Miasma Mod Settings: plant predation, pollination gate, stranded deformation
- `MIASMA_MOTHERS_PRICE_1` — Miasma giant: the mother's price (sell a stranded young and she never forgives; succession void)
- `MIASMA_DECAY_CELLS_1` — Miasma tech: decay cells, a learned generator making power from rot; spent cells become rotting beds
- `MIASMA_ROTTING_BED_CUISINE_1` — Rotting bed (spent decay cell) grows a Star Wars Cuisine ingredient (mandrake.rsw.cuisine)
- `MIASMA_RECALL_WRITTEN_OFF_RITE_1` — The Recall of the Written-Off rite (Rekko): a struck-out disposal order calls a salvage operation on you
- `NORTHSTAR_ISHKO_PILOT_1` — Northstar pilot on IshkoDarkLandmarks: walk arrows, ishko tier, mock clean, record status, first live_session run to green

## Commits

```
521eb7c46 ledger: NORTHSTAR_ISHKO_PILOT_1 to FOUNDRY for the live run
1441e651b Ledger sync: close NORTHSTAR_DRIVER_RECORD_STATUS_1 at 1f39992ed; Ishko pilot steps 1-4 note
1f39992ed northstar_driver records live runs via status.record_run; suite components become rows
d5f4c7640 lint_calls: check literal-key **{"def": x} splats instead of UNCHECKED
a27a59c5d Ishko north-star tier and plan: `ishko` = Core + 5 DLCs + art + ishkolandmarks; USE_SUITE
2aacfbec4 IshkoDarkLandmarks script: arrows on every must-be-true line, placement behaviour bar
5e965e830 ledger: owner note on MIASMA_DECAY_CELLS_1
e617ad5bc Decay cells: rotting bed also disposes of corpses, yielding skulls and bones (owner)
2ca6c89a8 File NORTHSTAR_ISHKO_PILOT_1 (bedazzle scoring sittings all closed)
db348086f Ledger sync: file and close MIASMA_SCORING_SITTING_1 at 4d426ea50, 14 Miasma items, turn-1 rulings; track (a) done
4d426ea50 Miasma turn-1 ticket-out: 14 FOUNDRY items, 11 art jobs; the Recall of the Written-Off in the register (B17)
14830155b Slime follow-ups ruled: Pomp is Oomo (at cap), seal on the Slough vault only, bomb and rite power are exceptions
09a832f6d Messy Conduit live pass 2: 19/19 live checks pass twice; save/load fixed (cord layer crashed on load) and proven identical; mod-removal fixed (map component kept out of save); real-art screenshots; script gains --save-load and --removal-check
1b6ec46dc Cactipine, Needlepost, Terrorworm confirmed Alpha Animals (owner): wiring log corrected, re-home item widened to five ports
28388e1eb Miasma bedazzle review, turn 1 drafted (grandfathered sitting 12, the last) + GPT consult files
63b5f360f Art wiring pass 3: 8 real Messy Conduit renders replace placeholders (4 kept); 14 requeued renders wired (vents, livingbolt, greatbole hardwood, sweetline wool)
c89b86fda Close pit chain items (moved to closed/); refresh tool_schemas.json from the live bridge (493 tools) so the O8 lint sees job_probe and fillInLevels
0b455c895 Art requeue: 14 failed jobs fixed (9 bad_job_file: facing + top-down wording; 3 worker_error; 2 master_failed) and done
e79f8de4f FlowWorks: a pit is only a depth-4 cell (holder building removed, width rule W=round(sqrt(BodySize)) decides holding); 26 legacy pit defs + 18 .cs files retired; Northstar v2 63 pass 0 fail
75a77f7be Ledger sync: close GELATINOUSSLIME_SCORING_SITTING_1 at f214b5385; program note (Miasma next)
... 15 more: git log --oneline c1b8654c1..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : UP  → corrected to DOWN, measured now
- Bridge: for     FlowWorks oscillation fix + Northstar v2 (owner: pause lifted, bridge his gift)

Working tree clean apart from untracked `Transient/`.

