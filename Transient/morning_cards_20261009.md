# Morning question-card drafts, 2026-10-09

Drafts only; nothing asked. Each set is up to 4 questions. Time line to be printed from date at ask time.

# SET 1 - Art keeps and the Return Gallery schematic (4 questions)

Sources: `Transient/belt_art4_20261009.md`, `Transient/belt_art5_20261009.md`, `src/RimMandrake/DivingInteraction/Defs/ThingDefs_Items/RM_ReturnGalleryRewards.xml`, `src/RimMandrake/DivingInteraction/Source/RM_MapComponent_ScaldImmersionBerth.cs`, `design/Jawa/worldbuilding/biomes/the_scald_floor_sitting_agenda_2026-10-02.md`.

## Q1.1 Schematic (asked twice before, unanswered; he said "I would need more context")

Lead-in: Solving the Scald's Return Gallery puzzle opens a locker that hands out two items: an "immersion-engineering schematic" and a heat log. The heat log is just lore. The schematic is a stub today: it sits in the colonist's inventory and does nothing. Nothing written says what it should do. Separately, the Scald already has a "parked ship slowly heats up" rule (built, not yet proven in play): each room warms in proportion to how much of its wall touches open water, and ordinary coolers and power are the only counter. The sitting that invented the gallery said the schematic is "discoverable technology", but never picked what.

- Header: `Schematic`
- Question: What should the immersion-engineering schematic do when a colonist has it?
- Option A, "Cheaper hull cooling": reading it cuts the parked-ship heating by a fixed share (say a third) for that colony. Buys: a direct reward that answers the problem the Scald poses, tiny build (one multiplier on code that exists). Costs: removes some of the Scald's pressure once found; pure number, nothing new to see.
- Option B, "Unlocks a new cooler" (Recommended): research-style unlock of one new buildable, a hull-mounted immersion cooler that is much stronger than a vanilla cooler but only works on hull edges touching water. Buys: a visible new building and a reason to design the ship around it; fits "the Cathedral crews did this". Costs: needs a new building def, art, and a recipe gate; the most work of the three.
- Option C, "Keepsake only": the schematic is a valuable trade/ lore item, sold or displayed, with no mechanic. Buys: zero risk and no balance questions. Costs: the gallery puzzle pays out nothing playable; the item description already promises more.
- Recommended: B, because the puzzle is about understanding a coolant circuit and the reward should be a coolant machine.

## Q1.2 Venomvine art (the kept thicket picture)

Lead-in: You kept one thicket picture of the venomvine. Since then about eleven venomvine plants have been using a copy of that same picture as a placeholder until each got its own art. Four finished own renders are waiting (Strangler, Weeper, Sleeper, Lure) plus six earlier ones and a Sleeper-awake one. The art system refuses to replace any slot holding your kept picture without your word. Your kept picture stays on the thicket itself in every option.

- Header: `Venomvine`
- Question: May the new own renders replace the copied thicket picture on the other venomvine plants?
- Option A, "Replace all" (Recommended): every plant that has its own finished render gets it; the thicket keeps yours. Buys: each plant looks like itself, in one pass. Costs: if one of the new renders is worse than the thicket copy, it gets in without a look (the first pass checks only that they look right).
- Option B, "You pick each": I build one sheet pairing each plant's own render beside the thicket copy and you keep/replace per row. Buys: nothing goes in unseen. Costs: another review sheet in the queue; the plants keep sharing one picture until you get to it.
- Option C, "Keep the thicket on all": the shared picture stays everywhere and the own renders are shelved. Buys: consistency with what you approved, no more art work. Costs: about eleven plants look identical, which is what the placeholder was meant to avoid.
- Recommended: A, since you approved the thicket itself, not eleven copies, and the renders were checked for subject and transparency.

## Q1.3 Cistrel and Nubrith art

Lead-in: Two water-edge plants from the canal mod, the red lotus (Cistrel) and the glowing-gill mushroom (Nubrith), both show one kept picture between them, a single image standing in for two plants. Fresh own renders exist for each and look right (a red lotus with a water pool; a mushroom with glowing gills). Replacing needs your word because that picture is owner-kept.

- Header: `Two plants`
- Question: What should happen with the single kept picture shared by Cistrel and Nubrith?
- Option A, "Use own renders" (Recommended): both plants take their own new art; the kept picture is retired from those two slots. Buys: two distinct plants. Costs: you lose the picture you kept on those two plants.
- Option B, "Keep for one, new for other": you tell me which plant the kept picture truly belongs to; the other gets its own render. Buys: preserves your pick where it was meant. Costs: needs a quick look at the picture to decide (I will put it next to both renders).
- Option C, "Keep as is": no change. Buys: nothing risked. Costs: the two plants stay identical, and the good renders go unused.
- Recommended: A, because a single picture was never a ruling for two different plants.

## Q1.4 Leachmoss

