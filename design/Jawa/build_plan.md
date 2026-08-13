# build_plan.md — the execution strategy (how we actually build this)

_Created 2026-08-09. The complement to `first_live_access.md`: that file says **what to prove first**;
this one says **which tier every piece of the design lives in, in what order we build, and what v1 is
allowed to omit.** Owns the **four-tier allocation rule**, the **stamp→save→polish** resolution of the
start-save blocker, and the **M0–M5 milestone ladder**. Consumes `save_authoring_pipeline.md`,
`rimworld_file_lore.md`, `rimbridge.md`, `design/Jawa/worldbuilding/enrichment_agents.md` §4, `required_mods.md` §5._

**Decisions recorded this session (user, 2026-08-09):**
1. **Build order = vertical slice first.** Get an ugly-but-real playable tile as early as possible;
   widen from play, not from design. Explicitly accepts that v1 will not look like the full corpus.
2. **The start save is hand-edited** — but produced by the engine, not hand-written (see §3).
3. **v1 scope includes the LLM voice layer.** Core loop + voice. Heat gauge and authored set-pieces
   are fast-follow, not v1 blockers.

---

## 0. Two findings that reset the baseline

**(a) Phase A is ~70% done, not 0%.** A recorded live-demo run already proves a live
*write* round-trip against the running game: `jump_camera_to_pawn` → `select_pawn` → `set_draft` →
`spawn_thing` (Silver ×500 at 120,113; Steel ×200 at 121,113) → `get_selection_semantics` →
`take_screenshot` → `list_debug_action_children`. That is arbitrary-coordinate placement with visual
confirmation. What remains of Phase A is the **LLM-in-the-loop half** and
the **companion BridgeTools DLL** (needed for anything requiring typed text — `skills/rimbridge/SKILL.md`).

**(b) The "one true blocker" has a proven solvent.** Every ship doc states three times that a large
pre-broken hull can't be expressed as a scenario and can't be hand-injected into the map thing-graph.
But `spawn_thing` at coordinates + `apply_architect_designator` over a rect + `find_random_cell_near`
is exactly *"script ~4,000 engine-mediated placements"*, and `src/RimMandrake/mapsynth/build_sheet_15.py` already
emits the placements. The blocker converts from **"author an impossible save"** to **"write a
stamper"** — and a stamper is **re-runnable**, which is strictly better than the original plan: the
Kolyska's design can change without re-authoring a start save.

---

## 1. The allocation rule

