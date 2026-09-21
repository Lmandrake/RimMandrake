# DRUM_LURE_PREDATOR_BUILD_1 — the drum-lure subsurface predator + its egg-trap clutch

## what is wrong

`EXTREME_DESERT_SUBSURFACE_PREDATOR_1` ported `AA_SandLion` (`RSW_SandLion`,
"vekka") as the extreme desert's interim strike predator, but the roster's
actual named archetype — `deep_desert.md` §4's **drum-lure subsurface
predator** ("The ground lies to you": predators appraise by vibration and
some carry **lures that drum juicy**, an angler's decoy sounding like a fat
animal) and its **egg-trap clutch** ("some eggs are birth traps... the
newborn tries to drink the intruder... the clutch is bait") — has no def and
no mechanic anywhere. `AA_SandLion` is a straight ambush predator (claws/bite,
no lure, no clutch); it fills the icon role, not the mechanic.

## why it matters

Two of the deep desert's most distinctive, sheet-documented behaviors — a
predator that fakes being prey to bait a strike, and an egg that is a weapon
disguised as water — are pure prose right now. Nothing in the game does
either.

## checked: does SARLACC_HABITAT_BUILD_1 already own the egg-trap clutch?

**No — different mechanic, different creature, verified by reading both
sources directly (not inferred from the word "clutch" appearing in both).**

- `SARLACC_HABITAT_BUILD_1`'s "clutch = THE birth-traps" (its spec's fork 4)
  is a **life STAGE of the sarlacc itself** — `sarlacc_native_habitat_draft.md`
  §8's three-stage life cycle (swimmer → anchored → cistern/throat). The
  "anchored" stage (`RSW_SarlaccAnchored`, already built per that item's own
  build-status section) rarely strikes anything adjacent — it does not "hatch"
  from an egg object, is not laid by a mother, and is not approached by a
  player picking up water. It is the sarlacc's own body, mid-metamorphosis,
  not a clutch of eggs in the ground.
- `deep_desert.md` §4's egg-trap is a **distinct object**: a portable-water
  item (an egg, laid by an unspecified drum-lure-adjacent mother animal) that
  a Jawa picks up believing it is a canteen, and which hatches violently on
  approach/pickup, the newborn attacking with "sharp beaks and needle claws."
  It belongs to the drum-lure predator's own reproduction, not the sarlacc's.

No overlap. Filing this separately does not duplicate `SARLACC_HABITAT_BUILD_1`'s
owed work; that item's "clutch" is sarlacc-only vocabulary that happens to reuse
the same English word.

## the work

1. **The drum-lure subsurface predator.** A real creature (RSW-tier, new
   defName — not `AA_SandLion`/`RSW_SandLion`, which stays as the interim
   ambush predator and is not replaced by this item) whose signature mechanic
   is the vibration lure: a **C# job/comp** that makes it broadcast a false
   "juicy prey" vibration signal to draw a target close before striking from
   ambush — the roster's "mechanic_load" entry per `deep_desert.md` §4's own
   framing ("both sides evolved to falsify the signal... predators with lures
   that drum juicy"). This cannot be done in XML alone: RimWorld has no stock
   comp for "broadcast a decoy signal that alters another pawn's pathing/AI
   toward this tile," so tier c (C#/Harmony) is the right layer per
   `rimworld-modding` §3 — confirm no existing `CompProperties_*` covers this
   before writing new C#.
2. **The egg-trap clutch.** A placeable/spawnable Thing (the "egg") that
   reads as portable water (matches `deep_desert.md`'s "eggs are canteens"
   framing) until interacted with, at which point it hatches a hostile
   newborn pawn that attacks the interacting pawn — likely a
   `CompProperties_ExplosiveIncomplete`-style "trap on interact" pattern or a
   custom comp spawning a pawn on `CompInteractable`/hauling pickup. Needs its
   own newborn PawnKindDef (small, "sharp beaks and needle claws").
3. Wire both into `RUT_ExtremeDesert` at a commonality the design sheet's
   "predators appraise and usually decline" / "no large surface herds" bans
   support (low — this is a rare, dangerous encounter, not a common spawn).

## Watch out

- Do not touch `RSW_SandLion`/`AA_SandLion`'s wiring — it is
  `EXTREME_DESERT_SUBSURFACE_PREDATOR_1`'s own closed work, the interim
  archetype, not this item's target.
- Do not reuse or extend `CompSarlaccSwimmer`/`CompSarlaccAnchoredMouth`
  (`SARLACC_HABITAT_BUILD_1`) for either mechanic here — confirmed above they
  are unrelated creatures with unrelated life cycles.
- `deep_desert.md` is FROZEN (`BIOME_FREEZE_FABLE_REVIEW_1`) — this item adds
  a creature and mechanic, it does not reinterpret a ruling.

## verify

A real predator ThingDef/PawnKindDef with a working vibration-lure ambush
mechanic exists and is observed drawing a pawn closer before striking on a
quicktest map; an egg-trap Thing exists, reads as a water item until
interacted with, and spawns a hostile newborn on interaction, observed live.

## criteria

The deep desert's two signature "the ground lies to you" mechanics (the lure,
the trap-egg) are real, playable content, not prose.

