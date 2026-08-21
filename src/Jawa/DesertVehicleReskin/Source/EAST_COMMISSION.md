# EAST_COMMISSION.md — the four east facings, specified and NOT commissioned

🔴 **Nothing here has been generated.** No image model was called to write this file, and
none may be called until the owner approves the spend. He has approved exactly one
generation so far — a single dewback — and this document exists so that approving the rest
costs one paste, not an afternoon. The commands are at the bottom, complete and unrun.

⚠️ **The game is up.** Building the four textures writes only into this repo. Deploying
them into `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods` is a separate act
for a separate time, and it is not in the command block below.

---

## Why this is new art and not a rotation, with the arithmetic

The donor draws its east animals in **side elevation** — flank, profile head, harness in
profile, legs under the body — while every pair we own is a **plan view of the animal's
back**, drawn to be seen from above. Turning a plan view ninety degrees does not produce an
elevation; it produces a top-down animal lying on its side, and that is what was tried and
rejected on 2026-08-21. The arithmetic says the same thing independently. The OxCart east
band is 224×180, **aspect 1.244**; the bantha south pair turned 90° is **aspect 0.732**.
Filling the band with it diverges the two axis scales by 1.244/0.732 = **+69.9% distortion**,
against the ~18% that is invisible on a top-down animal. Contain-fitting instead costs no
distortion and spans only **66% of the band's width** even after the bounded 12% stretch —
a team that no longer reaches its own yoke. Both routes fail, and they fail for the same
reason: the projection is wrong, so no fit can rescue it. East is a missing asset, not a
fit bug.

---

## 1. What the donor actually draws on east — the reference crops

Extracted from the donor's own `AV_<Vehicle>_east.png`, cropped to the east animal band
from `GEOMETRY.md` §3 (already measured — not re-measured here) and upscaled **6× NEAREST**,
matching `donor_Chariot_horse_south_6x.png`.

| vehicle | band (x0,x1,y0,y1) | size | aspect | crop |
|---|---|---|---|---|
| Chariot | 254,486,191,342 | 233×152 | 1.533 | `art/ref/donor_Chariot_east_6x.png` (1398×912) |
| WarChariot | 212,494,148,336 | 283×189 | 1.497 | `art/ref/donor_WarChariot_east_6x.png` (1698×1134) |
| OxCart | 282,505,158,337 | 224×180 | 1.244 | `art/ref/donor_OxCart_east_6x.png` (1344×1080) |
| CoveredCarriage | 280,506,155,324 | 227×170 | 1.335 | `art/ref/donor_CoveredCarriage_east_6x.png` (1362×1020) |

Provenance, so the crops are reproducible without the image model:

```python
# python3, from Source/ — the same six lines that made the four files above
c = Image.open(DONOR + "/%s/AV_%s_east.png" % (v, v)).convert("RGBA").crop((x0, y0, x1+1, y1+1))
c.resize((c.width*6, c.height*6), Image.NEAREST).save("art/ref/donor_%s_east_6x.png" % v)
```

**What the crops show, looked at rather than assumed:**

- Side elevation, **head to the right**, the whole animal seen from its left flank.
- One hard black keyline of even weight around every form; flat interior fill with a soft
  vertical gradient; no rendering, no texture noise.
- The harness is drawn in **dark navy straps** with a browband, a throat strap and traces
  running off the **left** edge toward the cart; the yoke is a pale wooden bar crossing both
  bodies vertically.
- The pair is **stacked, not side by side** — see §3.

---

## 2. The three species, their bands, and a legal generation size for each

`gpt-image-2` requires **both edges multiples of 16**, **total pixels 655,360–8,294,400**,
max edge 3840, long:short ≤ 3:1. A 512×512 facing is 262,144 px and cannot be asked for at
all, so each of these generates large at the band's *aspect* and is downscaled by the
compositor.

| species | vehicle whose band it fills | band | band aspect | generation size | ratio | pixels | aspect error |
|---|---|---|---|---|---|---|---|
| **bantha ×2** | OxCart | 224×180 | 1.2444 | **1792×1440** | 56:45 | 2,580,480 | **0.00%** |
| **ronto ×2** | CoveredCarriage | 227×170 | 1.3353 | **1792×1344** | 4:3 | 2,408,448 | −0.15% |
| **dewback ×2** | WarChariot | 283×189 | 1.4974 | **1728×1152** | 3:2 | 1,990,656 | +0.18% |
| **dewback ×1** | Chariot | 233×152 | 1.5329 | **1472×960** | 23:15 | 1,413,120 | +0.03% |

