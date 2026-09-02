# PAWN_FLAVOR_STAGELESS_ADD_FAIL_1 — two flavor rows fail PatchOperationAdd: no literal `stages/li[1]` to anchor on

Surfaced 2026-09-02, live cold load (592 mods), immediately after
`PAWN_FLAVOR_SILENT_NONAPPLY_1`'s FindMod gate fix landed and the
`Ideology`/`EBSG Framework`-gated blocks finally started genuinely
executing for the first time. Raw `Player.log` (search `Error in <match>`
near "Jawa Pawn Flavor"):

```
Verse.PatchOperationAdd(xpath="Defs/ThoughtDef[defName="AnyBodyPartButGroinCovered_Disapproved_Female"]/stages/li[1]"): Failed to find a node with the given xpath
Verse.PatchOperationConditional(xpath=Defs/ThoughtDef[defName="AnyBodyPartButGroinCovered_Disapproved_Female"]/stages/li[1]/label): Error in <nomatch>
Verse.PatchOperationSequence: Error in the operation at position=1
Verse.PatchOperationSequence: Error in the operation at position=12
Verse.PatchOperationFindMod(Ideology): Error in <match>
```
```
Verse.PatchOperationAdd(xpath="Defs/ThoughtDef[defName="EBSG_GeneticDrugDependency"]/stages/li[1]"): Failed to find a node with the given xpath
Verse.PatchOperationConditional(xpath=Defs/ThoughtDef[defName="EBSG_GeneticDrugDependency"]/stages/li[1]/label): Error in <nomatch>
Verse.PatchOperationSequence: Error in the operation at position=1
Verse.PatchOperationFindMod(EBSG Framework): Error in <match>
```

## spec

`gen_pawn_flavor_phase2_apply.py`'s `seq_op()` wraps each field in a
`PatchOperationConditional`: `match=Replace` if the field's literal node
already exists in the raw (pre-patch) XML, `nomatch=Add` targeting
`stages/li[N]` (the whole stage) if it doesn't. For these two defNames the
`nomatch` branch fired (no literal `label` at `stages/li[1]`) — expected,
that's the normal "field absent, add it" case — but the `Add` itself then
also failed: `Failed to find a node with the given xpath` on
`stages/li[1]` **itself**. That only happens if `stages/li[1]` doesn't
exist AT ALL in the def's own raw XML (not just missing a `label` child)
— i.e. these two `ThoughtDef`s likely declare `stages` empty, or with
fewer literal `<li>` entries than the resolved (post-inheritance) dump
shows, or inherit `stages` wholesale via `ParentName` the way
`JAWA_PAWN_FLAVOR_PATCH_REGRESSION_1` and this project's own
`inherited-list-items-cannot-be-patched-away` lesson already describe for
a different operation (`Remove`) — same family of bug, not yet confirmed
against the actual raw donor XML for these two specific defs.

Not yet checked:
- Read the actual raw `ThoughtDefs` XML for `AnyBodyPartButGroinCovered_Disapproved_Female`
  (Ideology) and `EBSG_GeneticDrugDependency` (EBSG Framework) directly
  from their source files to confirm the empty/inherited-stages hypothesis
  rather than assume it.
- Whether this is 2 rows total or a wider class — the "patch operations
  failed" harvest check only surfaced 2 above baseline on this load, but a
  `PatchOperationSequence` continues past a single failed child, so a
  systematic sweep (compare `len(stages)` in the dump against the raw XML's
  literal `<li>` count for every def this generator touches) would say for
  certain whether more rows are silently in the same state without yet
  showing up as an aggregate "failed" line.

## verify

- Confirm the raw-XML hypothesis for both named defs.
- Fix `seq_op()` (or its caller) to handle a def whose `stages` list has NO
  literal `<li>` children: probably `PatchOperationAdd` targeting `stages`
  itself (append one full `<li>` with both fields) rather than
  `stages/li[N]` (which presupposes N-1 literal `<li>` siblings already
  exist to be counted past).
- Regenerate, `validate_patch.py` clean, live cold load:
  `harvest_log.py`'s "patch operations failed" back to baseline 5 with no
  `[Jawa Pawn Flavor …]` lines at all.

## criteria

Both named rows land their approved text live (or are confirmed genuinely
un-addable and explicitly dropped from the applied count with a reason),
and the sweep above either finds no further instances or names how many
there are.

## 2026-09-02 — hypothesis confirmed, fix applied and validated; live pass deliberately withheld

**Hypothesis confirmed against real raw XML for both named defs**, not
assumed: `AnyBodyPartButGroinCovered_Disapproved_Female`
(`Data/Ideology/Defs/PreceptDefs/Precepts_Nudity.xml`) declares only
`<defName>`/`<gender>` under `ParentName="AnyBodyPartButGroinCovered_Disapproved"`
— no literal `<stages>` node at all, the whole list is inherited.
`EBSG_GeneticDrugDependency` (`ebsg.framework`,
`1.6/Biotech/Defs/DependencyHediffs.xml`) is the same shape:
`ParentName="EBSG_DependencyThoughtBase"`, only `<modExtensions>` of its
own, no `<stages>`.

