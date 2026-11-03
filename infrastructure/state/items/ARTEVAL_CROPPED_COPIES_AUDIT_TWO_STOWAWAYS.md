## spec
Found 2026-11-02 by the FOREIGN_GUARD_WIDEN_MIRROR_CROP census calibration: two artpipe outputs that the
old foreign-copy guard passed as "ok" are CENTRE-SQUARE CROPS of unrelated 1536x1024 renders in the shared
base home (`C:\Users\Mandrake\.codex\generated_images`), made hours before their jobs existed:

- `arteval_RM_Dustflutter_r1_east` (generate, placed 2026-10-23 17:01Z) = a sheet of bollards, centre square of
  `01a16960-840f-77e2-9a73-8f726b7d3238/exec-db15843c-....png` (15:29Z); picture distance 0.78, detail 0.99.
- `arteval_RM_Peeper_r3_south` (edit from r3_east, placed 2026-10-24 09:12Z) = a pipe flange, centre square of
  `01a16c75-8c13-7ec3-b3f8-ac4e9d43dfb7/exec-a90f0b59-....png` (05:50Z); distance 0.63, detail 1.00.

Side by side: `D:\ClaudeWork\rimmandrake\guard_vet\mirrorcrop\crop_pairs.png`; rows in
`D:\ClaudeWork\rimmandrake\guard_vet\mirrorcrop\calib.tsv`. The widened guard now refuses both.

## verify
Every judgement, sheet row, install or regen decision that consumed either output is undone or re-run on a real
render (neither creature should carry that art anywhere); grep the art ledger and sheets' .decisions.json for the
two job ids.