Every edge divides by 16 (112·90, 112·84, 108·72, 92·60) and every total sits inside the
window with room either side.

### 🔑 Which band drives the dewback, and why it is TWO frames and not one

DECIDE's ruling puts a dewback on both chariots — **×2 on WarChariot, ×1 on Chariot** — so
the two bands are not alternatives to choose between, they are two different subjects.

- **The dewback PAIR is driven by WarChariot's band, 283×189, aspect 1.497.** That is the
  only dewback band a *pair* has to fill, so it is the only one whose aspect the pair's
  drawing must match.
- **Chariot needs a separate single-beast frame** at its own 233×152 / 1.533. It cannot be
  cropped out of the pair: the same thing was tried on south and the two animals overlap by
  495 px at centre, which is why `dewback_single_south.png` was generated as its own asset
  in `65ec90d`. East stacks them harder, not less. Halving the east pair would cut a
  dewback in two.
- The aspects happen to sit 2.4% apart, which is a coincidence and not a licence: what
  separates the frames is the **number of animals**, not the shape of the box.

---

## 3. The stacked, merged pair — how the prompt handles it

`GEOMETRY.md` §3 measures it and the crops confirm it: on east the two animals are drawn
**one behind the other in depth, overlapping**, not abreast with a gap. OxCart's silhouettes
merge outright over x 400–474 and leave only a 6 px separation at y 250–255; CoveredCarriage
has a 5–7 px trunk gap at y 240–246; WarChariot's is 2–7 px at y 241–248. The far animal
sits **higher in frame and slightly ahead**, the near animal lower and in front, occluding
the far one's near flank and forelegs.

**So the prompt asks for exactly that, positively phrased, in the composition sentence** —
"drawn stacked: the far beast sits higher in frame and slightly ahead, the near beast lower
and in front of it, their silhouettes touching and overlapping across the hindquarters so
the two read as one team". A pair drawn abreast with clear green between them would be
wrong art, not merely a fit problem: `build_beast_vehicle.py` composites east **UNDER** the
surviving donor art, and the donor's yoke bar and traces are drawn across the seam where the
two bodies meet. Two separated bodies leave that yoke spanning empty green.

---

## 4. The four commissions

Every prompt below is complete and ready to paste. Constraints come first, the subject
second, per `skills/generating-images/references/prompting.md`; every requirement is stated
as the state to draw, never as a prohibition. `codex_image.py` prefixes `Use $imagegen to `
and appends its own chroma-key clause, so each prompt begins with a verb and carries the
size itself.

**Invariants, identical in all four and repeated in each prompt because drift across
iterations is the normal failure mode:**

1. Side elevation matching image 1 — flank view, head to the right, legs under the body.
2. The donor's own harness language from image 1 — dark navy straps, browband, throat
   strap, traces leaving the frame at the left edge, one even black keyline, flat fill with
   a soft vertical gradient.
3. Our species' palette, markings and surface texture from image 2.
4. A flat solid `#00ff00` field everywhere the beasts are not, meeting the keyline directly
   and holding one uniform value across the whole frame.
5. Every horn, muzzle, foot and tail terminates inside the frame.

**Reference order is load-bearing.** Image 1 is always the donor east crop (projection,
harness, line weight); image 2 is always our existing south pair (species, palette,
keyline colour). `codex_image.py --image` is repeatable and order is meaningful.

### 4a. bantha ×2 — OxCart

- image 1 `art/ref/donor_OxCart_east_6x.png` · image 2 `art/bantha_pair_gen_south.png`
- size **1792×1440**

```text
generate a 1792x1440 game sprite of two banthas in side elevation, seen from due east, on a flat solid #00ff00 field that holds one uniform colour everywhere the animals are not and meets their outline directly.

Projection, harness and line weight come from image 1: a left-flank elevation with the heads to the right of frame, legs under the bodies, one hard black keyline of even thickness around every form, flat interior colour with a soft vertical gradient, dark navy harness straps with a browband and a throat strap, and the traces leaving the frame at the left edge toward the cart.

The two banthas are drawn stacked: the far bantha sits higher in frame and slightly ahead, the near bantha lower and in front of it, their silhouettes touching and overlapping across the hindquarters so the two read as one team. The team fills the frame with a narrow even green margin on all four sides, and every horn, muzzle, hoof and tail terminates inside the frame.

Species, palette and surface come from image 2: shaggy chestnut-brown fur in long combed strokes, heavy cream spiral horns curling forward, dark brown lower legs, brown leather harness. Even flat lighting from above.
```

