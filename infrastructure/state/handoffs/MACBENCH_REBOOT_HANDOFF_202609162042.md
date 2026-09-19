# MACBENCH_REBOOT_HANDOFF_202609162042 — READ FIRST on wake

First handoff for this seat. Everything below is committed and pushed.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
🔴 **RimSage does not work on this machine, and never has.** `CLAUDE.md` and `CHARTER.md` both name it
as the FIRST instrument for any question about a def, a field, or engine C#. On this Mac it has never
connected: five `mcp-logs-rimsage` session logs (2026-09-02 → 09-16), every one ending
`connection timed out after 30000ms`; `mcp.rimsage.com` resolves to 106.55.255.227 but TCP 443 and 80
are dead while general egress is fine; `rimsage.com` itself also returns HTTP 000; and no
`mcp__rimsage__*` tool appears in the toolset at all, main window or subagent. There is no cached
decompiled tree either.

**So on this machine an engine-internals question is UNMEASURABLE — say so rather than reasoning from a
doc.** What still works offline here: the frozen def dump (`measure`, `refresh.py`) for DEF questions,
and reading our own source. Engine C# needs the Windows Desktop — ILSpy/dnSpy on the real
`Assembly-CSharp.dll`, or reflection over the type through the bridge.

⚠️ **The corollary is the part that actually bites**: several repo docs assert engine facts that trace
to an earlier agent's prose rather than to a decompiler — `About.xml`'s claim that "vanilla ignition
already works on any flammable terrain", and the claim that `Flood`'s `noPossibleCell` is private with
no accessor. Do not launder those into measurements. An owner-installed local RimSage was attempted
this window and **cancelled by him** once the cost was clear (Bun-only runtime, plus a RimWorld install
or a 100–200 MB decompiled-tree copy); do not re-propose it without leading with that cost.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
1. **Pits is now REFUSED, and that is the north-star system's falsification test passing.** He
   authorised validating its checklist ("Do as much of 1, 2, and 3 as you can", recorded on the
   event); the 12 lines bind at hash `145a6b5d9072`, and the visual floor refuses Pits naming all 11
   uncovered must-show ids — measured offline against the real suite, no game. ⚠️ **The registry still
   reads GREEN** from the 2026-09-12 run and will until a real run happens on Windows: a status entry
   is the output of a run, not of a validation, and `block_forged_validation.py` refuses hand-edits.
   Nothing is wrong; do not "fix" that GREEN.

