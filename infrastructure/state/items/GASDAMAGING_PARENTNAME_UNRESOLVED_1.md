# GASDAMAGING_PARENTNAME_UNRESOLVED_1 — RM_BaseGasDamaging ParentName never resolves

## what was found

Found incidentally during `THEY_MOD_REPLICATION_1`'s live-verify pass, 2026-09-28, on a
full 614-mod `Player.log`:

```
XML error: Could not find parent node named "RM_BaseGasDamaging" for node "ThingDef".
```

One occurrence on the full-list boot. Not chased down that pass — that item fixed three
other instances of the identical defect class (`RM_ChillHeatedSuit`→`Apparel_Vacsuit`,
`RM_SandBusterMound`→`Hive`, `RM_SandBusterTunnel`→`TunnelHiveSpawner`; see its own
2026-09-28 entry for the full root-cause writeup and the RimSage evidence against
`Verse/XmlInheritance.cs`).

## the mechanism (already established, re-stated here so this item is self-contained)

RimWorld's `XmlInheritance.GetBestParentFor` indexes inheritance-parent candidates
**only** by an XML node's own `Name="..."` attribute, never by `<defName>`. A
`ParentName="X"` referencing a def whose node has no `Name="X"` attribute — i.e. any
concrete/playable def, as opposed to an abstract template — silently fails to resolve,
logs `Could not find parent node named "X"`, and leaves every field that node meant to
inherit unset (for a `ThingDef`, most dangerously `thingClass`, which NREs
`ReadingPolicyDatabase.GenerateStartingPolicies()` inside `Game..ctor()` the moment the
def is active for ANY fresh `Game` — new colony, quicktest, or save load).

## what's needed here specifically

1. Find which of our `ThingDef`(s) declare `ParentName="RM_BaseGasDamaging"`
   (`grep -rn 'ParentName="RM_BaseGasDamaging"' src/`).
2. Find where `RM_BaseGasDamaging` itself is meant to be declared — check whether it
   ever carried a `Name="RM_BaseGasDamaging"` attribute (a genuine abstract template
   that regressed) or never did (same authoring mistake as the three fixed in
   `THEY_MOD_REPLICATION_1`).
3. Fix by either adding the missing `Name=` attribute to the intended abstract base (if
   one exists and was meant to be a template), or by restating the fields the child(ren)
   needed directly, same pattern as the three fixed instances.
4. Deploy, restart (minimal tier is fine — this doesn't need the full list to prove),
   confirm the specific "Could not find parent node named" line is gone and no
   null-`thingClass` Config error appears for the affected def(s).

## why this matters

Same severity class as what blocked `THEY_MOD_REPLICATION_1`'s own live verify: a def in
this state can crash `Game..ctor()` for ANY fresh game construction once it's active,
silently, with no Config-error line naming it directly (the crash is generic — "has null
thingClass" only fires from `ConfigErrors()`, which is a separate check from the
`Game..ctor()` crash path and may not always catch it depending on which field is
missing).

## a broader sweep is probably owed, not chased here

Given this is the **fourth** live instance of this exact defect class found in one day
(three in `THEY_MOD_REPLICATION_1`, this one), a repo-wide grep for `ParentName="X"`
where `X` has no matching `Name="X"` anywhere in an active mod's defs (ours or vanilla)
would likely find more. That sweep is bigger than this one def and is scoped out of this
item — worth its own item if the owner wants it done proactively rather than reactively
(one crash at a time, discovered only when something happens to construct a `Game` with
the bad def active).
