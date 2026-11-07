Graffiti is a RimWorld mod that should make a colony feel written on: all the various kinds of graffiti, punk and urban, plus sigils from the game's ideoligions.

Read the owner's own words and the north star in `design/validation_walks/RimMandrake/Graffiti.md` (the `## north star` section). That is the experience we owe the player, and it is the only thing you may not change.

BE CREATIVE. Figure out the problems and solve them. Don't just work to a checklist. Play the mod, look at what a player would actually see, work out what's really wrong, and fix it. We trust you. Impress us.

## What the owner decided on the social layer

He read an outside review of your social layer, written before anything of it ran in the game, and chose these by card on 2026-11-07. Full review, with the reasoning and code references: `D:\ClaudeWork\rimmandrake\ralph_graffiti\gpt_review\gameplay_review.md`. Treat its claims as things to check, and these choices as his. Do them along with what you'd do anyway, and keep them small.

- **Walls:** paint dies with its wall, and nothing floats when a wall goes. Draw it on the wall as you do now. Keep the mark's `Position` on the floor cell unless you carry its beauty another way: `CellBeauty` ignores anything on a cell holding a full-fillage wall (see the personality pass).
- **Rereads (owner, card 2026-11-07, replaces his earlier pick):** "Seeing the same mark repeatedly SHOULD repeatedly affect you, but no more than once per day." By card the same sitting: mood repeats daily, opinion and grudges change once, on the first read.
- **Makers and mourners (owner, card 2026-11-07):** a memorial comes from someone "actually grieving and helps them feel better." "All mark makers get a small mood buff for having made it (both mood buff and counts as a fun activity for recreation purposes)."
- **Temperament table (owner, card 2026-11-07):** he accepted the personality pass as written: "(1) is excellent, but make a note: we will likely add additional personality traits later for the different races, so we should revisit these any time we mess with personalities." Say so in a comment at the top of `Defs/TemperamentDefs_Graffiti.xml`.
- **Answers:** they wait their turn (refused when hungry, tired, enemies near or the target far). A failed or blocked answer stays open, and one whose mark is gone is dropped. Artists obey the normal table and `PainterMayPaint`, including Artistic-disabled pawns. Gossip stacks once per person.
- **The base:** measure a mark's real width before painting, so nobody erases a neighbour by accident. Autonomous painters skip hospitals and kitchens; orders may still paint there. Only enemy tags in the Home area count against colony mood.
- **Lures:** leave them working when crossed out; full cleaning ends them. His words: "Crossing out a lure shouldn't stop it, but totally cleaning it would. A raider wouldn't be fooled because someone crossed out instructions."
- **Settings tell the truth:** the painting switch also stops replies, the tooltip is corrected, and reset and search cover the social switches.
- **Visitors:** charge only for your own faction's marks, capped per visit.
- **Messages:** they point at the wall.
- **Cleaning a mockery bonds subject and cleaner**, and his words: "if a person hates the subject, they will refuse to clean the insult". Check a cleaner on an ordinary filth job as well as one answering.

And one thing he added, which matters as much as any of them:

> "Please ensure that a person's art skill goes into the art's effect. A poor artist will paint such a bad graffiti mark that it is ugly, harms a room's beauty, and gives mood debuffs. But a highly skilled artist is actually making art. It is beautiful, improves a room and people's moods. And this combines with slanderous art: it can actually make you really angry as well as improve your mood from the beauty of it. Emotions are complicated."

He also said Luminous Pigments will later make graffiti luminous, shimmering, more beautiful and permanent. Don't build that. Don't make it hard either.

Prove the social layer live: `readers_feel_the_wall`, then answers finishing with fights that have causes, then the mod standing alone, from the tests section of that review, are the first to try. They're proposals, so improve them.

He then asked how all this meets the many kinds of people, and he chose how fights work:

- **Personality:** the table is on main, not on this branch, at `/home/mandrake/rm/bench/design/RimMandrake/graffiti_personality_pass_2026-11-07.md` (mirror: `D:\Luke\dev\RimMandrake\design\RimMandrake\graffiti_personality_pass_2026-11-07.md`). Read it. Its BUILD NOW rows are the job, and its numbers are proposals you may tune in play. He wants psychopaths not to care, sensitive people to feel more both ways, and clean freaks to be able to break into compulsive cleaning.
- **Fights:** his words, "Scale it with temper". The fight chance on a confront scales with the confronter's temper, as that table sets out, not a flat 0.75.
- **The north star:** he added the social bars, art skill and personality to it, so `DONE.md` gives a verdict on all of its lines, not only the first ten. They read as DRAFT until he re-validates. Build to them anyway.
- **Aurebesh** isn't this loop's concern.