### 4b. ronto ×2 — CoveredCarriage

- image 1 `art/ref/donor_CoveredCarriage_east_6x.png` · image 2 `art/ronto_pair_gen_south.png`
- size **1792×1344**

```text
generate a 1792x1344 game sprite of two rontos in side elevation, seen from due east, on a flat solid #00ff00 field that holds one uniform colour everywhere the animals are not and meets their outline directly.

Projection, harness and line weight come from image 1: a left-flank elevation with the heads to the right of frame, legs under the bodies, one hard black keyline of even thickness around every form, flat interior colour with a soft vertical gradient, dark navy harness straps with a browband and a throat strap, and the traces leaving the frame at the left edge toward the wagon.

The two rontos are drawn stacked: the far ronto sits higher in frame and slightly ahead, the near ronto lower and in front of it, their silhouettes touching and overlapping across the hindquarters so the two read as one team. The team fills the frame with a narrow even green margin on all four sides, and every muzzle, foot and tail terminates inside the frame.

Species, palette and surface come from image 2: heavy taupe-olive hide in smooth flat panels, a high humped shoulder falling to a small narrow head, a long tapering tail, dark brown leather harness with brass rings. Even flat lighting from above.
```

### 4c. dewback ×2 — WarChariot

- image 1 `art/ref/donor_WarChariot_east_6x.png` · image 2 `art/dewback_pair_gen_south.png`
- size **1728×1152**

```text
generate a 1728x1152 game sprite of two dewback lizards in side elevation, seen from due east, on a flat solid #00ff00 field that holds one uniform colour everywhere the animals are not and meets their outline directly.

Projection, harness and line weight come from image 1: a left-flank elevation with the heads to the right of frame, legs under the bodies, one hard black keyline of even thickness around every form, flat interior colour with a soft vertical gradient, dark navy harness straps with a browband and a throat strap, and the traces leaving the frame at the left edge toward the chariot.

The two dewbacks are drawn stacked: the far dewback sits higher in frame and slightly ahead, the near dewback lower and in front of it, their silhouettes touching and overlapping along the flanks so the two read as one team. The team fills the frame with a narrow even green margin on all four sides, and every snout, clawed foot and tail tip terminates inside the frame.

Species, palette and surface come from image 2: olive-green pebbled scale hide with a mottled dorsal ridge, darker grey-olive splayed reptilian legs, a blunt lizard head, a long tapering tail, brown leather harness with metal rings. Even flat lighting from above.
```

### 4d. dewback ×1 — Chariot

- image 1 `art/ref/donor_Chariot_east_6x.png` · image 2 `art/dewback_single_south.png`
- size **1472×960**

```text
generate a 1472x960 game sprite of one dewback lizard in side elevation, seen from due east, on a flat solid #00ff00 field that holds one uniform colour everywhere the animal is not and meets its outline directly.

Projection, harness and line weight come from image 1: a left-flank elevation with the head to the right of frame, legs under the body, one hard black keyline of even thickness around every form, flat interior colour with a soft vertical gradient, dark navy harness straps with a browband and a throat strap, and the traces leaving the frame at the left edge toward the chariot.

A single dewback fills the frame nose to tail with a narrow even green margin on all four sides, standing square on the ground line, and every snout, clawed foot and tail tip terminates inside the frame.

Species, palette and surface come from image 2: olive-green pebbled scale hide with a mottled dorsal ridge, darker grey-olive splayed reptilian legs, a blunt lizard head, a long tapering tail, brown leather harness with metal rings. Even flat lighting from above.
```

---

## 5. Two things that will bite between the generation and the build

- 🔑 **`ROTATE["east"]` is now `0`, changed in `build_beast_vehicle.py` alongside this file.**
  It was `90` to serve the turned-south-pair experiment. East art is authored already facing
  east, so a turn would lay the team on its side. Nothing shipped ever used the old value —
  the sled's east came from `build_eopie_sled_east.py`, which is untouched.
