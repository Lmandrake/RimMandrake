# enrichment_agents.md — the world-enrichment agent catalogue

_What we want an authoring pass to **add to the world**, sorted by the lifecycle phase it acts
in. Design and brainstorm only — nothing here is committed; an entry graduates to a task once
specced and pillar-checked._

**Salvaged from `RimMaster.md` when that spec was retired.** The dead part was the *mechanism*
(an external save-editing agent behind a GABP relay). The catalogue below never depended on it:
every entry is an authoring intent, and the pipes that execute one are now
`skills/rimbridge/SKILL.md` (live map) and `skills/rimworld-savegame/SKILL.md` (`.rws`).

**Sibling files:** `concept.md` (pillars + the 7-question test) · `desert_world_design.md` (the
terrain/discovery layer these populate) · `jawa_xenotype_and_religion.md` §2.0b (the pantheon §5
leans on) · `design/Jawa/mods/required_mods.md` (which of these a mod already does, and the 1.6 pins).

> **Discipline:** mark claims ✅ verified / 🔎 inference / ❓ unknown. Never write a defName,
> endpoint or command as fact until confirmed against real files.

---

## 1. Scope and stance

**Design stance:** the initial scenario/world is a *seed*, deliberately minimal. Enrichment is how
the world keeps *becoming* — set-pieces, responses to how the game is actually going. This is the
campaign's answer to "don't try to specify every little thing initially."

**In scope:** map enrichment (creatures, structures, ruins, loot, terrain features, sites onto an
already-landed map), narrative/event orchestration, pawn/faction adjustment, staged reveals,
condition-triggered content, QA of our own defs, screenshot-based inspection.

**Out of scope (hard line):** anything that turns enrichment into in-fiction *player power*. It is
an **authoring/GM tool**, never a way for the colony to self-upgrade past the gravship /
VFE-Factory progression trees. Concretely, against `concept.md`:

- **Anti-exponential:** enriches the *world*, never hands the *player* scalable capability.
- **§19.5 no arms race:** injected weapons/loot pass the same balance bar as hand-placed content —
  qualitative interest, not stat inflation.
- **Containment items** (lightsabers) stay quest-earned, never generic loot.
- **Scarcity/mobility levers** (DroidBrain rarity) are respected, not circumvented.

---

## 2. Capability backlog 🔎

Enrichment intents, roughly in build order.

