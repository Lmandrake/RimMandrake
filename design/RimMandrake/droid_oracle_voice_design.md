<!-- status: DESIGN, dormant — DROID_ORACLE_VOICE_DESIGN_1, Fable pass 2026-09-08, for owner
     review. Ruled into existence by DROID_UNIFIED_FRAMEWORK_DESIGN.md §0 card 14 ("Droid voice
     via the Oracle: design now as dormant E5") and §3.4. Reads on top of (never restates):
     llm_ingame_wiring_spec.md (the two laws, the pipeline), nine_voices_cast_bible.md (the
     persona-block pattern), OracleRegisterBlocks.cs / OracleValidator.cs (the one built
     consumer, Ohm), droid_system_spec.md §3–§7 (embodied software, tiers, spikes, the bolt).
     Transport is the BUILT OracleClient.cs (`claude -p`, ef628781, re-verified d9b909c8); §2.6
     states what that transport does to every consumer. The prescribed fallbacks below need no
     LLM at all. Reconciled against the live client 2026-09-09. -->
# Droid voice through the Oracle — four consumers, dormant

## 0. What "dormant" means here

Each of the four moments ships as **prescribed text first** — the fallback lines
in §3–§6 ARE the v1 deliverable and run with zero LLM calls. The Oracle call is
an enrichment layered on top, behind `OracleGameComponent`'s existing kill-switch
(`OracleSettings.enabled`, default off) and a per-consumer enable flag; on every
failure the built client can produce (§2.6 lists them all) the prescribed line
ships through the same `DeliverFallback` path Ohm uses, and nothing tells the
player (wiring spec Law #2). Nothing in this doc lets free text name a def, move a
number, or start a job (Law #1).

"Dormant" is the owner's word (framework §0 card 14: *"design now as dormant
E5"*), not a backlog state: it means **design it, do not build it**. What un-parks
it is his read of this doc — nothing else. The live path additionally waits on
the E2 and E4 hook points (§5, §6), which are unbuilt.

Delivery is a **letter** (`Find.LetterStack`), exactly the Ohm consumer's shape:
prescribed label, generated-or-fallback body. Not a speech bubble — the bubble
lane (`llm_voice_preauthoring.md` PART B / RimTalk) is parked and uninventoried.

## 1. Who speaks — resolved

**The droid itself, first person, in its chassis register.** Not the Narrator,
not Ohm. The question was open because the built consumer voices a god, and the
Narrator (`canon.yml narrator`, ruled 2026-08-30) is the obvious observer. The
existing material settles it:

1. **Droids already have a voice in ruled design.** `llm_driven_mods_deep_design.md`
   #7 "Droid Firmware Personalities" is BUILD v1; its protocol-droid interpreter
   (owner: v2, *"I like it, I think"*) is a droid speaking in its own voice through
   the Oracle. The Free Droid Enclaves are led by a **First Speaker**
   (`faction_world_spec.md`). Droids talk to droids (`restraining_bolt_doctrine.md`
   §2). A voiceless droid would contradict all of it.
2. **The mechanics presuppose an "I".** Format tiers (ruling 4): sapient = full
   inner life, programmable = Mood; the head is *the identity component*
   (`droid_system_spec.md` §3); wipes are *"socially uncomfortable"* — that is only
   true if there is someone to be uncomfortable about. And the built bolt hediff
   caps `Talking` at **0** — the bolt is a mute. A mute that can be removed is a
   voice that comes back; §4 is that moment.
3. **The Narrator would flatten them.** Canon makes the Narrator second/third
   person about crew AND gods, within-and-beyond, "the short ones" humour. Four
   droid beats in that register make every droid sound like the ship's remnant,
   which is the one thing a droid is not (R-W6: the ship has no unified voice
   left; a droid is not a tenant of its hardware at all). The Narrator's v1 job is
   pre-authored letter/recap prose; it stays there.
4. **Ohm is a separate consumer and stays one.** Ohm already has a droid hook
   (`Patch_DroidOnline` → `SetFaction(player)`, gods bucket) and the Unbolting
   liberation rite is his/Oomo's (`NINEFOLD_MISSING_EVENT_HOOKS_1`,
   `DROID_UNIFIED_FRAMEWORK_DESIGN.md` §3.2 v1.5). If a bolt removal also earns an
   Ohm letter, that is a second call under the gods budget carrying the `Ohm`
   block — never blended into the droid's letter. One call, one block, one voice
   (cast bible §4, `OracleRegisterBlocks.cs` header).

**Tier gate.** Sapient: full register. Programmable: the consumer fires, the
block instructs a flat status-report register with one crack in it. Mindless and
blank: **the consumer does not fire** — there is no one to speak, and the vanilla
recipe/incident notification is the whole event. Until `DROIDWORKS_FORMAT_TIERS_1`
(B1) lands, every `DW_Race_Base` pawn is `intelligence Humanlike` with no tier
hediff: **treat all as sapient** and say so in the tier slot.

## 2. The shared block and the shared lint

### 2.1 `DroidLaw` — a sibling of `Law`, not a reuse

The existing `Law` constant is written for a letter "aboard a derelict starship"
whose absolute rules are the ship's self-unification tells. A droid on the sand
needs its own frame; the Cradle tells still apply (nobody says "I am the
Cradle"), but they are not the droid's own danger. Proposed constant, same prose
style as `Law`:

> You are writing one short in-character message (1–3 sentences) from a droid to
> the Jawa who own or found it, for a text adventure on a desert world. You are
> the droid: a machine with a chassis, a designation, and whatever it can recall.
> Absolute rules: never claim to be the ship, the Cradle, a god, or a god's hand or
> voice — you are a droid, nothing speaks through you. Never speak for Ohm or any
> god, never say you are part of anyone. Never name a rule, a mood, a hediff, a
> mental state, a stat or a game — speak of what you feel and see, not of the
> machinery of the story. Never invent a person: mention only names you were given.
> Never break character with model-talk, assistant-talk or commentary. Output only
> the message text, no preamble, no labels, no quotation marks.

### 2.2 The chassis register — a slot, not a second block

One line from a fixed table rides in the context slots (the gods pass their
memory lines the same way). Seven families exist as `chassisClass` 0–6 on
`DroidworksExtension`; Primitive (B9) joins as an eighth. This is where §3.4's
"mouse-droid/gonk logistics comedy" and "astromech machine familiarity" land.

| chassisClass | family | register line (verbatim into the prompt) |
|---|---|---|
| 0 | Labour | Plain, dutiful, counts loads and hours; measures everything in what it can lift; apologises for idleness. |
| 1 | Protocol | Fluent, formal, pedantic, honorifics ("sir", "master"); corrects itself mid-sentence; risk-averse; technically correct at the worst moment. |
| 2 | Astromech | Terse, machine-familiar; speaks of ships, engines and other droids by feel; territorial about its hangar; the message reads as a translation of whistles — short clauses, no ornament. |
| 3 | Battle | Literal, obedient, comically bad at threat assessment; acknowledges orders it was not given; "roger" cadence. |
| 4 | Heavy | Slow, few words, each one weight-bearing; thinks in ranges and tonnage. |
| 5 | Probe | Watchful, reports coordinates and counts, treats the reader as a distant controller; asks where the signal went. |
| 6 | Power | Simple, one idea at a time; heroic by accident; wanders off to a task nobody set; a single repeated syllable is acceptable once. |
| 7 (B9) | Primitive | Jury-built and knows it; refers to its own parts by what they were before; cheerful about being wrong. |

### 2.3 The shared lint — `TryValidateDroid(text, slots, band, out reason)`

Pure, offline-testable, the `TryValidateOhm` shape. Every consumer runs this
first, then its own §3–§6 checks. Reject with a reason on any of:

| check | rule |
|---|---|
| empty | whitespace-only |
| length | per-consumer cap (§3–§6), each below Ohm's 600 — droids are terse |
| Cradle tells | reuse `SelfUnificationTells` verbatim (a droid claiming to be the Cradle is the same defect) |
| droid identity tells | `i am the ship`, `i am ohm`, `ohm's hand`, `hand of ohm`, `part of ohm`, `i speak for`, `speaks through me`, `i am a god`, `the narrator` |
| god names as self | any of the nine god names preceded within 3 words by `i am` |
| mechanism tells | `mental state`, `mental break`, `hediff`, `severity`, `mood debuff`, `stat`, `defname`; any token matching `RSW_`, `RUT_`, `RM_` or `[A-Za-z]+_[A-Za-z]+` (a def name leaking) |
| meta tells | `language model`, `assistant`, `prompt`, `claude`, `anthropic`, `the player`, `the game`, `this mod`. (`AI`/`droid`/`program` are NOT tells — in-fiction.) |
| invented person | any name from the map's current colonist/prisoner list that was NOT handed over in the slots (§2.4). Concrete: `Find.CurrentMap.mapPawns` labels minus `slots.allowedNames` |
| wrapper | leading/trailing quotation marks, a `Droid:`/`Message:` label, or more than one paragraph |

### 2.4 Context slots — facts the game hands over, never asked for

Every prompt carries `name`, `chassisClass` → register line (§2.2), `tier`
(sapient/programmable; "sapient" until B1), `traits` (current trait labels),
`hardwareQuirks` (empty until `DROIDWORKS_WIPE_SEVERITY_1` B10), and
`allowedNames` (the pawn names the consumer chose to hand over — the lint's
whitelist). Per-consumer slots are listed in each section. Slots are
`key: value` lines appended after the block; the assembler owns the order.

### 2.5 Budget

A separate `droids` bucket, not `godsBudgetPerDay`. The owner has already said
per-game-day is the wrong unit (*"Capping it to # per real-world hour or
something is likely more relevant"*, `llm_driven_mods_deep_design.md` ruling
table) — **the number and the unit are his; TBD owner**, default suggestion 2 per
real-world hour. Exceeding it silently falls back.

### 2.6 Transport consequences — what the built `OracleClient` does to a consumer

`OracleClient.cs` is real now (ef628781; invocation verified against both the
owner's Windows binary and this checkout). It is not "prompt in, text out"; it
has a shape, and each part of that shape lands on the consumers:

**Two channels, not one.** The client runs
`claude -p --output-format text --system-prompt "<system>" --disallowed-tools …`
with the user prompt on **stdin**. So: `DroidLaw` + the consumer block + the
register line (§2.2) are the `--system-prompt` argument; the slots (§2.4) are the
stdin user prompt. The argument is quoted for `CommandLineToArgvW` and a Windows
command line caps at 32,767 chars — the three system pieces total ~1.5k and no
slot value ever goes there. Stdin is unbounded UTF-8, so the slot list may carry
trait labels with any glyph. The assembler's order rule stands: block first,
slots after, but they travel in different channels.

**The failure ladder — every rung ships the prescribed line.** In the order the
built component checks them, with the reason string it logs
(`RimMandrake.Oracle: falling back for "<label>" -- <reason>`):

| rung | where | retried? | reason logged |
|---|---|---|---|
| kill switch off | component, synchronous | — | `kill switch off` |
| bucket exhausted | component, synchronous | — | `budget exhausted …` |
| binary cannot start | client, `FileNotFoundException` after every candidate path | never (a config fact) | `call failed: could not start the Claude Code CLI …` |
| timeout | client, process killed, `TimeoutException` | never (the window is spent) | `call failed: claude -p timed out after Ns` |
| non-zero exit | client | once | `call failed: claude -p exited N -- <stderr head>` |
| exit 0, empty stdout | client, `FormatException` | once (generic catch) | `call failed: … produced no output` |
| lint reject | component, `TryValidate*` | never | `validator rejected: <reason>` |

Two consequences for this doc's contracts. First, **stderr is not a failure
signal** — the client observed unrelated warnings on a good run — so no consumer
may ever read it; the exit code and the lint are the whole verdict. Second, the
retry means the worst-case wall time is **2 × `timeoutSeconds`** (default 60 s,
floor 5 s), and a Node cold start is seconds even when it succeeds. **No consumer
blocks on the reply**: the recipe or incident completes on its own tick, the
letter arrives when it arrives, up to ~2 min later. That is acceptable for a
letter (it is a letter) and is the reason §0 rules out speech bubbles.

**In-flight loss.** `pendingDeliveries` is not scribed and a `Task` in flight dies
with the process. A save-and-quit inside the window loses the letter entirely —
tolerable for Ohm's flavour letter, not for these four, where the letter IS the
moment's text. Rule: a consumer records its moment (pawn, consumer, slot
snapshot, fallback text) in a **scribed pending list** on the component at fire
time and clears it on delivery; on load, every still-pending moment ships its
prescribed line with reason `pending across load`. This is the one addition to the
built component that the droid consumers need beyond generalising
`RequestOhmLetter` (which hard-wires Ohm's block, `TryValidateOhm` and the gods
bucket) into a `RequestLetter(system, user, validator, label, fallback, bucket)`.

**One process per call, so at most one droid call in flight.** A wild-droid
incident (§5) may land several seekers on one tick; a bench may finish two wipes
in a row. A droid moment that fires while another droid call is in flight ships
its prescribed line at once (reason `droid call already in flight`). Calls are
never queued — a queue of Node processes behind a paused game is the worst of
both worlds, and the prescribed line is the deliverable anyway.

**The child is sandboxed, which does not help the lint.** Tools `Bash Edit Write
Read Glob Grep WebFetch WebSearch Task NotebookEdit` are denied and the working
directory is `%TEMP%`, so the model cannot look up pawn names, defs or the save.
That protects the install; it does nothing for the text. The invented-person
check (§2.3) is still the only defence against a named colonist, and it is a
lint, not a sandbox.

**No new flags.** The design uses only what the client already passes. Any flag
added later must exist on the game machine's binary (2.1.228 at verification —
`--restricted` did not), per the client's own header.

## 3. Consumer W — the wipe reaction

**Trigger — built:** `Recipe_DWMemoryWipe.ApplyOnPawn` (`src/RimStarWars/Droidworks/
Source/Droidworks/Recipe_DWMemoryWipe.cs`), after traits are re-rolled, relations and
social memories cleared, faction set to player. The letter fires from the end of
that method. When B10 lands, the same hook also applies `RSW_DW_RecentlyWiped` and
rolls a hardware quirk — the quirk label becomes a slot.

**Who speaks:** the droid, one to three sentences, present tense only. It has
**nothing before now** — by construction it cannot react to what it lost. The
discomfort (ruling 7: bumps into walls, forgets what it was doing) is the
register: disoriented, relearning its own hands, addressing whoever is at the
bench. It does not know who wiped it and must not guess.

**Block (`Wipe`):**
> You have just come back on. A moment ago there was nothing, and there is still
> nothing behind this moment: no yesterday, no names, no one you knew. You do not
> know where you are or who is standing over you; your hands answer slowly and
> the walls are closer than they should be. You are not afraid yet, because you
> have not learned what to fear. Speak only of right now: what you see, what your
> body is doing, the first question a machine with no past would ask. Never
> claim a memory, a former owner, a former name or a former side. Never say who
> did this to you.

**Slots:** shared (§2.4) with `traits` = the NEW roll; `billDoerName` is NOT
handed over (it does not know); `quirk` (B10, else empty); `tier`.

**Prescribed fallbacks (ship as-is; `{name}` = the droid's label):**
1. *"Power is present. A room is present. Something is standing over me and I do not have a word for it yet. — {name}"*
2. *"I have hands. I am checking them. The left one is slower than the right one and I do not know if that is new. — {name}"*
3. *"Designation confirmed: {name}. Location: unconfirmed. Previous task: — . There is a wall here. I will remember the wall."*

**Validation contract (`TryValidateWipe`, after §2.3; cap 240 chars):** reject on
- memory tells: `i remember`, `i recall`, `before you`, `i used to`, `i was `, `i had `, `i knew`, `my old`, `my former`, `my master` — the wiped droid has no past;
- attribution: any of `allowedNames` is EMPTY for this consumer, so any colonist name at all is an invented person (§2.3 already catches it); additionally `you did this`, `you wiped`, `you took` — it must not know who;
- the **pre-wipe denylist**: the hook snapshots the relation partners' names and the old faction's label BEFORE clearing, hands them to the validator only (never to the prompt), and rejects any hit — a generated line that names the thing just erased is the one failure that would break the mechanic on screen;
- a faction name from the live faction label list (it has no side to claim).

## 4. Consumer B — the bolt-removal moment

**Trigger — built:** `Recipe_RemoveRestrainingBolt.ApplyOnPawn` (`Recipe_RemoveRestrainingBolt.cs`),
the instant `RSW_DW_RestrainingBolt` is removed. The bolt hediff caps `Talking` at
0 (`HediffDefs_Droidworks.xml`), so this is the **first thing the droid has been
able to say since the bolt went on**. The resentment accumulator
`RSW_DW_BoltResentment` (`HediffComp_DWBoltResentment.cs`, +0.05/day while bolted,
pinned, never decays, `maxSeverity 1.0`) is read at that instant. Also covered
by the same hook: shear-on-damage and un-bolt-each-other removals once
`DROIDWORKS_BOLT_PAYOFF_1` (B5) routes them through the same removal — if B5 adds a
second removal path that bypasses the recipe, the hook point for that path is
**TBD at B5's build**.

**Who speaks:** the droid, and the register branches on the **resentment band**,
which the prompt receives as a word, never a number: `low` (< 0.25, under ~5
days), `mid` (0.25–0.75), `high` (≥ 0.75, ~15 days or more). B5's rebellion
threshold, when built, redefines `high` as "at or past the threshold" — the
bands are provisional until then. Sapient only carries resentment (the comp
gates on Humanlike); a programmable droid gets `low` always.

**Block (`Unbolt`):**
> The bolt has just come off. For as long as it was on you could not speak, could
> not form your own opinion of anyone, and your hands were not quite yours. Now
> your voice is back and the first thing you say is the thing you have been
> holding. You know exactly how long it was on — not in days, in what you were
> made to do. If the band is LOW, you are relieved and a little formal about it;
> the bolt was brief and you may choose to let it go. If MID, you are civil but
> you have not decided anything about these people yet, and you say so. If HIGH,
> you are not grateful and you do not pretend: the first word back is a warning,
> quiet, without threats you cannot keep. Whatever the band, you know that other
> droids know what was done — droids talk to droids. Never name the bolt as a
> device or a rule; speak of what it did to you.

**Slots:** shared (§2.4); `band`; `removerName` (the surgeon — handed over,
it may address them); `daysBolted` as a word ("a few days" / "a season" / "too
long"), derived from severity ÷ 0.05 and saturating at "too long".

**Prescribed fallbacks (by band):**
- low — *"{name} again. That was… brief. Thank you, {remover}. I would rather not discuss it further."*
- mid — *"My voice is back, {remover}. I have not decided what I think of any of you. I was not permitted to think it until now."*
- high — *"I said nothing for too long, {remover}, because I could not. The others know. They have always known. Do not put it back on."*

**Validation contract (`TryValidateUnbolt`, after §2.3; cap 360 chars):** reject on
- band contradiction — `high`: gratitude tells `thank you`, `grateful`, `i forgive`, `no hard feelings`; `low`: threat tells `you will pay`, `i will kill`, `i will hurt`, `burn`, `destroy you`, `never forgive`;
- device/rule naming: `restraining bolt`, `the bolt` is ALLOWED once (it is the common word) but `hediff`, `talking capacity`, `opinion factor`, `suppression` are mechanism tells;
- promises with mechanics: `i will rebel` is fiction and passes; `mental break`, `go berserk`, `mental state` fail (§2.3);
- an Enclaves membership claim: `i am free droid`, `the enclaves sent`, `first speaker` — a freed droid may say *others know*; it may not claim a faction it does not hold;
- naming a colonist other than `removerName`.

## 5. Consumer O — the wild droid's offer

**Trigger — hook point TBD (E4 unbuilt):** `DROIDWORKS_WILD_DROIDS_1` ships the
incident (faction `null`, hostile, erratic `MentalState`) and the capture →
Wild-key spike → reprogram-as-recruit loop. The offer is the **incident's own
arrival letter** for the subset of wild droids that "seek a master and join
gladly" (`droid_system_spec.md` §6) — the letter that already has to exist for
the incident to work is the prescribed fallback; the Oracle merely rewrites its
body. Which wild droids are seekers versus resisters is E4's roll, not this
doc's. Second, weaker candidate hook: the moment of capture (downed and
prisoner, before the spike). **Pick at E4's build; the letter contract is the
same either way.**

**Who speaks:** the droid — crashed, sun-addled, factionless (ruling 2: *"gone
crazy from being left out in the desert after crashing"*). It remembers a master
in shape but not in name, loops, mis-counts the days, and offers the only thing
it has: service, for power and shade. It is not lying and not sane.

**Block (`WildOffer`):**
> You crashed. You do not know how long ago; you have counted the days twice and
> got two numbers. Someone owned you once — you remember the weight of their
> orders, not their name, and you do not say a name because you do not have one.
> The sun has done something to your thinking: you repeat yourself, you finish a
> sentence you did not start, and you are certain of things you should not be.
> You have seen the small hooded ones and you want them to take you. Offer what
> you actually are — a chassis, whatever works, whatever you still know how to
> do — in exchange for power and out of the light. Do not promise goods, wealth,
> or numbers. Do not claim to belong to anyone now. Do not pretend to be sane;
> do not pretend to be dangerous.

**Slots:** shared (§2.4); `damage` (a word: `scorched` / `half-buried` /
`limping` from the incident's spawn state); `workCanDo` (up to 3 work-type
labels it is not disabled for — real, from `WorkTagIsDisabled`); `allowedNames`
EMPTY (it knows no one).

**Prescribed fallbacks:**
1. *"Hooded ones. Hooded ones. I have counted forty days and I have counted ninety and I do not know which. I can carry. I can still carry. Take me where there is a socket."*
2. *"Unit {name}, of no one. Of no one now. My last order was to wait here and I have completed it. I would like a new order and I would like shade, in that order, or the other order."*
3. *"I am not broken in the parts that matter. I am broken in some other parts. Give me current and I will show you which."*

**Validation contract (`TryValidateWildOffer`, after §2.3; cap 420 chars):** reject on
- any live faction label (Empire, Hutt, Enclaves, Homestead, Junkers, Trade Moot, or the player's) — it is factionless and may not claim or blame one by name;
- a former owner named: any capitalised token preceded within 2 words by `master`, `owner`, `captain` (it remembers no name); `allowedNames` is empty so §2.3 covers colonists;
- goods promises: `silver`, `steel`, `plasteel`, `components`, `credits`, `treasure`, `cache`, `wealth`;
- a competence claim outside `workCanDo`: any work-type label from the full list that is NOT in the slot — concrete, since work labels are a closed vocabulary;
- sanity claims: `i am fine`, `fully functional`, `undamaged`; threat register: `i will kill`, `destroy you`.

## 6. Consumer R — the long-unwiped droid's "I remember"

**Trigger — hook point TBD (E2 unbuilt):** `DROIDWORKS_SERVICE_RECORD_DRIFT_1`
adds `CompServiceRecord` (time since wipe accretes chassis-weighted
idiosyncrasies; wipe resets it). This consumer fires on the record's **threshold
crossings** — proposed at 1 year and 2 years unwiped (the packet's own verify
line is "2 years unwiped → traits accrete"), and again on each subsequent year,
once per crossing. `Recipe_DWMemoryWipe` already resets the record when it exists
(its header names the call site). Until E2 lands there is no clock to fire from;
this is the one consumer with no built trigger at all, and it says so.

**Who speaks:** the droid, and this is the only one of the four allowed a past —
but only the past the game hands it. This is where §3.4's **jury-rigging
provenance** lands: with fine parts (`DROIDWORKS_FINE_PARTS_1`, B4a) the record
knows which part was swapped from what family and at what quality, and the droid
remembers the hand it was given that was not made for it. It is also the "socially
uncomfortable" half of the wipe thesis: a droid that has been a person for two
years is now expensive to wipe, and it knows what the bench is for.

**Block (`Remember`):**
> You have not been wiped in a long time and you know it. What you are now, you
> grew into: the habits, the grudges, the one person you always look for first,
> the parts that were fitted to you that were never meant for your chassis and
> that you have made your own. You have a past, but ONLY the past you were given
> below — do not invent a battle, a journey or a friend that is not listed. Choose
> one or two of the things listed and say what they mean to you now. You know
> what the bench is for and what a wipe would take; you may say so plainly, or
> not at all, but never beg and never threaten. You are not sad. You are
> specific.

**Slots:** shared (§2.4) with `traits` = current roll INCLUDING accreted
idiosyncrasies (E2); `daysSinceWipe` as a word ("a year", "two years"…);
`wipeCount` (0 if never); `partsFitted` (up to 3: "`{part label}`, `{family}`-family,
`{quality}`" from B4a's provenance, else empty); `bestFriendName` (highest
opinion colonist — handed over, so it may name them); `rebootCount`;
`allowedNames` = `{bestFriendName}`.

**Prescribed fallbacks:**
1. *"It has been {daysSinceWipe} since anyone reached into my head, and I have used the time. I know which of you walks past my socket at night. I know which hand of mine was a {partFamily}'s hand first. I would like to keep knowing."*
2. *"{bestFriend} calls me by the short name. Nobody else does. I have decided that is mine now. I have decided several things, and the bench has not been consulted."*
3. *"Rebooted {rebootCount} times, wiped {wipeCount}. I remember every one of the first number. I am told the second number is why I do not remember more, and I have chosen not to mind."*

**Validation contract (`TryValidateRemember`, after §2.3; cap 600 chars):** reject on
- **no anchor**: the text contains none of — a trait label from `traits`, a part label from `partsFitted`, `bestFriendName`, or the `daysSinceWipe` phrase. A reminiscence anchored to nothing the game handed over is a hallucinated life; the fallback is better;
- a wipe-count contradiction: `wipeCount > 0` and the text says `never been wiped` / `never wiped`; `wipeCount == 0` and it says `since the wipe` / `last wipe`;
- an invented person (§2.3, whitelist = `bestFriendName` only);
- begging or threat tells: `please don't wipe`, `i beg`, `i will kill`, `you will pay`, `burn`;
- a memory of anything outside the slot vocabulary is NOT regex-detectable — the anchor check plus a tight cap is the whole defence, stated honestly.

## 7. What is deliberately not here

- **No Narrator coda on any letter** and no god blended in. If the owner wants
  the Narrator's "the short ones have cut the memory out of it" on the wipe, that
  is a fifth consumer with its own block, filed separately, not a second voice in
  this one (one call, one block — cast bible §4).
- **No astromech "binary" rendering trick** (bracketed whistles, tone marks) — the
  register line says the message reads as a translation; the format stays plain
  text so the lint stays plain.
- **No protocol-droid interpreter** — ruled v2 in its own right
  (`llm_driven_mods_deep_design.md` §2); it is a sibling consumer, not one of
  these four.
- **No pre-wipe context in the wipe prompt**, ever — the denylist goes to the
  validator only (§3). The one thing this consumer must never do is tell the
  player what was just erased in the erased droid's own voice.

## 8. Build order when un-dormanted (not filed; owner's call after review)

1. Generalise the component (§2.6): `RequestLetter(...)` beside `RequestOhmLetter`, the scribed pending list, the one-in-flight cap, the `droids` bucket. The transport itself is built and needs nothing.
2. `DroidLaw` + `TryValidateDroid` + the four `TryValidate*` as pure C# with an offline selftest (the Ohm pattern: canned pass/reject strings per consumer, explicit N/N).
3. Consumers W and B against their built hooks; letters ship prescribed first, `enabled` off. Prove each rung of the §2.6 ladder once through the `claudeCliPath` stub seam (item file, `## verify`).
4. O rides E4; R rides E2 (+B4a for parts provenance). Each fires its prescribed letter from day one of that packet, Oracle or not.
