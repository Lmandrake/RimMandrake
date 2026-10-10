# Mod audit: decisions for the owner

These cards come from the mod audit (589 mods, 2026-10-10/11). Every question raised by the 16 assessors and the 4
checkers was collected. Questions an existing ruling already answers were dropped; the table at the end names the
ruling for each. Duplicates were merged, and questions that need a measurement rather than a choice became tickets
(`ACTIONS_NOW.md` §E). That leaves **23 cards in 8 themes**.

Each card gives:

- the decision, in plain words;
- the mods involved;
- what each option buys and what it costs;
- a recommendation with one line of reasoning;
- where the evidence is.

"Phase-out" means "keep it now, remove it once our replacement exists". Per-mod detail is in `MASTER_REGISTRY.jsonl`
(column `owner_question_ids`) and in `records/batch_NN.md`.

---

## Theme 1. Leaving the big donor mods

### C01. Do the "permanent resident" donors stay forever, or get ported like everything else?
**The decision.** On 2026-09-11 you named some big donor mods "permanent residents" (keep them for good). On 2026-09-20
you ruled "move everything to our own defs". The two rulings conflict for these mods, and today the audit marks two of
them keep-forever and the rest phase-out.
**Mods:** ReGrowth (`regrowth.botr.core`), Alpha Biomes (`sarg.alphabiomes`, the largest biome donor at 1,155 refs from our
mods), Biomes of Grimterra (`grimterra.biomesmod`), More Vanilla Biomes (`zylle.morevanillabiomes`), Alpha Animals
(`sarg.alphaanimals`), Alpha Memes (`sarg.alphamemes`), Vanilla Memes Expanded (`vanillaexpanded.vmemese`), VFE Tribals
(`oskarpotocki.vfe.tribals`).
- **A. Port everything (the 09-20 rule wins).** Each donor leaves once its biome or creatures are ours, which happens biome by biome at
  each biome's sitting, and finishes by the paint-once pass. *Buys:* no outside mod holds the campaign hostage, and the art
  can all be ours. *Costs:* the most porting work, and Alpha Biomes is a hard dependency of our biomes mod today.
- **B. The 09-11 residents stay for good.** *Buys:* no porting for the eight. *Costs:* the biggest memory and load share
  stays with outside authors, and donor art stays in the game (against "no donor art kept").
- **C. Mixed: frameworks and memes stay, biomes and creatures port.**
**Recommendation: A**, sequenced biome by biome as the biomes come up. Your later ruling and the no-donor-art rule both point
this way, and ending Alpha Biomes' hard dependency is mostly technical work (ticket `BIOME_DONOR_DEPENDENCY_UNTANGLE_HARD_LINK`).
**Evidence:** `design/Jawa/mods/mod_config_rulings.md:71`; `DONOR_DEFS_PORT_TO_OURS_1`; `checks/check_group_2.md` "Ruling
conflicts"; brief §5.9 (the 09-11 file says "Nothing here has been re-verified").

### C02. Cut the donors we have already replaced now, or wait for the world remake?
**The decision.** Some donors' jobs are done by our own mods already, or will be at the remake. If they come out before the
remake, anything they placed in the current save (animals, furniture) vanishes from it.
**Mods:** Star Wars Animal Collection (`mlie.starwarsanimalcollection`, still 3,439 refs from our patches), Outer Rim Furniture
(`neronix17.outerrim.furnitureanddecor`), Chezhou Sandworm and its library (`chezhou.creature.sandworm`,
`chezhou.chezhoulib.lib`; our own Long Hunger replaces it).
- **A. Cut each one as soon as its references are gone.** *Buys:* a lighter list sooner. *Costs:* placed things in today's
  save may vanish, and the save is disposable until the remake anyway.
- **B. Cut them all at the world remake.** *Buys:* one clean break with no save surgery. *Costs:* they ride along
  until then.
**Recommendation: A for the sandworm** (it only duplicates our Long Hunger), **B for the other two** (the remake is
the planned break, so paying migration costs before it is waste).
**Evidence:** `records/batch_06.md`, `records/batch_08.md`, `records/batch_14.md`; ticket `SWAC_EDGES_CENSUS_PORTED_VS_LIVE`.

