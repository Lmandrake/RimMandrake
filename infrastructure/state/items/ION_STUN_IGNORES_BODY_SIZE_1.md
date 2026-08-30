# ION_STUN_IGNORES_BODY_SIZE_1 — overload severity has no body-size term at all

Owner, 2026-08-29, live play: "The ion gun (and I think the sonic weapons) just took down a
HUGE behemoth (alpha animals) in a few shots with the Ion building (overloaded) effect. That
was WAY too easy. The barrier to doing this should scale with the body size too, likely
squared. (and the other way, tiny things are taken out in one shot for sure)"

## spec
Every flesh target — a rat and a 32×-human-bodySize Alpha Animals Behemoth alike — currently
needs the identical ~4-5 ion hits to go from 0 severity to "overloaded" (downed, alive,
unharmed). `severity` per hit has no body-size term whatsoever. Add one, direction and rough
magnitude per the owner's ask (scale with body size, "likely squared"); exact constant is a
tuning call, not decided here.

## mechanism, read from our own source, not guessed
`src/Jawa/JawaIonWeapons/Defs/DamageDefs_JawaIon.xml`:
```xml
<additionalHediffs>
  <li><hediff>JawaIon_Stun</hediff><severityPerDamageDealt>0.03</severityPerDamageDealt></li>
</additionalHediffs>
```
`src/Jawa/JawaIonWeapons/Source/DamageWorker_IonBuildup.cs:114-116`:
```csharp
float severity = entry.severityFixed > 0f
    ? entry.severityFixed
    : entry.severityPerDamageDealt * dinfo.Amount;
```
`dinfo.Amount` is the bolt's raw damage (8), never the victim's `RaceProps.baseBodySize` —
`Hediff.Severity` climbs identically regardless of who's hit. `JawaIon_Stun`'s `maxSeverity`
is 1.0, decay -1.2/day (`Defs/HediffDefs_JawaIonStun.xml`), "overloaded" (forced-down) stage
at `minSeverity: 0.9` — so **~0.24 severity/hit × 4-5 hits overloads anything**, human or
Behemoth, exactly matching what the owner watched happen.

**Measured `baseBodySize`, off the live def dump (584-mod set):**
| creature | baseBodySize | hits to overload TODAY |
|---|---|---|
| Rat | 0.2 | ~4-5 (same as everything) |
| Human | 1.0 | ~4-5 |
| Muffalo | 2.4 | ~4-5 |
| Thrumbo / Elephant | 4 | ~4-5 |
| vanilla `Behemoth` | 6 | ~4-5 |
| **`AA_Behemoth` (Alpha Animals)** | **32** | **~4-5** ← what the owner hit |

