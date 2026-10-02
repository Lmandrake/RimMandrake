# RUSTCATHEDRAL_WORN_BIT_ARC_1 — The Worn Bit: take the borehulk's drill off, have the Junkers refurbish it, bring it back, restore the giant; then keep it or free it

Caused by `RUSTCATHEDRAL_SCORING_SITTING_1` (turn 1). Mechanism free tier (`mandrake.rm.rustcathedral`),
campaign wiring in `mandrake.rut.rites` and `UtinniPatches` (part 6). Design:
`design/Jawa/worldbuilding/biomes/rustcathedral_mining_droid_hooks_2026-10-02.md` §2 (the pitch, now
superseded where the owner's words below differ), review
`design/Jawa/worldbuilding/biomes/rustcathedral_bedazzle_review_2026-10-02.md` §8.

Ruling, owner, typed 2026-10-02: *"I like the Worn Bit. This should be a MAJOR pain to repair. Gotta take
its drill off, bring it to the Junkers for refurbishment, then bring it back to restore it along with a
bunch of other unusual components. Taking the droid for yourself earns the droid that mines wherever you
tell it to (and this should be very cool, because it's expensive materially and politically). Leaving it
free earns major favor elsewhere as stated, but it will not mine the Rust Cathedral where you point of
course."*

**Reconciled with the droid-repair rite** (`RUSTCATHEDRAL_STRANGERS_OVERHAUL_RITE_1`): the final stage
(stage 4) **is** the Stranger's Overhaul performed on the borehulk, and the rite's own fork is the arc's
fork: the rite's **capture** branch is *keep it*, the rite's **complete and release** branch is *free it*.
The arc adds the three stages before it, the giant's payoffs, and multiplies the rite's political and
divine effects (the "major" in his words). Where the pitch differs it is superseded: the pitch had Rekko
and Ta'Baa reacting and a released borehulk digging where you mark; the owner's version has neither.

**The Junkers** exist: `FactionDef RUT_Jawa_Junkers` (`src/RimUtinni/UtinniPatches/Defs/FactionDefs/JawaJunkers.xml`;
`design/Jawa/worldbuilding/FACTION_SPEC.md` §12): *"The bottom of the scrap heap, given weapons and a
grudge"*, category Pirate, **hostile on sight but bribable**, `permanentEnemy false`, settlements on wreck
fields and tailings, **no trader caravans** (`canRequestTraders false`: *"a loot source, not a market"*),
leader title Scraplord. So the refurbishment cannot ride a caravan trade or a settlement trade screen; it is
a **work order** delivered to them, specced below.

## spec

Owner-level shape: four stages, each a real cost, each readable; nothing of the Cathedral's mind explained
(sheet §6 ban 1). Every number below is a Mod Settings default.

1. **Stage 1: take the drill off.** Available when a colonist selects the borehulk (comp state `Worn`,
   `RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1`) during a calm band (band 0 or 1). A float-menu order "Unbolt the
   drill head" starts a **long multi-visit job** `RM_Job_UnbitBorehulk`: total work about 6,000 ticks at
   Construction 8+, needing at least two colonists working at once (the second "holds the boom"; a lone
   worker makes no progress), and it can only progress while the borehulk stands still (it idles, then
   wanders off; progress is saved on the comp and resumes on the next visit). A hum drop below band 1
   stops the work (everyone freezes, the bolts first). On completion the comp goes `Unbitted` and
   `ThingDef RM_WornDrillHead` drops: an enormous item, **mass 250 kg** (cannot be carried by one colonist
   on foot; a pack animal, a vehicle, a caravan or the gravship hold).
2. **Stage 2: to the Junkers.** Unbitting fires a quest offer `QuestScriptDef RM_WornBitRefurbishment`: a
   world site `RM_RefurbishYard` appears within a travel range of a settlement of the refurbisher faction
   (part 6), the vanilla peace-talks shape (a world object with an arrival dialog). The player brings the
   drill head there by caravan or by ship, plus a fee (silver, default 1,500, scaled by wealth; a bribe, in
   their register). The arrival dialog: hand it over and pay, haggle (Social; a failed haggle raises the
   fee), or leave. The yard keeps the head for **10 days**; the quest timer shows it.
   - It is a major pain on purpose: the drill head is too heavy to fly in a shuttle pod; the yard's
     hostility is real (a Junker faction is hostile on sight; the site is a **truce yard**, peaceful only
     while the work order stands: attacking it voids the order and loses the head); and on the return visit
     there is a warned chance (default 0.35) the Scraplord demands a second payment ("the price went up"),
     with the choice to pay, haggle, or fight for the head at the yard.
3. **Stage 3: bring it back.** Collect `ThingDef RM_RefurbishedDrillHead` (same mass) and carry it to the
   map where the borehulk lives. The borehulk is still on its Rust Cathedral map (a map with a quest-kept
   borehulk is kept alive: a world-object or quest lock the builder measures; it never despawns unseen; if
   the map is abandoned the quest says so and the borehulk waits in the world record for the next landing).
4. **Stage 4: restore it (the Stranger's Overhaul on the giant).** With the refurbished head on the map and
   the components in a stockpile, the Overhaul rite (built by `RUSTCATHEDRAL_STRANGERS_OVERHAUL_RITE_1`)
   accepts the borehulk as a target only now. Its repair consumes **the refurbished head plus a set of
   unusual components** (a list in a def, `RM_BorehulkRestorationDef`, tunable): 1 `RM_RefurbishedDrillHead`,
   12 `RM_DeadSmartsteel`, 6 `ComponentSpacer`, 3 `RM_BoltShedCuriosity` (the bolts' shed parts: an
   unusual, watched component), 2 `RM_CoolantEelCatch` (rendered to coolant grease; a desecration the
   Cathedral already prices), 1 vanilla `PowerfocusChip` or another rare chip that exists in the def dump
   (measure; never guess a defName). The work is long (two sessions minimum), Crafting 10+. The rite's
   mid-repair choice is the arc's choice:
   - **Keep it (the rite's capture branch).** The borehulk joins the colony. Payoffs and costs:
     - **It mines wherever you tell it.** A player area `RM_Area_BorehulkDig`; the borehulk mines every
       mineable cell inside it, any rock, at a very high speed (about ten times a colonist), dropping the
       normal yield. That includes the Rust Cathedral's plate **and** its sacred tiers if the player draws the
       area over them: every sacred cell it mines is the player's sacrilege under the ruled economics (−15 per
       sacred building, the hum), and the inspect line warns before the first such cell. It never mines deep
       (no drilling below the surface; ban 6 untouched).
     - **Expensive materially:** a maintenance need on the comp; every 5 days a colonist must service it
       (a job consuming 2 `ComponentIndustrial` + 30 `Chemfuel`), or it stops digging and stands idle (never
       hostile). Its armour and strength stay.
     - **Expensive politically:** the rite's capture deltas multiplied (default ×3): Free Droid Enclaves
       goodwill (the neutral droids) falls hard; the Cathedral's irritation jumps and, in the campaign, its
       Regard falls (`CATHEDRAL_REGARD_BLACKBOARD_1` reads the event); Ozzik's displeasure; Mob'Unloo and Ohm
       pleased. While it serves the colony, each landing on Rust Cathedral ground starts the hum a band
       lower (a standing sign, read from the comp; readable through the hum readers).
     - ⚠️ **Ownership path, measure first:** a player-faction mechanoid with no mechanitor is not a vanilla
       state. Read the engine (RimSage) for the overseer requirement and either exempt `RM_Borehulk` by a
       `DefModExtension` checked in one patch, or ride the Droidworks player-droid path if it already solves
       owned machines without a mechanitor. Never make it require a mechanitor (it is not a Biotech mech in
       the fiction).
   - **Free it (the rite's complete-and-release branch).** The borehulk stays wild on its map, drill
     restored (comp `Restored`): it now really bores plain deck plate on its own now and then (cells mined,
     plain tier only, yield left where it falls). It **answers favours, not orders** (question card 2026-10-02 10:44
     PDT): no dig area and no command, but when the colony asks (a comms/letter request, a few times a
     year, cooldown in Mod Settings) it comes to help on a dig job as a friend would, on any map except the
     Rust Cathedral, where it never mines for you. Each favour shows as a letter and an inspect line. The payoff is **major favour elsewhere**: the
     rite's release deltas multiplied (default ×3): Free Droid Enclaves goodwill rises a lot; the Cathedral
     calms (irritation falls) and, in the campaign, Regard rises; Ohm pleased; Mob'Unloo annoyed. Each
     shows as the rite already shows it (goodwill numbers on the faction screen, the hum's band, the
     Narrator for the gods; never a buff).
   - **Leave it unfinished:** the components consumed so far are lost; the head stays fitted or not, as the
     work reached; the offer stays open.
5. **Readable signs throughout:** the inspect line per stage (*"Its drill head is gone."* / *"A
   refurbished drill head is fitted."*), the quest log, letters at each stage, the dig area overlay, the
   maintenance bar on the comp, the borehulk visibly working (or not).
6. **Tier split (Q11a: the free mod plays the same arc).** The refurbisher is data:
   `RM_DrillRefurbisherExtension` on a `FactionDef`. The free tier puts it on vanilla `Pirate` (scrappers,
   approached by the same truce-yard work order); the campaign patch
   (`src/RimUtinni/UtinniPatches/Patches/RUT_WornBit_Junkers.xml`) removes it from `Pirate` and puts it on
   `RUT_Jawa_Junkers`, and relabels the yard's dialog in the Junkers' voice (the Scraplord). God deltas and
   Regard exist only in the campaign (the rite is campaign); the free tier keeps the goodwill and hum
   effects (the free tier's "neutral droids" is no faction: the goodwill line applies only where a faction
   carries `RM_NeutralDroidsExtension`, which the campaign patch puts on `RUT_Jawa_FreeDroidEnclaves`).
7. **Mod Settings:** on/off; fee; refurbishment days; second-demand chance; maintenance interval and cost;
   political multiplier; dig speed.

Depends on: `RUSTCATHEDRAL_BOREHULK_GIANT_BUILD_1`, `RUSTCATHEDRAL_STRANGERS_OVERHAUL_RITE_1` (stage 4 and
the fork), `RUSTCATHEDRAL_FREE_NAMES_TIDY_1`. Campaign wiring: `SALVATION_RITES_UNIFICATION_1` (rite
machinery), `CATHEDRAL_REGARD_BLACKBOARD_1` (Regard reads the keep/free event; without it, the campaign
Regard line is a logged would-be, never silent). Art: `RM_WornDrillHead`, `RM_RefurbishedDrillHead` in
`infrastructure/artpipe/art_lists/rustcathedral_turn1_2026-10-02.csv`.

## criteria

Deterministic state reads through `jawa/get_defs` and debug `[Tool]`s, recorded as cases in
`RUST_CATHEDRAL_FIRST_SCRIPT_1`'s `validation.py` (campaign cases in `src/RimUtinni/Rites/validation.py`):
- Defs resolve: `ThingDef/RM_WornDrillHead`, `ThingDef/RM_RefurbishedDrillHead`,
  `JobDef/RM_Job_UnbitBorehulk`, `QuestScriptDef/RM_WornBitRefurbishment`, `WorldObjectDef/RM_RefurbishYard`,
  `RM_BorehulkRestorationDef` (one def), both drill heads with mass ≥ 200.
- Stage 1: with one colonist assigned, comp progress after 2,500 ticks is unchanged; with two, it rises;
  setting the band to 2 stops progress; at completion comp state = `Unbitted` and one `RM_WornDrillHead`
  exists on the map.
- Stage 2: unbitting creates exactly one active `RM_WornBitRefurbishment` quest and one `RM_RefurbishYard`
  whose faction carries `RM_DrillRefurbisherExtension`: `Pirate` on the free tier, `RUT_Jawa_Junkers` with
  the campaign loaded (and `Pirate` then carries none). Delivering the head and fee starts a timer equal to
  the setting; attacking the yard ends the quest with the head lost.
- Stage 3/4: with the restoration def's items present, the Overhaul's target filter accepts the borehulk;
  with any one item missing it refuses with a reason naming the item.
- Keep: borehulk faction = player; comp state `Restored`; cells inside `RM_Area_BorehulkDig` count down to 0
  mineable over simulated time; after 5 days unserviced its dig job stops and it is not hostile; Free Droid
  Enclaves goodwill (campaign) and the hum irritation moved by the setting's multiple of the rite's capture
  deltas (read before/after); a sacred cell in the area records a sacrilege event.
- Free: borehulk faction null; comp `Restored`; no dig area or draft order is offered (float-menu and gizmo
  lists read empty of them); over 60,000 ticks it mines ≥ 1 plain-plate cell and 0 sacred cells; goodwill and
  irritation moved by the multiple of the release deltas.
- Campaign: Ninefold logs deltas tagged "The Worn Bit" for exactly the gods the branch names, with the
  branch's signs (Mob'Unloo +, Ohm +, Ozzik displeased on keep; Mob'Unloo annoyed, Ohm + on free).
- No hediff or stat buff is added to any colonist by any stage.
- Each Mod Settings toggle off removes exactly its effect.
