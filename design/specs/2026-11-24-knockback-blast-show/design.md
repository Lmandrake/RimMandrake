# Explosive Knockback 0.2.0: the blast show (design study, 2026-11-24)

Item `RIMMANDRAKE_OPEN_KNOCKBACK_ZERO_TWO_BLAST_SHOW_HE_SAID_GET_CREATIVE`. Build item
`RIMMANDRAKE_ABSORB_EXTRA_EXPLOSION_EFFECTS_OWN_FLECKS`. The bars are the nine `blast_show_*` rows of
`design/concepts/ExplosiveKnockback/record.json`. This file designs; it builds nothing and queues no art.

His words, 2026-11-24 (OWNER:1795565769863524396): *"Our own blast show YES. They look horrible right now. Let's drop all
those mods and replace them with SO MUCH BETTER stuff. Screen shake, bright fiery explosions. Air distortion ripples.
Proportional to the damage done. Realistic and wonderful. Smoke that looks like smoke, not rotating cartoon cotton. Ugly
crater scars that look like ugly crater scars. Black soot like Pyrelands (black paint left on things). Soot on affected
pawns. Get a Designer pass on just this aspect itself... let's get creative! How many different game engine aspects can we
couple in so that explosions really feel realistic and impressive and enduring? Get inspiration from other explosion mods
or even web research if you need inspiration."*

Tags: `[measured]` is read from a def, our source, or the RimWorld 1.6 source through RimSage on 2026-11-24.
`[guess ~N%]` is not checked.

## 1. Survey

### 1.1 What draws a blast on our lists today

`ModsConfig.FULL.LATEST.xml` (315 active mods, parsed) holds three explosion-visual mods. The Explosive Knockback small
list and MINIMAL hold none of them [measured]. The full reading of each mod, with its Harmony patches, is in
`design/RimMandrake/explosion_mods_characterized_2026-11-12.md`.

| mod | what it draws [measured from its defs] | what a drop loses |
|---|---|---|
| Extra Explosion Effects (`Keshash.ExtraExplosionEffects`) | Twelve FleckDefs on a postfix of `GenExplosion.DoExplosion`: `Fleck_EEE_ExplosionBlast`, `Fleck_EEE_ShockWave` (shader `MoteLargeDistortionWave`), `Fleck_EEE_RotatingDistortion`, sparks, `Fleck_EEE_DirtBits`, `Fleck_EEE_StoneBits`, `Fleck_EEE_SmokeDarkened` and `Fleck_EEE_Soot` (both the vanilla `Things/Mote/Smoke` puff, tinted), `Fleck_EEE_BombCrater` and `Fleck_EEE_BombCrater_Dirt`. | Nothing that our set does not replace, except its sparks and ripples on Stun blasts (our later set) and its Combat Extended variant (not on our lists). |
| Better Explosions (`nephlite.advexplosions`) | XML only. It points the fleck and colour fields of Bomb, BombSuper, Flame, Extinguish, Smoke, Stun and EMP at its own flecks (`Mote_AdvExplosion1`, `Mote_AdvExplosion2`, `Mote_AdvFlame`, `SubMote_AdvParticle*`) and replaces the texture of the vanilla Smoke fleck. | Its looks for Extinguish, Smoke, Stun and EMP blasts, which return to vanilla. Its Smoke texture, which every smoke source in the game shows. |
| Dynamic Effects Forge (`blues.forge`) | A postfix on `Explosion.StartExplosion` hides the vanilla visuals and plays staged particle sequences (`Bomb`, `Antigrain`, `Elemental` defs; flecks `ForgedSplash`, `ForgedInstaFlash`, `BrightDenseDown`, `BrightSoftUp`). | More than blasts: its projectile trails, its fire flicker and fire smoke changes, its sky palette, and its humidifier building. A colony that built a humidifier loses that building. |

