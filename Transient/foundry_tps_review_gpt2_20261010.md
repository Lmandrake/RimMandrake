**Build 2 is not ready to trust.** It contains defects that hide recovered incidents, replay committed records, misplace long-tick measurements, and generate invalid profiler durations under ordinary Harmony skip behavior. Its external observer does not persist two of the three advertised findings. The outstanding work is larger than deployment and the stated C3/C4 experiments. (`JawaBenchTpsSampler.cs::Incident`; `JawaBenchTpsWriter.cs::WriteBatch/Loop`; `JawaBenchTpsMath.cs::FrameAccumulator.Post`; `JawaBenchTpsProfiler.cs::TickPre/TickPost`; `tps_record.py::observe`; `belt_watchdog.py::gather` diff.)

I reviewed the implementation and tests before using the earlier reports as a comparison. Below, **bug** means behavior established by the supplied code; **design gap** means missing information or guarantees; **conditional risk** means the installed engine, Harmony configuration, or mod behavior must be checked. File references use the supplied basenames; I did not open the files from disk or run their selftests.

**A. Independent implementation findings**

1. **BUG — Recovered incidents lose their `incident` discriminator.**

   `JawaBenchTpsSampler.cs::Incident` calls `W.Enqueue("incident", ...)`, but includes `JawaBenchTpsMath.cs::GapFields`, which supplies another `"kind":"stall"` or `"kind":"longevent"`. The resulting row contains duplicate keys:

   ```json
   {"kind":"incident","type":"stall","kind":"stall","gapS":40}
   ```

   Python retains the last duplicate key. Consequently, `tps_record.py::summarise`, `timeline`, `sessions`, and `render_row` do not recognize this as an incident: incident counts omit it and the dedicated `INCIDENT` rendering is bypassed. The row remains on disk but becomes an unfamiliar event kind. The selftest constructs an incident manually with the correct discriminator and never tests this production composition. (`selftest_tps_record.py::reader_checks`.) Python documents this duplicate-key behavior in its [JSON decoder documentation](https://docs.python.org/3/library/json.html).

   `Incident` also emits duplicate `mult` fields: `GapFields` supplies the newly observed multiplier; `JawaBenchTpsWatchdog.cs::ContextFields` supplies cached `LastMult`. `TmuPrefix` updates that cache **after** calling `Incident`, so the old multiplier wins precisely when a transition matters.

   **Change:** reserve envelope keys, use `gapKind`, and distinguish `multBefore`/`multAfter`; reject duplicate keys in integration tests and the reader.

2. **BUG — Sample duration, simulation timing, and timestamp use different boundaries.**

   `JawaBenchTpsMath.cs::FrameAccumulator.Pre` accumulates prefix-to-prefix intervals. `Post` then includes the **current** invocation’s simulation duration and completed ticks. `JawaBenchTpsSampler.cs::Emit` receives its UTC timestamp from `JawaBenchTpsWriter.cs::Enqueue`, after that invocation completes.

   Consider a frame whose prefix closes five seconds of accumulated intervals, followed by a 40-second `DoSingleTick`:

   - `dReal` is approximately five seconds.
   - `simMs` includes approximately 40 seconds.
   - `simShare` can exceed eight.
   - The sample’s UTC is approximately 40 seconds after the accumulator’s interval end.
   - The next prefix records the 40-second gap, although the expensive tick and its profiler totals were already emitted in the preceding window.

   These are not merely rounding errors. `tps_record.py::timeline` reconstructs the interval as `utc - dReal .. utc`, placing the preceding measurement at the wrong historical time. A recovered stall can therefore appear as a short `run` window with enormous simulation share followed by a long `stall` window with little simulation cost. (`FrameAccumulator.Post`; `TmuPostfix`; `Emit`; `timeline`.)

   **Change:** persist explicit measurement start/end monotonic timestamps and corresponding wall-clock anchors, separately from enqueue time. Define how invocation timings crossing a measurement boundary are assigned. Add a trace with a long **current invocation**, rather than only a long interval before a cheap invocation.

3. **BUG — An unexplained gap with a state transition is removed from expected ticks.**

   In `JawaBenchTpsMath.cs::FrameAccumulator.Pre`, `gap && transition` adds `r` to `AmbigS` and skips both the paused and running branches. That time contributes no `RunS` or `Expected`.

   A 90-second unexplained gap followed by a speed change can therefore retain an approximately healthy ratio from the preceding running interval. It still produces a stall classification, but the claim “unexplained gaps are never subtracted” is false. Ambiguity also has inconsistent accounting: gap ambiguity replaces a duration category, whereas mid-loop ambiguity overlays running duration. (`FrameAccumulator.Pre/Post`; `Window.State`; `tps_record.md`, “One window”.)

   **Change:** retain unexplained elapsed time and explicitly represent uncertain expected ticks, preferably with an expected range or unavailable normalization. Do not manufacture a precise denominator by omitting the uncertain interval.

4. **DESIGN GAP — Save timing is not itself connected to explained time.**

   `JawaBenchTpsSampler.cs::SavePostfix` updates `_saveTotal` and writes a save event; it never updates `_explained`. Exclusion depends on the save also being covered by `LongEventsUpdate` or waiting-frame accounting. A mod calling `SaveGame` synchronously outside that coverage will be labeled unexplained despite the save hook identifying it. Conversely, `AnyEventNowOrWaiting` causes the entire `LongEventsUpdate` invocation to be timed without establishing which work consumed that time. (`SavePrefix/SavePostfix`; `LePrefix/LePostfix`; `RootPrefix/RootPostfix`.)

   The supplied files do not establish the precise base/derived `Root.Update`, long-event, and tick-update call order. That ordering determines whether `_leDur` reaches `_explained` before the relevant `Acc.Pre`, and whether elapsed scopes are attributed once. The selftest supplies `explained=12` directly; it tests none of this runtime accounting. (`selftest_tps_record.py::traces`.)

   **Change:** measure identified scopes as intervals and calculate their union against the observation interval. Explicitly test direct saves, nested saves, synchronous events, asynchronous waiting, and event completion ordering.

5. **BUG — Profiler prefixes can be skipped while their postfixes still execute.**

   `JawaBenchTpsProfiler.cs::TickPre`, `TlPre`, and the other timer prefixes have `out __state`. If an earlier Harmony prefix returns false, these prefixes can be skipped because they have side effects; postfixes still execute. The default `__state` is zero, and `End` then measures `Stopwatch.GetTimestamp() - 0`, producing an enormous fabricated duration.

   `TickPost` can additionally pass that duration to `NoteWorst` with a stale `TickBase`. This is a concrete compatibility path, not a hypothetical timer precision issue. Harmony documents [prefix skipping](https://harmony.pardeike.net/v2/articles/patching-prefix.html).

   **Change:** use an invocation state containing an explicit “started” flag, check it in every postfix, and record original-skipped calls separately using `__runOriginal` where supported.

6. **BUG / SAFETY — The claimed nonthrowing patch boundary does not cover the profiler.**

   `JawaBenchTpsSampler.cs` catches exceptions in `TmuPrefix`, `TmuPostfix`, and the main root bodies. `JawaBenchTpsProfiler.cs::TlCat`, `Begin`, `End`, `TickPre`, `TickPost`, and `NoteWorst` have no containment. An instrumentation exception can escape into tick execution. `LePrefix` also accesses `LongEventHandler.AnyEventNowOrWaiting` outside a protective boundary; `SavePrefix/SavePostfix` and `LoadPrefix` are unguarded.

   Additionally, original or other-patch exceptions skip ordinary postfix cleanup. Timers, `_saveStart`, `_leStart`, and phase nesting are not closed reliably. Harmony provides finalizers for exception-safe observation and cleanup. [Harmony finalizer documentation](https://harmony.pardeike.net/v2/articles/patching-finalizer.html).

   **Change:** ensure telemetry failures disable telemetry without replacing game exceptions. Cleanup must preserve the original exception, not suppress it to keep the recorder alive.

7. **CONDITIONAL RISK — Patch ordering does not guarantee observation of effective engine state.**

   `JawaBenchTpsSampler.cs::Install` and `JawaBenchTpsProfiler.cs::Patch` specify no priorities or before/after relationships. Another prefix can change speed, pause state, arguments, or execution after this sampler observes them. Another postfix can perform expensive work outside this profiler’s measured scope. The actual effective `CurTimePerTick` can also change inside the loop; only the endpoint difference is recorded. (`TmuPrefix/TmuPostfix`; `FrameAccumulator.Post`.)

   On the owner’s load, inventory the actual prefixes/postfixes/transpilers on every target and define the observation boundary. “Before tick work” is insufficient unless the position relative to other patches is known.

8. **BUG — Installation failure leaves partial instrumentation installed.**

   `JawaBenchTpsSampler.cs::Install` patches methods sequentially and starts the writer before completing installation. An exception leaves earlier patches and the writer running. `_attempted` prevents another attempt; no rollback occurs.

   `JawaBenchTpsProfiler.cs::Install` has the same problem: previously installed stages remain active if a later patch throws, while `Installed` remains false. `Emit` then never drains their accumulated totals. Missing targets can instead yield `Installed=true` with incomplete coverage. (`Install`; `Patch`; `Emit`.)

   **Change:** validate targets first, publish per-target installation status, and roll back this telemetry’s patches on installation failure. Distinguish complete, partial, disabled, and failed instrumentation.

9. **BUG — Attribution is not reset when the game changes.**

   `JawaBenchTpsSampler.cs::RootPrefix` resets `Acc` and `Streak`, but never resets `JawaBenchTpsProfiler` counters or worst ticks. A short game that ends before emitting its next sample contributes timing to the next loaded game’s first sample.

   The first accumulator frame also establishes `_tick0` after ticking and excludes that frame’s simulation duration, while the profiler has already recorded its ticks. The first attribution window therefore includes work absent from its tick-count baseline. (`RootPrefix`; `FrameAccumulator.Post`; `TakeWindowFields`.)

   **Change:** reset attribution at the same game/window boundaries and label attribution intervals explicitly.

10. **CONDITIONAL RISK — Most invocation state assumes no reentrancy and one calling thread.**

    `JawaBenchTpsSampler.cs` uses global `_tmuStart`, `_ticksPre`, `_gcAtPre`, `_saveStart`, and `_leStart`. `JawaBenchTpsProfiler.cs` uses one global `TickBase` and shared mutable arrays. `JawaBenchTpsWatchdog.cs` uses one shared phase stack.

    Recursive calls overwrite outer state. Calls from worker threads race counters and phase state. Calls on a noncurrent `TickManager` are not rejected by comparing `__instance` with `_game.tickManager`. (`TmuPrefix/TmuPostfix`; `SavePrefix/SavePostfix`; `TickPre`; `Begin/End`.)

    **Change:** use per-invocation state, verify the game-thread ID, and explicitly mark or reject unsupported concurrent/reentrant execution.

11. **BUG — Worst-tick identifiers do not identify the measured tick.**

    `JawaBenchTpsProfiler.cs::NoteWorst` records `WD.LastTicksGame`, which `TmuPrefix` sets once before the frame’s tick loop. All expensive ticks in that frame can receive the same pre-loop tick number. `TickPost` reads a second duration after `End`, so the worst-tick duration is also different from the duration accumulated in `Total[CTick]`.

    The profiler’s header promises worst-tick breakdowns, but `NoteWorst` saves only `{tg, ms, top}`. The stage deltas used to derive `top` are discarded.

    **Change:** capture the actual tick identity and retain bounded numerical breakdowns.

12. **DESIGN GAP — Exclusive attribution assumes a call tree that is not validated.**

    `JawaBenchTpsProfiler.cs::Exclusive` assumes tick lists, world stages, map stages, and game components are nonoverlapping children of `DoSingleTick`, with map components nested only inside `MapPostTick`.

    Modded calls outside those scopes, recursive ticks, skipped prefixes, or overlapping instrumentation invalidate subtraction. Negative residuals are silently clamped to zero; child totals exceeding parent totals produce no validity flag. `Top` can consequently report a plausible percentage from invalid accounting. (`Exclusive`; `Top`; `TakeWindowFields`.)

    **Change:** track scope membership and invalid/incomplete measurements. Report unattributed or inconsistent time explicitly.

13. **BUG — Writer retry is not commit-aware.**

    `JawaBenchTpsWriter.cs::WriteBatch` can successfully append one chunk or segment and then fail later. `Loop` retries the **entire batch**, replaying the already committed prefix.

    A partial append can also leave a torn tail. The retry appends complete rows after that tail, potentially joining a partial JSON object to another object. `_bytes` is updated only after successful completion, so it may cease to match actual file length.

    `tps_record.py::read_record` neither deduplicates `(session, seq)` nor detects conflicting duplicates. Replayed samples inflate counts and can satisfy sustained-warning checks. (`WriteBatch`; `Loop`; `read_record`; `sustained_from_rows`.)

    **Change:** maintain an acknowledged cursor, repair/quarantine partial tails, reconcile file length after failures, and make replay explicitly detectable and idempotent.

14. **BUG — The advertised queue bound excludes in-flight records.**

    `JawaBenchTpsWriter.cs::Enqueue` checks only `Pending.Count + Retry.Count`. `Loop` removes a batch from those structures before writing it. Another full queue can accumulate while a full batch is in flight: the total outstanding count can approach twice `QueueCapacity`.

    `QueueDepth` and `HealthFields` hide `_inFlight`. The failure path removes records from the **front** of the failed batch, dropping the oldest uncommitted evidence, despite its “oldest first” retry comment. (`Enqueue`; `Loop`; `QueueDepth`; `HealthFields`.)

    **Change:** bound queued plus in-flight bytes/records, document the drop policy, and expose dropped sequence ranges and outstanding work.

15. **DESIGN GAP — Critical records have no protection against sample traffic.**

    Session, error, shutdown, silence, incident, and sample rows all compete for the same capacity in `JawaBenchTpsWriter.cs::Enqueue`. An error or silence record can be dropped exactly when storage trouble makes it most useful. Exceptions inside `Enqueue` return `-1` without incrementing `Dropped`.

    `JawaBenchTpsSampler.cs::Marker` can therefore write a Player.log marker containing `seq -1`; writer health describes the state before the sample enqueue, and the in-memory ring can contain samples absent from disk. (`Enqueue`; `Marker`; `Emit`.)

    **Change:** reserve bounded capacity for lifecycle/incident/error records and make memory-versus-disk coverage explicit.

16. **DESIGN GAP — “Never blocks the game” is too strong.**

    `JawaBenchTpsWriter.cs::Enqueue` waits for `Q`. The writer holds that lock while copying retry records and draining potentially thousands of pending strings. Every enqueue formats its envelope under the same lock.

    `JawaBenchTpsSampler.cs::Install` performs directory creation, settings I/O, and `W.Start`; `Start` invokes directory enumeration and retention synchronously. `OnQuit` performs a synchronous full Player.log copy outside its drain timeouts. (`Enqueue`; `Loop`; `Start`; `RunRetention`; `OnQuit`; `ArchiveLogNow`.)

    **Change:** measure lock latency, shorten critical sections, and distinguish steady-state nonblocking disk access from startup/shutdown work. A shutdown log copy has no supplied time or size bound.

17. **BUG / DESIGN GAP — Durability and shutdown claims exceed implementation guarantees.**

    A process kill can interrupt an active `WriteBatch`, not merely discard queued rows. Closing a batch does not guarantee its last row was committed if the process dies before closure. A stalled disk or starved writer makes the claimed “normally under a second” loss bound unmeasured. (`JawaBenchTpsWriter.cs::WriteBatch`; `tps_record.md`, “Durability”.)

    `JawaBenchTpsSampler.cs::OnQuit` writes `shutdown` **before** checking whether either drain succeeds. It ignores both return values, does not stop producer threads, and does not emit a completion acknowledgment. A durable shutdown-intent row can therefore coexist with undrained data or an incomplete archive. `tps_record.py::observe` nevertheless treats any shutdown row as evidence of a clean end.

    `Drain` uses UTC for timeout arithmetic, so a clock adjustment can alter the intended bound. The `ProcessExit` handler can invoke `OnQuit` outside the game thread, where it accesses a Unity API. (`Drain`; `OnQuit`; `Install`.)

    **Change:** separate shutdown intent/completion, use monotonic deadlines, cache Unity-derived paths, and document queued **and in-flight** abrupt-exit loss.

18. **BUG / DESIGN GAP — Retention is neither a seven-day guarantee nor a hard directory cap.**

    `JawaBenchTpsMath.cs::PlanRetention` deletes younger files whenever total bytes exceed the cap. Thus “at least seven days” is conditional on available capacity.

    `JawaBenchTpsWriter.cs::Prune` protects every filename containing the current session, including every closed segment. One long-running session can exceed the cap indefinitely. Conversely, another active RimWorld instance has a different session ID and receives no protection; retention can delete its live or retained files. Delete sharing makes such interference more feasible. (`PlanRetention`; `Prune`; `WriteBatch`.)

    `observer.jsonl` is excluded from retention entirely. Manifests, heartbeats, and segments are pruned independently, so retained measurements can lose their identifying metadata. The approximately 300-byte sample estimate ignores the emitted window/context/attribution fields. (`RunRetention`; `WindowFields`; `TakeWindowFields`; `tps_record.md`, “Where it lives”.)

    **Change:** define the actual guarantee, protect all active sessions through leases, retain closed segments under a coherent policy, and prune session bundles with their necessary metadata.

19. **BUG / DESIGN GAP — Player.log preservation still has a relaunch-loss window.**

    `JawaBenchTpsSampler.cs::ArchivePrevLog` runs only after companion registration, then delegates copying to a thread-pool job. If registration follows the lengthy play-data load described in `low_tps_2026-10-10.md`, a crash during that load can leave the previous incident unarchived before another launch rotates logs again.

    `Player-prev_<mtime>.log` has no session ID and only second-resolution naming. `JawaBenchTpsWriter.cs::ArchiveLogNow` treats equal length as equality and otherwise overwrites the destination. Two archives with different content can therefore collide or be incorrectly deduplicated. Concurrent retention and archive operations have no common coordination. (`ArchivePrevLog`; `ArchiveLog`; `ArchiveLogNow`; incident note, “Load times”.)

    **Change:** preserve logs before launching/rotating them, use unique archive identities or content hashes, and persist the archive’s source-session association.

20. **BUG — Heartbeat files do not contain the advertised last-main-heartbeat timestamp.**

    `JawaBenchTpsWatchdog.cs::WriteHeartbeat` stores `utc` and `mono` for the **watchdog write**. `_beatTicks` is not persisted directly. `tps_record.py::observe` labels that `utc` as `lastHeartbeatUtc`, conflating watchdog progress with main-thread progress.

    During a permanent main-thread hang, heartbeat files and silence rows continue advancing. The record therefore does not literally end at the main thread’s last heartbeat. An approximate main-thread timestamp can be reconstructed from `silentS`, subject to rounding and clock behavior, but that is not what the observer reports. (`WriteHeartbeat`; `Loop`; `observe`; `BRIDGE_TPS_CAPTURE_FIXES_1.md::C4`.)

    **Change:** persist separate main-progress and watchdog-progress timestamps, sequence numbers, and tick identities.

21. **BUG / DESIGN GAP — Watchdog context is not a coherent snapshot.**

    `JawaBenchTpsWatchdog.cs::Set` publishes `_phase` before `_phaseSinceTicks`; `ContextFields` reads independently changing phase, timestamps, speed, multiplier, tick count, and flags. A watchdog row can combine fields from different moments.

    `Exit` resets the parent’s phase-entry timestamp instead of restoring its original timestamp. If invoked at depth zero, it restores `Stack[0]`, potentially stale state. `QuietPhase` is overwritten during quiet periods but is not cleared on game changes or ordinary recovery without an incident. (`Set`; `Enter/Exit`; `ContextFields`; `Loop`; `RootPrefix`.)

    `Incident` runs after `RootPrefix` has reset the current phase, so its ordinary `phase` usually describes recovery, not the blocked operation. `tps_record.py::render_row` displays that phase and omits the more relevant `quietPhase`.

    **Change:** publish a versioned snapshot, retain phase-entry timestamps through nesting, clear stale quiet observations, and display blocked versus recovery phases separately.

22. **DESIGN GAP — Silence is not deadlock, and heartbeat failure is not whole-process suspension.**

    `JawaBenchTpsWatchdog.cs::Loop` cannot execute during a stop-the-world suspension of managed threads. A main-thread native wait does **not** necessarily stop the watchdog; the design document’s broad “native hang” statement needs qualification. Unity documents its Boehm collector and incremental versus stop-the-world behavior, but the installed collector mode remains unverified. [Unity GC documentation](https://docs.unity3d.com/2022.3/Documentation/Manual/performance-incremental-garbage-collection.html).

    `tps_record.py::observe` calls a live PID with stale heartbeat “whole process frozen.” Other explanations include heartbeat write failure, disk blockage, watchdog failure/starvation, debugger suspension, or machine sleep. `WriteHeartbeat` swallows every exception, so these explanations are not distinguished. The heartbeat is rewritten in place, allowing readers to see an empty or partial file. (`observe`; `WriteHeartbeat`; `read_heartbeats`.)

    **Change:** label the observation accurately: “heartbeat unavailable/stale while process exists.” Record heartbeat writer errors and atomically replace heartbeat snapshots.

23. **BUG — `silent` and `frozen` observer findings are never persisted.**

    `tps_record.py::observe` sets `new` only on `exited-without-shutdown`. The supplied `belt_watchdog.py::gather` diff calls `record_observation` only when `f.get("new")` is true.

    Therefore `silent` and `frozen` findings are displayed but not archived, contradicting the documentation’s “appending each finding once” claim. A transient whole-process freeze observed externally can be absent from the next morning’s record. (`observe`; `record_observation`; `gather`; `tps_record.md`, “The watchdog thread and the external observer”.)

    **Change:** persist incident transitions, bounded updates, and recovery for all finding types, rather than once per finding name for an entire session.

24. **DESIGN GAP — No independent periodic observer deployment is supplied.**

    The `belt_watchdog.py` diff adds observations to `gather`; it supplies no service, timer, startup registration, or scheduling evidence. The next-morning external record depends on someone running that path at the necessary time.

    Its `win_bridge_probe` also calls `jawa/tps_report`, whose `TpsReport` explicitly attempts installation. A bridge-enabled watchdog run can therefore mask an autostart failure. (`belt_watchdog.py::gather/win_bridge_probe` diff; `JawaBenchTpsSampler.cs::TpsReport`.)

    **Change:** provide and verify an external observer lifecycle independent of bridge calls. Test automatic startup with bridge probing disabled.

25. **BUG — The external observer cannot correctly handle multiple processes or PID reuse.**

    `tps_record.py::observe` receives one `game_pid`. A stale heartbeat belonging to another still-running RimWorld instance is treated as an exited session. A reused PID can make an old heartbeat look like a currently frozen process. “PID unavailable” is conflated with “PID no longer exists.”

    **Change:** pass all matching processes with creation times and match a process identity, not one numeric PID.

26. **BUG — Reader validation permits rows that later crash or corrupt analysis.**

    `tps_record.py::_valid` permits missing sample metrics, arbitrary state strings, booleans as numbers, negative durations, nonfinite numbers, malformed session values, and arbitrary event kinds. Python’s JSON decoder accepts nonfinite values by default. `read_record` can subsequently fail on an unhashable session; `by_target` and `timeline` can fail on unchecked field types.

    `read_heartbeats` does not verify that decoded JSON is an object and does not catch resulting `TypeError`s. `observe` assumes `silentS` converts to float. UTF-8 replacement can turn corrupted text into an accepted but altered row. (`_valid`; `read_record`; `read_heartbeats`; `observe`; `timeline`; `by_target`.) See [Python JSON decoding behavior](https://docs.python.org/3/library/json.html).

    **Change:** version the schema; validate finite values, domains, identifiers, envelope keys, and required fields. Count and isolate each bad row without aborting the complete read.

27. **BUG — Session ordering is used where chronological ordering is required.**

    `tps_record.py::read_record` groups entire sessions by their first timestamp. That preserves per-session sequence order but does not produce a chronological timeline for overlapping processes.

    `timeline` compares samples across that grouped sequence and can generate backwards or negative coverage holes. `summarise` gets freshness from the maximum timestamp across sessions, but gets `last`, writer health, speed, and trailing sustained behavior from list order. A fresh session can therefore lend “FRESH” coverage to a verdict derived from another, stale session. (`read_record`; `timeline`; `summarise`; `sustained_from_rows`.)

    **Change:** analyze each session independently and merge only for display. Require explicit session selection or clearly report separate active-session summaries.

28. **BUG — Sustained logic does not enforce the documented continuity.**

    `tps_record.py::contiguous` permits a ten-second separation between ordinary five-second samples. One whole missing sample therefore does not break the streak.

    `sustained_from_rows` ignores `game`, `menu`, and error events; three low samples before a game replacement plus three afterward can become a six-sample warning. The C# sampler clears its streak on game replacement, so the two implementations disagree. (`contiguous`; `sustained_from_rows`; `JawaBenchTpsSampler.cs::RootPrefix/BreakStreak`.)

    C# streaks use full-precision ratios, whereas disk rows use three decimals. Ratios such as `0.5996` or `1.1504` can receive different classifications in the tool and Python. `Report` also has no freshness bound on its retained streak after runtime failure. (`Emit`; `Report`; `JawaBenchTpsMath.cs::F/Sustained`.)

    **Change:** persist game identity and window sequence, break on lifecycle/errors/dropped coverage, use monotonic continuity, and make threshold precision consistent.

29. **DESIGN GAP — A fresh verdict can understate severe recovered stalls.**

    `tps_record.py::verdict` returns `INFO` when there are no judged run windows, including recent stall windows. Once a healthy run window arrives after a severe stall, the result can be `OK`; the incident discriminator bug further removes the incident count.

    Excluding stalls from sustained simulation-ratio judgment is defensible, but the output must independently report experienced stalls and their durations. Otherwise “performance OK” can describe the five minutes containing the owner’s worst interruption. (`verdict`; `summarise`; `Window.State`; `Incident`.)

30. **BUG / DESIGN GAP — Historical placement ignores monotonic time and interval events.**

    `JawaBenchTpsWriter.cs::Enqueue` stores both UTC and monotonic time, but `tps_record.py::contiguous`, `timeline`, and freshness calculations use UTC alone. Clock adjustments can produce false gaps, overlap, reversed continuity, and discarded “future” rows.

    `Gap.Start` is never serialized by `GapFields`; incidents are selected only by their endpoint UTC. A query inside an exceptionally long recovered stall can overlap its sample but omit its endpoint incident and associated explanation. `resumed` is likewise not treated as an interval. (`Gap`; `GapFields`; `read_record`; `contiguous`; `timeline`.)

    **Change:** retain original interval boundaries, use monotonic session continuity, and select duration events by overlap.

31. **BUG / DESIGN GAP — DST input and output are ambiguous.**

    `tps_record.py::parse_when` attaches `ZoneInfo` directly to naive input. Repeated fall-back times silently select the default fold; nonexistent spring-forward times are not rejected. `_local` omits UTC offset and timezone abbreviation, so two distinct instants can print identically. `_tz` is called even for epoch or explicitly offset input, and timezone errors escape the CLI.

    Windows Python installations also require suitable timezone data; that dependency is undeclared in the supplied files. [Python documents fold behavior and Windows timezone-data requirements](https://docs.python.org/3/library/zoneinfo.html).

    **Change:** reject or require clarification for ambiguous/nonexistent local times, print offsets, document explicit-offset input, and handle missing timezone data cleanly.

32. **BUG — Segment enumeration eventually stops recognizing generated filenames.**

    `JawaBenchTpsMath.cs::SegmentName` formats the segment number with a **minimum** width of three. `tps_record.py::SEGMENT_RE` requires exactly three digits. Segment 1000 and later are valid writer filenames but invisible to the reader.

    This is a long-running-session defect, made more relevant by protecting all current-session segments indefinitely. Change the regex to accept three or more digits and sort segment numbers numerically where needed.

33. **BUG / DESIGN GAP — Settings parsing silently accepts malformed configurations.**

    `JawaBenchTpsSettings.Load::Bool/Num` searches text with regex rather than parsing JSON. Duplicate keys, unrelated nested keys, malformed documents, and truncated numeric syntax can be accepted without a diagnostic. Exponent syntax can be read only as its numeric prefix. Very large values lack finite/range validation before conversion to `long`.

    The configuration says retention “can only grow,” but `RetentionMB` and `LogRetentionMB` can be lowered to 16 MB; only retention days are constrained against the shipped default. Settings are read once, with no explicit restart requirement in the settings section. (`Load`; `Num`; `ToJson`; `JawaBenchTpsSampler.cs::Install`; `tps_record.md`, “Settings”.)

    **Change:** parse a strict versioned JSON object with finite bounded values and state the reload policy.

34. **DESIGN GAP — Ordinary numeric precision is not the principal risk; discontinuities are.**

    `JawaBenchTpsWriter.cs::Clock` and the accumulator use double-valued Stopwatch seconds, avoiding the earlier float-uptime problem. The remaining important numerical hazards are unchecked integer tick subtraction, counter reset/discontinuity, invalid mod-supplied multipliers, and silent negative-delta clamping. Negative `DTicks` becomes zero without a discontinuity event. (`FrameAccumulator.Pre/Post`; `WindowFields`.)

    **Change:** detect tick-counter resets and invalid multipliers, record discontinuities, and test unchecked integer boundaries. Do not prioritize a speculative double-precision rewrite over these defects.

35. **DESIGN GAP — Main-thread observer allocation is continuous.**

    `JawaBenchTpsSampler.cs::TmuPrefix` formats `LastMult` through `M.F` and obtains `CurTimeSpeed.ToString()` every played frame. `Emit` allocates several builders, strings, JSON rows, and a new accumulator window. `JawaBenchTpsProfiler.cs::NoteWorst/Exclusive/Top` allocates arrays and strings for accepted worst ticks. Writer/watchdog allocations contribute to the same managed heap even when performed off the main thread.

    `Context` accesses collections whose construction cost cannot be established from the supplied property names, especially `AllPawnsAliveOrDead`; “cheap counts only” must be checked against the actual engine implementation. `Report` copies and parses potentially hundreds of strings while holding or using shared state. (`TmuPrefix`; `Emit`; `Context`; `Report`; `NoteWorst`; `WriteBatch`; `WriteHeartbeat`.)

    **Change:** cache numeric/enum values without per-frame formatting, verify collection access costs, and measure allocation and GC changes for the entire recorder.

**B. What the requested scenarios would actually show**

These predictions assume installation succeeds, the relevant patches execute, and storage remains writable.

| Scenario | Expected record and limitation |
|---|---|
| Owner idles in menu, then loads | `session`, markers, menu event, and heartbeat updates; no TPS samples in menu. A new-game event and samples follow once `_game` is recognized. Initial application loading before companion registration is invisible. Loading a retained `Current.Game` while `ProgramState != Playing` does not explicitly clear `_game` or set a loading lifecycle event. (`Install`; `RootPrefix`; `LoadPrefix`; `WriteHeartbeat`.) |
| Three hours, mixed speeds, two autosaves, 40-second mod stall | Approximately five-second samples integrate observed speed changes. Autosaves yield `save` rows and, if correctly covered by long-event accounting, explained windows. Recovered gap rows are mis-discriminated as `stall`/`longevent`. A stall inside the window-closing tick can split duration and attribution across adjacent windows. (`FrameAccumulator`; `SavePostfix`; `Incident`; `Emit`.) |
| Ninety-second main-thread freeze, recovery | If other managed threads run, approximately 10/40/70-second silence observations and progressing heartbeat files, then `resumed`, a recovered gap row, and a long sample. If all managed threads are suspended, no internal silence rows during the freeze; an external finding appears only if the observer runs, and `frozen` is not persisted by the supplied path. (`JawaBenchTpsWatchdog::Loop`; `observe`; `gather`.) |
| Permanent hang, then kill | A main-thread-only hang can leave repeated silence rows. A whole-process suspension leaves the last existing files. Kill loses unfinished measurement and outstanding writer work. Later observation may persist `exited-without-shutdown`, but the claimed last-main-heartbeat UTC is actually the watchdog-write UTC. (`Loop`; `WriteHeartbeat`; `WriteBatch`; `observe`.) |
| Windows Update steals CPU | Low TPS and longer elapsed stage timings may appear. Descheduling while inside `tl:Normal` increases that stage’s measured cost, potentially resembling expensive simulation code. Nothing here records thread CPU time, ready time, or the competing process. (`Begin/End`; `TmuPostfix`; `Context`.) |
| Alt-tab, run-in-background disabled | Unity can stop background updates. The watchdog can report silence; on return, the sampler treats the absence as an unexplained gap and reduced throughput. Focus is cached, potentially stale, and the run-in-background setting is not recorded. This cannot establish a mod-induced stall. (`RootPostfix`; `Loop`; `FrameAccumulator.Pre`.) [Unity’s background-execution setting](https://docs.unity3d.com/2022.3/Documentation/ScriptReference/Application-runInBackground.html). |
| Two RimWorld instances | Segment filenames are distinct, but retention can delete the other instance’s files; archived log names can collide; the observer accepts only one PID; the default reader mixes sessions incorrectly. (`SegmentName`; `Prune`; `ArchiveLogNow`; `observe`; `read_record/summarise`.) |
| Machine sleeps/resumes | On a QPC-backed Stopwatch, sleep contributes elapsed time. Resume can look like a huge unexplained stall or stale-heartbeat freeze. Neither power-state transitions nor an awake-time clock are supplied. Verify Unity/Mono’s actual Stopwatch implementation on this installation. (`Clock`; `FrameAccumulator.Pre`; `observe`.) [Microsoft documents QPC’s inclusion of sleep time](https://learn.microsoft.com/en-us/windows/win32/sysinfo/acquiring-high-resolution-time-stamps). |
| “Why was 3pm slow?” next morning | The reader may locate overlapping samples and broad subsystem timings, subject to timestamp, discriminator, retention, and session-ordering defects. It cannot identify the responsible mod, distinguish execution from CPU deprivation, recover unarchived/transient external evidence, or reproduce the vanished map state. (`timeline`; `Top`; `WriteSessionStart`; `ArchivePrevLog`; incident note, “Not ruled out”.) |

`JawaBenchTpsSampler.cs::LoadPrefix` also sets `_loadName` before load success and never clears it for a subsequently generated new game. `_saveTotal`, `LastSave`, and several watchdog caches persist across game changes. A later game can therefore carry the previous game’s save name and cumulative context. These fields need explicit process-versus-game scope.

**C. “Why” attribution is a lead, not a causal verdict**

`JawaBenchTpsProfiler.cs::Begin/End` measures **elapsed residence in a scope**. That includes CPU execution, scheduler deprivation, GC suspension, blocking I/O, and waits incurred while the scope is open. Accordingly, the design document’s “high sim → simulation-bound” and “low sim/fps → rendering” rules are hypotheses, not conclusions. The measurement-boundary defect makes those hypotheses less reliable still. (`tps_record.md`, interpretation table; `FrameAccumulator.Post`; `TmuPostfix`.)

`JawaBenchTpsSampler.cs::WriteSessionStart` records ordered package IDs in the manifest, but its digest sorts them, erasing load-order identity. It records no mod versions/content hashes, assembly-to-package mapping, settings fingerprints, or patches-by-target inventory. Harmony owner **counts** are not a culprit list: expensive unpatched mod implementations may have no Harmony owner, while a patch owner may be unrelated to the hot stage. (`WriteSessionStart`; `tps_record.md`, “Attribution”.)

`JawaBenchTpsSampler.cs::Context` preserves map ID, dimensions, biome, and aggregate counts for at most eight maps. It does not preserve generator/seed identity, component types, pawn/species composition, jobs/pathing activity, or enough state to recreate the first quicktest map. The supplied incident specifically leaves the first generator/biome and session-specific state unresolved. (`Context`; `low_tps_2026-10-10.md`, “Not ruled out” and “NEXT if it recurs”.)

A mod-level hunt would need:

- **Type-level candidates:** bounded component, tickable-type, or sampled-stack evidence, with assembly/package mapping. (`JawaBenchTpsProfiler.cs::TakeWindowFields`; `WriteSessionStart`.)
- **Patch-chain evidence:** actual patches and order on the hot targets, plus declaring implementation assemblies. (`WriteSessionStart`, currently owners/counts only.)
- **CPU-versus-wait evidence:** process/thread CPU, scheduler and I/O context, and collector configuration. (`Begin/End`; `Context`, currently elapsed and memory only.)
- **Preserved reproduction state:** save or approved incident snapshot, map-generation identity, exact mod/settings/build identity, and workload context. (`RootPrefix`; `Context`; `WriteSessionStart`.)
- **A bounded detailed capture:** activated while the bad state still exists, with its own overhead limit and persisted results. Restarting with DPA can destroy the evidence being investigated. (`low_tps_2026-10-10.md`; `tps_record.md`, targeted-follow-up policy.)

The profiler itself can cause measurable slowdown. Each `Begin/End` pair also performs phase-stack work, atomic timestamp publication, additional clock reads, counter updates, and Harmony dispatch. `TickPre` copies arrays; `TickPost` reads another timestamp and can format worst-tick evidence. Calls scale with ticks and maps. (`JawaBenchTpsProfiler.cs::Begin/End/TickPre/TickPost`; `JawaBenchTpsWatchdog.cs::Enter/Exit/Set`.)

`Calibrate` measures two bare timestamp calls in a loop, not that complete path. Its result is an incomplete estimator, **not a mathematically guaranteed lower bound**: calibration scheduling/JIT noise can also inflate it. An attribution-off comparison measures only the profiler’s incremental cost, not the sampler/writer/watchdog’s total observer cost. (`Calibrate`; `TakeWindowFields`; `tps_record.md`, “Attribution”; progress log, “owed live”.)

**D. Safety assessment**

- **Game execution can be interrupted by telemetry exceptions.** Unguarded profiler hooks and incomplete cleanup are the direct risk; the sampler’s nonthrowing claim does not cover them. (`JawaBenchTpsProfiler.cs::TickPre/TickPost/TlCat/NoteWorst`; `JawaBenchTpsSampler.cs::LePrefix/SavePostfix`.)
- **No supplied TPS code directly edits simulation state or save contents.** Save hooks observe filenames and durations. I cannot establish save safety for earlier-triggered module-initializer behavior because only a small `JawaBenchInit.cs` diff is supplied. (`SavePrefix/SavePostfix`; init diff, startup comment.)
- **Telemetry files can be duplicated, malformed, overwritten, or prematurely deleted.** These are established writer/archive/retention paths, including cross-instance interference. (`WriteBatch`; `Loop`; `ArchiveLogNow`; `Prune`.)
- **State leaks between loaded games in one process.** Save labels, cumulative save time, profiler totals, and watchdog context can survive game replacement. Process sessions are UUID-separated, but that does not repair game-level identity. (`RootPrefix`; `LoadPrefix`; `TakeWindowFields`; watchdog static fields.)
- **Shutdown can become slower than the advertised bounds.** Log copying is synchronous and unbounded by the two drains; Unity API access is also attempted from `ProcessExit`. (`OnQuit`; `ArchiveLogNow`; `Install`.)

**E. Missing tests and live acceptance work**

The supplied parity harness compiles only the pure maths under net8.0. It does not establish production Unity/Mono patch execution, writer correctness, automatic startup, or actual engine semantics. The synthetic engine retains fractional debt and models an assumed delta-time clamp independently of simulated work duration; that is not a replay of the installed `TickManagerUpdate`. The claimed 49/49 result was not reproduced in this review. (`selftest_tps_record.py::Sim.frame/traces/cs_parity`; `JawaBenchTpsMath.cs`, semantic comments.)

Before trusting the recorder, add these tests:

| Test group | Required cases and assertions |
|---|---|
| Production serialization | Compose actual `Enqueue` envelopes with actual sample/gap/context fields. Reject duplicate keys; assert incidents remain incidents and current versus cached multiplier is explicit. (`Incident`; `GapFields`; `Enqueue`.) |
| Window timing | Long current tick at a cadence boundary; long previous tick; repeated slow ticks; gap plus pause/speed transition; fully explained interval with residual ticks; first-frame alignment; tick reset and integer boundaries. Assert explicit time boundaries and attribution validity. (`FrameAccumulator`; `TmuPrefix/TmuPostfix`.) |
| Lifecycle | Menu, new game, load failure, same-process second game, direct save, nested save, synchronous/asynchronous events, return to menu during a partial window, runtime disable. Assert no stale labels or profiler carryover. (`RootPrefix`; save/load/event hooks; `TakeWindowFields`.) |
| Harmony compatibility | Earlier prefix returns false; later prefix changes speed; original throws; another postfix throws; target missing; patch-install failure; reentrant invocation; worker-thread invocation. Preserve original exceptions and reject invalid measurements. (`Install`; `Patch`; timer hooks.) |
| Writer fault injection | Failure before append, mid-line, after one segment succeeds, during rotation, during retry; producer load while disk is blocked; queue exhaustion; abrupt termination during append. Assert bounded outstanding work, replay detection, readable tails, and loss accounting. (`Loop`; `WriteBatch`; `Drain`.) |
| Retention and archive | Two active processes; session exceeds cap; metadata/segment association; same-time and same-length different logs; concurrent prune/archive/read; oversized lines; segment 1000. (`Prune`; `ArchiveLogNow`; `SegmentName`; `SEGMENT_RE`.) |
| Reader/observer | Duplicate/conflicting sequence rows, malformed field types, NaN/infinity, invalid heartbeat objects, PID reuse, two processes, missing PID probe, missing sample, game transition inside a streak, UTC jumps, DST folds/gaps, interval-overlap selection. (`read_record`; `observe`; `contiguous`; `timeline`; `parse_when`.) |

The owner’s full load then needs these experiments:

1. **Autostart without assistance.** Cold launch with no bridge client, no `tps_report`, and no bridge-enabled belt probe. Inspect files directly. Verify session startup, menu heartbeat, gameplay samples, actual host/companion identity, and what happens before registration. Repeat with new game and save load. (`JawaBenchTpsTools::.ctor`; `Install`; `win_bridge_probe` diff.)

2. **Independent throughput validation.** Measure completed ticks and elapsed time externally over controlled workloads at each speed, pause patterns, forced-normal transitions, superfast multiplier changes, and differing frame limits. Verify the installed engine’s actual multiplier/cap/budget behavior rather than treating comments as source evidence. (`FrameAccumulator`; `Sim.frame`; `TmuPrefix/TmuPostfix`.)

3. **Controlled interruption matrix.** On disposable test state, exercise 2–10-second hitches, 40- and 90-second main-thread blocking, whole-process suspension, saves/loads, permanent hang plus kill, and random forced kills near sample/segment boundaries. Require readable records with separate last-main-progress and last-watchdog-progress times. Verify external findings survive until the next morning. (`Loop`; `WriteHeartbeat`; `observe`; `WriteBatch`.)

4. **Environmental discrimination.** Test focus loss with background execution on/off, sleep/resume, CPU competition, disk stalls, and two game processes. Require appropriately qualified labels rather than “mod stall” or “whole process frozen” by inference. (`RootPostfix`; `ContextFields`; `observe`; `Prune`.)

5. **Actual overnight reconstruction.** Leave the recorder running, induce a documented slowdown, shut down/relaunch, and query the incident next morning. Require the correct game, local time with offset, interval, duration, ratios, attribution validity, map identity, and linked archived log. (`timeline`; `WriteSessionStart`; `Context`; `ArchivePrevLog`.)

Measure observer overhead with **three separately restarted configurations** on the same full mod list and controlled save/workload:

- Sampler disabled.
- Sampler enabled, attribution disabled.
- Full recorder enabled.

This separates total recorder cost from the profiler’s incremental cost. Ensure module-initializer and companion startup behavior otherwise match; settings are loaded only at installation. (`JawaBenchTpsSettings.Load`; `Install`; `Calibrate`; init diff.)

Use repeated, counterbalanced runs after a defined warm-up. Hold speed, camera, frame cap, focus, save workload, and mod versions constant. Measure fixed-tick completion time, wall TPS, frame-time distribution, main-thread CPU, allocations/GC, and recorder I/O. Include both normal play and a demanding colony at high speed: capped 60-TPS play can conceal overhead. Declare acceptance limits before seeing results, report uncertainty and outliers, and repeat any external profiling consistently across configurations. (`FrameAccumulator`; `Begin/End`; `Context`; `HealthFields`.)

**F. Ranked concrete changes**

Ranked within each priority; “why” describes the immediate failure being addressed.

| Priority | Category | Change and pointer | Why |
|---|---|---|---|
| MUST 1 | Bug | Remove duplicate envelope/context keys. `Incident`; `GapFields`; `ContextFields`. | Recovered incidents currently evade incident analysis. |
| MUST 2 | Bug | Make every profiler timer skip-safe and exception-contained. `TickPre/TickPost`; `TlPre/TlPost`; `Begin/End`. | Ordinary Harmony behavior can fabricate huge durations or interrupt ticks. |
| MUST 3 | Bug | Align and persist measurement boundaries. `FrameAccumulator.Pre/Post`; `Emit`; `timeline`. | Long ticks corrupt historical placement and attribution. |
| MUST 4 | Bug | Make writer retry commit-aware and torn-tail-safe. `WriteBatch`; `Loop`; `read_record`. | Failures replay records and can corrupt JSONL tails. |
| MUST 5 | Bug | Preserve unexplained gap exposure when state changes. `FrameAccumulator.Pre`. | Ambiguity currently removes time from expected ticks. |
| MUST 6 | Bug | Reset profiler/game-scoped state and persist game identity. `RootPrefix`; `LoadPrefix`; `TakeWindowFields`. | Measurements and labels cross loaded games. |
| MUST 7 | Bug | Repair continuity, lifecycle resets, and threshold consistency. `contiguous`; `sustained_from_rows`; `Emit/Report`. | “Sustained” warnings can bridge missing samples or games. |
| MUST 8 | Bug | Analyze sessions separately. `read_record`; `summarise`; `timeline`. | Concurrent sessions produce incorrect freshness and timelines. |
| MUST 9 | Bug | Persist all observer incident types and handle all process identities. `observe`; `gather`. | Whole-process freezes can disappear from history or be mislabeled as exit. |
| MUST 10 | Design gap | Persist separate main/watchdog progress; atomically publish heartbeats with errors. `WriteHeartbeat`; `ContextFields`. | Current heartbeat UTC does not identify last main-thread progress. |
| MUST 11 | Bug/design gap | Protect active sessions and retain metadata coherently. `Prune`; `PlanRetention`. | Another process can delete live evidence; retention claims are misleading. |
| MUST 12 | Design gap | Preserve previous logs before lengthy startup; eliminate archive collisions. `ArchivePrevLog`; `ArchiveLogNow`. | Relaunch can still erase the incident’s log. |
| MUST 13 | Bug | Strictly validate versioned rows/settings and accept segment numbers ≥1000. `_valid`; `read_heartbeats`; `Load`; `SEGMENT_RE`. | Accepted malformed input can break analysis or hide records. |
| MUST 14 | Design gap | Bound all outstanding work and prioritize critical evidence. `Enqueue`; `Loop`; `HealthFields`. | Queue health omits in-flight work and important events can be dropped. |
| MUST 15 | Design gap | Verify identified-time unions and original-exception cleanup. Save/event hooks; `FrameAccumulator.Pre`. | Synthetic explained time does not prove runtime exclusion. |
| MUST 16 | Design gap | Add installation rollback/status and shutdown completion semantics. `Install`; `Patch`; `OnQuit`; `Drain`. | Partial install and shutdown intent currently resemble success. |
| MUST 17 | Design gap | Run the full-load acceptance/overhead matrix and deploy an independent periodic observer. `C3/C4`; `gather`; `Calibrate`. | Offline parity cannot establish standing coverage or acceptable observer cost. |
| SHOULD 1 | Design gap | Persist bounded numerical worst-tick breakdowns and valid tick IDs. `NoteWorst`; `TickPost`. | Current worst records cannot reconstruct their own attribution. |
| SHOULD 2 | Design gap | Add CPU/wait/collector/power/focus context. `Context`; `ContextFields`; `observe`. | Elapsed scope time cannot establish computational cause. |
| SHOULD 3 | Design gap | Record ordered mod/version/content/settings identity and target patch chains. `WriteSessionStart`. | Owner counts and sorted package digests do not identify the effective load. |
| SHOULD 4 | Design gap | Add bounded type-level or sampled-stack capture while the incident state exists. `TakeWindowFields`; `Context`. | Coarse subsystem totals cannot name a culprit. |
| SHOULD 5 | Bug/usability | Handle DST ambiguity and print offsets; expose blocked phase and historical severity. `parse_when`; `_local`; `render_row`; `verdict`. | The timeline and verdict can mislead the person interpreting them. |
| SHOULD 6 | Performance | Remove per-frame formatting and verify collection getter costs. `TmuPrefix`; `Context`; `Report`. | Continuous measurement should not allocate avoidably. |
| SHOULD 7 | Design gap | Persist schema version, measurement validity, coverage-loss ranges, and installation inventory. `Enqueue`; `TakeWindowFields`; `WriteSessionStart`. | Future readers need to distinguish evidence from incomplete measurements. |
| SKIP | Design choice | Always-on instrumentation of every pawn/method/mod. Profiler policy in `tps_record.md`. | Too much potential observer cost without a demonstrated need. |
| SKIP | Unsupported inference | Automatic blame from `top`, GC count, heap growth, or Harmony owner count. `Top`; `ContextFields`; `WriteSessionStart`. | These are correlations or candidate evidence, not causation. |
| SKIP | Nice to have | UI/dashboard work and speculative double-clock precision refactoring before the defects above. `Report`; `Clock`; `timeline`. | They do not repair missing or incorrect evidence. |

The earlier reviews’ central objections still apply where build 2’s replacements are incomplete. In particular, the supplied progress log marks persistence, observer recording, attribution, and continuous fresh judgment “Done,” but the corresponding runtime paths contain the defects above. (`foundry_tps_fixes_20261010.md`, sections 2/4/5/7; `Incident`; `WriteBatch`; `observe`; `sustained_from_rows`.)

**G. What could not be verified**

- The installed RimWorld 1.6 method bodies, signatures, overloads, parameter names, call order, and actual cap/budget behavior. Comments and earlier decompilation reports are not those bodies. Harmony argument-name injection makes the exact `SaveGame`/`LoadGame` signatures material. (`Install`; `SavePrefix`; `LoadPrefix`.) [Harmony parameter injection](https://harmony.pardeike.net/v2/articles/patching-injections.html).
- Companion discovery timing and constructor execution in the installed RimBridgeServer, including SDK/version compatibility. The constructor’s presence does not prove host execution. (`JawaBenchTpsTools`; `Install`; design document, “What starts it”.)
- The complete `JawaBenchInit` initializer and safety of moving its other installations earlier. Only the supplied diff is available. (`foundry_tps_init_diff_20261010.patch`.)
- The complete belt watchdog, process enumeration, scheduling, and overall-verdict aggregation. The diff does not prove periodic deployment or that TPS signals are excluded from the aggregate verdict. (`foundry_tps_belt_watchdog_diff_20261010.patch`.)
- Production compilation, Unity/Mono runtime behavior, installed Harmony patch chains, collector mode/count semantics, filesystem/WSL sharing behavior, and actual log rotation naming. (`Install`; `cs_parity`; `Prune`; `ArchivePrevLog`.)
- The reported 49/49 parity result, live startup, overhead, durability bounds, real records, or the original vanished slow map. These were supplied as reports, not independently reproduced evidence. (`foundry_tps_fixes_20261010.md`, “owed live”; `selftest_tps_record.py`; `low_tps_2026-10-10.md`.)

**The acceptance decision should remain blocked until the runtime defects are repaired and the full-load experiments establish coverage, interpretation, and overhead.** The present C3/C4 wording is insufficient because it can pass while incident parsing, retry correctness, historical placement, and persisted external freeze evidence remain broken. (`BRIDGE_TPS_CAPTURE_FIXES_1.md::criteria`; `Incident`; `WriteBatch`; `timeline`; `observe`.)