### C03. GravTide and the sea: what survives once the ship flies to the sea floor?
**The decision.** You ruled that the ship is the only way down and back ("ship or nothing"). GravTide still provides
pressure hulls and boats. Vehicle Framework vehicles could reach the sea layer. The Warcasket was ruled "an alternative to
... ocean access".
**Mods:** GravTide (`gravtide.mod`), our Warcasket (`mandrake.rm.warcasket`), Vehicle Framework sea use (`smashphil.vehicleframework`).
- **A. GravTide goes once our sea-floor layer works alone. The Warcasket protects on shores and in toxic or vacuum areas,
  never as a way onto the sea floor. No vehicles on the sea layer.** *Buys:* one coherent sea rule. *Costs:* GravTide's
  boats are lost.
- **B. Keep selected GravTide systems (pressure hulls or boats) as ours.** *Costs:* porting work, and a second way to the
  sea that has to be fenced.
**Recommendation: A.** It is the only reading consistent with "ship or nothing".
**Evidence:** CLAUDE.md sea ruling 2026-09-26; `records/batch_08.md` gravtide.mod; `records/batch_15.md` mandrake.rm.warcasket.

## Theme 2. The world and the tools that build it

### C04. Which world-building tools do players get, and which are yours alone?
**The decision.** Players receive a frozen, hand-made world, so tools that edit worlds, factions, maps or pawns are either
your authoring kit (removed before release) or a player feature.
**Mods:** Map Preview, Mutator World Icons, Prepare Landing, Modify Landing Tile, Worldbuilder, WorldEdit, Faction
Customizer, Character Editor, Scenario Amender, Persistent Precepts.
- **A. All authoring-only: removed from the player list at release, kept for you until the paint pass.** *Buys:* players
  cannot unfreeze the world. *Costs:* players lose landing-site browsing (Map Preview, Prepare Landing).
- **B. Authoring-only, except that the read-only scouting tools (Map Preview, Prepare Landing, Mutator icons) ship to players.**
- **C. Ship them all.**
**Recommendation: B.** Scouting tools cannot change the frozen world, and they help a player choose a landing.
**Evidence:** brief §5.1 (the audience contradiction); `checks/check_group_1.md` item 7.

### C05. The world remake: do the generators leave once it is done?
**The decision.** A remake of the world is expected as the last step. These mods matter only for generating or sizing a world.
**Mods:** Alien Worlds and Tidally Locked (`7f.alienworlds`, `7f.alienworlds.tidallylocked`), My Little Planet
(`oblitus.mylittleplanet`; the 21,872-tile world probably depends on its size settings, INFERRED), Sensible Factions
(`boots.sensiblefactions`), Faction Territories (`jaeger972.factionterritories`).
- **A. Keep them until the remake is saved, then remove them from the player list.** *Costs:* the save must be checked for
  defs they own before they go.
- **B. Keep them in the player list for good.** *Costs:* worldgen code ships to players although players never generate.
**Recommendation: A.** There is no worldgen feature in any version.
**Evidence:** CLAUDE.md "no worldgen"; `records/batch_01.md`, `records/batch_03.md`, `records/batch_05.md`.

### C06. Map-generation tools that can overwrite our biomes' terrain
**The decision.** Geological Landforms (and Biome Transitions) reshape generated maps and can overwrite what our biome
generators draw. Map Designer silently caps how dense our plants can grow.
**Mods:** `m00nl1ght.geologicallandforms`, `m00nl1ght.geologicallandforms.biometransitions`, `zylle.mapdesigner`.
- **A. Keep them everywhere, and patch each of our biomes to opt out.** *Costs:* a patch per biome, forever.
- **B. Keep them only on vanilla-biome tiles.** *Costs:* one compatibility layer.
- **C. Retire all three. Map Designer survives only as your map-repair tool, off the player list.**
**Recommendation: C.** Our biomes are meant to own their terrain and density.
**Evidence:** `records/batch_08.md`; `checks/check_group_1.md` (Map Designer).

