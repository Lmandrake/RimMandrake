# Load Tracer (local) — validation walk
subject: src/RimMandrake/LoadTracer  (packageId `mandrake.rm.loadtracer`)
deps: none (Ludeon.RimWorld, brrainz.harmony only)
list: minimal
status-hint: diagnostic instrument for COLD_LOAD_STALL_INTERMITTENT_1 — a byte-identical replacement for `StaticConstructorOnStartupUtility.CallAll` that logs every `[StaticConstructorOnStartup]` type to Player.log BEFORE invoking it, via `UnityEngine.Debug.Log` directly (Verse.Log's message cap would silence a large trace), plus brackets around `FloatMenuMakerMap.Init` and atlas baking. Not player-facing content — remove once the stall is attributed. Ships no XML defs.

## must be true
- On load, exactly one Harmony patch group named `mandrake.rm.loadtracer` applies and logs `"[LoadTracer] armed: CallAll per-type trace + FloatMenuMakerMap.Init/BakeStaticAtlases brackets"` — its absence means tracing is OFF for this load and no other check in this file means anything.
- `CallAll`'s replacement logs `"[LoadTracer] CallAll begin"`, then `"[LoadTracer] CallAll: <N> static ctors to run"`, then one `"[LoadTracer] ctor <i>/<N>: <TypeFullName> [<AssemblyName>]"` line per type IN ORDER, then `"[LoadTracer] CallAll complete"` — a full cold load must show a first and a last ctor line with no unexplained gap between two consecutive `ctor i/N` indices.
- If the byte-identical loop itself fails to enumerate types, it falls back to the ORIGINAL `CallAll` and logs `"[LoadTracer] type enumeration FAILED, falling back to original CallAll: <ex>"` rather than silently doing nothing.
- `FloatMenuMakerMap.Init` and `BakeStaticAtlases` are each bracketed with a begin/done pair (`"[LoadTracer] FloatMenuMakerMap.Init begin/done"`, `"[LoadTracer] BakeStaticAtlases begin/done"`) — on a load that stalls inside one of these two stages, the LAST line in Player.log must be the matching "begin" with no "done", which is the diagnostic payoff this whole mod exists for.

## the walk
1. [L] Player.log from a full cold load (not the 13-mod minimal list — this diagnostic's whole purpose is a large-modlist trace, so run it against whatever list is under investigation) contains `"[LoadTracer] armed: ..."` near the top of the load, before the first `"[LoadTracer] CallAll begin"`   # load-time
2. [L] Player.log contains `"[LoadTracer] CallAll: <N> static ctors to run"` with N matching (or close to) the active mod count's expected StaticConstructorOnStartup type population — a suspiciously low N (e.g. tens instead of hundreds on 500+ mods) is itself a finding
3. [L] Player.log's `ctor i/N` lines are strictly increasing with no duplicate or skipped index, ending at `i=N`, followed by `"[LoadTracer] CallAll complete"`
4. [L] on a load that reaches the main menu successfully, confirm both bracket pairs appear complete: `"FloatMenuMakerMap.Init begin"` immediately followed (allowing intervening ctor/asset noise) by `"FloatMenuMakerMap.Init done"`, and likewise for `BakeStaticAtlases`
5. [L] (regression case) deliberately using a known-stalling large mod list, confirm the LAST line in Player.log at the moment of the stall is a `ctor i/N:` line (names the culprit type) or a bracket "begin" with no matching "done" — never silence with no LoadTracer line at all, which would mean the mod itself failed to arm

## anti-guessing notes
- Every string above is quoted verbatim from `src/RimMandrake/LoadTracer/Source/LoadTracer.cs`, per the anti-guessing rule for a mod with no XML defs.
- Per this mod's own About.xml: it is a diagnostic instrument, "not player-facing content", meant for removal once the stall is attributed — do not treat a clean run of this walk as validating any gameplay behavior.
- No [S] line: purely a log-trace instrument, nothing visual.
