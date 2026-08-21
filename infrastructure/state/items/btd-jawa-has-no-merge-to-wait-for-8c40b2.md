## spec
R28a's 16 `BTD_Jawa` references are resolved, and the answer needed no ruling:
🔴 **`BTD_Jawa` no longer loads at all** — it is absent from the live def dump,
exactly like `OuterRim_Jawa`. Both were replaced when the three donors went off
and `mandrake.starwarsraces` came on. Everything that named it was matching zero.
The live target is `MandrakeJawa`, which `ideoligion/APPROVED.md` already ruled
the only active Jawa xenotype.
Retargeted and deployed: `JawaAppearance_Tuning.xml` (8 xpaths) and
`JawaCombatViability_Tuning.xml` (4). They are no-ops today — `MandrakeJawa`
already satisfies all six of their conditions — and are kept as the guard that
keeps those ratified decisions true if the xenotype is regenerated from the
`.xtp`. Stale claims corrected in `JawaJunkers.xml`, `Jawa_EyeColours.xml`,
`FACTION_SPEC.md` and `tidally_locked_world.md`.

## verify
done offline against the 578-mod list: **2 files, 0 errors, 0 warnings**, and the
"0 nodes on disk" notices that flagged every dead op are gone. R28a's premise was
tested rather than believed: `MandrakeJawa` (35 genes) contains 32 of
`RimMandrakeJawa`'s 24, including the `Outland_AllMale` and `DarkVision` the doc
awarded to the smaller set alone. The only three it lacks are `Hair_DarkBlack`,
`Hair_Grayless` and `Outland_Chest_Fur` — hair, on a species ruled bald,
beardless and hooded.

## criteria
no `Could not load reference to Verse.XenotypeDef` line naming a Jawa xenotype in
the next load's `harvest_log.py --show scribe`.
⚠️ Then look at an actual Jawa: the two appearance decisions these patches exist
to guarantee are **plain head, no arachnid eyes or fangs** and **male only**. If
either is wrong the xenotype lost a gene, and the guard did not fire.

## notes
**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

ready
