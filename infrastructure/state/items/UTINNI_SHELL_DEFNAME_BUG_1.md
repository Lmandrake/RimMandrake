# UTINNI_SHELL_DEFNAME_BUG_1

## finding (2026-09-08, FOUNDRY)
The broken defName is generated at RUNTIME by a third-party mod, not by
anything in this repo. Confirmed: the literal string "Utinni Shellmandrake..."
appears nowhere in our code or XML — only in doc/queue text.

Source: Vanilla Backgrounds Expanded (VBE)'s RimThemes-compat shim,
`ModCompat.cs` (workshop content 2775017012), lines ~78-95:
```
var arr = key.Split('§');
var defName = arr[1] + arr[0].Replace(' ', '_');
```
`key` is RimThemes' internal dictionary key, `"{packageId}§{ThemeName}"`. For
our theme (packageId `mandrake.rut.menushell`, theme name "Utinni Shell"),
this produces `"Utinni Shell" + "mandrake.rut.menushell"` — exactly the
observed broken defName. VBE runs this unconditionally whenever RimThemes is
active, scanning every registered theme's background texture — a convention
our own `RimUtinni/MenuShell/RimThemes/Utinni Shell/` theme folder
deliberately opts into (added by the earlier fix for
`RIMTHEMES_VBE_BACKGROUND_CONFLICT_1`, a real black-screen bug).

**Impact confirmed cosmetic only**: `DefDatabase.ErrorCheckAllDefs` just
`Log.Error`s this — it does not remove the def from `defsByName`. The game is
unaffected; this is log noise on every full-list load, not a functional bug.

## why not fixed
No safe fix exists in-repo:
- The packageId's dots make ANY defName built from it invalid, regardless of
  theme name — renaming the "Utinni Shell" folder does not help.
- A real fix needs a Harmony patch on VBE's `ModCompat.cs` (or on RimThemes'
  dictionary-key format), but `MenuShell`'s own `About.xml` explicitly
  declares "no C#, no Harmony" — this mod is deliberately pure-XML.
- Removing the theme background asset entirely would regress the
  already-fixed `RIMTHEMES_VBE_BACKGROUND_CONFLICT_1` black-screen bug.

## decision owed
Accept the cosmetic log noise as the cost of `RIMTHEMES_VBE_BACKGROUND_CONFLICT_1`'s
fix, OR authorize a small Harmony assembly for MenuShell (reversing its
"no C#" convention) to intercept/rename the bad defName before
`ErrorCheckAllDefs` sees it. Not a FOUNDRY call to make solo — it changes a
mod's own stated architecture.

## verify
```
PROVE   the exact Config error string on a fresh full-list load
EXPECT  cosmetic only - no other def/behavior affected, confirmed via
        DefDatabase.ErrorCheckAllDefs source read
LIES    treating this as a rename-fixable bug in our own authoring, when the
        string is manufactured by a third-party mod at runtime from our
        packageId + theme name
```
