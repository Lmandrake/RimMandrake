# Condition-gated rituals: concept (2026-10-01)

_Status: BENCH concept for the owner's ruling. Nothing is built. Item (filed separately):
`CONDITION_GATED_RITUALS_MOD_1`. Source of the pitch: the Abyss review
`design/Jawa/worldbuilding/biomes/blackcrags_bedazzle_review_2026-09-30.md` §11, mark 9 (a),
"the Veil Vigil"._

## 1. The idea

His words, typed 2026-10-01 08:33 PDT:

> *"These are very good ideas about having a special ritual. They should not be about this
> particular biome, but rather something that you can do in absolute darkness, and this entire
> biome is resident with that so this should have implications into the Uini gods very richly and
> enable certain rituals that can be done in darkness. This may be an entire new mod for the idea,
> religion concept of rituals that can be done in certain situations or in certain conditions."*

In one paragraph: a ritual is not tied to a place. It is tied to a **condition** of the world at
the moment it is held: absolute darkness first, and later others (eclipse, storm, the sea floor,
killing cold, silence, the dead nearby, the open sky at an Unveiling). A rite can only be started
while its condition holds at the ritual spot. Its quality rises the more deeply the condition
holds, and it fails or sours if the condition breaks partway through. The Abyss is not the rite's
home; it is simply the one place on the planet where absolute darkness is the weather, so it is
where darkness rites are easiest. A colony anywhere can still hold one, in a sealed, unlit room
dug into rock. The free mod ships the framework and a set of rites for any ideoligion. The
campaign layer gives each condition to the Utinni gods who care about it, and darkness belongs
to Ishko the Unmaskable.

## 2. The general mechanism

### 2.1 A condition is a small def, read in three places

One new def type, `RM_RitualConditionDef`, names a condition and a C# worker that answers two
questions for a cell on a map: **does it hold?** (bool) and **how deeply?** (0..1). Darkness is
the first one. The same condition is read in three places in vanilla's ritual pipeline, all
confirmed by RimSage against decompiled 1.6 source (2026-10-01):

| Where | Vanilla hook (MEASURED) | What the condition does there |
|---|---|---|
| **Can it start?** | `RitualOutcomeComp.BlockingIssues(Precept_Ritual, TargetInfo, RitualRoleAssignments)` is virtual; so is `RitualObligationTargetFilter.GetBlockingIssues(...)`; `RitualBehaviorWorker.CanStartRitualNow(...)` is virtual and returns a reason string | A new comp `RM_RitualOutcomeComp_Condition` returns a blocking line ("The spot is not dark: 34% light") while the condition fails. The ritual window greys out and says why. |
| **How good is it?** | `RitualOutcomeComp_QualitySingleOffset`; `RitualOutcomeComp_Indoors` is the exact template (`Count()` and `GetQualityFactor()` read the room at `ritual.Spot`) | The same comp adds a quality factor scaled by depth: "Absolute darkness +25%", "Dim, not dark +5%". |
| **Where can it be held?** | `RitualObligationTargetFilter` subclasses (`RitualObligationTargetWorker_AnyRitualSpotOrAltar` and 20 others) with `protected abstract CanUseTargetInternal(TargetInfo, RitualObligation)` | Optional: a target filter that only offers spots where the condition can hold at all (for example, never a spot under an unroofed sky for a "sealed dark" rite). |

**Darkness reads the vanilla glow grid**: `map.glowGrid.GroundGlowAt(IntVec3, ignoreCavePlants,
ignoreSky)` and `PsychGlowAt(IntVec3)` both exist (MEASURED). "Absolute darkness" is ground glow
at or below a threshold, defaulting to 0, at the spot and across every participant's cell. Inside
the Abyss, once `ABYSS_DARK_BUILD_1` lands, it also counts any cell inside the Dark field
regardless of glow, because the Dark swallows lamplight. That build is not done yet, so the Abyss
hook is a soft dependency (`MayRequire` on the Abyss assembly's types; the darkness condition works
without it everywhere else).

