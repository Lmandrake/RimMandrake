# Pyrelands 0.1.0, visit 1: findings filed from the sitting (2026-11-15, Archmagi)

Game 1.6.4871 rev590, `pyrelands` tier (17 mods, all five DLC: `evidence/modlist_pyrelands_tier.json`), FireEcologyHook.dll
sha256 be276fb1 (game copy == repo, measured), site `NS_Pyrelands_site_1_090cd707f5_visit1` (tile 178, map 1).
Scripts named below are in `scripts/`; their outputs in `evidence/`.

## RIMMANDRAKE_FIX_BLACK_RAIN_LOSES_TO_EMBER_GRASS_FIRE (MOD, Problem; bar three_skies, inv_weather)

The scene says fires go out under black rain while a clear-sky pad still burns. Live, `scripts/rain_fire.py`: each sky
fully blended in (4,500 ticks; `jawa/weather_get` read `RM_FE_BlackRain`, rainRate 1.1, age 4,500), a fresh 8x8 ember-grass
pad on deep ash ringed by concrete, 64 fires lit. Black rain: 64 fires every 250 ticks to 1,750, 26 at 2,000, 0 at 2,250.
Clear: 64 to 1,750, 14 at 2,000, 0 at 2,250. Black rain shortened nothing [measured, one pad each].
Why (vanilla `Fire.DoComplexCalcs`, RimSage): every 150 ticks rain deals Extinguish 10 (fireSize -0.10) while the fire grows
+0.00055 x flammability x 150; ember grass is Flammability 1.6, so +0.132. Vanilla rain cannot put out an ember-grass fire.
The WeatherDef comment ("Extinguishing is equally vanilla") is the false premise. How hard black rain should hit a fire is a
tuning number, so it was not fixed in the sitting.
Acceptance test: `python.exe design/concepts/Pyrelands/version/in_game/visit_1/scripts/rain_fire.py` (live, game up on the
pyrelands tier): the black-rain pad's fire count reaches 0 at least 1,000 ticks before the Clear pad's. Fails today (both 2,250).

## RIMMANDRAKE_EXTEND_SKY_CHAINS_TO_READ_THE_SCENE_CLAUSES (HARNESS; scene sc_three_skies)

The brief runs sc_three_skies as `--live cinderfall`, but the `cinderfall` and `blackrain` chains only check that two
WeatherDefs differ in a field and take one screenshot. None of the scene's clauses is read: lightning under cinderfall and
none under ash fall, the ash patch's depthSum falling under black rain, fires out under black rain. This visit read them by
hand (`scripts/three_skies.py`, `evidence/three_skies.json`): cinderfall lit fires in 5 of 10 1,000-tick windows
(0,0,12,0,0,3,4,17,0,4; total 40); ash fall 3 in its first window only (most likely the blend from the previous sky) [guess ~70%], 0 after;
a 30x30 patch's depthSum 283 under ash fall, 315 after 2,500 ticks of black rain (still blending), 161 after 5,000. The
fires clause fails (item above). Acceptance test: the two chains carry one row per clause, and each row fails on a def
with the clause's mechanism removed.

## RIMMANDRAKE_FIX_RUINS_CHECK_COUNTS_CHARRED_FLOORS_AS_MISSES (HARNESS; check judged wrong, row UNMEASURED)

`ruins_scorched` wants >= 90% of 3x3 ruin samples to be RM_FE_Ash_Deep. It read 83% twice (75 deep ash, 6 AncientConcrete,
9 TileLimestone). The mod keeps a ruin's floor on purpose and paints it charred (`CharFloor`, FireEcologyHook.cs; landed
with the 2026-11-08 main merge after a judge said "the ruin floors look clean"); the check's comment still says the genstep
lays deep ash on every footprint cell, ruin floors included. The floors read charred on screen (`ruin_limestone` shot).
The ash half held: 10 of 10 sampled ruins carry ash. Acceptance test: the check counts a cell as scorched when it is deep
ash OR a floor whose terrain colour is RM_FE_Charred, and fails on a fixture where CharFloor is disabled.

## RIMMANDRAKE_FIX_HERD_CHECK_WINDOW_ASSUMES_PRE_SAND_PACE (HARNESS; check judged wrong, row UNMEASURED)

