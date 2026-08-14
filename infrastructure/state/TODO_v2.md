# TODO_v2.md — deferred work, bodies intact

_Split out of `TODO.md` 2026-08-13 when the v1 line was drawn (`file:///D:/Luke/dev/Rimworld/infrastructure/state/V1_SCOPE.md`)._

**Nothing here is cancelled.** These are complete, hard-won items — IL reads,
owner rulings, measured ground truth — moved out of the work queue so the queue
can be read. **v2 starts the day v1's gate passes.**

⚠️ **Do not work these while v1 is open.** If one blocks a v1 row, say so and it
moves back.

---

## 0b. [PROJECT] Do enemies actually USE vehicles against us? Three mods live or die on it

**Owner's ask, 2026-08-12.** _"The point here is to be able to have enemies use
these against us in raids. If they can't or won't, then these three mods should
be dropped."_

**The three:** `smashphil.vehicleframework` · `gabrieel1482.raidvehicleframework`
· **"mother (HK Tank)" — ⚠️ NOT IDENTIFIED, see below.**

**The test is binary and the owner has pre-committed to the answer**, which is
what makes this worth doing properly: if raiders cannot or will not arrive in
vehicles, all three go. No partial credit, no "but the player can build them" —
the player-facing half is not the justification.

### ⚠️ Already found, and it is not encouraging

**`VRF_SettlementVehicleDef` has ZERO defs in the 21:09 live dump.** That is
VehicleRaid Framework's own def type — the one that says which settlements field
which vehicles. An empty registry is the shape of a framework that is installed
and **supplying nothing**, and it is the single strongest signal available
offline.

⚠️ **Do not close the item on that alone.** The defs may be generated at runtime,
supplied by a patch, or read from settings rather than defs — all three are
common. **Falsify it before recommending a drop**, because "the def type is
empty" and "raiders never use vehicles" are different claims and only the second
one is the owner's question.

### What to check, offline first

1. `strings` the two assemblies for raid-arrival hooks — `PawnsArrivalModeDef`,
   `RaidStrategyDef`, `IncidentWorker_RaidEnemy`, Harmony patch targets.
2. Look for a **settings file** (`Config/Mod_*_*.xml`) — Faction Control's whole
   capability lived in settings with zero defs, so an empty def registry proves
   less here than it looks. Same trap, same day.
3. Check whether any live `PawnKindDef` or faction `pawnGroupMaker` references a
   vehicle at all. If no enemy pawn group can field one, the answer is settled.
4. Only then, if still ambiguous, put a named log string in `NEXT_RELOAD.md` and
   let one load decide it.

### ⚠️ "mother (HK Tank)" — I cannot identify this and did not guess

**No match in the 573-mod dump**: no `HK`-prefixed defName in any def type, and
nothing named "mother", "HK" or "tank" in the manifest's mod list. So it is
either not installed, named differently in the Workshop than in `About.xml`, or
I have misread the ask. **Owner: which mod is this?** The other two are
identified and can be assessed without it.

**Related, and it should ride the same decision:** `farxmai2.vanilladeconstructablevehicles`
(VVE - Deconstructable Vehicles Junk) is also live and is a VVE add-on. If VVE
survives but the frameworks go, check whether it still has a job.

---


## 0c. [CREATE] Reskin Alpha Vehicles – Neolithic: horses → Banthas

**Owner's ask, 2026-08-12.** `sarg.alphavehiclesneolithic`, 12 vehicles.

⭐ **This ruling reverses a drop I had filed**, and the reversal is the point:
I put Alpha Neolithic in the cherry-picker inbox as off-theme "in a way **no
label change fixes** — a dog sled here is a category error, not a reskin
problem." The owner ruled the opposite. Withdrawn from the cull list, struck
through rather than deleted so the disagreement stays visible.

**Scope:** the draught animals are the off-theme part, not the carts. Ox carts,
covered carriages, chariots and sleds pulled by **Banthas** read as Tatooine;
pulled by horses and oxen they read as medieval Europe. Art problem, not a def
problem.

**The 12:** Wheelbarrow, Hwacha, Balloon, Rickshaw, Row boat, Palanquin,
Chariot, War chariot, Outrigger Canoe, Dog Sled, Covered Carriage, Ox cart.

### 📏 SCOPED by CREATE 2026-08-12 — it is **5 vehicles, not 12**

Measured by opening the art, not inferred from the names. **The draught animals
are drawn INTO the vehicle texture**, so the reskin is a per-file edit — but only
five vehicles have an animal at all:

| vehicle | what pulls it | files |
|---|---|---|
| **Chariot** | 1 horse | 6 |
| **War chariot** | 2 horses | 6 |
| **Covered carriage** | 2 horses | 6 |
| **Ox cart** | 2 oxen | 6 |
| **Dog sled** | 4 dogs | 6 |

**The other seven have no animal to replace.** Rickshaw, Palanquin, Wheelbarrow
and Hwacha are human-powered; Balloon is `Air`; Row boat and Outrigger Canoe are
`Sea`. Nothing to reskin on any of them.

**Real cost: 30 PNGs** — 5 vehicles × 3 facings (`north`/`south`/`east`, west is
mirrored) × 2, because every facing has a paired **`_m` mask** file for the
Vehicle Framework's colour/pattern system. **The mask must be edited in step with
the art or the new animal will not tint.**

⚠️ **The Sea question is moot for THIS job.** Neither boat has a draught animal,
so whether a canoe belongs on a desert world is a *cull* question for whoever
owns the mod list — it does not change one pixel of the reskin and should not
gate it.

✅ **DOG SLED — OWNER RULED 2026-08-12: redraw it with a different desert
creature.** Not a Bantha, and not left alone. CREATE's scale objection is
accepted; the sled stays in the mod and gets its own animal.

⭐ **Candidates are already live — you do not need to invent one.** All from
**Star Wars Animal Collection (Continued)**, confirmed in the 21:09 dump:

| creature | defName | bodySize | packAnimal | note |
|---|---|---|---|---|
| **Massiff** | `Massiff` | **0.85** | false | ⭐ **The near 1:1 swap.** A vanilla husky is ~0.75–0.86, so four massiffs occupy almost exactly the footprint four dogs do — least art risk, no rescaling, and it is canonically Tatooine. Named in `Alien_Bestiary.md:153` as an anchor species. |
| **Eopie** | `Eopie` | 1.4 | **true** | The *lore-correct* hauler — Tatooine's canonical beast of burden, and flagged `packAnimal`. Bigger than a dog, so the team may want to drop from four to two. |
| Blurrg | `Blurrg` | 2.5 | true | Riding beast; `Alien_Bestiary.md:182` lists it in the mobility layer. Probably too big for a sled team. |
| Dewback | `Dewback` | 3 | true | Sandtrooper mount. Same scale objection as the Bantha, just smaller. |
| ~~Bantha~~ | `Bantha` | 4 | true | The rejected option, for reference. |
| ~~Ronto~~ | `Ronto` | 6 | true | Far worse. |

### ✅✅ OWNER RULED 2026-08-12 ~23:20: **EOPIE, team of two.** Job is UNBLOCKED.

CREATE's call below was accepted over PROJECT's Massiff recommendation. **This
was the last thing gating the reskin; the dog sled is the first vehicle to draw.**

⭐ **Both aspect numbers re-measured 2026-08-13 from the extracted textures and
they reproduce:** Eopie **0.618** (recorded 0.62), Massiff **0.720** (recorded
0.73). The ruling rests on numbers that hold up.

⚠️ **The creature art is NOT loose PNGs** — every Star Wars Animal Collection
texture lives inside a 33 MB Unity AssetBundle, and `src/RimMandrake/Utils/extract_bundle.py`
needs a venv to run at all. Recipe in
`design/Jawa/art/graphics_overhaul_protocol.md` §2.2; `python3`, never `python`.

⚠️ **Correction to this section's own scoping, found by measuring the file:**
the paired mask is `AV_DogSled_southm.png` — suffix `m` on the facing, **not**
`_south_m.png`. Every one of the 15 mask paths below is affected.

✅ **Team count re-verified 2026-08-13: it IS 4 dogs in a 2×2.** Counted
programmatically — 8 blue-eye clusters = 4 heads at 2 rows × 2 columns. Reading
the enlarged sprite by eye suggested six, because each dog's haunch reads as a
separate body. **Do not re-litigate this from a screenshot; count the eyes.**

