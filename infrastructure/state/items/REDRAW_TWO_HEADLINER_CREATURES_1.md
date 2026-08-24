## spec
🔴 **THE ART FREEZE IS LIFTED FOR EXACTLY TWO CREATURES.** The standing directive is that art
*fixing* is stopped until the owner personally verifies art is broken. **He has now done that** —
he reviewed all 621 cast creatures himself in `creature_art_review.html` on 2026-08-23 and ruled
`redraw` on these two and only these two. ⛔ **This authorises NOTHING else.** Every other
creature he saw is `keep`, `shrink` or `replace`.

Both are **SUPER** band — the headliner of their biome, the one everybody looks at.

### `AA_Atispec` — Alpha Animals · cast in `Wasteland`
> *"So alien and bizarre I want to honor it. Regenerate the art to be alien, beautiful, horrible,
> and fierce."*

⭐ **Note what this is NOT.** My generator scored it **2,850 px, contrast 0.30** — comfortably
fine, and it was pre-filled `keep`. He overruled that. **The trigger was not art quality, it was
that the creature is worth honouring.** No metric in the sheet can see that, which is exactly why
he looked.

### `AA_Behemoth` — Alpha Animals · cast in `PoisonForest`
> *"It's classic, beautiful, amazing, and comes from the cold part of the world that needs some
> love. Regenerate to be truly alien, dangerous, mystical, and intimidating."*

This one the sheet did flag — 1,614 px carrying a SUPER silhouette, the weakest headliner in the
cast.

## Watch out
🔑 **Keep the silhouette.** Both are being redrawn to be *more* themselves, not replaced. A redraw
that changes the outline loses the thing he said he wanted to honour.
⚠️ Use `generating-rimworld-sprites` — it wraps the game's hard constraints (canvas, real alpha,
silhouette inside the original footprint) and ships an offline validator that rejects art before
it costs a game load.
⚠️ **Prove the current art is what you think it is first.** `reading-rimworld-graphics` covers the
`Graphic_Multi` case where a def resolves per facing; redrawing one facing and not the rest is a
silent half-fix.

## verify
Both sprites replaced, silhouette recognisably the same creature, validator clean, and the owner
looks at them. **He is the authority on whether they honour the original — no metric closes this.**

## criteria
- [ ] `AA_Atispec` and `AA_Behemoth` redrawn to his direction.
- [ ] Silhouettes preserved.
- [ ] No other creature's art touched.

## closed — owner approved at the bench, 2026-08-24
> *"Item (1) has already been approved by me. Accept and close."*

Four creatures drawn and deployed, not two: **Atispec** and **Behemoth** (the two he authorised by
name in this item), plus **Bantha** and **Eopie** — the freeze was extended to those two by voice and
that extension is recorded only in commit `25a07700`'s body. ⛔ **Nothing beyond these four is
authorised.** Every other creature he reviewed on 2026-08-23 remains `keep`, `shrink` or `replace`.
