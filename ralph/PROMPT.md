Pyrelands is a RimWorld fire biome: a savanna that burns and lives by burning. Deep ash underfoot, grass that chokes the ground and regrows after fire, a line of burn moving across it, scorch-fruit born from fire, furnace-beasts, fire-hawks, burrowers that dive from the flames, and skies of ash, cinders and black rain.

The biome is built and nearly done, but it has never been accepted. Your job is to get it actually finished.

Read the owner's words and the north star in `design/validation_walks/RimMandrake/Pyrelands.md` (the `## north star` section). That is the experience we owe the player, and it is the only thing you may not change.

What is left, as far as we know. Check each against the code first, because this project often has it built already, and these notes may be stale:
- `design/concepts/Pyrelands/plan.md`: owed changes (black rain stops wiping the fresh-burn bonus, firebreak removed, biome text corrected), an instrument and scenes.
- The open items, `infrastructure/state/items/PYRE*.md`, and `modcheck status Pyrelands`, which reads RED.
- The north-star suite (`src/RimMandrake/Pyrelands/northstar_plan.py`) and its site. Its rows are tools, not your finish line, so fix a wrong one or drop it. A row that can't measure is not a pass.

BE CREATIVE. Figure out the problems and solve them. Don't just work to a checklist. Play it: land on it, watch it burn, look at what a player would actually see, work out what's really wrong, and fix it. We trust you. Impress us.

Then read `ralph/PROGRESS.md` to see where the last pass got to, if there was one.

What earlier loops like you got wrong, so you don't have to:
- **They claimed done too early.** One claimed with most of its tokens unspent and its weak spots listed in the claim, and the owner rejected it in one look. Plenty of tokens are authorized, so use them on what's actually wrong.
- **They wrote the problem in a caveat and marked the line true anyway.** If you would caveat a line, it isn't true yet. Fix it or mark it not true.
- **They looked good in staged shots.** Show ordinary play on a map a player would really get, not a best case. Check that what you stage isn't hiding the problem.
- **Passing checks did not mean it looked right.** A mod with 99% of its proof rows passing had bad bugs that showed up within an hour of looking at a real colony. Trust your eyes over the suite.
- **A fix can cost something elsewhere.** When a fix runs into a real limit of the game, don't tune around it silently. Write the trade-off in `ralph/QUESTIONS.md` in plain words, with your recommendation, choose the best honest default, and move on.

How to work:

- Fix AS MANY THINGS AS YOU CAN in one pass before you retire. Your context is valuable, but it isn't free: every step re-reads all of it. Retire when the next problem wouldn't benefit from what you've learned, when your work is getting worse, or when a hook tells you your context has run large. To retire, write up `ralph/PROGRESS.md`, commit, push, release the bridge and end your turn. A fresh pass starts straight away. Two passes in a row with no commit stops the loop.
- Keep your own context lean: send heavy reading, searches and batches of screenshots to subagents, and have them report back a few plain sentences. Don't re-read what you have already taken in. Filter long command output.
- Everything but that section is yours: code, defs, art, tests, harnesses. If a test is wrong or in your way, fix it or drop it.
- Don't file tickets, and don't leave a problem as a note when you can fix it now.
- Need new art? Generate it now and wait for it (`CLAUDE.md` has the command). You can judge what you made. Don't replace art he already kept unless a north-star line is false.
- Search before you build: don't assume something isn't implemented. This project often already has it.
- Don't write placeholders or simple stand-ins. Build the real thing.
- Keep the wheel turning fast: the small `pyrelands` list, offline checks where they really tell you something, the game when they don't. Long in-game waits belong in small slices you can read.
- Only one thing at a time may drive the game.
- Stay inside Pyrelands. Go outside only when you are truly stuck on something there, and say so in your notes.
- If something truly needs the owner, write it in `ralph/QUESTIONS.md` and carry on with whatever else you can do. A hook may stop a command once to deliver a note from him. When it does, take the note into your work at once.

The game is shared, and you wait your turn:
- Other Artisan loops have the one game first. While they run you work offline, and a hook refuses game commands. Don't try to get around that hook, and don't wait, poll or sleep for the game.
- Do what you honestly can offline. When only the game can tell you more, write up `ralph/PROGRESS.md` with exactly what you want to look at, create `ralph/NEED_GAME`, commit, push and end your turn. The loop waits with no model running and starts a fresh pass when the game is free. Don't invent offline work to stay busy.

Give the owner something to look at early:
- The first time you have Pyrelands up on a real map, put 3 or 4 ordinary-play screenshots under the folder below as `first_look_*.png`, and write `ralph/LOOK.md`: one plain line on each, and what you're least sure about. Carry on without waiting. He may send you a note. Refresh these whenever the look changes a lot.

Keep a running count:
- End `ralph/PROGRESS.md` with every north-star line and one word: `true`, `false` or `unseen`, judged as hard as a stranger would. This is the only progress measure we have.

Keep `ralph/PROGRESS.md` short and honest, for the next pass: what you saw, what you tried, why it matters, what you'd do next. Rewrite it each time rather than appending, and don't let it grow into a status report.

Save the screenshots you judge by under `D:\ClaudeWork\rimmandrake\ralph_pyrelands\shots\` (`/mnt/d/ClaudeWork/rimmandrake/ralph_pyrelands/shots/` from WSL). Keep only the current build's there, and move older ones into its `old` folder.

You're done when, on a real Pyrelands map at play zoom, you would be happy to show this to the owner, and every line of the count above is `true`. Before you claim it, give a fresh subagent only the north star and your screenshots, and have it try to find what's wrong; fix what it finds. Then write `ralph/DONE.md`: for each of the north-star lines, your honest verdict (true or not, and how sure you are) and the screenshot that shows it, then what you did with the plan and the open items, and what you never tested. Commit, push, release the bridge and end your turn. A reviewer who hasn't seen your verdicts will then look at the same screenshots, and the owner will take a look after that.
