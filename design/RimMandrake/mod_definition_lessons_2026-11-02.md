# What three mods taught us about defining a mod (2026-11-02) — DRAFT

DRAFT: a fresh GPT review (`D:\ClaudeWork\rimmandrake\mod_def_lessons\gpt_review.md`) is not yet applied. Do not show
this to the owner until it is.

The Designer reads this first. It sets out what Gimme Some Slack (GSS), FlowWorks and Pyrelands taught us about the
eight elements of a well-defined mod (`src/RimMandrake/rimflow/roles/designer.md:47`). It then gives the principles
we already hold, why acceptance criteria failed or worked, and a worked set of key-moment stories for each mod.

The owner asked for this on 2026-11-02: *"Examining Gimme some slack, flowworks, and pyrelands might be beneficial as
examples of what we've learned about what it takes. Some of the wisdom there is even incomplete: even though FlowWorks
isn't entirely done, we DO know the principles we've learned that will get it there (e.g. capture the human experience
fully of using the mod, not just mechanical tests and behavior)."* (relayed verbatim in the Conductor's brief)

How to read it:
- Text in *italics inside quotation marks* is his own words, copied from the cited file. Everything else is agent text.
- Short names for the cited files:
  - "rulings" = `design/RimMandrake/gss_flowworks_rulings_2026-10-11.md`
  - "interrogation" = `design/RimMandrake/flowworks_northstar_interrogation_2026-10-02.md`
  - "FW walkthrough" = `design/RimMandrake/flowworks_walkthrough_2026-10-23.md`
  - "ash" = `design/RimMandrake/pyrelands_ash_redesign_2026-10-12.md`
  - "trial" = `design/RimMandrake/northstar_trials/Pyrelands_trial_plan.md`
  - "walk:X" = `design/validation_walks/RimMandrake/X.md`
  - "OWNER:n" = line n of `infrastructure/state/ledger/events/OWNER.jsonl`
- Line numbers are as of commit 44062292f3.

## Part 1. The eight elements, mod by mod

### 1. Why reach for it
- **FlowWorks.** The canal statement gives the purpose: *"The mod is intended to allow natural irrigation of
  crops"*. The walk records his ranking as defense first, then irrigation, then industry, and finally
  terraforming (walk:FlowWorks:81-102).
  With that ranking fixed, the pit, the moat and the pump each had a reason to exist.
- **GSS.** The why is a look he wants, not a function: *"I normally hate how they make conduit invisible... loose
  wirey mess like it does in real life"* (walk:GimmeSomeSlack:53-56).
- **Pyrelands.** The why killed a mechanic. The old ash ladder turned soil into ash step by step, and he asked
  whether *"watching the transformation of soil to ash is really a mechanic we need?... this feels like a mechanic
  intended to turn non-Pyreland into Pyreland"* (ash:8-12). The ladder was retired (ash:226+). If no player desire
  sits behind a mechanic, it goes.

### 2. Using it (what you do, see and hear)
- **FlowWorks.** The pit had to feel like a pit. A working mechanic that read as *"stuck in a trap with "Pit"
  written on it. Not at all "falling in a pit""* was rejected (walk:FlowWorks:115-121). He also wanted the motion
  right: *"Falling into a pit is FAST"* (OWNER:233), and *"All depths must be visually legible... pawn should visibly
  rise up and lower down"* (walk:FlowWorks:130-133).
- **GSS.** Use is mostly seeing (GSS is cables only now: *"We moved the hoses into FlowWorks!"*, OWNER:663). *"Sparking if live, dead if not"* (walk:GimmeSomeSlack:70-72). Cables take *"much
  larger excursions that avoid unwalkable areas or even pile up against them"*; he sent a photo (L76-77). The
  hose rulings, made while hoses still lived in GSS and now FlowWorks's: *"a single connected run... single art style"* (L95-97) and *"reels don't have a choose
  style option"* (L101).
