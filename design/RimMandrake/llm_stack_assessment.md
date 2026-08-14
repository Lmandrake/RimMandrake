# llm_stack_assessment.md — how far the live LLM stack gets us

_Written 2026-08-09 against the **28 LLM mods now installed and ACTIVE** on the machine (27 RimTalk-family +
RimAI Framework/Core). Read from `About.xml` on disk, not from Workshop marketing. The question this file
answers: **how much of the enrichment-agent design can we get by configuring what is already installed,
before writing a single line of code?**_

**Headline: much more than expected. Two of the corpus's hardest blockers are plausibly solved off-the-shelf,
and one of my earlier recommendations was wrong.**

---

## 0. Correction to `rimtalk_analysis.md`

**RimTalk – Quests (3642675329) does NOT generate quests.** I called it an unbounded reward faucet and
recommended against it. Its own description, read from disk: *"It doesn't modify the original quest info;
instead, it appends rich, emotional narratives to the existing descriptions."* It supplies **motive** for
mechanical requests — *why* does this traveller need 2 medicine, what has he been through. It adds no
rewards, no quest generation, no defs. **Pillar-safe. Recommendation reversed: adopt.**

---

## 1. The stack, sorted by what it does for *us*

### 1a. The three that change the design's risk profile

| Mod | WS | Why it matters |
|---|---|---|
| **RImtalk Expand: News, Expert and Colony Chronicle** | 3714540653 | *"Automatically captures and records all important events (raids, disease, weddings, deaths…), archives them graded by importance, provides a historical timeline UI, plus situation-analysis / combat-assessment / personnel-change expert services."* **This is the semantic event feed.** `design/Jawa/worldbuilding/enrichment_agents.md` §7.3 names the missing event stream as "the most likely place the design meets an unplanned C# requirement" — RimLog is dead on 1.6, and the bridge only exposes state reads. A mod that captures graded, structured events and writes them to a readable store is exactly agent G's `§8b` input channel. **Priority-one thing to test in Phase A.** |
| **RimTalk Ideology Patch** | 3724752618 | *"Allows RimTalk to read full Ideology data — including belief descriptions, cult structures, member titles, worship places, and **deity names with their divine epithets**."* The nine-god pantheon in `jawa_xenotype_and_religion.md` §2.0b becomes visible to the voice layer **for free**. Agents A (ritual dramaturge), B (calendar-keeper) and H (atonement broker) all need exactly this and nothing more on the read side. |
| **RimTalk StyleExpand** | 3694936738 | You drop writing-style samples as `.txt` into a `Styles/` folder; the mod does semantic chunking + **vector retrieval via an embedding API (Ollama recommended)** + LLM style analysis, then injects the style into generation. **This is a credible Jawaese solution** — feed it the `jawa_dialogue_source_audit.md` §3 Grade-A Ben Burtt corpus as the style corpus. It reframes the JawaVoice-vs-RimTalk conflict from "pick one" to "can retrieval hold the canon tightly enough?" — an empirical question we can answer in Phase A. |

### 1b. Direct agent-cluster coverage

| Design agent (`design/Jawa/worldbuilding/enrichment_agents.md` §5) | Covered by | Gap |
|---|---|---|
| **D — colony health digest → voice** (flagged SAFEST, build-first) | RimTalk base reads pawn state; **Context Upgrade** (3641774579) already compresses health into "how many bandaged, how many untreated, time-to-death from blood loss, disease detail, wounds merged by body part" | Essentially **done off-the-shelf**. The custom hediff-read bridge tool predicted as a C# requirement (`design/Jawa/worldbuilding/enrichment_agents.md` §7.2) may not be needed at all. |
| **G — divine satiation engine** | **News/Chronicle** for the event feed · **Ideology Patch** for pantheon awareness · **Mood Reactions** (3755539006) as the payoff channel | The **vector + Mood walk + scoring stays ours**, external, as designed. What's solved is the input and output plumbing. |
| **A — ritual-outcome dramaturge** | **Ideology Patch** (read outcome context) + **CQF-RimTalk addon** (3684497117) + **AI Storyteller** (3715752189) | Reading the *outcome tier* specifically still unverified. |
| **B — observance scheduler** | Ideology Patch reads precepts/rituals/worship places | The Phase-B authoring half is still XML we write. |
| **F — relic & provenance historian** | **MemoryDigest** (3726488698) + Chronicle | Item-level provenance still ours. |
| **H — confession / atonement broker** | Ideology Patch + **Mood Reactions** (real mood offsets from analysed conversation) | Sin *detection* rules stay ours. |
| **C — ghost ledger** | — | **Afterlife: Ghosts of the Rim is not installed.** Unchanged. |
| **Ship voice (Cradle-Mind)** | **RimAI Core** — talk to a buildable Server/Terminal, environment-aware (weather, power, stocks, mood, threats), distinct personas, server-to-server banter | Adopted as designed. See risk table. |

