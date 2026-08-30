<!-- status: live -->
# Droid ruling — ion, capture, and what detonates

_Owner's design ask, 2026-08-12, with everything verified against the live install
and the game assembly. Referenced from `design/V2_DREAMS.md` §1._

**Status: research complete and UNBLOCKED, nothing built.** No XML written, no mod changed. This
doc exists so the build starts from ground truth instead of from a guess.

---

# 🔴 OWNER'S RULING, 2026-08-13 — the three-family question is CLOSED

**This settles the longest-running open question in the droid design. Read this
before anything below it; where the older analysis weighs options, this decides
them.** Nothing below is deleted, because the reasoning is still how the mechanics
work — but the *choices* are made now.

## Per family, decided

| family | downable / capturable | ruling |
|---|---|---|
| **JDS Separatist** (`M3.Continued.JangoDsoul.StarWars.TSDA`) | ❌ neither — **force-killed on downing** | ✅ **CORRECT AS-IS. This is a feature, not a defect.** |
| **KotOR** (`guy762.KotORDroids`) | ✅ both | ✅ **THE capture target. Must NOT detonate on ion.** |
| **Outer Rim Droid Depot** (`Neronix17.OuterRim.DroidDepot`) | ✅ both | unchanged by this ruling; capturable via its **reprogram job** — ⚠️ corrected 2026-08-29: "data spike" was a misnomer; no data-spike mechanic exists in any accepted mod (census: `design/Jawa/droid_census_2026-08-29.md`). The real verb is `JobDriver_ReprogramDroid` (600 ticks on a downed/prisoner droid). "Data spike" survives only as a candidate verb we might author (`DROID_SYSTEM_EMBRACE_1`) |

### JDS droids are never taken alive — and that is the point

> Owner: *"JDS droids are all seriously battle droids, and it's totally ok if they
> blow up when downed and cannot be captured by Jawa. It actually makes sense,
> since they are built for combat and would not want the enemy just reprogramming
> them."*

🔴 **THE RULING HOLDS. THE MECHANISM BELOW IS THE CORRECTED ONE — measured
2026-08-13, merged here 2026-08-20 (closes `design/V2_DREAMS.md` B19).** This
section used to be headed *"JDS droids blow up, and that is the point"*, which read
as a description of the mod. **It is not one.** Measured across all three active
droid mods:

- **`M3.Continued.JangoDsoul.StarWars.TSDA` contains no `deathAction`, no
  `CompExplosive` and no DLL at all.** No JDS droid self-destructs.
- **Exactly one droid in the entire stack self-destructs** —
  `guy762_DroidRace_KX12APD`, the K-X12 assassin probe, via
  `DeathActionWorker_BigExplosion` (`AlienRace_KX12probe.xml:479`). That is a
  KotOR def, not a JDS one.
- **The real mechanism is `fleshType Mechanoid`.** `Pawn_HealthTracker::CheckForStateChange`
  forces `deathOnDownedChance = 1.0` when `IsMechanoid` — see §2. A JDS droid that
  *would* be downed is **killed instead**. Uncapturable by force-kill, not by blast.
- **The wreck is ordinary salvage and the mod ships its own repair recipes**
  (`JDSCIS_ResurrectDroid_Light` / `_Heavy`, 1 corpse + 150 steel) that rebuild it
  into a working droid.

⭐ **The owner's intent survives the correction intact, and gains something.** JDS
droids still cannot be captured and still must not be ion-stunned for capture —
but their wrecks rebuild, so the Jawa fantasy applies to the *corpse* rather than
to the standing chassis. **Nothing has to be removed from the mod to get the ruled
behaviour; it is already the shipped behaviour.**

⚠️ **The explosion tier in §6 is OUR DESIGN, not a claim about this mod.** §6
authors an `explodeOnKilled` tier for energy-dense units. That is additive and
unaffected by the above — do not read §6 as evidence that JDS droids already explode.

⚠️ **So `fleshType Mechanoid` on JDS droids is no longer a GAP — stop filing it as
one.** §4's gap table and §11 treat "JDS cannot be downed" as a problem to solve.
It is not. It is the designed behaviour of a purpose-built combat droid, and the
fiction is better for it.

_Measurement of record: `design/Jawa/worldbuilding/droid_taxonomy.md`._

This also **retroactively vindicates the ion guard shipped on 2026-08-12**, which
used `IsMechanoid` rather than `!IsFlesh` and thereby excluded JDS droids. That was
argued at the time as a technicality about force-kill; it is now the intended
design.

### KotOR droids are the capture-and-upgrade line

> Owner: *"KotOR droids are capturable and have lots of buildable upgrade parts.
> That's AWESOME and totally on brand. They should NOT blow up when ion blasted."*

**This is where the Jawa fiction lives** — down it, spike it, bolt it, repair it,
upgrade it. The buildable upgrade parts are the reason this family carries the
loop rather than Droid Depot.

🔴 **HARD REQUIREMENT: an ion hit on a KotOR droid must leave a recoverable
chassis.** Ion is explicitly the way *around* detonation (§1, §6). A KotOR droid
that detonates on ion destroys the entire capture loop, so that is a **defect of
the highest priority** wherever it is found — not a balance question.