- ⚠️ **The compositor trims to the subject bbox, so the SUBJECT's aspect is what matters,
  not the canvas's** — and the chroma-key clause asks for padding. After cutting, compare
  the trimmed subject's aspect to the band's. The east fit is `contain` with a bounded 12%
  stretch, so anything inside ~12% composites cleanly; further out than that, crop the raw
  to the band aspect rather than regenerating.
- The dewback is olive, not green, and its south pair keyed cleanly on `#00ff00`. If
  `chroma_key.py` reports holes in the subject, re-run that one generation on `#ff00ff`.

---

## 6. The commands, once approved

```bash
cd /mnt/d/Luke/dev/Rimworld
S=src/Jawa/DesertVehicleReskin/Source
G=skills/generating-images/scripts

# --- 1. GENERATE. Four calls, four generations of the owner's quota. Prompts are §4;
#        paste each one in place of <PROMPT 4a> etc. Add --dry-run to see the resolved
#        command without spending anything.
python3 $G/codex_image.py edit \
  --image $S/art/ref/donor_OxCart_east_6x.png \
  --image $S/art/bantha_pair_gen_south.png \
  --chroma-key '#00ff00' \
  --out $S/art/raw/bantha_pair_east_raw.png \
  --prompt "<PROMPT 4a>"

python3 $G/codex_image.py edit \
  --image $S/art/ref/donor_CoveredCarriage_east_6x.png \
  --image $S/art/ronto_pair_gen_south.png \
  --chroma-key '#00ff00' \
  --out $S/art/raw/ronto_pair_east_raw.png \
  --prompt "<PROMPT 4b>"

python3 $G/codex_image.py edit \
  --image $S/art/ref/donor_WarChariot_east_6x.png \
  --image $S/art/dewback_pair_gen_south.png \
  --chroma-key '#00ff00' \
  --out $S/art/raw/dewback_pair_east_raw.png \
  --prompt "<PROMPT 4c>"

python3 $G/codex_image.py edit \
  --image $S/art/ref/donor_Chariot_east_6x.png \
  --image $S/art/dewback_single_south.png \
  --chroma-key '#00ff00' \
  --out $S/art/raw/dewback_single_east_raw.png \
  --prompt "<PROMPT 4d>"

# --- 2. CUT THE KEY TO ALPHA. chroma_key.py validates its own output and exits
#        non-zero if the subject vanished or a corner stayed opaque.
python3 $G/chroma_key.py --input $S/art/raw/bantha_pair_east_raw.png    --out $S/art/bantha_pair_gen_east.png
python3 $G/chroma_key.py --input $S/art/raw/ronto_pair_east_raw.png     --out $S/art/ronto_pair_gen_east.png
python3 $G/chroma_key.py --input $S/art/raw/dewback_pair_east_raw.png   --out $S/art/dewback_pair_gen_east.png
python3 $G/chroma_key.py --input $S/art/raw/dewback_single_east_raw.png --out $S/art/dewback_single_east.png

# --- 3. COMPOSITE. Writes ../Textures/.../AV_<Vehicle>_east.png and its mask.
python3 $S/build_beast_vehicle.py OxCart          --facing east --pair $S/art/bantha_pair_gen_east.png
python3 $S/build_beast_vehicle.py CoveredCarriage --facing east --pair $S/art/ronto_pair_gen_east.png
python3 $S/build_beast_vehicle.py WarChariot      --facing east --pair $S/art/dewback_pair_gen_east.png
python3 $S/build_beast_vehicle.py Chariot         --facing east --pair $S/art/dewback_single_east.png

# --- 4. VALIDATE against the donor facing each one replaces. 0 REJECT is the bar the
#        other eight facings cleared.
D="/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/3028675048/Textures/Things/Vehicles/Land/Tier0"
T=src/Jawa/DesertVehicleReskin/Textures/Things/Vehicles/Land/Tier0
for v in OxCart CoveredCarriage WarChariot Chariot; do
  python3 skills/generating-rimworld-sprites/scripts/validate_sprite.py \
    --reference "$D/$v/AV_${v}_east.png" --candidate "$T/$v/AV_${v}_east.png"
done

# --- 5. LOOK AT IT. Sprite size is the only size that decides whether art reads.
python3 $S/preview_derived_facings.py
```

⛔ **Deploying is not in this block and is not part of the commission.** The game is up;
`deploy_custom_mods.py` comes later, on the owner's word.
