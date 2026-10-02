# Helix Tellurox — validation walk
subject: src/RimStarWars/SWBestiary  (packageId mandrake.rsw.swbestiary)
feature: tellurox-race
absorbed: HelixTellurox (dying id rsw.helixtellurox) folded into SWBestiary at Defs/HelixTellurox/ThingDefs_Races/Races_Tellurox.xml in Sprint wave A (commit 247cd6d40) — no longer ships alone.
deps: none
list: minimal
status-hint: Tellurox — Ascendant Helix labour-line draft/pack animal with a PERMANENT non-molting shell; first-rate plate only from slaughtering a mature working animal, never a shear cycle. Not yet wired into HorrorWastes' curated wild-spawn cast (owner-documented follow-up, out of scope here).

## must be true
- RSW_TelluroxRace (ThingDef, ParentName AnimalThingBase) exists as a tameable, pack/herd animal with ComfyTemperatureMin -60 (cold-hardy for HorrorWastes) and butcherProducts including RSW_TelluroxShell x6 via the `<li><thingDef>` cross-ref form, not the `<RSW_TelluroxShell6>` collapsed form the file's own comment warns breaks corpse-gen.
- RSW_TelluroxShell (ThingDef, ParentName LeatherBase) is a stuff-capable material with StuffPower_Armor_Sharp 1.65 and commonality 0.04.
- RSW_Tellurox (PawnKindDef, ParentName AnimalKindBase) resolves race=RSW_TelluroxRace and has 3 lifeStages, each pointing texPath Things/Pawn/Animal/Tellurox/Tellurox (the one real texture on disk) with drawSize 1.3/2.0/2.6.
- The mod has no third-party dependency and no C# — it is pure content, so this walk is entirely [L]/[D]/[B].

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rsw.swbestiary" and no XML error naming Races_Tellurox.xml
2. [D] def read-back: ThingDef RSW_TelluroxRace exists; race.body = QuadrupedAnimalWithHooves, race.packAnimal = true, race.herdAnimal = true, statBases.ComfyTemperatureMin = -60
3. [D] def read-back: ThingDef RSW_TelluroxRace.butcherProducts contains RSW_TelluroxShell with count 6 (proves the `<li><thingDef>` cross-ref form parsed correctly rather than silently producing a null-thingDef corpse-gen NRE, per the def file's own warning comment)
4. [D] def read-back: ThingDef RSW_TelluroxShell exists; stuffProps.commonality = 0.04, statBases.StuffPower_Armor_Sharp = 1.65
5. [D] def read-back: PawnKindDef RSW_Tellurox exists; race = RSW_TelluroxRace, combatPower = 70, lifeStages count = 3, each lifeStage's bodyGraphicData.texPath = "Things/Pawn/Animal/Tellurox/Tellurox"
6. [B] jawa/spawn_pawn {kind: RSW_Tellurox} → expect a live pawn, race RSW_TelluroxRace
7. [B] jawa/list_things {defName: RSW_TelluroxShell} after butchering a spawned-then-killed adult tellurox → expect RSW_TelluroxShell items present (proves the butcherProducts cross-ref actually resolves at runtime, not just in the def read-back)
X. [S] (human pass) Tellurox.png sprite at each of the 3 drawSize life stages — out of scope here

## north star
state: DRAFT
validated-hash:

Seeded 2026-10-01 by an agent (NORTH_STAR_WALK_AUTHORING_1) from this walk's
`## must be true` and the mod's shipped sprites, defs and settings, on the owner's
ruling that day: *"You are mostly seeding the field right now with reasonable
initial guesses for refinement later through debugging needs or live feedback."*
Every line is an agent guess for him to accept, edit or cut; `(guess)` marks the
least certain. `### the experience` is his to dictate.

### the experience  (OWNER'S WORDS)
(not yet dictated)

### must show

**The tellurox**
- [ ] `tellurox_reads_shelled_beast` — `RSW_Tellurox` reads at play zoom as a
      heavy armoured labour animal, its permanent shell the obvious feature.
      (guess)
- [ ] `tellurox_grows_visibly` — the three life stages (drawSize 1.3 / 2.0 / 2.6)
      read as a calf, a youngster and a full-grown beast side by side.
- [ ] `tellurox_reads_as_pack_animal` — a caravan tellurox carrying packs reads as
      a beast of burden. (guess)

**The shell**
- [ ] `tellurox_shell_reads_as_plate` — `RSW_TelluroxShell` in a stockpile reads as
      shell plate, not ordinary leather.

### cannot show

- [ ] `tellurox_never_shorn` — a shear job or molt yielding shell plate; the shell
      only arrives from a butchered mature animal. (guess)

- [ ] `tellurox_never_sideways_walking_north` — one `Graphic_Single` texture, so
      the beast may show its side profile walking north or south; acceptable or
      not is his call. (guess)
