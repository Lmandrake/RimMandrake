# RimMaster.md — spec for the RimMaster agent (external RimWorld enrichment agent)

_Living specification for **RimMaster**: an external agent we are building to enrich and
evolve a running RimWorld 1.6 + Odyssey game for this campaign. RimMaster works through
**two mechanisms** — offline **save-game editing** (`.rws`) and live **RimBridge / GABP-MCP**
interaction — choosing whichever (or both) gets a given task done safely._

**Started:** 2026-08-04. **Status:** design / not yet built.
**Sibling files (read together):**
- `concept.md` — portable campaign brief (premise, pillars, 7-question test, mod stack).
- `rimbridge.md` — everything we know about the RimBridgeServer mod (the live pipe).
- `rimworld_file_lore.md` — how to edit `.rws`/scenario/def files safely (the offline pipe).
- `concept_defnames.md` — verified defName / packageId / Workshop-ID vocabulary.
- `setup_checklist.md` — live checklist of game-setup decisions before the first save.

> **Discipline (inherited from the whole project):** mark claims ✅ verified / 🔎 reasonable
> inference / ❓ unknown-pending. Never write a defName, endpoint, or command as fact until
> confirmed against real files or a credible source. A wrong defName in a save's thing-ID
> graph is unforgiving.

---

## 1. Purpose & scope

**Mission:** configure the world + scenario as well as we can *up front* (Tier 1), then use
RimMaster to add the much larger set of things we can't or shouldn't bake in initially —
on demand, after arrival, throughout the playthrough.

**Design stance:** the initial scenario/world is a *seed*, deliberately minimal. RimMaster is
how the world keeps *becoming* — enrichment, set-pieces, responses to how the game is actually
going. This is the campaign's answer to "don't try to specify every little thing initially."

**In scope (initial):** map enrichment — inject/create creatures, structures, ruins, loot,
terrain features, sites onto an already-landed map on demand.
**In scope (aspirational, "possibly do more"):** narrative/event orchestration, pawn/faction
adjustments, staged reveals, condition-triggered content, QA/verification of our own defs &
patches, screenshot-based inspection of game state. Grow this list deliberately (§7).
**Out of scope (hard line):** anything that turns RimMaster into in-fiction *player power*.
It is an **authoring/GM tool**, not a way for the colony to self-upgrade past the gravship /
VFE-Factory progression trees. (See §5 pillars.)

---

## 2. Two mechanisms, one agent

RimMaster picks a mechanism per task based on **safety + whether the game is running**.

### 2a. Offline save-editing (`.rws`)  ✅ mechanism understood
- **What:** edit the plain-XML save directly while the game is NOT loaded.
- **Best for:** legible, low-linkage nodes — scenario name/summary/parts, pawn `<story>` +
  `<skills>`, faction names, starting research/things. (See `rimworld_file_lore.md` §2.)
- **Avoid for:** the map thing-ID reference graph + cell/region/pathing data — fragile,
  dangling-reference risk. Only with heavy backup+reload discipline and tiny increments.
- **Guardrails:** timestamped backup → edit → parse-validate XML → reload-test. Always.

### 2b. Live RimBridge / GABP-MCP  ✅ mechanism verified from source (2026-08-04)
- **What:** talk to **RimBridgeServer** v2.1.0 (pardeike, MIT, packageId
  `brrainz.rimbridgeserver`; runs a GABP/MCP host inside a *running* RimWorld) to inspect state
  and invoke the game's own dev/debug/Architect actions programmatically. (Full detail +
  tool list in `rimbridge.md`; per-tool schema in `mod_sources/RimBridgeServer-main/docs/tool-reference.md`.)
- **Best for:** anything touching the live map. ✅ **Confirmed safe:** architecture makes
  *main-thread ownership* non-negotiable — mutations flow through RimWorld's own main-tick /
  long-event paths, sidestepping raw thing-graph injection.
- ✅ **Rich enough — open question RESOLVED.** Built-in tools cover enrichment directly:
  `spawn_thing`, `execute_debug_action` (any dev-menu leaf, incl. cell/thing-targeted),
  `apply_architect_designator` (place buildings/terrain over cell/rect, with `dryRun`),
  `find_random_cell_near` / `flood_fill_cells` (validated placement cells), `get_cell(s)_info`
  (read map), plus save/load, screenshots, camera. Companion mods (New Blueprint WS 3534166729,
  etc.) are optional force-multipliers, not required.
