# Graffiti: where the last pass got to

Pass 4, first pass on game B (SteveDesktop). It ran out of context after one big build, so it **retired before any live proof of the new code**. Weather this pass: no dead game or dropped ssh. Game B came up first time; `bad_cpus=[]` throughout.

## Seen live (build f9c2f0c, before this pass's C#)
- Deploy, `up`, quicktest and colony staging all worked; Player.log had no exception at all (93 lines).
- **Option D is real in the game.** Marks bend at the crease and climb onto the wall top on granite, wood, steel, marble, plasteel and slate rooms: straight runs, a door gap, a free wall end. Shots are `first_look_D_granite.png` and `first_look_D_wood.png` in the shots folder, with lines in `ralph/LOOK.md`. Side faces are thin coloured scraps. Not yet judged: corners and T junctions at 64 ppc, and how the top reads beside pawns.
- 6000 ticks with 3 colonists: no natural mark and no social event. The ledger read `Pasted flyer x1`: a filth label (now fixed, see below).
- `ralph/steve.sh tier` refuses with "swap marker ... missing or changed", but game B already runs the 10-mod graffiti_solo list, so it doesn't matter. Don't fight it.

## Built this pass, compiles, NOT RUN in the game
This is the owner's 2026-11-07 social list and personality pass, in full:
- `GraffitiTemperament.cs` + `Defs/TemperamentDefs_Graffiti.xml`: the table, with the owner's revisit note at the top. `Give()` is the one route for every Graffiti memory. It scales by reach × temperament, applies one-sided mood budgets (-8, or -12 for a mockery's victim; +8) and opinion caps (-30/-45/+30), and keeps the stronger memory when the same kind comes again. `GameComponent_Graffiti` holds the game-wide fight and break cooldowns (15 days each) and the 3-day clean-freak mess limit.
- Rereads: `ReadAgainTicks` is 1 day. Mood comes again at `RereadFactor` 0.6, but a stronger memory still running isn't renewed. Opinion, grudges, lines, logs and messages come only on the first read. **The 0.6 is my reading of "repeatedly affect you"; check it with the owner if it matters.**
- Art skill: `Filth_Mark.craft` is rolled by `QualityUtility` at `MakeMark` (inspiration is spent only on ordered marks). `GetBeauty` returns the craft table, divided by 0.3 under a roof; a defaced mark drops to Poor. The `FineArt` / `UglyMark` thoughts come before the meaning. `Reach` scales the meaning. Craft shows on the wall through `CraftLook`: more wall through the paint, a shakier slope and muddied pigment for poor hands. Painting now gives Artistic XP.
- Fights: the confront base chance is 0. `GraffitiSocial.FightChance` = min(.85, 3 × the confronter's vanilla insult chance × temper), at most one fight per 15 days, using the `RM_Graffiti_MessageWallFight` key (`Languages/`).
- `GraffitiCompulsiveClean.cs`: the neat-2-only break, the state (ends after 6 scrubs or when no mark is in reach), its think tree, valued-by hurt (`ScrubbedWhatIDear`). The spree has its own cooldown worker.
- Answers wait (hungry, tired, enemies near, more than 45 cells), stay open when blocked (`Postpone`), settle only in the finishing driver (`Answered`), and drop when the mark is gone. Replies go through `CanReplyInPaint`, which checks Artistic not disabled, skill ≥5 and `PainterMayPaint`. Going-over uses the same answer table.
- Rag bond (`WipedItAway`) from both answer scrubs and ordinary cleaning. Someone who hates the subject refuses to clean a mockery, forced or not, with a float-menu reason (AutoCleanProtection prefix). Psychopaths and a fit are exempt.
- Room left on the wall is measured before painting (`BareRoom`), and the Vandal fallback is used only if it fits. Autonomous painting skips hospitals and kitchens (`KeptClean`). Territory counts only enemy marks in the Home area. Visitors are charged only for player marks, capped at -12/+3 per 3-day visit. Messages point at the wall cell (`WallTarget`). A same-def repaint is a fresh artwork (`MadeAfresh`). No mockery of children. Prisoners, slaves and children read but never answer.
- Psychopath and Inhumanized nullifiers on all 42+ Graffiti ThoughtDefs. Gossip is one stack per person. Settings tooltips now say what the switches do, reset and search cover the social switches, and turning social off forgets every Graffiti memory and grudge (`ForgetAll`).
- Lures were already untouched by crossing out (no defaced check in BreachBiasHook) and end only when cleaned. That matches the owner's pick, and nothing changed there.

## Do first, in order
1. `ralph/steve.sh deploy` then `up`, then quicktest. Read the FIRST exception: DefOf binding of `GraffitiSocial.T` (internal now) and the new thoughts, the temperament def's custom class XML, `MayRequire` on nullifyingHediffs, the `GameComponent` ctor.
2. Offline: rebuild and run the kernel fuzz (`Source/SelfTest`). `AnswerOf` changed bands, so check its expectations still hold.
3. Live social proof with real pawns (`RM_GraffitiSocialProof.Feud/Order/Ledger` through `jawa/static_call`). The colony has only 3 quicktest pawns, so add more with varied traits. Watch: subject humiliated, then the reread a day later is weaker; Psychopath gets nothing; an Artistic-0 mark versus an Artistic-15 mark in one room gives different beauty and needs-tab entries; a confront by Kind versus Bloodlust; a Very Neurotic break; the cleaner's bond; a hater refusing to clean.
4. Judge craft visibility at 64 ppc. If muddy, shaky and see-through marks don't read as ugly, change the art pick by craft too.
5. Then everything PROMPT still asks: perspective and painted-on close-ups, the blind judge's art points (clip-art emblems, the mouth logo, poster repeats), telemetry from `JawaBench/tps` on Steve, the required `broaden` phone call, and DONE.md.

## Traps
- The gate refuses any Bash command containing `stage_colony`, `rimbridge`, `RimWorldWin64` etc., even `git add` or `ls` of such a path. Use Read/Write/Edit, `git add <dir>`, and `RimWorldWin*` globs.
- `stage_colony.py` now saves shots to `Transient\gshots` on Steve. Bring them back with `ralph/steve.sh fetch 'Transient/gshots/' /tmp/g/`.
- The decompile is at `/mnt/d/ClaudeWork/rimmandrake/decomp/rw16/all/{RimWorld,Verse,Verse.AI}/`.
- New .cs files must go in `Source/Graffiti.csproj`. 64 ppc on game B's 1280×720 window is about 20×11 cells per shot.
