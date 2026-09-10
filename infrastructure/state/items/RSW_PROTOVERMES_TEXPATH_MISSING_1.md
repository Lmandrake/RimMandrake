## spec
`validate_patch.py` flagged `RSW_Absorbed_Protovermes.xml`'s `PawnKindDef
'RSW_Protovermes'` with 3 ERRORs: `<texPath>Things/Pawn/Animal/Boomrat/
Dessicated_Boomrat</texPath>` — "no file, folder or _north/_south/_east/
_west variant of that path exists under any Textures/ root scanned...
renders as a pink placeholder." Found as a side effect of
`BOOM_FAMILY_CUT_1` (this file's `useMeatFrom` was also touched there, for
an unrelated reason — cutting Boomrat's ThingDef — confirmed via `git diff`
that edit never came near this `texPath` line).

## finding: false positive, not a game defect
Per the `reading-rimworld-graphics` skill's core lesson ("renders in game
but comes up blank offline ⇒ the art is bundled, not missing"): ran
`extract_bundle_textures.py --only Core` (fresh, since the cached
`observed/inventory/bundle_textures/index.csv` only held one unrelated
mod's textures — Core's `resources.assets` had never been extracted into
it). `Dessicated_Boomrat_east/_north/_south` all exist in
`ludeon.rimworld.core`, 64x64. **The texture is real and resolves in the
running game.** `RSW_Protovermes` is not broken.

## root cause: `validate_patch.py`'s ERROR/WARN split is fooled by a
   coincidental top-level folder name

Read the classifier (`skills/rimworld-modding/scripts/validate_patch.py`,
around line 2062-2087): when a texPath doesn't resolve against the loose
files it scanned, it decides ERROR vs. WARN by checking `top = tp.split
("/")[0].lower()` against `tex.own_top` — the set of top-level folder
names the SAME mod's own `Textures/` tree uses anywhere. If `top` is in
`own_top`, it calls this the mod's own namespace and errors ("nothing else
can supply it"); otherwise it correctly warns that a vanilla `Things/`
path is indistinguishable offline from a typo.

The bug: **"Things" (and "Pawn", "Buildings", etc.) are RimWorld's own
universal top-level texture categories, reused by vanilla AND by nearly
every mod that ships any loose art at all.** `RSW_Absorbed_Protovermes`'s
OWN mod tree almost certainly has *something* under its own
`Textures/Things/...` too (for other defs), which puts "things" in
`own_top` — so a texPath that happens to ALSO start with `Things/` but is
actually pointing at VANILLA content gets wrongly classified as "this
mod's own namespace, therefore ERROR" instead of the correct "ambiguous,
cannot be called a typo offline, WARN." This is a general false-positive
class, not specific to this one def — any mod with its own `Things/`
subfolder that ALSO legitimately references a vanilla `Things/...` texPath
will hit it.

## NOT done — the validator fix itself
Did not change `validate_patch.py`. The right fix (compare against a
short, fixed list of RimWorld's own universal top-level categories —
Things, Pawn, Buildings, Terrain, UI, etc. — and never classify a texPath
starting with one of THOSE as "mine" purely from a first-segment match) is
a real, separate change to a shared tool used project-wide, and a wrong
heuristic there risks new false negatives (missing a real "mod's own
namespace" typo) as easily as it fixes this false positive. Filed as its
own item rather than guessing at a fix under this item's scope.

## verify
`extract_bundle_textures.py --only Core` (this session) →
`Dessicated_Boomrat_east/_north/_south` present in
`ludeon.rimworld.core`, confirmed via `observed/inventory/
bundle_textures/index.csv`.
