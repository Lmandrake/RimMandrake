# BRIDGE v2.0: three scenes on the scene library, old against new

Item `RIMMANDRAKE_CONVERT_THREE_SCENES_SHOW_IF_TEN_NAMES_HELP`. Written 2026-11-24. This file tests the hypothesis of
`11_design.md`, challenge point 5: that ten names help an agent write a live test. Tags: MEASURED (counted from a file or
from a run on the fake game), READ (read from a record), GUESS n%. **No converted scene has run in a game.** Every new
reading below is from the fake game of `src/RimMandrake/Utils/scene_fake.py`, whose replies for the new hands are made from
their wire pages, not recorded.

The converted scenes:
- FlowWorks `sc_moat_raid`, row `MOAT_rim_wardens_not_stabbed`: `src/RimMandrake/FlowWorks/northstar/scene_moat_rim_wardens.py`
- Explosive Knockback, the storeroom bomb pit (arm A): `src/RimMandrake/ExplosiveKnockback/proof/scene_storeroom_pit.py`
- Gimme Some Slack `sc_wall_lamp_looks`, row `SC_wall_lamp_draws_each_look`: `src/RimMandrake/GimmeSomeSlack/northstar/scene_wall_lamp_looks.py`
  (first written by a fresh agent; see below)

The offline test: `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_scene_conversion.py`.
Its `--mutants` mode plants the four wrong codes of the ticket; each turns a check red (4 of 4, MEASURED 2026-11-24).

## The readings

Columns: lines of the code that decides the row (old: the functions of the scene that the row runs through, Python only; new:
the script); bridge calls in one run; distinct tool or entry-point names; `s.raw` calls left in one unplanted run; runs
needed to the first valid run; spoiled runs and their class.

| scene | old/new | lines | bridge calls in one run | distinct tool or entry-point names | s.raw calls left | runs to first valid run | spoiled runs and class |
|---|---|---|---|---|---|---|---|
| sc_moat_raid | old | 338 (21 functions of `concept_scenes.py`) and the C# helpers of `RM_NorthstarProofs.cs` | UNMEASURED: no record counts the calls of one live run; 32 call sites MEASURED | 11 tools and 9 C# proof helper methods MEASURED | not applicable (the old layer has no `s.raw`) | UNMEASURED; visit 9 gave PASS, FAIL, PASS in three valid runs READ | visit 9: 1 FAIL whose cause was not read READ |
| sc_moat_raid | new | 68 | 51 on the fake (MEASURED): 16 status, 12 process-mark, 8 session, 2 read_paths, 2 spawn, 1 act_batch, 2 run_until | 10 library names, 1 verb (`job`, in one batch) MEASURED | 0 (1 under `--plant melee_rule_off`) | UNRUN | UNRUN |
| storeroom bomb pit | old | 310 (`storeroom_pit_proof.py`, three arms and the storage arms) and 526 lines of `RM_KnockbackProof_StoreroomBombPit.cs` in a PROOF build | UNMEASURED: no record counts the calls of one live run; 24 call sites MEASURED | 8 tools and 5 C# proof helper methods MEASURED | not applicable | UNMEASURED | UNMEASURED |
| storeroom bomb pit | new | 72 | 58 on the fake (MEASURED): 9 read_paths, 1 act_batch, 2 run_until, the rest open and close | 10 library names, 1 verb (`damage`) MEASURED | 0 (1 under `--plant knockback_off`) | UNRUN | UNRUN |
| sc_wall_lamp_looks | old | 110 (6 functions of `scene_rows.py`) and 751 lines of `ConduitStyleProbe.cs` and `AerialProbe.cs` | UNMEASURED: no record counts the calls of one live run; 18 call sites MEASURED | 6 tools and 6 action strings of the mod's probe MEASURED | not applicable | UNMEASURED | UNMEASURED |
| sc_wall_lamp_looks | new | 75 (the fresh agent's first version: 131) | 126 on the fake (MEASURED): 10 run_until (4 of them only to let the probe act), 9 read_paths, 4 mod_settings_field | 11 library names, 0 verbs MEASURED | 4 (each gives a lamp its look through the mod's probe; 6 more under the plant and the restore) | UNRUN | UNRUN |

