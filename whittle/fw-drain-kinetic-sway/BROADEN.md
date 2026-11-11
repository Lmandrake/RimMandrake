# Fresh scenario broadener

Transport: read-only fresh `claude -p --model opus`, neutral temporary cwd, empty MCP, no session persistence. Exact call and raw JSON: `evidence/broaden_call.json`, `evidence/broaden_raw.json`.

## Exact question

You are a fresh read-only scenario broadener, not the maker or final judge. Read whittle/fw-drain-kinetic-sway/STATEMENT.md and NOTES.md and current GimmeSomeSlack AerialProbe/AerialMath explode path, validation_aerial.py M22 rows, restring_style_proof.py launcher, and KineticArms damage XML. Task is L0 tooling only, no live attach/deploy or appearance changes. Planned change: optional registered DamageDef name with strict malformed-name rejection, actual DefDatabase lookup and resolved identity in reply, preserve Bomb default and synthetic kinetic token; real RM_Repulse_Palm M22 on/off proof using baseline/after census deltas, independent setting readback, successful matching replies, reciprocal connected span/no cuts. Launcher must require BOTH exact fresh MOD PASS rows AND whole-driver success, retain bounded failures. What plausible user scenarios or false-pass cases should these focused production-path tests cover? Prioritize one or two revealing additions and explain why. Do not read DONE or prior judges. Return scenarios only; no acceptance verdict. Repo root: /home/mandrake/rm/scratch/BENCH/fw-drain

## Exact reply

These are scenarios only, with no verdict. I read the current source as it stands. `SwitchFlipChecks.cs:29-39` already has in-progress `ExplodeDamageName` parse checks, and I've taken those as the maker's starting point.

## Two additions I'd put first

### 1. The M22b off row needs proof that the blast was kinetic and actually reached the span

As written, M22b passes on `sways==0, cuts==0, span Up`. That is exactly what several broken setups also produce:
- **The KineticArms "Kinetic blasts cut aerial cords" setting is on.** That setting strips the `RM_KineticBlastExtension` marker at runtime (`RM_KineticArmsMod.cs:90-116`). If `explosionsCut` is also off, `BlastKindFor` returns None. The off row then passes because the blast wasn't kinetic, not because `kineticSway` is off.
- **The lookup quietly falls back to Bomb** while `explosionsCut` is off: same false pass.
- **The blast misses the span** (wrong mid cell or radius): `Notify_Blast` finds no hit and the off row still passes.
- **A registered name with `harmsHealth=false` is used.** The postfix returns early (`RM_MapComponent_Aerial.cs:1194`), so nothing happens either way.

The on row (M22a) catches some of these, but only for its own freshly built pair. Nothing ties the off row's "nothing happened" to the kinetic path.

**What I'd add:** the explode reply reports `kinetic` using the hook's own `Patch_GenExplosion_CutSpans.IsKineticBlast(def)` on the def object passed to `DoExplosion`. It also reports `harmsHealth` and a kind-independent `reached` count (spans whose ground line `SpanHit` touches). M22b passes only if `kinetic==true`, `reached>=1`, the census `kineticSways` and `explosionCuts` deltas are both 0, and both link sides keep the same `state` and `hp` before and after (the census already gives per-link `hp`, `AerialProbe.cs:226`).

**Offline test:** feed the M22 verdict a fake bridge reply of `{success:true, damageDef:"RM_Repulse_Palm", sways:0, cuts:0, kinetic:false}`, then the same with `reached:0`. Both must give non-PASS.

### 2. The launcher must pin the M22 evidence to a real resolved def, not just a row ID and PASS

`MemberwiseClone` of Bomb keeps `defName == "Bomb"`, so the synthetic token, the Bomb default and a silent fallback all report the same name. A stale driver that still sends `,kinetic` produced passing M22 rows in earlier proofs (`northstar/proof_all_20261107T031035.json:2209`). Under a launcher that checks only row ID, status and class, it would satisfy "fresh exact MOD PASS".

**What I'd add:** treat this like M15f's `schema` / `jobDef` check in `restring_style_proof.py:29-32`. Require exactly one M22a and exactly one M22b, each `class=="MOD"`, with a detail schema int carrying:
- `damageDef=="RM_Repulse_Palm"`, resolved from DefDatabase rather than echoed from the parsed string
- `synthetic==false`, `kinetic==true`
- the census readback of `kineticSway` matching the row (`"True"` / `"False"`)
- reciprocal Up on both sides, with cuts delta 0

**Offline tests:**
- a fixture with M22 rows that are PASS/MOD but `synthetic:true` or `damageDef:"Bomb"` is rejected
- a fixture where M22a is duplicated (one PASS, one FAIL) is rejected
- valid rows plus `driverReturncode=1` is rejected, and the receipt still keeps the row-level reason