`herd_follows_two_day_old_burn` gives the herd one 2,500-tick step to close 30% of ~149 cells on burn A, on the premise
"Walk urgency covers ~100 cells in it". Measured: about 19 cells per 1,000 ticks (ash is Odyssey sand depth since
2026-11-08). Even with every ullai walking straight, the centroid can close about 30% only if none is held back; one of ten
had no reachable cell, two ran RM_ShadeDash (noon Direct Sun on a 50 C site) first. The decision half is right every time:
anchor 31,103 = burn A, goAnchor 10 of 10, issued 9. Watched past the window (`scripts/herd_exp.py`): centroid distance to
A 149 -> 118 -> 75 -> 63 -> 54 -> 48 over 12,500 ticks, never towards B. Acceptance test: the motion row's window comes
from a measured pace on the site (cells per tick of one ullai on deep ash) and the row fails on a herd whose giver goes
to B.

## RIMMANDRAKE_FIX_OLD_SAVE_ROW_MISREADS_A_NEW_FIXTURE (HARNESS; P_opening_front, no bar)

`opening_front_old_save_inert` expects lit=0 and litTick=-1 on any map past its window. A fixture built after the opening
front shipped lights it at birth (litTick 372539 = map birth, lit 5), so it reads FAIL once an earlier chain has aged the
map past the window. The re-arm half, run by hand on a fresh reload (`scripts/rearm.py`): done=True, lit=27, 27
free-standing fires, scar laid (2,877 cells). Acceptance test: the row reads UNMEASURED SITE when litTick equals the map's
birth tick, and still fails a pre-change save that lights late.

## RIMMANDRAKE_JUDGE_ULLAI_NORTH_VIEW_READS_AS_A_STICK (art, for the art judge)

Six wild ullai staged facing north (walk save, station 5) read as thin vertical sticks about a cell and a half tall, beside
a furnace-beast giant several cells wide; from the side (ruin station) the same creature reads as a full giraffe-like
body. The north facing may be correct for a long-necked animal seen from behind, or a facing-art defect. Acceptance test:
none, an art judgement (rimworld-sprite-facings; the owner approved the art as a sheet).

## RIMMANDRAKE_FIX_WALK_DIGEST_COMPARES_A_TICK_STAMP (HARNESS; sc_walk, check judged wrong, row UNMEASURED)

`walk_digest` keeps ProbeRegrowth's and ProbeBurnHistory's `now=` field and the burn line's `burning`/`center`. Measured on
the full list (316 mods, `scripts/walk_steps.py`, `evidence/walk_state.json`): every count matched across the reload (Fire 46,
scorch-fruit 26, the 7-row regrowth table, 168 history samples, newest and ago), but `now` read 1101501 before and 1101502
after, and `burning=46;center=176,11` read `burning=0;center=invalid`. `scripts/walk_reload_probe.py`: that is a cache the
next 60-tick watch rebuilds (0 at load, 45 and centre 177,11 after 60 ticks, 54 after 480: the front walks on). So the
digest can never match on a correct reload. Also fixed in the sitting (validation.py): the walk's error filter read `level`
where drain_log returns `type`, and its log window was a count, blind once the buffer sits at its 1000-line cap (it read
mark 1000, total 1000); it is now a sentinel line. Acceptance test: the digest drops the `now=` stamps and the watch-rebuilt
`burning`/`center`, matches across a reload of pyre_walk_mid, and still differs from pyre_walk_pre.

Also on the walk digest: `jawa/list_things defName=RM_Ullai` (and RM_FurnaceBeast) counts 0 while `jawa/list_pawns` lists 6
ullai and 1 furnace-beast on the same map (measured after staging the full-list walk save), so the digest's two creature
fields were blind (0 = 0 on every read). The fix reads pawns through list_pawns.

## RIMMANDRAKE_TRACE_ZHAKKA_ON_THE_WALKED_PYRELANDS_MAP (strange; populations on his list)

After two walked weeks on the full list (316 mods), the Pyrelands map held 9 RSW_Zhakka and 1 RSW_WompRat (neither among
the 16 roster kinds), plus 2 Tribal_Warrior and 1 Tribal_HeavyArcher, not hostile. `jawa/biome_probe` on the same game reads
the RM_Pyrelands roster as exactly the 16 manifest kinds, so the biome's own spawner is clean; the newcomers came some other
way, although both weeks ran under the quiet site profile (the site build and the return to mid both settle with it). A
mod's own event outside the storyteller is my guess [guess ~50%]. Acceptance test: none, a trace (load `pyre_walk_end`, read the incident history or the pawns' spawn records,
name the route).
