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

## verify
Live: overload a Rat, a Human, and (if the mod is active) a Behemoth-class creature with the
same weapon and count hits before/after the fix. `jawa/spawn_pawn` + repeated `jawa/fire_raid`-
adjacent single-target damage calls, or a direct `TakeDamage` companion call if one exists.

## criteria
- [ ] Owner picks the scaling shape (pure `bodySize²`, capped, or a softer curve past some
      threshold) — the `AA_Behemoth` near-immunity consequence above is surfaced for that call.
- [ ] `DamageWorker_IonBuildup.cs` applies the chosen body-size term; human-scale behavior
      (~4-5 hits) is unchanged (regression check).
- [ ] Sonic weapons' mechanism named (which mod, which DamageDef/HediffDef, does it already
      read body size) — separate follow-up if a fix there is warranted and is ours to make.
- [ ] Live-verified: a small creature drops in ~1 hit; a huge one takes dramatically more (or
      is confirmed effectively immune to solo fire, per the owner's chosen curve).