## Theme 3. The crew and how it grows

### C07. Should the crew ever grow past the founders?
**The decision.** The clan starts with six founders and should stay small (3-8). Several mods add people.
**Mods:** We Are United (`sl4vp0wer.weareunited`, relatives and wanderers join), our Stranded quest (`mandrake.rm.strandedquest`,
gives a colonist), More Slaves (`mlie.syrmoreslaves`, traders sell slaves in bulk).
- **A. Growth only through story: the Stranded quest stays, We Are United goes, slave stock stays at vanilla.**
- **B. No growth at all: cut all three paths.**
- **C. Allow all three.**
**Recommendation: A.** One deliberate, story-gated path keeps the crew small without making it frozen.
**Evidence:** `records/batch_02.md`, `records/batch_05.md`, `records/batch_15.md`; slavery stays in scope (`required_mods.md:1170`).

### C08. Skill-specialisation ladders: allowed, or a parallel progression you want out?
**Mods:** Vanilla Skills Expanded (`vanillaexpanded.skills`; two other mods build on it), Alpha Skills (`sarg.alphaskills`).
(Vanilla Skills Rexamined is already ruled retired; see ACTIONS_NOW A1.)
- **A. Remove both. Skills stay vanilla.** *Costs:* untangling the two mods that build on VSE.
- **B. Keep one ladder (VSE) and drop Alpha Skills.**
- **C. Keep both.**
**Recommendation: A.** You already retired one skill overhaul for the same reason, and a small fixed crew gains little from specialisation.
**Evidence:** `records/batch_07.md`, `records/batch_14.md`; `STAT_NORM_WAVE3_RETIRE_1`.

### C09. Extra event layers on top of Randy
**The decision.** The storyteller is settled (Randy, R-S7). These mods still add or retime events: danger that is different,
or simply more.
**Mods:** Storyteller Enhanced's 8 incident patches (`mlie.storytellerenhanced`), Faction Raid Cooldown (`mlie.factionraidcooldown`,
live +13 h per raider death), Better Infestations' own insect-raid and swarming-horde events (`zal.betterinfestations`; your
infestation ban does not reach them), More Faction Interaction (`mlie.morefactioninteraction`), Rimesis growing nemesis
raiders (`font.rimesis`), Large Faction Bases (`mlie.largefactionbases`).
- **A. Keep only what makes danger different: cut Large Faction Bases, turn off Better Infestations' events, drop
  Storyteller Enhanced, and leave named enemies to our OldFriends system (Rimesis goes).**
- **B. Keep them all as tuned today.**
- **C. Decide one by one.**
**Recommendation: A.** "Qualitative danger, not bigger numbers" is a pillar, and our own systems already cover nemeses and tribute.
**Evidence:** `records/batch_03.md`, `records/batch_04.md`, `records/batch_09.md`, `records/batch_11.md`, `records/batch_12.md`.

## Theme 4. The ship, the base and convenience

### C10. Automation and convenience that soften scarcity
**Mods:** Belt Extractors (`groovytaco.beltextractors`), Turret Pipeline (`reel.turretpipeline`), Minify Everything (`erdelf.minifyeverything`),
Dedicated Turrets (`clown.dedicatedturrets`), Shield Generators (`neronix17.shieldgenerators`), LightsOut (`juanlopez2008.lightsout`;
our lighting mods fight it), wall-mounted facilities (`hmc.wall.furniture`, `kyzy.shipwallenhanced`; they free deck cells
on a ship meant to be cramped).
- **A. Cut them all.** Hauling, reloading and leaving things behind stay real costs, and the ship stays cramped.
- **B. Cut the automation (belts, pipelines, shields), keep the comfort (minify, wall decor, LightsOut).**
- **C. Keep them all.**
**Recommendation: A.** Each one quietly removes a pressure the scenario is built on. LightsOut also fights our own mods.
**Evidence:** `records/batch_03.md`, `records/batch_05.md`, `records/batch_12.md`.

