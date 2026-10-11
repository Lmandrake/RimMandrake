# Standing art laws — owner rulings that bind every art brief, sheet and install

Unlike the `*.decisions.json` files beside this one (per-sheet rulings on specific variants), these are
standing laws: every artpipe brief, review-sheet builder and `art install` obeys them. Typed words are
quoted verbatim; anything else is marked as how it was decided. Promoted 2026-10-11 from the lessons inbox,
where no generator reads them.

## 1. Realistic, never cartoonish (2026-09-28)

The owner overrode 5 of 9 rows on one sheet with *"too cartoonish, more realistic"*. The prompt phrase
"painterly vanilla-RimWorld animal art style" is what produced the cartoonish read.
- Creature prompts say: realistic painted natural-history illustration, grounded anatomy, never cute.
- Every faced job carries an explicit "true rear view, no eyes/face/mouth visible" line for NORTH, because
  derived north facings keep leaking faces and mouths. Corrected pattern:
  `desert_fillout_redo_2026-09-27.csv` (desert fill-out art review, 2026-09-27).

## 2. Palette variety within a biome (2026-09-29, typed three times in one review night)

*"Your color palette is too uniform per biome. Needs more variety."*
- Every artpipe brief pushes palette diversity within the biome; a biome's cast must not share one hue family.

## 3. No geometric placeholder may ever be selectable (2026-10-07 22:33 PDT, typed)

*"make sure that at no time can geometric placeholder art ever remain a viable Variant or selection, ok?"*
- A flat single-colour circle or shape placeholder is never offered as a pickable column or variant on a
  review sheet, never installed or kept by `art install`, and a lint fails if a shipped def references one
  (dated allowlist of queued regens only).
- Context: 21 plants shipped as circles, and he picked some because sheets offered them as ordinary columns.

## 4. The Abyss's black, many-eyed family

Naming and look rulings for that family live with the biome's cast:
`design/Jawa/worldbuilding/biomes/abyss_cast_bible_2026-10-01.md` §0 rows 18-19 (pitch-black hide, four glowing
yellow eyes; the sibilant -ith/-tha/-thia names are reserved for it).
