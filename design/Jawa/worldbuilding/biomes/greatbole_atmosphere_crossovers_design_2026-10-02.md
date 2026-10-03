# Greatbole atmosphere and crossovers — design (GREATBOLE_ATMOSPHERE_AND_CROSSOVERS_1)

**Status: DRAFT for owner ruling, 2026-10-02 (BENCH).** Design only — no defs, no code, no items filed.
Parent spec: `design/Jawa/worldbuilding/biomes/kits/greatbole_harvest_spec.md` §5, §7, §8a, §8b (owner
rulings 2026-09-23). This doc does not re-rule anything there; it turns those four sections into a buildable
shape and answers the engine questions that spec's §10 left UNMEASURED, where RimSage could answer them.

**Which greatbole, every time.** Three defs carry the name:

| def | what it is | where | tier |
|---|---|---|---|
| `RM_Greatbole` | the mature, **fellable** giant tree (roster row 22) | `src/RimMandrake/Greentide/Defs/ThingDefs_Plants/RM_Greatbole.xml` | RM_, free mod |
| `RUT_GreatboleHeartwood` | the **mineable blob** (`RockBase`) a player digs into | `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_GreatboleHeartwood.xml` | campaign patches |
| `RUT_GreatboleCore` | a **1×1 bookkeeping marker**, draws nothing, selectable, carries both comps | `src/RimUtinni/UtinniPatches/Defs/ThingDefs_Buildings/RUT_GreatboleCore.xml` | campaign patches |

Everything in this doc — song, sanctuary, pilgrims, crossovers — is about the **landmark**: the heartwood blob
plus its core. None of it is about `RM_Greatbole`, the fellable tree, except where stated.

---

## 1. What exists (measured 2026-10-02 from our own source)

### 1a. Already built and directly reusable

| need | what serves it | path |
|---|---|---|
| "how hollow is this bole" as a 0–1 number | `RM_MapComponent_LivingRegrowth.GetRemovedFraction(boleId)` — fraction of the footprint whose edifice is no longer `RUT_GreatboleHeartwood`. **Sealed cells count as removed.** Also `GetBoleCenter`, `GetFootprintCells`, `AllBoleIds` | `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_LivingRegrowth.cs` (l.169) |
| per-cell regrow state (which cuts are still open wounds) | `BoleRecord.timers` (`CellTimer` Scheduled / Warning / Crushing) and `footprint`, both Scribed. ⚠️ `BoleRecord` is `internal` — a content mod cannot read the timers; a small public query is owed (§4) | same file, l.496–555 |
| sealing | `RUT_ToxinSealant` terrain; regrowth skips a cell whose terrain is the sealant | same file, l.262/318 |
| the 40/60/70 ladder and its events | `RUT_CompGreatboleHarvestLadder` on `RUT_GreatboleCore` — `GreatShaking()`, `AnnounceViolentHealing()`, `Catastrophe()`; polls every 250 ticks; Wildsteam −70 goodwill on the catastrophe | `src/RimUtinni/UtinniPatches/Source/RUT_CompGreatboleHarvestLadder.cs` |
| ladder thresholds as sliders | `UtinniPatchesSettings.greatboleShakingThreshold` / `HealingThreshold` / `CatastropheThreshold` / `CatastropheEnabled` | `src/RimUtinni/UtinniPatches/Source/UtinniPatchesSettings.cs` |
| layered camera-attached hum | `RM_MapComponent_ProximitySoundscape` + `RM_ProximitySoundscapeExtension` (`mandrake.rm.creaturebehaviors`), PerTick sustainers, hysteresis, `minLayerChangeIntervalTicks` pop-mitigation, settings kill-switch `proximitySoundscapeEnabled` | `src/RimMandrake/CreatureBehaviors/Source/` |
| the pattern for authored hum layers | `RM_Hum_Thalquith_Low/Mid/High` — three SoundDefs, three pitchRanges, placeholder Obelisk ambience clips | `src/RimMandrake/Greentide/Defs/SoundDefs/RM_GreentideHummingGrove.xml` |
| holding a room's temperature, calibrated | `RM_MapComponent_WarmGround` — room-scoped sweep every 250 ticks, `room.PushHeat`, ramp cap calibrated against `RoomTempTracker` arithmetic. `RM_ColdSink` — `GenTemperature.ControlTemperatureTempChange` | `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_WarmGround.cs`, `src/RimMandrake/BlueDesert/Source/RM_ColdSink.cs` |
| chambers are under thick roof | `RM_GenStep_LivingBoles` roofs every bole cell with `RoofDefOf.RoofRockThick` by default; `RUT_Greentide.xml` leaves `roofDef` unset | `src/RimMandrake/EnvironmentalHazards/Source/RM_GenStep_LivingBoles.cs` l.44/106 |

