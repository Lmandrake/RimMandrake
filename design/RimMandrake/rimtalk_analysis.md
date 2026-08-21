<!-- status: superseded-by: design/RimMandrake/llm_stack_assessment.md ; 2026-08-09 ; the RimTalk - Quests verdict is reversed to adopt; kept only as the record of why RimDialogue is delisted -->
> 🔴 **PARTLY REVERSED — do not act on the RimTalk – Quests verdict below.** `design/RimMandrake/llm_stack_assessment.md` §0 ("Correction to `rimtalk_analysis.md`", 2026-08-09, written against 28 mods read from disk) overturns it: RimTalk – Quests (3642675329) generates no quests and is pillar-safe — **recommendation reversed to adopt**.
> This file is kept as the only record of *why* RimDialogue is delisted and what vacated that slot. Read the assessment for the current verdict.

# rimtalk_analysis.md — RimTalk adoption analysis

_Researched live from the Steam Workshop, 2026-08-09. Written because **RimDialogue is delisted**, which
vacates the "LLM reframes what pawns say" slot the corpus had assigned to it. RimTalk is the surviving
occupant of that slot — and it is a substantially bigger thing than RimDialogue was._

---

## 1. What RimTalk is

**RimTalk** — WS **3551203752**, by **Juicy**, 1.5+1.6, ~1.9 MB, **121,890 subscribers**, last updated
**2026-08-08** (i.e. yesterday — actively maintained).

The loop is simple and matches what the corpus wanted:

1. Reads what a colonist is thinking and doing.
2. Builds a prompt from that state.
3. Sends it to an LLM.
4. Renders the reply as a **chat bubble** over the pawn.

**Providers:** OpenAI, DeepSeek, OpenRouter, Google AI, any OpenAPI-compatible endpoint — explicitly
including **local Ollama and LM Studio**. That matters: `ollama.md`'s Phase-A1 local backend plugs straight
in, and the Claude path is reachable through an OpenAI-compatible shim.

**Personality system:** per-pawn personas, fully editable — "grumpy elder, poetic dreamer, sarcastic doctor."
This is the hook the Jawa crew personas would attach to.

**Performance stance:** the author's claim is that all inference is remote so TPS is unaffected. With local
Ollama that claim inverts — you pay in GPU, not in TPS, but the game thread still isn't blocked.

---

## 2. The ecosystem — 30 sub-mods, and that is the real story

This is not one mod, it is a small platform. Ranked by subscribers (a decent proxy for "does it work"):

| Sub-mod | WS | Subs | Updated | What it does |
|---|---|---:|---|---|
| **RimTalk Event+** | 3612632140 | 64,377 | 2026-07-11 | Feeds **major map events** (raids, refugees, mech clusters, solar flares) into the prompt: which faction, how they arrived, what the letter said. Author claims ~0 TPS cost, no known incompatibilities, **safe to add/remove mid-save**. |
| **RimTalk - Expand Memory** | 3608181242 | 53,467 | 2026-07-27 | Four-layer memory architecture (ABM→SCM→ELS→CLPA), timeline UI, knowledge library with batch injection, time-decay + importance scoring. The heavyweight memory solution. |
| **RimTalk: Persona Director** | 3619548407 | 45,384 | 2026-04-07 | Authoring layer for personas. Already named in `design/Jawa/worldbuilding/enrichment_agents.md` §4 as the PRIMARY tool for per-map NPC hand-crafting. |
| **RimTalk.DisplayOptimization** | 3629456304 | 28,547 | 2026-05-22 | Bubble rendering/perf. |
| **RimTalk - Enhanced Prompt & Announcement** | 3628795263 | 16,677 | 2026-01-25 | ⛔ **Discontinued** — superseded, don't adopt. |
| **RimTalk - Expand Toddlers** | 3659064387 | 13,098 | 2026-08-01 | Child/toddler speech behaviour. |
| **RimTalk Context Upgrade** | 3641774579 | 7,808 | 2026-04-26 | Prompt-quality surgery: stops the LLM mistaking "walking to work" for "working," tells it *what* is being butchered, where a pawn is sleeping, who a breakdown is attacking, real research names. Compresses skills/health/events to save tokens. **Pure logic, no save data, add/remove freely.** |
| **RimTalk - Expand Actions** | 3628755033 | 6,936 | 2025-12-24 | Lets dialogue reference/trigger actions. |
| **RimTalk - Expand Literature** | 3633249209 | 5,955 | 2026-06-06 | Books/reading content. |
| **RimTalk - Quests** | 3642675329 | 5,142 | 2026-04-26 | LLM-driven quest generation. ⚠️ **Highest pillar risk — see §4.** |
| **RimTalk TTS Addon** | 3618965326 | 4,422 | 2026-08-06 | Text-to-speech voicing. |
| **RimTalk - Expand Thoughts** | 3661175034 | 3,425 | 2026-02-27 | Thought/mood surfacing. |
| **RimTalk - Expand Relation** | 3661493651 | 2,567 | 2026-02-12 | Relationship context. |
| **RimTalk-Message Filter** | 3697500330 | 2,583 | 2026-07-15 | Filters what reaches the model. |
| **RimTalk Lucid Chronicle** | 3749797638 | 1,379 | **2026-08-09** | Memory + **AI-written colony Chronicle**, Conversation Mode (talk while paused), "peek at inner thoughts", player-written Common Knowledge, per-day Diary. Rebuilt simpler than Expand Memory; can use a **separate cheaper model** for summarisation. |
| **RimTalk - Generate Knowledge** | 3733532193 | 1,645 | 2026-05-26 | Knowledge-base generation. |
| Others | — | <1,500 | — | PromptCleaner, JSON & Color Fix, Streaming End Fix, Expand Dialogue, Expand Actions Core, Expand Memory Beta, DynamicColors, translations. Mostly fixes and localisation. |