How to read the bridge calls: on the fake, about two thirds of the calls of a new scene are the library's own bookkeeping
(the status, the process mark, the session). A live run adds the calls that the fake does not make (the load waits). The old
scenes' live counts were never recorded, so the two columns cannot be compared yet.

The scopes differ, and this changes the line counts. The new moat and storeroom scenes start from the fixture saves of the
sittings (`TP_MOAT_HELD_A`, `EK_SITTING_STATION1_STOREROOM_PIT_20261112`), so they do not build the moat or the room; the old
moat scene builds everything on a fresh map and decides five more rows. The new storeroom scene reads 6 goods stacks, not 12:
one condition holds at most 64 nodes (`conds.MAX_NODES`), and the success over 12 stacks needed 124.

## Did the ten names help

Yes for two of the three scenes, and partly for the third. The evidence, scene by scene:

- **The verdict moved out of the game, and the hidden reads replaced the text searches.** The moat row was a text search for
  `held=True` in a C# helper's output and a count over a damage-recorder ring. It is now one forbidden condition on a value
  that the game keeps (`mindState.lastMeleeThreatHarmTick`, set on every melee swing at a pawn) and a judge outside the game.
  The storeroom row was staged and judged by 526 lines of C# in a PROOF build; it is now 72 lines of Python on the mod's own
  build. On the two kept moat traces the judge gives MOD FAILURE (the melee rule off) and SUCCESS (on): the same split as the
  old row's selftest (MEASURED, checks 13 and 14).
- **An act on an exact tick and a batch with no frame between acts are one line each** (`s.act.batch()`, `s.act.damage`).
- **The help was enough for a fresh agent to lay out a whole scene, and not enough to fill it.** The fresh agent (below) used
  8 of the 10 names (all but `s.act` and `scene.attach`) in the right order with no wrong turn on the order of a session, and wrote a contract that the judge
  accepts. Every fact that it lacked was a fact about the game or the mod, not about the library: a def name, a field path, the
  arguments of a raw tool.