### 1b. Findings that change the item's own text

1. 🔴 **`RM_Greatbole` now exists** (`f521c0c79`, 2026-09-26, `GREENTIDE_JUNGLE_TREE_ROSTER_1`). The item's
   point 5 says the seed's planting is "blocked on that def shipping … only a placeholder exists" — that is
   **no longer true**. The seed wiring is unblocked. It is not in this doc's scope; the item text is stale and
   should be corrected by whoever next touches the item.
2. 🔴 **The landmark exists only in the campaign layer.** `RUT_GreatboleHeartwood`, `RUT_GreatboleCore`, the
   ladder and the living-bole GenStep are all in `mandrake.rut.patches`; `RM_Greentide` places no living bole
   (only `RM_FeverWood` and `RUT_*` biomes carry a `LivingBole` extension). ⇒ The spec's "pilgrims are RM_-tier
   with a campaign skin" has **nothing to visit in the free mod** — the free mod's only greatbole is the
   fellable tree. This is Question 1.
3. **No readable sign exists today for how hollow a bole is.** Neither `RM_CompLivingBoleMarker` nor
   `RUT_CompGreatboleHarvestLadder` overrides `CompInspectStringExtra`. The 40% Shaking is invisible until it
   fires (spec §1 accepted that as a cost; §5 said the song removes it — but the song cannot be the only sign).
4. The ladder's three events all play `SoundDefOf.Building_Complete` as a stand-in. Fine as placeholder;
   the song design below gives them real sounds.

### 1c. Engine answers to the spec's §10 (RimSage, decompiled 1.6, 2026-10-02)

