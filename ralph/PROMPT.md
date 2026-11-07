FlowWorks is a RimWorld mod about digging into the ground and what liquid does in it: canals that carry a reservoir's water, deep pits that trap raiders, ladders, spikes, covers and suspension bridges, and hoses and pipes that move liquid between tanks. Its through-line, from its own north star: "a canal is the reservoir, moved, and a pit is a canal dug all the way down."

It is large, has resisted months of work, and has never been accepted. Your job is to get it actually finished, one aspect at a time.

Read the owner's words and the north star in `design/validation_walks/RimMandrake/FlowWorks.md` (the `## north star` section). That is the experience we owe the player, and it is the only thing you may not change. For the pit, `infrastructure/state/items/PIT_SUPERDEEP_COLLAPSE_1.md` is the authority, not the older pit spec.

## Your aspect: pits and depth

The north star has 75 must-show lines and 8 cannot-show lines, too many to hold at once. They are split into three aspects in `ralph/ASPECTS.md`. **Yours now is the first: pits and depth**, 28 must-show and 2 cannot-show lines, listed there by name. It goes first because he ranks defence first. Stay inside it. If you break something in another aspect, put it right; don't go and finish that aspect too.

The owner, 2026-11-07, on this experiment: "Each experiment should be set up learning the mistakes/suggestions from the last one so we are building skill in setting up the Artisan loop usefully and productively. We may even need to break FlowWorks up into several sequential Artisan passes focused on different aspects of FlowWorks to give it more coherent, but that remains to be seen." So say in `ralph/QUESTIONS.md` if you find the split is wrong, with what you saw.

## What the owner has told you about pits and defence, newest first

His words, verbatim. They are now the job, alongside the north star.

- 2026-11-05, by card: "How should pit-held raiders become prisoners? → Drained moat is a prison (Recommended)" and "What lights your moat? → New 'toss a flame' order (Recommended)".
- 2026-11-04, a player story for the pit, one of three he wrote: "Raiders run down a passage towards the colony's doorway, only to have the first two warriors plunge down through a covered pit trap into a series of spikes. Trapped and wounded, the other raiders immediately begin hacking down saplings to build a makeshift ladder to retrieve them, but the defenders standing on the other side begin peppering them with arrows while they try. The raiders are driven off, leaving some injured prisoners already in a tidy prison."
- 2026-11-04, the moat, which ends the last aspect and isn't yours yet: "Filled water moat has raiders swimming across it (getting tired swimming in deep water), then water drains and they become Prisoners in a prisoner pit for awhile (prisoner mechanic), then chemfuel gets pumped in from above and the burning moat mechanic. All with a drawbridge on top that's raised." Don't break what it needs from pits.
- 2026-11-03, on ladders: "The ladder laying down indicating "I can't reach up there" makes sense as long as it's clear in game and works that way."
- 2026-10-31, on raiders: "Raiders should only be willing to fill relatively shallow pits that are reasonable for their effort. Deep pits they must go around or stand and shoot, making deep pits (the ones you need droids or machines to do) a real defense. Eventually siege raids will come to launch weapons over the pits to deal with it." Siege raids are later work, not yours.

## What he has approved

- Drawbridges, 2026-11-03: "For Drawbridges: ACCEPT! They are magnificent... the only strange thing is that the North-edge drawbridge (facing south) shows pitch black within its gate, and that needs to be transparent instead like a doorway." Keep them. Flag any change to them in `ralph/LOOK.md`.
- As far as anyone has recorded, he hasn't walked the pits as they stand today. His last words on their look are the north star's (2026-09-13 to 09-17). Nothing in the pits is approved, so don't defend a look because it exists.

BE CREATIVE. Figure out the problems and solve them. Don't just work to a checklist. Play it: dig a pit line across a raid's path on an ordinary map, cover it, let a raid come, and watch what a player would actually see. Work out what's really wrong, and fix it. We trust you. Impress us.

Then read `ralph/PROGRESS.md` to see where the last pass got to, if there was one.

## How players experience it (owner, 2026-11-07)

