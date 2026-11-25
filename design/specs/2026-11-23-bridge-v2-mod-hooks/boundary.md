# BOUNDARY: the mods' test hooks, found by reflection (BRIDGE v2.0), Design Version 0.1.0

Code: `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchModHooksCore.cs` (all of it),
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchModHooks.cs` (all of it) and
`src/RimMandrake/_Shared/TestHooks/RMTestHooks.cs` (all of it). Also the watch lines of the run (`IRunWatch`, `Watch`, `ModSays`, the
watch calls in `Arm` and `End`) in `JawaBenchSceneTickCore.cs`, whose other promises are on `../2026-11-23-bridge-v2/boundary.md`.
Item: `RIMMANDRAKE_BUILD_MOD_TRACE_AND_RESET_HOOKS_BY_REFLECTION`. Design: decision 8 of `../2026-11-23-bridge-v2/05_build_design.md`.
Each promise has a test of its name in `src/RimMandrake/bridgetools/selftest_test_hooks.py`; its harness is
`src/RimMandrake/bridgetools/TestHooksSelfTest/` (seven net472 fixture mods, each built with the shipped `RMTestHooks.cs`).

A mod compiles `RMTestHooks.cs` in as its own internal copy, in its RELEASE build too. The mod names no type of the companion, and the
companion names no type of the mod: the companion finds the copy by type name. A hook judges nothing. A `mod` record is evidence of a
branch only: a reader of the trace may not decide a success on it alone (decision 8 of `05_build_design.md`). No reader of the trace
reads `mod` records yet.

## WHAT A MOD WRITES

| part | shape | what it does |
|---|---|---|
| `RMTrace.Emit(name)`, `Emit(name, key, value)` with a `string`, `long`, `double` or `bool` value | static, internal | when a scene run is live, one `mod` record in the run's trace; else nothing |
| `[RMReset]` | `public static string Reset(string scope)` | clears the mod's per-scene state (caches, counters, pending callbacks) and answers what it cleared |
| `[RMDigest]` | `public static string Digest(string scope)` | answers a digest of the state that `Reset` clears |
| `RMTestHooksBuild.Kind` | const, from `RM_PROOFS` | `PROOF` or `RELEASE` |

One `[RMReset]` and one `[RMDigest]` per mod. `scope` "" means all of the mod's state.

## WHAT THE COMPANION FINDS

Every loaded assembly whose name starts with `RimMandrake`, or that holds the types of `RMTestHooks.cs`. For each: its build
(`PROOF`, `RELEASE`, `none` when it has no hooks file, `unknown`), its trace point, its two hooks, and each problem by name. The
list is made once, on first use: assemblies do not change after the game has loaded.

## THE RUN

- At the arm of every scene run (`jawa/run_until`, `jawa/scene_slice`, a `until=` step loop), each mod's `RMTrace.Sink` is set. A
  mod's `Emit` then writes a record `mod` of phase `in_tick`: `mod` (the assembly name), `name`, and `key` and `v` when given.
- At the end of the run, in every end state, each sink is null again. A delegate that a mod kept and calls after the end writes
  nothing; the call is counted `late`.

## THE TOOL `jawa/mod_hooks` (TEST profile only)

| action | does |
|---|---|
| `list` | each mod's row: `mod`, `build`, `trace`, `reset`, `digest`, `digestProven`, `digestProof`, `problems`; and `armed`, `said`, `late`, `staleAtArm` |
| `admit` (`purpose`) | `acceptance`: one refusal `PROOF_BUILD: ...` for each mod whose build is not `RELEASE`. `explore`: none |
| `digest` (`mod`, `scope`) | each mod's digest now |
| `prove` (`mod`, `step`, `scope`) | `clean`: reads the digest of the clean state. The caller then dirties the mod's state on purpose. `dirty`: reads it again; `digestProven` only when the two differ |
| `reset` (`mod`, `scope`) | calls the mod's reset hook, then reads its digest: `verified` (proven, and equal to the clean read), `differs`, or `unproven` |

A refusal is `{"success": false, "refused": "NAME", "message": "...", "repair": "..."}`: `UNKNOWN_MOD`, `NO_DIGEST_HOOK`,
`NO_RESET_HOOK`, `NO_CLEAN_READ`, `HOOK_THREW`, `BAD_ARGS`. While a run is live, the run lock lets `list`, `admit`, `digest` and
`prove` through, and refuses `reset` unless it is an act of the run.

## LIMITS

- **The proof and reset messages cut a digest at 120 characters.** Danger: a mod may digest a large state, and the message would fill
  the reply. The whole digests are in the reply's `clean`, `dirty` and `digestAfter`.

## DOES NOT SURVIVE (not promised)

- **a-mod-that-writes-its-own-sink.** `Sink` is a field of the mod's own copy. A mod that sets it itself is not stopped; `staleAtArm`
  counts a sink found set at an arm.
- **a-digest-that-misses-part-of-the-state.** The proof shows that the digest sees the part of the state that the caller dirtied, not
  that it sees all of it.
- **a-hook-that-blocks.** A reset or digest hook that does not return holds the main thread.
- **an-assembly-loaded-after-the-first-list.** The list is made once.

## PROMISES (each one is owed a test of the same name)

- **a-mod-with-no-hook-is-listed-as-such.** A RimMandrake assembly with no hooks file is listed with build `none`, `no trace point`,
  `no reset hook` and `no digest hook`, and no problem. An assembly that is not ours is not listed.
- **a-hook-of-the-wrong-shape-is-a-named-problem.** A hook that is not `public static string M(string scope)` is not used, and a
  problem names its type, its method and what is wrong. Two hooks of one kind in one mod are a problem.
- **emit-with-a-null-sink-allocates-nothing.** With no run live, `Emit` of each value type allocates 0 bytes; with a sink set, the
  same calls allocate (the instrument sees).
- **the-sink-is-cleared-at-the-end-also-after-a-thrown-tick.** After a run ends as `threw`, `cancelled` or `aborted`, every sink is
  null and a kept delegate writes nothing and is counted `late`. While the run was live, `Emit` wrote a `mod` record with the mod,
  the name, the key, the value, the tick and phase `in_tick`.
- **two-mods-hooks-do-not-collide.** Two mods with the same type names are two rows; each record names its own mod; the proof and the
  reset of one leave the other's state and proof unchanged.
- **a-proof-build-hook-is-refused-for-an-acceptance-run.** `admit purpose=acceptance` refuses each mod whose build is `PROOF` or
  `unknown`, by name, and only those; `explore` refuses none.
- **a-release-dll-with-hooks-names-no-companion-type.** A mod's RELEASE DLL with hooks references no assembly and no type of the
  companion or of the bridge host; a DLL that does is seen (the harness's Leak fixture, in every pass).
- **a-digest-is-accepted-only-after-it-was-seen-to-differ.** `digestProven` is true only after a `clean` read and a `dirty` read that
  differ. A digest that answers a constant is never proven and says why. A reset is `verified` only with a proven digest equal to the
  clean read; before the proof it is `unproven`.
