<!-- status: aspirational -->
# Explosion energy model — everything detonates, scaled by energy density

_The build spec for `design/V2_DREAMS.md` §1. Drained out of that register 2026-08-14 so the
spec has a home; the register keeps one line. Every claim here is a quoted def or
an IL read — nothing is inferred from behaviour._

**The ask (owner, 2026-08-12).** Vanilla only lets turrets, IEDs and batteries blow
up. In Star Wars, powered things fail violently. Bring it to droids, workbenches,
machines and **powered equipment carried by pawns** — and **scale the blast to the
energy density of the device, not its physical size.** A big empty crate is not a
bomb; a lightsaber hilt is.

Named poster children: **lightsabers** (small, absurdly energy-dense) and **shield
belts** (should vent when the shield is *broken*, not only when destroyed).

⚠️ **The droid half of this design is NOT here.** Ion, capture, which droids may
detonate and the three incompatible droid families are all in
`design/Jawa/droid_ruling.md` — §6 in particular. Read it before writing droid XML.

---

## 1. The vanilla mechanism, and why the thesis is already in the game

`CompProperties_Explosive`; turrets are the reference implementation.
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Data\Core\Defs\ThingDefs_Buildings\Buildings_Security_Turrets.xml`

| Def | line | radius | `basePowerConsumption` | never-explode chance |
|---|---|---|---|---|
| `Turret_MiniTurret` | 112 | 3.9 | 80 W | 0.5 |
| `Turret_Autocannon` | 325 | 5.9 | 150 W | 0.5 |
| `Turret_Sniper` | 428 | 5.9 | 150 W | 0.5 |
| `Turret_Mortar` | 532 | 4.9 | — | (none — always) |
| `Turret_RocketswarmLauncher` | 833 | 6.9 | — | 0.8 |
| `Turret_FoamTurret` | 646 | 0 | — | 1.0 (never) |

**Radius already tracks power draw, not footprint** — all three powered turrets are
the same 1×1 building. That is the entire design thesis, present in vanilla and
never generalised. (Two data points: 80 W→3.9 and 150 W→5.9 fit ≈ `W^0.66`. An
anchor, not a law.)

Other knobs worth stealing, from the IED traps in `Buildings_Security.xml`
lines 240–330: `startWickHitPointsPercent` (0.2), `startWickOnDamageTaken` (a
damage-def whitelist), `preExplosionSpawnSingleThingDef` (`Filth_BlastMark`),
`postExplosionGasType`, and non-`Bomb` damage types — `Flame`, `EMP`, `Smoke`.

**Shield belts are stat-driven, not comp-driven, in 1.6.**
`…\Data\Core\Defs\ThingDefs_Misc\Apparel_Belts.xml` line 5: `Apparel_ShieldBelt`
has `<thingClass>Apparel</thingClass>` and **no `CompProperties_ShieldBelt`** —
there is no such comp anywhere in the game data. The shield runs entirely on
`<statBases>`: `EnergyShieldEnergyMax` 1.1, `EnergyShieldRechargeRate` 0.13.

Two consequences: the energy budget is **already a literal number we can XPath-patch**,
and **shield-break venting cannot be done in XML** — nothing in the def describes
the break event.

**The lightsaber donor is identified:** Star Wars: The Force – Lightsaber,
`lee.theforce.lightsaber`, WS `3466124712`, KotOR hard-dep. Roster ruling at
`design/Jawa/mods/required_mods.md`: *"only The Force – Lightsaber (KotOR
hard-dep)."* **Its defNames are still unread.**

---

## 2. ✅ SETTLED — no wick. Destroyed means detonated, immediately.

**Owner's ruling, 2026-08-12.** Vanilla turrets hiss for 240 ticks. We do not want
that. Destroyed → explodes, that frame, no fuse, no warning sound, no countdown.

Dropped by that ruling: `wickTicks`, `startWickHitPointsPercent`,
`startWickOnDamageTaken`, `chanceNeverExplodeFromDamage` as a *tuning* knob (it
gates the damage-triggered path we no longer use), and the per-tick performance
risk. This is a strictly **smaller** mechanism than the turret reference — a single
event hook on destruction, with only `explosiveRadius`, `explosiveDamageType` and
the pre/post-explosion spawn fields left.

With the performance argument gone, breadth is a **design** choice, not a cost one
— so the `E = 0 → no comp` rule below now carries the whole weight of keeping the
colony from becoming a minefield. Keep it strict.

---

## 3. ✅ The mechanism — read out of the assembly 2026-08-12, do not re-derive

Disassembled from `…\RimWorldWin64_Data\Managed\Assembly-CSharp.dll` with
`src/RimMandrake/Utils/ilprobe/`. Cited as type + method + IL offset; a DLL has no
line numbers.

**1. It is pure XML.** No Harmony, no C# assembly, no solo game load.
`CompProperties_Explosive` has real public bools `explodeOnKilled` and
`explodeOnDestroyed`. `CompExplosive::PostDestroy` is 47 bytes of IL and
transcribes exactly to:

```csharp
if (!destroyedThroughDetonation &&
    ((mode == DestroyMode.KillFinalize && Props.explodeOnKilled) || Props.explodeOnDestroyed))
    Detonate(previousMap, true);
