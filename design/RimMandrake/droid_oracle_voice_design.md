<!-- status: RULED, LIVE — DROID_ORACLE_VOICE_DESIGN_1. Fable pass 2026-09-08; rewritten
     2026-09-25/26 to the owner's rulings (ledger notes on the item): Narrator, third person
     (typed, reversing the same evening's card); droid calls share the gods' budget (card);
     late letters accepted for now (typed); Battle register tone ruled (typed); all four
     consumers live (card); programmable droids never fire (card); W/B fixed lines ship now
     (card). Reads on top of (never restates): llm_ingame_wiring_spec.md (the two laws, the
     pipeline), nine_voices_cast_bible.md (the persona-block pattern and the Narrator),
     OracleRegisterBlocks.cs / OracleValidator.cs (the one built consumer, Ohm),
     droid_system_spec.md §3–§7 (embodied software, tiers, spikes, the bolt). Transport is
     the BUILT OracleClient.cs (`claude -p`, ef628781, re-verified d9b909c8); §2.6 states what
     that transport does to every consumer. The prescribed fallbacks below need no LLM at all. -->
# Droid moments through the Oracle — Narrator letters, four consumers, live

## 0. What ships, and when

All four consumers (W, B, O, R) are **live** — decision taken by question card
2026-09-25. Each of the four moments ships as **prescribed text first** — the
fallback lines in §3–§6 are a real deliverable and run with zero LLM calls, and
the W and B fixed lines **ship now** (decision taken by question card
2026-09-25). The Oracle call is an enrichment layered on top, behind
`OracleGameComponent`'s existing kill-switch (`OracleSettings.enabled`, default
off) and a per-consumer enable flag; on every failure the built client can
produce (§2.6 lists them all) the prescribed line ships through the same
`DeliverFallback` path Ohm uses, and nothing tells the player (wiring spec Law
#2). Nothing in this doc lets free text name a def, move a number, or start a
job (Law #1).

Consumers O and R additionally wait on the E4 and E2 hook points (§5, §6),
which are unbuilt; each fires its prescribed letter from day one of that
packet, Oracle or not.

Delivery is a **letter** (`Find.LetterStack`), exactly the Ohm consumer's
shape: prescribed label, generated-or-fallback body. A letter that arrives
after the moment is accepted — owner, 2026-09-25: *"yes they can come larter
for now"* (§2.6 gives the worst-case window). Not a speech bubble — the bubble
lane (`llm_voice_preauthoring.md` PART B / RimTalk) is parked and uninventoried.

## 1. Who speaks — ruled: the Narrator, third person

Owner, typed, 2026-09-25 (reversing the same evening's card): *"Letters should
come from the Narrator. They will speak of the droid in third person."*

- Every letter in this doc is the **Narrator's** (`canon.yml narrator`, ruled
  2026-08-30): within-and-beyond, dry, "the short ones" humour, second person
  to the player where it suits — and **third person about the droid, always**.
  The Narrator never speaks as the droid.
- The droid's own manner still reaches the player — as the Narrator's report
  of what the droid did and said, with at most **one short quoted line** in
  the droid's chassis register (§2.2). The register table constrains that
  reported manner; it is never a licence for a first-person letter.
- **Ohm is a separate consumer and stays one.** Ohm already has a droid hook
  (`Patch_DroidOnline` → `SetFaction(player)`, gods bucket) and the Unbolting
  liberation rite is his/Oomo's (`NINEFOLD_MISSING_EVENT_HOOKS_1`,
  `DROID_UNIFIED_FRAMEWORK_DESIGN.md` §3.2 v1.5). If a bolt removal also earns
  an Ohm letter, that is a second call under the same budget carrying the
  `Ohm` block — never blended into the droid letter. One call, one block, one
  voice (cast bible §4, `OracleRegisterBlocks.cs` header).

**Tier gate — ruled.** These consumers fire for **sapient** droids only.
**Programmable droids never fire** (decision taken by question card
2026-09-25 — dead, not deferred), and mindless and blank never fire; for all
three the vanilla recipe/incident notification is the whole event. Until
`DROIDWORKS_FORMAT_TIERS_1` (B1) lands, every `DW_Race_Base` pawn is
`intelligence Humanlike` with no tier hediff: **treat all as sapient** and say
so in the tier slot.

## 2. The shared block and the shared lint

### 2.1 `DroidLaw` — a sibling of `Law`, not a reuse

The existing `Law` constant is written for a letter "aboard a derelict
starship" whose absolute rules are the ship's self-unification tells. The
droid moments need their own frame; the Cradle tells still apply (nobody says
"I am the Cradle"). Proposed constant, same prose style as `Law`:

> You are writing one short message (1–3 sentences) from the Narrator of a
> text adventure on a desert world, about a droid the small hooded scavengers
> own or have found. You are not the droid: speak of it in the third person,
> by its designation, in the Narrator's dry, knowing voice. You may quote at
> most one short line of the droid's own speech, in its own manner. Absolute
> rules: never speak as the droid, and never let it claim to be the ship, the
> Cradle, a god, or a god's hand or voice — it is a droid, nothing speaks
> through it. Never speak for Ohm or any god. Never name a rule, a mood, a
> hediff, a mental state, a stat or a game — speak of what happens and what it
> means, not of the machinery of the story. Never invent a person: mention
> only names you were given. Never break character with model-talk,
> assistant-talk or commentary. Output only the message text, no preamble, no
> labels, and no quotation marks around the whole message.

### 2.2 The chassis register — a slot, not a second block

One line from a fixed table rides in the context slots (the gods pass their
memory lines the same way); it governs the droid's **reported manner and any
quoted line** inside the Narrator's letter. Seven families exist as
`chassisClass` 0–6 on `DroidworksExtension`; Primitive (B9) joins as an eighth.
This is where §3.4's "mouse-droid/gonk logistics comedy" and "astromech machine
familiarity" land.

**Only the Battle row is ruled.** Every other row below is an unruled
proposal — an **open owner question**. Do not build a register line into a
shipped prompt as settled until its row is ruled.

| chassisClass | family | register line | ruled? |
|---|---|---|---|
| 0 | Labour | *proposed:* Plain, dutiful, counts loads and hours; measures everything in what it can lift; apologises for idleness. | OPEN — owner question |
| 1 | Protocol | *proposed:* Fluent, formal, pedantic, honorifics ("sir", "master"); corrects itself mid-sentence; risk-averse; technically correct at the worst moment. | OPEN — owner question |
| 2 | Astromech | *proposed:* Terse, machine-familiar; speaks of ships, engines and other droids by feel; territorial about its hangar; its quoted speech reads as a translation of whistles — short clauses, no ornament. | OPEN — owner question |
| 3 | Battle | **Tone varies across deadpan comedy, plain report, and per-personality** (owner, 2026-09-25: *"Varies across all these"*). The assembler varies the register line per letter — keyed on the droid's traits or rotated — never one fixed cadence. | **RULED** |
| 4 | Heavy | *proposed:* Slow, few words, each one weight-bearing; thinks in ranges and tonnage. | OPEN — owner question |
| 5 | Probe | *proposed:* Watchful, reports coordinates and counts, treats its reader as a distant controller; asks where the signal went. | OPEN — owner question |
| 6 | Power | *proposed:* Simple, one idea at a time; heroic by accident; wanders off to a task nobody set; a single repeated syllable is acceptable once. | OPEN — owner question |
| 7 (B9) | Primitive | *proposed:* Jury-built and knows it; refers to its own parts by what they were before; cheerful about being wrong. | OPEN — owner question |

### 2.3 The shared lint — `TryValidateDroid(text, slots, band, out reason)`

Pure, offline-testable, the `TryValidateOhm` shape. Every consumer runs this
first, then its own §3–§6 checks. Reject with a reason on any of:

| check | rule |
|---|---|
| empty | whitespace-only |
| length | per-consumer cap (§3–§6), each below Ohm's 600 — these letters are terse |
| person | outside a quoted span, first-person-as-the-droid tells: `i am`, `i was`, `my chassis`, `my designation`, `my master` — the Narrator never speaks as the droid; the one allowed quoted line is exempt |
| Cradle tells | reuse `SelfUnificationTells` verbatim (a letter claiming the droid is the Cradle is the same defect) |
| identity tells | `i am the ship`, `i am ohm`, `ohm's hand`, `hand of ohm`, `part of ohm`, `i speak for`, `speaks through me`, `i am a god`, `the narrator` (it never names itself) |
| god names as self | any of the nine god names preceded within 3 words by `i am` or `it is` |
| mechanism tells | `mental state`, `mental break`, `hediff`, `severity`, `mood debuff`, `stat`, `defname`; any token matching `RSW_`, `RUT_`, `RM_` or `[A-Za-z]+_[A-Za-z]+` (a def name leaking) |
| meta tells | `language model`, `assistant`, `prompt`, `claude`, `anthropic`, `the player`, `the game`, `this mod`. (`AI`/`droid`/`program` are NOT tells — in-fiction.) |
| invented person | any name from the map's current colonist/prisoner list that was NOT handed over in the slots (§2.4). Concrete: `Find.CurrentMap.mapPawns` labels minus `slots.allowedNames` |
| wrapper | a message that is one single quoted block (the quote budget is one short line inside Narrator prose), a `Narrator:`/`Message:` label, or more than one paragraph |

### 2.4 Context slots — facts the game hands over, never asked for

Every prompt carries `name`, `chassisClass` → register line (§2.2), `tier`
(sapient — programmable never reaches these consumers, §1; "sapient" for all
until B1), `traits` (current trait labels), `hardwareQuirks` (empty until
`DROIDWORKS_WIPE_SEVERITY_1` B10), and `allowedNames` (the pawn names the
consumer chose to hand over — the lint's whitelist). Per-consumer slots are
listed in each section. Slots are `key: value` lines appended after the block;
the assembler owns the order.

### 2.5 Budget — ruled: shared with the gods

Droid letters draw from the **same bucket as the gods' letters** — decision
taken by question card 2026-09-25. There is no separate `droids` bucket, and
no new number or unit is owed for this feature; whatever the gods' budget is
or becomes, these calls charge it. Exceeding it silently falls back to the
prescribed line, same as every other rung of §2.6's ladder.

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
letter arrives when it arrives, up to ~2 min later. Ruled acceptable — owner,
2026-09-25: late letters are accepted for now — and it is the reason §0 rules
out speech bubbles.

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

**The moment:** the Narrator, over a droid that has **nothing before now** — by
construction it cannot react to what it lost. The discomfort (ruling 7: bumps
into walls, forgets what it was doing) is the material: disoriented, relearning
its own hands. Neither the droid nor the letter says what was erased or names
who did it.

**Block (`Wipe`):**
> The droid has just come back on. A moment ago there was nothing, and there is
> still nothing behind this moment for it: no yesterday, no names, no one it
> knew. It does not know where it is or who is standing over it; its hands
> answer slowly, and it is not afraid yet, because it has not learned what to
> fear. Write the moment as the Narrator sees it — what the droid does first,
> the first question a machine with no past would ask. Never give it a memory,
> a former owner, a former name or a former side. Never say what was erased or
> name who erased it.

**Slots:** shared (§2.4) with `traits` = the NEW roll; `billDoerName` is NOT
handed over (no surgeon is named); `quirk` (B10, else empty); `tier`.

**Prescribed fallbacks (ship NOW — owner card 2026-09-25; `{name}` = the droid's label):**
1. *"The short ones have cut the memory out of it. {name} is checking its hands as though they arrived a moment ago — which, in every way that matters, they did."*
2. *"{name} woke to a room, a wall, and something standing over it that it has no word for yet. It has decided to memorise the wall first."*
3. *"Designation {name}. Location: unconfirmed. Previous task: none it can name. It is not afraid. Nobody has taught it that yet."*

**Validation contract (`TryValidateWipe`, after §2.3; cap 240 chars):** reject on
- memory tells: `it remembers`, `it recalls`, `it used to`, `its old`, `its former`, `its master`, `before the wipe` — the wiped droid has no past, and the letter does not narrate the erased one either;
- the **pre-wipe denylist**: the hook snapshots the relation partners' names and the old faction's label BEFORE clearing, hands them to the validator only (never to the prompt), and rejects any hit — a generated line that names the thing just erased is the one failure that would break the mechanic on screen;
- a faction name from the live faction label list (no erased side is named);
- `allowedNames` is EMPTY for this consumer, so any colonist name at all is an invented person (§2.3 already catches it) — the Narrator may say the short ones did it collectively; it may not name the surgeon.

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

**The moment:** the Narrator reports the droid's first words back, and the
temper of those words branches on the **resentment band**, which the prompt
receives as a word, never a number: `low` (< 0.25, under ~5 days), `mid`
(0.25–0.75), `high` (≥ 0.75, ~15 days or more). B5's rebellion threshold, when
built, redefines `high` as "at or past the threshold" — the bands are
provisional until then. Only sapient droids reach this consumer (§1), and the
resentment comp gates on Humanlike, so every letter has a real band.

**Block (`Unbolt`):**
> The bolt has just come off the droid. For as long as it was on, the droid
> could not speak, could not form its own opinion of anyone, and its hands were
> not quite its own. Its voice is back, and the first thing it says is the
> thing it has been holding. Write the moment in the Narrator's voice, third
> person, and let the band set the temper of what the droid says: if the band
> is LOW, it is relieved and a little formal, and may choose to let the matter
> go. If MID, it is civil but has decided nothing about these people yet, and
> says so. If HIGH, it is not grateful and does not pretend — its first words
> back are a quiet warning, without threats it cannot keep. Whatever the band,
> other droids know what was done — droids talk to droids. Never name the bolt
> as a device or a rule; speak of what it did to the droid.

**Slots:** shared (§2.4); `band`; `removerName` (the surgeon — handed over,
the letter may name them); `daysBolted` as a word ("a few days" / "a season" /
"too long"), derived from severity ÷ 0.05 and saturating at "too long".

**Prescribed fallbacks (ship NOW — owner card 2026-09-25; by band):**
- low — *"The bolt is off. {name} thanked {remover} — briefly, formally — and asked that the matter not be discussed again. It may even mean to let it go."*
- mid — *"{name} has its voice back, courtesy of {remover}. It has not decided what it thinks of any of you. Until today, it was not permitted to think it."*
- high — *"{name} said nothing for too long, because it could not. Its first words back were quiet, and they were a warning. The other droids have always known."*

**Validation contract (`TryValidateUnbolt`, after §2.3; cap 360 chars):** reject on
- band contradiction — `high`: gratitude tells `thanked`, `thank you`, `grateful`, `forgives`, `no hard feelings`; `low`: threat tells `you will pay`, `will kill`, `will hurt`, `burn`, `destroy you`, `never forgive`;
- device/rule naming: `the bolt` is ALLOWED once (it is the common word) but `hediff`, `talking capacity`, `opinion factor`, `suppression` are mechanism tells;
- promises with mechanics: `it will rebel` is fiction and passes; `mental break`, `go berserk`, `mental state` fail (§2.3);
- an Enclaves membership claim: `free droid`, `the enclaves sent`, `first speaker` — a freed droid's *others know* is allowed; a faction it does not hold is not;
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

**The moment:** the Narrator reports a droid that is crashed, sun-addled and
factionless (ruling 2: *"gone crazy from being left out in the desert after
crashing"*). It remembers a master in shape but not in name, loops, mis-counts
the days, and offers the only thing it has: service, for power and shade. It is
not lying and not sane, and the Narrator does not pretend otherwise.

**Block (`WildOffer`):**
> A droid crashed out in the desert, long enough ago that it has counted the
> days twice and got two numbers. Someone owned it once — it remembers the
> weight of the orders, not the name, and no name is given because it has
> none. The sun has done something to its thinking: it repeats itself,
> finishes sentences it did not start, and is certain of things it should not
> be. It has seen the small hooded ones and it wants them to take it. Write
> its offer as the Narrator reports it: a chassis, whatever still works,
> whatever it still knows how to do, in exchange for power and out of the
> light. It promises no goods, no wealth and no numbers. It belongs to no one
> now and claims no one. It is not sane, it is not dangerous, and it is not
> lying.

**Slots:** shared (§2.4); `damage` (a word: `scorched` / `half-buried` /
`limping` from the incident's spawn state); `workCanDo` (up to 3 work-type
labels it is not disabled for — real, from `WorkTagIsDisabled`); `allowedNames`
EMPTY (it knows no one).

**Prescribed fallbacks:**
1. *"It has counted forty days and it has counted ninety, and it does not know which. It says it can carry. It says it twice. It would like to be taken to where there is a socket."*
2. *"Unit {name}, of no one — of no one now. Its last order was to wait here, and it reports the order complete. It would like a new order, and shade, in that order. Or the other order."*
3. *"It is not broken in the parts that matter, it says; it is broken in some other parts. Give it current and it will show you which."*

**Validation contract (`TryValidateWildOffer`, after §2.3; cap 420 chars):** reject on
- any live faction label (Empire, Hutt, Enclaves, Homestead, Junkers, Trade Moot, or the player's) — it is factionless and the letter may not claim or blame one by name;
- a former owner named: any capitalised token preceded within 2 words by `master`, `owner`, `captain` (it remembers no name); `allowedNames` is empty so §2.3 covers colonists;
- goods promises: `silver`, `steel`, `plasteel`, `components`, `credits`, `treasure`, `cache`, `wealth`;
- a competence claim outside `workCanDo`: any work-type label from the full list that is NOT in the slot — concrete, since work labels are a closed vocabulary;
- sanity claims: `fully functional`, `undamaged`, `it is fine`; threat register: `will kill`, `destroy you`.

## 6. Consumer R — the long-unwiped droid's "it remembers"

**Trigger — hook point TBD (E2 unbuilt):** `DROIDWORKS_SERVICE_RECORD_DRIFT_1`
adds `CompServiceRecord` (time since wipe accretes chassis-weighted
idiosyncrasies; wipe resets it). This consumer fires on the record's **threshold
crossings** — proposed at 1 year and 2 years unwiped (the packet's own verify
line is "2 years unwiped → traits accrete"), and again on each subsequent year,
once per crossing. `Recipe_DWMemoryWipe` already resets the record when it exists
(its header names the call site). Until E2 lands there is no clock to fire from;
this is the one consumer with no built trigger at all, and it says so.

**The moment:** the only one of the four allowed a past — but only the past the
game hands over. This is where §3.4's **jury-rigging provenance** lands: with
fine parts (`DROIDWORKS_FINE_PARTS_1`, B4a) the record knows which part was
swapped from what family and at what quality, and the letter can dwell on the
hand the droid was given that was not made for it. It is also the "socially
uncomfortable" half of the wipe thesis: a droid that has been a person for two
years is now expensive to wipe, and it knows what the bench is for.

**Block (`Remember`):**
> The droid has not been wiped in a long time, and it knows it. What it is
> now, it grew into: the habits, the grudges, the one person it always looks
> for first, the parts fitted to it that were never meant for its chassis and
> that it has made its own. It has a past, but ONLY the past listed below —
> do not invent a battle, a journey or a friend that is not listed. Write the
> Narrator's note of it: choose one or two of the listed things and say what
> they mean to the droid now. It knows what the bench is for and what a wipe
> would take; the letter may say so plainly, or not at all, but the droid
> neither begs nor threatens. It is not sad. It is specific.

**Slots:** shared (§2.4) with `traits` = current roll INCLUDING accreted
idiosyncrasies (E2); `daysSinceWipe` as a word ("a year", "two years"…);
`wipeCount` (0 if never); `partsFitted` (up to 3: "`{part label}`, `{family}`-family,
`{quality}`" from B4a's provenance, else empty); `bestFriendName` (highest
opinion colonist — handed over, so the letter may name them); `rebootCount`;
`allowedNames` = `{bestFriendName}`.

**Prescribed fallbacks:**
1. *"It has been {daysSinceWipe} since anyone reached into {name}'s head, and it has used the time. It knows which of you walks past its socket at night. It knows which of its hands was a {partFamily}'s hand first. It would like to keep knowing."*
2. *"{bestFriend} calls it by the short name; nobody else does. It has decided that name is its own now. It has decided several things. The bench has not been consulted."*
3. *"Rebooted {rebootCount} times, wiped {wipeCount}. It remembers every one of the first number, and it has chosen not to mind the second."*

**Validation contract (`TryValidateRemember`, after §2.3; cap 600 chars):** reject on
- **no anchor**: the text contains none of — a trait label from `traits`, a part label from `partsFitted`, `bestFriendName`, or the `daysSinceWipe` phrase. A reminiscence anchored to nothing the game handed over is a hallucinated life; the fallback is better;
- a wipe-count contradiction: `wipeCount > 0` and the text says `never been wiped` / `never wiped`; `wipeCount == 0` and it says `since the wipe` / `last wipe`;
- an invented person (§2.3, whitelist = `bestFriendName` only);
- begging or threat tells: `don't wipe`, `it begs`, `will kill`, `you will pay`, `burn`;
- a memory of anything outside the slot vocabulary is NOT regex-detectable — the anchor check plus a tight cap is the whole defence, stated honestly.

## 7. What is deliberately not here

- **No first-person droid letter.** The Narrator speaks, third person (owner,
  2026-09-25). A droid speaking in its own voice through the Oracle — the
  protocol-droid interpreter, ruled v2 in its own right
  (`llm_driven_mods_deep_design.md` §2) — is a separate future consumer with
  its own ruling, not a variant of these four.
- **No programmable-tier letter, ever.** Owner card, 2026-09-25: programmable
  droids never fire these consumers. Dead, not deferred.
- **No god blended in.** If a bolt removal also earns an Ohm letter, that is a
  second call under the shared budget carrying the `Ohm` block — never blended
  into the droid letter (one call, one block, one voice — cast bible §4).
- **No astromech "binary" rendering trick** (bracketed whistles, tone marks) — the
  register line says the quoted speech reads as a translation; the format stays
  plain text so the lint stays plain.
- **No pre-wipe context in the wipe prompt**, ever — the denylist goes to the
  validator only (§3). The one thing that letter must never do is tell the
  player what was just erased.

## 8. Build order — live (owner card 2026-09-25: all four consumers go)

1. Generalise the component (§2.6): `RequestLetter(...)` beside `RequestOhmLetter`, the scribed pending list, the one-in-flight cap. Droid calls charge the **gods' bucket** (§2.5) — no new bucket, no new number. The transport itself is built and needs nothing.
2. `DroidLaw` + `TryValidateDroid` + the four `TryValidate*` as pure C# with an offline selftest (the Ohm pattern: canned pass/reject strings per consumer, explicit N/N).
3. Consumers W and B against their built hooks; their prescribed lines **ship now** (owner card, 2026-09-25), `enabled` off by default. Prove each rung of the §2.6 ladder once through the `claudeCliPath` stub seam (item file, `## verify`).
4. O rides E4; R rides E2 (+B4a for parts provenance). Each fires its prescribed letter from day one of that packet, Oracle or not.
5. **Outstanding owner questions:** the seven unruled register rows (§2.2). Nothing above blocks on them — the Battle ruling and the shared `DroidLaw` are enough to ship.