Two facts change the picture. First, the "rotating cartoon cotton" is the vanilla puff: `Things/Mote/Smoke`, which Extra
Explosion Effects tints for both its smoke and its soot [measured], so no kept mod can fix it. Second, RimWorld 1.6 itself
lays a scar: mortar shells spawn `Filth_BlastMark`, a 3 by 3 filth drawn 7 cells wide [measured]. On a list without the
three mods, that vanilla mark is the "crater" a player sees [guess ~70%].

His card of 2026-11-12 kept Better Explosions and Dynamic Effects Forge. His words above replace that card: all three
leave the lists when our show ships. Custom Gas Types is a gas system, not a blast visual, and stays.

### 1.2 How Pyrelands lays black soot

Pyrelands uses the vanilla paint slot, with no new graphic and no comp [measured,
`src/RimMandrake/Pyrelands/Source/FireEcologyHook.cs`, `CharRuinBuilding` and `CharFloor`]:
`Building.ChangePaint(RM_FE_Charred)` on a building and `map.terrainGrid.SetTerrainColor(cell, RM_FE_Charred)` on a built
floor. `RM_FE_Charred` is a ColorDef (58, 52, 49), type Misc, so the colour stays off the player's paint list. The blast
show reuses exactly this: one soot helper in `src/RimMandrake/_Shared`, used by both mods, that resolves `RM_FE_Charred`
and registers the same def in code when Pyrelands is not loaded [guess ~70% that a code-made ColorDef saves and loads
cleanly]. There is no second soot colour and no second soot method.

### 1.3 Other mods and other games

- Extra Explosion Effects' Workshop page says its shockwave needs Royalty for the distortion shader, and that its crater
  draws under its ash. A commenter there notes that 1.6 now leaves shell marks itself. Requests for a quake on/off switch
  recur in its comments: a strength control for the shake is wanted.
- Drop FX (LoggerC4) adds smoke and blast marks to shells in flight and on landing: the show can start before the bang.
- Developers' write-ups on 2D blasts agree on four points: build the blast from several layers with different timing; make
  the flash a large soft additive disc that dies in a few frames; make the fireball swell fast and slow down (ease out);
  let smoke rise with turbulence under a lit top and a dark base. One team's stated hardest problem was keeping the scene
  readable through shake and debris. A studio ducks small sounds under a big blast.
- The trauma model of camera shake (shake follows the square of an accumulated value that decays) keeps many small blasts
  from summing into nausea [from memory, guess ~90%]. Games known for blasts that endure keep the mark: the burnt ground,
  the stain, the hole.

Sources: steamcommunity.com/sharedfiles/filedetails/?id=3066208882 and its changelog and comments;
top-mods.com/mods/rimworld/graphics/6729-better-explosions.html; pcgamer.com/how-great-game-explosions-are-made;
moddb.com/news/explosions-destruction-effects; uhiyama-lab.com/en/notes/godot/gpu-particles2d-effects;
construct.net/en/forum/construct-2/how-do-i-18/good-looking-top-down-view-100802.

## 2. One measure of a blast

Every part reads one number, the blast's **power**: the damage amount of this explosion against the reference damage of
its type, the same ratio that the throw already uses (`RM_KnockbackMath.DamageRatio`), times its area. A blast that throws
far is a blast that looks big. The function is kernel code with an offline test. Vanilla scales its shake by radius only
(`DamageWorker.ExplosionStart`: `DoShake(4 * radius * screenShakeFactor / distance to camera)`) [measured], so a wide weak
blast shakes like a wide strong one today.

The show runs on harmful blasts. Bomb-like types get every part. Flame gets fire, smoke, scorch and soot, with no thrown
dirt and no crater. Stun, EMP, Smoke and Extinguish keep their vanilla look in 0.2.0. Another mod's harmful type keeps its
own cell flecks and gains our shake, ripple, smoke, scar and soot.

The hook is a prefix and a postfix on `Explosion.StartExplosion`, apart from the knockback hook
(`DamageWorker.ExplosionDamageThing`). The prefix sets `doVisualEffects` false when our fire part is on, which stops the
vanilla flash, cell flecks, shake and water splash [measured: all four sit behind that field]. The show changes no
damage, radius, cell list or throw.

## 3. Every system an explosion can couple to

