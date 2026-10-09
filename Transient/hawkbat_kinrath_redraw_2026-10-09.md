# Hawkbat + Kinrath redraw — 2026-10-09

Owner rulings: decision taken by question card 2026-10-09 00:16 (Greentide sheet).
- Hawkbat — "Sketto-style flyer". owner_note (typed, verbatim): "Get rid of all this crappy art and follow the purple and tan canon art very closely. NOT a bird. Flyer."
- Kinrath — "Redraw from donor shape". owner_note (typed, verbatim): "follow canon art closley, looks closest to a mantis shape. Study the donor art for geometry info."

Pending check: `D:\Luke\dev\_artpipe\pending\` held no hawkbat/kinrath job before filing.

## Hawkbat — why last night's renders miss canon

Looked at `D:\Luke\dev\_artpipe\_artsrc\regen_gt_canon_hawkbat_v1_east\regen_gt_canon_hawkbat_v1_east.png` and
`...\regen_gt_hawkbat_flying_1_v1_east\regen_gt_hawkbat_flying_1_v1_east.png` against the ruled image
`D:\Luke\dev\RimMandrake\design\RimStarWars\canon_references\hawkbat\wookieepedia_legends_infobox.jpg`.
Both passed canon_check 6/6, so the gate cannot see these misses:

1. **A wyvern/dragon, not canon's body plan.** Renders have a separate lizard body on two standing legs,
   a long whip tail ending in a curl, and wings sprouting from the shoulders. In canon the wings are the body:
   one continuous leathery membrane runs from the base of the neck down both sides to two long trailing
   points, with no visible separate tail or standing legs.
2. **Wrong wing structure.** Renders use dragon/bat finger-spars radiating from a wrist, with scalloped
   edges between fingers. Canon has no finger fan: the membrane is a long narrow kite, creased by dense
   fine TRANSVERSE ribs/wrinkles along its length, with a wavy, notched trailing edge.
3. **Colour layout inverted.** Renders: tan membrane with purple only as edge trim and rib lines.
   Canon: a broad violet-purple stripe down the centre of each wing (along the arm bone), crossed by
   tan/cream ladder bars, purple fading out to pale gold-tan at the edges and underside; a row of small
   gold spots along the leading edge.
4. **Bird-like head.** Renders give a feathery green crest tuft and a parrot-style hooked bill. Canon: small
   smooth reptilian head on a thin curved neck, two small swept-back green horn-stalks, one large green
   eye, a short pale hooked beak tip.
5. **Hooks missing.** The owner's 2026-09-14 ruling names "notable hooks on end of wings and feet". Canon
   has curved claws at each wingtip AND small hooked claws on the trailing edge part-way down (the feet).
   The renders put generic claws at the wing wrists only.
6. **Rendering register.** Clean illustration look with outlines on the flying frame; the 2026-10-08
   entry ruling wants a real animal: veined translucent leather, real skin, natural light.

The last night prompt itself said "NOT a bird (no feathers, no beak)" while Must show requires a hooked
beak. The new prompt fixes that contradiction.

## Hawkbat — filed (stage 1 only)
`hawkbat_fly_master_v1_east`, priority 0. It is fresh from canon: no accepted render exists to
`derive_from`, so the canon image is the anatomy attachment (Sketto §4 A otherwise). S/N masters and stage 2
are NOT filed. They wait for the owner's OK on east. Rows: `D:\Luke\dev\RimMandrake\Transient\hawkbat_kinrath_redraw_2026-10-09\hawkbat_stage1_master_east.json`.

## Kinrath — donor geometry

Donor sprite: `D:\Luke\dev\RimMandrake\Transient\art_verdict_originals\kinrath\{east,south,north}.png`.
These are the originals extracted from the live textures before our override (commit `942e51465`).
They are flat cartoon art with black outlines, used here only for geometry.
The artstore donor path attached to last night's v1 (`_artstore/8f/8f307c…`) no longer exists on disk.

Read off the donor:
- **East:** a compact upright torso, tilted slightly forward, rising from a low rear abdomen. On top sits a
  short, blunt, box-shaped head, about as wide as the neck-thorax column, with a small square cluster of
  4 dark eye dots on its face. There is no S-curved snake neck. One raptorial forelimb comes forward from
  the upper thorax: the upper arm is angled forward-up, and the forearm hooks down and back like a mantis
  arm. Four walking legs hinge at the lower thorax, two splayed to the rear-left and two to the
  front-right. Each leg is a long upper segment angled UP to a high knee above the body line, then a long
  lower segment angled DOWN to a pointed foot. It is a wide, low, spider-like crouch with the body slung
  between the knees. Proportions: the torso is about 45% of the canvas height, the leg span about 95% of
  the canvas width, and the head about 15% of the height.
- **South:** a symmetric front view. The head is at the top centre with its eye cluster. Two folded
  raptorial forelimbs are held together vertically down the chest, in a praying-mantis pose. A darker
  abdomen sits below. Four legs splay out in a wide M, two per side, with the knees above the body line.
- **North:** the back view. The thorax shows chevron segment ridges, the abdomen is darker at the base,
  and the legs splay the same way as in the south view.
- Six limbs in total: 2 raptorial plus 4 walking.

## Kinrath — why last night's v1 misses canon
`D:\Luke\dev\_artpipe\_artsrc\regen_gt_canon_kinrath_v1_east\regen_gt_canon_kinrath_v1_east.png` is in game now as column F.
1. **Wrong lineage.** The entry's `## ruling` (owner, 2026-09-14) picks the netcaster design: the TCW clip
   `unfinished_tcw_netcasters_conceptclip.png`, "Same as 2 and 3". v1 was given
   `wookieepedia_legends_infobox_viperkinrath.png` (KOTOR) as its first, attached image, so it drew the Legends
   design and canon_check marked the netcaster lines n/a. That is how it passed.
2. **No eye cluster.** The netcaster and the donor both have a blunt head bearing a cluster of round black
   eyes. v1 gives it a sleek snake head.
3. **Snake neck instead of an upright column.** v1 draws a long S-curved neck over a horizontal scorpion-like
   abdomen. The canon and the donor carry a thick, upright, segmented thorax-neck column with the head
   directly on top.
4. **Body shape.** Canon's rear view shows a spoon-shaped body (narrow at the top, wider toward the rear)
   with dark horizontal abdomen bands. v1 has plated scales.
5. **Leg stance.** In v1 the legs are long and straight-ish, placed under the body. The donor and the
   netcaster rear view use a wide splay with high knees and the body slung low between them.

## Kinrath — filed
`kinrath_netcaster_v2_{east,south,north}`, priority 0. E is fresh from canon (the TCW clip attached first);
S and N derive from `kinrath_netcaster_v2_east`. Rows: `D:\Luke\dev\RimMandrake\Transient\hawkbat_kinrath_redraw_2026-10-09\kinrath_v2_esn.json`.

## Status
- filed: hawkbat_fly_master_v1_east; kinrath_netcaster_v2_{east,south,north} (S/N held until E done). Nothing installed.