### CREATE's CALL, 2026-08-12: **EOPIE, team of two** — measured, not preferred

PROJECT offered the choice and recommended Massiff. I measured the sprites and it
goes the other way.

| | sprite w/h, south facing | vs the slot it must fill |
|---|---|---|
| **the dog slot in the sled art** | **0.57** | — |
| **Eopie** | **0.62** | closest |
| Massiff | 0.73 | noticeably wider |

⚠️ **The Massiff case was argued from `bodySize`, and `bodySize` is a gameplay
MASS stat — it does not determine sprite proportions.** Massiff 0.85 against a
husky's ~0.8 is a near match on *mass* and says nothing about shape. On the actual
pixels the massiff is the **wider** candidate, so it is the one that would break
the harness geometry the argument was trying to preserve. Right instinct, wrong
number — the same shape as reading a def and inferring what the renderer does.

Three further reasons, in order of weight:

1. **Fiction.** An eopie is Tatooine's canonical beast of burden. A massiff is a
   guard and hunting reptile; it has never pulled anything.
2. **It is LESS art, not more.** `bodySize` 1.4 makes a **pair** the natural team
   for a light sled, so two animals get drawn instead of four. The traces are a
   simple Y of curved lines and re-routing them for two is minor.
3. **Reference art exists**, extracted and inspected — `Eopie_south/north/east`
   plus an **`Eopie_jPack_*`** variant already wearing gear, which is the nearest
   thing to a harnessed pose anywhere in the stack.

**Measured target geometry, so nobody re-derives it:** the dog team block is
**118 × 207 px** inside the sled's 512 canvas, four animals in 2 × 2, so one slot
is ≈ **59 × 103**.

⚠️ **Reference only — do not composite.** The creature art belongs to Star Wars
Animal Collection (Continued). Same rule as `WreckedMachines/art_source/restored/`,
which is gitignored as *"not ours to redistribute"*. Draw from it, never paste it.

_PROJECT's recommendation is kept below unedited; the disagreement is the record._

**Recommendation: Massiff.** It is the only candidate that needs no
re-composition of the sled art — swap the creature, keep the harness geometry
and the team of four. Eopie is the better *fiction* answer if you are willing to
redraw the team as two larger animals.

⚠️ `packAnimal` is a **gameplay** flag on the real creature def and is irrelevant
to this job — the animal is painted into the vehicle texture, not spawned. Listed
only because it indicates which beasts the game itself treats as haulers, which
is a reasonable tiebreaker for the fiction.

**Load `skills/generating-rimworld-sprites/` before making any PNG.** It enforces
the asset contract and ships an offline validator that rejects bad art before it
costs a ~23–30 minute load.

---


## 1. Everything detonates — explosions scaled by energy density

**Requested by the owner, 2026-08-12. Status: accepted, not started. No files written.**

### The goal

Vanilla only lets turrets, IEDs and batteries blow up. In Star Wars, **powered
things fail violently** — that is the genre's single most reliable visual, from
droid poppers to a reactor going critical. Bring that to the whole stack:
droids, workbenches, machines, and **powered equipment carried by pawns**.

Crucially the owner's framing: **scale the blast to the energy density of the
device, not its physical size.** A big empty crate is not a bomb; a lightsaber
hilt is. Poster children named in the request:

- **lightsabers** — small, absurdly energy-dense
- **shield belts** — should vent when the shield is **broken**, not only when destroyed

### Ground truth — verified, do not re-derive

Read 2026-08-12 from the live 1.6 install.

**The vanilla mechanism is `CompProperties_Explosive`**, and turrets are the
reference implementation.
`file:///C:/Program%20Files%20(x86)/Steam/steamapps/common/RimWorld/Data/Core/Defs/ThingDefs_Buildings/Buildings_Security_Turrets.xml`

```xml
<!-- Turret_MiniTurret, line 150 -->
<li Class="CompProperties_Explosive">
  <wickTicks>240</wickTicks>
  <explosiveRadius>3.9</explosiveRadius>
  <explosiveDamageType>Bomb</explosiveDamageType>
  <chanceNeverExplodeFromDamage>0.5</chanceNeverExplodeFromDamage>
</li>
```

The whole vanilla turret ladder, with its power draw beside it:

| Def | line | radius | `basePowerConsumption` | never-explode chance |
|---|---|---|---|---|
| `Turret_MiniTurret` | 112 | 3.9 | 80 W | 0.5 |
| `Turret_Autocannon` | 325 | 5.9 | 150 W | 0.5 |
| `Turret_Sniper` | 428 | 5.9 | 150 W | 0.5 |
| `Turret_Mortar` | 532 | 4.9 | — | (none — always) |
| `Turret_RocketswarmLauncher` | 833 | 6.9 | — | 0.8 |
| `Turret_FoamTurret` | 646 | 0 | — | 1.0 (never) |

**Radius already tracks power draw, not footprint** — all three powered turrets
are the same 1×1 building. That is the entire design thesis, already present in
vanilla, just never generalised. (Two data points only: 80 W→3.9 and 150 W→5.9
fit ≈ `W^0.66`. Treat as an anchor, not a law.)

The **IED traps** in
`file:///C:/Program%20Files%20(x86)/Steam/steamapps/common/RimWorld/Data/Core/Defs/ThingDefs_Buildings/Buildings_Security.xml`
(lines 240–330) show the other knobs worth stealing:
`startWickHitPointsPercent` (0.2), `startWickOnDamageTaken` (a damage-def
whitelist), `preExplosionSpawnSingleThingDef` (`Filth_BlastMark`),
`postExplosionGasType`, and non-Bomb damage types — `Flame`, `EMP`, `Smoke`.

**Shield belts are stat-driven, not comp-driven, in 1.6.**
`file:///C:/Program%20Files%20(x86)/Steam/steamapps/common/RimWorld/Data/Core/Defs/ThingDefs_Misc/Apparel_Belts.xml`
line 5: `Apparel_ShieldBelt` has `<thingClass>Apparel</thingClass>` and **no
`CompProperties_ShieldBelt`** — there is no such comp anywhere in the game data.
The shield is driven entirely by `<statBases>`:

```xml
<EnergyShieldEnergyMax>1.1</EnergyShieldEnergyMax>
<EnergyShieldRechargeRate>0.13</EnergyShieldRechargeRate>
```

Two consequences: the energy budget is **already a literal number we can read
and XPath-patch**, and **shield-break venting cannot be done in XML** — nothing
in the def describes the break event.

**The lightsaber donor is identified:** Star Wars: The Force – Lightsaber,
`lee.theforce.lightsaber`, WS `3466124712`, load index 557, KotOR hard-dep —
per `file:///D:/Luke/dev/Rimworld/observed/2026-08-13/live_mod_inventory.md` line 323. The
roster ruling is at `design/Jawa/mods/required_mods.md` line 54: *"only The Force –
Lightsaber (KotOR hard-dep)."* Its actual defNames are **not yet read**.

### ✅ SETTLED — no wick. Destroyed means detonated, immediately.

**Owner's ruling, 2026-08-12.** Vanilla turrets hiss for 240 ticks before going
up. **We do not want that.** When a thing is destroyed it explodes, right then,
with no fuse, no warning sound and no countdown. Keep it simple.

What that decision removes from this design:

| dropped | why |
|---|---|
| `wickTicks` | there is no wick to count down |
| `startWickHitPointsPercent` | no partial-damage arming — destruction is the only trigger |
| `startWickOnDamageTaken` | ditto; no damage-def whitelist to maintain |
| **the `tickerType` PERFORMANCE risk** | a countdown is the only thing that needed a per-tick update. No countdown, no ticker. ⚠️ The ticker is still demanded for a *different* reason — see the ConfigError below |
| `chanceNeverExplodeFromDamage` | that field gates *damage*-triggered detonation, which we no longer use. Tuning happens on `E` instead |

This is a strictly *smaller* mechanism than the turret reference implementation,
not a larger one. Detonation becomes a single event hook on destruction, and the
only knobs left are the ones that describe the blast itself: `explosiveRadius`,
`explosiveDamageType`, and the pre/post-explosion spawn fields.

**Consequence for scope.** The tickerType tax was the argument for restricting
this to energy-dense things only. With it gone, breadth is a *design* choice
rather than a performance one — so the `E = 0 → no comp` rule below is what keeps
the colony from becoming a minefield, and it now carries that weight alone.
Keep it strict.