- Place ruins / derelict structures with themed loot (crashed-Factory-ship debris fields).
- Spawn creatures / threats appropriate to the biome + campaign tension.
- Add terrain / resource features (ore, geysers, saber-crystal deposits if in scope).
- Stage set-pieces (the pursuing Empire's arrival beats).
- Condition-triggered content (fire an enrichment when X happens in-game).
- QA mode: validate our own scenario/xenotype/patch defs against the running game.
- Inspect/screenshot game state for planning + verification.

---

## 3. PARKED CONCEPT — real-time NPC (caravan/raid) lore-reshaping 🅿️ (user, 2026-08-07)

**Intent:** when a visiting caravan — or a raid — is inbound/present, *intercept and significantly
edit that group* before (or as) the player engages it. Rather than accepting vanilla-rolled pawns,
rewrite the group into something that fits the fiction: faction-correct gear and xenotypes, themed
names/backstories, a coherent "why are these people here" hook, set-piece composition (a Czerka
survey team, a Hutt debt-collector escort, a scav gang in our established junk aesthetic), maybe a
planted item or objective.

**Why attractive:** turns the single most repetitive content stream in RimWorld (the endless
procedural encounter) into authored, on-theme beats — high enrichment leverage per unit of effort.

**Why PARKED (open questions, not yet a task):**

- **Timing/interception seam (❓):** where in the incident lifecycle can we edit safely? A spawned
  caravan/raid group lives on the live thing-graph, so this is a **live-bridge** job, not `.rws`
  editing. Need to find whether we edit at spawn, on approach, or only once on-map — and whether
  pawn mutation (apparel swap, xenotype, story) survives without desyncing the incident's own state
  (raid AI, trade inventory).
- **Pillar check:** must NOT become a difficulty cheat in either direction — reshaping a raid can't
  covertly nerf threats or hand the player loot. Flavor + interest, balance-neutral; a reshaped raid
  stays as dangerous as the one it replaced.
- **Scope creep risk (⚠️):** editing *raids* is more fragile than editing *caravans* (combat AI,
  hostility state). Prove it on a friendly **caravan/visit** first; consider raids only if caravan
  reshaping is clean across save/reload.

---

## 4. Phased agent catalogue 🔎 (brainstorm — expanded from user seed, 2026-08-08)

Legend: **◇ user-seeded**; all others are extrapolations to grow the space.

> **Cross-cutting rule — prefer setup-time to live.** Phases A–C are almost all **offline**
> (`.rws`/def/texture editing) — safe, backup-able, re-runnable. Phase D is the **live/fragile**
> frontier and carries the §7.1 save/reload-survival unknown. **When an idea can be done at
> setup-time instead of live, do it at setup-time.** The reusable skeleton for nearly all of these
> is *read → propose → human-approve → write-with-V&V → re-verify*; most are **interactive**
> (human-in-the-loop before commit), not fire-and-forget.

### Phase A — Pre-start asset agents (before a game even exists: textures, defs-as-art)

- ◇ **Gravship "aged & broken" texture agent.** Re-skin gravship/Factory-ship structural elements to
  look brown, worn, ancient, sand-scoured — and generate *pre-repair broken* variants of the same
  pieces (scorch, hull breaches, dead running-lights) to inspire the repair-progression art and give
  us before/after reference. Feeds `ship_distinctive_features.md` (running-lights-as-repair-bar) and
  the repair-gate table in `ship_deck_plan.md`.
- **Faction visual-identity kit agent.** Generate a coherent palette + insignia + apparel-tint set per
  NPC faction so Czerka, Hutt, scav, Empire-remnant, droid enclaves *read* distinct at a glance;
  emit the texture/def tints for the ones that are XML-tintable.
- **Icon/label legibility agent.** Batch-audit modded item/def icons for at-a-glance readability at
  RimWorld's tiny UI scale; flag or re-render the muddy ones (many third-party weapon packs share
  near-identical silhouettes).
- **Sound-pack curation agent.** Assemble a Star-Wars-appropriate blaster/door/ambient sound set from
  license-clear sources and map them onto the def soundDefs — a pre-start asset pass, not a live one.

### Phase B — Scenario-start normalization agents (one-time, def-level, before first launch)

_These read the fully-assembled modlist's defs and reconcile the work of many separate authors into
one coherent, pillar-compliant ruleset. All offline def-patch generation._

- ◇ **Weapon/armor normalization agent.** Read ALL weapons + armor across every loaded author and do a
  global sanity/balance pass (damage, cooldown, range, AP, cost, tech-level, market value) so cross-mod
  gear coheres and obeys the **§19.5 no-arms-race** bar. Emit a review table + a patch. (This finally
  operationalizes the long-standing §19.5 audit — see `design/Jawa/mods/world_interest_and_mech_danger.md`.)
- ◇ **Animal normalization agent.** For every animal: reconcile damage, wildness, manhunter tendency,
  beauty, **biome-specific frequency + abundance**, **which factions sell it and at what price**, and
  assign **Star-Wars-appropriate names**. Emit per-animal cards + patch. (Extends the beast-monger
  subsystem + the silver price list in `Livestock_Trade_Utility_Pets_v1.md`; consumes the four-axis
  biome palette.)
- ◇ **Faction repair/enrichment agent.** Read every Faction and fix/complete what the configurable
  world-start mods left thin: **racial mixes, tech availability, willingness to enslave, behavioral
  tendencies, and which cross-faction relations are FIXED vs DYNAMIC.** Reconcile against
  `design/Jawa/worldbuilding/faction_roster_v2.md` (the canonical roster is the spec; the agent makes the running
  game match it).
- **Trader-inventory coherence agent.** Ensure each faction's stock/buy tags match its established
  identity (Jawa buy junk + slaves; Hutts deal contraband; Czerka sells industrial) so trade *feels*
  faction-specific — pairs with the animal agent's "who sells what" output.
