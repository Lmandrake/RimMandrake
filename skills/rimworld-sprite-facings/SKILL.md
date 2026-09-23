---
name: rimworld-sprite-facings
description: The facing half of generating-rimworld-sprites. Use for ANY north/south/east/west facing question; wiring or auditing a Graphic_Multi facing set or _north/_south/_east files; mirror/flip and west-mirrors-east; a creature that looks huge or small from one side, or whose north shows a face; flying-animation frames, flyingAnimationFramePathPrefix and flip-book asset shape; PawnRenderNodeProperties_Spastic appendages; and before generating, validating or shipping any multi-facing creature or building art.
---

# RimWorld sprite facings

The facing half of `generating-rimworld-sprites`: what each of the four facings
must show, how to generate a set that agrees with itself, the checks that catch
a wrong facing before the owner does, and the separate asset shape a flier needs.
Canvas, alpha, downscaling and the validator live in the parent skill; the
validation-plan format the flying section refers to is
`../generating-rimworld-sprites/references/validation-plan.md`.

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

⛔ **A top-down view rotated 180° is NOT a north/south pair.** It is the same view
turned around, and it is the specific defect the owner named. North and south must
show *different surfaces of the animal* — back versus face — not one surface at
two rotations.

### Why this section exists — measured 2026-09-15

Nothing in this skill previously said what north and south *mean*, and the cost
showed up in one review sitting of 28 Pyrelands rows. Of 19 creature rows only
about three had no defect against them, and the owner's own rejection notes were
dominated by this one fact: *"North is HUGE compared to east, and South isn't
south"* (Anooba) · *"Norht isn't north, south isn't very south either"* (Orray) ·
*"south isn't south, north isn't north"* (Iriaz).

🔴 **The donor art obeys the convention and our regenerated art breaks it.** Three
creatures exist as both donor art and our override; mirror-symmetry measured on
the visible silhouette:

| creature | donor (SWBestiary) | our override |
|---|---|---|
| Dalgo | 0.96 / 0.97 | **0.31 / 0.18** |
| Iriaz | 0.99 / 0.99 | **0.49 / 0.47** |
| Nuna | 1.00 / 1.00 | 1.00 / 0.99 |

Across 190 donor three-facing sets the convention is consistent (norths cluster
0.96–1.00), with occasional shipped errors — Nuna's donor north shows a beak,
which is inverted. ⛔ **Vanilla base-game art has NOT been checked**: there is no
RimWorld install on the Laptop and no `resources.assets`, so whether vanilla
itself is internally consistent is still owed from the Windows box.

### Generate to satisfy this, not to be judged against it

- **Say the surface, never the compass.** A prompt that says "north" invites a
  top-down rotation. Say *"rear view, seen from behind, no face or eyes visible"*
  and *"front view, eyes toward the viewer"*.
- 🔑 **Derive facings from ONE master rather than prompting three.**
  `ARTPIPE_FACING_COHERENCE_1` already rules this — *"N faces away, S faces toward,
  facings derived from one master"* — and prompting three independently is
  precisely why height, palette and facing all disagree: each is a separate roll of
  the dice with no shared reference. It also takes 3 renders per creature to 1.
- **Yield, measured**: 94 generations produced 65 sprites (1.45 attempts each);
  25 of 65 targets needed more than one attempt, some three. Getting the facing
  right in the prompt is the cheapest credit you will ever save.
- ⚠️ **East/west drifts top-down too, not just north/south.** East and west
  facings drift toward an overhead camera even when the prompt explicitly says
  "strict side profile" — the daemon's facing hook must forbid the overhead
  camera explicitly, not just word the facing correctly (owner ruling
  2026-09-16, gizka east). A canon entry's own hedge ("reads almost one-eyed")
  can become a literal cyclops in the render if you don't.

### What can be checked without a model, and what cannot

Mirror symmetry about the vertical axis separates a profile-as-north from a real
rear view: Orray's north scores **0.53** against a donor cluster of 0.96–1.00,
and it agrees with the owner's eye on Orray, Iriaz and Anooba-south.

⚠️ **Symmetry cannot catch a FACE in the north** — a frontal face is symmetric.
Anooba's north scores 0.84 while showing teeth to camera. That one needs something
that looks at the image.

