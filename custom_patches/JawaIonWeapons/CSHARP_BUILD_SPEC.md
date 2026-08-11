# Jawa Ion Weapons — C# build spec

**Status:** TO DO. Authored 2026-08-11 as a handoff for a separate thread.
Nothing in this document has been built yet.

**Why this exists:** the mod's defining mechanic has never once run in game, and
it cannot be made to run from XML. This spells out exactly what is broken, what
was already proven, and what to build — so the implementing thread does not have
to re-derive any of it.

---

## 1. The design intent (unchanged, this is the target)

The Jawa ion blaster is a **capture weapon, not a killing weapon**. Jawa are
weak; they win by patience, numbers and good ground. The gun should:

- **Machines / droids / mechs** — overload almost instantly. One or two hits and
  they are hard-stunned. Very effective.
- **Flesh pawns** — never wounded, never killed. Instead each hit deposits an
  accumulating *ion buildup* that **decays over time**, so isolated potshots fade
  and only focused, stacked fire from several Jawa pushes a target over the edge.
  At the top of the buildup the target **collapses, downed and uninjured** —
  which is exactly the state CPERS: Arrest Here wants for a clean capture.
- It must **never** be able to kill a fleshy target.

That gradient — mechs drop fast, people slowly — is the whole point of the
weapon and the reason it fits the campaign.

---

## 2. What is actually broken

### 2.1 FIXED already (2026-08-11, XML, deployed) — read so you don't redo it

`JawaIon_Damage` used `ParentName="StunBase"`. Core's `StunBase`
(`Data/Core/Defs/DamageDefs/Damages_Stun.xml`) declares **only**:

```xml
<DamageDef Name="StunBase" Abstract="True">
  <harmsHealth>false</harmsHealth>
  <makesBlood>false</makesBlood>
</DamageDef>
```

No `workerClass`, and critically **no `causeStun`**. Vanilla EMP does not stun
because it descends from `StunBase` — it stuns because **EMP itself** sets
`causeStun=true`. We had inherited the "harms nothing" half and none of the
"does something" half, so every bolt landed as a total no-op: no injury, no
blood, no stun, no combat-log line. In game this was reported as *"it never
seems to hit, even when the shooter has 20 in shooting"* — it was hitting every
time and doing literally nothing.

Added to `JawaIon_Damage`, mirroring Core EMP: `causeStun`,
`externalViolenceForMechanoids`, `stunAdaptationTicks`, `impactSoundType`,
`combatLogRules`. **The mech half of the design now works.** Do not revert this.

### 2.2 THE REAL JOB — `additionalHediffs` is inert and cannot be fixed in XML

`DamageDefs_JawaIon.xml` carries:

```xml
<additionalHediffs>
  <li>
    <hediff>JawaIon_Stun</hediff>
    <severityPerDamageDealt>0.03</severityPerDamageDealt>
  </li>
</additionalHediffs>
```

**This has never executed.** `additionalHediffs` is read by
`DamageWorker_AddInjury.ApplyDamageToPart`. A `StunBase`-derived def never
reaches that worker. Confirmation from Core: every single def that uses
`additionalHediffs` is an injury damage, and they all live in
`Damages_MeleeWeapon.xml`.

So the flesh half of the weapon — the buildup, the decay, the live collapse, the
capture pipeline — has never run.

**Why XML cannot fix it.** The two requirements are mutually exclusive under
stock damage workers:

| Route | Buildup applies? | Can it kill a fleshy pawn? |
|---|---|---|
| `StunBase` family (current) | No — never reaches the worker | No |
| `DamageWorker_AddInjury` + tiny damage | Yes | **Yes** — any injury can kill |

There is no stock worker that applies a hediff without dealing an injury. That
is the gap C# closes.

---

## 3. What to build

A small assembly. Two viable designs — **prefer A**.

### Design A (preferred): custom `DamageWorker`

Subclass `DamageWorker` (or `DamageWorker_AddInjury` and suppress the injury)
so that on a successful hit it:

1. Applies / increments `JawaIon_Stun` severity on the pawn by
   `severityPerDamageDealt × damage`, respecting `maxSeverity`.
