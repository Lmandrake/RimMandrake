# CLAUDE.md history — measurements and incident detail moved out of the root CLAUDE.md

The root `CLAUDE.md` holds rules and pointers. When a measurement that goes stale, or the story behind a rule, leaves
it and has no better home (a rulings file, a skill, a lesson), it lands here, under the rule it belongs to. The rule
itself stays in `CLAUDE.md`.

## Facts you cannot guess — how long a cold load takes

Moved 2026-11-19 (Crystallize W47, knowledge merge), because the figure grows with the mod list.

- **A cold load is ~15 minutes on the full list; a quicktest map is ~90 s.** *(MEASURED 2026-09-07, second launch
  of a session; a first launch after a reboot may run slower.)*
- An earlier figure: ~25 minutes on the owner's full list against 22 seconds on a 13-mod minimal list (measured
  2026-08-19; the `rimworld-load-round` skill carries it with its method).
- The rule that stays in `CLAUDE.md`: never "restart and see"; a quicktest map is the cheap instrument.

## The owner's words the root CLAUDE.md quoted, by rule

Moved 2026-11-19, when the root `CLAUDE.md` was drained to rule lines and pointers (owner, 2026-11-19: *"No
provenance either, that's for git."*; `standing_rulings.md` §The root CLAUDE.md holds rule lines and pointers only).
Each heading is the rule's old `CLAUDE.md` heading, with its date. Each line is the excerpt of his words that
`CLAUDE.md` quoted. His full words are in the rule's home (`standing_rulings.md`, `biome_rulings.md`, or the file the
rule points at); an excerpt here is often part of a longer sentence there. Rules whose `CLAUDE.md` quotes already
appear word for word in their home are not repeated here.

### How we debug — owner, 2026-10-01
- "I really do mean stop and start working a new way."
- "Both autonomy questions are yes"

### 🔴 A BIOME WITH ZERO TILES IS NOT A DEFECT — owner, 2026-09-20, said repeatedly
- "It is a RECORD of the planet, not a rival to it."

### 🔴 Six biome mods are HELD BY OWNER; Pyrelands is the only biome mod advancing — owner, 2026-11-16
- "And stop the new biome mods work. Only Pyrelands as a biome mod right now."

### 🔴 No mod runs forward on a broken pipeline — owner, 2026-11-19
- "We're not running mods forward until the pipeline is fixed, ok? So now you don't have to ask me anymore for that."

### Biomes, rosters and seas — owner rulings (full text: `design/RimMandrake/biome_rulings.md`)
- "Animals sound be biome-specific unless there is an in-game reason"
- "I meant pick one arid home."
- "Let's stop evictions right now"
- "This is a human review process issue."
- "what you encounter as an animal there … as well as what you can FISH out"
- "It's ship or nothing."

### 🔑 "Star Wars style" naming is NOT Star Wars IP — owner, 2026-09-22 (Q11a)
- "The fact that we will use "star wars style" naming doesn't mean they have to live in the star wars layer."

### 🔴 One Direct Sun, a pure function of geometry — owner, 2026-09-29 and 2026-10-19
- "It can't be a new "kind" of heat."
- "no biome-specific heat, no biome-specific sun. It's a matter of geometry (low sun is less intense AND produces longer shade, high sun produces only covered shade and much more intense effect). Ambient heat is normal Rimworld rules."
- "If we have an excellent tree shade model working, then YES direct sun works the same everywhere on the day side."

### 🔑 Every DLC is assumed — owner, 2026-09-19/25/26
- "ALL TEST MOD LISTS should include ALL THE EXPANSIONS; we're not trying to ablate expansions out of our list at this time."

### Every mod ships superb Mod Settings — owner, 2026-09-12
- "We can't guarantee they will work in other biomes beyond our framework. They should… but we're not going to validate that at this time."

### 🔴 Agents decide nearly everything; only five acts stay his, and the Conductor may do the rest, mindfully — owner, 2026-10-22 and 2026-11-19
- "Nearly everything including art. An agent can absolutely ask another agent for an art ruling based on some prose constraints and requirements we can draft."
- "I only want to preserve Flyer flights, replacing art I kept, pass at my walk, spending money, public publishing. Everything else the Conductor should mindfully be able to do."

### 🔴 The Evidence-for-Ask rule — owner, 2026-11-15
- "For ALL questions and choices from now on, Conductor must have evidence why it does not select the obvious answer before it pauses for the human, alright? This is a RimMandrake-wide ruling for all pausing agents."
- "Don't keep telling me we can't do things when it's from pre-maturation pipeline decisions."

### 🔴 The pipeline fixes its own defects — owner, 2026-11-15
- "the Pipeline fixes its own issues once detected. When there's a clear problem and a known fix... do it. It's not a ticket for someone else, it's a ticket to file then do yourself."

### 🔴 No trial is spent by a system failure — owner, 2026-11-18
- "I will not accept ANY system that pointlessly expends such statistical measurements based on failed system calls or behavior."

### 🔴 No limit without the danger it guards — owner, 2026-10-31 to 2026-11-17
- "Each element must defend precisely what it's protecting against and have evidence that it actually happens... but when it has... protect cheaply!"
- "Please stop building arbitrary pauses into the system..."
- "No time limits please."
- "please get rid of these arbitrary cuts!"

### 🔴 A passing bar is an experience, never a tuning number — owner, 2026-11-16
- "The mod passing bars should not specify flora and fauna yield rates! That would mean every time we renormalize every mod must repass its bars... drop that!"

### 🔴 The test is built with the item, offline and live — owner, 2026-11-13
- "from now on, we build the test at the same time as the item, both offline and online versions. then they get consolidated into the formal tests."

### 🔴 A refusal carries its path to pass — owner, 2026-11-12
- "ANY refusals must be as detailed as the evidence they are rejecting and include the fixes and paths towards passing that are attainable and reasonable."