---

## ✅ LIVE-VERIFIED 2026-09-20 (FOUNDRY) — BOTH MECHANICS CONFIRMED, CLOSING

Bridge taken, `beastmechanics` tier (extended this session with
`mandrake.rm.proximityhatch` — see `BRIDGE_PAWN_SPAWN_CRASHES_VEF_1.md`,
required for the egg's real trap comp rather than falling back to
`CompHatcher`'s vanilla timer) applied and cold-loaded via Steam, 15 mods.

### Mechanic 1 — the vibration lure ambush: CONFIRMED

Spawned `RSW_Drazzik` via `jawa/spawn_pawn` at (130,105), ~8-14 cells from
three player colonists (Clara, Marjot, Alaska). Stepped `rimworld/
step_game_ticks` in 90-tick increments (map left PAUSED throughout — ticks
still advance and resolve jobs per the rimbridge skill's own note that
stepping runs a pawn's normal tick logic regardless of UI pause state).

Independently observed, not just `success: true`:

1. **`RM_DrumLureLured` hediff appeared on Marjot** (`jawa/pawn_get` ->
   `hediffs`) at tick 270 — the lure fired.
2. **Position converged toward the drazzik, not randomly**: Marjot walked
   (138,113) -> (134,109) -> (134,107) -> (134,105) -> (133,105) over the
   following ticks, while the drazzik sat at (133-134,104-105) the whole
   time — this is the "drawing closer" observable the item's own `## verify`
   asks for.
3. **The strike happened**: Marjot's hediffs gained `Stab`, `Scratch` and
   `BloodLoss` (drazzik's claw/bite tools), and `rimworld/list_colonists`
   read her `downed: true` at (133,105), 1.4 cells from the drazzik — inside
   `ambushRangeCells` (1.9).

Screenshot (post-ambush, Marjot downed next to the drazzik, "Colonist needs
rescue" letter live):
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Screenshots\drumlure_ambush_evidence.png.png`

### Mechanic 2 — the egg-trap clutch: CONFIRMED

First attempt (101,100) landed inside solid unwalkable rock (a mountain
tile) — the egg silently failed to spawn there (a `rimworld/spawn_thing`
silent failure on an impassable cell, worth its own trap-file entry someday,
not filed here to keep this item scoped). Re-tested at a verified-walkable
Sand cell (115,110) after checking `walkable: true` first.

Spawned a `Chicken` at (115,110) and `RSW_DrazzikEggFertilized` at (116,110)
(1 cell away, inside the egg's `triggerRadius` of 1.5). One `scanIntervalTicks`
cycle later (60 ticks):

- The egg was gone from its cell (`rimworld/get_cell_info` — no longer in
  `things`).
- A **new** `RSW_Nizzek` pawn (id `RSW_Nizzek9014`, confirmed NOT the same as
  a pre-existing wildlife `RSW_Nizzek` elsewhere on the map — checked by id,
  not just kindDef, after a false-positive first pass matched the wrong one)
  appeared at exactly the egg's former cell, alongside `Filth_AmnioticFluid`
  (vanilla `CompHatcher.Hatch()`'s own birth filth — confirms the vanilla
  hatch path ran, not a custom spawn).
- **Combat occurred**: after 2 more minutes of ticks, both the hatchling and
  the chicken carried fresh `Bite` + `BloodLoss` hediffs — the newborn
  attacked the triggering pawn ("sharp beaks and needle claws" per
  `deep_desert.md` §4) and the chicken fought back. This is
  `CompProximityHatch.Aggro()`'s forced `AttackMelee` + `ManhunterPermanent`
  working exactly as built.

Both of this item's two named mechanics are real, playable, and observed live
— not prose. Closing.

**Note for whoever reads `## Watch out` above:** the placeholder art and the
drazzik name are both still exactly as drafted — this verification pass did
not touch either, only the mechanics.
