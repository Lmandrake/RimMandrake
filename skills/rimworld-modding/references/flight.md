# Creature flight in RimWorld 1.6 — stat, race flags and the flip-book animation

Moved from the project `CLAUDE.md` on 2026-10-11 (weekly cleaning), text unchanged except heading levels. CLAUDE.md keeps a one-line rule and points here. Entries state what IS: delete a line the moment it turns false, never annotate it.

## If it flies in the fiction, it flies in the game — owner, 2026-09-19

*"if we're going to wait for it as though it's not available, we might as well make
it a Flyer while we're here. Standing rule: we make flyers flyers when we can, ok?"*

Any creature whose description, canon entry or art shows it airborne gets real
flight, not a walking animal with wings drawn on. Applies to new defs and to any
def already open for another reason — the rule is "when we can", so the trigger is
touching it, not a sweep.

## 🔴🔴 NEVER live-test a flyer's flight without the owner present — said THREE times, 2026-09-25

Verbatim, third repetition, same day: *"For the third time, do not do live testing
of flyers without a human present. It doesn't work."* Also said the same day: *"Don't
try to capture images of flight. It doesn't work."* **You don't need to keep
rediscovering this — stop reaching for a live-bridge flight test at all.**

- ⛔ **No unattended bridge session — of any length, any sampling strategy — spent
  hunting a live mid-air frame or takeoff.** This includes screenshot hunts
  (`take_screenshot`/`screenshot_cell_rect` timed against `step_game_ticks`) AND any
  other unattended live-drive attempt at proving flight in the moment. One such pass
  ran ~35 minutes, ~25 screenshots, dozens of movement-segment checks, and caught
  nothing — inconclusive, not proof either way, and not a productive use of bridge
  time regardless of sampling density (worked example, now superseded:
  `FIREHAWK_FLIGHT_BEHAVIOR_1`).
- ✅ **Verify flight via a deterministic STATE read instead**, never a screenshot/visual
  hunt: a debug `[Tool]` (see `rimbridge-companion` skill) that reads
  `Pawn_FlightTracker`'s current state on a pawn directly. That is buildable and
  provable offline/asynchronously; a live *visual* sighting of the animation is the
  one thing that needs the owner actually watching.
- **How to apply:** if a flyer's live behavior needs eyes on it, that is a
  `rimworld-live-review`-style session done WITH the owner present, or it waits —
  it is never a FOUNDRY solo bridge pass. Don't file a "live verify" bar on a flyer
  item that can only be closed by an unattended screenshot/observation hunt; close it
  via the state-read instead, or leave the visual bar for a joint session.

🔑 **1.6 flight is CORE, not a donor framework and not Odyssey.** The stat
`MaxFlightTime` is declared in `Defs/Core/Stats/Stats_Pawns_General.xml` and Core's
own chicken uses it. MEASURED from the decompiled engine 2026-09-19.

⛔ **The switch is a STAT, not a bool.** `Pawn_FlightTracker.CanEverFly` returns
`GetStatValue(StatDefOf.MaxFlightTime) > 0f` — there is no `canFly` field, and
setting `race` flags alone gives you a grounded animal that reads as configured.

The vanilla shape, copied from `Locust` (`Races_Animal_Insect.xml`):

```xml
<statBases>  <MaxFlightTime>10</MaxFlightTime>  <FlightCooldown>5</FlightCooldown>  </statBases>
<race>
  <flightStartChanceOnJobStart>0.1</flightStartChanceOnJobStart>
  <flightSpeedFactor>2.5</flightSpeedFactor>
  <canFlyIntoMap>true</canFlyIntoMap>
  <canLeaveMapFlying>true</canLeaveMapFlying>   <!-- birds; omit for something that lairs -->
</race>
```

⚠️ **The flight ANIMATION is separate from the flight STAT, and it is its OWN
whole-body multi-frame system — not a wing render-tree.** `PawnKindDef`'s
`flyingAnimationFramePathPrefix` + `flyingAnimationFrameCount` need a real frame
sequence (Locust ships 5, Chicken/Duck/Goose/Sparrow ship 8). With none,
`GetBestFlyAnimation` returns null and the creature flies with no wing-beat —
correct behaviour, plainer look. Never block flight waiting on frames.

🔴 **REVERSED 2026-09-19 — do not build a `PawnRenderNodeProperties_Spastic`
wing-layer render tree for this.** `FIREHAWK_FLIGHT_BEHAVIOR_1` did exactly
that (a custom `BodyDef` wing part + a Spastic node jiggling one wing texture)
and the owner's own live test found it broken: standing still sideways with no
visible flap, and north missing one wing entirely with the other misaligned.
Root cause is architectural, not a bug to patch — Spastic drives a small idle
wiggle on ONE static texture per node; it was never a per-facing, per-frame
flying animation, so it cannot express "wings up" vs "wings down" the way the
directional flip-book below does, and nothing keeps a single wing texture
aligned across four facings.

**The correct mechanism, MEASURED against the installed game** (Core's own
Chicken/Duck/Goose retrofits, `Data/Core/Defs/ThingDefs_Races/
Races_Animal_ChickenGroup.xml`, and their textures pulled live from
`resources.assets` via UnityPy):

```xml
<PawnKindDef>
  <flyingAnimationFramePathPrefix>Things/Pawn/Animal/Chicken/Chicken_Flying_</flyingAnimationFramePathPrefix>
  <flyingAnimationFrameCount>8</flyingAnimationFrameCount>
  <flyingAnimationTicksPerFrame>2</flyingAnimationTicksPerFrame>
  <flyingAnimationDrawSize>2.4</flyingAnimationDrawSize>
  <flyingAnimationDrawSizeIsMultiplier>true</flyingAnimationDrawSizeIsMultiplier>
  <flyingAnimationInheritColors>true</flyingAnimationInheritColors>
</PawnKindDef>
```

The texture set is a **whole-animal directional flip-book**, one full-body pose
per frame, NOT a separate wing layer: `<prefix><N>_<direction>` for N = 1..
frameCount, directions `north`/`east`/`south` only (west mirrors east, same as
every other RimWorld facing set) — confirmed by extracting all 24
`Chicken_Flying_*` textures and diffing frame 1 (wings tucked) against frame 5
(wings spread) at `_east`: genuinely different poses, not a static image
jiggled. `flyingAnimationDrawSizeIsMultiplier` scales the whole flying sprite
relative to the grounded one (birds read bigger mid-flight); gendered species
(Quail, Peafowl) add `flyingAnimationFramePathPrefixFemale` alongside the
default (male) prefix. Sparrow is the cleanest from-scratch template and
Chicken/Duck/Goose the retrofit references. Verify: loop correctness,
all-facing correctness, landing restores the grounded graphic, save/load
safety.
