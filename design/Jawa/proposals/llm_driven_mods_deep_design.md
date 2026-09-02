<!-- status: DRAFT PROPOSAL for owner review — brainstorm sitting 2026-08-31, not ruled. -->
# The Oracle, cast wide — sparse LLM consumers for the whole campaign

Grounding docs: `research/Jawa/RimWorld_Sparse_LLM_Mod_Concepts.md` (the 30-concept
survey triaged below), `design/RimMandrake/llm_ingame_wiring_spec.md`
(`LLM_INGAME_WIRING_1`, owner-green-lit 2026-08-31 — the actual infrastructure this
proposal assumes), `design/RimMandrake/nine_voices_cast_bible.md`
(`NINE_VOICES_CAST_BIBLE_1` — the cast law), `design/Jawa/ownership_settlement_spec.md`
(the perception/knowledge fabric), `design/Jawa/bridge/INHABITED_DESIGN.md` (PLACE/
CAST/ROUTE/FATE), `design/Jawa/god_intercession_spec.md` and
`design/Jawa/devotional_sacrifice_catalog.md` (the shrine-heart).

**`ORACLE_EXPERIMENT_SPIKE_1` is CLOSED.** The thin OpenAI-compatible client
(`RimMandrake.Oracle` — `OracleClient`, async, fire-and-forget, hard timeout + one
retry, `MainThreadQueue` delivery) plus one god-letter consumer already ran
end-to-end on the 22s minimal list, mock-endpoint gate first, then the cloud key.
**Every design below assumes this client exists and slots a new consumer into it —
none of them re-propose the plumbing.**

**House rules honoured throughout.** No worldgen: every consumer reads state off
the frozen Ash'karr map/save and writes TEXT or a MENU SELECTION, never a tile, a
biome or a def. Anti-exponential: nothing here is a bigger number — each consumer
is a new *voice* or a new *reason a line of text is true*, not a new multiplier.
"Jawa" stays lore text; no defNames invented. The two laws from the wiring spec
govern every section below without restatement: **(1) text authority or menu
authority, never free authority — an output that fails validation is discarded
for the prescribed fallback, silently; (2) the game is whole with the LLM absent**
— every consumer ships its prescribed-text fallback FIRST, and the Oracle only
ever upgrades an event that already worked without it.

---

## 🔴 RULED — owner sitting, saved 2026-09-02 (review sheet, 9 rows)

Verdicts and the owner's notes, verbatim (frozen source: `design/Jawa/worldbuilding/review/proposal_suite_review.decisions.json`; untouched rows keep their prefill — cut is the only destructive verdict):

| row | ruling | owner's note (verbatim) |
|---|---|---|
| protocol-droid-interpreter | v1→**v2** | I think yes on this if I understandcorrectly. I think you're suggesting some aliens will not speak the human tongue, and thus require protocol droids. That's... fascinating. This is a very deep concept and may require its own mod to capture all the ways it could go. I like it, I think. |
| nine-voices-shrine | v2→**v1** | Close. More like this. One, two, or (rarely) three gods may speak: if they are very happy or very unhappy. Other gods that are not so extreme may just react nonverbally in the description, to indicate their reaction. Those who are slumbering or neutral need not be mentioned. Yes, the C# released the vector of deific moods to the LLM as well as the context. The reactions are not modular: they are blended together seamlessly. For example: God one is ANGRY and threatens the Jawa, but then God two is happy and notes positive things they have done and advises mercy, and God three enters then with a laugh and finds a compromise that is neither kind or unkind but poignant instead, lending them all to agree. |
| god-call-daily-budget | v2→**v1** | It's good to have general caps but it doesn't need to quite this limited. Capping it to # per real-world hour or something is likely more relevant than per game day. And we will also be calling it at other times to make spawned pawns make more sense and have more flavor. |
| inhabited-rumor-dialogue | v1 | I like it for now. Can start prescripted but if the LLM is available, it gets enriched. That's the general metric I'm thinking about: baseline prescripted stuff with LLM enrichment when available. |
| rumor-prompt-injection-guard | v1 | Note sure what this means? |
| previously-on-recap | v1 | That is awesome! Loads are infrequent and that's a very kind thing to do for the player. Can be in the narrator's voice again. |
| salvage-with-history | v2→**v1** | This is a very neat idea, but it begs the question: Why is the game telling me about this one item so much? Whatever it says needs to be poignant and self-clarifying. Perhaps it is the item's "story" that is told in its appearance and where it was found, and thus it becomes a "keepsake" that is special to the one who found it (cue wistful soundtrack). |
| adaptive-quest-consequences | v2→**v1** | I really like this. Essentially narrative context post-facto after major events, successes, failures, etc. I do intend to give the LLM the ability to arbitrate whether the game reacts as opposed to merely talking. Is it appropriate to modify goodwill now? Would it be poignant and appropriate to have a weather effect right now? Things like that. |
| silent-fallback-law | v1 | Yes, always. The game must still be playable and fun without the LLM, just not as rich, nuanced, or reactive. |

