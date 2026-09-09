# BLASTDOOR_LUMI_PORT_1

Owner ruling, 2026-09-08 (asked directly: port the dependency vs. retire and
accept the bug returning): **"Port the dependency first."**

## spec
`src/RimStarWars/BlastDoorFrameAsyncFix` (packageId
`mandrake.rsw.blastdoorframeasyncfix`) is a pure texture-fix mod — 6 loose
PNGs, no Defs, no Patches, no code (see
`design/validation_walks/RimStarWars/BlastDoorFrameAsyncFix.md`) — that
replaces 3 blank east-facing split-frame textures on `Lumi.doorsexpanded`'s
("Doors Expanded — Star Wars edition") own blast door ThingDefs:
`PH_DoorBlastCDoor`, `PH_DoorThickBlastBDoor`, `PH_DoorBlastDDoor`.

This fix mod is a hard `loadAfter`/functional dependent on `Lumi.doorsexpanded`
existing at all — the moment that donor retires, these textures target
nothing and the fix mod becomes dead weight, and STARWARS_DONOR_SUNSET_1's
last wave cannot close.

**Port, don't just re-texture**: copy the three blast-door ThingDefs (and
whatever supporting defs they need — check `DesignationCategoryDef`,
`ThingSetMakerDef` or recipe entries that reference them) out of
`Lumi.doorsexpanded`'s own XML into our own tier (RSW_ prefix, per
`design/NAMING_SCHEME_PLAN.md`), carrying the already-fixed textures with
them (fold `BlastDoorFrameAsyncFix`'s 6 PNGs into the new absorbed def's own
texture folder rather than leaving them as a separate override mod).
Follow this project's established absorption pattern (see how
`guy762.mm.kotorcore` content was absorbed for precedent — same repo,
`Absorbed_*` folder convention).

## verify
```
PROVE   validate_patch.py --live --defs finds the new RSW_ blast door defs,
        0 errors; xml.etree.ElementTree.parse() clean on every touched file
EXPECT  the ported def's texPath resolves to OUR OWN folder (not still
        pointing at Lumi.doorsexpanded's texPath), and BlastDoorFrameAsyncFix
        can then be retired as its own mod (folded in, not just deleted)
LIES    "the textures still work" without checking the def itself no longer
        needs Lumi.doorsexpanded active - a texture override with no def
        behind it once the donor is gone does nothing
```

## criteria
Done when the blast door content is fully ours (def + texture, RSW_ tier),
`BlastDoorFrameAsyncFix` is retired/folded, `Lumi.doorsexpanded` can be
dropped from StarWarsPatches' `loadAfter` and STARWARS_DONOR_SUNSET_1's last
wave gap is closed. Live cold-load proof is a separate step, owed to a
game-down/game-up cycle — not required to close the offline authoring here.
