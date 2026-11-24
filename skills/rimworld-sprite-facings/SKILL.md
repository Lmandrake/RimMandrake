---
name: rimworld-sprite-facings
description: The facing half of generating-rimworld-sprites. Use for ANY north/south/east/west facing question; wiring or auditing a Graphic_Multi facing set or _north/_south/_east files; mirror/flip and west-mirrors-east; a creature that looks huge or small from one side, or whose north shows a face; flying-animation frames, flyingAnimationFramePathPrefix and flip-book asset shape; PawnRenderNodeProperties_Spastic appendages; and before generating, validating or shipping any multi-facing creature or building art.
---

# RimWorld sprite facings

This skill is the facing half of `generating-rimworld-sprites`. The skill covers four things:

- what each of the four facings must show;
- how to generate a set whose facings agree;
- the checks that catch a wrong facing before the owner does;
- the separate set of pictures that a flier needs.

The parent skill holds canvas, alpha, downscaling and the validator. The flying section refers to a validation plan.
The format of that plan is in `../generating-rimworld-sprites/references/validation-plan.md`.

A building's SOUTH facing is drawn from the measured building camera: orthographic, ~35° above horizontal. A round top
is an ellipse 0.56 tall for its width. Full text:
`../generating-rimworld-sprites/references/building_camera_perspective.md`.

## 🔴 WHAT NORTH AND SOUTH MEAN — owner ruling, 2026-09-15

> *"North facing is 'looking away from the player camera' (their butt). South
> facing is 'looking at the player camera' (standard eyes-forward). We should NOT
> have 'top down view rotated north or south.' That's not Rimworld perspectives.
> Some of our animals currently show this."*

| facing | what the viewer sees |
|---|---|
| **south** | the creature's **front** — eyes-forward, face and belly toward camera |
| **north** | the creature's **rear** — its back, its behind; **no face, no eyes** |
| **east / west** | a side **profile** |

⛔ **A top-down view rotated 180° is NOT a north/south pair.** Such a pair is one view turned around. The owner named
this specific defect. North and south must show *different surfaces of the animal*, back versus face. North and
south must not show one surface at two rotations.

### Why this section exists — measured 2026-09-15

This skill once did not say what north and south *mean*. The cost showed in one review sitting of 28 Pyrelands rows. 19
rows were creatures. Only about three of the 19 had no defect. The wrong north and south dominated the owner's rejection
notes: *"North is HUGE compared to east, and South isn't south"* (Anooba) · *"Norht isn't north, south isn't very south
either"* (Orray) · *"south isn't south, north isn't north"* (Iriaz).

🔴 **The donor art (the `SWBestiary` art that came from other mods) obeys the convention. On that date our regenerated
art broke it.** Three creatures existed both as donor art and as our override. The numbers are the mirror-symmetry of
the visible silhouette:

| creature | donor (SWBestiary) | our override |
|---|---|---|
| Dalgo | 0.96 / 0.97 | **0.31 / 0.18** |
| Iriaz | 0.99 / 0.99 | **0.49 / 0.47** |
| Nuna | 1.00 / 1.00 | 1.00 / 0.99 |

190 donor three-facing sets were measured. The convention is consistent across them: the norths cluster at 0.96–1.00.
A few shipped donor files are wrong. For example, Nuna's donor north shows a beak, so that north is inverted.

**Vanilla agrees on symmetry. Measured 2026-11-23 on the 127 vanilla animals of `facing_scale_calibration.json`**, with
the formula of `art_checks.py`:

- The median score is 0.99 for north and 0.99 for south. East has a median of 0.73.
- 123 norths and 122 souths reach the floor of 0.80. Five animals fail in one facing or both: Squirrel, Cobra,
  HermitCrabC, HermitCrabA and HermitCrabA_Stationary.
- A symmetric silhouette fits a front view and a top-down view alike. `facing_scale_lint.py` models the vanilla north
  and south as top-down. The owner's ruling above decides our art, whatever vanilla does.

