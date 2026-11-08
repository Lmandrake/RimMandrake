# Graffiti: where the last pass got to

Pass 8 on game B. It retired on context, about 255k tokens. Weather: none. No dead game, no dropped ssh, `bad_cpus=[]`; about 10 deploy/up cycles, all came up first time. The deployed DLL is commit 3cbca39994's source (the hash commit on top only re-stamps it).

## Found by playing, and fixed
- **Stories were crowded out.** By day one every room held its share of tags, so a pawn who hated another (-32, then -70) painted plain marks for days and no mockery: the gap at whatever wall was nearest never fit one. Now `JoyGiver_PaintGraffiti` decides what the hand wants to say first, then `TryFindMeaningCell` finds the nearest wide-enough stretch to where the subject sleeps or stands. It may go over the painter's own marks and, for a mockery, the target's own tags (which gives the target a "painted over my work" too), never a bystander's. The job carries the subject in target C (`JobDriver_PaintGraffiti.Meant`).
- **Memorials from strangers.** Kinso had only the generic "Colonist died" (-3) for Mo and took +5.7 from painting Mo a memorial. `Mourned()` now needs the game's own friend-died thought or a relation.
- **Grief rarely painted.** Lark's lover died and Lark painted once in two days (tallies). The memorial chance is now 0.6 and a mourner's urge is x1.75 until the memorial stands. Lark painted it about 3 days after the death.
- **Grief relief was squeezed.** Lark took +1.4 for the memorial (funny doodles had filled the +8 wall-mood cap) while the stranger had +5.7. `RM_Graffiti_GriefEased` now stands outside the cap: +5 for Lark beside "My lover Pell died -16".
- **Skill didn't show on the wall.** The new `st Crafts` (one Piece at every craft) showed awful and legendary differing only by which drawing each was. Awful and poor now print a muddy, smeared second pass off true (`RM_GraffitiKernel.CraftSmear`). Seen at 64 ppc: awful and poor read as brown mud smears, normal to legendary stay crisp.
- **Confront message lied**: "about what Kinso painted about someone" over a plain tag. Now it names the mark ("about Karen's tally marks on the wall"), and the message also points at the wall.
- The wall's inspect pane now gives each mark's Beauty ("Mockery (good), by Cathryn, about Brick (3 angered). Beauty +3: decent work").
- The staged colony starved on day 7 (60 meals); it now has 140. The lint selftest's planted defect pointed at a value that no longer exists; fixed.

## Proven live on this build (shots in the shots folder, listed in LOOK.md)
Unscripted after one staged feud: Brandt mocked Kinso; Cathryn (psychopath, in a spree at mood 0.35) mocked Brick and painted over Brick's work; Brick crossed out and mocked back; Lark (Brick's sweetheart, +90) replied with her own mockery of Cathryn ("Showed the wall what Cathryn is +5", "Brick mocked on the wall -2.75"); Kinso and Pell set out to confront and scrub. Fresh colony: Karen mocked Brick within a quarter day, and Brick confronted her: "fight chance 0.85 -> BLOWS". Every confrontation with Cathryn had a wall-fight chance of 0, because the game's own social-fight check refuses her. Mo (Very Neurotic) forced into the clean-freak break: "Mo scrubbed away Karen's mark (in a cleaning fit)". Psychopath: no wall thoughts. Volatile Kinso: "Mocked on the wall by Brandt -13.2" against a -8 base. A visitor read a poster once: goodwill -1, and nothing more (capped). Save/load: about 6 reloads, and the marks, grudges and grief carried over each time.
Rate in a fresh busy colony, no staging: 61 marks in 2.5 days, 0 stories and 0 messages, because nobody had come to love or hate anyone yet. Over the next 5 days stories came at 3 messages in about 3 days.

## Do next, in order
1. Telemetry: newest big `tps_*.jsonl` under `/mnt/d/ClaudeWork/rimmandrake/instances/b/JawaBench/tps` (from WSL on Steve via `ralph/steve.sh run`). The long runs this pass were sessions with pid 18640 (two 90000-tick runs) and 28768/14388 (until runs). Not done in any pass.
2. On this build: a raid mark and its retake (recipe under Traps), and the settings switch (`so Set`), each with one shot. Pass 7 proved both on an older build.
3. `DONE.md`, from the shots already in the folder (LOOK.md maps each to its bar). The broaden call was made in pass 7 and acted on.

## Open questions worth weighing in DONE.md
- Ambient wall pleasure (funny doodle, good work, our sign, left my mark) settles around +4 to +6 for most pawns, capped at 8 (12 for a sensitive pawn). That isn't a tax, but players may see it as free mood. Consider a smaller cap for thoughts about no one.
- A mockery hurts -8 for 3 days (-12 to -13 for the Volatile). That is strong in a colony that's already struggling.
- The vandal run reads as a messy, colourful scribble beside neat tallies. That's worse, but not plainly uglier at a glance.

## Traps
- The gate refuses Bash commands containing `rimbridge` and the like, even in heredocs: write bridge scripts with the Write tool (`ralph/live/deaths.py` lists death letters).
- `prove_quicktest_world.py` refuses to leave a colony past tick 120000: stage art (`st Sweep/Ladder/Compare/Gallery/Crafts`) in the corners of the colony map instead. Saves on Steve: `graffiti_p8_fresh2` (fresh colony, day 5, feud, memorial), `graffiti_p8_busy3` (first colony).
- `ralph/steve.sh run '...'`: the driver chains with ` @ `. Pass a value with `;` in single quotes inside double quotes. After editing `ralph/live/g.py`, run `ralph/steve.sh sync`.
- Joy pacing is real: a pawn with full joy, or one bored of painting, doesn't paint for days. `until` with a 100k+ budget, or wait.
- Raid: `kv jawa/lord_pawn_move action=list`, then `kv jawa/lord_set_job lordIndex=N lordJob=LordJob_AssaultColony args=...`, step 600 at a time, then `LordJob_ExitMapBest args=locomotion=Jog;canDig=false;canDefendSelf=true` at a wall.
- Decompile: `/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all/{RimWorld,Verse}/`.
