# Lexicon audit, 2026-11-12: every candidate word and what was decided

This paper is the reasoning behind `LEXICON.md` at the repo root. The Lexicon file itself holds entries only
(a word and one line saying what the thing is). Everything else the request asked for lives here: what each
word is NOT, which near-synonyms to retire, which file or tool is the authority, the words that still have two
live meanings and need the owner, and the words that were refused an entry and why.

Companion: `design/RimMandrake/production_system_map_2026-11-12.md` (the map of the production system).

## 1. Where the idea comes from, and one place the request and the skill disagree

- The Lexicon is defined by the `lexicon` skill (`~/dev/Lodestar/docs/lexicon/`, installed as a Claude skill).
  The fleet's own file is `~/dev/Lodestar/LEXICON.md`; a project's file is `LEXICON.md` at its root. A session
  reads both; the project file wins where they collide, and a collision must be said out loud.
- **Disagreement.** The request asked for each entry to carry a definition, what it is not, synonyms, and an
  authority file. The skill forbids all but the first: *"The file is entries only"*; a path, a flag, a count or
  a reason inside the file is a defect. The skill was followed. The extra material is in this paper instead.
- **The skill says this step is early.** It expects a `grill` session first (an argument with the owner over
  each definition) and calls a Lexicon *"the residue of a definition fight"*. No such session has been held for
  RimMandrake. Read section 4 as the agenda for one.
- **How a word earned an entry.** The skill's five gates, in order: (1) the thing exists today; (2) the line
  says what it is, not how it is built; (3) it is the owner's word, not an agent's; (4) it has exactly one
  meaning; (5) no other place already carries it. A word that fails names the gate.
- **Whose word it is was measured, with a caveat.** "His uses" below counts the owner-typed messages that
  contain the word, out of 2,675 messages (71,464 words) in the saved conversations of the main window,
  2026-10-02 to 2026-11-12, with question-card text and automatic wake prompts removed `[measured]`. Treat every
  count as an upper bound: pasted agent text inside his messages still counts, and other windows' conversations
  are not included.

## 2. Collisions with the fleet's Lexicon (said loudly, as the skill requires)

| Word | Fleet meaning | Here | What to do |
|---|---|---|---|
| **Dispatch / Dispatcher** | Dispatch: handing a subtask to a cheaper or bigger model | Dispatcher: the clock that starts scheduled roles | Near-collision, one letter apart. Entry kept; always say "Dispatcher" in full here. |
| **Ticket / item** | Ticket: one thing to finish, with the evidence that would prove it | The same thing is called "item" by RimFlow and by him (189 messages) and "ticket" by him too (81) | Unsettled, section 4. |
| **Bench** | The fleet's RimMandrake line says "the bench that tests it" | He ruled: *"We seem to have confounded Conductor and Bench. It really should only be called Conductor from now on."* | Entry is a tombstone. The fleet line should lose the word; not edited by this work. |
| **Ledger** | Cut at fleet level as a synonym for Board | RimFlow's record of events | No entry (he typed it 3 times). Agents may say "RimFlow's record". |
| **Sprites** | Ambient light-creatures, one per session | Game art images | No entry here; say "game art" or "texture" to him. |

## 3. Words that got an entry (31)

"Reason" is the skill's justification: **saves** a sentence, **stops** a real confusion, or **often** said.

### Who does the work