- **Pyrelands.** The bars describe what a player meets, not stored data: ash is fertile when watered, a burn feeds
  the field, black rain falls, a firehawk carries an ember, burrowers dive (walk:Pyrelands:82-117). On ash in the
  air he asked for *"a LOT of free-flying ash blowing around like snow"* (ash:191-192).

### 3. The result
- **FlowWorks.** The through-line is that a canal is the reservoir moved somewhere else, and a pit is a canal dug
  all the way down (walk:FlowWorks:141-144). One idea yields several stories: a moat for defence, a ditch for
  fields, a dry quarry.
- **Pyrelands.** Burning on purpose pays (ash:18-19). This changes a decision the player makes, not just the
  scenery.

### 4. The costs
- **FlowWorks.** *"intake needs a pump. Adding liquid to any storage takes work (pump)"* (rulings:16-19). Every
  source is stock and refills slowly (walk:FlowWorks:103-105). A spill off the hose means *"you have to have
  colonists "clean it up""* (rulings:13).
- **FlowWorks hose (first ruled under GSS).** The hose exists so you can avoid the cost of pipe: it is *"all about NOT having to build out permanent
  pipe for fast deployment"* (rulings:6-11). Reach is limited, so he asked: *"if the hose can only reach 30 cells,
  how does the player go farther?"* That question produced relay reels (walk:GimmeSomeSlack:90-91).
- **Performance is a cost too.** The flying ash became a weather overlay instead of per-cell flecks because of
  tick cost (ash:196-199).

### 5. When it goes wrong
- **FlowWorks.** Failures need a readable sign. Deep water was judged broken because the player could not read it
  as water: *"Water 5.0 is broken... jump... no water effect... walking, not swimming... easily walk out"*
  (OWNER:2256). He made the pit's failure absolute: *"you can't climb out. Period. Welcome to your pit."*
  (walk:FlowWorks:125-126).
- **GSS.** A dead cable must look dead (*"dead if not"*).

### 6. Edges (what it deliberately does not do)
- *"Pitch stays pitch."* and *"not what we're after today"* (rulings:24-26).
- *"GimmeSomeSlack shouldn't even have hoses in it anymore!"* (OWNER:663). This drew the border between the mods.
- Irrigation has no visual sign, by his ruling 36: he was told a player might irrigate for hours without seeing it
  work, and ruled the yield is enough (walk:FlowWorks:252-254).
- Pyrelands has *"no biome-specific heat, no biome-specific sun"* (trial:369). A cannot-show bar forbids ordinary
  rain (walk:Pyrelands:128). Ash is *"Normal ground."* (ash:39).

### 7. Neighbours
- **Vanilla first.** The lamp mast is *"registered just like vanilla Rimworld handles wall lights"*
  (rulings:38-42). For the pit he said the design *"best leverages how Vanilla already works"*, because people
  suffer in a pit by being *"exposed to the elements"* (rulings:58-64).
- **Other systems.** *"rotate Reels or they can't go on a gravship"* (OWNER:1688).
- **Our own mods.** A builder wrote a new propane terrain while FlowWorks already shipped one, and the owner caught
  it (lesson 20260924T033213Z). Mod-to-mod compatibility for GSS is still UNBUILT (walk:GimmeSomeSlack:31-32).

### 8. Settings (the numbers that are the experience)
- The pit's 8 °C each way is a Mod Setting (rulings:67-69).
- Every Pyrelands number is PROVISIONAL, is a Mod Setting, and gets tuned in a walk (ash:21). The furnace-beast is
  a Mod Setting (walk:Pyrelands:17-18).
- The FlowWorks settings table says where each effect shows up in play (FW walkthrough:146-175). Overflow shipped
  OFF while the sign said on, and Mod Settings outlive a save (FW walkthrough:16). A setting is part of the
  experience, so it needs a check like any other part.

## Part 2. Principles we already hold, and the incident behind each