**Breaking the condition mid-rite.** A lamp lit, a door opened onto day, a fire started. The
concept: a `MapComponent` (or the ritual's own lord job) re-reads the condition every 250 ticks
while the rite runs and records the worst depth seen; the outcome reads that. A full break above a
threshold ends the rite as interrupted. **UNMEASURED:** whether vanilla's `LordJob_Ritual` exposes a
clean per-tick hook or needs a Harmony postfix on its tick. Read it in RimSage before building.

**Slot budget.** `MaxRituals = 6` per ideoligion (from `skills/rimworld-ideoligion`), and
`divine_satiation_engine.md` §5b already flags that the campaign will need a "more rituals" mod.
Condition rites compete for those six slots. The framework should therefore **also** offer a
precept-free path: any ritual can be marked condition-gated by an XML patch on its pattern, so
vanilla rites (a funeral, a party, a skylantern night) can gain a darkness variant without a new slot.

**What needs C#:** the condition def and its workers, the comp (gate plus quality), the mid-rite
watcher, a few outcome workers, and the settings screen. **What is pure XML:** the
`RitualPatternDef`s, `PreceptDef`s, `RitualOutcomeEffectDef`s, `ThoughtDef`s and art-tale grammar.
There are **no** `PreceptDef`/`RitualPatternDef`/`RitualBehaviorDef` in `src/RimMandrake` today.
The one ritual-shaped def that exists is `RM_Ishko_RitualOutcome_PlaceSacredMark` (an inert
`RitualOutcomeEffectDef` in `src/RimMandrake/SacredGraffiti/Defs/RitualOutcomeEffects.xml`, with
its worker `RitualOutcomeEffectWorker_PlaceSacredMark`), built and waiting for a ritual to call
it. Darkness rites are the natural first caller (§4).

### 2.2 The condition catalogue (first is darkness; the rest are candidates)

Each is tied to a system that already makes the condition happen somewhere on the planet. It is
one condition per row, read by the same comp.

| # | Condition | Holds when (sketch) | Where it naturally occurs | Status of the system |
|---|---|---|---|---|
| 1 | **Absolute darkness** | ground glow 0 at spot and all participants, or inside the Dark | The Abyss (everywhere); any sealed, unlit, roofed room; the permanently dark half of the tidally locked world | Glow grid is vanilla. The Dark is `ABYSS_DARK_BUILD_1`, open. |
| 2 | **The sun hidden** | vanilla `Eclipse` game condition active | Anywhere, as an event | Vanilla. |
| 3 | **Killing light** | `SolarFlare` active, or the spot under open sky in an overhead-sun heat biome | The dayside; `SOLAR_HEAT_EXPOSURE_1`'s overhead-sun biomes | Flare is vanilla; solar heat is an open item. |
| 4 | **In the storm** | a storm weather on the map (sandstorm, Dune Gale, thunderstorm) | The Stillsand (`RM_DuneGale`), the Abyss's ghorrumak storms | Built in part (`RM_DuneGale.cs`). |
| 5 | **Under the sea** | the ritual map is a sea-floor map | The four seas, reached only by the ship (`RM_SeaDiveHatch`) | Built. |
| 6 | **Killing cold** | outdoor or room temperature below a threshold (for example -20 C) | Ice biomes; any unheated room on the nightside | Vanilla temperature. |
| 7 | **Silence** | no running machine, drum, speaker or combat within a radius | Anywhere, by choice: switch the colony off | Needs a small "noise" read. |
| 8 | **Among the dead** | N or more corpses, graves, skulls or great bones within a radius | The Stillsand's giant skeletons (`RM_GiantSkeletons.cs`); graveyards | Built in part. |
| 9 | **The Unveiling** | the Abyss's rare lifting of the Dark is active and the spot is under open sky | The Abyss only, by nature (the condition is general; the weather is local) | Part of `ABYSS_DARK_BUILD_1`, open. |
| 10 | **Rootless** | the ritual is held aboard a gravship in flight, or within N hours of landing | Anywhere the ship goes | Odyssey gravship. |

Rows 9 and 10 show the pattern the owner asked for: the **condition** is general and the biome
(or the ship) is simply where it naturally comes true.

## 3. Darkness rites in depth

All five run under condition 1. Each says what it asks, what it gives, and how it reads on screen.
Outcome tiers follow vanilla's four-band pattern (`outcomeChances` with `positivityIndex`).

### 3.1 The Dark Vigil (the general form of the Veil Vigil)

- **Asks:** an organiser and at least three spectators keep still at a ritual spot in absolute
  darkness for a long rite (about two in-game hours). No one may carry a light. Quality comes from
  darkness depth, the number of still participants, and how many hold Darkvision or a
  dark-tolerant gene.
- **Gives:** Poor: "a long cold sit" (small mood penalty). Fair: a shared mood memory, "kept
  the vigil". Good: that memory plus a lasting reduction in fear of the dark for the participants
  (the vanilla darkness mood debuff waived for a season; the hediff route is UNMEASURED and must
  be read first). Excellent: the same, plus an art tale ("They sat in the dark until the dark
  sat with them").
- **Reads:** pawns walk in, lamps go out one by one, and then for two hours nothing happens on
  screen. That is the point. **Held during an Unveiling** (condition 9 as a bonus factor, not a
  gate), the vigil becomes the Veil Vigil of the review: a large shared memory and a guaranteed art
  tale. Nobody appears; ban 7 holds.

### 3.2 The Blind Offering

- **Asks:** an item laid on an altar or a ring in absolute darkness, then left there unwatched
  overnight. No pawn may look: the rite ends with everyone leaving the room.
- **Gives:** by morning the offering is either untouched (Poor: nothing, "it was not taken"),
  gone (Fair or Good: a mood boost, "it was accepted"), or gone and replaced by something small
  and strange (Excellent: a random modest item from a curated list, never silver). **Nobody sees
  who took it.** In the Abyss the review's Nhaleth exchange already describes this act, and this
  rite is its mechanical form.
- **Reads:** the colony leaves a thing in the dark and walks away. The next morning a letter says
  what was found. It is a rite about not looking.

### 3.3 The Unlit Wedding (the darkness variant of a vanilla rite)

- **Asks:** the vanilla marriage ceremony held at a spot in absolute darkness (a precept-free
  condition patch on the existing pattern, §2.1).
- **Gives:** the vanilla outcomes, with a darkness quality bonus and a distinct memory, "married
  in the dark".
- **Reads:** it is the same wedding, unlit. In the campaign it is the pious form of an existing
  canon fact, below.

### 3.4 The Lightless Burial

- **Asks:** the vanilla funeral, held in absolute darkness at a grave dug into rock, and closed
  before any light returns.
- **Gives:** the vanilla funeral outcomes, with darkness quality, and a memory that the dead
  "went unseen".
- **Reads:** the funeral party stands around a grave in the black. In the campaign this is
  Ishko's "death as the ultimate concealment" made into a rite.

### 3.5 The Snuffing

- **Asks:** a short rite with an organiser and spectators at a lit spot: each light within a
  radius is put out, one by one, by a participant. It **creates** the condition rather than
  needing it, so it is the gate's way in for a colony that has no dark room yet.
- **Gives:** Poor: lights relit within the hour (nothing). Fair: the room is dark until someone
  relights it, and a small memory. Good: the dark lasts and the next darkness rite in that room
  gains quality. Excellent: the same, plus participants are steadier in the dark for a day.
- **Reads:** a ceremony of switching things off. It costs light, work speed and comfort, which
  is the trade.

## 4. The Utinni gods

All of this is the **campaign layer** (RimUtinni, `RUT_`), riding the Utinni patch layer on top
of the free framework. The gods are those of The Salvation, canon of record in
`design/Jawa/divine_satiation_engine.md` (§2.0b, "The Pantheon"). Nothing below contradicts it;
where this concept leans on it, the line is cited.

### 4.1 Why darkness is doubly sacred already

The canon says it outright: Sh'kaar the All-Searing *"hates Ishko above all … together the two
make darkness doubly sacred (one demands you hide, the other punishes those who break the dark)"*
(§2.0b ⑧). Ishko the Unmaskable is *"a pair of glowing orange eyes in the dark"*, the god of
hiding, stillness and outlasting, and his deepest facet is *"death as the ultimate concealment …
for the grave is the deepest dark"* (§2.0b ①). The clan already *"mate only in total darkness"*
(§2.0b ①), and the cross-god table lists *"Light ⇄ dark (Sh'kaar ⇄ Ishko) — lighting the dark
feeds evil Sh'kaar AND offends hiding-Ishko"* (§8). The ambient channel already gives
*"eclipse ↑Ishko + ↓Sh'kaar"* and *"Dark-obscured tile → ↑Ishko"* (§8b). So darkness rites are
not a new theology. They are the rite that the pantheon has been missing.

### 4.2 How each rite addresses the gods

Under the §5 model (*"a ritual is an open floor the gods may speak from"*), every rite pre-moves
the god vector by its nature, then each god decides whether to speak.

| Rite | Pre-move (by its nature) | Who tends to speak, and with what |
|---|---|---|
| Dark Vigil | ↑Ishko strongly; ↓Sh'kaar (he is starved) | Ishko, pleased: the eyes. A pair of orange eye-glints is seen on a wall after the rite (the existing `RM_Ishko_RitualOutcome_PlaceSacredMark` is its outcome: Ishko's sacred mark left at the spot, exactly what that inert def was built for). |
| Blind Offering | ↑Ishko; ↑Mob'Unloo (an exchange is sanctified, §2.0b ④: *"nothing is ever handed directly; a thing is set down and the other takes it up"*) | Mob'Unloo answers the trade; Ishko keeps the taker unseen. A Slighted Mob'Unloo, rarely, leaves the offering untouched and counts it against the ledger. |
| Unlit Wedding | ↑Ishko (the canon practice, kept); ↑Oomo faintly (the family grows) | Oomo blesses fertility; Ishko is content. A wedding held lit is not forbidden, but it is the impious form. |
| Lightless Burial | ↑Ishko strongly, more if the dead died unseen (§8b: *"died unseen … ↑Ishko"*); ↑Rekko if the body is interred, not scrapped | Ishko, and Rekko for the kept body. |
| Snuffing | ↑Ishko; ↓Sh'kaar; ↓Ohm faintly if the lights put out are machines | Zizzik, rarely, if a machine was switched off badly: the wrong spark. |

**The one dangerous answer.** The canon already names it: *"Wrathful Sh'kaar draws something to a
lit night-rite"* (§5). So a darkness rite whose condition **breaks** (a lamp lit, a door opened
onto day) is the worst kind of failure: it is a lit night-rite. The mid-rite watcher (§2.1) hands
that event to Sh'kaar. This is the rite's teeth, and it is canon, not invention.