⚠️ **And it cannot catch a PROFILE passed off as a north either, for the opposite
reason: a blobby silhouette is symmetric by accident.** `Gizka_north.png` scores
0.845 mirror-symmetry — comfortably past the 0.80 north/south floor — while being
an unmistakable side profile facing right; the check's own docstring concedes it
cannot catch this. A visual judge caught it in 17.8s. Keep this as the
counterexample whenever someone argues a numeric gate makes looking at the image
unnecessary (BENCH 2026-09-15).

🔑 **The general rule this points at: when a visual property resists every
numeric proxy tried, the ruled LLM judge IS the instrument, not a fallback
for when the real check is unavailable.** A facing-camera-elevation audit
(south camera height vs. a true top-down angle) found no pixel statistic that
separated the two, so `claude -p` judging the rendered frame became the
measurement itself — and an UNMEASURED verdict from that judge must be
flagged as UNMEASURED, never passed through silently as though a numeric
check had run (BENCH 2026-09-17).

### Cross-facing size and height, not just symmetry

- 🔴 **Run a cross-facing size audit at WIRING time, for every creature facing
  set** — major-axis bbox spread across facings, flag anything over 15%. The
  sprite validator's structural gates check each facing against its own
  reference; they do not check facings against EACH OTHER, and that gap is
  exactly the anooba-looks-huge defect class (2026-09-16 audit: all 12 sets
  passing at the time; `nuna-female` at 14.3% and `sytheclaw` at 10.6% were the
  borderliners).
- **Facing HEIGHT is measurable and predicts an owner rejection before he
  looks**: height cannot legitimately change with viewing angle, so measuring
  it across a set caught the one row he flagged, at 1.85x. Pre-filling a review
  sheet on provenance alone (did the current wave touch it) mispredicted 6 of
  his first 9 verdicts — he judges whether it LOOKS painterly, canon anatomy,
  and cross-facing scale, and only the last of those is something you can
  measure before asking him to look (2026-09-15).

### No facing may BE another facing — and what that test does and does not find

**✅ The identity case is the single highest-yield check in this skill.** Hash every
facing and every variant; a match means a file was copied, not drawn. Measured
2026-09-15, it found seven real pairs in one biome's roster: Anooba's male sprite
is byte-identical to the female in **all three** facings, Nuna's male north and
south are the female's, and GizkaW differs from Gizka on east alone. One of those
*caused* an owner complaint he could only phrase as *"north and south aren't the
right color"* — the colour was wrong because the file was the wrong animal's.

⛔ **The rotation/flip extension was measured and abandoned.** The idea was to
catch a facing manufactured from another by testing all eight dihedral transforms
(90/180/270, each with and without a flip), exempting east↔west since west
legitimately *is* a flipped east. Across 84 within-set pairs, comparing at native
scale over the union silhouette so shared transparency could not inflate the
score, **nothing reached 0.90** — the whole corpus sits between 0.57 and 0.86.
No defect here is a literal rotation of another facing.

Three measurement traps burned on the way to that answer, all of which make the
metric look like it works when it does not:

| what I did | why it lied |
|---|---|
| cropped each sprite to its own bbox and stretched both to 64×64 | destroys scale, so a wide profile and a narrow rear view look alike — Porg, a **correct** pair, scored 0.86 |
| compared whole canvases at native scale | mostly-transparent 512×512 art matches on *emptiness*; every pair scored 0.83–0.98 |
| `point(lambda v: 1 if …)` then `.convert("1")` | `convert("1")` thresholds at 128, so 1 → 0 and every IoU came out **0.00** on all 40 sets |

🔑 The wrong views we actually have were drawn from the wrong angle, not
manufactured — so **mirror symmetry catches them and exact-transform matching
does not**. Keep the hash; do not add a fuzzy transform threshold without a corpus
that separates.

The full ruleset, both tiers, lives in
`design/RimMandrake/art_review_facts_spec.md`.

### Measuring a sprite's extent — use the VISIBLE silhouette

🔴 **Never take an alpha bounding box at `alpha > 0`.** Renders in this project
carry a sub-visible export halo (alpha 1–16, under 6% opacity) on **13 of 19**
rows sampled, which inflates the box far past the painted body:
`FurnaceBeast_east` has 3,901 such pixels reaching y=480 while the body stops at
y=400 — a 460px box around a 286px animal.

