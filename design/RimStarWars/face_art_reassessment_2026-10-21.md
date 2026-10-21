# Face art re-assessment — every head, aligned, tinted and dressed (2026-10-21)

Item: `FACE_ART_DESIGN_ALIGNING_EARS_AND_HELMETS`. **Design only: no code, art, def or texture was changed.**
Owner, 2026-10-20: *"create a background ticket to re-assess all the in-game alien face art (and humans too) so we can
figure out how we'd like to handle that. Right now it's just a ticket to do the design, not a work order, for Bench."*
Builds on, does not redo: `design/RimStarWars/head_parts_painted_vs_attached_2026-10-20.md` (paint silhouette parts,
attach only separable cosmetics) and `design/RimStarWars/head_envelope_2026-10-20.md` (vanilla envelope, skull-mass
detector, the four refitted species, head size set in the def).
Status key: MEASURED (a tool read the pixels or defs tonight) · READ (from a def or decompile) · PREDICTED (offline
composite) · PROPOSED (an agent's number; yours to move) · UNMEASURED.

## Look first (mockups)

Open each once; the doc below explains what you are seeing.

| | picture | what it shows |
|---|---|---|
| A | `\\wsl.localhost\Ubuntu\home\mandrake\rm\bench\Transient\face_art_2026-10-21\A_vanilla_envelope.png` | the vanilla head per facing: 8 vanilla heads stacked, the red target box, the Narrow head (cyan) and today's appendage zone (yellow) |
| B | `\\wsl.localhost\Ubuntu\home\mandrake\rm\bench\Transient\face_art_2026-10-21\B_every_head_on_envelope.png` | all 40 head families in use, four facings each, on that envelope; green = fits, red = how many rules it breaks |
| C | `\\wsl.localhost\Ubuntu\home\mandrake\rm\bench\Transient\face_art_2026-10-21\C_hats_on_heads_predicted.png` | 13 heads on a vanilla body, bare and under four vanilla hats (PREDICTED: drawn offline, not taken from the game) |
| D | `\\wsl.localhost\Ubuntu\home\mandrake\rm\bench\Transient\face_art_2026-10-21\D_skin_tint_options_simulated.png` | four heads under four skin colours: painted as-is, tint on the painted art, tint on a grey repaint |

What the pictures say, in one breath:
1. **Two art styles live side by side.** 91 of the 93 heads in use are the old donor-style grey cartoons, with thick black outlines and
   skin-tinted (B, C). Only the four new paintings (Lasat, Mimbanese, Nelvaanian, Ortolan) are painterly. Two of those, Mimbanese and
   Ortolan, are in full colour. This style split is the biggest open decision, and no earlier pass raised it.
2. **About 40% of the heads in use break the envelope**, nearly all of them old donor heads: 39 of 93 HeadTypeDefs (MEASURED). The four
   refitted species pass.
3. **Hats sit on the vanilla skull.** Anything wider or taller pokes out around the hat (C): Rakata stalks, Cerean and Mon Calamari
   domes, Lasat ears, Ortolan and Twi'lek hanging parts, Quarren tentacles.

## 1. Every head in the game (inventory, per facing, measured)

**Method (MEASURED tonight).** Every HeadTypeDef was parsed from the source with parent inheritance resolved. Each texture was found
by its `graphicPath` and every facing measured with `fit_head_canvas.measure_image`: the alpha bbox, plus the skull mass with
ears, horns and trunks removed (owner's 2026-10-20 skull-mass ruling). Each head was then judged by `fit_head_canvas.judge`
against `src/RimMandrake/Utils/art/head_envelope.json`. West is the mirrored east everywhere: no `_west` file exists in any
head we ship. Raw tables (one row per head and facing, ratios to the vanilla median): `D:\ClaudeWork\rimmandrake\face_art\head_inventory.csv`
and `D:\ClaudeWork\rimmandrake\face_art\head_judgement.csv`. Scripts sit beside them (`inventory.py`, `judge_all.py`, `donor_measure.py`, `mockups.py`).

| source | head types | in use | measured | pass today's envelope |
|---|---|---|---|---|
| our StarWarsRaces + Droidworks HeadTypeDefs | 147 | 103 used by one of our xenotypes, plus 19 droid heads (see note) | 136 (the 10 Togorian furskin heads use Biotech textures and are measured there; the Droidworks blank head is empty) | **54 of 93 in use** |
| vanilla Core (human heads, Gaunt, Skull, Stump) | 17 textures | all | 17 | 13 (the 3 Male Narrow heads fail only the chin rule, by 0.06–0.08; Stump is a stump) |
| Biotech (furskin) | 10 | yes | 10 | 7 (the 3 wide heads' east chin sits 0.08 low) |
| Anomaly (ghoul, cultist, leathery …) | 10 | yes | 10 | 9 |
| donor heads in the live list (ModsConfig parsed with ET: 325 active, 319 resolved) | 67: Outland Genetics 32, Big and Small 18, VRE Archon 8, Saurid 4, Genie 3, Det's Keshig 2 | gene-gated | 67 | 37 |

**Our 93 in-use heads come in 40 families** (identical variants such as Pantoran 0–8 merged; B shows one of each):
- **Fit already (19 families):** Cathar, Dathomirian, Duros-type Egghead, HeavyBone (Sith), Kaminoan, Lasat, Mimbanese,
  Mirialan, Nelvaanian, Nikto, Ortolan, Pantoran, Sullustan, Togruta and the other near-human heads. Most are a vanilla
  human silhouette and carry their difference (montrals, horns, ears) as gene attachments.
- **Break the envelope (21 families).** The rule broken most often (MEASURED, out of the 93 in use) is the skull chin sitting below the vanilla chin (24 heads, often by
  only 0.06–0.15 of a head; see §2). Next come too wide with appendages (19), appendages hanging below the chin (12), facings that
  disagree in height (11), a side view wider than the front (10), and a skull too tall (10). The big offenders:

| family | south bbox w / skull h (x vanilla) | why |
|---|---|---|
| Quarren | 1.60 / 1.26 | head tentacles below the chin, wide crown; 9 rule breaks |
| Rakatan | 1.54 / 1.53 | eye-stalks and a tall dome (see §5) |
| Cerean | 1.03 / 1.56 | tall cone skull 0.58 of a head above the crown |
| Fathead (Hutt) | 1.54 / 1.04 | wide slug head, chin 0.26 low |
| Wookiee (both texture sets) | 1.08–1.11 / 1.38–1.43 | the fur ruff reads as skull, chin 0.32–0.37 low |
| Pyke, Mon Calamari | 1.10–1.13 / 1.30–1.35 | domes above the crown |
| Twi'lek (4) | 1.39–1.41 / 1.02–1.04 | lekku hang 0.52 of a head below the chin |
| Iktotchi | 1.39–1.48 / 1.00 | horns sweep wide |
| Kubaz, Selkath, Geonosian, Ithorian | east bbox 1.25–1.32 | side profile wider than the front (snout or hammerhead) |

- **Canvas:** 126 of our textures are 512 px, 7 are 256 and 3 are 128 (the Wookiee_Average set); vanilla is 128. That is fine,
  because the game stretches every head over the same 1.5-cell mesh (READ, `head_envelope_2026-10-20.md`).
- **Colour (MEASURED, mean chroma of the south texture):** 91 of 93 are neutral grey (≤ 0.053), made for the skin tint. Mimbanese (0.34) and
  Ortolan (0.40) are full colour.
- **Unused heads (25, no xenotype of ours references them):** Devolved and Devolved Nomad, Fivehead (three types), Geonosian, Gungan,
  Ithorian, Rodian and Trandoshan in the SWX set, Selkath_Normal, and the absorbed `Male/Female_HeavyBoneNormal`. They are candidates to delete
  when this work runs, not to fix. Checking whether a PawnKind reaches them is part of the work order.
- **Droid heads (19, Droidworks):** they have no `requiredGenes` and no `randomChosen=false`. HAR alien races list them in their own
  `headTypes`, so they are not organic heads and are out of scope. UNMEASURED: whether HAR stops a baseline human from rolling one;
  one look in a character-creation screen would settle it.

## 2. The envelope and the allowed overhang

**The target (MEASURED, unchanged from 2026-10-20; A shows it).** The median of the 8 Average/HeavyJaw vanilla heads, in 512-px terms:
south 184 w x 200 h, chin at 358; east 200 x 200, chin 356, centred at 256; north the same as south. The Narrow heads are 156 wide with the chin at
366. Every painted head's SKULL must land in that box. Ears, horns, crests and trunks are judged separately against the
alpha bbox allowance.

**One correction found tonight (MEASURED): the chin rule is stricter than vanilla itself.** At the current ±0.06 of a head, 7 of
35 vanilla and DLC heads fail: all three Male Narrow heads, the three Biotech wide furskins and one ghoul. At **±0.08 all 35 pass**, and 66 of our 93 do
(64 today). PROPOSED: chin tolerance 0.08, the narrowest value under which the game's own heads pass. The tool's selftest sanity probe then
proves the instrument still flags the pre-fit Mimbanese and the ear-seated Ortolan.

**Allowed overhang, PROPOSED as named classes instead of per-species numbers.** Today two species carry one-off overrides (Lasat, Ortolan). With 21
failing families, overrides do not scale, so each kind of appendage gets one allowance:

| class | example | width x vanilla | above crown | below chin | why |
|---|---|---|---|---|---|
| none (default) | human, Pantoran | 1.25 | 0.25 | 0.25 | today's numbers |
| side ears | Lasat, Iktotchi horns | 1.65 | 0.40 | 0.25 | Lasat override, as ruled on 2026-10-20 |
| hanging (lekku, pendant ears, tentacles, ruff) | Twi'lek, Ortolan, Quarren, Wookiee | 1.55 | 0.25 | 0.80 | Ortolan override; the hang rides down over the body, which the head layer already draws over |
| dome (tall skull) | Cerean, Mon Calamari, Pyke | 1.25 | 0.60, plus a skull height up to 1.60 | 0.25 | the dome IS the skull: a skull limit of 1.25 would force a shrunken face |
| stalks | Rakata | 1.80 | 0.60 | 0.25 | §5 |

Hard limits that do not move: 0.02 of canvas clear of every edge (nothing draws past the mesh), skull centred within 0.03, and
facings agreeing in skull height within ±10%. A side view wider than the front is allowed to 1.35x for snouted species (Kubaz, Selkath,
Geonosian, Gungan), with a class `snout`. The class lives in `head_envelope.json` against the HeadTypeDef, so the check stays data.

## 3. Painted vs attached parts, per species

The rule stands as written on 2026-10-20: **silhouette parts are painted; attachments only for separable cosmetics; a painted species carries no attachment gene for a painted feature.**
Tonight's census (MEASURED from the xenotype gene lists, Core + Biotech + ours, inheritance resolved): 36 of the 55 xenotypes
that use our heads carry render-node attachment genes. Body-only nodes (`RSW_Body_gaunt`, tails, furskin, the Falleen body attachment) are
not head parts and are left out of the list below.

| species | head attachments today | verdict |
|---|---|---|
| Lasat | `RSW_FacialRidges_bumpy` | **strip**: the painted head shows its ridges (the only duplicate left on the four new species) |
| Mimbanese, Nelvaanian, Ortolan | none | done (stripped 2026-10-20) |
| Cathar | `Ears_Pointed` | keep for now: the head is a vanilla silhouette and the ear is the only difference. Becomes "strip" if Cathar is repainted |
| Togruta | `RSW_TogrutaMontrals` | keep: an attachment on a vanilla-shaped head is the *other* coherent pattern (below) |
| Dathomirian | `RSW_ZabrakHornsMale` | keep (same pattern) |
| Zygerrian | `RSW_Ears_BigCat`, `RSW_Beard_chinspines` | keep, until it gets its own head (today it borrows Cathar's) |
| Taung | ridges, brow, headbone, webbed ears, big yellow eyes (5) | has its own head (`RSW_*_TaungHead`): **audit it against the art when repainted** (UNMEASURED whether the head already paints any of the 5); the 5-attachment stack is the likeliest case of double features |
| Kel Dor, Feeorin, Klatoonian, Weequay, Tusken, SithZ, Neimoidian | ridges, flaps, noses, chin tendrils | keep while their heads stay vanilla-style; strip each one the day its head is painted |
| Duros, Sullustan, Ewok | `RSW_Eyes_HugeRed` / `RSW_Eyes_Big` | strip if the head paints the eyes (UNMEASURED for Duros and Sullustan: **check in game**) |
| Gamorrean, Jawa Gamorrean, Snivvian, Ugnaught | jowls, tusks, pig nose and ears | keep (vanilla-style heads) |
| Gungan, Defel, Togorian | ears | keep (vanilla-style heads) |

**So there are two coherent patterns, and each species should be clearly one of them:**
- **A, painted:** the head PNG carries the whole silhouette and the species has no head attachments. Used by Lasat,
  Mimbanese, Nelvaanian and Ortolan, and needed by any head that leaves the vanilla outline.
- **B, vanilla-style with attachments:** a vanilla-outline head (ours or vanilla) plus gene parts. Fits Togruta, Dathomirian, Cathar and the
  near-humans. It is cheap, tints cleanly and works under hats the vanilla way.
Mixing the two (a painted feature plus an attachment of the same feature) is the defect. **The slot placeholder:** `Ears_Human` has no
render node (READ). Whether a xenotype with no ear gene rolls a random ear is still UNMEASURED; the work order checks it with one generation
read before adding `Ears_Human` everywhere.

## 4. Skin colour (and the mask-split test)

**What the game does (READ + MEASURED 2026-10-20):** the head shader multiplies the painted RGB by the skin colour. D shows the result:
a full-colour painting tinted again turns muddy (Ortolan blue on blue, Mimbanese red on grey). A neutral head, like every donor
head and our Twi'lek, takes any skin cleanly. The painted Lasat is near-neutral (chroma 0.053), so it tints reasonably.

**Per species, PROPOSED:**

| species | choice | why |
|---|---|---|
| Mimbanese, Ortolan | painted-as-is (all-black `CutoutComplex` mask, as Mimbanese has now) | single-colour species in canon; the paintings' colour is the art; body skin gene set to the head's mean colour so they match |
| Lasat, Nelvaanian | tinted as now | already near-neutral; skin variety stays |
| all 91 neutral heads | tinted as now | made for it |
| future painted species with canon skin variety (Twi'lek, Togruta, Mirialan) | mask-split | keep painted eyes and markings, tint the skin |

**Humans:** keep the vanilla heads, vanilla-tinted. Repainting them would put our painterly style on every human for very little gain, cut
the tie with every hair, beard and hat mod, and is the largest art bill on the list. Revisit only if you choose "repaint everyone" in
decision 1.

**Mask-split test (design; run with the owner, needs a load):** one species (Ortolan: one colour in the art, so a wrong mask shows at once).
1. Hand-paint `Ortolan_Head_{south,east,north}m.png`: red channel = skin (dome, trunk, ears), black = eyes and mouth.
2. Spawn three Ortolans with skin colours light, blue and green; shoot S/E/N.
3. Pass when the eyes keep their painted colour in all three, the skin follows the gene colour, and no fringe shows at the mask edge
   at zoom 13. Read `Pawn.story.SkinColor` per pawn so the picture and the state agree.
4. UNMEASURED today: whether Tabula Rasa's `CutoutComplex` head shader honours the red channel the way apparel masks do. This is the one
   fact the test exists to settle.

## 5. The wild species

The heads wider than a skull, MEASURED (south bbox w, skull h, in vanilla units): Rakatan 1.54 / 1.53, Quarren 1.60 / 1.26,
Fathead 1.54 / 1.04, Iktotchi 1.39–1.48, Twi'lek 1.39–1.41 (+0.52 below the chin), Cerean skull 1.56, Ithorian east 1.32 with a skull
facing ratio of 0.62 (the hammerhead's side view is short and long). Ortolan 1.52 and Lasat 1.47 pass only under their overrides.

- **Canvas room exists.** On a 512 canvas the vanilla head fills 0.36 x 0.39. The widest allowance in §2, 1.80x, uses 0.65 of the
  canvas, leaving the 0.02 margin with room to spare. **No head needs a larger canvas or mesh.** The limit is legibility under hats
  and next to vanilla pawns, not pixels.
- **Rakata:** paint the stalks (rule 1), class `stalks`. The canon wants both eyes visible from the front, outside the skull width
  (`design/RimStarWars/canon_references/rakata/description.md`). Today's head is an old donor cartoon (1.54 wide, dome 0.55 above the crown),
  not yet one of our paintings.
- **Trunks, tentacles, lekku** (Ortolan, Quarren, Twi'lek) all hang below the chin over the chest. The head draws over the body on
  south and east (C shows it). On north, the hang hides behind the head; it shows only where it is wider than the skull.
- **Ithorian:** the side view breaks facing agreement by design (a hammerhead is short seen from the side). Give it a `facing_height_tol`
  override with a reason rather than forcing a distorted side view.
- **Antennae** (none in the in-use list today): class `stalks`.

## 6. Headgear (and the joint hat test)

**What is known (READ, 2026-10-20):** a hat draws on the same head mesh, at the vanilla head's size and place. Big and Small scales it with
the head. No vanilla or Tabula Rasa field gives a per-head-type hat offset or scale: `DefModExt_HeadTypeStuff` only changes the shader, and
`DefModExt_ApparelAlts` keys on a static that is never set, so it looks inert. **PREDICTED (C):** a vanilla hat covers the skull of
every envelope-fitting head and leaves the appendages showing around it. Lasat ears through a helmet, Ortolan ears below a cowboy hat
and the Cerean dome above a tuque all look intentional enough. The Rakata stalks *through* the helmet do not, because the hat draws over them.

**Options:** (a) **leave it**: vanilla hats on every head, appendages showing (zero cost; reads fine for 19 + 4 families); (b) **hide hats per species**
(`renderSkipFlags`/hat-hiding for the few that look wrong: Rakata, Quarren, Cerean, Mon Calamari); (c) **species helmets** only where a hat
matters to the fiction; (d) per-head-type hat offset/scale needs our own C# (a Harmony postfix on the apparel node's
`drawData`). That is a real build, not a def, and only worth it if (a) fails in game.

**Joint hat test (design; with the owner, bridge holder runs it):**
1. Save: the 2026-10-20 keeper `XENO_HEADS_REVIEW_2026-10-20.rws` (grid L→R: Human×2, Lasat×2, Mimbanese×2, Nelvaanian×2, Ortolan×2), plus one
   Rakatan, Twi'lek, Cerean and Quarren spawned in the row.
2. Put the same three hats on everyone: SimpleHelmet, CowboyHat, PowerArmorHelmet. Also put one Lasat in the painted-ear state and one
   with an attachment ear (`Ears_Pointed` added), for the layer question.
3. Read per pawn: the head node scale, the apparel node's layer, whether hair is hidden, and `HeadTypeDef`. Shoot S/E/N/W at zoom 13, midday,
   beside the offline C composite.
4. Decide on the spot: does C match the game (if so, the offline composite becomes the hat check for every future head)? Does the
   attachment ear draw over the helmet (layer 70) while the painted one sits under it? Which species, if any, go to option b or c?
5. Records: a lesson for any PREDICTED/live disagreement; a ruling by card for b/c per species.

## 7. Hair, beards, Facial Animation

- **Hair on painted heads (MEASURED from gene lists):** 48 of the 55 xenotypes using our heads carry a Bald gene. Six (Bothan, Cathar,
  Mirialan, Pantoran, Snivvian, Ugnaught) roll hair on purpose: all vanilla-outline heads, so vanilla hair fits. **Cerean carries no
  hair or beard gene at all**, so it rolls random hair onto a 1.56x cone skull. PROPOSED: Bald for Cerean, or a Cerean-only hair tag.
- **Rule, PROPOSED:** pattern A (painted) species are Bald and beardless, with any hair painted into the head. Pattern B species may roll vanilla hair,
  because their head is the vanilla outline the hair mesh was built for (`hairMeshSize` 1.5 on AverageBase, READ).
- **Beards:** `RSW_Beard_chintendril/chinspines/fishmouth` are attachments that sit on the vanilla chin. They follow the same rule: painted species
  paint them.
- **Facial Animation:** our species are excluded through FA's ignore list, which tonight holds 68 `Human-RSW_*` entries (MEASURED).
  **But that list lives in the owner's own `Config\Mod_1635901197_FacialAnimationMod.xml`, not in any mod we ship (READ: grep of `src/` finds no FA ignore-list patch).** On a player's
  install every one of our species would draw FA's anime face over the painting, as happened on 2026-10-20. That is a shipping
  defect, not a design choice. The fix lives in our mod: a patch, or our own small Harmony gate that skips FA for `RSW_` xenotypes, plus a
  live proof on a fresh config. It belongs in the work order (§8), and the existing `HeadSetForFA_Revive.xml` in MandrakePatches shows we
  already patch the FA family.

## 8. Tooling follow-on (proposed work order, only after your ruling)

Name for filing: `HEAD_TOOLS_TEACH_THE_CLASSES` (not filed). Steps:
1. `head_envelope.json`: chin tolerance 0.08 (§2); add the appendage classes and a per-HeadTypeDef class map; Lasat and Ortolan
   move from overrides into classes `side ears` and `hanging`.
2. `fit_head_canvas.py check --all-defs`: walk every HeadTypeDef the way tonight's `inventory.py` did (inheritance, `graphicPath`,
   in-use by xenotype), so the census is one command and runs in the nightly selftests.
3. `fit_head_canvas.py hats`: the offline hat composite (mockup C) as a subcommand, once the joint test says it predicts the game.
4. A skull-detector fix for fur ruffs (the Wookiee's ruff reads as skull, chin +0.37): an ear-tip / ruff walk like the trunk walk.
5. Unused-head deletion (25 heads), after checking PawnKind `forcedHeadTypes` reach.
6. Ship the Facial Animation exclusion in a mod (§7), proved on a clean FA config.
7. A selftest that a painted (chroma > 0.15) head is Bald, has an all-black or real mask, and no attachment gene of its own kind.

## Decisions for the owner

**D1. Two art styles: what do we do about it?** (91 donor-style cartoon heads vs 4 painterly ones; picture B)
1. *Mix on purpose:* paint only the species that leave the vanilla outline, and leave near-humans as clean cartoons. Cheapest; the mix stays visible side by side.
2. *Repaint every alien, keep humans vanilla:* about 40 families in our style. Consistent aliens, and a big art bill.
3. *Repaint everyone, humans too:* fully consistent, the biggest bill, and it breaks compatibility with hair and hat mods.
4. *Pull the four paintings back to the cartoon style:* consistent with the game, but loses the art you called much higher quality.

**D2. Chin tolerance:** (1) 0.08, the narrowest value under which every vanilla head passes; (2) keep 0.06 and list the 3 Narrow heads as known exceptions;
(3) 0.10, which passes 75 of our 93 at once but lets a head sit visibly low.

**D3. Appendage allowance:** (1) the five named classes in §2; (2) keep per-species overrides (fine for 4 species, painful for 21);
(3) one generous allowance for everyone (simple, and lets a sloppy head through).

**D4. Skin colour for painted heads:** (1) as §4: painted-as-is for single-colour species, mask-split for species with skin variety;
(2) everything neutral-repainted and tinted (one system, loses painted colour; see the eyes in D); (3) everything painted-as-is (no skin
variety for any painted species).

**D5. Hats:** (1) leave vanilla hats on everyone and see it in the joint test first; (2) hide hats on the 3–4 species where they look wrong;
(3) species helmets for a chosen few; (4) build per-head hat offset/scale in C# (only if 1 fails).

**D6. Joint tests:** (1) run the hat test and the mask-split test in the same sitting (one load, about 15 minutes cold); (2) the hat test only, with the mask
waiting on D4; (3) neither until D1 is ruled.