**P1. A passing mechanic is not a passing experience.** In the FlowWorks walk marked VALIDATED, only 4 of 43 bars
proved anything; 15 were VACUOUS, 7 WRONG and 17 UNREACHABLE (interrogation:8, 140). 15 of 28 live PASSes only
waited and checked nothing (the interrogation calls such a PASS noise, interrogation:268). Every channel depth drew Gravel art, so
the state was right while the player looked at gravel (interrogation ~314; walk:FlowWorks:509). The pit worked and
still read as a trap with a label. Define what the player sees, does and feels, and accept against that.

**P2. Some numbers are only settled by looking at them in the game, so make them settings.** For hose and pipe
width, a card fixed the pipe at 30 cm. On 10-21 he said *"Make the pipes half as thick. Flexible hoses need to be
much thinner too"* (walk:FlowWorks:471-474). The next day he said *"Hoses need to be twice as thick, too thing to see
now"* (OWNER:1685). He had already said: *"Both pipe and hose art need a better definition of width. Colonists don't
have arms. Need an in-game look."* So write such numbers down as provisional, make them settings, and name the walk
that will settle them (ash:21).

**P3. The player's desire decides what is built, and real bodies decide how it behaves.** The ash ladder had no
player desire behind it and was retired (ash:8-12). Pit depth comes from what an *"athletic human could not
reasonably raise their arms over their head and jump"* to (OWNER:1118). Falling is fast (OWNER:233). Deep water
must mean swimming (OWNER:2256). Before choosing a number, ask what a real person would experience.

**P4. Lean on vanilla.** The lamp is registered the way vanilla wall lights are, and pit suffering comes from
vanilla exposure (rulings:38-42, 58-64). When a design rides on a system the player already knows, it reads
without explanation and is cheaper to build.

**P5. Some experience cannot be tested automatically; say which, and give it a human pass.** *"Much of this won't be
Northstar testible... Movement/animation is not appropriate for Northstar... combinatorially useful pattern
absolutely IS possible and valuable"* (walk:GimmeSomeSlack:81-86). FlowWorks shipped with the written claim that
nothing was visual-only. It was one of 7 walks that dismissed the visual pass in writing (walk:FlowWorks:509).

**P6. Separate a SITE problem from a MOD problem.** A census of a single tile found 78% foreign plants. The cause
was biome blending at the edges of the tile, not the mod (walk:Pyrelands:35-43). A tile count is never evidence on
its own (walk:Pyrelands:6). Probe the instrument with a planted foreign def first (trial:525-548).

**P7. A port or move can lose what already worked.** *"had the connectors working in GImmeSomeSlack. Somehow we've
regressed"* (OWNER:1827). On the hose splice: *"I really felt like we already had this"* (OWNER:1971). The hose
tests moved to FlowWorks intact, but they measured walls with the function under test, so a seam hole passed both
before and after the move (lesson 20261023T024112Z). Write down what the experience was before a port, and walk it
again after.

**P8. Keep his words his own.** In the GSS walk, words relayed by another seat stood in for his (walk:GimmeSomeSlack:
103-106). A definition built on paraphrase drifts. Quote him, cite the source, and mark anything else as agent text.

**P9. When he finds a defect by eye, it must become a check.** *"Please find ways to test for those defects in your
own offline and in-game testing from now on, so we don't repeat mistakes"* (OWNER:2268). The FlowWorks walkthrough
lists 15 visual and joint defects found only by looking (FW walkthrough:93-114). Each one is owed a check.

**P10. Ask him only what is truly open.** For the build menu he said follow convention, and *"Only ask me this if
there is ambiguity"* (rulings:20-22). Feel questions that only he can answer go to him; an unanswered one goes to a
delegated judge, and the judge's call never counts as his approval (FW walkthrough:116-119).

## Part 3. What made acceptance fail or succeed

Failed:
- **Bars about data, not about the player.** A walk could say VALIDATED while 12 bars were UNBUILT and 12
  behaviours had no check at all (interrogation ~300, ~320). The GSS walk now states the rule: a bar for a feature that is not built yet fails until it
  is built (walk:GimmeSomeSlack:45).