**Ishko and skipping.** He *"alone does not punish a skipped rite"* (§5b), so darkness rites are
never owed to him. They are the one family of rites the player holds purely by choice, which suits
the god of stillness.

### 4.3 What the gods give back (campaign only)

- **Ishko's mark.** The `RM_Ishko_RitualOutcome_PlaceSacredMark` outcome, already built, on a
  Good or Excellent Dark Vigil.
- **His sanction for the dark home.** Ishko wants the ship to become *"the eternal hidden lurker
  … terraform the dark itself into a home"* (§2.0b ①). Repeated Excellent darkness rites on one
  map can count toward that vision (design input to the satiation engine, which is design prose
  only and not built; until it is, the gift is mood and art).
- **The Council of Voices, in the dark.** §5c places the climax at the ship's sacred centre, with
  the gods speaking from its speakers. A darkness rite held there means the shrine-heart's lamps
  are put out first, so the voices come out of the black, and Ishko's line, if he speaks, is the
  only one heard without light. This needs the RimAI/Cradle-Mind voice layer, as §5c already says.
- **The Abyss's Sith whisper (Star Wars tier, never confirmed).** In the Abyss, a Dark Vigil held
  at the rare **wrong** ring (review §11, mark 9 (c)) advances the lore ladder toward the Sith
  whisper. No god claims it. The Narrator frames it as a voice that is **not** one of the nine,
  which makes the gods uneasy (a faint ↓ across the pantheon). It never resolves into a visitor.
