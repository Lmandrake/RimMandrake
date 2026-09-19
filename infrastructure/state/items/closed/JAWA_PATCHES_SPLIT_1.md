# JAWA_PATCHES_SPLIT_1

Thin item — FOUNDRY decision on spec/verify/criteria, 2026-08-31.

## spec

`design/NAMING_SCHEME_PLAN.md` §5 Phase 3: "Jawa_Patches triage; extract
the straddle packs (SacredGraffiti marks, WreckedMachines relics,
Droidworks campaign layer, Armoury doctrine patches). Each is a small
FOUNDRY item off this plan." Phase 2 (the mechanical folder/defName/
packageId migration) is already done (`git log`: "Rename Phase 2b: 31 mod
folders moved to tier dirs"); `Jawa_Patches` was deliberately parked at
`src/SPLIT_Phase3/Jawa_Patches` awaiting this per-file triage — this is
authorized, sequenced work, not renaming ahead of the gate CLAUDE.md
warns about.

`infrastructure/state/naming_rename_map.csv` carries one placeholder row
for the whole mod (`kind=mod, SPLIT, VERIFY`) with exactly this
item's brief as its note — this item exists to resolve that row.

## Scope decided by FOUNDRY, given the owner went AFK mid-session

The destination is `mandrake.jawa.patches`, the CAMPAIGN'S OWN catch-all
patch mod, loaded LAST specifically so it can patch everything else —
currently ACTIVE in the live 588-mod stack. Physically splitting 93
files (12 of them genuine content straddles needing actual judgment, not
just a file move) into three separate mods, with no owner present to
review the straddle calls and no verification cycle available before the
next restart, is exactly the high-blast-radius action CLAUDE.md's
"Executing actions with care" section reserves for a check-first pause —
unlike this session's two earlier items (brand-new, inert mods that
could not break anything already working).

**This pass produces the full classification (the decision record) and
does NOT execute the physical split.** That mirrors how the beast-norm
and seas-waterline items built a manifest before generating a patch —
except here the manifest itself, not just its execution, is the safe
stopping point, because execution touches a live load-bearing mod.

## verify

Every one of the 93 files under `src/SPLIT_Phase3/Jawa_Patches/{Patches,Defs}`
was actually read (not classified from filename alone) by five parallel
census agents, cross-checking xpath targets, defNames, comments, and the
naming plan's own tie-break rules ("a fix mod takes the tier of the mod
it fixes"; "the Jawa species is RimStarWars, this clan's culture is
RimUtinni"; "doctrine is Utinni even when it patches SW content").

## criteria

- Every file gets a tier (RUT/RSW/RM), a confidence (HIGH/MEDIUM/LOW),
  and a one-line reason. **Met**: `infrastructure/state/jawa_patches_split_map.csv`,
  93/93 rows.
- Genuine straddles (content mixing tiers, not cleanly split by moving
  the whole file) are named explicitly, not silently classified. **Met**:
  12 rows flagged, each with what the campaign-specific/generic halves
  are.
- The five named straddle packs from the naming plan (SacredGraffiti
  marks, WreckedMachines relics, Droidworks campaign layer, Armoury
  doctrine patches, JawaVoice campaign lines) are **NOT present in this
  batch** — Jawa_Patches itself carries none of those; they live in
  their own already-split mods (SacredGraffiti, WreckedMachines,
  Droidworks, Jawa_Armoury, JawaVoice) and are each their own separate
  Phase-3 item, not part of this one. One related straddle WAS found
  inside Jawa_Patches: `Defs/PawnKindDefs/JawaFactionRoster.xml`'s
  `Jawa_Droid_*` kinds mix generic droid mechanics with the Ash'karr
  Free Droid Enclaves faction — flagged for whoever does the Droidworks
  extraction.

## Summary — 93/93 classified

57 RUT · 28 RSW · 8 RM. 12 straddles (see the CSV's `straddle` column
for which; none silently absorbed into one tier).

## Not done — the physical split, owed to a session with the owner present

Executing the CSV (moving/splitting file content into
`src/RimUtinni/Jawa_Patches`, `src/RimStarWars/...`, `src/RimMandrake/...`,
updating `MayRequire`/xpaths/`Ikee_Rename`-style cross-references, then
`validate_patch.py` on all three resulting mods, then a restart to
confirm the live campaign still loads clean) needs the owner's review of
the 12 straddle calls first, plus a verification window this session
doesn't have (the AFK instruction was explicit: unfinished work becomes
a normal item, not a rushed finish). Left `doing`.

## Remaining work re-routed — 2026-09-08 (BENCH, owner present; ruling on event)
*(An earlier version of this note said "do not start the split" — stale
premise, corrected same sitting: the split already ran.)*
The Jawa_Patches per-file split itself is DONE (2385af29, 2026-09-04):
95 Patches/Defs + 70 assets moved into MandrakePatches/StarWarsPatches/
UtinniPatches; `src/SPLIT_Phase3/Jawa_Patches` is a tombstone (0 XML).
What remains, and where each piece goes:
- Cold-load proof of the successors + retiring the deployed old copy —
  rides COLD_LOAD_RUN_SHEET_3, unchanged by the sprint.
- The straddle EXTRACTIONS (SacredGraffiti marks, WreckedMachines relics,
  Droidworks campaign layer, Armoury doctrine, JawaVoice campaign lines)
  + tombstone removal — execute INSIDE the consolidation sprint:
  MOD_NAMING_CONSOLIDATION_AUDIT_1 (rulings section, 2026-09-08). Do not
  start them standalone — they ride the map the owner reviews.

## Re-verification, no action taken — 2026-09-09 (FOUNDRY, BELT)

Recounted `src/SPLIT_Phase3/Jawa_Patches` fresh rather than trusting this
file's history: **0 files** (`find ... -type f` → 0; the directory itself
is empty except its own presence). Confirms the 2026-09-08 note — there is
no TBD triage backlog left under this item. Before: 93 files (95 rows
after the +2 post-census additions) at filing; after: 0. There is nothing
left for a bulk-triage pass to pick off.

Checked whether the successor work is now unblocked: it is not.
`MOD_NAMING_CONSOLIDATION_AUDIT_1` is signed off (plan v3 + map, R1–R15
ruled, 2026-09-08) and its execution vehicle `MOD_CONSOLIDATION_SPRINT_1`
exists (`rimflow show` → state `ready`), but that sprint is explicitly
gated on `CHRONICLE_EVENT_SPINE_1`, `GRAFFITI_GENERIC_MARKS_1`,
`PYRELANDS_GENERIC_TEXT_1`, and "scheduling is the owner's call" — not
claimed, not started. The straddle extractions this item still owes
(SacredGraffiti marks, WreckedMachines relics, Droidworks campaign layer,
Armoury doctrine, JawaVoice campaign lines) ride inside that sprint per
the owner's explicit "do not start them standalone." `SPRINT_SRC_WRITE_
FREEZE_1` (the src/ write-freeze for the sprint's game-down window) is
itself `done`/closed right now — not a live blocker — but the sprint has
simply not been claimed yet, so there is nothing under this item's own ID
to execute.

**Left `doing`, not closed**: real work remains (the straddle
extractions), it is just not this item's to run standalone — it surfaces
again the moment `MOD_CONSOLIDATION_SPRINT_1` is claimed. No files moved
this pass.