## Other scenarios worth one assertion each

**Parsing and lookup**
- **Case-sensitive tokens:** `kinetic` is the synthetic token, but `Kinetic` and `KINETIC` should go through registered lookup and be rejected. Also decide what lowercase `bomb` does now. Strict lookup should give `success:false`, not a silent Bomb, even though the existing check at line 27 still holds.
- **Well-formed but unregistered names** (`RM_Repulse_Palmm`, or Palm with KineticArms not loaded): `success:false`, with lookup happening *before* `DoExplosion`. The census `explosionCuts` / `kineticSways` must not move.
- **Registered but harmless def** (`harmsHealth=false`): either reject it, or report `harmsHealth:false` so no row can count it.
- **Explicit `Bomb`:** it should resolve to the same object as `DamageDefOf.Bomb` with `synthetic:false`. The no-fifth-part default must still cut under `explosionsCut` (M15 regression).

**XML inheritance**
- Palm declares its own `<modExtensions>` list, which merges with the parent's. A `Inherit="False"` slip would silently drop the marker. Scenario 1's `kinetic` field catches this live. Offline, add an assertion that the marker list survives in the effective Palm def.

**M22 rows**
- **Setting readback:** M22 currently checks only `s.get("success")`, not `value` and not a second census read. Cover an echo that says `success:true, value:"False"` on the on row.
- **Reciprocal span:** `validation_aerial.py:1164` checks only F1→i2. Add F2→i1, and check `hp` on both sides, since a sway must not wound.
- **Reply vs census:** the reply's `sways` and the census delta come from the same counter. A test where they disagree (reply says 1, census delta 0) should fail. That catches a fabricated or stale reply.

**Launcher**
- **Timeout:** the receipt is still written, with the error, stdout/stderr and no `row`, and the return code is 1.
- **Bounded retention:** a fixture with hundreds of FAIL rows or a huge stderr, to check the receipt stays within the bound.
- **Freshness:** an output file whose mtime falls outside the start/finish window, an `aborted` result, and `mode != "live"` must each be rejected.
- **Whole-driver success:** this already requires no FAIL or UNMEASURED anywhere in `--live` (`validation_aerial.py:1778`). Make sure the launcher doesn't treat "M22 rows PASS" as enough when the driver exits 1 because of an unrelated row.

## Scenarios exercised

The two revealing additions were the marker removed at runtime / blast missing the span, and a launcher accepting old synthetic PASS rows. AerialProbe now reports the real hook marker verdict, harmsHealth and the number of standing spans in blast range; M22 requires these in both arms, plus unchanged reciprocal span hp. Focused tests inject kinetic=false, harmsHealth=false, spansReached=0, synthetic=true and Bomb identity, all requiring non-PASS. The executable launcher validates the observed schema and both exact rows, and rejects a nonzero whole-driver exit even with passing rows. It reuses the existing retained-attempt transport.

Parsing tests cover case-sensitive registered lookup and explicit Bomb, unknown and malformed selectors without an explosion, while preserving the synthetic token. XML checks verify the named Palm child and parent marker; runtime marker readback handles later patch/settings removal. Baseline/after counter tests start with nonzero cumulative totals to reveal absolute-count errors; reply/census disagreement, missing counters, wrong types and stale same-command serials fail. Span geometry uses the production SpanHit helper. These are offline instrument tests with engine doubles; no live integration or appearance result is claimed. Final runner results are recorded after these additions.

Additional source-boundary readback found that Service trimmed the whole request before parsing. The preserved pre-fix commit was replayed through the exact extracted production normalization and explode branch: three whitespace-selector cases failed the refusal check. Service now preserves explode selector text verbatim; other commands retain their trimming behavior. The updated focused harness compiles both the actual normalization and production parse/lookup branch. Evidence: `evidence/service_dispatch_red2.json` and raw external output. A new standard test run/build and independent judge follow this final source repair; the first verdict is retained as superseded.

The second independent judgment identified a generic-caller compatibility regression: GSS-only --live/--flips callers must keep synthetic kinetic. The exact no verdict is preserved in evidence/judge2_verbatim.md and external raw judge2 JSON. Replaying the actual 913a415fdf helper without KineticArms gives two FAIL rows (generic_missingmod_red). The repaired generic default sends kinetic, while the new launcher explicitly passes --kinetic-damage RM_Repulse_Palm and verifies the selected mode in the result. Actual CLI/default/explicit/missing-mod tests, synthetic rejection by the real proof launcher, and existing GSS-only bindings are covered before the final focused run.
