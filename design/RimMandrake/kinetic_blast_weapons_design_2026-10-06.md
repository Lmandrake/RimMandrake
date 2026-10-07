# Kinetic blast weapons — design (KINETIC_BLAST_WEAPONS_1)

Status: DRAFT, 2026-10-06, BENCH. Design and art commission only; nothing built. Rides on
**Explosive Knockback** (`src/RimMandrake/ExplosiveKnockback/`, design
`design/RimMandrake/explosive_knockback_design_2026-10-06.md`, live 18/18 PASS).

## 0. Owner's words

Typed into a question card, 2026-10-06 21:40 (item `infrastructure/state/items/KINETIC_BLAST_WEAPONS_1.md`):

> *"Thump cannons throw farther... and I can see a whole class of weaponry to create that create Kinetic
> Blast-type attacks that are unusually cool! We should commission such a range of projective kinetic blasts"*

Two deliverables: (1) the thump cannon throws farther than a mortar of equal damage; (2) a range of projectile
weapons whose main effect is a kinetic blast — a throw, little damage — designed, then their art commissioned.

## 1. What already exists (searched first)

**Finding that changes deliverable (1): the thump cannon throws NOTHING today.** Vanilla's `Gun_ThumpCannon`
(Core `Weapons_Breach.xml`) fires `Bullet_ThumpCannon` (`Projectile_Explosive`, `damageDef Thump`,
`damageAmountBase 9`, `explosionRadius 1.9`). `Thump` is its own DamageDef (Core `Damages_Misc.xml`), not
`Bomb`. Explosive Knockback's `RM_Knockback_DamageDefs.xml` patches only `Bomb` (force 1.0, `BombSuper`
inherits) and zero-forces Flame/EMP/Smoke/Extinguish/ToxGas. `ForceOf()` falls back to
`unpatchedHarmfulPercent` (default **0**) for any other DamageDef ⇒ `Thump` force 0 ⇒ no throw. "Farther"
starts from zero.

**Per-weapon hooks in Explosive Knockback today: none.** The only knob is `RM_KnockbackExtension.force` on a
**DamageDef** (`RM_KnockbackMod.cs`). The kernel `RM_KnockbackMath.ThrowCells` is
`round(baseCells 4 × force × falloff × massScale × global)`, capped by the global `maxThrowCells` (6), with
`refMass 70`. Force on a DamageDef is enough for Thump (only `Bullet_ThumpCannon` uses it in projectile
position — the other hits in installed mods are building damage multipliers), but a weapon range needs
per-projectile tuning and two behaviours the kernel lacks: a per-weapon cap, and a push **along the shot**
instead of radially. §2 adds them.

**Engine (RimSage, decompiled 1.6):** `Explosion` carries `public ThingDef weapon;`, `public ThingDef
projectile;`, `public Thing instigator;` and `public FloatRange? affectedAngle;`. `Projectile_Explosive.Explode`
passes `weapon = equipmentDef`, `projectile = def` and `direction = origin.AngleToFlat(destination)` into
`GenExplosion.DoExplosion`. ⇒ the postfix can read the projectile and weapon ThingDefs at no cost, and a
custom projectile class can pass `affectedAngle` to make a cone.

**Our source.** No kinetic/repulsor/concussion weapon exists. Nearest:
- Absorbed KotOR pack (`src/RimStarWars/Armoury/Defs/Absorbed_KotorCore/`): `guy762_ThrownGrenade_sonic`
  ("sonic grenade", damage `guy762_GrenadeDamage_sonic` "sonic fracturing", r 3, 50 dmg), `..._stun` (vanilla
  `Stun`, r 3.5). Its header says *do NOT deploy until the source pack retires*. They are damage grenades, not
  throws. ⇒ the RSW layer may later give `guy762_GrenadeDamage_sonic` a small force, not more (a later RSW-layer call).
- `ExplosiveGrowth` "burst" knocks DOWN (hediff), does not displace.
- `GimmeSomeSlack` `Patch_GenExplosion_CutSpans` cuts aerial spans for **any** `harmsHealth` explosion with
  damage > 0 inside its radius (`RM_MapComponent_Aerial.Notify_Explosion`). Every kinetic weapon below would cut
  cords unless told otherwise (Q3).

**Installed mods (2,842 About.xml across `…/common/RimWorld/Mods` and `…/workshop/content/294100`, name +
description; sanity probe "gravship" = 108 hits).** Matches on knockback/concuss/repulsor/kinetic/shockwave/
force push/thump/pushback/sonic/gravit: JecsTools (melee/ability knockback hediff — prior art, already cited by
the knockback design), VFE Insectoids 2 ("thump" = its thumper building), Winston Waves ("push back" = waves),
gravit* hits are gravship content. **No installed mod ships a kinetic-blast projectile weapon line.** Not
already built.

