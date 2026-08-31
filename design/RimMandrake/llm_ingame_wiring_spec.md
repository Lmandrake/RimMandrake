<!-- status: spec — LLM_INGAME_WIRING_1, BENCH 2026-08-31, green-lit by the owner, verbatim:
     "actually wiring an llm into the game as was always the intent so that small calls out could
     make the gods really come alive with more than prescribed dialog, create truly interesting
     raids, and provide real in game content specialization on an infrequent cadence (event
     triggered)." RimMandrake tier: the wiring is campaign-agnostic plumbing; the consumers
     (gods, raids, flavor) are campaign layers. Consumes: nine_voices_cast_bible.md (the cast
     law), sarlacc_spec.md §5 (a future consumer). -->
# The Oracle — in-game LLM wiring

## 0. The two laws over everything

1. **Text authority, or menu authority — never free authority.** An LLM
   output is either (a) DISPLAY TEXT (a letter, a fragment, a bubble), or
   (b) a SELECTION from a pre-validated menu with every field range-checked
   in C# before it touches the game. Free text never names a def, spawns a
   thing, or moves a number directly. An output that fails validation is
   discarded for the prescribed fallback — silently.
2. **The game is whole with the LLM absent.** Every consumer ships its
   prescribed-text fallback first; the Oracle only ever UPGRADES an event
   that already works. No endpoint, timeout, garbage output, or kill-switch
   flip can leave a hole. (This is also the v1 boundary: felt-not-heard
   stands until the owner says otherwise — the wiring can ship dormant.)

## 1. Architecture — `RimMandrake.Oracle` (companion module)

```
game event ──► OracleRequest (consumer id, context slots, fallback text)
     ──► PromptAssembler   one persona/template block + the context, NEVER the whole cast
     ──► OracleClient      async HTTP, OpenAI-compatible; default local Ollama;
                           fire-and-forget Task, hard timeout, one retry
     ──► Validator         per-consumer: register lint / menu range-check
     ──► MainThreadQueue   delivery next tick or later (letters don't care)
     └─► on ANY failure: the fallback text ships and nothing logs to the player
```

- **Threading:** the call runs entirely off the tick (Task + a concurrent
  queue drained by a GameComponent tick); latency of seconds is FINE because
  every consumer is letter-shaped, never a blocking dialog.
- **Cadence and budget:** event-triggered only — no polling, no ambient
  chatter. A hard budget (calls per in-game day, per consumer) in settings;
  exceeding it silently falls back. Infrequency is the owner's stated design,
  not a limitation.
- **Config surface:** base URL, model, API key (blank = local), per-consumer
  enable flags, the budget, and a global kill-switch. Defaults to local
  Ollama; any OpenAI-compatible endpoint works.
- **Memory:** a bounded `GameComponent` store saved in the save file —
  per-god rolling memory lines, named antagonists, delivered-fragment
  history. Hard caps (N lines each); the LLM sees only its own consumer's
  slice.

## 2. The three consumers

### 2a. The gods (the cast bible executed)
Trigger: satiation threshold crossings, ritual completions, the pressure
clocks, first-entries. The call carries exactly ONE god's §2 register block +
the §0 law + that god's memory lines; the output is a letter/fragment
attributed to that god. **Validation is the register lint**: reject outputs
containing self-unification tells ("I am the Cradle", "part of me", "my other
selves", naming itself), length caps, and the god's own taboos (Ohm's output
may never contain Zizzik's name). Rejected → that god's prescribed fragment
pool. The ancient sarlacc reuses this consumer with its own cast.

### 2b. Raids ("truly interesting")
The LLM receives a LEGAL MENU: faction, points budget, the arrival-mode list,
composition presets, named-antagonist roster (its own prior inventions,
persisted), and returns a parameterization + a threat letter. C# validates
every field (faction exists and is hostile, points within storyteller band,
arrival mode legal for the map) — any miss ships the standard raid with
standard text. What makes it interesting is composition CHOICE plus narrative
continuity: a named raid-captain who survived last time comes back, because
his name is in the store. The engine executes only vanilla-shaped raids; the
LLM only picks and narrates.

### 2c. Content specialization (infrequent, event-triggered)
Template-and-slots: trader manifest flavor, quest text specialization, rumor
letters about world events that actually happened (the context slots are
facts the game hands over, never asked for). Same validation shape: slots
filled, lengths capped, no def names accepted from the model.

## 3. Precedents on this disk — measured 2026-08-31

- **RimAI Framework + Core** (subscribed, workshop 3529263357 / 3560404184):
  DLL-only, **NO license** either mod — patterns readable, nothing absorbable.
  The retained symbols confirm exactly our §1 shape and add three refinements
  worth copying as ideas: a clean **two-layer split** (Core owns
  triggers/prompting/UI and contains zero network code; Framework owns all
  HTTP), a **`SchedulerGameComponent`** whose Tick dispatches queued async
  work items without awaiting them, and **in-flight request coalescing**
  (join a pending identical call instead of duplicating it) plus
  retry-with-exponential-backoff policies and separate chat/embedding
  endpoint configs. We build the same shape as our own thin module — the
  Oracle needs a fraction of RimAI's surface (no chat window, no streaming,
  no embeddings).
- **RimDialogue is NOT on this disk** — measured zero hits across all 1258
  About.xml (only its dependency, Jaxe's Bubbles, is present).
  `llm_voice_preauthoring.md` PART B's paste-ready prompt targets a mod we do
  not have; corrected there. **RimTalk** (`cj.rimtalk` + two addons) IS
  subscribed — a third precedent, uninventoried; check it only if the bubble
  lane (Part B) is ever revived.
- ⇒ **Adopt-vs-build verdict: BUILD.** Both candidate frameworks are
  unlicensed; the owner's single-owned-mod instinct holds; and our authority
  model (§0) is stricter than either mod's — a thin client we own is smaller
  than the compatibility surface of adopting theirs.

## 4. Verification plan

1. **Offline selftest, no model:** PromptAssembler + Validator run against
   canned good/bad outputs — the register lint must reject a seeded
   "I am the Cradle-Mind" and accept a clean Ohm fragment. Ships as
   `selftest_*.py`-style gate beside the C#.
2. **Mock endpoint quicktest:** a 5-line local HTTP stub returns
   deterministic responses; PROVE the full path on the 22s minimal list —
   EXPECT the letter arrives with the stub's marker text; LIES: a fallback
   firing looks identical to a delivery, so the stub's marker is the
   discriminator.
3. **Live Ollama trial** (model quality per llm_voice_preauthoring.md B.4),
   then the budget/killswitch proofs.

## 5. Open for the owner

1. **Host**: local Ollama (private, free, quality-limited) vs a cloud key vs
   the NVIDIA free tier (works for dev fanout; in-GAME use is a different
   posture — flag, not a recommendation).
2. **v1 dormancy**: wiring ships dark in v1 (felt-not-heard holds) — confirm,
   or name the first consumer to go live.
3. **Budget numbers**: calls/day per consumer (proposal: gods 3, raids 1,
   flavor 2).
