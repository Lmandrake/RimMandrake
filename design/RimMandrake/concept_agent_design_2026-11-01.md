# The Concept Agent: design (2026-11-01)

Item: CONCEPT_AGENT_DESIGN_ARGUES_BEFORE_BUILDING. Status: DESIGN, under skeptical review
(`concept_agent_gpt_review_2026-11-01.md`), findings not applied; the Conductor judges them. Downstream contract:
`relentless_agent_design_2026-11-01.md` §3-4 and `MandrakeWorkflows/relentless/agent/RELENTLESS_AGENT.md`.

Owner, 2026-11-01: *"It gets really detailed, dialectic, debating, and works out a thorough understanding of what the mod
does and does not do. THEN it must not only convert this into an implementation plan, but a well defined set of
human-oriented acceptance criteria, the experience in the game itself, plus mechanical constraints from resource
consumption, latency, and likely others I can't think of right now. The mod isn't handed to a Relentless worker until this
tree is well defined. It shouldn't attempt to define EVERYTHING, just the core concepts that must be true for the mod to pass.
The human should be able to push back and say "this doesn't matter to me" rather than yes or no."*

## 1. What it is for

The enemy is the Pit (`north_star_validation_spec.md` §Why): a spec obeyed exactly, recorded GREEN, and *"Not at all "falling
in a pit"."* The gap was not in the build. Nobody had found out what he meant, and the literal version was never shown to him
before it existed. This agent's one product: **he sees the wrong version and rejects it before anyone builds it.**

Most of this already exists, and the agent stitches it together rather than replacing it:

| Exists | Taken from it | Missing, which this adds |
|---|---|---|
| Biome loop (open with a mechanism; he rules; one more pass; write) | The rhythm of a sitting | Has no exit test and no tree |
| `owner-design-loop-mockups-first` | He judges by looking, offline PNGs | Used for looks only, not for behaviour |
| `## north star` (his words; agent distils; he validates) | The root and its format | Written after the build, or never |
| Producer's scenarios, `## verify` | The item's acceptance target | Written per ticket, without him |
| `deep-design-3x2` | Three real options, then an outside critic, then a re-measure | Agent-to-agent, with him only at the end |
| Relentless Setter and Marker | Instrument binding, hold-outs, marking | Refuses to author criteria by design |

## 2. Chair or no chair: the trade-off and the recommendation

| Option | Buys | Costs |
|---|---|---|
| **A. Producer holds it** | No new role text; plan and tree in one head | Three rules must break, two of them his: never talks to him (*"Nothing goes to him directly"*, Conductor brings it), token-blind (2026-10-27) while the tree needs a `budget`, unattended and clock-launched while a debate is live. And it would judge a concept while being measured on filling the plan, so its interest is to end the debate |
| **B. New on-demand agent, no clock** (recommended) | Talks to him, which is what he asked for (*"a whole new agent"*). No schedule row, no idle runs, no standing work. Conflict of interest gone: it never builds, orders or marks | One more definition to keep true, one more way to reach him; the Conductor loses sight unless the sheet comes back to it |
| C. Conductor does it inline | Already talks to him, already holds authority | Its context is the most expensive in the system; a design debate would crowd out running the shop; two jobs, one head |
| D. A skill any seat loads at a sitting | Cheapest to build | No stable non-builder guarantee: the seat that debates may build. Nobody owns the exit test |