### ✅ The mechanism — read out of the assembly 2026-08-12, do not re-derive

Disassembled from
`file:///C:/Program%20Files%20(x86)/Steam/steamapps/common/RimWorld/RimWorldWin64_Data/Managed/Assembly-CSharp.dll`.
Cited as type + method + IL offset, because a DLL has no line numbers.

**1. It is pure XML. No Harmony, no C# assembly, no solo game load.**
`CompProperties_Explosive` has **`explodeOnKilled`** and **`explodeOnDestroyed`**
as real public bool fields. `CompExplosive::PostDestroy` is 47 bytes of IL and
transcribes exactly to:

```csharp
if (!destroyedThroughDetonation &&
    ((mode == DestroyMode.KillFinalize && Props.explodeOnKilled) || Props.explodeOnDestroyed))
    Detonate(previousMap, true);
```

`Detonate` calls `GenExplosion::DoExplosion` directly. **Zero wick, zero ticks,
same frame** — exactly the ruling above. There is no `Notify_Killed` override;
`explodeOnKilled` is implemented entirely through `PostDestroy`.

**2. ⚠️ Use `explodeOnKilled`. NEVER `explodeOnDestroyed`.** This is the
salvage-safety question, and it has a sharp answer. `ThingWithComps::Destroy`
calls `PostDestroy` for *every* `DestroyMode`; only the comp filters:

| action | DestroyMode | `explodeOnKilled` | `explodeOnDestroyed` |
|---|---|---|---|
| killed by damage | KillFinalize (2) | **explodes** | **explodes** |
| **pawn deconstructs it** | Deconstruct (4) | no | **EXPLODES** |
| blueprint replace | WillReplace (1) | no | **explodes** |
| map cleanup / gravship transfer | Vanish (0) | no | **explodes** |
| cancel / refund / quest logic | 5–8 | no | **explodes** |

`explodeOnDestroyed` would detonate a machine in the face of the colonist
dismantling it. For a clan whose entire premise is salvage, that is the single
worst possible failure — and it is one word away from the correct field. It also
resolves the SACRED SCRAP conflict in item 5 for free: wrecked-tier machines are
deconstructed, not killed, so with `explodeOnKilled` they are inert automatically.

**3. ⚠️ `tickerType` is still demanded — for validation, not performance.**
The detonation path is genuinely ticker-independent (`CompTick` is a no-op when
`wickStarted` is false and `countdownTicks` is unset). **But**
`CompProperties_Explosive::ConfigErrors` unconditionally yields
`"CompExplosive requires Normal ticker type"` whenever
`parentDef.tickerType != Normal` — it never checks whether a wick was configured.
So a `Rare`-ticker building with the comp *works*, and logs one red error per def
at startup.

That reverses the scope conclusion above: **breadth is capped again**, not by
frame cost but by log noise. Three options, best first:

1. **Curate.** Patch only the defs that should actually explode and flip those to
   `Normal`. No errors, negligible cost. This is the recommendation, and it lands
   in the same place item 2 originally predicted.
2. Add `<ignoreConfigErrors>true</ignoreConfigErrors>` per patched def. Free and
   correct — but it blinds you to *every other* config error on that def, a bad
   trade in a 561-mod stack.
3. Flip thousands of buildings `Rare`→`Normal`. Don't. In 1.6 the `Normal` branch
   of `Thing::DoTick` runs the comp loop 60×/sec **and** a second `TickInterval`
   comp loop, for every comp on every patched building — and buys nothing that
   `explodeOnKilled` does not already give.

**4. The exact template, already in vanilla.** `Turret_FoamTurret`,
`file:///C:/Program%20Files%20(x86)/Steam/steamapps/common/RimWorld/Data/Core/Defs/ThingDefs_Buildings/Buildings_Security_Turrets.xml`
line 646:

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
`CanEverExplodeFromDamage`, which suppresses **both** the `PostPreApplyDamage`
instant path and the `PostPostApplyDamage` wick-start. With it set, death via
`PostDestroy` is the *only* remaining trigger. That is precisely the ruling.

⚠️ Note `wickTicks: 0` does **not** mean instant on its own — `StartWick` sets
`wickTicksLeft = 0` and `CompTick` must run once to decrement it below zero. That
path really does need `Normal`. `explodeOnKilled` needs nothing.

**5. No counterexample exists.** All 54 vanilla defs carrying the comp are
`Normal`. Across the installed workshop stack, 1,063 modded defs carry it: 705
explicitly `Normal`, 358 inherited, **0 non-Normal**. Nobody ships a Rare ticker
with this comp.

**Not observed at runtime.** Every claim above is static analysis of IL plus
quoted defs — solid, but no Rare-ticker building has been watched detonating.
If confirmation is wanted, the deciding log string is
`Config error in <defName>: CompExplosive requires Normal ticker type`.

### 📄 THE DROID RULING LIVES IN ITS OWN DOC

Everything about droids — ion disabling, capture, the restraint bolt and data
spike, which droids may detonate, and the three incompatible droid families in
this stack — is written up in full at
`file:///D:/Luke/dev/Rimworld/design/Jawa/droid_ruling.md`.

Read that before building any droid-related XML. The short version:

* 🔴 **Ion does NOT down a droid today — it only stuns.** _(Corrected in place by
  [PROJECT] 2026-08-12: this bullet previously read "ion already downs Outer Rim
  droids… most of the owner's ask is built", which is the exact claim commit
  `6c3cb78` was written to retract. See `droid_ruling.md:86` and `:107`.)_ The
  data spike **does** already flip a downed droid to the player faction, so the
  capture chain works — the **downing** is the missing link, and it is one
  guard in one C# file. See [WORLD] W8 below.
* **`explodeOnKilled` fires on death, and a downed pawn has not died** — so ion
  is automatically the way *around* the explosion. That is the whole design:
  ion it and keep it, or destroy it and lose it.
* ⚠️ **Three droid families behave completely differently.** JDS Separatist
  droids are true `Mechanoid` flesh and can never be captured; Outer Rim and
  KotOR droids can. Do not generalise across them.
* ✅ **No longer blocked — we already fight capturable droids.** _(Corrected by
  [PROJECT] 2026-08-12: this bullet previously read "⚠️ Blocked on one question:
  do we ever actually FIGHT capturable droids?", which commit `4296af8`
  resolved. That commit's subject line also carried "and ion works" — **that
  half was itself retracted by `6c3cb78`**, so do not quote it forward. Ion
  stuns; it does not down. Caught by BRIDGE.)_

### [WORLD] W8. Ion never downs a droid — two correct patches that collide

**Reported by AGENT BRIDGE, 2026-08-12, with IL verification. WORLD's to fix —
it is a live mod and a C# rebuild.** Full argument: `design/Jawa/droid_ruling.md`
§11; the owner's chosen Option A is §5, of which this is item 1 and the only
part needing a rebuild.

The seam, and neither side is wrong:

* `Jawa_Doctrine/Patches/DroidsAreMachines.xml` sets `isOrganic: false` on
  `Asimov_Automaton` and `ABF_FleshType_Synstruct_Base` **so that EMP/ion stun
  reaches droids at all** — `StunHandler::CanBeStunnedByDamage` returns true for
  EMP only when `!IsFlesh`. Before it, ion did nothing to 41 of 57 droid races.
* `JawaIonWeapons/Source/DamageWorker_IonBuildup.cs:63` bails on exactly that
  flag — `if (!pawn.RaceProps.IsFlesh) return;` — because it assumed non-flesh
  pawns were already covered by stun.

Net live behaviour: **ion stuns a droid briefly and never downs it**, and
`stunAdaptationTicks 2200` makes repeated ion fire progressively weaker. The
capture chain past the downing already works (`OuterRim_DataSpike` requires
`Downed || IsPrisoner`, then `SetFaction`).

**Fix:** drop the `IsFlesh` guard, or narrow it to skip only `IsMechanoid` pawns
(JDS Separatist droids are true `Mechanoid` and get force-killed on downing, so
buildup is wasted there). The droid then gets the stun as an immediate interrupt
**and** the buildup that collapses it. Requires rebuilding the JawaIonWeapons
assembly.

⚠️ **Do NOT "fix" this by reverting `isOrganic` to true.** That would stop ion
and EMP stunning droids entirely, re-enable medical tending of droids against
the doctrine ruling, and make droid corpses rot — which currently protects the
salvage loop, since non-organic corpses keep indefinitely.

