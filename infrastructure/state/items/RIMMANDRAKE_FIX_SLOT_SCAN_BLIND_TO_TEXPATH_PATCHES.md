# RIMMANDRAKE_FIX_SLOT_SCAN_BLIND_TO_TEXPATH_PATCHES

Found 2026-11-11 by CLAUDE_ARCHMAGI_OFFLINE2 (AGARILUX_PRIME_COPIES_RECONCILE_SPLIT).

`artledger.scan_def_slots` (src/RimMandrake/Utils/art/artledger.py) records only texPaths that sit under an element with a `defName`.
A `PatchOperationReplace` that repoints `graphicData/texPath` is invisible to it. `subject.World().tex_by_def` is built from those slots, and
`art_sheet.subject_row` prefers it over the live dump for our own defs ("dump texPath ... is STALE; using src ..."). So for
every patch-repointed def, the sheet's "IN GAME" column shows the UNPATCHED base-slot picture, and the picture the game really
draws appears as an ordinary render. Seen: RM_AgariluxPrime on gpt_review_therot_sheet_2026-10-24, art_eval_shadow_gptredo_03_sheet_2026-10-24,
therot_sheet_2026-11-03 and flora_legibility_sheet_2026-11-05 (column A "IN GAME — TheRot" = a 256 px donor-slot copy, never drawn).
gptredo_03 then judged the two never-drawn copies. Same exposure for the 11 defs in
RIMMANDRAKE_RETIRE_ROT_DONOR_SLOT_COPIES_ELEVEN_SHADOWED and any other patch-repointed def.

## spec
Make the src texPath read apply our own texPath/graphicClass replace patches (at least unconditional and PatchOperationConditional
`match` ones on `/Defs/ThingDef[defName="X"]/graphicData/texPath`). Alternatively, stop art_sheet overriding the dump when a patch of ours
names that def's texPath. Regression check: RM_RecurvedStropharia (still repointed) resolves to `RotSpecies/RecurvedStropharia`.
