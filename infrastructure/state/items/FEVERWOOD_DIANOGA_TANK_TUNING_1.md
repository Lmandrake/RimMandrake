# FEVERWOOD_DIANOGA_TANK_TUNING_1 — Sekkulaath prison tank, real numbers not placeholders

## spec

Authority: `FEVERWOOD_DIANOGA_PRISON_1` (build), `design/Jawa/worldbuilding/biomes/fever_wood_deep_and_mud_2026-09-23.md`
§6j/§6m. Same posture as the sibling `FEVERWOOD_TENTACLE_SETPIECE_TUNING_1`: the
tank BUILT and playable, every numeric field flagged `INVENTED` in code/XML
comments — this item is where the owner's real numbers replace them, not where
the mechanism gets invented.

## what shipped as a flagged placeholder

- `RM_CompProperties_CapturedSpecimen` (`src/RimMandrake/FeverWood/Source/`):
  `neglectDaysBeforeEscapeRisk` (3), `neglectEscapeMtbDays` (4),
  `damageEscapeThresholdFraction` (0.5), `damageEscapeChancePerHit` (0.35),
  and each product's `mtbDays`/`countRange`.
- `RM_SekkulaathTank.xml`: `costList` (Steel 90 / WoodLog 40 / ComponentIndustrial 2),
  `MaxHitPoints` 260, `WorkToBuild` 2200, `CompRefuelable.fuelConsumptionRate`/
  `fuelCapacity`.
- `RM_Sekkulaath_Juvenile.xml`: `Wildness` 0.85, `manhunterOnTameFailChance` 0.55,
  `manhunterOnDamageChance` 0.85 — owner ruled the DIRECTION ("large wildness...
  very challenging to tame... high chance of attacking if you fail") but not the
  numbers. ⛔ Do not treat these three as delivered; they are the same kind of
  placeholder the eye set-piece's ambient weight was in the sibling item.

## open, and rulings-shaped — do NOT guess

- **The three taming numbers themselves** (Wildness / tame-fail manhunter chance /
  damage manhunter chance) — owner explicitly said not to guess them.
- 🔴 **"It remembers the tank" — the real mechanism.** `RM_Hediff_CaptivityMemory`
  ships as a pure marker hediff (zero stat/cap effects) applied to every escapee —
  the DATA half only. The owner's own framing is *grudge, not difficulty*:
  whether the effect is a tame-chance penalty specifically against the colony
  that held it, a manhunter bias, or something else is unruled. Do not resolve
  this by adding a flat wildness/tame-chance modifier to the hediff and calling
  it done.
- **Whether stage 2 and stage 3 are the same event.** This build's
  `RM_CompEscapedCaptive.Install()` treats "reaches a pool" as immediately
  un-killing the map's ambient elder-being system (`RM_MapComponent_TentacleWatch.
  Notify_SekkulaathInstalled()`) — a conservative reading that does NOT build a
  timed maturation ("small horror -> full elder being, on a clock"). If the owner
  wants a true staged maturation with its own duration and an interruptible
  window, that is new mechanism work, not a tuning pass.
- **Corpses as tank fuel.** This build accepts only raw meat (`CompRefuelable`
  `fuelFilter: MeatRaw`) — corpses were deliberately left out (documented scope
  cut in `RM_SekkulaathTank.xml`'s header) because CompRefuelable's fuel-value
  model doesn't fit a `Corpse` Thing cleanly. If corpse-feeding matters, it needs
  either a custom hauling/consumption path or confirmation that the cut is fine.
- **A stronger "beeline for water" behaviour.** Stage 1 currently rides the
  vanilla `waterSeeker` race flag only (an approximation, not a custom
  water-seeking JobGiver) — flagged in `RM_Sekkulaath_Juvenile.xml`'s header.
- **The "teaches" mechanical payoff's own number.** `RUT_MapComponent_TheTenant`
  now halves (`2x` MTB, hardcoded) the strike chance at registered water for
  colonists once taught — an invented multiplier, not ruled.
- **Whether the generic abstraction chosen here (`RM_LivingCapturePodBase` +
  `RM_CompProperties_CapturedSpecimen`) is the right shape for the OTHER
  4a-named candidates** (venom creature, egg-layer, blood donor, nectar-drinker)
  before a second one gets built against it.

## reuse note for whoever picks this up

Read `RM_CompCapturedSpecimen.cs` and `RM_CompProperties_CapturedSpecimen.cs`
fully first — every number is commented in place with what it does and why the
placeholder value was chosen; this item does not repeat that detail.