| §10 | question | answer |
|---|---|---|
| 8 | can two live sustainers make a beat? | **Partly answered.** Beating needs two tones a few Hz apart; it does **not** need a phase lock (phase only shifts *when* the throb falls, not its rate) — the spec's caveat was over-stated. The real obstacle: `SubSustainer` restarts samples on `sustainIntervalRange` with a random `startDelayRange`, and a `pitchRange` is re-rolled per sample, so a non-zero pitch range would wander the beat rate. With fixed single-value pitches the rate should hold. ⚠️ **Not heard — still UNMEASURED as a sound.** Recommendation stands: bake the throb into one authored file. |
| 9 | can a chamber be held at deep-ground temperature? | **Yes, and the engine has its own number.** `RoomTempTracker.DeepEqualizationTempChangePerInterval` pulls a room under thick roof toward **15 °C** — but **only downward** (returns 0 when the room is colder than 15) and at `5E-05` per tick-interval on a surface map vs `0.002` on an underground one. So bole chambers *already* cool faintly toward 15 °C and never warm. Reading/pushing room temperature is proven in our own code (`room.PushHeat`, `room.Temperature +=`). "Pinned" (set every sweep) is possible; see §3 for why not to. |
| 10 | visitor disposition from a map reading at arrival; detecting "witnessed" | **Both answered.** `IncidentWorker_VisitorGroup.CreateLordJob(parms, pawns)` is `protected virtual` and `LordJob_VisitColony(faction, chillSpot)` takes the spot they stand at — so a subclass reads the bole at arrival and sends them to the core. "Witnessing" needs no engine detection at all: the Great Shaking is **our own method** (`GreatShaking()`), so at that call we ask the map's lords whether a pilgrim lord is present. `LordJob_VisitColony`'s graph already has `Trigger_BecamePlayerEnemy` → defend-local-group (they fight if their faction turns hostile). `IncidentQueue.Add(QueuedIncident(firingInc, fireTick))` exists for an advance-warned arrival. |
| 12 | can meditation focus strength vary at runtime? | **Yes.** `FocusStrengthOffset` is an abstract class with `virtual float GetOffset(Thing parent, Pawn user)`; vanilla ships ~13 subclasses (`_Lit`, `_RoomImpressiveness`, `_ArtificialBuildings` …) evaluated live by `StatWorker`. A `FocusStrengthOffset` subclass reading `GetRemovedFraction` is the whole harmony-tracking feature. |
| 13 | can anima grass attach to a non-anima Thing? | **Probably.** Anima is three comps on `Plant_TreeAnima`: `CompMeditationFocus`, `CompSpawnSubplant` (`subplant` = `Plant_GrassAnima`), `CompPsylinkable`. No `(Plant)parent` cast in `CompSpawnSubplant` (only in `CompSpawnSubplantDuration`). ⚠️ `CompPsylinkable` and the linking ritual's target rules on a **Building** parent are UNMEASURED. |
| 14 | can the dryad / connected-pawn system attach to a custom tree? | **UNMEASURED for a Building host.** `CompTreeConnection` loses connection strength per day for every artificial building within `radiusToBuildingForConnectionStrengthLoss` — and a greatbole is, by §7's design, *the best base site on the planet*, so a colony living in it would starve its own connection. That is a design problem before it is an engine one (§5b). |

Also measured: `MemeDef TreeConnection`, `PreceptDef TreeCutting_Prohibited` / `TreeCutting_Horrible`, and
`MentalStateDef Berserk` / `BerserkShort` all exist in the loaded defs.

---

## 2. The song

### 2a. What the player hears (the spec's five beats, made concrete)

| removed fraction (live) | layer set | character |
|---|---|---|
| 0 – 25 % | **Root** | an ultra-deep bass, almost felt rather than heard, drifting slowly in pitch over ~20 s. Consonant. |
| 25 % – (Shaking − 5 %) | **Root + Rise 1** | a second, higher partial, a clean fifth or octave above. Still consonant — the tree "rings higher" as it hollows. |
| (Shaking − 5 %) – Shaking | **Rise 1 + Grate** | Root drops out; a partial a semitone off Rise 1 enters. **First dissonance — this is the 40% warning.** |
| Shaking – (Healing − 5 %) | **Rise 2 + Grate** | higher again, dissonance held. |
| (Healing − 5 %) – Catastrophe | **Throb** | one authored file: two close tones beating ~3–6 Hz under a non-harmonic overtone. Deliberately unpleasant. |
| falling back (healing) | the set for the new band, entered **through a 30 s "resolve" sting** | the harmony audibly returns — forgiveness heard. |
| dead (post-catastrophe) | silence | the bole is a husk (`RUT_GreatboleDeadHusk`); nothing hums. |

Band edges ride the three existing Mod Settings sliders, so moving a threshold moves its warning with it.

### 2b. Mechanism — one generalisation, not a second soundscape

The component today is **additive**: layer *n* is added when the nearby count earns it. The song is not
additive — the Root must *leave* as the tree hollows. ⇒ Generalise `RM_ProximitySoundscapeExtension` with:

