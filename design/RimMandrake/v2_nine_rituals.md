# v2: the rituals of the Nine found in the Baroque Biomes

**Deferred to v2 by the owner, 2026-10-23, verbatim:**

> *"All "rituals" to interact with the Nine that are based on unique Baroque Biome content are hereby documented and
> deferred to v2. They are NOT part of the current deployment of Baroque Biomes. Please identify ALL Bench and Foundry
> queue item content specific to these Ritual discoveries and executions and move them into a single descriptive
> document (unless they are already well captured elsewhere) as v2 content. Do this as a subagent now. Any unique items
> or mechanics already added to the game should be removed at this time, including art."*

This file is the single v2 record. Each rite's full design already lives in its spec (the register and the biome
reviews, cited per row); this file says what each one was, how far it got, and how to bring it back. Nothing here is
scheduled. Work happened on 2026-10-23 (FOUNDRY helper).

## What counts, and what does not

**In scope (deferred):** a rite of the Salvation that pleases or appeases one of the Nine and that a Baroque biome
teaches through its own content: an inscription, a site, a creature or a material found only there. That is the
"found rite" programme of `design/Jawa/salvation_rites_2026-10-01.md` (sections B2 and B7 to B18, plus the discovery
machinery in its section (d)). It also covers how the rites are found: the inscriptions, the "found rites" row on the
Rites tab, `RUT_ResearchMod_GrantRite`, and the darkness gate the Abyss rites needed.

**Out of scope (left in v1 as they are):**
- The Nine's engine itself (`GameComponent_Ninefold`, the event patches, god favour tilts, first-contact letters) in
  `src/RimUtinni/Rites/`. These are reactions to ordinary play, not rituals built on biome content.
- The liturgy research tab (`RUT_Rites_Research.xml`: Scrap Shrine, Conduit Choir, God-Speaker Array, Liturgy of the
  Hull, The Gods Speak Back), the 23 rituals in The Salvation's `.rid`, the pantheon rites (register B4) and the
  devotions (B5). None of these is taught by a biome.
- Rites of other faiths: the Sun-Debt's Return at Stillsand (`RUT_TheReturn.xml`), the Deep Tribes' fire rite in the
  Pyrelands (`src/RimUtinni/PyrelandsMechanics`), Revering the Holy Flame. They belong to other factions' faiths, not
  to the Nine.
- The Rite of Tipping (Wasteland): a Junker waste-convoy contract quest with no god assigned (`RM_RiteOfTipping`).
- Ishko's three Odyssey landmarks (`RUT_IshkoLandmarks.xml`): world landmarks, not rituals.

## Removed from the game (built, now deleted)

All three were removed in **`9476b52d1`** ("Defer the Nine's biome rituals to v2"). To restore one, check its files out
of that commit's parent (`git checkout 9476b52d1^ -- <path>...`), re-add the csproj `Compile` lines and the settings
fields, rebuild with `winbuild.py`, and re-install the art through the art ledger (the pictures were **retired**, not
purged: the bytes are still in the art store under the shas below, so `art.py install <mod> <rel> <sha>` puts them back).
The per-rite file lists below are exactly what that commit deleted or edited.