- **Three limits of the hands were found, each a struggle sign of `11_design.md`.** A value that no path reaches (FlowWorks'
  held flag is computed by `RM_SuperdeepTrap.IsHeld`, a method; what a lamp draws is computed by `Graphic.MatAt`); a proof
  helper compiled into a mod for one scene (Gimme Some Slack's `AerialProbe`, the only way to give a lamp its look). Each is a
  hands ticket, filed with this item.
- **What the names did not help:** a scene that needs a mod's own action (a look, a restyle) still goes through `s.raw`, and every
  such run is EXPLORED and counts for no bar. The wall lamp scene cannot pass a bar until a generic `style=` hand exists.

`[GUESS 70%]` that the hypothesis holds for scenes whose acts are generic (damage, a job, a placement) and whose evidence is a
stored value; it does not hold yet for scenes that act through a mod's own UI path.

## The fresh agent: its questions and wrong turns

The first version is kept as `design/specs/2026-11-23-bridge-v2/experiments/fresh_agent_wall_lamp_looks_v1.py.txt`. An Opus agent was given only `scene.py help` (the README, the ten pages, `help cond`, `help verbs`, `scene.py tools`) and the
old scene's claim, and wrote the wall lamp scene (131 lines, 21 tool uses, 72,033 tokens, Opus 5.5). It ran nothing. Its
own verdict: "Partly", because "the help gives no def names and no field paths. It has no non-raw way to give a thing a look,
and it shows no tool argument schemas."

Its questions (each became a `# GUESS` constant in its script):
1. How a lamp gets its look: no `s.stage` key and no verb takes a look. It chose `s.raw("jawa/gss_stage", op="set_look")`.
   **Wrong:** that tool has no look op; the look is the mod's probe (`AerialProbe`, `cplace`).
2. How a look is read: it guessed `graphicInt.path` and one texture path per look. **Wrong:** the stored look is
   `comp<CompStyleable>.styleDef` (`WallLamp_<Look>`); what is drawn has no path at all.
3. Def names: `Wall` and `Steel` (right), `WallLamp` (right), `StandingLamp` (right), `GSS_FloorCord` (**wrong**: the cord is
   `PowerConduit`); the mod name for `needs["mods"]` (right, `GimmeSomeSlack`).
4. Where a wall lamp stands and what `rot` means for it: it put the lamps south of the wall with rot 2. **Wrong:** in the old
   scene the lamps stand in front of the wall's south face, and the rotation names the side the wall is on.
5. The master switch: type and field guessed as `GSS_Settings.enabled`. **Half wrong:** the field is `enabled`, the type is
   `RimMandrake.GimmeSomeSlack.GimmeSomeSlackSettings`. The arguments of `jawa/mod_settings_field` were guessed (`type=`):
   **wrong** (`typeName=`, `action=`); `scene.py tools` cuts each description at about 150 characters and shows no schema.
6. The attributes of a `Cast` item (`.id`): right, but no page says so.
7. Whether `c.value(...)` compares with a text: yes, but `help cond` says "compare a probe with a number".
8. The run folder for `scene.judge`: it guessed `r.trace.rsplit("/", 1)[0]`. **Wrong on Windows** (the path has `\`);
   `s.run_dir` exists and no page names it.
9. A free station on `fresh:quicktest`: nothing names the map's size or its free area.
10. The rotation field: `rotationInt` (right).

Its wrong turns:
- `scene.py tools` with "restyle", "wall lamp", "master switch" and "gizmo command" found nothing; "look style" found
  `jawa/gss_stage` "only by luck", and that tool was the wrong one.
- It reread `contract.md` to learn whether a success that is true from the spawn is refused. It is (an APPARATUS FAULT), so it
  joined `c.played(60)`: the page led it right on the second read.
- It first planned the master switch as a step of the scene, then found `tune` NOT_BUILT and `raw` stamped EXPLORED, and kept
  the switch for the planted fault only.
- The restyle acts (east, west and south lamps; the cord's "All connected") have no verb; it left those rows unconverted and
  said so.
- `help cond` lists the probes without showing how to call them; it used `c.state(...) == "ok"` for "on the map".

What the pages owe after this (polish of the library's pages, `design/specs/2026-11-23-scene-library/polish.md`): `s.run_dir`
on a page; the attributes of `Cast`, `Made`, `Effect` and `Value`; `help cond` with one example for text and one for each
probe; `scene.py tools <name>` printing a tool's argument schema.

## What could not be measured

- **Every live column.** No converted scene has run in a game: both Archmagi games were held by other runs during this run
  (`game_lock.py query all`, 2026-11-24 7:36 PM PST). The live test is UNRUN; its commands are below.
- **The old scenes' bridge calls in one run.** No record counts them; the call sites are counted instead, and a call site in
  a loop is many calls.
- **Runs to the first valid run, and spoiled runs, of the old storeroom and wall lamp scenes.** Their run records were not
  read for this.
- **Whether a fresh agent with the facts of the mod (def names, field paths) would finish the scene.** One agent was asked once.
- **Whether a converted scene equals its old row on the same build.** That is the live test.

## The live test (UNRUN)

For each scene, on a free game with the scene's small list, from a clean tree:

```
python.exe src\RimMandrake\Utils\scene.py accept src\RimMandrake\FlowWorks\northstar\scene_moat_rim_wardens.py
python.exe src\RimMandrake\Utils\scene.py accept src\RimMandrake\FlowWorks\northstar\scene_moat_rim_wardens.py --plant melee_rule_off
python.exe src\RimMandrake\Utils\scene.py accept src\RimMandrake\ExplosiveKnockback\proof\scene_storeroom_pit.py
python.exe src\RimMandrake\Utils\scene.py accept src\RimMandrake\ExplosiveKnockback\proof\scene_storeroom_pit.py --plant knockback_off
python.exe src\RimMandrake\Utils\scene.py accept src\RimMandrake\GimmeSomeSlack\northstar\scene_wall_lamp_looks.py
python.exe src\RimMandrake\Utils\scene.py accept src\RimMandrake\GimmeSomeSlack\northstar\scene_wall_lamp_looks.py --plant master_switch_off
```

The moat and storeroom scenes open on ArchBig, whose Saves folder holds their fixtures. The plants differ from the ticket's in
one place: the storeroom plant is the master switch off (arm C of the old proof), not the compiled mutant "the carried pawn is
not spared", which needs a mutant build. The wall lamp plant turns the switch off before the picks, so that the pick stores no
look; whether the mod's pick still stores a look with the switch off is `[GUESS 60%]` no. The old rows stay the deciding rows
of their test tables until each converted scene was seen to FAIL on its plant and PASS on the real build in one sitting.