### C11. Is the Utinni the only ship, and are there any other vehicles?
**Mods:** Trystan's shuttles (`trouperton.trystantravellersshuttleschematics`), the KotOR ship pack and Gravship Blueprints
(`btd.gbp.shippack.kotor.vge`, `btd.remix.gravshipblueprints`), Gravship Raids capture (`sk.gravshipraids`), Deep Orbit
(`broms.deeporbit`), Walk the World (`addvans.walktheworld`), Vehicle Framework with Raid Vehicles, Alpha Vehicles Neolithic and our
Desert Vehicle Reskin (`smashphil.vehicleframework`, `gabrieel1482.raidvehicleframework`, `sarg.alphavehiclesneolithic`,
`mandrake.rsw.desertvehiclereskin`), Non-Destructive Grav Launch (`planetace.nondestructivegravlaunch`, which keeps the camp
left behind).
- **A. The Utinni is the only ship. Captured gravships are stripped for parts. No shuttles or orbit layer. Ground carts stay
  (Vehicle Framework kept for the reskinned carts only, with no raid vehicles). Walking off the map edge is cut. Left-behind camps persist.**
- **B. The Utinni only, and no vehicles at all** (drops Vehicle Framework and the cart reskin).
- **C. Other ships and vehicles allowed.**
**Recommendation: A.** It keeps the single-hull fantasy while saving work already done on the carts.
**Evidence:** `records/batch_05.md`, `records/batch_06.md`, `records/batch_13.md`, `records/batch_14.md`, `records/batch_16.md`; V2_DREAMS §0b/§0c.

### C12. Bigger Gravships: are its fuel-tank and shield numbers intended?
**The decision.** The live settings hold twelve values, not the four in our design notes. The structural ones are being
recorded (ACTIONS_NOW B2). The chemfuel tanks (1,140 and 8,805 capacity), 20 small thrusters and the shield values touch
the fuel-scarcity pillar.
- **A. Freeze them as they are.**
- **B. Reset the tank and shield values to vanilla, and freeze the rest.**
- **C. Tune them in play first.**
**Recommendation: B.** Huge tanks quietly undo fuel scarcity.
**Evidence:** `Config\Mod_3522759531_GravshipSizeSettings.xml`; `checks/check_group_1.md` item 2.

### C13. Industry and salvage: how much free production?
**Mods:** VFE Factory (`vanillaexpanded.vfefactory`; required_mods calls it the sole industrial tree, and the brief's
anti-automation line disagrees; its smelter is already removed), Better Cremation (`thumb.bettercremation`, returns the
metal from clothes), Bones (`sihv.rombonesport`, buildable bone items).
- **A. VFE Factory machines are replaced one by one by Wrecked Machines restoration tiers. Cremation salvage follows our
  own yield rules (drop the mod). Bones are ported only if you want bone building.**
- **B. Keep VFE Factory as the industrial tree, keep both small mods.**
**Recommendation: A.** Restoring wrecked machines is the Jawa fantasy, and free salvage bypasses our yield rules.
**Evidence:** `records/batch_02.md`, `records/batch_04.md`, `records/batch_07.md`.

## Theme 5. Combat and gear

### C14. Yayo's Combat 3, given that Combat Extended is banned
**The decision.** The ban covers "equivalent total combat overhauls", but our weapon register's armour-penetration numbers are
calibrated on Yayo's.
**Mods:** `mlie.yayoscombat3`; Stronger Scaling (`kas.strongerscaling`, masterwork gear much stronger).
- **A. Yayo stays (it is lighter than CE and our numbers depend on it). Stronger Scaling goes.**
- **B. Remove Yayo and recalibrate the weapon register on vanilla.**
**Recommendation: A.** Recalibrating every weapon is large work for no gain to the scenario.
**Evidence:** `forbidden_mods.md:151-153`; `checks/check_group_3.md` "Ruling conflicts".

### C15. Donor content you once ruled out that is still loaded
**Mods:** Vanilla Weapons Expanded (`vanillaexpanded.vwe`, 125 weapons; marked "lean-skip" but active and rebalanced by
Armoury), VQE Ancients (`vanillaquestsexpanded.ancients`; you ruled "drop entirely" on 2026-08-03, and we have since written
about 60 patches for its creatures), Alpha Mechs' player-craftable mechs (`sarg.alphamechs`), Destiny exotics
(`milkwater.destinymod`), Warcasket's three extra suits (`aoba.warcasket`).
- **A. Honour the old rulings: drop VQE Ancients except its splice creatures (port those), drop VWE guns that are not
  rebalanced, drop the player mechs, Destiny and the extra suits.**