1. **Flash.** The player sees a white-hot disc that outshines the scene for a few frames. Size and time follow power.
   Engine: a FleckDef on shader `MoteGlow`, as vanilla `ExplosionFlash` [measured]. Frame cost: none to speak of. Art: one
   soft disc. **Verdict: 0.2.0.**
2. **Fireball.** The player sees an orange-white ball that swells fast, slows, darkens to red and breaks into smoke.
   Count and size of lobes follow power. Engine: three to six flecks with growth and fade [measured: `growthRate`,
   `fadeOutTime` are fleck fields]; a flip-book sheet if single textures read flat [guess ~60% that a fleck flip-book is
   simple]. Cost: low. Art: four fireball lobes. **0.2.0.**
3. **Sparks and embers.** Bright streaks fly out and drop; a few embers glow on the ground for seconds. Count follows
   power. Engine: thrown flecks (`FleckSystemThrown`) [measured]. Cost: low, capped per blast. Art: two streaks, one
   ember. **0.2.0.**
4. **Thrown dirt and stone.** Clods fly from the ground the blast hit: dirt from soil, chips from stone, splinters from a
   wood floor. The terrain under the centre picks the bit and its colour. Engine: thrown flecks tinted by the terrain's
   colour [guess ~75%]. Cost: low. Art: four dirt bits, four stone bits. **0.2.0.**
5. **Screen shake.** The view kicks, then settles. Strength follows power and falls with distance; a far small blast adds
   none. Engine: `Find.CameraDriver.shaker.DoShake(mag)` and `DoShake(mag, durationTicks)`; vanilla caps shake at 0.2
   times the player's own Screen shake preference and decays it at 0.5 per second [measured]. Our slider multiplies inside
   that cap, and many blasts add by the trauma rule, not by sum. Cost: none. Art: none. **0.2.0.**
6. **Air ripple.** A ring of bent air races out to the blast's edge. Width and strength follow power. Engine: a fleck on
   shader `MoteLargeDistortionWave` with the vanilla `PsychicDistortionCurrents` texture; Core's own `Fleck_Visual.xml`
   uses it [measured]. Cost: one full-screen-read quad per blast; cap live rings in a barrage. Art: none (vanilla
   texture). **0.2.0.**
7. **Heat shimmer.** Air over the fresh crater wavers for some seconds. Engine: shader `MoteHeatDiffusion` exists in Core
   [measured]. Cost: low. Art: none. **Later**: the ripple already shows bent air; two distortions risk a muddy read.
8. **Smoke.** A dark column boils up from the root, pales to grey, leans downwind and thins over tens of seconds; a big
   blast leaves a taller, longer column. It never spins. Engine: our own non-rotating flecks with growth and upward
   drift, wind read once from `map.windManager.WindSpeed` at the blast [measured]. Cost: the highest of the
   flecks; smoke puffs are capped per view and culled off screen. Smoke draws under thrown pawns and goods, so flight
   stays readable. Art: six puffs. **0.2.0.**
9. **Light on the scene.** Walls and ground near the blast are lit warm for an instant at night. Engine: an additive glow
   fleck as `FleckMaker.ThrowFireGlow` [measured]; a true light through `GlowGrid` costs a grid rebuild [guess ~70%].
   **0.2.0 as a glow fleck inside the flash part; a true light: cut.**
10. **Sound.** A crack, then a low boom that carries; farther blasts sound duller and later. Engine: `SoundDef` per size
    class, played where vanilla plays `damType.soundExplosion` [measured]; distance delay needs our own timer [guess
    ~60%]. Cost: none. Art: sound files, which the art pipeline does not make. **Later**, with a sound source decided.
11. **Crater scar.** Torn, burnt ground with a ragged dark rim, sized by power; none on water, and a scorch without a pit
    on stone and built floors. It lasts days; rain and time wear it away; a colonist can clean it. Engine: our own Filth
    ThingDef, as vanilla `Filth_BlastMark` (3 by 3, map mesh only) [measured], with a weathering stage; the vanilla mark
    is not spawned beside ours. Cost: none at rest (map mesh). Art: six scars. **0.2.0.**