- ✅ **Extensible:** we can add **custom RimMaster primitives as first-class bridge tools** via
  the `RimBridgeServer.Sdk` (`[Tool]` methods in a `BridgeTools` folder) if built-ins fall short.
- ✅ **Batchable:** `rimbridge/run_script` (JSON) or `run_lua` (lowered subset) run ordered
  multi-step sequences in one call — good for compound enrichments.
- **Connect:** via **GABS** launcher (manages port/token) or **Direct mode** (read port+token
  from the RimWorld log, connect to `127.0.0.1:port`).
- **Caveat:** requires RimMaster to speak GABP/MCP as a client — a real programming task, but
  the surface is documented + MIT.

### 2c. Choosing between them (decision rule — draft) 🔎
1. Is the change on the **live map / thing-graph**? → prefer **2b** (engine route).
2. Is the game **not running** and the target a **legible low-linkage node**? → **2a** is fine.
3. Does a **maintained mod or in-game action** already do it? → prefer that over raw edits.
4. When unsure → **2b via a debug action** beats hand-injecting XML.

---

## 3. Architecture — hybrid Python + Cowork-agent-md ✅ (decided 2026-08-04)

**RimMaster is a single agent composed of two cooperating layers**, chosen by how much
determinism a task needs:

- **Python layer — the deterministic spine.** Everything that must be exact, repeatable, and
  safe lives here: `.rws` XML read/edit/validate, backup + rollback, the GABP/MCP client
  transport, defName lookups against `concept_defnames.md`, schema/precondition checks,
  and post-action verification. Reliable plumbing that behaves identically every run.
- **Cowork agent-md layer — the agentic judgment.** Non-deterministic, context-sensitive
  decisions live in agent markdown: *what* would make this map more interesting right now,
  *which* enrichment fits the campaign fiction and pillars, *how* to sequence a set-piece,
  interpreting screenshots/state read-backs. Reasoning and taste, not fixed procedure.
- **How they cooperate:** the agent-md layer decides *intent*; the Python layer executes it
  through **validated, deterministic primitives** (save-edit ops + bridge actions) and reports
  structured results back for the agent to judge and iterate. The Python primitives are the
  guardrail — the agent can only act through them, so non-determinism never reaches raw XML
  or the live thing-graph unchecked.

**Component map:**
- **Client core (Python):** GABP/MCP client — connects to the in-game bridge, discovers
  available tools/actions (via the `RimBridgeServer.Annotations` contract), invokes them.
- **Save-editor module (Python):** XML read/edit/validate for offline `.rws` work, backup-first.
- **Primitive library (Python):** the vetted, typed set of actions the agent is allowed to call
  (e.g. `place_ruin`, `spawn_thing`, `edit_pawn_skills`) — each with preconditions + validation.
- **Task / intent layer (Cowork agent-md):** turns high-level enrichment intents (e.g. *place a
  derelict ruin with loot near the crash site*) into sequences of primitive calls; judges results.
- **Safety/validation layer (Python):** backup, dry-run, post-action verification (screenshot /
  state read-back via the bridge), rollback.
- **Knowledge:** reuses `concept_defnames.md` as vocabulary; logs newly verified defNames back.

**Invocation seam — now informed by the source (2026-08-04):** RimBridgeServer already speaks
**GABP/MCP**, and Cowork agents natively call **MCP tools**. So the cleanest shape is likely:
the Cowork agent-md talks to the bridge as an **MCP client directly** for discovery + simple
calls, while the **Python layer wraps compound/guarded operations** (backup-first save-edits,
multi-step validated enrichments, rollback) that the agent invokes as its own tools. Two viable
integration patterns to choose between when we build:
  - **(A) Python-as-MCP-server:** RimMaster's Python primitives are themselves exposed as MCP
    tools to the Cowork agent; Python internally holds the GABP client to the game. One surface
    for the agent, all guardrails server-side. *Leading candidate.*
  - **(B) Agent-direct + Python sidecar:** agent calls RimBridge MCP tools directly for reads/
    simple spawns, and calls Python only for save-editing + heavy validated sequences.
  - Decide once we prototype; (A) keeps the "agent can only act through vetted primitives"
    guarantee strongest.

