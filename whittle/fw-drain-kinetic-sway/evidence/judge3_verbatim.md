**Verdict:** all three frozen bullets hold at L0. There is no missing-mod regression for the GSS-only callers. I found four low-severity points and nothing that blocks.

The review was read-only. I didn't attach to the game, didn't run anything live and make no appearance claim. I couldn't recompute file hashes myself because I had no shell, so the identity checks below compare the hashes recorded in the raw logs with each other. I didn't read DONE.md, the maker's findings or earlier judge outputs.

**Bullet 1 – AerialProbe explode parsing**
- **Old form and default:** `explode:x,z,r,dmg` (4 parts) still resolves to `Bomb` (`AerialMath.cs:1017`). All three existing 4-part callers (`validation_aerial.py:582,654,916`) are unchanged.
- **Synthetic token:** the `kinetic` 5th part still selects the cloned-Bomb synthetic def, checked before any name lookup (`AerialProbe.cs:153-154`). Its reply is `damageDef:"Bomb", synthetic:true`.
- **Registered names:** a 5th part that is a valid identifier is looked up with `DefDatabase<DamageDef>.GetNamedSilentFail`. An unknown name returns `Fail("unknown damage defName …")` and nothing explodes (`:155`). A malformed selector or wrong part count throws before any `int.Parse` or `DoExplosion` call, and `Service` turns that into `success:false`.
- **Whitespace:** the request is now only trimmed at the start for `explode:`, so a padded selector can't become valid by trimming (`:51`).
- **Offline checks (raw log, `tests_final3.writes.strace` lines 62-95):**
  - the dispatched object and reply match for `""`, `,Bomb`, `,kinetic` and `,RM_Repulse_Palm`;
  - all 12 bad inputs are refused with no explosion, including `bomb`, empty, leading/trailing space or tab, `RM-Bad`, `1Bad`, `éBad`, 6 parts and 3 parts;
  - `failures=0`.

  `SwitchFlipChecks.cs:26-40` covers the same parsing on the normal SelfTest entry point.
- **Minor compatibility narrowing:** two forms the old code accepted are now refused: `…,kinetic ` with trailing whitespace (the old code trimmed it) and 6-part forms (the old code ignored extra parts). No caller in the repo uses either, so I see this as intended strictness, not a regression.

**Bullet 2 – the kinetic rows (`validation_aerial.py:1067-1147`)**
- **Real definition, no silent fallback:** in real-definition mode the row requires `damageDef == selector` and `synthetic is False`. It also requires `kinetic is True`, which comes from production `IsKineticBlast`. That check matches the `RM_KineticBlastExtension` type name (`RM_MapComponent_Aerial.cs:1180-1188`), which `RM_Repulse_Palm` inherits from `RM_RepulseBase` in the XML. A missing def fails at the probe, so there is no route back to the synthetic blast.
- **Setting readback:** the `set:` echo must match, and an independent census read of `kineticSway` must equal the requested value both before and after the blast.
- **Census deltas:** each arm builds its own fresh span and uses its own census delta. On requires a delta above 0, off requires exactly 0. The census delta must equal the blast reply's `sways`, and the cut delta must be 0 in both the census and the reply. Cumulative counters are deliberately nonzero in the test fake, so stale totals can't pass.
- **Span survival:** both anchors must be unique, match id and position, share the same net, and have exactly one `Up` link to each other. Span health must be finite and positive, equal in both directions, and unchanged by the blast.
- **Missing, failed or malformed data:** every read requires `success is True`, the echoed `cmd`, and a strictly increasing `_probeSerial`. Counters must be non-negative ints, not bools or floats. Exceptions become FAIL. The 16 unit tests cover each of these mutations at each phase (`Ran 16 tests … OK`).
- **Possible false FAIL, not a false pass:** any link whose `other` is `-1` fails `integer()`. That could fail a run spuriously but can't let a bad one through.

**Bullet 3 – the live-proof command**
- **Binding:** `GSS_CORD_SWAY_TAME_PER_FRAME_ALLOC.txt` declares `live-mods: GimmeSomeSlack, KineticArms`. It runs `kinetic_sway_proof.py`, which passes `--flips --kinetic-damage RM_Repulse_Palm` explicitly.
- **Fresh result:** `read_result` requires the output's mtime inside the run window, `mode` = flips, no `aborted`, and `kineticDamage` = `RM_Repulse_Palm`.
- **What `check_result` then requires:**
  - no FAIL or UNMEASURED rows anywhere;
  - exactly one MOD PASS row for each of M22a and M22b;
  - in each, the selector and def name are both `RM_Repulse_Palm`, with `synthetic:false`, `kinetic:true` and `harmsHealth:true`;
  - reach above 0, readback before and after, typed deltas, zero cuts and the span still up.
- **Driver success:** the driver must exit 0, and every attempt keeps its stdout, stderr and a receipt. The tests execute the registered shell line with only the live child swapped for a stub, and exit 2 is correctly rejected.

**Parent question – GSS-only callers**
- `--kinetic-damage` defaults to `"kinetic"`, and both `run_flips` and `_run_live` use `getattr(args, 'kinetic_damage', 'kinetic')`.
- That covers every existing entry point:
  - SWITCHES A1 runs bare `--flips`;
  - SWITCHES A2 runs `proof_all --live`, whose `ns()` has no `kinetic_damage` attribute, so it falls back to the default;
  - RESTRING A1 runs `restring_style_proof`, which passes no driver arguments;
  - RESTRING A2 runs bare `--live`.
- All four therefore send the synthetic `kinetic` token, as the original code did (`original/validation_aerial.py:1161`). The synthetic blast is detected through GSS's own private `RM_KineticBlastExtension`, so it works without KineticArms.
- The regression tests cover this directly:
  - generic mode with the registered def unavailable gives PASS/PASS;
  - explicit mode with it unavailable gives FAIL/FAIL;
  - the actual `main(["--flips"…])` exit codes are 0 for default, 0 for explicit with the def installed, and 1 for explicit without it;
  - both binding files still say `live-mods: GimmeSomeSlack` and contain no `--kinetic-damage`.
- The strengthened successful-read and census-delta checks apply in both modes.

**Source and build identity**
- The focused tests ran at HEAD `913a415` with rc 0. The tracked file hashes were the same before and after the run: AerialProbe `225a06d9…`, AerialMath `26f58f44…`, which the parse harness also printed.
- The shipping build came from clean `913a415` (not dirty), and the DLL hash is `c16983bc…`.
- The `.srchash` file in the tree lists the same DLL hash and the same AerialProbe and AerialMath hashes.

**Low-severity findings**
1. **Trailing-whitespace and 6-part explode forms are now refused** (detailed under bullet 1). No caller uses them.
2. **The offline harness can't test the real kinetic-marker check.** Its stand-in for `IsKineticBlast` matches by def name, so the synthetic reply shows `kinetic:false` there. Only the XML inheritance test and a future live run can confirm the real check.
3. **The normal SelfTest build is stamped with an older, uncommitted commit.** Its BUILD_SOURCE is from dirty `0cd82b62`, made before the final AerialProbe fix. This isn't material: that project doesn't compile `AerialProbe.cs` or `ExplodeProbeChecks.cs`, and the AerialMath hash is the same.
4. **Possible false FAIL on links with `other = -1`** (bullet 2 detail). It can't cause a false pass.

would show: yes