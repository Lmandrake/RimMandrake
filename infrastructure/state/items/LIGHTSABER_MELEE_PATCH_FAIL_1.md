# Armoury_MeleePower.xml's lightsaber PatchOperationSequence fails against the live lightsaber mod

## spec
`src/RimStarWars/Armoury/Patches/Armoury_MeleePower.xml` (mod display name
"Jawa Armoury Rebalance", packageId `mandrake.rsw.armoury`) has a
`PatchOperationFindMod` block (line 106) gated on
`Star Wars : The Force - Lightsaber` (`lee.theforce.lightsaber`, active),
wrapping a `PatchOperationSequence` of ~15 `PatchOperationReplace` calls
retuning `tools/li[label=...]/power` on `Force_Broadsaber`,
`Force_Darksaber`, `Force_LightsaberBase`, `Force_Lightsaber_Crossguard`,
`Force_Lightsaber_Curved` and others. Player.log logs the WHOLE
`PatchOperationFindMod` as `failed` (2 identical lines, confirmed present in
`Player-prev.log` too — pre-existing, NOT caused by tonight's
`WEAPONS_DONOR_RETIREMENT_1` work; unrelated donor, unrelated file).

Diagnosis not done yet: one `PatchOperationReplace` inside the `Sequence`
is presumably targeting an xpath that no longer matches (label renamed,
tools list restructured in a lightsaber mod update, or a defName typo) and
that failure cascades to make the whole wrapping FindMod report failed —
same cascade shape documented elsewhere in this session's other patch
finds. Needs: read the mod's current `tools` XML for each named ThingDef,
diff against the xpaths here, isolate and fix (or gate) the one bad entry
rather than the whole block.

## verify
`validate_patch.py --defs <Data> --defs <Mods> --defs <Workshop>` against
this file should show every operation inside the Sequence matching; and
Player.log on the next load should show zero `[Jawa Armoury Rebalance]
Patch operation ... failed` lines.

## criteria
- [ ] Bad xpath(s) identified and fixed (or gated) — the tuning intent for
      every named lightsaber stands, none silently dropped.
- [ ] Cold-load confirms zero patch-failure lines for this mod.
