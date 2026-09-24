# WATER_TRUCE_RETRIBUTION_1 — break the truce at the water, the biome fights back

RULED by the owner, typed 2026-09-24, redirecting the shine portfolio's
option 5 (`weeping_stones_shine_options_2026-09-24.md` ⚖️ head, verdict 5,
verbatim there): anyone fighting near the water — raiders attacking the
player included — gets **animal retribution**; *"Don't fight back and the
creatures will fight for you. Unless rimworld can tell 'who started it?' If
they can then it doesn't even need to be 'don't fight back'."*

## ✅ The engine question is ANSWERED (MEASURED, RimSage decompiled source, 2026-09-24)

RimWorld CAN tell who started it, per hit:

- `Verse/DamageInfo.cs:90,114` — every damage event carries `Instigator`
  (Thing) and `InstigatorGuilty` (bool).
- `Bullet.cs:22` and `Verb_MeleeAttackDamage.cs:50` — vanilla sets
  `instigatorGuilty = !(caster is Pawn) || !pawn.Drafted`: an undrafted pawn
  defending itself is NOT guilty.
- `Verse/AI/Group/Trigger_PawnHarmed.cs` — stock trigger filtering
  retaliation by instigator faction (hives/mechs use it today).
- `RimWorld/Faction.cs:749-` — `Notify_MemberTookDamage` already excuses
  `IsMutuallyHostileCrossfire(dinfo)`.
- `Verse/Hediff_Shambler.cs:239-248` — the targeted-retaliation pattern:
  set `mindState.enemyTarget = dinfo.Instigator`, notify nearby kin.

⇒ **"Don't fight back" is NOT required.** Design: retribution keys on the
FIRST GUILTY hit inside the truce radius; that hit's instigator faction
becomes the biome's target. A defender (undrafted, or returning fire after
the aggressor is established) never flips it. Raiders opening fire near a
pool get the wildlife; the player's colony, defending, gets the wildlife ON
ITS SIDE — the owner's *"the creatures will fight for you"*, exactly.

## build shape

- MapComponent listening for damage near pool terrain (the truce-v1
  water-radius machinery this biome already owes per
  `weeping_stones_fauna_roster_2026-09-24.md` row §2f — same radius, one
  system: suppression inward, retribution outward).
- On first guilty hit: nearby wild animals get faction-targeted aggro at the
  instigator's faction (custom mental state or Lord duty — vanilla manhunter
  is everyone-hostile, so a filtered variant is the one new piece; the
  Shambler enemyTarget pattern is the cheap v1).
- Reference the owner's "animal mind control" recall: the psychic animal
  pulser architecture (wild animals weaponized) — ours is biome-baked,
  faction-aimed, water-scoped.
- Letter + mood/flavor so the player reads WHY the animals rose.
- Mod Settings toggle per the biome-kit law.

## bounds

§6 ambush ban intact — retribution is the biome answering violence at sacred
water, not predators hunting there. Truce v1's accepted side effect
(player-tamed predators don't hunt near pools) is unchanged.
