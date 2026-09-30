# The Contagion's five grown limbs — owner review sheet (2026-09-30)

Item: `CONTAGION_GROWN_LIMBS_DESIGN_1`, which feeds `CONTAGION_MECHANICS_BUILD_1` §5.
The limb line was ruled at the bedazzle sitting (`the_contagion.md`, 2026-09-27 amendment,
point 5). This sheet is a draft. Nothing here is built.

## Recommendation

Keep all five limbs as a **lottery**. A new "Monstrous" grade goes on the genome samples the
Coalescence already drops when it dies. Injecting one grows a single random limb, and that
limb is unmatched to anyone. That reuses the loop as it is built today and needs one new
field, not a new system. Build **Pillar Arm and Lash first**, since both are plain melee tools
on the Anomaly flesh-whip shape. The other three each add one vanilla ability, so they come
second.

Every limb gives one real thing and costs one real thing that lasts. Ban 6 holds because you
choose each limb by surgery, and a pawn never mutates into one.

---

## What all five share (read once)

**What exists today, measured this pass:**
- **The genome loop.** A surgery draws `RM_GenomeSample` from a colonist
  (`Recipe_ExtractGenomeSample`, humans only). You inject it into an amoeba host (`AA_RedGoo`,
  `AmoebaHostUtility.HostDefName`). The host gestates it (`Hediff_AmoebaGestation`), dies, and
  drops 2–4 items. The pool is Kidney, Liver, Lung, Heart, `RM_GrownLeg` and `RM_GrownArm`.
  Every item is stamped with the donor through `CompGenomeMatched`. Samples have **no grade
  field**, and nothing in the code is called "Monstrous" except the Unfinished's
  `RM_UnfinishedMonstrous` hediff, labelled "runaway growth".
- **Sourceless samples already exist.** When the Coalescence dies in a Burn, it drops 2–14
  `RM_GenomeSample` with no donor (`Building_RM_Coalescence`, tranche-1 report). Nothing
  uses them yet except to grow unmatched organs.
- **The Anomaly mechanism, read from the installed defs and the decompiled source.**
  `Tentacle` and `FleshWhip` (`Data/Anomaly/Defs/HediffDefs/Hediffs_BodyParts_Prosthetic.xml`)
  are both `Hediff_AddedPart`. Each installs on the **Shoulder**, so it replaces the whole
  arm and hand. Each carries a `renderNodeProperties` entry of class
  `PawnRenderNodeProperties_Spastic`, with `texPaths` variants, `parentTagDef Body`,
  `drawSize` 1.3–1.4, and per-facing `drawData` covering rotation, flip, layer and
  `bodyTypeScales`. FleshWhip's weapon is `HediffCompProperties_VerbGiver` `<tools>`: Cut 20.5,
  armour penetration 0.6, cooldown 2.
- **Graphics are directional.** `PawnRenderNode.GraphicFor` loads `Graphic_Multi`, so each limb
  texture wants `_north`, `_east` and `_south` files, and west mirrors east.
- **Spastic can only twitch.** The node gives a random writhe (rotation, scale and offset
  ranges) to one still image. It **cannot** play a real swing, flap or jump. That is the
  flyer lesson, and no brief below asks it to animate.

**Engine limit that forces one small piece of C#: removal.**
`HediffComp_FleshbeastEmerge` is hard-coded. It always spawns a **Fingerspike** in the
Entities faction, and it only does so while Anomaly is active. It cannot spawn our Unfinished.
We therefore need one comp of our own, `HediffComp_UnfinishedEmerge`, about 30 lines copied
from that one. On `Notify_SurgicallyRemoved` or `Notify_SurgicallyReplaced` it spawns
`RM_TheUnfinished` as a manhunter beside the patient. The existing
`CompRandomizeUnfinished` then rolls that Unfinished's own limbs and lifespan. It sends a
ThreatBig letter.
- Rule: keep / change / cut