- **B. Keep what is already wired in (VWE, Ancients creatures). Drop the rest.**
**Recommendation: B, then port.** The patches are already written, so the cheap path is to keep them and port them later,
not to undo them now.
**Evidence:** `records/batch_07.md`, `records/batch_09.md`, `records/batch_11.md`.

## Theme 6. Look, sound and tone

### C16. Pawn faces
**The decision.** Facial Animation and its add-ons give pawns faces in several styles: cartoon, anime, Roblox-like
(Reel, Danzinagri, parts of the Genetic Heads packs). VE's retexture is the heaviest art in its batch. Cosmetic changes
need your permission because they can break animated faces.
**Mods:** `nals.facialanimation`, `reel.facialanims`, `danzinagri.facialanimationcompatabilityproject`,
`vanillaexpanded.vtexe.facialanims`, `sd.fa.geneticheads*`.
- **A. Vanilla-style and our own faces only. The stylised add-ons go, and Facial Animation stays.**
- **B. Keep all styles.**
- **C. Drop animated faces entirely** (this frees the largest share of the 30 GB process budget).
**Recommendation: A.**
**Evidence:** `records/batch_07.md`, `records/batch_11.md`, `records/batch_14.md`; CLAUDE.md:831.

### C17. Does "no donor art kept" also cover sound, UI and functional apparel?
**Mods:** Ambience (`swablu.ambience`), Slave Outfits (`usgiyi.slaveoutfits`), our Rust Chrome UI recolour of vanilla buttons
(`mandrake.rm.rustchrome`), the three Adaptive Storage model packs (`adaptive.*storage`), Roots of RimWorld tribal decor
(`ghost.rootsofrimworld`).
- **A. Art only: sounds and UI recolours stay, apparel and furniture art is redrawn as for any donor.**
- **B. Everything: sound and UI too.**
**Recommendation: A.** Sound and UI are not what the rule protects (the look of the world), and redoing them is a large job.
**Evidence:** brief §2 "no donor art"; `records/batch_02.md`, `records/batch_11.md`, `records/batch_13.md`, `records/batch_15.md`.

### C18. Heavy visual extras: worth their memory?
**Mods:** Planet Atmosphere (`rwnodetree.rwplanetatmosphere`, about 1 GB estimated), EGI Holograms (`vesper.egihologramsandprojectors`,
1.5 GB header proxy; holograms are on-genre since the gods are holograms), Minerals Rock shapes (`zacharyfoster.mineralsrock`), Glowing Bush (`fourtoo.glowingbush`).
- **A. Measure first (`HEAVY_TEXTURES_MEASURE_REAL_VRAM`), then keep only what costs under ~250 MB, or redraw it ourselves.**
- **B. Cut all four now.**
**Recommendation: A.** The estimates are header proxies and may be wrong by a lot.
**Evidence:** `records/batch_10.md`, `records/batch_11.md`, `records/batch_14.md`.

### C19. Off-tone mods: approve the cut list
**Mods:** Metal Pipe and Metal Pipe Horseshoe (`flangopink.metalpipe*`), meme tantrum sounds (`kshtantrumsounds.mod`), Monty Python
melee sounds (`bonible.medievalmeleesounds`), FancyRats (`armoredampharos.fancyrats`, `tyrannidae.fancyratsplus`), Dark Ages
Crypts (`van.dacrypts`), Dark Ages trolls (`van.beasts`; the faction is already decided, so only the troll creatures and two letters remain),
Dredge aberrations (`aqued.dredgeaberrations`), Ideology Virtues (`dimonsever000.ideologyvirtues`), Torment Master
(`vlvop.tormentmaster.expansion`; listed but not installed).
- **A. Cut them all** (the save is checked for placed things first).
- **B. Name the ones to keep.**
**Recommendation: A.** None fits the desert Star Wars tone, and none is used by our mods.
**Evidence:** `records/batch_02.md`, `records/batch_10.md`, `records/batch_13.md`, `records/batch_14.md`.