- **Research-tree / techprint placement agent.** Verify the three-gate progression chain
  (techprint→prototype→research) is intact across all modded research, and that no mod silently hands
  the player a shortcut around the two sanctioned trees (anti-exponential guard).
- **Apparel/xenotype-legality agent.** Cross-check that faction pawnkinds spawn wearing lore-appropriate
  gear and legal xenotypes (no stormtrooper armor on a Jawa scav).
- **Name-pool localization agent.** Replace generic RimWorld name pools with SW-appropriate name banks
  per faction/race so procedurally-named pawns already read on-theme.
- **Precept/meme consistency agent.** Validate that our buildable Jawa ideoligion + the leveled-up NPC
  belief systems have no contradictory precepts and that custom ThoughtDefs (mourn-death, "a clan is not
  a crowd") are wired correctly — a pre-launch lint of `jawa_xenotype_and_religion.md` against the save.

### Phase C — Tile-map-start agents (each time a new map is generated)

- ◇ **Map hand-crafting agent (the complex one).** Improve a freshly-generated tile toward a
  hand-crafted feel: sensible terrain/coastline/elevation, **appropriate weather events**, and
  **unique scenario-specific opportunity structures** the player can leverage while on the tile. This
  is the `player_maps/` LLM-in-the-loop map-improver line of work, generalized. ⚠️ Biggest V&V surface.
- ◇ **NPC hand-crafting agent (per map).** Sweep the NPCs present on a tile map and significantly
  improve them: lore-appropriate identities, description rewrites, believability, and narrative
  excitement **tuned to the context/state inherited** (who's here, why, what's happening). The offline,
  per-map cousin of the §3 parked live reshaper.
- **Opportunity-structure seeding agent.** Explicitly place the "leverageable" set-pieces: a half-buried
  cache, a defensible chokepoint, a derelict worth salvaging, a tripwire hazard — the tile-specific beats
  catalogued in the 14 set-pieces (see `context.md`).
  ⭐ Parts list for this agent and Landmark-narrative below: `design/Jawa/worldbuilding/tile_augmentation_catalogue.md`
  (31 def-verified augmentations) — which also corrects the pointer above: **15** set-pieces, in `desert_world_design.md` §3E/§3E-bis.
- **Threat-appropriateness agent.** Given the tile's biome + current campaign tension, verify the
  spawned/eligible threats fit (no jungle predators on a salt flat) and read as qualitative danger, not
  point inflation.
- **Landmark-narrative agent.** Attach a short authored "what happened here" hook to native Odyssey
  Landmarks / Ancient Urban Ruins on the map so exploration surfaces story, not just loot.

### Phase D — Mid-game continuous / live agents (during play; live bridge, fragile)

- ◇ **Emergent ship-sentience voice agent.** Let the Kolyska's waking machine-spirit speak to us, guide
  us, and even *make demands* — an in-character AI presence that reacts to game state. Builds on the
  adopted LLM-voice stack (RimAI "Cradle-Mind" persona in `design/RimMandrake/llm_voice_preauthoring.md`); the
  *demands* angle is the new escalation (it wants power routed, scrap tithed, a pod re-lit).
- ◇ **Jawaese speech-shaping agent.** Shape Jawa dialogue into properly-styled Jawaese (canon/chitter/
  synth tiers) — the runtime companion to the built JawaVoice mod + the RimDialogue Jawaese prompt
  (`src/Jawa/JawaVoice`, `design/RimMandrake/llm_voice_preauthoring.md`).
- ◇ **"State of affairs" summarizer agent.** Read the game log — **especially the social log** — and
  maintain a rolling world-state summary that ALL downstream elements (dialogue, ship advice, NPC
  speech, event flavor) draw on. This is effectively the shared **context/blackboard** the two voice
  agents and the live NPC reshaper all read from — arguably build this *first* among Phase D, since it
  is the substrate.
- ◇ **Live caravan/raid reshaper** — the §3 parked concept; belongs here in the lifecycle map. Prove on
  friendly caravans before raids.
- **Social-drama chronicler agent.** Turn notable social-log beats (rivalries, breakups, poly-colony
  fallout) into short in-fiction "clan chronicle" entries — pure read → text, no state mutation, so the
  *safest* Phase D agent.
- **Ship-repair-progress narrator agent.** Watch restoration milestones (running-lights bar) and have
  the Cradle-Mind + crew react to each phase — couples the repair gate to voice.
- **Quest-hook proposer agent.** Watch state for dangling threads (a spared enemy, an unpaid Hutt debt,
  a stolen droid schematic) and propose CQF quest instantiations that pay them off — human-approved
  before injection.
- **Difficulty-drift monitor agent (read-only guardian).** Continuously watch colony wealth/power vs.
  threat scaling and *flag* (never silently fix) when the run drifts toward the exponential failure the
  pillar forbids — a diagnostic conscience, not an actuator.
- **Screenshot/state journaler agent.** Periodically capture annotated state for planning + verification.

---

## 5. Religious-observance & hediff-visibility cluster (added 2026-08-08, user seeds 1 & 2)

_Two user seeds ("more interesting outcomes from religious observances" + "monitor HeDiffs and make
them visible in behavior AND a colony overview the ship-voice speaks to") fanned into 8 agents. All
lean on "The Salvation" pantheon (`jawa_xenotype_and_religion.md` §2.0b — Ohm=ship-AI/Cradle-Mind,
Zizzik=malfunction, Mob'Unloo=ship-ghosts, Oomo=water/atonement, Ta'Baa=leave, Rekko=salvage,
Sh'kaar=evil light). **Pillar bar (§19.5): every ritual/atonement payoff stays in the
narrative/mood/quest register — never material power; any loot routes through the balance-bar gate.**
User verdict 2026-08-08: **"I love all of these" — all 8 logged.**_

- **A. Ritual-Outcome Dramaturge (Phase D, live) 🔨.** Intercept a *completed* ritual's outcome tier
  (vanilla resolves flat outcome→mood) and **author the consequence** as narrative, not dice: a bad
  Reckoning launch-rite spawns a Ta'Baa complication (a pawn "refuses to leave," cargo "claimed by the
  dune"); a good Ohm machine-funeral seeds a CQF quest hook ("the Cradle-Mind remembers this servant").
  This is where **Ohm⇄Zizzik** lives mechanically (blessed-by-Ohm vs spoiled-by-Zizzik = two authored
  branches per rite). *Established:* vanilla exposes outcome tiers. *Inference:* the bridge or a
  save-edit can read the outcome + inject a letter/quest/hediff/memory. *Speculation:* timing the
  injection to feel causal. **Flagship of seed 1; highest §19.5 watch (must never become a faucet).**
- **B. Observance Scheduler / Calendar-Keeper (Phase B author + Phase D nudge) 🔨.** Author a liturgical
  calendar at scenario-start (Oomo water-rationing day, the Reckoning before every launch, a Mob'Unloo
  ledger-balancing day); at runtime nudge toward observance + note lapses ("the clan has not honored
  Oomo in 15 days") for the voice to scold. Phase-B half = pure def-authoring (safe); Phase-D nudge is
  soft (can't force pawns — GM-not-player line). **Low-risk fallback: ship Phase-B-only.**
- **C. Ghost-Ledger Officiant (Phase D) 🔨 — DESIGNABLE NOW; wiring needs an install-time def extract.**
  Give each ship-ghost (Afterlife: Ghosts of the Rim, WS 3737587610, author "Antediluvian") an authored
  "unsettled account" of Mob'Unloo + a *specific* balancing condition (a trade completed, a debt paid,
  an item returned to a wreck), then lay it to rest with a scripted payoff. Turns a generic haunting
  into per-ghost micro-quests. **★ Source status resolved 2026-08-08:** the mod has **NO public GitHub
  repo** (2 search passes + 3 repo-path guesses all 404; Steam-only). But its full behavioral spec is
  already source-read from the Steam page (2026-08-07, `ship_distinctive_features.md` §Afterlife) — five
  spirit types keyed to cause of death; each resolves an "unfinished business" thread (avenge, watch
  over kin, proper burial, finish their work→haunts workbench, guard grave, reunite with lost lover,
  pet-stays-with-owner); gentle spirits pass on with burial, **Vengeful need a built Spirit Shrine +
  seance ritual** (medium channels; success=peace, fail=shaken medium + deepened fury; odds scale with
  Psychic Sensitivity + Social); ignored Vengeful → poltergeist. **C maps ~1:1 onto this system** —
  reframe each ghost's "unfinished business" as a Mob'Unloo *debt* and the seance as *ledger-balancing*.
  **Only the internal defNames (ghost hediffDef, ritualDef, Spirit-Shrine buildingDef, business-job
  hooks) are missing — extract from the subscribed mod folder at install, NOT a web pull.** Deps to
  resolve at install: Harmony (hard) + Anomaly (likely soft; moot if we run Anomaly).
- **D. Colony Health-State Summarizer → Cradle-Mind voice (Phase D, READ-ONLY) 🔨 — SAFEST, build-first
  candidate.** Walk every pawn's hediff set (injuries, diseases, chronic conditions, addictions,
  implants, mood-linked conditions), roll into a colony health digest, hand to the RimAI voice to
  narrate ("two of the clan burn with the same fever; the Cradle-Mind counts three failing hearts").
  The **health-specific instance of the "state of affairs" blackboard substrate** (§4 Phase D).
  *Pure read→text, no write, zero pillar risk.* Directly answers seed-2's "overview the voice speaks
  to." **Free marriage of both seeds:** let the voice editorialize theologically — untended rot =
  "Zizzik's rot," clean recovery = "Ohm held the current steady." (See §7.2 on the read itself.)
- **E. Hidden-Condition Surfacer / Behavior Amplifier (Phase D, live-write) 🔨 — build the read-only
  version first.** The "make conditions visible in behavior" half of seed 2. *Fragile version:* inject
  behavior (addict drifts to drug stock, chronic-pain pawn takes more breaks, disease-incubator gets a
  "restless" micro-event pre-diagnosis) — live job/mental-state injection is brittle and risks feeling
  like puppeteering. *Recommended safe version first:* a **read-only "tell" layer** — detect the hidden
  condition, let the *voice* drop a hint ("the Cradle-Mind notices Griz favors his left side") +
  optional unobtrusive UI marker; escalate only if the tell feels too weak.
- **F. Relic & Sacred-Object Historian (Phase B + D) 🔨.** Rekko's doctrine: every repaired wreck is a
  woken relic. Track which salvaged machines the clan has repaired, author *provenance* (a fabricated
  component "remembers" the wreck it came from, becomes a named minor relic the voice references). Pure
  narrative metadata layer — safe, low-cost, deeply on-theme.
- **G. Divine-Satiation Engine (Phase D) 🔨 — THE SPINE of the religious cluster.** A per-god signed
  satiation vector (8 scalars) on the colony blackboard; A/H/C/F/D all read/write it. Full mechanics
  live in `design/Jawa/divine_satiation_engine.md`. **★ USER DESIGN 2026-08-08 (supersedes the earlier
  "drift-to-baseline" sketch):**
  - **(1) NO drift-to-baseline. Satiation moves by colony events, free-floating,** with a per-god
    resting **bias/temperament** (positive / negative / calm). Gods "feed" on events — sometimes
    *your* misfortune feeds a god (an explosion burning your own stuff *pleases* Sh'kaar; he's lenient
    a while after, "fed"); prolonged peace/abundance can *anger* a god.
  - **(2) Two-sided scalar** — Exalted is rewarded as strongly as Wrathful is punished; symmetric
    around neutral. Bands: Exalted / Content / Neutral / Slighted / Wrathful.
  - **(3) Rituals are NOT one-god** — every rite scores as a weighted sum over the WHOLE vector:
    `Σ ritual_affinity(god) × colony_need(god) × satiation(god)`. A (Dramaturge) reads this to pick the
    outcome branch; a launch-rite triumphs when Ta'Baa starves + the colony needs to move, backfires
    when Ta'Baa is sated but Oomo is wrathful.
  - **(4) Each god gets THREE input channels (design requirement, not "+X% success"):** (a) **ambient/
    random stimulants**; (b) **costly player levers** — actions with real non-religious cost/benefit
    that ALSO move the god (scrapping a repairable machine gives resources but enrages Rekko);
    (c) **strongly unusual extreme-band outcomes** — creative blessings when Exalted / creative harms
    when Wrathful, with **plentiful narrative build-up**. NEVER a flat percentage buff.
  - **(5) Fickle divine Mood** — a SEPARATE self-driven scalar per god, radiating the god's *own* temper
    independent of its view of the colony. Modulates responses.
  - **(6) PC death is contextual & agent-adjudicated** — can settle debts OR greatly anger a god.
  - **(7) Ghosts-as-divine-actors (HYPOTHESIS, parked):** ship-ghosts (agent C) may be the mechanical
    delivery vehicle for earned divine kindness/wrath — revisit when the mod's defs are extracted.
  - **Exalted ≠ resource parachute (cheese-ban):** Exalted yields a *stream of biased-positive
    opportunities* that reward competent play, not free material.
- **H. Confession / Atonement Broker (Phase D) 🔨.** Detect "sins" in state (wasted water → Oomo; a lamp
  lit in the field → Sh'kaar; a pawn who fled an ambush → Ishko) and offer an authored atonement path
  with a mood/social payoff. Feeds G's satiation vector. **§19.5 watch: rewards stay mood/social only.**

**Cross-agent architecture note:** G (satiation vector) is the shared religious blackboard the way the
"state of affairs" summarizer is the shared world blackboard. A and H both read/write G's vector; D
narrates it theologically. Build order within this cluster: **D (safe, standalone) → G (the barometer
substrate) → A + H (hang off G) → B (author-time, ship Phase-B half anytime) → F (cheap, independent)
→ C, E-fragile (gated on source reads).**

---

## 6. Highest-leverage picks (recommendation, for when we start building)

Not a decision — a suggested read of the space: **(1)** the Phase-D "state of affairs" summarizer is
the substrate everything conversational depends on, so it likely comes first among live agents; **(2)**
the Phase-B weapon/armor + animal + faction normalizers are the highest enrichment-per-effort and are
*offline/safe*, so they're the natural first builds overall; **(3)** the Phase-C map + NPC crafters are
high-value but high-V&V, best attempted after a throwaway-save test rig exists. Tradeoff throughout:
**offline (safe, re-runnable) vs live (fragile, save/reload-risky)** — bias to offline wherever an
effect can be baked at setup-time.

**Which of these a mod already does** — the ADJUSTER-vs-DEFINED-EFFECT verdicts and the 1.6
`<supportedVersions>` pins — is in `design/Jawa/mods/required_mods.md`, not here.

---

## 7. Open questions ⚠️

### 7.1 Does live-injected content survive save/reload cleanly?
❓ Untested. Every Phase-D agent inherits the answer. Test early on a throwaway save. Live map
mutation is the fragile frontier — even via the engine route, verify + backup per action. Version
drift is the companion risk: the bridge, companion mods and our defs must all stay 1.6-consistent.

### 7.2 The colony health/hediff read
🔎 Agent D needs to walk every pawn's hediff set. This was predicted as a custom C# requirement; it
may not be, since off-the-shelf context mods already compress health state (see
`design/RimMandrake/llm_stack_assessment.md`). Confirm before building anything.

### 7.3 The event-feed gap — **the most likely place the design meets an unplanned C# requirement**
❓ The divine-satiation engine (§5 G) and the "state of affairs" summarizer (§4 Phase D) both need
*semantic acts* — graded, structured events — and the live bridge only exposes **state reads**, not an
event stream. Nothing in the stack currently emits one that we can rely on: the obvious candidate
(RimLog) is 1.5-only. Either a mod supplies a readable graded-event store, or this is where we write
C#. **Resolve this before committing to any Phase-D build.**