**How limbs are gained: proposed "Monstrous" grade.**
- Add `grade` (Normal / Monstrous) to `CompGenomeSample`, saved like its existing fields.
- **Where Monstrous samples come from.** Recommended: **A only**.
  - **A.** Every sample the Coalescence drops on death is Monstrous. This is the smallest
    change, and it makes killing the giant pay out in limbs.
  - **B.** Butchering an Unfinished that carries `RM_UnfinishedMonstrous` gives one Monstrous
    sample. This is rarer, and it spreads limbs across normal play.
  - **C.** The Helix sell them. That is BENCH's trade table and is not designed here.
- **What gestation does with one.** When `AmoebaHostUtility.CompleteGestation` gets a
  Monstrous sample, the batch becomes **one grown limb, rolled from the five**, and no organs.
  The limb carries no donor stamp, so the genome-match mood bonus never applies to it.
  - *Variant:* weight the roll toward the limb that "fits" the source. This only works with
    option B, where the Unfinished's own budded limbs can be read: a claw or spike makes Pillar
    Arm likelier, and a vestigial wing makes Bellows likelier. Recommended: plain random for
    v1.
- **How a limb is installed.** Each limb is an item (`ThingDef`, parent `BodyPartBase`) with
  a `RecipeDef` whose worker is vanilla `Recipe_InstallArtificialBodyPart`, plus `addsHediff`
  and `appliedOnFixedBodyParts`. This is the ordinary bionic-install shape, **not** our
  `Recipe_InstallGrownBodyPart`, which restores natural parts.
- Rule on grade source: A / B / C / A+B · Rule on roll: random / weighted

**Shared rider, an option.** All five hediffs could count as Contagion tissue under the
Burn. A pawn wearing one would gain `RM_BurnDose` at twice the rate in open sky. It would be a
two-line change in `RM_GameCondition_ContagionBurn` (a hediff-def check). It fits the lore,
since the limb is UV-shy flesh. It also stacks on each limb's own cost below.
- Rule: keep / cut

**Mod Settings (standing law):** grown limbs on/off, which also removes them from the gestation
roll, and a Monstrous-sample chance slider if option B is taken.

---

## Pillar Arm

**Looks like:** a slab of bone-cored meat as thick as a thigh, which hangs to the knee and
ends in a knuckled club, and has no fingers at all.

- **Attaches to:** Shoulder, the same as the flesh tentacle. That arm and its hand are
  replaced.
- **Does:** it is a heavy melee club, set by `HediffCompProperties_VerbGiver` `<tools>`:
  Blunt, power 24, armour penetration 0.35, cooldown 3.2. That is slow, but it is the
  hardest-hitting thing a pawn can grow. `extraMeleeDamages` adds Stun 8, so a hit staggers.
  `addedPartProps` `solid` true.
- **Cost rider:**
  - `partEfficiency` 0.3. With no fingers the pawn loses most of that side's Manipulation,
    so crafting, medicine and research slow down.
  - The stage gives `MoveSpeed` −0.4, from the weight.
  - `hungerRateFactorOffset` +0.25, because the arm has to be fed.
  - `PawnBeauty` −1.
  - The trade: a better brawler, and a worse worker, walker and eater, for good.
- **Gained:** the Monstrous roll (see the shared section).
- **Removal:** `HediffComp_UnfinishedEmerge`. Removing it spawns a manhunter Unfinished, and
  the patient is left with a missing arm.
- **Art brief:** one static node. Use `PawnRenderNodeProperties`, not Spastic, because a
  pillar should not wriggle.
  - Texture: `Things/Pawn/Humanlike/BodyAttachments/RM_PillarArm/RM_PillarArm` with
    `_north`, `_east` and `_south`, 2 variants.
  - Draw: `parentTagDef Body`, `drawSize` 1.6, per-facing `drawData` with anchors copied from
    Tentacle. North sits on layer 0, behind the body.
  - Colour: skin-coloured (`colorType Skin`, `useSkinShader`), with bone showing through at the
    knuckles.
- **Rule:** keep / change / cut

## Lash

**Looks like:** a pink rope of muscle, three times the length of an arm. It coils on the
ground behind the pawn and keeps twitching after the pawn has stopped.