12. **Soot on things.** Walls, doors, furniture and built floors near the centre turn charred black; reach follows power.
    The helper of §1.2 remembers the paint a thing had and gives it back when the soot is removed. Vanilla Remove paint
    and repainting both clear soot [guess ~65% that the restore hooks cleanly]; outdoors, rain weathers soot off over
    days. Cost: each painted thing dirties its map section once; a barrage spreads the paint over a few ticks. Art: none.
    **0.2.0.**
13. **Soot on pawns.** A person or animal in the blast is smudged black over body and head. It wears off in a day or so
    and washes off in rain or water. A look only: no stat, no thought. Engine: a hediff that drives an overlay drawn as
    vanilla firefoam is (`PawnFirefoamDrawer`, a `PawnOverlayDrawer` masked by the body texture, with a render node
    worker) [measured]; ours is a second drawer class, because vanilla's is a fixed field of `PawnRenderer` [measured].
    Cost: one cached overlay per sooted pawn. Art: four soot tiles. **0.2.0.**
14. **Roofs and dust.** Indoors, dust sifts from the ceiling across the room; under a thin rock roof, grit falls. Engine:
    `FleckMaker.ThrowDustPuffThick` on roofed cells of the room [measured]. Cost: low. **Later**: cheap, and second in the
    later set.
15. **Water, snow and steam.** A blast in or beside water throws a splash and a burst of steam; on snow it leaves a melted
    bowl with a steam wisp. Engine: vanilla already splashes (`FleckMaker.WaterSplash`) and melts snow
    (`explosionSnowMeltAmount`) [measured]; steam is one fleck. **Later**, first in the later set: our prefix must keep
    the vanilla splash alive in 0.2.0.
16. **Sand and ash.** A blast on loose sand or Pyrelands ash blows a bare ring. Engine: `SandGrid.AddDepth` [measured].
    **Later.**
17. **Plants.** Grass and crops in the radius are flattened or burnt to stubble, beyond the damage vanilla already does.
    **Cut**: vanilla blast damage already kills plants, and more is a gameplay change.
18. **Weather.** Rain shortens smoke and washes scars and soot; wind leans smoke. **0.2.0**, as conditions that parts 8,
    11, 12 and 13 read. No part changes the weather.
19. **Pawn stagger near the edge.** A pawn just outside the throw staggers a step. Engine: `stances.StaggerFor`
    [measured]. **Later**: a mechanic, not a look; it needs its own bar and its own load statement.
20. **Animals flee.** Vanilla already does this: wild animals within radius plus 7 flee a blast of radius 3.5 or more
    [measured, `Pawn_MindState.Notify_Explosion`]. **Cut**: built.
21. **Thoughts and noise.** A "shaken by a blast" mood, sleepers woken (`GenClamor.DoClamor`) [measured]. **Later**, with
    19.
22. **Terrain burn.** A flammable floor under the centre becomes its burned form (`TerrainDef.burnedDef`,
    `TerrainGrid.Notify_TerrainBurned`) [measured]. **Cut**: it destroys the player's floor, which is damage, not show.
23. **Lights flicker.** Nearby lamps dip for a moment. **Later** [guess ~50% feasible without a power-net touch].
24. **Time.** A few frames of slow motion on a huge blast. **Cut**: the clock is the player's.
25. **Soot on goods and corpses.** Thrown goods land blackened. **Later**: items have no paint slot, so it needs a new
    overlay on every item kind.
26. **A warning before the bang.** A falling shell's whistle and shadow, as Drop FX does. **Later**: it belongs to the
    weapon, not to the blast.

## 4. The choice

### The 0.2.0 set, ranked

