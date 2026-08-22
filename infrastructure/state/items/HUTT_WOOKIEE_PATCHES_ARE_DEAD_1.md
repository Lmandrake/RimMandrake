## spec
🔴 **Two `Jawa_Patches` patches target defs that do not exist in the live game. They are
guarded, so they fail SILENTLY and have been doing nothing.** Found 2026-08-22 by running
`validate_patch.py --defs --live` over all three of our mods as a pre-load gate — 62 files,
**11 errors, all in these two**.

| patch | targets | status |
|---|---|---|
| `Patches/HuttEyes_Slitted.xml` | `BTD_Hutt` ×5 conditional groups | **ABSENT from the 578-mod capture** |
| `Patches/WookieeHead_Upgrade.xml` | `OuterRim_WookieeHead`, `BTD_Wookiee` | **both ABSENT** |

**Cause, measured:** `btd.XenotypeRemix.StarWars` is **not in `ModsConfig.xml` at all** —
zero occurrences — and no `BTD_Hutt` or `BTD_Wookiee` def survives anywhere in the capture.
The campaign migrated its species onto our own `RimMandrake*` set and these two patches were
never migrated with it.

🔑 **The successors exist and they are OURS**, which is what makes this cheap:

```
BTD_Wookiee / OuterRim_WookieeHead  ->  RimMandrakeWookiee      XenotypeDef  ours
                                        RimMandrake_WookieeHead GeneDef      ours
                                        RimMandrake_Wookiee     HeadTypeDef  ours
BTD_Hutt                            ->  RimMandrake_Head_hutt   GeneDef      ours
                                        RimMandrake_Tail_hutt   GeneDef      ours
```

⚠️ **`OuterRim_WookieeHead` → `RimMandrake_WookieeHead` is a straight rename** — same word,
new namespace.

🔴 **THIS IS THE THIRD SIGHTING OF ONE HALF-FINISHED RENAME TODAY.** `genideo.py` gated on
`OuterRim_Jawa` / `OuterRim_JawaTribal` after its output had already moved to
`RimMandrake_*` (`GENIDEO_REVERTS_DEAD_KINDS_1`, fixed `3bb39e5`). Same migration, same
`OuterRim_*` → `RimMandrake_*` shape, different file. ✅ **The sweep for more is already
done and came back clean:** the validator checked all 62 files in `Jawa_Patches`,
`RimMandrake_StarWarsRaces` and `JawaVoice` against the live capture, and these two are the
only ones left.

## What is BUILD's and what is not
- ✅ **BUILD's, and mechanical:** re-point both patches at the surviving defs, or delete them.
- ⛔ **NOT BUILD's:** whether the *intent* still stands. Do we still want Hutt eyes slitted
  and the Wookiee head upgraded, now that both species are ours and may already ship the look
  the patches were adding? **Answer that first** — re-pointing a patch that duplicates what
  our own species def already does is worse than deleting it.

## verify
`validate_patch.py --defs --live` over `src/Jawa/Jawa_Patches` reports **0 errors**, and
every remaining op in the two files is reported MATCHING rather than absent — or the files
are gone and `About.xml`'s `loadAfter` no longer names `btd.XenotypeRemix.StarWars`.

## criteria
No patch in the repo targets a def absent from the frozen capture.

## notes
⚠️ One further loose end, not an error: `src/Jawa/Jawa_Patches/About/About.xml` still lists
`btd.XenotypeRemix.StarWars` in `loadAfter`, commented *"BTD_Hutt, BTD_Jawa, BTD_Wookiee"*.
That mod is not installed. Clean it up with whichever way this item goes.
ℹ️ The gate's 12th error is a false positive worth knowing about:
`Languages/English/Keyed/ImperialVocabulary.xml` is reported as *"root element is
<LanguageData>, expected <Patch>"* — correct for a Keyed file, and only raised because the
whole mod directory was passed. Not a defect.
