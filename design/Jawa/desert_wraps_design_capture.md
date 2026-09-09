# Desert Wraps + Devolved Head — design capture

**Status: capture taken 2026-09-09 pre-unsubscribe; source mod described from observation, no assets copied.**

Source: Steam Workshop item 3665584152, "Rimwars - Sand People Xenotype (Continued)",
inspected on disk at
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3665584152\`.
This document is prose + numbers only. No image file, palette swatch, or pixel data
from the source mod is reproduced or derived here; all hex values below were read
off-screen with an eyedropper/histogram tool and are reported as *facts about the
source asset* (its own colors), not as copyable material. Def field names, values
and XML structure are game-mechanism facts (uncopyrightable) and are quoted verbatim
for that reason only.

---

## 1. The Wraps* body-apparel family

### 1.1 What the family actually is (mechanism, not just art)

`GS_SandP_Body` (`ThingDef ParentName="ApparelMakeableBase"`) is ONE apparel def.
The 13 PNGs are not 13 items — they are the one def's `Graphic_Single` art, resolved
per-pawn by RimWorld's own body-type + rotation substitution
(`wornGraphicPath = Things/Apparel/Body/Wraps`, and the loader appends
`_<BodyTypeDef>_<direction>` automatically). The body-type suffixes present are
`Fat`, `Female`, `Hulk`, `Male`, `Thin` (RimWorld's five vanilla `BodyTypeDef`s)
crossed with `_east`/`_north`/`_south` (12 files), plus one direction-less
`Wraps.png` that is byte-for-byte the same artwork as `Wraps_Male_south.png` and
serves as the icon/no-body-type fallback — 13 files total, exactly as briefed.

Critically: **the def carries no `<colorGenerator>`** (there is a `ColorGenerator_StandardApparel`
line present in the source XML but it is commented out) and it DOES carry
`<stuffCategories><li>Fabric</li><li>Leathery</li></stuffCategories>` with
`<costStuffCount>120</costStuffCount>`. That combination means the garment is
Stuff-colored at craft time (dyed by whatever cloth/leather the crafter used), and
the art is built accordingly: **every one of the 13 textures is pure neutral
grayscale** — measured, not eyeballed: sampling all opaque pixels of every file
finds only achromatic values (equal R=G=B) at eight tonal steps —
`#000000, #707070, #808080, #909090, #a0a0a0, #b0b0b0, #c0c0c0, #d0d0d0, #e0e0e0, #f0f0f0`.
There is no hue anywhere in the family. This is the single most important
transferable fact for the commission: **do not paint the wrap in a fixed tan/sand
color** the way our absorbed SovereignTusken wraps do (see §3) — build it as a
neutral value-only mask so RimWorld's Stuff-color multiply does the tinting, if we
want the same "any cloth, any dye" flexibility.

### 1.2 Canvas and subject bounds (measured per file, `PIL` bbox of alpha>10)

All 16 files (13 body + the 3-head-and-base counted separately in §2) share a
**512×512 canvas**, RGBA. Opaque-pixel bounding boxes, in pixels (`width × height`
of the drawn silhouette, canvas is 512×512 so center is (256,256)):

| file | bbox (x0,y0)-(x1,y1) | subject size (w×h) | canvas coverage |
|---|---|---|---|
| Wraps.png (base = Male_south) | (155,176)-(356,431) | 202×256 | 16% |
| Wraps_Male_south | (155,176)-(356,431) | 202×256 | 16% |
| Wraps_Male_north | (152,176)-(355,432) | 204×257 | 16% |
| Wraps_Male_east | (174,173)-(340,426) | 167×254 | 13% |
| Wraps_Female_south | (164,157)-(347,445) | 184×289 | 15% |
| Wraps_Female_north | (157,156)-(345,446) | 189×291 | 15% |
| Wraps_Female_east | (147,158)-(324,449) | 178×292 | 14% |
| Wraps_Fat_south | (102,156)-(409,450) | 308×295 | 28% |
| Wraps_Fat_north | (96,154)-(414,452) | 319×299 | 29% |
| Wraps_Fat_east | (90,157)-(397,458) | 308×302 | 28% |
| Wraps_Hulk_south | (112,131)-(399,502) | 288×372 | 30% |
| Wraps_Hulk_north | (106,130)-(406,503) | 301×374 | 32% |
| Wraps_Hulk_east | (113,146)-(376,501) | 264×356 | 26% |
| Wraps_Thin_south | (202,174)-(309,430) | 108×257 | 9% |
| Wraps_Thin_north | (202,174)-(309,430) | 108×257 | 9% |
| Wraps_Thin_east | (173,176)-(308,424) | 136×249 | 8% |

