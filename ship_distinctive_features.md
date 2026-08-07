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

_Net:_ keep the SpeakUp(state-keyed voice) + CQF(dialog tree) + persona-core recipe. That is
the closest thing to "personality + moods + talkable" achievable without an LLM. **Decision
unchanged; now evidence-backed that nothing better exists.**

### Q2 — graffiti / signs on walls: YES, two clean options → PROMOTE to [ACCEPTED]

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

### Q3 — holograms & haunted crew: YES → PROMOTE to [ACCEPTED]

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