| Rite | Biome | God (kind) | What it was | State at deferral | Removed |
|---|---|---|---|---|---|
| **The Struck Glass** | Pyrelands | Zizzik (feeding, by breakage) | A 3x3 ring filled with 25 glass sand; during any lightning storm (thunderstorm, dry thunderstorm, Cinderfall) the group stamps it out and one very powerful lightning blast (bomb, radius 7.9, fire) lands on a random cell, the ship included. Cohesion memories only. Owner, typed: *"Make a ~ring of the lightning glass, and then during any lightning storm step on them violently to break them. Triggers a REALLY powerful lightning blast somewhere randomly on the map (maybe even the ship) and utter delight within the god."* Input changed from fulgurite to glass sand by card 2026-10-15. Spec: `design/Jawa/worldbuilding/biomes/pyrelands_bedazzle_review_2026-10-01.md` §6 R1; register B9. | `PYRELANDS_STRUCK_GLASS_RITE_BUILD_1` validated to L1 (defs and ring placement PASS live 2026-10-21); the gizmo gate and a completed strike were never run (L2, L4 owed). No discovery wiring; precept not in the `.rid`. Placeholder art. | `src/RimMandrake/Pyrelands/Source/RM_StruckGlass.cs` (engine, `GenStep_StruckGlassRing`), `Defs/ThingDefs_Buildings/RM_StruckGlassRing.xml`, the `RM_StruckGlassRing` GenStepDef and its `extraGenSteps` row in `Pyrelands.xml`, four settings (`struckGlassEnabled`, `struckGlassBlastRadius`, `struckGlassMayHitBuildings`, `struckGlassRingOnNewMaps`) and their two settings groups, `struck_glass_live.py` and its two `diag/` captures, `src/RimUtinni/Rites/Defs/RUT_StruckGlass.xml` (precept, pattern, behaviour, outcome, two memories). Art: `Textures/Things/Building/Misc/RM_StruckGlassRing/RM_StruckGlassRing.png`, sha `77cd3a3c1fdf…`. |
| **The Answering** | Lantern Deeps | Ohm (settlement) | A colony droid stands in a Shard-mind's or mindstone's sight while the organiser speaks the clan's terms. Poor: the droid stalls and must be carried out. Fair: Ohm +6. Good: +8 and a log line it did not write. Excellent: +10 and the line names where the next mindstone vein lies (one is placed). Spec: `design/Jawa/worldbuilding/biomes/lanterndeeps_bedazzle_review_2026-10-01.md` §6 R1; register B8. | `LANTERNDEEPS_ANSWERING_RITE_BUILD_1` validated, BLOCKED since the owner's 2026-10-03 *"table the rites until the biome mod is fully complete and checked out"*. A1 recorded 2026-10-09; A2 (L2, per-tier outcomes) never run. Learning the rite never built. | `src/RimMandrake/LanternDeeps/Source/RM_Answering.cs`, `RM_AnsweringKernel.cs` and its fuzz block, `Defs/HediffDefs/RM_Answering.xml` (`RM_AnsweringStalled`, `RM_AnsweredLogLine`), three settings (`answeringRiteEnabled`, `answeringStallEnabled`, `answeringNextStoneEnabled`), `src/RimUtinni/Rites/Defs/RUT_Answering.xml`. No art of its own (vanilla icon). Kept: the Shard-minds, the Working Dead and `RUT_MindstoneVein`, which are biome content in their own right. |
| **The Joining Water** | Gelatinous Slime | Oomo ("Pomp", by card) | Everyone briefly joins hands round a ring of hand-prints in hardened slime, each holding slime; one participant's permanent conditions are reduced and spread as weak, passing ones (`RM_SharedBurden`) over the others. Owner, typed: *"Pomp's rite. The joining water. The uncomfortable truth that we are all connected not so unlike the slime. Separate for now. Everyone briefly joins hands holding some slime. Can reduce permanent hediffs on one person to weak hediffs on several instead."* Spec: `design/Jawa/worldbuilding/biomes/gelatinousslime_bedazzle_review_2026-10-02.md` §6, §8; register B16. | Built by `GELATINOUSSLIME_JOINING_WATER_STANDALONE_1` (done); live start with 3 participants and `RM_SharedBurden` carried after ~2000 ticks, 2026-10-09 (`GELATINOUSSLIME_JOININGWATER_RECHECK_1`). The parent item `GELATINOUSSLIME_JOINING_WATER_RITE_1` was still `proposed`. | `src/RimMandrake/GelatinousSlime/Source/JoiningWater.cs` (target and outcome workers, `GenStep_SlimeHandRing`), `Source/Kernel/RM_JoiningWaterKernel.cs` and its fuzz family, `Defs/GenStepDefs/RM_SlimeHandRing.xml`, `Defs/ThingDefs_Buildings/RM_SlimeHandRing.xml`, `Patches/RM_SlimeHandRing_MapGenPatch.xml`, `Defs/HediffDefs/RM_SharedBurden.xml`, the `joiningWaterEnabled` setting and its group, the `joining_water_wired` check in `validation.py` (and its mock and selftest plant), `src/RimUtinni/Rites/Defs/RUT_JoiningWater.xml`. Art: `Textures/Things/Building/RM_SlimeHandRing.png`, sha `60e45d761fbd…`. |

