## spec
`skills/rimworld-modding/scripts/validate_patch.py` recurses into `Languages/` and judges a
keyed-translation file as a PatchOperation file:

```
=== src/Jawa/Jawa_Patches/Languages/English/Keyed/ImperialVocabulary.xml ===
  ERROR   root element is <LanguageData>, expected <Patch>
FAIL TOTAL - 63 file(s), 1 error(s), 183 warning(s)
```

The file is correct. `<LanguageData>` is exactly what a keyed translation must have. The
validator is wrong to be reading it at all.

🔴 **Why this is worth an item rather than a shrug.** This tool is the **pre-load gate** —
it is what a seat runs to decide whether a cold load is safe to spend. It currently prints
`FAIL TOTAL` on a mod with zero real defects, and a gate that cries wolf gets ignored, which
is the entire value of the gate. It was already the top-line result on `Jawa_Patches` after
`HUTT_WOOKIEE_PATCHES_ARE_DEAD_1` cleared the two genuinely dead patches: 11 real errors
became 1 fake one, and the verdict stayed `FAIL`.

## What to do
Skip `Languages/` when walking a mod directory — or, better, dispatch on the ROOT ELEMENT:
`<Patch>` gets the patch checks, `<Defs>` gets the def checks, `<LanguageData>` is a
translation and is not this tool's business. ⚠️ Do not "fix" it by renaming or moving the
translation file; the mod layout is right and the tool is wrong.

⭐ While in there, one more thing that would make the gate honest: the summary line counts
`info` and `WARN` rows into a total that reads as failure. **155 of the 183 warnings on
`Jawa_Patches` are the same benign add-if-missing pattern** — `nomatch` whose inner xpath
differs from the conditional test, which the tool's own message says is "intentional for
add-if-missing patterns". Consider a distinct exit summary for "0 errors, N intentional".

## verify
`python3 skills/rimworld-modding/scripts/validate_patch.py src/Jawa/Jawa_Patches --live <dump>`
reports **0 errors** and does not print `FAIL`, with `ImperialVocabulary.xml` either skipped
or checked as a translation.

## criteria
A seat can trust the pre-load gate's verdict without reading 183 lines to find out the one
error is not real.