- **Attaches to:** Shoulder. That arm and its hand are replaced.
- **Does:** it is a fast, weak striker that stuns. `<tools>`: Blunt, power 9, cooldown 1.4,
  with `extraMeleeDamages` Stun 12.
  - It is not a killer. It holds a target down so others can kill it.
  - This keeps it separate from vanilla FleshWhip, which is a Cut 20.5 blade.
- **Cost rider:**
  - `partEfficiency` 0.6, so it is clumsy for work.
  - The stage gives `socialFightChanceFactor` ×3, because the lash lashes out at people.
  - The stage gives `PawnBeauty` −1.
  - The trade: a crowd-control arm that picks fights in the dining room.
- **Gained:** the Monstrous roll.
- **Removal:** `HediffComp_UnfinishedEmerge`.
- **Art brief:** Spastic node. This is the one limb where the writhe *is* the look.
  - Texture: `RM_Lash` with `_north`, `_east` and `_south`, 3 variants A/B/C, the same way the
    tentacle picks one per pawn.
  - Draw: `drawSize` 1.8, `rotationRange` −40~40, `nextSpasmTicksRange` 10~50, which is the
    tentacle's twitch.
  - Pose: the rope trails behind and down, so it reads as lying on the ground.
- **Rule:** keep / change / cut

## Eyeburst

**Looks like:** where one eye was, a wet cluster of a dozen mismatched eyes has pushed out.
They are pink and blue, all sizes, and they blink out of step.

- **Attaches to:** Eye, one socket.
- **Does:** better sight and aim.
  - `partEfficiency` 1.5. Sight is the capacity, and a bionic eye is 1.25.
  - The stage gives `ShootingAccuracyPawn` +0.1.
  - ⚠️ **Ban 5 holds.** This is a pawn stat. The Bloom's ×0.4 weather accuracy still applies
    on top of it, so the eyes see further but not through the fog.
- **Cost rider:**
  - `painOffset` 0.1, because it never stops stinging.
  - `MentalBreakThreshold` +0.08, because it never closes and the pawn sees too much.
  - `restFallFactor` 1.2, because the pawn sleeps badly.
  - `PawnBeauty` −2, the worst of the five: it is on the face.
  - The trade: a better shooter who is closer to a mental break, forever.
- **Gained:** the Monstrous roll.
- **Removal:** `HediffComp_UnfinishedEmerge`, which leaves a missing eye.
- **Art brief:** one static node, with `parentTagDef Head`, so it draws on the head and not
  the body.
  - Texture: `RM_Eyeburst` with `_north`, `_east` and `_south`. North can be nearly empty,
    since the eyes face forward and you only see an edge from behind.
  - Draw: `drawSize` about 0.5, anchored to the head's eye side.
  - Optional: a Spastic twitch with a tiny `rotationRange`, −5~5, so it reads as blinking.
- **Rule:** keep / change / cut

## Caudal Spring

**Looks like:** a coiled, segmented tail of gristle that grows out of the base of the spine.
It is folded under itself like a compressed spring and ends in a flat pad.

- **Attaches to:** Spine. The human body has no tail part, so the spring *replaces* the spine,
  the same way the tentacle replaces a shoulder.
- **Does:** it gives a jump. `HediffCompProperties_GiveAbility` grants a new
  `RM_CaudalLeap` ability, built on vanilla Biotech `Longjump`: `Verb_CastAbilityJump`, job
  `CastJump`.
  - It has **no hemogen cost**, which is our change.
  - Range 12, against Longjump's 19.9. Cooldown 1 day (`cooldownTicksRange` 60000).
  - It crosses walls, water and red pools, and it is the way out of a Burn caught in open
    ground.
- **Cost rider:**
  - `partEfficiency` 0.75 on the spine, so Moving drops. Walking is slower between leaps.
  - The stage gives `painOffset` 0.05.
  - The stage gives `ComfyTemperatureMin` +5, because the gristle stiffens in the cold.
  - The trade: one daily escape leap, paid for by a permanently slower walk.
