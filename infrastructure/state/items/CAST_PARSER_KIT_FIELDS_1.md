## spec
`design/Jawa/bridge/INHABITED_CAST_*.md` now carry four optional lines that
`src/RimMandrake/Utils/cast_to_xml.py` does not read. Format and rules:
`INHABITED_DESIGN.md` §5.7a.

They sit directly under the existing `` `traits:` `` line, in the same backticked style, and
**any subset may be present or absent**:

```
`weapon: OuterRim_CyclerRifle`
`apparel: Apparel_Parka, Apparel_Tuque`
`item: BionicArm, BionicEye`
`skills: Shooting 18, Intellectual 2`
```

Parse them exactly like `TRAITS_RE` at `cast_to_xml.py:82` — one regex each, anchored, the
value split on commas and stripped. Emit them into the `Inhabited.CharacterDef` alongside
`<traits>`.

**Counts to expect** — a parse that finds fewer has a bug:

| line | count |
|---|---|
| `weapon:` | 18 |
| `apparel:` | 15 |
| `item:` | 27 |
| `skills:` | 101 |
| characters carrying at least one | **123 of 294** |

⚠️ **`skills:` is `<Name> <0-20>` pairs, not defNames.** The twelve vanilla skill names.
⚠️ **`item:` holds bionics as well as carried things** — `BionicArm`, `BionicEye`,
`BionicJaw`, `BionicLeg` all appear. Whether they are installed or carried is a
`CharacterApplier` question, not a parser one; parse them as ThingDefs and let the applier
decide.
⛔ **Do not make any of the four required.** 171 of the 294 characters carry none, and that
is the specification, not missing data.

## verify
- `cast_to_xml.py` runs clean and still reports **294** people across 12 files
- the four counts above are matched exactly
- every ThingDef named resolves — all were checked against
  `observed/2026-08-13/dumps/defnames.live.2026-08-15.json` on 2026-08-21, so a miss here
  means the parser mangled a value, not that the value is wrong
- a character with no optional lines still emits, unchanged

## criteria
The generated `CastRoster_*.xml` carries Shaa Nel with an `OuterRim_CyclerRifle` and
Shooting 18, and carries the 171 people who have none of it exactly as before.
