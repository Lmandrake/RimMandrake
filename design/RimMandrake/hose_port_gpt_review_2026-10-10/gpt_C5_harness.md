## Findings

Paths below are relative to `src/RimMandrake/`.

1. **BLOCKER — Moved scripts cannot import against FlowWorks’ `validation.py`.**  
   **Evidence:** `GimmeSomeSlack/validation_hose.py:49,64` imports `validation as V` and subclasses `V.Bridge`. FlowWorks’ `validation.py:31-40,108-211` provides suite wiring, not `Bridge`, `row`, `hrow`, save helpers or the other script-support APIs.  
   **Why:** Changing `HPROBE` alone leaves an immediate import failure.  
   **Design fix:** Explicitly extract mod-neutral harness support and supply FlowWorks-specific identity/configuration. Gate step 2 with import smoke tests and the moved offline scripts, with GSS unavailable.

2. **BLOCKER — Style proof still requires GSS’s aerial machinery.**  
   **Evidence:** `GimmeSomeSlack/validation_style_hose.py:127-130` imports `validation_aerial`; `:172-185` imports `validation_style`, calls its site preparation, and uses aerial `place`/`finishbuild` verbs.  
   **Why:** Moving this file and the five style patches does not produce a standalone FlowWorks proof. Keeping these imports creates a harness dependency on GSS.  
   **Design fix:** Move the generic designator/style proof operations into shared harness support and provide a FlowWorks-owned probe. Require the style proof to run with FlowWorks alone.

3. **MAJOR — The moved style offline gate retains three incompatible identities.**  
   **Evidence:** `GimmeSomeSlack/validation_style_hose.py:71` opens `RM_Hoses.xml`; `:87` requires the GSS `Graphic_HoseReel` class; `:104` requires the GSS texture-root literal in C#. V2 §5.3 renames the file to `RM_HoseReel.xml`, and §5.2 changes namespace and root.  
   **Why:** Updating only `ROOT` at line 42, as §5.4 names, still makes the offline proof fail.  
   **Design fix:** Add all three predicates to the mechanical move list and run `validation_style_hose.py --offline` in step 2.

4. **MAJOR — Removing five blocks does not remove hose use from GSS’s proof driver.**  
   **Evidence:** `GimmeSomeSlack/northstar/proof_all.py:253-258` eagerly imports both hose scripts and inherits `VH.H`; `:449-450` requires the hose probe during preflight; `:533` resets it after matrix execution. Save checks also require hose state/styles at `:714-715` and compare hose/reel snapshots at `:755-758`.  
   **Why:** Removing `BLOCKS` entries or only moving SL4 leaves GSS’s full proof broken after the scripts disappear.  
   **Design fix:** Split imports, bridge composition, preflight, matrix cleanup, save staging, **SL2 and SL3**, SL4, dispatch and restoration. Add an offline GSS full-run mock that fails on any hose-probe call.

5. **MAJOR — The row-manifest and result integration need an explicit combined contract.**  
   **Evidence:** `GimmeSomeSlack/northstar/proof_all.py:169-177` loads the GSS reduced matrix and declares **every** scene, independently of `DECLARED_ROWS`. FlowWorks’ `validation.py:155-165,182-195` reads only `validation_v2_result_*.json`; its registered suite sources are EXT/RIV at `:207-211`.  
   **Why:** Splitting `DECLARED_ROWS` alone neither splits matrix declarations nor makes hose results consumable by FlowWorks. Pointing `checkout:` solely at a hose-only manifest also needs reconciliation with the existing core rows.  
   **Design fix:** Specify a combined required-row manifest preserving FlowWorks core rows, filtered hose matrix declarations, and a current-hash hose-result reporting chain. Test declaration/emission equality, missing results, stale results and partial runs offline.

6. **MAJOR — RL6 contradicts the new provider design; it still proves debug flow only.**  
   **Evidence:** `GimmeSomeSlack/validation_hose.py:576-582` enables `flow:` and requires B’s provider to equal `"relay"`. V2 §4.3 deletes `RelayHoseFlow` and propagates debug flow through `DebugHoseFlow`.  
   **Why:** The moved row fails after step 6 even when debug propagation works. Merely changing the provider string cannot prove liquid transport.  
   **Design fix:** Update the debug-propagation predicate separately. Give the new real-flow rows explicit scheduler, tank-unit, liquid and route-stamp reads; disable debug flow throughout them. Require offline mutations for zero transport, wrong quantity, off-route credit and wrong tint.