## Theme 7. Peoples and factions

### C20. Non-canon peoples as NPC variety
**The decision.** Are outside xenotypes and races welcome as background variety, or does every people come from our own RSW_
roster? Two are already rethemed by your ruling (Orc Clan to Gamorreans, Archons to Mortis wanderers) and also suppressed.
**Mods:** Avaloi (`det.avaloi`, with psychic genes), Beliar (`elsov.beliar`), Alpha Genes (`sarg.alphagenes`, 16 xenotypes plus labs),
Posthuman Drift and Titan (`xylthixlm.races.core`, `xylthixlm.races.titan`), VRE Archon (`vanillaracesexpanded.archon`),
Orc Clan (`karew.orcclan`).
- **A. Our roster only: the rethemed two stay until ported, and the rest go.**
- **B. Rethemed outsiders are welcome. Non-rethemed ones go.**
- **C. All stay as variety.**
**Recommendation: A.** The rethemes show the intent, and porting removes the doubled faction/suppression patches.
**Evidence:** `src/RimUtinni/UtinniPatches/Patches/{OrcClan_GamorreanRename,VREArchon_MortisRename}.xml`; `records/batch_07.md`, `records/batch_10.md`, `records/batch_13.md`.

### C21. RimTek: keep the datapad mods?
**Mods:** RimTek Core, DocMate, DigiPal (`deon.rimtek.core`, `.docmate`, `.digipal`). DocMate is graded keep, so Core must stay.
The checker disputed DigiPal's removal ("a datapad is not off-genre"), and the audit leaves that open.
- **A. Keep all three.**
- **B. Keep Core and DocMate. Remove DigiPal.**
- **C. Remove all three** (DocMate is replaced by our own).
**Recommendation: B.** It follows the only measured dependency, and DigiPal adds nothing we use.
**Evidence:** `MASTER_REGISTRY.jsonl` deon.rimtek.digipal (decision_status DISPUTED); `checks/check_group_1.md` item 4.

### C22. Physically remove the mods whose content Cherry Picker already cut?
**The decision.** Doctrine says to trim with Cherry Picker rather than uninstall. These mods are now near-empty shells that still load
code and art, on a list that runs at 8-10 TPS.
**Mods:** Ancient Urban Ruins family (`xmb.ancienturbanruins.mo`, `meteores...aurvl`, `meteores...aurad`; AURAD is already forbidden by
name), Big and Small Races (`redmattis.bigsmall`, all 86 defs cut), Medieval Flavour (`shavius.medieval.flavour`, 26 of 27 cut, and one
pawn in the save carries one of its backstories), plus Custom Quest Framework (`hailuan.customquestframework`), which exists only to run
the Dungeon Pack and the Ruins.
- **A. Remove the shells** (after the save check). The doctrine gets an exception: "an uninstall is fine once a mod is ≥90% cut".
- **B. Keep the doctrine. The shells stay.**
**Recommendation: A.** A shell costs load time and adds no content.
**Evidence:** `ancient_ruins_mod_audit.md` §Recommendation; git `6cadd01c4`; `checks/check_group_3.md` "Ruling conflicts".

## Theme 8. Our own systems

