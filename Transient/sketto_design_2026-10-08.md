# Sketto design pass — 2026-10-08

Contact sheet: `D:\Luke\dev\RimMandrake\Transient\sketto_design_2026-10-08_contact.png`
(donor | canon | our renders | flyer exemplars. Lock maps: green = a pixel that is identical in every flight frame, red = a pixel that changes.)

Owner, 2026-10-08 ~10:45: *"Do a brief design pass to help out the sketto. Look at the donor art. Look at the canon art. You will see what we're up against. Help design an excellent prompt to get us where we need to be that also can be made into a flyer with a stable body. Look At the donor mod, for examples of flyers with rock-solid stable bodies to emulate."*
Owner, same day: *"The Star Wars donor mod did have some excellent stable flyers. They simply were extremely cartoonish, so we can't use them, but they are good to study."* So we take the donor's **construction** and none of its style.

Design and evidence only. Nothing was queued, withdrawn or edited, and no def was touched.

## 1. What we're up against

- **The donor is cartoon, but it is perfectly rigid.** Every donor flyer keeps its body pixel-locked and moves only its wings, which pivot at a fixed shoulder. The Sketto's own frames hold 0.48 (E), 0.41 (S) and 0.40 (N) of each frame's pixels identical across all four frames. The rest of each frame is wing. Frame 4 is byte-identical to frame 1 in every donor set I checked. The style is a thick black keyline with flat fill, which the art law has retired (`fill_queue.py` refuses "black outline").
- **Canon is a lean dragonfly-reptile.** It has a long straight whip tail ending in a fin-tuft, four narrow veined wings, two downward tusk-fangs, and spindly legs tucked in flight. The colour is unsettled: the prop is cream-pink with amber veined wings, while the Legends art is olive/blue. The owner has already picked a colour. He chose render **B** (`longshade_rsw_sketto_v1_east`, cream-amber, close to the prop) and noted *"Yes, now do North and South"*. Colour is not an open question.
- **Our flight frames are redrawn from scratch every frame, so the body boils.** The 2026-10-08 frames `regen_ls_canon_sketto_flying_*` hold only **0.010 (E), 0.006 (N) and 0.036 (S)** of their pixels steady across frames. The donor holds about 0.4–0.5 and Core's Chicken 0.35–0.44. Even `flying_1_east` and `flying_2_east`, which re-draw nearly the *same pose* as the accepted standing render, change nearly every pixel. Painterly regeneration noise alone fails the test, so **no prompt can deliver a stable body by itself**. A deterministic lock step is required.
- **The poses ignored the prompt.** `flying_1` and `flying_2` east are the standing pose: legs dangling, tail coiled in a C, wings in the same place. The prompt asked for "legs tucked, wings level mid-downstroke". Only `flying_3` east moves the wings, and it re-poses the whole body to do it.
- **Viewpoints are mixed within one facing.** South `flying_2` is a front-on face view, while south `flying_3` is front-on with the body hanging vertically. North frames are dorsal, but the wing count and shape differ from frame to frame.
- **The root cause is in the job wiring, not the model.** The flight jobs carried the accepted east only as `canon_reference[0]`. That attaches it under `CANON_PROMPT_PREFIX`, which reads: *"The attached image is a CANON REFERENCE … not a sprite to edit … draw a NEW game sprite"*. The prompt literally asks for a redraw.
- **The flight draw size is a separate defect, in the def.** `RSW_Sketto`'s adult `bodyGraphicData.drawSize` is 1.25, but the PawnKindDef sets `flyingAnimationDrawSize 1.0` with `flyingAnimationDrawSizeIsMultiplier false`. The sprite therefore shrinks 20% at take-off. FOUNDRY should file this. The fix is `IsMultiplier true` with `1.0`, so flight matches the grounded scale.
- **4 of the 14 jobs produced nothing.** `flying_1_v1_south` and `flying_4_v1_{east,north,south}` are in `failed/` with "worker exited 1, image_present=False" after 2 attempts.

## 2. Evidence: defs and art found

