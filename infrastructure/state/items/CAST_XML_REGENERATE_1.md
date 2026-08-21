## spec
`CAST_TRAIT_CONFLICTS_1` changed the `traits:` line on 14 people across eight
`design/Jawa/bridge/INHABITED_CAST_*.md` files. `src/Jawa/Inhabited/Defs/CastRosters/*.xml`
is **derived from those files and is now stale** — it still carries the impossible pairs.

```
python3 src/RimMandrake/Utils/cast_to_xml.py
```

⛔ **Do not hand-edit the XML.** The tool's own header: *"the XML it writes is derived:
delete it and re-run, never hand-edit it."* The prose files are the source of truth.

⚠️ **Expect the tool to still report the Deepwater Compact has no cast file.** That is
authoring debt (`DEEPWATER_CAST_ROSTER_1`), not a parser failure, and it is not this item.

## verify
- `cast_to_xml.py` completes and reports 269 people
- ⭐ the conflict audit returns **0**: build the pair map from the shipped `TraitDef`s'
  `conflictingTraits` and scan every `<traits>` block in
  `src/Jawa/Inhabited/Defs/CastRosters/`. It returned 0 against the **prose** on
  2026-08-21; this proves it survived the regeneration
- spot-check three by defName: `Inhabited_Tusken_HarraGhul` now carries `Ascetic` +
  `Abrasive` + `GreatMemory`; `Inhabited_Helix_PrithVane` carries `Psychopath` + `TooSmart`;
  `Inhabited_Homestead_BessaTrull` carries `Ascetic` + `Kind`

## criteria
no `Config error in Inhabited_` naming a conflicting trait pair at the next load.
