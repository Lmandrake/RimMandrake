# Page one — what the Cracked Lands now are

The Cracked Lands are dry canyon country where shade and high ground decide where you can live. Water chimes announce a flood that fills the canyon floor from bank to bank, so you leave useful work behind to get people out. When the water drains, wet mud feeds a short burst of plants and small animals, then the ground dries and the canyon grows quiet again.

**Land:** cracked pans, stained cut walls, dry skies, shaded vegetation and accessible upper banks with refuges cut into the cliff.

**Life:** the existing alien roster and ordinary gathering, materials, predators and calls, with real flight for present fliers; wet plants, irqit and pan sleepers show the changing conditions. No roster eviction.

**Signature:** heed chimes, escape dangerous water, use its brief wet aftermath, return to dry work.

The runner-up was hidden-water discovery and the carried Swale technique. I moved that separate prospecting/water/unlock loop to next version; escape and wet life do not need it. These are my scope decisions under this pass, not new words attributed to you.

**Next version, off:**

- Wind/ticking/hush herald sequence; core chimes and roar stay.
- Reactive uttaqar wound-stone and rock disguise.
- Salvage scatter, stakes, rival crews and repeated wreck rewards.
- Collectible fossil seams, recutting, goods and unique identities.
- Talus prying, mining bonuses and fossil drops; passive plants stay.
- Zennaq filament and luqqim lighting; ordinary plants stay.
- Wax suit and its missing protection.
- Special Acoustic Scanner payload.
- Hidden-water surveys, veqma blush and prospecting cisterns.
- Canyon Swale refill/integration and discovery unlock; external FlowWorks stays.
- Muttavaq hydraulic trail; wet waking and dry sealing stay.
- Special titan passages, toll encounter and bloom-market pricing.
- A new invented free-tier flier; current flight requirements cover present fliers.

**Recommend retiring:** obsolete planet placement, mood carvings, the newer decorative fossil case, and lithops metal/stone production. They conflict with a standing ruling or add duplicate reward/decoration mechanics. Previously retired display mounts, lightning attraction, dust reversal and timed migrant arrivals remain out; their recorded exclusions are not reopened. Built deferred/recommended extras keep their code and defs behind gates; prohibited worldgen never gains a next-version enable option.

**Counts:** capabilities 81 before → 49 kept; next-version 24; recommend-retire 8, including historical exclusions. Bars 0 before → 8 proposed; live-only bars 0 before → 4 proposed. Before-bar counts come from the CASE’s empty old-bar set; capability counts use this source-expanded census consistently, including dependencies and missing promises. Checks 15; rules 13; unknown shared meetings 7; models 4; tickets 32; questions 0. These are the counts in result.json.

# Page two — what to check

**Decisions that matter:**

- “Wall to wall” is literal across the open canyon bed. A capped random patch cannot pass. A saved local canyon layout must supply the bed, banks, upstream order and access; this does not generate a planet.
- A roof shades but does not elevate. Low covered rooms remain exposed to the flood; floors and excavations retain their ownership.
- Your November answers supersede the earlier injury ceiling: impact and drowning can kill; death is not compulsory. Prompt recall gets mobile people clear; finishing slow freight remains risky.
- Wet fertility expires. Floods deposit ordinary soil on wetted natural bed in shared geometric shade, including campaign sand. It lasts while shaded; exposed bed returns to mineral ground. Repeated floods cannot enrich it further or spread it into unwetted neighbours. Native gathering/growth matters, a newly sown crop harvest does not.
- Rewetting extends only the places reached again. Another flood elsewhere cannot extend an old irqit cohort’s life. Carrying/exporting an irqit must not erase its lifespan or make it vanish.
- A sleeping pan is the same inspectable animal, not a disappeared pawn. Hydraulic terrain editing is separate.
- Shared geometric shade governs plants and sun exposure. Keep the plant-def glow law too; neighbour counts cannot redefine sunshine.
- The external free-tier Swale stays normal. The campaign still requires discovery; delaying its discovery loop does not authorise a free unlock. It is outside the retained biome’s unlocked whole test.
- Existing rosters stay. The free roster has no flier; adding one waits for next version. Present fliers must fly, proved by actual flight-tracker state during feeding travel and landing. Looks/captures exclude flight; visual flight requires a joint session with you.

**Models, first to build first:**

- Canyon geometry and evacuation: full cross sections, genuine upper refuge capacity, crowd paths and warning margins.
- Situation and lifecycle generator: contact, damage-adapter cases, wet overlap, player edits, transported animals, disable/re-enable and actual save/load.
- Whole canyon season and resource budget: bounded soil deposition, wet fertility, growth terminals, animals, corpses/Bones, work and weather together through dry return and accumulated history.
- Shade and plant eligibility sweep: compare plant and deposited-soil sites to shared geometric shade, roofs and plant glow limits.

Each model has its inputs, sweep, limits, real-game calibration, outputs and decision trigger in models.md. None is built or claimed as a game measurement.

**Unsettled:** whether the complete geometry, evacuation timing, wet feedback and saved lifecycles actually hold together. Those shared meetings are explicitly unknown and assigned instruments; they are not requests for you to predict measurements. Current source still uses patch flooding, a light arrival hit and permanent rich soil, so this proposal is not a passing build. Fresh review identified the missing soil producer, impossible free-tier flight promise and forbidden visual flight reading; this revision repairs them and awaits the second look. The program’s reviewer must check this proposal before application, and nothing changes the mod until you have read these pages and said so.