| what | where |
|---|---|
| our def | `D:\Luke\dev\RimMandrake\src\RimStarWars\SWBestiary\Defs\ThingDefs_Races\RSW_Sketto.xml`. Body `RSW_Bogwing`, 4 frames × 4 ticks, prefix `swanimals/Sketto/Sketto_Flying_`, no colour mask (`flyingAnimationInheritColors false`) |
| donor | `Mlie.StarWarsAnimalCollection` ("Star Wars Animal Collection (Continued)"), workshop `3497316713`, defs in `1.6\Defs\ThingDefs_Races\Races_Animal_SW.xml`, textures in AssetBundle `AssetBundles\Mlie_StarWarsAnimalCollection` (387 flyer textures extracted with UnityPy, `~/.venvs/rimworld`) |
| live textures | `D:\Luke\dev\RimMandrake\src\RimStarWars\SWBestiary\Textures\swanimals\Sketto\` (16 PNGs, 256², RGBA). Only `Sketto_east.png` is ours (accepted B, installed `e49edf505`). N/S and all 12 flight frames are still **donor cartoon**, so the game currently mixes painterly east with cartoon everything-else |
| canon | `D:\Luke\dev\RimMandrake\design\RimStarWars\canon_references\sketto\` (description.md and 3 Wookieepedia images pulled 2026-10-04: prop `canon_1`, watercolours `legends_1`/`legends_2`). `## Engine limits`: not yet assessed. `## ruling`: empty |
| owner ruling | `D:\Luke\dev\RimMandrake\infrastructure\state\art_rulings\2026-10-08_leaningscrub_sheet_2026-10-05.decisions.json` → `RSW_Sketto` decision B, note *"Yes, now do North and South"* |
| our renders | `D:\Luke\dev\_artpipe\_artsrc\longshade_rsw_sketto_v1_east\` (accepted) and `…\_artsrc\regen_ls_canon_sketto_*` (10 done) |
| Core reference | Chicken and Goose flight frames (8 × E/N/S) extracted from `RimWorldWin64_Data\resources.assets`. Duck and Sparrow are not in that file |

## 3. Flyer exemplars — measured body stability

**Metric (locked share)** is the number of pixels that are opaque in every frame and within RGB L1 ≤ 40 of frame 1 in every frame, divided by the mean opaque area of one frame. It is a lower bound on the rigid-body share. Wings that sweep across the body lower it, so a big-winged animal scores lower while still being perfectly rigid. Script: `/home/mandrake/rm/scratch/BENCH/sketto/stab.py`. All 96 facing sets are in `stab_all.json` beside it.

| set | E | S | N | read |
|---|---|---|---|---|
| **donor Brezak** | 0.61 | 0.19 | **0.64** | best top-down: the body is a solid green column on the lock map and only the two wings are red |
| **donor Drexl** (winged reptile, closest analogue to Sketto) | **0.59** | 0.53 | 0.46 | best side view: rigid body and head, near wing in front of the body, far wing behind |
| donor Whisperbird | 0.50 | 0.36 | 0.58 | long-bodied flyer, same construction |
| donor Sketto | 0.48 | 0.41 | 0.40 | same anatomy as ours, so the right floor for our acceptance |
| donor median, 23 sets per facing | 0.48 | 0.41 | 0.46 | |
| Core Chicken (8 frames) | 0.35 | 0.41 | 0.44 | vanilla: the body bobs and tilts a little, so it is less rigid than the donor |
| Core Goose (8 frames) | 0.23 | 0.35 | 0.35 | |
| **ours, regen_ls_canon_sketto_flying_*** | **0.010** | **0.036** | **0.006** | body redrawn each frame |

**Donor construction to copy (construction only, never style):**
1. One body per facing, and that same body in every frame. Only the wings change, rotating about a fixed shoulder pivot.
2. Legs tucked and tail trailing straight behind, so the silhouette is a stable spine.
3. Three wing poses: up, level and down. The donor loops 1-2-3-1, since frame 4 equals frame 1.
4. In the east view, the near-side wings are drawn over the body and the far-side wings behind it.
5. North and south are top-down views with the wings spread laterally and symmetric, and the tail visible.

## 4. Generation strategy (stable body)

**Core idea: generate the body once per facing, then generate wing poses, then LOCK the body by compositing it deterministically onto every frame.** The generator is never trusted to hold a body still; it cannot (§1). The output stays a whole-body directional flip-book (`Sketto_Flying_<N>_<facing>.png`), which is the 1.6 mechanism. This is not a Spastic wing render-tree.

**Frames:** 4 frames × east/south/north (west mirrors east) = 12 PNGs. Ping-pong: **1 = wings up, 2 = wings level, 3 = wings down, 4 = copy of 2**. That is three unique wing poses per facing, matching the donor, with a smoother loop than the donor's 1-2-3-1. Keep `flyingAnimationTicksPerFrame 4`.

**Canvas and size:** 256×256 RGBA, the same as every Sketto texture. Subject bbox ≤ 244 px with ≥ 6 px margin in the widest pose (wings up in the east view, wings level in N/S). Draw size: grounded adult stays 1.25. Flight should be `flyingAnimationDrawSizeIsMultiplier true` with `flyingAnimationDrawSize 1.0`, which is a def change owed by FOUNDRY (§1). **No colour mask**: `InheritColors` is false and no `_m` files are needed.

**Wings vs alpha:** canon wants translucent wings. Paint the translucency (pale membrane, darker veins and amber blotches) with fully opaque or fully clear alpha. Do not use semi-alpha haze. The engine's default animal shader is Cutout, an alpha-test: that is a known default, but I did not measure its threshold this pass. Our renders already carry 16% soft-edge alpha, which is acceptable at the edges.

**N/S view convention for flight:** use a high top-down view from above, as the donor and Brezak do. North: back view, head at the top of the canvas. South: head toward the bottom, with the face and the two tusks readable, wings spread laterally, and the tail trailing up the canvas. A front-on south (what we got) hides the long tail, which is a must-show.

**Pipeline (per facing f ∈ E, S, N):**

| stage | job | how it's wired | gate |
|---|---|---|---|
| A | **flight master** = frame 1 (wings up) | E: `derive_from: longshade_rsw_sketto_v1_east` (the accepted B), edited into the flight pose. S/N: `derive_from` the finished E master (the fill_queue facing-coherence default) | owner looks at the 3 masters before stage B. They are the identity of every frame |
| B | **body plate** = the master with all four wings removed | `derive_from` the master. Edit: wings out, nothing else changed | plate silhouette ⊂ master silhouette. After alignment, ≥ 97% of plate pixels are within L1 40 of the master |
| C | **wing pose 2 (level) and 3 (down)** | `derive_from` the master. Edit: move only the wings | pre-lock: align the frame to the plate (translation search ±8 px). The plate silhouette must stay ≥ 92% covered by non-wing pixels in the frame, or the body was re-posed: reject |
| D | **lock** (offline script, new, small) | for frames 1–3: within the plate mask, every pixel the generated frame did not paint as wing becomes the plate pixel exactly. A wing pixel is one that differs from the plate by L1 > 60, or lies outside the plate. Frame 4 is a byte copy of frame 2 | post-lock acceptance, §6 |

Job count is 3 masters + 3 plates + 6 wing poses = **12 jobs**. 3 of them (the E-derived S/N masters) depend on the E master's acceptance. The lock step (D) is about 60 lines of PIL plus numpy in `D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\art\`. It is the piece that turns "approximately the same animal" into rigid, and it is the only way the painterly pipeline gets the donor's rigidity.

## 5. Prompts

These rows are in `fill_queue.py` row format, with the field names the existing Sketto jobs use. `fill_queue` appends the house register and the `canon: sketto` brief and Must-show to `style_notes`. **Not queued. They are a design, ready to paste once BENCH or the owner says go.** `priority 0` is valid because these are redraws the owner ruled on.

**Shared owner note (verbatim, carried on every row):** `"Please follow canon closely and regenerate N and S" / "Yes, now do North and South" / (2026-10-08) "help out the sketto … can be made into a flyer with a stable body"`.

### A — flight master, east (frame 1, wings up)
```json
{"id": "sketto_fly_master_v1", "rimflow_item_id": "BIOME_FLORAFAUNA_ART_REVIEW_1",
 "target_def": "RSW_Sketto", "target_texpath": "swanimals/Sketto/Sketto_Flying_1",
 "canon": "sketto", "facings": ["east", "south", "north"], "canvas_w": 256, "canvas_h": 256,
 "drawsize": 1.25, "background": "transparent", "priority": 0,
 "derive_from": "longshade_rsw_sketto_v1_east",
 "owner_note": "Please follow canon closely and regenerate N and S. Yes, now do North and South. (2026-10-08) help out the sketto ... can be made into a flyer with a stable body.",
 "prompt": "Edit the attached accepted render of this exact sketto into its IN-FLIGHT pose. Keep the same individual: same head, same open fanged mouth with the two long curved tusk-fangs hanging from the upper jaw, same cream-pink skin, same tan banding, same amber veined wings, same painted matte style, same scale. Change only the pose: body held level and straight along a horizontal line as if gliding; neck extended forward in line with the body, head pointing right; all four thin spindly clawed legs folded tight up under the belly so they barely break the belly line; the very long whip-like tail held STRAIGHT and trailing directly behind, level with the body, as long as the body or longer, ending in its small fin-tuft (not coiled, not curled). Wings: all four narrow veined wings raised high at the top of the upstroke, two forewings and two hindwings, rooted at one fixed shoulder point; the near-side pair drawn in front of the body, the far-side pair behind it. Wing membranes pale and translucent-looking by paint alone: light amber membrane, darker veins, no glow, no blur, no motion streaks. Whole animal inside the canvas with margin. No ground, no shadow, no outline."}
