# ship_distinctive_features.md — the Kolyska's identity layer

_Created 2026-08-07. A running list of **accepted** distinctive-flavor ideas for the
Kolyska (#15 Falcon Halo hollow hull) — the touches that make it feel like a specific,
lived-in salvaged ship rather than a generic gravship. These are aesthetic / narrative /
light-mechanical identity features, distinct from:_

- _`ship_deck_plan.md` — the wing→region map, heat doctrine, repair-progression gates._
- _`Factory_lore.md` §11 — the buildable interior (fit-check, skeleton, build sheet)._
- _`ship_designs.md` — the hull topology (#15 locked)._

_Status tags: **[ACCEPTED]** = user said yes, log it. **[RESEARCH]** = user liked, a mod
hunt is in flight (see Fetcher). **[IDEA]** = brainstormed, not yet ruled on._

---

## 1. Dead frozen in carbonite — the reliquary heart [ACCEPTED]

The crew's honored dead are **frozen in carbonite** and enshrined, rather than buried or
cremated. The hollow shrine-core at the true ring center (tile 45,92, around the grav-engine)
becomes a **hall of ancestors**: carbonite slabs line the shrine wall — the crew's dead, plus
(canonically) one frozen enemy trophy.

- **Why it fits:** we already have a locked custom carbonite mod (`carbonite_trophy_mod.md`,
  spec v3 — the "Class 3 Carbon Freezing Chamber", black-monolith Slab, minifiable, stacks
  5-high in `SWC_CarboniteRack`). This reuses it as a **funerary** practice, not just a trophy
  one. Zero new mechanics needed — it's a placement + ideoligion-precept flavor.
- **Ties into:** the "engine IS the god" idea (§2) — the dead ring the machine-spirit they
  tend. Reinforces the Jawa reverence-for-the-ship theme.
- **Build hook:** a Jawa ideoligion precept ("the dead are given to the cold, to keep") +
  hand-placed `SWC_CarboniteRack` slabs around the shrine-core wall. Possibly a ritual at the
  freezing chamber for interment.
- **Open:** confirm the carbonite Slab can hold a colonist corpse as "interred" state (spec
  freezes living pawns / material stacks; a corpse is an edge case — verify at build).

## 2. The engine IS the god [ACCEPTED — voice route in RESEARCH]

Frame the restored central grav-controller as a caged, half-understood **machine-spirit** the
Jawa tend but never fully repair — it hums louder as more of the ship comes online. The
shrine-core isn't a metaphor; the engine is literally the object of the faith.

- **Consistency w/ prior decision:** MESSAGE-C batch already decided **ship personality = YES**
  (context.md §D): the restored grav-controller BE a vanilla **persona core**, given a voice via
  a **Custom Quest Framework DialogTree** on a talkable ship-core building. The LLM route
  (RimTalk/RimMind/RimAgentOrca) was DECLINED there. A single earned/quested core = anti-exp
  clean.
- **[RESEARCH] open question the user re-raised:** are there mods that give the ship itself a
  **personality + moods + be spoken to**, beyond the CQF dialog-tree approach? → Fetcher
  `2026-08-07_distinctive_ship_mods.txt` Q1 filed (non-LLM persona/mood/affinity building mods).
  Decision pending delivery; CQF-on-a-persona-core remains the safe baseline if nothing better.

## 3. Asymmetry as identity [ACCEPTED]

Lean INTO the lopsided Falcon mandible arm instead of balancing it. Treat the arm as a
**bolted-on piece from a different wreck** (which, lore-wise, it is): paint it a different
scavenged color, mismatched plating, visibly "not original." The ship reads as assembled from
salvage at a glance.

- **Why it fits:** the whole premise is a Jawa crew repairing an inherited hulk from scavenged
  parts. Visual asymmetry = the premise made legible from orbit.
- **Build hook:** floor/wall material choices + color on the arm wing (M command + H shuttle
  tips) that deliberately differ from the ring hull.

## 4. The dead prong [ACCEPTED]

Leave **one mandible tip as a deliberately un-repaired, exposed structural stub** — a docking
scar where a second shuttle pad used to be. The Falcon arm has two prong tips (two H shuttle
pads in the current design); one stays a broken, open-to-space stump.

- **Why it fits:** reinforces the wreck-being-healed story; a permanent visible wound even
  late-game. Pairs with the [DECIDE E] leaning toward keeping 1–2 wings permanently derelict.
- **Build hook:** author one shuttle-tip region as missing plating / exposed substructure;
  never gets a repair gate. Cosmetic + a small "this ship was hurt" storytelling beat.
- **Note:** trades one of the two shuttle pads → confirm one shuttle bay is enough for the
  campaign's caravan/escape needs before committing both prongs' worth of function to one tip.

## 5. Running lights as a repair progress bar [ACCEPTED]

Most of the hull's lights are **dead**; only repaired sections glow. You can **read the ship's
repair progress from orbit / at a glance** — a living, diegetic progress bar. As each wing is
restored, its lights come on.

- **Why it fits:** the campaign spine is repair-as-progression (7-phase table in
  ship_deck_plan.md). This makes that progression *visible* without any UI.
- **Build hook:** wing lighting tied to repair state — dark wings unlit, restored wings lit.
  Likely hand-managed (place lights only as a wing is restored) or a light-on-repair trigger.

## 6. A shrine to what each pod once did [ACCEPTED]

Each of the 7 rim function-pods gets a **small dedicated altar to its trade** — the food pod
an offering bowl, the forge pod a smith's icon, the raw-extraction pod a miner's shrine, etc.
The factory reads as **devotional, not merely industrial**: the Jawa venerate the work each
pod does.

- **Why it fits:** deepens the "engine is god / ship is sacred" theme down to the pod level;
  turns a factory floor into a temple complex. Cheap to author (décor placement per pod).
- **Build hook:** one small altar/shrine décor object per pod, themed to its region function
  (A/B/C/D/E/F + cargo). Possibly a Jawa precept about honoring the machines' labor.
- **Pairs with:** §1.1 belt-shrine "tithe" node idea (where the 7 belt trunks converge, a
  fraction of goods is ritually offered) — logged as [IDEA] below, not yet accepted.

## 7. Hammocks AMONG the machines [ACCEPTED]

The crew sleeps **in the machinery**, not in proper bedrooms — cramped stacked sleeping nooks
in the keel spine / between pod machines. The Jawa **live inside the ship's working guts**, and
this should be baked into their **religion** somehow (not just a layout quirk).

- **Why it fits:** matches "Jawa live in the machinery" flavor + the prior "prefers-barracks"
  Jawa precept already in the mod batch (memory: mod_batch_2026-08-07 added a prefers-barracks
  precept). This extends it: not just barracks-tolerant but **machine-dwelling as doctrine**.
- **Build hook (religion):** a Jawa ideoligion precept — e.g. "one sleeps where the ship
  breathes" / closeness-to-the-machine as a virtue; mood bonus for sleeping near active
  machinery or in the keel spine, rather than the vanilla "impressive bedroom" drive.
  Mechanically leans on the barracks-preference precept already chosen; confirm we can tie a
  mood/precept to proximity-to-machine (may need a custom precept or a reskin of an existing
  "prefers X room" precept).
- **Layout consequence:** sleeping nooks distributed into the keel/utility spine (K) and pod
  interstitials, not a dedicated habitat wing — frees R-region area and reinforces density.

## 8. Heat vents as a visible ship feature [ACCEPTED]

Make the outboard thermal banks (the B and E hot wings) **vent visibly** — glowing red when
the factory runs hot, an external "the ship is working" tell. The thermal spine isn't hidden
plumbing; it's part of the ship's face.

- **Why it fits:** the heat doctrine (Factory_lore.md §5 / ship_deck_plan.md) already puts the
  booster/heatsink banks OUTBOARD on B/E. This makes that mechanically-required placement into
  a **signature visual** — heat bloom on the hull edge, brightest during 500%-burst production.
- **Build hook:** the thermal banks are already exterior (B/E outboard, 9.9-tile-verified in
  the build sheet). Add glow/vent visuals; possibly the vents open (visual state) when the
  overclock policy is in burst mode. Pairs with §5 (running lights) as the two at-a-glance
  "ship status" tells: lights = repair progress, vents = current workload.

---

## Parked / not-yet-ruled-on ideas [IDEA]

_Brainstormed alongside the accepted eight; kept here so we don't lose them. Not yet approved._

- **Oculus floor** — a single transparent tile at the true center (45,92) looking down through
  the hull to the planet/stars; the one "prayer" spot.
- **Vertical scrap-totem that grows** — the T-totem gains a welded piece per major salvage /
  slain nemesis, visibly recording the run's history.
- **Tractor-beam salvage claw** — reskin the (surviving) shuttle pad as a magnetic grapple that
  hauls in debris/derelicts.
- **Hull graffiti / clan glyphs** — Jawa territory markings + raid tally-marks near airlocks.
  **✅ PROMOTED to [ACCEPTED]** 2026-08-07 — mods found: Signs and Comments Continued (text) +
  Graffiti Mod Continued (painted grime). See "Mod research" §Q2 below.
- **Haunted crew as holograms** — "ghost" former crew rendered as holograms. **✅ PROMOTED to
  [ACCEPTED]** 2026-08-07 — mods found: EGI: Holograms and Projectors (holo décor, 1.4–1.6) +
  Afterlife: Ghosts of the Rim (emergent haunting by our own dead). See "Mod research" §Q3.
- **The sealed pod** — one rim pod kept dark/locked as an ominous mystery, opened late-game as
  an authored CQF encounter.
- **Belt-shrine "tithe" confluence** — where the 7 belt trunks converge, a node where a
  fraction of goods is ritually offered to the totem.
- **Droid mausoleum** — a niche of powered-down droid chassis stood upright like statues
  (fits Tobb the droid-mourner persona).
- **The Cradle nursery** — one intentionally soft, warm, well-lit room (the ship is named
  "Kolyska" = Cradle), jarring against the salvage grime — an emotional anchor.
- **Trophy wall of scavenged tech** — mounted broken weapons/parts they can't use but won't
  scrap: a museum of things-not-understood.
- **Phantom production events** — a long-dead assembler briefly whirs to life on its own;
  eerie, cheap to author (pairs with the hologram idea).
- **Parasite hull-dwellers** — authored vermin/mechanite nests in un-repaired sections, cleared
  as you restore the ship (repair-progression as light dungeon-crawl).
- **Two-faced hull** — port side "Empire clean," starboard "Jawa scavenged."

---

## Mod research — DELIVERED 2026-08-07

Fetcher request `2026-08-07_distinctive_ship_mods.txt` completed (10/10 searches; now in
`Fetcher/Complete/`, raw results in `Fetcher/Delivery/2026-08-07_distinctive_ship_mods/`).
Findings by question. **All Steam Workshop IDs below still need in-hand `About.xml` 1.6 +
`packageId`/deps verification** before adoption (standing rule) — the version tags cited are
from search snippets (evidence), not from the manifests (unverified).

### Q1 — talkable ship AI with moods (NON-LLM): no dedicated mod exists; assemble from parts

_Evidence:_ the search space is dominated by **LLM-backed** mods — RimTalk (3551203752),
RimMind (3707742035), RimAI Core (3560404184), EchoColony (Nexus 604), RimAgentOrca — all of
which need an external/local model. We already **DECLINED the LLM route** (prior decision).
Privacy/offline-leaning ones (RimWorldAI Core 3269938006, Colonist Voices) are still AI-driven.

_Assessment:_ **No off-the-shelf non-LLM "moody, talkable ship-core character" mod surfaced.**
The baseline stands, and it decomposes into three pieces we already own or can add cheaply:

- **Voice / mood-keyed lines → SpeakUp (2502518544).** SpeakUp is a *rules-based* (non-LLM)
  Social Interaction Framework that fires lines conditioned on mood, weather, traits, thoughts,
  needs, and current task. **We already run SpeakUp — JawaVoice is built on it.** A SpeakUp
  extension patch (see SpeakUp Extension 3383734373) could give the ship-core its own reskinned
  voice lines keyed to ship state, so the engine "speaks" without any LLM. _Speculative but
  low-risk:_ needs a talker entity; SpeakUp targets pawns, so the core may need to be a pawn-like
  hidden entity or the lines routed through a nearby tender pawn ("the engine says, through me…").
- **Be-spoken-to / branching dialogue → Custom Quest Framework DialogTree** on the persona-core
  building (unchanged from prior decision). This is the "interact → menu" half.
- **The core object itself → vanilla persona core**, or **Craftable Cores (1985991383)** if we
  want it buildable behind the vanilla AI-persuasion research (anti-exp: prefer the single
  *quested* core, keep Craftable Cores as a fallback only).

_Net (non-LLM baseline):_ keep the SpeakUp(state-keyed voice) + CQF(dialog tree) + persona-core
recipe. That is the closest thing to "personality + moods + talkable" achievable without an LLM.

> **⤴ UPDATE 2026-08-07 — user reopened the LLM route.** The user decided we SHOULD seriously
> evaluate the LLM-powered speaking mods after all. Deep-research request filed:
> `2026-08-07_llm_speaking_mods_deep.txt` — evaluates RimTalk, RimMind, RimAI Core, EchoColony,
> RimAgentOrca on: LLM backend (cloud API vs. local/Ollama offline), cost/privacy, offline
> fallback, 1.6 compat/deps, and **whether a building / the ship-core can be made to speak**
> (RimAI Core's "talk to a Server/Terminal" is the most promising for the engine-is-god voice).
> The SpeakUp+CQF baseline remains the safe fallback if the LLM route proves too heavy/costly.
> ⚠️ Note this would be a real departure from the earlier anti-LLM decision — capture the
> tradeoff (immersion vs. external dependency/cost/determinism) when results land.

#### Q1-bis — LLM speaking mods, DEEP DIVE (Fetcher `2026-08-07_llm_speaking_mods_deep`, delivered 2026-08-07)

_All five mods share one architecture:_ a C# mod scrapes live colony/pawn state, packages it as a
prompt, sends it to an **LLM backend**, and renders the reply as in-game speech/thoughts. They
differ mainly in **what** they voice (pawn chatter vs. a talkable machine vs. the storyteller) and
in **which backends** they support. The backend axis is the one that matters for us:

- **Cloud API** (Google Gemini free tier, OpenAI, OpenRouter, DeepSeek) — easiest, but every line
  leaves your machine, and the free tiers rate-limit (Gemini ≈ 60 requests/day) then either stop
  or bill you.
- **Local / offline** (Ollama, LM Studio, KoboldAI/KoboldCpp) — private, free to run, no request
  cap, but needs a capable CPU/GPU and more setup.
- **Player2** — a free desktop app several of these mods bundle as the "zero-setup" default; it
  brokers the model (and adds TTS voice) without an API key. Still an external process.

_Per-mod findings:_

- **RimTalk (Steam 3551203752; GitHub `jlibrary/RimTalk`, v1.0.16, CC-BY-NC-SA).** The most
  mature / most-recommended. **Hybrid backend by design:** paste a free Gemini key to start; when
  you hit the 60/day cap it **auto-switches to a local Ollama server** ("free to run, works
  offline, completely private; needs a good CPU/GPU"). Advanced Settings → "Local Provider" radio
  → point at your Ollama/LM-Studio LAN endpoint (e.g. `https://SERVER-IP:8443`). Also supports
  Player2. Rich add-on family (Prompt Enhance, Event Plus, Expand Memory/Actions/Literature, TTS).
  Voices **pawn-to-pawn chatter** in speech bubbles. _Best-supported, most flexible backend._
- **RimMind (suite; Core 3707741395 + Storyteller 3707742035, author mcochaa, tagged 1.6).** The
  most ambitious: a 7-module suite (Core/Actions/Advisor/Dialogue/Memory/Personality/Storyteller,
  GitHub org `RimWorld-RimMind-Mod`) that gives colonists **daily LLM personality assessments,
  persistent editable personality profiles, mood-offset thoughts, memories, autonomous
  decisions**, and even an AI storyteller. Notably it ships a **Bridge (RimTalk)** module
  (3710599042) so it can piggyback RimTalk's backend, and community **local relays exist** for LM
  Studio (`raz334/Local_LMStudio_RiMind_Relay`, `archdukejim/rimmind-lmstudio-bridge`). _Heaviest
  footprint, most LLM calls (daily per-pawn) → highest cost/latency; deepest simulation._
- **RimAI (Framework 3529263357 + Core 3560404184 BETA; GitHub `oidahdsah0/Rimworld_AI_*`, v4).**
  **The standout for our "engine is god" idea.** Framework is the LLM-comms dependency/API; Core
  adds a **talkable "Server/Terminal" BUILDING** — "you'll talk to an AI Server/Terminal that
  watches your base, jokes with other servers, and gets things done." This is the only mod where
  the voice is natively a *machine you build and address*, not a pawn — a near-perfect vehicle for
  the grav-controller-as-machine-spirit. Setup: subscribe to Framework, choose a provider, set
  base URL + API key, run a Test + Save (so **cloud or local** both work via the base-URL field).
  _Beta; enterprise-y architecture; the machine-voice fit is uniquely on-theme._
- **EchoColony (Steam 3463505750; Nexus 604; GitHub `CarlosNahuelcoy/EchoColony`, MIT-modified,
  1.5–1.6, active `1.6/` branch).** Talk **directly to individual colonists** ("their feelings,
  memories, relationships, traumas, goals"); per-colonist memory persists across sessions.
  Backends: **Player2 (default, free, +voice), Gemini, Local (Ollama/LM Studio/KoboldAI),
  OpenRouter.** Caveats: author's self-described first mod, mixed EN/ES code, and the license
  **hard-mandates keeping Player2 wired in** (can't ship a Player2-free fork). _Good local
  support; roleplay-forward; messier codebase + Player2 lock-in clause._
- **RimAgent: Orca Deepseek (Steam 3736679812; GitHub `RedstonePanda00/RimAgentOrca`, 1.6, BETA).**
  An **LLM storyteller/companion**, not a chat layer: "Orca" observes the colony, talks with you,
  and picks story incidents when a provider is configured. **Best offline story of the five:** it
  ships **XML storyteller comps for offline play**, and with *no* LLM configured "the AI decision
  layer stays silent and RimWorld falls back to the XML-defined storyteller" — i.e. it degrades
  gracefully to vanilla. _Different job (narrative pacing) than a talkable ship-core._
- **RimDialogue (johndroper; `RimDialogueClient` + `RimDialogueServer`, already downloaded in
  Fetcher `2026-08-05_rimdialogue_llm_reframe`).** A fork of Jaxe's Interaction Bubbles: takes the
  *vanilla* interaction ("X and Y chatted about crazy eels") and has an LLM **rewrite it into real
  dialogue** in the existing speech bubbles — a lighter, more contained approach than full agentic
  pawns. Killer feature for us: **"Additional Instructions"** free-text in settings sets the whole
  colony's culture/voice (e.g. "everyone speaks in salvage-cult reverence"; "only Jawa-named pawns
  chitter"). Backend via its own server: **local Ollama or cloud API key** (needs .NET 9 + an
  internet connection for cloud). _Lowest-risk LLM option: reskins existing chatter rather than
  driving behavior; the culture-prompt is a clean lever for the Jawa/salvage tone._

_Decision translation (this is a design choice, not yet made):_

- **If the goal is the "engine is god" talkable machine-spirit → RimAI Core's Server/Terminal is
  the on-theme pick** (only native *building* voice), pointed at a **local Ollama** backend for
  privacy/no-cost. Tradeoff: BETA maturity + a Framework dependency + LLM nondeterminism.
- **If the goal is atmospheric Jawa/salvage-cult flavor with least risk → RimDialogue** (reskins
  vanilla chatter; the "Additional Instructions" culture prompt does the Jawa voice) **or RimTalk**
  (most mature, hybrid Gemini→Ollama). Either layers cleanly over JawaVoice's *text* reskin —
  JawaVoice changes the words shown; an LLM mod changes what's *said*.
- **Avoid stacking with SpeakUp-driven lines for the same pawns** — SpeakUp/JawaVoice and an LLM
  chatter mod both write to interaction/speech text, so pick one owner per surface (LLM for
  free-form dialogue; SpeakUp for the deterministic Jawaese gloss) or scope them to different
  triggers to prevent double-talk.

_Principal risks / dependencies to weigh:_ (i) **external dependency** — every option needs either
a cloud key (privacy + rate-limit + possible cost) or a local model (hardware + setup);
(ii) **nondeterminism** cuts against the anti-exponential/authored-tone pillar — LLM output can
drift off-lore or off-tone; (iii) **1.6 compat + deps** still need in-hand About.xml verification
at install for all of them; (iv) **performance** — RimMind's daily per-pawn calls are the heaviest;
RimDialogue/RimTalk are lighter. _Missing info that would help:_ your hardware (can it host a
7–12B local model at playable latency?) and whether you want the AI to *drive behavior*
(RimMind/RimAgentOrca) or only *speak* (RimDialogue/RimTalk/RimAI-Core). _Recommended next step:_
if we pursue this, prototype **RimAI Core (engine voice) + a local Ollama** first, keeping the
**SpeakUp+CQF baseline** as the no-LLM fallback; treat RimDialogue as the low-risk alternative if
RimAI's beta proves fragile. **No adoption logged yet — awaiting your call on backend + which mod.**

#### Q1-bis DEEP DIVE — RimAI Core vs. RimDialogue, source unpacked (user "Go for it," 2026-08-07)

_Both source trees fully unpacked + read from disk (Fetcher `2026-08-07_rimai_rimdialogue_source`;
RimDialogueClient from `2026-08-05` delivery). Verbatim About.xml / README findings below. This is
the head-to-head the "NEXT" block promised — verdict at the end. **Still no adoption logged; this is
the evaluation, your call remains open.**_

**Hard facts pulled from the actual files:**

| | **RimAI (Framework + Core)** | **RimDialogue (Client + optional Local Server)** |
|---|---|---|
| Author / pkgId | Kilokio — `kilokio.rimai.framework` (v4.2.1) + `kilokio.rimai.core` (v5.1.1-**beta**) | John Roper — `ProceduralProducts.RimDialogue` (BETA) |
| Supported ver | Framework **1.5+1.6**; Core **1.6 only** | Client **1.6** |
| Deps | Framework: none but base + Newtonsoft (**no Harmony**). Core: **Harmony + Framework**. Load: Harmony→Framework→Core | **Harmony + Jaxe's Interaction Bubbles** (`Jaxe.Bubbles` 1516158345) |
| Backend | Provider-agnostic via JSON `provider_template_*` — OpenAI / Ollama / Groq / DeepSeek; base-URL + optional key in Mod Options (blank key = local) | Hosted (Roper's server, free tier + Patreon) **OR** self-run **RimDialogue Local Server** (.NET 9): Ollama (`OllamaUrl` :11434) or cloud key (Groq/OpenAI/AWS) |
| What it voices | A buildable **"Server/Terminal"** object with personas/worldview/backstories; env-aware chat; can *call tools* (intel scans, logistics tallies, production nudges w/ cooldowns) | Transforms **vanilla pawn interactions** into real speech bubbles (fork of Interaction Bubbles); ~100 data points/interaction |
| Steer-the-tone lever | Persona module (per-server personality) + multilingual LLM support | **"Additional Instructions"** free-text — scoped ALL_PAWNS / COLONISTS / **per-pawn by ThingID** |
| Offline | Yes (point base-URL at Ollama) | Yes (Local Server + Ollama) |

**⇒ HOW WE'D BENEFIT (benefits first, as asked):**

1. **RimAI = the literal "engine is god" payoff (feature §2).** It's the only mod in the whole
   search space that gives a *buildable, talkable in-world object* with its own persona. We build
   ONE and theme it as the grav-controller / machine-spirit: crew "consult the engine," it answers
   in-character from live ship state. That's the distinctive-feature §2 promise delivered natively,
   no reskin gymnastics. The **Persona module** means we author its worldview once (the Kolyska's
   dead-ship melancholy, the Jawa reverence) and it stays in voice.
2. **RimDialogue = ambient life with almost zero authoring.** It quietly upgrades the pawn chatter
   we already get from Interaction Bubbles into real dialogue. Lowest-risk, lowest-touch: it never
   invents *new* systems, it just re-skins text that vanilla already generates. Great "colony feels
   alive" texture without any anti-exp exposure (see below).
3. **Both run fully offline** (Ollama base-URL), which kills the recurring cost + privacy objection
   for a personal single-player game. RimAI needs no server process at all (base-URL straight to
   Ollama); RimDialogue needs the small .NET 9 Local Server but it's free/open-source.
4. **They're not mutually exclusive.** RimAI voices *the ship* (one oracle building); RimDialogue
   voices *the pawns* (ambient bubbles). Different surfaces → they could co-exist: engine-as-god for
   set-piece consultation, RimDialogue for background Jawa banter. (Would want to confirm they don't
   both try to drive the same bubble; RimAI's chat is its own window, RimDialogue owns the bubbles,
   so likely clean.)

**⇒ THE JAWAESE-TRANSLATION IDEA — verdict: FEASIBLE, and RimDialogue is the better vehicle.**
   You asked whether one of them could translate ordinary game speech into Jawaese without "running
   away" from the narrative. Confirmed from the source:
   - RimDialogue's About.xml ships the exact precedent — *"All the men in the colony speak French"* →
     only male pawns speak French. And the client code stores instructions **per pawn ThingID** and
     per group (`InstructionsSet.COLONISTS` / `ALL_PAWNS`), and the server prompt templates inject
     `Initiator.Instructions` / `Target.Instructions` verbatim. So an instruction like *"Jawa pawns
     speak in their own Jawaese chitter, with a short English gloss in parentheses"* is directly
     supported and can be **scoped to Jawa only** — non-Jawa crew keep normal speech.
   - **Why this is narrative-SAFE rather than narrative-run-away:** the LLM here is only rewording an
     interaction the *game already decided happened* ("X and Y chatted about crazy eels"). It doesn't
     invent events, spawn items, or change world state — it's a pure **presentation post-processor**.
     That's exactly the "doesn't run away" property you want.
   - **This is the LLM-powered evolution of what JawaVoice already does by hand.** JawaVoice
     (built 2026-08-06) is a *static* SpeakUp reskin: fixed `Jawaese. (English gloss)` line pool.
     RimDialogue-with-instructions would make that gloss **dynamic and context-aware** (the Jawaese
     "wraps" whatever the pawns are actually talking about). ⚠️ **They'd collide** if both are live —
     JawaVoice/SpeakUp and RimDialogue both want to own interaction text. Pick one lane: either keep
     JawaVoice static (deterministic, free, offline, already built) OR let RimDialogue own Jawa speech
     dynamically (richer, but LLM-dependent). Don't run both driving the same bubbles.
   - RimAI *could* also be prompted into Jawaese via its Persona, but that only voices the *one ship
     object*, not pawn-to-pawn chatter — wrong surface for a colony-wide speech style. For the
     translation idea specifically, **RimDialogue wins**; for the talking-ship idea, **RimAI wins**.

**⇒ TRADE-OFFS / COSTS (only after the upside):**

- **Both are BETA.** RimAI Core is explicitly `5.1.1-beta` / "playable content (BETA)"; RimDialogue
  is BETA in its own About. Expect churn, occasional breakage on RimWorld point-updates.
- **RimAI = the bigger anti-exp watch-item.** Its selling point is that the AI can *call tools*
  ("logistics tallies, production nudges, security tips, intel scans"). Anything that *acts on* the
  colony (not just talks) is exactly the kind of power-creep the anti-exponential pillar guards
  against. Mitigation: it's cooldown/requirement-gated by design, and we can treat it as
  **voice-only** (consult/flavor) and ignore the actuator tools. Needs a play-test to confirm the
  tools are ignorable and don't trivialize decisions.
- **RimAI dependency weight:** two mods (Framework + Core) + Harmony, Core is 1.6-only (fine, we're
  1.6). RimDialogue also needs Harmony + a *third-party* mod (Jaxe's Interaction Bubbles) and — for
  offline — a separate **.NET 9 server process** you launch alongside the game. That server is real
  setup friction (install .NET 9, run Ollama, edit `appsettings` for `OllamaUrl`/model). RimAI has
  **no separate process** — arguably simpler offline.
- **LLM nondeterminism vs. authored-tone pillar (both).** Output varies run-to-run; can drift
  off-lore or produce anachronisms. RimDialogue's per-pawn instructions + RimAI's Persona both damp
  this but neither eliminates it. This is the core reason the *static* JawaVoice still has a place.
- **Hardware / model quality (offline).** A small local model may produce flat or garbled Jawaese;
  good output wants a capable Ollama model = RAM/VRAM cost on the play machine.
- **Hosted RimDialogue** (if you skip the local server) = internet dependency + free-tier throttle
  that the author explicitly says may shrink "based on server load and my bank account." Not
  something to build a campaign identity on → if we adopt RimDialogue, use the **Local Server**.

**⇒ RECOMMENDATION (inference / recommendation, not established fact):**
   Two independent decisions, not one:
   - **Talking ship (feature §2):** prototype **RimAI (Framework + Core)** pointed at local Ollama,
     used *voice-only* (persona consultation, ignore the actuator tools) — it's the only native fit
     for a buildable machine-spirit. Keep SpeakUp+CQF as the deterministic fallback if the beta is
     flaky.
   - **Jawa speech style:** this is a **fork in the road, decide don't stack** — (A) keep the already-
     built, free, offline, deterministic **JawaVoice** (recommended default; zero new deps, no LLM),
     or (B) adopt **RimDialogue Local Server** with a Jawa-scoped "Additional Instructions" prompt for
     *dynamic* context-aware Jawaese, accepting the .NET 9 + Ollama setup and beta/nondeterminism
     cost. **Do not run both** — they fight over the same interaction bubbles.
   - _Missing info that would sharpen this:_ (i) a play-test confirming RimAI's tools are safely
     ignorable; (ii) confirm RimAI window vs. RimDialogue bubbles truly don't collide if co-run;
     (iii) local-model quality check on actual Jawaese gloss output.

> **✅ DECISION (user, 2026-08-07): ADOPT BOTH — "we will compare in situ when we have an
> installation."** Both logged into `required_mods.md`: RimAI (Framework `3529263357` + Core
> `3560404184`) as **§(8) the talking ship** (feature §2), used voice-only with SpeakUp+CQF as
> fallback; RimDialogue verdict in §(1) flipped to ✅ ADOPTED. **One thing still to resolve AT
> INSTALL, not now:** the Jawa-speech FORK — RimDialogue's Jawa Special-Instructions and the static
> JawaVoice SpeakUp reskin both write interaction bubbles, so pick ONE lane in situ (don't stack).
> RimAI (ship) and pawn-speech (whichever) are complementary surfaces and both stay.
>
> **📝 PASTE-READY PROMPTS PRE-AUTHORED 2026-08-08 → `llm_voice_preauthoring.md`.** The actual
> text is now written and ready for install: PART A = the RimAI Persona for the Kolyska
> machine-spirit ("Cradle-Mind" — identity/worldview/backstory fields, anti-exp refusal baked into
> voice, voice-only); PART B = the RimDialogue "Additional Instructions" Jawa-scoped dynamic-Jawaese
> prompt + the A/B-vs-JawaVoice table + scope/model-quality install checks. The two in-situ
> decisions (RimAI tools ignorable? Jawa lane JawaVoice-vs-RimDialogue?) remain open by design.

### Q2 — graffiti / signs on walls: YES → ✅ BOTH ADOPTED (user, 2026-08-07)

_Adopted into `required_mods.md` §(7) "Wall signs + graffiti". About.xml 1.6/deps still to
confirm at install._

- **Signs and Comments Continued (3281950776)** / **…Fixed (3656641385)** — placeable signs
  with *arbitrary custom text*, adjustable font size + label color, and adds sign functionality
  to some vanilla buildings. GitHub: `JTJutajoh/RimWorld.Signs`. Snippet-tagged current/1.6.
  → **PICK for readable text** (clan names, airlock labels, memorials, per-pod dedications for §6).
- **Graffiti Mod (Continued) (2986996933)** — actual painted wall graffiti (GitHub
  `emipa606/GraffitiMod`); note the author says graffiti is intentionally "ugly"/grungy and you
  may want CleaningArea to stop auto-cleaning. → **PICK for the grungy clan-glyph / tally-mark
  look** near airlocks (the "hull graffiti" parked idea).
- _Also seen:_ `Falconne/LabelsOnFloor` (floor labels — utility, not decor).

→ Promotes the parked **"Hull graffiti / clan glyphs"** idea to ACCEPTED. Suggest **both**:
Signs&Comments for legible text, Graffiti Mod for the painted grime. Feeds §3 (asymmetry),
§6 (per-pod dedications can be signs), and airlock territory-marking.

### Q3 — holograms & haunted crew: YES → [ACCEPTED]; Afterlife under active exploration

_Follow-up filed 2026-08-07: `2026-08-07_afterlife_ghosts_explore.txt` downloads the Afterlife
source + Steam page so we can read its real mechanics/defs/deps before wiring it in._

- **EGI: Holograms and Projectors (2979598490)** — snippet-tagged **v1.4–1.6**, CC-BY-4.0,
  save-safe. 571 holographic projections / 14 categories / 2 projector "thrones", gated behind a
  **"Holo-Projection" research** and built at a fabrication bench; three passive-buff modes
  (incl. teaching children). Lite predecessor = "Holograms And Projectors" (2847321165).
  → **PICK for holographic décor** — the shrine-core, per-pod altars (§6), and the "engine is
  god" hall can all be dressed with holograms. Research-gated fits anti-exp.
- **Afterlife: Ghosts of the Rim (3737587610)** — dead colonists can **linger as ghosts**;
  tiles near a ghost grow colder, passing colonists feel a chill; bonded pets can return as
  companion spirits. → **PICK for the "haunted former crew" beat** — this is the closest to
  walking apparitions of *your own* dead, and the tone (melancholy, environmental) fits a
  tech-wreck better than a monster-hunt. Pairs beautifully with §1 (carbonite dead) — the
  frozen honor the body, the ghost is the lingering self.
- _Weaker fit:_ **Hauntings and Ghosts (3350002888)** = 10 combat/exorcism ghosts (horror
  boss-fights) — more of a threat system than an ambient "haunted ship." Skip unless we want a
  hostile-haunting encounter.

→ Promotes the parked **"Haunted crew as holograms"** idea to ACCEPTED, split cleanly:
**EGI** for deliberate holographic *decoration/projection*, **Afterlife** for emergent *haunting
by our own dead*. Both are optional flavor layers, not load-bearing on any system.

> Interaction/compat note: none of these five touch the ship/grav layer, so none collide with
> VGE-as-sole-ship-layer. EGI and Afterlife add their own defs/research; low interaction risk.
> Confirm each About.xml is genuinely 1.6 before install.

---

## Afterlife: Ghosts of the Rim — explored 2026-08-07 (Steam page fully read)

_Source: Fetcher `2026-08-07_afterlife_ghosts_explore` — Steam page fetched (200, rendered).
GitHub source zipball NOT found under emipa606; **actual author = "Antediluvian"** — retry
`2026-08-07_afterlife_src_retry` filed (may simply have no public repo, which is fine — the
Steam description is complete)._

**Identity / version (evidence, from the live Steam page):**
- WS **3737587610**, author **Antediluvian**, tagged **"Mod, 1.5, 1.6"**, 216 KB, updated
  Jun 2026. ~2,655 subscribers. RUS translation exists (3742695079).
- **Deps:** requires **Harmony**. **Anomaly DLC** — the Steam sidebar lists it under "REQUIRED
  DLC," but the description text says *"No DLC required, though Anomaly is recommended"* and
  *"Compatible with Royalty, Ideology, Biotech, and Odyssey, and none of those are needed."*
  ⚠️ **Contradiction to resolve at install** — the store's hard-required-DLC flag vs. the
  author's prose. [Inference:] Anomaly is likely a *soft* requirement — without it ghosts stay
  translucent but lose the "hard-to-target shimmer" (which reuses Anomaly's invisibility hediff;
  a comment shows `PsychicInvisibility` from Anomaly in use). **We do plan to consider Anomaly
  anyway; if we run it, this is a non-issue.** If we skip Anomaly, verify the mod still loads.

**What it actually does (this is a rich, story-driven mod — more than ambient chill):**
- **The ghost is THEM** — a translucent copy with the same name, backstory, skills, appearance,
  relationships. Can't be harmed or killed normally. *Perfect* for "haunted former Kolyska crew."
- **Who returns:** colonists have a high (tunable) chance; outsiders only if their death "carried
  weight." Hard per-map cap. All in mod settings.
- **Five spirit types keyed to how they died:** Friendly (comforts family), Protective (shields a
  living blood relative/ward), Mournful (died alone — easiest to lay to rest), Vengeful
  (murdered/executed/wronged — haunts the living), Companion (a bonded pet).
- **Unfinished business** each ghost resolves to move on: avenge death, watch over a loved one,
  get a proper burial, finish their work (haunts their workbench!), guard their grave, reunite
  with a fallen lover, or a pet staying with its owner.
- **Laying to rest:** gentle spirits move on with a proper burial; **Vengeful ones need a built
  "Spirit Shrine" (Building>Misc) + a SEANCE ritual** — a colonist medium channels; success =
  peace, failure = the medium is shaken and the ghost's fury deepens. Odds scale with the
  medium's Psychic Sensitivity + Social.
- **Escalation:** an ignored Vengeful ghost becomes a **poltergeist** — hurls chunks, flings
  colonists, drives them mad. Disturbing a grave resurrects that colonist as furious.
- **Resurrection** pulls a spirit back into its revived body (ghost vanishes).
- **"Play as a ghost"** endgame: if your last colonist falls but a ghost lingers, you can
  continue AS the spectral guardian — terrify intruders, draw a new wanderer to resettle.
- **Atmosphere:** shimmer + cold spots + chill when walked through. Optional wall-phasing (blink
  toward the focus of their business).

**Fit assessment for the Kolyska:**
- **Strong thematic fit + surprisingly deep.** This is *emergent story*, not just decor — it
  pairs beautifully with §1 (carbonite reliquary dead) and the "engine is god / ship remembers"
  theme. The "finish their work → haunts their workbench" business is *chef's-kiss* for a
  factory ship; a dead crafter lingering at their bench is pure Kolyska.
- **Anti-exponential check:** it's a *narrative/mood* system, not a power faucet. Protective
  ghosts give a mood/defense comfort and Vengeful ones inflict dread — both tunable/disableable
  in settings. No production, research, or economy lever. **Passes the pillar** as long as we
  don't lean on protective-ghost mood as a crutch; dial colonist-ghost chance to taste.
- **Tone caution:** the escalation (poltergeist flinging pawns) is more *active horror* than the
  "melancholy hologram" the user first pictured. That's tunable ("Vengeful ghosts haunt" → off
  makes them passive), but note one comment reports the passive toggle didn't take for a
  poltergeist-stage child ghost — **verify the passive setting actually holds at install.**
- **Known rough edges (from comments, [evidence] but anecdotal):** passive-toggle not always
  respected once poltergeist stage hits; raider ghosts getting "finish the work" business with
  no workbench to finish; interaction with other death-adding mods (Zombieland) spawning
  unwanted ghosts. All minor; none blocking.

**Verdict:** **ADOPT-leaning, pending (a) the Anomaly dependency resolution and (b) a settings
pass to keep the tone melancholy rather than horror.** Wire the Spirit Shrine into the shrine-core
(§2) region; let dead crew haunt their old pods (§6). Awaiting user confirm before flipping to
formal ADOPTED in `required_mods.md`.

---

## Follow-up research still in flight (filed 2026-08-07)

- `2026-08-07_afterlife_src_retry.txt` — corrected attempt to find Afterlife's source under
  author "Antediluvian" (may have no public repo).
- `2026-08-07_llm_speaking_mods_deep.txt` — deep dive on the LLM speaking mods (see Q1 UPDATE).
  _Note: a prior related delivery exists — `2026-08-05_rimdialogue_llm_reframe` (RimDialogue,
  johndroper) — worth cross-reading when synthesizing._

_Adopted so far from this line of work:_ **Signs and Comments Continued** + **Graffiti Mod
Continued** (required_mods.md §(7), user 2026-08-07).