## ⚠️ CONSISTENCY CHECK vs `DroidsAreMachines.xml` — done 2026-08-13, and it HOLDS

The owner asked whether this ruling is consistent with where the droid-flesh
patch landed. **It is** — but only because of the W8 guard change, and checking it
turned up one stale doc and one untested family.

**Verified from the live 573-mod dump (573 active on 2026-08-13, the date of this check), all three flesh types:**

| flesh type | family | `isOrganic` | `IsMechanoid` | our ion | ruling |
|---|---|---|---|---|---|
| `Mechanoid` | JDS | false | **TRUE** | **blocked** | ✅ they scuttle |
| `Asimov_Automaton` | Outer Rim | false | false | applies | ✅ capturable |
| `ABF_FleshType_Synstruct_Base` | KotOR | false | false | applies | ✅ the capture line |

⇒ **`DroidsAreMachines.xml` made all three `isOrganic=false`, so `!IsFlesh` no
longer separates anything.** `IsMechanoid` is the only discriminator left — which
is exactly what the ion guard uses, and exactly what this ruling needs.

🔴 **DO NOT "fix" the ion guard back to `!IsFlesh`.** It would catch all three and
make JDS ion-stunnable, reversing this ruling. The patch header used to imply that
was desirable; corrected 2026-08-13.

**The patch is still right for its own purpose.** `isOrganic=false` is what makes
droids *repaired rather than tended* — the Jawa fiction the owner re-affirmed for
KotOR. It was never the ion mechanism, after W8.

## ✅✅ KotOR ION TEST — PASSED, MEASURED LIVE 2026-08-13 ~08:4x

**The gap below is CLOSED.** Owner directed the test; run on the live 573-mod
stack (573 active on 2026-08-13), game paused throughout, five KotOR droids across **both** the `Good` and
`Bad` lines, against the `OuterRim_BattleDroid` control W8 used.

| kind | line | downed | dead | destroyed | damage dealt | still on map |
|---|---|---|---|---|---|---|
| `KotORDroidBad_KM1MD` | Bad | **true** | false | false | 0.0 | **yes** |
| `KotORDroidBad_DevWD_weak` | Bad | **true** | false | false | 0.0 | **yes** |
| `KotORDroidBad_KX12APD` | Bad | **true** | false | false | 0.0 | **yes** |
| `KotORDroidGood_3C` | Good | **true** | false | false | 0.0 | **yes** |
| `KotORDroidGood_R8009` | Good | **true** | false | false | 0.0 | **yes** |
| `OuterRim_BattleDroid` | *control* | **true** | false | false | 0.0 | **yes** |

⇒ **KotOR droids ion-down to a recoverable chassis and do NOT detonate.** The
owner's hard requirement is met, on the family the design depends on.

**`totalDamageDealt` is 0.0 on every row**, which is the same signature W8 found:
the droid goes down by **capacity loss, not injury** — which is precisely what
makes it capturable rather than dead.

✅ **The `CorpsesMechanoid` worry was unfounded.** It was flagged as the plausible
failure — a downed chassis resolving as a corpse instead of a pawn. It does not:
`dead=false`, `destroyed=false`, and every pawn was still in `list_pawns`
afterwards. Recorded as a **negative with its evidence** so nobody re-raises it.

**Live flesh-type read, confirming the static analysis exactly:** all five report
`fleshType=ABF_FleshType_Synstruct_Base`, `isFlesh=false`, `isMechanoid=false` —
so the `IsMechanoid` guard passes them, as designed.

⚠️ **Method note, because it nearly produced a false negative.** My first pass
parsed `jawa/damage`'s response for a `targets` key and got an empty ion list —
**on the control too**. The control is what caught it: a known-good pawn reading
empty means the *query* is wrong, not the game. The key is `results`, and the
decisive fields are `downed`/`dead`/`destroyed`, not a hediff list.
**Always ion a known-good control in the same run.**

⚠️ Also: `jawa/list_pawns` uses **`kind`**, not `kindDef`. Filtering on `kindDef`
returns zero rows and reads exactly like "nothing spawned". Same trap, twice.

**Map left clean** — all six test droids destroyed, verified absent by re-reading
`list_pawns`, game left paused.

---

## ~~🔴 THE GAP THIS RULING CREATES — KotOR has NEVER been ion-tested~~ ✅ CLOSED ABOVE

**W8 tested `OuterRim_BattleDroid` (Asimov) and `JDSCIS_B1_Battle_Droid`
(Mechanoid). It did not test a single KotOR droid.** The ruling just made KotOR
the load-bearing capture line, so **the one family the design now depends on is
the one family never verified under ion.**

Its flesh type is a *third* def, not either of the tested two, and it carries
`CorpsesMechanoid` as its corpse category — which is exactly the kind of detail
that could make a downed chassis resolve as a corpse instead of a prisoner.
**[INFERRED — not measured. That is the point.]**

