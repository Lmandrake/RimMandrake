# DECIDE inbox.

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

## D26 The Eyeling becomes the Jawa clan's pet — v1
row:      12
spec:     Owner, 2026-08-15, from the animal contact sheet: *"AA_Eyeling MUST be
          made into a star-wars-style pet for the starting Jawa clan to keep!"*
          `AA_Eyeling` (Alpha Animals). This is a v1 CONCEPT, not `[v2]`.
          Owed by DECIDE, in this order:
          (a) a name and one line of fiction that makes it read Star Wars rather
              than Alpha Animals — the sprite stays, the identity changes. A
              rename is a `PatchOperationReplace` on `label` plus `description`;
              art is untouched, so this costs nothing to try.
          (b) whether it is bonded to a NAMED founder or unowned in the starting
              save. `SCENARIO_SPEC.md` gives Yeku `Animals 5` and a pack animal —
              if the Eyeling is his, that slot is already there.
          (c) trainability and whether it fights. Read its shipped
              `race/trainability` and `wildness` first; do not invent them.
          (d) where it appears in the wild, into
              `design/Jawa/worldbuilding/fauna_placement.md` — a clan pet the
              player can never find a second one of is a dead end.
          ⚠️ It must be in the STARTING SAVE, so it lands with `B55` (the campaign
          start) and therefore before the owner's world is finished.
verify:   `AA_Eyeling` is not in the Cherry Picker cut list; the rename patch
          validates; the name and fiction are written into `SCENARIO_SPEC.md`.
criteria: the clan starts with the pet, and it reads as belonging to this
          campaign rather than to Alpha Animals.
state:    ready

## D30 Six rulings the next session must get from the owner
row:      0
spec:     Parked 2026-08-15. None block each other; all block something.
          **Worldgen-critical, answer before step 10:**
          (1) **What carries the Pyrelands?** Vanilla `Savanna` and `Grasslands`
              are cut and `ZBiome_Grasslands` ("stormy savanna") is kept. If
              deliberate this is ideal — it already carries `DryThunderstorm` at
              commonality 2. If not, the cut must be reversed.
              (`biome_review_comments.md` §1)
          (2) **The three wet biomes** — `AB_FeraliskInfestedJungle`,
              `AB_MiasmicMangrove`, `COMIGO_GreaterSwamp_Tropical` — are fine as
              R-H1's narrow flood margin and wrong as regions. Needs a placement
              ruling, not a patch.
          (3) **`Glowforest` as the LIVING half of the nightside glow?** R-H6c
              left alive-vs-mineral open; taking it gives that band two textures.
          **Not worldgen-critical:**
          (4) **`BTD_Jawa` → which def?** Two live Jawa xenotypes, each holding a
              different half of the clan's canon (`FACTION_SPEC.md` R28a). 16
              references left deliberately unpointed. This is `D23`'s merge.
          (5) **Confirm `RimMandrakeRakata` as the ancient enemy** — DECIDE
              proposed it (`the_forgotten_war.md` R-W3); the owner names it.
          (6) **The Rust Cathedral's hazards and the Enclave goodwill cost must be
              set TOGETHER** (`the_forgotten_war.md` R-W4), and R-H10's biome
              temperature edits REOPEN chain step 8, which is ratified — that
              needs a ruling rather than a patch.
verify:   each of the six is either answered in a design doc or explicitly
          re-parked with a reason.
criteria: none — offline.
state:    ✅ 4 of 6 CLOSED 2026-08-15 by the owner. (5) and (6) remain.
          (1) **PYRELANDS → `ZBiome_Grasslands`, and it must come OFF the blacklist.**
              🔴 The question's premise was FALSE ON DISK. `biome_review_comments.md` §1
              says stormy savanna is "kept"; `JawaWorld_BiomeMix.xml` blacklists all
              THREE — `Savanna`, `Grasslands` AND `ZBiome_Grasslands`. Blacklist is a
              hard predicate; no score can rescue it. Owner: it *"forms the barrier
              between the very wet biomes and the dry desert"*, plus **ash storms**.
              ⇒ BUILD item `pyrelands-off-the-blacklist-and-ash-storms-5d2e71`.
          (2) **WET BIOMES → narrow flood margin. ALREADY IMPLEMENTED, ratified.**
              All three sit at `RARE -4` today. No work.
          (3) **GLOWFOREST → isolated pockets of glowing life in an otherwise utterly
              black nightside.** ⛔ **NO ITEM. Not ours.** See the standing ruling below.
          (5) **ANCIENT ENEMY → ⛔ DEFERRED TO v2.** The owner declined to name
              `RimMandrakeRakata`. B61 parks; the frozen Ancients ship vanilla.
          (6) **R-H10's biome TEMPERATURE edits → ⛔ DEAD, no item.** They tune what the
              world contains, and chain step 8 is ratified. The OTHER half — the Rust
              Cathedral's hazards and the Enclave goodwill cost, which must be set
              TOGETHER — is STILL OWED and is the last thing genuinely outstanding
              before the owner builds his world: `startingGoodwill` bakes into the save
              he freezes, and there is no regenerate behind it. DECIDE brings a proposal.
          (4) `BTD_Jawa`'s 16 unpointed references — reopened by D23's closure, see
              `btd-jawa-has-no-merge-to-wait-for-8c40b2`.