```

`Detonate` calls `GenExplosion::DoExplosion` directly. **Zero wick, zero ticks, same
frame.** There is no `Notify_Killed` override; `explodeOnKilled` is implemented
entirely through `PostDestroy`.

**2. ⚠️ Use `explodeOnKilled`. NEVER `explodeOnDestroyed`.** This is the
salvage-safety question and it has a sharp answer. `ThingWithComps::Destroy` calls
`PostDestroy` for *every* `DestroyMode`; only the comp filters:

| action | DestroyMode | `explodeOnKilled` | `explodeOnDestroyed` |
|---|---|---|---|
| killed by damage | KillFinalize (2) | **explodes** | **explodes** |
| **pawn deconstructs it** | Deconstruct (4) | no | **EXPLODES** |
| blueprint replace | WillReplace (1) | no | **explodes** |
| map cleanup / gravship transfer | Vanish (0) | no | **explodes** |
| cancel / refund / quest logic | 5–8 | no | **explodes** |

`explodeOnDestroyed` would detonate a machine in the face of the colonist
dismantling it. For a clan whose premise is salvage that is the worst possible
failure, and it is one word away from the correct field. It also resolves the
WreckedMachines SACRED SCRAP conflict for free: wrecked-tier machines are
deconstructed, not killed, so with `explodeOnKilled` they are inert automatically.

**3. ⚠️ `tickerType` is still demanded — for validation, not performance.** The
detonation path is genuinely ticker-independent (`CompTick` is a no-op when
`wickStarted` is false and `countdownTicks` is unset). But
`CompProperties_Explosive::ConfigErrors` unconditionally yields
`"CompExplosive requires Normal ticker type"` whenever `parentDef.tickerType !=
Normal` — it never checks whether a wick was configured. A `Rare`-ticker building
with the comp *works*, and logs one red error per def at startup.

So breadth is capped again — by log noise, not frame cost. Three options, best first:

1. **Curate.** Patch only the defs that should explode and flip those to `Normal`.
   No errors, negligible cost. **This is the recommendation.**
2. `<ignoreConfigErrors>true</ignoreConfigErrors>` per patched def. Free and
   correct — but it blinds you to every *other* config error on that def, a bad
   trade in a stack this size.
3. Flip thousands of buildings `Rare`→`Normal`. Don't. The 1.6 `Normal` branch of
   `Thing::DoTick` runs the comp loop 60×/sec **and** a second `TickInterval` comp
   loop, per comp per building — and buys nothing `explodeOnKilled` does not.

**4. The exact template, already in vanilla.** `Turret_FoamTurret`,
`Buildings_Security_Turrets.xml` line 646:

```xml
<tickerType>Normal</tickerType>
<comps>
  <li Class="CompProperties_Explosive">
    <wickTicks>0</wickTicks>
    <explodeOnKilled>true</explodeOnKilled>
    <explosiveRadius>0</explosiveRadius>
    <explosiveDamageType>Extinguish</explosiveDamageType>
    <chanceNeverExplodeFromDamage>1</chanceNeverExplodeFromDamage>
  </li>
