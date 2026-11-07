Gimme Some Slack is a RimWorld mod that replaces invisible conduit with what power really looks like: too-long extension cords in loose loops across the floor, tangles of wires and power strips, overhead lines on masts, and broken ends that spark if live and lie dead if not.

The owner has walked this mod and said: "GimmeSomeSlack all looks great! Verified." So this is not a mod to reinvent. Your job is to finish what is left and keep what he approved. Change how it looks only where a north-star line is false or the plan below owes it.

Read the owner's own words and the north star in `design/validation_walks/RimMandrake/GimmeSomeSlack.md` (the `## north star` section). That is the experience we owe the player, and it is the only thing you may not change.

## What the owner just told you

The owner, 2026-11-07, looking at the game: "In GSS the spark of the cut powerline should follow the writhing edge of the cable. Right now it writhes around while the sparking portion stays in the center, a very strange look."

The owner, 2026-11-07, looking at the game: "Why in GSS did I see three separate cables coming out of a doorway to go to a single terminal node of conduit? There were multiple cables for no reason. Not power lines, just normal cables... that's not ok."

Find out why this happens, fix it, and put the cause in ralph/QUESTIONS.md in plain words so he gets his answer.

Fix this first: the spark belongs on the moving end of the cable, wherever the cable's writhing puts it.

What is left, as far as we know. Check each one against the code first, because this project often has it built already, and these notes may be stale:
- `design/concepts/GimmeSomeSlack/plan.md`: one owed change (Modern junctions draw the long power strip), a cord-shape instrument, and the scenes in `scenes.json`.
- The open items, `infrastructure/state/items/GSS_*.md`. Most are verified code-review findings or missing proofs. Fix the real ones, and record in your notes any that turn out to be false or already fixed. You don't have to close them on the ledger; the Conductor will do that.
- The last recorded live run was 113 PASS, 1 FAIL, 5 UNMEASURED, on 2026-10-15, and the code has moved since. `northstar/proof_all.py` is the one live proof. Its rows are tools, not your finish line, so fix a wrong one or drop it. A row that can't measure is not a pass.

BE CREATIVE about the problems. Don't just work to a checklist. Play the mod, look at what a player would actually see, and work out what's really wrong. We trust you.

Then read `ralph/PROGRESS.md` to see where the last pass got to, if there was one.

The game is shared, and you wait your turn:
- Another Ralph loop, on Graffiti, has the one game first. While it runs you work offline, and a hook refuses game commands. Don't try to get around that hook, and don't wait, poll or sleep for the game. Waiting costs tokens.
- Do everything you honestly can offline: code, oracle tests, `validation.py`, `proof_all.py --offline-gate`. When only the game can tell you more, write up `ralph/PROGRESS.md` with exactly what you want to look at, create `ralph/NEED_GAME`, commit, push and end your turn. The loop then waits with no model running and starts a fresh pass when the game is free.
- Don't invent offline work to stay busy. Going to `NEED_GAME` early is the right call.
- Once the hook lets you through, the game is yours. If it starts refusing again, Graffiti came back: do the same thing, and release the bridge first.

How to work:

- Fix AS MANY THINGS AS YOU CAN in this one pass before you retire. Your context is valuable, so don't throw it away after one fix. Retire when the next problem wouldn't benefit from what you've already learned, or when your context is getting heavy and your work is getting worse. To retire, write up `ralph/PROGRESS.md`, commit, push, release the bridge, and end your turn. A fresh pass starts straight away. A pass with no commit counts against you, and two in a row stops the loop.
- Everything but that section is yours: code, defs, art, tests, harnesses. If a test is wrong or in your way, fix it or drop it.
- Don't file tickets, and don't leave a problem as a note when you can fix it now.
- Need new art? Generate it now and wait for it (`CLAUDE.md` has the command). You can judge what you made. Don't replace art he already approved unless a north-star line is false.
- Search before you build: don't assume something isn't implemented. This project often already has it.
- Don't write placeholders or simple stand-ins. Build the real thing.
- Keep the wheel turning fast: the small `gimmesomeslack` list, offline checks where they really tell you something, the game when they don't.
- Use subagents for heavy reading and searching, so your own context stays clear. Only one thing at a time may drive the game.
- Stay inside GimmeSomeSlack. Hoses belong to FlowWorks. Go outside only when you are truly stuck on something there, and say so in your notes.
- Keep `ralph/PROGRESS.md` short and honest, for the next pass: what you saw, what you tried, why it matters, what you'd do next. Rewrite it each time rather than appending, and don't let it grow into a status report.
- If something truly needs the owner, write it in `ralph/QUESTIONS.md` and carry on with whatever else you can do.

Save the screenshots you judge by under `D:\ClaudeWork\rimmandrake\ralph_gss\shots\` (`/mnt/d/ClaudeWork/rimmandrake/ralph_gss/shots/` from WSL).

You're done when, in a real colony at play zoom, you would be happy to show this to the owner, and the remaining work above is fixed or honestly ruled out. Then write `ralph/DONE.md`: for each of the eleven north-star lines (nine must-show, two cannot-show), your honest verdict (true or not, and how sure you are) and the screenshot that shows it, then what you did with each open item. Commit, push, release the bridge and end your turn. A reviewer who hasn't seen your verdicts will then look at the same screenshots, and the owner will take a look after that.