Measuring at `alpha > 0` on downscaled thumbnails produced two false "clean"
verdicts that were reported to the owner before being caught: FurnaceBeast at
1.03× (really **1.64×**) and BarbSlinger at 1.15× (really **1.61×**). ✅ Threshold
at **`alpha > 16` on the original**, never the thumbnail.

That halo is itself a pipeline defect worth fixing at the export step rather than
by re-rendering 13 sprites.

🔴 **LANCZOS resampling on a sprite carrying sub-visible alpha dust (near-zero
but nonzero alpha reaching past the visible silhouette) amplifies it via
ringing** — measured 1055→3452px of such pixels on one facing, trading a
boundary-clip finding for a worse `transparency_real` finding. Of 4
resamplers tested (LANCZOS/BICUBIC/BILINEAR/BOX), only **BOX** (area-averaging)
left the file no worse than it found it. Prefer BOX for any repad/recenter-
in-place fix on existing game art.

### Two more traps from the same sitting

- ⛔ **A delivered file is not proof a render happened.** Anooba's male sprite is
  byte-identical to the female in all three facings; Nuna's male north and south
  are the female's; GizkaW differs from Gizka on east alone. Duplicates masquerade
  as finished work, and one of them *caused* an owner complaint he could only
  phrase as *"north and south aren't the right color"*. **sha256 every facing and
  variant** before calling a set complete.
- ⛔ **Provenance is not appearance.** Pre-filling an art review with "this came
  through the current pipeline, so keep it" mispredicted **6 of the owner's first
  9 verdicts**. He rejected Bolotaur and Iriaz as *"cartoonish"* despite both
  passing through the painterly wave. What the pipeline touched says nothing about
  what the sprite looks like.

⚠️ **This file needs a curation pass**: "Multi-facing assets" appears three times

## Multi-facing assets

RimWorld `Graphic_Multi` things ship four facings that must agree — a hole in
one flank appears in every view that can see that flank.

**Prove one facing before attempting four.** Four-view consistency fails for
reasons unrelated to whether the pipeline works, and one facing is enough to
learn whether the art direction survives downscaling.

### ⚠️ Generate facings individually, not as a 2×2 sheet

The sheet is the obvious way to get consistency — one machine drawn four ways,
in one pass. **Measured 2026-08-12, it is the wrong trade**, and the reason is
resolution rather than art.

A generation returns roughly a fixed pixel budget regardless of what is in it.
Put four facings in one image and each gets a quarter of it:

| approach | pixels per facing | oversampling vs a 512×640 sprite |
|---|---|---|
| 2×2 sheet (1254×1254) | ~393,000 | **1.2×** |
| individual (1120×1405) | ~1,574,000 | **4.8×** |

**4× fewer pixels per facing, leaving almost no downsampling headroom.** The
crispness of a finished sprite comes from generating well above target and
area-averaging down; at 1.2× there is nothing to average.

What the sheet *did* do well, so this is a trade rather than a failure: it held
the 2×2 layout, kept each cell's own viewing direction, and produced four
panels more stylistically alike than four independent runs. It still did not
deliver verifiable damage correspondence between views.

**Recommendation: generate each facing individually, anchored to a chosen
sibling** — pass the reference as image 1 and the approved facing as image 2,
and ask for a match on palette, material and damage language. That buys most of
the consistency at full resolution.

→ The Codex `edit` hang saga behind the 120 s cap, in full: `references/codex-edit-hang-history.md`.

⚠️ **Codex `edit` hangs on roughly one call in four, with no error of its own.**
Cap `--timeout` at **120 s** (a good call returns in ~80) and wrap every facing in a
retry loop. 🔑 **The full measurement, the budgeting table and the harness bug that
made it look worse than it is live in `../generating-images/SKILL.md` >
"Cost and timing"** — they are engine facts, not sprite facts, so they are kept in
one place rather than two.

⚠️ **Two-image anchoring is not reliable here** — it hung three times running, which
looked like the cause and was not. ✅ **Anchor with WORDS instead:** edit each facing
from ITS OWN reference and carry the approved sibling's treatment in the prompt —
*"segmented chitin plating with clean segment breaks, speckled shell, wet translucent
flesh with a bioluminescent glow inside it, deep red and rose palette, hard black
outline"*. Write that sentence down the moment the first facing is approved. Measured
2026-08-24: it held three facings together on two different creatures.

## Small animated appendages: `PawnRenderNodeProperties_Spastic`