Lead-in: Leachmoss had two candidate pictures on the desert sheet: column A and column B. You rejected column A as "redo", and kept column B on 2026-10-07; B is installed. A third, redo-version-2 render has since come out. It is a fine low olive moss mat but would replace what you kept. An earlier note wrongly said nothing kept B; that is corrected.

- Header: `Leachmoss`
- Question: Is column B settled for Leachmoss, or do you want the new version considered?
- Option A, "B is settled" (Recommended): discard the new render; no further work. Buys: closes the item; matches your 10-07 ruling. Costs: nothing but the lost option.
- Option B, "Compare B and new": put B and the new render side by side on a one-row sheet for you. Buys: a real choice if B has bothered you. Costs: one more sheet to look at.
- Option C, "Use new, retire B": swap now. Buys: possibly better art. Costs: overrides your own earlier keep without a look.
- Recommended: A, since your keep was explicit and typed after you saw both columns.

# SET 2 - Cracked Lands, Forge sky, Vexxith (4 questions)

Sources: `infrastructure/state/items/CRACKEDLANDS_THREE_HEIGHT_FLORA_1.md`, `CRACKEDLANDS_FULL_RENAME_1.md`, `FORGE_SKY_PASTURES_1.md`, `closed/VEXXITH_CLOSED_LOOP_BUILD_1.md`, `LEANINGSCRUB_SWEETLINE_NAME_REGISTER_1.md`, `design/Jawa/worldbuilding/biomes/forge_bedazzle_cast_2026-09-29.md`.

## Q2.1 Talus clasp "pry cracks wider"

Lead-in: The Cracked Lands is getting two new plants. Qirra mats are red-brown mats that open only on clay a flood has just wetted. Talus clasps are pale plants rooted beside fossil rock, described in the pick as "slowly prying cracks wider". Nothing says what prying does in play. The harvest amounts are also unset ("minor"). The plant art goes to a review sheet before any def ships; this question only decides the clasp's behaviour.

- Header: `Clasp pry`
- Question: What should a talus clasp's slow prying of cracks actually do?
- Option A, "Opens fossil seams" (Recommended): over many days, a chance that the adjacent natural wall cell becomes a fossil seam or rubble. Buys: a visible, slow change the player can use or fight; ties to the fossil rock already built. Costs: a small tick-based mechanic to build and test; must not eat player-built walls (natural walls only).
- Option B, "Flavour only": the description says it, nothing happens. Buys: no code, no risk. Costs: a promise in the text that the game never keeps.
- Option C, "Mining bonus": mining the wall cell next to a clasp yields extra. Buys: a clear, cheap reward for noticing the plant. Costs: nothing slow or visible happens to the land; it is a number, not a crack.
- Recommended: A, because the biome is about land that changes after water, and A is the only option that shows it.

## Q2.2 Rename Flooded Canyon to Cracked Lands in all internal names

Lead-in: You asked for every internal name (definitions, code, folders, docs) to match the player-facing "Cracked Lands" (typed 2026-09-28). It is a large mechanical change across many files, and the item's own safety rule says to check whether the start savegame or keeper saves still point at the old biome name before touching it. The world is also due to be remade at the end, so the old name may vanish on its own.

- Header: `Rename`
- Question: Do the internal rename now, or wait for the world remake?
- Option A, "Rename now, check saves first" (Recommended): sweep everything, but first read the start save for old-name references; if any, report and stop rather than break it. Buys: fulfils your typed order; stops the old name spreading into new work. Costs: a big multi-file change plus a mod rebuild; if the save does use the old name, the item stops and comes back to you.
- Option B, "Rename and fix the save": same, and if the save uses the old name, edit the save to match. Buys: no further stop. Costs: edits a save file (the project has had save-corruption traps); the save may be disposable anyway.
- Option C, "Wait for remake": leave internal names until the planet is repainted. Buys: no work, no save risk. Costs: the wrong name keeps appearing in new work in the meantime, which is how the last rename drifted for 16 days.
- Recommended: A, because it honours your order and the stop-on-save-risk is built in.

## Q2.3 Forge sky pastures: who gathers in the columns

Lead-in: The Forge has rising vapour columns, and the pick says the "aerofleets, beldons, fleet fliers and admitted giants" gather there. Only some of those are real defs. Aerofleet is the donor's old name for the Fumerider (renamed). Beldon is a Star Wars creature that exists only in the campaign layer. The drifting code is already on the fleet flier and the jossur (the hunting bird). No "admitted giants" are named; the Forge's actual giant is the dhokkur.

- Header: `Sky pasture`
- Question: Which creatures should the base-tier sky pastures carry?
- Option A, "Fumerider, fleet flier, jossur" (Recommended): the three flying creatures the base mod owns; beldons added by the campaign layer only. Buys: matches what exists, no new work. Costs: no giant overhead; the pastures feel like fliers only.
- Option B, "Add the dhokkur": also give the giant a column behaviour. Buys: the giant appears in the sky story. Costs: it is a ground giant; this needs a new behaviour and a design you have not reviewed.
- Option C, "Campaign layer only": no base pasture content; wait for the campaign tier. Buys: no half-built base feature. Costs: the base Forge loses the column hunting scene.
- Recommended: A, because it uses exactly what is built.