### Generate to satisfy this, not to be judged against it

- **Say the surface, never the compass.** A prompt that says only "north" invites a top-down rotation. Say *"rear view,
  seen from behind, no face or eyes visible"* and *"front view, eyes toward the viewer"*.
- **The art daemon stamps these words itself.** When a creature job declares a `facing`, `build_job_prompt` in
  `artpiped.py` adds a stamp: text that names the surface and the camera height.
  - `common.load_job` refuses a facing job whose own prompt holds one of the phrases top-down, top down, overhead, or
    three/four/all facings. A negated phrase is refused too. The check does not see a wrong surface, such as a visible
    face in a north prompt.
  - A prompt with the words "building sprite" gets another stamp. That stamp asks for a camera that looks straight
    down, not the ~35° camera above. So check the camera of such a render.
- **Derive facings from ONE master rather than prompting three.** `ARTPIPE_FACING_COHERENCE_1` rules this: *"N faces
  away, S faces toward, facings derived from one master"*.
  - Three independent prompts share no reference. So height, palette and facing can all disagree.
  - `fill_queue.py` does the derivation for a row that asks for east and has no `reference`. East is the master, and
    north and south carry `derive_from`. An explicit row `derive_from` overrides the east master.
  - A row with no east, no `derive_from` and no `reference` files independent prompts. A row with `--no-derive-facings`
    does the same. Avoid such a row.
  - Each derived facing is still one render, an edit of the master.
- **Yield, measured**: 94 generations produced 65 sprites (1.45 attempts each). 25 of 65 targets needed more than
  one attempt, and some needed three. A correct facing in the prompt is the cheapest credit that you will ever save.
- **East/west drifts top-down too, not just north/south.** East and west facings drift toward an overhead camera.
  The drift happens even when the prompt says "strict side profile" (owner ruling 2026-09-16, gizka
  east). So the prompt must forbid the overhead camera explicitly. The daemon's stamp does this. In a prompt outside the
  daemon, write that yourself.
- The hedge of a canon entry ("reads almost one-eyed") can become a literal cyclops in the render. The cyclops comes
  when the prompt does not forbid the overhead camera.

### What can be checked without a model, and what cannot

Mirror symmetry about the vertical axis separates a profile-as-north from a real rear view. Orray's north scored
**0.53**. The donor cluster is 0.96–1.00. The check agrees with the owner's eye on Orray, Iriaz and Anooba-south. The
check is `facing_symmetry` in `src/RimMandrake/Utils/art_checks.py`.

⛔ **Symmetry cannot catch a FACE in the north**, because a frontal face is symmetric. Anooba's north scored 0.84 while
it showed teeth to the camera. Something that looks at the image must catch that fault.

**Symmetry also cannot catch every PROFILE passed off as a north. A blobby silhouette is symmetric by accident.**

- `Gizka_north.png` scored 0.845 mirror-symmetry, above the 0.80 north/south floor. The picture was an unmistakable side
  profile that faced right.
- The comment on `SYMMETRY_MIN_NS` in `art_checks.py` says that no value of the floor separates the two cases. A visual
  judge caught the profile in 17.8s.
- Use this counterexample when someone argues that a numeric gate makes a look at the image unnecessary (BENCH
  2026-09-15).

🔑 **When a visual property resists every numeric proxy tried, the ruled LLM judge IS the instrument.** The judge is not
a fallback for the time when the real check is unavailable.

- The example is an audit of the camera height of south facings, against a true top-down angle. No pixel statistic
  separated the two. So a `claude -p` judge of the rendered frame became the measurement (BENCH 2026-09-17).
- Flag an UNMEASURED verdict of the judge as UNMEASURED. Never pass it as if a numeric check had run.
- **The judge must first pass a calibration on art that our pipeline never touched.** The judge of that example failed
  the calibration of 2026-09-20. The judge called 5 of 6 donor sets OVERHEAD (83%), more than our own art. So its OVERHEAD
  verdict in `src/RimMandrake/Utils/artpipe/facing_set_audit.py` is ADVISORY: a list for a human look, never a gate.