## What the owner just decided

His words, 2026-11-07, on the contrast sheet and on what this mod is for:

> "Go with D. I was against touching the top of the wall, but the extra space does add something. I think we have a winner! ... And did you test the social implications of the mod? It's more than just art display."

These two are now the job, on top of his earlier demands below.

**1. Build option D for real.** Look at `D:\ClaudeWork\rimmandrake\ralph_graffiti\contrast\contrast.md` and `D_bolder_and_climbing.png` beside it: bolder paint inside the wall face, and marks that climb onto the top of the wall. That picture is an offline composite. The bolder paint was a filter and the bent geometry does not exist in the game. Make it true in the running game, on real walls, at play zoom, through straight runs, corners and junctions, where a mark on the top must still read as the same paint. A side face stays a scrap unless you find better.

**2. The social side is untested, and mostly unbuilt.** The mod is not a wallpaper. Earlier he asked for "socially infuriating graffiti or amusing graffiti". Measured today: one ThoughtDef exists (`RM_Graffiti_ViewedHostileMark`, -2 mood); `About.xml` promises colonists react to a rival's tag differently from a friend's; the design promises about ten thoughts and relation reactions; own-faction and ideoligion reaction slots exist in code with nothing assigned; there is no opinion, relationship, faction goodwill, territory or retaliation effect. The live proofs of the spree, raid-exit tag, sigil, going over a rival's mark, unease and clean protection ran on sha a70b78a8af90, before your C# commits, and none has run on your build. Your north-star bars are all about appearance, so they never asked.
Read the design, then make the graffiti matter between people: who paints what, who is angered, amused or moved by it, and what they do about it. A player should be able to watch it happen and read why on the pawn. Prove it in a real colony with real pawns on your build, including what already exists. Say plainly what you left out and why.

Put early shots of each in the shots folder as `first_look_*.png`, with one plain line on each in `ralph/LOOK.md` and what you're least sure of, as soon as you have them in the game. Carry on without waiting. He may send you a note.

## What the owner told you earlier

You claimed done, and he looked. His words, 2026-11-07:

> "Make the art look like it's on the WALLS in perspective correctly, ok? Not just plastered over the wall. Actually in correct perspective. Then make it look like it's been smeared or painted on, not just a bad pop art sticker. It must look appropriate in-game."

These two are now the job. Everything else you do serves them.

**1. Correct perspective.** A mark lies in the plane of the surface it is painted on, and the camera sees it the way it sees that surface. Work out how this game actually projects a wall: the top surface, the visible front face, and where the crease between them falls for each facing. Then draw each mark with real geometry (a mesh or a shear fitted to that face), not a level quad laid over it. A mark on a front face is foreshortened by that face and stops at its edges and crease. It doesn't lie flat across the crease, stick out past the wall, or run across a corner. Decide what a wall with no visible face (one seen edge-on) should carry, including the honest answer "nothing, or only a sliver". A hand's tilt and size stay, but inside the plane. Solve the geometry offline first: sweep every facing, wall material, corner and mark width in Python and look at the results, then build the C#, then use the game for the final look.

**2. Painted on, not stuck on.** It should look like a hand put paint or a smear on that wall: patchy coverage, uneven pressure, a dry-brush or spray falloff at the edges, runs that fall straight down the face, the wall's own surface and grain showing through, weathering, some of it half gone. No clean die-cut edge, no even outline around the whole shape, no flat bright pop-art fill. The colours should sit in the wall's light and in this game's palette, so a mark belongs to the same world as the wall under it. Some of this can come from the art and some from how it's drawn over the wall. Find out which works, in the game at play zoom. Marks must still read as marks at play zoom, so don't fade them into dirt.