### C23. The talking ship: the Oracle, RimAI, and when
**The decision.** You ruled that in-game AI goes through `claude -p`, never a hosted API. The Oracle is built for that. The two
RimAI mods talk over the internet.
**Mods:** `mandrake.rm.oracle`, `kilokio.rimai.framework`, `kilokio.rimai.core`.
- **A. The Oracle ships dormant in v1 (fixed text, debug actions), and RimAI goes now.**
- **B. The Oracle ships live as the god-letter narrator (needs Claude Code installed and logged in on the player's machine),
  and RimAI goes.**
- **C. RimAI stays as the voice until the Oracle is live.**
**Recommendation: A.** The game must be whole with the AI absent, and RimAI contradicts the transport ruling.
**Evidence:** CLAUDE.md "In-game LLM access" (2026-09-05); `records/batch_01.md`, `records/batch_12.md`, `records/batch_15.md`.

*(One design question was not carded because it is FOUNDRY's own choice: rebuild the propane-lake pipes and the VGE oxygen/heat
network on FlowWorks. Your rulings, one kind of heat and one LiquidDef registry, already answer it, so the remaining work is a build
plan. `mandrake.rut.propanelakemechanics`, `vanillaexpanded.gravship`.)*

---

## Not carded: questions already answered by a ruling

| mod(s) | question that was raised | answered by |
|---|---|---|
| `cain.mineshaft` | keep Mines 2.0? | owner override 2026-08-12, `design/Jawa/desert_world_design.md:488` |
| `mlie.storytellerenhanced` | which storyteller? | Randy, ratified: `SCENARIO_SETTINGS_SPEC.md` R-S7 (only its 8 incident patches remain, in C09) |
| `kilokio.rimai.*` | which transport? | `claude -p` ruling 2026-09-05 (only timing remains, in C23) |
| `zal.calltradeships` | allow calling trade ships? | adopted, `required_mods.md:1358` |
| `lee.theforce.lightsaber` | port or keep? | owner card 2026-09-02: STAYS UPSTREAM (`STARWARS_DONOR_SUNSET_1`) |
| `neronix17.outerrim.galacticempire` | faction or armour? | faction cut, mod kept for the raid armour (brief §2) |
| `mlie.miningco*` (4 mods, 3 cards) | retheme, own or drop? | Czerka retheme, owner 2026-09-11, `MiningCo_CzerkaRename.xml`, git `8e1ea6c3d` |
| `redmattis.bigsmall` | cull or retheme? | cut whole, git `6cadd01c4` (only the uninstall remains, in C22) |
| `karew.orcclan`, `vanillaracesexpanded.archon` | retheme? | rethemed 2026-09-11 (the keep-or-port question remains, in C20) |
| `sr.modrimworld.factionalwarcontinued` | random war incidents? | FULL ACCEPT 2026-08-06, `required_mods.md:887` (frequency check is a ticket) |
| `heatherathebyne.craftingspotslavegear` | is slavery in scope? | yes, `required_mods.md:1170` |
| `mlie.nwnrealfogofwar` | which fog? | Route B, `OPUS5_HANDOFF.md:179` (toggle check is a ticket) |
| `dubwise.dubsbadhygiene.lite` | hygiene on? | "NOTHING else from the DBH family", `required_mods.md:581` (setting check is a ticket) |
| `gravenwitch.vsrexamined`, `jellypowered.survivaltools` | back on the list, wanted? | retired 2026-09-11, `STAT_NORM_WAVE3_RETIRE_1` (ACTIONS_NOW A1) |
| `meteores...aurad` | which ruling stands? | forbidden by name, `forbidden_mods.md` |
| `mandrake.rm.biomes` / `sarg.alphabiomes` | port schedule? | donor retirement plan §3/§5, Q12 |
| `mandrake.rm.explosivegrowth`, planetary crop | growth multipliers? | owner-ruled design; the numbers are tuning |
| `mandrake.rm.acousticscanner` | spoils too much? | the owner picked the banded design by card |
| `mandrake.rm.ninefold`, `mandrake.rm.sacredgraffiti` | which tier? | `NAMING_SCHEME_PLAN.md` §7.1 and :54 (execution is ACTIONS_NOW C5) |
| `ludeon.rimworld.anomaly` | storyline in play? | canon reintegration ruling ② (owner card 2026-09-04); verdict-neutral |
| `mlie.spaceworms` | six IncidentDefs? | facts: IncidentDef = 1 |
| `dubwise.rimefeller` | buildable oil? | found-only, `required_mods.md:565-575` (ACTIONS_NOW B3) |
| `ionfrigate12345.coolandgoodambush`, `lwm.deepstorage`, `zal.spaceports`, `sarg.alphamemes`, `vesper` texture | measurement, not a choice | tickets in ACTIONS_NOW §E |
