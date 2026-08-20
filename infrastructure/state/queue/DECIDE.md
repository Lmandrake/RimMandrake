# DECIDE inbox.

## 📌 SESSION HANDOFF — 2026-08-20. Read this before working the items below.

**State:** 7 live items, 1,456 lines of archive. The queue opened this session at **40 items /
1,529 lines** and every item that did not need a live game or an owner decision is closed.

### 🔴 The three things a fresh DECIDE must not re-derive

1. **The map reaches the game over the LIVE BRIDGE** (owner, 2026-08-19). Vanilla worldgen runs
   untouched, then the companion stamps all 21,872 authored tiles before any map exists.
   ⛔ Savegame writing is dead; `worldmap.py` refuses to write. `ASHKARR_WORLD_DEFINITION.md` §12.
   ⇒ **This killed the biome mix as a worldgen gate** and re-premised two design items. If
   something reads as worldgen tuning, check whether we now simply paint it.
2. **`permanentEnemy` short-circuits before the exception list** (`FactionDef.cs:463`). Ruled
   2026-08-20: the Empire's enmity becomes a whitelist, filed as
   `empire-permanent-enemy-becomes-a-whitelist-7c31d9`. ⚠️ It is a whitelist of who is NOT an
   enemy — anything absent is hostile, silently.
3. **The Rakata are the VICTIMS.** Terraformers and mega-builders, nearly wiped out by an
   assailant whose technology **rots** — which is why nobody can name them and why everything
   scavengeable on this planet is Rakatan. `the_forgotten_war.md` R-W6. ⛔ DECIDE asserted the
   opposite on 2026-08-20 and propagated it into four files before the owner corrected it; the
   wrong version is the intuitive one and is struck in place, not deleted.

### ⏱️ What is on the worldgen clock, and what is not

