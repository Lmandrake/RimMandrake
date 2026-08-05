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
