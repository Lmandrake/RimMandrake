# C7 — incomplete directional texture sets, triaged

_CREATE, 2026-08-13. Triage and preparation only; **no art was built in this pass.**
Every row below was re-verified against disk today, against the donor's own def and
its own pixels. Queue item: `infrastructure/state/queue/CREATE.md` §C7, tagged `[v2]`._

---

## 🔴 DO THESE THREE FIRST

| # | what | donor | cost | why first |
|---|---|---|---|---|
| **1** | `BarkSkinFemale_Wide_Normal_east` | VRE Phytokin | **zero art** — the file already exists in the donor under the wrong name | A colonist's whole head is wrong in both side facings, and the fix is a byte copy |
| **2** | `bandolier_chewbacca` + `bandolier_traveler` north, 5 body types + masks | SW KotOR Resources | 20 files, **derived** not drawn | The most-seen defect in all of C7 — worn apparel, broad generation tags, ~1 facing in 4 |
| **3** | `GravshipGenebank_north` | Vanilla Gravship Expanded | **zero art** — 180° rotation of its own south | Free, and it lands in a mod we already ship |

**Mod count implied: two new mods, plus one addition to a mod that already exists.**
Row 3's donor is `vanillaexpanded.gravship`, which we already fix in
`src/RimMandrake/GravshipAstronautFix/`. The owner's ruling is **one mod per
DONOR**, not one per defect, so row 3 is a new texture plus an `About.xml`
paragraph in that mod — not a ninth folder.

New mods needed:

| folder | packageId | `loadAfter` |
|---|---|---|
| `src/RimMandrake/PhytokinBarkHeadFix/` | `mandrake.phytokinbarkheadfix` | `vanillaracesexpanded.phytokin` |
| `src/RimMandrake/KotORBandolierNorthFix/` | `mandrake.kotorbandoliernorthfix` | `guy762.MM.KotORCore` |

🔴 **The KotOR fix cannot join the existing art-fix slot.** Our seven fix mods sit
at `activeMods` positions **556–564**; `guy762.mm.kotorcore` is at **573**, i.e.
*after* them. Its art is loose, so a fix mod placed in the existing slot would be
**overwritten by the donor and invisible**. It must go after 573 — next to
`mandrake.jawa.armoury` at 575. Every other donor here is comfortably earlier
(`van.beasts` 108, `vanillaexpanded.gravship` 376, `vanillaracesexpanded.phytokin`
389, `sarg.alphagenes` 477, `biomesteam.biomescaverns` 479,
`biomesteam.biomespollutedlands` 480).

---

## 🔴 Two corrections to C7's own method — read before triaging art again

C7 says its entries "were already checked against trap #37", i.e. against the def's
`graphicClass` and `visibleFacing`. I re-verified every row anyway, and the check
as stated is **not sufficient**. Two engine facts, both read out of
`Assembly-CSharp.dll` with `src/RimMandrake/Utils/ilprobe/il.py` this session
rather than taken from memory:

### 1. `visibleFacing` is often set in C#, where no XML grep will find it

`Verse.PawnRenderNodeProperties_Eye::.ctor` sets, in compiled code:

```
IL_000d: ldsfld  Rot4::East      → visibleFacing
IL_0018: ldsfld  Rot4::South
IL_0023: ldsfld  Rot4::West
IL_002d: stfld   PawnRenderNodeProperties::visibleFacing
IL_003d: stfld   PawnRenderNodeProperties::workerClass  = PawnRenderNodeWorker_Eye
IL_004d: stfld   PawnRenderNodeProperties::nodeClass    = PawnRenderNode_AttachmentHead
```

The def's XML says none of this. **Grepping XML for `visibleFacing` and finding
nothing does not mean all four facings render.** Any def rendering through
`renderNodeProperties` must be checked against its props *class*, not only its
markup.

### 2. `Graphic_Multi.Init` has a bare-path fallback that almost nobody accounts for

Disassembled in full this session. Suffix probes fill `array[0..3]` = north, east,
south, west. If **north** is null it substitutes, in this order:

| substitute | `drawRotatedExtraAngleOffset` |
|---|---|
| south (`array[2]`) | **180°** |
| east (`array[1]`) | **−90°** |
| west (`array[3]`) | **90°** |
| **the un-suffixed file at `req.path`** (`IL_011f`, `reportFailure: false`) | **0°** |

`Failed to find any textures at` (`IL_0139`) fires **only if all five lookups
fail** — the four suffixes *and* the bare filename. So:

- A texPath with a suffix accidentally baked in still resolves, silently, off the
  bare-path branch.
