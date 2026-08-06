# rimbridge.md — living context on RimBridgeServer (live game modification)

_Dedicated wisdom file for **RimBridgeServer**, the mod we intend to use to modify a
running RimWorld game live — our route to **Tier 2b live-map enrichment** (improve an
already-landed map on demand, instead of pre-specifying everything in a scenario/mod).
This file grows as we learn. **Discipline:** mark every claim ✅ verified from source /
🔎 reasonable inference / ❓ unknown-pending. Never record a defName, endpoint, or setup
step as fact until confirmed against the actual mod files or a credible source._

**Started:** 2026-08-04. RimWorld **1.6 + Odyssey**. Companion to `concept.md`,
`rimworld_file_lore.md`, and `concept_defnames.md`.

---

## 0. Why this mod (the campaign role)

Our world-delivery model has three tiers (see `rimworld_file_lore.md` §0–2):
- **T1** — author defs/patches up front (scenario, xenotype, factions).
- **T2** — surgical hand-edits of legible, low-linkage save nodes.
- **T2b (this mod's job)** — enrich the *live map after arrival*: inject creatures,
  structures, ruins, loot on demand. The fragile part of a save is the map thing-ID
  reference graph + cell/region/pathing data; hand-editing it is dangerous.
- **T3** — pure in-game (dev mode, Map Designer).

🔎 **Working thesis (to confirm):** RimBridgeServer likely exposes a live bridge/endpoint
into the running game, so mutations go **through the engine's own spawn/gen calls** rather
than raw XML injection into the `.rws`. If true, that sidesteps exactly the dangling-
reference risk `rimworld_file_lore.md` warns about — making it the *safe* enrichment route.
This is inference from the mod's name/class, NOT yet verified against source.

---

## 1. Identity & provenance ✅ (located 2026-08-04; source download pending)
- **Author:** ✅ **pardeike** — Andreas Pardeike, the author of **Harmony** (the universal
  RimWorld patch library) and Zombieland. This is a heavyweight, credible modder, not a
  hobby one-off. Raises confidence in code quality; also signals the mod is *developer/
  automation-grade*, not a casual content tool.
- **GitHub source:** ✅ `https://github.com/pardeike/RimBridgeServer` — repo is public and
  has a **`/1.6` subfolder on `main`** → 1.6 is supported. Docs live in `/docs`
  (incl. `architecture.md`).
- **Companion repo:** ✅ `pardeike/RimBridgeServer.Annotations` — the shared tool-annotation
  contract between the bridge host and external mods/plugins whose tools it discovers.
- **Workshop ID:** ✅ `3727949765`
- **packageId:** ✅ `brrainz.rimbridgeserver`
- **modVersion:** ✅ `2.1.0`  ·  **supportedVersions:** ✅ `1.6` (single `1.6/Assemblies`)
- **License:** ✅ **MIT** — we can freely build on / fork / distribute derivative tooling.
- **Companion launcher:** ✅ **GABS** (`github.com/pardeike/GABS`) — recommended way to start
  RimWorld, discover the live tool surface, and connect a client without hand-managing
  ports/tokens. Exposes `games.start` / `games.connect` / `games.call_tool`.
- **Source in hand:** ✅ full repo extracted (MIT, code+docs, assets stripped) to
  `~/GDrive/Personal/Rimworld/mod_sources/RimBridgeServer-main/`; Annotations repo alongside.
  Key docs local: `docs/tool-reference.md` (1087 lines, full per-tool schema),
  `docs/architecture.md`, `docs/lua-frontend-design.md`, `docs/semantic-state-design.md`.
- Fetcher: `2026-08-04_rimbridgeserver_1p6.txt` (locate) + `_source.txt` (download+docs) both
  DELIVERED; `2026-08-04_liveedit_companions.txt` (companion mods) DELIVERED. All complete.

## 1a. What this mod actually is (verified from source 2026-08-04) ✅
RimBridgeServer is **NOT a content/map-editor mod** — it's a **live automation bridge**: it
runs a **GABP host (an MCP server) inside a running RimWorld** so an external program/agent
can inspect and drive the real game. The intended driver is a *program on the outside*, not a
human clicking. It stays "as close as possible to RimWorld's own logical seams instead of
reimplementing gameplay logic outside the game" (architecture.md).
- ✅ **Transport = GABP (Game Agent Bridge Protocol)**, via the `Lib.GAB` package. Two connect
  modes: **GABS** (launcher discovers the surface + manages port/token) or **Direct mode**
  (start RimWorld, read `[RimBridge] GABP server running standalone on port 5174` + a bridge
  token from the log, connect client to `127.0.0.1:port` with that token).
- ✅ **It IS rich enough for enrichment.** The
  tool surface (full schema in `mod_sources/.../docs/tool-reference.md`) includes real
  content/map mutation tools, not just QA:
  - `rimworld/spawn_thing` (defName + x/z + stackCount) — direct thing spawn.
  - `rimworld/execute_debug_action` — runs ANY RimWorld debug-action leaf by stable path,
    incl. cell- or thing-targeted "ToolMap" actions. `search_debug_actions` enumerates the
    whole dev-mode tree → this is the entire vanilla+modded dev spawn menu, programmatically.
  - `rimworld/apply_architect_designator` — place any Architect designator over a cell/rect,
    with `dryRun` validation. (`list_architect_categories`/`_designators` to discover ids.)
  - `rimworld/find_random_cell_near` / `flood_fill_cells` — engine cell-search with walkable/
    standable/unfogged/reachable footprint criteria → pick *valid* placement cells safely.
  - `get_cell_info` / `get_cells_info` (≤1024 cells) — read map cells (things/zones/designations).
  - `set_god_mode`, save/load, screenshots, camera framing, `spawn`/letters/alerts inspection.
- ✅ **Engine-route confirmed = the safety win is real.** architecture.md makes **main-thread
  ownership** a *non-negotiable*: every read/write touching game/map/selection/designators/
  save-load/input flows through one execution abstraction with main-thread affinity, frame-
  bounding, and long-event awareness (uses `LongEventHandler.QueueLongEvent` etc.). So
  mutations happen through RimWorld's own main-tick code paths, NOT raw `.rws` thing-graph
  injection. This is exactly what `rimworld_file_lore.md` says to prefer.
- ✅ **Extensible:** third-party mods can add their own bridge tools via the
  `RimBridgeServer.Sdk` NuGet package + `[Tool]`-annotated methods dropped in `BridgeTools`
  folders — so we can author **custom RimMaster primitives as first-class bridge tools** if the
  built-ins aren't enough. (Companion tools can even drive game time: `ctx.Game.RunForTicksAsync`.)
- ✅ **Scripting layer:** `rimbridge/run_script` (JSON, ordered capability calls + control flow)
  and `rimbridge/run_lua` (a *lowered Lua subset*, not full Lua — `local` bindings, `rb.call`/
  `rb.poll`, static indexes only). Get the machine-readable grammar from `get_script_reference`
  / `get_lua_reference` before authoring. Lets us batch a multi-step enrichment in one call.
- ✅ **Discoverability:** `rimbridge/list_capabilities` / `list_operations` / `list_logs` +
  operation journal → an agent discovers the live surface at runtime instead of hardcoding it.
- ⚠️ **Practical caveat (still true):** driving it well means writing/using an external
  **GABP/MCP client** — a programming task. But the surface is well-documented and MIT, and it
  matches Mandrake's build-tools style. See RimMaster.md §3 for our hybrid client design.

## 2a. Companion mods for live enrichment ✅ (searched 2026-08-04; verified Workshop IDs)
The bridge can already invoke the *whole dev-mode + Architect surface*, so companions are
**optional force-multipliers**, not required. Candidates confirmed to exist (re-verify 1.6 in
RimSort before subscribing; a few IDs came from 429-prone pages):
- **New Blueprint** — WS `3534166729` ✅. Uses RimWorld **1.6's new Prefab system** to capture
  both terrain + buildings in a selected area into shareable blueprints. Most 1.6-native option
  for stamping pre-designed ruins/structures. **Top pick for structure enrichment.**
- **Universal Blueprints** — WS `3540066516` ✅. Ships 101 ready-made categorized blueprints
  with tech/dependency/material info. Good as a *content library* to stamp from.
- **Blueprints (Fluffy)** — WS `708455313`, source `github.com/fluffy-mods/Blueprints` ✅.
  The classic copy/paste-build mod; export/import blueprints as files. Long-standing; confirm 1.6.
- **Map Designer** — WS `2111424996`, `github.com/Zylleon/MapDesigner` ✅. Terrain/biome/stone
  shaping (mostly map-gen time, not live). Already on our radar.
- **Character Editor** — ✅ exists (Nexus + Workshop). Deep pawn spawn/edit; heavier than we
  need if `spawn_thing`/debug-actions cover pawns. Evaluate only if we need rich pawn authoring.
- **Fluxilis Debug Actions** — WS `2898787033` ✅. Adds extra debug-action leaves; since the
  bridge can call any debug action by path, any such mod *automatically* widens RimMaster's reach.
- Pillar note (§6): all are *authoring tools* — fine to use, must not become in-fiction player power.

## 2b. Debug-action mod sweep — verdicts (2026-08-04) ✅ searched / ⚠️ source re-pull pending
**Key reframe (important):** the bridge's `execute_debug_action` already exposes the *entire*
vanilla **+ modded** debug-action tree by stable path (`search_debug_actions` enumerates it). So
a mod extends RimMaster's *programmatic* reach ONLY if it **adds new action leaves**. A mod that
merely improves the debug *UI* (searchable grids, dark theme, pinning) adds **zero** new callable
paths — it helps a human clicking, not the agent. Judge every "dev tools" mod by that test.
- **Modern Dev Tools** — WS `3771602203`, **MIT, open source** (author states full source on
  GitHub). ✅ It *reuses the vanilla action tree* → **adds no new callable paths → no benefit to
  the agent's reach.** Value is (a) a much nicer *human* dev UI for manual T3 work, and (b) its
  MIT source is worth STUDYing to learn how the debug-action tree/paths are structured (the exact
  paths RimMaster will pass to `execute_debug_action`). Verdict: **optional human QoL + study
  reference, NOT a reach-extender.** Source re-pull filed (`2026-08-04_debug_tools_source_repull`).
- **Fluxilis Debug Actions** — WS `2898787033`. ✅ Genuinely *adds* a few leaves (modify HP of
  non-pawn things on a clicked cell, quality-affects-HP). **Marginal** reach gain, on-theme for
  salvage/wear scenarios. Adopt only if that specific action is wanted. (First Fetcher FILE
  grabbed a GitHub *search page* not a zip — real source re-pull pending.)
- **alextd/RimWorld-TDBug** — GitHub `alextd/RimWorld-TDBug` (not on Steam) ✅. Modder-oriented
  dev/debug enhancements; niche, some features now vanilla. Low priority; source re-pull filed.
- **Character Editor** — see §2a; deep pawn authoring, heavier than `spawn_thing`/debug-actions
  need. Only if rich pawn authoring is required.
- **Net verdict:** RimBridgeServer's built-in surface + a couple of *content*-adding leaves
  (Fluxilis) is sufficient; no debug-*UI* mod materially extends the agent. The real reach
  extenders are the **blueprint mods** (§2a: New Blueprint 3534166729) that give the bridge
  pre-designed structures to stamp, not the dev-menu mods.

### 2c. World-map editing mods — a WORLD-tile analog of the same test (2026-08-06)
World-authoring mods (adopted in `required_mods.md` §"World-Map Authoring & Setup Tools") raise
the same "adds-new-leaves?" question, but at the **world-tile** layer. RimWorld has a vanilla
`DebugActionType.ToolWorld` (per RimWorld Wiki: "mouse targeter that calls the method on each
world-tile click, WorldMap only") — the world analog of the `ToolMap` actions the bridge already
calls. So a world-edit mod extends the bridge's reach ONLY if it registers `ToolWorld`
DebugActions; a bespoke-window/gizmo editor does not.
- **Tile Biome Editor** (`boringbiome`, source read 2026-08-06): edits via `Command_Action`
  **gizmos** on `Tile.GetGizmos()` — GUI-only, **NOT** bridge-callable. (Not adopted anyway.)
- **WorldEdit 2.0** (WS 3590928058): bespoke hotkey/window editor → **inference: no callable
  paths**, human-only setup/repair tool. Fine — that's its role.
- **Modify Tiles at Game Start** (WS 3667490447, author Halicade): ✅ CONFIRMED (source pull
  `2026-08-06_mapdesigner_modifytiles_source`, Workshop description = authoritative, no public
  repo) it adds real **dev-mode commands** — "Set Biome (mod)", "Set Landmark (mod)", and a
  landmark-remove — that act on a **selected world tile** (WorldMap, per-tile). That IS the
  `ToolWorld` pattern, so it is **the one world-edit mod that plausibly registers
  bridge-enumerable debug-action leaves** (`search_debug_actions` would list them). 🔎 The exact
  registration mechanism (`[DebugAction]`/`ToolWorld` attribute vs a custom dev button) is
  *inference* — raw C# not obtained (Workshop-only, no repo). 1.6-tagged, no hard deps.
- **Map Designer** (WS 2111424996, Zylleon): ✅ RESOLVED = **map-generation settings GUI**, NOT a
  debug-action tool. Its own Workshop text describes Terrain-tab biome/stone/river shaping that
  overrides other stone mods *at gen time*; four targeted searches (incl. "MapDesigner DebugAction
  ToolWorld") returned **zero** debug-action hits. GitHub repo is real (active `1.6` folder, 100%
  C#) but adds **no new callable debug-action paths** → not a bridge reach-extender. Value is
  human setup-time map shaping/repair (its assigned role), not agent reach.
- **Reframe (matches §2b + the mods' own docs):** world-tile edits mostly apply **pre-map-gen** and
  persist in the world save. The bridge operates on the **already-loaded** map. So even a
  bridge-callable "set biome" wouldn't rewrite the current map — it'd affect only future-generated
  tiles. World authoring is therefore a **human, setup-time** activity; the bridge's live role stays
  the loaded-map enrichment (blueprint stamping), not planet editing.

## 2. Dependencies ❓ (pending)
- ❓ Harmony (`brrainz.harmony`) — near-universal for C# mods; confirm, don't assume.
- ❓ Companion client / external library the server talks to — unknown whether one exists.
- (Fill in each real dependency with name + Workshop ID + source once known.)

## 3. Architecture — how it actually works ❓ (pending source read)
_To fill in after extracting the source. Questions to answer:_
- What transport? (socket / HTTP / named pipe / file-watch?)
- What's the command/message schema? What actions are exposed?
- Does it spawn via engine calls (`GenSpawn`, thing/pawn generators) or raw state writes? ← key safety question
- Threading: does it act on the main game tick or off-thread? (off-thread map mutation is a classic corruption source)
- Auth/binding: does the server bind localhost-only, or open a network port? (security)
- Persistence: do live-injected things survive save/reload cleanly?

## 4. Setup & operation — how to use it well ❓ (pending Reddit sweep + testing)
_Practitioner wisdom goes here as it accumulates. Structure:_
- **Install/config:** …
- **Starting the bridge / connecting a client:** …
- **Known-good live-modification patterns:** …
- **Performance notes:** …

## 5. Gotchas / failure modes ⚠️ (grow this aggressively)
_Every "this breaks saves / TPS / references" lesson lands here. Empty for now — the
whole point of Tier 2b caution is that live map mutation is the fragile frontier._

## 6. Fit with our campaign & pillars
- Anti-exponential: a live-editor is an **authoring tool**, not an in-fiction power — using
  it to place content is fine; it must not become a way for the colony to self-upgrade past
  the gravship/VFE-Factory progression trees. Use it to enrich the *world*, not to hand the
  *player* scalable capability.
- §19.5 (no arms race): any weapon/loot injected live must still pass the same balance bar.
- Containment items (e.g. lightsabers) stay quest-earned — do NOT inject as generic loot.

## 7. Open questions / next steps
- ❓ Await Fetcher delivery of 1.6 source + dep list + Reddit findings.
- ❓ Then: extract to `mod_sources/`, read About.xml + C#, fill §1–3 with ✅ facts.
- ❓ Decide raw-injection vs engine-route (§3 threading/spawn answer decides this).
- ❓ Trial a tiny live injection on a backup save; record result in §4/§5.