| Word | His uses | Reason | It is NOT | Retire / keep | Authority |
|---|---|---|---|---|---|
| Conductor | 55 | often; stops confusion with Bench | Not a builder; not "BENCH" | Retire "Bench", "the seat"; keep "Conductor" | `src/RimMandrake/rimflow/roles/conductor.md` |
| Relentless | 82 | often; his own definition: *"a builder/test-builder/judge pipeline, not an everything pipeline"* | Not the whole production system; not running today (off since 2026-11-06) | Retire "the pipeline" used alone | `src/RimMandrake/rimflow/relentless.py`, `relentless_rules.json` |
| Artisan | 34 | saves "the per-mod loop with a fixed checklist and an outside judge" | Not a person or one session; not Whittle | Keep "Artisan loop"; retire "head" and "bar" when talking to him | skill `artisan`; `src/RimMandrake/rimflow/roles/artisan.md` |
| Whittle | 19 | saves "the worker that takes one small ticket at a time" | Not the leftover `whittle/` folder; not the cost page | Retire "whittle" for the folder (call it "Whittle's leftover evidence") | skill `whittle`; `src/RimMandrake/rimflow/roles/whittle.md` |
| Designer | 31 | stops confusion: a role, not a person | Not the one who builds; not "design" in general | Keep | `src/RimMandrake/rimflow/designer_stage.py`, `roles/designer.md` |
| Operations | 26 | his rename: *"Operation Steward should just be calls Operations"* | Not a builder; decides nothing about the game | Retire "Steward", "Operation Steward" | `src/RimMandrake/rimflow/roles/operations.md` |
| Dispatcher | 6 | stops confusion with fleet "Dispatch" and with an AI role | Not an AI; decides nothing | Always the full word | `src/RimMandrake/rimflow/dispatcher.py` |
| Test Pilot | 7 | saves "one live debugging sitting on one stuck item" | Not a proof run; not the test queue | Keep | `.claude/agents/rm-testpilot.md`; `rimflow pilot` |
| Foundry | 151 | retired thing still named in live files (the skill's one allowed tombstone) | Not a place to send work today | Goes when the references go | `design/RimMandrake/standing_rulings.md` |
| Bench | 123 | retired word still everywhere; his ruling quoted above | Not a second role | Goes when the references go (seat name, clone path, role files still say BENCH) | his ruling; `standing_rulings.md` |

### The game and the proof

| Word | His uses | Reason | It is NOT | Retire / keep | Authority |
|---|---|---|---|---|---|
| Bridge | 97 | often | Not the game; not the test queue; "the bridge is up" does not mean a map is loaded | Retire "GABP", "JawaBench", "companion" when talking to him | root script `./bridge`; skill `rimbridge` |
| Live | 83 | stops confusion: *"I'll have to see it live in game to judge it"* | Not "currently running" for a program, and not "current" for a file. Say "running" and "current" for those | Retire "in-game" as a second word only if he agrees; he types both | skill `live-debugging-proof-harness` |
| Offline | 29 | pair of Live | Not "the machine is down" | Keep | `src/RimMandrake/Utils/run_selftests.py` |
| Deployed | 31 | stops the most repeated mistake in the repo: a written file the game never read | Not committed; not published; not built | Retire "installed", "synced" | `src/RimMandrake/Utils/deploy_custom_mods.py` |
| Minimal mod list | 4 | his own example of clear wording: *"'Only proven on the minimal mod list' is clear"* | Not proof for his real game | Retire "min tier", "GREEN-MIN" when talking to him | `src/RimMandrake/Utils/modlist_swap.py` |
| Full mod list | 15 ("mod list") | pair of Minimal | Not one fixed list: it is whatever his real game loads | Retire "full tier", "prod", "campaign list" | game's `ModsConfig.xml` (read by a parser) |
| Lightspeed | 2 | he coined it, 2026-11-06 | Not any fast test; not Relentless | See section 4, item 7 (is it the same thing as "the test queue"?) | `design/RimMandrake/lightspeed_2026-11-06.md` |
| North star | 14 | saves "the written list of what the player must see, used as the test" | Not a goal in general; not a proof script | Retire "walk", "walk map", "validation walk" for the paper | `design/validation_walks/` |
| UNMEASURED | 3 | stops a real confusion: reading "no answer" as "passed" | Not PASS; not FAIL; not "skipped on purpose" | Keep capitalised; retire "inconclusive", "n/a" | skill `live-debugging-proof-harness` |
| Blocked | 13 | his usage: *"make them blocked on the items they need"* | Not "slow"; not "nobody picked it up"; not "waiting for him" (that is "needs him") | Retire "held", "parked" unless section 4 item 9 gives them a meaning | `src/RimMandrake/rimflow/cli.py` |
| Ruling | 21 | stops confusion between his decision and an agent's choice | Not an agent's decision; not a design paper | Keep; "standing ruling" is the same thing written down | `design/RimMandrake/standing_rulings.md`; the OWNER ledger file |

### Names (10)

FlowWorks (73), Gimme Some Slack / GSS (30), Huge Things (6), Pyrelands (22), Explosive Knockback (2),
Baroque Biomes (21), Star Wars layer (21), Utinni layer (13), Archmagi (30), SteveDesktop (77). Each line was
written from the mod's own `About.xml` or from `design/NAMING_SCHEME_PLAN.md`. Only names he types got a line;
the other 129 mods have none, on purpose.

## 4. Unsettled — needs the owner

Each of these has two or more meanings in use today. No meaning was picked. Each is a question for him.

1. **done / closed / built / validated / proven / accepted / shipped.** Five different facts hide here: the code
   is written; the offline tests pass; one live proof passed; every live proof passed on his real mod list; he
   looked and said yes. RimFlow's "done" can be reached without the last three: 5,161 items are done, while no
   mod has his acceptance on record `[measured]`. He types "done" in 125 messages, "close" in 54, "accept" in 44,
   "proven/proof" in 14, "ship" in 6, "validated" in 3. Which word names which fact?
2. **ticket or item.** The fleet's Lexicon defines Ticket. RimFlow says item. He types both. One word, or two
   words for two things (for example: a ticket is small, an item can be large)?
3. **bar / leaf / row / line / criterion / check.** Six words for "one thing a mod must pass". Artisan says bar,
   Designer says leaf, proof scripts say row, per-item proofs say line, modcheck says check. He types "check"
   (137, mostly the plain verb), "bar" 4 times, "leaf" never in this sense. Which one word should agents say to
   him?
4. **look / walk / showing / sitting.** Four words for "he judges it in the running game". He types "look"
   (146, mostly the plain verb) and "walk" (38, mostly "walk me through"). RimFlow says "needs owner". Is there
   one word for this step, the one only he can do?
5. **tier.** It means the three families (RimMandrake, Star Wars, Utinni) in the naming plan, and it means a
   test mod list (57 of them) in the tools. He types it twice. The Lexicon uses "layer" for the first and "mod
   list" for the second, following his own words; confirm or correct.
6. **validated.** A RimFlow state (one live proof passed), a north-star state (he signed that exact text), and a
   script's answer. Three meanings. Keep it for one, or stop using it with him?
7. **Lightspeed and "the test queue" (testq).** He named the test lane with no AI in it Lightspeed. The agents
   built it and call it testq, a word he has never typed. Are these the same thing? If yes, testq should be
   renamed in everything he reads.
8. **round / pass / run / session / sitting.** Whittle has rounds, Artisan has passes, proofs have runs, the
   game has loads, he has sittings. He types "round" 7 times. Probably five real things; they need one line each
   or a ruling that only some are worth a word.
9. **held / parked / paused / off / stopped / disabled.** Six words for "not running", used for builders and for
   items. The map found the switches and the reality disagree (section 7 of the map), partly because the words
   do. Which words mean "he turned it off", "it is waiting", "it broke"?
10. **window / seat / role / helper / worker / subagent.** He types "subagent" (208) and "window" (48); agents
    write "seat" (he typed it 3 times). A window is something he can see; a seat is an identity in the ledger; a
    role is a job. Should "seat" be kept out of what he reads?
11. **North star.** Entered as one meaning (the written list), though agents also use it for a folder of proof scripts and a driver program, and 86 of 94 written north stars are drafts he has not signed
    `[measured]`, and he wrote that the system *"hadn't strongly panned out yet"*. If he no longer wants the
    word, delete the entry.

## 5. Words refused an entry, and the gate that refused them

| Word | Gate | Why |
|---|---|---|
| seat | 3 | Agents' word; he typed it 3 times. The fleet cut it too. See section 4, item 10. |
| testq / test queue | 3 | He has never typed either. See section 4, item 7. |
| lane | 4 | Test lane, offline lane, build lane: three uses. The fleet cut it too. |
| floor, leaf, tree (Designer's) | 3 | Agents' words; his "tree" and "floor" are the ones in the game. |
| hold, driver lock | 2 | Mechanism. The idea he needs is in the Bridge line: one driver at a time. |
| INVALID, quarantined | 3 | He typed "quarantine" once, as a plain verb; never INVALID. |
| cold load | 3 | Never typed. He says "restart" (38). |
| epic, task | 1 | RimFlow has no such thing. |
| subagent, helper, worker | 5 | Plain words that already mean what they say. |
| notch | 3 | One notch is half a metre of FlowWorks depth (`design/RimMandrake/flowworks_elevation_play_2026-10-17.md`), but he typed the word once, in another sense. Say "half a metre". |
| fill | 3 | He uses it as a plain verb only. |
| canon | 5 | Plain word, one meaning (the Star Wars source material); nothing to protect. |
| concept | 4 | Designer's output and the plain word, mixed (40 uses). |
| GREEN-MIN, GREEN-FULL, L0 to L4 | 3 | Agents' labels. The entries "Minimal mod list" and "Full mod list" carry the meaning. |
| PASS, FAIL | 5 | Plain words. |
| question card, review sheet, handoff, RimFlow | 5 | Fleet-level words, not this project's. RimFlow and Handoff already have fleet entries; question card (170) and review sheet (53) do not. |
| GPT, Codex | 5 | Product names, not our vocabulary. |
| modcheck, prereview, standing ruling, verdict | 3 | Never typed by him, or (standing ruling) covered by "Ruling". |
| Producer, Auditor, Innovator, Artist, Night Shift | 1 or 3 | Roles that are disabled, or names he does not type. |

## 6. Words he may want to coin (his to mint, not ours)

The skill asks for proposals where he retypes a long phrase because no word exists. Three were seen:

- *"live in game"* / *"see it live in game to judge it"*: the step only he can do (section 4, item 4).
- *"offline validated, live game tested, and give me empirical proof of its passing"*: he spelled out three of
  the five facts in section 4, item 1, in one sentence, because no word carries them.
- *"Only proven on the minimal mod list"*: a status he called clear. It has no one-word name.

## 7. What registering the Lexicon needs

- Nothing must be registered. Lodestar's `bin/project_drift.py` checks only that `LEXICON.md` exists at the
  project root.
- Optional, not done here (they are outside this work's permission): one line in this repo's `CLAUDE.md`
  pointing at `LEXICON.md`; fleet entries for "question card" and "review sheet"; removing "the bench" from the
  fleet's RimMandrake line.