**Proposed formula, for the owner to react to, not adopted here:** divide
`severityPerDamageDealt` by `bodySize²`, human (bodySize 1) as the unscaled reference point so
the weapon's identity against people is untouched:
```
severity = (entry.severityPerDamageDealt * dinfo.Amount) / (pawn.BodySize * pawn.BodySize)
```
Worked hits-to-overload at this exponent (0.24 baseline severity/hit at bodySize 1, decay
ignored):
| creature | bodySize | hits to overload (proposed) |
|---|---|---|
| Rat | 0.2 | 1 (severity 6.0 in one hit — the owner's "tiny things, one shot" case) |
| Human | 1.0 | ~4-5 (unchanged) |
| Muffalo | 2.4 | ~24 |
| Thrumbo / Elephant | 4 | ~67 |
| vanilla `Behemoth` | 6 | ~150 |
| `AA_Behemoth` | 32 | ~4270 — effectively immune to solo sustained fire once decay is
  counted; **flag this to the owner explicitly**, since "squared" at bodySize 32 may be far
  past what he intended and could need a softer curve (e.g. `sqrt(bodySize)` past some
  threshold) rather than a pure square all the way up.

## Sonic weapons — NOT ours, not yet read
"I think the sonic weapons" too — no Jawa-authored sonic mod exists; the candidates are
third-party: `guy762_sonpistol`/`KotORSonicWave_stun` (Star Wars KotOR Weapons and Armor) and
`OuterRim_SonicGrenade` (Outer Rim - Core). Neither's mechanism was read this pass — unlike
ion, these are NOT our `workerClass`, so a fix (if one is even ours to make) means either a
compatibility patch on their `DamageDef`/`HediffDef`, or confirming vanilla's own
`StunHandler`/`EMPResistance` path (which THEIR stun likely routes through, unlike our custom
buildup) already has some size term we're not seeing and it's just calibrated too low.

## 🔴 RULED 2026-08-29, owner: "Nope, we're going with square. It should take a
## ship-weapon-scale ion gun to take this thing down, and that's good. Fix it, deploy it."
Pure `bodySize²`, no cap, no softening curve. `AA_Behemoth` reading as ~4270 hits (effectively
immune to solo hand-weapon fire) is the INTENDED outcome, not a consequence to soften.

## Fixed (`9a421aa8`)
`DamageWorker_IonBuildup.cs`: `severity /= pawn.BodySize * pawn.BodySize` (guarded `> 0f`),
applied uniformly to both the `severityFixed` and `severityPerDamageDealt` paths, right after
`severity` is computed and before the existing `severity <= 0f` skip. Human (BodySize 1) is
the unscaled reference point — the weapon's identity against people is untouched. Built clean
(`dotnet build -c Release`, 0 warnings/errors) and committed together with the rebuilt
`Assemblies/JawaIonWeapons.dll`.

**Deploy BLOCKED, not done**: `deploy_custom_mods.py --mod JawaIonWeapons --apply` failed —
`OSError: [Errno 22] Invalid argument` copying `Assemblies/JawaIonWeapons.dll` — the running
game holds the DLL open, same lock class as the JawaBench companion
(`rimworld-deploy` skill: "a companion DLL cannot be written while the game runs", and this
turns out to apply to any loaded mod assembly, not just the companion). **Deploy at the next
game-down window**: `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod JawaIonWeapons
--apply`, plan is clean (one file, no other drift).

## verify
Once deployed: overload a Rat, a Human, and an `AA_Behemoth` with the same ion weapon and
count hits. Expect Rat ~1 hit, Human ~4-5 (unchanged), `AA_Behemoth` effectively unstunnable
by hand fire within a normal engagement (severity decays -1.2/day faster than solo fire could
plausibly outpace it at this scale).

## criteria
- [x] Owner picked the scaling shape: pure `bodySize²`, no cap.
- [x] `DamageWorker_IonBuildup.cs` applies it; human-scale behavior (~4-5 hits) unchanged by
      construction (bodySize 1 → division by 1).
- [x] Deployed 2026-08-29T18:54:14Z (`deploy_custom_mods.py --mod JawaIonWeapons --apply`).
- [x] Live-verified 2026-08-30 (quicktest, game UP): fresh Rat downed in 1 hit
      (severity 6.0 in one hit, matches `0.24/0.2²`). Fresh `Tribal_Warrior`
      downed after 2 hits, not the 4-5 baseline — `hediffsBefore` was already
      7 at hit 1, same pre-existing-hediff noise `ION_TIERS_MEASURED_LIVE_1`
      already flagged as per-pawn generation variance, not a math defect.
      `AA_Behemoth`: `downed=false` after 3 hits, hediff count plateaus at 2
      (severity negligible, matches the ~4270-hit prediction). `totalDamageDealt
      = 0.0` on every hit for all three — capture-not-kill holds. Bonus:
      `OuterRim_BattleDroid` read `stunTicksLeft: 720`, exactly matching the
      prior droid-tier measurement — confirms `DROIDWORKS_ION_GUARD_1`'s guard
      change didn't disturb the machine/droid tier.
      **Not verified**: the multi-hour decay/floor-stage curve
      (`DROIDWORKS_ION_GUARD_1`'s own change) — needs a long observation
      window, not practical in a quicktest pass; left open there.
- [ ] Sonic weapons' mechanism named (which mod, which DamageDef/HediffDef, does it already
      read body size) — separate follow-up, not blocking this item's close.
