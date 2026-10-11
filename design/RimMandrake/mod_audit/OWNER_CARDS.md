# Mod audit: decisions for the owner

These cards come from the mod audit (589 mods, 2026-10-10/11). Every question raised by the 16 assessors and the 4
checkers was collected. Questions an existing ruling already answers were dropped; the table at the end names the
ruling for each. Duplicates were merged, and questions that need a measurement rather than a choice became tickets
(`ACTIONS_NOW.md` §E). That gave **23 cards in 8 themes**.

**State on 2026-10-10:**

- **8 cards are ANSWERED** (C01-C04, C07-C10). The rulings are in `OWNER_RULINGS.md` and are applied to `MASTER_REGISTRY.jsonl`
  (field `owner_ruling_id`). The mods those rulings retire now are listed in `ACTIONS_NOW.md` under "RETIREMENT WAVE 1".
- **15 cards are open.** GPT's review (`GPT_REVIEW_DISPOSITION.md` §7) reworded them.
- **2 cards are new** (C24, C25). GPT surfaced decisions that no existing card asked.

Each open card gives:

- the decision, in plain words;
- the mods involved;
- what each option buys and what it costs;
- a recommendation with one line of reasoning;
- where the evidence is.

"Phase-out" means "keep it now, remove it once our replacement exists". A verdict is where a mod is headed. Whether it is
safe to remove *today* is a separate check (save census and dependency review, `ACTIONS_NOW.md`). Per-mod detail is in
`MASTER_REGISTRY.jsonl` (column `owner_question_ids`) and in `records/batch_NN.md`.

---

## Answered

| card | question | ruling (OWNER_RULINGS.md) | carried out as |
|---|---|---|---|
| C01 | Do the "permanent resident" donors stay forever? | **ANSWERED: port everything.** The eight donors leave biome by biome, ending at the paint-once pass. | 8 rows PHASE-OUT, `owner_ruling_id` C01. Frameworks (VEF, HAR, Vehicle Framework) are not in C01's list and stay KEEP. |
| C02 | Cut replaced donors now, or at the remake? | **ANSWERED: Sandworm and ChezhouLib now.** Star Wars Animal Collection and Outer Rim Furniture wait for the remake. | Sandworm pair ELIMINATE (WAVE 1). The other two are PHASE-OUT. |
| C03 | GravTide and the sea | **ANSWERED: GravTide goes once our sea-floor layer works alone.** The Warcasket protects on shores and in toxic or vacuum areas, never as a way onto the sea floor. No vehicles on the sea layer. | GravTide PHASE-OUT. Warcasket KEEP. Vehicle Framework keeps its C11 question. |
| C04 | World-building tools for players | **ANSWERED: all removed from the player list at release.** We may keep some for our own scouting until shipping. | 11 tools PHASE-OUT, "authoring only". |
| C07 | Crew growth | **ANSWERED: retire We Are United and More Slaves now.** Study them first, to build our own crew quests. | Both ELIMINATE (WAVE 1). Our Stranded quest is read as *not* retired; please confirm. |
| C08 | Skill ladders | **ANSWERED: remove both.** Skills stay vanilla. | VSE and Alpha Skills ELIMINATE (WAVE 1). |
| C09 | Event layers over Randy | **ANSWERED: keep only what makes danger different.** Study the others. | Large Faction Bases, Storyteller Enhanced and Rimesis ELIMINATE (WAVE 1). Better Infestations' own events off. Faction Raid Cooldown and More Faction Interaction wait for the study. |
| C10 | Convenience and automation | **ANSWERED: cut them all, then add back only what we need.** | 9 mods ELIMINATE (WAVE 1). Replacements are designed in `design/RimMandrake/convenience_replacements.md`. |

---

## Theme 2. The world and the tools that build it