Everything that referred to them was edited in the same commit: the Mod Settings selftest (`selftest_settings_screens.py`),
the Pyrelands pre-flight defaults and review-map feature list (`preflight_pyrelands.py`, `human_review.py`,
`review/COVERAGE.md`), the modcheck manifest (`required_checks.json`, regenerated) and the Oomo's-shrine comment in
`RUT_OomoGrudgingShrine.xml`. The three DLLs touched were rebuilt with their `.srchash` (GelatinousSlime, LanternDeeps,
Pyrelands' FireEcologyHook; the Rites mod lost XML only). **Nothing was deployed**: the game folder still holds the old
copies until the next deploy of `mandrake.rm.biomes` and `mandrake.rut.rites`.

Not removed, on purpose: glass sand (`RM_GlassSand`) and the sand shovel (also the Stillsand glass chain), Cinderfall,
the Shard-minds, and one line of flavour on a Working Dead's inspect pane (*"the cousins' terms"*, `RM_WorkingDead.cs`)
which was the Answering's found inscription; it promises nothing and reads as lore.

A built review sheet still carries a row for the ring: `D:\ClaudeWork\scratch\art_regen_night\art_regen_night_sheet_2026-10-21.html`
(row `RM_StruckGlassRing`). The subject no longer exists; a ruling on that row changes nothing.

## Deferred before any code (design and queue only)

Each item below was retargeted to v2 on the ledger with the owner's words; its item prose stays where it is
(`infrastructure/state/items/<ID>.md`) and is the full spec.

| Item | Rite | Biome | God (kind) | Intent, one line | State at deferral | Spec |
|---|---|---|---|---|---|---|
| `SUMP_SINKING_RITE_BUILD_1` | The Sinking | the Sump | Ishko (warding) | One valuable into the tar: the next Imperial probe or raid pushed 5x away, raids lull, other parties' claims on the colony's things erased; riders: the tar beast sleeps, dug-up traps fizzle. | ready, BLOCKED by the 2026-10-03 tabling. The claim-wipe API it needs exists (`RimProperty` `ClaimWipe.cs`, kept: content-blind). | item prose; `design/Jawa/worldbuilding/biomes/sump_bedazzle_review_2026-10-01.md` §6, §9; register B14 |
| `SUMP_EFFIGY_RITE_BUILD_1` | Mob'Unloo's Price | the Sump | Mob'Unloo (venting) | One good thing plus a hated effigy into the tar: an Empire effigy holds the Empire off 5x on this map, a faction effigy tars that faction's next group. | proposed | item prose; same review §6, §9; B14 |
| `WEBWORK_FELLED_NOON_RITE_1` | The Felled Noon | the Webwork | Sh'kaar (feeding) | Fell the tallest living tree by hand at highest sun; participants stand bare-headed in the hole; the owners gather at the shade line. | proposed | item prose; `webwork_bedazzle_review_2026-10-02.md` §6 R1; B10 |
| `GREENTIDE_CEDED_ROOM_RITE_1` | The Ceded Room | Greentide | Ozzik (venting) | Cede a finished room built outside the ship to the jungle with everything in it; the better the room, the better the reward. | proposed | item prose; `greentide_bedazzle_review_2026-10-02.md` §6 R1, §8; B11 |
| `WARSCAR_OPEN_BOAST_RITE_1` | The Open Boast | the Warscar | Ozzik (feeding) | Each participant declares an ambition and the congregation answers with the colony's name; days later a warned challenge raid may come; once per colony. | proposed | item prose; `greentide_bedazzle_review_2026-10-02.md` §5 idea 4, §8; B11 |
| `RUSTCATHEDRAL_MENDING_WELD_RITE_1` | The Mending Weld | Rust Cathedral | Rekko (feeding, very sacred) | Rebuild a broken stretch of old, non-colony structure in its own material into one whole roofed room that keeps its original owner. | proposed | item prose; `rustcathedral_bedazzle_review_2026-10-02.md` §6 R1, §8; B12 |
| `RUSTCATHEDRAL_STRANGERS_OVERHAUL_RITE_1` | The Stranger's Overhaul | Rust Cathedral | Ohm (Mob'Unloo and Ozzik react) | Repair a free droid in the open as a sacred act; at half progress capture it or finish and release it, each branch moving gods and factions differently. | proposed | item prose; same review §8; B12 |
| `ROT_UNJOINING_RITE_1` | The Unjoining | the Rot | Ta'Baa (feeding) | A symbiont-carrying colonist is held through a hard purge until the symbiont dies, just before the clan leaves; counts if the clan launches within days. | proposed, BLOCKED (no found-rite machinery). The Unjoining Draught it was to teach is built separately and stays in v1 (ordinary research, `RM_UnjoiningDraught.xml`, `ROT_UNJOINING_DRAUGHT_1` done). | item prose; `rot_bedazzle_review_2026-10-02.md` §6 R2, §8; B13 |
| `WEEPINGSTONES_REFUSED_TOLL_RITE_1` | The Refused Toll | Weeping Stones | Mob'Unloo (feeding) | Draw water in the open at an Imperial metering station and walk away unpaid; the toll-keeper answers; striking first turns the truce's herds on the clan. | ready, BLOCKED (needs a new quest-site map type). | item prose; `weepingstones_bedazzle_review_2026-10-02.md` §6 R2, §8; B15 |
| `GELATINOUSSLIME_JOINING_WATER_RITE_1` | The Joining Water | Gelatinous Slime | Oomo | The parent item of the built rite above. | proposed (its build was the removed code above) | item prose; B16 |
| `MIASMA_RECALL_WRITTEN_OFF_RITE_1` | The Recall of the Written-Off | the Miasma | Rekko | A found disposal order, struck out in the rite, calls an old salvage operation that strips loose metal, then the colony's powered buildings, until driven off. | proposed | item prose; `miasma_bedazzle_review_2026-10-02.md` §5 idea 4, §8; B17 |
| `SCALD_BATHING_RITE_1` | The Margin Bath | the Scald | Ta'Baa (consolation; god pitched, owner's to rule) | Three or more unarmoured participants bathe in the Scald's cool margin cove; arrivals by recent launch raise the outcome. | doing (design only; waited on the margin cove). | `design/Jawa/worldbuilding/biomes/the_scald_margin_bath_rite_2026-10-03.md`; B18 |
| `SALVATION_RITES_UNIFICATION_1` | the found-rite machinery | all | all | A biome teaches a rite through an inscription (`CompStudiable`) that yields a techprint rubbing; a "found rites" row on the Rites tab; `RUT_ResearchMod_GrantRite` adds the precept to The Salvation at runtime; the darkness gate for the Abyss rites. Owner R1, 2026-10-01: *"I am starting to love the idea that you don't just discover tech in the biomes you discover new rites."* | proposed, BLOCKED by the 2026-10-03 tabling; nothing built. | item prose; register §(d), §(f), §(e) |