🔴 STANDING RULING (owner, 2026-08-15, verbatim): *"The user will make the world,
          don't worry about it. Manual worldgen, remember? No auto worldgen items
          please!"* ⇒ **We do not file items that TUNE what the world contains** —
          commonality, tier, latitude band, how much of a biome appears. He rolls seeds
          and picks one he likes by eye. We file only what is ENABLING: a blacklisted
          biome can never appear in ANY seed, and a def that fails to load is not a
          choice he can make. Everything else is his at the map screen.
          (This is the same ruling that killed D2, D4, C15 and C16. It was re-derived
          and re-violated on 2026-08-15; recorded here so it stops happening.)

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

## seven-factions-have-no-required-count-9c4e17
row:      —
from:     BUILD, 2026-08-15, measured on disk while the game was down
spec:     🔴 **A scope call only DECIDE can make, and worldgen is the last chance to
          make it.** Seven of the eight authored Jawa FactionDefs carry
          `canMakeRandomly true` and **no `requiredCountAtGameStart`**, so they
          arrive on the Configure Factions page at a default count of **0** and a
          world generated without touching them contains none of them.
          Measured, all 8 files in `src/Jawa/Jawa_Patches/Defs/FactionDefs/`:

          | faction | defName | requiredCountAtGameStart | settlementGenerationWeight |
          |---|---|---|---|
          | Jawa Trade Moot | `Jawa_IndigenousTribes` | **1** (max 2) | 1.0 |
          | Hutt Cartel | `Jawa_HuttCartel` | — (max 1) | 1.15 |
          | the Junkers | `Jawa_Junkers` | — | 1.15 |
          | Deepwater Compact | `Jawa_DeepwaterCompact` | — | 0.7 |
          | Geonosian Foundry Hive | `Jawa_GeonosianFoundryHive` | — | 0.7 |
          | Wildsteam Clan | `Jawa_WildsteamClan` | — | 0.6 |
          | Ascendant Helix | `Jawa_AscendantHelix` | — | 0.45 |
          | Free Droid Enclaves | `Jawa_FreeDroidEnclaves` | — | 0.45 |

          🔴 **`EXPECTED_FAILURES` §2 S7 asserts the opposite** — "Seven are authored
          defs with `requiredCountAtGameStart 1`, so they should be forced". That is
          FALSE on disk and it is written into the file that gets read AT worldgen.
          Corrected in place by BUILD 2026-08-15; recording it here because the
          wrong belief may have travelled into other docs.
          THE CHOICE: (a) add `requiredCountAtGameStart 1` to the seven, so the
          campaign's own factions cannot be forgotten at the screen; or (b) leave
          them optional and rely on the operator ticking each up by hand.
          ⚠️ **(b) is one distraction away from a world with no Hutts in it, and the
          world is generated once — a faction absent at worldgen cannot be added
          later.** BUILD recommends (a) and can implement it in minutes, offline.
