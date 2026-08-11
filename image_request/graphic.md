# Art request — Gamorrean head sprites for RimWorld 1.6

_Upload this file to ChatGPT together with the whole `seed/` folder._

You are producing sprite assets for **RimWorld 1.6**. I am authoring a Gamorrean
xenotype (Star Wars — the pig-like brutes Jabba the Hutt keeps as palace guards)
and I need six head sprites drawn to match an existing mod's art style so
exactly that a player cannot tell they were drawn by someone else.

Read section 2 before you look at the images. The art appears white/grey for a
technical reason and that reason governs everything you do.

---

## 1. What I want

Six new head sprites — **Gamorrean male and female**, each in three facings:

- **south** — facing the viewer, full face
- **east** — facing right, profile (the game mirrors this for west)
- **north** — back of the head, no face

---

## 2. The single most important technical fact

**These textures are greyscale masks. RimWorld multiplies a skin colour over
them at runtime.**

The Gamorrean's green hide comes from the game engine, from a `Skin_Green` gene
— *not* from you. Every pixel you draw must be a neutral grey. Any colour baked
into the texture renders wrong in game and cannot be fixed afterwards.

That is why every attached PNG looks like a white ghost. It is correct. Do the
same.

---

## 3. What is in `seed/`

### `00_contact_sheets/` — look at these first

Everything below, composited onto a grey checkerboard so you can see the
transparent PNGs at a glance.

| Sheet | What it shows |
|---|---|
| `A_donor_hutt_head_all_views.png` | The donor head, all six views. Top row male S/E/N, bottom row female S/E/N. |
| `B_colonist_vs_donor_same_scale.png` | **Top row: an ordinary human colonist head.** Bottom row: the donor Hutt head, at the same scale. Shows how much bigger and broader the donor is than a normal pawn. |
| `C_vanilla_pig_parts.png` | RimWorld's own Biotech pig features — snout, ears, mini-horns, heavy brow. This is the engine's native visual language for "pig-like human". |
| `D_style_range_aliens.png` | Eight other alien heads from the same mod. Shows how far the artist pushes non-human anatomy while staying in style. |
| `E_current_gamorrean_kitbash_south.png` | **What a Gamorrean looks like in my game today.** This is the thing you are replacing. See section 4. |
| `F_true_ingame_scale.png` | The donor head at 512 px next to its real on-screen size (roughly 40–128 px depending on zoom). Read this before adding fine detail. |
| `G_current_gamorrean_full_pawn.png` | The whole pawn as it stands today: head on body, wearing Gamorrean leathers, then the leather hood, then the heavy battle harness. Shows how much of the head is actually visible once apparel is on — the hood crops the cranium, so **the snout, tusks, jowls and ears carry the entire species read**. |

### `01_donor_hutt_head/` — your primary style and geometry reference

The Hutt "FatHead" head type from the mod I am extending (*Star Wars Xenotypes*,
Steam Workshop 2915192253). Six files, male and female × south/east/north.

Broad, heavy, fleshy, wider than tall, low sloping cranium, massive jowls, sour
downturned mouth. It is already about 80% of a Gamorrean skull. **Start here.**

The male→female difference across these two sets is exactly the amount of sexual
dimorphism this mod uses. Copy that delta; do not invent your own.

### `02_colonist_baseline/` — a typical colonist, for scale and proportion

An ordinary human head as RimWorld draws it: `Male_Average_Normal` in all three
facings, plus `Female_Average_Normal` and `Male_HeavyJaw_Normal`.

These tell you what "normal" looks like in this game, so you can judge how far
the Gamorrean should deviate. Two things to notice:

- **The Gamorrean head is much bigger than a colonist's.** A colonist head
  occupies about **186 × 206 px** of the 512 canvas. The donor Hutt head
  occupies about **284 × 213 px** — roughly 50% wider. Your Gamorrean should
  keep the donor's bulk, not shrink to human size.
- **Faces are minimal.** Two dot eyes, a simple mouth line, almost nothing else.
  RimWorld faces carry expression through silhouette, not detail.

`Male_HeavyJaw_Normal` is the head the Gamorrean uses *right now* — see below.