**Deferred with no queue item of its own**, each fully specced in the register and the biome rites pass (nothing built):
the four Abyss rites and the Unlit Wedding variant (register B2, §(c): the Dark Vigil for Ishko, the Blind Offering for
Mob'Unloo, the Snuffing for Sh'kaar, the Lightless Burial for Ozzik), and the 23 found rites of register B7 (Contagion:
the Sunning, the Unfinished Laid Down, the Kept Mistake; Wasteland: the Storm's Receipt, the Salted Keeping, the
Inherited Wreck; Blue Desert: the Returned, the Charged Reed; Cracked Lands: the Chime Vigil, the Mud Claim; Cauldron:
the Filtered Cup, the Engine Hour, the Capping; the Forge: the Anvil Gift, the Flawed Masterwork; Leaning Scrub: the
Stall-Hold; Long Shade: the Shade Tithe, the Shadow Walk; Stillsand: the Last Track, the Unspilled March; Warscar: the
Deserter's Welcome, the Vindication Walk; Nightside Ice: the Cold Ledger). Specs: `design/Jawa/salvation_rites_2026-10-01.md`
§(b), §(c); `design/Jawa/biome_rites_pass_2026-10-01.md` §1 to §10;
`design/Jawa/worldbuilding/biomes/nightsideice_bedazzle_review_2026-10-01.md` §6 R1. The per-god cap of five and the
renormalising pass (`SALVATION_RITES_RENORMALIZE_PASS_1`) apply to these when v2 opens.

## Partly-ritual items: trimmed, kept in v1

- `RUSTCATHEDRAL_WORN_BIT_ARC_1` (the Worn Bit): stage 4 and its keep-or-free fork were written as the Stranger's
  Overhaul performed on the borehulk. The item now says stage 4 is a plain restoration job with the same parts and the
  same fork, and that the god deltas rode on the rite and go with it to v2. Owner's own words for the arc name no rite.
- `BEDAZZLE_TOP_SHAPE_PROGRAM_1`: track (d), the rites pass over the eleven finished biomes, and the "biomes teach rites"
  half of its principle are struck as v2 here.
- `SALVATION_RITES_RENORMALIZE_PASS_1`: narrowed to the rites that stay in v1 (register B1, B3, B4, B5); the found rites
  are renormalised when v2 opens.
- `BIOME_MECHANICS_JUDGE_FLUFF_ON_TRIAL` and its inventory `design/RimMandrake/special_mechanics_review_2026-10-22.md`:
  every found-rite row is now ruled (v2); the review's other rows are untouched.
- `GREENTIDE_BASE_PORT_BUILD_1`: its "Blocks" line no longer names the Ceded Room.

## Ambiguous: kept in v1, and why

| Thing | Why it might count | Why it stays |
|---|---|---|
| **Nine Faults** and the Left Behind (`NINEFOLD_FAVOUR_ODDS_BUILD_1`; `RUT_NineFaults.xml`, `NineFaults.cs`, `Offerings.cs`) | Register B8 lists Nine Faults as a found rite of the Lantern Deeps (a dead droid with nine wires crossed). | Its condition is generic (any machine just taken on any map, never run), its discovery wiring was never built, and it is a Ninefold offering mechanic, not biome content. Built and validated. If the owner reads it as a Lantern Deeps rite, it moves here. |
| **The calling-pyre** (Leaning Scrub; `RM_CallingPyre.cs`, `Defs/Ideology/RM_CallingPyre.xml`) | Register B4 merges it with Zizzik's "controlled waking" as its Leaning Scrub form. | Ruled by card N3 (*"Only fire- and ritual-themed ones"*): it is an ordinary Ideology precept for fire and ritualist memes, names no god, and is not a found rite. |
| **Oomo's grudging shrine** (Cauldron; `RUT_OomoGrudgingShrine.xml`) | A shrine to one of the Nine placed by the Cauldron's ruin kit. | It is a meditation focus, not a ritual; built and validated with the ruins. Its unbuilt "sour water-rite tint" rode the Joining Water and is now noted as v2. |
| **Ishko's sacred-mark outcome** (`RM_Ishko_RitualOutcome_PlaceSacredMark`, SacredGraffiti) | The register names the Dark Vigil (an Abyss rite) as its caller. | It is a general outcome mechanism for any ritual and has no caller today; no biome content. |
| **RimProperty claim wipe** (`ClaimWipe.cs`, `PROPERTY_CLAIM_ERASE_API_1`) | Built for the Sinking. | A content-blind API; nothing ritual in it. |

## North-star text to revise by the owner

None found. Every `## north star` section under `design/validation_walks/` was scanned for rites, rituals, the Struck
Glass, the Joining Water, the Answering, offerings and the Nine: no bar names a deferred rite. The Scarlands walk's
agent-written "must be true" line on the Open Boast was corrected.
