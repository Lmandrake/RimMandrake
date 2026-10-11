# Tools with surprising side effects — RimMandrake

Moved from the project `CLAUDE.md` on 2026-10-11 (weekly cleaning), text unchanged except heading levels. CLAUDE.md keeps a one-line rule and points here. Entries state what IS: delete a line the moment it turns false, never annotate it.

## Machine and research facts

- 🔴 **RimSage answers on the Windows Desktop ONLY — on the Mac laptop it has never
  connected** (MEASURED 2026-09-16: five timed-out session logs 2026-09-02→09-16,
  `mcp.rimsage.com` TCP-dead while general egress is fine, no `mcp__rimsage__*` tool in
  the toolset at all, no cached decompiled tree). So on the laptop an **engine-internals
  question is UNMEASURABLE** — say so rather than reasoning from a doc, and never brief a
  subagent to "use RimSage" there: it costs a whole run to rediscover. Still fine offline
  on either machine: the def dump (`measure`, `refresh.py`) for DEFS, and reading our own
  source. ⚠️ **Several docs assert engine facts that trace to an earlier agent's prose,
  not a decompiler** — `About.xml`'s "vanilla ignition already works on any flammable
  terrain", and `Flood.noPossibleCell` being private with no accessor. Do not launder
  those into measurements.
- ✅ **CANON research DOES work from the Mac, and directly.** Wookieepedia's
  `action=parse&page=<X>&format=json&prop=wikitext` API answers unauthenticated over plain
  `curl` with **no size cap** (MEASURED 2026-09-23: 13 dianoga pages pulled clean). ⇒ Prefer it
  over Fetcher, which **silently TRUNCATES AT 50,000 chars** and has eaten a species' whole
  Biology section. Resolve titles with `action=query&list=search&srsearch=<name>` — a guessed
  exact page title returns MISSING for real subjects constantly, which is not evidence a subject
  is non-canon. ⚠️ `timeout` does not exist on macOS and its failure **resets the shell's cwd**;
  use `curl --max-time`.

## Tools with surprising side effects
- 🔴 **When a new game or world won't start, read the FIRST exception in `Player.log`, not the
  loudest.** `rimworld/start_debug_game_ready` and `load_game_ready` both work (VERIFIED on the
  full mod list, 2026-09-27). They were "broken on any mod list" for a while, but every
  visible symptom was a cascade from one of three bugs in our own content, and none was in the
  engine. (1) A `BiomeWorker.GetScore` called `SurfaceTile.Rivers`, which NREs because the
  biome isn't assigned yet during `WorldGenStep_Terrain`. Terrain gen died on tile 0, and the
  loud `WorldPathGrid`/`WorldGrid.get_Item` out-of-range spam came after it. Read the raw
  `potentialRivers` instead. (2) A drug (non-`None` `drugCategory`) with no
  `CompProperties_Drug` NREs `DrugPolicy.InitializeIfNeeded` inside `Game`'s constructor.
  `DrugBase` does not supply that comp. (3) A creature ThingDef naming a type from an
  inactive mod gets discarded, and the raceless PawnKindDef it leaves behind kills
  `GeneticRim.Core`'s cctor, which stops starting-pawn generation
  (`DEBUG_GAME_READY_WORLDUI_CRASH_1`). Harness: `src/RimMandrake/bridgetools/prove_quicktest_world.py`.
- 🔴 **A `PreToolUse` hook added to `.claude/settings.json` mid-session does not fire** — not for this window's Bash calls and not for its subagents' — until a new session starts; a hook already present at session start does fire for subagents. Test a new hook in a fresh window, never by exercising it in the one that added it.

- 🔴 **A backgrounded `Agent` dies at 600 s of silence and leaves NOTHING on disk.** Three died
  that way 2026-09-17, all mid-read before their first write, all leaving a clean tree — so each
  cost a whole run rather than being truncated; the two that survived streamed output at 385 s
  and 575 s. **Brief every writing subagent to create its output file as a skeleton FIRST and
  fill it section by section** — a file write emits progress and persists partial work. A long
  read-then-write brief is the shape that trips it.
  🔴 **It happened AGAIN 2026-09-23** on a mechanical creature census, and the cheaper lesson is:
  for a **mechanical** census (glob, parse, count, tabulate), writing the script inline costs less
  than briefing an agent to survive the watchdog. Reserve subagents for work that needs judgement.
- ⚠️ **Two `PreToolUse` gates refuse tool calls outright and are easy to trip:**
  the `Agent` tool **refuses without an explicit `model`** (omitting it silently inherits this
  seat's tier, which is how past censuses ran on Opus; named agent types and `fork` are exempt) —
  ladder in `infrastructure/agents/Agent_Policy.md`. And `AskUserQuestion` is validated by
  `validate-question-card.py`: a `header` longer than **12 characters**, or a question not ending
  in `?`, refuses the **whole card**. Count the header before calling.
- 🔑 **A question-card option LABEL the owner clicks is OUR sentence, not his** — record it with
  `--by-card`, never `--owner-said`. Full rule: one field per kind of authority (owner, by question card 2026-10-11): `--owner-said` = his words (typo fixes and joining his own sentences are fine, meaning unchanged) · `--by-card "<question → option>"` = a decision he took by card (the label is our text) · `--per-ruling <item-id|event>` = a standing ruling cited by reference (it stands until he changes it) · `--why "…"` = your own words. No transcript proof runs; nothing checks a quote but its shape.
- ⚠️ **`RM_CreatureBehaviors.csproj` sets `EnableDefaultCompileItems false` and lists every file.** A new
  `.cs` in `Source/` without a `<Compile Include>` line **compiles into nothing, with no error**. Adding a
  file to that assembly is always a two-file change.
- 🔴 **`handoff.py` cannot tell two BENCH windows apart.** It REFUSES on "BRIDGE still held by
  BENCH" even when the hold belongs to the *other* window's live session, because both sign as
  `BENCH`. ⛔ Do not release it to satisfy the gate — that breaks a live game. `--force` records
  it as open, which is the correct exit, and the handoff must name whose hold it was.
- 🔴 **`modcheck run <Mod>` REWRITES the live `ModsConfig.xml`** — it calls `modlist_swap` and
  swaps to MINIMAL. It reads like a query verb and is a Charter expensive-list action. On the
  Mac it dies on the Windows path; on the Desktop it swaps his list unasked (2026-09-17).