### 1c. Quest / arc integration — better than the corpus assumed

**Custom Quest Framework – RimTalk addon** (3684497117, by CQF's own author HaiLuan): colonists generate
talk on opening lootboxes, interacting with things, triggering traps; they **receive the content of CQF's
native dialogue system**; on CQF maps they know the map's identity.

This matters because the corpus's unreconciled contradiction (§CQF, `build_plan.md` §6 item 1) was "we said we
didn't need heavy authored quests, then built the whole 3-act arc, the three win paths and LifeDawn's voice
on CQF." This addon means **authored CQF content and the generative voice layer are already wired together**
by the framework author. The arc can be authored deterministically *and* narrated dynamically. That is the
best of both, and it was not on the table when that contradiction was written.

### 1d. The rest, briefly

| Mod | WS | Role |
|---|---|---|
| RimTalk (base) | 3551203752 | Reads state → prompt → bubble. OpenAI/DeepSeek/OpenRouter/Gemini/**Ollama/LM Studio**. |
| Event+ | 3612632140 | Raid/refugee/mech-cluster/solar-flare context from letters. ~0 TPS, save-safe. |
| Context Upgrade | 3641774579 | Prompt hygiene — stops "walking to work" being read as "working", real research names, merged wounds, skill compression. Pure logic, no save data. |
| Expand Memory | 3608181242 | Four-layer memory (ABM→SCM→ELS→CLPA), decay + importance + relevance injection. |
| MemoryDigest | 3726488698 | Summarises past dialogue into an injected memory chain; token-saving. **Overlaps Expand Memory — pick one.** |
| Persona Director | 3619548407 | Reads genes (endo/xeno), skills, relationships; generates 3 persona options; "Director Notes". The Jawa crew attach here. |
| Expand Dialogue | 3662962455 | **Main-Character mode**: pauses the game and offers *you* 3 candidate lines for a chosen pawn. A real RPG surface — obvious fit for the Jawa chief. |
| Expand Thoughts / Relation / Literature / Toddlers | 3661175034 / 3661493651 / 3633249209 / 3659064387 | Context breadth. |
| Quests | 3642675329 | Narrative colour appended to existing quests. Pillar-safe (see §0). |
| AI Storyteller | 3715752189 | LLM-driven storyteller expansion. See risk table. |
| Mood Reactions | 3755539006 | Analyses conversations, emits **AI-generated mood buffs/debuffs with custom label, description, offset, duration**; NPC-to-NPC too. |
| Expand Actions / Actions Core | 3628755033 / 3661055729 | **Dialogue drives behaviour** — 50+ actions, item matching, action queue. Per-action toggles, job whitelist, mental-state whitelist. |
| DisplayOptimization · PromptCleaner · Message Filter · Dialogue Patch · DynamicColors · Custom Room Names addon | — | Rendering, prompt hygiene, UI, filtering. Low risk. |
| RimAI Framework / Core | 3529263357 / 3560404184 | The ship-voice lane. |

---

## 2. Pillar risk register — the parts that can *act*

The stack's read side is nearly risk-free. Everything below writes to game state, and the anti-exponential
pillar applies to all of it.

| Mod | Risk | Ruling |
|---|---|---|
| **Expand Actions** (3628755033) | 🔴 **Recruit-via-conversation.** Its feature list includes *recruiting NPCs into the colony through dialogue*, plus enemy *surrender*, romance start/end, inspiration granting, and item gifting. Recruitment-by-talking is a **direct breach of the anti-exponential pillar** — crew growth is supposed to be bounded by demographic churn and externally-sourced droid brains. Enemy surrender-on-request trivialises the §19 danger design. | **Disable `recruit` and `surrender` at minimum.** Both have per-action toggles and success-rate sliders. Social dining, gifting, inspiration are defensible flavour. |
| **Expand Actions Core** (3661055729) | 🟠 Moves the LLM from narrator to actor across 50+ actions. | Governable — per-action switches, job whitelist, mental-state whitelist. **Start fully disabled**, enable individually, and never enable anything that produces or moves resources. |
| **Mood Reactions** (3755539006) | 🟠 Writes **real mood offsets** the LLM invents. That is mechanical power derived from conversation. | Genuinely useful as agent H's payoff channel — mood/social reward is exactly the §19.5-legal register. But cap the offsets. Audit magnitudes before trusting it. |
| **AI Storyteller** (3715752189) | 🟠 An LLM directing incidents competes with the **Imperial Heat gauge**, which is the sanctioned pacing mechanism and is supposed to live on our external blackboard. Two directors fight. | **Leave off for now.** Revisit only if Heat proves too laborious. |
| **RimAI Core actuator tools** | 🟡 Known watch-item: "intel scans, logistics tallies, security tips, production nudges (with cooldowns/requirements)". | Standing ruling holds: **adopt voice-only, actuators disabled.** The Cradle-Mind persona is already written to refuse exponential requests as a second line of defence. |
| **Whole-stack cost/latency** | 🟡 28 mods all enriching prompts = large context per call. | MemoryDigest + PromptCleaner + Message Filter + Context Upgrade all exist to fight this. Use a local Ollama model for bulk chatter and reserve a strong model for summarisation (StyleExpand and Lucid-style splits support this). |

---

## 3. How far we can go with zero code

Mapping the design's asks against the installed stack:

**Solved or near-solved by configuration:**
- Agent D (health digest → voice) — Context Upgrade already does the hard part.
- Agent G's *input* (semantic event feed) — News/Chronicle. **This is the big one; it was the corpus's
  headline C# risk.**
- Agent G's *output* (mood/narrative payoff) — Mood Reactions.
- Pantheon awareness for A/B/H — Ideology Patch.
- Ship voice — RimAI Core.
- Jawaese — StyleExpand fed the Grade-A corpus (empirical, needs testing).
- Quest narration over the authored arc — CQF-RimTalk addon + Quests.
- Per-pawn persona authoring — Persona Director.

**Still ours to build (unchanged):**
- The satiation vector, Mood walk, ritual scoring, Council theatre — all external `(f)`, as designed.
- Imperial Heat + the orbital-detection timer — external blackboard.
- Sin-detection rules, relic provenance rules, the liturgical calendar defs.
- The ship stamper and per-map enrichment via RimBridge.

**Still genuinely blocked:**
- Agent C (ghost ledger) — Afterlife: Ghosts of the Rim not installed.
- Ritual *outcome-tier* reads — unverified whether anything exposes them.
- Anything needing typed text through the bridge — still wants the companion `BridgeTools` DLL.

---

## 4. Proposed Phase-A configuration ladder

Run these in order on the **stock-ish vanilla spike**, not the campaign save. Each step answers one question.

1. **Baseline.** RimTalk + Context Upgrade + DisplayOptimization + PromptCleaner, pointed at local Ollama.
   Everything that can act is **off**. Question: does the loop work, and what does it cost per call?
2. **Context breadth.** Add Event+, Expand Thoughts/Relation, Ideology Patch. Question: does the model
   correctly reference a raid, a relationship, and a *deity by epithet*?
3. **Memory.** Add **either** MemoryDigest **or** Expand Memory — not both. Question: which holds continuity
   at lower token cost?
4. **The event feed test (highest value).** Add News/Expert/Chronicle. Question: **where does it write its
   event archive, in what format, and can an external process read it?** If yes, agent G's input problem is
   solved and the biggest C# risk in the corpus evaporates.
5. **Voice identity.** Add StyleExpand with the Ben Burtt Grade-A corpus. Question: does retrieval hold the
   `Jawaese. (gloss)` shape, or does it invent grammar? This decides JawaVoice's fate.
6. **Ship voice.** RimAI Core, one Server/Terminal built, actuators disabled. Question: does the Cradle-Mind
   persona hold, and are the actuator tools cleanly ignorable?
7. **Controlled action.** Expand Actions Core with everything off, enabling one harmless action. Question:
   how does GM-driven behaviour *feel* — alive, or puppeteered?
8. **Never in this ladder:** Expand Actions' `recruit`/`surrender`; AI Storyteller.

---

## 5. What this changes about the build plan

`build_plan.md` M0–M5 stands, but Phase A gains a second track. The bridge spike (primitive library, stamper,
reload-survival) was about **writing to the game**. This stack is about **reading and narrating** it, and it
turns out to cover far more of the agent design than the corpus assumed — most of the A–H cluster's plumbing
is already on disk.

The sharpest single experiment in the whole project right now is **step 4**: if the Chronicle mod's event
archive is externally readable, then agent G — the spine of the religious cluster — becomes a Python script
reading a file, instead of a C# exporter we have to write and maintain.