### C05. The world generators: do they leave once the remake is saved?
**The decision.** The world is remade once, as the last step, and then frozen. These mods only matter for generating or
sizing a world, so once the remake is saved they have no job for players.
**Mods:** Alien Worlds and Tidally Locked (`7f.alienworlds`, `7f.alienworlds.tidallylocked`), My Little Planet
(`oblitus.mylittleplanet`; the 21,872-tile world probably depends on its size settings, INFERRED), Sensible Factions
(`boots.sensiblefactions`).
- **A. Keep them until the remake is saved, then take them off the player list.** *Buys:* no worldgen code ships.
  *Costs:* we must first check that the saved world does not need their defs or types to load.
- **B. Keep them in the player list for good.** *Costs:* worldgen code ships, although players never generate.
**Recommendation: A.** There is no worldgen feature in any version, and removing them is mostly a technical check.
**A separate question, same card:** Faction Territories (`jaeger972.factionterritories`) is not a generator. While you play, it lets
factions grow, found new settlements and invade by territory. **Should factions be able to add settlements to the frozen world
during play?** *Yes* keeps a living map and makes raids depend on settlement count. *No* means the mod goes, or its expansion is
switched off (`FACTION_TERRITORIES_VERIFY_SETTINGS` reads the setting).
**Evidence:** CLAUDE.md "no worldgen"; `records/batch_01.md`, `records/batch_03.md`, `records/batch_05.md`; GPT review §6 C05.

### C06. Map-generation tools that can overwrite our biomes' terrain
**The decision.** Geological Landforms (and Biome Transitions) reshape generated maps and can overwrite what our biome
generators draw. Map Designer silently caps how dense our plants can grow. The world is frozen, but every landing site and quest
map is still generated when you arrive, so this matters for the whole game.
**Mods:** `m00nl1ght.geologicallandforms`, `m00nl1ght.geologicallandforms.biometransitions`, `zylle.mapdesigner`.
- **A. Keep them everywhere, and patch each of our biomes to opt out.** *Costs:* a patch per biome, forever.
- **B. Keep them only on vanilla-biome tiles.** *Costs:* one compatibility layer.
- **C. Retire all three. Map Designer survives only as your map-repair tool, off the player list.** *Costs:* landforms
  (cliffs, valleys) vanish unless our own generators draw them.
**Recommendation: C**, accepted only once maps generated with and without them are compared on the same landing sites.
Our biomes are meant to own their terrain and density.
**Evidence:** `records/batch_08.md`; `checks/check_group_1.md` (Map Designer).

## Theme 3. The ship, the base and convenience

### C11. Is the Utinni the only ship, and what else moves?
This is five smaller choices. Each can be answered alone.
**Mods:** Trystan's shuttles (`trouperton.trystantravellersshuttleschematics`), the KotOR ship pack and Gravship Blueprints
(`btd.gbp.shippack.kotor.vge`, `btd.remix.gravshipblueprints`), Gravship Raids capture (`sk.gravshipraids`), Deep Orbit
(`broms.deeporbit`), Walk the World (`addvans.walktheworld`), Vehicle Framework (`smashphil.vehicleframework`), Vanilla Vehicles
Expanded (`oskarpotocki.vanillavehiclesexpanded`, landspeeders and skimmers; you cut 12 of its 23 vehicles on 2026-08-12),
Raid Vehicles (`gabrieel1482.raidvehicleframework`), Alpha Vehicles Neolithic (`sarg.alphavehiclesneolithic`), our Desert
Vehicle Reskin (`mandrake.rsw.desertvehiclereskin`), Non-Destructive Grav Launch (`planetace.nondestructivegravlaunch`).
1. **Other ships.** *Only the Utinni* (shuttles, ship packs and the orbit layer go), or *other hulls allowed*.
2. **Captured enemy gravships.** *Stripped for parts only*, or *flyable*. Flyable gives the player a second hull.
3. **Ground vehicles.** *Carts only* (our reskinned carts), *carts plus motor vehicles* (VVE landspeeders and skimmers, cargo
   and mobility only), or *none* (Vehicle Framework goes).
