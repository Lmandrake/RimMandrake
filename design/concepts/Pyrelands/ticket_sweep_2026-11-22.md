# Pyrelands ticket sweep, 2026-11-22

Item RIMMANDRAKE_SWEEP_PYRELANDS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE (detached BENCH run). His words, 2026-11-22
about 3:05 PM PST: "Did we ever do a Pyrelands ticket sweep to clear up all the old/outstanding tickets ... Find.
Adjudicate. Eradicate the stale. Merge the modern. Apply/build them RIGHT NOW if they're valuable".

## Earlier sweep

Yes, one: 2026-11-16, `D:\ClaudeWork\rimmandrake\conductor\ticket_sweep_pyrelands_20261116.md` (60 open then, 28 retired,
32 kept; ledger bf5f62083c, prose 0c2828de2f). No other Pyrelands sweep is on record.

## How the items were found [measured]

`model.replay(model.read())` over the whole ledger: 1950 open items. A regex over id, title, item prose and notes for
Pyrelands and its parts (pyre, firehawk, ullai, zeer, zizzik, scorch-fruit, crestfeather, furnace beast, cinderfall,
black rain, ash field, FireEco, RM_FE_, flamefang, firefoam, firebreak, the other creatures, burn line, fire front, fire
rite, fire clock, ash sand/dust/cover/print). 186 open items name a term; 89 in id or title. Each of the 89 was read
(state, prose head, last three ledger events) and its subject checked. 53 are about this mod (its code, tests, art,
harness or its pipeline runs); this sweep is the 54th. The Conductor's rough count was 110 item files naming it
(`grep -li pyrelands items/*.md` reads 104 today): most of those name Pyrelands only as an example.

Not about this mod, left alone (36): 7 PyrelandsMechanics (Deep Desert Tribes, its own mod and version); LeaningScrub
(4, incl. the calling-pyre and the scrub pins re-read); river steam (3, mod mandrake.rut.riversteam); pipeline machinery
that cites a Pyrelands case (the Designer stage loss, void hold to midnight, six runs in one clone, bridge client bound
to its game, the tick's 1 GB peak, the heap-growth scope, the stage ceilings release, the static-cache census whose
Pyrelands half is gone, the four full-list holdouts, the FlowWorks gaps to the Designer, the Pyrelands-and-Slack
switch-on whose Pyrelands half is done); other mods' items (FlowWorks tar fire and river site, Ninefold, the settings
kit, ExplosiveGrowth tree burst, the biome defName wave, the landmark pass, art audits of other flyers and facings, the
Gizka sheet, fixtures, sprint sites). Could not look: nothing; items with prose in no file and no title match would be
missed by this search.

## Count per class (53)

| class | n | items |
|---|---|---|
| DONE | 9 | About text, fire-clock label, crestfeather pin (all 71dcee74a7, this run); regrow reader (897516fc92); judge recalibration and restamp (47e044e556); comb-lane burn (2910619418); fire wasp flight (8e3ccc69d4); visit 2 (2c7579fdf2) and visit 4 (b99d7df504) records |
| DUPLICATE | 4 | two extra visit-2 launches, an extra visit-5 launch, the killed visit-3 route (each into its run that did it) |
| STALE | 4 | rescue decision after visit 2 (visits 3-5 since); ash-field watering, medium ground, opening front (fixes landed in 8fb9f7f2b6; their pre-pipeline live criteria replaced by the locked test table) |
| DEAD | 1 | the Lightspeed FireEcology walk-bar drain (Lightspeed tools retired d2a0462048) |
| NOT WORTH THE TOUCH | 10 | rain-list pin, wind callers, probe clamp, deciders' last two plants, donor Grasslands entry, anchorless herd, paved review stations, Tutor sky on sites, Zeer browse (GPT opinion), the 'own' health preset ghost key; one line each on `version/polish.md` |
| NEEDS HIM | 6 | ullai judge and card, fire-hawk east S, ash footprints look, flamefang card and its design question: merged into one ticket |
| KEEP, CURRENT | 14 | the finishing ticket, the shore-ring clause, grass hidden under ash, the fixer limit; and 10 merged into 3 tickets (4 long live reads, 2 art, 4 SteveDesktop testq) |
| KEEP, NEXT | 5 | black rain fills moats, smoke weather, wind fire for all biomes (Pyrelands 0.2.0, his cards); the Struck Glass rite (Rites v2, his 2026-10-23 deferral); the Tribes fire-clock incidents' live criterion (PyrelandsMechanics 0.1.0) |