---

## 3. How it maps onto the existing design

**It does not replace RimAI Core.** These voice different surfaces, and the corpus already made that
distinction correctly — it just made it about the wrong mod. RimAI voices **one buildable in-world object**
(the Cradle-Mind on a Server/Terminal), which is uniquely on-theme for "the engine is god." RimTalk voices
**every pawn**. They are complementary; run both.

**It does collide with SpeakUp/JawaVoice.** Both write interaction bubbles. The corpus's standing rule —
run exactly one bubble owner — now reads: **SpeakUp+JawaVoice (deterministic, authored, canon-anchored)
vs RimTalk (generative, unbounded, alive)**. That is the real decision, and it is sharper than the old
JawaVoice-vs-RimDialogue framing because RimTalk is much more capable than RimDialogue was.

**It solves the Phase-D event-feed gap — partially.** `design/Jawa/worldbuilding/enrichment_agents.md` §7.3 flags "the most likely place the
design meets an unplanned C# requirement": the divine-satiation engine needs *semantic acts*, but the bridge
only exposes state reads and logs, and RimLog is dead on 1.6. **Event+ and Lucid Chronicle both build exactly
that semantic layer** — Event+ parses letters into structured event context; Lucid Chronicle writes a
persistent per-day, per-pawn memory record. Reading Chronicle output is a far cheaper route to an event feed
than forking RimLog or writing an exporter in C#. **This is the strongest argument for adoption.**

---

## 4. Pillar risks

| Risk | Severity | Note |
|---|---|---|
| **RimTalk - Quests generates quests** | 🔴 **High** | An LLM inventing quests is an unbounded reward faucet — directly against the anti-exponential pillar and §19.5. It also competes with the authored CQF chain that carries the 3-act arc and the three win paths. **Recommend: do not adopt.** |
| **Expand Actions can trigger actions** | 🟠 Medium | If dialogue can cause game effects, the LLM becomes an actor, not a narrator. Adopt read-only components first; audit what "actions" actually means before enabling. |
| **Tone drift** | 🟠 Medium | The original decline of LLM voices was "unbounded tone." Persona Director + Context Upgrade materially reduce this, but Jawaese specifically needs the `Jawaese. (gloss)` shape held — small local models may not manage it. `jawa_dialogue_source_audit.md` §10 (never invent Jawa grammar) is a real constraint on a generative system. |
| **Cost / latency** | 🟡 Low-med | Every pawn talking is far more inference than one ship voice. Local Ollama makes it free but GPU-bound; a paid API makes it metered. Lucid Chronicle's split-model support (cheap model for summarisation) is the mitigation. |
| **Ecosystem churn** | 🟡 Low-med | 30 sub-mods, several already discontinued or superseded within months. Pin what you adopt; expect breakage on updates. |

---

## 5. Recommendation

**Adopt a narrow, read-only core. Refuse the parts that let the model act.**

**Tier 1 — adopt now (the case is strong):**
- **RimTalk** (3551203752) — the base.
- **RimTalk Event+** (3612632140) — biggest quality gain per token; explicitly save-safe; and it is half the
  answer to the satiation engine's event-feed problem.
- **RimTalk Context Upgrade** (3641774579) — pure prompt hygiene, no save data, removes the most immersion-
  breaking failure mode (the model misreading pawn state).
- **RimTalk.DisplayOptimization** (3629456304) — rendering/perf.

**Tier 2 — adopt after the Phase-A spike, once the local endpoint is proven:**
- **RimTalk: Persona Director** (3619548407) — the Jawa crew personas attach here; already the designated
  NPC-authoring tool in `design/Jawa/worldbuilding/enrichment_agents.md` §4.
- **RimTalk Lucid Chronicle** (3749797638) — evaluate specifically as the **event-feed substrate** for
  agent G, not just as flavour. Conversation Mode (talk while paused) is also a genuinely novel GM surface.
- Pick **one** memory system: Lucid Chronicle *or* Expand Memory (3608181242) — they overlap by design;
  Lucid Chronicle is explicitly the simpler rebuild.

**Tier 3 — do not adopt:**
- **RimTalk - Quests** (3642675329) — unbounded reward generation, collides with the authored arc.
- **Enhanced Prompt and Announcement** (3628795263) — discontinued.
- **Expand Actions / Actions Core** — until audited; they move the LLM from narrator to actor.

**The open decision this forces:** RimTalk and SpeakUp/JawaVoice cannot both own interaction bubbles.
The honest framing is that JawaVoice buys **canon control** (13 Grade-A Ben Burtt phrase pairs, no invented
grammar, perfectly on-tone comedy) and RimTalk buys **aliveness** (every pawn, context-aware, endlessly
varied, but it will invent Jawaese). A middle path worth testing in Phase A: **RimTalk scoped to non-Jawa
pawns and NPCs, JawaVoice retained for the crew** — if RimTalk's per-pawn scoping supports that, you get
both. Confirm whether it does before committing either way.