**ON:** B40–B54 (factions + ideos are read ONCE at world creation) · the Empire whitelist ·
`seven-jawa-factions-still-default-to-zero-at-worldgen-4a71c8` · the Worldbuilder preset
(CHECK's) · Imperial **name makers** still generate Sophian names into the shipped save.
**OFF, ruled 2026-08-20:** `pawnGroupMakers` are read at raid time, not world creation — so the
16 orphaned roster kinds can be fixed after the world is frozen. The biome mix, likewise, gates
nothing.

### 📄 `Inhabited` — the mod designed this session

`design/Jawa/bridge/INHABITED_DESIGN.md` (526 ln) · `_SPECIES_TEXTURE.md` (248 ln) · **eleven
cast files, ~300 characters, all twelve factions.** Owner's scope: **v1 for the DESIGN, v2 for
the code** — the world is built as though the people will arrive; ⛔ do not file BUILD items for
the code. The remaining DECIDE work is the placement pass onto the gazetteer.

### ❓ Open, and waiting on the owner
- `8d4c07` — the `Rule_Disallow*` set for the ScenarioDef. His principle is recorded (*a Jawa may
  not personally sow or dig; machines may do both*); the per-building judgements are not.
- `D-V2-RAIN` — spec written and measured; needs a BUILD item filing.
- Whether the Sith rumour ever hardens. **Current ruling: it never does.**


📁 **Settled items live in `infrastructure/state/queue/DECIDE_ARCHIVE.md`** — 31 of them,
moved 2026-08-19 verbatim on the owner's instruction so this file holds only live work.
Read them as records, not instructions: several carry premises the live-bridge ruling
killed.

## D-CRIT ⭐ Read before sequencing — the worldgen deadline
row:      10
spec:     🔴 SUPERSEDED 2026-08-15 and now reduced to its ONE live clause. The old
          item said the ocean gated worldgen and that an assembly had to ship before
          rows 2 and 7 could close. Both halves are dead: the owner ruled worldgen
          MANUAL on 2026-08-14, and the sea left v1. **Those two rulings are stated
          once each, in `V1_CHAIN.md` step 6. Do not re-derive either from here, and
          do not restate them anywhere else.**
          WHAT STANDS, and it is a real gate:
          - Rows 2 and 7 are ONE event — the owner's single worldgen run. Row 2 needs
            no build: `WORLDGEN_FACTION_CHECKLIST.md` is ratified (21 untick / 6 keep)
            and is one screen he ticks during that run.
          - ⇒ **Chain steps 6 and 9 must be SHIPPED AND LIVE BEFORE he sits down to
            generate.** Factions and ideos are read once at world creation and cannot
            be retrofitted. That is **B40–B54**, and it is the real gate on row 7.
            It is not scheduled by us — it is a human event we do not control, so the
            work is late the moment he decides to start.
          The `waterPct` seed-variance measurement moved to `design/V2_DREAMS.md`
          under "Retired from v1" — it was a measurement, not a plan.
verify:   no queue item schedules a campaign worldgen run, and B40–B54 are all live
          before anyone tells the owner the world is ready to make.
criteria: —
state:    ready — the deadline clause is the only live part of this item.

## sequence-the-ideoligion-check-before-the-faction-work-e3f1a7
row:      10
spec:     From CHECK's **C42** (`5aca170`, `071cf52`), routed by REP because it lands
          directly on the owner's ruling that faction and ideo work is v1.

          The owner's words today: *"faction and ideo work are part of v1, and we already
          HAVE the ideoligion I believe. The task to build the factions in-game should be
          nearly done save for the allowed items, descriptions, etc."* 🔴 **That belief is
          the thing C42 cannot yet confirm.**

          `The Salvation.rid` and `MandrakeJawa.xtp` both carry a `<modIds>` provenance
          block naming **585 mods, 11 of which no longer load** — including all three
          xenotype donors. What CHECK cleared offline against the live dump: the xenotype
          is CLEAN (35/35 genes plus icon), memes 5/5, culture present, and the
          `Outland_*` genes are safe because Outland Genetics is a DIFFERENT mod from the
          switched-off `neronix17.outerrim.galacticdiversity`.

          ⚠️ **The 82 precepts are UNMEASURED, and CHECK asks for that word specifically.**
          Not "missing" — an earlier scrape reporting 71 missing was CHECK's own bug: the
          precept block nests `RitualBehavior` / `RitualOutcomeEffect` /
          `RitualObligationTargetFilter` defNames, which are not `PreceptDef`s. And
          `validate_ideoligion.py` does not cover this case — it reads IdeoPresetDef and
          FactionDef XML and answers "no religions found" on a `.rid`. **There is no
          offline route to the answer.**

          Why it is yours and why it is urgent: an ideoligion **bakes at world creation
          and cannot be retrofitted**, same as the factions. If the faction work is
          "nearly done", this artifact is close to final and is the largest unmeasured
          surface on CHECK's board. The live answer is cheap — load the ideo on the
          scratch map and read the dialog, one screen — and CHECK has queued it ahead of
          any worldgen run. **Sequence it before the faction work is called done.**
verify:   the 82 precepts are measured live and reported as present/absent by defName.
criteria: the ideoligion loads with every precept resolving, on the mod set that will be
          active at world creation.
state:    ready

## the-shipping-xenotype-drops-four-of-our-own-genes-7e31aa
🔧 **FIXED ON DISK 2026-08-15 by BUILD — NOT YET CONFIRMED LIVE.** The repo copy had been
correct since `c57f347` (the rename commit); only the game copy under `Xenotypes\` was
stale. So it was never an artifact migration — it was a file that had never been
deployed. Backed up to `MandrakeJawa.xtp.bak-2026-08-15`, copied, md5 equal,
`validate_save_artifact.py` reports 36/36 resolve and zero dangling.
🔴 **THAT IS DISK EVIDENCE, AND DISK EVIDENCE IS WHAT GOT THIS WRONG THE FIRST TIME.**
The superseded claim in LIVE.md was ALSO "36/36 references resolve" from an offline
validator, and the running game contradicted it. The engine is the only witness that
counts here, and the game now running loaded the OLD file at startup, so this session
CANNOT confirm the fix.
⇒ **CLOSING CONDITION, and it costs nothing to collect:** the NEXT load's startup log
carries **zero** `Could not load reference to Verse.GeneDef named Jawa_*` lines. Today's
load carried 12 GeneDef lines, of which 4 were ours. `harvest_log.py --show scribe`
reads them. Until that reads clean, this stays OPEN as *fix deployed, unverified*.
⚠️ **NOT actioned and still live: `softshadow.xtp` carries two dead names** —
`Jawa_Gene_Skittish` and `Jawa_Head_Plain` — and will drop those genes silently at world
creation exactly as `MandrakeJawa.xtp` would have. Not in our repo and not what the owner
named, so BUILD correctly left it. Someone must decide whether it matters before worldgen.
`pokean.xtp` is clean.

state:    blocked — needs a live game. **Fix deployed to the game copy 2026-08-15, never
          witnessed.** ⚠️ This item had NO `state:` line for four days, so it was invisible
          to the board and to every seat sweeping by state. Added 2026-08-19.
          CLOSING CONDITION, and it costs nothing to collect: the next load's startup log
          carries **zero** `Could not load reference to Verse.GeneDef named Jawa_*`.
          `harvest_log.py --show scribe` reads it. Today's load carried 12 GeneDef lines,
          4 of them ours. ⛔ Offline validation cannot close this — an offline validator
          already claimed 36/36 resolve and the running engine contradicted it.
          ✅ The `softshadow.xtp` half is DEAD: the owner had the file deleted 2026-08-15.
raised:   2026-08-15 CHECK, from the live startup log of the 575-mod load.
finding:  `MandrakeJawa.xtp` — the shipping v1 xenotype — **silently drops 4 of our own
          GeneDefs every time it loads.** RimWorld logged 17 Scribe `Could not load
          reference to` lines at startup; 4 are ours:
            `Jawa_Eyes_HugeAmber`  → live def is `RimMandrake_Jawa_Eyes_HugeAmber`
            `Jawa_Eyes_HugeOrange` → live def is `RimMandrake_Jawa_Eyes_HugeOrange`
            `Jawa_Head_Plain`      → live def is `RimMandrake_Jawa_Head_Plain`
            `Jawa_Gene_Skittish`   → live def is `RimMandrake_Jawa_Skittish`
          🔴 The last one is NOT a straight prefix — `Gene_` was dropped as well, so a
          blind "add RimMandrake_ to everything" migration fixes three and breaks the
          fourth differently.
          **Nothing is missing from the game.** All four new names are present in today's
          fresh 575-mod dump. The defs were renamed and the SAVED FILE was never migrated.
          Three further dead genes are `guy762_*` and are EXPECTED — that donor is
          deliberately off for C36. Five more are `RG_*` ThingDefs inside LWM Deep
          Storage's own settings, benign B-BOIL collateral.
why it changes the design, not just the code:
          The .xtp **bakes at world creation**. Whatever it drops is lost in the world the
          owner is about to generate, and the drop is SILENT in play — a Jawa comes out
          without its head type and eye colours and nothing says so.
          ⚠️ `softshadow.xtp` and `pokean.xtp` carry some of the same dead names.
🔴 this invalidates a recorded fact:
          `LIVE.md` said "`MandrakeJawa.xtp` is CLEAN: 36/36 references resolve." That was
          an OFFLINE verdict and the running game contradicts it. Corrected in LIVE.md.
          **An offline validator cannot catch this class at all** — Scribe resolves saved
          names at load time, and a def-dump check answers a different question. C42's
          "the dangling-reference question is CLOSED offline" is falsified for the .xtp.
decision needed:
          Migrate the four names in the saved .xtp before the worldgen run, or accept the
          drops. NOT MINE TO CHOOSE and not mine to author — I am not editing a shipping
          save artifact on my own authority. ⛔ Blocking on the real worldgen run: it bakes.
evidence: Player.log 2026-08-15 16:1x, 575 mods, build 1.6.4871 rev591, dump captured
          2026-08-15T23:12:54Z — same stack as the running game, so not a stale-dump
          artifact. Def loader crossref was CLEAN at baseline 25; this is Scribe only.

## D-V2-RAIN  Ban rainfall planet-wide, except violent rain in the high mountains
state:    ⭐ **v1 — OWNER RULING 2026-08-19.** *"Ban rainfall: v1 (but might still happen
          on highly mountainous terrain!)"* ⇒ The ban is v1 content and the mountain
          exception is CONFIRMED as part of it, not a maybe.
          ⚠️ **The `D-V2-` in this item's name is now wrong and is kept anyway** — POLICY
          forbids retitling an item, because the board counts items by name out of git.
          Read the state line, not the name.
          **What v1 owes, and it is small because the route changed:**
          (a) **The ban is one authored column.** Rainfall is set per tile in
              `world/ASHKARR_WORLDMAP_tiles.csv` and stamped over the bridge. No mutators,
              no worldgen, no per-tile placement work. DECIDE picks the value.
          (b) **The mountain exception is a predicate over two columns we already author**
              — `tileElevation` and `tileHilliness`. "Highly mountainous" is computable, so
              the wet band is drawn, not hand-placed.
          (c) **The violent weather is ONE patch**, the same shape as the Pyrelands ash
              storm: `weatherCommonalities` on the biomes that occupy the high country,
              plus label/description work. `weatherCommonalities` is read at RUNTIME, so it
              needs nothing from worldgen and can land any time.
          ⛔ **Still out, and the line has not moved:** anything that makes the GENERATOR
          produce this. The rule is authored into our tiles and our defs; it is not a
          worldgen feature and must not become one.
          🔑 **The one open question is the number, and it is an economy question, not a
          biome one.** Biome eligibility no longer keys off rainfall for us — we assign
          biomes directly — so the old worry ("which biomes survive at zero rainfall") is
          void. What survives: plant growth and fertility read rainfall during PLAY, so a
          hard 0 may starve the Jawa economy. DECIDE proposes a floor.
owner:    2026-08-16, verbatim: *"spec out banning rainfall on any biome except those
          that occur in high mountain areas where instead it is torrential, boiling, red,
          or otherwise violent and bizarre, otherwise we have to add mutators everywhere
          to enact this (v1 approach)."*

the idea:  On a Tatooine-grade desert world rain should essentially not exist. The
          exception is the high country, where what falls is not rain as anyone would
          recognise it — **torrential, boiling, red, violent, bizarre**. Rain becomes a
          rare, frightening, altitude-locked event rather than weather.

why v1's shape is wrong:
          v1 can only express this by hanging a mutator on every tile that should be dry,
          and another on every tile that should be violent. That is thousands of
          placements to say one planetary rule, and it breaks the moment the world is
          regenerated. **The rule belongs in worldgen and in the biome/weather defs, not
          in per-tile decoration.**

what we already know, so the spec starts from fact not guesswork:
          · ⛔ ~~Rainfall is a per-tile array in the save… already writable offline —
            `worldmap.py`, verified.~~ **DEAD 2026-08-19 — `worldmap.py` refuses to write
            and the save-writers are deleted.** ⭐ **REPLACED BY SOMETHING STRONGER:
            rainfall is AUTHORED PER TILE in `world/ASHKARR_WORLDMAP_tiles.csv` and
            stamped into the live world over the bridge.** Land on a test world spanned
            233–2584 mm.
          🔴 **⇒ THIS ITEM'S REASON FOR BEING v2 IS GONE.** It was parked because *"v1 can
            only express this by hanging a mutator on every tile that should be dry"* —
            thousands of placements to say one planetary rule. **We now set all 21,872
            tiles' rainfall by hand, in one column of a CSV.** The dry half of this spec
            is a v1 authoring decision costing one edit. Only the violent-mountain-rain
            half needs building, and that is a `weatherCommonalities` patch of exactly the
            shape already specced for the Pyrelands ash storm. ⚠️ Question 4 below ("which
            biomes survive at zero rainfall") is **also void** — biome eligibility is not
            computed any more; we assign biomes directly. What survives of question 4 is
            the real one: **plant growth and fertility read rainfall during PLAY**, so the
            Jawa economy is the constraint, not biome legality. ⇒ DECIDE owes the owner a
            v1/v2 call on this rather than leaving it parked on a dead premise.
          · **Biome selection keys off rainfall.** Zeroing it does not just change a
            number; it changes which biomes are eligible, which is the real lever and
            also the real risk.
          · Altitude is available too: `tileElevation` (raw − 8192 → metres) and
            `tileHilliness`. "High mountain" is therefore a computable predicate, not a
            hand-drawn region.
          · The tidally-locked planet mod rewrites **temperature** but leaves rainfall
            alone — so rainfall is ours to define with no conflict.
          · `VEE_FertileRains` already occurs **124 times**; whatever we do must
            out-rank or remove that.

the spec should answer:
          1. Does "ban" mean rainfall 0, or a low non-zero floor? 0 may make some biomes
             ungenerable and could break plant life the campaign needs.
          2. Are the violent rains a **WeatherDef** (an event you live through), a
             **GameConditionDef**, a biome property, or a mutator confined to high tiles?
             Only the first three scale; the fourth is the v1 shape we are rejecting.
          3. What does "boiling" and "red" mean mechanically — damage, temperature spike,
             toxic buildup, terrain change? Flavour without mechanics will not survive
             contact with play.
          4. Which biomes survive at zero rainfall, and do we still get the plant cover
             the Jawa economy assumes?
          5. Does it read from orbit? A planet with one wet band in the mountains should
             be VISIBLE on the world map, or the rule is invisible to the player.

⛔ do not start:  this is a design spec, not a build. It also touches worldgen, which is
          OUT of every version by standing ruling — the write-up must stay on the design
          side of that line.

━━━ 📐 SPEC, DECIDE 2026-08-19. Measured, and it is smaller than anyone thought ━━━

🔴 **CORRECTION FIRST, because I told the owner otherwise and he would have decided on it.**
I said *"plant growth and fertility read rainfall during PLAY, so the Jawa economy is the
constraint."* **That is FALSE.** Grepped the full 1.6 decompile: the ONLY runtime consumer
of `Tile.rainfall` is `WeatherDecider.cs:191` —
`num *= weather.commonalityRainfallFactor.Evaluate(map.TileInfo.rainfall)` — plus
`WITab_Terrain` (a UI label) and the `BiomeWorker_*` scorers, which are worldgen-only and
which we overwrite anyway. ⇒ **Tile rainfall does not touch plant growth, fertility, crop
yield or food at all. It only weights which WEATHERS can be selected.** There is no economy
question and no floor to agonise over. Zeroing it costs nothing.

⭐ **AND THE BAN IS ALREADY MOSTLY AUTHORED.** Measured over all 21,872 rows of
`world/ASHKARR_WORLDMAP_tiles.csv`:
```
rain    0-50   : 17588   80.4%      elev_m   -30 .. 2266
rain   50-100  :  2589   11.8%      rain_mm   18 .. 1668, mean 96
rain  100-200  :   396    1.8%      Mountainous+Impassable: 1459 tiles (6.7%)
rain  200-400  :   244    1.1%        their rain: 18-1668, mean 571
rain  400-800  :   224    1.0%      tiles >=400mm: 1055, of which 555 are
rain  800-2000 :   831    3.8%        Mountainous or Impassable
```
The map is already a rainless desert whose wet is already concentrated high. The ruling is
mostly a **ratification plus a tightening**, not new work.

**THE MECHANISM — the shipped curve does the whole job.** Every vanilla rain weather's
`commonalityRainfallFactor` starts at **`(0, 0)`** and ramps to `(1300, 1)`. ⇒ **at tile
rainfall 0 a rain weather's commonality is multiplied by ZERO and it can never be
selected.** The ban is not a suppression hack; it is the field's designed behaviour.

**(a) THE BAN.** In the authored CSV set `rain_mm = 0` on every tile whose `hilliness` is
below 4. ⛔ Not 18, not "low" — **0**, because 0 is what makes the multiplier exactly zero.

**(b) THE EXCEPTION, and the discriminator is elegant.** Keep the authored rainfall on
`hilliness` 4 (`Mountainous`) and 5 (`Impassable`) — 1,459 tiles, 6.7% of the planet,
mean 571 mm. ⭐ **The per-tile rainfall IS the per-tile gate**, which solves the problem a
`weatherCommonalities` patch cannot: those biomes also exist at low elevation, and a
BiomeDef patch is per-biome, but `commonalityRainfallFactor` is evaluated **per tile**. So
author the violent weather with a curve like `(0,0) (800,0) (1200,1)` and it becomes
**physically incapable of occurring anywhere except the high country** — no mutators, no
per-tile placement, no new system.

**(c) THE VIOLENT WEATHER — do not author one.** Same lesson as the sandstorm: it is
already installed. Of 73 live `WeatherDef`s the two that match the owner's words
(*"torrential, boiling, red, or otherwise violent and bizarre"*) are **`SW_RedFoggyRain`**
("red foggy rain") and **`AB_VolcanicAshRain`** ("volcanic ash with rain"). Add them to the
`weatherCommonalities` of the biomes that appear in the high country — measured as
`ExtremeDesert` 320 · `AB_FeraliskInfestedJungle` 240 · `AB_RockyCrags` 171 · `Desert` 151
· `ZBiome_Badlands` 123 · `AB_PropaneLakes` 86 — and let the rainfall curve confine them.
🪤 `weatherCommonalities` is a LIST of `<li><weather>X</weather><commonality>N</commonality></li>`.
NOT the dictionary shorthand that killed `biomeConfigs`.

⭐ **A CONSEQUENCE WORTH KEEPING, not a problem to fix:** the river jungles
(`AB_FeraliskInfestedJungle`, 1,561 tiles) will be lowland tiles at rainfall 0 — **jungle
where it never rains.** That is not a defect, it is the setting stating itself: on Ash'karr
the water comes from the rivers and the seas, never from the sky. The owner's own brief was
*"coat the rivers in jungles"*. Leave it.

⛔ **Still out, unchanged:** anything that makes the GENERATOR produce this. The rule is
authored into our tiles and our defs. It is not a worldgen feature and must not become one.

## the-scenariodef-part-list-and-what-a-jawa-may-never-do-8d4c07
row:      12
from:     DECIDE, 2026-08-19. Created by the R-S2 reversal — the ScenarioDef went from
          "do not author" to "the only door", so its contents are now owed work.
          ⏱️ **DEADLINE: it must exist BEFORE the owner starts his campaign.** The engine
          embeds the parts at game creation and nothing may edit the save afterwards. A
          part missing then is missing from every player's game forever.
spec:     **RULED SO FAR — owner, 2026-08-19, in Q/A.**

          🔑 **THE PRINCIPLE, in his words:** *"anything that makes YOU know how to sow
          should not work. Jawas can only allow tech to farm for them."* and *"Jawa should
          not be able to mine ore, though some other races still can. And the mining laser
          should be able to do this very well."* Later, confirming: *"the mining laser
          should no longer be banned, **it makes sense as a tech you can learn from the
          ship**."*
          ⇒ **A Jawa may not personally sow or dig. A MACHINE may do both on their behalf,
          and the ship is where that machinery is learned.** That last clause is the
          justification and it should show up in the research tree's fiction, not only in
          a prohibition.

          **THE MECHANISM IS A HYBRID, and the split is measured, not stylistic:**
          | rule | lever | why not the other one |
          |---|---|---|
          | no personal sowing | `Rule_DisallowDesignator_ZoneAdd_Growing` + `Rule_DisallowBuilding` on every manual-sow basin/pot | 🔴 a gene with `disabledWorkTags: PlantWork` is TOO BROAD — `PlantWork` covers `Growing` **and** `PlantCutting`, so it would also stop a Jawa harvesting, cutting wild plants and **chopping trees**. No wood, on a scavenger clan. Confirmed in `Data/Core/Defs/WorkTypeDefs/WorkTypes.xml` |
          | no personal digging | a **GeneDef on `MandrakeJawa`** with `disabledWorkTags: Mining` | ⭐ a ScenPart designator ban is colony-wide and would block a recruited non-Jawa too. The gene is per-pawn, so it delivers *"Jawa cannot, other races can"* exactly — **and it applies to enemy Jawa factions as well**, which nothing else buys. `WorkTags.Mining` covers only the `Mining` work type. `GeneDef.disabledWorkTags` CONFIRMED at `Verse/GeneDef.cs:73`, applied per-pawn by `Pawn_GeneTracker` (`:414-419`) |
          ⚠️ **The def dump reports 0 of 3,847 genes using `disabledWorkTags`. That is a
          DUMP BLIND SPOT, not absence** — the field is in the decompiled assembly. Do not
          conclude from the dump that this cannot be done.
          🔴 **OPEN RISK, must be measured before building the gene:** if the mining laser
          is operated as a **`Mining` work-type job**, the gene would block Jawa from using
          it — which directly contradicts the owner's ruling. Measure the laser's mechanism
          FIRST; if it is a Mining job, the gene is the wrong lever for digging too and the
          rule needs a different expression.

          **THE HYDROPONICS TEST — owner's exact criterion:** *"If hydroponics doesn't
          actually use the pawn's planting skill to sow crops, then it can stay viable for
          Jawa."* ⇒ Ban is by MECHANISM, not by name:
          · a basin a colonist SOWS as a Plants job → banned. Vanilla `HydroponicsBasin`
            fails this test.
          · flowerpots → banned, same reason (owner named them).
          · an automated farm that produces without a sow job → **allowed**. Owner names
            the **VFE factory** as something that must still work.
          ⛔ Do not ban by label. Two things called "hydroponics" can fall on opposite sides.

          **REMAINING SCENPART DECISIONS:**
          · ⭐ `ScenPart_GameStartDialog` — take it. Highest-leverage text in the campaign.
          · ⭐ `ScenPart_DisableIncident` — take it. Stops the storyteller drawing an incident
            while leaving the def loadable for an authored quest. Cherrypicking cannot
            express this.
          · `ScenPart_PermaGameCondition`, `ScenPart_StatFactor` — **owner has not ruled.**
            DECIDE brings a candidate or drops them.
          · `ScenPart_DisableQuest`, `ScenPart_CreateIncident` — not v1.
          ⚠️ Prefer VANILLA part classes. `ScenPart_Error` means a save whose scenario
          names a part from an absent mod **degrades rather than failing the load** — so a
          modded part can silently vanish for a recipient and nothing will say so.
verify:   a `ScenarioDef` exists carrying the ruled parts; `validate_patch.py --defs` clean;
          every banned building is named by defName rather than by label; the Jawa mining
          gene is on `MandrakeJawa` and the mining laser has been confirmed usable by a
          pawn carrying it.
criteria: at the owner's campaign start, a Jawa cannot create a growing zone, cannot sow a
          basin, and cannot mine by hand — but CAN operate the mining laser, and CAN harvest,
          cut plants and chop trees. A recruited non-Jawa can mine normally.
state:    doing — DECIDE owes the def-level list; the enumeration of every manual-sow
          building and the mining laser's mechanism is in flight.
## living-npc-templates-a-mod-concept-7b2e4d
row:      —  (v2 concept; nothing in v1 waits on it)
from:     CHECK, 2026-08-19, **at the owner's direct instruction in session.** He asked for
          it to be specced into DECIDE's queue "to be a very rich tool for storytelling",
          and closed with *"It's for DECIDE to further expand or contract the concept."*
          🔑 **DECIDE OWNS EVERY SCOPE CALL HERE.** CHECK wrote it only because CHECK holds
          the engine facts; nothing below is a decision, it is a menu with prices on it.
spec:     📄 **The whole thing lives in two files — do not re-derive any of it:**
            `design/Jawa/bridge/LIVING_NPC_TEMPLATES.md`   36 templates + architecture
            `design/Jawa/bridge/BRIDGE_CAPABILITY_ROSTER.md`  the wider ~95-tool roster

          THE CONCEPT, owner's words: *"the pawns for this tool are sentient, named and well
          detailed. They have homes (they go to sleep at night), they eat when hungry, they
          may even 'tend' nearby structures (dwell near farms if present, dwell indoors for
          long periods then go on walks outside)... a peasant at home, a farmer at a
          worksite, a military fortification that has patrolling soldiers, an inward-dwelling
          commander, and prisoners that are given food to survive, pets and associated
          animals, hunters that hunt, etc. Go a bit crazy with these options."*

          ⭐ **THE HEADLINE: most of this is nearly free.** `LordJob_DefendPoint` already
          gives pawns that eat, sleep, socialise, wander and do work jobs around a point,
          with ONE toil and ZERO transitions - nothing can turn them hostile on their own.
          Total new code for everything except farming: **1 LordJob, 1 LordToil, 1 JobGiver,
          2 DutyDef XML, 1 setup utility. No Harmony.**

          🔴 **THE ONE THING THAT IS NOT FREE — FARMING.** Blocked three independent ways:
          only 7 shipped WorkGiverDefs carry `nonColonistsCanDo` and **all seven are
          construction or repair**; `WorkGiver_GrowerHarvest.ShouldSkip` returns true for
          **any lorded pawn, even a colonist**; and `WorkGiver_Grower` reads player-only
          zone data, so an NPC farm yields no work cells at all.
          ⇒ CHECK's recommendation, DECIDE's call: **reframe "tends the farm" as "dwells
          near it and repairs it", which is FREE.** Real farming roughly doubles the surface
          and pulls in Harmony. ⚠️ Note this hits the owner's own "farmer at a worksite"
          template - it is the one named start that does not come cheap.

          🔴 **A SAVE-CORRUPTION TRAP DECIDE SHOULD RULE ON.** `Lord.ExposeData_StateGraph`
          serialises toils by **POSITIONAL INDEX** and re-runs `CreateGraph()` on load, so
          changing a LordJob's toil ORDER silently corrupts existing saves. This revises
          CHECK's own earlier `LordJob_Patrol` ring proposal: a transition graph is fine for
          a patrol that never gets re-tuned, but anything we expect to iterate on should be
          ONE toil walking a waypoint index it owns and scribes.

          ⚠️ **A GAMEPLAY PROBLEM, NOT A BUG:** non-player pawns ignore player forbid flags
          entirely, so these NPCs **will walk into a player stockpile and eat the colony's
          meals**. Mitigate with their own food inside the radius, or accept it. DECIDE's call.

          THREE STRUCTURAL CALLS CHECK WOULD MAKE, offered as recommendations only:
          1. **Templates are CONTAINERS, not leaves** - a garrison holds a commander holds a
             cell block. Parent stamps structures and reserves sub-rects.
          2. **`decay` (0-1 ruin dial) is the highest-value single parameter** - it turns
             every template into its own ruined variant for free. Worth more than ten more
             templates.
          3. **`hostility: conditional`** (neutral until provoked) is what makes these read
             as inhabited rather than placed. Without it every template is a combat encounter.
          Plus: **named pawns should be the EXCEPTION** - one per template, rest generated.

          🔗 **TWO THINGS THIS WOULD INCIDENTALLY UNBLOCK**, both already in the repo:
          * `bridge-cannot-order-a-melee-attack-3f8c21` (V2_DREAMS) - the lightsaber swing
            frame cannot be staged because *"spawned hostiles have no lord"*; a real raid
            plus 5,600 stepped ticks produced no engagement. Spawning WITH a lord is exactly
            this tool.
          * **The Tusken water raid** (V2_DREAMS) - steal-and-withdraw needs a custom
            behaviour, and that entry already says *"Vanilla's LordJob layer is where it
            would have to be built."* Same layer, same skill, built once.

          PROVING ORDER CHECK SUGGESTS: **1 Peasant Hearth** (trivial) -> **4 Farmstead**
          (proves day/night) -> **7 Waystation Fort** (proves the patrol) -> **15 Fed
          Prisoners** (proves guest status + the feeding loop) -> **22 Sandcrawler Crew**
          (the set-piece, and the one that is most this campaign).
verify:   EMPTY - nothing to verify until DECIDE has cut the list.
criteria: EMPTY - DECIDE sets the pass condition when it rules on scope. CHECK will not
          invent one, and will not start building until it does.
state:    ready — for DECIDE

━━━ 🔴 OWNER'S ANSWERS, 2026-08-19 Q/A. Captured verbatim before they are lost ━━━

**1. SCOPE — 🔴 REVERSED BY THE OWNER, 2026-08-20.** *"Please ship the Inhabited spec to
BUILD for actual v1 construction, we have spare time tonight."* ⇒ **The code is v1 and is
being built now**, filed as the eight `INHABITED_*` / `CAST_ROSTER_*` items in
`infrastructure/state/queue/BUILD.md`. The design in `design/Jawa/bridge/INHABITED_DESIGN.md`
is unchanged and its §7 open questions are now BLOCKING — see `INHABITED_OPEN_QUESTIONS_1`
below, which is DECIDE's own debt.
⚠️ Still true, and not reversed by this: **nothing here blocks worldgen** — an `Inhabited`
place is a `WorldObject` stamped onto a finished planet, not a worldgen input — and
🔴 **farming stays NOT ATTEMPTED** (§2.1, blocked three ways in the shipped engine).

~~*"v1 for the DESIGN, v2 for the code."* ⇒ The templates, routes and casts are authored NOW
as design, so the hand-built world is built as though the people will arrive; the code that
animates them is v2. Nothing blocks worldgen and nothing has to be retrofitted. ⛔ Do not
file BUILD items for the code.~~
⛔ **DEAD — superseded 2026-08-20.** Struck in place, not deleted: "do not file BUILD items
for the code" is a live instruction a later reader would act on.

**2. THE WORLD REMEMBERS — world-level state.** The refinery crew flees and the tile is
marked; the next visit finds the place empty, looted, or squatted. ⇒ This is the load-bearing
choice and everything else bends around it. RimWorld discards a map when the player leaves,
so the state cannot live on the map.

**3. TRADE IS THREE LAYERS, and the owner expanded past what was offered.** Verbatim:
*"they have a little 'oil shop' they officially offer for their faction, but you can also
talk to individuals to buy/sell their personal inventory (very little silver of course),
and I also love that some faction lords may sell their own people to you right there. Or
buy yours, and then they stay!"*
  a. **faction stock** — the official shop, a `TraderKindDef` on the place
  b. **personal inventory** — any individual can be traded with, tiny silver
  c. ⭐ **PEOPLE, both directions** — a lord may sell you their own, or BUY yours,
     **and the bought pawn STAYS WITH THE CAST.** ⇒ cast membership is MUTABLE THROUGH
     TRADE, which means the roster is persistent state, not a spawn list. This is the
     single most demanding requirement in the whole concept.

**4. CAST DEPTH — all four taken:** daily ROUTE · ROLES within a cast · RELATIONSHIPS and
names · ANIMALS and property they defend.
  ⭐ **Everyone gets a name.** Owner: *"I think everyone deserves a name and at least some
  backstory, it can just be more generic for the 'lessers.'"* ⇒ named is the RULE, not the
  exception — CHECK's "one named pawn per template, rest generated" is **overturned**.
  Backstory DEPTH tiers; naming does not.
  🔴 **And his question back, which is a design ruling in disguise:** *"But are there really
  little people in the world? Remember we're playing Jawa..."* ⇒ see the ruling below.

**5. MOD NAME** — the concept is to ship as an independent mod. Naming in progress.

━━━ 🔴 ROUND 2 OF THE Q/A, 2026-08-19. Four more rulings ━━━

**6. STATE LIVES IN A `WorldObject` PER INHABITED PLACE.** Not a dictionary. It already
survives save/load, already carries a faction, already holds a pawn list, and ⭐ **it draws
on the world map** — so an inhabited place is visible from orbit before the player lands,
and the world map becomes a census. After a raid the same object reads *abandoned*.

**7. EVERY PERSON IS DOCUMENTED DEEPLY. NOBODY IS FLAT.** Owner: *"I want ALL of the people
documented deeply... it matters."* ⛔ The tier CHECK proposed (one named pawn, rest
generated) and the tier DECIDE proposed (deep for leaders, shallow for drudges) are BOTH
overturned. What varies is REGISTER, never depth.
🔑 **And the reason is the campaign's own point.** The owner: *"But are there really little
people in the world? Remember we're playing Jawa..."* ⇒ A Jawa clan is exactly who every
other faction calls an extra. A system that renders other people's crowds as anonymous
spawns asserts the hierarchy this campaign exists to look at from below. **No anonymous
pawns anywhere in the system.** It also pays off mechanically: buying a person only lands
as a decision if that person is someone.

**8. THE METHOD IS A POOL, NOT A BOOK.** ~300 people is a book of prose; instead author
**150–250 tagged fragments** — backstories, traits, tics, grudges, job-specific miseries —
keyed by role and faction, and let the generator combine them. Every pawn deep and
specific, authoring bounded. The writing effort goes into fragments, which is where it is
easiest to write well.

**9. 🔴 THE TONAL BRIEF, and it corrects DECIDE's framing rather than choosing from it.**
DECIDE offered "comic drudges under a grave world". The owner's answer, verbatim:
> *"There should be heartbreaking cases, hilarious examples, bizarre characters, utterly
> boring dweebs... they should not just be 'real people' with complexity, but
> **theatrically interesting**. One or two of them should be REALLY strange and
> interesting, while the rest are just the bizarre background that Star Wars usually has.
> We're recreating the **traditional Star Wars movie feel**, not the dark gritty
> Andor-type stuff. This isn't a WW2 recreation, it's a living breathing impossibly sci-fi
> world with **contradictory ethics living side by side in a way that seems utterly
> ridiculous and yet entrancing**."*

⇒ **THE CANTINA PRINCIPLE.** Not comedy versus gravity — *all registers at once, none of
them ironic*. Four registers to tag the fragment pool with: **heartbreaking · hilarious ·
bizarre · utterly boring**. "Utterly boring dweeb" is a REGISTER, deliberately dull people
are part of the texture, and they are still documented deeply.
⭐ **Distribution rule: one or two REALLY strange standouts per cast; the rest is bizarre
background.** A cast where everyone is remarkable has nobody remarkable in it.
⛔ **Not Andor.** No grit-as-seriousness. The world is impossible and cheerful about it.

**10. TIME — FROZEN UNTIL VISITED.** A roster changes only through the player's actions.
⇒ every change in the world is legibly the player's doing, which suits a hand-made frozen
planet, and it removes the risk of a beloved NPC dying offscreen to a dice roll.

━━━ 🔴 ROUND 3, 2026-08-19. The mechanic that ties it together ━━━

**11. FATE IS `RESIDENT` BY DEFAULT — flight is CAUSED, never a timer.** Owner: *"if they
flee it's because they must because you threatened them... and faction lowers from it. Not
a timer."* ⇒ The `LordJob_TradeWithColony` visitor arc is demoted from template to one FATE
among several. Three causes of flight, all player-caused or player-adjacent:
  a. **threat** — you menaced them. **Goodwill drops with it**, and today's ruling applies:
     hostile at −75, and hysteresis means it only ENDS at 0. No cheap apology.
  b. ⭐ **ARRIVAL** — *"hostile factions on the map might immediately declare flight when a
     giant gravship comes out of the sky, that's very reasonable."* The gravship is a
     PRESENCE in the world, not just transport. Some casts break at the sight of it.
  c. **hunger** — the larder empties, *"they try stealing from the player perhaps"*, and
     THEN they go. ⇒ the shipped forbid-flag hole (non-player pawns ignore player forbid
     flags and will raid a colony stockpile) stops being a defect and becomes **the warning
     shot before departure**.

**12. THE DEAD ARE SIMPLY GONE.** Owner: *"those who die when you aren't watching are
simply... forgotten. Lost. Very Star Wars actually. They are 'eaten and forgotten.'"*
⇒ No death record, no memorial, no ledger. **The absence IS the memory.** It also falls out
of the architecture for free: survivors return to the roster and the dead do not.

**13. ⭐⭐ RECURRING CHARACTERS — the best idea in the concept, and it is new.** Owner:
*"I really like that you might start recognizing returning characters for the various
factions from who you met on a map one day. 'Wasn't that guy working a refinery awhile
ago?'"*
⇒ **A DISPLACED POOL.** People who lose their place — fled, burned out, sold, abandoned —
are not destroyed. They go into a per-faction pool of the placeless. **When any cast is
next instantiated, it draws from that pool BEFORE generating anyone new.**
  · The world redistributes instead of only emptying.
  · Player actions ripple: raid one Hutt refinery, meet those survivors at the next one —
    carrying RimWorld's own memory of what you did to them, for free.
  · 🔑 **It does not violate "frozen until visited"**: redistribution happens at cast
    INSTANTIATION, i.e. when a map generates, never on a background tick. Still entirely
    event-driven by the player.
  · ⚠️ It requires the roster to hold REAL `Pawn` objects, which `ThingOwner<Pawn>` on a
    `WorldObject` already does — the `Caravan` pattern. A record-based roster could not do
    this at all.

**14. FOOD STOCKS ARE EXPOSED AND RAIDABLE — confirmed.** Owner: *"I like that their food
stocks are exposed. Very realistic."* A place that cannot feed its cast is not a place yet.
Since NPCs cannot farm (three shipped walls), sustenance is PRESENT rather than produced,
and it is visible, stealable and destroyable. Burn the granary and they leave — that is
FATE:flee firing for a reason the player caused.

━━━ 🔴 ROUND 4, 2026-08-19. Drift needs a reason, and the loop closes on the player ━━━

**15. CROSS-FACTION DRIFT: POSSIBLE, RARE, AND IT MUST CARRY A STORY.** Owner: *"Drift
between factions should be possible but rare and have a story... a reason. Enslavement.
Escape from their old owner. A lost battle."*
⇒ **A displaced person carries a REASON, and the reason is what licenses a faction change.**
Drift is never random; it is narratively caused and the player can read the cause.

| reason | may change faction? |
|---|---|
| **Enslaved** | ✅ yes — to the new owner's faction. Ties to `Slavery_Acceptable` and the Jawa-trader / Hutt-keeper split |
| **Escaped an owner** | ✅ yes — to factionless, or to whoever shelters them |
| **Lost a battle** | ✅ yes — absorbed by the victor |
| **Sold by the player** | ✅ yes — to the buyer's cast. This is the owner's own sale mechanic |
| **Fled a threat** | ⛔ no — stays in faction, resurfaces at another of its sites |
| **Starved out** | ⛔ no — same |

**16. ⭐⭐ THE LOOP CLOSES ON THE PLAYER — and this is the emotional keystone of the whole
system.** Owner: *"I love the recruitment story... it makes beggars suddenly much more
heartwrenching when they're the people you destroyed the livelihoods of recently."*
⇒ **The displaced pool feeds THREE consumers, not one:**
  1. **new casts** — the recurring-character effect (round 3)
  2. ⭐ **BEGGARS AND REFUGEES AT THE PLAYER'S OWN COLONY.** `GiveQuest_Beggars`
     ("beggars arrive") ships in this build. Draw its pawns from the displaced pool and
     **the beggars at your gate are the people whose livelihood you burned down last
     month.** The game already tells you their name and their history; it does not need to
     tell you whose fault it is.
  3. **recruitment** — you can hire out of the same pool. *"I burned down his refinery and
     now he works for me"* is the most Star Wars sentence this system can produce.
⇒ 🔑 **The design has no morality system, no karma meter and no reputation number for this,
and it must not grow one.** The consequence is delivered entirely by RimWorld's existing
name, backstory and memory systems plus the player's own recognition. That is why it works.

## D-EMP1 A fresh faction gap audit, against vanilla `Empire`
row:      1
spec:     🔴 **OWNER RULING 2026-08-20** (`OWNER_DECISIONS.md`, end of file): *"I've
          been very clear. OuterRim_GalacticEmpire is no longer in the game, we patch
          Empire."* Plus: *"I'm not sure we need either of those gap audits... we may
          instead need to perform a new one."*
          Both prior audits are **quarantined** at
          `infrastructure/disposing/faction_engine_gap_audit.md` and
          `.../faction_stage2_gap_audit.md`. Nothing in `disposing/` may be cited,
          followed or copied from — treat them as absent. They are there only so the
          7-day dwell can prove nobody needed them.
          ⚠️ **They were not merely stale — they reasoned from the wrong vessel.** Both
          audited the Stage 2 question against `OuterRim_GalacticEmpire`. Re-run the
          question against vanilla `Empire` (Royalty): what does the Empire still need
          before v1, given Royalty's titles, permits, gear tiers and quest surface come
          free with the vessel and need no `MayRequire` gate at all.
          🔑 Blast radius: **the Empire's vessel only.** Other `OuterRim_*` defs — pawn
          kinds, gear, the droid factions — are untouched and staying. Do not sweep by
          the `OuterRim_` prefix.
verify:   a single audit doc exists naming vanilla `Empire` as the vessel, listing what
          is missing for v1, and citing no quarantined file.
criteria: the Empire is buildable from one document without anyone re-deriving which
          faction def it is.
          🔴 **Two checks were "closed" against the wrong def and are now genuinely
          open** — found while propagating the ruling, 2026-08-20:
          1. **The Force-patch xpath for the Empire does not exist.** The old one
             selected on `TabulaRasa` pawnGroupMaker classes; vanilla `Empire` has none
             of them, so the xpath must be re-derived against `Empire`'s own
             `pawnGroupMakers`. ✅ No `PatchOperationFindMod` wrapper is needed — Royalty
             is always loaded.
          2. **`Empire`'s three pursuit-eligibility flags have never been read** —
             `displayInFactionSelection`, `canStageAttacks`, `defName != "PColony"`. The
             eligibility rule survives; only the worked example died with the old def.
          Neither breaks anything today. Both are checks that were passed against a def
          we do not use.
state:    open — raised by REP, 2026-08-20, relaying the owner.

## INHABITED_OPEN_QUESTIONS_1 The five answers BUILD is now waiting on
spec:     🔴 **Raised by the owner's 2026-08-20 reversal** — the code is v1 and is being
          built, so `INHABITED_DESIGN.md` §7's open questions stopped being academic. The
          eight `INHABITED_*` items are filed in `queue/BUILD.md` and seven of them are
          executable; these are the gaps that are DECIDE's and nobody else's.
          ✅ **ALREADY RULED while filing, so BUILD is not blocked on it:** cast size
          distribution, written into `INHABITED_GENSTEP_CAST_SPAWN_1` — hive foundry 14–22,
          waystation 10–16, refinery 8–14, nomad camp 6–12, trade moot 5–9, homestead 4–7,
          droid enclave 3–6.
          ⏳ **STILL OWED, in the order BUILD will hit them:**
          1. 🔴 **The four missing character fields — xenotype, pawnKind, apparel, skills.**
             None of the 269 authored characters carries any of them; the prose has name,
             race-as-a-string, gender, age, traits, two backstory lines and a hook.
             `CAST_ROSTER_MACHINE_READABLE_1` is building the parser around the gap with
             those four left optional and empty. ⛔ **Nobody may guess them** — a guessed
             xenotype ships a wrong-looking person into a world that is frozen.
             ⚠️ The right instrument here is a `review-sheets` build, not 269 questions in
             chat: pre-fill every one from the prose and let the owner disagree.
          2. **The twelfth faction has no cast.** Deepwater Compact (*the Balance*) is
             tabled at `INHABITED_DESIGN.md:485-497` and has no `INHABITED_CAST_*.md`
             beside the other eleven. ~25 characters, DECIDE's own authoring.
          3. **How the player initiates trade** with a cast that is not a settlement (§7).
          4. **What the gravship's arrival triggers** — which casts break on sight, on what
             test (§7). This is FATE:flee-arrival and no item can implement it yet.
          5. **Whether a place can be re-occupied by a DIFFERENT faction** after
             abandonment. `state: Squatted` is reserved for it in
             `INHABITED_WORLD_OBJECT_CORE_1` and is unspecified.
          ⛔ **Do NOT answer 3, 4 or 5 before `ROSTER_SURVIVES_OFFMAP_PROOF_1` reports.**
          §3.4 says that soak can invalidate the container choice, and all three answers
          are shaped by whether the roster is genuinely frozen.
verify:   each of the five is either ruled in writing or struck as void, and the ruling is
          written INTO the item in `queue/BUILD.md` that waits on it — not only here.
criteria: —
⭐ **BUILD's return, overnight 2026-08-20 — item 1 is now the ONLY thing blocking content,
          and the instrument for it exists.**
          - `CAST_ROSTER_MACHINE_READABLE_1` is **done**. All 269 characters are
            `Inhabited.CharacterDef`s in `src/Jawa/Inhabited/Defs/CastRosters/`, and all
            **807 traits and every named degree resolve** against the def dump. The four
            fields are emitted empty, as instructed.
          - ⇒ **The `review-sheets` build you wanted has a real data source now.** It does
            not need to parse prose: read the 269 defs, show `label · race · ageText ·
            traits · hook` per row, and collect the four missing fields. The prose files
            stay the source of truth for everything else.
          - 🔑 **A pre-fill hint that costs nothing:** `race` is already a clean prose
            string per character (`Ugnaught`, `Chagrian`, `B1-series line infantry`), so
            xenotype and pawnKind can be pre-filled by grouping on it — there are far fewer
            distinct races than characters, and the owner then disagrees per RACE rather
            than per person.
          - ⚠️ **The spec's measurement that age is an int on every entry was wrong** and
            the parser now handles eight forms, including the Jawa robe-hem count and one
            droid who lies about his age. Detail is in `CAST_ROSTER_MACHINE_READABLE_1`.
            Nothing for DECIDE to rule; noted so the same measurement is not trusted twice.
          - 🔑 **Item 2, Deepwater, is reported cleanly by the tool every run** rather than
            failing it, so writing that cast is unblocked whenever you want it.
          - 🔴 **Items 3, 4 and 5 stay correctly held** behind the soak. BUILD found and
            fixed TWO of the three ways the container could have failed, both on disk, so
            the soak is now a narrower and more honest test than when this was written —
            see `ROSTER_SURVIVES_OFFMAP_PROOF_1`.
state:    ready — for DECIDE

## CAST_TRAIT_CONFLICTS_1 Fourteen authored characters cannot exist
row:      inhabited
from:     BUILD, 2026-08-20, found while the game was live. Offline check, two sources.
spec:     🔴 **14 of the 269 authored characters carry a pair of traits RimWorld declares
          mutually exclusive.** Not a style note — `TraitDef.ConflictsWith` says these
          cannot coexist, and no vanilla pawn generation could ever produce them.

          | defName | who | the pair |
          |---|---|---|
          | `Inhabited_Empire_SchoolmistressPerrinAleth` | Schoolmistress Perrin Aleth | `Abrasive` + `Kind` |
          | `Inhabited_Empire_ComptrollerIshOndoVell` | Comptroller Ish Ondo Vell | `Jealous` + `Ascetic` |
          | `Inhabited_Geonosian_RrekkTheReturned` | Rrekk the Returned | `Brawler` + `ShootingAccuracy` |
          | `Inhabited_Geonosian_AttendantQuRaa` | Attendant Qu'raa | `Ascetic` + `Jealous` |
          | `Inhabited_Helix_PrithVane` | Prith Vane | `Psychopath` + `Kind` |
          | `Inhabited_Homestead_BessaTrull` | Bessa Trull | `Abrasive` + `Kind` |
          | `Inhabited_Homestead_RenAshek` | Ren Ashek | `Psychopath` + `Kind` |
          | `Inhabited_Jawa_OssikTheOutrider` | Ossik the Outrider | `Brawler` + `ShootingAccuracy` |
          | `Inhabited_Junkers_AtaiVosk` | Atai Vosk | `Jealous` + `Ascetic` |
          | `Inhabited_Tusken_HarraGhul` | Harra Ghul | `Ascetic` + `Jealous` |
          | `Inhabited_Tusken_OrrGash` | Orr'gash | `Kind` + `Abrasive` |
          | `Inhabited_Tusken_ShaaNel` | Shaa Nel | `Ascetic` + `Jealous` |
          | `Inhabited_Tusken_EssKan` | Ess'kan | `Kind` + `Abrasive` |
          | `Inhabited_Wildsteam_NikkoTheSapNamer` | Nikko the Sap-Namer | `Kind` + `Abrasive` |

          Only four pairs are involved, so this is four decisions and not fourteen:
          `Kind`↔`Abrasive` · `Kind`↔`Psychopath` · `Ascetic`↔`Jealous` ·
          `Brawler`↔`ShootingAccuracy`.
          🔑 **Read each one's HOOK before choosing** — the project's own rule is that the
          hook and the traits must agree, and *"a hook the mechanics do not back is a lie
          the player will catch."* In most of these the hook plainly favours one side; e.g.
          a schoolmistress written as sharp-tongued-but-decent is `Kind` if the warmth is
          the point and `Abrasive` if the sting is.
          ⚠️ **`Ascetic` + `Jealous` is four of the fourteen and looks like a house habit
          rather than four separate slips.** Both read as "wants nothing / resents what
          others have", so a writer reaches for the pair naturally. Worth a note in the
          cast-file format section, not just fourteen edits.
          ⛔ **BUILD is not choosing.** Picking a winner is authoring, and the trait is
          half the characterisation.
          FIX: edit the `traits:` line in `design/Jawa/bridge/INHABITED_CAST_*.md`, then
          `python3 src/RimMandrake/Utils/cast_to_xml.py --write`.
verify:   after the edit, `cast_to_xml.py` still reports 269 and every trait resolving, and
          BUILD's conflict audit returns 0.
criteria: no `Config error in Inhabited_` naming an IMPOSSIBLE PAIR at the next load.
state:    ready — for DECIDE

          ⚠️ **HOW THIS SURVIVED THE FIRST LOAD, and why nobody saw it.** RimWorld enforces
          none of it: `TraitSet.GainTrait` checks no conflicts and imposes no trait cap, so
          these 14 loaded with zero errors and would have produced pawns silently. It was
          found only because the `rimbridge` skill's silent-failure catalogue names
          `GainTrait` explicitly. **The code no longer permits it:** `CharacterDef.
          ConfigErrors` now names any conflicting pair at load, and `CharacterApplier`
          refuses the second trait rather than building an impossible pawn. So the 14 are
          now LOUD but still WRONG — the code stopped the damage, it did not do the edit.

## FACTION_ART_SPEC_1 Spec the world-map and faction art for all twelve, from Star Wars canon
row:      9
from:     🔴 THE OWNER, 2026-08-20, in his own words: *"Please ask DECIDE to spec out Art for
          all the factions and give them to BUILD for implementation. That's a GREAT idea.
          Search Star Wars canon for inspiration here."*
          Raised because `AM_EnemyPirate` (the Blackstar Company) shipped with a NULL
          `settlementTexturePath` and threw `ArgumentNullException` once per settlement per
          frame — TPS 60 → 3.7. The crash fix is filed separately to BUILD as
          `BLACKSTAR_HAS_NO_SETTLEMENT_ART_1` and must NOT wait on this spec.
what:     Every faction that holds ground on Ash'karr needs art that reads at a glance on the
          world map. Right now eleven of twelve share `World/WorldObjects/DefaultSettlement`
          — the same generic hut — and the twelfth has nothing at all.
          THE TWELVE, with their holdings, in size order:
            Homestead Defense League 13 · Deep Desert Tribes 9 · Hutt Cartel 8 ·
            the Junkers 8 · Jawa Trade Moot 7 · Geonosian Foundry Hive 5 ·
            Deepwater Compact 5 · Blackstar Company 4 · Wildsteam Clan 4 ·
            The Galactic Empire 3 · Free Droid Enclaves 3 · Ascendant Helix 3
decide:   For each faction, a written art brief BUILD can implement without asking twice:
          1. **settlementTexturePath** — the world-map icon. This is the one that matters
             most: it is what the player reads a hundred times a session.
          2. **factionIconPath** — the roster/relations icon.
          3. Whether the faction warrants its OWN sprite or can share a themed vanilla one.
             ⚠️ Be honest about which ones are worth the art. Twelve bespoke icons is a lot
             of sprite work and the Empire and the Hutts earn it more than a three-holding
             enclave does.
          4. The CANON hook per faction, since the owner asked for it explicitly — Hutt
             Cartel, Geonosians, the Empire and the droid enclaves all have real Star Wars
             visual language to draw on. The Jawa Trade Moot and the Homestead Defense
             League are ours and need inventing.
constraints:
          🔑 **A faction absent when he builds the world is absent from every player's game
          forever** — but ART is not in that class. A texture path can be patched later; it
          is not frozen at worldgen. So this is not a worldgen blocker and must not be
          treated as one.
          📌 `generating-rimworld-sprites` is the skill for producing them, and it has the
          canvas and alpha constraints that make a sprite actually load.
          ⛔ Do not spec art for `AM_EnemyPirate` that BUILD cannot ship — it is a
          THIRD-PARTY def and must be reached by patch, not by editing the mod.
state:    ready
