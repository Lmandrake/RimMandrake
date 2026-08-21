# player-log-triage.md — reading a RimWorld `Player.log`

Open this whenever you are actually reading a log.

`%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log`

🔴 **Do not reach for `grep` first — run `harvest_log.py`.** The blind-scan hook refuses
a scanner on `Player.log`, and it earns the refusal: one error spans 30 lines, so a
`grep -c` counts LINES and not errors, and that number then decides severity.

```bash
python3 src/RimMandrake/Utils/harvest_log.py --log <path>    # note --log, not positional
python3 src/RimMandrake/Utils/harvest_log.py --show dead     # print the matching lines
```

It groups traces, carries a measured baseline per check, and REFUSES a log written before
the current `ModsConfig.xml` — which is the failure a hand grep cannot see at all.
Searching for one literal error string to learn IF it occurred is still legitimate; run it
as `MEASURE_ALLOW_SCAN=1 grep -F '<string>' "$LOG"` and say that you overrode.

Triage in this order, because it sorts by severity of consequence rather than by
position in the file:

1. **`--show dead` and `--show reflect`** (`static constructor`, `TypeInitializationException`, `ReflectionTypeLoadException`) — these mods are *dead*, not noisy. A mod that
   throws in its static constructor did not load at all, and it will not say so
   again later. In a large stack, failures concentrate here: mods that reflect
   over *other mods'* types at startup are the fragile class.
2. **`Could not execute post-long-event action`** — one queued post-load action
   failed. **It cost exactly that action; the queue continues.** Verified against
   the IL of `Verse.LongEventHandler.ExecuteToExecuteWhenFinished` (1.6.4871):
   the `try` spans 18 bytes around a single `Action::Invoke`, the catch logs via
   `Log.Error`, and its `leave` targets the loop *increment*, not the exit. The
   loop even re-reads `.Count` each pass, so actions queued during execution
   still run.

   Severity is therefore per-action — usually one def's `ResolveIcon` — not
   "everything after this silently didn't happen." Weigh it accordingly before
   blaming unrelated breakage on it, or disabling a mod over it.

   ⚠️ The one real abort path in that method is *outside* the try: the
   per-iteration DeepProfiler block dereferences
   `action.Method.DeclaringType`. An NRE there escapes the loop, skips the final
   `Clear()`, and leaves the re-entry flag set — which bricks the queue
   permanently behind "Already executing." Distinguish the two by the stack: a
   frame for the queued action itself (e.g. `BuildableDef.<PostLoad>b__78_0`)
   means the survivable path.
3. **`Could not resolve cross-reference`** — a def referenced something absent.
   Usually a `MayRequire` guarding the wrong thing (see SKILL.md §4). **Do not
   file these as harmless without reading the `wanter`.** The consequence depends
   entirely on the field that wanted it:

   - **A plain `List<Def>` field** (`wanter=pawnKindDefs`, `thingDefs`, …) drops
     the unresolved entry and degrades gracefully. Genuinely benign.
   - **A record that later becomes a dictionary key** — `BiomeAnimalRecord`,
     `WeatherCommonalityRecord` and their kin — keeps the record and leaves the
     def field **null**. The next consumer to build that dictionary calls
     `Add(null, …)` and throws `ArgumentNullException: key`, which kills whatever
     mod touched it first, in its static constructor, far from here.

   Five such lines, filed as "five spawn-table entries are skipped", were the
   sole cause of a dead mod for three loads running. A large count still means
   content is silently incomplete; a *small* count is not evidence of safety.
4. **`Patch operation ... failed`** — a no-op. Almost always benign, and the most
   common noise category in a big stack.
5. **Translation errors, missing sounds** — cosmetic. The engine says so itself
   ("using undefined sound"). Do not spend time here.

Two behaviours worth keeping:

**Key a triage rule on a failure SIGNATURE, never on a mod's name.** A grep for
`RimAI` flagged it RED with 5 hits on a load where it was healthy — the hits were
`SettingsManager: Initialized successfully` and `All Parts Boot OK`. "Zero hits =
healthy" only holds for mods that are silent when working, which most are not.
Match `RimAI\.Core.*Exception|assembly RimAI` instead.

**Maintain a triage list of errors judged safe**, with the exact log string, the
owning mod, the root cause, and *why* it's harmless. If you can't fill all four,
it isn't safe yet — it's just unexplained. Without this list you re-investigate
the same benign noise every single load.

**Load order can look like a code bug.** A `ReflectionTypeLoadException` naming
another mod's types usually means load order, not a broken assembly: a mod can
declare a `modDependency` and still load *before* it, because dependency ≠
ordering. `loadAfter` is what orders. When it's missing upstream, fix it locally
with a sorter rule rather than touching the mod.
