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
  throws. ⇒ the RSW layer may later give `guy762_GrenadeDamage_sonic` a small force (§3, Q4), not more.
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
   | `maxCellsBonus` | 0 | added to the global "Maximum throw distance" for this blast (so lowering the global lowers every weapon together) |
   | `pushAlongShot` | false | throw direction = shooter→impact (or the trap's facing, §2.3) instead of centre→thing |
   | `impactFactor` | 1.0 | scales wall/pawn impact damage for this blast |
2. **Lookup order**, first hit wins: the explosion's **projectile ThingDef** → its **weapon ThingDef** → its
   **DamageDef** → `unpatchedHarmfulPercent`. The prefix already early-exits on force 0; it now reads
   `explosion.projectile`/`explosion.weapon` first (two `GetModExtension` calls per thing reached — negligible).
3. `KbSettings` is built **per request** (global settings + the extension's bonus), so the pure kernel stays
   Verse-free and its selftests extend with one row per field.

### 2.2 The value
Patch `Thump` (DamageDef — so the Odyssey unique thump cannon variant inherits it with no second patch):
**`force 2.5`, `maxCellsBonus 2`**. Kernel results (human 70 kg; 250 kg = a heavy, still under the 2.5
body-size immunity):

| blast | radius | force | cap | human at d 0 / 1 / 1.4 / 2 | 10 kg item at d 1 |
|---|---|---|---|---|---|
| mortar (Bomb, today) | 2.9 | 1.0 | 6 | 4 / **3** / 2 / 1 | 5 |
| thump cannon (today) | 1.9 | 0 | 6 | 0 / 0 / 0 / 0 | 0 |
| **thump cannon (proposed)** | 1.9 | 2.5 | 8 | 8 / **5** / 3 / 0 | 8 |

A thump bomb (9 dmg) beside a colonist throws it **5** cells against the mortar shell's **3** (50 dmg) — the
owner's "farther". The small radius keeps it a **precision** throw: one target and its neighbour, not a crowd.
Alternatives in Q1.

### 2.3 What else this enables
`pushAlongShot` makes the "shove" weapons in §3 push targets **away from the shooter**, which is what a player
reads as a kinetic hit; radial throw from an impact point *behind* the target would pull it toward the
shooter. For a trap, the trap's own class supplies the direction (its `Rotation`), via one public entry point
`RM_KnockbackAPI.Blast(map, centre, radius, force, Vector3? dir, instigator, KbOverrides)` that enqueues the
same requests the explosion hook does. Cones use the engine's own `affectedAngle` (§1).

## 3. The weapon range

Tier: **RimMandrake** (`RM_`), franchise-free — every name below is invented or plain English (CLAUDE.md Q11a).
Faction assignment to campaign (Jawa/RUT) factions is a **Utinni-layer patch** (`RUT_` weaponTags), never in
the RM mod. Proposed home: a new mod **`mandrake.rm.kineticarms`** ("RimMandrake: Kinetic Arms"), hard-
depending on Explosive Knockback (Q2). One shared new DamageDef family:

- **`RM_Concussive`** — `DamageWorker_AddInjury`, hediff `Bruise`, `armorCategory Blunt`, `isExplosive`,
  `harmsHealth true`, `buildingDamageFactor 0.25` (a kinetic blast barely scratches walls, tanks or doors — the
  niche vs frag), `plantDamageFactor 0.2`, `explosionCellFleck` a pale ring, own `soundExplosion`
  (`RM_Explosion_KineticThud`). Extension `force 2.0`.
- **`RM_Repulse`** — as above but `harmsHealth false` and `defaultDamage 1` (zero wound; the throw and the
  impact are the damage). Extension `force 2.5`. Used where the weapon must be non-lethal.

Every weapon below sets its own extension on its **projectile** ThingDef; the DamageDef value is the fallback.

| # | defName (weapon / projectile) | label | role | radius | force / cap | human d0/d1 | blast dmg | tech · research | cost (craft) |
|---|---|---|---|---|---|---|---|---|---|
| — | `Gun_ThumpCannon` (vanilla, patch only) | thump cannon | breach + precision throw | 1.9 | 2.5 / 8 | 8 / 5 | 9 Thump | Spacer · not craftable | — |
| 1 | `RM_Weapon_ThudderGrenade` / `RM_Proj_ThudderGrenade` | thudder grenade | thrown crowd-breaker; clears a doorway, tips raiders off a lip | 2.4 | 2.0 / 6 | 6 / 5 | 6 RM_Concussive | Industrial · Machining (as frag) | Steel 20, Chemfuel 40 (×5) |
| 2 | `RM_Gun_PalmThumper` / `RM_Proj_PalmThump` | palm thumper | sidearm: one-target shove at short range | 1.4 | 2.5 / 5 | 5 / 3 | 3 RM_Repulse | Industrial · Gunsmithing | Steel 40, Component 2 |
| 3 | `RM_Gun_SlamLauncher` / `RM_Proj_SlamCharge` | slam launcher | 2-handed launcher; lobbed kinetic charge at range 23.9 | 2.4 | 2.2 / 7 | 7 / 5 | 8 RM_Concussive | Industrial · Mortars | Steel 75, Component 4 (as incendiary launcher) |
| 4 | `RM_Gun_RepulsorRifle` / `RM_Proj_RepulsorBolt` | repulsor rifle | spacer rifle: every hit shoves the target **away from the shooter**; 90° cone | 1.9 | 2.8 / 8, `pushAlongShot` | 8 / 5 | 2 RM_Repulse | Spacer · ChargedShot | Plasteel 50, Component (spacer) 2 |
| 5 | `RM_KickerMine` (Building_Trap subclass `RM_Building_KickerMine`) | kicker mine | rotatable buried trap: launches whoever steps on it **in its facing**; re-arms | 1.5 (180° cone ahead) | 3.0 / 7, facing-directed | 7 / 4 | 0 (Repulse) | Industrial · IEDs | Steel 40, Component 1, Chemfuel 10 per re-arm |
| 6 | `RM_Shell_Thump` / `RM_Bullet_Shell_Thump` | thump shell | mortar shell for the **vanilla mortar**: wide, low-damage throw | 3.9 | 2.2 / 8 | 8 / 7 | 10 RM_Concussive | Industrial · Mortars | Steel 15, Chemfuel 25 |
| 7 | `RM_Turret_PulseCannon` / `RM_Proj_PulseWave` | pulse cannon | powered 2×2 emplacement: slow (cooldown 6 s) cone shove, **no ammo**, 350 W | 2.9 (90° cone) | 2.5 / 8, `pushAlongShot` | 8 / 7 | 2 RM_Repulse | Industrial→Spacer · HeavyTurrets | Steel 200, Component 6, Plasteel 40 |
| 8 | `RM_Gun_GravRam` / `RM_Proj_GravRamPulse` | grav-ram | gravitic two-hander: the strongest throw in the game, moves body size up to 3.5 | 2.9 | 4.0 / 10, `immuneBodySizeOverride 3.5` | 10 / 10 | 4 RM_Repulse | Ultra · AdvancedGravtech (Odyssey; every DLC assumed) | Plasteel 90, Component (spacer) 4, Gravlite panel 2 |

Distances are the kernel's for a 70 kg human; heavier is shorter (`massScale`), light items fly to the cap.

### 3.1 Per weapon — role, throw vs damage, fun
1. **Thudder grenade.** The frag grenade's twin: same throw arc and cost class, a fifth of the wound, double the
   throw. It is the answer to "they are bunched in the doorway". With 6 blast damage a colonist can throw it at
   a melee scrum with a friend inside and only bruise him. **Pits:** a raider line on a pit lip goes in.
   **FlowWorks liquids:** tip pawns into burning tar or a liquid-filled pit (`RM_PitDrowning`). Low building
   factor: safe to use beside your own liquid tanks and pumps.
2. **Palm thumper.** A short-barrel (range 12.9) pistol whose bolt pops a 1.4-radius blast. One target, 3–5
   cells. Pure control: shove a charging melee pawn back two seconds of distance, or off a ladder lip.
   Non-lethal (`RM_Repulse`): the "arrest" weapon for prisoners-to-be.
3. **Slam launcher.** Incendiary-launcher shape and cost. Mid-range crowd throw; 1 shot then 4 s cooldown.
   Reaches the raid's second rank where the grenade cannot.
4. **Repulsor rifle.** Every hit shoves along the shot line, so a firing line of repulsors pushes an assault
   **back** step by step — a moving wall. A cone (`affectedAngle` ±45° around the shot) so it does not throw
   things behind the target toward the shooter. Paired with a pit in front of your line it is a killing
   machine without killing.
5. **Kicker mine.** Rotatable on placement (shows its throw arrow). Lay it at a pit lip facing the pit: an
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
  empire — repulsor rifle, grav-ram on janissaries (rare). Mechanoids: none (Q5).
- **Campaign factions (Utinni patches, `RUT_` weaponTags — Q6):** Junkers — thudder grenades, slam launchers
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
- **Stun-lock guard.** A thrown pawn lands with a 60–120 tick stun; a repulsor line firing every 1.5 s could
  chain. Each pawn gets a **throw immunity window** after landing (default 90 ticks): a blast in that window
  staggers but does not throw. Kernel-testable.
- **Shields — a gap today.** Vanilla `CompShield.PostPreApplyDamage` (RimSage) absorbs any `isRanged` **or
  `isExplosive`** damage, so a shield belt eats the blast's wound — but Explosive Knockback throws every thing
  the wave *reaches* (its design rejected `requiresWound`), so **a shielded pawn is still thrown**. Proposed:
  an active `CompShield` on the pawn absorbs the throw too (costs shield energy = force × 10), so a shield belt
  is the counter to the whole class. Needs a knockback change; Q7.
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
| Throw immunity after landing (ticks) | 90 | 0 = chain throws allowed |
| Kicker mines re-arm | on | off = single use |
| Kicker mines hidden from enemies | on | as IEDs |
| Pulse cannon power draw (W) | 350 | |
| Enemies carry kinetic weapons | on | off removes the weaponTags from vanilla and campaign kinds |
| Kinetic blasts cut aerial cords | off (Q3) | needs GSS to read a flag (§3.3) |
Nothing here affects worldgen.

## 5. Validation — runner scenes per weapon

A `Suite` in the new mod's `validation.py`, a walk at `design/validation_walks/RimMandrake/KineticArms.md`,
reusing **knockback_runner.py**'s scene harness (scratch quicktest map, explosion/projectile fired from C#,
JSONL journal, verdict re-derived from the file). Every scene fires the **real projectile** from a real pawn
holding the weapon (`Verb.TryStartCastOn`), never a synthetic `DoExplosion`, so the per-projectile extension
lookup is what is tested.
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
| immunity_window | two hits 30 ticks apart | second hit: staggered, journal "immune", not thrown |
| kicker_facing ×4 | mine in each rotation | thrown in the mine's facing, all four |
| kicker_pit_gate | mine at a pit lip facing it | descent +1 |
| kicker_rearm | trigger, re-arm job, trigger | two throws; 10 chemfuel consumed |
| thump_shell_stockpile | shell on a stockpile | item moves ≤ caps; ms/tick under knockback's budget |
| pulse_cone | turret, targets in and outside its 90° cone | inside thrown away from turret; outside untouched |
| pulse_tank_yard | pulse fires beside a FlowWorks liquid tank | tank HP loss ≤ 5% |
| gravram_centipede | centipede (body 3.0) beside a pit | thrown; descent +1; megasloth (4.0) not thrown |
| shield_counter | shield-belted target, repulsor (after Q7) | not thrown; shield energy down by force × 10 |
| hose_drop | colonist carrying a GSS hose end, repulsor hit | hose end on the takeoff cell, state Dropped |
| settings_each_off | each weapon toggle off | recipe gone; no pawnkind spawns it |
| faction_tags | generate 50 pirate grenadiers | some carry thudders; none when "enemies carry" off |
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

## 7. GPT evaluation — accept/reject

(pending)

## 8. Questions for the owner

(pending)