## Q2.4 Vexxith recipes

Lead-in: Vexxith (acid-proof metal) now has its acid immunity and strong stats ruled and built. What remains is which things to make from it. Filter vessels and vent liners wait on machines not built yet. A vexxith door is already fireproof as an ordinary stuff door. Gravship scab-scrapers sit next to a rule you declined ("None of these thanks").

- Header: `Vexxith`
- Question: What should vexxith be used to make?
- Option A, "Filters and liners only" (Recommended): vessels and vent liners when their machines land; no special door; no scab-scrapers. Buys: nothing built that you declined; recipes arrive with their machines. Costs: no new recipe for a while.
- Option B, "Add a plate door too": also a distinct acid-proof plate door. Buys: a visible acid-proof choice. Costs: a new def and art for something the ordinary door already half does.
- Option C, "Everything incl. scrapers": all four. Buys: complete material. Costs: revives the scraper idea you declined.
- Recommended: A.

# SET 3 - Where minerals belong (4 questions)

Source: `design/RimMandrake/minerals_where_they_belong_design_2026-10-02.md` section 7 (the design pass left these four as his questions; the lead-in below restates them in plain words). Context: you said real ore should not lie in random outcroppings like vanilla; precious and canon metals belong to specific places. The design found vanilla ore is not tied to biomes at all, and that tying it needs no engine code, only map-generation data changes.

## Q3.1 Gold, silver, uranium, jade: how strict?

Lead-in: Today any map can have gold and silver veins. The design puts them in their home places only (Scald nodules, Blue Desert meteoritic metal, canyon jade, cave gems). Every ordinary map keeps iron and stone.

- Header: `Precious`
- Question: How strictly should precious metals and gems be tied to their home biomes?
- Option A, "Home biomes only" (Recommended): ordinary maps have only iron and stone. Buys: places matter; trips have a point. Costs: a colony far from those places must travel or trade for precious metals.
- Option B, "Home plus thin trace": a fifth of today's rate everywhere else. Buys: softer economy. Costs: keeps a bit of the "random outcrop" you called absurd.
- Option C, "None natural": only salvage and trade. Buys: strongest flavour. Costs: the harshest economy; early game may stall.
- Recommended: A, because it is exactly what you asked for with a safety valve of travel and trade.

## Q3.2 Plasteel's name