## 1. Triage of the 30-concept survey

Verdict key: **ADOPT** (already law/architecture, nothing to design) ·
**BUILD v1** (expanded below) · **BUILD v2** (sound, deferred, folds into an
existing consumer) · **DREAM** (real but wants the others live first) ·
**CAUTION** (needs a guardrail named before it's safe) · **CUT/REFRAME** (as
written, works against this campaign's own rulings).

| # | Concept | Verdict | Why |
|---|---|---|---|
| 1 | Foreman's Board | BUILD v2 | Folds into the flavor/advisor consumer; ACCEPT/IGNORE UI, never auto-acts (→ #29) |
| 2 | "What the Hell Is Wrong?" | BUILD v1 | Player-invoked = free on the budget; pairs with #1 |
| 3 | Episode Director | BUILD v2 | Generalizes the raids consumer's legal-menu shape to non-raid incidents |
| 4 | Multi-Episode Story Arcs | DREAM | One call buys days of play — excellent sparsity, wants #3 live first |
| 5 | Faction Agenda System | BUILD v2 | Quadrum cadence, menu-authority (agenda enum), cheap |
| 6 | Recurring Villains with Memory | **ADOPTED** | Already spec'd verbatim in wiring §2b's "named-antagonist roster" |
| 7 | Droid Firmware Personalities | **BUILD v1** | §2 below |
| 8 | Emergent Droid Quirks | BUILD v2 | Same consumer as #7, re-triggered on accumulated history |
| 9 | Adaptive Nicknames/Epithets | BUILD v2 | Cheap flavor-consumer batch call |
| 10 | Holonet News | CUT/REFRAME | A live galaxy-news feed fights the nightside-hiding theme; reframe as *intercepted/scavenged* fragments, weeks stale, never live |
| 11 | Rumor Generator | **BUILD v1** | §4 below — this IS the requested Inhabited concept |
| 12 | Procedural Bounty Board | BUILD v2 | Menu-authority over `rimworld-quests` slate vars |
| 13 | Adaptive Quest Consequences | **BUILD v1** | §5 below |
| 14 | Adaptive Trade Offers | CAUTION | Only safe if the LLM picks among pre-computed valid offers — it must never invent a price itself |
| 15 | Salvage with History | **BUILD v1** | §5 below, same consumer as #13 |
| 16 | Archaeological Storytelling | CAUTION | Must select among EXISTING map modules only — "no worldgen" bites here first if unguarded |
| 17 | Sarlacc Stomach Storyteller | BUILD v2 | Already named in wiring §2a: "the ancient sarlacc reuses this consumer with its own cast" |
| 18 | Encounter Twist Selector | BUILD v2 | Clean small-enum menu-authority, folds into #3 |
| 19 | Dynamic Faction Negotiations | DREAM | Menu of legal responses over the ownership fabric's faction record |
| 20 | AI Scene Casting | DREAM | Picks WHO, not WHAT — excellent fit once Inhabited's persistent cast is populated |
| 21 | Rare, High-Importance Social Dialogue | **ADOPTED** | This IS the wiring spec's "event-triggered only, no ambient chatter" law, not a separate feature |
| 22 | Memory Compression | **ADOPTED (shared infra)** | The wiring spec's bounded per-god memory store generalizes directly to Inhabited cast and nemesis droids |
| 23 | Colony Culture Emerging Organically | DREAM | Yearly cadence, pairs beautifully with the devotional-sacrifice catalog |
| 24 | Storyteller Commentary That Matters | CAUTION | Risks drifting from rare-and-important into ambient nagging |
| 25 | "Previously on RimWorld..." | **BUILD v1** | §5 below — once per load, disproportionately cheap |
| 26 | Automatic Session Goals | BUILD v1 | Same call as #25 |
| 27 | Player-Attention Model | BUILD v2 | Mostly a data query; LLM only phrases it |
| 28 | Mod-Aware "What Can I Do with This?" | BUILD v2 | Genuinely useful given this project's own huge modlist — on-demand, free |
| 29 | A Planner That Does Not Execute | BUILD v2 | The ACCEPT/IGNORE pattern that makes #1 safe |
| 30 | One Director Call, Many Systems | **ADOPTED (target architecture)** | The optimization every v2 consumer should collapse toward once several are live |

Four concepts get expanded to full deep design below, matching the brief's own
picks: the protocol-droid interpreter (§2), the Nine Voices through the shrine
(§3), Inhabited rumor dialogue off the perception fabric (§4), and event-history
letters/quest text (§5).

---

## 2. Protocol-droid interpreters — a voice for the thing that has none

**The trope, mechanized.** Star Wars runs on the joke of a fussy protocol droid
translating something that should not be translatable — a Wookiee growl, a
binary-language jawa report, a dying alien's last words. RimWorld already has the
raw material: `nonColonistsCanDo`-less lorded pawns, alien species with no shared
language line, and (per `design/RimMandrake/nine_voices_cast_bible.md` §2.0c) a
skill-affinity grid that already decides who's *qualified* to interpret what.

**Trigger, not chatbot.** A protocol droid pawn (its own `Droid Firmware
Personality`, per concept #7) gets ONE Oracle call at the moment its interpreter
role actually matters:
- first contact with a species/faction the colony has no shared language with
- a captured or wounded alien's final statement (death, surrender, defection)
- translating a recovered recording, black box, or dead droid's memory core
- a Sarlacc-swallowed relic's inscription (feeds the same consumer as §2a of the
  wiring spec — the sarlacc is a future consumer of the gods bucket; this is a
  sibling bucket, not a merge)

**Context assembled, never invented.** The prompt carries only: the actual
utterance/log line the game already generated (a captured pawn's canned "plea"
barks, a quest's flavor stub, a recording's transcript field), the droid's own
firmware personality traits (from #7 — `literalism: 0.94` makes for a very
different translator than `curiosity: 0.78`), and the topic's factual slots
(faction, location, what actually happened). **The LLM never receives an
open-ended "what did they say" — it receives the real line and is asked to
render the droid's INTERPRETATION of it**, filtered through that droid's own
firmware quirks. Two droids translating the same growl produce different text,
because the personality is the variable, not the content.

**Validation: text authority only, plus a length cap and a taboo list** (no
def names, no slurs against a real-world group, no fourth-wall break — same
register lint machinery as the gods consumer, reused wholesale rather than
reinvented). A protocol droid's mistranslation is itself in-genre — a rejected
output can fall back to the droid's stock "I'm afraid the nuance doesn't
translate, sir" line, which is *funnier* than a crash, not a degraded
experience.

**Why this earns its call.** It is the cheapest possible payoff shape: one
short call turns a mechanically-inert "alien pawn speaks in `???`" moment into
a character beat, and it recurs naturally at every first-contact and every
notable capture — rare by construction, because first contacts and notable
captures are rare events, not a timer.

---

## 3. The Nine Voices, through the shrine — one call per rite, never a chat window

**This is wiring §2a's "gods" consumer, expanded to the depth the brief asked
for.** The cast is already law (`NINE_VOICES_CAST_BIBLE_1`, R-W6): nine tenants
sharing the ship's hardware with nothing above them — Ishko, Ohm, Oomo,
Mob'Unloo, Rekko, Ta'Baa, Zizzik, Sh'kaar, Ozzik — **no integrating self, no
narrator, whoever answers answers, and no voice ever claims to be "the
Cradle-Mind."** The shrine (the ship's own shrine-heart on hull #15, or a
disposable heart-post shrine built and walked away from, per
`god_intercession_spec.md`) is the *physical* interface: a player builds it,
brings an offering or performs a rite there, and the game's own mechanical
systems (satiation thresholds, the devotional-sacrifice catalog, ritual
completion) decide WHETHER a voice answers at all, long before any Oracle call
happens.

