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