```

`chanceNeverExplodeFromDamage: 1` is load-bearing: it disables
`CanEverExplodeFromDamage`, suppressing **both** the `PostPreApplyDamage` instant
path and the `PostPostApplyDamage` wick-start. With it set, death via `PostDestroy`
is the only remaining trigger — precisely the ruling.

⚠️ `wickTicks: 0` does **not** mean instant on its own — `StartWick` sets
`wickTicksLeft = 0` and `CompTick` must run once to decrement it below zero. *That*
path needs `Normal`. `explodeOnKilled` needs nothing.

**5. No counterexample exists.** All 54 vanilla defs carrying the comp are `Normal`.
Across the installed workshop stack, 1,063 modded defs carry it: 705 explicitly
`Normal`, 358 inherited, **0 non-Normal**.

**Not observed at runtime.** All of the above is static analysis. If confirmation is
wanted, the deciding log string is
`Config error in <defName>: CompExplosive requires Normal ticker type`.

---

## 4. Death, salvage and the corpse — answered from IL

*"How could a droid ever be deactivated without exploding?"* — the answer inverts
the question: **a thing can explode AND leave full salvage, and vanilla already does
exactly that.**

**1. The corpse exists before the blast.** `Pawn::Kill` despawns the pawn
(`IL_0250`), creates and places the corpse (`MakeCorpse` `IL_02d8`, `TryPlaceThing`
`IL_02f0`), drops `killedLeavings` (`IL_041e`) and **only then** calls `Thing::Kill`
→ `Destroy(KillFinalize)` → `PostDestroy` → `Detonate`. The blast is centred on the
corpse.

**2. 🔑 Whether the salvage survives is decided by ONE field:
`explosiveDamageType`'s `harmsHealth`.** `DamageWorker::Apply` `IL_003d` skips all
hit-point damage when `harmsHealth: false`. A stun-type blast destroys nothing at
all — not the corpse, not the leavings, not your colonists' gear.

**3. Vanilla's only exploding mech is deliberately non-destructive — this is the
template.** `Mech_Apocriton`: `explodeOnKilled: true`, `wickTicks: 0`,
`explosiveRadius: 30.9`, `explosiveDamageType: MechBandShockwave` which is
`harmsHealth: false`. A 30.9-tile pulse that stuns for 20 s and damages nothing. You
recover its corpse, its slag and its `NanostructuringChip`.

**4. ⚠️ Pawns do NOT get the leavings shield buildings get.** `Thing::Destroy`
`IL_00dc` registers killed-leavings as ignored-by-explosion — but only
`if (spawned)`, and `Pawn::Kill` already despawned. So a `harmsHealth: true` blast
on a droid **destroys its own corpse and its own leavings**. Buildings are
protected; pawns are not. This asymmetry is the whole salvage risk.

**5. ⚠️ Always set `chanceNeverExplodeFromDamage: 1`** on death-explosive pawns, as
Apocriton does. Without it a lucky shot triggers `PostPreApplyDamage` and detonates
mid-fight, which **bypasses `MakeCorpse` entirely** — no corpse, no salvage, no
warning.

**6. Guaranteed salvage even from a lethal blast:**
`postExplosionSpawnSingleThingDef` spawns at `Explosion::ExplosionEnded`, after
every cell resolves, so it is immune to the blast. One item per explosion.

**7. `explodeOnKilled` cannot be made probabilistic in XML.** It is a bool and
`PostDestroy` has no chance check. `chanceNeverExplodeFromDamage` gates only the
damage path — and is rolled *per instance* from `thingIDNumber.GetHashCode()`, so
each spawned thing is permanently a dud or permanently live, never per-event.
**"Some droids explode" therefore needs two ThingDefs or Harmony.** Recommend two
defs: deterministic-by-type is better design anyway, because the player can learn
which droids are dangerous.

### The three tiers

| tier | example | comp |
|---|---|---|
| **inert** | protocol, astromech, labour droids; any wreck | `E = 0`, **no comp** — falls over, fully salvageable |
| **stun-burst** | battle droids, most combat units | `explodeOnKilled`, custom `harmsHealth: false` damage type, `chanceNeverExplodeFromDamage: 1`. Spectacle, no salvage loss |
| **genuinely destructive** | reactor units, droidekas, anything carrying a power cell | `Bomb`/`EMP`, accepts that it destroys its own corpse — plus `postExplosionSpawnSingleThingDef` for a guaranteed scrap drop |

Most droids belong in tier 1. That is both the `E = 0` rule and the fiction: battle
droids come apart in pieces, they do not detonate.

---

## 5. The energy model to build

One scalar **energy score `E`** per thing, from whatever proxy that family exposes,
then a single curve. Blast physics says radius goes as the cube root of yield:

```
radius = R0 · (E / E0)^(1/3),  clamped to [minR, maxR]
anchor: E0 = the mini-turret, R0 = 3.9
```

…checked against the `W^0.66` fit above during balance.

| family | energy proxy | where it lives | confidence |
|---|---|---|---|
| powered buildings, workbenches | `basePowerConsumption` | `CompProperties_Power` | **verified** |
| batteries, capacitors | `storedEnergyMax` | `CompProperties_Battery` | to verify |
| fuelled machines | fuel def × capacity (chemfuel ≫ wood) | `CompProperties_Refuelable` | to verify |
| shield belts / packs | `EnergyShieldEnergyMax` | `<statBases>` | **verified (1.1 vanilla)** |
| droids / mechs | Biotech mech energy + weight class | field names **unread** | to verify |
| lightsabers, powered weapons | hand-authored table (few defs) | `lee.theforce.lightsaber` | defNames unread |
| unpowered anything | `E = 0` → **no comp added** | — | by design |

**`E = 0` must mean silence.** The failure mode of this whole idea is a colony where
every chair and wooden table is a grenade.

⚠️ **Read CURRENT power state, not a def-time maximum** (a retired seat, 2026-08-12).
`basePowerConsumption` is a property of the *def*, so a switched-off or derelict
machine reads as a bomb. The proxy must be what the thing is actually drawing or
holding — otherwise a wreck reads identically to a live reactor, which is exactly
the distinction the rule exists to make. Owner's framing, verbatim: *"a wreck has no
power, hence it cannot explode. POWER DENSITY explodes, not the fact it's a
machine."*

---

## 6. Decide these before writing a line of XML

1. **Does an existing mod already do this?** Read `ModsConfig.xml` for the live
   count, never a number in a doc. A blanket "everything explodes" patch colliding
   with one already in the stack is the most likely way this wastes a load.
   **Census first.**
2. **Chain reactions.** Workshops cluster; benches sit next to batteries. Needs a
   global multiplier and a hard radius cap.
3. **`Flame` will burn the ship down.** The Kolyska is a gravship interior. Probable
   ruling: `EMP`/`Bomb` inside a hull, `Flame` only outdoors or for genuinely
   combustible fuel stores.
4. **WreckedMachines (SACRED SCRAP) is reconciled by construction, not exception** —
   a wreck is not *exempted* from detonation, it simply fails the power test. See
   `src/RimMandrake/WreckedMachines/DESIGN.md` and its `V2.md` §6. ⚠️ The **kludged**
   middle tier is a live machine and therefore a detonation candidate — arguably the
   right one, since a bodged repair should fail violently.
5. **How much is C#?** The destroy-and-detonate half is **pure XML**
   (`explodeOnKilled`) and batches into an ordinary load. **Shield-break venting
   still needs Harmony**, since the break event is not in the def — that, and only
   that, is the piece that rides a load alone. Ship the XML mod first; it is
   independently useful and costs nothing extra.
6. **Does `CompExplosive` fire on apparel and on equipped weapons at all?** The comp
   is on buildings everywhere in vanilla. A lightsaber detonating when its wielder is
   downed is the marquee case and it is **unverified**. Test on one def before
   scaling.

## 7. Suggested first slice

One machine, one weapon, one belt — not the stack. Author energy tiers for a handful
of named defs, prove the comp fires in each of the three contexts, then generalise.
Same logic as the WreckedMachines pilot: discover the cost at 3 defs, not 3,000.