**Still open (❓):**
- Pick pattern (A) vs (B) above at prototype time.
- Repo location + project scaffold (likely a dev area under `~/GDrive/Personal/Rimworld/`).
- Whether to author any custom bridge tools via `RimBridgeServer.Sdk` (C#) vs staying on
  built-in tools + Python — decide once we hit a gap.

---

## 4. Capability backlog (grow this) 🔎
Enrichment intents we'll want, roughly in build order. Each becomes a task once specced.
- Place ruins / derelict structures with themed loot (crashed-Factory-ship debris fields).
- Spawn creatures / threats appropriate to the biome + campaign tension.
- Add terrain / resource features (ore, geysers, saber-crystal deposits if in scope).
- Stage set-pieces (the pursuing Empire's arrival beats).
- Condition-triggered content (fire an enrichment when X happens in-game).
- QA mode: validate our own scenario/xenotype/patch defs against the running game.
- Inspect/screenshot game state for planning + this project's verification steps.

### 4a. PARKED CONCEPT — real-time NPC (caravan/raid) lore-reshaping 🅿️ (user, 2026-08-07)
**Intent:** when a visiting caravan — or even a raid — is inbound/present, have RimMaster
*intercept and significantly edit that group* to make it more lore-appropriate and interesting
before (or as) the player engages it. Rather than accepting vanilla-rolled pawns, RimMaster
rewrites the group into something that fits the campaign fiction: faction-correct gear and
xenotypes, themed names/backstories, a coherent "why are these people here" hook, set-piece
composition (a Czerka survey team, a Hutt debt-collector escort, a scav gang wearing our
established junk aesthetic), maybe a planted item or objective.

**Why this is attractive:** it turns the single most repetitive content stream in RimWorld
(the endless procedural encounter) into authored, on-theme beats — high enrichment leverage per
unit of effort, and squarely in RimMaster's GM-tool lane.

**Why it's PARKED (open questions, not yet a task):**
- **Timing/interception seam (❓):** where in the incident lifecycle can we edit safely? A
  spawned caravan/raid group lives on the live thing-graph, so this leans on mechanism **2b**
  (bridge / engine route), not raw `.rws` editing. Need to find whether we edit at spawn, on
  approach, or only once on-map — and whether pawn mutation (apparel swap, xenotype, story)
  survives without desyncing the incident's own state (raid AI, trade inventory).
- **Pillar check (§5):** must NOT become a difficulty cheat in either direction — reshaping a
  raid can't be a covert way to nerf threats or hand the player loot. It's *flavor + interest*,
  balance-neutral; a reshaped raid stays as dangerous as the one it replaced.
- **Determinism boundary (§3):** "make it interesting" is agent-md judgment; the actual pawn
  edits must go through vetted Python primitives (`edit_pawn_skills`-style ops extended to
  apparel/xenotype/story) with backup + post-edit verification.
- **Scope creep risk (⚠️):** editing *raids* is more fragile than editing *caravans* (combat AI,
  hostility state). Likely sequence when we pick this up: prove it on a friendly **caravan/visit**
  first, then consider raids only if caravan reshaping is clean across save/reload.
- **Dependency:** wants the same pawn-authoring primitive set as offline pawn editing, so it
  benefits from that library existing first (§3 primitive library).

---

## 4b. Agent possibilities catalogue 🔎 (brainstorm — expanded from user seed, 2026-08-08)

A running idea-pool of enrichment agents, sorted by the **lifecycle phase** they act in. This is a
*possibilities* list — nothing here is committed; each promising entry graduates to §4 (backlog) →
task once specced and pillar-checked. Legend: **◇ user-seeded** (explicitly proposed by the user);
all others are extrapolations to grow the space. Every agent honors the §5 pillars and the §3
determinism boundary: **agent-md supplies judgment/authoring; a vetted Python primitive does the
actual file/graph write, with backup + V&V of the product.** Most of these are *interactive* (a
human-in-the-loop review before commit), not fire-and-forget scripts.

> **Cross-cutting architecture note.** Phases A–C are almost all **offline** (`.rws`/def/texture
> editing, mechanism 2a) — safe, backup-able, re-runnable. Phase D is the **live/fragile** frontier
> (mechanism 2b) and carries the §6 save/reload-survival unknown. When an idea can be done at
> setup-time instead of live, prefer setup-time. A shared **"read → propose → human-approve →
> Python-writes-with-V&V → re-verify"** loop is the reusable skeleton for nearly all of them.

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
- **Loading-screen / main-menu skin agent.** Produce the Kolyska splash + campaign-title art from the
  concept renders in `promo/` (ties the promo bucket to an actual in-game artifact).

### Phase B — Scenario-start normalization agents (one-time, def-level, before first launch)
_These read the fully-assembled modlist's defs and reconcile the work of many separate authors into
one coherent, pillar-compliant ruleset. All offline def-patch generation._
- ◇ **Weapon/armor normalization agent.** Read ALL weapons + armor across every loaded author and do a
  global sanity/balance pass (damage, cooldown, range, AP, cost, tech-level, market value) so cross-mod
  gear coheres and obeys the **§19.5 no-arms-race** bar. Emit a review table + a patch. (This finally
  operationalizes the long-standing §19.5 audit — see `mods/world_interest_and_mech_danger.md`.)
- ◇ **Animal normalization agent.** For every animal: reconcile damage, wildness, manhunter tendency,
  beauty, **biome-specific frequency + abundance**, **which factions sell it and at what price**, and
  assign **Star-Wars-appropriate names**. Emit per-animal cards + patch. (Directly extends the
  beast-monger subsystem + the silver price list already designed in the Livestock doc; consumes the
  four-axis biome palette.)
- ◇ **Faction repair/enrichment agent.** Read every Faction and fix/complete what the configurable
  world-start mods left thin or unspecified: **racial mixes, tech availability, willingness to enslave,
  behavioral tendencies, and which cross-faction relations are FIXED vs DYNAMIC.** Reconcile against
  `worldbuilding/faction_roster_v2.md` (the canonical roster is the spec; the agent makes the running
  game match it). 
- **Trader-inventory coherence agent.** Ensure each faction's stock/buy tags match its established
  identity (Jawa buy junk + slaves; Hutts deal contraband; Czerka sells industrial) so trade *feels*
  faction-specific — pairs with the animal agent's "who sells what" output.
- **Research-tree / techprint placement agent.** Verify the three-gate progression chain
  (techprint→prototype→research) is intact across all modded research, and that no mod silently hands
  the player a shortcut around the two sanctioned trees (anti-exponential guard).
- **Apparel/xenotype-legality agent.** Cross-check that faction pawnkinds spawn wearing lore-appropriate
  gear and legal xenotypes (no stormtrooper armor on a Jawa scav), reconciling the equip-fielding tool
  against the roster.
- **Name-pool localization agent.** Replace generic RimWorld name pools with SW-appropriate name banks
  per faction/race so procedurally-named pawns already read on-theme before any per-pawn hand-crafting.
- **Precept/meme consistency agent.** Validate that our buildable Jawa ideoligion + the leveled-up NPC
  belief systems have no contradictory precepts and that custom ThoughtDefs (mourn-death, "a clan is not
  a crowd") are wired correctly — a pre-launch lint of `jawa_xenotype_and_religion.md` against the save.

### Phase C — Tile-map-start agents (each time a new map is generated)
- ◇ **Map hand-crafting agent (the complex one).** Improve a freshly-generated tile from whatever the
  game produced toward a hand-crafted feel: sensible terrain/coastline/elevation, **appropriate weather
  events**, and **unique scenario-specific opportunity structures** the player can leverage while on the
  tile. This is the existing `player_maps/` LLM-in-the-loop map-improver line of work, generalized.
  ⚠️ Flagged complex — biggest V&V surface.
- ◇ **NPC hand-crafting agent (per map).** Sweep the NPCs present on a tile map and significantly
  improve/streamline them: lore-appropriate identities, description rewrites, believability, and
  narrative excitement **tuned to the context/state the agent inherits** (who's here, why, what's
  happening). The offline, per-map cousin of the §4a parked live caravan/raid reshaper.
- **Opportunity-structure seeding agent.** Explicitly place the "leverageable" set-pieces: a half-buried
  cache, a defensible chokepoint, a derelict worth salvaging, a tripwire hazard — the tile-specific beats
  catalogued in the 14 RimMaster set-pieces (see memory + `context.md`).
- **Threat-appropriateness agent.** Given the tile's biome + current campaign tension, verify the
  spawned/eligible threats fit (no jungle predators on a salt flat) and read as qualitative danger, not
  point inflation.
- **Landmark-narrative agent.** Attach a short authored "what happened here" hook to native Odyssey
  Landmarks / Ancient Urban Ruins on the map so exploration surfaces story, not just loot.

### Phase D — Mid-game continuous / live agents (during play; mechanism 2b, fragile)
- ◇ **Emergent ship-sentience voice agent.** Let the Kolyska's waking machine-spirit speak to us, guide
  us, and even *make demands* — an in-character AI presence that reacts to game state. Builds on the
  already-adopted LLM-voice stack (RimAI "Cradle-Mind" persona in `runtime/llm_voice_preauthoring.md`);
  the *demands* angle is the new escalation (it wants power routed, scrap tithed, a pod re-lit).
- ◇ **Jawaese speech-shaping agent.** Shape Jawa dialogue into properly-styled Jawaese (canon/chitter/
  synth tiers) — the runtime companion to the built JawaVoice mod + the RimDialogue Jawaese prompt
  (`custom_patches/JawaVoice`, `runtime/llm_voice_preauthoring.md`).
- ◇ **"State of affairs" summarizer agent.** Read the game log — **especially the social log** — and
  maintain a rolling world-state summary that ALL downstream elements (dialogue, ship advice, NPC
  speech, event flavor) draw on, so behavior + speech stay context-appropriate. This is effectively the
  shared **context/blackboard** the two voice agents and the live NPC reshaper all read from — arguably
  build this *first* among Phase D, since it's the substrate.
- ◇ **Live caravan/raid reshaper** — already specced as the §4a parked concept; belongs here in the
  lifecycle map. Prove on friendly caravans before raids.
- **Social-drama chronicler agent.** Turn notable social-log beats (rivalries, breakups, the turbulent
  poly-colony fallout) into short in-fiction "clan chronicle" entries — a narrative read-out of the
  breeding-colony chaos, no state mutation (pure read → text), so it's the *safest* Phase D agent.
- **Ship-repair-progress narrator agent.** Watch restoration milestones (running-lights bar) and have
  the Cradle-Mind + crew react to each phase — couples the repair gate to voice.
- **Quest-hook proposer agent.** Watch state for dangling threads (a spared enemy, an unpaid Hutt debt,
  a stolen droid schematic) and propose CQF quest instantiations that pay them off — human-approved
  before injection.
- **Difficulty-drift monitor agent (read-only guardian).** Continuously watch colony wealth/power vs.
  threat scaling and *flag* (never silently fix) when the run drifts toward the exponential failure the
  pillar forbids — a diagnostic conscience, not an actuator.
- **Screenshot/state journaler agent.** Periodically capture annotated state for our own planning +
  this project's verification steps (already in the §4 backlog; lives here as the continuous form).

### Highest-leverage picks (recommendation, for when we start building)
Not a decision — a suggested read of the space: **(1)** the Phase-D "state of affairs" summarizer is
the substrate everything conversational depends on, so it likely comes first among live agents; **(2)**
the Phase-B weapon/armor + animal + faction normalizers are the highest enrichment-per-effort and are
*offline/safe*, so they're the natural first builds overall; **(3)** the Phase-C map + NPC crafters are
high-value but high-V&V, best attempted after the offline primitive library + a throwaway-save test rig
exist. Tradeoff throughout: **offline (safe, re-runnable) vs live (fragile, save/reload-risky)** — bias
to offline wherever an effect can be baked at setup-time. Principal shared dependency: the §3 Python
primitive library (backup + write + verify) that every one of these leans on.

### Off-the-shelf mod findings — "does a mod already do this?" (Fetcher 2026-08-08)

Motivation (user): *"the less I have to write, the faster I get to play."* A first 20-search Fetcher
batch (`Delivery/2026-08-08_agent_normalization_mods/`) gave optimistic first-pass verdicts; a
follow-up **25-item source-level deep-dive** (`Delivery/2026-08-08_mod_deepdive_claims/`, filed
because the user rightly warned *"a lot of animal frequency things are just 'adjusters' without
normalized effects clearly spelled out — useless"*) then read the actual GitHub READMEs/source and
**materially reversed several verdicts.** The controlling distinction the deep-dive forced:

- **ADJUSTER** — the mod exposes a knob (a slider / an editable stat field) but encodes **no notion of
  what a *coherent* value is**. Customize Animals says it outright: *"This mod does not change anything
  on its own… there are basically no limitations in regards to balance, you decide on what fits."*
  Animal Commonality Tweaker: *"It's a tool for tweaking the wild animal commonality value."* An
  adjuster is a **write surface with no brain** — adopting it deletes *zero* of the agent's real work
  (deciding every value + the §19.5 balance judgment); it only saves writing an XML-poker.
- **DEFINED-EFFECT** — the mod ships spelled-out semantics/targets (per-def rules, event cadences, a
  balance model). *Dynamic Diplomacy* is the clean example: hostility flips ≈every 20 days, conquest
  ≈15 days, new settlements ≈40 days, alliance thresholds, rebellions — a real simulation, not a knob.
  These can genuinely **supersede** a build.

**Verdict legend (revised):** ⛔ **SUPERSEDED** (a *defined-effect* mod does the whole job — build
nothing, just configure) · 🧰 **ADJUSTER-ONLY** (mod is a knob with no defined coherent state — the
agent still decides **every** value + carries the balance judgment; near-zero build saved beyond an
XML-writer) · 🟡 **MECHANISM-ONLY** (mod is a *structured* write surface — richer than a bare knob,
e.g. per-pawnkind/per-faction schema — so the agent shrinks to "decide values + drive the mod") · 🔨
**BUILD** (no off-the-shelf coverage — the agent stays a real build). **⚠️ Every Workshop ID below is
a search/deep-dive hit, NOT yet About.xml-`<supportedVersions>`-verified for 1.6 from the extracted
tree before adopting** (standing rule); items the deep-dive source-tagged 1.6 are noted `[1.6 src✓]`.

| Agent (phase) | Verdict | Off-the-shelf mod(s) — the leverage | Residual we still author |
|---|---|---|---|
| Weapon/armor normalization (B) | 🔨 (pending re-fetch) | **Combat System Rebalanced**, **RWWB / RimWeapon Balance** (932311074), **Vanilla Expanded Rebalance – Weapons** (3619272479); RIMMSQOL for live stat edits — **⚠️ all four 429'd/timed-out in deep-dive; verdict rests on search snippets only, re-filed `2026-08-08_mod_deepdive_refetch`.** First read: RWWB/VE-Rebalance are *authored patch sets* (fixed opinionated values for a scoped mod list), not a general normalizer. | No mod does a *holistic cross-author* pass over OUR exact mod stack; the §19.5 judgment + coherent target values stay ours. Even a defined patch-set only covers its own curated list. **Stays a BUILD until re-fetch proves otherwise.** |
| Animal normalization (B) | 🧰 **ADJUSTER-ONLY** (was 🟡→⛔ — **downgraded**) | **Customize Animals** (2587157544; GitHub ChrisF-127 `1.6/` folder `[1.6 src✓]`) — rich per-animal stat surface but **self-described "changes nothing on its own, you decide what fits"**; **Choose Wild Animal Spawns** (2564042934 `[1.6 src✓]`) per-biome-per-animal slider + density + copy/reverse; **Animal Commonality Tweaker** (2591446825) — *"a tool for tweaking the commonality value"*, and explicitly **only wild spawns — not manhunter, not trader, not enemy-attached animals**; **Livestock Traders** (2960610215 `[1.6 src✓]`) adds generic livestock traders but does **not** map which-faction-sells-what | **Almost everything.** These are knobs, not normalizers — the agent must still decide every commonality/density/stat value AND own the anti-exponential balance model. Adopting them saves only writing an XML-poker. Choose Wild Animal Spawns has the best granularity (per-biome-per-animal) so it's the preferred write surface *if* we drive it. |
| Faction repair/enrichment (B) | **split** | **Dynamic NPC-NPC layer → ⛔ SUPERSEDED: Dynamic Diplomacy – Continued** (NilchEi, 1875168898 `[1.6 src✓]`) is a genuine **defined-effect** sim — hostility flips ≈20d, conquest/razing ≈15d, new settlements ≈40d, ideology adoption, alliances (>10 settlements / 40–60% planet), rebellions, save-safe "History Generation" option. **Static per-faction identity layer → 🟡 MECHANISM-ONLY:** **yc's Faction Editor** (3670833973, **1.6-only** `[1.6 src✓]`, deepest — per-pawnkind gear/forced-gear/material/quality/biocode/xenotype-prob/traits/genes/appearance/trade inventory + faction create/modify; ships AGENTS.md+Api.md+CLAUDE.md) and **TotalControl** (feldoh, *already in stack*, `[1.6 src✓]` — role names/apparel/hair/weapon types/colors/caravan animals per pawnkind per faction); **Xenotype Spawn Control** (bbradson `[1.6 src✓]`) racial mixes; **Faction Customizer** (3336572602 `[1.6 src✓]`) rename/ideology/relations/colour/add | For the **dynamic** layer: only choosing to enable it + initial relations — the *becoming* is off-the-shelf. For the **static** layer: the editors are structured write surfaces (per-pawnkind schema, not bare knobs) but carry **no idea of our roster** — the reconciliation *to* `faction_roster_v2.md` (deciding every value) is still ours. |
| Trader-inventory coherence (B) | 🧰/🟡 | **TraderGen** (3525848981) per-trader specializations = closest to *defined-effect* (ships opinionated trader archetypes) — re-verify; **Trading Options** (2876541977) freq/stock/silver = knobs; **Livestock Traders** (`[1.6 src✓]`, generic, no faction mapping) | The faction-identity → stock *mapping* itself — no mod knows our roster. |
| Research-tree / techprint gate guard (B) | 🔨 | **NONE** — Research Tree (Continued)/ResearchPal/Organized Research Tab are *visualizers/queues*, not gate-requirement editors. Notable negative result. | The entire three-gate integrity check stays an agent/patch job. |
| Name-pool localization (B) | 🧰 ADJUSTER-ONLY | **Cool Names** (3726665156, custom pools per thematic group — 429'd, re-filed), **Pawn Name Variety (Continued)** (3548290568), **[RF] Tribal Pawn Names**, TotalControl (names per faction) | **No SW name-pack exists** — we author every bank ourselves; the mod is just the loader. Correct by nature: a name pool is content, not a normalizable effect. |
| Map hand-crafting (C) | 🟡 (set-pieces) / 🔨 (holistic) | **New Blueprint** (3534166729 — 429'd, re-filed; reportedly built on the *native 1.6 prefab system* = candidate write-primitive for stamping authored set-pieces), **Alpha Prefabs** (3070780021, deep-dive confirmed 1.6 v3.1 + blueprint export + modder Wiki `[1.6 src✓]`), **Real Ruins** (1552146295), **Vanilla Landmarks Expanded** (3656316229); Map Designer (owned) | The *holistic "make a generated tile feel hand-crafted"* judgment — the hard, high-V&V core — stays a build. Prefabs are set-piece *content* (author once, stamp) not a normalizer. |
| NPC hand-crafting per map (C) | 🟡 | **Pawn Editor** (ISOR3X, "change backstories that don't fit the narrative"), **Character Editor** (owned), **Backstory Constructor** (2907131508, *already PRIMARY* in personas doc), **RimTalk Persona Director** (3619548407) | The authored per-NPC content + context-tuning; mods are the write surface. |
| Emergent ship-sentience voice + **demands** (D) | ⛔ candidate (re-verify) | **RimTalk Expand: AI Storyteller** (3715752189 — 429'd, re-filed; search says storyteller *becomes a character* w/ personality dims, "makes demands" almost verbatim); **RimAgentOrca / Orca Deepseek** (GitHub, deep-dive confirmed 1.6 + Skills/orca-storyteller-gm + RAG+Memory + controllerHook + offline XML fallback `[1.6 src✓]`); **Powerful AI Integration** (3744421283); RimAI (already adopted) | Decide **adopt RimTalk-Expand vs keep the RimAI "Cradle-Mind" persona** — may retire a planned build. **⚠️ RimTalk-Expand blurb 429'd; confirm the personality/demands feature from source before retiring anything.** |
| "State of affairs" / social-log summarizer (D) | ⛔ substrate (re-verify) | **RimLog** (3263020460 — 429'd, re-filed; search: logs events/tales/quests/chat/battle to CSV, pitched "for crafting local-LLM story prompts" = our blackboard feed); **RimTalk Lucid Chronicle** (3749797638); **RImtalk Expand: Colony Chronicle** (3714540653) | Agent reads RimLog's export instead of scraping the live log. **⚠️ RimLog page 429'd — confirm the CSV-export claim from source before treating the fragile scraper as deleted.** |
| Social-drama chronicler (D) | ⛔ (re-verify) | **RimLegend** (3697076313 — 429'd, re-filed), **EchoTales** (3473331410), **RimSaga** (3258739992), **RimStory**, Rimworld-Diary (manual) | Style/voice choice only — the chronicler agent likely collapses into one of these. **⚠️ RimLegend page 429'd; confirm scope from source.** |
| Difficulty-drift monitor (D, read-only) | 🟡 | **Visible Wealth** (3461137081, breakdown + pie), **Wealth Display (Continued)** (3298960397), **Wealth Tweaks** (Nexus 694, cap scaling = manual actuator). NB from results: raid points hard-cap ~10,000. | The *automatic pillar-drift flag* (vs a static readout) isn't off-the-shelf; monitoring + manual cap are. |

**Decision translation (revised after the source deep-dive — the earlier optimism was wrong).** The
user's warning held: *most of the "collapse into config" verdicts were overstated because the mods are
adjusters, not normalizers.* The honest breakdown:

- **Genuine build-deletes (defined-effect mods that really do the job):** exactly **one** in the
  normalization space — **Dynamic Diplomacy – Continued** for the dynamic NPC-NPC relations layer (it
  ships a real event sim with spelled-out cadences). The Phase-D substrate deletes (**RimLog** feed,
  **RimLegend/EchoTales** chronicler, **RimTalk-Expand** ship-voice) are *plausible* but **all rest on
  429'd Steam blurbs** — held as "re-verify," not banked, until `2026-08-08_mod_deepdive_refetch` lands.
- **Adjuster-only (🧰) — NOT a build-shrink, correction from the earlier claim:** the animal layer
  (Customize Animals, Choose Wild Animal Spawns, Animal Commonality Tweaker, Livestock Traders) and the
  name-pool layer are **knobs with no defined coherent state**. Adopting them saves only writing an
  XML-poker; the agent still decides **every value** and owns the entire anti-exponential/§19.5 balance
  model. This is the bulk of the work and it does **not** go away. *"The less I have to write" barely
  moves here — what I have to* decide *is unchanged.*
- **Mechanism-only (🟡) — structured write surface, brain still ours:** the static faction-identity
  layer via **yc's Faction Editor** / **TotalControl** / **Xenotype Spawn Control** (per-pawnkind
  schema, richer than a bare knob) — but none know our `faction_roster_v2.md`, so the reconciliation is
  still authored.
- **Still-real builds (unchanged):** research-gate integrity guard (no mod exists), holistic map
  hand-crafter (only set-piece *stamping* is covered), cross-author weapon/armor balancing brain
  (verdict now **🔨 pending re-fetch** — the RWWB/VE-Rebalance "patch sets" are curated to their own
  mod lists, not a general normalizer over our stack).

*Principal risk:* the AI-chronicler/voice mods (RimTalk family, RimLegend, Orca) need an external/local
LLM endpoint and mutate live — they inherit the §6 save/reload-survival unknown + a model-quality
dependency; Phase-D fragile. *Missing info that would change verdicts:* the 8 re-filed 429'd pages
(weapon balance, name pools, New Blueprint prefab API, RimTalk-Expand, RimLog, RimLegend) — until those
land, four ⛔/build verdicts are provisional. *Next step:* read `2026-08-08_mod_deepdive_refetch` on
delivery, finalize the weapon + Phase-D rows, then file About.xml-`<supportedVersions>` confirms for the
front-runners actually worth adopting (Dynamic Diplomacy, yc's Faction Editor, Choose Wild Animal Spawns
as the best-granularity write surface, RimAgentOrca) before promoting any to the §4 backlog or
cross-filing into `mods/required_mods.md`.

---

## 5. Pillar compliance (non-negotiable)
RimMaster must honor the campaign's governing pillars (`concept.md`):
- **Anti-exponential:** RimMaster is an authoring tool; it enriches the *world*, never hands the
  *player* scalable capability that bypasses the two sanctioned progression trees.
- **§19.5 no arms race:** any weapon/loot RimMaster injects passes the same balance bar as
  hand-placed content — qualitative interest, not stat inflation.
- **Containment items** (e.g. lightsabers) stay quest-earned; RimMaster does NOT inject them as
  generic loot.
- **Scarcity/mobility levers** (e.g. DroidBrain rarity) are respected, not circumvented.

---

## 6. Risks & unknowns ⚠️
- ✅ RESOLVED: bridge action set is rich enough for enrichment (spawn_thing + full debug-action
  tree + Architect designators) — companion mods are optional force-multipliers, not required.
  The real reach-extenders are blueprint mods (structures to stamp), not debug-UI mods. (rimbridge.md §2b)
- ⚠️ Live map mutation is the fragile frontier — even via the engine, verify + backup per action.
- ⚠️ External-client complexity: GABP/MCP client is real software to build + maintain.
- ⚠️ Version drift: RimBridge, companion mods, and our defs must all stay 1.6-consistent.
- ❓ Does live-injected content survive save/reload cleanly? (test early on a throwaway save.)

---

## 7. Open questions / next steps
- ❓ Study RimBridge source + GABP spec (download request `2026-08-04_rimbridgeserver_source.txt`
  filed) → fill §3 architecture + §2b action set with ✅ facts.
- ❓ Evaluate companion mods (`2026-08-04_liveedit_companions.txt`) → decide which supply the
  enrichment actions RimMaster will call.
- ❓ Decide RimMaster's language/runtime + repo location after reading GABP docs.
- ❓ Prototype: one tiny end-to-end enrichment on a backup save (bridge route) → record result
  here and in `rimbridge.md` §5 gotchas.
- Keep this file updated as the spec grows (standing directive, 2026-08-04).