4. **Enemy vehicles in raids** (Raid Vehicles). *Yes* or *no*.
5. **Leaving on foot.** Walking off the map edge to another tile on the same layer: *allowed* or *cut*. And should a camp left
   behind when the ship launches *persist* or *vanish*?
**Recommendation:** 1 only the Utinni; 2 stripped for parts; 3 carts plus the VVE vehicles you already kept; 4 no; 5 walking cut, camps persist.
This keeps the single-hull fantasy and the vehicle work already done.
**Evidence:** `records/batch_05.md`, `records/batch_06.md`, `records/batch_13.md`, `records/batch_14.md`, `records/batch_16.md`;
V2_DREAMS §0b/§0c; `required_mods.md:1043` (VVE guardrail "mobility plus cargo only").

### C12. Bigger Gravships: are its fuel-tank and shield numbers intended?
**The decision.** The live settings hold twelve values, not the four in our design notes. The chemfuel tanks (1,140 and
8,805 capacity), 20 small thrusters and the shield values touch the fuel-scarcity pillar. A bigger tank does not create fuel:
it lets one load last longer, at the cost of deck space and mass.
- **A. Freeze them as they are.**
- **B. Reset the tank and shield values to vanilla, and freeze the rest.** *Costs:* shorter range between refuels, which may break
  routes you already fly.
- **C. Measure first:** compare capacity, burn rate, range and deck cost against vanilla in one flight, then decide.
**Recommendation: C.** We do not know yet whether the big tanks undo scarcity or only reduce refuelling chores.
**Evidence:** `Config\Mod_3522759531_GravshipSizeSettings.xml`; `checks/check_group_1.md` item 2; ACTIONS_NOW B2.

### C13. Industry and salvage: how much free production?
Three choices.
**Mods:** VFE Factory (`vanillaexpanded.vfefactory`; our Wrecked Machines hard-depends on it today), Better Cremation
(`thumb.bettercremation`, returns the metal from burned clothes), Bones (`sihv.rombonesport`, buildable bone items).
1. **The factory machines.** *Replace them one by one with Wrecked Machines restoration tiers* (VFE Factory stays underneath as the
   engine until nothing uses it), or *keep VFE Factory's machines as the industrial tree*.
2. **Cremation salvage.** *Our own salvage yields* (drop the mod), or *keep it*.
3. **Bone building.** *Port it*, or *drop it*.
**Recommendation:** 1 replace by restoration, 2 our yields, 3 drop unless you want bone building. Restoring wrecked machines is the Jawa
fantasy. One salvage rule stops double rewards.
**Evidence:** `records/batch_02.md`, `records/batch_04.md`, `records/batch_07.md`.

## Theme 4. Combat and gear

### C14. Yayo's Combat 3, given that Combat Extended is banned
**The decision.** The ban covers "equivalent total combat overhauls". Our weapon register's armour-penetration numbers are
calibrated on Yayo's. Yayo's has separate options for armour, accuracy and ammunition.
**Mods:** `mlie.yayoscombat3`; Stronger Scaling (`kas.strongerscaling`, masterwork gear much stronger).
- **A. Yayo's stays as a named exception, with its option set written down** (which of armour, accuracy and ammo are on). Stronger Scaling goes.
- **B. Remove Yayo's and recalibrate the weapon register on vanilla.** *Costs:* every weapon re-tuned.
**Recommendation: A.** Recalibrating every weapon is large work for no gain to the scenario. Writing the options down stops them drifting.
**Evidence:** `forbidden_mods.md:151-153`; `checks/check_group_3.md` "Ruling conflicts".