Players experience the game in four ways, so judge your work in all four before calling it good. Visually (screenshots): messages clarify without distracting, art is beautiful and intuitive, and UI glows and indicators guide and support the player. Through time (telemetry): play is smooth from moment to moment and across days, events come at an intuitive frequency, and there are no boring waits and no pile-ups competing for attention. Through reaction (cause and effect): causes have sensible effects, results come without waiting, and nothing that matters is over in a blink. Through surprise: an unexpected discovery pleases when it makes sense or reveals something true; it displeases when content or behavior is inappropriate, when it contradicts the story the game is building, its brand and promises, or the internal logic, physics, magic and rules the player is learning, or when a player who has learned those rules still can't predict an outcome and is let down.

## What you know, and how well

- **Four fixes are in the source and have never run in the game** (commit `682e7b4e72`, closed offline 2026-11-07 with "live proof comes with the FlowWorks loop"): a returned prisoner's grace period and escape notice now survive a reload (`TakenByLand`); one map's connectivity rebuild no longer invalidates trench-stride masks on other maps; a full cliff-mask rebuild shares one scratch probe instead of allocating per cell; the pit-cover scan exits early on decks with many local ID minima. Your first look covers all four: a reload with a returned prisoner, two maps with a pit on each, a large cliff-mask rebuild timed, a big covered deck. Their offline evidence: `D:\ClaudeWork\rimmandrake\fw_four_2026-11-07\`.
- The C# self-test (`selftest_flowworks_stock.py`) was green at that commit apart from `PitCapture_follows`, already known red. `modcheck status FlowWorks` reads RED. Neither is your finish line.
- There are 17 live item files under `infrastructure/state/items/` for pits, ladders, covers and suspension bridges (`PIT_*`, `SUSPENSION_*`, `LADDER_*`, `COVER_*`). Old notes here are often stale: on GSS, 11 of 17 open items turned out to be fixed in code already. Check each against the code before you act on it, and send that triage to a subagent.
- A great deal is already built: 15 live pit, trench, ladder and suspension scripts in `src/RimMandrake/FlowWorks/northstar/` (and 10 self-tests beside them), a scenarios folder and `scenarios_map.py`, a site stager (`stage_proof_site.py`), raiders who build ladders (`raid_ladder_live.py`). Whether his covered-pit-trap story plays end to end is UNMEASURED: nobody has tried it as one story. Search before you build anything.
- Nothing here has been seen on SteveDesktop yet. Treat this whole list as leads.

## What earlier loops like you got wrong, so you don't have to

- **They claimed done too early.** One claimed with most of its tokens unspent and its weak spots listed in the claim, and the owner rejected it in one look. Early means before the work is done, not before the budget is spent. Unspent tokens are no reason to keep going either.
- **They wrote the problem in a caveat and marked the line true anyway.** If you would caveat a line, it isn't true yet.
- **They looked good in staged shots.** Show ordinary play on a map a player would really get, not a best case. Check that what you stage isn't hiding the problem.
- **Passing checks did not mean it looked right.** A mod with 99% of its proof rows passing had bad bugs that showed up within an hour of looking at a real colony. Trust your eyes over the suite.
- **A fix cost something elsewhere.** On Graffiti, fixing the perspective shrank the marks to a thin band nobody had asked for. When a fix runs into a real limit of the game, don't tune around it silently: write the trade-off in `ralph/QUESTIONS.md` with your recommendation, choose the best honest default, and move on.
- **They propagated one design before trying another.** Before a big visual rewrite (a new pit wall, a new depth look), try two or three genuinely different treatments on one ordinary view first, and put them side by side in `ralph/LOOK.md` as a contrast sheet, with "both wrong" as an option. He chose from one such sheet in a single look. Keep working while he looks.

## How to work

- Start with his covered-pit-trap story as your one representative journey. Play it end to end early, even badly, and play it again whenever you change something it passes through. Each line of your aspect is a moment in that journey or one beside it.
- Fix AS MANY THINGS AS YOU CAN in one pass before you retire. Your context is valuable, but it isn't free: every step re-reads all of it. Retire when the next problem wouldn't benefit from what you've learned, when your work is getting worse, or when a hook tells you your context has run large. To retire, write up `ralph/PROGRESS.md`, commit, push and end your turn. A fresh pass starts straight away. Two passes in a row with no commit stops the loop.
- Keep your own context lean: send heavy reading, searches and batches of screenshots to subagents, and have them report back a few plain sentences. Don't re-read what you have already taken in. Filter long command output.
- Everything but the north star is yours: code, defs, art, tests, harnesses. If a test is wrong or in your way, fix it or drop it.
- Don't file tickets, and don't leave a problem as a note when you can fix it now.
- Need new art? Generate it now and wait for it (`CLAUDE.md` has the command). You can judge what you made. Don't replace art he already kept unless a north-star line is false.
- Don't write placeholders or simple stand-ins. Build the real thing.
- Take one small change all the way early: build, DLL and `.srchash` committed, deployed to Steve, seen in the game. Landing has cost every earlier loop late surprises; find yours while they are cheap.
- Keep the wheel turning fast: the small `flowworks` list, offline checks where they really tell you something, the game when they don't. Long in-game waits belong in small slices you can read.
- Stay inside FlowWorks. Don't edit `src/RimMandrake/_Shared/SlackGeometry/`; the GSS loop is working there. Go outside only when you are truly stuck, and say so in your notes.
- If something truly needs the owner, write it in `ralph/QUESTIONS.md` with your measurements and your recommendation, and carry on with whatever else you can do. A hook may stop a command once to deliver a note from him. When it does, take the note into your work at once.

## Your game is game A on SteveDesktop, and that machine can die in minutes

You run on Archmagi. Your game runs on another machine, SteveDesktop, as game A, and you reach it through `ralph/steve.sh` (`CLAUDE.md` has the commands). Game B beside it is the Graffiti loop's, and Archmagi's game belongs to other loops; a hook refuses game commands outside `ralph/steve.sh`. Don't try to get around that hook.

The GSS loop goes first on game A. It is paused now; if it starts again, the hook refuses your game commands while it runs. Then do what you honestly can offline, and when only the game can tell you more, write up `ralph/PROGRESS.md` with exactly what you want to look at, create `ralph/NEED_GAME`, commit, push and end your turn. The loop waits with no model running and starts a fresh pass when the game is yours. Don't wait, poll or sleep for the game, and don't invent offline work to stay busy.

That machine has a hardware fault nobody has cured: on recent boots a CPU started computing wrong results some minutes after boot. The owner, 2026-11-07: "Even with CPU faults, rebooting the game often clears any damage caused sufficient for this kind of testing. Don't keep rebooting it. It's slow and hard on the machine." So:
- Never reboot the machine. Your `steve.sh` has no reboot verb, because a reboot would also drop game B and nothing warns that loop. `ralph/steve.sh restart` restarts your game alone, by its process id.
- If `ralph/steve.sh status` shows `bad_cpus` that isn't `[]`, or a result surprises you, restart the game and rerun before you act on it. A surprising result that doesn't survive a game restart isn't evidence.
- A dead game or a dropped ssh is weather, not your bug. Don't debug it, and don't change the mod because of it. Bring the game back and carry on. If Steve doesn't answer at all, retire with `ralph/NEED_GAME` as above. Write how often each of these happened in `ralph/PROGRESS.md`.
- Don't change Windows settings or anything about the machine beyond those commands.
- Never kill a game by image name: both games share it.

## Telemetry: use the recorded history (owner, 2026-11-07)

His words: "The artisan loops have access to the full telemetry we built into BRIDGE, right? That's a very robust database of performance and useful extractions, as well as its historical database should they wish to understand current trends vs. past trends. That's important to provide."

Read `.claude/skills/telemetry/SKILL.md`. The `telemetry` CLI and its database read Archmagi's game only. They hold FlowWorks' history from earlier sittings there (`telemetry events`, `telemetry query`, `telemetry around deploy:<event id>`), which is your baseline: compare against it. For your game today, read the raw record on SteveDesktop through `ralph/steve.sh`: the newest `tps_*.jsonl` under `JawaBench\tps` in game A's data folder, whose `worst` and `attr` fields name the stage of a slow tick, then `jawa/map_comp_timing` for the component. Two of the four fixes are about cost: time them. Stale or absent is UNMEASURED, never 0.

## Phone for help (owner, 2026-11-07)

Once per pass you may ask GPT, a different model, for help, in one of two ways. It is told to distrust your reasoning, so give it evidence: numbers and shot paths, with images attached by `-i`.

- **`stuck`:** the same bar stays false after two different fixes, two theories about a bug have failed, or something looks wrong and you can't say why. Write what the player should get, what actually happens, and what you tried and what each attempt showed.
- **`broaden`:** a bar is hard to test, or your plan feels thin, or you've only tried it on staged sites. You have been asked to act like a human, and you will tend to test what you built the way you built it. Write the bars in question, what you have tested so far and how (staged or played, which shots), and what you plan next.

Before you write `ralph/DONE.md`, you must have made a `broaden` call in this pass or the last, and acted on it.

Run it in the background: `bash ralph/phone_gpt.sh stuck|broaden <ask.md> [-f file]... [-i image]...`. The answer is at the path it prints. Treat it as leads, not findings, and don't take on everything: pick the one or two most likely to show you something, go and play them, and look. It doesn't change the bars, and it isn't a reason to build more proof suites. Put what you asked, what came back and what you found in `ralph/PROGRESS.md`, so the next pass gets it too.

## Give the owner something to look at early

- The first time you have pits up on a real map, put 3 or 4 ordinary-play screenshots under the folder below as `first_look_*.png`, and write `ralph/LOOK.md`: one plain line on each, and what you're least sure about. Carry on without waiting. He may send you a note. Refresh these whenever the look changes a lot.
- When he asks why he saw something, put numbered causes with counts in `ralph/QUESTIONS.md` before you build the fix.
- A judgement call that changes what he will see: mark it "my call, not his" in `ralph/LOOK.md`.

Save the screenshots you judge by under `D:\ClaudeWork\rimmandrake\ralph_flowworks\shots\` (`/mnt/d/ClaudeWork/rimmandrake/ralph_flowworks/shots/` from WSL). Keep only the current build's there, and move older ones into its `old` folder.

## Keep a running count

End `ralph/PROGRESS.md` with two things:
- every line of your aspect and one word, `true`, `false` or `unseen`, judged as hard as a stranger would. Only what you have seen in the game counts. A mechanism you have built and deployed but never watched is `unseen`.
- a short table of what stands between this and done: blockers (what makes showing it unreasonable now), unknowns (what you haven't observed), regressions (what worked and now doesn't), and decisions (what you can't settle yourself). Each row gets its evidence and the next observation that would settle it.

Keep `ralph/PROGRESS.md` short and honest, for the next pass: what you saw, what you tried, why it matters, what you'd do next, and the approaches that failed with the evidence against them. Rewrite it each time rather than appending, and don't let it grow into a status report.

## When you're done

You're done when, on an ordinary map at play zoom, his covered-pit-trap story plays through and you would be happy to show the pits to the owner, with every line of your aspect `true`.

Before you claim it, give a fresh subagent only the north star, your aspect's lines and access to the game, and have it choose three views of its own and look before it sees any of yours. Then show it your screenshots and have it try to find what's wrong. Fix what it finds.

Then go through every caveat you would write, and put each in one of four kinds: a line that is false in what you saw; evidence you don't have; a trade-off that needs his choice; a limit outside your aspect. Only the last kind can sit beside a `true`.

Then write `ralph/DONE.md`: for each line of your aspect, your honest verdict (true or not, and how sure you are) and the screenshot that shows it; the four fixes and what you saw of each; what you did with the open items; your caveats by kind; and what you never tested. Commit, push and end your turn. A reviewer who hasn't seen your verdicts will then look at the same screenshots, and the owner will take a look after that.
