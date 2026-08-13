# RimMaster.md — RETIRED residue (the dead mechanism sections only)

> ⛔ **Not authoritative. Do not cite, follow or copy from this file** (`disposing/README.md`).
>
> **RimMaster was an external agent that would drive RimWorld by save-editing behind a GABP relay.
> It was never built and is abandoned.** What replaced it: `skills/rimbridge/SKILL.md` +
> `Utils/rimbridge_client.py` + the `JawaBench.BridgeTools` companion DLL for the live game, and
> `skills/rimworld-savegame/SKILL.md` for `.rws` work.
>
> **Everything live in this file was salvaged before it landed here:**
> - the enrichment-agent catalogue, the Phase A–D lists, the religious/hediff cluster, the parked
>   caravan/raid reshaper, the leverage picks and the open questions →
>   `worldbuilding/enrichment_agents.md`
> - the "does a mod already do this" audit, the ADJUSTER-vs-DEFINED-EFFECT taxonomy and the
>   ship-voice bake-off verdict → `mods/agent_supersession_audit.md`
> - the 1.6 `<supportedVersions>` pins → `mods/required_mods.md`
>
> **Dropped as relay-only:** the relay-restart rule (the relay held a socket to the RimWorld
> process and had to be restarted after every game restart — `rimbridge_client.py` re-reads
> host/port from `Player.log` each call, so the failure mode no longer exists); the
> Python-as-MCP-server vs agent-direct integration choice; the "decide RimMaster's language,
> runtime and repo location" open questions.

**Started:** 2026-08-04. **Status:** design / never built. **Retired:** 2026-08-13.

---

## 2. Two mechanisms, one agent

RimMaster picks a mechanism per task based on **safety + whether the game is running**.

### 2a. Offline save-editing (`.rws`)
- **What:** edit the plain-XML save directly while the game is NOT loaded.
- **Best for:** legible, low-linkage nodes — scenario name/summary/parts, pawn `<story>` +
  `<skills>`, faction names, starting research/things.
- **Avoid for:** the map thing-ID reference graph + cell/region/pathing data — fragile,
  dangling-reference risk.
- **Guardrails:** timestamped backup → edit → parse-validate XML → reload-test. Always.

### 2b. Live RimBridge / GABP-MCP
- **What:** talk to **RimBridgeServer** v2.1.0 (pardeike, MIT, packageId
  `brrainz.rimbridgeserver`) to inspect state and invoke the game's own dev/debug/Architect
  actions programmatically.
- **Best for:** anything touching the live map. Architecture makes *main-thread ownership*
  non-negotiable — mutations flow through RimWorld's own main-tick / long-event paths.
- Built-in tools cover enrichment directly: `spawn_thing`, `execute_debug_action`,
  `apply_architect_designator`, `find_random_cell_near` / `flood_fill_cells`, `get_cell(s)_info`,
  plus save/load, screenshots, camera.
- **Extensible** via `RimBridgeServer.Sdk` (`[Tool]` methods in a `BridgeTools` folder).
- **Batchable:** `rimbridge/run_script` (JSON) or `run_lua` run ordered multi-step sequences.
- **Connect:** via the **GABS** launcher, or **Direct mode** (read port+token from the log).
- **Caveat:** requires speaking GABP/MCP as a client — a real programming task.

### 2c. Choosing between them (decision rule — draft)
1. Is the change on the **live map / thing-graph**? → prefer **2b** (engine route).
2. Is the game **not running** and the target a **legible low-linkage node**? → **2a** is fine.
3. Does a **maintained mod or in-game action** already do it? → prefer that over raw edits.
4. When unsure → **2b via a debug action** beats hand-injecting XML.

---

## 3. Architecture — hybrid Python + Cowork-agent-md (decided 2026-08-04, never built)

**RimMaster is a single agent composed of two cooperating layers**, chosen by how much determinism
a task needs:

- **Python layer — the deterministic spine.** `.rws` XML read/edit/validate, backup + rollback, the
  GABP/MCP client transport, defName lookups, schema/precondition checks, post-action verification.
- **Cowork agent-md layer — the agentic judgment.** *What* would make this map more interesting,
  *which* enrichment fits the fiction and pillars, *how* to sequence a set-piece, interpreting
  screenshots/state read-backs.
- **How they cooperate:** the agent-md layer decides *intent*; the Python layer executes through
  **validated, deterministic primitives** and reports structured results back. The Python
  primitives are the guardrail — non-determinism never reaches raw XML or the live thing-graph
  unchecked.

**Component map:** client core (GABP/MCP client) · save-editor module · primitive library (vetted
typed actions, e.g. `place_ruin`, `spawn_thing`, `edit_pawn_skills`, each with preconditions +
validation) · task/intent layer (agent-md) · safety/validation layer (backup, dry-run, post-action
verification, rollback) · knowledge (reuses `mods/concept_defnames.md` as vocabulary).

**Integration patterns never chosen between:**
- **(A) Python-as-MCP-server:** the Python primitives are themselves exposed as MCP tools; Python
  internally holds the GABP client. One surface for the agent, all guardrails server-side.
  *Leading candidate.*
- **(B) Agent-direct + Python sidecar:** agent calls RimBridge MCP tools directly for reads/simple
  spawns, and Python only for save-editing + heavy validated sequences.