## Still refused after the second look (the reviewer's words)

The proposal cannot be applied until each of these is resolved or you accept it.

- two bars, or a bar and a rule, that cannot hold together (bars.json B4 and R6 against B6 and R9; definition.md 'Living, grounded pawns contacted by the front receive an impact consequence...' and 'Muttavaq remains a pawn ... wet contact wakes it'). B4 says 'Grounded people and animals caught by the flood suffer impact and continued immersion danger that can kill'. R6 exempts only nonbreathers, real airborne creatures and unnamed 'shared trait' immunities. The muttavaq sleeps in the low pans, which are flood bed, and B6/R9 say water wakes it there. So under B4 every woken muttavaq is a grounded breathing animal standing in the front, and each flood can injure or drown it. The lore says the opposite. design/Jawa/worldbuilding/biomes/the_cracked_lands.md §4: 'The admission test: lives in the shade line, survives the flood'. cracked_lands_bedazzle_cast_2026-09-28.md: 'The flood wakes it wherever the water reaches ... Awake, it spends the flood-weeks feeding ... wading the wet canyon floor'. B6's 'seal again at the dry' relies on sleepers outliving the flood, while B4 and R6 make that a matter of chance. No file defines which native kinds are flood-adapted. The pawn_contact meeting is marked 'unknown' and sent to M2, but this is a missing definition, not a missing measurement. Would pass: A rule that names which native canyon-floor kinds are flood-adapted (at least the muttavaq woken by water) and what the flood does to them, consistent with the lore's admission test. B4's range and pictures distinguish flood-adapted natives from colonists, visitors and non-native animals. B6 gets an accept picture of a woken muttavaq standing in the front and later sealing alive, and a reject picture of the flood killing the pan sleepers it woke. Smallest fix: Add rule R6a: 'Native flood-adapted kinds (muttavaq; any other roster native the lore admits as flood survivors) take no flood impact or drowning; everyone else follows R6.' Add that class to B4.range.varies, add one accept and one reject picture to B6, and move the pawn_contact meeting's muttavaq case from unknown to argued.
- a sourced core promise omitted or weakened (owner_pages.md page one 'A new invented free-tier flier' under Next version; definition.md 'The current free roster has no flier ... recorded for next version'; census.json free_tier_flier_hole fate next_version; B6 'feeding fliers, wherever present'). the_cracked_lands.md §4: '⭐ The fliers live here (owner's ruling): ... this is the fliers' country'. §5 Always true: 'The fliers feed here and nest elsewhere'. §9: 'Motion: none, then the flood; fliers as the only daily movement'. CLAUDE.md (Q11a): 'A RM_ roster is rich enough to stand alone — never a thin fallback' and 'A hole in a roster is filled with a NEW creature'. In the proposal the free RM tier's 0.1.0 Life has no flier at all, and B6's flight clause holds vacuously there. That drops an owner-ruled defining part of the biome's life from the base tier by delegated default. Page two raises no question about it (questions: 0), although these two rulings are concrete evidence against deferring. Would pass: Either the free-tier feeding flier is kept in 0.1.0 as life, with its deletion argument citing §4/§5 and Q11a and a T31 build ticket carrying the B6 flight acceptance. Or the deferral goes on page two as one clear question that cites those rulings, takes the default, and says what changes if he answers otherwise. Smallest fix: Move free_tier_flier_hole to fate 'life' with needed_by 'life: the fliers' country (lore §4 owner ruling; Q11a no thin fallback)'. Drop 'wherever present' from B6. Turn T31 into a definition and build ticket. Failing that, add the question to owner_pages.md page two with this evidence.
- a kept mechanic with no definition (bars.json B1 'native green vegetation confined to shade'; checks C7; T29; census.json rows thorn_flora, harrovaq, ruqqal_cloth, sevvuq_dye, zennaq_ordinary, luqqim_light (all fate life)). B1 and its reject picture ('Green ground spreads across exposed flats') make shade confinement part of the land bar. The proposal defines shade placement only for Veqma (glow law plus geometric shade) and Nabbuq (C7, T29). The other kept flora are not covered. src/RimMandrake/CrackedLands/Defs/ThingDefs_Plants/RM_TwistingThorns.xml: the cracked thornwood has 'Tufts of olive leaf', fertilityMin 0.05, and no FloraLaw thingClass or glow limit, so it can grow on open-sun Sand. RM_CrackedLandsFlora.xml header: 'No green anywhere (only Veqma shows green, on the shade line)'. 'Green' is undefined, so one judge can pass olive-tufted thornwood on the sun flats as not green and another can refuse it under B1's reject picture. No rule says which kept plants are shade-bound and which are sun-tolerant and non-green. Would pass: A rule listing each kept wild plant as shade-bound (geometric shade, R3) or sun-tolerant and not green, with 'green' in B1 defined or marked figurative together with an accept picture. C7 and M4 cover every kept flora def, not only Veqma and Nabbuq. Smallest fix: Add rule R3a classifying the kept flora (thornwood, thorngrass, thornweed, harrovaq, ruqqal, sevvuq, zennaq, luqqim, nabbuq, veqma, qirra, talus) as shade-bound or sun-tolerant/non-green. Add a 'figurative' entry for 'green' to B1. Extend C7 to all kept flora.