- A file shipped with **no** directional suffix at all is a **valid** `Graphic_Multi`
  source, not a broken one.
- The offset differs per branch, so two defects that both "render something" can be
  rotated differently from each other.

**This killed two candidate defects below that a file census would have filed as
red errors.**

---

# The rows, ranked by value per effort

## 1. VRE Phytokin — `BarkSkinFemale_Wide_Normal_east` ⭐ DO IT

**Real.** `.../294100/2927323805/1.6/Defs/HeadTypeDefs/HeadTypeDefs.xml`
L84–92: `HeadTypeDef` `VRE_BarkHeavy_Female`, L86
`<graphicPath>Things/Pawn/Humanlike/Heads/BarkSkinFemale_Wide_Normal</graphicPath>`,
gender Female, `requiredGenes` `VRE_BarkSkin` + `Jaw_Heavy`.

**Trap #37 re-verified — it is a defect.** `HeadTypeDef` has **no** `graphicClass`
field and no facing control: zero hits for `graphicClass|visibleFacing|drawSize|
renderNodeProperties` across the mod's `HeadTypeDefs/`, and zero across all of
`Data/*/Defs/HeadTypeDefs/`. It is hardcoded `Graphic_Multi`, all four rotations,
west mirrored from east. Nothing licenses a missing east.

**Trap #43 re-verified — pixels opened, all 30 files in the folder.** All 256×256,
all healthy, nothing blank. Every one of the 10 head sets has north+south+east.
Exactly one file is absent, and one file is spare:

| file | canvas | drawn | subject |
|---|---|---|---|
| `BarkSkinFemale_Wide_Normal_north.png` | 256×256 | 8,034 (12.26%) | 90×101 at (83,78) |
| `BarkSkinFemale_Wide_Normal_south.png` | 256×256 | 8,238 (12.57%) | 91×102 at (82,78) |
| `BarkSkinFemale_Wide_Normal_east.png` | — | **ABSENT** | — |
| `BarkSkin_Wide_Normal_east.png` (male) | 256×256 | 8,981 (13.70%) | 105×109 at (75,80) |
| `BarkSkin_Wide_Normal_east copy.png` | 256×256 | 8,981 (13.70%) | 105×109 at (75,80) |

🎁 **The missing art is already in the donor's folder under the wrong name.** The
male→female head edit in this mod is a fixed ~90 px RGB-only patch in the lip
region (alpha delta 0 — silhouettes identical), at the same coordinates for every
head type. Measured: male↔female differs by 90 px at x[145,164] y[131,146] on the
Average set; `BarkSkin_Wide_Normal_east.png` ↔ `... east copy.png` differs by 91 px
at x[145,164] y[131,147]; Jaccard overlap of the two coordinate sets **0.93**
(the Average-vs-Narrow baseline is 0.98). At those coordinates the values decide
it: the copy matches the *female* glyph 45/90, the male 4/90; the original matches
the male 43/90, the female 0/90. Confirmed on disk today — the two files have
different md5 (`647df98a…` vs `7e0b47d9…`) and no female east exists.

**The artist saved the female Wide east under the male's name with " copy"
appended.** The fix is a byte copy, not a commission.

**What the player sees:** a female Phytokin with `VRE_BarkSkin` + `Jaw_Heavy`
renders a **front-facing head on a side-facing body, in both east and west** —
`Graphic_Multi` fills the null east from north at −90°, and west mirrors it. A
whole head, on a colonist, whenever she walks horizontally. Currently latent: no
pawn in the save has that gene pair, and `Player.log` has zero `BarkSkin` hits.

**Fix:** copy `BarkSkin_Wide_Normal_east copy.png` → `BarkSkinFemale_Wide_Normal_east.png`.
**True canvas 256×256**, from the healthy `_north`/`_south` siblings of the *same*
set (not from the copy). Expected ≈8,900 drawn px, subject ≈105×109 at (75,80).

**Donor:** `vanillaracesexpanded.phytokin`, ws **2927323805**, read from
`.../2927323805/About/About.xml:32`. **LOOSE** — `loadFolders.xml` v1.6 = `/` + `1.6`,
textures at mod root, `1.5/` and `1.6/` hold no PNGs, no `AssetBundles/` anywhere.
**`loadAfter` is load-bearing.** Active at position 389.

---

## 2. SW KotOR Resources — `bandolier_chewbacca` + `bandolier_traveler` north ⭐ DO IT

**Real, and it is two of four bandoliers, not "the bandoliers".**
`.../294100/3254370945/1.6/Defs/ThingDefs_WeaponsArmorsGadgets/Apparel_SWAccessories.xml`
— chewbacca L383–387 / L403–432, traveler L478–482 / L497–525.

