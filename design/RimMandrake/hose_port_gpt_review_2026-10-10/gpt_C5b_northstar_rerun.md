## Findings

Paths below are relative to `src/RimMandrake/FlowWorks/northstar/`. Line numbers refer to the supplied text.

1. **MAJOR — The settings move list misses independent harness registries.**  
   **Evidence:** `extensions.py:79-90` independently registers `liquidHosesEnabled`, its owning settings type and restoration default; `_setting` indexes that registry at `extensions.py:262`. `validation_v2.py:84-110` has separate defaults tables containing neither machinery nor hose settings. Preflight checks coverage against `site_spec.toggles()` at `preflight_flowworks.py:158` and reads defaults from `site_spec.SETTINGS` at `:405`.  
   **Why:** Updating only `validation.py`’s `suite.toggles`, as §5.7/step 4 specifies, leaves stale-field calls or silently excludes new settings from defaults checks. A renamed field absent from `SETTINGS_OF` raises `KeyError`.  
   **Fix:** Explicitly census/update these registries and `site_spec` in steps 4–5. Require equality between expected settings and harness coverage, with typed checks for numeric and look settings. Extend the all-off fixture to include machinery, river and hose switches.

2. **MAJOR — Missing renamed settings can pass preflight.**  
   **Evidence:** `preflight_flowworks.py:409-413` records “No public field” as `ABSENT` and skips adding a failure. `:421-425` then reports PASS whenever `bad` is empty, counting even absent fields as “at shipped defaults.”  
   **Why:** A stale `liquidHosesEnabled` entry after the rename—or an undeployed hose setting—can produce a green settings gate.  
   **Fix:** Keep `ABSENT` for diagnostic snapshots, but make required absent fields fail `P-B4`. Add an offline negative test where the renamed pipe field and a hose field are unavailable.

3. **MAJOR — Log hygiene misses the proposed mixed-version error and job cleanup warning.**  
   **Evidence:** `preflight_flowworks.py:348-352` recognizes only config errors, XML errors, duplicate-def messages and exceptions; `:361` applies only those patterns. V2’s exact proposed message, “Gimme Some Slack is older than this FlowWorks; update both,” matches none. “Cleaning up invalid job state” also matches none.  
   **Why:** Step 8 can receive PASS from this log gate while the port reports an unsupported mixed installation or drops a pawn’s migrated job.  
   **Fix:** Add explicit patterns for the mixed-version diagnostic, unresolved legacy hose classes and invalid-job cleanup. Test each message offline; do not rely on the word “Exception.”

4. **MAJOR — The 60-tick rebuild bar conflates port discovery with scheduled transfer.**  
   **Evidence:** `extensions.py:92` fixes `PULSE=250`; `_wait` rounds every requested delay up to whole pulses at `:214-217`. V2 §5.7 nevertheless requires rebuilt-port flow to resume within 60 ticks, while §4.2 specifies a 250-tick pump cadence.  
   **Why:** `_wait(60)` observes after 250 ticks and cannot prove a 60-tick bound. Conversely, a correct pump need not transfer during the first 60 ticks after rebuilding.  
   **Fix:** Split the predicate: discover the replacement port within 60 ticks, then transfer by the next pump cycle. Use exact tick stepping and record observation timestamps for timing bars.

5. **MAJOR — The mission chain goal can pass without liquid traversing the tested hose.**  
   **Evidence:** `player_missions.py:677-688` searches tanks globally, inspects the first three and takes their maximum existing stock. `:692-693` compares that stock with a threshold; it checks neither a designated destination nor a transfer delta. The health read at `:672-675` also treats a failed reply without pawns as “no injuries.”  
   **Why:** An unrelated filled tank can satisfy the goal while the hose is wound, disconnected or inert. Failed health/selection reads can further weaken the result. This existing defect makes the mission unsuitable as evidence for the new real-flow bars.  
   **Fix:** Bind the destination tank by identity and fixture location; compare baseline/end units and liquid identity across controlled cycles. Require successful reads and selection. Add negative fixtures with an unrelated full tank, an inactive hose and unavailable readers.

## Design claims verified

- `machinery_hoses` builds a pump, five static `RM_LiquidHose` cells and a distant tank, then exercises `liquidHosesEnabled` OFF. Renaming that fixture to pipes is appropriate; it currently proves no flexible-reel behavior.
- Extensions are explicitly excluded from the default core proof (`extensions.py:21-25`).
- `validation_v2` has offline oracle checks and fault-injected mock checks. Their present model covers excavation mechanisms, not hose links or route crediting.
- Golden-site contracts reject changed FlowWorks DLLs and defs (`preflight_flowworks.py:267-270`); the port requires regenerated trial fixtures.
- The mission fake explicitly describes its physics as a toy that proves nothing about FlowWorks (`player_missions.py:163-166`).

## Outside this slice

- `validation.py`, `proof_all.py`, moved hose validators, extension-driver dispatch and their selftests: complete row/block migration cannot be verified.
- Walk `checkout:` parsing and result joining: verify that adding `proof_hose.py` preserves existing `validation_v2.declared_rows()` coverage.
- `site_spec.py`, mission JSON/brief and backup implementation: registry contents, mission def references and legacy-settings backup coverage.
- Production C#, `HoseProbe` output, save aliases and shared sources: actual topology, transfer, tint, cache and save compatibility.
- This was a static audit; the supplied modules were not executed.