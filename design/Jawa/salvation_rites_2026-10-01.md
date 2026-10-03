# Salvation rites: where they live, every rite, and how a biome teaches one (2026-10-01)

_Status: BENCH design. Nothing below is built unless a row says so. Item:
`SALVATION_RITES_UNIFICATION_1` (supersedes `CONDITION_GATED_RITUALS_MOD_1`). Gods are canon of
record in `design/Jawa/divine_satiation_engine.md` §2.0b; rites-as-invitation is §5 to §5c there._

**The two rulings this doc applies** (owner, card Thu 2026-10-01 10:08 PDT, typed):

- **R1**, asked which of four rites the Abyss teaches: *"Unlike all four of those! Amazing! Each of
  these should do different sorts of appeasrmentsnif the utinni gods. I am starting to love the
  idea that you don’t just discover tech in the biomes you discover new rites."* ("Unlike" read as
  "I like".) All four are found in the Abyss's deep dark; each appeases a different god in a
  different way; biomes yield rites as well as tech.
- **R2**, asked for a mod name: *"This is part of the Jawas religion already. So it’s part of the
  salvation mod suite. Decide where rites go in there and unify them."* There is no separate
  rituals mod.

## (a) Where rites live

**Decision: every rite of The Salvation lives in `mandrake.rut.rites`, folder
`src/RimUtinni/Rites/`, display name "Salvation Rites" (owner, typed, 2026-10-01; deploy owed).** Why: it already exists, it is
already the Salvation's liturgy (a research tab whose rites are *"revealed, not bought"*), so a rite
found in a biome is one more revealed row in the tree the clan already reads, not a new mod.

The Salvation suite, as it now stands:

| Piece | Tier | packageId / path | Holds | Exists? |
|---|---|---|---|---|
| The ideoligion | RUT | `src/Jawa/ideoligion/The Salvation.rid` | the 103 precepts, 23 rituals, of the owner's approved ideo | yes |
| The gods' engine | RM | `mandrake.rm.ninefold` (`src/RimMandrake/Ninefold/`) | satiation/mood vector, bands, `ApplyDelta(God, float, reason)`; names no faith | yes |
| **The rites** | RUT | **`mandrake.rut.rites`** (`src/RimUtinni/Rites/`) | **every Salvation rite: the liturgy tab, found rites, their precepts, patterns, outcomes, discovery inscriptions, the darkness gate** | yes (tab and 5 research projects only) |
| The Salvation pack | RUT | `mandrake.rut.salvation` (does not exist) | non-rite sacredness: relic veneration precept, the grade-change subscriber (`ancient_machines_design.md` §5) | no |
| The lore record | RUT | `mandrake.rut.antiquities` | the stages that gate the liturgy tab's tiers | yes |

**The RM engine and RUT content split** (`ancient_machines_design.md` §1, `NAMING_SCHEME_PLAN.md`
§7.1): the gods' arithmetic stays in Ninefold; every rite calls it with `ApplyDelta` and never
reaches into it. The rite gate (the darkness condition, the mid-rite watcher) is C# **inside
`mandrake.rut.rites`**, not an RM engine, because the owner ruled the darkness rites
campaign-only (card 2026-10-01 09:22, Q4). If a later rite needs the gate outside the campaign,
the gate moves down to RM then, not now.

**What moves in.** A rite of The Salvation now has exactly one home. When each is next touched:

- `RM_Ishko_RitualOutcome_PlaceSacredMark` and its worker
  (`src/RimMandrake/SacredGraffiti/Defs/RitualOutcomeEffects.xml`) name a god inside an RM mod,
  which the tier grammar forbids. It moves into `mandrake.rut.rites` with the Dark Vigil, its one
  caller. The marks themselves (`SacredMarks.xml`) stay in SacredGraffiti.
- Any new Salvation `PreceptDef`/`RitualPatternDef`/`RitualOutcomeEffectDef` is authored here,
  never in `UtinniPatches` and never in a biome mod.
- The `.rid`'s own 23 rituals stay in the `.rid` (they are the owner's approved artifact); they are
  registered below so the liturgy is read in one place.