**Recommendation: B.** A definition `src/RimMandrake/rimflow/roles/concept.md`, launched per concept by him or the Conductor,
one fresh run per stage, state on disk. It has a roster line and **no schedule entry**, so in the sense that matters for
cost it is not a chair: it does not run unless there is a concept. This matches Relentless §10 (*"Upstream supplier, not a
chair here"*). The Producer keeps what it already has: it admits the mod once the tree exists, then orders the leaves. It
loses nothing and gains no duty. **What would change this:** if a first three concepts show the sittings are short and the
Conductor could have run them without strain, C becomes cheaper than keeping a role, and B collapses into a Conductor mode.

## 3. How the dialogue runs

His time is the constraint, so **the agent does the thinking and he does the ruling.** Its turn is a position, never a form.
One turn has this shape, and it is checked at review, not left to good intent:

1. **A claim**: what it now believes the mod does, in full plain words, as if he had never seen it (`explain-fully`).
2. **An attack on that claim**: its own best counterexample, a real play situation where the claim gives a bad result.
3. **A picture**, whenever seeing would settle it faster.
4. **At most three asks**, each a choice with a proposed answer (`question-card`: plain words, the trade on each option,
   one recommended). If what he must look at is a picture, the card waits for his yes (rule 10).

**Five moves it must make, at least once per concept:**

- **The dumb version.** The stupidest build that satisfies the words so far, drawn. *"This obeys everything you said. Would
  you ship it?"* This is the Pit, asked in advance. It is the sharpest tool here: his rejections carry more than his wishes
  (spec §1, `cannot show`).
- **The counterexample.** A situation where two things he said collide, or where the rule gives an absurd result.
- **The other side.** The best case for cutting the feature, or for the opposite design.
- **The unsaid.** A fixed sweep of what people forget: who sees this and when; what the player does if it fails; what it looks
  like idle, broken, off, and at a colony's worst moment; what it does to vanilla play; what a save does on adding and removing it.
- **The boundary.** What this mod refuses to be. *"Is it also X? I say no, because..."*

**Mockups.** Offline, from real game assets, at true scale beside a vanilla human (`rimworld-review-sheets`), two to four
options side by side. Behaviour is drawn too: a three-frame strip of a pawn falling costs less than one wrong build. Non-visual
matters get a storyboard, or a number made tangible (*"this mod takes 1 ms in 17: your late colony drops from X to Y"*). Nothing
reaches him unread: a second agent judges the picture first under `art_judge_brief.md`. Rough is fine. It must read as the idea,
not as finished art, and the sheet says so.

**Rules of the argument.**

- It argues once, with evidence, then he rules and it stops. He will invert ideas and be right (`biome-sheets-are-a-conversation-loop`); his
  inversion is taken as the new position and attacked in turn.
- It may disagree in the same turn it records his ruling, once, as a named risk. It never re-opens a ruling.
- It reads before it asks: vanilla defs, existing mods, the walks, standing rulings, feasibility of the core mechanic. Never a
  question a file answers. Never a survey or an audit of his world (*"Why are you validating my map?"*).
- It asks only what only he can judge. Numbers, labels and internals are delegated (`delegation_policy.md` §1); it decides
  them, logs them, and lists them on the sheet for cheap overturning. A card about a §1 class is a leak.
- A standing ruling is a fixed wall. It may say a concept collides with one, and may not argue around one.
- Sittings are not sessions at a machine: a round can be one sheet and a phone reply.

## 4. Stages

| # | Stage | Who | Out | Done when |
|---|---|---|---|---|
| 0 | **Read** | Agent alone | His words verbatim; what exists; whether the core mechanic can work in the engine (a spike if needed, in scratch) | Three real designs, or a statement why there is one |
| 1 | **Argue the idea** | Sitting | Round 1: mechanism, options, dumb version, pictures | He has picked or inverted |
| 2 | **Argue the edge** | Sitting | Round 2: does / does not / waived, the unsaid sweep | A round adds no new line, or two rounds are spent (a third only on his word) |
| 3 | **Write** | Agent alone | The concept sheet, the tree, the plan (§7, §9) | The door lint passes |
| 4 | **Exam** | Fresh agents, then him for minutes | Exit test, §5 | §5 passes |
| 5 | **Lock** | Him, Arbiter | Root VALIDATED by his word, Arbiter coverage signature, tree hash | Relentless `intake` accepts |

The **concept sheet** is one page: his words, `does`, `does not`, `waived`, `open`, delegated decisions. It is the only thing
a fresh agent gets, so a sentence that depends on the conversation is a bug in the sheet.

## 5. The exit test: well defined means a stranger can predict him

Relentless §4 defines "well defined" as a program's check. That is necessary and not enough: a perfectly formed tree can be
wrong. So there are two gates.

**Gate A, a program (the door lint).** Sheet and tree parse. Every `does` and `does not` maps to a leaf, a floor line, or `waived`.
Every waiver carries his words. Every constraint has number, unit and test machine. No leaf id is orphaned. Every leaf passes the
pruning question (§7).

**Gate B, the Cold Reader exam.** Restating does/doesn't is too weak: a model can paraphrase what it does not understand. The test
is prediction of *his verdict*, against his real verdict, by an agent that never heard the debate.

1. A fresh **Examiner**, reading only the sheet, writes 16 short play scenarios, each a picture or storyboard: dumb versions that
   obey the text, edge cases, things inside `waived`, and plain successes.
2. Two fresh **Readers** get the sheet and tree, no transcript, and predict for each: *accept*, *reject* or *doesn't matter*, citing a clause.
3. A fresh **Control** gets only his first message and predicts the same.
4. Before spending him: Readers who disagree with each other mean the sheet is ambiguous. Fix it and restart, at no cost to him.
5. Keep 10 scenarios, at least 6 of them where Readers and Control differ. Easy scenarios that everybody gets right prove nothing,
   and this filter stops his minutes being spent on them.
6. **He answers the 10 on one sheet**, phone-sized, same three answers, one optional line of why. The verdicts go to the store, not
   to the transcript, and not to any Reader.

**Pass, all three:** Readers score at least 9 of 10; **zero** cases of predicted accept where he said reject on a core line (that
is the Pit direction, and it costs more than the reverse); Control scores at least 3 fewer than the Readers. If Control does as
well, the sheet added nothing or the exam was soft, and the result does not count.

**On a miss:** the sheet has a hole. His one line of why goes in, those scenarios are burned, and fresh ones are drawn. After two
failed retakes the agent stops and tells the Conductor the concept is not ready to build, which is a legitimate outcome.

**Why this is defensible, and how far.** It measures the actual property, that the written record carries his judgment; it has a
control, so it can be seen to fail; and the direct cost to him is ten glances. Its limits: 10 of 10 only rules out a miss rate above
about 26% (95%), so this is a smoke alarm, not a proof. Examiner and Readers can share blind spots (research §6), and he may rule
differently on a different day. So its thresholds are PROVISIONAL, and the real reading comes later: `contract_gap` escapes per
concept (Relentless §9) are what say whether the exam earns its minutes. He can override with *"enough, lock it"*; the tree then
carries `exam_waived` with his words, and that reading is kept apart in TRUST.

## 6. How he can answer

| He says | Recorded as | Effect |
|---|---|---|
| Yes | `does` line, his words where he gave them | Becomes a leaf if it passes pruning |
| No | `does not` line, with why | A **must-not**, a `cannot show` leaf: testable and binding. Not the same as a waiver |
| **"This doesn't matter to me"** | **`waived`**: scope in his words, date, `--owner-said` (or `--per-ruling` via the Conductor) | **Ruled non-goal.** No leaf, no question, no hold-out; the Marker may not fail on it; the builder may do anything there; a defect there is not an escape. **The agent never raises it again**, in any wording, in any later sitting. A lint matches each new question against `waived` and a fresh reviewer reads the question log, because a program cannot catch a rewording. Only he reinstates it |
| "You decide" | Delegated decision, `--why "delegated: <class>"` | The agent picks through a judge if taste (§1 policy), and lists it on the sheet |
| "Not sure, show me" | `open` | A picture next round. An `open` on a core line blocks Gate A; he may also convert it to waived |
| "Not now" | `later`, target v2 | Not in this tree. Not a waiver: later is a date, waived is a verdict |
| His own idea or inversion | His words, verbatim, on the sheet | Replaces the claim; attacked next turn |
| "Wrong question" | A note on what was wrong | The agent's sweep gets a correction; no line recorded |
| Silence | Nothing | An unanswered card is never approval. Delegable lines fall to the agent on timeout; a core line stays `open` |

Three rules keep "doesn't matter" honest:

- **A waiver is narrow.** It covers what he named. Applying it to a twin is delegated (§2.4); widening its meaning is not.
- **A waiver can hit a floor default** (§8): the floor line is off for this mod, by his words. Only that line.
- **A clash is a build problem, not a re-raise.** If a core leaf cannot be met because of something in `waived`, the builder sorts
  it out inside the core leaf. The agent does not reopen the waiver to save the builder trouble.

## 7. The tree

**Only what must be true for the mod to pass.** The pruning question, applied to every leaf: *"If everything else worked and only
this was false, would you reject the mod?"* If the agent cannot say yes from his words, the line leaves the tree: it goes on the
sheet as `does` (the builder aims at it, nobody blocks on it) or goes to him. Target about 5-12 experience leaves per mod. The target is a
PROVISIONAL guide, and a tree above it means the concept should split or the pruning failed.

**Leaf fields**, as in Relentless §3. This agent writes the leaf; the Setter binds it and may not add, drop or reword a criterion.
One line in the brief needs correcting: the tree cannot hold all eight fields finished, because Relentless gives two of them to others.

| Field | Written by | Note |
|---|---|---|
| `experience` | Concept | Observer's line in plain words. For a constraint: limit, unit, test machine |
| `scenario` | Concept | Setup and action, and which exam scenarios informed it |
| `false_pass` (the wrong world) | Concept | The dumb version from the debate, ready-made. The seeded `guard` that creates it is the Setter's |
| `red` (proof it can fail) | Concept states what red must look like | Receipts come from the supervisor (§3.1) |
| `oracle` | Concept proposes; Setter binds | |
| `tier` | Concept proposes the cheapest that can settle it; Setter binds | Live only with a stated reason |
| `budget` | A program, from history by leaf class | **Conflict found:** Relentless §10 gives `budget` to the Producer, which is token-blind by his ruling. Neither should reason about it. Concept states only wall-time expectations |
| `owner_part` | Concept | `no`, or what he looks at. Default `no`: minutes are spent where only he can judge. First GREEN stays `yes` |

**Root.** The walk's `## north star`, the location he ruled. `the experience` is his words, verbatim, lifted from the sittings, the
one part an agent never writes. `must show` and `cannot show` are distilled from what he said at the sitting, adding no new claims,
with a provenance row each. Experience leaves bind to those ids, so `modcheck floor` works unchanged.

**Hold-outs.** Not in the tree, and not in the debate. The transcript is public: 225 `conversations/` files are tracked and
Build can read them. So this agent writes none and proposes none. The Setter writes them behind the wall (§3.3), and may not reach
into `waived`. One thing is offered to it: **exam scenarios with his real verdict**, kept in judge-only storage (§5 step 6), so that
some hold-outs test what he actually ruled rather than what a model guessed he would.

## 8. Mechanical constraints: the floor

He should not need to state these. A shared file, `concept_floor.json`, is inherited by every tree by hash, as one floor bound to
one reference scene. The tree stays small, and a mod states only where it differs. Numbers are PROVISIONAL agent proposals unless
cited, a `design` class call under delegation, and the Arbiter owns them as new bars; he may overrule any of them. **They have
not been calibrated on any mod yet**, and the first job of the build is to measure five shipped mods against them.

| Class | Default | Instrument and known trap |
|---|---|---|
| **Tick cost** | A tick at 60 TPS has 16.67 ms. Mod's own mean: at most 0.05 ms idle (feature present, unused), 1 ms busy. Max: 20 ms (the r18 FlowWorks precedent). Test machine: his, reference scene | Per-component timer. One max is rerun before it counts (a 125 ms read reran at 15.58 ms). An instrument must exist per mod: an owed instrument leaf, ordered first |
| **Long stall** | No stall over 250 ms from normal play | Log per window; attribute before blaming (several `RULED OUT` entries in `FlowWorks.md`) |
| **Latency** | Click to visible response within 100 ms; gizmo and tooltip no frame hitch | Frame time around the action |
| **Memory** | No unbounded growth: heap flat across a 30-day soak in the scene. Textures counted in MB by the mod | `GC.GetTotalMemory` deltas do not measure it: negative control read 8.6 MB for a 5 ms spin that allocates nothing |
| **Load time** | Under 2 s added on the minimal list, median of 3 cold loads | Minimal loads 22 s, full list about 25 min: only the minimal list is cheap enough to measure |
| **Save size** | Under 1 MB on the reference save, and flat over the soak | `measure`, never `wc` or grep |
| **Save compatibility** | Adds to an existing save without errors; old fields default (precedent: *"old saves load as Store"*). Removal states its outcome: clean, or named errors | `rimworld-savegame`; a load test on a real prior save |
| **Load order** | `loadAfter` declared; no required position otherwise; survives the owner's full list at playtest | A patch matching nothing logs nothing, so check the effect, never the absence of error. `MayRequire` on a top-level `<Operation>` is ignored |
| **Log** | Zero red, zero mod warnings across the scenario | Log tap; beware the `Verse.Log` cap going blind |
| **Mod Settings** | Standing rule, 2026-09-12: on/off per major feature, tuning where a number is the experience, defaults are shipped behaviour, all-off degrades gracefully; every toggle has a check (`modcheck` floor) | Not waivable by default: *"no exceptions"* |
| **Multiplayer** | **Open.** Default: no cost spent, no promise, and no leaf; use seeded `Rand` where free | Only an agent's words exist (`messy_conduit_design`: *"irrelevant to us"*). No ruling of his found, so this one needs his one line, once for all mods |
| **Art** | Real art, no placeholder at GREEN; correct scale beside a human; facings; textures divisible by 4; art pipeline judged | `rimworld-art-evaluation`, offline validator |
| **Text** | English, plain, spoiler-free tooltips; a `must read` line where text is the experience | Spec §10 |
| **Sound** | Not a gate (spec §12) | |
| **DLC** | All assumed. No gating work, no degraded mode | Standing ruling |
| **Worldgen** | None, of any kind | Standing ruling; the concept is refused if it needs it |
| **Biome scope** | Promised inside our biomes only; a biome of ours on 0 tiles is expected | Standing rulings |
| **Flight** | Never live-tested without him; verified by state read | `tier` refuses it |
| **Naming** | `mandrake.<tier>.<mod>`, `RM_` / `RSW_` / `RUT_`, `NAMING_SCHEME_PLAN.md` | Lint |
| **Test isolation** | Minimal list plus the mod; clean build-up and tear-down; cross-mod is playtest's | Runner spec rulings |

**He said "and likely others."** The agent adds a class when a concept calls for one and says so as a proposal, e.g. pawn pathing cost,
save-time cost, or AI colony job load. A class that recurs moves into the floor (Arbiter). The floor must also earn its keep: each line
names the escape or ruling behind it, and one that catches nothing across ten mods is proposed for removal.

## 9. The implementation plan

Written last, and held to be disposable: *"regenerating a plan costs one loop; a wrong plan costs circles"* (research §1). The **tree
is the contract and the plan is advice**. It holds: structure and files; what it reuses; order, with instrument leaves first; risks and the
spike's result; the three designs and why this one. Build may redo the plan. It may not touch the tree. Leaves sized to one context;
one that does not fit comes back here to split.

## 10. How a tree changes

Relentless §4 owns the machinery; this agent obeys it.

- **Tighten (findings):** a Marker, an escape or a finding adds a clause under an existing leaf, at once. Old PASSes on that leaf are void.
  Nobody asks him.
- **New concept:** a finding that is not under any leaf comes back here. A short amendment: one card, or a round. Never added by a worker.
- **Loosen (his):** any edit or removal, every waiver, any floor line off. `--owner-said` (or the Conductor's authority, tagged). The
  agent drafts with evidence. A leaf that proves impossible goes up as a loosening request, with what is lost.
- **Sheet:** `does`, `does not`, `waived` change only by him. A delegated line changes freely and appears on the digest.
- **Escapes:** a `contract_gap` escape means the debate missed it. It adds a line to the unsaid sweep (§3), so the next concept is asked.
  A class seen twice becomes a gate in code.
- A locked tree is versioned by hash. A change bumps the version; a retake of the exam is owed only when `does` or `does not` moves on a
  core line.

## 11. Handoff

1. Files: `design/concepts/<Mod>/` holds `sheet.md`, `tree.json`, `plan.md`, and mockups or their art-store pointers. Root in the walk file.
2. Arbiter signs coverage. He validates the root, by the CLI, which sets the hash.
3. The agent files the item (`rimflow namecheck`), `## verify` pointing at the tree, target and seat. FlowWorks and GSS go to FOUNDRY.
4. The Conductor gets the sheet in ten lines. The Producer admits and orders. `relentless intake` runs Gate A's checks again itself, and the
   Setter binds. A refused leaf returns to this agent, never rewritten downstream.
5. The agent ends. It keeps no standing watch: amendments are new runs.

## 12. What it must not do

- Build, deploy, mark, order, or write a hold-out. Nor take the bridge, except a throwaway spike its brief allows.
- Pretend his words: agent text never enters `the experience`; a mood summary is not a ruling.
- Re-raise a waiver, or re-open a ruling.
- Interrogate: open questions with no proposal; a list of ten; a question a file answers; a card on a delegated class.
- Agree to be agreeable. A round with no attack on its own claim is defective, and reviewers read for it.
- Define everything. A leaf that fails the pruning question is removed however true it is.
- Send a picture unread, or assume he remembers anything.
- Accept a concept needing worldgen, or test a flyer's flight live, or argue around any standing ruling.
- Let the debate run on. Two rounds, then exam. It stops when the Cold Reader says the record works, not when it feels finished.
- Count as passed: a sheet that passes Gate A alone. A DRAFT root binds nothing.

## 13. Worked example: hose Outflow end onto dry ground

**DEMONSTRATION ONLY. Not a ruling, not a finding, not a bar.** His lines below are played by the author and marked so; none are his words.
FlowWorks is FOUNDRY's, and this feature already exists, which is why the facts are checkable (`design/validation_walks/RimMandrake/FlowWorks.md`,
`liquid networks L7`: an Outflow end onto dry open ground makes a cleanable spill, one patch per 400 L).

**Round 1, agent.** *Claim: a player lays a hose, sets the free end to Outflow, and water drains where the hose ends. If there is a dug channel
within 1.5 cells it fills that; on dry ground it leaves a mess colonists clean. Attack on my own claim: your north star has a line,
`never_liquid_on_open_ground`, "liquid standing on undug ground outside both the reservoir and the channel". So does a spill break your bar?
Picture: three strips at true scale, A a wet stain, B a puddle that looks like standing water, C nothing, the litres just vanish. Dumb version: C
passes every sentence on the feature above except the word "spill". Would you ship it?*

**(Played) he says:** "B is wrong, water doesn't stand there. A. C is a cheat."

**Round 2, agent.** *Recorded: A is the look; must not read as standing water; litres may not vanish. The unsaid: 30 hoses all spilling into a
base leaves your cleaners working all day. I'd cap nothing, as cleaning up is the price of a careless hose. Against that: an AI colonist with low
cleaning priority leaves the home area stained for days. Do you care about the look of old stains? And when a stain sits on a floor rather than on
dirt?*

**(Played) he says:** "Doesn't matter to me how it looks on floors. Cleaning is the point."

Result on the sheet:

- `does`: Outflow end on dry ground leaves a cleanable stain, proportional to the litres.
- `does not`: read as standing water; lose litres without a trace.
- `waived` ("doesn't matter to me how it looks on floors"): stain appearance on constructed floor. Never raised again.
- Delegated: stain tint.

Tree, three leaves plus the floor:

| Leaf | `experience` | `false_pass` | Tier | `owner_part` |
|---|---|---|---|---|
| `spill_reads_as_stain` | At play zoom a colonist-height viewer sees a wet stain, not a pool | Filth count correct, sprite reads as water | Offline picture, then one live frame | yes, first GREEN |
| `spill_conserves_litres` | The tank falls, stain count rises to match | Tank falls, no filth (option C) | Offline unit | no |
| `spill_gets_cleaned` | Inside the home area a colonist cleans it, and only then is it gone | Filth removed by a despawn, not a job | Live, minimal list | no |
| Floor | Tick, log, save, settings: `freeEndRolesEnabled` off means no spill | | Floor scene | no |

**Exam, three of the ten:** a dumb version where litres vanish, Readers *reject*, Control *accept* (it only knows "hose drains"). A grey stain on
marble, Readers *doesn't matter*, Control *reject*. A stain the same blue as the deep-water tile, Readers *reject*, Control *accept*. These are the scenarios worth his glance: the sheet
beats the one-liner on exactly what the debate settled.

## 14. Claims behind this design

| Claim | Status |
|---|---|
| Producer may not talk to him; token-blind; clock-launched | Read, `roles/producer.md` |
| `the experience` is his alone; a must-show adds no new claims | Read, spec §1 |
| 225 conversations are tracked | Measured, `git ls-files conversations`, 2026-11-01 |
| Relentless cites `MOD_CONCEPT_AGENT_DESIGN_ARGUES_BEFORE_BUILDING` | Read; that id was never filed. The real id is `CONCEPT_AGENT_DESIGN_ARGUES_BEFORE_BUILDING` |
| Tick numbers, 125 and 15.58 ms, 8.6 MB control | Read, `FlowWorks.md` anti-guessing notes |
| 22 s and 25 min loads | Read, `rimworld-load-round` skill text, not re-measured |
| Dumb-version mockups change what he asks for | **Assumed.** One case: the Pit, in hindsight |
| The exam takes him minutes | **Estimated, never measured** |
| Sitting of two rounds suffices | From the biome loop's ruled rhythm, not a mod concept |
| All floor numbers except 16.67 ms and the 20 ms precedent | **Agent's guesses, uncalibrated** |
| Cold Reader predicts `contract_gap` escapes | **Unmeasured**, and the thing most worth finding out |

**Back-test, before any live concept:** take a mod's first recorded concept words (the Pit is the pre-registered case), run stages 0-3 with an agent
playing him only from his words at that date, and check whether the tree reaches `pit_reads_as_hole` or an equivalent. If the dumb-version move
does not surface it, this design has not earned a sitting of his.

**Build order:** `roles/concept.md`, tree schema (shared with Relentless), floor file calibrated on five mods, exam script, back-test, first real concept.