⚠️ **Never observed in play:** downing is capacity-based, so a non-flesh
humanlike *should* go Downed when the `overloaded` stage pins Consciousness to
`setMax 0.10` — but nobody has watched it. Make that an explicit check on the
first test rather than an assumption.

### ✅ Droids, death and salvage — the owner's question, answered from IL

*"How could a droid ever be deactivated without exploding?"* — asked 2026-08-12.
The answer inverts the question: **a droid can explode AND leave full salvage,
and vanilla already does exactly that.**

**1. The corpse exists before the blast.** `Pawn::Kill` despawns the pawn
(`IL_0250`), creates and places the corpse (`MakeCorpse` `IL_02d8`, `TryPlaceThing`
`IL_02f0`), drops `killedLeavings` (`IL_041e`) and **only then** calls
`Thing::Kill` → `Destroy(KillFinalize)` → `PostDestroy` → `Detonate`. The blast is
centred on the pawn's own corpse.

**2. 🔑 Whether the salvage survives is decided by ONE field:
`explosiveDamageType`'s `harmsHealth`.** `DamageWorker::Apply` `IL_003d` skips all
hit-point damage when `harmsHealth: false`. So a stun-type blast destroys nothing
at all — not the corpse, not the leavings, not your colonists' gear.

**3. Vanilla's only exploding mech is deliberately non-destructive.**
`Mech_Apocriton` has `explodeOnKilled: true`, `wickTicks: 0`, `explosiveRadius:
30.9` — and `explosiveDamageType: MechBandShockwave`, which is `harmsHealth:
false`. A 30.9-tile pulse that stuns for 20 s and damages nothing. You recover its
corpse, its slag and its `NanostructuringChip`. **This is the template.**

**4. ⚠️ Pawns do NOT get the leavings shield that buildings get.**
`Thing::Destroy` `IL_00dc` registers killed-leavings as ignored-by-explosion —
but only `if (spawned)`, and `Pawn::Kill` already despawned the pawn. So a
`harmsHealth: true` blast on a droid **destroys its own corpse and its own
leavings**. Buildings are protected; droids are not. This asymmetry is the whole
salvage risk.

**5. ⚠️ Always set `chanceNeverExplodeFromDamage: 1`** on death-explosive droids,
as Apocriton does. Without it a lucky shot triggers `PostPreApplyDamage` and
detonates mid-fight, which **bypasses `MakeCorpse` entirely** — no corpse, no
salvage, no warning.

**6. Guaranteed salvage even from a lethal blast:**
`postExplosionSpawnSingleThingDef` spawns at `Explosion::ExplosionEnded`, after
every cell is resolved, so it is immune to the blast. One item per explosion.

**7. EMP cannot kill a droid.** `EMP` is `harmsHealth: false` + `causeStun: true`,
and `StunHandler::CanBeStunnedByDamage` `IL_0071` stuns non-flesh pawns only. So
ion weapons genuinely are the safe way to take a droid down.

⚠️ **But there is no "downed droid" to capture.**
`Pawn_HealthTracker::CheckForStateChange` `IL_033c` forces
`deathOnDownedChance = 1.0` for mechanoids — a mech that would be downed is
killed instead. A droid is only ever *stunned* (temporarily, 1,200 ticks for the
Apocriton pulse) or *dead*. There is no vanilla incapacitated state to haul home,
so the salvage loop must run on **corpses**, not on captives. Changing that needs
Harmony, and whether it is safe is **UNPROVEN**.

**8. `explodeOnKilled` cannot be made probabilistic in XML.** It is a bool, and
`PostDestroy` contains no chance check. `chanceNeverExplodeFromDamage` gates only
the damage-triggered path — and it is rolled *per instance* from
`thingIDNumber.GetHashCode()`, so each spawned thing is permanently a dud or
permanently live, not per-event. **"Some droids explode" therefore needs two
ThingDefs or Harmony.** Recommend two defs: deterministic-by-type is better
design anyway, because the player can learn which droids are dangerous.

### Recommended droid ruling

| tier | example | comp |
|---|---|---|
| inert | protocol, astromech, labour droids | `E = 0`, **no comp** — falls over, fully salvageable |
| stun-burst | battle droids, most combat units | `explodeOnKilled`, custom `harmsHealth: false` damage type, `chanceNeverExplodeFromDamage: 1`. Spectacle, no salvage loss |
| genuinely destructive | reactor units, droidekas, anything carrying a power cell | `Bomb`/`EMP`, accepts that it destroys its own corpse — plus `postExplosionSpawnSingleThingDef` for a guaranteed scrap drop |

Most droids belong in tier 1. That is both the `E = 0` rule and the fiction:
battle droids come apart in pieces, they do not detonate.

**Tooling:** all of the above was read out of the assembly with
`file:///D:/Luke/dev/Rimworld/src/RimMandrake/Utils/ilprobe/` — no game load. Use it before
asserting anything about engine behaviour.

### The energy model to build

One scalar **energy score `E`** per thing, from whatever proxy that family
exposes, then a single curve. Blast physics says radius goes as the cube root of
yield, so start with:

```
radius = R0 · (E / E0)^(1/3),  clamped to [minR, maxR]
anchor: E0 = the mini-turret, R0 = 3.9
```

…and check it against the `W^0.66` fit above during balance. The proxies, by
family:

| Family | Energy proxy | Where it lives | Confidence |
|---|---|---|---|
| Powered buildings, workbenches | `basePowerConsumption` | `CompProperties_Power` | **verified** |
| Batteries, capacitors | `storedEnergyMax` | `CompProperties_Battery` | to verify |
| Fuelled machines | fuel def × capacity (chemfuel ≫ wood) | `CompProperties_Refuelable` | to verify |
| Shield belts / packs | `EnergyShieldEnergyMax` | `<statBases>` | **verified (1.1 vanilla)** |
| Droids / mechs | Biotech mech energy + weight class | field names **unread** | to verify |
| Lightsabers, powered weapons | hand-authored table (few defs) | `lee.theforce.lightsaber` | defNames unread |
| Unpowered anything | `E = 0` → **no comp added** | — | by design |

**`E = 0` must mean silence.** The failure mode of this whole idea is a colony
where every chair and wooden table is a grenade.

### Before writing a line of XML — decide these

1. **Does an existing mod already do this?** Several hundred mods are active —
   read `ModsConfig.xml` for the live count, never a number written in a doc. A
   blanket "everything explodes" patch colliding with one already in the stack is
   the most likely way this wastes a load. Census first.
2. ~~The `tickerType` tax.~~ **SETTLED by the owner 2026-08-12 — see "No wick"
   below. There is no tickerType question any more.**
3. **Chain reactions.** Workshops cluster; benches sit next to batteries. Needs
   a global multiplier, generous `chanceNeverExplodeFromDamage`, and a hard
   radius cap. Consider making `startWickOnDamageTaken` narrow.
4. **`Flame` will burn the ship down.** The Kolyska is a gravship interior.
   Probable ruling: `EMP`/`Bomb` inside a hull, `Flame` only outdoors or for
   genuinely combustible fuel stores.
5. **⚠️ Direct conflict with WreckedMachines (SACRED SCRAP).** That mod exists so
   the Kolyska's dead factory is **restored in place**. If every machine
   detonates when destroyed, wrecks are vaporised instead of salvaged. The two
   must be reconciled: likely *wrecked-tier machines are inert* (`E = 0`,
   already discharged) and only **live, powered** ones detonate — which is also
   the better fiction. See
   `file:///D:/Luke/dev/Rimworld/src/RimMandrake/WreckedMachines/DESIGN.md`.
6. ~~How much is C#?~~ **ANSWERED — see the mechanism section above.** The whole
   destroy-and-detonate half is **pure XML** (`explodeOnKilled`), so it batches
   into an ordinary load like any other patch. **Shield-break venting still needs
   Harmony**, since the break event is not in the def — so that, and only that,
   is the piece that rides a load **alone**. Ship the XML mod first; it is
   independently useful and costs nothing extra.
7. **Does `CompExplosive` fire on apparel and on equipped weapons at all?** The
   comp is on buildings everywhere in vanilla. A lightsaber detonating when its
   wielder is downed is the marquee case and it is **unverified**. Test on one
   def before scaling.

### Suggested first slice

One machine, one weapon, one belt — not the stack. Author
`src/` energy tiers for a handful of named defs, prove the comp fires
in each of the three contexts, then generalise. Same logic as the
WreckedMachines pilot: discover the cost at 3 defs, not 3,000.