```
384    <texPath>SWApparel/Accessories/bandolier_chewbacca/Apparel</texPath>
385    <graphicClass>Graphic_Single</graphicClass>
426    <wornGraphicPath>SWApparel/Accessories/bandolier_chewbacca/Apparel</wornGraphicPath>
427    <useWornGraphicMask>true</useWornGraphicMask>
428    <drawData><dataNorth><layer>65</layer></dataNorth></drawData>
```

| set | Male | Female | Thin | Fat | Hulk |
|---|---|---|---|---|---|
| `bandolier_double` | N/E/S | N/E/S | N/E/S | N/E/S | N/E/S |
| `bandolier_knife` | N/E/S + masks | ✅ | ✅ | ✅ | ✅ |
| **`bandolier_chewbacca`** | **E/S only** | **E/S only** | **E/S only** | **E/S only** | **E/S only** |
| **`bandolier_traveler`** | **E/S only** | **E/S only** | **E/S only** | **E/S only** | **E/S only** |

**Trap #37 re-verified — it is a defect.** No `visibleFacing`, no
`bodyTypeGraphicPaths`, no per-facing suppression anywhere in either def. The
`Graphic_Single` on L385 governs only the **ground/inventory** item art; the worn
graphic comes from `wornGraphicPath` and is always resolved as `Graphic_Multi` over
`<path>_<BodyType>_<facing>`. Nothing declares north deliberately absent. Missing
for all 5 body types in both sets, masks included (`_eastm`/`_southm` exist, no
`_northm`) — 22 files each where a complete set is 32.

⚠️ **C7's `layer 65` premise is true as XML but proves less than it claims.** The
block is verbatim. But 65 is not a bandolier-specific "draw on the back" flag — it
appears **11 times** across this mod, on all four bandoliers *and* the flight suits,
and the author's own inline comments in the same file decode the scheme as absolute
render layers (`<layer>21</layer> <!-- ONSKIN -->`, `22 <!-- MIDDLE -->`,
`71 <!-- OVERHEAD -->`). It is the house value for a Shell item facing north. What
it does establish is that the author **intended these visible from the north**,
which is why the gap reads as an oversight.

**Trap #43 re-verified — absent, not blank.** Every file that exists is healthy,
all 512×512: chewbacca `Apparel_Male_south` 13,200 px (5.04%), subject 200×255;
traveler `Apparel_Male_south` 9,358 px (3.57%), subject 207×237; the healthy
sibling `bandolier_knife/Apparel_Male_north` 15,023 px (5.73%), subject 195×216 at
(167,167). This is the C6 shape, not the Cerean-mane shape.

⚠️ `check_sprite.py` REJECTs the `*m.png` masks on "not one fully transparent
pixel". **False positive** — a tint mask is legitimately opaque. See the validator
note at the bottom.

**🔴 What the player sees — C7's expectation is wrong, and the truth is worse.**
The bandolier does **not** vanish facing north. `Graphic_Multi.Init` fills the null
north from the south at 180° (confirmed in IL above), so the pawn gets **chest
pouches drawn on its back**, at layer 65, on top of everything. Wrong art, never
absent art, and never a log line — so it reads as intentional and nobody reports it.

**Frequency: the highest in C7.** Both items carry wide generation tags — chewbacca
`KotORAccessory_any/heavy/outlaw/trooper/bandolier`, traveler adds
`civilian/richcivilian` — so they land on colonists, traders and raiders alike, and
north is roughly one facing in four.

**Fix — a derivation, not a commission.** C7's caution that "an apparel north is
not a mirror of south" is right in principle and mostly wrong for *this author*.
Measured on his own complete sets, north against its horizontally-mirrored south:

| set | silhouette differs | RGB differs |
|---|---|---|
| `bandolier_double` Male / Hulk | **4.4% / 4.5%** | 34.1% / 33.9% |
| `bandolier_knife` Male / Hulk | 22.4% / 23.3% | 34.5% / 35.4% |

The `bandolier_double` north outline is a **95.6% pure mirror** of its south; only
the interior detail is repainted. Recipe: **mirror the south, then repaint the
central detail cluster as the back of the garment.** `bandolier_traveler` (a simple
pouch) is nearly free; `bandolier_chewbacca` (heavier detail) is the harder half.
10 art files + 10 masks.

**True canvas 512×512**, from the healthy sibling
`.../3254370945/Textures/SWApparel/Accessories/bandolier_knife/Apparel_Male_north.png`
— a real north view in the same family, not a placeholder and not the broken set.