### C15. Donor content you once ruled out that is still loaded
Five choices.
**Mods:** Vanilla Weapons Expanded (`vanillaexpanded.vwe`, 125 weapons, "lean-skip" but active and rebalanced by Armoury),
VQE Ancients (`vanillaquestsexpanded.ancients`; "drop entirely" on 2026-08-03; about 60 of our patches now use its creatures),
Alpha Mechs (`sarg.alphamechs`), Destiny exotics (`milkwater.destinymod`), Warcasket's three extra suits (`aoba.warcasket`).
1. **VWE guns.** *Keep the rebalanced ones and drop the rest*, or *drop all*.
2. **VQE Ancients.** *Keep its creatures* (port later) *and drop its quests*, or *drop entirely*.
3. **Alpha Mechs.** *Keep as enemy threats only* (players cannot craft them), or *drop*.
4. **Destiny exotics.** *Drop*, or *keep*.
5. **Extra Warcasket suits.** *Drop*, or *keep*.
**Recommendation:** 1 keep the rebalanced; 2 creatures only; 3 enemy threats only; 4 drop; 5 drop. Patches already written are a
reason to port later, not to undo now.
**Evidence:** `records/batch_07.md`, `records/batch_09.md`, `records/batch_11.md`.

## Theme 5. Look, sound and tone

### C16. Pawn faces
**The decision.** Facial Animation and its add-ons give pawns faces in several styles: cartoon, anime, Roblox-like (Reel,
Danzinagri, parts of the Genetic Heads packs). Cosmetic changes need your permission because they can break animated faces.
**Mods:** `nals.facialanimation`, `nals.facialanimationexperimentals`, `reel.facialanims`,
`danzinagri.facialanimationcompatabilityproject`, `vanillaexpanded.vtexe.facialanims`, `sd.fa.geneticheads*`.
- **A. Vanilla-style and our own faces only. The stylised add-ons go, and Facial Animation stays.**
- **B. Keep all styles.**
- **C. Drop animated faces entirely.**
**Recommendation: A.** It keeps the look the founders already have. How much memory each option saves is not known yet. The
figures so far are estimates from image sizes, and our own art packs are estimated as large as the face packs.
**Evidence:** `records/batch_07.md`, `records/batch_11.md`, `records/batch_14.md`; CLAUDE.md:831.

### C17. How far does "no donor art kept" reach?
Three separate questions.
**Mods:** Ambience (`swablu.ambience`, sound), our Rust Chrome UI (`mandrake.rm.rustchrome`, a recolour of vanilla buttons), Slave
Outfits (`usgiyi.slaveoutfits`, functional apparel), Space Base Furniture (`mingtuwuxiang.spacebasedecorative`, about 500 MB of
ship furniture art), the three Adaptive Storage model packs (`adaptive.*storage`), Roots of RimWorld tribal decor
(`ghost.rootsofrimworld`).
1. **Sound recordings.** *Covered* (replace in time), or *not covered*.
2. **Interface art**, including recolours of vanilla art. *Covered*, or *not covered*.
3. **Apparel and furniture that players see in the world.** *Covered* (redraw it like any donor), or *keep it where it is functional*.
**Recommendation:** none. This is a question about the scope of your rule, and each answer costs a different amount of redraw work.
**Evidence:** brief §2 "no donor art"; `records/batch_02.md`, `records/batch_11.md`, `records/batch_13.md`, `records/batch_15.md`.

### C18. Heavy visual extras: worth their memory?
**Mods:** Planet Atmosphere (`rwnodetree.rwplanetatmosphere`), EGI Holograms (`vesper.egihologramsandprojectors`; holograms
are on-genre, since the gods are holograms), Minerals Rock shapes (`zacharyfoster.mineralsrock`), Glowing Bush (`fourtoo.glowingbush`).
- **A. Measure what each really costs in memory (`HEAVY_TEXTURES_MEASURE_REAL_VRAM`), then decide one by one on value against cost.**
  For EGI, keep only the holograms the gods use.
