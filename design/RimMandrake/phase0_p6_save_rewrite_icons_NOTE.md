# Phase 0 P6 second pass: ideo-icon refs in the donor-free save (2026-10-16)

Item `DONOR_PHASE0_P6_SAVE_REWRITE`. Tool: `src/RimMandrake/Utils/save_donor_rewrite.py` (unchanged; byte splices, CRLF kept).

- Input: `Saves\CANONICAL_ASHKARR_START_2026-09-12_donorfree.rws` (sha256 `de54dd3e9f2e5e2b11daa97432dc0f1bb423d929f400dc1675bb96ec9aba3a51`,
  17,327,511 bytes; differs from the 17,328,923-byte sha recorded in the first pass, so it was re-saved after that note).
- Output COPY (not installed, not in git): `D:\ClaudeWork\rimmandrake\scratch\p6\CANONICAL_ASHKARR_START_2026-09-12_donorfree2.rws`,
  17,327,570 bytes, sha256 `3c28ca1c394457bdb6a23e43210f4053e701377e3e70cdf4809c3d3d0a07daec`. Parses; 493,866 CRLF lines, 0 LF-only.
- Backups: `D:\ClaudeWork\rimmandrake\scratch\save_backups\CANONICAL_donorfree.rws.bak-pre-p6-icons-20261016` and `CANONICAL.rws.bak-pre-p6-icons-20261016`.
- Table: `D:\ClaudeWork\rimmandrake\scratch\p6\table.md` (the tool's output; same 6 renames and 7 holds).

Which of the 11 element refs in the input were real: all 11 (6 icon `iconDef` rows, 1 `AA_EyeBody`, 4 element-form `AA_Eyeling`;
a looser tag match finds 6 `AA_Eyeling` rows). Grid blobs were not touched.

- RENAMED (6, each 1 row, each target defined in `src/RimUtinni/UtinniPatches/Defs/IdeoSymbolDefs/RUT_IdeoIcons.xml`):
  `sw_JediGray`->`RUT_IdeoIcon_Astropolitan`, `sw_Pentastar`->`RUT_IdeoIcon_Contract`, `sw_OnderonRoyalty`->`RUT_IdeoIcon_AscendantGenome`,
  `sw_JediNova`->`RUT_IdeoIcon_Balance`, `sw_SithExarKun`->`RUT_IdeoIcon_Weight`, `sw_Bantha`->`RUT_IdeoIcon_SunDebt`.
  Output now holds 0 of the old names and exactly 1 of each new `<iconDef>`.
- HELD, untouched (ikee ruling pending; runbook step 6): `AA_Eyeling` (BS cache x2, pawnsAlive def + kindDef, things def + kindDef) and
  `AA_EyeBody` (hediff part body). `RSW_Ikee` uses the Monkey body, so the hediff cannot be re-pointed.
- Not done: world tile mutators (binary grid), game load of the copy (L1 does that), installing the copy.
