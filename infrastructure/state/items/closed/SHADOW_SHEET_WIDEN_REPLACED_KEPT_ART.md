# SHADOW_SHEET_WIDEN_REPLACED_KEPT_ART

On owner_escalations_cauldron_sheet_2026-10-24 the pipeline's accepted install (Bileworm r3, CrystalMit r3, Suush r2) is column A, but the owner-kept art it replaced is not a column (Bileworm old live, Suush old south b599ac; CrystalMit old kept showed only as D). He therefore could not choose keep-vs-revert visually; he clicked no REVERT.
The skill says a redraw over kept art is flagged "replaced your kept art" with REVERT; the flag needs the old picture beside it.
Fix: shadow.py build / art_sheet must add the replaced kept picture (from its art-ledger sha, backups or git) as a column on any row whose accepted install overwrote owner-kept art.
Evidence: D:\ClaudeWork\rimmandrake\pipeline_tuning\cauldron.md (NOT_SHOWN rows).