## Modern tickets that remain

Current version (0.1.0):
- RIMMANDRAKE_FINISH_PYRELANDS_AGAINST_TREE_FURNACE_GREW_TO_NINE: the mod's carrier through the pipeline.
- RIMMANDRAKE_STAGE_PYRE_POND_SO_SHORE_RING_CLAUSE_GETS_A_READING: a bar clause no live check decides.
- RIMMANDRAKE_SHOW_PYRE_GRASS_UNDER_ASH_COVER_COUNTED_UNSEEN: grass not drawn after ash fall; his 2026-11-17 card made it a 0.1.0 defect (the ash layer draws at Terrain altitude, so the cause is elsewhere; not found in this run).
- RIMMANDRAKE_UNSTICK_PYRELANDS_FIXER_COUNT_TWELVE_FOUR_REFUSED: steward_max_per_version names no danger (the Conductor's).
- RIMMANDRAKE_READ_PYRE_LONG_RUN_FOUR_OWED_ZHAKKA_FIRST (new): foreign kinds on his list, the 1 s stall, a Titan pool dump, scorch-fruit freezer fill.
- RIMMANDRAKE_JUDGE_PYRE_POST_SHEET_ART_CRESTFEATHER_A_HORN (new): 17 unjudged art entries, the crestfeather's own sprite.
- RIMMANDRAKE_ROUTE_PYRE_TESTQ_OFF_STEVE_NO_SITE_THERE (new): 5 SteveDesktop jobs since 11-19, 0 PASS; no loadable site there.
- RIMMANDRAKE_PASS_OWNER_ITEMS_ON_ROAD_BACK_ULLAI_HELD (new, pipeline): a needs=owner road-back item held Pyrelands at fixer_spent; acceptance test red (PASS 2/3); `maturation_autonomy.py` is held by the live FlowWorks walk route run.

Needs him: RIMMANDRAKE_SHOW_PYRE_HIS_WALK_FOUR_PICKS_ULLAI_FIRST (new).

Next version (0.2.0): RIMMANDRAKE_BUILD_BLACK_RAIN_FILLS_MOATS_TANKS_STAY_DRY, RIMMANDRAKE_BUILD_PYRE_SMOKE_WEATHER_ONLY_LONGSHADE_HAS_ONE,
RIMMANDRAKE_GENERALIZE_WIND_FIRE_ALL_BAROQUE_BIOMES_NEXT_VERSION.

## Built in this run

- 71dcee74a7: About.xml says "Behind the fire, some solace." for "Fire pays." (his 2026-11-05 reword); the fire-clock
  label and tooltip name the biome's own fire fronts it also stops (FireEcologyHook.dll rebuilt); the crestfeather test
  reads the chance from the def. New checks no_fire_pays_text and clock_label were red on the parent, green on the fix,
  each with a planted mutant red. Offline: cut_stays_cut, settings_sweep, firehawk_crestfeather, self_contained,
  defs_offline, round6_gaps, round6_parts, settings_screens --mod Pyrelands, all green.
- UNRUN live: the label on the Mod Settings screen, after the next deploy (`python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Pyrelands --apply`, game down; ArchBig is in his walk).
- afc872abb4: the three deciders this run edited had no red record and the rebuilt DLL left the offline deciders stale,
  so visit 6's certificate refused 9 of 16 bars and the tick filed RIMMANDRAKE_REPAIR_PYRELANDS_FORM_REFUSAL_AT_THE_RUN_SEVEN.
  Repaired: `maturation.py red-seen` for T_CUT_STAYS_CUT, T_SETTINGS_SWEEP_OFFLINE and T_FH_CRESTFEATHER (patches in
  `version/evidence/patches/`), `certificate Pyrelands --run`; the certificate reads OK; the repair item closed.
- Merging the ullai judge item freed the road back: `./pipe why Pyrelands` no longer reads fixer_spent (4:04 PM PST).
- The pipeline fix's acceptance test, `src/RimMandrake/rimflow/acceptance/road_back_owner_item_holds_nothing_accept.py`.

## Needs him (his plain words)

At your Pyrelands walk: (1) look at the ullai herd in game, then pick redraw, bigger, or keep; (2) look at the fire-hawk
east view S and say install or not; (3) see a walked path in the ash and the hover label; (4) after the tune, one
untended flamefang bite is survivable and two can kill: is that the danger you want?