**What does not move.** Rites of **other** faiths stay with their faction: the Sun-Debt's Return
(`UtinniPatches`, the Deep Desert Tribes' ideoligion), the deep tribes' fire rite
(`PyrelandsMechanics`), the Holy Flame precept (any Ritualist ideo). They are in the register so
the gods' map is complete; they are not Salvation rites.
Ruled 2026-10-01 (decision taken by question card): a Salvation colony cannot learn other faiths' rites; they stay with their own faiths and factions.

**Correction carried in.** The concept doc said *"`MaxRituals = 6` per ideoligion"* and planned
slot-free variants to save slots. That was false: there is no engine cap
(`infrastructure/state/facts/salvation_ritual_precepts.json`, MEASURED 2026-09-03:
`PreceptDef.maxCount` is per-precept; The Salvation already carried 26). Slot-free variants stay,
because the owner ruled them (card 09:22, Q2), but no rite is cut to save a slot.

## (b) Register of every rite

Status: **BUILT** (defs in `src/`), **IN .RID** (in The Salvation, donor-mod worker), **SPECCED**
(a design doc gives the full shape), **PITCHED** (named in a biome sheet), **RULED OUT**.
Appeasement kinds, used throughout: **feeding** (raise a god's satiation), **settlement** (balance
a ledger), **starving** (deny a hungry god what feeds him), **venting** (bleed a dangerous meter
safely), **consolation** (lay grief down), **warding** (keep a god's attention away).

### B1. The liturgy tab (`mandrake.rut.rites`, BUILT as research projects, no ritual yet)

| Rite | God | Kind | Condition | Found | Status | Source |
|---|---|---|---|---|---|---|
| The Scrap Shrine | Rekko | feeding | none | given at start | BUILT (research) | `src/RimUtinni/Rites/Defs/RUT_Rites_Research.xml` |
| Conduit Choir | Ohm | feeding | power conduits | revealed by Antiquities LANGUAGE | BUILT (research) | same |
| God-Speaker Array | all nine | invitation | the array | revealed by RELIGION | BUILT (research) | same |
| Liturgy of the Hull | all nine | invitation | the ship walked | revealed by CULTURE | BUILT (research) | same |
| The Gods Speak Back | all nine | the Council of Voices | none | revealed by VOICE | BUILT (research) | same; `divine_satiation_engine.md` §5c |

### B2. The four found rites of the Abyss (§c; SPECCED here)

| Rite | God | Kind | Condition | Found | Status | Source |
|---|---|---|---|---|---|---|
| The Dark Vigil | Ishko | feeding (stillness offered) | absolute darkness | the Abyss, the inscription where no light has reached | SPECCED | this doc §c1 |
| The Blind Offering | Mob'Unloo | settlement | absolute darkness | the Abyss, the Nhaleth circle | SPECCED | §c2 |
| The Snuffing | Sh'kaar | starving | makes the dark | the Abyss, the ring of dead lamps | SPECCED | §c3 |
| The Lightless Burial | Ozzik | consolation (grief vented) | absolute darkness | the Abyss, the rescue ship in Lightfall | SPECCED | §c4 |
| The Unlit Wedding | Oomo, Ishko | variant (no new rite) | absolute darkness | unlocked by learning any darkness rite | SPECCED (variant) | §c5 |

### B3. The Salvation's rituals in the `.rid` (IN .RID, 23, XML-parsed 2026-10-01)

Campaign-named: Profitting Jubilee (`AM_ScrapRitual`), Scavenging Burial (`Funeral`), Wealthy
Records (`QuarterlyReport`), Scrounging Revel (`Festival`), Blade Dance of Redemption
(`LightsaberPracticeDuel`). Vanilla or donor, unrenamed: funeral (no corpse), child birth,
conversion ritual, public execution, leader speech, prisoner interrogation, role change, wedding
ceremony (RotR), three trials, five VFE Tribals tech-advance rituals, tribal gathering, trading
fair. **God, kind and condition: unmapped** for all 23. They predate the pantheon's rite model;
§5's pre-move per rite is owed when each is next reviewed (open, not filed). Throne speech, anima
tree linking and tree connection are **RULED OUT** (`design/Jawa/ideoligion_precept_removals.md`).

### B4. Rites the pantheon design names (SPECCED or PITCHED in design prose)

| Rite | God | Kind | Condition | Status | Source |
|---|---|---|---|---|---|
| The launch-rite, "The Reckoning" | Ta'Baa (offends Ishko) | feeding | a launch | SPECCED (prose) | `divine_satiation_engine.md` §2.0b ⑥, §5 |
| The machine-funeral | Ohm (offends Rekko if scrapped) | feeding | a machine's end | SPECCED (prose) | same, §5; `devotional_sacrifice_catalog.md` ⑤ The Mourning |
| The Seating (a relic into a hull socket) | Rekko, both scalars | feeding | a seated relic | SPECCED | `design/RimMandrake/ancient_machines_design.md` §5.2 |
| The Unburdening (potlatch) | Ozzik | venting | wealth destroyed | SPECCED | `salvation_engine_review.md` F13; catalog ⑨ |
| The controlled waking (its Leaning Scrub form is the Calling-Pyre: own field fired, herds and enemies present; Leaning Scrub, a charred stake ring) | Zizzik | settlement (the bank spent) | a chosen moment | SPECCED; Leaning Scrub form ruled-merged (card, 2026-10-01) | `salvation_engine_review.md` F11; `biome_rites_pass_2026-10-01.md` §7.1 |
| The Nine-Course Ninefold Feast | all nine | invitation | a feast | ruled-kept (owner 2026-10-02, typed: "Accept all rites for now.") | `design/Jawa/proposals/high_cuisine_deep_design.md` §5 |
| Triggered rites (landing, after battle, after trade, outpost, emancipation, a god's demand) | all nine | invitation, owed | the event | SPECCED (prose) | `divine_satiation_engine.md` §5b |

### B5. The devotions (acts the rite frames; SPECCED, `design/Jawa/devotional_sacrifice_catalog.md`)

Each is an act, not a ritual precept; several are "formalized as rite" in the catalog's words.
Zizzik (feeding, the bank): the Weathered Cell, the Open Latch, the Honored Break, Nine Faults
(the burnt offering, also row B8). Ishko (feeding): the Deep Berth, the Hour of Stillness, the Passed Cup. Ohm
(feeding): the Idle Made Whole, the Choir Hour, the Day of Current. Oomo (feeding): the Nursed
Stranger, the Open Table, the Overpaid Kin. Mob'Unloo (settlement): the Named Debt, the God's
Account, the Collected Grudge. Rekko (feeding, consolation): the Woken Sleeper, the Mourning, the
Second Skin. Ta'Baa (feeding): the Left Behind, the Rehearsal, the Far Walker. Sh'kaar (starving,
warding): the Kindled War, the Released, the Feast of the Unowned. Ozzik (venting): the
Unburdening, the Named Grief, the Dedication.

### B6. Biome-pitched rites (the principle's existing harvest)

| Rite | Faith / god | Kind | Biome | Status | Source |
|---|---|---|---|---|---|
| The Return (pour water toward the star) | Sun-Debt (Deep Desert Tribes), the sun | settlement | Stillsand | BUILT (XML) | `src/RimUtinni/UtinniPatches/Defs/PreceptDefs/RUT_TheReturn.xml` |
| The deep tribes' fire rite | deep tribes | feeding | Pyrelands | BUILT (C#) | `src/RimUtinni/PyrelandsMechanics/Source/LordJob_RUT_FireRite.cs` |
| Revering the Holy Flame | Sh'kaar (any Ritualist ideo) | warding | carved-stone flame | BUILT (precept) | `src/RimUtinni/UtinniPatches/Defs/PreceptDefs/RUT_HolyFlamePrecepts.xml` |
| The Rite of Tipping | unassigned | unknown | Wasteland | ruled-kept (owner 2026-10-02, typed: "Accept all rites for now.") | `design/Jawa/worldbuilding/biomes/warscar_bedazzle_review_2026-09-30.md` |
| The Watch (stand a night facing outward) | — | — | Warscar | RULED OUT (turn 3) | `design/Jawa/worldbuilding/biomes/warscar_turn3_development_2026-09-30.md` |
| The pilgrim camps (lore rungs, not a rite) | Rust Cathedral, "a god's deathbed" | — | Warscar | SPECCED (lore ladder caller) | same, §2.10 |
| The pool rites | Mob'Unloo (resolved as the Refused Toll, B15) | feeding | Weeping Stones | RULED as B15 (owner, 2026-10-02, typed) | `design/Jawa/worldbuilding/biomes/weeping_stones.md` §4; `weepingstones_bedazzle_review_2026-10-02.md` §6 R2, §8 |
| The rite of offering and forgetting | Deep Desert Tribes | settlement | sarlacc habitat | DRAFT | `design/Jawa/worldbuilding/sarlacc_native_habitat_draft.md` §3.1 |

### B7. Found rites of the other ten biomes (accepted 2026-10-02)

Pitched 2026-10-01 by `design/Jawa/biome_rites_pass_2026-10-01.md`, which has each rite's
condition, inscription site, outcomes and draft inscription. Every row accepted by the owner, 2026-10-02, typed: *"Accept all rites for now."*

| Rite | God | Kind | Condition | Found | Status | Source |
|---|---|---|---|---|---|---|
| The Sunning | Oomo | feeding | a Burn; red water in the open | Contagion, burn-shelter wall at a valley mouth | ruled-kept (owner 2026-10-02, typed: "Accept all rites for now.") | `biome_rites_pass_2026-10-01.md` §1.1 |
| The Unfinished Laid Down | Rekko | consolation | an undissolved Unfinished at the burn line | Contagion, a half-transformed tree at the front | ruled-kept (owner 2026-10-02, typed: "Accept all rites for now.") | `biome_rites_pass_2026-10-01.md` §1.2 |
| The Kept Mistake | Zizzik | warding | a broken thing left before a Bloom sortie | Contagion, the rim boulder among aerofleet husks | ruled-kept (owner 2026-10-02, typed: "Accept all rites for now.") | `biome_rites_pass_2026-10-01.md` §1.3 |
| The Storm's Receipt | Mob'Unloo | feeding | a fresh storm-exhumation site | Wasteland, a cargo plate the storm turned up | ruled-kept (owner 2026-10-02, typed: "Accept all rites for now.") | `biome_rites_pass_2026-10-01.md` §2.1 |
| The Salted Keeping | Ozzik | venting | a vitrified crater; the colony's finest thing buried | Wasteland, fused into a crater rim | ruled-kept (owner 2026-10-02, typed: "Accept all rites for now.") | `biome_rites_pass_2026-10-01.md` §2.2 |
| The Inherited Wreck | Rekko | settlement | a failed expedition's wreck in the hot ground | Wasteland, the dead crew's log panel | ruled-kept (owner 2026-10-02, typed: "Accept all rites for now.") | `biome_rites_pass_2026-10-01.md` §2.3 |
| The Returned | Ta'Baa | consolation | a body the ablation line gave up, sealed aboard | Blue Desert, a returned hull's hatch | ruled-kept | `biome_rites_pass_2026-10-01.md` §3.1 |
| The Charged Reed | Ishko | feeding | a charged reed cut from a ripe field's heart; no fire, ion or light carried | Blue Desert, a Rakatan Warning panel | ruled, reworked | `biome_rites_pass_2026-10-01.md` §3.2 |
| The Chime Vigil | Oomo | warding | the chime window, on a refuge ledge | Cracked Lands, chime-tenders' marks | ruled-kept (owner 2026-10-02, typed: "Accept all rites for now.") | `biome_rites_pass_2026-10-01.md` §4.1 |
| The Mud Claim | Rekko | feeding | the salvage-strike window after a recede | Cracked Lands, a flood-turned hull | ruled-kept (owner 2026-10-02, typed: "Accept all rites for now.") | `biome_rites_pass_2026-10-01.md` §4.2 |
| The Filtered Cup | Oomo | consolation | first water from a filter converter | Cauldron, a spent cartridge housing in a ruin | ruled-kept (owner 2026-10-02, typed: "Accept all rites for now.") | `biome_rites_pass_2026-10-01.md` §5.1 |
| The Engine Hour | Ohm | feeding | the ground loud, not a bloom's silence | Cauldron, a capped wellhead's housing | ruled-kept (owner 2026-10-02, typed: "Accept all rites for now.") | `biome_rites_pass_2026-10-01.md` §5.2 |
| The Capping | Zizzik | starving | an uncapped vent; no flame in radius | Cauldron, a blown capping collar | ruled-kept (owner 2026-10-02, typed: "Accept all rites for now.") | `biome_rites_pass_2026-10-01.md` §5.3 |
| The Anvil Gift | Sh'kaar | venting | a lava lake or crater; a weapon given | Forge, an obsidian slab on a crater lip | ruled-kept (owner 2026-10-02, typed: "Accept all rites for now.") | `biome_rites_pass_2026-10-01.md` §6.1 |
| The Flawed Masterwork | Ozzik | feeding | a masterwork made at a vent forge | Forge, a tender's tool rack in a foundry tower | ruled-kept, pending `FLAWED_MASTERWORK_ENGINE_CHECK_1` | `biome_rites_pass_2026-10-01.md` §6.2 |
| The Stall-Hold | Ishko | feeding | a Stall; everyone still in the open | Leaning Scrub, a sweetline tree's hide | ruled-kept (owner 2026-10-02, typed: "Accept all rites for now.") | `biome_rites_pass_2026-10-01.md` §7.2 |
| The Shade Tithe | Sh'kaar | warding | golden hour; a new roof raised; no Searing | Long Shade, under Shipfall Commons' oldest roof | ruled-kept (owner 2026-10-02, typed: "Accept all rites for now.") | `biome_rites_pass_2026-10-01.md` §8.1 |
| The Shadow Walk | Ta'Baa | feeding | a gloomcast crossing the map | Long Shade, a midden in a shadespire's lee | ruled-kept (owner 2026-10-02, typed: "Accept all rites for now.") | `biome_rites_pass_2026-10-01.md` §8.2 |
| The Last Track | Ohm | consolation | a crawler tread ending at a dead crawler | Stillsand, the dead crawler's dash | ruled-kept (owner 2026-10-02, typed: "Accept all rites for now.") | `biome_rites_pass_2026-10-01.md` §9.1 |
| The Unspilled March | Oomo | feeding | a mirage on the horizon | Stillsand, sealed jars on a glasscrust line | ruled-kept | `biome_rites_pass_2026-10-01.md` §9.2 |
| The Deserter's Welcome | Ohm | feeding | a hospice waking (day 7+) | Warscar, a campaign-tier old-tongue chassis plate | ruled-kept (owner 2026-10-02, typed: "Accept all rites for now.") | `biome_rites_pass_2026-10-01.md` §10.1 |
| The Vindication Walk | Ta'Baa | consolation | a Settling; ends when wind lifts the prints | Warscar, chalk inside a firing slit | ruled-kept (owner 2026-10-02, typed: "Accept all rites for now.") | `biome_rites_pass_2026-10-01.md` §10.2 |
| The Cold Ledger | Mob'Unloo | consolation | a frozen dead man's debt, a ledger tablet calved from the ice | Nightside Ice, a calved body carrying a tablet | ruled-kept (owner, 2026-10-01, question card) | `design/Jawa/worldbuilding/biomes/nightsideice_bedazzle_review_2026-10-01.md` §6 R1 |

### B8. Found rites of the Lantern Deeps (RULED)

| Rite | God | Kind | Condition | Found | Status | Source |
|---|---|---|---|---|---|---|
| Zizzik's Nine Faults | Zizzik (Rekko pays) | feeding, the bank (a favour transfer) | a newly found machine, never run, still on its map | Lantern Deeps, a dead droid with nine wires crossed | RULED (owner, 2026-10-01) | `design/Jawa/nine_faults_permanent_rite_2026-10-01.md` |
| The Answering | Ohm | settlement | a mindstone or Shard-mind in line of sight and a colony droid present; lit is fine | Lantern Deeps, a Working Dead chassis that scratches the cousins' terms into the gallery wall | RULED (owner, 2026-10-01, question card) | `design/Jawa/worldbuilding/biomes/lanterndeeps_bedazzle_review_2026-10-01.md` §6 R1 |

### B9. Found rites of the Pyrelands (RULED)

| Rite | God | Kind | Condition | Found | Status | Source |
|---|---|---|---|---|---|---|
| The Struck Glass | Zizzik | feeding, by breakage | a rough ring of lightning glass, stamped to pieces during any lightning storm; triggers a really powerful lightning blast at a random cell (the ship included) | Pyrelands, an old stamped ring on bare ash with a crater off across the plain | RULED (owner, 2026-10-01, revised by him, typed) | `design/Jawa/worldbuilding/biomes/pyrelands_bedazzle_review_2026-10-01.md` §6 R1 |

### B10. Found rites of the Webwork (RULED)

| Rite | God | Kind | Condition | Found | Status | Source |
|---|---|---|---|---|---|---|
| The Felled Noon | Sh'kaar | feeding | the tallest living tree felled by hand at the hour of highest sun; participants stand bare-headed in the hole it leaves; on the Webwork the owners gather at the shade line and wait | Webwork, a great kollavane stump carved with a sun-mark, ringed by bleached ollathrix legs | RULED (owner, 2026-10-02, question card); build `WEBWORK_FELLED_NOON_RITE_1` | `design/Jawa/worldbuilding/biomes/webwork_bedazzle_review_2026-10-02.md` §6 R1 |

### B11. Found rites ruled at the Greentide sitting (RULED)

Owner, typed 2026-10-02: *"Use first and third. First can be here. Build it outside the ship and let it be
taken.  Works better the better the room. The third works on another map that doesn’t have one for this god
yet. Likely one with open sight lines."* The Open Boast's home, decision taken by question card 2026-10-02
07:52 PDT: the Warscar.

| Rite | God | Kind | Condition | Found | Status | Source |
|---|---|---|---|---|---|---|
| The Ceded Room | Ozzik | venting | a finished room built outside the ship, above an impressiveness floor, ceded with everything in it: doors held open, cooling off, wild seed sown; nothing reclaimed for a season; works better the better the room | Greentide, a grown-through mud dome with a lintel scratched *we were proud of this* | RULED (owner, 2026-10-02, typed); build `GREENTIDE_CEDED_ROOM_RITE_1` | `design/Jawa/worldbuilding/biomes/greentide_bedazzle_review_2026-10-02.md` §6 R1 |
| The Open Boast | Ozzik | feeding | each participant declares an ambition and the congregation answers with the colony's name; days later a warned hostile challenge may arrive; once per colony | Warscar, a broken reviewing rostrum on a slag terrace with long sight lines, its rail gouged with names | RULED (owner, 2026-10-02, typed; home by question card); build `WARSCAR_OPEN_BOAST_RITE_1` | `design/Jawa/worldbuilding/biomes/greentide_bedazzle_review_2026-10-02.md` §5 idea 4 |

Ozzik carries five found rites (the Lightless Burial, B2; the Salted Keeping, B7, accepted; the
Flawed Masterwork, B7, ruled-kept; the Ceded Room and the Open Boast, B11): at the cap.

### B12. Found rites ruled at the Rust Cathedral sitting (RULED)

Owner, typed 2026-10-02: *"Mending Weld (Rekko): Repair a stretch of old structure here into a properly
formed room, restoring an old creation. Very sacred. 2nd ritual should be about droids: offer to repair one
of the free droids here as a sacred act. Option to capture it while it is being repaired (pleases trading
god, pleases Ohm, angers prideful god, angers neutral droids, angers Cathedral) or complete the repair and
release it (annoys trading god, pleases Ohm, pleases neutral droids, pleases Cathedral)."* Readings
(BENCH): trading god = Mob'Unloo, prideful god = Ozzik, neutral droids = the Free Droid Enclaves; the droid
rite is Ohm's and is named the Stranger's Overhaul.

| Rite | God | Kind | Condition | Found | Status | Source |
|---|---|---|---|---|---|---|
| The Mending Weld | Rekko | feeding (very sacred) | a broken stretch of old, non-colony structure rebuilt by hand, in its own material where it has one, into one enclosed, roofed room that keeps its original owner; scrapping it later is scrapping the mendable | Rust Cathedral, a conduit-wall gap mended in a foreign hand and roofed, its plate scratched *what was broken is whole* | RULED (owner, 2026-10-02, typed); build `RUSTCATHEDRAL_MENDING_WELD_RITE_1` | `design/Jawa/worldbuilding/biomes/rustcathedral_bedazzle_review_2026-10-02.md` §6 R1, §8 |
| The Stranger's Overhaul | Ohm (Mob'Unloo, Ozzik react) | feeding | a damaged droid that is not the colony's, repaired in the open; at half progress, capture it (Mob'Unloo and Ohm pleased; Ozzik, the Free Droid Enclaves and the Cathedral angered) or finish and release it (Mob'Unloo annoyed; Ohm, the Enclaves and the Cathedral pleased); on the borehulk it is the Worn Bit's last stage | Rust Cathedral, a droid chassis on its back by the enclaves' road, panel open, tools laid round it, scratched *fixed, not kept* | RULED (owner, 2026-10-02, typed); build `RUSTCATHEDRAL_STRANGERS_OVERHAUL_RITE_1` | `design/Jawa/worldbuilding/biomes/rustcathedral_bedazzle_review_2026-10-02.md` §8 |

Ohm carries five found rites (the Engine Hour, the Last Track, the Deserter's Welcome, B7, accepted; the
Answering, B8, ruled; the Stranger's Overhaul, B12): at the cap. Rekko's count is at B17 (five, at the cap).

### B13. Found rites ruled at the Rot sitting (RULED)

Decision taken by question card 2026-10-02 10:20 PDT: *the Unjoining, for the god of flight*. Ta'Baa is *"the
Unrooted — flight, the refusal to root"* (`divine_satiation_engine.md` ⑥).

| Rite | God | Kind | Condition | Found | Status | Source |
|---|---|---|---|---|---|---|
| The Unjoining | Ta'Baa | feeding | a colonist carrying a Rot symbiont is held by the participants through a hard purge until the symbiont dies (benefit gone for good); counts if the clan launches within days, sours if it stays the season; the first one teaches the Unjoining Draught | The Rot, a Wildsteam pilgrim path: an overturned empty brewing vessel, a rag stiff with dried Sheen, footprints that stop shining halfway | RULED (owner, 2026-10-02, question card); build `ROT_UNJOINING_RITE_1` | `design/Jawa/worldbuilding/biomes/rot_bedazzle_review_2026-10-02.md` §6 R2, §8 |

Ta'Baa carries four found rites (the Returned, B7, ruled-kept; the Shadow Walk and the Vindication Walk, B7,
accepted; the Unjoining, B13): one under the cap.

### B14. Found rites ruled at the Sump sitting (RULED)

Ruled 2026-10-02 (turn 2, owner typed the split into two rites; the Sinking's god by question card 06:24 PDT).
These two were ticketed without a register row; added here.

| Rite | God | Kind | Condition | Found | Status | Source |
|---|---|---|---|---|---|---|
| The Sinking | Ishko | warding | one valuable thrown into the tar: the next Imperial probe or raid is pushed 5x further away (Heat untouched), other raids lull on this map, other parties' ownership claims on almost anything the colony owns are erased; offering riders: the tar beast sleeps a season, the next three dug-up ancient traps fizzle | the Sump, a sunk tar ring with a tally board at a barrel yard | RULED (owner, 2026-10-02, typed + question card); build `SUMP_SINKING_RITE_BUILD_1` | `design/Jawa/worldbuilding/biomes/sump_bedazzle_review_2026-10-01.md` §6, §9 |
| Mob'Unloo's Price | Mob'Unloo | venting | one good thing plus one hated effigy into the tar: misfortune on someone else, paid by you; Empire effigy holds the Empire off 5x on this map (Heat untouched), faction effigy makes that faction's next group arrive tarred | the Sump, a ring of half-sunk effigies, one holding a carved stormtrooper helmet | RULED (owner, 2026-10-02, typed); build `SUMP_EFFIGY_RITE_BUILD_1` | same, §6, §9 |

### B15. Found rites ruled at the Weeping Stones sitting (RULED)

Owner, typed 2026-10-02: *"This is pretty cool (2). Gotta do it."* Option (2) was *the refused toll, for the god
of debt and trade* (Mob'Unloo). The Open Water (Oomo) was not chosen. (Oomo's count is in B16: he is at five.)

| Rite | God | Kind | Condition | Found | Status | Source |
|---|---|---|---|---|---|---|
| The Refused Toll | Mob'Unloo | feeding | water metered by someone who does not live on it (an Imperial metering station, a new campaign site): draw in the open, in sight of the meter, and walk away without paying; the toll-keeper answers, and a participant who strikes first at that water turns the truce's wild herds on the clan | Weeping Stones, an oasis outside an Imperial garrison: a water meter torn off its post, face-down in the pool's ring, dial jammed at zero, scratched *nothing owed* | RULED (owner, 2026-10-02, typed); build `WEEPINGSTONES_REFUSED_TOLL_RITE_1` | `design/Jawa/worldbuilding/biomes/weepingstones_bedazzle_review_2026-10-02.md` §6 R2, §8 |

Mob'Unloo carries five found rites (the Blind Offering, B2; the Storm's Receipt, B7, accepted; the Cold Ledger,
B7, ruled-kept; Mob'Unloo's Price, B14; the Refused Toll, B15): at the cap. B6's "pool rites" row resolves to this.

### B16. Found rites ruled at the Gelatinous Slime sitting (RULED)

Owner, typed 2026-10-02: *"Pomp's rite. The joining water. The uncomfortable truth that we are all connected not so
unlike the slime. Separate for now. Everyone briefly joins hands holding some slime. Can reduce permanent hediffs on
one person to weak hediffs on several instead."* None of the three pitched rites was chosen. **"Pomp" is Oomo** (decision taken by question card, 2026-10-02 14:44 PDT). Oomo is now at five, **the cap**. The rite's power (injuries spread) overrides the cohesion-only rule for this rite (decision taken by question card, 2026-10-02 14:44 PDT).

| Rite | God | Kind | Condition | Found | Status | Source |
|---|---|---|---|---|---|---|
| The Joining Water | Oomo | — (unruled) | everyone briefly joins hands, each holding some slime; one person's permanent hediffs are reduced to weak hediffs spread over several participants (the owner's explicit ask; a power, ruled an exception to the cohesion-only rule) | the Slime (site to draft at build) | RULED (owner, 2026-10-02, typed); build `GELATINOUSSLIME_JOINING_WATER_RITE_1` | `design/Jawa/worldbuilding/biomes/gelatinousslime_bedazzle_review_2026-10-02.md` §8 |

### B17. Found rites ruled at the Miasma sitting (RULED)

Decision taken by question card 2026-10-02 15:39 PDT: *the recall of the written-off, for the god of salvage* (GPT's pitch, review §5
idea 4). Rekko is *of the Second Hand*: salvage, repair, the discarded rewoken. The second-hand young (Rekko) and the mother's blind
side (Ishko) were not chosen.

| Rite | God | Kind | Condition | Found | Status | Source |
|---|---|---|---|---|---|---|
| The Recall of the Written-Off | Rekko | — (unruled) | a found disposal order, struck out in the rite, calls an old salvage operation whose machines strip loose metal and then the colony's powered buildings, the ship included, until driven off; a dramatic, risky world event | the Miasma, a river-mouth disposal depot: an inscription under condemnation stamps | RULED (owner, 2026-10-02, question card); build `MIASMA_RECALL_WRITTEN_OFF_RITE_1` | `design/Jawa/worldbuilding/biomes/miasma_bedazzle_review_2026-10-02.md` §5 idea 4, §8 |

Rekko carries five found rites (the Unfinished Laid Down, the Inherited Wreck, the Mud Claim, B7, accepted; the Mending Weld, B12;
the Recall of the Written-Off, B17): **at the cap**. (The Seating, B4, is a pantheon-design rite, not a found one, and is not counted,
as at every earlier count.)

### B18. Found rites of the Scald (PITCHED)

Sitting Q4 (b), 2026-10-02 (decision taken by question card): a bathing rite for the water pilgrims.

| Rite | God | Kind | Condition | Found | Status | Source |
|---|---|---|---|---|---|---|
| The Margin Bath | Ta'Baa (Oomo is at the cap) | consolation | three or more unarmored participants in the Scald's cool margin cove; arrivals by recent launch raise the outcome | the Scald, a pilgrim's bathing-stone at the cove edge | PITCHED (god choice owner's to rule); build waits on the margin cove and the found-rite machinery; item `SCALD_BATHING_RITE_1` | `design/Jawa/worldbuilding/biomes/the_scald_margin_bath_rite_2026-10-03.md` |

