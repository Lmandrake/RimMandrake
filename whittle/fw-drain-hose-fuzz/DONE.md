# Evidence per frozen statement

- true: The hose fuzz family proves meaningful successful lay coverage and cannot pass when every generated hose lay is refused. | evidence: `whittle/fw-drain-hose-fuzz/evidence/proof_checks.json` `whittle/fw-drain-hose-fuzz/evidence/source_diff.patch`
- true: Executable production-linked controls demonstrate the old false pass and repaired failure, while legitimate individual refusals and supported single-seed/debug modes remain usable. The relevant FlowWorks selftest passes on final sources. | evidence: `whittle/fw-drain-hose-fuzz/evidence/proof_checks.json` `whittle/fw-drain-hose-fuzz/evidence/selftest_receipt.json` `whittle/fw-drain-hose-fuzz/evidence/csharp_stdout.txt` `whittle/fw-drain-hose-fuzz/evidence/selftest_stdout.txt`
- true: Evidence identifies the exact tested source and its limits. The repair preserves shipping behavior and the approved GSS cord appearance. | evidence: `whittle/fw-drain-hose-fuzz/evidence/proof_checks.json` `whittle/fw-drain-hose-fuzz/evidence/integrity_after_test.json` `whittle/fw-drain-hose-fuzz/evidence/stage_identity.json` `whittle/fw-drain-hose-fuzz/evidence/output_extraction.json`

## Coverage and limits

The source change is confined to `src/RimMandrake/FlowWorks/Source/SelfTest/HoseFuzz.cs`. Normal positive-scale hose runs require seed 2 to pass the real RunHose checks in both outlet and free modes. The fixture must have a nozzle, both lays must succeed, and both must avoid fallback. Failures enter the existing family failure tally and grouped diagnostics. Random case, step and laid counters exclude these fixed witnesses.

Explicit `--fuzz-seed` runs retain refusal-only debugging. Their summary states that successful lay coverage is optional. Scale zero retains the existing skip. Trail-only selection retains its existing scope. These modes provide the coverage described by their output. A deterministic witness establishes successful invariant exercise in each actual mode. It provides no minimum random-sample success ratio.

## Executable observations

The original full-scale isolated total-refusal mutant reports PASS with 2,798 cases, 8,200 steps and zero lays. The final source with the byte-identical whole mutated HoseMath reports a family FAIL with two coverage failures. Outlet-only and free-only refusal each produce one mode-specific family coverage failure. Tiny-scale production, g2/g2off, refusal-only seed 18, partial-refusal seed 7, positive seed 2, disabled fuzz and trail-only controls are saved under the final fast-control directories. The actual C# entry point also exercises g2/g2off, seed-18 debugging and total refusal. Raw stdout and input hashes are indexed in `evidence/proof_checks.json`.

The only full wrapper invocation was `python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/Utils/selftest_flowworks_stock.py --workers 1`. It returned zero. Captured actual C# stdout reports 1,240/1,240 cases, 457/457 hose assertions, HoseFuzz 4/4, 2,409 sampled lays, and 2/2 successful checked witnesses. Before/after hashes match, as do staged source inputs. The installed assembly and reused engine-reference hashes match their provenance.

One earlier actual-entry staging attempt failed before C# compilation because the staging script read a generated MSBuild Compile entry as a static filename. Its console, partial inputs and diagnosis remain in `evidence/entry_g2_console.txt`, `evidence/fast_entry_g2/` and `evidence/entry_g2_preparation_failure.json`. The retry used the actual unchanged project and its original generation target. All pre-broaden fast controls remain preserved alongside final controls.

The runner refused known-result cache recording on absent-input directory mtimes, clock reads and Windows external inputs. The raw refusal is preserved in `evidence/cache_record_refusal.json`. The executed result is PASS, supported by raw stdout and stable source hashes. The runner and its cache logic received no edits.

The whole observer trace and runner logs remain at `/mnt/d/ClaudeWork/rimmandrake/codex_wsl/fw-drain/hose-fuzz-raw/`. Extraction kept the original trace intact. The proof covers offline kernel and selftest behavior. Live gameplay and visual acceptance are outside this proof. Full-mod/tool/media hashes cover shipping and approved-art byte identity during the final proof and review.

Parent retains publication, ledger updates and closure. Independent judgment and explicit workflow validation follow this evidence claim.

## Control-build overlap

Three focused actual-entry control builds overlapped the one authorized wrapper run. They used separate isolated scratch stages and build outputs and bypassed the wrapper’s dotnet lock. The wrapper’s captured C# output and its independently measured stage identities establish the production result. This run had concurrent build load. Exact intervals and stage paths are preserved in `evidence/control_overlap.json`.
