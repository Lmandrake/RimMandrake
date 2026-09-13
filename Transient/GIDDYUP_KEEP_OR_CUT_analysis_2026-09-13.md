# GIDDYUP_KEEP_OR_CUT_1 — background analysis (Fable agent, 2026-09-13)

Owner's framing (2026-09-12): fun to ride Star Wars animals, but a known bug
confounder historically; keep only if the content is worth it AND the mod is
now better written. This report answers both halves. Every claim is tagged
DISK (this machine) or WEB (secondary).

## 1. What the stack actually carries (spec pt 1)

DISK — `ModsConfig.xml` (live list) has exactly two entries from this lineage:
- `memegoddess.giddyup` → **Giddy-Up 2 - Continued**, workshop id 3674332861,
  modVersion **2.2.5**, supports 1.4/1.5/**1.6**.
- `memegoddess.runandgun` → **RunAndGun - Continued**, workshop id 3562365100,
  supports 1.0–**1.6**.

No Roolo-era module (`roolo.giddyupcore` etc.) and no Owlchemist original is
installed or active. Yayo's Animation (`com.yayo.yayoAni.continued`) is on
disk (workshop 2877292196) but **not** in ModsConfig — its `loadBefore`
interaction is moot.

## 2. Lineage and code quality now (spec pt 2)

DISK — `.../294100/3674332861/About/About.xml`:
- `<author>Roolo, Owlchemist, dav9670, Meme Goddess</author>`, url
  `https://github.com/MemeGoddess/GiddyUp2`, description: "renovated,
  overhauled fork ... with permission from the original author Roolo ...
  all-in-one, internally modularized within the mod options."
- `incompatibleWith` lists ALL four Roolo-era modules AND `Owlchemist.GiddyUp`
  — i.e. this **is the Owlchemist rewrite line (GiddyUp2), continued by
  MemeGoddess**, not the old breaker. The old-era code cannot coexist with it.

DISK — full C# source ships in the mod folder (95 .cs files,
`Source/{Core,BattleMounts,Caravan,RideAndRoll,SaddleUp,Mechanoids,Compatibility}`).
Read directly, not decompiled:

**Harmony patch surface** (attribute census over `Source/`): ~35 patches.
Heaviest targets: `Pawn_JobTracker` (4), `Pawn` (3), `PawnRenderer` (2),
`IncidentWorker_Raid` (2), `Pawn_HealthTracker` (2); singles on `PathUtility`,
`CaravanEnterMapUtility`, `AnimalPenUtility`, `WorkGiver_Train`,
`TransferableUtility`, UI. So yes: **jobs, rendering, raids/visitors,
caravans, pathing** — exactly the four hot systems, but a *modest* count
(~35 patches is small; our stack's big frameworks carry hundreds).

**Rendering is done the modern way**: `Source/Core/Render/` implements the
1.5+ PawnRenderNode/RenderTree API (`DynamicPawnRenderNodeSetup_MountedRider`,
`MountedRiderRenderNodeWorker`, `PawnRenderer_ParallelGetPreRenderResults`)
rather than the old-era draw detours that made Roolo's version a breaker.

**Defensive where it bit us**: `Source/Core/MountUtility.cs:44-59` —
`BuildAnimalBiomeCache()` wraps each biome's `AllWildAnimals` walk in
try/catch, logs `[Giddy-Up] An error occured calling AllWildAnimals ...
Skipping...` and continues. A malformed def costs one biome's NPC-mount cache
entry, **not the game**.

**RunAndGun** is tiny: 8 patches (`Verb` ×3, `Pawn` ×2, `VerbProperties`,
`MentalStateHandler`, `JobDriver`), full source shipped.

WEB — `github.com/MemeGoddess/GiddyUp2`: **zero open issues**; commits
monthly through **Aug 29, 2026** ("Fixed an issue where pawns would be
invisible after mounts forgot they had a rider"; Jun 24, 2026 added a
**drawing-offset adjustment dialog**; Jun 11, 2026 "improved rendering
performance"). Actively maintained on current RimWorld, and the recent bug
class is cosmetic (invisible rider, silhouettes, dismount edge cases) — not
save corruption.

## 3. Our own defect record, weighed honestly (spec pt 3)

Both 2026-09-12 "Giddy-Up crashes" were **our cast-data defects that
Giddy-Up's eager startup cache surfaced first** — canary, not culprit:

- `CORRECT_GIDDYUP_NULLKEY_1` (closed): dead `GR_Mantistanis` PawnKindDef ref
  in OUR `BiomeCast_Ashkarr.xml` fed a null key to vanilla
  `BiomeDef.CommonalityOfAnimal`. Fixed with an existence guard; fix deployed.
- `GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1` (**still open**): OUR overlap between a
  donor `<wildBiomes>` block and an independent `BiomeCast_*.xml` entry on the
  same biome (`AA_Eyeling` latest) throws duplicate-key inside **vanilla's**
  lazy commonality cache. Any caller of `CommonalityOfAnimal` hits it;
  Giddy-Up merely calls it first, at startup, loudly.

Cutting Giddy-Up removes the canary, not the disease: the duplicate-key data
defect would still detonate later in whatever vanilla system touches that
biome's commonality table, only quieter and further from the cause. The
honest reading: Giddy-Up has been giving us free, early, attributable
detection of our own generator bugs, and its own code caught-and-skipped
rather than crashing.

## 4. Gameplay value in THIS campaign (spec pt 4)

DISK — `design/Jawa/fauna/cast_assignment.csv`: the rideable-scale Star Wars
cast is not hypothetical, it is the shipped desert roster:
- `RSW_Bantha` (bs 4.0) — Desert ICON, commonality raised 0.5→0.8 (row 196);
  also AridShrubland, DesertOasis pilgrim.
- `Ronto` (bs 6.0) — Desert/AridShrubland herd giant (rows 108, 206).
- `RSW_Eopie` (bs 1.4) — the pack/caravan icon across four biomes (rows 104,
  210, 342, 358).
- `RSW_Dewback` (bs 3.0) — weeping_stones, owner-ruled placement (row 353).
- `RSW_Dactillion` (bs 3.0) — kept explicitly as "the flier mount" (row 355).

A Jawa clan crossing a desert planet on banthas and dewbacks is about as
close to the campaign's core fantasy as a mechanic gets. Concretely:
- **Caravan speed** (`caravansEnabled`, `giveCaravanSpeed`): on a desert
  world built around roads, oasis strings and scavenger caravans, mounted
  caravans are the difference between the map being walkable and not.
- **Mounted NPC raids/visitors** (`enemyMountChance`, `visitorMountChance`):
  Tusken-style mounted raiders and mounted traders arriving is world flavor
  we get for free from the same cast.
- Without Giddy-Up, banthas/rontos/eopies are cargo stat-sticks; with it they
  are the campaign's vehicles. (We do also carry Vehicle Framework + VVE +
  a desert reskin, but powered vehicles are a different fantasy tier from a
  Jawa on a bantha.)

Cost side: our custom RSW_ animals have had **zero mount draw-offset tuning**
— riders may sit visibly wrong on a bantha until someone tunes offsets. The
mod's Jun 2026 offset dialog (WEB) makes that a settings-screen job, not C#.

## 5. Compat matrix against the heavy hitters (spec pt 5)

Active heavy hitters, DISK-confirmed in ModsConfig: `smashphil.vehicleframework`,
`oskarpotocki.vanillavehiclesexpanded`, `krkr.rule56` (CAI-5000),
`nals.facialanimation` (+experimentals), `neku.largepawns`,
`co.uk.epicguru.meleeanimation`, `mlie.yayoscombat3`.

| System | Overlap | Risk read |
|---|---|---|
| Vehicle Framework / VVE | No mention of VF anywhere in GiddyUp source (DISK). Both touch caravans, but VF drives its own VehiclePawn types; GiddyUp mounts plain animals. | Low. Orthogonal by design. |
| CAI-5000 | GiddyUp's 4 `Pawn_JobTracker` patches + BattleMounts raid patches meet CAI's AI job control on **mounted raiders**. | **The one real overlap.** Failure mode: raiders stuck mounted / not dismounting — exactly what upstream has been fixing (Jun–Aug 2026 dismount commits, WEB). Tunable to zero via `enemyMountChance`. |
| Facial animation, Large Pawns | Both render-node based; GiddyUp's rider node moves the pawn. | Moderate, cosmetic-only (misplaced face/oversize clipping). Nothing save-breaking. |
| Melee Animation | Draws pawns during animation; mounted melee could glitch visually. | Low-moderate, cosmetic. |
| Yayo's Combat 3 | Overlaps **RunAndGun**, not GiddyUp: both patch `Verb`/aim behavior. | RunAndGun is the friction point, and its gameplay value here (Jawas firing while sprinting) is peripheral to the scenario. |

Shipped compat shims (DISK, `Source/Compatibility/`): AnimalApparel,
WalkTheWorld (active in our list), WhatTheHack (not active).

## 6. Options (spec pt 6)

---
**CARD A — Keep both mods as they are**
Riding, mounted caravans, mounted raiders, and run-and-gun shooting all stay
on, at their default settings.
*Trade: most content for most moving parts. RunAndGun and mounted raiders are
the two most likely places for a future confusing bug, and we keep both.*

**CARD B — Keep Giddy-Up, trim it; cut RunAndGun** ← recommended
Keep riding, mounted caravans, and mounted raiders/visitors. In Giddy-Up's
mod settings: turn OFF **Mechanoid mounts** (`mechanoidsEnabled`) — nothing
in the campaign wants ridden mechs and it deletes the whole Mechanoids module
from play. Leave `enemyMountChance` at default for now; it is the one dial to
drop to 0 if mounted raiders ever misbehave with the combat AI. Cut RunAndGun:
delete `<li>memegoddess.runandgun</li>` from ModsConfig.xml.
*Trade: we give up shoot-while-moving (a small, off-theme feature that rubs
against Yayo's Combat) and in exchange the remaining risk is one dial we
control. We still owe a one-time pass in the mod's offset dialog so riders
sit right on banthas.*

**CARD C — Cut both**
Delete `<li>memegoddess.giddyup</li>` and `<li>memegoddess.runandgun</li>`
from ModsConfig.xml (whole-mod removal — no Cherry Picker entry needed; both
of our existing BiomeCast guards stay in place and stay harmless).
*Trade: simplest stack, but banthas, dewbacks, rontos and eopies become
walking cargo racks on a desert world built for riding them — and we lose the
early-warning the mod has been giving us on our own cast-data bugs. The open
duplicate-key defect is OURS and still needs fixing either way.*
---

## Recommendation: **B**, clearly argued

The owner's own test was two-part: *worth it?* and *better written now?* Both
answers are yes, DISK-verified. (1) Worth it: the rideable cast is the shipped
desert roster's spine — bantha as Desert icon at 0.8 commonality, a ruled-in
flier mount — and mounted caravans are load-bearing on a road-and-oasis desert
planet. (2) Better written: this is the Owlchemist rewrite continued, not the
Roolo-era breaker (the About.xml declares the old modules incompatible); ~35
Harmony patches, modern render-tree rendering, defensive try/catch exactly
where our data hit it, full source shipped, zero open issues and monthly
maintenance through Aug 2026. Our two "Giddy-Up crashes" were our own cast
defects it surfaced first. The cheap trim (mech mounts off, RunAndGun out)
removes the two lowest-value/highest-friction pieces while keeping everything
the scenario is actually about.

Follow-ups if B is ruled: close out `GIDDYUP_WILDBIOMES_DUPLICATE_KEY_1` (our
data, owed regardless), and file a small item for a rider draw-offset pass
over RSW_Bantha/RSW_Dewback/Ronto/RSW_Eopie/RSW_Dactillion using the mod's
built-in offset dialog.