**Count (by hand from the tables above, not an instrument): 114 rows.** B1 5 + B2 5 + B3 23 +
B4 7 + B5 28 + B6 8 + B7 23 + B8 2 + B9 1 + B10 1 + B11 2 + B12 2 + B13 1 + B14 2 + B15 1 + B16 1 + B17 1 + B18 1. **105 are the Salvation's** (B1 to B5, B7 to B18;
the Unburdening appears in both B4 and B5, and Nine Faults in both B5 and B8, so 103 distinct). Sh'kaar
now carries four found rites (the Snuffing, the Anvil Gift, the Shade Tithe, the Felled Noon): one under the cap.

**Per-god cap: five found rites** (decision taken by question card 2026-10-02 09:23 PDT, raising it from
four when Ozzik reached five). Zizzik carries five, all kept (owner, 2026-10-01, typed: *"Just leave them all for
now"*): the controlled waking / Calling-Pyre (B4, ruled-merged), Nine Faults (B8, ruled), the Struck Glass
(B9, ruled), the Kept Mistake (B7, accepted), the Capping (B7, accepted). B6's 8 are other faiths' rites or unassigned biome pitches,
one ruled out. The calling-pyre is a form of B4's controlled waking, so it has no row of its own.

## (c) The four Abyss rites

Each answers R1: a different god, a different kind of appeasement, a different outcome. All four
need absolute darkness (the Snuffing makes it); all four are learned in the Abyss and held anywhere
dark afterwards (card 09:22, Q1). Every one follows §5: the rite pre-moves the gods by its nature,
then each god decides whether to speak. The darkness itself always pre-moves **Ishko up** and
**Sh'kaar down** (§2.0b ⑧, *"together the two make darkness doubly sacred"*); what differs is who the
rite is **for**.

**Shared teeth (ruled, card 09:22 Q3).** If the dark breaks mid-rite (a lamp, a door onto day, a
fire), the rite fails and Sh'kaar answers: *"Wrathful Sh'kaar draws something to a lit
night-rite"* (§5). A watcher re-reads the condition every 250 ticks and records the worst depth.
**UNMEASURED:** whether `LordJob_Ritual` exposes a per-tick hook or needs a Harmony postfix.

### c1. The Dark Vigil, for Ishko: feeding by stillness

- **Grounding:** stillness itself pleases him; he alone does not punish a skipped rite
  (§2.0b ①, §5b). The one rite held purely by choice.
- **Asks:** an organiser and at least three still spectators, about two in-game hours, no light
  carried. Quality from darkness depth, stillness, and Darkvision or dark-tolerant genes.
- **Outcome:** Poor, "a long cold sit". Fair, "kept the vigil" (shared memory). Good, Ishko's mark
  on the wall (`RM_Ishko_RitualOutcome_PlaceSacredMark`, built and waiting for this caller) and
  the darkness mood debuff waived for a season (hediff route UNMEASURED). Excellent, plus an art
  tale. Ninefold: a satiation gain for Ishko. Repeated Excellent vigils on one map count toward
  his Body-vision, *"terraform the dark itself into a home"*.

### c2. The Blind Offering, for Mob'Unloo: settlement

- **Grounding:** *"nothing is ever handed directly; a thing is set down and the other takes it
  up"* (§2.0b ④); his ledger is how debts are balanced, and the devotion "The Named Debt" names
  a debt before it is paid (catalog ④).
- **Asks:** the organiser names a debt (a theft from the clan, a ghost unlaid, a bargain gone sour)
  and lays an item on a ring in the dark; everyone leaves; nobody watches overnight.
- **Outcome:** by morning the offering is untouched (Poor: "it was not taken"; the debt stands),
  gone (Fair or Good: the named debt is settled, a ledger entry, not a mood buff), or gone and
  replaced by something small and strange from a curated list, never silver (Excellent). Nobody
  sees who took it. In the Abyss this is the Nhaleth exchange, never confirmed. Ninefold: a
  settlement entry for Mob'Unloo sized by the item's value.

### c3. The Snuffing, for Sh'kaar: starving the hungry god

- **Grounding:** Sh'kaar is fed by light cast into darkness and starved by *"staying dark, hidden,
  and unfought"* (§2.0b ⑧); his battle-escalation meter is cooled by stillness (§3⑧). The only
  appeasement a hungry god accepts is to be denied.
- **Asks:** a short rite at a lit spot. Each light within a radius is put out by a participant,
  one by one. It makes the condition the other three need, so it is a colony's way in.
- **Outcome:** Poor, the lights are relit within the hour. Fair, the room stays dark until relit.
  Good, Sh'kaar's escalation meter drops by a step (the clan has hidden from him; fewer and later
  brute attacks), and the next darkness rite there gains quality. Excellent, plus participants are
  steadier in the dark for a day. **The risk is sharpest here:** a Snuffing that fails to hold is
  the clan lighting a night-rite in front of the god it was hiding from.

### c4. The Lightless Burial, for Ozzik: consolation

- **Grounding:** beneath his arrogance Ozzik is grief, *"we were once great, and we cannot bear
  the memory"*; his satiation is a pride-meter that draws Sh'kaar and Zizzik (§2.0b ⑨). The
  Unburdening vents that meter by destroying wealth; this vents it by laying grief down, for
  *"the grave is the deepest dark"* (§2.0b ①).
- **Asks:** the funeral held in absolute darkness at a grave cut into rock, closed before any light
  returns. Once learned it is also the funeral's dark variant, using no new ritual (card 09:22 Q2).
- **Outcome:** the vanilla funeral outcome, plus: Poor, "buried in the dark" (neutral). Fair, the
  mourners' grief memories shorten. Good, Ozzik's pride-meter vents a step, lowering its upward
  bias on Sh'kaar's and Zizzik's rolls, without the Unburdening's cost in wealth. Excellent, plus
  the dead "went unseen" (Ishko's deepest facet), an art tale. Ishko is pleased as a side effect;
  the rite is aimed at Ozzik.

### c5. The Unlit Wedding (variant, not one of the four)

The wedding ceremony held in absolute darkness: the canon *"mate only in total darkness"*
(§2.0b ①) made pious. Vanilla outcomes, a darkness quality bonus, the memory "married in the
dark"; it pre-moves Oomo (the family grows) and Ishko. Unlocked by learning any darkness rite.

## (d) Discovering a rite in a biome

**Machinery that already exists, used whole:**

- **The Rites tab** (`mandrake.rut.rites`): each rite is a `ResearchProjectDef` and the tab's
  promise is *"revealed, not bought"*. Its tiers are gated by `hiddenPrerequisites` on Antiquities
  stages; that gate shows the row greyed until met (verified 2026-09-04 against
  `MainTabWindow_Research.cs`, recorded in the mod's About.xml).
- **`CompStudiable`** (core, MEASURED present in 1.6): a thing a pawn studies over time.
- **`ResearchProjectDef.researchMods`** (MEASURED: `List<ResearchMod>`, abstract `ResearchMod`
  with `Apply()`): runs code when a project completes.
- **`Ideo.AddPrecept(Precept, bool init, FactionDef, RitualPatternDef fillWith)`** (MEASURED,
  `Ideo.cs:1044`) with `PreceptMaker.MakePrecept(def)`: adds a ritual precept to a live ideo.
- **`GameComponent_LoreStage`** (`mandrake.rm.lorestages`, BUILT): `AdvanceStage(ladderId)`
  rewrites def descriptions stage by stage.

**Locked.** A found rite's `PreceptDef` and `RitualPatternDef` ship in `mandrake.rut.rites` but
are **not** in The Salvation. Its project sits in a new **"found rites"** row of the Rites tab,
grouped by biome, with `techprintCount 1` and `techprintCommonality 0`, so no bench, trader or
quest can supply it. The row is visible and greyed, its description a LoreStages placeholder
("A rite the dark keeps.").

**Found.** The biome places the rite's **inscription**: a `CompStudiable` thing at a site with a
reason to be there (the four Abyss sites in B2). A pawn studies it in place, under the rite's own
condition (in the dark; a lamp brought to read it spoils the study and is a lit night-rite, so
Sh'kaar may answer). Study completion yields the rite's techprint, the **rubbing**, and advances
the rite's LoreStages ladder so the project's description now says what was found and where.

**Learned.** Applying the rubbing unlocks a short contemplation project. On completion its
`ResearchMod` (`RUT_ResearchMod_GrantRite`) calls `AddPrecept` on the player's Salvation ideo with
the rite's pattern, and the rite appears in the ritual list, performable anywhere its condition
holds. This avoids hand-injecting a ritual into the frozen `.rid`, which is U10's untested shape
(`ancient_machines_design.md` §8). **UNMEASURED:** that `AddPrecept(init: true)` at runtime fills a
ritual's obligations and name correctly; read the method body in RimSage before building, and fall
back to the `.rid` route plus a "not yet learned" `BlockingIssues` comp if it does not.

**Surfaced.** A letter in the Narrator's register when the rubbing is taken ("The stone said what
to do. It did not say who carved it."), the Rites tab row lighting, and the ritual gizmo's own
reason line while the condition fails ("The spot is not dark: 34% light"). Nothing on screen
names a god's number (canon F8: Mood is weather).

**Settings** (Mod Settings, every mod ships them): on/off per found rite; darkness threshold
(default ground glow 0); strict participants (every participant's cell, default) or the spot only;
break tolerance; the slot-free variants on/off; "count the Abyss's Dark as absolute darkness"
(labelled: affects only Abyss maps).

## (f) The darkness gate (carried from the retired concept doc)

The one condition is **absolute darkness** (no second condition; *"There are no eclipses on this
planet"*, card 09:22). One small def, `RUT_RitualConditionDef`, names it and a worker answering
*does it hold?* and *how deeply (0..1)?* at a cell. It is read in three vanilla places, all
confirmed by RimSage against decompiled 1.6 (2026-10-01):

| Where | Vanilla hook (MEASURED) | What the gate does |
|---|---|---|
| Can it start? | `RitualOutcomeComp.BlockingIssues(...)`, `RitualObligationTargetFilter.GetBlockingIssues(...)`, `RitualBehaviorWorker.CanStartRitualNow(...)`, all virtual | `RUT_RitualOutcomeComp_Condition` returns a reason line while the spot is lit |
| How good is it? | `RitualOutcomeComp_QualitySingleOffset`; `RitualOutcomeComp_Indoors` is the template | a quality factor scaled by depth |
| Where can it be held? | `RitualObligationTargetFilter` subclasses, `CanUseTargetInternal(TargetInfo, RitualObligation)` | optional: only offer spots that can be dark at all |

Darkness reads `map.glowGrid.GroundGlowAt(IntVec3, ignoreCavePlants, ignoreSky)` (MEASURED), at the
spot and every participant's cell. On Abyss maps, once `ABYSS_DARK_BUILD_1` lands, any cell inside
the Dark also counts (soft dependency). XML: patterns, precepts, outcome effects, thoughts, tale
grammar. C#: the condition def and worker, the comp, the mid-rite watcher, `RUT_ResearchMod_GrantRite`,
a few outcome workers, settings.

**The gods' larger answers (campaign, carried).** A darkness rite held at the ship's shrine-heart
puts its lamps out first, so the Council of Voices (§5c) speaks out of the black; it needs the
RimAI/Cradle-Mind voice layer, as §5c says. In the Abyss, a Dark Vigil at the rare **wrong** ring
(review §11, mark 9 (c)) advances the lore ladder toward the Sith whisper, a voice that is not one
of the nine (a faint fall across the pantheon); it never resolves into a visitor. The Blind Offering
left in the Abyss is the Nhaleth exchange; the Nhaleth are never shown or confirmed.

## (e) The program principle, for every biome sitting

> **A biome is discovered for its rites as well as its tech.** Every biome sitting asks, beside
> mark 2 (discoverable technology): *what rite does this place teach the Salvation, which god does
> it appease, and in what way that no other rite already does?* The rite is found in the biome (an
> inscription at a site with a reason to be there), learned through the Rites tab's "found rites"
> row, and performable anywhere afterwards. Its home is `mandrake.rut.rites`; its god comes from
> §2.0b's real appetites, never invented; and its kind of appeasement is checked against this
> register so two biomes never teach the same rite twice.

Owner, R1: *"I am starting to love the idea that you don’t just discover tech in the biomes you
discover new rites."* A biome may answer "none"; the question must still be asked and recorded.

## Still open (not decided here)

- The Unveiling name collision: `design/Jawa/first_contact_chains.md`'s "nine unveilings" against
  the Abyss's rare lifting of the Dark, "the Unveiling". Neither renamed.

Ruled 2026-10-01: the Rites mod display name is "Salvation Rites"; other faiths' rites are not learnable by a Salvation colony (card); the Lightless Burial appeases Ozzik for now, to be renormalized by `SALVATION_RITES_RENORMALIZE_PASS_1`.