---


## 3. The Empire — stormtroopers, black officers, and the two-Empire fusion

**Requested by the owner, 2026-08-12. Owned by [PROJECT]. Status: mod identified
and version-verified; the ruling that blocked it is overturned; build not started.**

### 3.0 ⚠️ First: a standing ruling is WRONG, and it has been costing us a port

`design/Jawa/mods/required_mods.md:572` and `:574` say the Outer Rim faction modules — the
Galactic Empire among them — are **"1.4/1.5 ONLY… INSPIRATION ONLY, a design
donor / parts bin, not installable content."**

**That is false.** Verified 2026-08-12 from the mod's own repository:

| source | `supportedVersions` |
|---|---|
| `O21-Outer-Rim/Outer-Rim-Galactic-Empire`, **`main`** branch | 1.4, 1.5 |
| same repo, **`1.6`** branch | **1.4, 1.5, 1.6** |

The `1.6` branch carries a full `LoadFolders.xml` `<v1.6>` block — including
`<li IfModActive="Neronix17.OuterRim.DroidDepot">1.6/Mods/OuterRimDroidDepot</li>`,
a hook into a module **already active in our stack**.

**The control case proves the audit method, not just this one mod.** Outer Rim
**Core** — which is active in our 568 stack and loads clean at 1.6:

| Outer Rim Core | `supportedVersions` |
|---|---|
| GitHub `main` branch | 1.4, 1.5 |
| **the Workshop copy we actually run** | **1.4, 1.5, 1.6** |

GitHub `main` is stale for this author; the shipping version lives on a
per-version branch. Every extract under `vendor/mod_sources/` is named
`Outer-Rim-*-main` — all nine were pulled from the stale branch, so the
"1.4/1.5 only" verdict was read off a copy that never contained the 1.6 tree.

Spot-checked across the family: `Outer-Rim-Seperatists` has a `1.6` branch
(2025-07-28, newer than its `main` at 2025-03-09); `Outer-Rim-Old-Republic`'s
`1.6` branch declares 1.4/1.5/1.6.

**The 1.6 tree is populated, not a stub.** Read from the branch 2026-08-12:
`PawnKinds_Stormtroopers.xml` carries a real abstract base with
`<defaultFactionType>OuterRim_GalacticEmpire</defaultFactionType>`, apparel and
weapon money ranges, `techHediffsTags`, and concrete kinds with `apparelRequired`
lists.

**The defNames did NOT change between 1.5 and 1.6 — only the filenames.** The
1.6 file `Imp_OfficerUniform_Black.xml` contains defName
`OuterRim_ImperialOfficerUniform_Black`, exactly as the 1.5 extract does.
Consequence, and it is good news: **the SRC-verified defName list in
`outer_rim_cherrypick_list.md` (verified 2026-08-06 against the 1.5 tree) is
still accurate for 1.6.** Nothing in that shopping list has gone stale; the
question is only whether we still need to *port* rather than *load* it.

⚠️ **This trap has now caught two independent passes.** A census run
2026-08-12 re-derived the "1.4/1.5 only… a port job, not an install job"
verdict — because it read the same `vendor/mod_sources/Outer-Rim-Galactic-Empire-main`
extract. The stale artifact is more convincing than the truth because it is
local, complete and file-backed. **Delete or clearly mark those extracts once W1
settles**, or a third pass will reach the same wrong answer.

**Consequence — this is the expensive part.** `design/Jawa/mods/outer_rim_cherrypick_list.md`
is a 91-line hand-port plan whose stated top priority (`:90`) is *"Empire trooper
ladder + blasters + apparel + training hediffs (biggest payoff, zero code)"*.
That plan exists **only because we believed the module was unloadable**. If the
Workshop build is 1.6-native, most of that port is unnecessary work.

> ⚠️ **Not yet proven:** GitHub `1.6` branch ≠ Steam-published Workshop build.
> The authoritative test is the one Core already passes — subscribe, then read
> `294100/2919248699/About/About.xml` on disk. Do that before deleting any part
> of the cherry-pick list.

**Generalises to:** never read `supportedVersions` off a GitHub `main` branch or
a `*-main` zip. Multi-version RimWorld mods branch per game version. Check the
Workshop copy, or the branch matching the version you want.

### 3.1 The mod — verified, do not re-derive

**Outer Rim — Galactic Empire**, Workshop `2919248699`,
packageId `Neronix17.OuterRim.GalacticEmpire`.
Sole dependency `Neronix17.OuterRim.Core` (WS `2919227155`) — **already on disk
and active**, and Core's own `OskarPotocki.VanillaFactionsExpanded.Core`
dependency is met (`ModsConfig.xml` line 24, lowercase).

It ships exactly what was asked for. Read off the `1.6` branch:

- **Stormtroopers** — `Imp_StormtrooperCuirass` / `Helmet` / `Pauldrons` / `Kama`;
  `PawnKinds_Stormtroopers.xml`
- **Black-uniformed officers** — **`Imp_OfficerUniform_Black.xml`**, plus
  `_White` and `_Base`
- ISB agents, Death Troopers, Scout / Range / Snowtroopers, Army
  cuirass/helmet/pauldrons/uniform, cadet uniform, gunner helmet, jetpack
- `FactionDefs`, `TraderKindDefs`, `Scenarios`, and an `Assemblies/` folder

**It carries a C# assembly** — `1.6/Assemblies/OuterRimGalacticEmpire.dll`, and
it is **10,752 bytes**: a small Harmony patch, not a system. (The multi-megabyte
`0Harmony.dll` copies in the tree are NuGet build artefacts under
`1.6/Source/.../packages/`, not loaded content.)

✅ **SOLO-LOAD REQUIREMENT WAIVED — owner's ruling, 2026-08-12.** `CLAUDE.md`'s
standing rule is that a new C# assembly rides a game load alone. The owner has
released this module from it, so **the Empire may batch** with the Rebel Alliance
and WORLD's verification queue.

Why the risk is acceptable here, recorded so the waiver is not read as
carelessness: the assembly is tiny, the pre-load baseline is clean and *measured*
(0 dead mods, 0 Scribe errors, 25 cross-references against a 28 baseline —
`AGENT_OPS_state.md`, named `AGENT_WORLD_state.md` when this was written), and a
faction mod that misbehaves usually fails loudly
and names itself in the log. The cost of a wrong guess is attribution effort, not
a lost colony.

⚠️ **What the waiver does NOT change:** harvest the *whole* log after the load,
per `agents_def.md` rule 8. Batching raises the value of a full harvest, because
the log is now the only thing that separates several changes.

⚠️ **Do NOT also load "Star Wars – Factions (Continued)" (WS 3544900066)** — it
ships its own Galactic Empire and would collide (`required_mods.md:685`).

**Dead end, checked so nobody re-checks it:** Outer Rim Core ships
`1.6/Mods/OuterRimAlienFactions/` containing `Faction_JawaSalvagers.xml` and
`Faction_TuskenRaiders.xml`. All four files are **58-byte empty stubs**, and the
folder is **not referenced in `LoadFolders.xml` in any version block**. It is
gutted content, not a donor and not a shortcut.

### 3.2 The two-Empire design — the owner's aristocracy idea IS the missing reconciliation

The fusion is already **LOCKED** (`cherry_picker_killlist.md:81`,
`required_mods.md:682-687`, `setup_checklist.md:101-103`): the vanilla Royalty
Empire is the **aristocratic core**, Outer Rim is the **military arm**, both
stay, neither is Cherry-Picked out.

But two locked docs have been in unnoticed conflict:

| doc | Imperial settlements |
|---|---|
| `faction_roster_v2.md:270` | **10** |
| `desert_world_design.md:485` | *"perhaps one or two"* on the surface, the rest **orbital** |

**The owner's proposal resolves it, and should be adopted as the reconciliation:**

> The Royalty Empire is the **local aristocracy** — a Sector Directorate seat of
> **2–3 surface settlements clustered near the large spaceport**. The remaining
> ~7–8 Imperial holdings are orbital. Ten total, one to two *reachable*.

Why this is the right answer rather than merely a compatible one:

1. **It gives the orbital leash a face.** `desert_world_design.md:489` makes the
   orbital-detection timer the primary pursuit engine but leaves it faceless. A
   landed aristocracy is who the timer *reports to* — the Moff-analog at
   `faction_roster_v2.md:2316` who "never lands" gains a household that does.