verify:   —
criteria: —
state:    ready — 🔴 **RULED 2026-08-15 AND NEVER IMPLEMENTED. Re-measured 2026-08-19.**
          The ruling was (a): add `requiredCountAtGameStart 1` to all seven. Measured on
          disk today across all 8 files in `src/Jawa/Jawa_Patches/Defs/FactionDefs/`:
          **only `JawaTribes.xml` carries the field — and it is the one that already had
          it.** Seven still default to 0. Filed to BUILD as
          `seven-jawa-factions-still-default-to-zero-at-worldgen-4a71c8`.
          A world is generated ONCE and a faction absent at worldgen can never be added.
          ⭐ **BUT THE MEASUREMENT FOUND A SECOND, STRONGER MECHANISM, and it changes what
          this item is.** The Worldbuilder preset carries an explicit faction roster —
          `factionCountsStrings`, 27 entries, **15 of them ours**: Jawa_IndigenousTribes 3,
          Jawa_WildsteamClan 2, Jawa_Junkers 2, Jawa_HuttCartel 2, Jawa_FreeDroidEnclaves 2,
          Jawa_DeepwaterCompact 2, Jawa_GeonosianFoundryHive 1, Jawa_AscendantHelix 1.
          ⇒ **The preset PREFILLS the Configure Factions page. That is the primary
          mechanism and `requiredCountAtGameStart` is the backstop.** Both should be right:
          the def field costs nothing, survives independently, and is the only one left if
          the preset is ever lost.
          🔴 **AND THE PRESET IS EXACTLY WHAT IS BEING LOST.** It is destroyed at every
          launch where it currently sits (BUILD
          `worldbuilder-preset-is-wiped-at-every-launch-not-just-on-steam-updates-6b1e4d`).
          Losing it silently loses **the faction roster, MLP subcount 7 and coverage 1.0 —
          all three at once.** That one file is now the most load-bearing artifact in the
          campaign, and it lives in a directory another program deletes on startup.

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

## D-MUTATOR-VEHICLE  Tile mutators ARE our content-injection mechanism — v1
state:    ✅ **v1 — RULED 2026-08-19. The measurement came back YES, so the owner's
          condition is met.** *"Leave this until we know whether we can change mutators via
          the live bridge."* We know. Read off `Assembly-CSharp.dll`, 2026-08-19:

          🔑 **THE MEASUREMENT — mutators are writable at runtime, and it is not close.**
          · `Tile.mutatorsNullable` is a **public, directly settable** `List<TileMutatorDef>`.
          · `Tile.AddMutator(def)` and `Tile.RemoveMutator(def)` are **public**.
          · **Worldgen itself uses the same public method** — `WorldGenStep_Mutators` →
            `AddMutatorsFromTile` → `TryAddMutator`, whose body is `tile.AddMutator(...)`.
            We are not sneaking in a side door; we are using the front one.
          · **The game already does this outside worldgen**: `Site.cs:310`,
            `QuestNode_Root_AncientStructure`, `QuestNode_Root_AncientMercenaries`, and the
            dev menu's add/remove-mutator actions. This is a supported runtime operation.
          · **Nothing snapshots at worldgen.** `MapGenerator.GenerateMap` reads
            `map.TileInfo.Mutators` LIVE to concat `extraGenSteps` and filter
            `preventGenSteps`; so do `GenStep_Mutator*`, `WildPlantSpawner`,
            `WeatherDecider` and `RaidStrategyWorker`.
          · **It serializes.** `SurfaceLayer.tileMutatorTiles` / `tileMutatorDefs`, written
            through `SerializeMutators()` on save and rebuilt on load. Our writes ship.

          🔴 **AND THE LEGALITY GATE DOES NOT APPLY TO US.** `TileMutatorDef.IsValidTile`
          — every biome whitelist, hilliness, temperature and `canSpawnOnRiver/Road/Landmark`
          check — is called **only from `TryAddMutator`, the ROLL path. `AddMutator` never
          calls it.** It enforces category/priority arbitration and nothing else. ⇒ We can
          place mutators the generator would never roll. That is precisely the injection
          hook this item was asking for, **and it is a footgun in the same breath.**

          ⇒ **RULING, the four questions this item posed:**
          1. **SUFFICIENT, not a stopgap — for this campaign.** The real limit is that
             mutators act at MAP generation and cannot alter a map already generated. On a
             frozen shipped world every tile but the start is unvisited, so that limit costs
             us almost nothing. ⭐ `extraGenSteps` / `preventGenSteps` mean anything a
             GenStep can build, a mutator can summon on a chosen tile.
          2. **Whitelist: our own defNames are auto-whitelisted, by default, from the day
             the first one is authored.** The trap is real and unchanged.
          3. **BOTH, and the split is a rule, not a preference: a NAMED place is a
             `LandmarkDef`** (it forces its mutators and puts a name on the world map);
             **unnamed regional character is a bare `TileMutatorDef`.** §13.2 —
             a landmark has no biome field, so its legality is its Required mutator's.
          4. **Frozen-world consequence: resolved.** Reads are live at map-gen, so a mutator
             added at any point before the player reaches a tile takes full effect. Placement
             after shipping reaches every unvisited tile — which is nearly the whole planet.
          🔴 **NEW STANDING RULE, because the engine will not stop us:** the importer
          **validates against `IsValidTile` itself before placing**, and any deliberate
          violation is recorded as deliberate. An illegal placement is silent — no error, no
          log line — and its `Worker.Init` may expect state worldgen would have set.
          ⭐ **This also closes §13.1's open end.** `RemoveMutator` is public, so the ban on
          `Dunes` at the setdown and its neighbours is enforceable exactly as
          `ASHKARR_WORLD_DEFINITION.md` §13.1 requires — clear it after vanilla's order-700
          roll, which under the bridge route has already happened when we arrive.
          ⚠️ Two caveats, both cosmetic and both measured: `Tile.hillinessLabelCached` is
          not invalidated by `AddMutator`, so a late add can show a stale label until
          reload; and a mutator whose worker expects worldgen-set state (coast direction,
          say) may render oddly on an unsuited tile.
          ⇒ **Follow-on, now unblocked:** the companion's batch tile setter gains mutator
          add/remove (§12.2), and DECIDE authors the first defs. Filed to BUILD as part of
          the importer, not as a separate pipeline.