The corpus already carries the right bias (*"whenever an effect can be baked at setup-time, bake it at
setup-time"*, `design/Jawa/worldbuilding/enrichment_agents.md` §4). This adds the second axis that actually resolves the four-way
tension: **does this thing need to vary over the campaign?**

> **Bake what must be TRUE. Script what must be PLACED. Run live only what must CHANGE.**

> ⚠️ **Tier ① no longer includes the sacred-scrap wreck ThingDefs.** They were
> already deferred by `src/RimMandrake/WreckedMachines/V2.md` (entry 7, "sacred
> scrap"), and the owner then cut the surrounding mechanism outright on
> 2026-08-12:
>
> > "For V1, we will just put some mangled metal salvage in for the machines
> > normally on the ship, and role-play that it's the fancy wrecked machines. No
> > new research, just normal research progress using Research Reinvented and
> > VFE factory… Let's stand down from that whole line of reasoning, keep it in
> > the docs, but put it in v2."
>
> **This matters more here than in an ordinary doc**, because this table calls
> Tier ① "the **most irreversible** tier — get it right once, then freeze it."
> An entry listed there reads as *bake this in before worldgen*, so a cut item
> left in the list is an instruction to permanently build something nobody
> wants. **v1 progression rides Research Reinvented + VFE-Factory as they
> already are; no new research is authored.**

| Tier | Share of the design | What belongs here | The real constraint |
|---|---|---|---|
| **① Config + def patches (pre-worldgen)** | **~60%** | The rules of the universe: four-axis terrain schema, Cherry Picker culls, Configurable Techprints gating, biome commonality, Custom difficulty, faction roster, the ideoligion, ~~sacred-scrap wreck ThingDefs~~ (**deferred to v2** — see below), Jawa_Patches (trader buy-filter, SpeakUp lines), JawaIonWeapons | Free at runtime, version-controlled — but the **most irreversible** tier. `required_mods.md` §5 Tier 6 is explicit: AUR Hit Point, Rimesis, and anything Cherry-Picked cannot be changed mid-save. **Get it right once, then freeze it. Never treat as a tuning surface mid-campaign.** |
| **② Save-game editing** | **~5%, ONCE** | The `<game><scenario>` node (name, splash, `PlayerPawnsArriveMethod`, starting research/things, pawnCount) and `GravshipCrew` (the five founders: names, backstory defNames, traits, 12 skills + passions, appearance). Faction flavor renames | **Not periodic.** Periodic save-editing means quitting the game — the flow-killer that stalls ambitious projects — and every extra edit is another roll against the thing-ID graph. Now that the bridge writes live, the reason for periodic editing has evaporated. **One pass at t=0, plus emergency repair.** |
| **③ Per-new-tile-map RimBridge authoring** | **~25% — highest leverage** | The ship stamp; two-tier set-pieces; terrain treasures; §3F hazards; curated ruin stamping; per-biome mineral seeding; arrival threats | Under-rated by the docs as "fragile." It runs **while paused, in a bounded batch, on a fresh map with no history** — the safest moment in the game to write. This is where the campaign gets its texture. |
| **④ Live dynamic during play** | **~10% of writes, 100% of the GM feel** | Imperial Heat, the orbital-detection timer, the dark-tile pause, the nine-god satiation vector, consequence injection, the LLM voice | See §2 — most of it isn't a game write at all. |

## 2. The convergence — one primitive, three uses

**Put all GM state outside the game.** Imperial Heat, the orbital timer, the dark-tile flag, the
satiation vectors: none of it needs to live in the save. The agent keeps the numbers in its own files,
polls the bridge for state, and touches the game **only to fire a consequence**. (This is tier (f) in
`design/Jawa/worldbuilding/enrichment_agents.md` §5 and is already the stated home for agent G's math — generalize it to the whole GM
layer.) It removes the persistence problem, removes save-compat risk, and makes every number
hot-tunable mid-campaign.

Once GM state is external, tiers ②/③/④ collapse onto **one capability**:

> **Engine-mediated placement and incident injection, batched, executed while paused.**

Build it once; use it three ways — **stamping the ship at t=0**, **enriching each new tile map**, and
**firing consequences mid-campaign**. One tooling investment, not three. This is the thing to build
first, and it is what M0/M1 below are.

## 3. The start save — stamp → save → polish

**The reconciliation.** The user wants a hand-edited start save; `rimworld_file_lore.md` Golden Rule 3
forbids hand-writing the map thing-graph; `save_authoring_pipeline.md` already states the rule that
resolves it: *"never author a whole save from scratch; only modify an engine-generated one."*

**Therefore the pipeline is:**

1. **T1 (offline, agent).** Defs/patches finished and in the load order — wreck ThingDefs, xenotype,
   ideoligion, faction reskins, Jawa_Patches. The world is generated already embodying the rules.
2. **T3a (user).** Subscribe → generate world → embark on the chosen tile → save. Minutes.
3. **③ STAMP (agent, via bridge).** Drive `build_sheet_15.py`'s placements into the live map:
   substructure, hull walls (with the deliberate ~40–55% disconnected/RED sections), machine wrecks,
   ring corridor, causeway, airlocks, the dead prong. Paused, batched, `dryRun`-validated.
4. **T3b (user).** Save. **This `.rws` is the start save** — engine-generated, every load ID valid,
   terrain grid written by the engine so the base64/shortHash problem never arises.
5. **② POLISH (agent, offline).** Surgical T2 edits on a backup: scenario node, the five founders,
   faction names. Parse-validate → reload-test.
6. **Iterate 3–5 freely.** The hull is re-stampable, so ship-design changes cost one re-run, not a
   re-authored save.

**What this buys:** the authored save the user asked for, without hand-writing the fragile region,
and with the ship design staying live-editable. **What it costs:** the stamper has to work at scale —
which is exactly what M1 tests, and it is the single highest-information experiment in the project.

---

## 4. The milestone ladder

Each milestone has a hard exit criterion. Do not start the next one until the previous one's criterion
is met.

### M0 — The primitive library
Harvest the working relay (`relay.ps1` + `rimmaster/gabp.py`) into a durable verb set, not ad-hoc spool
batches: `place_thing_at` · `stamp_rect` · `paint_terrain` · `fire_incident` · `send_letter` ·
`read_colony_state` · `read_map_cells` · `screenshot`. Wrap them in the read → propose →
human-approve → write-with-V&V → re-verify loop from `design/Jawa/worldbuilding/enrichment_agents.md` §4. Emit it as a reusable
agent skill, since that's Phase A's actual deliverable.

**Also run the cheap experiment nobody has run yet: does bridge-injected content survive save/reload?**
`design/Jawa/worldbuilding/enrichment_agents.md` §7.1 calls this "the headline unknown" and every Phase-D agent inherits the answer.
Spawn a thing, save, reload, verify. Ten minutes of work that de-risks the entire architecture.

> **Exit:** every verb proven once against the vanilla world; reload-survival answered in writing.

### M1 — The stamper, on ONE pod
Not the whole Kolyska. Take one wing from the §11.3 build sheet and stamp it into a vanilla map.
Answers: does the coordinate mapping hold; can substructure be placed; **is a disconnected/damaged
state actually reachable through the bridge** (deck plan "missing info" item (a)); does it survive
reload; how long does ~500 placements take (the throughput number that decides whether 4,000 is
sane).

> **Exit:** one pod stamped, saved, reloaded, screenshotted. Throughput measured. Go/no-go on §3.

### M2 — Full stack + the live inventory
`first_live_access.md` Phase B, unchanged, except B4 is now just a bridge call against the primitive
library. Load order assembled, red-error pass, real save, one consolidated dump of every
def/item/creature/terrain/faction/xenotype/pawnkind/trait. Build the **shortHash→defName resolver**
first as the offline backstop — it's deterministic and buildable right now.

> **Exit:** the stack loads clean; one catalog file we read through together.

### M3 — The thin slice
One landing, one real tile, full stack. A single per-arrival enrichment script that places **one**
ambient beat, **one** threat, and **one** terrain treasure. Plus the v1 voice layer (§5).
**Then play it for two hours.** This will teach more than another week of design docs.

> **Exit:** a session played end to end, with notes on what was fun and what wasn't.

### M4 — Heat in shadow mode
The external blackboard: Imperial Heat + the orbital-detection timer + the dark-tile pause, as a
Python state machine driven by polled reads. Runs in **shadow mode** for a whole playthrough of the
thin slice — logs what it *would* fire, fires nothing. Then flip injection on a throwaway save, then
for real. This is the instrument-autonomy staging ramp from `first_live_access.md`.

> **Exit:** a shadow log we can read and believe, before anything is live.

### M5 — Widen
Set-pieces to the two-tier cadence · the faction pass · the religious agent cluster (build order
D → G → A+H → B → F → C/E-fragile) · the win paths.

---

## 5. v1 scope

**IN:** the core loop (Jawa crew, broken ship, desert world, a reason to leave every tile) **+ the LLM
voice layer** — RimAI Persona "Cradle-Mind" and/or Jawaese, with the paste-ready prompts already
written in `llm_voice_preauthoring.md`. Note the standing constraint: **JawaVoice and RimDialogue both
own interaction bubbles — run exactly one lane.**

**DEFERRED past first-playable** (each is cheaper to build once M2's catalog exists):
the carbonite trophy mod (the corpus's single largest unavoidable C# commitment) · the divine
satiation engine and agents A–H · the three win paths · the full 15 per-terrain set-pieces · the
ten-faction "Samuel Streamer level" pass · the Imperial Heat gauge (fast-follow at M4, not v1).

---

## 6. Open items this plan does not settle

1. **⚠️ The CQF contradiction — unreconciled in the corpus.** The 2026-08-02 analysis collapsed 6 of 7
   custom-mod jobs into config and concluded the heavy mod isn't worth building. But the 08-05/06 arc
   work adopts **CQF** and assumes authored quest chains, DialogTrees, and milestone-keyed letters for
   the 3-act arc, the three win paths, LifeDawn's voice, and the six ship-relationship beats. That is a
   partial return to the heavy authoring tier through a framework, and a reversal of §4.5's "CQF = not
   a core dependency." **Settle before Phase C.**
2. **Which LLM backend leads** (Ollama local/free/private vs Claude quality — plan is to try both).
3. **The companion BridgeTools DLL.** Confirmed necessary for anything requiring typed text, and
   suspected necessary for per-pawn hediff reads (agent D) and ritual-outcome-tier reads (agent A).
   First C# commitment; small. Test the hediff-read question early in M0 — it determines whether the
   whole religious cluster needs an assembly.
4. **The event-feed gap** (`design/Jawa/worldbuilding/enrichment_agents.md` §7.3, "the most likely place the design meets an unplanned C#
   requirement"): agent G's §8b audit is written against *semantic acts*, but the bridge surface is
   state reads + debug actions + logs, and RimLog is 1.6-dead. Not a v1 problem; will be a real one at
   M5.
5. **Sensible Factions roster/casting** — still the gating decision for the parked per-faction pass.

## 7. Corrections owed to other docs

- `first_live_access.md` — Phase A should record that the write path is already proven (spool
  `04-live-demo`); what remains is the LLM half + the companion DLL.
- `ship_deck_plan.md` §6 — the collected [DECIDE] list still shows **A as open**; §1 resolved it to
  SACRED SCRAP and says so explicitly. §6 is stale.
- `required_mods.md` — **[DECIDE D] resolution (SMELTER first, not the oven) has not been propagated**
  to the "recommended starting state" section or the phase-0 table.
- `STRUCTURE.md` — needs a line for this file under `runtime/`.
