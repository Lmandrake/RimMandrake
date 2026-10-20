# Head parts: painted into the head art, or attached by gene? — design pass 2026-10-20

Owner question (2026-10-20): is the game's add-on ear behaviour in any way better than painting ears into the head?
He suspects it only lets ears overlap the body and causes more trouble than it saves. Then: Rakata eye-stalks, and helmets.
Evidence in the lineup shot `D:\ClaudeWork\screenshots\2026-10-20\heads_lineup_ALL_FACINGS.png`. Status key: MEASURED / READ (from a Core or Biotech def) / UNMEASURED (needs a test).

## How the game does an add-on ear (READ, `Data/Biotech/Defs/GeneDefs/GeneDefs_Endogenes.xml`, `Ears_Pointed`)
- A `PawnRenderNode_AttachmentHead` child of the `Head` node, one texture, `colorType Skin` + `useSkinShader`, `drawData layer 70`.
- It is positioned relative to the VANILLA head (no per-head-type offset exists on `HeadTypeDef`), skin-tinted automatically, and is not tied to our painted head at all.
- `Ears_Floppy`, `Ears_Pig`, `Ears_Cat` are the same pattern. `Ears_Human` has no render node: it is the "no extra ears" choice.

## What an attachment buys, and what painting buys

| | add-on part | painted into the head |
|---|---|---|
| Overlap the body | yes, layer 70 | **also yes**: the 512 px head canvas has margin and the head draws over the body (the Ortolan ears already overlap its body in the shot). READ: the whole canvas is a 1.5 x 1.5-cell mesh, so the margin is finite (`head_envelope_2026-10-20.md`) |
| Lines up with our head | **no**: anchored to the vanilla head; this is the Ortolan/Nelvaanian/Lasat defect | yes, by construction |
| Art quality | one generic ear for every species | ours, per facing |
| Skin colour | automatic | needs a mask, or the head is drawn as painted (see below) |
| Hide under headgear | UNMEASURED: no `skipFlag` on the ear node, so probably drawn over a hat | no: shares the head sprite |
| Toggle by gene / vary | yes | no (fixed per head type — fine for a fixed species) |
| Facial Animation | n/a: FA is excluded for these species (`Human-RSW_*` list), so painted eyes lose nothing | |

**Verdict: the owner is right.** The only thing attachments do that painting cannot is the gene toggle and automatic tint, and neither is a feature for a fixed, hand-painted species. They cost alignment, a double set of ears and a second source of truth.

## The rule
1. **Silhouette parts are painted:** ears, horns, crests, snouts, trunks, stalks, brow ridges. Part of the creature, part of the head PNG, per facing.
2. **Attachments only for what is genuinely separable:** a species-agnostic cosmetic a player may add to anyone, or something that must render beyond the canvas margin or in front of hair. Today's list of such parts in our species: none.
3. **A painted species carries no attachment gene for a painted feature.** Remove `Ears_Floppy`/`Ears_Pointed`/`Outland_Ears_FlatPointed`/`RSW_Eyes_Big*`/`RSW_FacialRidges_*`/`RSW_Brow_Ridged` where the head art already shows it. To keep the endogene slot from rolling a random ear, put `Ears_Human` in it (READ: no render node; UNMEASURED: whether generation would otherwise add a random ear to a xenotype).

## Skin colour
The head shader multiplies the painted PNG by the skin colour (MEASURED 2026-10-20: ~0.65 grey on the red Mimbanese head). Three honest options per species:
- **Painted-as-is** (what Mimbanese does: `CutoutComplex` + all-black mask): the head is exactly the art; skin genes cannot recolour it. Right for a single-colour species. The body skin gene is set to the head's mean colour so they match.
- **Neutral paint + skin tint:** paint the skin in near-grey, let the tint colour it. Skin variety works; costs a repaint and a loss of painterly colour.
- **Mask-split** (UNMEASURED beyond the all-black case): a mask that names which painted pixels take the tint (skin, ears) and which stay fixed (eyes, markings). Best of both, one extra PNG per facing. Test on one species before committing.
Ortolan today is tinted blue-on-blue, which is why its head is darker than its body. Recommended: painted-as-is, same as Mimbanese.

## Rakata (eyes on lateral stalks, canon `canon_references/rakata/description.md`: both eyes visible in front view, *well outside the width of the skull*)
- Paint the stalks and eyes in the head; they are the head's silhouette (rule 1). The canvas must hold a head roughly twice normal width: this is the real constraint, and it is the SAME constraint as the Mimbanese side view. The fit tool must be told the allowed extents per facing, not just align bottoms.
- Do not use eye attachments: they could not follow facings or the stalk and the species has no blink to animate (FA off).
- Risk: the game uses the head's bounding region for things like hair and hat fit; a very wide head will look wrong under a vanilla hat (next section).

## Helmets (UNMEASURED: nothing here is tested)
Headgear is drawn at the vanilla head size and offset. A head wider or taller than vanilla, or with ears/stalks, means the helmet covers the middle and the painted parts stick out around it. Options, cheapest first:
1. **Hide headgear on the species** (their own gear skips the head graphic, helmets still give stats). Zero art, loses the look.
2. **Species helmet defs** with their own world textures (a Lasat helmet that fits Lasat). Canonical, a lot of art, one def per helmet per species — only worth it for the few helmets the owner wants seen.
3. **Scale/offset per head type**: does not exist (READ: `DefModExt_HeadTypeStuff` is shader-only, `DrawData.scale` varies by child stage and body type only). Tabula Rasa's `DefModExt_ApparelAlts` (per-head-type worn textures) looks inert in 1.6. Detail: `design/RimStarWars/head_envelope_2026-10-20.md`.
Painted ears vs attachment ears make little difference here, except that attachment ears (layer 70) might poke through a helmet while painted ones sit under it.

## Work this implies (not filed or started)
1. Measure the vanilla head's drawn extents per facing from the game, then define the allowed envelope for painted heads. Fixes the Mimbanese side width, the Ortolan height and the Rakata question in one stroke.
2. Teach `src/RimMandrake/Utils/art/fit_head_canvas.py` the envelope (it aligns only the bottom edge now, which caused the Ortolan east shift).
3. Strip duplicate attachment genes from Ortolan, Nelvaanian, Lasat, Mimbanese (Ears_Human in the slot) and re-shoot with `shoot_lineup_facings.py`.
4. One live test: a hat on a painted-eared pawn and on an attachment-eared pawn. Answers the helmet and layer questions with a state read plus a picture, joint with him.