- **A harness hiding a mod bug.** Channels running east or north oscillated forever. The suite read the NOT_SETTLED
  failures as a harness budget problem (interrogation:78-111). The conservation ledger could not see the flicker
  because the total stayed constant (interrogation:105-106).
- **Bars validated, then made stale by a design change.** Asked to validate the Pyrelands bars, he wrote *"Use gpt
  to review instead."* GPT validated them on 10-01 (trial:642). The 10-12 ash ruling retired the ladder those bars
  assumed. A bar is only valid while the design under it holds.
- **Evidence that only looked like evidence.** The hose walk frames were flat MOCK placeholders that looked like
  captures by name and size (lesson 20261022T041408Z). A test fixture wrote True/False while the real export wrote
  1/0, so the fixture passed while the live site picker took ocean tiles as land (lesson 20261021T114235Z).
- **Stories that skipped the player's path.** No component ever designated a dig, which is how a player actually
  makes a canal (interrogation ~274).

Succeeded:
- **Staged scenario walks.** The FlowWorks walkthrough stages 22 stations, and each station is a small story, for
  example C3, The Labyrinth Rescue, where water from a pond reaches a colonist trapped in a pit through a maze of
  hose (FW walkthrough:32).
  He walked it, gave rulings on the spot (L68), and found the 15 defects by eye.
- **Feel questions asked outright.** Is the speed right, too fast or too slow? Does depth read at a glance? Is the
  current too strong? (FW walkthrough:116-144). Feedback in a fixed `station VERDICT text` form (L177-194).
- **Bars written as experience.** The Pyrelands bars (walk:Pyrelands:82-117) and his request for *"Correct animal
  and plant distributions"* (L60-62) say what a player meets. A human pass checks that the animals read as the fire-ecology cast, not a mixed zoo (L52-54).
- **A sheet he could approve whole.** *"Ok, I'm approving this whole sheet. This is amazing..."* Tuning was left
  for later: *"That's playtest tuning much later."* (OWNER:644).

What we learned from both:
- Each check names an observer, a situation, what good looks like, and its proof.
- A mechanical test can back up an experience check, but it never accepts one.
- A live PASS that only waits is not a check.
- A sanity probe proves the instrument can see before its zero is trusted.

## Part 4. Key-moment stories, one set per mod

AGENT TEXT, NOT HIS WORDS. Each set is a trial of the format (first build, routine use, the failure, the payoff),
written from what Parts 1-3 cite. He corrects them; they are not rulings.

**FlowWorks**
1. *First build.* A colonist digs a ditch from the pond toward the fields. Water creeps in cell by cell, and the
   ditch darkens as it deepens.
2. *Routine use.* At dawn a pump hums at the stock tank, and at harvest the canal-side field yields as though
   watered through a dry week. The canal shows no sign of it; the harvest is the sign. The tank level drops visibly, and it refills slowly.
3. *The failure.* A raider charges across the moat line and drops fast into the dug pit. He cannot climb out. The
   pit is dark and its walls stand above his head.
4. *The payoff.* At the end of the siege, the hose runs through the maze to the colonist trapped in the 4 m pit, and
   the rescue water reaches her.

**Gimme Some Slack**
1. *First build.* The player lays power across the base. The cable shows up as a loose, too-long extension cord
   that sags around the workbench.
2. *Routine use.* Cables pile up against a wall the way real ones do. When the generator kicks in, every live cable
   sparks faintly.
3. *The failure.* A breaker trips, and the run to the freezer goes dead grey. The player sees which cable is dead
   before reading any alert.
4. *The payoff.* Seen from above, the base reads as a map: sources, destinations, places where runs go into walls,
   and the slack too-long cords between them.

**Pyrelands**
1. *First build.* The colony lands on grey ash under black rain, with ash blowing like snow. The first field looks
   hopeless.
2. *Routine use.* The player waters an ash field, and it comes up thick. Ash here is fertile.
3. *The failure.* A firehawk drops an ember into the dry stockpile, and the fire spreads.
4. *The payoff.* The player then burns a field on purpose before planting, and the burn feeds the next harvest.
   Burrowers dive as the flames pass.
