## Spec
Found during `FISH_BESTIARY_COMMISSION_1`'s reconciliation pass, 2026-09-10.

`src/RimStarWars/UtinniPatches/Patches/BiomeFishTypes_Greentide.xml`'s
`fishTypes` list (closed by `FISH_TYPES_PATCH_BUILD_1`, commit `689195d3`)
includes `RSW_Mee`, `RSW_Faa`, `RSW_Laa` — but these are the scalefish
**race** ThingDefs (`SeaBeasts_Scalefish.xml`, `ParentName="AnimalThingBase"`
+ a matching PawnKindDef), not fish-item defs. `FishingUtility.GetCatchesFor`
→ `ThingMaker.MakeThing(def)` + `stackCount` has no category guard anywhere
in the path, so a net cast in the Greentide would spawn a stack of bare
`Pawn`s rather than a fish item.

RSW_Faa/Laa carry `specificMeatDef swfish_Faa`/`swfish_Laa` (their butchery
yield, not a catchable item); RSW_Mee has no associated item def at all.
The original census mislabelled these as fish-item stand-ins for the
donor's `swfish_*` items — they aren't.

## Verify
```
PROVE   a quicktest colonist fishes in a Greentide-biome water tile and the
        catch is a real item stack, not a Pawn
EXPECT  either RSW_Mee/Faa/LaaCatch (new fish-item defs) or the donor's
        swfish_Mee/Faa/Laa items appear in fishTypes instead of the race defs
LIES    validate_patch.py passing proves the XML is well-formed, not that
        the fishTypes entries resolve to the right KIND of def — this needs
        a live catch, or at minimum a `get_def_details` check that
        RSW_Mee/Faa/Laa are Pawn-category ThingDefs
```

## Criteria
- [ ] Decide: ship new `RSW_MeeCatch`/`FaaCatch`/`LaaCatch` item defs (owned
      content, consistent with the rest of the RSW_ scalefish family), or
      fall back to the donor's `swfish_Mee`/`Faa`/`Laa` items
- [ ] `BiomeFishTypes_Greentide.xml` repaired to reference the chosen items
- [ ] Live-proven via a quicktest fishing pass