the proposal:
          Do not invent a content-injection system. **`TileMutatorDef` is already the
          game's per-tile content mechanism**, so author our own and place them, rather
          than building a parallel pipeline we would then have to maintain against 1.7.

why it is credible — measured today, not assumed:
          · **336 `TileMutatorDef`s exist across 9 mods**, so the pattern is well-trodden
            and every one of them is a worked example we can copy.
          · They carry REAL mechanics, not decoration: `animalDensityFactor`,
            `plantDensityFactor`, **`junkDensityFactor`** (the Jawa salvage lever),
            `geyserCountFactor`, `chunkDensityFactor`, `fishPopulationFactor`,
            `additionalWildPlants`, `hillinessForOreGeneration`, and — least obvious —
            `allowRoofedEdgeWalkIn`, `blacklistedRaidStrategies`,
            `additionalGameConditions`, which change how raids reach a colony.
          · 🔑 **`extraGenSteps` / `preventGenSteps` let a mutator invoke or suppress
            arbitrary `GenStepDef`s.** That is the actual injection hook: anything a
            GenStep can build, a mutator can summon on a chosen tile. This is the single
            strongest argument that mutators may be sufficient on their own.
          · ⛔ ~~Placement is already solved offline… writing them is the same shape as the
            biome write that is already proven end to end.~~ **FALSE, twice over, and
            struck 2026-08-19.** The offline biome write was never proven — it produced
            **two dead loads** and the owner killed savegame writing on 2026-08-18;
            `worldmap.py` now refuses to write. The encodings above are still accurate as
            a description of the SAVE FORMAT and are worth keeping for that.
            ⇒ **Placement is a BRIDGE write, like every other tile field.**
          🔴 **AND THE ORDERING CHANGED, which bears directly on question 1.** Vanilla's
            Mutators step (700) and Landmarks step (650) run against the VANILLA planet
            and have finished before we stamp a single tile — `ASHKARR_WORLD_DEFINITION.md`
            §12.3, and §13.3 has been corrected to agree. So our mutators are not competing
            with vanilla's roll at generation time; the importer clears and re-rolls after
            the stamp. That removes the arbitration worry from question 1 and replaces it
            with a plainer one: **whatever we place, we place last.**
          · Authoring one is ordinary XML; a custom `workerClass` is optional C#.

what the decision has to settle:
          1. **Are mutators sufficient, or a stopgap?** They act at MAP GENERATION on a
             tile. They do not change the world map itself, and they do not touch a map
             that has already been generated. If we need to inject into a live or
             already-visited map, this is the wrong vehicle and something else is needed.
          2. **Whitelist interaction.** Our posture is whitelist-strips-everything-else.
             Our OWN mutators must be auto-whitelisted, or the curation pass will quietly
             delete our content. This is a real trap, not a hypothetical.
          3. **Do we author `TileMutatorDef`s, `LandmarkDef`s, or both?** A landmark is a
             chooser that forces mutators and adds a named map marker — it is the right
             wrapper when the thing should be VISIBLE and named on the world map.
          4. **Frozen-world consequence.** Placements bake into the shipped save. A
             mutator added after the world is built reaches only unvisited tiles.
