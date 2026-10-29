# ARTPIPE_FOREIGN_COPY_AUDIT_111_DONE_JOBS

## What happened
`arteval_RM_TruffleMole_r1_south` (canvas 256) came back 1536x1024. Root cause: image_gen gave the codex
agent no output path, so the agent copied the newest PNG from the GLOBAL `C:\Users\Mandrake\.codex\generated_images`
(an unrelated sheet of 8 bollards) into the output path. `codex_image.py` trusted any file the agent placed, so the
real mole renders in `w4/generated_images/01a169c2-.../` were never harvested. The aspect check caught it only by
luck: a square foreign image would have passed.

## Fixed
Commit 8cea1c2d5f adds the CODEX_FOREIGN_IMAGE_COPY guard to
`skills/generating-images/scripts/codex_image.py`. If the placed file is byte-identical to a cache image that
existed before the run, it is replaced by this run's newest same-suffix render; if there is none, the run fails.
Covered by selftests; a replay on the TruffleMole evidence finds the twin. The two files are still DIRTY under
`code_review_status`: two Opus reviews looked at the diff only, so they are not a full-file review.

## Audit (2026-10-24, FOUNDRY judge)
- 111 done jobs had the worker report failure while the daemon said ok. List:
  `/home/mandrake/.seat-tmp/FOUNDRY/foreign_suspects.txt`.
- 105 of them say `harvested exec-...` in `worker_stderr_tail`: the wrapper took this run's own render, so they
  are legitimate. arteval_RM_Barbslinger_r1_south (installed) is one of these.
- 6 jobs had the agent place the file: RM_Muttavaq_south, RSW_Sandstrider_north,
  dregen_RSW_Runyip_RunyipjSwimming_v1_east, nysyllin_v1_r2, rmvenomvine_v1, rut_firehawk_flying_v2_2_north.
  - nysyllin and firehawk are byte-identical to a render in their OWN worker home, so they are probably
    legitimate.
  - The other 4 cannot be traced: their caches were pruned or the files were post-processed.
  - Split: `/home/mandrake/.seat-tmp/FOUNDRY/audit/reclass.txt`.

## Spec (owed)
- Look at the 4 untraceable outputs and check each matches its prompt. Re-run any that does not.
- TruffleMole r1 south was requeued on 2026-10-24 (failed/ to pending/, manifest parked). Judge it when it lands.
- Open, lower priority (raised by the review): a run that uses the shared default home can mix up renders from
  concurrent runs.

## Verify
- Each of the 4 untraceable outputs is viewed and recorded as matching its prompt, or re-run.
- A new TruffleMole r1 south render is 1:1, shows a mole, and is judged by art-eval.