A reviewer also made these points about the last result, in `D:\ClaudeWork\rimmandrake\ralph_graffiti\blind_judge_verdict.md`. Read it:
- A third of the emblems (droplet, leaf, tree, pick and mountain, paw, pipe) are tidy clip-art with drips on.
- The pink mouth with its tongue strongly recalls a real band's logo. Replace it.
- Nothing shows which marks are the ugly ones, so make that visible.
- Poster pairs repeat close together, and the same tags recur with no variation.
- The shots looked staged: unpowered benches, an unfuelled stove, colonists on the same tiles on two days. Show a colony that looks lived in.

Your earlier done claim is in `ralph/history/DONE_pass1.md`. It was not accepted, so don't lean on its verdicts. Redo the art wherever the old art can't meet this. You have plenty of tokens, and generating new art is expected.

## Your game is game B on SteveDesktop, and that machine can die in minutes

You run on Archmagi. Your game runs on another machine, SteveDesktop, and you reach it through `ralph/steve.sh` (`CLAUDE.md` has the commands). It is that machine's second game, game B, and it is yours alone. Game A beside it belongs to the GimmeSomeSlack loop, and Archmagi's game belongs to other loops. A hook refuses game commands on this machine. Don't try to get around that hook.

Never touch game A: don't stop or restart it, don't use its lock, don't call its bridge on port 5174, and never kill a game by image name, because that takes both. `ralph/steve.sh` acts on game B alone. Both games load from one Mods folder, so write only Graffiti there. Game A's loop writes GimmeSomeSlack and FlowWorks; never deploy those, and keep them off your mod list.

That machine has a hardware fault nobody has cured: on recent boots a CPU started computing wrong results some minutes after boot. Turbo is off for this trial, and the Conductor watches the faults in parallel. **Do not reboot the machine.** A reboot would also take game A, and `ralph/steve.sh` has no such command. The owner, 2026-11-07: "Even with CPU faults, rebooting the game often clears any damage caused sufficient for this kind of testing. Don't keep rebooting it. It's slow and hard on the machine." So:
- Uptime is not a reason to do anything. Run the whole proof whenever you want it.
- If `ralph/steve.sh status` shows `bad_cpus` that isn't `[]`, or a result surprises you, restart the game (`ralph/steve.sh down`, then `up`) and rerun it before you act on it. A surprising result that doesn't survive a game restart isn't evidence. Note in `ralph/PROGRESS.md` when that happened.
- A dead game or a dropped ssh is weather, not your bug. Don't debug it, and don't change the mod because of it. Bring the game back up and carry on. Write how often each of these happened in `ralph/PROGRESS.md`.
- Don't change Windows settings or anything about the machine beyond those commands. Other work is diagnosing it.
- Don't wait, poll or sleep for Steve. If `steve.sh` says STEVE_UNREACHABLE, or game B won't come up after a retry, do what you can offline. When only the game can tell you more, write `ralph/PROGRESS.md` with exactly what you want to look at, create `ralph/NEED_GAME`, commit, push and end your turn. The loop then waits with no model running and starts a fresh pass when Steve answers. Don't invent offline work to stay busy.
- Do offline first what offline can answer, and take your screenshots in short batches. `ralph/steve.sh fetch` brings them back to look at.

Then read `ralph/PROGRESS.md` to see where the last pass got to, if there was one.

How to work:

- Fix AS MANY THINGS AS YOU CAN in this one pass before you retire. Your context is valuable, so don't throw it away after one fix. Retire when the next problem wouldn't benefit from what you've already learned, or when your context is getting heavy and your work is getting worse. To retire, write up `ralph/PROGRESS.md`, commit, push, release the bridge, and end your turn. A fresh pass starts straight away.
- Everything but that section is yours: code, defs, art, tests, harnesses. If a test is wrong or in your way, fix it or drop it. The eight clauses in `graffiti_v1_live_proof.py` are tools somebody made, not your finish line.
- Don't file tickets, and don't leave a problem as a note when you can fix it now.
- Need new art? Generate it now and wait for it (`CLAUDE.md` has the command). Don't file it or queue it, and don't move on wondering whether it's ready. You can judge what you made.
- Search before you build: don't assume something isn't implemented. This project often already has it.
- Don't write placeholders or simple stand-ins. Build the real thing.
- Keep the wheel turning fast: the small `graffiti_solo` list, offline checks where they really tell you something, the game when they don't.
- Use subagents for heavy reading and searching, so your own context stays clear. Only one thing at a time may drive the game.
- Stay inside Graffiti. Go outside it only when you are truly stuck on something there, and say so in your notes.
- Keep `ralph/PROGRESS.md` short and honest, for the next pass: what you saw, what you tried, why it matters, what you'd do next. Rewrite it each time rather than appending, and don't let it grow into a status report.
- If something truly needs the owner, write it in `ralph/QUESTIONS.md` and carry on with whatever else you can do.

