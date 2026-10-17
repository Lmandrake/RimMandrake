# Donor offline day report 2026-10-17 (FOUNDRY, no bridge, no game)
## 1. L04_TEX_OURS texture repoints
DONE. Round kept no full log, so the miss set was rebuilt from source. 17 of the 38 lines were already fixed by `0aba1c303` (post-round).
Repointed 6 `immatureGraphicPath` fields to the plants' one existing sprite; validate_patch 0 errors; deploy dry run (`--compose biomes`) shows them as drift, not applied.
Remaining 14 plants/items point at Vanilla Plants Expanded Succulents (not vanilla, in no mod list): need art. Table: `D:\Luke\dev\RimMandrake\Transient\donor_tex_fix_2026-10-17.md` (repo copy `/home/mandrake/rm/foundry/Transient/`).
## 2. P6 save rewrite
DONE on a COPY. Canonical `CANONICAL_ASHKARR_START_2026-09-12.rws` (sha 1ff32916...) untouched. Existing `_donorfree` copy still held 6 ideo icons (ports now exist) + 7 ikee rows.
New copy `..._donorfree_p6b.rws` in the Saves folder: 6 ideo icons renamed to RUT_IdeoIcon_*, parses; census: remaining donor refs = AA_Eyeling x6 + AA_EyeBody x1 (the ikee pawn, held) plus alphabiomes (report-only).
Not rewritten: SWAC tile mutators on 1429 world tiles (binary grid). Table: `Transient/phase0_p6b_save_renames.md`.
## 3. Roster gaps
Proposal only: `Transient/donor_roster_gaps_2026-10-17.md`. Bileworm = bad MayRequire `mandrake.rm.scarlands` (never existed); Zrrik = cast row gated on donor `sarg.alphaanimals`.