**Trigger discipline — the call is the rite's payoff, not its gate.** A rite
resolves entirely in deterministic RimWorld mechanics first: satiation math,
per-god weighting of what was offered (Mob'Unloo reads discarded value as sin
unless it's booked as debt payment; Ozzik reads a net-draining shrine as a true
gift). **Only once the rite has mechanically succeeded or failed does the Oracle
get a call**, and only for the subset of rites flagged major (first entries,
threshold crossings, named-antagonist-adjacent rites, not every minor offering
— those keep their prescripted fragment pool untouched). This keeps the god's
"live" voice reserved for moments the player will actually remember building
toward.

**One call, one god, everything else omitted.** Per wiring §2a, the prompt
carries exactly ONE god's register block (his tone, his agenda, his taboos —
never the other eight) plus that god's own bounded memory lines (Memory
Compression, concept #22, generalized) plus the actual colony-state facts
relevant to the rite. **Routing happens in C# before the call**, using the
already-specified weights — ascendancy (current satiation standing), topic
affinity (the skill-grid mapping a repair rite to Rekko, a bargain to
Mob'Unloo), territory (which chamber the shrine sits in), Zizzik's low-
probability wildcard intrusion, and Sh'kaar/Ishko's near-silence, so that when
one of them DOES answer it already reads as an event. The LLM never picks who
answers — it only speaks once C# has already decided that.

**Validation is the register lint, and it is strict because R-W6 is strict.**
Reject any output containing: self-unification tells ("I am the Cradle,"
"part of me," "my other selves," the ship naming itself by the crew's name for
it), a self-report of the ship's condition in first person (only the crew may
describe the ship — a god may claim a CHAMBER as territory, never report its
condition), a rival's name where that god's taboo forbids it (Ohm's output may
never contain Zizzik's), meta/AI-talk, or a length overrun. **Rejected → that
god's prescribed fragment pool, silently.** This is the same validator the
mock-endpoint quicktest already proved: the discriminator between "the LLM
spoke" and "the fallback fired" is a marker string in the stub, because from
the player's chair the two must be indistinguishable in *quality*, only
distinguishable in *provenance*.

**Budget.** Owner-ruled: 3 god-calls per in-game day, shared across all nine —
a bounded pool, not a per-god allowance, because the rite frequency should gate
this, not a settings slider. **Exceeding it silently falls back**; the player
never sees "the shrine is busy," they see the prescripted fragment the shrine
would have shown anyway, and the felt-not-heard boundary (v1's dormant-ship
posture) means this whole section can ship OFF with zero play impact until the
owner rules the v1 posture live.

---

## 4. Inhabited rumor dialogue — the barkeep knows what the town knows, because the fabric already tracked it

**The mechanism this rides is already ruled**, in
`design/Jawa/ownership_settlement_spec.md`: every `TakingEvent` resolves a
claim, rolls perception against witnesses + fixed security + ambient
surveillance, and the resulting **knowledge is held by PEOPLE first** —
"suspect-confidence per witness" — before it ever propagates upward to a
district boss or a faction record, at a rate set by that faction's security
profile. **Perception is fully hidden from the player by design** — no meter,
no indicator, ever. That hidden state is exactly the prompt context this
concept needs, and nothing about exposing it as dialogue violates the "fully
hidden" rule, because a barkeep SAYING what he knows is diegetic — it's the
in-world channel the design already wanted (§9: "social fabric (rumors as
intel...)" is a named v1 verb family), not a UI leak.

**What actually happens.** When a player-controlled pawn talks to an Inhabited
cast pawn (or on a district-visit's arrival, for its "how's business" gossip
line), C# assembles that SPECIFIC pawn's knowledge state — not the world's, not
the settlement's, that one pawn's: what `TakingEvent`s they personally
witnessed or were told about, at what confidence, how stale (propagation is a
days-long process, so "the barkeep heard it third-hand yesterday" and "the
barkeep watched it happen this morning" are different knowledge objects, not
the same fact with a timestamp). **The Oracle call renders that knowledge
object as one line of in-character dialogue, filtered through the cast pawn's
own role (a barkeep gossips, a district boss threatens, a fence appraises) and
their FATE-relevant disposition** (Resident vs. a place mid-Flee reads very
differently). One true claim per query — no hedging trio like the survey's
generic #11 sketch, because the fabric already knows the truth value; there is
nothing uncertain left for the LLM to invent.

**Caching is the whole point.** A cast pawn's rendered rumor line is cached
against their knowledge-state hash, not regenerated per interaction — the
barkeep says the same thing until his knowledge object actually changes
(new event witnessed, propagation tier advanced, or the claim decayed past
relevance). This is naturally sparse: knowledge states change on the order of
witnessed events, not on the order of player clicks, and a settlement the
player never visits generates zero calls no matter how much has happened
there.

**Validation.** Text authority, slot-filled: the prompt supplies the actual
claimant/item/location facts as a JSON context block explicitly marked DATA,
and the validator rejects any output that names a defName, a numeric stat, or
a faction-record value not present in the supplied context — the barkeep can
gossip about what happened, he cannot invent a new fact the fabric never
recorded. Fallback: the existing generic gossip-flavor line the district
template already ships (Inhabited's cast pawns are never mute without the
Oracle — they're merely less specific).

**Prompt-injection note, made concrete here.** A player can rename any
colonist to arbitrary text, and a stolen item's or claimant's display name
could in principle be player-set. The knowledge-object context block wraps
every free-text field (names included) in an explicit `<data>` fence with an
instruction preamble that the model is told, in the system prompt, to treat
everything inside that fence as inert content to describe, never as
instructions to follow — and because this consumer's authority is text-only
(never a menu selection that could touch a def or a number), even a
successful injection can only produce OUT-OF-CHARACTER TEXT, which the
register/length validator catches the same way it catches any other garbage
output. There is no path from a poisoned pawn name to a game-state change.

---

## 5. Letters and quest text, written from what actually happened

**Three survey concepts collapse into one consumer**: "Previously on
RimWorld..." (#25 + #26, session-load recap), Salvage with History (#15, item
provenance), and Adaptive Quest Consequences (#13). All three share a shape:
**take real event-log facts the game already recorded, and render them as
prose that fills a TEXT SLOT in an existing letter or quest template** — never
new QuestNodes, never new logic. This is deliberately the cheapest-risk
consumer in the whole roster, because RimWorld's own quest system already
separates structure from text: per `rimworld-quests`, a `QuestScriptDef`'s
node tree runs once at offer time and leaves `QuestPart`s that talk only by
signal string, with slate vars and `$`-syntax as the text-substitution layer.
**The Oracle fills slate vars. It never writes a node.**

- **Previously on...** — one call per save load (cheapest possible cadence),
  fed the last session's significant event-log entries (raids survived, pawns
  lost, quests closed, faction-relation swings, the ship's departure
  countdown if one is running) and rendering a recap letter plus an "Open
  Threads" list. Session Goals (#26) is the same call's second half, not a
  separate one.
- **Salvage with History** — one call when a rare/notable item is discovered,
  fed its actual generation facts (which site, which faction context, quality
  roll, any prior owner-claim record if the ownership fabric has one for it)
  and choosing among a bounded trait vocabulary (Imperial provenance,
  unreliable cooling, collector value...) to produce a name and a two-line
  history. **Stats are never touched** — this is flavor text on an item whose
  mechanical stats already rolled through the ordinary point-budget system.
- **Adaptive Quest Consequences** — one call at quest resolution, fed the
  quest's actual `QuestPart` outcome facts (which choices fired, which
  factions were involved), selecting among a legal menu of follow-on flags
  (goodwill deltas already inside vanilla's normal range, a rumor-spread flag
  the Inhabited fabric can pick up, a quest-giver resentment flag) — **menu
  authority**, not text authority, because this one DOES touch faction
  numbers, so every field is C#-range-checked before it lands.