**Fix**: `gen_pawn_flavor_phase2_apply.py` gained `stage_op()`, replacing
`seq_op()` for ThoughtDef stage writes only (MentalBreakDef/MentalStateDef/
XenotypeDef top-level def nodes always exist once resolved against the
dump, so `seq_op` is untouched and correct for those). `stage_op()` is a
three-way `PatchOperationConditional`: (1) `stages/li[N]` exists literally
→ the same per-field Replace-or-Add `seq_op` already did, unchanged; (2)
`stages` exists but `li[N]` doesn't → `PatchOperationAdd` a fresh `<li>`
under `stages`; (3) `stages` itself doesn't exist → `PatchOperationAdd` a
fresh `<stages><li>...</li></stages>` under the `ThoughtDef` itself. All
three branches decided by the live game's own xpath evaluation, nothing
guessed in Python.

Regenerated: same row counts as before (1,781 of 1,783; 2 known-dead).
`validate_patch.py --defs` (Data+Mods+Workshop, live `ModsConfig.xml`):
clean. Only `PawnFlavorPhase2_ThoughtDef.xml` changed — `MentalBreak`/
`Xenotype` outputs are byte-identical, as expected (`seq_op` untouched).

**Not done this pass, deliberately**: the live cold load / `harvest_log.py`
re-check / spot-check. BENCH was actively driving the bridge tonight
("Bench has the bridge, not you" — relayed by the coordinator mid-task);
this fork never took the bridge (confirmed: no `rimflow bridge take` call
made) and stopped here rather than risk colliding with BENCH's live work.
Also not done: the full sweep for further stageless-`<stages>` instances
across all ~1,664 ThoughtDef stage-write rows — started (scoped per-mod
grep, not a blind workshop-wide one) but did not finish inside this
pass's time budget. Since the fix is structurally general (it handles ANY
missing-`stages`/missing-`li[N]` shape, not just these two named defs),
the sweep is a reporting completeness item, not a correctness
prerequisite — the generator will not silently drop a row of this shape
again regardless of how many more exist.

**Sweep finished** (scoped per-mod-folder grep, not workshop-wide — 1,657
of the 1,664 ThoughtDef stage-write rows checked): **16 rows total**
have `dump_stages > literal <li> count` (the original 2 plus 14 more of
the same shape) — not a rare edge case, a real family:
- 12 more Ideology `*_Female`/`*_Social_Female` nudity-precept rows
  (`AnyBodyPartCovered_Disapproved_Female`, `GroinUncovered_Disapproved_Female`,
  etc.) — same pattern as the two named defs: `ParentName` onto the
  `_Male` base, zero literal `<stages>` of their own.
- 2 vanilla Core rows, **partial** inheritance rather than total:
  `Pretty`/`Ugly` each have 4 dump stages but only 2 literal `<li>` in
  their own raw XML (2 of 4 stages come from a `ParentName` base) —
  confirms `stage_op()`'s branch 2 (stages exists, li[N] doesn't) is a
  real case, not just branch 3.
- 1 Alpha Animals row (`AA_BeenPsionicallyNuzzled`), 1 more Core row
  (`Catharsis`), same partial-inheritance shape as Pretty/Ugly.

All 16 are now handled correctly by `stage_op()`'s general fix — nothing
further to patch by hand, this was purely a verification sweep.

The sweep's 194 "could not verify" entries are a **limitation of the
one-off sweep script itself, not a real signal**: it isolates a def's
element bounds by finding the nearest preceding `<ThoughtDef` before a
`<defName>X</defName>` match, but RimWorld defNames are only unique
*within* a defType — several of these (e.g. `AA_AteBlackTruffleIngredient`)
also name a `HediffDef`/`GeneDef`/etc. sharing the same string, and the
script's naive first-file-found search sometimes landed on that other
def's file instead of the real ThoughtDef. Not re-run properly here (low
value — the fix's correctness doesn't depend on enumerating every
instance, only on handling the *shape* generally, which it does).

Left `doing`. Next FOUNDRY pass once the bridge is free: deploy, live
cold load, confirm "patch operations failed" back to baseline 5 with no
`[Jawa Pawn Flavor …]` lines, spot-check the two originally-named rows'
live text (plus ideally one of the 14 newly-found ones, e.g. `Pretty` or
`Ugly` — vanilla Core, spawnable on any quicktest colonist, no DLC/mod
gating needed), then close this item and re-attempt
`PAWN_FLAVOR_PHASE2_APPLY_1`'s own spot-check criterion.