```
fill_queue then files S/N as derivations of this E. Their per-facing view lines are as follows.
- **south:** `"High top-down view from above and in front: head toward the BOTTOM of the canvas with face and both tusk-fangs readable, body a straight vertical spine, tail trailing straight UP the canvas to its fin-tuft, all four wings spread out to both sides symmetrically and raised (upstroke), legs tucked out of sight under the body."`
- **north:** `"Top-down view from directly above and behind: head toward the TOP of the canvas, back and spine visible, tail trailing straight DOWN the canvas to its fin-tuft, all four wings spread out to both sides symmetrically and raised (upstroke), legs tucked out of sight."`

### B — body plate (per facing; derive_from that facing's master)
```json
{"id": "sketto_fly_plate_v1_<facing>", "derive_from": "sketto_fly_master_v1_<facing>", "...": "same subject/canvas/owner_note fields as A",
 "canon_na": [2], "canon_na_reason": "wings removed on purpose: this is the wingless body plate composited under every flight frame",
 "prompt": "Remove all four wings completely from the attached sketto, including their roots, and leave EVERYTHING ELSE pixel-for-pixel unchanged: same position on the canvas, same pose, same head, fangs, tucked legs, straight tail and fin-tuft, same colours and painted texture, same scale. Where a wing covered the body, paint in the body that would be underneath, matching the surrounding skin. Do not move, re-pose, re-light or restyle anything. Transparent background."}