Read-out: **Fat and Hulk are drawn noticeably wider AND taller than Male** (Hulk
reaches y≈502–503, i.e. almost the full 512 canvas height, vs Male's y≈431) — the
family is not a uniform silhouette recolored per body type, each body type has its
own hand-drawn outline. **Thin is the narrowest by a wide margin** (108–136 px wide
vs Male's 167–204 px) but is drawn to nearly the same height as Male, i.e. Thin
reads as "same torso length, much narrower shoulders/waist," not "shrunk
uniformly." **Female is narrower and noticeably taller than Male** (289–292 px tall
vs 254–257 for Male) — a waisted, elongated silhouette rather than Male's stockier
one.

### 1.3 Silhouette and coverage, per body type

The garment is a single OnSkin-layer piece that occupies the ENTIRE visible pawn
body silhouette (bodyPartGroups: `Neck, Torso, Shoulders, Arms, Legs` — everything
except the head and hands/feet). There is no under-layer visible anywhere: 0%
"skin exposed" — full-body coverage is total, hands/feet are implicitly bare
(not in the bodyPartGroups list) but the apparel renders as one continuous wrapped
mass, so the read is "fully cocooned torso," not "wrapped limbs with visible skin
between them."

Per body type, describing the *silhouette shape itself* (not the surface bands):

- **Male (base):** a rounded-shoulder, tapered-waist "bucket" or truncated-cone
  outline — wide flat-ish top (shoulders), narrowing smoothly to a rounded bottom
  edge (waist/hip line where the sprite ends, since legs are drawn as part of the
  same wrapped mass rather than separated). Slightly asymmetric — the east-facing
  variant shows a small hip/elbow bulge on the near side.
- **Female:** the same bucket family but visibly **waisted** — the outline pinches
  inward around the vertical midpoint before flaring slightly again lower, giving
  a two-lobe "figure-8 / gourd" silhouette rather than Male's single smooth curve.
  This waist pinch is the one clear gendered shape cue in the whole family (there
  is no chest/bust modeling — it is purely a waistline inflection).
  drawn taller and narrower than Male.
- **Fat:** the bucket silhouette scaled outward roughly isotropically — shoulders
  and waist both bulge, corners are rounder, no waist pinch at all; visually the
  closest to a plain sphere/dome sitting on a slightly narrower base.
  drawn ~30% wider than Male body coverage.
  outline holds a small chin-notch at the top edge (like the front of a cowl) on
  the east and north variants.
- **Hulk:** the tallest and widest of all five, roofline is flatter and squarer,
  drawn with pronounced trapezoidal shoulders and a straighter (less tapered)
  drop to the waist than Male — the "biggest bruiser" silhouette, occupying up to
  32% of canvas.
  On the north variant there is a visible V-notch cut into the top-center of the
  silhouette (a hood/collar gap), absent on Male/Female/Fat.
- **Thin:** a slim vertical ellipse, almost a stick — the narrowest waist of the
  set (108 px, roughly half Male's) but full torso height; north and east are
  identical in outline to a few pixels (108×257 both), suggesting these two
  directions barely differ in the Thin build.

### 1.4 Layering / banding structure (surface detail)

Every single body type/direction shares the same graphic language, just re-warped
to its silhouette:

- A **thick, uniform, solid-black outer contour** (roughly 8–12 px stroke at this
  resolution) traces the entire silhouette — this reads as the wrap's outer edge/
  hem, not a lighting effect; it's flat black with no gradation.
- Inside that outline, the body is filled with a **radial-gradient base tone**
  (lightest near the upper-center, darkening slightly toward the edges — a cheap
  "sphere" shading fake, not directional lighting) running through the grayscale
  steps in §1.1.
- Over that base, **2–4 diagonal darker-gray band lines** cross the torso,
  converging toward a point roughly 1/3 up from the bottom of the silhouette (this
  convergence point is consistent across body types and reads as "wraps spiraling
  around and cinching at the waist/hip"). The bands are drawn as thin **stroked
  lines** (single-pixel-weight curves, mid-gray, no fill between them) rather than
  as filled alternating stripes — so the read is "a few visible wrap seams over a
  continuous garment," not "distinct bandage strips."
  a fan/spiral pattern of 3 principal lines meeting near the lower-third, similar
  to lines converging on a wrapped bandage roll.
- No additional trim: no buckles, straps, patches, fringe, stitching marks, or
  color-blocking. The entire surface vocabulary is (a) black outline, (b) radial
  base-tone gradient, (c) a handful of diagonal seam lines. This minimalism is
  itself a fact worth transferring or deliberately upgrading from.

### 1.5 How the three directions differ

- **South (front-facing):** the seam-line fan is roughly bilaterally symmetric,
  converging center-low; darkest gradient sits at the very top (shoulder shadow)
  and bottom edge.
- **North (back-facing):** near-mirror of south in outline, but the seam lines
  shift to emphasize a diagonal running from upper-left to lower-right (reads as
  a single long wrap-strip crossing the back); the gradient's lightest point sits
  slightly higher/more centered than south's.
- **East (profile, mirrored for west by the engine):** the silhouette narrows and
  loses bilateral symmetry — a lean/hook to one side is introduced (visible as
  the small notch/bulge on the trailing edge in Male/Hulk/Thin east), and the
  band lines run more steeply diagonal (near 45°) than in south/north, consistent
  with wrapping visible in profile rather than face-on.

### 1.6 Palette, restated as numbers

Achromatic only. Approximate 8-step gray ramp measured across the family
(quantized to 16-value buckets, values are R=G=B for all of them):
`#000000` (outline), `#707070`, `#808080`, `#909090`, `#a0a0a0`, `#b0b0b0`,
`#c0c0c0`, `#d0d0d0`, `#e0e0e0`, `#f0f0f0` (brightest highlight). Black outline
pixels are consistently ~19–38% of each canvas's opaque-pixel count (heaviest on
Thin, where the thick outline is a larger fraction of a narrow silhouette; lightest
on Hulk, where more interior area dilutes the outline's share). No warm or cool
cast at any tonal step — this is a lighting/value study, not a colored garment; the
in-game color comes entirely from the Stuff (cloth/leather) chosen at crafting.

---

## 2. The devolved head shape

### 2.1 Files and mechanism

`Textures/Things/Heads/M/HeadSandM_{east,north,south}.png` and the `F/` equivalents,
6 files, 512×512 canvas each. These are wired as `HeadTypeDef.graphicPath` values
(§2.3), i.e. they replace the pawn's base head mesh entirely — not a mask/hood
layered over a vanilla head (the mask/hood is a separate item, `GS_SandP_Hood`,
worn on the `Overhead` layer over whichever head is underneath).

### 2.2 Geometry vs. vanilla, measured

Vanilla comparison used our own already-extracted vanilla head art
(`Male_Average_Normal_south.png` / `Female_Average_Normal_south.png`,
128×128 canvas, both identical bbox 46×50 px, aspect ratio 0.92 w:h).

The mod's south-facing heads: `HeadSandM_south` bbox 182×198 (ratio 0.92),
`HeadSandF_south` bbox 180×199 (ratio 0.90) — at 512×512 canvas (4× vanilla's
resolution). So the **overall silhouette aspect ratio is essentially unchanged**
from vanilla (roughly 0.9:1 width:height, an egg standing on its narrower end) —
the devolved head is NOT dramatically squashed or elongated versus stock.

What IS different, from direct visual comparison at matched scale:

- **Crown/jaw taper:** vanilla heads narrow gradually and continuously from crown
  to a distinct, rounded chin — there's a real taper across the whole face.
  The devolved head's taper is concentrated much lower: the silhouette stays
  almost cylinder-straight (crown width ≈ mid-face width) through the upper two-
  thirds, then narrows abruptly in a short curve at the very bottom, and on
  south/front views that bottom third additionally carries a **separate darker
  gray blob/shadow patch** (roughly 30–40% of the head's width, centered low)
  that has no vanilla equivalent — it reads as a heavy jaw/chin shadow or a
  fused jowl mass rather than a modeled chin.
- **Crown shape:** the devolved head's crown is flatter and squarer across the
  very top than vanilla's more continuously-rounded crown — vanilla arcs smoothly
  from side to top-center, the mod's head has a shorter, flatter arc before the
  sides drop away, giving a "helmet" or "pot" reading rather than an ovoid skull.
- **Eyes:** vanilla eyes are almond-shaped with a visible lid/brow stroke above
  each (a short angled dark mark that gives brow expression — e.g. the vanilla
  female south reference shows a mild "angry" brow). The devolved head's eyes are
  **plain solid filled circles/dots**, no lid, no brow mark, no highlight —
  smaller and simpler than vanilla, set at roughly the same vertical position
  (upper-middle of the face) but with no surrounding modeling at all.
- **No nose, mouth, ears, or other facial landmarks** are drawn on any devolved
  head variant — the entire face below the eyes is the flat gradient fill plus
  the one jaw-shadow blob described above. Vanilla likewise omits nose/mouth
  detail (RimWorld heads are minimal), so this is not a delta — noted for
  completeness only.
- **Net read:** the devolved head is a **wider-feeling, flatter-crowned, more
  cylindrical "bucket/pot" head** with a heavy, undefined lower jaw-mass and
  blank dot-eyes, versus vanilla's more continuously-tapered "egg" head with
  expressive almond eyes. It reads as deliberately blunt and inexpressive rather
  than anatomically shrunken — worth noting since the gene fluff text
  ("devolved," implying a *smaller* brain/head) is not what the silhouette
  numbers show; the mod's head is not measurably smaller than vanilla, just
  blockier and less detailed.

### 2.3 Male vs. female variant — measured, and it is nearly nothing

`HeadSandM_south` bbox size 182×198 vs `HeadSandF_south` bbox size 180×199 — a
2 px difference in width, 1 px in height, at 512 px canvas (≈1% delta, within
anti-aliasing/rounding noise). Visually, side by side, the M and F south/north/
east textures are indistinguishable in silhouette, eye placement, eye size, and
jaw-shadow-blob shape and position. **There is no deliberate geometric sexual
dimorphism in this head family** — male and female share one head sculpt; the
split into two `HeadTypeDef`s exists only to satisfy RimWorld's requirement that
a `gender`-scoped `HeadTypeDef` be provided for each gender the xenotype can roll,
not because the art differs. (Any residual pixel diffs are almost certainly
independent hand-touch-ups on two separately-saved files, not an intentional
design difference.) This is a place our own commission can legitimately choose to
do better/different without being unfaithful to "what the source mod does,"
since the source mod itself does nothing here.

### 2.4 The `HeadTypeDef` mechanism — verbatim structure (facts, not art)

Full content of `1.6/Defs/Genes/HeadTypes.xml` in the source mod:

```xml
<HeadTypeDef Name="HeavyBoneBase" Abstract="True">
  <randomChosen>false</randomChosen>
  <requiredGenes>
    <li>Head_Devolved</li>
  </requiredGenes>
</HeadTypeDef>

<HeadTypeDef ParentName="HeavyBoneBase">
  <defName>Male_DevolvedNormal</defName>
  <graphicPath>Things/Heads/M/HeadSandM</graphicPath>
  <gender>Male</gender>
</HeadTypeDef>

<HeadTypeDef ParentName="HeavyBoneBase">
  <defName>Female_DevolvedNormal</defName>
  <graphicPath>Things/Heads/F/HeadSandF</graphicPath>
  <gender>Female</gender>
</HeadTypeDef>
```

Mechanism read-out: an **abstract base def** (`HeavyBoneBase`) centralizes the one
shared gate — `<requiredGenes><li>Head_Devolved</li></requiredGenes>`, meaning
this `HeadTypeDef` can only be selected/rolled for a pawn that actually carries the
`Head_Devolved` gene — plus `<randomChosen>false</randomChosen>`, which keeps the
game's ordinary random head-type roller from ever picking this head type for a
pawn that doesn't have the gene (it is reachable only by forced assignment, see
below). Two **concrete leaf defs** then each just set `<defName>`, the per-gender
`<graphicPath>` (note: no `_south`/`_north`/`_east` suffix or file extension in the
def — RimWorld's head-graphic loader appends rotation suffixes itself, exactly
like the apparel `wornGraphicPath` convention), and `<gender>` to scope which sex
each is eligible for.

The forcing side of the mechanism is the `GeneDef` (`1.6/Defs/Genes/Genes.xml`),
which is what actually makes carriers of the gene use these heads instead of
rolling a normal one:

```xml
<GeneDef ParentName="GeneJawBase">
  <defName>Head_Devolved</defName>
  <label>Devolved head</label>
  <description>Carriers of this gene have a devolved facial appearance.</description>
  <iconPath>UI/DevHead</iconPath>
  <forcedHeadTypes>
    <li>Male_DevolvedNormal</li>
    <li>Female_DevolvedNormal</li>
  </forcedHeadTypes>
  <statFactors>
  </statFactors>
  <displayOrderInCategory>97</displayOrderInCategory>
  <exclusionTags>
    <li>Jaw</li>
  </exclusionTags>
</GeneDef>
```

So the wiring is a closed loop, two def types, three fields doing the real work:
`GeneDef.forcedHeadTypes` names the two `HeadTypeDef`s → each `HeadTypeDef`
declares `requiredGenes` pointing back at the same gene (belt-and-suspenders: the
gene forces the head type, and the head type refuses to be picked without the
gene) → `HeadTypeDef.gender` splits the pair so the correct sex gets the correct
graphicPath. `exclusionTags: [Jaw]` and `ParentName="GeneJawBase"` mark this as a
vanilla-style "Jaw" slot gene (the same slot vanilla `Jaw_Normal`/`Jaw_Elongated`
etc. occupy), so it correctly displaces any other jaw-slot gene on the same pawn
rather than stacking. `GeneJawBase`/`GeneVoiceBase` are vanilla Biotech base defs,
not defined by this mod — only referenced by `ParentName`.

The xenotype (`SandXenotype.xml`) simply includes `Head_Devolved` in its `<genes>`
list alongside its other genes (`Beauty_VeryUgly`, `Hair_BaldOnly`, etc.) — nothing
xenotype-specific about the head-forcing lives there; the gene alone is sufficient
to force the head on any pawn/xenotype that carries it.

---

## 3. What reads "desert nomad" here, and the delta from our own SovereignTusken garb

We already own overlapping content: `src/RimStarWars/Armoury/Defs/Absorbed_KotorCore/
ThingDefs_WeaponsArmorsGadgets/Absorbed_KotorCore_Apparel_SovereignTusken.xml`
(absorbed from a different Workshop mod, guy762's KotOR Core, under
`WEAPONS_ABSORPTION_WAVE_1`). Directly comparing the two, since both are on disk:

- **Same visual language for the wrap band pattern.** The absorbed
  `SWApparel/Sovereign_Tuskens/Wraps.png` (our own asset, one static texture, no
  body-type variants) uses the identical "thick black outline + radial gray
  gradient + 3 converging diagonal seam lines" recipe as the Rimwars mod's Wraps
  family in §1.4 — same silhouette family, same minimal banding, same
  bucket-shaped torso wrap. This is the *generic* "desert-wrap" visual grammar
  common to both sources, not something unique to the mod we're capturing —
  useful confirmation that the language itself (thick outline, spiral bands, no
  hue) is the load-bearing "desert nomad" signal, not any one artist's specific
  file.
- **Fixed color vs. Stuff-driven color.** Our SovereignTusken apparel hard-codes
  `<colorGenerator Class="ColorGenerator_Options"><options><li><only>(190,155,120)</only>
  </li></options></colorGenerator>` (a single fixed beige/tan, RGB 190,155,120 ≈
  `#BE9B78`) on BOTH the hood and the body wrap, and does so with
  `Inherit="False"` explicitly overriding any base coloring — it always renders
  tan regardless of crafting stuff. The Rimwars mod (§1.1) instead leaves color
  ungenerated and grayscale, letting the Stuff dye it. **This is the clearest
  mechanical/visual delta to decide on purpose**, not inherit by accident.
- **No body-type variation in what we already own.** SovereignTusken's `Wraps.png`
  is one `Graphic_Single` texture — no Fat/Female/Hulk/Male/Thin, no directional
  variants at all. The Rimwars family's 13-texture per-body-type/per-direction
  build (§1.2–1.3) is strictly richer coverage than what we currently ship.
- **Our hood already carries "Tusken Raider" iconography the Rimwars body-wrap
  family does not attempt**: `SandHead_south.png` (our SovereignTusken mask) has
  goggle-lens eyes with visible eye-stalk/tusk spikes projecting from the temples
  and a separate dark mouth-grille with visible teeth — a much more creature-like,
  masked-warrior read. The Rimwars devolved HEAD (§2, a bare skull, no mask) and
  its separate hood item (`GS_SandP_Hood`, not inspected pixel-by-pixel here since
  it is not one of the two families this brief asked for) sit at a plainer,
  less-embellished register by comparison.
- **The delta our commission should aim for:** keep the shared grammar that both
  sources already agree on — thick black contour, spiral/converging wrap-band
  seams, minimal trim, full-torso coverage reading as "everything covered against
  heat and sand" — but (a) make the NEW body-wrap Stuff-colorable (grayscale art)
  the way Rimwars does rather than hard-locking a single tan the way our own
  SovereignTusken apparel does, since Stuff-coloring is the more flexible,
  more-RimWorld-idiomatic choice and lets one wrap serve many factions/palettes;
  (b) actually build the five body-type × three-direction variant set (13
  textures) instead of the single static texture we currently have, since that
  coverage gap is real and visible in play (a Fat or Hulk pawn currently wears
  art drawn for Male); (c) keep the new devolved-style bare head plain (dot eyes,
  no mask) as its own separate, undecorated asset, and reserve tusk/goggle/
  mouth-grille embellishment for the hood layer where we already have it, so the
  two layers stay visually distinct instead of duplicating detail.

---

## What could not be captured in words

- Exact anti-aliasing/dithering micro-texture at the seam-line edges is a
  pixel-level rendering detail no verbal description can reproduce faithfully;
  an artist should treat "thin mid-gray stroked line, roughly 2–4 px at 512
  canvas" as the actionable spec rather than trying to match dither noise.
- The precise Bezier/spline curvature of each silhouette's contour (i.e. the
  literal path data) is inherently a drawing, not a describable numeric
  quantity beyond the bounding-box/aspect-ratio and qualitative-shape language
  already given in §1.3 and §2.2 — recreation should target the same
  proportions and shape *language*, not an attempted point-for-point trace.
- `GS_SandP_Hood` (the mask/hood item's own texture) was not itself in scope for
  this brief (only the two named families — Wraps* body apparel and the
  Head_Devolved head shape) and so was viewed only for the §3 comparison, not
  fully catalogued; if the hood is wanted as a third asset family it needs its
  own capture pass before unsubscribe.
