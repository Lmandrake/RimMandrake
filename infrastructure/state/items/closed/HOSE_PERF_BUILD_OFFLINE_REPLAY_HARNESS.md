# HOSE_PERF_BUILD_OFFLINE_REPLAY_HARNESS

## Spec
Recommendation #1 of design/RimMandrake/hose_wire_algorithms_advisory_2026-10-28.md (section 5; GPT q6 design in
D:\ClaudeWork\rimmandrake\research\hose_wire_2026-10-28\q6\answer.md). Stop live-tuning hose/cord/liquid-net performance:
replay a 325x325 map snapshot plus an ordered event stream against the real FlowWorks cores, offline, with work-count,
allocation and invariant gates on every commit, and a Mono timing lane.

Route decision (2026-10-28, BENCH helper; cheapest credible route):
- NOT a headless host that links the FlowWorks DLL against stubbed Verse types. The tick orchestration
  (RM_MapComponent_Hoses, 2.9k lines) reads Find, Map, ThingComp, CompHoseReel, RM_HoseSettings and the def database on every
  line; a stub layer big enough to run it is a second game to maintain, and a stub that drifts measures the stub.
- YES a new net8.0 console project beside SelfTest, `FlowWorks/Source/Replay/RimMandrakeFlowWorks.Replay.csproj`, that
  source-links the SAME Verse-free production files the SelfTest already compiles (CordWorld, CordPlanner, HoseMath,
  HoseWorldPatch/HoseWorldDirty, RM_LiquidNetKernel, RM_LiquidTransfer). Production code is compiled in, never copied, so a
  change to a core changes what the replay measures in the same commit. It is a separate project (not more SelfTest cases)
  because a replay runs thousands of ticks and prints a report; the SelfTest is a pass/fail suite.
- The per-tick schedule of TickBody (the (now + id) % 250 recheck, CorridorHashLive -> CheckReplan -> retract, dirty-cell
  patch with the 16,384 overflow -> whole rebuild, the 250-tick settle with RouteLive before every Move) is mirrored in a
  small Verse-free `ReplayTick` with each mirrored line citing its production line. That mirror is the known drift risk;
  the cure is the follow-up that moves the schedule itself into a Verse-free class both the game and the replay compile
  (which recommendation #2 needs anyway).
- Traces: a versioned text format, first line `RMREPLAY 1` (header, map snapshot rows, reels, tanks, events
  `(tick, phase, seq, kind, char, args)`; Replay/Trace.cs). v1 ships a
  deterministic GENERATOR for the corpus (325x325, 200 reels, 100 tanks; DRY, SETUP, RAIN, COLD, dirty 16383/16384/16385,
  settings-flip-all, aligned-250 rechecks, split/rejoin). Recording live traces needs a recorder inside the game DLL:
  follow-up item, because RM_MapComponent_Hoses is being live-tuned in the tree today.
- Mono lane: no standalone Mono is installed; RimWorld ships MonoBleedingEdge\EmbedRuntime\mono-2.0-bdwgc.dll (the game's own
  Boehm-GC Mono). Route: the replay core also builds as net472, and a tiny host embeds the game's mono DLL to run it, so the
  timing lane measures the game's runtime, not a stand-in. Advisory only; the counters are the gate.

Build:
1. Replay project + trace format + generator + ReplayTick mirror.
2. Counters per tick per system (hose world, recheck, liquid net): elapsed, allocated bytes
   (GC.GetAllocatedBytesForCurrentThread), GC count, work counts (cells patched, whole rebuilds, rechecks, corridor cells
   hashed, CheckReplan calls, retracts, component builds/visits, settle moves). Mean, p99, max, over-bar count; worst ticks
   with their events.
3. Gates (exit code): liquid conserved; no unit moves across a link cut earlier in the same tick; patched world == Full()
   oracle; components == independent union-find; two replays give the identical per-tick fingerprint stream; zero
   steady-state allocation in HoseWorldPatch.Patch; operation-count ceilings from a committed baseline file.
4. Wrapper `src/RimMandrake/Utils/hose_replay.py` (stage, build, run, gate) and `selftest_hose_replay.py` with a red-first
   fault injection proving each gate can fail.
5. Mono timing lane (embedded game Mono) - or a filed follow-up if it does not fit.

## Verify
- `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_hose_replay.py` green on HEAD.
- Each gate has an injected fault that turns it red (shown in the selftest).
- The dirty-16385 scenario reports exactly the overflow whole rebuild the live game shows (instrument sanity: it can see
  the cliff recommendation #3 removes).
- Two runs on one build give byte-identical fingerprint streams.

## Notes
Progress: D:\ClaudeWork\rimmandrake\hose_harness\PROGRESS.md
2026-10-28 11:25 built (steps 1-4): `python3 src/RimMandrake/Utils/hose_replay.py run` stages only the linked sources into
D:\ClaudeWork\rimmandrake\hose_harness\stage (own lock, not the shared FlowWorks selftest lock; `--head` takes production
files from git HEAD), builds in ~15 s and replays all 10 scenarios in ~7 s; all gates green, baseline in Replay/baseline.txt.
selftest_hose_replay.py (25 s): each of the 7 gates goes RED on its injected fault; dirty16385 = 1 overflow + 2 whole
rebuilds, dirty16384 = none; gen -> --trace round trip gives identical fingerprints. First catch: the patch gate found
CellSig omits BlockKind (lesson hose-cellsig-omits-blockkind; latent, unreachable in normal play). Step 5 (Mono lane) and
the live recorder are follow-ups.