**Donor:** `guy762.MM.KotORCore` (name: *Star Wars KotOR Resources and Materials* —
there is no separate "Resources 2"), ws **3254370945**, read from its own
`About/About.xml`. **LOOSE** — `Textures/` at mod root, no `AssetBundles/`, no
`.bundle` anywhere. **`loadAfter` is load-bearing, and see the position-573 warning
at the top.** Active at 573. Swept the whole workshop tree and local `Mods/`: exactly
one mod ships these paths, so nothing else is supplying the north.

---

## 3. Vanilla Gravship Expanded — `GravshipGenebank_north` ⭐ DO IT (into the existing mod)

**Real.** `.../294100/3609835606/1.6/Mods/Biotech/Defs/ThingDefs_Buildings/Buildings_Biotech.xml`
L212 `<texPath>Things/Structures/GravshipGenebank/GravshipGenebank</texPath>`,
L214 `<graphicClass>Graphic_Multi</graphicClass>`, L215 `<drawSize>(1, 1)</drawSize>`,
L229 `<size>(1, 1)</size>`.

**Trap #37 re-verified — it is a defect.** No `rotatable`, no `visibleFacing`, no
`drawData`, no `renderNodeProperties` in the def *or* in vanilla's parent
`GeneBuildingBase` (`Data/Biotech/Defs/ThingDefs_Buildings/Buildings_Misc.xml:137-159`).
`ThingDef.rotatable` defaults **true**, so all four rotations are placeable and the
rotate button shows.

**Trap #43 re-verified — both present files healthy.** `GravshipGenebank_east.png`
128×128, alpha max 255, 98.1% coverage; `GravshipGenebank_south.png` 128×128, 98.7%.
Neither blank. Because `_east` exists and differs from the north mat,
`ShouldDrawRotated` is false and RimWorld substitutes the **south texture,
unrotated**.

**What the player sees:** the south art is an open-fronted rack cabinet with a
distinct front lip along the bottom edge — 61.8% self-difference under 180°
rotation, so emphatically not symmetric. A north-facing gene bank is pixel-identical
to a south-facing one: its opening points *toward* the viewer when it should be
showing its back. Silent, no log line. **Moderate-low visibility** — a 1×1 Biotech
buildable, but players do rotate 1×1 furniture to line banks up beside an assembler.

**Fix: free transform, no new art.** Ship `GravshipGenebank_north.png` =
`GravshipGenebank_south.png` rotated 180°. **True canvas 128×128** from its own
healthy south sibling, ~98% coverage, full-bleed bbox (0,0,128,128). This
reproduces exactly what the engine's own `drawRotatedExtraAngleOffset = 180f`
branch would have done had `_east` been absent — the engine-sanctioned back view
rather than an invention.

**Donor:** `vanillaexpanded.gravship`, ws **3609835606**, from its own `About.xml`.
**LOOSE** — all 523 PNGs in the root `Textures/`; the bundle
`1.6/AssetBundles/vanillagravshipexpanded` holds only 38 terrain/edge assets, no
pawn or building art. `loadAfter` load-bearing; the existing mod already declares it.
Active at 376.

**🔴 Goes into `src/RimMandrake/GravshipAstronautFix/`, not a new folder** — same
donor, and the ruling is one mod per donor. Add the file and an `About.xml`
paragraph describing it. That mod is already deployed and enabled at position 557,
so this ships without any `ModsConfig` change at all.

---

## 4. Biomes! Polluted Lands — `BMT_ImpalingClaws` north + east

**Real, and C7 understated it.**
`.../294100/3390196656/1.6/Defs/Genes/Gene_ImpalingClaws.xml` L5
`<defName>BMT_ImpalingClaws</defName>`. Two `renderNodeProperties`, both texPath at
L112 and L150: `BMT_PollutedLands/Things/Pawn/Humanlike/BodyAttachments/ImplaingClawLimb/ImpalingClaw`
(the `Implaing` typo is in the folder name too — def and disk agree, not a bug).

**Trap #37 re-verified — the def asks for more than C7 said.**
Node `SpikeL` L111–141: `<visibleFacing>` L120–124 = **South, North, West**.
Node `SpikeR` L149–181: `<visibleFacing>` L158–162 = **South, North, East**.
C7 says "explicitly asks for N and W"; the union is all four. Decisively, the author
wrote explicit per-facing `offset` and `rotationOffset` blocks (L125–140, L163–180)
for facings whose art does not exist. Not correct as shipped.

**On disk the entire folder is one file:** `ImpalingClaw_south.png`. `FutureTextures/`
holds no claw art; the 1.5 branch is identical.