Vanilla creatures are static by default — a waving arm or twitching tail is
not free. `jawa/set_pawn_rotation dir:south lockRotation:true` faces a pawn at
the camera for an art shot, but the only thing that animates an appendage on a
still-standing pawn is a `PawnRenderNodeProperties_Spastic` node (the
Toughspike template) idle-jiggling a texture (BENCH 2026-09-17). AA_GreenGoo's
waving little arms read as alive against our art — study how Alpha Animals
builds that wiggle (graphic comp, multi-frame, or shader) before assuming a
creature needs a full flip-book (below) just to look animate; a small Spastic
appendage may be the cheaper, correct answer (owner, first art walk,
2026-09-14). ⚠️ Note the reversed flight ruling below: Spastic is fine for a
small IDLE jiggle on one static texture, and was specifically wrong for
expressing a per-facing flying pose.

## 🔴 Flying creatures need a DIFFERENT asset shape — not a wing layer

**A flier's animation is a whole-body directional flip-book, never a separate
wing texture jiggled by a render-tree node.** Owner ruling 2026-09-19, filed
after `FIREHAWK_FLIGHT_BEHAVIOR_1` shipped a custom `BodyDef` wing part +
`PawnRenderNodeProperties_Spastic` node and it looked broken live: standing
still with no visible flap going sideways, and one wing missing (the other
misaligned) going north. That is not a tuning miss — a Spastic node idle-jiggles
ONE static texture; it was never built to express a per-facing "wings up" vs
"wings down" pose, and nothing keeps a single wing texture registered across
four facings. Full account and the CLAUDE.md correction: search this repo's
CLAUDE.md for "If it flies in the fiction".

**The real mechanism is `PawnKindDef.flyingAnimationFramePathPrefix`** — MEASURED
against the installed game by extracting `Chicken_Flying_*` from
`resources.assets` (UnityPy) and diffing frame 1 against frame 5:

```xml
<flyingAnimationFramePathPrefix>Things/Pawn/Animal/Chicken/Chicken_Flying_</flyingAnimationFramePathPrefix>
<flyingAnimationFrameCount>8</flyingAnimationFrameCount>
<flyingAnimationTicksPerFrame>2</flyingAnimationTicksPerFrame>
<flyingAnimationDrawSize>2.4</flyingAnimationDrawSize>
<flyingAnimationDrawSizeIsMultiplier>true</flyingAnimationDrawSizeIsMultiplier>
<flyingAnimationInheritColors>true</flyingAnimationInheritColors>
```

**What to generate, per commissioned flier:** `frameCount` full-body poses (8 is
vanilla's number for Chicken/Duck/Goose/Sparrow; Locust ships 5), each one
covering the WHOLE animal wings-and-all in a different point of the wingbeat
cycle — frame 1 tucked/streamlined, a mid-cycle frame fully spread, same idea
as a walk cycle but for flight — **times three directions**, named
`<prefix><N>_<direction>` for N = 1..frameCount and direction in
`north`/`east`/`south` (no separate west — mirrors east, same convention as
every other RimWorld facing set). That is `frameCount × 3` individual images,
not `frameCount` images reused across facings and not a 2×2-style sheet (the
per-facing generation guidance above applies here too, doubled by frame count).
Gendered species (vanilla Quail, Peafowl) add a second full set under
`flyingAnimationFramePathPrefixFemale`.

**Before generating anything**, read the reference doc a fresh implementation
pass should start from: `~/Desktop/RIMWORLD_1_6_NATIVE_ANIMAL_FLIGHT_IMPLEMENTATION.md`
(owner, 2026-09-19) if present, or re-derive the same facts from the installed
game the way this section did — Sparrow (Odyssey) is the cleanest from-scratch
template, Chicken/Duck/Goose (Core) are the retrofit references for turning an
existing grounded animal into a flier. `flyingAnimationDrawSizeIsMultiplier`
scales the flying sprite relative to the grounded one — most vanilla fliers
read bigger mid-flight, and that is timing/scale tuning, not art.

**Validation plan for a flier specifically** (on top of the standard one below):
verify the cycle actually alternates pose (not a static image, per the
worked-example lie above), verify all three facings resolve (a missing
`_north_3` silently drops to the bare-path fallback — see "How sprite checks
lie"), and verify the grounded graphic returns cleanly on landing. A screenshot
of the animal standing still proves nothing about whether it flies; step ticks
until it actually takes off and look then.
