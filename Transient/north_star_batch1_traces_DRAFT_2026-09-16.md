# North star DRAFT — batch 1, "traces of what happened here"

⚠️ **DRAFT. BINDS NOTHING.** Per `design/RimMandrake/north_star_validation_spec.md`
§3, a DRAFT checklist **cannot fail a mod and cannot green one**. Nothing here is
a bar, nothing here is a ruling, and no line becomes real until the owner
accepts or edits it. Written 2026-09-16 on the **Mac laptop**: no game, no
bridge, no RimSage. Every claim below traces to a file on disk or is marked
UNMEASURED.

**Authored per §8**: candidates derived from (a) the owner's own recorded words,
(b) the walk's `## must be true`, (c) the mod's real defs and sprites, (d) its
About.xml. Never from imagination. Each line is tagged with where it came from:

| tag | meaning | weight |
|---|---|---|
| 🗣 | derived from the owner's verbatim recorded words | strongest |
| 📐 | derived from a def, a sprite measured/looked at, or the mod's own source | strong |
| 📄 | derived from About.xml or the walk's own `## must be true` | medium |
| 🤔 | **my inference.** No evidence behind it beyond reasoning | weakest — cut freely |

**Batch order** is §8's rule (visual surface area first), not the file list's:
Graffiti → SacredGraffiti → WreckedMachines → Antiquities → Inhabited →
AshkarrInhabited → AftermathRites → Aftermath → SalvageClaim.

🔴 **Two mods in this batch point defs at vanilla placeholder art** — the pit
defect's exact signature. Named in full under Antiquities and Inhabited.

---

## 0. Aftermath — the dismissed walk, re-examined first

`design/validation_walks/RimMandrake/Aftermath.md` ends with:

> *"No [S] line: this is a pure narrative/incident-timing system with no bespoke art."*

### Verdict: the CLAIM is half true; the REASONING is the pit's reasoning, and it hides a real defect.

Taking the sentence apart, both halves measured this pass:

- **"no bespoke art" — TRUE.** `src/RimMandrake/Aftermath/` holds 27 files, **zero
  PNGs**, and exactly one XML: `About/About.xml`. There is no art to look at.
  The walk's anti-guessing note is correct on this point.
- **"pure narrative/incident-timing system" therefore nothing to look at — FALSE.**
  This mod has one player-facing output and it is a **screen** artifact, not a
  state change. `AftermathRuleRunner.SendTelegraph` calls
  `Find.LetterStack.ReceiveLetter(label, text, LetterDefOf.ThreatBig, null, targetFaction)`
  — `src/RimMandrake/Aftermath/Source/AftermathRuleRunner.cs:337`. The mod's own
  design shape is *"trigger -> delay -> **telegraph** -> payload"*
  (`RM_AftermathRuleDef.cs:8`). The telegraph is the ONLY thing the player ever
  perceives as this mod; the payload is a vanilla `RaidEnemy` that looks like a
  vanilla raid.

So this is the pit's sentence with the nouns swapped. The pit walk said the
mechanics were the whole point and script-checkable; this walk says the system is
narrative and unarted. Both are true statements that do not answer the question
asked — *does the player see something this mod is responsible for?* Here he does:
he reads a letter this mod wrote.

### And the re-examination found a defect offline

