## spec
🔴 **OWNER, 2026-08-20, pulling this back from v2:** *"regenerate ALL the art for
dogsled, and try your hand at the other vehicles. Get creative and try other
Tatooine-appropriate animals too from Star Wars as befits the size of the vehicles."*
⇒ `design/V2_DREAMS.md` §0c is **no longer deferred**. It was parked on 2026-08-15
(*"defer adding any additional art to B62 for v2"*); that is superseded.
✅ **DONE AND COMMITTED (`d554568`):** all three `AV_DogSled` facings regenerated.
0 REJECT from `validate_sprite.py` on each, bboxes within 1 px of the donor.
✅ **DONE — the creature art for all three remaining species**, south facing,
committed under `src/Jawa/DesertVehicleReskin/Source/art/`:
  `bantha_pair_gen_south.png` · `ronto_pair_gen_south.png` · `dewback_pair_gen_south.png`
🔴 **THE ASSIGNMENT, ruled by DECIDE from measured `baseBodySize`** — the ladder is
the point, so do not swap one for another without redoing the whole ladder:
| vehicle | donor shows | beast | bodySize | why |
|---|---|---|---|---|
| `AV_DogSled` | 4 dogs | **eopie ×2** | 1.4 | ✅ shipped. Owner's 2026-08-12 ruling, unchanged |
| `AV_Chariot` | 1 horse | **dewback ×1** | 3.0 | one beast, light and fast |
| `AV_WarChariot` | 2 horses | **dewback ×2** | 3.0 | reuses the Chariot body twice — the two chariots amortise one build |
| `AV_OxCart` | 2 oxen | **bantha ×2** | 4.0 | the horns are the read at sprite size |
| `AV_CoveredCarriage` | 2 horses | **ronto ×2** | 6.0 | the heaviest vehicle gets the heaviest beast |
✅ **DONE 2026-08-21 — SIX facings, north AND south, `0a7cf25`:** OxCart (bantha x2),
CoveredCarriage (ronto x2), WarChariot (dewback x2), each `_south` and `_north` plus
masks, all six **PASS** `validate_sprite.py` against the donor facing. Distortion
OxCart -11.4% · CoveredCarriage +4.1% · WarChariot +11.4%, all inside the ~18% rule.
🔑 **The north band is the donor's VISIBLE animal, not the animal's length.** The
wagon and the chariot are drawn over the horses' hindquarters, so CoveredCarriage's
north band is 163 rows against south's 217. Filling it distorts 40%; contain-fitting
it shrinks the beast to 80% of its south size, so the team changes size when the cart
turns. ⇒ **Size the beast from the SOUTH band, anchor it at the FAR end, and composite
UNDER the surviving art** so the donor's own bodywork occludes the overhang.
🔴 **Anchor at the FAR end even when it opens a gap at the yoke.** OxCart north is the
one facing where the ANIMAL sets the sprite's outer extent — the donor's ox horns reach
y27, five rows above the black band — so hitch-anchoring cost 45 px of span and
`validate_sprite.py` returned three REJECTs. Close the gap with the bounded stretch,
never by moving the beast off the extent it has to reach.
🔴 **The erase must dilate by 8 and drop blobs under 600 px** (GEOMETRY §1). Without it
the donor's red-tagged keyline survives and an ox-shaped white halo stands on top of
every bantha. South was rebuilt through the same path for this reason.

⛔ **EAST IS BLOCKED ON MISSING ART, and it is proven, not assumed.** Attempted with the
south pair turned 90° CCW; bands are measured and wired in `build_beast_vehicle.py`.
The donor draws east animals in **side elevation** — flank, profile head, legs under the
body — and the south pair is a plan view of the animal's BACK. Turning a plan view does
not make an elevation. The donor also staggers the pair front-to-back (GEOMETRY §3:
OxCart merges over x400–474); a turned pair stacks them flat. OxCart is the arithmetic
proof too: band aspect 1.244 against the turned pair's 0.732 — fill costs +69.9%, contain
spans 66% of the band's width. ⇒ **East needs purpose-generated SIDE-view pairs, one per
species**, exactly as the sled needed `art/eopie_pair_gen_east.png`. See the rightmost
column of `src/Jawa/DesertVehicleReskin/Source/art/review/beast_facings.png`.
⛔ **Chariot is still unbuilt on every facing** — it needs ONE dewback in a 92×182 band
and only a merged pair exists (the two animals overlap by 495 px at centre, so it cannot
be halved). Also a missing asset.

⏳ **WHAT IS LEFT: the compositing, 12 facings, and it is the real work.**
`build_eopie_sled_{south,north,east}.py` are the working pattern — read one before
starting. ⚠️ **Only the south script parses argv**; north and east hardcode their
paths, so a peer passing arguments to them gets the OLD pair silently and identical
output. Fix that first or you will debug a no-op.
**Four things measured today that will otherwise cost an afternoon:**
1. 🔴 **Fit the beast to the band by STRETCHING, not padding.** Padding preserves the
   drawing and loses span: an 84%-width pad came out 17% narrow and
   `validate_sprite.py` rejected it — *"a damaged variant may lose area but must
   still span its footprint."* An 18% width stretch on a top-down animal is invisible.
2. 🔴 **Match palettes across facings by measured per-channel gain.** Three facings
   are three generations and they drift. East came back at mean RGB (156,124,95)
   against south/north's (187,140,73); gain (1.200, 1.137, 0.761) fixed it. Without
   this the vehicle changes species when it turns.