45 KotOR pawnkinds are installed to test with (`KotORDroidGood_*`,
`KotORDroidBad_*`). ⚠️ **No longer filed anywhere** — `NEXT_RELOAD.md` was
rebuilt from the queue files and carries neither this item nor a retired seat's tag
(that work is now BUILD's). Refile it in `infrastructure/state/queue/BUILD.md` if it
still matters.

## ~~Mechanoids are OFF~~ 🔴 REVERSED — MECHANOIDS ARE ON. They are the Forgotten Arsenal.

> 🔴 **OWNER'S RULING, 2026-08-20, and it is final:** *"Mechanoids are absolutely ON
> and are called the Forgotten Arsenal or the Forsaken Arsenal of the ancient Rakata
> race that built this place. Period."*

**This section used to rule the opposite**, off a 2026-08-13 quote (*"Mechanoids for
now should be turned off in the scenario"*). ⛔ **That is dead, and it had already died
once** — the owner deprecated it on **2026-08-15** (*"We are keeping the mechanoids.
Deprecate any action about turning mechanoids off"*, recorded in
`design/Jawa/worldbuilding/cherrypick_inbox.md`), and this file was never told. It is
now told.

### What the mechanoids ARE

**Faction 13, `FactionDef Mechanoid`, relabelled — `design/Jawa/worldbuilding/FACTION_SPEC.md` §13.**
`hidden`, no settlements, not a polity.

- **The Forgotten Arsenal** (also *the Forsaken Arsenal*) — the campaign's name for
  **self-replicating defensive systems** that never learned the war ended.
  `design/Jawa/worldbuilding/the_forgotten_war.md` R-W1.
- **Built by the Rakata**, the ancient precursor race that made this world.
  Named in v1 in full, owner 2026-08-20 —
  `design/Jawa/worldbuilding/ANCIENTS_AS_RAKATA_SPEC.md`. The sleepers in the vaults
  are Rakatan, and the Utinni is their vessel.
- **They are found buried**, guarding fortified vaults. They have a perimeter, not a
  grudge: approach and they respond, leave and they do not pursue.

⇒ **The droid roster is JDS (enemy, scuttles) + KotOR (capture line) + Droid Depot
+ the Forgotten Arsenal.** Vanilla mechs are not competition for the droid families;
they are a different register entirely — a *what*, not a *who*.

⚠️ **Mechanitor content is a separate question and this ruling does not decide it.**
The owner's objection in 2026-08-13 was to *strange content we'd have to heavily
augment*; keeping the faction does not oblige us to hand the player a mech workforce.
Judge the player-side mechanitor payload on the anti-exponential pillars, as
`design/Jawa/mods/required_mods.md` already does.

### ✅ DECIDED — the EMPIRE pursues. The mechanoids stay for the ancient dangers.

> 🔴 **OWNER, 2026-08-20:** *"Yes, we will use Ruthless Pursuit mod to have the
> Empire pursue the player... but the mechanoids still show up in ancient horrors, so we
> need a mechanism for that."*

**Both halves at once, and they are independent mechanisms — which is why this works.**

| | |
|---|---|
| **who chases the gravship** | the **Empire**, via `Ruthless Faction Pursuit` (WS `3621784437`, owner-adopted 2026-08-13) |
| **who is in the ancient dangers** | the **Forgotten Arsenal** — vanilla `Mechanoid`, faction intact, untouched by the above |

#### The build

1. **Remove the vanilla `PursuingMechanoids` ScenPart** from the scenario. It is
   `canBePlayerAddedRemoved: true`, so this is a scenario edit, not a patch.
2. **Add the `Ruthless Faction Pursuit` part, aimed at the Empire.**
   ⚠️ **Which Empire is NOT settled** — `required_mods.md` says the Galactic Empire, then
   kills `OuterRim_GalacticEmpire` as the wrong vessel (2026-08-20) and says re-check
   vanilla `Empire`. **Read the live def before pointing the part at anything.**
   Eligibility is `displayInFactionSelection && !isPlayer && canStageAttacks &&
   !permanentEnemy`-class filtering via `CommonUtil.ValidFactionDef`; the mod's picker
   iterates `DefDatabase<FactionDef>.AllDefs`.
3. **Do NOT keep both parts.** The Ruthless part *supplements* vanilla rather than
   replacing it — leave `PursuingMechanoids` in and the player is pursued twice.

#### 🔑 The mechanism the owner asked for

⛔ **NOTHING HERE REMOVES THE MECHANOID FACTION. Nobody is proposing that, in any form.**
Owner, 2026-08-20: *"We're not removing Mechanoids."* The only thing removed anywhere in
this section is the vanilla **`PursuingMechanoids` scenario part** — a ScenPart in the
scenario's part list, which is not the faction and has nothing to do with whether
mechanoids exist. **The Forgotten Arsenal is faction 13 and it stays, in full.**

**Ancient dangers need nothing from the pursuit and nothing from the raid roster.** They
are populated by a **predicate over pawn kinds** — `allowInMechClusters`, `isFighter`,
`combatPower` — which is a different mechanism from raids entirely. Measured: **21 of 93
mech kinds are cluster-eligible with zero raid slots**
(`design/Jawa/worldbuilding/data/mech_control_axes.md`).

⇒ **That is the mechanism, and it is already in the engine.** Swapping the pursuer from
the mechanoids to the Empire changes *who chases the gravship* and touches nothing else.
The Arsenal keeps its vaults either way.

⚠️ **One genuine unknown, and it is about the pursuit, not the faction:** how the removal
of the vanilla part interacts with **VGE Chapter 1's transpiler patch** on
`ScenPart_PursuingMechanoids_Tick`, which is live in this stack and patches a method that
will no longer run. From `required_mods.md`, still unchecked.

Mechanism and the decompiled proof:
`file:///D:/Luke/dev/Rimworld/design/Jawa/worldbuilding/gravship_pursuer_mechanism.md`

---

## 1. What the owner asked for

> Ion weaponry should disable **shields, droids, vehicles**, and — very slowly,
> with many shots — **people and similar-or-smaller animals**. They should **stay
> down**, not pause a moment, so they can be captured. Battle droids programmed to
> blow up when disabled is fine. The Jawa are portrayed as **repairing the droids
> they down**, so the downing should read as having harmed them until restored.
>
> Explosions remain about **energy density**: only droids with large shielding
> units, heavy weapons or big batteries detonate **on destruction** — and an ion
> weapon should be the way *around* that.

The last sentence turns out to be the load-bearing one, and the mechanics support
it exactly. See §6.

**One-line summary of the whole doc:** the capture loop exists and has real
targets, but ion currently only *stuns* droids rather than downing them — because
our own `DroidsAreMachines` patch and our own ion worker were built against
opposite assumptions. One line of C# joins them up. See §5 and §11.

---

## 2. The single most important discovery: there are THREE droid families

They behave completely differently, and almost every wrong conclusion in this
project came from treating them as one thing.

| family | mod | flesh type | downable? | capturable? |
|---|---|---|---|---|
| **Outer Rim droids** | Droid Depot `3096501398` | `Asimov_Automaton` | ✅ yes | ✅ data spike → `SetFaction(Player)` |
| **JDS Separatist droids** | `3276499495` | **`Mechanoid`** | ❌ **never** | ❌ nothing touches them |
| **KotOR droids** | `3047371944` on Artificial Beings Framework | `ABF_FleshType_Synstruct_Base` | ✅ yes | ✅ its own surgery suite — **and these are the ones you actually fight, see §7** |

All three are **active**.

**Why the difference is absolute.** Two vanilla properties, both one line of IL:

```
RaceProperties::get_IsMechanoid   ->  FleshType == FleshTypeDefOf.Mechanoid
RaceProperties::get_IsFlesh       ->  FleshType.isOrganic
```

`Pawn_HealthTracker::CheckForStateChange` forces `deathOnDownedChance = 1.0` when
`IsMechanoid` — a mech that *would* be downed is **killed instead**. That is why
vanilla droids can never be captured.

Neither droid flesh type is `Mechanoid`, so `IsMechanoid` is false for both and
**they are downable rather than force-killed.** That part is unconditional.

### ⚠️ But `isOrganic` is OURS, and it is FALSE

Both mods ship their flesh type without declaring `isOrganic`, which would default
to `true` (`FleshTypeDef::.ctor` does `ldc.i4.1; stfld isOrganic`). **We patch it
to false**, in
`file:///D:/Luke/dev/Rimworld/src/Jawa/Jawa_Doctrine/Patches/DroidsAreMachines.xml`.

Confirmed live in the def dump regenerated 2026-08-12 16:14:

| flesh type | isOrganic (live) |
|---|---|
| `Normal` | true |
| `Mechanoid` | false |
| **`Asimov_Automaton`** | **false** ← our patch |
| **`ABF_FleshType_Synstruct_Base`** | **false** ← our patch |

So in the running game **`IsFlesh` is FALSE for every droid we can capture.**
Any reasoning that starts from the mods' shipped XML is wrong; the patch is the
final word. See §11 for why that patch is right and what it costs.

---

## 3. What already works, and the one thing that does not

Most of the ask is already built. The exception is the most important part.

### ✅ SUPERSEDED 2026-08-30, DROIDWORKS_ION_GUARD_1 — this section describes the PRE-FIX guard

The code block and "THAT GUARD" callout below describe `!pawn.RaceProps.IsFlesh`
as the LIVE guard. It is not, and was not when DROIDWORKS_ION_GUARD_1 went to
verify it — `DamageWorker_IonBuildup.cs`'s own history comment dates the real fix
to 2026-08-12, a day before this doc's "CONSISTENCY CHECK... done 2026-08-13, and
it HOLDS" banner (§ below) — this section simply never got updated to match. The
live guard is `pawn.RaceProps.IsMechanoid` (skips true mechanoids only), exactly
what §5 Option A item 1 recommends. Read this section for the WHY, not the WHAT —
`ION_TIERS_MEASURED_LIVE_1` (rimflow, closed 2026-08-29) is the current, live-
measured state of all three tiers.

### 🔴 Ion does NOT down a droid today (historical — see the note above)

`file:///D:/Luke/dev/Rimworld/src/Jawa/JawaIonWeapons/Source/DamageWorker_IonBuildup.cs`

```csharp
if (pawn.RaceProps == null || !pawn.RaceProps.IsFlesh) return;   // line 63
...
float severity = entry.severityFixed > 0f
    ? entry.severityFixed
    : entry.severityPerDamageDealt * dinfo.Amount;
hediff.Severity += severity;
```

**🔴 THAT GUARD IS WHY IT DOES NOT WORK ON DROIDS TODAY.** `IsFlesh` is FALSE for
our droids (§2), so the worker returns immediately and **no buildup is ever
applied to a droid.** The comment beside the guard says why the author did it:

```csharp
// Mechanoids and droids are already handled by causeStun on the def.
```

So the live behaviour is: **ion STUNS a droid briefly and never downs it.** With
`stunAdaptationTicks 2200`, repeated ion fire works progressively *less* well.
That is precisely the "pauses a moment" outcome the owner does not want.

On **flesh** targets the mechanism does work, and works well:

* Severity uses **`dinfo.Amount`** — the incoming damage *value*, not the damage
  dealt. `JawaIon_Damage` is `harmsHealth: false`, so it applies **zero** hit
  points, but `Amount` is still 8. Buildup accrues at `0.03 × 8 = 0.24` per bolt
  regardless of the zeroed damage.
* At severity 0.9 the `overloaded` stage pins `Consciousness` to `setMax 0.10`,
  below the downed threshold — the pawn collapses, alive and undamaged.

**The fix is one line in our own C#** — see §5 Option A. Nothing about the flesh
patch needs reverting.

### Then the data spike takes it

`OuterRim_DataSpike` carries `Comp_TargetableOnDownedDroid`, validating
`pawn.Downed || pawn.IsPrisoner`, and the effect is one line:

```csharp
Pawn.SetFaction(Faction.OfPlayer, pawn);
```

A 600-tick (10 s) job. **No research gate, no skill check, no failure roll.**

### Then the restraint bolt keeps it

`OuterRim_RestraintBolt` — hediff: `Talking setMax 0` (mute), `Manipulation
setMax 0.75` (25% clumsier), `opinionOfOthersFactor 0`, and
`SlaveSuppressionFallRate 0`. A Harmony prefix on `MentalBreakWorker.BreakCanOccur`
returns false while it is fitted. **No mental breaks, no escape, mute, slightly
less capable** — the Owen Lars mechanic, near-exactly.

Two application paths: an item used on **any** droid (600-tick touch job, no
downed check), or the surgery `OuterRim_AttachRestraintBolt`
(`surgerySuccessChanceFactor 99999` — cannot fail, `anesthetize false`,
`isViolation true`). The surgery needs an operable pawn, so on a hostile the
order is **down → spike → bolt**.

### And a dead droid is not final

`OuterRim_DroidReactivationKit` → `ResurrectionUtility.TryResurrect` on a corpse
whose brain part survived, refitting missing limbs as makeshift ones, scaled by
`partsLeft`. **This is the owner's "Jawa repair what they downed" fiction, already
implemented.**

### People and animals

Ion buildup was designed for flesh and works there unchanged. Body size is not
currently a factor — see the gaps.

---

## 4. Verified gaps against the ask

| the ask | status | what is missing |
|---|---|---|
| disable **droids** | 🔴 **stun only** | Ion stuns but never DOWNS a droid: the buildup worker bails on `!IsFlesh`, and our own patch makes droids non-organic. One-line C# fix, §5 |
| **stay down**, not a pause | 🔴 **not for droids** | Flesh targets collapse and stay down (decay `-1.2/day` ⇒ ~1–2 in-game hours). Droids currently only get the brief vanilla stun, with adaptation making repeats worse |
| capture + restraining bolt | ✅ **works today** | Once downed by any means. Conventional damage downs them today; ion will after the fix |
| repair what you downed | ✅ **works today** | Restoration kit. But ion does **no damage**, so nothing needs repairing — the fiction is available, not enforced |
| disable **people** | ✅ **works today** | — |
| **small animals** slower/faster | ❌ | severity is flat per bolt; no `BodySize` scaling |
| disable **shields** | ❌ **verified broken** | `CompShield::PostPreApplyDamage` breaks the shield on `ldsfld DamageDefOf::EMP` — **reference equality against vanilla EMP**. `JawaIon_Damage` descends from `StunBase`, so it is not EMP and never drops a shield |
| disable **vehicles** | ❓ unknown | Vehicle framework not yet inspected |
| **JDS mechanoids** | ❌ | Cannot be downed (die instead), and ion cannot kill them either (`harmsHealth: false` = zero damage). Ion currently does **nothing but briefly stun** them |

---

## 5. The two simple options

Both are small. They are not exclusive — B is a superset — but A is shippable on
its own.

### Option A — "Ion downs it, you carry it home" ✅ recommended

Keep the existing mechanism. Three small changes:

1. ✅ **DONE, verified live** — `IsMechanoid` is already the guard (fixed
   2026-08-12, predating this doc's own 2026-08-13 consistency check; confirmed
   read of the CURRENT source 2026-08-30 by DROIDWORKS_ION_GUARD_1). Downing on
   the Consciousness cap for a non-flesh humanlike is measured live in
   `ION_TIERS_MEASURED_LIVE_1` — the "one step never observed" caveat below is
   closed.
2. ✅ **DONE 2026-08-30, DROIDWORKS_ION_GUARD_1.** `severityPerDay` slowed
   `-1.2` → `-0.3`, plus a floor stage added at `minSeverity 0.5` carrying the
   same `Consciousness setMax 0.10` as the top stage (vanilla's decay comp has
   no floor field to lean on — checked against the live def dump — so a stage
   floor is the XML-only route). `HediffDefs_JawaIonStun.xml` carries the full
   reasoning inline.
3. **Make ion break shields.** `CompShield::PostPreApplyDamage` tests reference
   equality against `DamageDefOf.EMP`, so the cleanest route is to have the ion
   projectile also deliver a small amount of real `EMP` damage.
4. **Scale by body size** so a thrumbo takes many more bolts than a squirrel.

Only item 1 needs a C# rebuild, and it is a one-line deletion. Everything else is
XML and balance.

### Option B — "Ion kills it, you rebuild it"

Give `JawaIon_Damage` real lethality against droids so they die and leave a
corpse, then recover them with the restoration kit.

**Cost:** more fragile and more work. The corpse must survive, its brain part
must survive, and the reactivation degradation is driven by how much of the body
is left — so a droid killed by a burst may come back crippled or not at all. It
also makes ion dangerous to the thing you are trying to capture, which inverts
the point of the weapon.

**Only worth it** if the "it was dead until we fixed it" fiction matters more
than the reliability. Option A can borrow that fiction cheaply by having capture
apply a damaged hediff that the Jawa must tend.

---

## 6. Where the explosions land — the design closes cleanly

The owner's instinct that *"an ion weapon would seem the way around that"* is
exactly right, and the mechanics enforce it for free:

**`explodeOnKilled` fires on `DestroyMode.KillFinalize` — on DEATH. A downed pawn
has not died, so it does not explode.**

That produces the whole design in one sentence:

> **Ion downs it and you keep it. Anything else destroys it, and the energy-dense
> ones take your squad with them.**

So the tiering is:

| droid | comp |
|---|---|
| astromech, protocol, labour | **no comp.** `E = 0`. Falls over, fully salvageable |
| battle droids, standard combat | **no comp**, or a `harmsHealth: false` stun-burst — dramatic, destroys nothing, corpse intact |
| shield-generator units, heavy weapons platforms, reactor/battery units | `explodeOnKilled` with a real damaging blast. **This is the energy-density tier** |

**The owner's ruling, verbatim, 2026-08-12:** *"a wreck has no power, hence it
cannot explode. POWER DENSITY explodes, not the fact it's a machine."*

That is the whole test, and it resolves the SACRED SCRAP tension by construction
rather than by special-casing: a wreck is not exempted from detonation, it simply
fails the test. Attributed carefully because this project has a documented case
of a claim gaining authority purely by being restated.

⚠️ **Two consequences, raised by a retired seat, 2026-08-12:**

* **Read CURRENT power state, not a def-time maximum.** `basePowerConsumption` is
  a property of the def, so an unpowered or switched-off machine would read as a
  bomb. The proxy has to be what the thing is *actually holding or drawing* —
  otherwise a derelict reads identically to a live reactor, which is precisely
  the distinction the rule exists to make.
* **The kludged tier is a detonation candidate, and arguably the worst one.** It
  is live art now and it *runs*, so it passes the power test — and a bodged
  repair is exactly the thing that should fail violently. Restored and wrecked
  tiers sit either side of it: one powered and sound, one dead.

⚠️ **Use `explodeOnKilled`, never `explodeOnDestroyed`.** The latter also fires on
`DestroyMode.Deconstruct`, which would detonate a machine in the face of the
colonist salvaging it — see `design/V2_DREAMS.md` §1.

⚠️ **A damaging blast destroys its own corpse.** Pawns do *not* get the
leavings-protection shield buildings get (`Thing::Destroy` registers it only
`if (spawned)`, and `Pawn::Kill` has already despawned). So a tier-3 droid killed
conventionally leaves nothing — which is precisely the incentive to ion it
instead.

⚠️ **Always set `chanceNeverExplodeFromDamage: 1`** on any death-explosive droid.
Without it a lucky shot detonates it mid-fight via `PostPreApplyDamage`, which
**bypasses `MakeCorpse` entirely** — no corpse at all, and no warning.

---

## 7. ✅ RESOLVED — we DO fight capturable droids, and ion works on them

Settled 2026-08-12 by a full-stack sweep: all 1,227 installed workshop folders
searched offline, then confirmed against the live def dump by joining
FactionDef → pawnGroupMakers → PawnKindDef → race → fleshType across 84 factions
and 1,741 pawnKinds. Every negative below is "searched and absent", not inferred.

### The enemy is the KotOR rogue droid collective — already live

`file:///C:/Program%20Files%20(x86)/Steam/steamapps/workshop/content/294100/3047371944/1.6/Defs/FactionDefs/Factions_RogueDroids.xml`

```xml
<defName>guy762_KotORFaction_RogueDroids</defName>
<label>rogue droid collective</label>
<permanentEnemy>true</permanentEnemy>
<earliestRaidDays>45</earliestRaidDays>
```

Twelve `KotORDroidBad_*` kinds across four group makers (quick raid, battle-droid
rush, sapper, siege). No world-map bases — drop-pod raids and sieges only.
**The faction is already in the current save**, which sits at tick 105, so the
first raid is ~45 days out. That is the whole early game to build this in.

**They are downable — but ion does not down them yet.** Their flesh type is
`ABF_FleshType_Synstruct_Base`, which is **not** `Mechanoid`, so `IsMechanoid` is
false and they are **downed rather than force-killed** by any damage that drops
them. Conventional weapons already capture them today.

⚠️ But our own `DroidsAreMachines` patch sets their `isOrganic` to **false**
(§2), so `IsFlesh` is false and the ion buildup worker skips them. **Ion stuns
them; it does not put them down.** Fixed by §5 Option A item 1.

They also carry `initialWillRange 0.5~2` / `initialResistanceRange 5~10`
(ordinary prisoner recruitment) and `pawnState: Reprogrammable`, which unlocks
the SynCore surgeries — `ABF_Recipe_Synstruct_ReprogramDrone`,
`FormatReprogrammable`, `FormatSapient`, `RemoveProgramming`.

**So the full ion → downed → capture → repair loop has real targets today, with
no config change at all.**

### Bonus: a quest that is the design brief, verbatim

`btd.gbp.shippack.kotor.vge` (3614012898, **active**) ships
`BTD_QuestScript_DroidDistressCall`: a crashed freighter, a hostile rogue-droid
force, and *"if you can defeat the rogue droids, you may salvage the ship's cargo
and the droid will join your colony."* `rootMinPoints 0`, so it can fire from day
one — well before the day-45 raid gate.

### Outer Rim droids are confirmed YOURS ONLY

Zero non-player factions field an `Asimov_Automaton` pawnKind. Droid Depot ships
no FactionDef and no pawnGroupMakers; Outer Rim Core references droids only in
trader kinds. You can **buy** them; nobody fields them against you.

**If you also want Star Wars battle droids as raid fodder** — B1s to ion and
repair — the shopping list is one checkbox:

| mod | WS | deps | gives |
|---|---|---|---|
| **Outer Rim – Separatists** | `3097604003` | Core ✅ + Droid Depot ✅, both already active | `OuterRim_Separatists` faction: B1 ×80, B2 ×25, BX commando ×10, destroyer ×5 — all capturable |
| ~~Outer Rim – Galactic Empire~~ | `2919248699` | — | **skip.** Exactly one droid kind in one group maker |

Two caveats on the Separatists, both real:

1. `permanentEnemyToEveryoneExceptPlayer = true` — they are **not** automatically
   hostile to you. They start at random goodwill and even ship trader kinds. You
   may have to break relations to see raids. The rogue droid collective, by
   contrast, is `permanentEnemy` and never negotiable.
2. `settlementGenerationWeight 0.3` means they want world-map bases, which are
   only placed at **world generation**. The save is at tick 105, so regenerating
   costs essentially nothing — but it is a decision, not a toggle. (`factioncontrol`
   and `factioncustomizer` are both active and can inject a faction into a
   running world instead.)

### Nothing else was missed

Every other mech mod in the stack — `sarg.alphamechs`,
`samael.npcmechsandanimals`, `el.biotechmechrt`, `veltaris.mechanoidskins`, and
JDS TSDA — uses true `Mechanoid` flesh: forced death-on-downed, never capturable.
Across the whole loaded set only three Humanlike families have a non-`Normal`
flesh type: KotOR synstructs (44 defs), Outer Rim automatons (22), and Yautja.

---

## 8. Bugs found in Droid Depot (upstream, not ours)

1. **Do not use a data spike on a corpse.** `Comp_TargetableOnDownedDroid` accepts
   corpses, but `JobDriver_ReprogramDroid` casts the target to `Pawn` — an
   `InvalidCastException`. Reactivate first, spike second.
2. **The restraint bolt's targeting is far too loose.** `Comp_TargetableOnAnyDroid`
   validates `HasModExtension<DefModExtension>()` — the *base* class — matching
   any def with a non-empty `modExtensions` list. It can be aimed at almost any
   pawn in the game. Worth reporting to Neronix17.

---

## 9. Corrections this doc supersedes

Recorded because each was stated confidently and was wrong, and the shape of the
error repeats.

- *"Mechanoids can't be downed, so there is no droid capture — the salvage loop
  runs on corpses."* True of **vanilla mechanoids**; false for the droids this
  campaign actually uses. The engine fact was right; the inference that it
  governed this content was not.
- *"Ion weapons only stun droids."* False. The buildup applies because
  `IsFlesh` is true for `Asimov_Automaton`.
- *"Ion is the safe way to take a droid down."* Right conclusion, wrong reasoning
  at the time — it holds because of the flesh type, not because of EMP.

**Generalises to:** verifying the engine is not verifying the campaign. A rule
read out of `Assembly-CSharp.dll` is a rule about a *class of thing*; whether the
content in front of you belongs to that class is a separate question, and in a
561-mod stack (as-of unknown — an earlier count carried forward into this doc; the same doc measured 573 on 2026-08-13, and canon reads 578 as of 2026-08-20, `infrastructure/state/canon.yml` `modlist`) it usually does not.

---

## 10. Evidence

| claim | source |
|---|---|
| `IsMechanoid` / `IsFlesh` / `isOrganic` default | `file:///D:/Luke/dev/Rimworld/src/RimMandrake/Utils/ilprobe/` — `python3 il.py RaceProperties get_IsFlesh` |
| shields break only on vanilla EMP | `il.py CompShield PostPreApplyDamage`, `IL_001a ldsfld DamageDefOf::EMP` |
| `explodeOnKilled` fires only on `KillFinalize` | `il.py CompExplosive PostDestroy` |
| ion buildup mechanics | `file:///D:/Luke/dev/Rimworld/src/Jawa/JawaIonWeapons/Source/DamageWorker_IonBuildup.cs` |
| data spike / restraint bolt / reactivation | Droid Depot `1.6/Defs/` and `1.6/Source/OuterRimDroids/` under `file:///C:/Program%20Files%20(x86)/Steam/steamapps/workshop/content/294100/3096501398/` |
| droid flesh type | `.../3096501398/1.6/Defs/ThingDefs_Automatons/Humanlike/Droid__BaseHumanoidDroid.xml` |
| JDS droids are true mechanoids | `.../3276499495/1.6/Defs/ThingDefs_Race.xml` |


---

## 11. Was the `DroidsAreMachines` flesh patch the right call?

**Yes — keep it.** It is correct, well-argued and owner-authorised. But it has an
unintended interaction with our own ion worker, and that interaction is exactly
what blocks the design in §1.

### Why it is right

`file:///D:/Luke/dev/Rimworld/src/Jawa/Jawa_Doctrine/Patches/DroidsAreMachines.xml`
sets `isOrganic: false` on `Asimov_Automaton` and `ABF_FleshType_Synstruct_Base`.

Its central claim is **verified**. `StunHandler::CanBeStunnedByDamage`:

```
IL_0072: ldsfld   DamageDefOf::EMP
IL_007f: callvirt RaceProperties::get_IsFlesh
IL_0084: brtrue.s IL_0088        // flesh -> NOT stunnable by EMP
IL_0087: ret                      // stunnable only when NOT flesh
```

**EMP stuns non-flesh pawns only.** Before the patch, 41 of 57 droid races were
organic to the engine, so ion and EMP did nothing to them at all — the Jawa
signature weapon was useless against the enemy it exists to fight. The patch is
what makes ion touch a droid in the first place.

Everything else about it is sound:

* **Two flesh types instead of 41 race defs.** Both frameworks already declare
  their droids as machines in every other respect — `Damage_HitMechanoid`
  effecter, mechanoid wound art, mechanoid corpse category. Only `isOrganic`
  disagreed. Patching the flesh type fixes every race that uses it, including
  ones the mods add later, and keeps each mod's own art.
* **It uses `PatchOperationConditional`** after a documented silent failure with
  `Replace` — correct, because neither mod declares the node at all.
* **Colonists can no longer tend droids**; they are repaired instead. Explicitly
  authorised: *"I don't want to be able to medically TEND droids anyway. They
  should break like machines, and get repaired."*
* **Bonus nobody claimed:** non-organic corpses do not rot, so a downed or
  destroyed droid keeps indefinitely until the Jawa get to it. That quietly
  protects the salvage loop.

### What it costs — the collision

Our own `DamageWorker_IonBuildup` bails on `!IsFlesh`, with the comment
*"Mechanoids and droids are already handled by causeStun on the def."*

The two systems were written against opposite assumptions:

* the **ion worker** assumed droids are non-flesh and therefore covered by stun
* the **flesh patch** made droids non-flesh precisely so stun would cover them

Nobody joined them up, so the *downing* path — the accumulating buildup that
collapses a target — is excluded from droids. Net effect: **ion stuns a droid
briefly and never puts it down**, and `stunAdaptationTicks 2200` makes repeats
progressively weaker.

### The fix, and what NOT to do

**Do not revert the flesh patch.** Setting `isOrganic` back to true would stop
EMP and ion stunning droids entirely, re-enable medical tending, and make droid
corpses rot — undoing a deliberate doctrine ruling to fix a problem that lives
somewhere else.

**Fix the guard instead.** In `DamageWorker_IonBuildup.cs`, drop
`if (!pawn.RaceProps.IsFlesh) return;`, or narrow it to skip only `IsMechanoid`
pawns — JDS droids, which cannot be downed regardless. Then a droid gets both:

* the **vanilla stun** on hit — an immediate interrupt, because it is non-flesh
* the **accumulating buildup** — collapse, downed, capturable

which is a better weapon than either alone, and is what §1 describes.

**Generalises to:** two correct components can compose into a broken system when
each was written against an assumption about the other. Both the patch and the
worker are individually right and individually well-documented; the bug lives in
the seam. When a flag is deliberately flipped project-wide, grep for every reader
of that flag, not just the one you flipped it for.
