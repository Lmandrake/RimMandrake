## spec
Owner report (2026-09-14): "Nuna Tom looks like it needs regeneration." A
prior pass (2026-09-16) delivered painterly regen art (3 facings,
`pyrelands_nuna_v2_{north,south,east}.png`, canvas 256, identity from
`design/RimStarWars/canon_references/nuna/description.md`, owner's E3 ruling
honoured — thick upright bird-like legs, not a sitting frog) but left it in
`Transient/pyrelands_full_review_2026-09-16/facings/`, per that pass's own
note "not yet wired into a mod Textures/ tree."

**Which Nuna**: "Nuna Tom" is literal — `RSW_Nuna`'s `PawnKindDef` sets
`<labelMale>nuna tom</labelMale>` (`src/RimStarWars/SWBestiary/Defs/
ThingDefs_Races/RSW_Nuna.xml`). This is the MLIE-fauna-absorption port
(owner ruling, `STARWARS_DONOR_SUNSET_1`: "port Mlie's under a NEW name and
keep both"), not vanilla Core's bare `Nuna`. Its adult-male life stage uses
`bodyGraphicData.texPath = swanimals/Nuna/Nuna_m`; the adult female/chick
stages use `swanimals/Nuna/Nuna_f`.

**Already wired, discovered this session**: a same-day-adjacent commit,
`9e7e773a0` ("Wire approved Pyrelands creature render wave into art-override
mods", 2026-09-17T09:12:19-07:00 — after the 2026-09-16 "not yet wired"
note), had already copied the v2 renders into
`src/RimStarWars/NunaArtOverride/Textures/swanimals/Nuna/Nuna_m_{north,
south,east}.png`. Verified this session by md5sum: all three are
byte-identical to the `Transient/.../pyrelands_nuna_v2_*.png` files. That
same commit also gave `Nuna_f` its own distinct (not byte-identical to `_m`)
regen, fixing a separate defect ("_f facings were byte-identical to _m ...
now distinct on every facing") — not part of this item's scope but confirms
the female texPath isn't just a leftover donor copy either.

**Load-order collision found and fixed this session**: `NunaArtOverride`'s
About.xml only declared `<loadAfter>Mlie.StarWarsAnimalCollection</loadAfter>`.
But `mandrake.rsw.swbestiary` — the mod that actually owns the live
`RSW_Nuna` def — bundles its **own** copy of `swanimals/Nuna/Nuna_m/f_*.png`
at the identical relative texPath (donor-vintage art, confirmed by
md5sum: none of SWBestiary's 6 hashes match NunaArtOverride's or the v2
renders). Same-path texture resolution is decided by mod load order; with no
`loadAfter mandrake.rsw.swbestiary`, whichever of the two mods happens to
load later wins, silently reverting to the old donor art if SWBestiary loads
after the override. Added `<li>mandrake.rsw.swbestiary</li>` to
`NunaArtOverride`'s `<loadAfter>` (`src/RimStarWars/NunaArtOverride/About/
About.xml`) plus a description note, matching the pattern every other
ArtOverride mod in this repo already uses against its own donor.

## verify
- `md5sum` comparison: `Nuna_m_{north,south,east}.png` in `NunaArtOverride`
  == `Transient/pyrelands_full_review_2026-09-16/facings/pyrelands_nuna_v2_
  {north,south,east}.png` byte-for-byte. `Nuna_f_*` differ from `_m_*`
  (female-specific art, not the v2 male regen — correctly out of scope).
  SWBestiary's own bundled `Nuna_{m,f}_*` differ from all of the above
  (donor-vintage, confirmed stale — this is exactly the collision the
  loadAfter fix addresses).
- Read/eyeballed all three current `Nuna_m_*` facings: north = back of
  head/body, no face; south = face-on, eyes and jowls visible; east = side
  profile, head to the right. Matches convention and the owner's
  upright-legs ruling (all three show straight bird-like legs, not a
  crouched/sitting pose). 256x256 RGBA, consistent with the mod's other
  facings.
- `deploy_custom_mods.py --mod NunaArtOverride`: found drift (missing
  `LICENSE`, and the `About.xml` edit above), applied with `--apply` —
  now "VERIFIED in sync" against the live game Mods folder.
  `mandrake.rsw.nunaartoverride` is not enabled in tonight's (minimal) live
  `ModsConfig.xml` — standing minimal-list regime, unrelated to this item.
- No Patches exist in `NunaArtOverride` (loose Textures/About.xml only), so
  `validate_patch.py` has nothing to check; the edited `About.xml` was
  confirmed to parse as XML.

## criteria
Nuna Tom's regenerated art is present under a mod's `Textures/` tree at the
exact texPath the live def resolves, wins the same-path resolution against
every other mod that ships art at that path, and is deployed to the game's
Mods folder.