### `03_vanilla_pig_parts/` — the engine's own pig vocabulary

RimWorld's Biotech expansion ships pig features as separate overlay genes:
`PigNose`, `PigEars`, `MiniHorns`, `HeavyBrow` (south and east each).

Study these. They are how the base game says "pig" in this art style, and three
of the four are already on the Gamorrean. Your drawn-in snout and brow should
feel like a bolder, better-integrated version of these — not a foreign style
grafted on.

**Note the ears.** `PigEars` is in the attachments but is *not* on the Gamorrean
today, which is part of why the current version fails. Your Gamorrean head must
have proper drooping pig ears drawn directly into it.

### `04_style_range_aliens/` — how weird this mod is willing to get

Trandoshan, Taung, Gungan, Quarren, Rodian, Geonosian, Wookiee, Kubaz. Eight
heads from the same mod, all south view.

These prove the ceiling: heavily non-human skulls, projecting snouts, eye stalks
and mandibles all live comfortably inside this style. You are not constrained to
a human head with bits added. Push the anatomy — just keep the line weight,
value palette and minimal-face discipline identical.

### `05_current_gamorrean/` — the inadequate art you are replacing

`tusks_south/east.png` — the entire current Gamorrean tusk art. Two tiny
slivers, and note there is **no north version at all**.

`Jowls2_south/east.png` — the jowl overlay it borrows from the *Bith* species.

Use these only to see intended tusk placement and line weight. **Do not imitate
their scale.** Real Gamorrean tusks should be several times this size.

### `06_body_context/` — what the head sits on

`Naked_Hulk`, `Naked_Fat` and `Naked_Male` bodies. The Gamorrean is a big,
heavy-set xenotype and will render on the Hulk or Fat body. Your head must not
look small or dainty perched on that mass.

---

## 4. What is wrong today, and what "better" means

Open `00_contact_sheets/E_current_gamorrean_kitbash_south.png`. That composite
is the real current appearance, assembled from the actual genes on the xenotype:
a vanilla `HeavyJaw` human head, plus a heavy brow, a small pig nose, mini-horns,
borrowed Bith jowls and those two tiny tusks.

It reads as **a grumpy human with horns**. It does not read as a Gamorrean.
Specifically:

- The snout is a flat decal on a human face — it does not project.
- The tusks are almost invisible at gameplay scale.
- There are no ears at all.
- The skull is a human skull; nothing about the silhouette says "pig".
- From behind (north) it is simply a bald human head.

**Better means: recognisable as a Gamorrean from the silhouette alone, at 40 px,
from any of the three facings.** That is the whole brief. Everything below serves
it.

---

## 5. Hard technical constraints

These are engine requirements, not stylistic preferences.

1. **Canvas: 512 × 512 px PNG with a true alpha channel.** Fully transparent
   outside the head silhouette. No background, no drop shadow, no ground plane,
   no framing border, no caption.

2. **Greyscale only — zero saturated pixels.** See section 2.

3. **Value palette.** Measured across the donor files, the distribution of
   opaque pixels is:
   - **~30% pure black `#000000`** — outline and all interior linework
   - **~30% in the 192–223 band** — shadowed and lower planes
   - **~40% in the 224–255 band** — lit upper planes
   - **~2% everything else** — only edge transitions

   So: black line, one mid grey, one near-white, and essentially nothing in
   between. No soft airbrushed gradients, no ambient occlusion, no noise, no
   grain, no texture overlay. A *slight* smooth falloff within each band is
   present in the originals and is fine; broad painterly rendering is not.

4. **Outline:** heavy solid black contour around the entire silhouette, roughly
   **10 px thick at 512 px**. Interior features use the same weight or slightly
   thinner.

5. **Lighting: top-lit.** Upper surfaces take the light band; undersides of
   jowls, jaw, chin and snout fall to the mid band.

6. **Framing.** Match the donor's placement on the canvas:

   | View | Head occupies | Size |
   |---|---|---|
   | south, north | x 114–397, y 199–411 | 284 × 213 px |
   | east | x 90–378, y 193–400 | 289 × 208 px |

   **South and north must share an identical outer silhouette** — north is the
   same skull seen from behind. (In the donor files those two views have
   byte-identical opaque pixel counts.)

   Get close and I will do the final pixel alignment myself; do not distort the
   drawing to hit the numbers exactly.