2. Deals **no** injury and **no** blood to flesh.
3. Leaves mechanoid handling to the existing `causeStun` path — do not
   reimplement EMP.
4. Returns a sensible `DamageResult` so the combat log and hit flecks read as a
   real hit (the "looks like a miss" failure must not come back in a new form).

Wire it up with `<workerClass>JawaIonWeapons.DamageWorker_IonBuildup</workerClass>`
on `JawaIon_Damage`. Keep `harmsHealth=false` and `makesBlood=false`.

Read the severity-per-damage figure **from the existing
`<additionalHediffs>` block** rather than hardcoding, so the XML stays the
tuning surface and the block stops being dead weight.

### Design B (fallback): projectile comp

A `ThingComp` on `JawaIon_Bullet` that applies the hediff in `Impact`. Simpler,
but it bypasses the damage system's own hit/miss resolution and armour, so the
buildup would ignore armour entirely. Only take this if A proves awkward.

### Explicitly out of scope

Do not touch the weapon's balance stats, research, recipe, or the `JawaIon_Stun`
hediff's stages — those are authored and reviewed. This is a mechanism fix.

---

## 4. Build toolchain on this machine

Do **not** go looking for Visual Studio, NuGet CLI, or a .NET Framework
targeting pack. None are installed and none are needed.

- SDK is **user-local**: `C:\Users\Mandrake\.dotnet\dotnet.exe` (8.0.423). It is
  **not on PATH** — invoke by full path. `C:\Program Files\dotnet` is
  runtime-only and will not build.
- `net472` targeting comes from the **`Microsoft.NETFramework.ReferenceAssemblies`**
  NuGet package.
- Reference the game's own DLLs from
  `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed`
  with `<Private>false</Private>` so nothing is copied into the mod folder. That
  folder ships its own `mscorlib.dll` and `netstandard.dll`.
- **Working reference implementation: `mods/dev/RimDefDump/Source/RimDefDump.csproj`.**
  Copy it rather than reconstructing the project file from scratch.

Output goes to `custom_patches/JawaIonWeapons/Assemblies/`, then deploy the whole
mod folder to
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\JawaIonWeapons`.

---

## 5. Project conventions that apply here

- **Deploy and parse-check in one command chain.** Never as separate steps — a
  broken `About.xml` once reached the git remote because the check ran
  separately and failed on its own while the deploy carried on.
- **Resolve every outward reference before shipping.** A `ParentName="EMP"` in
  this very mod silently discarded a def for days, because `ParentName` resolves
  only against **abstract** defs declared with a `Name=` attribute.
- **Never `git add -A`.** Another agent instance works in this tree
  concurrently; stage explicit paths only.
- A cold load is **~23 minutes**. Verify everything possible offline first and
  predict the exact log strings you expect before spending one.
- The mod's `About.xml` name is **"Jawa Ion Weapons (local)"** — no author
  handle, no "Kolyska", packageId `mandrake.jawaionweapons`.

---

## 6. Verification plan

Offline, before any load:

- Assembly builds clean against net472 and loads under the game's Managed refs.
- `JawaIon_Damage`'s `workerClass` resolves to a type that actually exists in the
  built DLL (spell-check it against the compiled type name, not the source).

In game, one load:

- Shoot a **droid** — hard-stunned, drops fast. (This already works; confirm the
  C# change did not regress it.)
- Shoot a **Jawa or other flesh pawn** repeatedly — an *ion buildup* hediff
  appears in the Health tab and its severity climbs with each hit.
- **Stop firing** — severity visibly decays (`-1.2`/day) and the hediff clears.
- **Sustained fire** — the target reaches the top stage and **collapses downed,
  with zero injuries listed**. This is the acceptance test.
- Confirm a flesh target **cannot** be killed by the weapon no matter how long
  you fire.
- Log clean: no `workerClass` resolution error, no NRE from the damage worker.

---

## 7. Nice-to-have, separate from the mechanic

The player reported the weapon's **sound and muzzle effect are underwhelming**.
Currently `soundCast` is Outer Rim's `OuterRim_Shot_DLT19DBlasterBolt` with
`muzzleFlashScale 7`. Purely cosmetic and XML-only — do it after the mechanic
works, not before.