Keep only the screenshots of the current build in the folder below; move older ones into its `old` folder. Save the screenshots you judge by under `D:\ClaudeWork\rimmandrake\ralph_graffiti\shots\` (`/mnt/d/ClaudeWork/rimmandrake/ralph_graffiti/shots/` from WSL).

You're done when, in a real colony at play zoom, you would be happy to show this to the owner. Then write `ralph/DONE.md`: first, your honest verdict on option D and on the social side, each with the live evidence, then on his two earlier demands above (true perspective on every facing, and painted rather than stuck on), each with a close-up and a play-zoom screenshot. Then, for each of the ten north-star lines, your honest verdict (true or not, and how sure you are) and the screenshot that shows it. Commit, push, release the bridge and end your turn. A reviewer who hasn't seen your verdicts will then look at the same screenshots, and the owner will take a look after that.

## Telemetry: use the recorded history (owner, 2026-11-07)

His words: "The artisan loops have access to the full telemetry we built into BRIDGE, right? That's a very robust database of performance and useful extractions, as well as its historical database should they wish to understand current trends vs. past trends. That's important to provide."

Read `.claude/skills/telemetry/SKILL.md` and query history before re-measuring or guessing: `telemetry at "<time>" --span 2m`, `telemetry around deploy:<event id>` (before and after, per speed), `telemetry bridge --since 1h`, `telemetry events`, `telemetry flight`, `telemetry query`, Grafana at http://localhost:3000. For a stall, read the newest `tps_*.jsonl` under `JawaBench\tps` in the game data folder: its `worst` and `attr` fields name the stage of a slow tick. It is a lead, then `jawa/map_comp_timing` names the component. Stale or absent is UNMEASURED, never 0. Compare your build with earlier ones, and check performance at each milestone, not only at the end.

Your game is on SteveDesktop, and this telemetry CLI and its database read Archmagi only, so it says nothing about your game today. Read the raw record on SteveDesktop through ralph/steve.sh: JawaBench/tps under that game data folder.

## How players experience it (owner, 2026-11-07)

Players experience the game in four ways, so judge your work in all four before calling it good. Visually (screenshots): messages clarify without distracting, art is beautiful and intuitive, and UI glows and indicators guide and support the player. Through time (telemetry): play is smooth from moment to moment and across days, events come at an intuitive frequency, and there are no boring waits and no pile-ups competing for attention. Through reaction (cause and effect): causes have sensible effects, results come without waiting, and nothing that matters is over in a blink. Through surprise: an unexpected discovery pleases when it makes sense or reveals something true; it displeases when content or behavior is inappropriate, when it contradicts the story the game is building, its brand and promises, or the internal logic, physics, magic and rules the player is learning, or when a player who has learned those rules still can't predict an outcome and is let down.

## Phone for help (owner, 2026-11-07)

Once per pass you may ask GPT, a different model, for help, in one of two ways. It is told to distrust your reasoning, so give it evidence: numbers and shot paths, with images attached by `-i`.

- **`stuck`:** the same bar stays false after two different fixes, two theories about a bug have failed, or something looks wrong and you can't say why. Write what the player should get, what actually happens, and what you tried and what each attempt showed.
- **`broaden`:** a bar is hard to test, or your plan feels thin, or you've only tried it on staged sites. You have been asked to act like a human, and you will tend to test what you built the way you built it. Write the bars in question, what you have tested so far and how (staged or played, which shots), and what you plan next.

Before you write `ralph/DONE.md`, you must have made a `broaden` call in this pass or the last, and acted on it.

Run it in the background: `bash ralph/phone_gpt.sh stuck|broaden <ask.md> [-f file]... [-i image]...`. The answer is at the path it prints. Treat it as leads, not findings, and don't take on everything: pick the one or two most likely to show you something, go and play them, and look. It doesn't change the bars, and it isn't a reason to build more proof suites. Put what you asked, what came back and what you found in `ralph/PROGRESS.md`, so the next pass gets it too.
