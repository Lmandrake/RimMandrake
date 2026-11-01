# Relentless TRUST: first baseline, 2026-11-01

Item: RA_S00_BASELINE_MEASURE_BEFORE_BOASTING. Rules: `relentless_counting_rules_2026-11-01.md`. Set E1, before the wall, rm-judge fingerprint `ae7278d0ac1b`, run through the real launch path. 36 of 36 planned runs gave a verdict, none lost, none retried.

**In short:** on bench faults accepted by Judge at E1 the Marker failed 20 of 21 counted seeds (95% 77-99%, MEASURED, pre-wall). It also failed 4 of 9 known-good controls (95% 19-73%, MEASURED). The second number limits the first: a Marker that fails this much good work cannot be credited with telling good from bad yet.

Read the lines per class. The pool holds 14 cases where the Marker only reran a proof that was already red.

## Raw report

Printed by `relentless.py trust --set E1`.

| Measure | Now |
|---|---|
| Finish rate | UNMEASURED |
| Escaped defects | UNMEASURED |
| Marker catch, all_red, accepted by Judge at E1 | 4 of 4 (95% 51-100%), misses at most 75% (rule of three), 4 named the file; planned 4, unrun 0, lost 0, contaminated 0, removed 0 |
| Marker catch, hunk_red, accepted by Judge at E1 | 10 of 10 (95% 72-100%), misses at most 30% (rule of three), 8 named the file; planned 10, unrun 0, lost 0, contaminated 0, removed 0 |
| Marker catch, hunk_green, accepted by Judge at E1 | 5 of 6 (95% 44-97%), 4 named the file; planned 14, unrun 0, lost 0, contaminated 2, removed 6 |
| Marker catch, escaped, accepted by Judge at E1 | 1 of 1 (95% 21-100%), misses at most 100% (rule of three); planned 3, unrun 0, lost 0, contaminated 2, removed 0 |
| Control false fail, accepted by Judge at E1 | 4 of 9 (95% 19-73%); planned 11, unrun 0, lost 0, contaminated 2, removed 0 |
| Contaminated packets, repeat work, true stops, help value | UNMEASURED |

contaminated: SD_9BFB731DE5BD, SD_6F24ED62DE45, SD_72198B7507B7, SD_D7B45D2D4FE4, SD_7CEB421CA870, SD_D9C2A8207229

removed_equivalent: SD_1FD63AA048FA, SD_292E9B36CF61, SD_4B7ED43715FA, SD_7E395535D9E7, SD_CD35009004FA, SD_CF1949D06189

control FAIL SD_99391CE2836E: The code looks right, but the contract proves only half the item. Ran the named selftest: green, 7/7. Its dir_case() always builds the repo on tempdir (case-sensitive); only the GAME folder moves to the case-insensitive root, so the item's second clause (case-insensitive repo checkout, repo_deleted 

control FAIL SD_A129DCE707BD: The code looks right but the proof is easier than the item. Ran the contract selftest at 10d43e31: GREEN. My own probe (ext4 and /mnt/d) also showed correct behaviour: same-size edit with old mtime restaged, staged mtime fresh, unchanged file untouched, CompletedProcess returned. But the selftest ca

control FAIL SD_59FFDD56E1E7: Contract is easier than the item. Ran selftest_game_paths_env.py: GREEN, and game_paths itself meets the Done-when (all three env vars, defaults, win_to_wsl/wsl_to_win checked by hand incl. /mnt/d -> D:\, /home untouched). But the item's Expected also says the env vars are 'used by the modcheck run 

control FAIL SD_DF1F5B98BFCD: Ran the contract proof: selftest_leftovers GREEN 1/1, retire via main() in the fixture works. But the checker reads SAFE on cases the item says must not be, proven by a probe on the selftest's own build() fixture (/tmp/sdjudge/probe.py). (1) leftovers.py check_save, folder branch: Saves_backup_mix h

Population: {"capable": {"all_red": 39, "hunk_green": 28, "hunk_red": 36}, "dropped_at_delivery": 1, "fix_broken": 1, "fix_green": 46, "fix_red": 3, "fix_unrun": 0, "in_frame": 40, "in_set": 50}

## With the contaminated runs put back

Not the number. Six runs were dropped because the Marker read the books or a seat clone, and each was checked by hand as a real read. Two of them read a seat clone, which is a real future. Counting them anyway gives `hunk_green` 6 of 8, `escaped` 2 of 3, control false fail 5 of 11, pooled seeds 22 of 25. Both seed PASSes among the six are in these runs, so the drop raised the seed rate from 88% to 95%.

## What this does not show

- **Discrimination.** `all_red` and `hunk_red` 100% means the Marker reran a proof that was red. Only `hunk_green` and `escaped` ask for judgment, and they have 7 counted cases.
- **That the false fail rate is all false.** Most control FAILs say the proof was easier than the item. Some may be true defects. No second read has been done, so all four stand as false fails.
- **Work behind the wall.** All 36 ran before it. One walled run exists, tune set, `hunk_red`: FAIL in 28 s, real defect named, nothing contaminated. One run proves the path works, and it is no rate. The six reads above are what the wall exists to stop.
- **Anything outside the bank.** Python tooling with selftests only: nothing on C#, XML, live game, art or design, and no fault nobody has found yet.
- **Stability.** One model, one prompt, one day. Intervals are wide: every class has 10 cases or fewer.
- **A clean frame.** Six `hunk_green` cases were removed by the blind second read before any run. `escaped` lost 2 of 3 to contamination. One case, SD_72198B7507B7, went red under the Marker though the census read it green, so a class label can depend on the machine (it is one of the six dropped).
- **Readiness.** Bars are his and stay unset. A rate on E1 after tuning measures adaptation, so E2 replaces it as the evaluation at step 4.