Lead-in: Three different "durasteel" materials already exist (the Outer Rim mod's, the KotOR alloy in our Armoury, and an Outer Rim ore). Vanilla plasteel is the game's super-metal.

- Header: `Plasteel`
- Question: What do we do about plasteel and the three durasteels?
- Option A, "Plasteel becomes durasteel" (Recommended): rename vanilla plasteel, retire the three donor ones into it with conversion recipes. Buys: one material with a canon name. Costs: a migration pass on every recipe naming a donor durasteel.
- Option B, "Keep plasteel; donors become curiosities": Buys: least work. Costs: two super-metals side by side, confusing.
- Option C, "No naming change": only stop mining. Buys: nothing to migrate. Costs: leaves the confusion exactly as it is.
- Recommended: A, because it is the only option that leaves one clear material.

## Q3.3 Duranium and doonium

Lead-in: These two canon metals exist in none of the mods we load. Beskar is the other canon metal and is meant to be salvage-only.

- Header: `Rare metals`
- Question: Should we create duranium and doonium?
- Option A, "No, beskar only" (Recommended): beskar is the one canon salvage metal, in troves and wrecks. Buys: nothing new to balance or draw. Costs: fewer treasures to find.
- Option B, "Yes, salvage-only relics": two new rare materials with uses. Buys: more treasure. Costs: two materials to design, balance and give art.
- Option C, "Yes, trader-only": bought at the Bazaar. Buys: out of the world, no map effect. Costs: depends on the trade system that is only one slice deep today.
- Recommended: A, since you asked for canon metals to be salvage-flavoured and each new material costs art and balance.

## Q3.4 Deep drilling

Lead-in: The ground-scanner drill finds deep deposits using vanilla's table (gold, lanternstone etc. anywhere).

- Header: `Deep drill`
- Question: What should deep drilling find?
- Option A, "Iron everywhere, rest by home biome" (Recommended): needs one small code change. Buys: drilling agrees with the surface. Costs: that code change and a test.
- Option B, "Vanilla table minus Star Wars metals": no code. Buys: easy. Costs: deep drilling still finds gold anywhere.
- Option C, "Iron and fuels only": simplest. Costs: drilling stops being a treasure hunt.
- Recommended: A.

# SET 4 - Things you were left to look at (4 questions)

These items finished their offline work and wait on your eyes. Each card asks how you want to handle the look, not what to build.

## Q4.1 Canon creature re-renders

Lead-in: Seven Star Wars creatures (Boma, Dewback, Insectomorph, Shiro, Vornskyr, Whisperbird, Zakkeg) were re-rendered from the canon library, 19 of 21 pictures done; Dewback and Insectomorph each lack one facing because the image service refused for a while. A comparison sheet (canon reference beside each render) sits at `Transient/canon_regen_wave4_2026-09-23/sheet.html`. Nothing has been installed. Nothing has been graded.

- Header: `Canon art`
- Question: How should these canon creature renders be judged?
- Option A, "You grade the sheet" (Recommended): open the sheet, mark each row keep/redo; then I install the keeps. Buys: your eyes on canon fidelity. Costs: you spend a few minutes; two creatures still lack a facing until the image service is back.
- Option B, "Install the five complete ones": Boma, Shiro, Vornskyr, Whisperbird, Zakkeg install as-is, then you can veto in play. Buys: faster; most are complete. Costs: unreviewed art ships, which the project has been burned by.
- Option C, "Park until after the world remake": no grading now. Buys: no time spent now. Costs: the old, wrong art stays.
- Recommended: A, because canon fidelity is exactly the thing only you grade.

## Q4.2 Primitive droid save

Lead-in: The primitive droid family (Jawa-built frames, parts, modules, and the G2 repair droid) is built and was put in two review savegames on 2026-09-13. The item has had nothing to build since; only your look at the saves is missing. The saves are `Saves/REVIEW_DroidworksG2_2026-09-13.rws` and `DROIDWORKS_G2_REVIEW_2026-09-13.rws`.

- Header: `Droid save`
- Question: How do you want to close the primitive droid review?
- Option A, "I will look, then say" (Recommended): load the save, walk the droid, tell me. Buys: real sign-off. Costs: a few minutes of play and a cold game load.
- Option B, "Accept as shipped": count it good because it passed live checks. Buys: closes now. Costs: nobody has judged the G2 art by eye, and the faces still show default human.
- Option C, "Look after the remake": fold into the end-of-project review. Buys: one big review later. Costs: the item stays open all that time.
- Recommended: A.

## Q4.3 World label sizes

Lead-in: Every one of the 71 regions on the planet draws its label at the minimum size. A curve based on tile count was applied to a new save slot (the canonical save is untouched) and an offline picture was rendered: large regions now read larger. The worry already on record: the same multiplier might read too large on the biggest regions. The picture is `Transient/world_label_sizes/CANONICAL_ASHKARR_START_2026-09-12.biome.equirect.png`.

- Header: `Label sizes`
- Question: Are the new region label sizes right to write into the canonical save?
- Option A, "Approve the curve" (Recommended): write it to the canonical save (with a backup and a byte-size check). Buys: map labels have a hierarchy. Costs: modifies the canonical save; undo means restoring the backup.
- Option B, "Smaller multiplier": ask for the same curve scaled down and a new picture. Buys: guards against giant labels. Costs: one more round trip.
- Option C, "Leave flat": keep every label at 10. Buys: no save write. Costs: Dune Sea letters exactly as large as a tiny region.
- Recommended: A, since the picture already shows the hierarchy and a backup protects the save.

## Q4.4 Label positions for multi-piece regions

Lead-in: 52 single-piece region labels were found misplaced and an offline fix exists; 8 regions come in several separated pieces (Salt in seven). One label per region must sit at the centre of all pieces, the centre of the biggest piece, or each piece can get its own label. Pictures per region are in `Transient/world_drawcenter_audit/` (one `drawcenter_multipiece_<Name>.png` each).

- Header: `Label spots`
- Question: Where should a multi-piece region's label go?
- Option A, "Biggest piece" (Recommended): label sits on the largest piece. Buys: the label is always over the region itself. Costs: small pieces look unlabelled.
- Option B, "Centre of all pieces": Buys: simplest, current method. Costs: can land on ground that belongs to none of the pieces.
- Option C, "One label per piece": every piece named. Buys: no ambiguity. Costs: a structural change to how labels are stored, and clutter on scattered regions like Salt.
- Recommended: A; whichever you choose, the 52 single-piece fixes are applied with it.

# SET 5 - Graffiti, junk, borrowed creatures, Shokkweave (4 questions)

Sources: `design/RM_GRAFFITI_SCOPE_WIDENING.md` section 7, `infrastructure/state/items/GRAFFITI_PUNK_IDEOLIGION_SCOPE_1.md`, `FASCINATING_WORLD_JUNK_1.md`, `STARWARS_JUNK_RESKIN_1.md`, `design/RimMandrake/starwars_junk_reskin_2026-10-03.md`, `DONOR_DEFS_PORT_TO_OURS_1.md`, `SHOKKWEAVE_SOLE_SOURCE_1.md`.

## Q5.1 Graffiti design forks

Lead-in: You asked for the base Graffiti mod to go wide: punk and urban tagging plus sigils from the game's ideoligions. The design has ten open forks, each with a recommended answer, and four of your earlier points are already ruled (art style NYC wildstyle and UK stencil, every vanilla meme gets a glyph, anti-authority stencils are a feature, a few glyph mappings). The ten: murals as real art buildings (later); sigil tier (shared symbols plus the eight-meme glyph slice); raiders tag only on exit, visitors later; going over others' marks in v1; abstract letterforms, no English slogans; a full paint designator for the player; protect own and devotional marks from auto-clean; rename two category names; settlement maps tagged later; keep the three shipped marks with mechanics.

- Header: `Graffiti`
- Question: How do you want to settle the ten graffiti design forks?
- Option A, "Accept all recommendations" (Recommended): build exactly the recommended answer on each fork. Buys: unblocks the whole feature set at once. Costs: you commit to ten answers without reading each; the player-facing paint tool is a real chunk of work.
- Option B, "Accept but change some": you name the ones to change (type them), the rest follow recommendations. Buys: control where you care. Costs: a short reply.
- Option C, "Minimal v1": ship only the sigils and raid tags, no paint tool, no going-over, no murals. Buys: smallest build. Costs: less of the "wide variety" you asked for; the player cannot paint.
- Recommended: A, since the recommendations were drawn to match your stated direction and are reversible per mark.

## Q5.2 Junk wreckage: the roster and the 184 pictures

Lead-in: Two overlapping asks: you want every old tank, truck and car on the maps reskinned as Star Wars scrapworld wreckage, with a roster of "flavours" (what it was, what it yields, what it risks) decided by you card by card. A second, narrower job produced 184 junk pictures for 24 vanilla defs (variants of cars, wheels, war machines) already in the art queue, aimed at "lots of images to choose from". Roster cards for the regions (Fall Line fresh, Zeddo's Yard accumulation, Rakatan ancient) have not been made.

- Header: `Junk`
- Question: How should the wreckage reskin be finished?
- Option A, "Appearance now, flavours later" (Recommended): curate the 184 pictures on a sheet and install them (appearance only, no stat changes), and defer the per-kind roster cards. Buys: the visible change you asked for "right away". Costs: no yields or risks yet; the creative roster sitting waits.
- Option B, "Flavour roster cards first": go kind by kind (what it was, what it yields, what it risks) before installing. Buys: junk becomes gameplay. Costs: a long sitting; pictures wait.
- Option C, "Both in order": pictures now, then roster cards in a later sitting as separate work. Buys: nothing lost. Costs: most total time.
- Recommended: A, as your own 10-03 ruling said "do this right away".

## Q5.3 Borrowed creatures that need the donor's private code

Lead-in: About 330 creature and plant entries in our biomes still come from donor mods; you ruled that everything should be ours. A cost count of 66 sampled creatures found 15 that cannot be copied as plain data because they use a class from the donor's own compiled code (acid-explosion on death, a graphics refresher, and similar); the other 51 are close to straight copies. Two donors carry 262 of the 330.

- Header: `Donor code`
- Question: What should we do with creatures that depend on the donor's own compiled code?
- Option A, "Port plain, drop the odd behaviour" (Recommended): copy as data, remove the special death/graphics trick. Buys: fastest path to dropping the donor. Costs: those 15 lose a signature quirk (for example the acid burst).
- Option B, "Rebuild the behaviour ourselves": reimplement each trick in our own code. Buys: no loss. Costs: real C# work per behaviour and tests.
- Option C, "Cut those creatures": remove them from rosters and add new ones instead (you said holes are filled with new cast). Buys: no porting cost. Costs: loses 15 designs and any art already made.
- Recommended: A.

## Q5.4 Shokkweave: proof and the harvest route

Lead-in: Shokkweave (renamed hyperweave) is stripped from every trader except two sanctioned rare exceptions (Wildsteam and Hutt) that you allowed on 10-06. Offline proof says no other trader can stock it; a live check would need a new test tool, which has never been built. Separately, one of three harvest routes (colonists harvesting from the border creep-web) needs a new work job that can fail silently if mis-wired.

- Header: `Shokkweave`
- Question: Is the source-level proof of the trader strip enough, and should the web-harvest job be built now?
- Option A, "Accept proof, build the job" (Recommended): count the strip as proven, and build the harvest job with a live check. Buys: closes the economy item and finishes the third route. Costs: the new job has to be live-tested; the rare exceptions remain unproven live.
- Option B, "Accept proof, skip the job": ship the other two routes (web-cutting, nest raid). Buys: smaller, safer. Costs: one planned source of Shokkweave is missing.
- Option C, "Build the test tool first": force a trader's stock generation and test live. Buys: strongest proof. Costs: a separate tool to design, build and verify on its own.
- Recommended: A, because the strip was verified from the code of all eleven trader kinds.

# SET 6 - Vaults, sound, air, camps (4 questions)

Sources: `GELATINOUSSLIME_VAULT_SEAL_BREACH_1.md`, `ABYSS_DARK_MUFFLE_ALL_SOUNDS_1.md`, `CHILL_AIR_PUMP_1.md`, `WARSCAR_PILGRIM_CAMP_SITES_1` (no prose file; context in `closed/WARSCAR_PILGRIM_CAMPS_1.md`), `design/Jawa/worldbuilding/dungeons_arc_spec.md`.

## Q6.1 Slime chunk and the sealed vault

Lead-in: You ruled that a chunk of the giant slime becomes a bomb that can open a vault blocked by an "Assailant seal", and by card that only the Slough vault carries the seal and a chunk is the only way through. The seal itself does not exist yet: the slime side is built (a chunk can dissolve anything marked breachable), but no actual seal object has been placed in the vault. The Slough vault is the one the Assailant's flesh weapon breached long ago, inside the Slime's own largest patch.

- Header: `Vault seal`
- Question: What should the Assailant seal look like in the Slough vault?
- Option A, "Flesh plug across the inner door" (Recommended): a growth of the Assailant's flesh fills the door, only slime dissolves it. Buys: the Slime visibly "eats its maker's work"; readable at a glance. Costs: a new building def and art, plus a place in the vault map.
- Option B, "Existing sealed door gets a flag": reuse a normal vault door, marked slime-breachable. Buys: no new art. Costs: reads as an ordinary locked door; loses the story.
- Option C, "Drop the vault; chunk is only a weapon": no seal, chunk just explodes. Buys: nothing to build. Costs: discards a design you typed and carded.
- Recommended: A, since it is the picture you described.

## Q6.2 Muffling every sound in the Abyss Dark

Lead-in: In the Abyss the Dark already muffles the four wind soundscape sounds. You asked for it to swallow every sound (gunshots, footsteps, calls). That needs a small engine hook where each sound is created, which means the Abyss mod takes on Harmony, or the hook lives in a shared engine mod. Sound can only be judged with you present.

- Header: `Dark sound`
- Question: How should the Dark muffle all sounds?
- Option A, "Hook in the shared engine mod" (Recommended): one reusable patch (the same tool Cauldron now uses). Buys: other biomes can reuse it; the Abyss stays patch-free. Costs: the shared mod grows; needs your ears to tune.
- Option B, "Abyss takes Harmony itself": local and self-contained. Costs: breaks the design that Abyss carries none; duplicate patching code.
- Option C, "Only the four wind sounds": keep what is built. Buys: no risk. Costs: guns and footsteps stay crisp in the Dark, contrary to your ruling.
- Recommended: A.

## Q6.3 Chill air pump numbers

Lead-in: On the Chill seabed a powered pump makes a sealed room breathable so a stove can light. Two numbers were invented as placeholders: 300 watts while pumping, and each pump serves 60 cells (a room larger than pumps times cells is not served). Mod settings let you change both (watts 50-1000, cells 10-400).

- Header: `Air pump`
- Question: Are the provisional air pump numbers acceptable?
- Option A, "Keep 300 W and 60 cells" (Recommended): ship as is; tune from play. Buys: nothing blocks the war-lab route that reuses this. Costs: possibly wrong feel; the settings allow later change.
- Option B, "Cheaper and larger": 150 W and 120 cells. Buys: easier to live down there. Costs: less pressure on the Chill's scarcity.
- Option C, "Harsher": 500 W and 30 cells. Buys: air is a real constraint. Costs: bases need many pumps; harder start.
- Recommended: A, since these are cheap to retune later.

## Q6.4 Pilgrim camps as world sites

Lead-in: The Scarlands ladder works: journals advance the lore stage, and pilgrim camps already appear in the biome map. What is missing is the same camps placed as sites on the planet map at authored tiles along the Ashfall Road. No tiles have been authored, and the project says the planet is painted once at the end.

- Header: `Camp sites`
- Question: When should the pilgrim camps become sites on the world map?
- Option A, "At the final world painting" (Recommended): do it with the single repaint pass. Buys: no tiles to move later. Costs: camps are map-only until then.
- Option B, "Pick tiles now": you name or approve tiles along the road now. Buys: done soon. Costs: may have to move when the planet is repainted.
- Option C, "Map-only forever": no world sites; camps only appear when you visit the biome. Buys: nothing more to build. Costs: players cannot see camps from the world map.
- Recommended: A, matching your "paint once at the end" ruling.

# SET 7 - Waste and Stenchlands cast, pits, validation (4 questions)

Sources: `design/Jawa/worldbuilding/biomes/the_chill_warlab_routes_spec_2026-09-27.md` (Route 1), `design/Jawa/worldbuilding/biomes/wasteland.md`, `src/RimUtinni/WasteRun/`, `src/RimMandrake/Warcasket/`, `Transient/fw_ovn_shots/pitG_x3.png`, `Transient/foundry_gss_proof_20261006.txt`.

## Q7.1 The Throat cask

Lead-in: The Glowing Throat is a dead sarlacc where Junkers have dumped hazardous casks for ages; its guts mingled into the worst substance on the planet. Route 1 of the Chill war-lab plan has the player pay Junkers to haul those casks away and detonate a fuel sea with them. The cask item has a proposed name (Throat Cask) but no stats. The Warcasket mod already has a hazard cask family and the WasteRun quest explicitly says the Throat cask is "not involved".

- Header: `Throat cask`
- Question: What should the Throat cask be as an item?
- Option A, "Heavy, hauled, unstable" (Recommended): one stack-size-1, very heavy cask; bursts if the carrier is hurt or it burns; huge value to the right buyer. Buys: matches "you deliver it and leave". Costs: needs hauling and damage rules, a hazard comp, and art.
- Option B, "Hazard cask variant": a stronger version of the existing hazard casks, same rules. Buys: cheap, uses existing code. Costs: loses the sense of a unique terrible object.
- Option C, "Quest item only": spawns only through the Chill route, cannot be traded. Buys: controlled, no exploit. Costs: nothing for the economy or other uses.
- Recommended: A.

## Q7.2 Junker pawnkind in a warcasket

Lead-in: The Wasteland cast calls for a Junker wearing a warcasket (a heavy hazard suit) and a scatter of sealed corpses in the wasteland. The suit item exists; the pawn kind and the scatter do not, and the idea is unspecified beyond that.

- Header: `Junker suit`
- Question: What should the warcasket Junker be?
- Option A, "Rare elite hostile" (Recommended): a tough raider kind wearing the suit, appears occasionally near Junker camps. Buys: a memorable threat. Costs: a combat balance pass; hostile pawn tuning.
- Option B, "Passive scavenger": non-hostile Junker working the sealed-corpse scatter. Buys: flavour, low risk. Costs: less drama; ignored by most players.
- Option C, "Scatter only": corpses and suits lying about, no pawn. Buys: easiest. Costs: no living Junker in the suit.
- Recommended: A.

## Q7.3 Pit occupant hidden by the lip

Lead-in: From live screenshots (2026-10-06): a pawn on the south row of a depth-4 pit, or in a 1x1 pit, is drawn 1.2 cells south and the near wall (lip) covers almost all of it; only the name label shows. Two player-facing bars (tell a pit is occupied, tell a pawn is trapped) may now read no. Screenshots: `Transient/fw_ovn_shots/pitG_x3.png`.

- Header: `Pit view`
- Question: How should a pawn in a pit be shown?
- Option A, "Cut the lip over the pawn" (Recommended): draw the near lip see-through around an occupied cell. Buys: a trapped pawn is always visible. Costs: a special draw rule and testing.
- Option B, "Raise pawn above lip": draw pawns on top. Buys: simple. Costs: reads as standing at the edge, not trapped in the pit.
- Option C, "Marker only": a warning icon and tooltip, art unchanged. Buys: no draw work. Costs: the picture still hides the pawn.
- Recommended: A.

## Q7.4 GimmeSomeSlack and the Ishko landmark test

Lead-in: You conditionally accepted GimmeSomeSlack on 2026-10-06 (not validated; the north star stays draft) pending nine untraced failures in a hose test row, likely a stale expectation after a hose fix. The Ishko dark landmarks have a plan for a first live run of the new live-session tool, ending in a recorded green result.

- Header: `Sign-off`
- Question: What should happen with GimmeSomeSlack's validation and the Ishko test pilot?
- Option A, "Trace failures, then validate" (Recommended): trace the nine hose failures first, then you validate with the sheet. Buys: a clean base to sign. Costs: some work before you can sign.
- Option B, "Leave conditionally accepted": move on with it open. Buys: no work. Costs: the north star stays draft and still counts as unvalidated.
- Option C, "Skip Ishko pilot too": park both. Buys: frees the bridge for other things. Costs: the live-session tool stays untried.
- Recommended: A.

# SET 8 - Names, canal art, trade UI, frame rate (4 questions)

Sources: `LEANINGSCRUB_SWEETLINE_NAME_REGISTER_1.md`, ledger notes on `SWALE_CANAL_ART_REFERENCE_1` (`Transient/swale_canal_reference_2026-09-30/compare_reference_vs_v2.png`), `BAZAAR_DISPLACEMENT_PASS_1.md`, handoff `FOUNDRY_REBOOT_HANDOFF_202610042203.md` (no prose file exists for the frame-rate item).

## Q8.1 Sweetline tree names

Lead-in: Every sweetline tree gets a generated name. The word list is a placeholder from shipped descriptions: names read like "the Silver Mark" or "Sweetline of the Giants". No ruling set the style. Trees already named in a save keep their name.

- Header: `Tree names`
- Question: What style should named sweetline trees have?
- Option A, "Plain landmark English" (Recommended): keep the current style, widen the word list. Buys: no new work. Costs: less exotic than the rest of the cast.
- Option B, "Invented exotic words": names like the creatures use. Buys: matches the cast's voice. Costs: a word list to write; harder to read.
- Option C, "After people or events": founder, battle, death. Buys: stories. Costs: needs a bank of names and events; odd pairings.
- Recommended: A, cheapest and already reads fine.

## Q8.2 Swale canal art

Lead-in: You asked for the Swale picture to be made from a real FlowWorks canal screenshot. That was done: a live canal shot exists and a new render (v2) was made. Side by side, v2 is a brown rippled strip with cracked banks, while the live canal is flat blue-grey with no bank art, so v2 does not look like the canal beside it. The old placeholder still ships.

- Header: `Swale art`
- Question: What should we do about the Swale picture?
- Option A, "Redo to match the canal" (Recommended): regenerate with the live water look (flat blue-grey) and a bank only where the Cracked Lands need one. Buys: reads as one channel family. Costs: one more art round.
- Option B, "Keep v2": install it. Buys: done now. Costs: mismatched look beside real canals.
- Option C, "Keep placeholder": do nothing. Buys: no work. Costs: placeholder stays indefinitely.
- Recommended: A.

## Q8.3 Retiring the old trade windows

Lead-in: The plan was to remove Trade UI Revised and Vanilla Trading Expansion once our own Bazaar trade window proves live. The Bazaar is one commit deep: no window code, not in the active mod list. Removing them now would leave only vanilla trading. The item says the condition is not met.

- Header: `Trade UI`
- Question: What should happen to the old trade window mods?
- Option A, "Keep until the Bazaar works" (Recommended): leave them, mark the item waiting. Buys: nothing breaks. Costs: two extra mods stay loaded.
- Option B, "Retire now": use vanilla trading for the interim. Buys: shorter mod list. Costs: worse trading, and an unrehearsed save change.
- Option C, "Drop the Bazaar plan": keep the old mods for good. Buys: no new build. Costs: abandons a designed feature.
- Recommended: A.

## Q8.4 Frame rate during normal play

Lead-in: On 2026-10-04 you saw heavy low-frame-rate stretches during bridge test runs and assumed the bridge (writes, screenshots) caused it. Nobody has checked the game without a bridge session.

- Header: `Frame rate`
- Question: How should the frame rate be checked?
- Option A, "You play a normal session" (Recommended): play 10 minutes with no bridge running; tell me if it stutters. Buys: the real answer. Costs: 10 minutes of your time.
- Option B, "I measure it": I run a bridge-free session and read frame-time stats. Buys: no time from you. Costs: needs a tool that can read frame time and a game load.
- Option C, "Assume the bridge": close it as explained. Buys: nothing more to do. Costs: a real problem might ship unnoticed.
- Recommended: A.

# SET 9 - Map maker and firehawk (2 questions)

Sources: ledger events for the mapgen items (`Transient/mapgen_v1/comparator_sheet.png`, `Transient/mapgen_gl3/comparator_gl_vs_painter_v3.png`), `FIREHAWK_FLIGHT_BEHAVIOR_1.md`. Note: these make single-map terrain, not planets, so they do not touch the no-worldgen ruling.

## Q9.1 Map generator sheets

Lead-in: Three connected items are built and waiting on your keep or cut: the first-version map maker (one idea per map, 8 sample maps beside real corpus maps), the improved painter (organic shapes, more terrains), and the in-game landform renders (all 8 landform types now proven). The real test is the sheet: can you see the one idea at thumbnail size, and does it look like a landscape rather than a diagram.

- Header: `Map maker`
- Question: How should the map generator be judged and continued?
- Option A, "Look at the one sheet" (Recommended): view the in-game versus painter sheet at `Transient/mapgen_gl3/comparator_gl_vs_painter_v3.png` and mark keep or cut. Buys: a decision on whether to keep investing. Costs: a few minutes; the items stay open until you do.
- Option B, "Park the generator": stop here; close the items as exploratory. Buys: frees effort. Costs: the 8-for-8 landform work stops mid-pipeline.
- Option C, "Go further": ask for structures and dressing next. Buys: closer to usable maps. Costs: a large build before you have judged the terrain.
- Recommended: A.

## Q9.2 FireHawk flight

Lead-in: The FireHawk now flies with a proper flip-book animation (the earlier wing-layer attempt was replaced after your live test). Static checks pass. The last bar is seeing a takeoff with your own eyes, and the standing rules are: spawn about 20, you watch, no unattended screenshot hunts.

- Header: `FireHawk`
- Question: How do you want to confirm FireHawk flight?
- Option A, "Joint session: spawn 20" (Recommended): a short bridge session with you watching. Buys: the one proof only you can give. Costs: you must be present; needs the game and bridge.
- Option B, "Accept the state read": rely on the flight-state check that passed. Buys: closes now. Costs: nobody has seen the animation since the redo.
- Option C, "Check it during normal play": no special session; flag it if you see a FireHawk in flight. Buys: no setup. Costs: may take a long time to happen.
- Recommended: A.