- **Nhaleth (free tier, never confirmed).** The free mod's Abyss cryptid. In the free tier, a
  Blind Offering left in the Abyss is the "Nhaleth exchange": something takes it, and nobody sees
  what. The Nhaleth are never shown and never confirmed. The campaign keeps the same name (owner's
  typed ruling, review §11, "Cryptid name, all tiers").

### 4.4 The tier split

| Layer | Contents | Stands alone? |
|---|---|---|
| **Free framework** (`mandrake.rm.*`) | The condition def and workers, the gate and quality comp, the mid-rite watcher, the five darkness rites as ordinary Ideology rites for any ideoligion, two generic precepts ("The Dark is holy", "Light is a trespass"), the Nhaleth exchange flavour when the Abyss mod is present | Yes. The rites work under any player ideoligion and any deity; nothing names a Utinni god. |
| **Campaign** (`RUT_`, Utinni patch layer) | The god pre-moves and responses, Ishko's mark wiring, the lit night-rite as Sh'kaar's answer, the Council in the dark, the Sith-whisper ladder, rite text in the Salvation's register | Rides on the free framework and The Salvation ideoligion (`src/Jawa/ideoligion/The Salvation.rid`). |

Per Q11a, an invented exotic name is free-tier material; only the Sith whisper is Star Wars IP.