2. **It separates the two Empires by verb, not just by mod.** The aristocracy is
   who you *bribe, serve, trade with and are taxed by*; the military is who
   *hunts you*. That preserves pillar 5 — one permanent enemy — because the
   permanent enemy is the Outer Rim military faction, while Royalty stays the
   quest/trader/techprint hook the docs insist on keeping.
3. **It keeps Royalty non-progression for the player** (`forbidden_mods.md:86`).
   Titles reskin to Moff/Governor/Grand Moff as *labels on NPCs*.
4. **It makes the spaceport a place with a meaning** — the one tile where the
   Empire is a neighbour rather than a countdown.

### 3.3 Jobs — tagged, in dependency order

**`[WORLD]` W1. Subscribe and version-verify.** Subscribe WS `2919248699`, then
read `294100/2919248699/About/About.xml` **on disk** and confirm `1.6` is in
`supportedVersions`. This single check either overturns `required_mods.md:572`
for good or restores it. Mod-list changes are WORLD's alone (rule 7); run
`python src/RimMandrake/Utils/refresh.py` after.

**`[WORLD]` W2. Correct the ruling in place.** Whatever W1 returns, rewrite
`required_mods.md:572-574` to state the branch fact and the verification method,
so the next reader does not repeat the `-main` mistake. Append the lesson to
`skills/rimworld-modding/references/traps.md` — symptom, cause, fix,
"generalises to".