7. **MAJOR — Reused log filtering can silently discard FlowWorks errors.**  
   **Evidence:** `GimmeSomeSlack/northstar/proof_all.py:150,154-162` treats GSS as the owned namespace and other mod frames as foreign. `:848-849` excludes foreign errors whenever their text does not name GSS. Startup checks likewise target GSS at `:400,419-420`.  
   **Why:** A FlowWorks exception can be excluded from the new driver’s log budget, producing a false green.  
   **Design fix:** Parameterize assembly, settings-entry, namespace and source ownership throughout startup/control/log filtering. Add injected FlowWorks-error fixtures that must turn the new proof red.

8. **MAJOR — Save hygiene needs one consistent job-driver exception.**  
   **Evidence:** `GimmeSomeSlack/validation_hose.py:442-444` rejects every hose-namespace occurrence. The combined driver instead permits a `curDriver` class under `GimmeSomeSlack.Hose.Jobs.` at `northstar/proof_all.py:705`; v2 §5.7 describes `FlowWorks.Hose.JobDriver_*` without that `Jobs` segment. H11 still searches only GSS classes at `validation_hose.py:483`.  
   **Why:** Blanket new-prefix rejection conflicts with legitimate mid-job saves; the removal check can miss new FlowWorks class-resolution errors. The actual moved C# namespace is outside this slice.  
   **Design fix:** Use a shared XML-aware whitelist of the actual carry/retract driver types, only under `curDriver`. Apply it consistently to H10b and SL2; update H11 to detect old, new and MessyConduit hose classes.

9. **MAJOR — SL4 can pass after losing the saved driver.**  
   **Evidence:** `GimmeSomeSlack/northstar/proof_all.py:781-786` accepts a saved Carrying reel returning Dropped and explicitly starts a replacement work job. SL2 permits zero expected driver occurrences through `expected <= carrying` at `:714`. The log budget considers only errors/exceptions at `:835`.  
   **Why:** This does not establish that the type alias resumed the saved job. A cleanup warning plus a replacement job can satisfy the state predicates.  
   **Design fix:** Keep the permissive ordinary round-trip test, but add dedicated pre-port carry **and retract** migration fixtures checking driver/toil continuity. Fail migration proof on invalid-job cleanup warnings and unresolved-class diagnostics.

10. **MAJOR — Settings rows cannot be moved as an untyped toggle list.**  
    **Evidence:** `FlowWorks/northstar/extensions.py:79-90` independently owns `liquidHosesEnabled`, field-to-settings-class mappings and defaults; unspecified defaults become boolean `True`. `FlowWorks/validation.py:40` initially copies that toggle list.  
    **Why:** Renaming the machinery chain and adding `suite.toggles` entries does not update reflection targets or restoration values. Numeric hose controls and the new look string need typed values.  
    **Design fix:** Census and update every setting registry, default and reflection mapping alongside the rows. Define Scribe-key versus runtime-field names explicitly. Add typed flip/restore tests and an all-off transport test before step 8.

11. **MAJOR — Existing FlowWorks row reporting converts SKIP into PASS.**  
    **Evidence:** `FlowWorks/validation.py:128-131` accepts `"SKIP"` without changing a component’s PASS verdict.  
    **Why:** A skipped moved proof can become passing bar/toggle evidence when routed through this adapter.  
    **Design fix:** Preserve SKIP, or report required skipped checks as UNMEASURED. Add an offline adapter test proving that skipped site-dependent checks cannot certify hose bars.

## Design claims verified

- `validation_hose.py:51` hard-codes the GSS probe namespace.
- `proof_all.py:84-101` contains the five named hose blocks and SL4.
- H10b rejects saved hose map-component/class names and requires `rmHoseState` (`validation_hose.py:442-444`).
- RL9 currently checks overhead queue ordering and span-material agreement (`validation_hose.py:593-594`).
- FlowWorks’ existing core-result lookup requires live mode and the current mod hash (`validation.py:155-165`).

## Outside this slice

- C# topology, route crediting, pump/converter/adapter/reaction/bath behavior, cache correctness, tint and runtime cost.
- Actual saved driver namespaces, aliases, Scribe fields, settings migration and Harmony application.
- SelfTest assertion preservation, defs/art, walk headers, `required_checks.py`, human-review and matrix-module implementation.
- The visible input truncates the middle of the northstar sources. The omitted machinery-chain, validation_v2, preflight and mission implementations could not receive an exact line-level audit here.