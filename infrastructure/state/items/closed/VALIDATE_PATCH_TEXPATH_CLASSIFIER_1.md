## spec
`validate_patch.py`'s texPath ERROR/WARN classifier false-positives on any
mod whose own `Textures/` tree happens to share a universal top-level
folder name (`Things`, `UI`, etc.) with a legitimate vanilla texPath
reference. Fix: compare against something stronger than a first-segment
match.

## root cause (measured, `RSW_Absorbed_Protovermes.xml`)
`TextureIndex.own_top` is every top-level folder name found under the
scanned mod's own `Textures/` roots (`os.listdir`). The classifier called
a texPath "this mod's own namespace, therefore ERROR" whenever its FIRST
segment matched `own_top` — but `Things` and `UI` are RimWorld's own
universal categories, reused by vanilla AND by nearly every mod that ships
any loose art at all. `RimStarWars/SWBestiary` genuinely owns
`Textures/Things/Pawn/Animal/{Cindermare,Karrask,Onnik,SeaBeasts,Skarnix,
Tellurox}/` — which puts `"things"` in its `own_top` — so a def in that
SAME mod legitimately pointing at vanilla's real
`Things/Pawn/Animal/Boomrat/Dessicated_Boomrat` (confirmed present in
Core's `resources.assets` via `extract_bundle_textures.py --only Core`,
64x64) got 3 false ERRORs, purely because `"things"` matched — even though
the mod owns no `Things/Pawn/Animal/Boomrat/` folder at all.

⚠️ **Checking one level deeper than the top segment is not enough either**
— `Things/Pawn/Animal/` genuinely exists in this same mod (holding the 6
real creature folders above), so a naive "does the immediate parent-of-
parent exist" check would still misclassify this case.

## fix
Added `TextureIndex.own_parent_exists(texpath)`: checks whether the
texPath's **full immediate containing directory** (every segment except
the final filename stem — `Things/Pawn/Animal/Boomrat`, not just
`Things`) exists under any of the mod's own roots. The classifier now
requires `top in own_top AND own_parent_exists(tp)` before calling
something "mine" — strictly narrower than before, so it can only convert
existing false ERRORs into correct WARNs, never the reverse.

## verify
- **The false positive is gone**: re-ran on `RSW_Absorbed_Protovermes.xml`
  — all 3 findings now WARN ("cannot be called a typo... check it against
  a def that already works"), 0 errors.
- **A genuine typo still errors**: synthetic test — a texPath under
  `Things/Pawn/Animal/Onnik/` (a folder this mod genuinely owns, confirmed
  containing `Onnik.png`) pointing at a deliberately nonexistent filename
  → still correctly `ERROR`, "this mod's own texture namespace." Cleaned
  up before committing (test file was never staged).
- **Project-wide regression check**: ran the validator across all 615
  `Defs/` XML files in `src/`, before and after (via `git stash` on just
  this one file, not a working-tree-wide operation). Before: 113 errors,
  89 warnings (202 total). After: 69 errors, 133 warnings (202 total).
  **Identical total finding count** — exactly 44 reclassified from ERROR
  to WARN, nothing newly appeared, nothing silently disappeared.

## NOT done
Did not investigate whether any of the other 68 remaining errors (or the
now-133 warnings) across the project are themselves further instances of
this same class needing per-case attention — that's real content-review
work, out of scope for a tooling fix. This item only had to prove the
classifier itself is now correct on both a false-positive and a true-
positive case, which it does.
