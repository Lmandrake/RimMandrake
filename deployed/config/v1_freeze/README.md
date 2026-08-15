# The v1 frozen mod state

Owner's ruling, 2026-08-14: **the current mod list is the frozen v1 list**, and
the freeze is **two files, not one**.

| file | what it fixes |
|---|---|
| `ModsConfig.xml` | which mods load — 585 active, 564 workshop · 15 local · 6 Core+DLC |
| `Mod_3521312241_Mod_CherryPicker.xml` | which defs are removed at load — 24 keys |

**The mod list alone does not define the def universe.** Cherry Picker runs at
load order 11 and deletes defs the mod list still contains, so a freeze that
covers only `ModsConfig.xml` leaves half the set undefined. Both files are frozen
here together, and a change to either is a deliberate, reviewable act.

## Restored, 2026-08-14

The live Cherry Picker config had **22** keys against the 24 in
`../Mod_3521312241_Mod_CherryPicker.24keys-gravtech-2026-08-14.xml`. Two of the
owner's picks were missing:

```
GeneDef/AG_MeatBurst
GeneDef/Turn_Gene_FleshbeastBurster
```

They were present both before and after the gravtech edit, so they were not
traded for it — something dropped them when the file was rewritten at 01:00.
Both are restored and the live file now matches the 24-key set exactly.
⚠️ **Cherry Picker applies its removals at LOAD.** The running game still holds
the 22-key set; the restore takes effect on the next cold load.

## Tooling stays in — owner's ruling

Seven active mods are tooling rather than campaign content. They are **kept**:
this is a personal campaign, nothing is distributed, and two of them are
load-bearing for our own pipeline.

| load | mod | why it stays |
|---|---|---|
| 3 | Better Stacktraces | act 5's gate is "no red errors" — traces are wanted exactly then |
| 11 | Cherry Picker | load-bearing: it *is* the item-cherrypick mechanism |
| 94 / 431 | Character Editor + retexture | the authoring route for the five founder pawns |
| 251 | Slower Pawn Tick Rate | performance |
| 566 | Dubs Performance Analyzer | profiling a ~25 min cold load |
| 569 | Performance Optimizer | performance |
| 585 | RimDefDump | ours — produces the offline def dump the whole pipeline reads |

They are recorded as tooling so the distinction survives; the list is content
plus these seven, deliberately.

## Not covered by this freeze

- **624 mods are installed but inactive** and have never been swept for something
  switched off during debugging that we actually want. `StrandedQuest` is off on
  purpose, which proves the inactive set carries decisions as well as accidents.
- **Load ORDER is not pinned.** Six `loadBottom` + `loadAfter` userRules are
  correct today but ride a tie-break rather than a constraint (BUILD B25a).
- `ModsConfig.xml` is also written by RimSort. If it moves, diff it against this
  copy before assuming the change was ours.