## 5. Naming and settings

**Suggested name: _Rites of Circumstance_**, packageId **`mandrake.rm.ritesofcircumstance`**, C#
namespace `RimMandrake.RitesOfCircumstance`, def prefix `RM_`. The name says the rule (a rite
belongs to a circumstance, not a place) and leaves room for every condition in §2.2.
Alternatives: _Conditional Rites_ (`mandrake.rm.conditionalrites`, plainer), _The Hour and the
Place_ (`mandrake.rm.hourandplace`, more evocative but implies place). Campaign patches:
ride the existing Utinni patch layer (`UtinniPatches`), not a new campaign mod.

**Mod Settings** (defaults are the shipped behaviour; all-off degrades to vanilla rites):

- On/off per condition (darkness, eclipse, storm, sea floor, cold, silence, the dead, the
  Unveiling, rootless).
- On/off per rite (the five darkness rites, each).
- **Darkness threshold**: the glow a spot may have and still count as absolute dark (default 0).
- **Strict participants**: whether every participant's cell must meet the condition, or only the
  spot (default: every participant).
- **Break tolerance**: how much a condition may waver mid-rite before the rite is interrupted.
- **Condition variants of vanilla rites** (the Unlit Wedding and Lightless Burial patches): on/off.
- **Abyss integration**: count the Dark as absolute darkness when the Abyss mod is present
  (labelled "affects only maps in the Abyss").

## 6. Open questions for the owner

1. **Should a darkness rite be possible anywhere, or only where it is naturally dark?**
   - **Anywhere you make it dark (Recommended):** a sealed, unlit room in any biome counts. The
     Abyss is simply the easiest place. Most players can use it, but it is less special.
   - **Only where it is naturally dark:** the Abyss, the nightside, deep caves. More precious, but
     most colonies will never see a darkness rite.
   - **Anywhere, but natural dark is better:** made darkness works, and natural darkness gives a
     large quality bonus. Both, at the cost of one more number to tune.

2. **Do these rites need their own ritual slots, or should they also change rites you already hold?**
   - **Both (Recommended):** new rites for the ideoligion, plus darkness variants of the wedding
     and funeral that need no slot. Richest, and it works around the six-rite limit.
   - **New rites only:** cleaner, but they compete with everything else for six slots.
   - **Variants only:** no slot pressure, but there is no rite that exists only in the dark.

3. **What happens when the dark breaks during a rite?**
   - **It fails, and in the campaign Sh'kaar answers (Recommended):** a lit night-rite draws
     something, as the canon already says. High stakes, and it uses your own lore.
   - **It fails quietly:** a poor outcome, nothing worse. Gentle, but the rite has no teeth.
   - **Quality just drops:** no failure, only a worse result. Forgiving, but the condition barely
     matters once started.

4. **Which condition should come second, after darkness?**
   - **The eclipse:** the sun hidden, Ishko's blessed dark and Sh'kaar's humiliation, already in
     your gods' event table. Cheapest, because the event is vanilla.
   - **Under the sea:** rites only on the sea floor, reached by the ship. Strong place feel, and
     the system is built.
   - **Among the dead:** rites near bones and graves, which suits the Stillsand's giant skeletons.
     Medium build.
   - **The open sky at the Unveiling:** the rare lifting of the Dark. Most special, but it waits
     on the Abyss's Dark being built.

### Note on a name collision

`design/Jawa/first_contact_chains.md` is titled "the nine unveilings" (each god's veiled
first-manifestation arc), and the Abyss's rare weather is also "the Unveiling". A rite that is
"best held during an Unveiling" will read ambiguously in the campaign. One of the two may need
another word; this concept does not rename either.