7. **Head only.** No hair, no headgear, no helmet, no armour, no neck, no
   shoulders, no body, no weapon. RimWorld draws hair and apparel as separate
   layers on top.

8. **If your pipeline cannot emit real alpha,** render on flat pure magenta
   `#FF00FF` instead — the art is greyscale, so I can key that out losslessly.
   State clearly which you did.

---

## 6. The design

Take the donor Hutt silhouette and push it porcine.

- **Snout** — pronounced, blunt, **upturned** pig snout projecting forward from
  the face, with two large round nostrils on its flat front disc. In the east
  profile it must clearly break the silhouette. This is the single most important
  read of the species, and the thing the current version most fails at.
- **Tusks** — two **upward-curving** tusks rising from the *lower* jaw at the
  corners of the mouth, tips passing the upper lip. Blunt, ivory, chunky — not
  thin fangs. Big enough to survive at 40 px. Visible in south and east; absent
  in north.
- **Ears** — broad, flat, fleshy pig ears set low and wide on the skull, angled
  back and drooping. Compare `03_vanilla_pig_parts/PigEars_*`, then draw them
  larger and integrated into the head rather than stuck on. They widen the
  silhouette in south and north and are the key read of the back view.
- **Eyes** — small, deep-set, close together, under a heavy sloping brow ridge.
  Much smaller relative to the head than the Hutt's. Dull, mean, stupid.
- **Jowls and neck** — thick sagging rolls of fat under the jaw.
- **Skull** — low, sloped, brutish; the cranium recedes sharply behind the brow.
- **Skin** — hairless, thick, slightly wrinkled. Suggest wrinkles with a few
  confident black creases; do not render skin texture.

**Female variant** — same species, unmistakably Gamorrean. Slightly narrower
skull, shorter and less flared tusks, marginally less extreme brow. Apply the
same delta measurable between the attached `Male_FatHead` and `Female_FatHead`.
Do **not** make her slim, pretty, or human — Gamorrean females are canonically
larger and more aggressive than the males.

**North view** — bald, lumpy skull from behind, ears clearly visible in profile
at the sides, neck fat rolls at the bottom, **no facial features**, same outer
silhouette as south.

---

## 7. Canon reference

The campaign keeps a scale + visual reference atlas at
`worldbuilding/star_wars_species_scale_reference_atlas.pdf` — 46 Star Wars
species, one page each, with sourced reference art and a height range normalised
against a 1.80 m human. Two things from it bear on this brief:

- **Gamorreans are 1.3–1.6 m — shorter than a human**, and read as broad and
  thick rather than tall. Keep the head heavy and wide; do not stretch it.
- Its Gamorrean entry is graded **portrait / upper body only**, so it will not
  give you a full-body turnaround. That is precisely why this commission exists.


- Gamorrean — Wookieepedia: <https://starwars.fandom.com/wiki/Gamorrean>
- Gamorrean Guards — StarWars.com Databank: <https://www.starwars.com/databank/gamorrean-guards>
- Gamorrean Warrior — Wookieepedia: <https://starwars.fandom.com/wiki/Gamorrean_Warrior>
- Gamorrean/Legends — Wookieepedia: <https://starwars.fandom.com/wiki/Gamorrean/Legends>

Canon description: *"A species of tall, strong bipeds, the Gamorreans had
porcine traits, like an upturned, large-nostriled cartilaginous snout, jowls,
and upturned tusks. Their hulking bodies were covered in green or rarely pink,
thick and hairless skin."*

---

## 8. Delivery

Produce **one image per message at maximum resolution** — do not lay them out as
a contact sheet, which starves each view of pixels.

1. Male south
2. Male east
3. Male north
4. Female south
5. Female east
6. Female north

**Stop after image 1 and wait for my approval.** The male south view sets the
style for the other five. Once approved, keep every subsequent view rigorously
consistent with it.

Before you draw, state in one or two sentences how you intend to handle the
snout projection and the ears, so I can correct the plan before you spend an
image on it.
