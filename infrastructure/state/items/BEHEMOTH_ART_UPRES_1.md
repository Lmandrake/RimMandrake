# BEHEMOTH_ART_UPRES_1 — redraw the Star Wars "Behemoth" at 512px

Owner, 2026-08-30 (verbatim, mid-AFK, "in the background"): *"improve the art of
the Behemoth that did not come from the Craigs. (it looks like a dinosaur with
something coming out of its jaw). It's very low res and should be made as large
as the Behemoth that DID come from the Craigs."*

## Identification — confirmed, not guessed

Two "Behemoth" creatures exist in the live mod set:

| defName | mod | texPath | source res | adult drawSize |
|---|---|---|---|---|
| `Behemoth` | Star Wars Animal Collection (Continued), `mlie.starwarsanimalcollection` | `swanimals/Behemoth/Behemoth_{m,f}[_Dessicated]`, asset-bundled | **256x256** | 8.0 tiles |
| `AA_Behemoth` | Alpha Animals, `sarg.alphaanimals` | `Things/Pawn/Animal/FO_ForsakenDragon/FO_ForsakenDragon[_Dessicated]`, loose PNG | **512x512** | 7.0 tiles |

`AA_Behemoth` is a fire-breathing dragon (description: "Legends speak of
incredibly intelligent and fierce dragons... devastating fire breaths") — not
the dinosaur. `Behemoth` (Star Wars) is described as an "armoured shaggy
quadruped animal" (its `BodyDef` label) / "Sith war behemoth", and its actual
art (viewed south/east/north, extracted via the bundle texture cache at
`observed/inventory/bundle_textures/mlie.starwarsanimalcollection/textures/swanimals/behemoth/`)
shows exactly "a dinosaur with something coming out of its jaw" — a
frilled/spiked head like a triceratops-ceratopsian and two large curved tusks,
an armored ridged back like an ankylosaur. **This is the target.**

`Behemoth` is drawn at a LARGER tile footprint (8.0) than `AA_Behemoth` (7.0)
from a texture with a QUARTER the pixel count (256² vs 512²) — the opposite of
what it should be, which is exactly why it reads as "very low res" in play.
`AA_Behemoth` — 512x512 — is what "made as large as the Behemoth that DID come
from the Craigs" means: match that pixel resolution, not the drawSize (already
fine/bigger — leave `drawSize` alone, this is an ART-ONLY item).

## Scope — the 4 wired texPaths, plus 2 unwired companions

Confirmed by reading `PawnKindDef[defName="Behemoth"]/lifeStages` in
`.../3497316713/1.6/Defs/ThingDefs_Races/Races_Animal_SW.xml:3664` — all THREE
life stages (calf/juvenile/adult) reuse the SAME four texPath stems, just at
different `drawSize`, so one PatchOperationReplace per stem (matched by current
VALUE, hitting all three `<li>` occurrences at once — see
`Jawa_Patches/Patches/GrimTerraTexPaths_Fix.xml` for the house pattern and why)
covers every life stage:

- `swanimals/Behemoth/Behemoth_m` — male, live (south/east/north + `_m` is the
  base stem; `_south`/`_east`/`_north` are the actual files, `Graphic_Multi`)
- `swanimals/Behemoth/Behemoth_f` — female, live
- `swanimals/Behemoth/Behemoth_m_Dessicated` — male corpse, live
- `swanimals/Behemoth/Behemoth_f_Dessicated` — female corpse, live

Two more exist in the donor's texture set but are **not referenced by any def**
(grepped the whole mod's XML for both, zero hits — confirmed, not assumed):
`Behemoth_mPack` / `Behemoth_fPack` (south/east/north each). Redraw these too if
time allows, for consistency, but they are not blocking — nothing in the live
game currently shows them.

## Route — retexture patch, NOT an edit to the donor mod

Same rule as `BUG_TURRET_ART_REDO_1`: the donor ships as Asset Bundles (About.xml:
"re-released using only Asset Bundles" for 1.6), but that does not matter here —
we are not touching the donor's bundle at all, only redirecting
`bodyGraphicData/texPath` (and `femaleGraphicData`, `dessicatedBodyGraphicData`,
`femaleDessicatedBodyGraphicData`) to a NEW loose-PNG path under our own
`Jawa_Patches` mod, exactly the mechanism that already works for the turret
retexture. `generating-rimworld-sprites` skill for the actual redraw (canvas
512x512, real alpha, silhouette matched to the existing reference, offline
validator) — reference art is the four 256x256 sources already extracted, listed
above.

## criteria

- [ ] Four live texPaths redrawn at 512x512, silhouette/style matched to the
      existing reference (same armoured-quadruped-with-tusks design, not a
      redesign).
- [ ] New patch file added to `Jawa_Patches`, `PatchOperationFindMod` on the
      donor mod, texPath redirects for all four stems, hitting all three life
      stages via a value-matched xpath.
- [ ] `validate_patch.py` clean against the live def dump.
- [ ] `generating-rimworld-sprites`'s offline validator clean on each new PNG.
- [ ] Deployed (`deploy_custom_mods.py --mod Jawa_Patches --apply`) — loose
      textures/XML are not DLL-locked, safe to deploy whether the game is up or
      down.
- [ ] In-game render is unconfirmed until the next load/lookout — note this
      plainly rather than claiming it, same as every other art item this
      session.

--- history ---