2. 🔴 **`handoff.py` has been mis-seating handoffs on this machine, and I fixed it mid-ritual.**
   `seat()` used to `return "FOUNDRY"` whenever nothing identified the seat. This laptop has no seat
   profile, so `AGENT_SEAT` is unset and `rimflow seat ready` REFUSES — meaning **every handoff ever
   written from this Mac was filed as FOUNDRY's.** My first attempt this window produced a
   `FOUNDRY_REBOOT_HANDOFF_*` listing FOUNDRY's six in-flight items as *my* unfinished work. Deleted
   it, fixed `seat()` to refuse rather than guess (matching `rimflow`'s own stance), re-ran as
   MACBENCH. **He may want to check whether any earlier `FOUNDRY_REBOOT_HANDOFF_*` was actually
   written from the laptop and is therefore mis-attributed.**

3. **The seat name MACBENCH is his, given this window verbatim ("You can call this seat MACBENCH").**
   I used it for this handoff only. It is NOT yet a real seat: there is no
   `infrastructure/agents/MACBENCH.md`, the charter still names only BENCH and FOUNDRY, and
   `rimflow --seat` documents `BENCH|FOUNDRY|OWNER`. **All of this window's ledger events were
   recorded as `BENCH`**, which is why this file's "Closed since" and "Filed and still open" sections
   came out empty — they filter on seat. Corrected by hand below. If MACBENCH should become a real
   third seat with its own charter file and rimflow acceptance, that is a process change needing his
   word.

4. **His context bar was overstating headroom by ~440k, now fixed.** `statusline.py` drew the bar from
   `used_percentage` and the digits from `total_input_tokens` — two different fields. The digits read
   "7k/1.00M · 993k left" while the transcript summed 449,524 (45%, matching the bar). The digits are
   now derived from the percentage so the two cannot disagree. `statusline.py` was CLEAN at
   `c057fb96` and is DIRTY by that edit, correctly — no full-file review was run.

5. **Removed from this machine at his instruction**: `bun` 1.4.2 (Homebrew, 58 MB) and
   `~/checkout/RIMCP` (53 MB, pristine clone, nothing authored). Both were the abandoned RimSage
   install. Nothing references them; `.mcp.json` was never touched, so the Desktop's RimSage config is
   intact.

## What is half-done, and where it stops

<!-- Anything left mid-flight, and the exact next action. An item in `doing` with no line here is a trap for the next seat. -->
**Nothing is mid-edit and nothing is unpushed.** All six subagents reported before wrap. What is queued
rather than half-done:

- **`FLOWWORKS_BUILD_PROGRAM_1`** — the whole liquid programme, ten phases, filed for the Desktop. He
  said he would start the Fable process there. **Next action: Phase 0, which is Desktop-only** — (a)
  can we ship our own `temporary="true"` terrains (decides the engine's recede policy and whether the
  family needs Odyssey), and (b) the exact `Verb` member for the shooting restriction. Read
  `design/RimMandrake/fluid_canals_mod_definition.md` first: 23 sections, 27 rulings from this date.
- **`FluidCanals`' own north star is DRAFT** (13 must-show + 3 cannot-show, in its walk) awaiting his
  validation. Validating it will refuse that mod too, for the same reason Pits is refused. Its
  `### candidate lines` block holds 4 agent-inferred lines that bind nothing until promoted.
- **Seven items re-homed onto the programme, all still `proposed`**:
  `FLUID_SOURCE_STOCK_MODEL_1` (carries a spec correction — ruling 24 deletes `CompFluidReservoir`, so
  do not build stock onto that comp), `MANY_WATERS_DRILL_BUILDINGS_1`, `LIQUID_SINK_DRAINAGE_1`,
  `CANAL_FILL_IN_DISPLACEMENT_1`, `TAR_VISCOUS_SURFACE_ART_1`, `CANYON_FLOOD_ERASES_CANALS_1`,
  `TEMP_TERRAIN_DLC_GATE_1`.
- **Four superseded by the programme**, so nobody spends a cycle on them:
  `FLOOD_ENGINE_CORRECTIONS_1` (its three defects were fixed 2026-09-02, closed at `747b0025`),
  `LIQUID_LOGISTICS_MOD_1` (that mod will never ship), `FLUIDITY_MOD_CONSOLIDATION_1`, and
  `CANAL_CONSTRAINED_SPREAD_1` — 🔑 **that last one's `needs bridge` blocker is MOOT**: it wanted
  vanilla `Flood`'s private cell gate read on the Desktop, but the Flood subclass is being dropped
  entirely. Do not spend a Desktop session on it.
- **Game state is UNKNOWN from here** — `./game` is not executable on this machine (permission denied,
  see the state section below), and the game lives on Windows. Bridge reads FREE since
  2026-09-14T18:25:31Z. Nothing in this window touched the game or the bridge.

⚠️ **The mechanical sections below say 0 closed / 0 filed because they filter on seat MACBENCH while
every event this window was recorded as BENCH.** The true figures: **1 closed** —
`NORTH_STAR_RUNNER_WIRING_1` at `758c6d7f6` — and **11 filed**, of which the four above are already
superseded. The commit list below also interleaves FOUNDRY's concurrent work (Pyrelands, Gizka,
ScorchFruit, Quickgrass, Deep Tribes); mine are the north-star, FlowWorks/ruling, statusline, lessons
and Pits-validation commits.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. Also file these to LESSONS_INBOX.md. -->
All four are in `LESSONS_INBOX.md` except the two marked NEW, which are in this file only because they
were found during the ritual itself.

1. **An instrument that does not exist, briefed to five agents.** I told 3 of 5 fan-out agents to use
   RimSage. Two burned full runs discovering it is unreachable here and correctly returned UNMEASURED;
   one partially substituted repo prose for a decompiler read, which is the failure the rule exists to
   prevent. **Check an instrument answers on THIS machine before briefing a subagent to use it.**
2. **A doc can block work on defects fixed before the doc was written.**
   `liquids_framework_design.md` (2026-09-13) declared "nothing builds on the engine until those
   corrections land", naming three FluidCanals flood defects that were fixed **2026-09-02** and closed
   at `747b0025`. An open item (`FLOOD_ENGINE_CORRECTIONS_1`) was still telling FOUNDRY to re-fix them.
   **Check the code and the ledger before believing a doc's "engine status" section.**
3. **A gauge whose parts come from different fields will eventually lie, in the dangerous direction.**
   `statusline.py`: bar from `used_percentage`, digits from `total_input_tokens`. Derive one from the
   other.
4. **NEW — `handoff.py` silently defaulted the seat to FOUNDRY** whenever it could not tell, so a
   MACBENCH reboot filed a FOUNDRY handoff carrying FOUNDRY's items. Fixed to refuse. The general
   shape: **a fallback to a real, valid-looking value is worse than an error**, because nothing
   downstream can tell it was a guess.