| rank | part | bar | why this rank |
|---|---|---|---|
| 1 | Fireball, flash, sparks, thrown dirt (1 to 4, 9) | `blast_show_fire_and_flash` | The blast itself. Without it, nothing else reads. |
| 2 | Smoke (8, with wind) | `blast_show_smoke` | His sharpest complaint: "rotating cartoon cotton". |
| 3 | Screen shake (5) | `blast_show_screen_shake` | First in his list; no art; the strongest feel for the least work. |
| 4 | Crater scar (11) | `blast_show_crater_scar` | "Ugly crater scars"; the part that endures. |
| 5 | Soot on things (12) | `blast_show_soot_on_things` | His Pyrelands ask; reuses a proven method. |
| 6 | Air ripple (6) | `blast_show_air_ripple` | His ask; the shader ships with the game. |
| 7 | Soot on pawns (13) | `blast_show_soot_on_pawns` | His ask; the most new code, so last. |

Two bars span the set: `blast_show_scales_with_damage` (§2) and `blast_show_switches_off_clean` (§5). The barrage bar of
0.1.0 (`barrage_frame_budget`) stays as it is, and the show must hold it: off-screen blasts draw nothing and still lay
their scar and soot.

### Later, in order, and cut

Later: water, snow and steam (15); roof dust (14); sound (10); stagger, thoughts and noise (19, 21); heat shimmer (7); sand
and ash (16); the looks of Stun, EMP, Smoke and Extinguish blasts; soot on goods (25); lights (23); the shell's warning
(26). Each is cut from 0.2.0 for one reason: his words do not name it, and seven parts with new art are already a full
version. Cut for good: a true light (9), more plant harm (17), wild animals fleeing (20, built), terrain burn (22), slow
motion (24).

### Against the guiding principles

- **Conditions, not a biome (entry 1).** Every part reads the blast and the place: its power, the terrain under it, a
  roof, the wind, rain, water. No part reads a biome.
- **No meaningless effect; an effect that implies harm is true (entries 2 and 4).** A scar and soot lie only where a
  harmful blast did damage. Soot on a pawn means that pawn was in a blast.
- **A limit lives in the world (entry 3).** Scars and soot accumulate. The brakes are rain, time, cleaning, Remove paint
  and repainting.
- **Combined load (entry 5).** On every map the show adds: nothing to read between blasts; cleaning of scars inside the
  home area, as any filth; no tick work except a slow weathering pass over the scars and sooted things that exist.

## 5. Mod Settings

All on by default; defaults are the shipped behaviour; with every switch off a blast looks as in the unmodded game.

- On/off: Fire and flash · Smoke · Screen shake · Crater scars · Soot on things · Soot on pawns · Air ripple.
- Slider: **Screen shake strength**, none to double, inside the player's own vanilla Screen shake preference.
- Choice: **How long scars and soot last** (short, normal, long). It acts on marks made after the change.

## 6. Art to commission (nothing is queued)

Style note for all: RimWorld's top-down painted look, soft edges, no outline, no cartoon shapes; the reference is the
practical pyrotechnics of the original films, a fuel fireball with white sparks and black oily smoke. The canon library
(`design/RimStarWars/canon_references/`) holds no entry named for a blast, fire or smoke [measured, by folder name], so the art judge reads this note and his
words above. His bar from 2026-11-20 stands: soot, scorch and crater must be a significant improvement on the donor's.

| texture | count | note |
|---|---|---|
| Flash disc | 1 | soft white-yellow, drawn additive |
| Fireball lobe | 4 | orange-white core, red ragged edge; reads when grown 1 to 8 cells |
| Spark streak, ember | 2 + 1 | thin, bright, tapering |
| Dirt bit, stone bit | 4 + 4 | neutral grey, tinted by the terrain's colour |
| Smoke puff | 6 | no symmetry and no rotation; dark base, lit top; reads from near black to pale grey by tint |
| Crater scar | 6 | torn ground, burnt ragged rim, radial streaks; drawn up to 7 cells; transparent edge; reads on soil, sand and stone |
| Pawn soot tile | 4 | smudge and streak pattern, masked to the body as firefoam is |

## 7. Not measured in this study

- No frame cost is measured; each cost line in §3 is a reading of how the engine draws the part.
- The restore of a thing's own paint after soot and the code-made ColorDef across save and load are guesses, tagged
  where they stand.
- Whether the "crater" of his walk on 2026-11-24 was the vanilla blast mark is a guess.
