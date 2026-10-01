# STILLSAND_EVENT_CREATURES_1 — krayt attacks, the muurrok, and the rest of the event ladder

From `STILLSAND_BEDAZZLE_SITTING_1` (closed 2026-09-30). Design source:
`design/Jawa/worldbuilding/biomes/stillsand_turn3_development_2026-09-30.md` §2.5 and §4 #10, with
the turn-4 rulings in `stillsand_bedazzle_cast_2026-09-30.md` §0. **Needs
`STILLSAND_SAND_SWIM_KIT_1`** (every creature here swims on that kit).

Owner, typed, volley turn 2: *"This biome needs event level creatures. Attacks by the mighty krayt
dragon. And others."*

## spec

1. 🔴 **The krayts and the war wyrm STAY WILD** (owner, by card, 2026-09-30; he declined the doc's
   incident-only recommendation). `RSW_KraytDragon` 0.15, `RSW_GreaterKraytDragon` 0.001 and
   `RSW_WarWyrm` 0.2 in `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Stillsand.xml` are
   unchanged. The attack events are added **on top**.
2. **The krayt attack incident (RSW/Utinni tier).** A biome-gated `IncidentWorker` on the
   `RM_IncidentWorker_SandBusterEruption` precedent, gated by the `RSW_SwimmerRoadExtension.biomes`
   defName pattern. Beats: a rumble on the windward horizon that grows for about a game minute and
   a letter (*"Something vast is moving under the sand."*); a wake toward whatever is loudest
   (drilling, a landing ship, a charged thumper); a breach with dust column and stagger ring; it
   **fights on the surface** (canon). It dives on hard ground, fire, or once fed. If it feeds, it
   takes the prey down: drag mark into a disturbed-sand funnel and a letter naming the taken.
   Odds are weighted up by vibration and by the Return's Debt (`STILLSAND_RETURN_RITUAL_1`).
3. **The muurrok (RM tier, the free tier's leviathan, ruled YES).** Invented, `RM_Muurrok`
   (name swept clean 2026-09-30), bs about 14, commonality 0 (incident only, so the free tier has
   a mighty event without the RSW layer, Q11a). A sub-sand swimmer whose sun-face is one **mirror
   crest**; the only thing you see is a line of glare moving across the dunes. It appraises a
   party from the edge of sight and takes one body. Owner, typed: *"Yes and use the beam attack
   style from mechanics due to reflections"*: its ranged attack is a **reflected-sun beam** off the
   crest in the mechanoid beam style.
   - **Verb, VERIFIED on RimSage 2026-09-30:** the mechanoid beam is `Verb_ShootBeam`
     (`Verse/Verb_ShootBeam.cs`), used by Biotech's `Gun_BeamGraser` (beamDamageDef `Beam`,
     `beamMoteDef` `Mote_GraserBeamBase`, `beamEndEffecterDef` `GraserBeam_End`, sound
     `BeamGraser_Shooting`, `beamFullWidthRange` 6.9).
   - ⚠️ **It cannot be used as-is on an animal.** `Verb_ShootBeam.ApplyDamage` reads
     `base.EquipmentSource.def` unguarded (for the battle log and the DamageInfo weapon), and an
     animal's natural verb has no equipment source, so it would throw on the first hit.
     `ApplyDamage` and `HitCell` are private, so a subclass cannot override them. Build
     `RM_Verb_MirrorBeam` (a copy of the beam's path/burst logic with a null-safe damage step and
     the race as the log's instigator), or Harmony-guard the null. Read the decompiled class first.
   - The beam **heats, never ignites** (no fire), works only in sun (none in the gale or in deep
     shade), and its strength scales with the tile's sun elevation.
   - Its corpse yields **crest-plate** (`RM_CrestPlate`, a mirror reflector material that feeds
     the high-performance solar oven in `STILLSAND_GLASS_LENS_CHAIN_1`).
4. **The sarlacc swimmer comes to root (RSW).** A Stillsand incident: a `RSW_SarlaccSwimmer`
   whose water is running out swims toward the largest seep (usually a precious cave,
   `STILLSAND_PRECIOUS_CAVES_1`) and roots there, on the built `src/RimStarWars/Sarlacc/` stages.
5. **The greater krayt den (quest, RSW/Utinni).** A greater krayt has denned in a rock cave; the
   Deep Desert Tribes and a Jawa crew ask for help. Bait (a bantha or eopie), the drumming lure,
   charges in the tunnels. The cleared den becomes a precious cave. Den set piece: the krayt-den
   row of the caves table.
6. **The krayt horn (lore IN, RSW).** `RSW_KraytHorn`, craftable; plays the shipped
   `RSW_Pawn_KraytDragon_Call`. It routs smaller predators and tribal raiders, and every blow has
   a small chance to queue a real krayt attack.
7. **The Long Hunger (RUT, built, never live-fired).** Its v2 summon is the thumper
   (`STILLSAND_SAND_SWIM_KIT_1` §5) via `RUT_Groundcaller`; live-fire it once on a Stillsand map.
8. **Mod Settings:** a toggle and an odds slider per incident; the horn's answer chance.

## criteria

- A wild krayt still spawns on a Stillsand map; the krayt attack incident fires by dev action on a
  Stillsand map and is refused on other biomes.
- The muurrok's beam damages a target on a quicktest without an exception in `Player.log`, and does
  nothing in the gale.
- Every take by any event creature leaves a funnel or drag mark plus a letter.
- The horn routs a test predator and logs its answer roll.