- `driver`: `NearbyCount` (today's behaviour, default) **or** `ExternalScalar`.
- `bands`: an ordered list of `{ upTo: float, layers: [SoundDef…] }` — used only by `ExternalScalar`; each
  band names its own full set. Today's `humLayers` stays for `NearbyCount`, so `RM_Thalquith` is untouched.
- **The scalar comes in through a provider, not a dependency.** `mandrake.rm.creaturebehaviors` must not
  reference EnvironmentalHazards (it ships no content and EnvironmentalHazards already depends on it). Add a
  tiny interface in CreatureBehaviors, e.g. `IRM_SoundscapeScalarSource { float SoundscapeScalar { get; } }`,
  implemented by `RM_CompLivingBoleMarker` (which knows its `BoleId`). The component reads the nearest tagged
  Thing within `radius` that implements it. Content-blind on both sides, which §12 of the spec requires.
- Existing hysteresis and `minLayerChangeIntervalTicks` apply to band changes unchanged. ⚠️ The recorded
  pop on `Sustainer.End()` still applies; band changes are rare (they follow mining, not walking), which is
  the best case for that mitigation.

The tag goes on `RUT_GreatboleCore` (the marker that knows the bole), never on `RUT_GreatboleHeartwood` —
tagging hundreds of heartwood cells would make every cell a listener-count hit.

### 2c. Sound spec (sourcing is NOT solved here — `design/RimMandrake/sound_sourcing_options_2026-10-02.md`)

Seven assets, all loopable unless stated, mono, mixed so the Root sits under ambient wind:

| asset | length | spec |
|---|---|---|
| `Root` | 20–30 s loop | 30–45 Hz fundamental, slow ±3 % pitch drift baked in, wooden resonance (hollow log, cello body), no attack |
| `Rise1` | 20 s loop | same timbre, a fifth/octave up, gentle |
| `Rise2` | 20 s loop | a further step up, thinner, more "ringing" |
| `Grate` | 20 s loop | a partial a semitone (≈6 %) off whichever Rise is playing, slight rasp |
| `Throb` | 10–20 s loop | two tones 3–6 Hz apart (audible beating), plus an inharmonic overtone; baked, not built from two live layers |
| `Resolve` | 4–8 s one-shot | dissonance sliding into a clean chord — the healing sting |
| `Groan` | 3–6 s one-shot | deep wooden groan; replaces `Building_Complete` on Shaking / healing / catastrophe |

Placeholder until sourcing is ruled: the Thalquith precedent (Obelisk ambience grains at fixed `pitchRange`
single values). ⛔ Do not report the song "works" until the owner has heard it.

---

## 3. The thermal sanctuary

### 3a. Design

**Chambers inside a greatbole are pulled, both ways, toward deep-ground temperature: 15 °C** — the engine's own
deep-ground figure (`RoomTempTracker`), so the fiction and the engine agree on what "deep ground" means.

- **Which rooms:** a proper, enclosed, roofed room with at least one cell inside a bole's footprint
  (`GetFootprintCells`). Sealed cells count; a sealed chamber is the intended home.
- **Strength scales with the sap column.** The pull is strongest at 0 % removed and fades linearly to nothing at
  the catastrophe threshold. 🔑 This ties the sanctuary to the ladder: the more you take, the worse your
  shelter — greed costs comfort before it costs lives, and the player can *feel* hollowing in a temperature
  readout, not just hear it.
- **A strong pull, not a pin.** Recommended over hard-pinning: a pinned room cannot be heated or cooled by the
  player at all (a freezer inside a bole would be impossible), and the Greentide's biome is hot, so the only
  thing a player ever wants from it is "cooler", which a pull delivers. Equilibrium target: a closed, unheated
  chamber in a 45 °C day sits at ~18–22 °C at 0 % removed. Calibrate with WarmGround's arithmetic, not by guess.

### 3b. Mechanism

A content-blind `RM_MapComponent_BoleThermal` in EnvironmentalHazards (or a sweep inside
`RM_MapComponent_LivingRegrowth`, which already ticks every 250): for each registered bole, collect rooms
touching its footprint once per sweep, push `room.PushHeat(step × cellCount)` toward the target with a capped
step — the exact shape of `RM_MapComponent_WarmGround.HeatMatFlooredRooms`. Target and strength are fields on
`CompProperties_LivingBoleMarker` (`deepGroundTemperature 15`, `thermalStrength`), so `RUT_FeverTrunkCore` can
opt in or not. No Scribe state.

⚠️ Caveat recorded: this stacks with vanilla's own thick-roof cooling (downward only, weak on a surface map).
Harmless, but the calibration must include it.

---

## 4. The pilgrims

### 4a. Who comes

- **Campaign (Utinni):** the Wildsteam Clan (`RUT_Jawa_WildsteamClan`), whose Green Oath already forbids
  "cutting a living tree".
- **Free mod (RM_):** any non-hostile faction whose ideoligion holds the `TreeConnection` meme or the
  `TreeCutting_Prohibited` / `TreeCutting_Horrible` precept. If none exists, the incident does not fire.
  ⚠️ Only meaningful if the free mod has a landmark bole at all — Question 1.

### 4b. The visit

1. **Warning, a day ahead.** A letter: *"Pilgrims of the [faction] will arrive in about a day to hear the
   greatbole's song."* Fired by queuing the real visit through `IncidentQueue` ~1 in-game day later. 🔑 This
   is what makes it a decision, not a dice roll (spec §8a) — the player has a day to seal, stop, or hide.
2. **Arrival reading** (subclass of `IncidentWorker_VisitorGroup`, overriding `CreateLordJob`): chill spot =
   a standable cell next to the bole; then read the bole:
   - `woundFraction` = open, unsealed cells **still waiting to regrow** ÷ footprint. Sealed cells and fully
     regrown cells are **not** wounds (spec §8a's three consequences). Needs one new public query on
     `RM_MapComponent_LivingRegrowth`: `GetOpenWoundCount(boleId)` (count of footprint cells that are not
     heartwood, not sealant, and have a live timer). `BoleRecord` is internal, so this is a one-method addition.
3. **Reaction bands** (numbers are INVENTED, for ruling):

| wound fraction at arrival | they… | sign to the player |
|---|---|---|
| < 5 % | **listen** — stay the normal visit length, sit at the bole; small goodwill gain on departure; may leave a gift (vanilla `TransitionAction_CheckGiveGift`) | arrival letter "they have come to listen"; departure message "the pilgrims leave content" |
| 5 – 20 % | **grieve** — shortened stay, goodwill loss on departure | letter "they see open wounds in the tree"; pilgrims' mood/thought visible on inspect |
| > 20 % | **furious** — leave at once, large goodwill loss | letter "the pilgrims are enraged by what you have done" |

4. **Witnessing a Great Shaking.** In `GreatShaking()` (our code), look for a live pilgrim lord on the map. If
   one is present, they attack — *how* is Question 2 (whole-faction hostility vs. a local frenzy).
5. **Catastrophe while they are present** is already covered: the existing −70 Wildsteam goodwill (campaign) plus
   being inside the 50-cell crush.

### 4c. Frequency

Rare: at most one visit per bole per ~30 days, only after the player has been on the map ~5 days (so they have
met the bole). A Mod Settings toggle and an interval slider.

---

## 5. Two opt-in crossovers

**What "opt-in" means, concretely:** two checkboxes in the owning mod's Mod Settings, **default OFF**, labelled
as changing the tree's character; Utinni ships with both off and no campaign mechanic, quest or balance number
may assume either. Toggling one live adds/removes the behaviour on the next load at the latest; no save
corruption if switched off mid-game (comps stay inert, nothing is Scribed that requires them).

⚠️ **Where they attach.** The comps must sit on `RUT_GreatboleCore` (the only Thing that *is* the bole). It is a
1×1 impassable building in the middle of the blob — pawns cannot stand next to it until they have mined to it.
⇒ The meditation spot is "anywhere within N cells of the core" (vanilla foci are used from a radius), and
anima grass grows on open floor cells inside or beside the bole.

### 5a. Anima crossover

- **Fixed-strength first:** `CompMeditationFocus` (Natural focus) on the core, strength above the anima tree's
  0.28 (it is "a superior anima tree"; propose 0.34, INVENTED). `CompSpawnSubplant` growing `Plant_GrassAnima`.
- **Harmony tracking — now shown buildable:** a custom `FocusStrengthOffset` subclass returning a negative
  offset proportional to `GetRemovedFraction` (e.g. −0.30 at the Shaking threshold). Its `GetExplanation`
  string makes it readable on the stat card: *"Hollowed: −18 %"*. So "mining degrades meditation" ships at the
  same time as the simple version, not after.
- **Grass only where you have not cut:** the subplant's cell choice must refuse footprint cells that were ever
  mined (i.e. not heartwood originally, now open). ⚠️ UNMEASURED: whether `CompSpawnSubplant`'s cell picking
  is overridable or needs a subclass.
- **Psylinking:** ⚠️ UNMEASURED on a Building parent (`CompPsylinkable` + the linking ritual's target filter).
  If it does not work, ship focus + grass without the linking ritual and say so in the settings tooltip.

### 5b. Arboreal servant crossover

- The Gauranlen system (`CompTreeConnection` + dryads) is the obvious host, but **it is built to punish nearby
  buildings**, and a greatbole colony *is* nearby buildings. Using it as-is gives a feature that fails exactly
  in the configuration the sanctuary makes optimal. ⇒ Two options, Question 4.
- Either way: servants are dryad-class pawns tied to the connected colonist; they fight grubs (spec §8b-iii,
  expected, document it); **grubs stay hostile in every configuration**.
- ⚠️ UNMEASURED: whether `CompTreeConnection` tolerates a Building parent, and what it does when the core is
  destroyed by the catastrophe (should: connected pawn takes the vanilla tree-death mood hit; servants die).

---

## 6. Readable signs (no effect without one; sound-off players included)

| effect | visual / text sign | sound sign |
|---|---|---|
| hollowing (any %) | **new inspect line on `RUT_GreatboleCore`**: "Hollowed 34 % — the song is strained (Shaking at 40 %)"; also shown when any heartwood cell is selected | the song's band |
| approaching Shaking (−5 %) | inspect line turns amber; one-time message "The greatbole's song has turned discordant." | Grate enters |
| approaching catastrophe | inspect line red; one-time letter (not message) | Throb |
| healing back | message "The greatbole's song is resolving." | Resolve sting |
| thermal pull | room inspect/temperature readout already shows it; core inspect adds "Chambers held toward 15 °C (strength 70 %)" | — |
| open wounds (pilgrim ledger) | core inspect: "Open wounds: 12 cells (sealed: 30)" — so the player can check before pilgrims arrive | — |
| pilgrims coming / reaction | advance letter; arrival letter naming the reaction band and why | — |
| pilgrims witness Shaking | red letter naming the cause | Groan |
| anima harmony | stat-card offset explanation "Hollowed: −18 %" | — |
| servants vs grubs | vanilla combat log; settings tooltip states it is expected | — |

---

## 7. Build plan (FOUNDRY), smallest first

Each step is independently shippable and has a scriptable check (debug_process.md first-script contract).

| # | work | mod | size | check |
|---|---|---|---|---|
| 1 | Inspect string on `RUT_GreatboleCore`: hollowed %, next threshold, open wounds, sealed count | UtinniPatches + one public `GetOpenWoundCount` / `GetSealedCount` on LivingRegrowth | S | read the string via bridge after mining N cells |
| 2 | Thermal pull (§3), fields on `CompProperties_LivingBoleMarker`, settings toggle | EnvironmentalHazards | S–M | build a sealed chamber, step ticks, read room temp vs outdoor |
| 3 | Soundscape `ExternalScalar` driver + bands + provider interface; `RM_CompLivingBoleMarker` implements it; placeholder clips | CreatureBehaviors + EnvironmentalHazards + UtinniPatches SoundDefs | M | state-read of active band per bole fraction (no listening needed for the logic) |
| 4 | Replace `Building_Complete` stand-ins with `Groan`/`Resolve` defs (placeholder clips) | UtinniPatches | S | — |
| 5 | Pilgrims: advance-warned incident, `CreateLordJob` override, reaction bands, `GreatShaking` hook | UtinniPatches (campaign); RM_ half waits on Q1 | M–L | fire via dev incident with wounds at 0/10/30 %, assert lord state + goodwill delta |
| 6 | Anima crossover: settings toggle, comps patched onto the core when on, harmony `FocusStrengthOffset` | UtinniPatches (or wherever Q1 puts the landmark) | M | stat value of `MeditationFocusStrength` at 0 % and 40 % removed |
| 7 | Servant crossover per Q4 | same | L | Desktop RimSage read of `CompTreeConnection` on a Building first |

Owner must **hear** step 3/4 before any "the song works" claim. ⛔ No unattended live audio judgement.

---

## 8. Questions for the owner

**Q1. The free mod has no living greatbole to visit — what should generic pilgrims come to?**
The mineable landmark (heartwood + core + the 40/60/70 ladder) lives only in the Jawa campaign patches. The
free Greentide mod has just the fellable tree.
- **(Recommended) Move the landmark into the free mod.** Heartwood, core, ladder and song become RM_ content;
  the campaign only adds Wildsteam on top. Most work (a rename/move with save risk on live Scribed regrowth
  state), but the free mod gets the whole greatbole experience, which the "same game minus Star Wars" ruling
  points toward.
- **Campaign-only pilgrims for now.** Cheapest; the free mod gets no pilgrims until a later move. Contradicts
  the spec's "RM_-tier with a campaign skin".
- **Generic pilgrims visit the fellable `RM_Greatbole` instead.** They judge chopped vs standing giants. Cheap,
  but loses the sealed/open-wound ledger that made the idea good.

**Q2. When pilgrims witness a Great Shaking and "attack outright", how big is that?**
- **(Recommended) A local frenzy.** The pilgrims on the map go berserk and fight; their faction loses goodwill
  but is not declared at war. Hurts, is survivable, and the clan can still be won back with seeds.
- **Their whole faction turns hostile.** The vanilla visitor logic already fights back when that happens. Very
  strong — in the campaign it would end the Wildsteam relationship from one mistimed blast.
- **They flee and the faction turns hostile later** (after they get home). A softer-feeling version of the
  above with time to prepare.

**Q3. Should the greatbole's chambers pull toward cool (15 °C) both ways, or be pinned there?**
- **(Recommended) A strong pull that weakens as the tree is hollowed.** Shelter quality becomes another cost of
  greed; heaters and coolers still work inside.
- **A hard pin at 15 °C, regardless of mining.** Simplest to understand; but no freezer or warm room can ever be
  built inside, and mining costs no comfort.
- **A pull at fixed strength (not tied to mining).** Middle ground; simpler to tune.

**Q4. For the opt-in servants: reuse the vanilla Gauranlen dryad system, or build a simpler one?**
- **(Recommended) Simpler, our own.** The connected colonist calls a small number of wooden servants that do not
  care about nearby buildings. Works inside a colony living in the tree — the very case the sanctuary creates.
  More code.
- **Vanilla Gauranlen as-is.** Least code, familiar to players; but it loses strength for every nearby building,
  so a colony living in the bole would barely get servants.
- **Gauranlen with the building penalty switched off for this tree.** Familiar and works in a colony; depends on
  an engine check not yet done (whether the system accepts a non-plant host).
