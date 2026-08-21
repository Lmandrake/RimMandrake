# Are the "missing facing" fixes real defects? — measured 2026-08-21, BUILD

**The owner's challenge, verbatim:** *"I'm not convinced there was graphical problems to
fix with BarkHead and Bandolier. I think we didn't understand how graphical assets are
stored and frequently don't carry the full SNWE full orientation... so I'd like to leave
them out until I can be shown it's a problem."*

He is **substantially right**, and one of the two fixes does not survive the check.

## The engine fact both cases rest on

`Verse.Graphic_Multi.Init`: `_north` absent falls back to `_south` with
`drawRotatedExtraAngleOffset = 180f`; `_west` absent falls back to `_east` **flipped**;
`BadMat` and `Failed to find any textures at` fire only when ALL FOUR suffixes AND the
bare path miss. ⇒ **A partially-shipped set never goes magenta**, so "no magenta" proves
nothing either way — which is exactly why this needed a different instrument.

## The instrument: compare an asset against its OWN SIBLINGS in the same folder

A convention shows up as *all* siblings behaving alike. An omission shows up as one
sibling differing.

### Bandolier — VERDICT: NOT A DEFECT. Do not activate the fix.

| bandolier | south | north | east | west |
|---|---|---|---|---|
| `bandolier_double` | 5 | **5** | 5 | 0 |
| `bandolier_knife` | 5 | **5** | 5 | 0 |
| `bandolier_chewbacca` | 5 | **0** | 5 | 0 |
| `bandolier_traveler` | 5 | **0** | 5 | 0 |

**West is 0 on all four** — the convention the owner described, exactly. West mirrors east
and nobody ships it.

🔴 **And the north gap is deliberate too, which the count alone could not show.** Rendered
side by side (`bandolier_north_evidence.png`): the knife bandolier's **authored north
carries no knives** — the author drew the back of the strap, because a rotated south would
put the sheaths on the pawn's spine. The two sets that DO ship north are the two whose
front and back genuinely differ. The two that do not — chewbacca and traveler — are plain
diagonal straps that read the same either way.
⇒ **Ship north only where it matters** is a coherent authoring decision. `KotORBandolierNorthFix`'s
own README claims the player gets *"chest pouches drawn on its back"*; the chewbacca sprite
has no pouches. That claim does not survive looking at the sprite.

### Phytokin bark head — VERDICT: STILL LOOKS LIKE A REAL OMISSION.

10 head sets in `.../Humanlike/Heads`. **All 10 ship south and north. 9 of 10 ship east.**
The only one missing east is `BarkSkinFemale_Wide_Normal` — the exact file the fix supplies.
🪤 And the accident is still lying in the folder: **`BarkSkin_Wide_Normal_east copy.png`**,
a mis-saved duplicate, beside the set that is short a file. One sibling differing, with the
slip that produced it still visible, is the opposite of a convention.
⚠️ NOT yet established: what a missing head east actually LOOKS like. Heads render through
`PawnRenderNode`, not plain `Graphic_Multi`, so the 180° fallback above may not apply.
**Do not activate this one either until someone looks at a female wide-headed bark Phytokin
walking east.** That is one spawn on any live map.

## What to keep from this

🔑 **Count the siblings before calling a facing missing.** All-siblings-alike is a
convention; one-sibling-differing is an omission. Neither is visible from the def, from a
log, or from magenta.