- **B. Cut all four now.**
**Recommendation: A.** Today's figures are estimates from image headers and may be wrong by a lot. Redrawing does not by itself
save memory; image size and count do.
**Evidence:** `records/batch_10.md`, `records/batch_11.md`, `records/batch_14.md`.

### C19. Off-tone mods: approve the cut list
**Mods:** Metal Pipe and Metal Pipe Horseshoe (`flangopink.metalpipe*`), meme tantrum sounds (`kshtantrumsounds.mod`), Monty Python
melee sounds (`bonible.medievalmeleesounds`), FancyRats (`armoredampharos.fancyrats`, `tyrannidae.fancyratsplus`), Dark Ages
Crypts (`van.dacrypts`), Dark Ages trolls (`van.beasts`; the faction is already decided, so only the troll creatures and two
letters remain), Dredge aberrations (`aqued.dredgeaberrations`), Ideology Virtues (`dimonsever000.ideologyvirtues`).
(Torment Master, `vlvop.tormentmaster.expansion`, is listed but not installed. It is just removed from the list, with no card needed.)
- **A. Cut them all.** First, the save is checked for placed things. Where our patches touch them, the patches are cleaned up:
  Crypts, Beasts and the ideology export do reference some of these.
- **B. Name the ones to keep.**
**Recommendation: A.** None fits the desert Star Wars tone. The creature cuts happen at each biome's sitting, not in one sweep.
**Evidence:** `records/batch_02.md`, `records/batch_10.md`, `records/batch_13.md`, `records/batch_14.md`.

## Theme 6. Peoples and factions

### C20. Non-canon peoples as NPC variety
Two questions.
**Mods:** Avaloi (`det.avaloi`, psychic genes), Beliar (`elsov.beliar`), Alpha Genes (`sarg.alphagenes`, 16 xenotypes plus gene labs),
Posthuman Drift and Titan (`xylthixlm.races.core`, `xylthixlm.races.titan`), VRE Starjack (`vanillaracesexpanded.starjack`, space-adapted),
VRE Archon (`vanillaracesexpanded.archon`), Orc Clan (`karew.orcclan`). Two are already rethemed by your ruling (Orc Clan to
Gamorreans, Archons to Mortis wanderers).
1. **Who the player meets.** *Our roster only* (rethemed outsiders stay until ported, the rest go), *rethemed outsiders welcome*, or
   *all as background variety*.
2. **What the player can build.** Should gene labs and outside genes be *reachable by the player*, or *NPC-only*?
**Recommendation:** 1 our roster only; 2 NPC-only. The rethemes show the intent, and NPC-only genes keep player biology on our own roster.
**Evidence:** `src/RimUtinni/UtinniPatches/Patches/{OrcClan_GamorreanRename,VREArchon_MortisRename}.xml`; `records/batch_07.md`, `records/batch_10.md`, `records/batch_13.md`.

### C21. RimTek: keep the datapad mods?
**Mods:** RimTek Core, DocMate, DigiPal (`deon.rimtek.core`, `.docmate`, `.digipal`). DocMate (a device that treats patients on
nearby beds) needs Core. DigiPal is a belt that gives a flat bonus to melee and ranged accuracy.
- **A. Keep all three.**
- **B. Keep Core and DocMate. Remove DigiPal.** *Buys:* no free accuracy bonus.
- **C. Remove all three.** *Costs:* we build our own auto-doctor if you want one.
**Recommendation: B.** The flat accuracy buff is the problem, not the look. DocMate is the only thing that needs Core.
**Evidence:** `MASTER_REGISTRY.jsonl` deon.rimtek.* ; `checks/check_group_1.md` item 4.