🔴 **`letterLabel` and `letterText` are declared and never read.** They are
declared at `RM_AftermathRuleDef.cs:56-57` ("the *ships a templated letter
baseline per rule* requirement"). A grep of the entire `Aftermath/Source` tree
for `letterLabel|letterText|ReceiveLetter|LetterDefOf` returns **only** those two
declarations and the single telegraph call at line 337. Nothing sends the payload
letter. All 8 rules in `AftermathRites` author a `letterLabel`/`letterText` pair
— *"They came back"*, *"Junkers, arriving second"*, *"The debt comes due"* — and
**none of it ever reaches the screen.** Authored experience, present in data,
absent from the game. That is the north star's exact defect class, found from
disk with no game running.

📐 **Every telegraph arrives identically.** `LetterDefOf.ThreatBig` is hardcoded
at line 337; `RM_AftermathRuleDef` carries no letterDef field. So *"A chartreuse
flicker runs through the ship's old lights"* (rule 6, a `ShortCircuit` omen) and
*"A lone scout was seen at the edge of your land"* (rule 1, a returning warband)
arrive as the same big-red-threat card.

### Honest caveat the owner must rule on

A letter is a boundary case for §1's *"answerable yes/no by LOOKING at one
screenshot"*. The letter icon sits in the stack in any play-zoom screenshot; the
letter **body text** needs the letter open, which is a click. I have not
pretended otherwise. Whether Aftermath's lines are admissible at all is his call,
not mine — and it is a general question, since several mods in this repo speak to
the player mainly through letters.

### what this mod is FOR visually
A raid you were warned about, in words that belong to the world — not a raid that
merely happens.

### must show — candidates

**The telegraph**
- [ ] `aftermath_telegraph_precedes_payload` 📄 — a telegraph letter is on screen
      *before* the aftermath raid lands, so the raid reads as foretold rather
      than as ordinary storyteller noise.
- [ ] `aftermath_telegraph_is_authored_prose` 📐 — the telegraph reads as the
      rule's own written text, never the engine's fallback string. (The fallback
      is literally `"{0} is stirring."`, `AftermathRuleRunner.cs:336`.)
- [ ] `aftermath_telegraph_presentation_fits_rule` 📐 — an electrical omen and a
      returning warband do not arrive with identical letter presentation.
      Currently they must: `LetterDefOf.ThreatBig` is hardcoded.

**The payload**
- [ ] `aftermath_payload_letter_reaches_screen` 📐 — when the queued payload
      fires, what the player reads is the rule's own `letterLabel`/`letterText`,
      not vanilla's generic raid letter. 🔴 **Cannot pass today** — the fields
      are never read. This line is the falsification test for this mod.

### cannot show
- [ ] `never_unnamed_stirring` 📐 — the string *"… is stirring."* on screen. It is
      the engine admitting no rule authored a telegraph, and it is the closest
      thing this mod has to a tile with "Pit" written on it.

### why these
Four lines, one cannot-show, all letter-surface. **The walk's dismissal should be
narrowed, not deleted**: "no bespoke art" stands and is worth keeping; "nothing
visual" does not. The mod is genuinely close to the legitimate answer §8 allows —
but it is not there, because it writes prose to the player and half that prose is
unreachable.

---

## 1. Graffiti (`mandrake.rm.graffiti`)

### what this mod is FOR visually
Walls that have been written on by somebody — a mark that reads at a glance as a
deliberate human act, not as dirt.

### the owner's own words — 3 verbatim quotes found

2026-08-30, filing `GRAFFITI_MOD_EXPANSION_1`:
> *"Add a queue item to assess the graffiti mod and expand it to include sacred
> graffiti, socially infuriating graffiti or amusing graffiti, or even beautiful
> graffiti. (we are subscribed)"*

2026-08-31, `GRAFFITI_FRAMEWORK_BUILD_1`:
> *"Fully flesh out the graffiti mod now for tremendous application in the Jawa
> game. Jawas love graffiti. All the various kinds. Go for it!"*

2026-09-09, `GRAFFITI_PUNK_IDEOLIGION_SCOPE_1`:
> *"we want the base Graffiti mod to have a wide variety of functionality within
> it, not just the base examples we've provided in vanilla. It should be a mod
> more aligned to punk style graffiti such as is seen in urban settlements, as
> well as ideoligion-inspired sigils taken from the Rimworld ideoligions as they
> exist in the game. Then we will go rich and fill in the Utinni modpack for it."*

🔑 Through-line: **variety, and marks that read as punk/urban graffiti.** "All the
various kinds" is a visual demand, not a mechanical one.

### what the art actually is (MEASURED and LOOKED AT, 2026-09-16)

12 PNGs, all 640×640, across 4 concrete marks:

| def | variants | ink coverage | motif bbox in 640² | Beauty |
|---|---|---|---|---|
| `RM_Graffiti_Vandal` (donor art) | **6** | 2.1–3.5% | ~9..625 × 25..630 — **whole tile** | −15 |
| `RM_Graffiti_Scratches` | **2** | 2.8–3.0% | 247..393 × 177..464 | −8 |
| `RM_Graffiti_TallyMarks` | **2** | 2.2–3.1% | 174..468 × 274..367 | −3 |
| `RM_Graffiti_WarningGlyph` | **2** | 4.9–5.6% | 172..467 × 176..464 | −6 |

Looking at them side by side:

- 🔴 **`RM_Graffiti_Vandal` contains real-world English lettering, including the
  donor author's own tag.** `vandal_0.png` is a scatter of a dozen small
  spray-doodles across the full canvas, several of them legible English words —
  **"TARTE'S"** is readable top-left. (Graffiti Mod (Continued) is by
  Tarte/emipa606, `Mlie.GraffitiMod`; the art was copied byte-for-byte under MIT
  per this mod's About.xml.) English signatures on a Star Wars desert world.
  `GRAFFITI_PUNK_IDEOLIGION_SCOPE_1` already lists "English lettering in art (F5)"
  as **out of scope** — but the shipped default mark has it.
- 🔴 **The default mark is the least legible of the four.** Vandal spreads a dozen
  tiny doodles over the whole tile; at play zoom each is a few pixels of coloured
  mush. The three new marks are one large centred motif and read cleanly. So the
  mod's *only* spontaneously-spawned mark is the one that does not read — and it
  is the one the walk's `[S]` line asks about.
- 📐 **`RM_Graffiti_WarningGlyph` is a modern ISO road-hazard triangle** with an
  exclamation mark in it. Contemporary Earth signage, not a punk scrawl.
- 📐 `RM_Graffiti_TallyMarks` and `RM_Graffiti_Scratches` both read clearly and
  carry no franchise or real-world vocabulary. These two are the batch's best art.
- 📐 **Variant counts are lopsided 6 : 2 : 2 : 2.** `Graphic_Random` over two
  variants repeats visibly the moment a spree places more than a couple of marks.

📐 **A mark appearing at all is not a given.** `RM_BaseGraffiti`'s own def comment
records that a colonist spent an entire mental-break spree — *"~20000 ticks,
dozens of TryMakeFilth calls every 250 ticks"* — painting at a wall and **never
once produced a mark**, because `placementMask` was `Any`. Fixed 2026-09-06. This
belongs in the checklist precisely because it passed every state assertion at the
time.

📐 Mod Settings (`RM_GraffitiMod.cs`): `paintingEnabled`, `viewerReactionEnabled`,
`breachBiasEnabled`, plus a paint-interval value.

### must show — candidates

**A mark on a wall**
- [ ] `mark_actually_appears` 📐 — after a paint job or spree completes, a mark is
      visibly on the wall. Not an empty wall with a clean job log.
- [ ] `mark_reads_as_deliberate` 🗣📐 — a mark reads at play zoom as something a
      hand made on purpose, not as scattered dirt or a smudge. (His *"punk style
      graffiti such as is seen in urban settlements"*; the measured failure case
      is Vandal's tile-wide doodle scatter.)
- [ ] `mark_scale_consistent` 📐 — all marks read at comparable scale on a wall;
      one is not a full-tile scatter while the next is a small centred motif.
- [ ] `mark_sits_on_the_wall` 📐 — a mark reads as being *on* the wall face, aligned
      to it, not as a decal floating over the floor beside it.

**Variety — his "all the various kinds"**
- [ ] `marks_visibly_various` 🗣 — several marks in one colony are visibly
      different kinds of mark, not recolours of one.
- [ ] `mark_variants_do_not_repeat` 📐 — a wall carrying several marks of the same
      def does not show the same variant twice adjacent. (2 variants per new mark
      makes this the hard case.)

**Register — punk/urban, and this world**
- [ ] `mark_register_is_punk_urban` 🗣 — the mark set reads as urban/punk
      graffiti, not as clip-art icons or modern signage.
- [ ] `mark_carries_no_earth_signage` 📐 — no mark reads as a contemporary
      real-world sign (road hazard triangle, exit sign, traffic glyph).

**Beauty legibility**
- [ ] `mark_ugliness_is_visible` 📐 — a Beauty −15 vandal scrawl looks worse than
      a Beauty −3 tally at a glance. The stat and the picture agree.

### cannot show
- [ ] `never_real_world_english` 📐 — legible real-world English words or a
      third-party author's tag in a mark. 🔴 **`RM_Graffiti_Vandal` shows this
      today**; "TARTE'S" is readable in `vandal_0.png`.
- [ ] `never_reads_as_dirt` 🗣 — a mark indistinguishable from vanilla filth at
      play zoom. If graffiti reads as a mess rather than a message, the mod is
      doing nothing his three quotes asked for.

### why these
Three verbatim quotes carry six of the nine lines. The two cannot-shows and
`mark_scale_consistent` come from looking at the sprites, which is where the
English lettering and the scale split surfaced — neither is written down
anywhere in the repo. **Recommend he sits with this one first**: it has the most
of his own voice behind it and the sharpest measured defect.

---

## 2. SacredGraffiti (`mandrake.rm.sacredgraffiti`)

### what this mod is FOR visually
A devotional mark — the one graffiti in the game that a colonist would be glad to
see on his wall.

### evidence

Owner's ruling on placement, recorded in `GRAFFITI_MOD_EXPANSION_1` and restated
verbatim in the def's own header:
> *"a sacred mark is placed as a RITUAL OUTCOME — a reward off a Salvation Matrix
> boon — not a Harmony patch on GraffitiMod's own spawn loop and not
> hand-placement."*

Canon iconography, `design/Jawa/divine_satiation_engine.md` pantheon section,
quoted in About.xml and in `GRAFFITI_MOD_EXPANSION_1`:
> *"a pair of glowing orange eyes in the dark."*

📐 **LOOKED AT `SacredMark_Ishko.png`** (640×640): a pair of yellow-orange
slit-pupil eyes set inside a loud spiky orange-and-yellow radial burst. Ink
coverage **15.77%** — roughly 5× the density of every vandal mark in the batch,
and the brightest asset in it. bbox 64..576 × 175..465, a wide horizontal band.

- The eyes ARE there and ARE canon-correct. Good.
- But the canon line says *"in the dark"* and this is the brightest thing in the
  batch. At play zoom the burst may win and the eyes may be lost inside it.
- 📐 `Beauty 6`, `Cleanliness -2` — positive Beauty, deliberately unlike every
  vandal mark. The "beautiful graffiti" direction he asked for on 2026-08-30 is
  a *visible* claim, not just a stat.
- 📐 One of nine gods shipped. `GRAFFITI_MOD_EXPANSION_1` tables the other eight
  with their canon Form lines; none is arted.

### must show — candidates
- [ ] `sacredmark_eyes_dominate` 📐 — the mark reads first as a pair of watching
      eyes. The surrounding strokes frame them; they do not out-shout them.
- [ ] `sacredmark_reads_devotional` 🗣📐 — the mark reads as a devotional mark
      painted on a wall, not as a sun, an explosion, or a hazard burst.
- [ ] `sacredmark_beauty_is_visible` 🗣 — a Beauty +6 sacred mark visibly looks
      better than a Beauty −15 vandal scrawl beside it. His *"or even beautiful
      graffiti"* is a look, not a number.
- [ ] `sacredmark_is_pigment_on_wall` 📐 — the mark reads as ochre/rust pigment
      daubed by a hand (its own description), not as an emissive glowing object.
- [ ] `sacredmark_gods_distinguishable` 🤔 — when more gods ship, two sacred marks
      are told apart at a glance without a tooltip. **My inference, and premature**
      — only Ishko exists. Include only if he wants the line waiting.

### cannot show
- [ ] `never_reads_as_light_source` 🤔 — a sacred mark that reads as a lamp or a
      glowing prop rather than as paint. My inference from the measured brightness,
      not from anything he said.

### why these
Two strong external sources (his placement ruling; the canon Form line, which is
design prose he owns rather than a quote from him). The rest is measured off the
one shipped sprite. **Cheap sitting — 4 real lines and 1 mod, worth 5 minutes.**

---

## 3. WreckedMachines (`mandrake.rm.wreckedmachines`)

### what this mod is FOR visually
A dead machine still bolted to the deck, and the visible difference between dead,
bodged and brought back.

### the owner's own words — 2 verbatim quotes found

2026-09-01, filing `WRECKED_MACHINES_RESURRECTION_1`:
> *"And then there's the speck for the Wrecked Machines mod... let's ressurect
> that now! Fix it. Make it work in the new regime."*

2026-09-15, filing `RAKATAN_ARCHOTECH_MACHINES_1` — the vision quote:
> *"It becomes a core Rakatan tech trait: it's ROBUST. It SURVIVES. It degrades
> gracefully whenever possible. Their ships are ancient and still somewhat
> functional. Their batteries just slowly lose capacity over millenia yet still
> work. And if we could refurbish them, they would exceed modern technology even
> in a still kludged manner. The existing mod is about repairing big machines in
> place, and that's excellent. […] Defunct, weakly functional, or semi-functional
> versions will be found in the game and added to the ship by the player as a
> form of sacred loot."*

📄 And this mod's **About.xml is already written as vision prose** — the closest
thing in the batch to a ready-made `### the experience`:
> *"Holy wreckage. The Kolyska's factory did not fail politely. Its machines are
> still bolted to the deck where they died — split open, scavenged, corroded,
> half-buried in their own slag. […] WRECKED — Dead. Deformed, scavenged, missing
> chunks, corroded. Occupies its tiles, does nothing, cannot be removed. Scenery
> and reproach. […] REPAIRED — holes filled with metal that does not match,
> cabling routed almost neatly, a few improvised vents still smoking. Full
> function. **It will never look factory-fresh again.**"*

### what the art actually is (MEASURED and LOOKED AT)

12 PNGs, own art throughout — **no vanilla placeholder anywhere in this mod.**
3 tiers × 4 facings, `Graphic_Multi`, `size (3,4)` / `drawSize (4,5)` matching
the donor. `Beauty` −30 / −20 / −10.

Tier-to-tier pixel difference (south and east facings): **42–47% of pixels differ
by >24, RGB RMS 22–28.** These are genuinely three different pictures, not
recolours.

Looked at, south facings side by side — **the tiers read**:
- **WRECKED** — holes punched clean through the housing, dull grey, no lights lit.
- **KLUDGED** — bodged copper piping and mismatched plate grafted on, warmer, the
  light ring still dark.
- **REPAIRED** — the orange ring of lights **lit**, the single clearest
  "it works now" tell in the batch.

🔴 **Two measured gaps:**
1. **No Mod Settings at all.** No `ModSettings` / `DoSettingsWindowContents`
   anywhere in `src/RimMandrake/WreckedMachines/`. Against
   `MOD_OPTIONS_RETROFIT_1` ("every mod we ship carries a real settings screen").
   Not a visual line, but it will block a GREEN and he should know now.
2. **The donor's untouched smelter stays buildable alongside ours** — About.xml's
   own words: *"both appear in the build menu. That is deliberate […] It is a
   testing arrangement, not a finished one."* A visible defect the mod has already
   confessed to.

### must show — candidates

**The three tiers, told apart**
- [ ] `tiers_distinguishable_at_glance` 📄 — wrecked, kludged and repaired are
      told apart at play zoom with no tooltip and no click.
- [ ] `wrecked_reads_as_dead` 📄🗣 — a WRECKED machine reads as dead: split open,
      missing chunks, nothing lit. *"Scenery and reproach."*
- [ ] `repaired_reads_as_running` 📐 — a REPAIRED machine reads as running. (The
      lit orange ring is the tell the art already has.)
- [ ] `kludged_reads_as_bodged` 📄 — a KLUDGED machine reads as bodged, not as
      finished: mismatched plate and exposed cabling visible on the sprite.
- [ ] `repaired_never_factory_fresh` 📄 — even REPAIRED still shows scars. Its own
      About: *"It will never look factory-fresh again."*
- [ ] `wrecked_degraded_not_absent` 🗣 — a wreck reads as a machine that **survived**
      in a degraded state, not as rubble or an empty footprint. His *"it's ROBUST.
      It SURVIVES. It degrades gracefully."*

**Placement in the world**
- [ ] `wreck_occupies_its_tiles` 📄 — a wreck fills its own 3×4 footprint and reads
      as bolted in place, not as a small prop sitting in a large empty rectangle.
- [ ] `wreck_reads_as_worth_saving` 🗣 — a wreck reads as something a scavenger
      would want, not as trash to clear. His *"sacred loot"* / *"Holy wreckage."*

### cannot show
- [ ] `never_two_identical_smelters` 📄 — ours and the donor's smelter side by side
      in the build menu or on the map, indistinguishable. 🔴 **True today by
      design**, and About.xml calls it unfinished.
- [ ] `never_reads_as_donor_machine` 📐 — a tier that reads as the donor's own
      intact VFE smelter rather than as our wreck.

### why these
Two verbatim owner quotes, one of them a full vision paragraph, plus an About.xml
that reads like a north star already. This is the **best-evidenced mod in the
batch** and the one where the shipped art most nearly earns its lines. **Strongly
recommend he sits with it** — his 2026-09-15 Rakatan quote is fresh and reshapes
what the mod is for.

---

## 4. Antiquities (`mandrake.rut.antiquities`)

### what this mod is FOR visually
An ancient object you carry to a cradle and turn under the light — three
different kinds of relic, and a station that reads as a scanning cradle.

### 🔴 THE PIT DEFECT, WORST INSTANCE IN THE BATCH

**MEASURED**: `src/RimUtinni/Antiquities/` ships **zero PNGs**. Five defs, and
every one of them points at the same **vanilla** texture:

| def | texPath | note |
|---|---|---|
| `RUT_AntiquityBase` (abstract) | `Things/Item/Special/AIPersonaCore` | ⇒ inherited by all 3 items |
| `RUT_Antiquity_Urn` | (inherited) | `MarketValue 140`, `Mass 3` |
| `RUT_Antiquity_Stele` | (inherited) | `MarketValue 220`, `Mass 12` |
| `RUT_Antiquity_Gravegood` | (inherited) | `MarketValue 180`, `Mass 1.5` |
| `RUT_AntiquityReadingStation` | `Things/Item/Special/AIPersonaCore` | `size (1,1)`, `drawSize (1,1)`, `rotatable`, `hasInteractionCell` |
| `RUT_AntiquityCipherBench` | `Things/Item/Special/AIPersonaCore` | `selectable false`, never spawns |

Consequences, read straight off the defs:

1. **An urn, a stele and a grave-good are visually the same object.** Three
   mechanically distinct relics — a glazed vessel, a carved boundary-stone, a
   personal burial item — all render as vanilla's AI persona core. The walk's whole
   flavour premise ("rarer than an urn and heavier with geography") is invisible.
2. **The reading station is a BUILDING drawn with an ITEM icon.** `size (1,1)`,
   `drawSize (1,1)`, its own description promising *"a scanning cradle for turning
   a piece slowly under glyph-light"*. A pawn standing at it to read for 60000
   ticks is structurally the pit's *"pawn standing on a labelled tile"* — the
   mechanism runs, the picture says nothing.
3. This is **honest, flagged placeholder** — the def's header says `🖼 PLACEHOLDER
   ART` and names slice 8 as the real art work. That is the difference between this
   and the pit (which flagged it too, and shipped anyway). The north star's point
   is that a flagged placeholder still cannot green a mod, and this is the mod
   where that rule earns its keep.

📐 Mod Settings (`AntiquitiesMod.cs`): `readingEnabled`, `keyTextBonusEnabled`.

### the owner's words: none about appearance

Three `ownerSaid` entries on `ANTIQUITIES_TREE_BUILD_1` — *"Ok, take these ideas
and do a major design pass to improve this. Flesh it out. […] Be innovative."*
(2026-09-04), *"Do not build yet, simply ingest these concepts everywhere they
belong."*, and *"yes"* (the unblock). All process, **no visual direction.** So
every line below is def-derived. He may want to write `### the experience` for
this one from scratch rather than react.

### must show — candidates
- [ ] `antiquity_kinds_distinguishable` 📐 — urn, stele and grave-good are told
      apart on the ground at play zoom with no tooltip. 🔴 **Impossible today**:
      one texture for all three.
- [ ] `antiquity_reads_as_ancient` 📐 — a relic reads as an old excavated object,
      not as high-tech hardware. 🔴 **The current placeholder is an archotech AI
      core** — the most advanced-looking item in vanilla.
- [ ] `readingstation_reads_as_station` 📐 — the reading station reads as a piece
      of furniture a pawn works at, not as a dropped item lying on the floor.
- [ ] `readingstation_own_art` 📐 — the station has art of its own, at its own
      texture path, not a vanilla texPath. This is the pit's `pit_not_vanilla_trap`
      line transposed.
- [ ] `readingstation_reading_is_visible` 🤔 — a pawn reading at the station is
      visibly *reading at it* — at the interaction cell, engaged with the object.
      **My inference**, from the walk's 60000-tick Wait toil.
- [ ] `catalogued_state_visible` 🤔 — a catalogued relic is distinguishable from an
      uncatalogued one without selecting it. **My inference.** The walk proves this
      via `jawa/inspect_string`, i.e. text, which is exactly the kind of proof the
      north star exists to distrust. He may reasonably rule this out of scope for
      v1.
- [ ] `cipherbench_never_seen` 📄 — `RUT_AntiquityCipherBench` never appears
      anywhere visible. Its own label is *"UNUSED — antiquity cipher bench (never
      spawns)"* and its description says *"If you ever see this in the architect
      menu, something is wrong."* Rare case of a def asking for its own must-show.

### cannot show
- [ ] `never_reads_as_ai_persona_core` 📐 — an antiquity or the station rendering
      as vanilla's AI persona core. 🔴 **This is the shipped state of all five
      defs**, and it is this batch's exact analogue of a pawn standing in a box
      labelled Pit.

### why these
No owner voice at all; everything from the defs. But the def evidence is the
strongest in the batch — the placeholder is unambiguous and self-documented.
**Recommend: skip the sitting, act on the finding.** He does not need to rule that
five defs sharing a vanilla AI-core texture is wrong. What he needs is slice 8
scheduled.

---

## 5. Inhabited (`mandrake.rm.inhabited`)

### what this mod is FOR visually
A place on the world map that looks like the *kind* of place it is, and that reads
on the ground as somewhere people actually live.

### 🔴 PIT DEFECT, SECOND INSTANCE — vanilla world-map art, shared

**MEASURED**: `src/RimMandrake/Inhabited/` ships **zero PNGs**, and both world
object defs carry the same vanilla texture:

- `Inhabited_Place` — `<texture>World/WorldObjects/TribalSettlement</texture>`
- `Inhabited_Settlement` — `<texture>World/WorldObjects/TribalSettlement</texture>`

There are four place archetypes (`Places_Inhabited.xml`): `RM_InhabitedPlace_Scrapyard`
("scrapyard seat"), `_Palace` ("palace seat"), `_MachineHold` ("machine hold"),
`_WaterHold` ("water hold"). **All four, and both object types, draw as vanilla's
tribal-settlement hut icon on the world map.** A Hutt palace, a droid charging
hold, a Deepwater cistern and a Junker scrapyard are indistinguishable at world
zoom.

The irony is written into the mod's own About.xml:
> *"RimWorld's world map is a set of props: a settlement is a name and a loot
> table, a visitor is a timer."*

### the owner's words

No verbatim quote about how a place should LOOK. What exists:
- 2026-09-01, `SETTLEMENT_VISIT_LOOP_1`: *"Superb! Work it out until we can see
  all the real work and decisions we need. […] This is amazing! (two mods)"* —
  enthusiasm, no visual direction.
- 2026-08-22, `HUTT_LORDS_AND_POSTS_1`: *"The Hutt settlements that are on oasis
  should all be named (Hutt Lord's name)'s Palace."* — naming, adjacent to the
  visual, and honoured: `Inhabited_Manifest_GorgaPalace` reads *"Gorga the
  Immense's Palace"*.
- 2026-08-24: *"Shelve anything about Inhabited for right now."* 2026-09-05: *"You
  take the FOUNDRY's Inhabited item now. Fully work it to completion."*

### what About.xml promises the player will SEE
> *"NPCs do not farm — three shipped walls make it impossible — so a place's
> sustenance is present rather than produced: a mess, a paste vat, a granary, a
> herd. **It is visible, stealable and destroyable**, and burning it makes the cast
> leave"*

### measured gaps against that promise

- 🔴 **Only the first district is built.** `GenStep_ComposeSettlementDistrict.cs:14`
  and `:113-116` — *"only `districts[0]` is composed"*. The Claim Jump authors
  four districts (scrapyard, dwelling cluster, cantina block, depot); a visiting
  player sees the scrapyard and bare ground.
- 🔴 **Sustenance is a heap, not a store.** `GenStep_InhabitedStock.cs`'s own
  docstring: *"WHERE THE GOODS GO, AND WHY IT IS NOT A GRANARY YET […] the anchor
  is derived rather than authored […] preferring a roofed standable cell."* Goods
  drop as a loose pile in whatever roofed cell was found. About.xml promised *"a
  mess, a paste vat, a granary."*
- 📐 **16 district templates** exist in `Templates/*.txt` (junkers 4, droid 4,
  deepwater 4, hutt 4). The walk says *"eleven"* — stale; MEASURED 16. All four
  campaign first-districts have a template (`junkers_scrapyard`,
  `deepwater_cistern_hall`, `hutt_palace_hall`, `droid_charging_hall`).
- 📐 Mod Settings (`RM_InhabitedMod.cs`): `fateEnabled`, `beggarsFromPoolEnabled`.

### must show — candidates

**On the world map**
- [ ] `place_icon_is_its_own` 📐 — an inhabited place draws its own world icon, not
      a vanilla settlement texture. 🔴 Fails today.
- [ ] `place_archetypes_distinguishable` 📐 — a palace, a machine hold, a water
      hold and a scrapyard are told apart at world zoom. 🔴 Fails today: one
      texture for all four.

**On the ground**
- [ ] `district_reads_as_authored` 📄 — a visited settlement's district reads as a
      built place with rooms, not as scattered props on bare terrain.
- [ ] `settlement_beyond_first_district` 📐 — the ground around the composed
      district does not read as an abandoned empty plain. 🔴 Only `districts[0]`
      exists; this line names the seam honestly rather than hiding it.
- [ ] `district_faction_legible` 🤔 — a Junker scrapyard and a Hutt palace hall
      read as belonging to different peoples on sight. **My inference**, though the
      16 templates are already authored per faction.
- [ ] `sustenance_reads_as_a_store` 📄 — the place's food and goods read as a
      larder/granary/paste vat somebody keeps, not as loose loot dropped on a
      floor. 🔴 Fails today by the GenStep's own admission.
- [ ] `cast_reads_as_inhabitants` 📄🤔 — the pawns on the map read as people who
      live there — placed in their districts, doing something — not as a huddle of
      idle spawns. From About's *"a persistent cast of real pawns who live there"*;
      the "reads as" phrasing is mine.

### cannot show
- [ ] `never_vanilla_tribal_icon` 📐 — an inhabited place drawn as vanilla's
      tribal-settlement hut. 🔴 **The shipped state of both world object defs.**
- [ ] `never_empty_settlement` 🤔 — a named settlement the player walks into and
      finds effectively empty. **My inference** — but it is the failure mode the
      districts[0] limit plus a heap-of-goods anchor most plausibly produces.

### why these
No owner visual voice; two hard def findings (vanilla shared world icon;
districts[0]) and two source-documented shortfalls against About.xml's own
promises. **Recommend he sits with this one** — not to rule the defects (they are
plain) but because "what does an inhabited place look like" has never been
written down by him, and the answer decides art work for four archetypes.

---

## 6. AshkarrInhabited (`mandrake.rut.inhabited`)

### what this mod is FOR visually
Nothing of its own — but it is the DATA that decides what four named Ash'karr
settlements look like on the ground.

### the honest position

Data-only: 4 `SettlementManifestDef` + 4 `SecurityProfileDef`, zero PNGs, zero
C#, no Mod Settings, no `validation.py`. Its walk says the visual pass is a human
matter (`[S]` step 12: *"walk each of the four settlements in-game and confirm
district shapes/adjacency and cast NPC placement read correctly against the
manifest's authored intent"*) — **that is correct and is not a dismissal.** The
walk is right; it just has no checklist.

But the mod is not visually inert, because of the districts[0] rule. 📐 **Each
manifest's FIRST district label is literally the only thing a visiting player
sees built.** So:

| settlement | districts[0] | template exists? | the other authored districts, unbuilt |
|---|---|---|---|
| The Claim Jump | scrapyard | ✅ `junkers_scrapyard` | dwelling cluster, cantina block, depot |
| Deepwater Hold | cistern hall | ✅ `deepwater_cistern_hall` | (per manifest) |
| Gorga the Immense's Palace | palace hall | ✅ `hutt_palace_hall` | cistern court, holding pens, spicehouse |
| The Cracking Yard | charging hall | ✅ `droid_charging_hall` | (per manifest) |

🗣 The palace name honours his 2026-08-22 ruling verbatim — *"The Hutt settlements
that are on oasis should all be named (Hutt Lord's name)'s Palace"* — and the def
reads `Gorga the Immense's Palace`. That is the one line here with his voice
behind it.

📐 **Stale walk, flag only** (I did not edit it): the walk's steps 6–9 name
`factionDefName=Jawa_Junkers` / `Jawa_HuttCartel` etc., but the defs read
`RUT_Jawa_Junkers` / `RUT_Jawa_HuttCartel` — post-`NAMING_SCHEME` prefixes. The
walk's `[D]` read-backs would fail on the written value.

### must show — candidates
- [ ] `settlement_first_district_matches_name` 📐 — the district a player walks
      into matches what the settlement is called. Gorga the Immense's Palace opens
      onto a palace hall; The Claim Jump onto a scrapyard.
- [ ] `settlement_reads_as_its_faction` 📐 — the four settlements are visibly four
      different peoples' places, not one template redressed.
- [ ] `palace_reads_as_a_palace` 🗣 — a Hutt lord's palace reads as a seat of
      power, not as a shed. (His naming ruling implies the place should carry the
      name.)
- [ ] `gate_posture_visible` 🤔 — a searching gate (Deepwater `searchChance 1`,
      Hutt `0.6`) looks different from a waving-through one (Junkers `0`). **My
      inference**, and probably premature — nothing renders posture today.

### cannot show
- [ ] `never_four_identical_settlements` 📐 — the four named settlements
      indistinguishable from one another on the ground.

### why these
Its lines are really *Inhabited's* lines instantiated on four named places, which
is what a data-only content mod should be. 3 real lines + 1 premature.
**Recommend: fold into Inhabited's sitting**, don't spend a separate one.

---

## 7. AftermathRites (`mandrake.rut.aftermath`)

### what this mod is FOR visually
Every word the aftermath system ever says to the player. It is defs-only and it
is entirely made of on-screen prose.

### its walk also dismissed the visual pass — and is also wrong

> *"X. [S] none — pure data defs, nothing to look at visually"*

📐 This mod ships **16 authored messages the player is meant to read** — 8 rules ×
2 messages each: a `telegraphLabel`/`telegraphText` pair and a
`letterLabel`/`letterText` pair per rule. That is not "nothing to look at"; it is
the whole visible surface of the aftermath feature, and it lives here rather than
in the engine. Same failure shape as `Aftermath.md` and the pit: "no art" was
allowed to mean "nothing visual".

🔴 **And half of it is unreachable.** Per §0 above: `letterLabel`/`letterText` are
declared on `RM_AftermathRuleDef` and read **nowhere** in the engine. So these
eight are authored and dead:
> *"They came back"* · *"An ally answers"* · *"Junkers, arriving second"* ·
> *"They come for their own"* · *"The sun's regard"* · *"Zizzik's spark"* ·
> *"Someone talked"* · *"The debt comes due"*

📐 **And three of eight rules cannot fire at all.** Rules 5, 7, 8
(`GodBandCrossed`, `RootedClockQuadrum`, `TakingEventWitnessed`) carry full
telegraph and letter prose against trigger kinds the runner does not evaluate —
the file's own header says so. So 3 of 8 telegraphs are unreachable *too*.
(MEASURED from the def file and
the engine grep; the file's header is corroborating, not the source.) Counting: 8
telegraph messages, of which 5 have a wired trigger kind; 8 payload letters, none
of which the engine reads. **5 of 16 messages reachable.**

📐 The prose itself is strong and world-specific: *"A lone scout was seen at the
edge of your land, studying your defenses before slipping away."* · *"Desert
scavengers circle the field where the bodies still lie unburied."* · *"A
chartreuse flicker runs through the ship's old lights, three quick pulses, gone
before anyone else sees it."* None of it is generic. That is exactly why its being
unreachable matters.

### the owner's words: none on this mod
`PLOT_MECHANISM_MODS_WAVE_1`'s only `ownerSaid` is *"Summarize and rule please."*
The 8 rules trace to `design/Jawa/proposals/plot_mechanisms_wave.md` §2.1, not to
a quote.

### must show — candidates
- [ ] `telegraph_text_is_in_world` 📐 — a telegraph reads as something observed on
      Ash'karr (a scout at the treeline, scavengers circling, a flicker in the
      ship's lights), never as a rules notification.
- [ ] `telegraph_names_no_mechanism` 📐 — no telegraph shows a defName, a trigger
      kind, a god enum, or a number. All eight currently pass this by inspection;
      the line exists so a future rule cannot regress it.
- [ ] `every_shipped_rule_can_be_read` 📐 — every rule that ships prose can
      actually put it on screen. 🔴 **Fails 11 of 16 messages today** (8 dead
      payload letters + 3 unwired trigger kinds).
- [ ] `payload_letter_is_the_rules_own` 📐 — when the payload lands the player
      reads this rule's letter, not vanilla's generic raid text. Pairs with
      Aftermath's `aftermath_payload_letter_reaches_screen`; the same id should not
      be claimed twice — the engine owns the mechanism, this mod owns the words.

### cannot show
- [ ] `never_generic_raid_letter_for_an_authored_rule` 📐 — an aftermath raid
      arriving with vanilla's stock raid letter while this mod ships a written one
      for it. 🔴 **The shipped behaviour.**

### why these
No owner voice, but the strongest single measured finding in the batch: **11 of
16 authored player-facing messages are unreachable.** A defs-only mod turned out to
be the batch's clearest case of absent experience. **Recommend: skip the sitting,
file the engine fix.** He does not need to rule that authored letters should reach
the screen.

---

## 8. SalvageClaim (`mandrake.rm.salvageclaim`) — the mod does not exist

🔴 **The walk's `subject:` path is gone.** `src/RimMandrake/SalvageClaim` does not
exist. The code lives at `src/RimMandrake/RimProperty/Source/SalvageClaim/`
(`SalvageClaimFeeUtility.cs`, `FloatMenuOptionProvider_PaySalvageClaim.cs`) inside
**`mandrake.rm.property`** — consolidated per `MOD_CONSOLIDATION_PLAN.md`. There
is no `mandrake.rm.salvageclaim` shipped mod, no `About.xml` for it, no defs.

### the honest answer: no visual lines, and the walk's own reason is right

The mod's entire surface is one float-menu string:
`"Pay salvage claim fee (" + fee + " silver) on " + clickedThing.LabelShort`. A
float menu **is a click**, which §1 excludes by construction. Its walk says
*"[S] none beyond the float-menu text itself, already covered by step 4"* — and
that is correct, unlike the two dismissals above, because the surface really is a
click-gated text string that a state assertion already reads verbatim.

This is §8's legitimate answer: *"A mod that is pure arithmetic goes last and may
honestly need no visual lines."* A fee formula and a menu label is that.

### must show — candidates
**None.** If the owner wants coverage, the right unit is a `## north star` on
`Property.md` with a line about the claim UI, since Property is the shipped mod.

### why these
Two findings, no lines: the walk names a mod that no longer exists as a unit, and
the surface is genuinely below the visual floor. **Recommend: skip, and re-point
the walk at Property under the naming/consolidation item.**

---

## Summary

| mod | candidate `must show` | `cannot show` | strongest evidence | verbatim owner quotes | vanilla placeholder art? | recommend |
|---|---|---|---|---|---|---|
| **Graffiti** | 9 | 2 | 🗣 3 verbatim quotes + looked-at sprites | **3** | no (donor art, but English lettering) | **SIT — first** |
| **WreckedMachines** | 8 | 2 | 🗣 2 quotes incl. a vision paragraph + About.xml prose | **2** | no — own art, all 3 tiers | **SIT — second** |
| **Inhabited** | 7 | 2 | 📐 shared vanilla world icon; districts[0] | 0 on appearance | 🔴 **YES** — `World/WorldObjects/TribalSettlement`, both defs | **SIT** |
| **SacredGraffiti** | 5 (1 premature) | 1 | 🗣 placement ruling + canon Form line | 0 direct (ruling paraphrased) | no | **SIT — cheap** |
| **AshkarrInhabited** | 4 (1 premature) | 1 | 📐 districts[0] × 4 manifests; 🗣 palace naming | **1** (naming) | n/a — data only | fold into Inhabited |
| **Antiquities** | 7 (2 inferred) | 1 | 📐 5 defs on one vanilla texture | 0 on appearance | 🔴 **YES** — `Things/Item/Special/AIPersonaCore`, all 5 defs | **SKIP — act** |
| **AftermathRites** | 4 | 1 | 📐 11 of 16 authored messages unreachable | 0 | n/a — data only | **SKIP — fix** |
| **Aftermath** | 4 | 1 | 📐 `letterLabel`/`letterText` never read | 0 | n/a — zero PNGs | **SKIP — fix** |
| **SalvageClaim** | **0** | 0 | 📐 mod folder does not exist | 0 | n/a | **SKIP — re-point walk** |
| **totals** | **48** | **11** | | **6** | **2 mods** | 4 sit · 4 skip · 1 fold |

### The two vanilla-placeholder mods, named plainly
1. **Antiquities** — `RUT_AntiquityBase` (→ urn, stele, grave-good),
   `RUT_AntiquityReadingStation`, `RUT_AntiquityCipherBench`: **all five** on
   `Things/Item/Special/AIPersonaCore`. Zero own PNGs.
2. **Inhabited** — `Inhabited_Place` and `Inhabited_Settlement`: **both** on
   `World/WorldObjects/TribalSettlement`, covering all four place archetypes.
   Zero own PNGs.

Both are flagged in their own source. Both are the pit's signature: a def pointing
at vanilla art while every state assertion passes.

### The three dismissed/near-dismissed walks in this batch
- `Aftermath.md` — *"pure narrative/incident-timing system with no bespoke art"*.
  **Half right.** "No bespoke art" is measured true; "nothing visual" is false —
  the mod writes letters, and one whole letter channel is dead.
- `AftermathRites.md` — *"none — pure data defs, nothing to look at visually"*.
  **Wrong.** 16 authored player-facing messages live there; 5 are reachable.
- `SalvageClaim.md` — *"none beyond the float-menu text itself"*. **Right**, and
  the only genuine §8 "no visual lines" answer in the batch.

### What I could not measure from the Mac
- **Any engine internal.** RimSage has never connected here. Specifically
  UNMEASURED: whether `LetterDefOf.ThreatBig` auto-opens or pauses (so whether a
  telegraph's body text is on screen without a click); how `linkType CornerFiller`
  composites a `Graphic_Random` filth over a wall; how a `size (1,1)`
  `drawSize (1,1)` building with an item texture is actually blitted.
- **Anything requiring the game.** No line above tells anyone to launch RimWorld;
  every one is a statement about a screenshot, judgeable when one exists.
- **Whether the defs on disk match the deployed Mods folder.** Not checked — this
  is the laptop; `ModsConfig.xml` and the Steam Mods tree are on the Desktop.
- **Play-zoom legibility itself.** I looked at sprites at source resolution
  (640²) and at 320², not at the ~64px a tile occupies in play. Every "reads at
  play zoom" line is a candidate *question*, not a measured verdict.

### One thing worth his attention beyond this batch
🗣 2026-09-15, filing `EVENT_TRACE_PROPS_LIBRARY_1`, he asked for:
> *"a new props library that's all about blaster marks, burn marks, scorch marks,
> floor scrapings, and other 'signs of something happening.'"*

and 2026-09-14, `PYRELANDS_SCORCHED_RUINS_1`:
> *"For the ruins on the map if any, they should be scorched and burned to warn
> the player of what happens here."*

That is this batch's family named in his own words, with a stated purpose —
**a trace exists to warn or tell the player something.** If he wants one sentence
to head every north star in this family, it is probably that one; it would give
`mark_reads_as_deliberate`, `wrecked_reads_as_dead` and `district_reads_as_authored`
a shared bar instead of three separate ones.