3. ⚠️ **The generated pairs contain fragments of the donor vehicle** — the white
   chariot yoke and carriage shapes are visible at the top of the ronto and dewback
   images. Trimming to the bbox does NOT remove them. Erase them before compositing.
4. **Band geometry is already measured** in `Source/GEOMETRY.md` §3 — do not
   re-measure. South bands: OxCart 202×149 · CoveredCarriage 160×217 ·
   WarChariot 183×258 · Chariot 92×182.
🔴 **The three north facings have NO isolated hitch** (Chariot, CoveredCarriage,
WarChariot) — GEOMETRY §2. On those the dilate-8 stencil is the only route, and the
component filter must keep blobs ≥600 px or CoveredCarriage loses its wheel rims.
⛔ **Do not author `_west`** — it is auto-mirrored from east on all five.
⚠️ **The def labels stay wrong and that is a separate, cheap job**: the health tab
says `FrontLeftDog`, `LeftOx`, `RightHorse` over a picture of an eopie, and the hurt
sound is `Pawn/Animal/Dog/Dog_Injured`. Label-and-sound only, no texture iteration.

## verify
`validate_sprite.py --reference <donor facing> --candidate <ours>` reports **0
REJECT** on all 12, and each bbox is within 2 px of the donor's.

## criteria
Architect ▸ Vehicles, then spawn each of the four and rotate north/south/east.
🔴 **A Vehicle Framework vehicle spawns as a PAWN** — `jawa/list_things` returns
nothing at the cell; use `jawa/list_pawns`.
🔴 **The FALSE PASS:** the art reaches every def by texPath override whether or not
any patch ran, so seeing new art proves nothing about the def work. Only the LABEL
and the per-def colour are evidence, and the **architect menu is the tell** because
the blueprint is a third def the reskin never touches.

## notes
**Imported from `queue/BUILD.md`. Its `state:` read, verbatim:**

ready — ⭐ **TWO SIDE JOBS DONE 2026-08-20; THE 12-FACING COMPOSITING IS
BLOCKED ON A MISSING DEPENDENCY AND THAT IS THE REAL NEWS.**

🔴 **PILLOW IS NOT INSTALLED, SO NONE OF THE COMPOSITING CAN RUN AT ALL.**
All three sled builders open with `from PIL import Image, ImageDraw` and
`python3 -c "import PIL"` fails with `ModuleNotFoundError`. There is no Windows
Python beside it carrying one either. ⇒ **The 12 facings cannot be built by
anybody until Pillow is installed** — this is not a "hard" item, it is a blocked
one, and it will read as unstarted until somebody notices why.
⚠️ Same root cause as `refresh.py --offline` never completing:
`animal_contact_sheet.py` dies on the same import, which is why the offline
artefacts have stayed STALE all day. **One `pip install Pillow` unblocks both.**
⛔ Not installed by me — adding a dependency to the owner's interpreter is his
call, not mine.

✅ **DONE (1): the north builder silently ignored its arguments.** The item says
*"only the south script parses argv; north and east hardcode their paths"* —
**east actually parses argv fine; only NORTH did not.** Fixed:
`build_eopie_sled_north.py` now takes `[pair.png [out.png [cx0,cx1
[attach_y_frac]]]]`, the same shape as the other two. Before this, a peer
compositing a new species for the north facing got the OLD eopie pair written to
the SHIPPED path with a success message and byte-identical output — exactly the
no-op the item warned about, one script narrower than it said.
⚠️ Verified by `ast.parse` on all three, NOT by running them — see Pillow above.

✅ **DONE (2): the labels.** `src/Jawa/Jawa_Patches/Patches/VehicleBeastLabels.xml`,
deployed. 11 component labels across the five vehicles, following DECIDE's
bodySize ladder: Front/Rear Left/Right **Eopie** · **Dewback** · Left/Right
**Dewback** · Left/Right **Bantha** · Left/Right **Ronto**.
`validate_patch.py --defs` -> `OK - 0 errors, 11 warning(s)`.
🔑 **`label` is patched and `key` is NOT** — `key` is the component's identifier,
addressed by the vehicle's code and by its own `tags` list, so renaming it would
be a mechanical change wearing a cosmetic hat. `<tags><li>Dog</li></tags>` left
alone for the same reason.
🪤 `PatchOperationFindMod` takes the mod's DISPLAY NAME and this one is
**"Alpha Vehicles - Neolithic"**, not any of the Vanilla Vehicles names.
⚠️ **The sled has FOUR components and TWO eopies.** Component count is structural
health, not a headcount, and changing it is out of scope; the four are named
Front/Rear Left/Right Eopie, which reads for a two-by-two team. Flagged to DECIDE
rather than resolved quietly.

⏳ **NOT DONE: the hurt sound, and it is not laziness.** The sled's fleshType
`AV_WoodenAndDogVehicle` points at SoundDef `AV_BulletImpact_Wood_And_Dogs`,
whose grain list carries `Pawn/Animal/Dog/Dog_Injured`. **The replacement path
cannot be verified offline: vanilla ships its sounds inside Unity asset bundles,
not as loose files**, so no herbivore clip folder can be confirmed to exist from
disk — and a wrong clip path is a silent no-sound, which is the failure mode this
project keeps paying for. Needs a live check or a known-good path.
⛔ Only the DogSled uses that flesh type, so the fix is one SoundDef and affects
nothing else.