### C22. Physically remove mods whose content Cherry Picker already cut?
**The decision.** Doctrine says to trim with Cherry Picker rather than uninstall. Some mods are now near-empty shells that still
load code and art.
**Mods:** the Ancient Urban Ruins family (`xmb.ancienturbanruins.mo`, `meteores...aurvl`, `meteores...aurad`; AURAD is already
forbidden by name) and Big and Small Races (`redmattis.bigsmall`; 83 of its 85 defs cut).
(Custom Quest Framework stays: Dungeon Pack, which we keep, needs it. Medieval Flavour is *not* a shell today. Its 26 lost cuts are
restored first, ACTIONS_NOW C9.)
- **A. Uninstall a mod once it has no behaviour we keep, no mod of ours that needs it, and nothing in the save.** The doctrine gets this
  exception. *Buys:* less load time and code.
- **B. Keep the doctrine. The shells stay.**
**Recommendation: A.** The test is "nothing kept, nothing needs it, nothing saved", not a percentage.
**Evidence:** `ancient_ruins_mod_audit.md` §Recommendation; git `6cadd01c4`; `checks/check_group_3.md` "Ruling conflicts".

## Theme 7. Our own systems

### C23. The talking ship: when does the Oracle speak?
**The decision.** In-game AI goes through `claude -p` (your 2026-09-05 ruling). The two RimAI mods (`kilokio.rimai.framework`,
`kilokio.rimai.core`) talk over the internet, so they go either way. The open choice is the Oracle's v1 role.
**Mods:** `mandrake.rm.oracle`, `kilokio.rimai.*`.
- **A. The Oracle ships dormant in v1** (fixed text, debug actions). *Buys:* the game is whole with no AI.
- **B. The Oracle ships live as the god-letter narrator.** *Costs:* needs Claude Code installed and logged in on the player's machine,
  and must be tested with it missing, logged out, slow and failing.
**Recommendation: A.** The game must be whole with the AI absent. Live can come later.
**Evidence:** CLAUDE.md "In-game LLM access" (2026-09-05); `records/batch_01.md`, `records/batch_12.md`, `records/batch_15.md`.

## Theme 8. New questions from the GPT review

### C24. What limits must the released game meet?
**The decision.** Right now the full list loads in about 15-21 minutes, uses about 30 GB of memory, and runs at 8-10 game speed
(TPS) on the measured map. Without targets, "is this mod worth its cost" has no answer.
- **A. Set targets now**, for example: load under 10 minutes, memory under 16 GB, 60 TPS on a normal map, measured on your desktop.
  *Buys:* every keep/cut decision gets a yardstick. *Costs:* some kept mods may then have to go.
- **B. No hard targets; fix the worst offenders as they are measured.**
- **C. Targets for a stated "minimum player machine"**, not yours.
**Recommendation: A, on your desktop first.** It is the only machine we can measure, and the numbers can be revised.
**Evidence:** `facts/session_context.json` (TPS, private memory); GPT review §8 Q1.

### C25. When the world is remade, what must the founders and the ship carry over?
**The decision.** The remake keeps the map, the gravship and the founders. "The founders" can mean just their bodies and skills, or
everything about them.
- **A. Everything:** genes, relationships, ideology, inventories, installed parts, bills, damage, ownership, and their story and god state.
  *Costs:* any mod that defines one of those things cannot be retired before the remake.
- **B. Bodies, genes, skills and the ship hull. The rest is re-authored after the remake.**
- **C. You list what matters.**
**Recommendation: B.** It frees the most donors before the remake. Story state is ours to re-author anyway.
**Evidence:** memory "world remake is the last step"; GPT review §8 Q2 (founder genes from `lovelydovey.sex.withrosaline` are save-critical).

---

## Not carded: questions already answered by a ruling

| mod(s) | question that was raised | answered by |
|---|---|---|
| `cain.mineshaft` | keep Mines 2.0? | owner override 2026-08-12, `design/Jawa/desert_world_design.md:488` |
| `mlie.storytellerenhanced` | which storyteller? | Randy, ratified: `SCENARIO_SETTINGS_SPEC.md` R-S7; the mod itself was then dropped by C09 (2026-10-10) |
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