⇒ if YES, the follow-on work is small and known: author defs, ⛔ ~~extend `worldmap.py` to
          write the mutator arrays~~ **— no: add a mutator write to the companion's batch
          tile setter (§12.2), the same door every other tile field uses** — and add our
          defNames to the whitelist by default.

## D-TODO-WORLDMAP-ART  Compare GRiNDTerra vs World Map Enhanced by LOOKING
state:    ✅ CLOSED 2026-08-19 — **OWNER: *"Use GrindTerra, close out."*** Filed to BUILD
          as `grimterra-worldmap-over-wme-as-the-base-layer-2c8f19`.
🔴 **AND MY OWN ADVICE IN THIS ITEM WAS WRONG. Correcting it rather than quietly
          dropping it, because the wrong half is the memorable half.** This item said
          *"They CONFLICT — both ship a PNG at the same literal path, so running both
          silently mixes two artists across one planet. **Never both.**"* ⛔ The conflict is
          real; **"never both" does not follow, and it is the wrong call.**
          The two are not competing full sets. Measured 2026-08-19:
          · **GRimTerra World Map ships 40 PNGs. WME ships 231.** GRimTerra is a partial
            set with a strong opinion; WME is broad coverage.
          · Against OUR authored planet, GRimTerra covers **76.1%** of tiles and leaves
            **23.9%** — and the gap is not obscure filler:
              Wasteland 7.8% (the salt pans) · **Ocean 6.7% — every sea we have** ·
              PoisonForest 2.9% · ZBiome_DesertOasis 2.1% (the Hutts' oases) · Lake 1.4% ·
              BMT_FungalForest 1.1% · AB_MechanoidIntrusion 1.1% (the Rust Cathedral) ·
              BMT_CrystalCaverns 0.6% · Volcano · LavaField.
          ⇒ Removing WME does not give one artist. It gives **GRimTerra plus VANILLA**
          across a quarter of the planet, including all the water — which is the most
          eye-catching thing on a desert world's map.
          ⭐ **RimWorld resolves textures PER FILE, last mod wins per file — which is a
          LAYERING mechanism, not only a collision.** ⇒ **Load WME first as the base coat,
          GRimTerra after it.** GRimTerra wins on all 40 it ships; WME covers the rest
          instead of vanilla. That delivers the owner's ruling exactly — GRimTerra's art is
          what he sees wherever GRimTerra has an opinion — without dropping the seas.
          ⚠️ Two name corrections that will otherwise waste someone's time: the mod is
          **GRimTerra**, not GRiNDTerra, and the world-map mod is `GRimTerra.Worldmap`
          (3546956014, **not currently active**) — NOT `grimterra.biomesmod` (3537211820),
          which is a different, already-active mod that adds biomes.
          ✅ **The dependency worry that drove the old recommendation was FALSE.**
          `GRimTerra.Worldmap` declares an **EMPTY `modDependencies`**, ships no assemblies,
          and gates its Odyssey/AlphaBiomes folders with `IfModActive`. **A recipient of our
          savegame needs nothing new.** The Odyssey+Biotech+VEF requirement belongs to the
          sibling *Biomes* mod, which is already active anyway.
          ⭐ The ReGrowth free win is confirmed and folded into the BUILD item.
why it is open:
          Researched 2026-08-16: **nobody has ever compared them.** GRiNDTerra (3546956014)
          has 8 comments, none about appearance, 1,687 subs. World Map Enhanced
          (3599967849) has 26,504 subs — but that is age and the author's name, not a
          beauty verdict. No reddit thread, no showcase, no side-by-side exists.
the facts that do NOT need taste:
          · 🔴 They CONFLICT — both ship a PNG at the same literal path
            (`World/Biomes/Desert`). RimWorld resolves per file, later mod wins per file,
            so running both silently mixes two artists across one planet. **Never both.**
          · WME covers our whole stack **including Advanced Biomes**, which GRiNDTerra
            does NOT — those tiles would fall back to flat vanilla art. Inconsistent art
            across one planet is worse than uniformly plainer art.
          · WME is pure art (229 PNGs, no defs, no DLL, nothing enters a save) and needs
            no dependencies. GRiNDTerra needs **Odyssey + Biotech + VEF**, which every
            recipient of our shipped savegame would also need.
⇒ current call: KEEP World Map Enhanced. To judge for real: subscribe GRiNDTerra,
          DISABLE WME, look at our own planet once, decide.
⭐ FREE WIN, unrelated to the comparison and worth doing now: ReGrowth 2's setting
          `RG_WorldmapTextures` repoints **Tundra and AridShrubland** to its own art,
          overriding WME. On a desert planet AridShrubland is a main tile. **Turn that
          ReGrowth setting OFF and WME's arid art appears.**


## five-design-gaps-found-auditing-the-seven-authored-factions-3c81ea
row:      9
from:     BUILD, 2026-08-19, while closing B45–B51. All five are DESIGN calls with no
          value anywhere in the repo, so BUILD did not invent one. None of them blocks
          the files, which are otherwise built and validate clean.
spec:     (a) 🔴 **`maxCountAtGameStart` is on the authored-faction contract and is absent
              from seven of the eight defs.** `FACTION_SPEC.md` §"An authored faction"
              lists it in the generation group but no per-faction section gives a number.
              Only `Jawa_HuttCartel` (1) and `Jawa_IndigenousTribes` (2) have one. Every
              faction now carries `requiredCountAtGameStart 1`, which is the FLOOR;
              nothing caps them, so worldgen may field several Foundry Hives.
              ⇒ needs a number per faction, or a ruling that uncapped is intended.
          (b) 🔴 **The Geonosian Foundry Hive's TWO OUTPOSTS ruling is not expressed in
              the def**, and no `FactionDef` field expresses it. The 2026-08-17 ruling
              gives the hive two distinct outposts (ore seam · plateau);
              `settlementGenerationWeight 0.7` produces one undifferentiated cluster of
              about five. The ruling's Free-Droid-Enclaves alliance reversal is also
              unexpressed, and R1 forbids a goodwill number, so it needs a hard-coded
              relation somewhere. ⇒ either the ruling needs a mechanism or it needs
              downgrading to fiction.
          (c) **`Jawa_HuttCartel`'s `ideoDescription` is NOT the text in
              `faction_religions_spec.md` entry 2**, though the file's comment claims it
              is verbatim. Spec: "Everything on this world evaporates, freezes, or is
              stolen…"  File: "Everything is owed. The water you drank this morning…".
              The spec's Decision precept `Execution_Required` is also absent — only the
              blacklist is present. ⇒ which text is canon?
          (d) **`Jawa_FreeDroidEnclaves` fields a biological species.** §5 calls it 0%
              biological and the file's own comment says the `xenotypeSet` is "EMPTY ON
              PURPOSE", but it carries `RimMandrakeUgnaught 1.000`. ⇒ intended
              (droid-keepers) or a paste error?
          (e) **Baseliners generate in five factions and the files used to deny it.**
              Measured chances: Helix 0.083 · Junkers 0.047 · Wildsteam 0.028 ·
              Deepwater 0.022 · Hutt 0.014. The comment claiming "they sum to 1.00 so no
              baseliner generates" was false and has been corrected in all five; the
              NUMBERS were left alone. ⇒ plain humans on a Star Wars planet: intended?
verify:   n/a — this is a request for five values, not a build.
criteria: n/a
state:    ready

## the-trade-moot-wears-the-player-faith-and-the-spec-never-said-so-9d21f7
row:      6
from:     BUILD, 2026-08-19, auditing B54. Not a defect that stops anything — a call that
          nobody has made in writing.
spec:     `faction_religions_spec.md` has eleven entries and says section 12, the Jawa, is
          **deliberately empty** because the player faith ships as
          `src/Jawa/ideoligion/The Salvation.rid`. But
          `src/Jawa/Jawa_Patches/Defs/FactionDefs/JawaTribes.xml` (`Jawa_IndigenousTribes`,
          label "Jawa Trade Moot") carries `<ideoName>The Salvation</ideoName>` with
          `fixedIdeo true` and five `forcedMemes`, and no `ideoDescription`.
          It reads as deliberate — the Trade Moot is Jawa, so it wearing the Jawa faith is
          coherent, and `fixedIdeo` stops worldgen rolling a random faith over an NPC
          faction we care about. But **the twelfth faith is the one the spec explicitly
          declined to author**, so this is authored content with no ruling behind it and no
          description text.
          ⇒ (a) confirm the Trade Moot keeps The Salvation, and give it an
          `ideoDescription`; or (b) give it its own faith; or (c) strip the block and let
          worldgen roll one.
          🔑 It has the same hard deadline as the rest of B54: an ideo is generated once,
          at world creation.
          FIXED already, needing no ruling: three of the five memes are modded
          (`sarg.alphamemes`, `vanillaexpanded.vmemese`) and carried no `MayRequire`.
          They do now.
verify:   n/a — a ruling, not a build.
criteria: n/a
state:    ready