```

### C — wing poses (per facing × frames 2 and 3; derive_from that facing's master)
```json
{"id": "sketto_fly_wing2_v1_<facing>", "derive_from": "sketto_fly_master_v1_<facing>", "target_texpath": "swanimals/Sketto/Sketto_Flying_2", "...": "as A",
 "prompt": "Move ONLY the four wings of the attached sketto; the body, head, fangs, tucked legs, straight tail and fin-tuft must stay exactly where they are, pixel-for-pixel, same colours, same painted texture. Wings pivot at the same shoulder roots as in the attached image. New wing position: all four wings held out LEVEL, spread flat and wide at the middle of the downstroke (east view: wings foreshortened to narrow shapes along the body line, near pair in front of the body, far pair behind; top-down views: wings straight out to both sides, symmetric). Same wing shape, veins and membrane colour as the attached image. No blur, no motion streaks."}
{"id": "sketto_fly_wing3_v1_<facing>", "target_texpath": "swanimals/Sketto/Sketto_Flying_3", "...": "as wing2, with the wing position replaced by:",
 "prompt_wing_position": "all four wings swept fully DOWN at the bottom of the downstroke (east view: near pair hanging below the belly in front of the body, far pair just visible behind it; top-down views: wings angled down and slightly back on both sides, symmetric, tips lower on the canvas than the shoulders)."}