**Trap #43 re-verified — real art, not a blank.** `ImpalingClaw_south.png` 256×256,
9,983 px (15.23%), subject 164×140 at (46,14), 0 saturated px as expected for
`colorType Skin`. The UI icon `Gene_ImpalingClaws.png` is a separate 128×128 asset
and **must not** be used to size the fix.

**What the player sees:** one texture exists, so no error and no invisible claw —
the south bitmap is drawn rotated wrongly on the pawn's back for three facings,
compounded by the def's own `rotationOffset` of −80/60/−60. **High if the gene is
in play** (a body attachment rendered every frame a pawn is on screen, and pawns
face north/east/west most of the time); **zero if no pawn carries it**, which is the
case today.

**Fix: genuinely new art, 2 files.** `_north` and `_east` at **256×256**, canvas
taken from `ImpalingClaw_south.png` itself — the only member of the set. `_west`
needs no file; `Graphic_Multi` mirrors it from `_east` free. West is *not* the gap;
north and east are.

**Donor:** `BiomesTeam.BiomesPollutedLands`, ws **3390196656**, from its own
`About.xml`. **LOOSE** — `LoadFolders.xml` declares only `1.5`/`1.6`/`\`, no
`AssetBundles/` and no `.bundle` anywhere. `loadAfter` load-bearing. Active at 480.

**Verdict: worth doing, but after the top three** — it is the only row here needing
genuinely new art whose payoff is conditional on a gene nobody in the colony has.

---

## 5. Dark Ages: Beasts — `BlackScribeScorpling_north`

**Real, and small.** `.../294100/3472275628/1.6/Defs/ThingDefs_Races/Animal_BlackScribe.xml`
L138–152, the juvenile life stage: L142
`<texPath>Animal/BlackScribe/BlackScribeScorpling</texPath>`, `drawSize 1`, no
`graphicClass`, no `visibleFacing`, no `bodyTypeGraphicPaths`, no suppression.
`PawnKindLifeStage.bodyGraphicData` resolves as `Graphic_Multi` for animals — which
is why no vanilla animal def declares one — so `_north` is expected. **The adult
`BlackScribe` in the same folder ships all three**, and the other ~20 animals in the
mod are complete: the author's own convention says the juvenile should be too.

**Trap #43 — absent, not blank.** All 256×256: `_east` 19,803 px (30.22%), subject
186×173; `_south` 18,157 px (27.71%), subject 148×237; healthy adult `_north`
10,876 px (16.60%), subject 122×193 at (68,15).

**What the player sees:** a north-facing scorpling renders its east art rotated —
a sideways scorpion sliding up-screen. **A juvenile life stage of a `combatPower`
300 biome-gated exotic animal. Seen rarely and briefly.**

**Fix:** 1 file, **256×256** from its own healthy `_east`/`_south` siblings. A
scorpion's dorsal view is close to its ventral, so mirror-and-touch-up from south,
not new art.

**Donor:** `Van.Beasts`, ws **3472275628**. **LOOSE** — `loadFolders.xml` at root,
no bundle. `loadAfter` load-bearing. Active at 108.

**Verdict: real, cheap, almost never seen. Do it only if someone is already in the
file** — on its own it does not justify a mod folder, an `About.xml` and a
`ModsConfig` slot.

---

## 6. Biomes! Caverns — pupae north + south

**Real, but the most expensive row here and among the least seen.**
`.../294100/2969748433/Textures/BMT_Caverns/Things/Animal/BeetlePupae/` holds 7
files, **all `_east`, no north, no south, no west.** All non-blank, all greyscale
(tinted per-def via `<color>`):

| file | canvas | drawn | subject |
|---|---|---|---|
| `AaroxisDendoriaPupa_east.png` | 256×256 | 18,834 (28.74%) | 242×109 at (6,68) |
| `BeetlePupa_east.png` | 512×512 | 62,104 (23.69%) | 419×201 at (40,155) |
| `BloodDropMothPupa_east.png` | 512×512 | 66,077 (25.21%) | 474×186 at (20,179) |
| `BoomPupa_east.png` | 512×512 | 56,812 (21.67%) | 399×198 at (64,164) |
| `Dessicated_*` ×3 | as above | as above | darkened recolours, identical pixel counts |

**Trap #37 re-verified — they are pawns, not props.** Each is a
`ThingDef ParentName="AnimalThingBase"` with a matching `PawnKindDef`, `MoveSpeed 0`
and `thinkTreeMain BMT_PupaeThinkTree` — immobile, but still a `Pawn` carrying a
`Rot4` and rendered through the pawn graphic path. And the donor's own convention
settles it: **every adult in the same tree ships three files** (`FoundryBeetle_east/
_north/_south`, `FoundryGrub_*`, `Crystalpillar_*`), leaving west to the mirror. The
pupae are short by the author's own standard.

🔴 **`BeetlePupa` backs SEVEN defs, not six** — all `PawnKindDef`
`lifeStages/li/bodyGraphicData/texPath` under `.../2969748433/1.6/Defs/Animals/`:
`BMT_BovineBeetlePupa` (`BMT_BovineBeetle.xml:216`), `BMT_CrystalBeetlePupa`
(`BMT_CrystalbackBeetle.xml:210`), `BMT_FoundryBeetlePupa` (`BMT_FoundryBeetle.xml:212`),
`BMT_JewelBeetlePupa` (`BMT_Jewelbeetle.xml:201`), `BMT_MossBeetlePupa`
(`BMT_MossBeetle.xml:208`), `BMT_ShatterjawBeetlePupa` (`BMT_ShatterjawBeetle.xml:209`),
`BMT_RoyalRhinoPupa` (`BMT_RoyalRhino.xml:208`). The other three textures have one
def each.

**What the player sees:** the east bitmap at a fixed rotation offset in every
facing — a sideways cocoon. Pupae never move, so they hold their spawn rotation,
most often one they have no art for. **Low-to-moderate:** a transient life stage of
cave fauna, seen on a cave map or when breeding these insects, not on the home
colony screen.

**Fix: genuinely new art, 8 sprites.** Canvas per texture, from that texture's own
set: **512×512** for `BeetlePupa`, `BloodDropMothPupa`, `BoomPupa` and the two
512 dessicated variants; **256×256** for `AaroxisDendoriaPupa` and its dessicated
twin. Add `_north` and `_south` each; `_west` mirrors from `_east` free. The east
subjects are wide-and-short (419×201, 474×186) — a side view — so **north and south
are not derivable by rotation**; a cocoon head-on is a different silhouette.

**Cheapest useful slice if this is ever taken:** `BeetlePupa` north+south alone
covers 7 of the 11 defs.

**Donor:** `BiomesTeam.BiomesCaverns`, ws **2969748433**. **LOOSE**, no bundle.
`loadAfter` load-bearing. Active at 479.

**Verdict: 8 new sprites for a rarely-seen transient life stage. Lowest value per
effort of anything real in C7.** Not recommended for the next art session.

---

# 👁️ `Eyes_Red` — why there is no log line, and why we must NOT patch it

**C7 was right to flag it and right to forbid a blind patch. The answer is: it is
correct as shipped, and so is the missing north on every face feature in the game.**

**The def.** `Data/Biotech/Defs/GeneDefs/GeneDefs_Cosmetic.xml` L503–547 (`Eyes_Red`).
It renders through **two** `<li Class="PawnRenderNodeProperties_Eye">` entries — one
`<side>Right</side>` / `<anchorTag>RightEye</anchorTag>`, one `<side>Left</side>` /
`<anchorTag>LeftEye</anchorTag>` with `<drawData><defaultData><flip>true</flip>` and
`<dataWest><flip>false</flip>`. **Both point at the same `<texPath>` /
`<texPathFemale>`.** `parentTagDef` Head, `drawSize 0.2`, `layer 54`.

**The files.** Biotech ships **no loose Textures folder at all**; everything is in
`Data/Biotech/AssetBundles/resources_biotech`. Its manifest lists exactly two eye
entries — `HeadAttachments/RedEyes/Female/RedEyes_Female_east.png` and
`HeadAttachments/RedEyes/Male/RedEyes_Male.png`. C7's description is exact.

**Why no error — three independent reasons, all confirmed in IL this session:**

1. **North is never drawn.** `PawnRenderNodeProperties_Eye::.ctor` sets
   `visibleFacing = {East, South, West}` **in C#** (disassembly quoted above), and
   `PawnRenderNodeWorker.CanDrawNow` refuses any facing not in that list. A pawn
   seen from behind shows the back of its head. `_north` was never in scope.
2. **One texture already serves both eyes.** `<side>` + `<flip>` means the engine
   mirrors a single asset into the left socket. Counting files against a presumed
   set of four is a category error before the facings even come up.
3. **The bare-path fallback swallows the male case.** `RedEyes_Male.png` sits at
   exactly `req.path`, so `Graphic_Multi.Init` hits `IL_011f`
   (`ContentFinder.Get(req.path, reportFailure: false)`), `array[0]` is non-null,
   and the `Failed to find any textures at` branch at `IL_0139` is skipped. The
   female case never reaches it either: `_east` is present, so north is filled from
   east at −90°. **Both are complete loads by every measure the engine has.**

**Siblings — C7's "every sibling ships east+south" is half right.** It holds for
*face* features (`HeavyBrow`, `FacialRidgesA/B/C`, `PigNose`) and not for *head*
features (`CatEars`, `FloppyEars`, `PigEars`, `PointedEars`, `MiniHorns`,
`CenterHorn` all ship east+north+south). No `_north` exists anywhere in the eye set
and none is wanted.

## ⭐ The generalisation — this is worth more than any patch in this document

**Face features are authored east+south only and declare `visibleFacing =
{East, South, West}`** — either from a props class constructor (`Eyes_*`) or spelled
out in XML (`Brow_Heavy`, `GeneDefs_Cosmetic.xml:605`). West is always the mirrored
east. North is never rendered.

So for any face feature: **a missing `_north` is correct, a missing `_west` is
correct, and even a missing `_south` is survivable** — the engine substitutes east
and rotates. **Only a path where all four suffixes *and* the bare filename are
absent is a real hole.** Audit by asking *"does `ContentFinder` resolve `<path>` or
any one of its four suffixes?"*, never by counting directional files against an
assumed set of four; and confirm any gap against `visibleFacing` **including the
props class**, not against a sibling's file count.

## 🔴 Two findings that fall out of this, neither of them ours to fix

- **`Eyes_Gray` is a genuine hole in vanilla Biotech.** It points at
  `.../GrayEyes/Male/GrayEyes_Male` and `.../GrayEyes/Female/GrayEyes_Female`, and
  **no GrayEyes texture exists in any bundle in the game** — only the UI icon
  `UI/Icons/Genes/Gene_GrayEyes.png`. Gray eyes are icon-only; the pawn art was
  never authored. This *would* print `Failed to find any textures at`. **Do not
  patch a Ludeon DLC to fix it** — record it and move on.
- **🔴 A clean log is not evidence that art exists.** `PawnRenderNode.EnsureInitialized`
  builds graphics **per pawn, lazily** — nothing warms them at startup. `Eyes_Gray`
  has literally nothing on disk and is still silent in our 7,247-line `Player.log`,
  purely because no gray-eyed pawn was ever drawn. **"Zero `Failed to find any
  textures at`" means nobody looked, not that everything resolved.** This weakens
  every past inference we have drawn from that line's absence.

---

# ❌ Not worth doing, and why

| row | verdict | evidence |
|---|---|---|
| **Biotech `Eyes_Red`** | **Correct as shipped. Close it.** | `visibleFacing` excludes North (set in C#); one texture serves both eyes via `<side>`+`<flip>`; the bare-path fallback resolves the male. Nothing is missing. |
| **Alpha Genes emblem** | **Correct as shipped. Close the row.** C7's own hypothesis was right. | Head emblem `GeneDefs_Forsaken.xml:89-93` — `<visibleFacing>` lists East, South, West and **omits North**. Body emblem L46 `defaultData layer -2` (behind the body mesh — north draws *underneath* the pawn) vs L49/52/55 `layer 15` for S/E/W. |
| ↳ *and its blank `_east` is a house idiom, not a defect* | | `AG_ForsakenBodyEmblem_east.png` is 0 drawn px — but so are 6 others, every one where the attachment must not render: `AG_SingleWing_west`, `AG_SingleEar_east`, `AG_LightLED{,Red}_{east,north}`. **A deliberately-empty PNG is Alpha Genes' way of suppressing a facing** while keeping `Graphic_Multi` satisfied. Confirmed across all 60+ attachment folders. Adding art here would make pawns *worse*. |
| **Dark Ages Muffton overlays** | **Correct as shipped.** Trap #37 in action. | `_Overlay` and `Female_Overlay` are not a `Graphic_Multi` set at all — `Patches/PatchGiddyUp.xml` L20/27/37/44 names them as four separate **`Graphic_Single`** texPaths with the suffix baked in, feeding GiddyUp's `<overlayFront>` / `<overlaySide>`. **That API has no north slot.** Do not commission these. |
| **Caverns `Dessicated_BeetlePupa_east` texPath** | **Renders fine. Do not "fix" it.** | 7 defs reference the path with `_east` baked in. All four suffix probes fail — but the bare-path branch finds `Dessicated_BeetlePupa_east.png`, which exists (35,416 B, verified on disk). **No error, correct texture.** The only consequence is `drawRotatedExtraAngleOffset = 0°` instead of the −90° the live pupae get. Patching the texPath would *change* the rotation, not turn on a missing sprite. |
| **Caverns `FacetMothPupa.png`** | **Not broken.** | Ships with no directional suffix at all (`BMT_FacetMoth.xml:204`). That is a **valid** `Graphic_Multi` source via the same bare-path branch. A file census flags it; the engine does not care. |
| **Dark Ages `RockTrollBaby_southm`** | **Leave it alone.** | Real inconsistency — `Animal_RockTroll.xml:169` sets `CutoutComplex` on the baby, which ships `_eastm`/`_northm` but no `_southm` while the adult ships all three. Effect unconfirmed and at most a tint difference on one facing of a baby. |
| **VGE VacBarrier blueprint east icon** | **Below the threshold worth shipping.** | All four `_MenuIcon_east` files are byte-identical (md5) to their `_Top_east`, while the south pair differ — the east icon lacks the field-glow. Affects only the placement ghost; `uiIconPath` is hardcoded to `_south` so the architect menu is fine, and under `EdgeDetect` the low-alpha glow may not contribute an edge at all. |
| **VGE — 20 further "incomplete" groups** | **All correct as shipped. Row exhausted.** | Three legitimate idioms a file census cannot tell from a defect: (a) **west instead of east** — `GravshipScannerCluster`, `IndustrialOxygenPump` ship N/S/**W** and `Graphic_Multi` mirrors west→east (handedness verified: the control readout ends up on the correct side); (b) **two-view VE machine art** — `Agrocell`, `CapacitorHarmonizer`, `GravshipHighDensityBattery` ship N+E as two separately drawn views; (c) **the single-texture rotating-door pattern** — all four `VacBarrier*_Barrier` ship south only, so every mat is equal, `ShouldDrawRotated` is true, and the sprite is drawn rotated by the thing's facing. |

## Rows that did NOT check out against disk

Two, and one of them is a method failure rather than a bad row:

1. **The Alpha Genes emblem row does not reproduce as a defect** — three independent
   lines of evidence say correct as shipped. C7 had already rated it "lowest
   confidence — `layer -2` may make it deliberate"; that hedge was right, and the
   row should be struck rather than left open.
2. **"Dark Ages Beasts" was a bare mod name with no specific defect attached.** A
   full sweep of the mod's `Textures/` tree found exactly four incomplete groups, of
   which **two are correct as shipped** (the Muffton overlays), one is negligible
   (`RockTrollBaby_southm`) and **one is real** (`BlackScribeScorpling_north`, §5).
   The row as written could not have been actioned by anyone.

Everything else in C7 reproduced, and two rows turned out **larger** than written:
`BMT_ImpalingClaws` asks for all four facings rather than "N and W", and
`BeetlePupa` backs **7** defs rather than 6.

---

# Notes for whoever runs the next art session

**Cost of the recommended set:** 2 new mod folders + 1 file into
`GravshipAstronautFix/`. Art actually drawn: **zero for rows 1 and 3** (a byte copy
and a 180° rotation), and rows 2's 20 files are mirror-and-repaint derivations from
the donor's own complete sets. If rows 4 and 5 are added later that is 2 further
mods and 3 genuinely new sprites.

**`check_sprite.py` false-positives on third-party donors, twice here.** It REJECTed
the KotOR `*m.png` tint masks on "not one fully transparent pixel" (a mask is
legitimately opaque) and REJECTed all four Alpha Genes emblems on "100% saturated /
1 distinct luminance" (they are flat tinted glyphs, `colorType Custom`,
`useSkinShader false`, and the def's own description says *"a yellow emblem"*).
**Those rules are house-style intake gates for art WE author. Do not read them as
evidence of a defect in a donor.** The tool was not changed.

**Two stray donor files noticed and deliberately not touched:**
`.../2927323805/.../BarkSkin_Wide_Normal_east copy.png` (which is row 1's fix) and
`.../3472275628/Textures/Animal/Taraal/Taraal_east copy.png`. Also
`.../2969748433/.../FoundryBeetle/BeetlePupa.png`, byte-identical to
`BeetlePupae/BeetlePupa_east.png` and referenced by no def — an orphan.

⚠️ **The workshop packageId index built for this pass is unreliable and was not
committed.** Reading the first `<packageId>` in an `About.xml` returns the first
`<modDependencies>` entry whenever dependencies precede the mod's own id — it gave
`brrainz.harmony` for Alpha Genes, Phytokin and VGE, and
`OskarPotocki.VanillaFactionsExpanded.Core` for Dark Ages Beasts. **Every packageId
in this document was read from the donor's own `About.xml` directly**, not from that
index.
