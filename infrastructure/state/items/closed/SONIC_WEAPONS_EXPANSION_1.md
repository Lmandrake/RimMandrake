## spec
Owner ruling, 2026-09-01 (question card): asked to creatively expand the Sonic
weapon school, picked **all three** offered directions — new weapon shapes, a
new signature mechanic, and more tiers of the existing archetypes. Canon:
`ownership_fabric`-adjacent sitting note in `infrastructure/state/canon.yml`
("SONIC school KEPT as its own thin Armory school... creatively EXPAND it
later with more sonic weaponry") — that "thin" framing is now STALE and this
item corrects it before building: `WEAPONS_ABSORPTION_WAVE_1` already pulled
in 10 named single-target weapons (`guy762_sonpistol`/`guy762_sonrifle` and
8 faction/quality variants of each) from guy762's KotOR content, all sharing
one `DamageDef` (`guy762_RangedDamage_sonic` — 0 armor penetration,
`harmAllLayersUntilOutside`, stacks `guy762_SonicDisorient` — sonic already
partially bypasses armor and disorients by design) and one research gate
(`guy762_ResearchKotOR_sonic`).

**Also already done, verified before filing this spec — do not rebuild**: a
sonic grenade exists (`guy762_grenadebelt_sonic`, an equippable belt firing
`guy762_ThrownGrenade_sonic` via `Verb_LaunchProjectileStatic`, its own
`guy762_GrenadeDamage_sonic` explosive DamageDef, art already present at
`Weapons/Projectiles/Grenades/grenade_sonic`). "New weapon shapes" therefore
means something NOT already covered by pistol/rifle/grenade.

Faction grounding: `design/Jawa/worldbuilding/faction_equipment_guidance.md` —
the Geonosian Foundry Hive is sonic's owning faction: "industrial manufacturer,
rich in materiel poor in everything else, sonic weapons, and droids doing the
dying. They do not spend on their own [defense]." Cost bands (ruled,
`canon.yml` `research_tree`): T0≤600, T1 600–1600, T2 1600–3000, T3 3000–5000,
T4 5000+.

**Distinctness from Jawa Ion weapons** (checked, do not collide): Ion
(`src/RimStarWars/JawaIonWeapons/`) is a NON-LETHAL capture weapon — buildup
hediff, never deals injury, works identically on flesh and mechanoid. Sonic is
the opposite: a LETHAL injury weapon (`Bruise`/`Crack`, real damage) whose
side effect is crowd disorientation. Do not give sonic an ion-style
non-lethal-buildup mechanic; that niche is already owned.

Scope for this pass — two new pieces, chosen because they cover the one real
gap (no AOE/area content beyond a single hand-thrown grenade) and the one
real gap in single-target tiers (nothing above rifle-class):

1. **New shape + new signature mechanic, combined**: a stationary sonic
   emitter/turret building — `RSW_Sonic_HiveEmitter` or similar. Fits
   "Geonosians... droids doing the dying" (a hive DEFENDS with fixed
   emplacements, doesn't march its own people out) and gives sonic a genuinely
   new gameplay shape: periodic-pulse AOE disorientation over a radius rather
   than a single well-aimed shot. Reuse the existing
   `guy762_SonicDisorient` hediff and, if the delivery shape allows it, the
   existing `guy762_RangedDamage_sonic`/`guy762_GrenadeDamage_sonic`
   DamageDefs rather than inventing a third — only add new C#/a new DamageDef
   if a periodic non-projectile pulse genuinely cannot be expressed with the
   existing ones (check `Building_TurretGun` and existing turret precedent at
   `src/RimStarWars/Armoury/Defs/ThingDefs/Absorbed_OPTurret.xml` and
   `src/RimStarWars/Armoury/Patches/Turrets_DamageDoctrine.xml`/
   `Turrets_Renames.xml` first — this mod already has a turret-doctrine
   pipeline, don't build a second one).
2. **New tier**: `RSW_Sonic_Cannon` or similar — a heavy, two-handed,
   slower-firing single-target tier ABOVE the existing rifle class (the
   existing 10 variants are all pistol- or rifle-shaped; nothing heavier
   exists). Reuse `guy762_RangedDamage_sonic` unchanged. Place in the T2/T3
   cost band per the ruled bands above, gated behind the same
   `guy762_ResearchKotOR_sonic` research (or a follow-on research node if the
   tier genuinely warrants gating past the base school — your call, document
   which).

Use the `RSW_` defName prefix for both new items (new content, not absorbed —
the three-tier naming scheme applies; `guy762_` stays reserved for verbatim-
preserved absorbed defNames per `NAMING_SCHEME_EXECUTION_1`'s migration rule).

Explicitly OUT of this pass: reworking/renaming the 10 existing absorbed
weapons, a sonic mine, any change to the Ion weapon system, any RimUtinni
faction-specific tuning (Geonosian pricing/availability stays in the
Armoury's own generic cost bands for now).

## verify
- `validate_patch.py` clean against the live mod set.
- If any new C# is added (only if the turret genuinely needs it — see above),
  it compiles clean.
- `Def.ConfigErrors()` triage on the next live cold load (grep
  `^Config error in`), same discipline as every other build tonight.
- Live-quicktest-observed: the hive emitter building placed and pulses
  disorientation on a nearby hostile pawn within its radius (screenshot or
  `jawa/list_pawns` hediff check); the sonic cannon spawns, is craftable
  behind its research, and fires using the existing sonic damage chain.

## criteria
A correct v1: one new AOE/area sonic object (the emitter) and one new
single-target tier above rifle-class (the cannon), both reusing the existing
`guy762_SonicDisorient`/`guy762_RangedDamage_sonic` machinery rather than
forking it, both correctly placed in the ruled cost bands, and the false
"thin school" framing corrected in this item's own record so nobody rebuilds
the grenade a second time.