```
Frame 4 is not generated: `Sketto_Flying_4_<f>.png` is a byte copy of locked frame 2.

## 6. Acceptance checklist

Floors are measured from the donor's own Sketto, which has the same anatomy and wing area (§3).

1. **Canon Must show** (from the canon entry, graded by `canon_check.py` on every frame): slim body, long thin neck, small wedge head · four narrow veined translucent-looking wings in two pairs (n/a on plates only) · very long thin whip tail ≥ body length, ending in a tuft or fan · mouth of fangs with two long curved tusk-fangs from the upper jaw · four thin spindly clawed legs **tucked in flight**.
2. **Owner pick holds:** same individual and palette as accepted render B. Never Legends olive/blue.
3. **Body stability:** after the lock step, the plate pixels not under a wing are **100% identical** across frames 1–4 (by construction; the test proves the lock ran). Locked share per facing must be **≥ 0.45 E, ≥ 0.38 S, ≥ 0.38 N** (donor Sketto: 0.48, 0.41, 0.40). Before the lock, a frame whose non-wing silhouette covers < 92% of the plate after alignment is **rejected**, because the body was re-posed and must not be painted over.
4. **Registration:** plate centroid shift between frames = 0 px after the lock. Frame-to-frame bbox height change ≤ wing travel only.
5. **Loop:** 1 up → 2 level → 3 down → 4 (= 2) → 1, with no frame identical to its neighbour except by design.
6. **Facing correctness:** E head points right, with the near wings over the body and the far wings behind. S is top-down with the head down and the face and tusks readable. N is top-down with the head up. West is not drawn (mirrors E). No mixed viewpoint inside one facing.
7. **Canvas and alpha:** 256×256 RGBA, transparent background, ≥ 6 px margin in every frame, no semi-alpha haze in the wing membranes, no outline or keyline, no shadow, no blur or motion streaks.
8. **Scale continuity:** grounded and flight scale match once the def uses `flyingAnimationDrawSizeIsMultiplier true` with `1.0`. Until then, frames drawn at 256 px show at 1.0 against 1.25 grounded.
9. **Legibility** at game zoom (`art_legibility.py`): the wings and tail still read at 32 px.

## 7. The 14 `regen_ls_canon_sketto_*` jobs — recommendation (recommendation only; nothing was changed)

**None of the 14 is still pending:** 10 are done and 4 failed. Registry `queued` events were followed by `generated`/`validated` for 10 jobs; the other 4 are in `failed/`. They were filed on 2026-10-08 at 05:39Z and ran around 11:00 local.

| jobs | state | recommendation |
|---|---|---|
| `regen_ls_canon_sketto_v1_south`, `…_v1_north` (grounded N/S) | done | **Keep and show the owner** as the grounded N/S he asked for. They match B's identity well. Note that south is a front-on view with a coiled tail, which is fine on the ground but is not the flight convention |
| `regen_ls_canon_sketto_flying_{1,2,3}_v1_{east,north}` and `flying_{2,3}_v1_south` (8 frames) | done | **Do not install; replace.** Locked share 0.006–0.036 against the floor of 0.38–0.45, legs not tucked, mixed viewpoints. They cannot be rescued by the lock step because the body is re-posed between frames (gate 3 fails) |
| `regen_ls_canon_sketto_flying_1_v1_south`, `flying_4_v1_{east,north,south}` | failed (worker exit 1, no image) | **Do not requeue.** Frame 4 is a copy of frame 2 in the new design, and frame 1 S comes from the new master |

Replace them with the 12 jobs in §4/§5 plus the lock script. The accepted east (B, live since `e49edf505`) remains the identity source for all of it.

## 8. Pilot built — 2026-10-08

**Lock script:** `D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\art\flyer_lock.py`, with its selftest `selftest_flyer_lock.py` beside it (22/22 PASS; fixtures under `/home/mandrake/rm/scratch/BENCH/flyer_lock/selftest`). The script has three verbs:
- `lock` is stage D. It aligns each frame to the plate (±8 px), rejects a re-posed body, keeps the wing pixels and writes the plate's exact RGBA everywhere else. It ping-pongs the frames, so frame 4 is a byte copy of frame 2.
- `compose` is the layer recipe from the flyer study §3.1: wing-only layers over or under a wingless body.
- `check` applies the §6 acceptance: the locked share against the floors E 0.45 / S 0.38 / N 0.38, plate pixels outside the wings 100% byte-identical, the 256² canvas, a margin of at least 6 px and the ping-pong rule.

The selftest has a sanity probe: the same frames left unlocked score 0.0 plate identity, and redrawn bodies score a share of 0.002. Both fail, so the checker can fail.

**Changes from §4–§5 needed to file the jobs:**
1. **Row A is split into three rows.** If the row carries an explicit `derive_from`, `fill_queue` derives EVERY facing from that job. That would have made S and N edits of B, not of the E master. So E derives from `longshade_rsw_sketto_v1_east`, and S and N each derive from `sketto_fly_master_v1_east`.
2. **The camera phrase "top-down" is removed from the S/N view lines and the wing prompts.** `common._FACING_CONTRADICTIONS` refuses any facing job that says "top-down", because the owner ruled that an overhead camera is never a facing. S now opens *"Front view, face toward the viewer:"* and N opens *"Rear view, seen from behind, no face or eyes visible:"*. The wing prompts say "north/south views". The rest of every line is verbatim. ⚠️ So the S/N masters are front and back views at vanilla elevation, not the donor's top-down views. If they lose the tail, that is the place to look.
3. **The re-pose gate uses opaque coverage of the plate (≥ 0.92), not §4 C's "covered by non-wing pixels".** In the E level pose the wings lie along the body line and legitimately cover it, so the literal metric would reject the right answer. That literal metric is still reported as `body_cover`, for information only.
4. `fill_queue` prepends its derive prefix (*"Derive this facing from the attached accepted master … Do not restyle."*) to every derived job. No canon image is attached to any of them, so the old CANON-REFERENCE redraw wiring (§1) is gone.

**Filed (stage 1, priority 0):** `sketto_fly_master_v1_east`, `sketto_fly_master_v1_south` and `sketto_fly_master_v1_north`. The daemon holds S and N in `pending/` until the E master has a done manifest and PNG. Rows: `D:\Luke\dev\RimMandrake\Transient\sketto_pilot_2026-10-08\stage1_masters.json`.

**Stage 2 is NOT filed, deliberately.** The queue can wait for a master to *finish*, but it cannot wait for the owner to *accept* it, and §4 makes his look at the three masters the gate before stage B. The nine rows (3 plates plus 6 wing poses, each `derive_from` its facing's master) are dry-run clean in `D:\Luke\dev\RimMandrake\Transient\sketto_pilot_2026-10-08\stage2_plates_wings.json`. Once he OKs the masters:

    python3 src/RimMandrake/Utils/artpipe/fill_queue.py --input Transient/sketto_pilot_2026-10-08/stage2_plates_wings.json

If a master is redone as v2, bump the `derive_from` values in that file first.

**Then lock, per facing f ∈ east, south, north** (frame 1 is the master itself; `A=/mnt/d/Luke/dev/_artpipe/_artsrc`):

    python3 src/RimMandrake/Utils/art/flyer_lock.py lock --facing f --prefix Sketto_Flying_ \
      --plate $A/sketto_fly_plate_v1_f/sketto_fly_plate_v1_f.png \
      --frame $A/sketto_fly_master_v1_f/sketto_fly_master_v1_f.png \
      --frame $A/sketto_fly_wing2_v1_f/sketto_fly_wing2_v1_f.png \
      --frame $A/sketto_fly_wing3_v1_f/sketto_fly_wing3_v1_f.png \
      --out Transient/sketto_pilot_2026-10-08/locked --report Transient/sketto_pilot_2026-10-08/lock_f.json

Exit 1 means a frame was re-posed or a floor was missed. The report says which. Nothing is installed into `src/` Textures. Install is a separate step, after the owner rules.

**What the owner looks at, and where:**
1. **Now (once rendered):** the three masters, at `D:\Luke\dev\_artpipe\_artsrc\sketto_fly_master_v1_east\sketto_fly_master_v1_east.png`, plus the `_south` and `_north` equivalents beside it. Check that each is the same cream-amber individual as B, with legs tucked, the tail straight and the wings up.
2. **After stage 2 and the lock:** the 12 locked frames, in `D:\Luke\dev\RimMandrake\Transient\sketto_pilot_2026-10-08\locked\`, with the `lock_<f>.json` reports beside them.