### Cross-facing size and height, not just symmetry

- 🔴 **Run a cross-facing size audit at WIRING time, for every creature facing set.** Run
  `src/RimMandrake/Utils/artpipe/facing_set_audit.py`. The audit measures the spread of the major-axis bbox
  across facings, and flags anything over 15%.
  - The structural gates of the sprite validator check each facing against its own reference. The gates do not check
    facings against EACH OTHER. The gap is exactly the anooba-looks-huge class of defect.
  - In the audit of 2026-09-16 all 12 sets passed. The borderliners were `nuna-female` at 14.3% and `sytheclaw` at 10.6%.
- **Facing HEIGHT is measurable and predicts an owner rejection before he looks.** The measurement caught the one row
  that he flagged, at 1.85x (2026-09-15).
  - Our art is drawn from a ground camera. There, height cannot legitimately change with the viewing angle. Width can.
  - In art drawn top-down, as vanilla is, north and south legitimately stand taller than east. `facing_scale_lint.py`
    judges each view by its own model. Our own quadruped, biped, flyer or animal of unknown plan is judged as top-down.
    The exception: that view and the east each show two or more feet. Our other body plans are judged as ground camera.
  - Two limits differ by tool. `art_checks.py` flags a height ratio above 1.35. `facing_scale_lint.py` uses the spread of
    vanilla. The art judge runs the gate of `facing_scale_lint.py`. That gate needs our own
    east picture of the creature, and a south or a north picture.
  - The art judge may refuse a set for a size that differs between facings (owner, 2026-11-19: "Allow the Judge to bounce
    incorrectly sized creatures").
- **Do not pre-fill a review sheet on provenance alone** (whether the current wave touched the row). That pre-fill
  mispredicted 6 of his first 9 verdicts.
  - He judges if the sprite LOOKS painterly, if the anatomy is canon, and if the scale agrees across facings. You can
    measure only the last one before you ask him to look (2026-09-15).

More traps for this section: [references/traps.md](references/traps.md) § Cross-facing size and height, not just symmetry.

### No facing may BE another facing — and what that test does and does not find

**✅ The identity case is the single highest-yield check in this skill.** Hash every facing and every variant. A match
means that a file was copied, not drawn. `art_checks.py` (`duplicate_facings`) does this for facings and variants.
`facing_set_audit.py` compares only the files that you give it, so it can miss a copy between `_m` and `_f`.

- Measured 2026-09-15, the hash found seven real pairs in one biome's roster:
  - Anooba's male sprite was byte-identical to the female in **all three** facings;
  - Nuna's male north and south were the female's;
  - GizkaW differed from Gizka on east alone.
- One of those pairs *caused* an owner complaint that he could only phrase as *"north and south aren't the right
  color"*. The colour was wrong because the file was the wrong animal's.
- Those pairs are gone: on 2026-11-23 no two of the installed Anooba, Nuna and Gizka files were the same.

⛔ **The rotation/flip extension was measured and abandoned.**

- The idea was to catch a facing that was manufactured from another. The test tried all eight dihedral transforms
  (90/180/270, each with and without a flip). The test exempted east↔west, since west legitimately *is* a flipped east.
- The test compared 84 within-set pairs at native scale, over the union silhouette. So shared transparency could not
  inflate the score.
- **Nothing reached 0.90.** The whole corpus sat between 0.57 and 0.86. No defect here was a literal rotation of another
  facing.

Three measurement traps burned on the way to that answer. Each trap makes the metric look correct when the metric is not:

| what I did | why it lied |
|---|---|
| cropped each sprite to its own bbox and stretched both to 64×64 | destroys scale, so a wide profile and a narrow rear view look alike — Porg, a **correct** pair, scored 0.86 |
| compared whole canvases at native scale | mostly-transparent 512×512 art matches on *emptiness*; every pair scored 0.83–0.98 |
| `point(lambda v: 1 if …)` then `.convert("1")` | `convert("1")` thresholds at 128, so 1 → 0 and every IoU came out **0.00** on all 40 sets |

The wrong views that we had were drawn from the wrong angle, not manufactured. So **mirror symmetry catches them and
exact-transform matching does not**. Keep the hash. Do not add a fuzzy transform threshold without a corpus that
separates the cases.

The full ruleset, both tiers, is in `design/RimMandrake/art_review_facts_spec.md`.

More traps for this section: [references/traps.md](references/traps.md) § No facing may BE another facing — and what that test does and does not find.

### Measuring a sprite's extent — use the VISIBLE silhouette

🔴 **Never take an alpha bounding box at `alpha > 0`.** Renders in this project carry a sub-visible export halo: alpha
1–16, under 6% opacity. **13 of 19** sampled rows carried it. The halo inflates the box far past the painted body.
`FurnaceBeast_east` had 3,901 such pixels that reached y=480, while the body stopped at y=400. The result was a 460px
box around a 286px animal.

A measurement at `alpha > 0` on downscaled thumbnails produced two false "clean" verdicts. The owner was told both
verdicts before the error was caught:

- FurnaceBeast at 1.03× (really **1.64×**);
- BarbSlinger at 1.15× (really **1.61×**).

✅ Threshold at **`alpha > 16` on the original**, never on the thumbnail.

The halo is a defect of the export step, worth a fix there. Do not re-render 13 sprites for the halo. The halo is a
defect of one sprite only when it displaces the silhouette (`transparency_real` in `art_checks.py`).

🔴 **LANCZOS resampling amplifies alpha dust.** Alpha dust is near-zero but nonzero alpha that reaches past the visible
silhouette. The resample rings. Measured on one facing: 1055→3452px of such pixels. The resample traded a boundary-clip
finding for a worse `transparency_real` finding. Of 4 resamplers tested (LANCZOS/BICUBIC/BILINEAR/BOX), only **BOX**
(area-averaging) left the file no worse than before. For a repad/recenter-in-place fix on existing game art, prefer
BOX.

More traps for this section: [references/traps.md](references/traps.md) § Measuring a sprite's extent — use the VISIBLE silhouette.

### Two more traps from the same sitting

- ⛔ **A delivered file is not proof a render happened.** Duplicates look like finished work. The three duplicate sets
  above (Anooba, Nuna, GizkaW) show this. **sha256 every facing and variant** before you call a set complete.
- ⛔ **Provenance is not appearance.** The pre-fill "this came through the current pipeline, so keep it" mispredicted
  **6 of the owner's first 9 verdicts**. He rejected Bolotaur and Iriaz as *"cartoonish"*, although both passed through
  the painterly wave. What the pipeline touched says nothing about what the sprite looks like.

## Multi-facing assets

RimWorld `Graphic_Multi` things ship four facings that must agree. A hole in one flank appears in every view that can
see that flank.

**Prove one facing before attempting four.** Four-view consistency can fail for reasons that have nothing to do with the
pipeline. One facing is enough to learn if the art direction survives downscaling.

### ⚠️ Generate facings individually, not as a 2×2 sheet

A sheet draws one machine four ways in one pass. A sheet is the obvious way to get consistency. **Measured 2026-08-12,
it is the wrong trade.** The reason is resolution, not art.

A generation returns roughly a fixed pixel budget, regardless of what is in the picture. When four facings share one
picture, each facing gets a quarter of the budget:

| approach | pixels per facing | oversampling vs a 512×640 sprite |
|---|---|---|
| 2×2 sheet (1254×1254) | ~393,000 | **1.2×** |
| individual (1120×1405) | ~1,574,000 | **4.8×** |

**4× fewer pixels per facing, leaving almost no downsampling headroom.** A finished sprite is crisp because it was
generated well above target and then area-averaged down. At 1.2× there is nothing to average.

The sheet also did some things well, so this is a trade and not a failure. The sheet held the 2×2 layout, and kept the
viewing direction of each cell. Its four panels were more alike in style than four independent runs. The sheet still did
not deliver verifiable damage correspondence between views.

**Recommendation: generate each facing individually, anchored to a chosen sibling.** Ask for a match on palette,
material and damage language. That buys most of the consistency at full resolution. The ways to anchor:

- **Through the art daemon: `derive_from`.** The job attaches the accepted master as its image. A job attaches one
  image only.
- ✅ **Anchor with WORDS.** Edit each facing from ITS OWN reference, and carry the approved sibling's treatment in the
  prompt: *"segmented chitin plating with clean segment breaks, speckled shell, wet translucent flesh with a
  bioluminescent glow inside it, deep red and rose palette, hard black outline"*.
  - Write such a sentence down the moment the first facing is approved. Measured 2026-08-24: the sentence held three
    facings together on two different creatures.
  - Copy the method, not the words "hard black outline". The house art now has no outlines (owner card 2026-10-04).
    The rule and its exception: `design/RimMandrake/art_judge_brief.md`, rule B1a (No outlines).
- **Two images: the reference as image 1 and the approved facing as image 2.** This form is not proven for sibling
  facings. Two-image calls hung three times running. That looked like the cause and was not. A two-image edit of a
  building worked on 2026-10-14 (`../generating-rimworld-sprites/references/building_camera_perspective.md`).

**Codex `edit` hangs on roughly one call in four, with no error of its own.**

- Cap `--timeout` near **105 s**. A good call returns in 79–93 s.
- Run one call at a time in the foreground. When a call fails, run the same call again. Do not put the retry loop inside
  a batch script.
- **The full measurement, the budgeting table and the harness bug that made the hang look worse than it is live in
  `~/dev/MandrakeWorkflows/skills/generating-images/SKILL.md` > "Cost and timing".** The facts are engine facts, not
  sprite facts. So the facts are in one place.

→ The history of the Codex `edit` hang: `references/codex-edit-hang-history.md`.

More traps for this section: [references/traps.md](references/traps.md) § Multi-facing assets.

## Small animated appendages: `PawnRenderNodeProperties_Spastic`

Vanilla creatures are static by default. An arm that waves or a tail that twitches needs its own work.

- `jawa/set_pawn_rotation dir:south lockRotation:true` faces a pawn at the camera for an art shot. On a pawn that stands
  still, only one thing animates an appendage: a `PawnRenderNodeProperties_Spastic` node (the Toughspike template). That
  node idle-jiggles a texture (BENCH 2026-09-17).
- AA_GreenGoo's little arms wave, and they read as alive against our art. Study how Alpha Animals builds that wiggle
  (graphic comp, multi-frame, or shader). Do this before you assume that a creature needs a full flip-book (below) only to
  look animate. A small Spastic appendage may be the cheaper, correct answer (owner, first art walk, 2026-09-14).
- Spastic is correct for a small IDLE jiggle on one static texture. Spastic is wrong for a per-facing flying pose: see
  the flight ruling in the next section.

## 🔴 Flying creatures need a DIFFERENT asset shape — not a runtime wing layer (layered OFFLINE authoring baked into whole-body frames is the way to make them)

**A flier's animation is a whole-body directional flip-book, never a separate wing texture jiggled by a render-tree
node** (owner ruling 2026-09-19).

- The cause of the ruling: `FIREHAWK_FLIGHT_BEHAVIOR_1` shipped a custom `BodyDef` wing part with a
  `PawnRenderNodeProperties_Spastic` node. The node looked broken live. Sideways, the bird stood still with no visible
  flap. Going north, one wing was missing and the other was misaligned.
- The fault is not a tuning miss. A Spastic node idle-jiggles ONE static texture. The node was never built to express a
  per-facing "wings up" pose against a "wings down" pose. Nothing keeps a single wing texture registered across four
  facings.
- The rule and the owner's words: `design/RimMandrake/standing_rulings.md`, section "If it flies in the fiction". The full
  account and the mechanics: `skills/rimworld-modding/references/flight.md`.

**The real mechanism is `PawnKindDef.flyingAnimationFramePathPrefix`.** The mechanism is MEASURED against the installed
game: `Chicken_Flying_*` was extracted from `resources.assets` (UnityPy), and frame 1 was compared with frame 5:

```xml
<flyingAnimationFramePathPrefix>Things/Pawn/Animal/Chicken/Chicken_Flying_</flyingAnimationFramePathPrefix>
<flyingAnimationFrameCount>8</flyingAnimationFrameCount>
<flyingAnimationTicksPerFrame>2</flyingAnimationTicksPerFrame>
<flyingAnimationDrawSize>2.4</flyingAnimationDrawSize>
<flyingAnimationDrawSizeIsMultiplier>true</flyingAnimationDrawSizeIsMultiplier>
<flyingAnimationInheritColors>true</flyingAnimationInheritColors>
```

**What to generate, per commissioned flier:**

- `frameCount` full-body poses. 8 is vanilla's number for Chicken/Duck/Goose/Sparrow. Locust ships 5.
- Each pose shows the WHOLE animal, wings included, at a different point of the wingbeat cycle. Frame 1 is
  tucked/streamlined, and a mid-cycle frame is fully spread. The idea is that of a walk cycle, for flight.
- **Times three directions.** The name is `<prefix><N>_<direction>`, for N = 1..frameCount and direction in
  `north`/`east`/`south`. There is no separate west: west mirrors east, as in every other RimWorld facing set.
- So the total is `frameCount × 3` individual images. Do not reuse `frameCount` images across facings. Do not make a
  2×2-style sheet. The per-facing generation guidance above applies to each frame too.
- A gendered species (vanilla Quail, Peafowl) adds a second full set under `flyingAnimationFramePathPrefixFemale`.

**Before you generate anything**, read `skills/rimworld-modding/references/flight.md`. The owner's document
`~/Desktop/RIMWORLD_1_6_NATIVE_ANIMAL_FLIGHT_IMPLEMENTATION.md` (2026-09-19) is also a start point, if present. The file
was not on Archmagi on 2026-11-23. Otherwise derive the same facts from the installed game, as this section did:

- Sparrow (Odyssey) is the cleanest from-scratch template.
- Chicken/Duck/Goose (Core) are the references for an existing grounded animal that becomes a flier.
- `flyingAnimationDrawSizeIsMultiplier` scales the flying sprite relative to the grounded one. Most vanilla fliers read
  bigger mid-flight. The size is timing/scale tuning, not art.

🔴 **Standing rule for every flier's flip-book, both at rest and in the air** (owner, verbatim, 2026-09-25, as he watched
FireHawk's shipped v1 art live): **wings move, the body does not, unless a specific creature has an explicit, unusual
reason to counter it** (none identified yet). FireHawk's own v1 art hit two failure modes. The rule exists to stop them:

- **Grounded/walking sprite: wings fully folded closed, symmetric left-right, in every facing.** A flier that stands or
  walks never shows a raised or asymmetric wing. Keep the raised-wing pose for the flying frames only. FireHawk's v1
  grounded prompt asked for "one wing slightly raised as if about to take flight". That line is the defect, not a
  rendering bug.
- **Flying flip-book: the head, neck and torso stay pixel-stable.** The three keep the same fixed, level position and
  silhouette across every frame of the cycle. Only the wing pose changes from frame to frame.
  - A body that bobs reads as flicker, and it looks silly the instant it moves. A static single-frame QA pass never
    catches the bob.
  - State both invariants explicitly in every frame's prompt and in `style_notes`. The "state the invariants every
    iteration" rule of `../generating-rimworld-sprites/SKILL.md` already asks for this in restyles generally.

**Keep the eyes level between frames.**

- Register on the rigid body, never on the ink bounding box. The wings drive that box, so the box couples wing motion
  into the body.
- Place the head on its skull mass. Ignore ears, horns and crests. Where the eyes show, use them. The back view has no
  eyes, so use the head mass.
- The owner calls the vanilla Chicken a bird that "satisfies the requirements perfectly". Its head moves 0 px across all
  8 frames of all three facings. Its wings and much of its torso are redrawn from frame to frame.
- **Hold the torso still.** Whether a torso may change as the Chicken's does is a looser bar. The owner rules on it, or
  the Conductor may by a mindful act (root `CLAUDE.md`, "Only five acts stay his"). No ruling allows it now.

### Cut-out flip-books: what `flyer_cutout.py` can get wrong

A cut-out keeps one master frame as a plate and swings wing layers over it. Its body is still by construction. So the
body gates pass the cut-out, whatever the plate contains. The four faults below all passed those gates, and the owner
saw each one.

**Before you build, run `flyer_eye_checks.py parts CONFIG --src DIR --out PNG` and look at the picture.** The picture
shows the plate alone and each wing layer alone. The plate must be a wingless body with its own natural outline. Each
wing layer must hold wing and nothing else. Faults 1 and 3 are obvious on that sheet. No check that exists shows them.

1. **Two wings at once: a wing baked into the plate.** Everything outside the wing polygon stays on screen in every
   frame.
   - Some masters have a folded wing along the flank and a raised wing as well. Then the plate holds the folded wing. So
     the folded wing stays while the moving wing flaps.
   - Pick the master from what its flank shows, not only from where its wing is. A clean source has a thin torso behind
     the wing root and no wing feathers on the flank.
   - To check, measure the torso at a column behind the root against the thinnest source frame. FireHawk's plate was 47 px
     thick at x=80. The clean frame was 32 px.
   - The cut-out pass did not draw this wing. The pass made one bad frame permanent.
2. **Static-like noise when the wing points at the camera: a squash through edge-on.** A side-view pose with `sy` near
   zero projects the wing edge-on, and `turn()` samples rows without an average.
   - At `sy` -0.1, each output row covers ten source rows and reads only a few. So the outlines break into specks, and the
     pattern changes every frame.
   - An area filter removes the specks and leaves a smear. So a filter is not the fix.
   - Keep every side-view pose at |`sy`| 0.5 or above (the SQUASH row of `flyer_eye_checks.py audit`). For mid-stroke,
     use a drawn pose: a wing seen edge-on or folded along the body.
3. **Flesh ripping away: a wing polygon that crosses the body.** The polygon takes whatever is inside it.
   - An inner edge through body texture leaves the plate with a straight sliced side. The lifted wing then carries a
     strip of body away. Route the polygon along the drawn outline of the wing.
   - Where the wing and the body differ in colour, count the body-coloured pixels in the layer. The Porg's south wing held
     514 belly-white pixels of 3478. Its pale moved pixels went from 81 at rest to 738 at full lift.
   - A static sprite has no body drawn under its folded wing. So a large lift uncovers a hole. Use a small lift or a drawn
     wing.
4. **A wing that does not flap, with a sliver of it elsewhere in the quadrant: a mapping error, not art.** The quadrant
   is a quarter of that facing's picture. Some polygon
   or mask does not cover the wing's whole sweep. So the pixels outside it behave differently. Fix the mask. Do not
   redraw.

**A facing with part of its art missing** shows as an empty quadrant. The eye finds the fault at once in motion, because
one side of a symmetric bird does nothing. Motion gates add both wings together and pass it. Compare the two sides
instead (the SIDES row of `flyer_eye_checks.py audit`). Pixels moved left of the axis against right of it read 0.05 on a
frozen or erased wing. Those pixels read 0.94 to 1.00 on every other north and south in `references/flyer_truth_set.md`.

More traps for this section: [references/traps.md](references/traps.md) § Cut-out flip-books: what `flyer_cutout.py` can get wrong.

### Beat timing

**The engine holds the last frame for two steps.** `durationTicks` is `(frames + 1) * ticksPerFrame`, and the last key is
at `(frames - 1) * ticksPerFrame`. So the eye gets the last frame the longest. **Put a stroke extreme last.**

- The evidence is two sets of identical frames. Only the last frame differed. The owner said that the set that held the
  full raise appeared "to beat more and that's better". The other set held a pose part way through the stroke.
- Both sets ran 12 ticks a cycle, 5 beats a second. So the beat count did not change.
- The HOLD row of `flyer_eye_checks.py audit` reports this as advice. The advice rests on that one comparison, and the
  Chicken holds mid-stroke.

### Checking a flip-book before anyone watches it

**Audit:** `flyer_eye_checks.py audit DIR --prefix P --n N --head FACING=x0,y0,x1,y1 [--ref K] [--config JSON]`.

- The rows are FRAMES, HEAD, SIDES, SQUASH, STATIC and HOLD. HEAD tests that the head is held on the skull mass. A person
  places the head box. No box is UNMEASURED.
- The rows are fitted on `references/flyer_truth_set.md`, the eight birds that he labelled. The rows are unproven on a
  fresh batch. So green is a lead. Score any new flyer check against that table.

**When a control he passed goes red, the check is at fault.**

- The Chicken reads OFFENDER at `flier_frame_registration` (17 px, wing mass read as body). The Chicken reads red at
  `flyer_cutout check`, and BROKE at stabilize (`flier_body_stabilize.py`).
- A set started one frame later reads red at `flier_body_stabilize.py`, and at its `--lines` check. The cause: the
  `master` index in the set's config now points at another frame.
- Do not redraw art to satisfy those readings. Fix the check, or set the check aside.

**A pass from stills is not evidence about motion.** The judge passed the double wing, the squash noise and the Porg rip.
The Porg had been accepted from its frames before he saw it move. Show a judge the `parts` sheet and every frame full
size. Count what the judge catches, never what the judge passes.

**Every flyer review page gets a frame-step control and a slow speed**, beside the true game rate.

- The page has full-size frames and a true-scale view next to a vanilla human. At 5 beats a second a fault goes by too
  fast to diagnose: he could only call it noise.
- Honour the double-held last frame in the playback. If you do not, the page does not show what ships.
- `src/RimMandrake/Utils/art/flyer_step_page.py` builds such a page from frame folders. The page draws west as east
  mirrored, as the engine does.

**Also verify** these three things:

- The cycle alternates pose, and is not one static image.
- All three facings resolve. A missing `_north_3` silently drops to the bare-path fallback. See "How sprite checks lie" in
  `../generating-rimworld-sprites/references/validation-plan.md`.
- The grounded graphic returns cleanly on landing.

A screenshot of the animal as it stands still proves nothing about whether it flies.

**Do not live-test flight or capture it without the owner present** (owner: "For the third time, do not do live testing of
flyers without a human present. It doesn't work." and "Don't try to capture images of flight. It doesn't work.").

- Verify by a deterministic state read of `Pawn_FlightTracker`. Leave the look to a joint session.
- In that joint session, spawn a batch, not one. Read "single spawned pawn is not a sample" in `rimworld-debug-testing`.
- For a flier specifically, `flightStartChanceOnJobStart` makes a lone pawn unlikely to fly at all in any one observation
  window. Spawn ~20 faction-`none` and let the odds work (owner ruling 2026-09-25).


More traps: [references/traps.md](references/traps.md) § 🔴 Flying creatures need a DIFFERENT asset shape — not a wing layer.

More traps for this section: [references/traps.md](references/traps.md) § Checking a flip-book before anyone watches it.