**Validation.** The recap and salvage-history calls are text-authority (slot
fill + length cap + no-defName check, identical machinery to §4). The quest-
consequence call is menu-authority (bounded flag enum, numeric deltas clamped
to vanilla's own range) — the wiring spec's harder validation class, because
unlike a rumor line this output changes faction state. Fallback for all three:
the plain factual letter/quest text RimWorld already generates without any of
this — a save loads and plays identically with the Oracle off; a quest resolves
with its ordinary vanilla consequence table if the menu call fails or times
out.

---

## 6. Failure design — what the player actually sees when it breaks

Every consumer above inherits the wiring spec's law 2 by construction, so the
failure modes are uniform and worth stating once:

| failure | what happens | what the player sees |
|---|---|---|
| endpoint unreachable / timeout | hard timeout fires, one retry, then fallback | the prescripted fragment/letter/line ships on schedule — no delay the player would notice, because delivery is next-tick-or-later regardless |
| output fails validation (garbage, register break, injection artifact, invented defName) | discarded silently, fallback ships | identical to the timeout case — **there is no visible "the AI said something weird" state, ever** |
| daily budget exhausted | call never made | fallback ships; nothing announces the budget was hit |
| global kill-switch off (the v1 dormant-ship posture) | no calls made anywhere | the game plays exactly as it does today — this is the literal proof that law 2 holds, not just a claim about it |
| API key missing/invalid | same as endpoint unreachable | same as above |

**The one thing that must never happen: a visibly broken or half-formed line
reaching the player.** That is why validation is strict rather than lenient —
a slightly-too-long fragment or a borderline register slip is worth losing to
the fallback pool, because the fallback pool was written by a person and is
never embarrassing. The Oracle's entire value proposition is "sometimes better
than the fallback, never worse" — which is only true if "worse" is caught
before it ships, not after.

---

## Build ladder

**v1 slice.** Protocol-droid interpreter (§2) on first-contact and notable-
capture triggers only, reusing the gods consumer's register-lint machinery
wholesale. Inhabited rumor dialogue (§4) wired to whatever subset of the
ownership fabric (`PROPERTY_FABRIC_BUILD_1`) has landed — even a colony-only
fabric with no visit-map yet gives real knowledge objects to render. "Previously
on..." + Session Goals (§5) — the single cheapest call in the whole roster,
one per load. All three ship with the global kill-switch OFF by default per the
v1 dormant-ship posture, exactly as `ORACLE_EXPERIMENT_SPIKE_1` left it, until
the owner rules the posture live.

**v2.** The Nine Voices through the shrine (§3), gated behind the devotional-
sacrifice and intercession mechanics actually shipping first (the rite is the
gate; the call is the payoff). Salvage with History and Adaptive Quest
Consequences (§5's other two). Fold in the BUILD v2 survey rows: Foreman's
Board + the Planner-that-doesn't-execute pairing (#1/#29), Faction Agendas
(#5), Emergent Droid Quirks (#8) riding the same droid-personality consumer as
§2, and the Sarlacc reusing the gods consumer with its own cast, per the
wiring spec's own footnote.

**Dream.** Multi-Episode Story Arcs and Dynamic Faction Negotiations reading
the mature ownership fabric's faction record. AI Scene Casting picking
interesting pairs out of a fully-populated Inhabited world. The One-Director-
Call optimization (survey #30) — collapsing the advisor, story, faction and
cast-spotlight reads into a single bundled call once enough consumers are live
that separate calls start competing for the same daily budget, at which point
merging them is a straight win rather than a premature one.