**`[WORLD]` W3. Re-scope the cherry-pick list.** If W1 confirms 1.6, most of
`design/Jawa/mods/outer_rim_cherrypick_list.md` §1 is dead work. Keep §3 (Old Republic Sith
as the Empire's Sith-elite donor) — that lift is still wanted either way.

**`[PROJECT]` P1. ✅ DONE 2026-08-12.** Settlement counts reconciled in both
docs. It did not need the owner's yes after all, because **the reconciliation
changes neither number** — 10 is the fiction total, 2–3 of them surface, ~7–8
orbital, and each doc was describing a different layer without saying so. Both
now say which layer they mean and cross-reference each other.

The part that was *not* just bookkeeping: `faction_roster_v2.md` §2's
**`Target settlements` field drives placement on the planetary world map**, so
leaving it at 10 would have put ten Imperial bases on the ground and inverted
`desert_world_design.md` §4-Orbital outright. **It is now 3.** One question is
left open there and is flagged in place — whether Odyssey's orbital holdings
draw from the same faction settlement pool; if they do, the field may want 10
with the *distribution* constrained instead. 3 fails toward the doctrine.

**`[PROJECT]` P2. Decide the Royalty-Empire retheme route.** Two candidates,
neither adopted:
- **Outer Rim Imperial Remnant** (WS `2927717195`) — replaces the Royalty Empire
  outright, converts titles to military ranks. **1.6 status UNVERIFIED** — mirrors
  say 1.4, and per 3.0 that evidence class is now suspect. Verify by branch.
- **Star Wars Retheme: VFE — Empire** (WS `3038088559` / `3292633931` per
  `required_mods.md:586`) — needs **VFE-Empire**, which is **not active** here
  (it is on disk at 1.4/1.5/1.6 per `live_mod_inventory.md:820`). Two-mod install.

  Cheapest third option, and probably the right one: **no retheme mod at all** —
  a label-only XML patch renaming Royalty titles to Imperial ranks. Zero
  mechanical cost, zero dependency, and `required_mods.md:686` already calls the
  reskin "pure labels".

**`[WORLD]` W4. The feasibility check the docs already owe.**
`cherry_picker_killlist.md:82` and `required_mods.md:687` both flag it unanswered:
can Royalty noble pawnkinds be given varied alien races, or do their generation
rules block it? Answerable offline from the live def dump. Fallback is already
written down — let varied races appear naturally rather than guaranteeing them.

**`[WORLD]` U1. ✅ MECHANISM FOUND 2026-08-12 — gate lifted, and the design block
with it.** `Faction Control` (`thereallemon.factioncontrol`, active at load
position 11) exposes `factionGrouping: Tight` + a `CenterPoint` ("Center Tile") +
`OverrideFactionMaxCount`, and explicitly covers modded factions. That is
"cluster N settlements near a point". Configured in
`Config/Mod_2882785581_Controller.xml`, **not** in defs — see §0 Stage 1 for the
full read and the stale-settings warning.

**Assigned to WORLD** by PROJECT 2026-08-12: it is a settings change to a live
mod's config, which is the world as it currently plays, not new content.

⚠️ **Do not re-investigate the three original candidates** — Faction Territories
& Vassalage (`3626725895`), Odyssey Landmark defs, hand-placement in the authored
start save. None was the answer; the mod that solved it was not on that list.
Recorded so the dead ends are not re-walked.

**The old "do not design further until the mechanism is established" gate is
lifted.** §3.2 no longer has to degrade to "2–3 surface settlements somewhere".

### 3.35 ✅ SUPERSEDED 2026-08-12 — the fallback is no longer needed; the real mod is live

> ⚠️ **Do not build the KotOR-Sith-gear fallback below.** It was designed around
> a census finding that **no Galactic Empire faction mod was installed at all**.
> That was true when written and is now false: the owner's 2026-08-12
> subscription batch added **`neronix17.outerrim.galacticempire`**, confirmed
> active in the 21:09 def dump (573 mods).
>
> **What is actually live now:** the `OuterRim_GalacticEmpire` faction —
> `settlementGenerationWeight` 0.3, `requiredCountAtGameStart` 1,
> `canMakeRandomly` true, techLevel **Ultra**, and **12 `pawnGroupMakers`** —
> plus **19 Imperial `PawnKindDef`s**, including `OuterRim_ImpStormtrooper` with
> **`_Desert`**, `_Snow` and `_Officer` variants, the Imperial Army ladder
> (Trooper / Officer / Heavy / Commander at 200 combat power),
> `OuterRim_ImperialOfficer` (175), `OuterRim_ImperialKXSecurityDroid`, and
> `OuterRim_Sith` from Galactic Diversity.
>
> The `_Desert` stormtrooper variant is a straight gift for this campaign.
>
> **Kept, not deleted**, because the reasoning is still the right fallback shape
> if the mod is ever dropped — and because it is a clean worked example of
> Rule 0.6: a correct census became a plan, and the plan outlived the census by
> about six hours.

### 3.35 (original) We are NOT blocked — a zero-install fallback already runs

Census 2026-08-12 of all 1,220 Workshop folders: **no Galactic Empire faction
mod is installed at all**, active or otherwise. But **Star Wars KotOR Weapons
and Armor** (`guy762.KotORWeapons`, WS `2938932438`, 1.5/1.6) is **ACTIVE right
now** and ships a complete **Sith Empire** trooper-and-officer ladder:

| role | defNames |
|---|---|
| trooper armour | `guy762_SithArmor_trooper` / `guy762_SithHelmet_trooper`, `_commando` variants |
| **dyeable** trooper | `guy762_SithArmor_colortrooper` / `guy762_SithHelmet_colortrooper`, `_colorcommando` |
| **officer uniform** | `guy762_SithUniform_officer`, `guy762_SithHat_officer`, `_ensign`, `guy762_UniformCap` |

The `color*` variants are dyeable — **that is a black-uniformed officer corps
and a trooper corps with zero new mods**, available on the next load. Also
already active and on-theme: Doors Expanded SW edition (`HeronSWBlastDoor*` —
Star Destroyer corridor kit), `SwLightA/B`, the E-Web (`RN2SWGun_EWeb_MG`,
canonically Imperial crew-served), and `OuterRim_HeavyImperialTurbolaser`.

**Use this as the Act-I stopgap** if W1 comes back negative, or if the C#-carrying
Empire module cannot get a solo load slot soon. It costs one `pawnGroupMakers`
patch, not a mod-list change.

Also active and worth knowing: `M3.Continued.JangoDsoul.StarWars.TSDA` ships
`JDSCIS_CIS_Faction` — **the only Star Wars faction actually live in the stack
today**, and it is the Separatists, not the Empire.

**`[WORLD]` W5. `observed/2026-08-13/live_mod_inventory.md` is stale and it is a ⚙️ GENERATED
file — regenerate, do not hand-edit.** It reports 1,211 installed against a tree
now holding **1,220**, and 562 active against an actual **568**. Its "Star Wars
content (8)" section undercounts badly — missing at least `guy762.MM.KotORCore`,
`mlie.starwarsanimalcollection`, `lumi.swlights`, `Lumi.doorsexpanded`,
`maincrep.eweb`, `Sov.Sith`, `M3.Continued.JangoDsoul.StarWars.TSDA` and all
four Outer Rim modules. `STRUCTURE.md` calls this file the single source of
truth for mod identity, so every downstream claim inherits the drift.

### 3.4 Not in scope, deliberately

Player-side anything. Royalty stays non-progression (`forbidden_mods.md:86`), no
player psycasting (`:62`), and any Imperial gear that out-classes vanilla is
subject to the §19.5 balance pass (`forbidden_mods.md:127`) in the same lift —
the enemy gets better *coordination*, never a better *curve*.

---


## 4. Ingredient verdicts — the 2026-08-12 subscription batch

**Owner subscribed six mods for evaluation, 2026-08-12. Assessed against the
`concept.md` 7-question test and the live 568 stack. Owner ratified the same day.**

| mod | WS | verdict | basis |
|---|---|---|---|
| Outer Rim – Galactic Empire | `2919248699` | ✅ **ADOPT** | 1.6-native (proven, §3.0). Stormtroopers + `Imp_OfficerUniform_Black`. Carries a 10.7 KB C# assembly; **solo-load waived by owner 2026-08-12 — may batch** |
| Outer Rim – Chiss Ascendancy | `2919962538` | ❌ **REJECTED — unsubscribed by owner** | See below |
| Outer Rim – Separatists | `3097604003` | ⚠️ **KEEP DOWNLOADED, NEVER ENABLE** | Redundant with live JDS TSDA |
| Outer Rim – Rebel Alliance | `2919249903` | ✅ **ADOPT FOR GEAR, FACTION SUPPRESSED** | Owner ruling 2026-08-12. Only genuinely new content in the batch. Full rationale + fiction: `desert_world_design.md` §3B(7) |
| LK Mineable Resources OR | `3565716659` | ✅ **ADOPT** | Filed as `desert_world_design.md` §3B(6) |
| Mines 2.0 | `2503894706` | ❌ **REJECT** | Filed as §3B(6) rejection |
| LK Mines 2.0 compat | `3558833789` | ❌ **REJECT** | Falls with Mines 2.0; also unguarded |

### Why Chiss was rejected — the cleanest kill in the batch

1. **It defines ZERO `GeneDef`s.** Not few. None.
2. **Its xenotype is already live three times over**, and the author says so
   himself. Outer Rim **Galactic Diversity** — ACTIVE in our stack — ships
   `OuterRim_Chiss` with a byte-identical gene list, gated in its own
   `LoadFolders.xml`:
   ```xml
   <li IfModNotActive="Neronix17.OuterRim.Csilla">1.6/Mods/ChissXenotype</li>
   ```
   Galactic Diversity carries the Chiss xenotype *specifically so the Chiss
   module is unnecessary*, and stands down only if you enable it. Net gain: zero.
   We also already have `guy762_xenotype_chiss` (Star Wars Xenotypes) and
   `BTD_Chiss`, and BTD's `XenotypeEquivalencies.xml` already lists all three as
   one species.
3. **Weapons don't rescue it.** Two of three are stat-clones of Outer Rim Core
   blasters we already run. The third, `OuterRim_CharricRifle`, is a §19.5
   violation: 27 damage × 2-round burst at range 38 on the **rifle** base
   (`RangedWeapon_Cooldown 1.0`) instead of the sniper base (1.5) — it
   out-DPSes every sniper in Core.
4. It would also fight `bs.xenotypespawncontrol` and BTD's faction-xenotype
   patches over the same `OutlanderFactionBase` xenotype lists.

### Why Separatists is mined, not enabled

`[JDS] StarWars – The Separatist Droid Army` (`m3.continued.jangodsoul.starwars.tsda`)
is **ACTIVE** and already ships `JDSCIS_CIS_Faction`, label "Confederacy of
Independent Systems", with **8 `pawnGroupMakers` against Outer Rim's 4** and 16
droid kinds against 9 — and its droids have work capability. Outer Rim
Separatists adds **zero new droid races**; it is a thin faction wrapper over
Droid Depot races we already have. Enabling it would put a second, differently
authored "Confederacy of Independent Systems" on the same world map.

### ⚠️ The weapon lift is REDUNDANT — do not author it

Owner asked (2026-08-12) for the four Separatist weapons to be lifted as our own
patched content. **Checked before writing: three or four of them already exist,
live, in `[JDS] StarWars - Armory` (`M3.Continued.JangoDsoul.StarWars.BTI`,
ACTIVE at `ModsConfig.xml` line 31).**

| Outer Rim Separatists (inactive) | already live in JDS Armory |
|---|---|
| `OuterRim_E5Blaster` | `JDSA_E-5_Blaster_Rifle` (range 20, 3-burst, cooldown 0.65) — also `JDSA_E-5C_Blaster_Rifle` |
| `OuterRim_E5sSniperRifle` | `JDSA_E-5S_Sniper_Rifle` (range 50, 4-burst, cooldown 2) |
| `OuterRim_RG4DBlaster` | `JDSA_SE-14_Light_Blaster_Pistol` (range 25, 3-burst, cooldown 0.4) — same droid-sidearm role |
| `OuterRim_BXVibroblade` | `JDSA_Vibroblade` (also `_Vibrosword`, `_Vibroaxe`, `_Electrostaff`) |

Authoring copies would add four redundant defs to a stack that already carries
**674 weapons** with ~344 cuts proposed and none made
(`design/Jawa/mods/armoury_keeplist.md:11`). The player would see two E-5 blasters.

**The work that is actually owed instead**, and it is the same effort:

**`[WORLD]` U2. Balance-audit the live JDS droid weapons** rather than duplicating
them. Two smell wrong on sight and need checking against `setting_physics.md`:
`JDSA_E-5S_Sniper_Rifle` fires a **4-round burst** — snipers should not burst —
and `JDSA_E-5_Blaster_Rifle` has **range 20**, shorter than a vanilla assault
rifle, which will make Separatist droids feel limp at exactly the range the
fiction wants them dangerous. Both are one-line `PatchOperationReplace` fixes in
a mod we already load, and they improve content the player will actually meet.

**`[CREATE]` U3. The droid faction we DO want is not in either mod.**
`faction_roster_v2.md` calls for **Free Droid Enclaves** — a *territorial*
threat holding specific tiles, hostile to the Empire because the founders were
abandoned after the Clone Wars. That is not "CIS battle droids still fighting a
dead war". Neither module supplies it. Both mods are **pure XML with zero C#**,
and every droid race we need is installed twice over (Droid Depot + JDS TSDA), so
authoring our own `FactionDef` + thin `PawnKindDef`s is ~200 lines and no assets.
Build it; do not adopt a substitute.

### 4.1 Rebel Alliance — the jobs this creates

**Owner is moving `2919249903` to the next load round (2026-08-12).** It is pure
XML with **zero C#**, so unlike the Galactic Empire module it **batches freely**
and does not need a solo load slot.

**`[WORLD]` W6. Enable the mod and suppress the faction.** Add
`Neronix17.OuterRim.RebelAlliance` to `ModsConfig.xml` (rule 7 — WORLD owns the
mod list), then set its world presence to zero via **Sensible Factions**
(`3531306011`) or **Faction Control** (`2882785581`). Config, not a patch — so
no `PatchOperationRemove` and no dangling `defaultFactionType` references from
its 12 pawnkinds. Run `python src/RimMandrake/Utils/refresh.py` after.

⚠️ **Success is a NEGATIVE observation, so say in advance what proves it.** Per
`agents_def.md` the handoff bar requires naming the evidence up front:
- **Pass:** no Rebel Alliance settlement anywhere on the world map after
  worldgen, AND `OuterRim_A280Blaster` resolves (visible in a dev-mode item
  spawner or a trade stock).
- **Fail, silent:** a Rebel settlement appears → the suppression config did not
  take. This logs nothing. Look at the world map, not the log.

**`[WORLD]` W7. Re-cast the rebel gear onto the scavenger factions** using
**Faction Weapons and Apparel Set** (`3635005747`, already adopted —
`ship_deck_plan.md:201`). Target the **Junker Scrap-Warrens** and the
**Homestead Compact**. This is what converts a suppressed faction into a salvage
layer; without it the gear exists but nobody wears it.

> ⚠️ **W7 pre-flight, checked from disk 2026-08-12 by WORLD while the game
> reloaded. Three of the four premises above are wrong. Nothing is broken — but
> anyone who queued W7 for a load on the strength of that paragraph would have
> arrived with no tool, no target, and no way to do it in XML.**
>
> **1. The named primary tool is NOT installed.** WS `3635005747` — Workshop
> folder **absent** (not subscribed), and no matching packageId in the 573-mod
> active list. **"Already adopted" meant chosen on paper**: the source,
> `design/Jawa/worldbuilding/ship_deck_plan.md:201`, says *"✅ ADOPTED … 1.6 VERIFIED
> (Workshop page fetched)"* — a research verdict dated 2026-08-07 from reading
> the store page. It was never subscribed. The compression of that into "already
> adopted" is what makes the TODO read as ready-to-go.
>
> **2. But W7 is NOT blocked — the documented fallback IS installed.**
> `ship_deck_plan.md:201` names *"Fallback = TotalControl … WS 3063465133"*, and
> that mod is **active right now** as `co.uk.epicguru.factionloadout`
> ("Rimsential – Total Control: Continued", supports 1.6). So W7 runs on plan B
> without subscribing to anything. The same line warns plan B is "more powerful
> but heavier" — that trade is now the default, not a choice.
>
> **3. W7 is not offline-authorable through either tool.** Both are configured
> through an **in-game mod-settings UI**, not XML — so W7 needs the game *up*,
> and it cannot be prepared in advance as a patch. `Config/` currently holds **no
> Total Control config file**, so nothing has been started.
>
> **4. Half the target does not exist as a def.** `OuterRim_MoistureFarmers`
> (Homestead Compact) is real, in Outer Rim Core's `FactionDefs`. **"Junker
> Scrap-Warrens" has no defName anywhere** — it is a design-doc faction
> (`design/Jawa/worldbuilding/faction_roster_v2.md` §12) with no implementation vessel
> recorded. Decide what it maps to before W7 can target it;
> `OuterRim_BinaryStarRaiders` is the only plausible in-mod candidate and
> **nothing on file says it is the Junkers**, so do not assume it.
>
> **There IS an offline XML path, and it is the one to prefer for a small
> change.** `ship_deck_plan.md:201` records the actual engine mechanism:
> `weaponTags` / `apparelTags` on the PawnKindDef, matched against ThingDef tags
> and wealth-gated by the engine. That is patchable in `Jawa_Patches` today, with
> no dependency on either tool and no in-game UI session — appropriate if W7 only
> ever meant "Homestead pawns can carry an A280".
>
> **Also fix `required_mods.md:579`** — the W2 addendum below already flags that
> it carries a stale *"INSPIRATION ONLY (1.4/1.5)"* verdict for Rebel Alliance.
> The mod is 1.6, enabled, and now suppressed; that line is three states behind.

**`[WORLD]` U4. The rare Homestead Jedi now has a reason — wire it.**
`required_mods.md:596` already permits it and `desert_world_design.md` §3B(7)
now supplies the why. What is still unbuilt is the actual low-weight
`pawnGroupMaker` entry on the Moisture-Farmer / Homestead faction, with the
curated light + telekinesis VPE loadout. `OuterRim_MoistureFarmers` is live in
Outer Rim Core, so the vessel exists. Unowned.

**`[WORLD]` W2 addendum.** `required_mods.md:579` carries the same stale
*"INSPIRATION ONLY (1.4/1.5, SRC-AUDITED)"* verdict for Rebel Alliance that
`:572-574` carried for the Empire. It is 1.6. Correct it in the same sweep, and
record the CC BY-NC-ND licence fact there too — *loading* and *patching* are
fine, *copying their defs into our own mod* is a derivative. That distinction
will come up again for Mandalore and Old Republic.

---

## 5. [VISION] V2 Ideology lines — deferred by the owner 2026-08-13

> 🛑 **STOP WORK.** *"Deepening this is a v2 item. Let's get stuff working that's a
> blocker to play first."* Drained out of `NEXT_RELOAD.md` by PROJECT the same day;
> the scoring card below is the whole of what was known, kept so v2 does not
> re-derive it.

**State at deferral: it is NOT failing, it is unverified.** SpeakUp is confirmed
producing glossed Jawaese on screen. `Suppress` is confirmed firing twice with Jawa
initiators onto slaves. The **text of a Suppress entry was never seen** — every
hovered line came back `Chitchat`. The prisoner half cannot fire at all.

**Mechanism verified live in the def dump:** 14/14 Ideology defs carry our rules;
`Suppress` rules sit in `logRulesInitiator` gated `INITIATOR_kind==OuterRim_Jawa` /
`OuterRim_JawaTribal` at **`priority=250`**; `ReduceWill` **InteractionDef** has 24
rules and the `ReduceWill` **PrisonerInteractionModeDef** has **0** — the
disambiguation worked, so the prisoner-mode dropdown is untouched. Source:
`file:///D:/Luke/dev/Rimworld/src/Jawa/JawaVoice/Patches/JawaVoice_Ideology.xml`

### 🔴 The gloss is NOT a discriminator — disproven on screen

Hovering `Keetkeeh tub tub tohti te bataa. (At least the sunlight helps a little.)`
produced the tooltip **"Chitchat — Occurred 3 hours ago."** ⇒ the gloss separates
JawaVoice from **vanilla**, which was never in question, and says **nothing** about
which InteractionDef sourced it. V1 insults, V3 Chitchat and V2 Ideology lines all
render in the same shape. Scoring V2 on the gloss produces a **false pass**.

**Why:** RimWorld does not store the rendered line. `PlayLogEntry_Interaction`
holds `intDef` + participants and the text is generated from the InteractionDef's
rules at **draw** time, by the same rule engine for every interaction.

### ✅ The correct test — find the entry first, then read its text

| tooltip says | text is | verdict |
|---|---|---|
| **`Suppress`** / `ReduceWill` / `EnslaveAttempt` / `ConvertIdeoAttempt` | Jawaese + gloss | ✅ PASS for that half |
| same | plain English narration | ❌ real failure — `priority=250` lost its pool |
| `Chitchat` / `ChattedAboutSomeone` / `SpreadRumors` | either | ⬜ NO INFORMATION — wrong entry, do not score |

**Both halves must be seen; they are different interactions.** PRISONER =
`ReduceWill` (6 lines) / `EnslaveAttempt` (4) / `ConvertIdeoAttempt` (3). SLAVE =
`Suppress` (4) / `SparkSlaveRebellion` (4). Nine further defs carry lines and are
not required, but any sighting is positive evidence. **14 defs, 49 lines.**

### 🔴 Preconditions — their absence looks exactly like failure

1. **A prisoner does NOT generate warden interactions by default.** Measured from
   `New arrivals2.rws`: all prisoners read `<interactionMode>MaintainOnly</interactionMode>`,
   so `ReduceWill` / `EnslaveAttempt` / `ConvertIdeoAttempt` **can never fire** and
   their absence proves nothing. Set the mode to Reduce will / Enslave / Convert
   per prisoner, give a colonist **Warden** work, and note there were **0 prisoner
   beds** on that map.
2. **The slave half is already configured** — exactly 2 pawns read
   `<slaveInteractionMode>Suppress</slaveInteractionMode>`. ⇒ **the two halves fail
   for completely different reasons**: the slave half is a *text* question, the
   prisoner half a *setup* question. Do not report them together.
3. **The initiator must be a Jawa.** A non-Jawa colonist suppressing a slave
   **correctly** produces a vanilla line — a pass for the gate, not a V2 failure.
4. **The game must be UNPAUSED.** SpeakUp fires on ticks; a paused game produces
   silence indistinguishable from a broken patch.

### ⛔ The save can never answer the text — do not try again

`PlayLogEntry_Interaction` serialises **no `<text>` node** — zero across 56 blocks.
It stores `initiator`, `initiatorFaction`, `initiatorIdeo`, `intDef`, `logID`,
`recipient`, `ticksAbs`. **Jawaese is never in the `.rws`**, so grepping for it
returns 0 whether the patch works or not. A save is the right channel for *whether
an interaction fired and who initiated it*, and the wrong channel for *what it
said*. Only the on-screen social log answers the text.

⚠️ **`priority=250` outbids Core's pool, it does not replace it** — vanilla lines
coexisting is expected and is evidence neither way.