- **Gained:** the Monstrous roll.
- **Removal:** `HediffComp_UnfinishedEmerge`. The patient is left with a **missing spine**,
  which is likely crippling. How badly a missing spine cuts Moving is unmeasured, so read the
  capacity worker at the build. Saying so in the surgery description is owed, and it is
  the honest price of "undoing" it.
  - ⚠️ Alternative for the owner: attach it to **Torso** as a non-replacing addition instead.
    That needs a different hediff class, because `Hediff_AddedPart` on Torso would destroy
    every child part. So this alternative means a small custom hediff, which is not free.
- **Art brief:** Spastic node with a slow, small writhe: `rotationRange` −15~15 and a long
  `nextSpasmTicksRange`, so it looks like a spring settling, not a whip.
  - Texture: `RM_CaudalSpring` with `_north`, `_east` and `_south`. It is visible below and
    behind the body. North is on top, since the back faces the camera. South is mostly hidden
    on layer 0.
  - Draw: `drawSize` 1.2.
  - There is no leap frame. The jump uses the engine's own flight arc.
- **Rule:** keep / change / cut · attach: Spine / Torso-addition

## Bellows

**Looks like:** a translucent bladder bulging out of one side of the ribcage. It swells and
empties with every breath, and you can see red fog moving inside it.

- **Attaches to:** Lung, one of them.
- **Does:**
  - `partEfficiency` 1.4 for Breathing.
  - `ToxicEnvironmentResistance` +0.3. The Anomaly fleshmass lung uses this same field.
  - `HediffCompProperties_GiveAbility` grants `RM_BellowsExhale`: vanilla
    `CompProperties_AbilityReleaseGas`, with `gasType` BlindSmoke and `cellsToFill` 20.
    Cooldown 2 days.
    - It is a blind-smoke cloud on demand, bringing a little of the Bloom along.
    - It blocks ranged fire in **both** directions, so it is a retreat tool and not an
      advantage.
- **Cost rider:**
  - `hungerRateFactorOffset` +0.3, because it takes a lot of air and a lot of food.
  - `totalBleedFactor` 1.5, because the bladder is thin and every torso wound bleeds more.
  - `PawnBeauty` −1.
  - The trade: better lungs and a smoke escape, for a body that starves and bleeds faster.
- **Gained:** the Monstrous roll.
- **Removal:** `HediffComp_UnfinishedEmerge`, which leaves a missing lung.
- **Art brief:** Spastic node used as a breathing pulse. `scaleRange` 0.9~1.1 with zero
  rotation gives a swell and shrink, which is the one "animation" Spastic can honestly do.
  - Texture: `RM_Bellows` with `_north`, `_east` and `_south`. It sits on one flank. East and
    west show it best. On north and south it is a bulge at the side edge.
  - Draw: `drawSize` 0.9, `parentTagDef Body`.
  - Colour: translucent pink with red haze inside, not skin colour.
- **Rule:** keep / change / cut

---

## Ban-6 ledger (gain vs cost, at a glance)

| Limb | Gain | Lasting cost | Net |
|---|---|---|---|
| Pillar Arm | Blunt 24 + stun | work −, walk −0.4, hunger +25% | trade |
| Lash | stun striker | clumsy, social fights ×3 | trade |
| Eyeburst | Sight 1.5, aim +0.1 | pain, break threshold +0.08, sleeps badly, ugliest | trade |
| Caudal Spring | daily 12-cell leap | walks slower, cold-stiff, spine lost on removal | trade |
| Bellows | Breathing 1.4, tox +0.3, smoke cloud | hunger +30%, bleeds ×1.5 | trade |

The numbers are first-pass. They are meant to be tuned at the build, and each one maps to a
named vanilla field, so tuning is XML only. No limb is net-positive on paper. If the owner
judges one still reads as an upgrade, raise its cost; do not cut its gain.

## Owed once ruled (not filed by this sheet)
- Build: 5 hediffs, 5 items, 5 install recipes, 2 abilities, `HediffComp_UnfinishedEmerge`,
  the `grade` field and the Monstrous batch branch in `CompleteGestation`, and Mod Settings.
  This goes to `CONTAGION_MECHANICS_BUILD_1` §5.
- Art: 5 textures × 3 facings × 1–3 variants, plus 5 item icons. Check `_artsrc/` and
  artpipe `done/` first. None were found for these names when the tranche-1 report was
  written.