5. **NEW — the ledger conflicts under concurrent appends, and the resolution is a UNION.**
   `events.jsonl` is append-only, so a rebase conflict there is resolved by keeping both sides' lines
   (8579 upstream + my 3 = 8582, verified every line valid JSON), and `queue/*.md` are regenerated with
   `rimflow render`, never hand-merged. `git pull --rebase --autostash` is the safe form here because
   the sync job leaves health artifacts dirty.
6. **`AskUserQuestion` is gated by a hook** that requires every question to end in `?`, every header
   ≤12 characters, and every option to state what it COSTS. It rejected two of my cards. Write them
   that way first.

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (0) — the next seat's queue

Nothing filed in this window.

## Commits

```
c2f6977c7 A v2 dream was mostly delivered by v1, and the walk says it is scheduled for replacement
e09bd85c4 Resolve the docs and queue items today's rulings falsified
01d3bcef1 Pits' north star is VALIDATED — and the falsification test passes offline
2b9f8fbe9 Three lessons from the FlowWorks design session
5a188da03 chore(sync): laptop 2026-09-16T11:39:40-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
0ced17e8a FLOWWORKS_BUILD_PROGRAM_1 — the ticket for the Fable process on the Desktop
7fa541ef3 Rulings 24-27: sources become terrain, rain needs no roof, SUPERDEEP captures regardless of fill, merge before the pit art
76ca92619 Gizka bipedal facing set validated — artpipe state for the quota-delayed drain
43af1ae4a Rulings 20-23: the mod is FlowWorks; terrace farming general and gated; one shooting exception
1e73ce51b DEEP_TRIBES_FIRE_RITE_1: the Deep Tribes come and light it themselves
ea4b748d3 Ruling 19: four depths - plus the two laws and one algorithm that give terraces without a Z-system
f27beebc4 ScorchFruit density: one 1-in-20 roll per burned cell, not per fire-tick
5e7ab077d Ruling 18: Pits IS Canals - depth is the primitive, and it collapses three ladders into one
4d6605cef Canals and Pits compose rather than merge - and it deletes planned work
930d82498 The Fluidity boundary as a principle, plus detonation, sticky-limitless, dry-channel cost, and fill-in advice
b2866cab0 chore(sync): laptop 2026-09-16T09:45:27-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
e45229d67 Gizka canon corrected: bipedal hopper — owner ruling recorded in the entry
9490e2aa8 FLAMEFANG_SNAKE_REBIRTH_1: recommit after a concurrent rebase dropped e63fae1e3
ad449c467 Propagate the Fluidity consolidation into the framework's client map
988599e40 Ruling: one mod called Fluidity, absorbing Many Waters and Liquid Logistics; sluice gates yes; ignition is per-liquid
dd5c2336c Ledger sync: PYRELANDS_SCORCHED_RUINS_1 closed, FIREHAWK_FLIGHT_BEHAVIOR_1 noted blocked-on-art
58a08013f Pyrelands: the biome's fire clock, and the furnace-beast's thermal capacitor
cad170e94 PYRELANDS_SCORCHED_RUINS_1: ruins scorch and burn via BiomeDef.extraGenSteps
f67c8d4b4 Pyrelands SW-canon fidelity check: 6 of 7 pass, iriaz fails the one-horn line
6d452b001 chore(sync): laptop 2026-09-16T09:04:38-07:00 — Transient/codebase_health.html, Transient/codebase_health.json, Transient/codebase_health_artifact.html and 2 more
5af00922c File the Desktop's first task (temp-terrain DLC gate) and the sink item
ee9b32883 Ruling: this mod IS the liquid engine - plus sinks, and it needs a new name
2102e0988 File the canyon-flood-erases-canals collision
80161da41 Three more rulings: three fill tiers, self-drain returns, and burn as a rate on the tier ladder
1688d9a2a Quickgrass reads its growth: sprout, half-grown, tall lush
```

## Game / bridge / tree state at wrap

- <could not run /Users/mandrake/dev/RimMaster/game: [Errno 13] Permission denied: '/Users/mandrake/dev/RimMaster/game'>
- Bridge: FREE    since 2026-09-14T18:25:31Z

Uncommitted (say for each whether it is yours or another seat's):

```
M Transient/codebase_health.html
 M Transient/codebase_health.json
 M Transient/codebase_health_artifact.html
 M infrastructure/dashboards/hub/data/health.json
 M infrastructure/state/codebase_health_last.json
 M src/RimMandrake/Utils/handoff.py
```

