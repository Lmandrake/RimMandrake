Graffiti is a RimWorld mod that should make a colony feel written on: all the various kinds of graffiti, punk and urban, plus sigils from the game's ideoligions.

Read the owner's own words and the north star in `design/validation_walks/RimMandrake/Graffiti.md` (the `## north star` section). That is the experience we owe the player, and it is the only thing you may not change.

BE CREATIVE. Figure out the problems and solve them. Don't just work to a checklist. Play the mod, look at what a player would actually see, work out what's really wrong, and fix it. We trust you. Impress us.

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

Save the screenshots you judge by under `D:\ClaudeWork\rimmandrake\ralph_graffiti\shots\` (`/mnt/d/ClaudeWork/rimmandrake/ralph_graffiti/shots/` from WSL).

You're done when, in a real colony at play zoom, you would be happy to show this to the owner. Then write `ralph/DONE.md`: for each of the ten north-star lines, your honest verdict (true or not, and how sure you are) and the screenshot that shows it. Commit, push, release the bridge and end your turn. A reviewer who hasn't seen your verdicts will then look at the same screenshots, and the owner will take a look after that.
