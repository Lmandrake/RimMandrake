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

- [x] Four live texPaths redrawn at 512x512, silhouette/style matched to the
      existing reference (same armoured-quadruped-with-tusks design, not a
      redesign).
- [x] New patch file added to `Jawa_Patches`, `PatchOperationFindMod` on the
      donor mod, texPath redirects for all four stems, hitting all three life
      stages via a value-matched xpath.
- [x] `validate_patch.py` clean against the live def dump.
- [x] `generating-rimworld-sprites`'s offline validator clean on each new PNG.
- [x] Deployed (`deploy_custom_mods.py --mod Jawa_Patches --apply`) — loose
      textures/XML are not DLL-locked, safe to deploy whether the game is up or
      down.
- [ ] In-game render is unconfirmed until the next load/lookout — note this
      plainly rather than claiming it, same as every other art item this
      session.

## Done — 2026-08-29

New file `src/Jawa/Jawa_Patches/Patches/BehemothArtUpres_StarWarsAnimalCollection.xml`,
new art under `src/Jawa/Jawa_Patches/Textures/swanimals/Behemoth/` (8 PNGs,
512x512, real alpha). Deployed via `deploy_custom_mods.py --mod Jawa_Patches
--apply` (9 files, verified in sync).

**texPath is NOT namespaced per-mod** — `ContentFinder` resolves a relative
texPath against every active mod's Textures folder, so reusing the donor's own
string (`swanimals/Behemoth/Behemoth_m`) would collide with the donor's own
bundled art. New art ships under a distinct stem, `swanimals/Behemoth/
JawaBehemoth_*`, never the donor's own string.

**North is identical between sexes** — verified `behemoth_m_north.png` and
`behemoth_f_north.png` are byte-for-byte identical in the donor's own art (a
rear/back-of-head view has no tusks or face to differ), so ONE redrawn north
image is deployed under both `JawaBehemoth_m_north.png` and
`JawaBehemoth_f_north.png` rather than drawn twice — guarantees they stay
identical rather than merely similar.

**Generation notes** (`codex_image.py`'s 120s watchdog fired "failed" on most
calls; the underlying generation had actually completed in every case —
recovered from `~/.codex/generated_images/<session>/` by directory-diff, same
pattern as the turret-art item earlier this session):
- South/east/dessicated (male) and a first north attempt all landed in one
  batch of generations; the model ignored "rear view" three times running and
  kept redrawing the front-facing bust — the reference's own north art is a
  face-less rump silhouette (no tusks, no eyes), which the model needed telling
  explicitly ("no face, no tusks are visible from this angle") before it
  produced the correct simplified silhouette.
- Female south twice came back **12-14% narrower** than the reference despite
  an explicit "do not narrow the frill outline" instruction, and once even
  with the approved male art attached as a second reference image for width
  matching. Third pass fixed it with a deterministic, non-generative step
  instead of a fourth prompt iteration: `pnglib.resize_rgba` widened the raw
  generation by the exact aspect-correction factor (0.958/0.845 ≈ 1.135x, X
  only) before cutting/conforming — this is a controlled, measured correction
  to a real generation, not a stretch masking a redesign, and the offline
  validator's span/aspect/origin checks all passed clean afterward.
- All 8 final PNGs passed `validate_sprite.py` (1 informational WARN each —
  faint alpha 1-31 fringe pixels within the silhouette, consistent with the
  soft cel-shading style, not a defect). `selftest.py` still 9/9.

**Still unconfirmed**: in-game render. Route to prove it —

```
PROVE    spawn a Behemoth (jawa/pawn_spawn or dev-mode spawn, PawnKindDef
         "Behemoth"), rotate through south/east/north, inspect the corpse
         after death
EXPECT   sharp 512px-source art (no visible upscaling blockiness vs the old
         256px), same silhouette/proportions as before across all three
         facings and both corpse variants, female showing one tusk vs male's
         two
LIES     bare-path fallback (Graphic_Multi.Init falls back to the unsuffixed
         texPath before erroring) — a mis-deployed _south file would silently
         render whatever sits at the bare `JawaBehemoth_m` path instead;
         confirm by naming the facing actually looked at, not just "it
         rendered"
```

--- history ---