## 2. Thump cannon throws farther — the per-weapon multiplier

### 2.1 Mechanism (a small Explosive Knockback change, owed to FOUNDRY)
1. `RM_KnockbackExtension` grows four optional fields (defaults = today's behaviour):
   | field | default | meaning |
   |---|---|---|
   | `force` | 1.0 | as today |
   | `maxCellsOffset` | 0 | signed, added to the global "Maximum throw distance" for this blast, result clamped ≥ 1 (lowering the global lowers every weapon together; the palm thumper uses −1) |
   | `pushAlongShot` | false | throw direction = the projectile's own flight vector `destination − origin`, **captured at impact** (a prefix on `Projectile_Explosive.Explode` stores it in a per-map table keyed by the explosion it spawns; GPT #2) — never the shooter's current position, which may have moved or died. Zero/absent vector → radial |
   | `impactFactor` | 1.0 | scales wall/pawn impact damage for this blast (0 for the palm thumper: an arrest tool) |
   | `immuneBodySizeOverride` | unset | replaces the global immunity size for this blast (grav-ram 3.6, so a 3.5 body is thrown — eligibility is `≥`); ignored when the global throw-animals/mechs toggles are off |
2. **Lookup order**, first hit wins and supplies the **whole** configuration (no field-by-field merge; an explicit `force 0` wins): the explosion's **projectile ThingDef** → its **weapon ThingDef** → its
   **DamageDef** → `unpatchedHarmfulPercent`. The prefix already early-exits on force 0; it now reads
   `explosion.projectile`/`explosion.weapon` first (two `GetModExtension` calls per thing reached — negligible).
3. Prefix and postfix call `ForceOf` once: the prefix resolves the configuration and passes it to the postfix
   in `__state`, and the request snapshots a **per-request** `KbSettings` (global + offsets, never mutating the
   shared one), so the pure kernel stays Verse-free and its selftests extend with one row per field.
4. **What `weapon`/`projectile` hold** (GPT #7): thrown grenade — projectile + grenade item; manned mortar —
   the loaded shell's projectile + the mortar building; turret — projectile + its `turretGunDef`; trap
   `CompExplosive` — usually both null. ⇒ **tune on the projectile**; weapon-level extensions are a fallback only.

### 2.2 The value
Patch `Thump` (DamageDef — so the Odyssey unique thump cannon variant inherits it with no second patch):
**`force 2.5`, `maxCellsOffset +2`**. Kernel results (human 70 kg; 250 kg = a heavy, still under the 2.5
body-size immunity):

| blast | radius | force | cap | human at d 0 / 1 / 1.4 / 2 | 10 kg item at d 1 |
|---|---|---|---|---|---|
| mortar (Bomb, today) | 2.9 | 1.0 | 6 | 4 / **3** / 2 / 1 | 5 |
| thump cannon (today) | 1.9 | 0 | 6 | 0 / 0 / 0 / 0 | 0 |
| **thump cannon (proposed)** | 1.9 | 2.5 | 8 | 8 / **5** / 3 / 0 | 8 |

A thump bomb (9 dmg) beside a colonist throws it **5** cells against the mortar shell's **3** (50 dmg) — the
owner's "farther". The small radius keeps it a **precision** throw: one target and its neighbour, not a crowd.
Honest limit (GPT #9): at distance 2 the thump is outside its 1.9 radius and throws nothing while a mortar
still throws 1 — "farther beside the impact", not "farther everywhere". Damage is not a kernel input, so the
result holds at any damage.
Alternatives in Q1.

### 2.3 What else this enables
`pushAlongShot` makes the "shove" weapons in §3 push targets **away from the shooter**, which is what a player
reads as a kinetic hit; radial throw from an impact point *behind* the target would pull it toward the
shooter. For a trap, the trap's own class supplies the direction (its `Rotation`), via one public entry point
`RM_KnockbackAPI.Blast(map, centre, radius, KbConfig cfg, Vector3? dir, FloatRange? cone, instigator)` that
mints a **unique activation id** (never the trap's thingID — dedupe would eat the second trigger), selects
cells with the shared cone selector below, runs the same eligibility/shield/budget code, and flushes from the
map component's own tick (there is no `Explosion.Tick` to flush it).
**Cones — not the engine's `affectedAngle` as-is.** RimSage: `DamageWorker.ExplosionCellsToHit` with an
`affectedAngle` **skips every cell within 0.5 of the centre** (`if (!(lengthHorizontal > 0.5f)) continue;`), so
the directly hit pawn would get nothing, and angles are signed `atan2(-z, x)` degrees with no wrap handling.
⇒ a custom `RM_Projectile_KineticCone` calls `DoExplosion` **without** `affectedAngle` and passes the cone to
the knockback request instead: the knockback flush drops requests outside the cone (centre cell always
kept, wrap-safe angle test, LOS as the explosion already applied). The damage wave stays circular, which at
1–3 damage is harmless.

## 3. The weapon range

Tier: **RimMandrake** (`RM_`), franchise-free — every name below is invented or plain English (CLAUDE.md Q11a).
Faction assignment to campaign (Jawa/RUT) factions is a **Utinni-layer patch** (`RUT_` weaponTags), never in
the RM mod. Proposed home: a new mod **`mandrake.rm.kineticarms`** ("RimMandrake: Kinetic Arms"), hard-
depending on Explosive Knockback (Q2). One shared new DamageDef family:

- **`RM_Concussive`** — `DamageWorker_AddInjury`, hediff `Bruise`, `armorCategory Blunt`, `isExplosive`,
  `harmsHealth true`, `buildingDamageFactor 0.25` (a kinetic blast barely scratches walls, tanks or doors — the
  niche vs frag), `plantDamageFactor 0.2`, `explosionCellFleck` a pale ring, own `soundExplosion`
  (`RM_Explosion_KineticThud`). Extension `force 2.0`.
- **`RM_Repulse`** — workerClass **`RM_DamageWorker_KineticOnly`** (applies nothing to pawns or things; the
  hook still sees the thing reached). ⚠️ `harmsHealth false` alone would NOT do it: RimSage shows
  `DamageWorker_AddInjury` injures pawns regardless — `harmsHealth` gates only HitPoints things
  (`DamageWorker.cs:123`) (GPT #3). `harmsHealth` stays **true** so enemy AI will still man and siege with it
  (`JobDriver_ManTurret`, `LordToil_Siege` skip non-harming shells) and FlowWorks' cover-break hook sees it.
  Extension `force 2.5`. The throw and its impact are the only damage — **displacement, not non-lethal**: a
  wall impact at 8 cells unspent is up to 32 Blunt, and a pit is a pit.

Every weapon below sets its own extension on its **projectile** ThingDef; the DamageDef value is the fallback.

| # | defName (weapon / projectile) | label | role | radius | force / cap | human d0/d1 | blast dmg | tech · research | cost (craft) |
|---|---|---|---|---|---|---|---|---|---|
| — | `Gun_ThumpCannon` (vanilla, patch only) | thump cannon | breach + precision throw | 1.9 | 2.5 / 8 | 8 / 5 | 9 Thump | Spacer · not craftable | — |
| 1 | `RM_Weapon_ThudderGrenade` / `RM_Proj_ThudderGrenade` | thudder grenade | thrown crowd-breaker; clears a doorway, tips raiders off a lip | 2.4 | 2.0 / 6 | 6 / 5 | 6 RM_Concussive | Industrial · Machining (as frag) | Steel 20, Chemfuel 40 (×5) |
| 2 | `RM_Gun_PalmThumper` / `RM_Proj_PalmThump` | palm thumper | sidearm: one-target shove at short range, `pushAlongShot`, `impactFactor 0` | 1.4 | 2.5 / 5 | 5 / 3 | 0 RM_Repulse | Industrial · Gunsmithing | Steel 40, Component 2 |
| 3 | `RM_Gun_SlamLauncher` / `RM_Proj_SlamCharge` | slam launcher | 2-handed launcher; lobbed kinetic charge at range 23.9 | 2.4 | 2.2 / 7 | 7 / 5 | 8 RM_Concussive | Industrial · Mortars | Steel 75, Component 4 (as incendiary launcher) |
| 4 | `RM_Gun_RepulsorRifle` / `RM_Proj_RepulsorBolt` | repulsor rifle | spacer rifle: every hit shoves the target **away from the shooter**; 90° cone | 1.9 | 2.8 / 8, `pushAlongShot` | 8 / 5 | 2 RM_Repulse | Spacer · ChargedShot | Plasteel 50, Component (spacer) 2 |
| 5 | `RM_KickerMine` (Building_Trap subclass `RM_Building_KickerMine`) | kicker mine | rotatable buried trap: launches whoever steps on it **in its facing**; re-arms | 1.5 (180° cone ahead) | 3.0 / 7, facing-directed | 7 / 4 | 0 (Repulse) | Industrial · IEDs | Steel 40, Component 1, Chemfuel 10 per re-arm |
| 6 | `RM_Shell_Thump` / `RM_Bullet_Shell_Thump` | thump shell | mortar shell for the **vanilla mortar**: wide, low-damage throw | 3.9 | 2.2 / 8 | 8 / 7 | 10 RM_Concussive | Industrial · Mortars | Steel 15, Chemfuel 25 |
| 7 | `RM_Turret_PulseCannon` / `RM_Proj_PulseWave` | pulse cannon | powered 2×2 emplacement: slow (cooldown 6 s) cone shove, **no ammo**, 350 W | 2.9 (90° cone) | 2.5 / 8, `pushAlongShot` | 8 / 7 | 2 RM_Repulse | Industrial→Spacer · HeavyTurrets | Steel 200, Component 6, Plasteel 40 |
| 8 | `RM_Gun_GravRam` / `RM_Proj_GravRamPulse` | grav-ram | gravitic two-hander: the strongest throw in the game, moves body size up to 3.5 | 2.9 | 4.0 / 10, `immuneBodySizeOverride 3.6` | 10 / 10 | 4 RM_Repulse | Ultra · AdvancedGravtech (Odyssey; every DLC assumed) | Plasteel 90, Component (spacer) 4, Gravlite panel 2 |

Distances are the kernel's for a 70 kg human; heavier is shorter (`massScale`), light items fly to the cap.

### 3.1 Per weapon — role, throw vs damage, fun
1. **Thudder grenade.** The frag grenade's twin: same throw arc and cost class, a fifth of the wound, double the
   throw. It is the answer to "they are bunched in the doorway". With 6 blast damage a colonist can throw it at
   a melee scrum with a friend inside and only bruise him. **Pits:** a raider line on a pit lip goes in.
   **FlowWorks liquids:** tip pawns into burning tar or a liquid-filled pit (`RM_PitDrowning`). Low building
   factor: safe to use beside your own liquid tanks and pumps.
2. **Palm thumper.** A short-barrel (range 12.9) pistol whose bolt pops a 1.4-radius blast. One target, 3–5
   cells. Pure control: shove a charging melee pawn back two seconds of distance, or off a ladder lip.
   Wound-free blast and `impactFactor 0`: the "arrest" weapon for prisoners-to-be (a pit is still a pit).
3. **Slam launcher.** Incendiary-launcher shape and cost. Mid-range crowd throw; 1 shot then 4 s cooldown.
   Reaches the raid's second rank where the grenade cannot.
4. **Repulsor rifle.** Every hit shoves along the shot line, so a firing line of repulsors pushes an assault
   **back** step by step — a moving wall. A cone (`affectedAngle` ±45° around the shot) so it does not throw
   things behind the target toward the shooter. Paired with a pit in front of your line it is a killing
   machine without killing.
5. **Kicker mine.** A persistent building with a saved armed/charge state and its own reload job — **not**
   vanilla `Building_Trap` rearm, which destroys and rebuilds (GPT #6). Rotatable on placement (shows its throw arrow). Lay it at a pit lip facing the pit: an
   **ejection gate**. Lay it facing outward at a door: a bouncer. Facing an incline/edge: off the map edge is
   "stop at the edge". Re-arms like a spike trap (re-arm job, 10 chemfuel). Hidden from enemies like IEDs.
   Animals trigger it (vanilla trap rules).
6. **Thump shell.** Uses the existing vanilla mortar; no new emplacement to build. Widest radius (3.9), lowest
   damage per cell: it scatters a raid's formation and its loot. **Stockpile hazard:** a stray shell flings
   light items up to 8 cells (capped by the per-explosion and per-tick item caps).
7. **Pulse cannon.** The defensive anchor: powered, ammo-free, slow. It does not kill; it buys time and feeds
   pits. Manned? No — a turret. Fires at the nearest hostile like a mini-turret but with a long cooldown;
   `pushAlongShot` means it always pushes **away from your wall**.
8. **Grav-ram.** The late-game toy. Moves things the others cannot (body size ≤ 3.5: a centipede at 3.0 —
   measured, Core `MechCentipede` — yes; megasloth and thrumbo at 4.0 no), throws a human 10 cells. Gravlite cost (Odyssey) gates it. Fun: clear a
   gravship deck, punt a centipede into a pit (body size 3.0 < 3.5 — the **only** weapon that pits a centipede).

### 3.2 Who uses them
- **Player:** all eight, by research.
- **Vanilla factions (RM tier, weaponTags):** pirates — thudder grenade (tag `RM_KineticGrenade` added to the
  grenadier kinds' allowed tags by patch) and slam launcher; outlanders — palm thumper, repulsor rifle (rare);
  empire — repulsor rifle, grav-ram on janissaries (rare). Mechanoids: none.
- **Campaign factions (Utinni patches, `RUT_` weaponTags — Q7):** Junkers — thudder grenades, slam launchers
  (scavenger bombers); Wildsteam Clan — kicker mines in their bases, palm thumpers; Hutt Cartel — enforcers with
  repulsor rifles; Geonosian Foundry Hive — pulse cannons as base defences; Free Droid Enclaves — grav-ram
  (rare, raid boss). Base generation places kicker mines and pulse cannons only where `SymbolResolver`s already
  place turrets/traps.
- ⚠️ **Enemy AI and pits:** AI does not aim throws at pits. That is fine and intended: the player is the one
  who builds pits. An AI repulsor line still pushes colonists back off sandbags.

### 3.3 Interactions
**FlowWorks (pits, covers, liquids, doors).** Everything Explosive Knockback already proves holds:
open pit = stop-in-pit + forced descent; a blast breaks a pit cover (FlowWorks Q5); a closed sluice door stops
the throw with impact. New: kinetic DamageDefs' low building factor means a pulse cannon can guard a
liquid-tank yard without rupturing it. Covered pit + kicker mine facing it = a sprung trap the enemy cannot
see twice. **Gimme Some Slack:** a carried hose end drops at the takeoff cell (knockback Q6) — a repulsor hit
makes a raider drop a hose he was stealing; cords: Q3. **Flyers:** never thrown (state-read proof only).
**ExplosiveGrowth / Ninefold / Scarlands** hook explosions and read; unaffected.

## 4. Balance notes and Mod Settings

**Balance rule: throw is bought with damage.** Every kinetic weapon's damage per blast is ≤ 20% of the
nearest vanilla lethal equivalent (frag 50 → thudder 6 … HE shell 50 → thump shell 10). Throw kills only
through what it throws you **into**: walls (impact `4 × cells not travelled`), pits, fire, other pawns. That
makes the class terrain-dependent — strong for a builder, weak in an open field — which is the intended
identity.
- **Stun-lock guard** (revised for GPT #4). A thrown pawn lands with a 60–120 tick stun; a repulsor line could
  chain. No new launch until **the landing stun ends + a recovery window** (default 120 ticks); a hit in that
  window is recorded "immune" and does **not** refresh stagger. The timestamp is saved (`Scribe`) on the map
  component. Pure rule in the kernel (`KbImmunity.CanLaunch(now, landedAt, stunEnd, window)`), selftested.
- **Shields — a gap today.** Vanilla `CompShield.PostPreApplyDamage` (RimSage) absorbs any `isRanged` **or
  `isExplosive`** damage, so a shield belt eats the blast's wound — but Explosive Knockback throws every thing
  the wave *reaches* (its design rejected `requiresWound`), so **a shielded pawn is still thrown**. Proposed:
  if a shield **absorbed this blast's damage** the throw is absorbed too, so a shield belt is the counter to the
  whole class. Absorption is captured **at damage time** (a postfix on `CompShield.PostPreApplyDamage` —
  `CompShield` sits on worn apparel or is built into a pawn, so look it up on both — recording
  (explosion, pawn) when `absorbed` is true), never as "shield still active afterwards", which misses a shield
  that absorbed and broke. One extra energy debit per (blast, pawn) of `force × 10` **damage-equivalent**
  (× the shield's `energyLossPerDamage`), so a strong throw can break the belt; a broken belt throws next time.
  Needs a knockback change; Q4. (GPT #5)
- **Body size.** Immune ≥ 2.5 (global setting) except the grav-ram's 3.5 override — thrumbos, megasloths and
  big mechs remain events.
- **Value.** Market values: thudder 22 ea, palm thumper 260, slam launcher 420, repulsor rifle 900, kicker
  mine 180, thump shell 45, pulse cannon 1100, grav-ram 2400 (vanilla-relative; recheck against `measure`).

**Mod Settings (Kinetic Arms; defaults = shipped):**
| Setting | Default | Notes |
|---|---|---|
| Enable each weapon (8 toggles) | on | off removes its recipe and its pawnkind tag (no spawns); existing items stay |
| Kinetic throw strength | 1.0 | multiplies only this mod's forces, on top of Explosive Knockback's global |
| Thump cannon throws farther | on | off reverts `Thump` to force 0 — (this toggle lives in **Explosive Knockback**, which owns the vanilla patch) |
| Recovery window after a landing stun (ticks) | 120 | 0 = chain throws allowed |
| Kicker mines re-arm | on | off = single use |
| Kicker mines hidden from enemies | on | as IEDs |
| Pulse cannon power draw (W) | 350 | |
| Enemies carry kinetic weapons | on | off removes the weaponTags from vanilla and campaign kinds |
| Kinetic blasts cut aerial cords | off (Q3, recommended) | needs GSS to read a flag (§3.3) |
Nothing here affects worldgen.

## 5. Validation — runner scenes per weapon

A `Suite` in the new mod's `validation.py`, a walk at `design/validation_walks/RimMandrake/KineticArms.md`,
reusing **knockback_runner.py**'s scene harness (scratch quicktest map, explosion/projectile fired from C#,
JSONL journal, verdict re-derived from the file). Every scene fires through the **real delivery route** — a pawn's verb for held weapons and grenades, a
**loaded, manned vanilla mortar** for the thump shell, the **turret's own verb** for the pulse cannon, a pawn
**walking onto** the kicker mine — never a synthetic `DoExplosion`, so the lookup-by-route (§2.1 item 4) is
what is tested. Deterministic geometry scenes force the hit (skip the accuracy roll); a separate accuracy
trial measures real-verb hit rates.
| Scene | Setup | PASS reads |
|---|---|---|
| thump_vs_mortar | colonist 1 cell from a thump-bomb impact; another from an HE mortar shell | thump 5 cells, mortar 3; journal force source = DamageDef `Thump` |
| thump_toggle_off | as above, setting off | thump 0 cells; wave processed it |
| lookup_order | a projectile with its own extension and a DamageDef with another | projectile value wins; journal records the source |
| thudder_doorway | 5 raiders in a doorway, grenade at the door | ≥ 3 thrown ≥ 3 cells; none dead from the blast alone |
| palm_shove | melee pawn 3 cells from shooter | thrown away from shooter, 3–5 cells; no wound from blast |
| slam_range | launcher at 22 cells | lands, throws per kernel |
| repulsor_along_shot | target with a pawn behind it | target thrown along shot line (angle within ±10° of shot); pawn **behind** target not pulled toward shooter |
| repulsor_line_pit | 3 repulsors, assault walking at an open pit | ≥ 1 descent recorded by FlowWorks |
| immunity_window | two hits 30 ticks apart; save/reload between them | second hit: journal "immune", not thrown, stagger not refreshed; timestamp survived the reload |
| direct_hit_cone | repulsor bolt hits its target dead-centre; cone straddling ±180° | the target IS thrown (centre cell kept); wrap-around angle correct |
| shooter_gone | shooter killed / despawned while the bolt flies | throw still along the captured flight vector |
| lookup_fallbacks | projectile ext / weapon-only ext / DamageDef only / none / explicit 0 | each source wins in order; explicit 0 throws nothing |
| kicker_repeat | mine triggered 3× in 10 s | 3 throws (unique activation ids), charge spent per trigger |
| item_conservation | thump shell on stacks beside a pit | total stack count before = after (merges + pit floor) |
| kinetic_he_mix | thudder + frag on one group, same tick | no exception; one launch per pawn |
| kicker_facing ×4 | mine in each rotation | thrown in the mine's facing, all four |
| kicker_pit_gate | mine at a pit lip facing it | descent +1 |
| kicker_rearm | trigger, re-arm job, trigger | two throws; 10 chemfuel consumed |
| thump_shell_stockpile | shell on a stockpile | item moves ≤ caps; ms/tick under knockback's budget |
| pulse_cone | turret, targets in and outside its 90° cone | inside thrown away from turret; outside untouched |
| pulse_tank_yard | pulse fires beside a FlowWorks liquid tank | tank HP loss ≤ 5% |
| gravram_centipede | centipede (body 3.0) beside a pit | thrown; descent +1; megasloth (4.0) not thrown |
| shield_counter | shield-belted target, repulsor (after Q4) | not thrown; shield energy down by force × 10 |
| hose_drop | colonist carrying a GSS hose end, repulsor hit | hose end on the takeoff cell, state Dropped |
| settings_each_off | each weapon toggle off | recipe gone; no pawnkind spawns it |
| faction_tags | read the pawnkinds' resolved allowed weapon tags (deterministic), not random rolls | thudder tag present; absent when "enemies carry" off |
Offline: kernel selftests for `maxCellsBonus`, `pushAlongShot` direction, `impactFactor`, body-size override
and the immunity window, beside the existing K-01…K-n.

## 6. Art list

128 px per cell (`skills/generating-rimworld-sprites/SKILL.md`). Weapons are held items drawn ~1.0–1.4 cells →
**256 px**; projectiles **128 px**; the pulse cannon is a 2×2 turret (top + base) → **512 px**; the kicker mine
1×1 building → **256 px**; UI icons (research tab / command gizmo) **128 px**. Transparent, side view for
held weapons (barrel pointing east, as vanilla), top-down 3/4 for buildings. House register (painterly, no
outlines) is added by `fill_queue.py`.

| job id | subject | canvas | notes |
|---|---|---|---|
| kba_RM_Weapon_ThudderGrenade | thudder grenade (item) | 256 | squat drum-shaped grenade, padded impact ring |
| kba_RM_Proj_ThudderGrenade | thudder grenade in flight | 128 | |
| kba_RM_Gun_PalmThumper | palm thumper | 256 | stubby flared muzzle pistol |
| kba_RM_Proj_PalmThump | palm thump bolt | 128 | pale air-ripple ring |
| kba_RM_Gun_SlamLauncher | slam launcher | 256 | |
| kba_RM_Proj_SlamCharge | slam charge | 128 | |
| kba_RM_Gun_RepulsorRifle | repulsor rifle | 256 | finned emitter muzzle |
| kba_RM_Proj_RepulsorBolt | repulsor bolt | 128 | |
| kba_RM_KickerMine | kicker mine (armed, top-down) | 256 | directional plate with arrow chevron |
| kba_RM_Shell_Thump | thump shell (item) | 256 | |
| kba_RM_Bullet_Shell_Thump | thump shell in flight | 128 | |
| kba_RM_Turret_PulseCannon_Top | pulse cannon top | 512 | |
| kba_RM_Turret_PulseCannon_Base | pulse cannon base | 512 | |
| kba_RM_Proj_PulseWave | pulse wave | 128 | |
| kba_RM_Gun_GravRam | grav-ram | 256 | |
| kba_RM_Proj_GravRamPulse | grav-ram pulse | 128 | |
| kba_icon_* (8) | one UI icon per weapon | 128 | research/gizmo icon |
| kba_RM_Explosion_KineticRing | kinetic blast ring fleck | 128 | pale shock ring, the class's signature |
The thump cannon keeps vanilla art.

**Commissioned 2026-10-06: 25 artpipe jobs, prefix `kba_`** (16 weapon/projectile/building sprites, the ring
fleck, 8 icons), item `KINETIC_BLAST_WEAPONS_1`, priority 40, filed with `fill_queue.py`. Before filing,
`artpipe_state.py` showed no prior job for any of these subjects (none had existed: every def is new).
All eight weapons are commissioned even though Q5 may trim the first build wave.

## 7. GPT evaluation — accept/reject

Full text: `design/RimMandrake/kinetic_blast_weapons_gpt_eval_2026-10-06.md` (gpt-6.1-sol, effort high,
2026-10-06). Its verdict: *"Viable foundation; revise before commissioning the full range."* Two engine claims
were checked in RimSage before acceptance (cone centre skip; `harmsHealth` not gating pawn injury) — both true.

| # | finding | verdict | where it landed |
|---|---|---|---|
| head | "the map-component/flyer implementation is absent, so 18/18 cannot certify" | **Reject the first half** — those files exist (`RM_MapComponent_Knockback.cs`, `RM_PawnFlyerPatches.cs`) and were simply not sent. **Accept the second half:** the old run certifies none of the new fields | §5 scenes |
| 1 | cones skip the centre cell; signed unwrapped angles | **Accept** (RimSage-verified) | §2.3 own cone filter, `direct_hit_cone` scene |
| 2 | `pushAlongShot` must capture the flight vector at impact | **Accept** | §2.1 table |
| 3 | `harmsHealth false` still injures pawns; impact makes Repulse lethal | **Accept** (RimSage-verified) | §3 `RM_DamageWorker_KineticOnly`; "displacement, not non-lethal" |
| 4 | 90-tick window can expire before the stun ends | **Accept** | §4 stun + recovery window, saved |
| 5 | shields: capture absorption at damage time, apparel comp, energy units | **Accept** | §4 shields |
| 6 | trap API: no cone, no flush, dedupe ids, vanilla rearm destroys | **Accept** | §2.3 API, §3.1 kicker mine |
| 7 | `weapon`/`projectile` differ by route; resolve config once | **Accept**; "unique variants may override damage" is **to measure at build** (Odyssey's unique thump cannon) | §2.1 items 2–4 |
| 8 | signed cap offsets; immunity override missing; `≥` at 3.5 | **Accept** | §2.1 `maxCellsOffset`, `immuneBodySizeOverride 3.6` |
| 9 | thump 2.5/+2 is right; promise "farther beside impact" | **Accept** | §2.2 honest limit |
| 10 | balance needs full firing stats, control/s, ammo-free turret farms captures | **Partly accept** — full verb stats are owed at build; pulse cannon pit-farming goes to the owner (Q6). **Reject** cutting throw distances now: numbers are calibrated to his "3 cells" ruling and get tested | §8 Q6 |
| 11 | validation overreach: real routes, centre hits, dead shooters, fallbacks, save/load, item conservation | **Accept** | §5 |
| 12 | cut to grenade, rifle, mine, shell (+thump); merge palm thumper; defer slam, pulse, grav-ram | **Reject as a unilateral cut** — the owner asked to *"commission such a range"*; art for all eight is commissioned. Put to him as Q5 | §8 Q5 |

## 8. Questions for the owner

**Q1 — How far should the thump cannon throw?** (a) **force 2.5: 5 cells beside the impact, 8 at its centre,
nothing 2 cells out** (recommended — precise, clearly beats the mortar's 3); (b) force 3.0: 6 beside, same
reach; (c) also widen its blast to 2.4 so it throws people 2 cells out too — a crowd weapon, but it then
overlaps the thump shell and hits more of your own side.

**Q2 — Where do these weapons live?** (a) **a new mod "Kinetic Arms" that needs Explosive Knockback**
(recommended — a player can take the throwing physics without new guns); (b) inside Explosive Knockback — one
mod, but the physics mod stops being "just physics".

**Q3 — Do kinetic blasts snap Gimme Some Slack's overhead cords?** Today every damaging explosion does.
(a) **no — a push wave sways cords, only real explosions cut them** (recommended; needs a small GSS change);
(b) yes, same as any blast — simplest, but a pulse cannon would keep cutting your own lines.

**Q4 — Do shield belts stop being thrown?** Today a shielded pawn takes no wound but is still thrown.
(a) **yes — the belt absorbs the throw and loses charge; a strong throw can pop it** (recommended — gives the
class a clear counter); (b) no — shields stop damage, never the shove; kinetic weapons become the anti-shield
tool.

**Q5 — How big is the first wave?** GPT argued four of the eight carry the class: (a) **all eight, as
designed** (art for all eight is already queued); (b) GPT's core four — thudder grenade, repulsor rifle, kicker
mine, thump shell — with the palm thumper folded into an early repulsor; slam launcher, pulse cannon and
grav-ram later; (c) the core four plus the grav-ram (the only way to pit a centipede).

**Q6 — The pulse cannon and pits make a capture farm.** An ammo-free turret beside a pit can drop raiders in
all day. (a) **it draws a charge: each shot costs a stored "pulse cell" the turret slowly refills from power**
(recommended — still no ammo hauling, but a big raid drains it); (b) leave it free and powered — a pit-and-pulse
base is the reward for building one; (c) give it ammo like the mortar.

**Q7 — Campaign factions.** Proposed: Junkers throw thudders and carry slam launchers, Wildsteam Clan lays kicker
mines, Hutt Cartel enforcers carry repulsor rifles, the Geonosian Foundry Hive mounts pulse cannons, Free Droid
Enclaves field a rare grav-ram. (a) **as proposed** (recommended); (b) keep kinetic weapons player-only for now —
no enemy ever throws your colonists; (c) a different split you type.

## 9. Owner decisions, 2026-10-06 ~22:30

By question card: Q1 thump cannon **force 2.5** (5 cells beside the impact, 8 at centre); Q2 a **new mod "Kinetic
Arms"** that needs Explosive Knockback; Q3 kinetic blasts **sway** Gimme Some Slack cords, only real explosions cut
them; Q4 shield belts **absorb the throw and lose charge** (a strong throw pops them).

Owner typed (verbatim): *"We need to assign this tech to someone in the game. I'm thinking this might be ancient
Rakatan technology (thump guns)."* — kinetic-blast weapons are framed as ancient Rakatan technology; see
RAKATAN_ARCHOTECH_MACHINES_1 for the existing Rakatan grade ladder. Q5–Q7 asked next in that light.
