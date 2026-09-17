# AtmosphericBase — the hook ecosystem

**Companion to `design/RimMandrake/atmospheric_base_mod_definition.md` §6, which points here for
detail and ranking.** Research pass, 2026-09-16, on the Mac laptop.

status: DRAFT — research only. Nothing was built and no existing file was changed.

---

## §0 What this document can and cannot claim

Written on the **laptop**, where nothing about the running game is measurable: no RimWorld
install, no def dump, no decompiler, and RimSage has never connected. So:

- Every claim about **our own source** was read from the file this pass and is cited by path
  (and line, where a line is load-bearing).
- Every claim about **engine behaviour** is marked `UNMEASURED — owed a Desktop check`.
- The mod list is read from the newest snapshot on disk,
  `infrastructure/state/modlists/ModsConfig.FULL.PRECAPTURE.20260913_032142.xml` (**599**
  `<li>` entries). The **live** `ModsConfig.xml` is on the Windows machine and is
  `UNMEASURED — owed a Desktop check`; treat every third-party mod below as "present on
  2026-09-13", not "present now".

---

## §1 Corrections to the brief

Six things in the commission are wrong or incomplete. Taking them first, because three of them
move a hook to a different mod.

### 1.1 Ninefold is not a loudness source today. It has no loudness concept at all.

Read in full: `src/RimMandrake/Ninefold/Source/GameComponent_Ninefold.cs`. Its **entire** public
read surface is five members:

```
static GameComponent_Ninefold Instance      // null outside Playing
float        GetSatiation(God)              // -100..100, signed, event-driven only
float        GetMood(God)                   // -100..100, private random walk
SatiationBand GetBand(God)                  // Wrathful < Slighted < Neutral < Content < Exalted
bool         IsUnveiled(God)                // first contact fired?
```

plus three write members (`ApplyDelta`, `Notify_Launched`, `NotifyViolentDeath`,
`TryFirstContact`). There is **no** `Loudness`, no rank, no ordering, and — the expensive part —
**no change notification of any kind.** Everything is pull-only. A compositor would have to poll
nine gods every evaluation.

So "the framework READS loudness rather than computes it" is true as a design principle but has
no supplier. Someone must compute it. Two facts constrain who:

- `canon.yml` `in_front` rules that **engagement, positive or negative, makes a god louder**. So
  loudness is *not* satiation — it is closer to `|satiation|` (a wrathful god is loud), possibly
  combined with `GetMood`. That combination is a **campaign** judgement, not a framework one.
- But if the RUT-tier campaign pack computes it, then a RimMandrake-tier framework is reading
  from a campaign mod. That is fine *only* if the interface is a bare `(claimantId, float rank)`
  with no god semantics in it — which is what §2.4/§2.5 of the design doc already says. Keep it
  that way and the tier holds.

**Recommendation:** Ninefold gains a small owed API — `float Loudness(God)` and an
`Action<God,float>` change event — so the *derivation* of loudness lives with the pantheon that
defines it, and the *ordering* lives in the compositor. Ninefold stays campaign-agnostic
(RimMandrake tier) because the nine gods are already in it.

### 1.2 Canon's landing reckoning is not built anywhere.

`canon.yml` `in_front`: *"The front is reckoned at each **LANDING** … AND can shift MID-MAP on a
sufficiently violent engagement swing."*

Ninefold has **launch** hooks only — `Patch_GravshipLaunched.cs` patches
`CompLaunchable.TryLaunch` and `WorldComponent_GravshipController.InitiateTakeoff`, both
departures. There is no landing hook in Ninefold and no reckoning step. Ta'Baa's spike and
rooted-clock reset are the only launch consequences.

So the "reckoned at each landing" half of the front rule is **unbuilt**, and AtmosphericBase's
landing RESET has nothing to reset *to*.

### 1.3 `GravshipLanding` is the wrong mod for the landing hook.

`src/RimMandrake/GravshipLanding` is **94 lines total**. It ships one Harmony postfix on
`GenStep_GravshipMarker.Generate` that flood-unfogs the outdoors before landing
(`Patch_GenStep_GravshipMarker.cs`). A gen step runs only when a map is **generated**, so it
cannot see a gravship landing back on an already-generated map at all. It carries no landing
event, no notification, and nothing to hook.

**The landing hook already exists, in `src/RimMandrake/Visibility`.**
`ColonyVisibilityRaidPatch.cs:100-124` patches **both** `GravshipUtility.ArriveExistingMap`
**and** `GravshipUtility.ArriveNewMap` with one shared postfix
(`Postfix_ApplyTileMemoryOnArrival`), and comments that both resolve the destination through
`gravship.destinationTile`. That is the proven two-method pattern AtmosphericBase should copy
verbatim. `GravshipLanding` should be left alone.

### 1.4 The Narrator gesture cannot hang off Oracle, and Oracle has no gameplay call site.

`RequestOhmLetter` (`OracleGameComponent.cs:53`) has exactly **two** callers in the whole repo:

- `src/RimMandrake/Oracle/Source/DebugActions_Oracle.cs:43` — a **dev debug action**.
- `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchOracleTools.cs:143` — a bridge tool.

Neither is gameplay. There is **no** in-game path that produces an Oracle letter today, and the
one that exists is hard-wired to Ohm (`OracleRegisterBlocks.Ohm`, `TryValidateOhm`) — Ohm is a
*god*, not the Narrator. Canon (`narrator`) rules the Narrator is the **Cradle-Mind**, "not a
god", and in v1 **pre-authored letter prose**.

So hanging the white-rise gesture on Oracle would wire it to the one producer that will almost
never fire, and to the wrong speaker.

**Recommendation:** the Narrator gesture is triggered at the **letter** layer, not the LLM layer
— one authored trigger any producer can use (a `LetterDef` marking, a def-declared signal per
design §2.8, or an explicit `PlayNarratorGesture()` call). Oracle then becomes *one* optional
producer of that trigger, ranked with everything else. This also discharges the design doc's own
⚠️ ("his gesture must be triggerable by an authored letter, not only by an Oracle call") without
inventing a dependency on a mod whose kill switch defaults to **off** (`OracleSettings.enabled =
false`).

### 1.5 The Oracle transport rewrite is already done — CLAUDE.md is stale on this.

The project `CLAUDE.md` says the CLI ruling "Affects `ORACLE_EXPERIMENT_SPIKE_1` (client rewrite
owed)". Measured this pass: `OracleClient.cs` already shells out to `claude -p --output-format
text --system-prompt …` via `ProcessStartInfo` / `System.Diagnostics.Process` (lines 24, 143,
156), and `OracleSettings` already carries `claudeCliPath` with the HTTP fields gone and a
comment recording their removal. There is no `OracleHttpClient` in the tree. **The rewrite
landed.** Do not brief anyone to do it.

### 1.6 There is more already built here than the brief names — including a live event spine.

Three independent static event spines already exist in our own source:

| spine | file | reflection front door? |
|---|---|---|
| `ChronicleEvents` | `src/RimMandrake/Aftermath/Source/ChronicleEvents.cs` | ✅ `Subscribe(Action<object>)` / `Unsubscribe` |
| `PropertyEvents` | `src/RimMandrake/RimProperty/Source/PropertyEvents.cs` | ❌ typed events only |
| `BeastWakeRequested` | `src/RimMandrake/EnvironmentalHazards/Source/RM_CompWorkedLottery.cs:90` | ❌ typed |

`ChronicleEvents` is the one that matters: it is a **working, documented, per-handler-isolated
soft-hook bus** with a reflection front door specifically so a consumer needs no assembly
reference. `RimMandrake.Ninefold.ChronicleSubscriber` and
`RimMandrake.Aftermath.NinefoldBandBridge` are two proven, opposite-direction bindings against
it. **AtmosphericBase should not invent a fourth bus.** Its code door subscribes to
`ChronicleEvents` for world events and exposes its own claim API for pushes.

---

## §2 What the framework owes every consumer

Derived by reading what each mod below would actually need. Five surfaces, and nothing here is
optional:

1. **`RegisterGroup(name, membership) / ReleaseGroup`** — else no consumer can name territory.
2. **`PushMood(claimantId, group, scheme, rank) / ReleaseMood`** — indefinite, replaceable.
3. **`PlayGesture(claimantId, group, scheme, duration)`** — finite, restoring; the Narrator's
   variant is rank-∞ (L12).
4. **`PlaySting(soundDefName, position | group)`** — the sound channel's one-shot.
5. **`WasWitnessed(eventHandle) -> bool`** — the L14 gate, queried *after* the fact.

Plus one non-API obligation that every consumer depends on and nobody owns yet: **the framework
must tell a consumer that a rank changed**, or every consumer polls. Given §1.1, the cleanest
shape is that the *rank supplier* pushes and the framework never polls anything.

---

## §3 The ranked hook list

Ranked strictly by **does the living-Utinni dream fail without this hook**.

| # | mod | tier | pushes | hook cost |
|---|---|---|---|---|
| 1 | **`RimMandrake/Ninefold`** | 🔴 dream dies | loudness → rank; nine moods; first-contact gestures | **large** — new read API + change event + landing reckoning |
| 2 | **the Utinni emitter + signature pack** (NEW, RUT) | 🔴 dream dies | group registration (Shrine/Rooms/internal/external); the nine schemes; the omen looks | **large** — new mod, and the ship has almost no fixtures (§4.2) |
| 3 | **a Narrator channel** (NEW, or a letter convention in AtmosphericBase) | 🔴 dream dies | the white rise / hold / slow dim, at rank ∞ | **medium** — trigger has no owner today (§1.4) |
| 4 | **`RimMandrake/Aftermath` + `RimUtinni/AftermathRites`** | 🟠 hollow | omen gestures on `chronicle.rule.queued`; per-god omen palettes | **small** — subscribe to a spine that already exists |
| 5 | **landing RESET** — copy `Visibility`'s arrival patch | 🟠 hollow | the reset itself | **small** — two `harmony.Patch` calls, pattern proven |
| 6 | **`RimUtinni/Rites`** | 🟡 poorer | a gesture per rite tier; "The Gods Speak Back" is the payoff beat | **small** — research-completed signal |
| 7 | **`RimMandrake/Visibility`** | 🟡 poorer | a mood on the `Exposed` band — the ship knows it is seen | **small** — `BandFor`/`Notify_BandCrossed` exist |
| 8 | **`RimUtinni/RustCathedralHum`** | 🟡 poorer | **nothing — do not touch it.** Accepted overlap; mitigation is a volume slider in *our* settings | **zero** |
| 9 | **stings: `Pits`, `WreckedMachines`, `Graffiti`, `ShipVermin`, `ProximityHatch`** | 🟢 flavour | one-shot stings at a shock beat | **tiny each** |
| 10 | **`RimMandrake/RaidRedesigner`** | — | **nothing, by ruling.** It *is* the other half of L2 | **zero** |

**The single mod the dream most depends on is `Ninefold`.** Territory, tremor, the front, the
cap of three and the whole compositor are *defined in terms of rank*, and Ninefold is the only
thing in the repo that could ever supply it. Everything else in this table degrades to "less
beautiful"; without rank the compositor has no input and step 2 of §2.6 cannot run.

⚠️ **The single largest build risk is not #1, it is #2** — see §4.2. Rank is a week of C#. A
canvas is a ship rebuild.

---

## §4 The cards

### 4.1 `src/RimMandrake/Ninefold` — the rank source 🔴

**What it does today.** 2093 lines across 25 files. A `GameComponent` holding two `float[9]`
vectors (satiation, mood), a per-hour random-walk on mood, Ta'Baa's rooted erosion, a
first-contact queue with nine authored letter chains (`FirstContactCorpus.cs`, seven wired —
Ishko and Oomo have no event hook), and **eighteen** Harmony patch files binding real game seams
(battle, art, birth, construction, repair, fire, marriage, mental break, downing, capture,
research, trade, droid online, explosion, faction joined, kill manner, launch). A
`ChronicleSubscriber` that soft-binds to Aftermath's spine by reflection.

**What it would push.**
- A **rank per god** (see §1.1 — owed).
- A **mood claim per god** whenever rank order changes: top two get territory, 3rd+ become
  tremor. Nine claims live, permanently, is the steady state.
- A **gesture on first contact** — `FireFirstContact` (line ~236) is the single choke point;
  every unveiling already funnels through it, so one call there gestures all nine.
- A **gesture on a violent swing** — canon's mid-map front flip. `ApplyDelta` is the single
  choke point for all eighteen hooks, so a "swing exceeded threshold" gesture is one `if` in one
  method.

**What it needs from the framework.** Group names it did not choose (the campaign registers
those), and `WasWitnessed` before any letter says "you saw".

**Hook cost: large.** Not because the calls are hard — because three things are owed:
1. `Loudness(God)` + a change event (§1.1).
2. A **landing reckoning** (§1.2) — currently absent.
3. 🔑 **A save-format hazard.** `God.cs`'s own header records
   `NINEFOLD_ENUM_ORDER_SAVE_TRAP_1`: the enum's declaration order is a save contract, because
   satiation/mood scribe as a plain `List<float>` indexed by ordinal, and `FromLists()`'s only
   guard is `Count`. If AtmosphericBase ever persists a claimant id as a god **ordinal**, it
   inherits the same trap. **Claimant ids must be strings**, and the framework must never
   round-trip an ordinal.

⚠️ Also note `EventMagnitude.cs`, `MoodAmplitude`, `RootedErosionPerHour` are all explicitly
flagged `🔴 UNTUNED — a first-pass ordering only`, with tuning deferred to a rig that does not
exist. **Rank derived from these numbers will be wrong in a way that shows** — the front will
flip on the wrong events. The Mod Settings sliders (`eventMagnitudeMultiplier`,
`moodWalkMultiplier`) are the acknowledged stopgap.

### 4.2 The Utinni emitter + signature pack — NEW 🔴

This does not exist, and it is the hook the design doc's §6 table lists as "the Utinni scenario
layer". It owns three things the framework refuses to own:

- **Group registration**: Shrine, Rooms, internal, external (owner-ruled).
- **The nine god signatures** — hue *and* motion per god. Design §10 item 1: an owner sitting.
- **The omen looks** — per-god, matched to the eight `RM_AftermathRule_*` defs.

🔴 **The measured problem: there is no canvas.** The newest exported ship layout,
`design/Jawa/worldbuilding/ship_build/exported/Gravship_v2_ring_2026-09-12.xml`, holds **2002**
placed things across 57 unique defs. Of those, the light-bearing ones are:

```
5  AncientLamp
6  Brazier          (fire, not an electric glow)
```

Against `658 HiddenConduit`, `553 VGE_AstrofuelPipe`, `505 GravshipHull`. **Five lamps is not a
tapestry.** The take-over-button ruling ("it will take over nearly any wall light, lighting
furniture, floor lighting") assumes fixtures the player built; on the shipped Utinni there are
almost none, and the campaign ships the ship as a savegame, so the player does not build it.

Two consequences, both owed to the owner rather than decidable here:
1. Either the ship build places 40–100+ light fixtures as a deliberate act, or the Utinni's
   ambient light channel is a handful of lamps and the tapestry is a claim the game cannot cash.
2. `AncientLamp`'s glow settability is `UNMEASURED — owed a Desktop check`. Only one
   colour-adjustable fixture exists anywhere in *our* source
   (`src/RimStarWars/Armoury/Defs/Absorbed_KotorCore/ThingDefs_Buildings/Absorbed_KotorCore_Lights.xml`,
   `GS_ImperialLamp`, with `<colorPickerEnabled>true</colorPickerEnabled>`) — and that file's own
   header says **do not deploy it** while the source pack `guy762.MM.KotORCore` stays active, so
   we do not even ship it today.

**Hook cost: large** — a new RUT-tier mod, plus a ship-build pass, plus an owner sitting.

### 4.3 A Narrator channel — NEW (or a convention) 🔴

See §1.4. The gesture is the owner's own image and is the most legible thing the whole framework
will ever do — a rise to bright white, held while he speaks, then a slow dim back. L11 reserves
white for it and L12 ranks it above a live raid alarm.

**What it pushes:** exactly one gesture kind, at rank ∞, with a duration bound to how long the
letter is on screen.

**What it needs:** L10 — the gesture must run **while the game is paused**, because a letter
pauses the game. That is design §8 question 1 and it is the one `UNMEASURED` item that can kill a
law outright. If no per-frame hook survives a pause, the Narrator's signature freezes at the
exact moment it exists for.

**Hook cost: medium** — the trigger has no owner. Recommend AtmosphericBase itself ship the
letter-side convention (a `LetterDef` marking, or a def-declared signal per §2.8) so no new mod
is needed and Oracle becomes optional.

### 4.4 `src/RimMandrake/Aftermath` + `src/RimUtinni/AftermathRites` — the omens 🟠

**What exists.** Aftermath is the Chronicle engine: a battle recorder, an outcome classifier,
eight rules in `RM_AftermathRuleDefs.xml`, and the `ChronicleEvents` spine (§1.6). Each rule
matches a closed battle, **sends a telegraph letter now**, and queues its payload incident
`delayDaysMin..Max` later. Measured spread across the eight rules: **0 to 12 days** (the
Rooted Receipt is `0..0`; the Reckoning is `5..12`).

That delay window **is** the omen lead time — and it is why this hook is load-bearing. The owner
cut the omen-warning line from a checklist and moved the burden onto the lights
(`REACTIVE_SHIP_LIGHTING_1`, `infrastructure/state/queue/BENCH.md:425`). So the lights are now
the *only* thing making an omen distinct.

**What it would push.** One **gesture** at `chronicle.rule.queued` (already published, already
carries `godTie` + `godDelta` as plain string+float on the rule def), then optionally a **held
mood** for the lead window so the omen *persists* rather than flashing once.

**Hook cost: small.** Copy `Ninefold/Source/ChronicleSubscriber.cs` almost verbatim: probe
`RimMandrake.Chronicle.ChronicleEvents` then `RimMandrake.Aftermath.ChronicleEvents` (the rename
is still gated), `Subscribe(Action<object>)`, read `Kind`/`Outcome`/`Payload` by field name.
Zero assembly references either way.

**The two open defects, both verified this pass:**

- `AFTERMATH_DEAD_LETTERS_1` — `letterLabel`/`letterText` are declared at
  `RM_AftermathRuleDef.cs:56-57` and **read nowhere**. All 8 rules author a letter the player
  never sees. The only `ReceiveLetter` is `AftermathRuleRunner.cs:337`, the telegraph, and it
  hardcodes `LetterDefOf.ThreatBig` — so **every omen arrives identically** in the letter
  channel. That is precisely the undifferentiation the lights are being asked to fix.
  🔑 **This is an argument for doing the light hook regardless of whether the letters are
  fixed** — and an argument against *only* doing the lights, since a `ThreatBig` on every omen
  actively fights the distinction the gestures are trying to draw.
- `AFTERMATH_TELEGRAPH_REFERENT_1` — `RM_AftermathRule_AlliesArrive`'s one substitution slot has
  two referents; `SendTelegraph` formats with the **ally** while `telegraphText` means the
  **defeated faction**. A light omen carrying god identity via `godTie` sidesteps the bug
  entirely (7 of 8 rules carry `godTie`), which is a small point in the hook's favour.

### 4.5 The landing RESET 🟠

**Not `GravshipLanding` (§1.3).** Patch `GravshipUtility.ArriveExistingMap` **and**
`GravshipUtility.ArriveNewMap`, exactly as `Visibility/Source/ColonyVisibilityRaidPatch.cs:100-124`
already does, with one shared postfix. Reset = release every claim, clear the witness ledger,
drop to the shipped default scheme, and wait for the campaign to push the new front.

Two cautions:
- The reset must be **idempotent** and safe on either arrival path; a landing back onto a map
  that already holds claims goes through `ArriveExistingMap`, which the gen-step route never
  sees.
- Design §8 question 6 asks what happens to lights and sustainers during **flight**. Since
  landing is a reset and nothing carries across, the honest answer is that flight needs no
  handling — but that is an inference, and it is `UNMEASURED — owed a Desktop check`.

### 4.6 `src/RimUtinni/Rites` 🟡

Five `ResearchProjectDef`s, revealed not bought: Scrap Shrine → Conduit Choir → God-Speaker
Array → Liturgy of the Hull → **The Gods Speak Back**, each gated on an `Antiquities` stage
(`RUT_Rites_Research.xml:33+`). This is the campaign's own ladder toward the gods becoming
audible — the natural place for the framework to escalate what it is allowed to do.

**Pushes:** a gesture per tier completion, and plausibly a *capability gate* — the tremor, or
acoustic territory, or the Narrator's voice, unlocking as the liturgy advances. **Cost: small**
(research-completed is already a patched seam in Ninefold: `Patch_ResearchCompleted.cs`).

Note the Shrine group has the same canvas problem as §4.2: `RUT_Rites_ScrapShrine` is a
*research project*, not a building. No `Shrine` ThingDef exists in our source
(`RUT_OasisShrine` is a `TileMutatorDef`, a world landmark, not aboard).

### 4.7 `src/RimMandrake/Visibility` 🟡

Not in the brief, and it belongs. A scribed 0–100 dial with a five-band ladder
(`Hidden/Discreet/Noticed/Marked/Exposed`, `GameComponent_ColonyVisibility.cs:78`), an
`Adjust(delta, reason)` write door (line 94), tile memory across launches, and an already-wired
`Notify_BandCrossed` that the file itself documents as *"deliberately inert until"* someone
builds the letter layer.

**Pushes:** a low-rank mood on `Marked`/`Exposed` — the ship registering that it is being
watched. This is exactly the kind of second, non-god claimant that proves the framework is a
framework rather than a Ninefold appendage. **Cost: small**, and `Notify_BandCrossed` is a
ready-made trigger point that currently does nothing.

### 4.8 `src/RimUtinni/RustCathedralHum` — do not touch 🟡

Verified: `RM_MapComponent_BiomeAttitude.cs` (410 lines) keeps a float `irritation` that events
bump and time decays, computes a 0..N band from `irritation - goodwill*weight` with
de-escalation hysteresis, clamps it to the active stage's ceiling, and drives
`SyncSustainers(def, displayBand)` over a `List<Sustainer> activeSustainers` — deliberately not
scribed, because a Sustainer is a live audio handle. Three layers in
`Defs/SoundDefs/RUT_HumLayers.xml`. `GetBand(Map)` is public and static (line 134). Zero
sustainers at the worst band is the survival tell: *"when the hum drops, stop moving."*

**This is a fully working second implementation of AtmosphericBase's bed layer** — band → layered
sustainer count, with hysteresis, with a mod-settings decay multiplier, with a bridge tool
(`JawaBenchCathedralAttitudeTools.cs`). The owner ruled 2026-09-16 to leave it alone.

**The accepted overlap, stated plainly:** aboard a ship in that biome, both systems drive
looping sustainers at once, with no shared mixer and no mutual awareness. Two independent
ambient beds can beat against each other, and neither ducks for the other.

**Player-facing mitigation** (the only sanctioned fix — a settings control in *our* mod, never a
refactor of theirs):
1. A **bed volume slider** for AtmosphericBase's own beds, so a player who prefers the cathedral
   hum can push ours down without turning either off.
2. A **bed on/off** independent of the light channel, so the whole sound channel can be dropped
   while the tapestry keeps running.
3. Naming that makes the choice legible in the UI — the labels must say which hum is which, or
   the slider is undiscoverable.
4. ⚠️ Its `GetBand(Map)` is public, so a *future* consumer could push a mood off the cathedral
   band into AtmosphericBase. That would give one coherent output, and it needs **no change to
   the hum mod** — the read is already there. Not proposed; recorded as the exit that exists if
   the beat becomes intolerable.

⚠️ One stale claim inside that mod, worth deleting when someone next edits it: `RUT_HumLayers.xml`
says *"No audio pipeline exists anywhere in this repo (no prior mod ships a custom .ogg/.wav;
confirmed by search before writing this file)."* **Measured 2026-09-16: 1048 audio files under
`src/`**, including `Absorbed_KotorCore_BuildingSounds_ShipAmbience.xml` (6 ship-ambience
sustainer defs: `kotorsound_ShipAmbience_ActionVI`, `_YT1300transport`, `_RaiderCorvette`,
`_CROCGozanti`, `_ImpGozanti`, `_CivGozanti`), plus door, generator, telemetry and
random-ambience banks in the same folder. The three hum layers are placeholders pointing at
vanilla mechanoid clips **that did not need to be**.

### 4.9 Stings — `Pits`, `WreckedMachines`, `Graffiti`, `ShipVermin`, `ProximityHatch` 🟢

Each owns a shock beat that is the sound channel's reason to have one-shots: a pit trap
springing, a machine waking, an ambush hatch forcing an early hatch on proximity. **Cost: tiny**
— one `PlaySting` at an existing choke point.

⛔ `Pits`, `Graffiti` and `WreckedMachines` are **VALIDATED north stars**. Do not edit their
`## north star` sections — the recorded hash covers the whole section including prose, so a
one-word fix silently reverts the checklist to DRAFT. A sting hook is a code change, not a
north-star change; keep them apart in separate commits.

### 4.10 `src/RimMandrake/RaidRedesigner` — pushes nothing, on purpose

**What it is.** Ships **only** `GameComponent_OldFriends`: a scribed roster of `OldFriendEntry`
records capped at 24 living entries, with eight Harmony postfixes writing one `Encounter` each at
real seams (raider fleeing, captain leaving, prisoner escaping/released, caravan robbed via
`RimProperty`'s `TakingEvent`, colonist kidnapped, Blackstar guest-status). A ninth is an
honest stub. **No LLM, no letter rewrite, no defs, no raid pipeline changes** — its own About
says the redesign layer proper is explicitly out.

**The boundary, from the owner's own words (L2):** *"the gods that would scream and attract
attention WILL affect raids directly independent of these lights (don't act through the lights,
act directly on the world)."*

So the boundary is not a coordination problem, it is a **prohibition**, and it runs one way:

- ✅ A god that wants raiders calls **`Visibility.Adjust()`** or a raid-pipeline lever — a real
  world mutation with a real consequence.
- ⛔ A god must **never** get raiders *by* running a scheme, and AtmosphericBase must expose no
  API that could be read as "make this dangerous". A claim carries a look and nothing else.
- ✅ Both may happen at once for the same reason. A screaming god turns the corridors red *and*
  raises visibility — but the red corridors caused nothing. The single test: **delete the light
  channel and the raid still arrives, unchanged.** If it does not, L2 is broken.
- ⛔ The inverse is equally forbidden: RaidRedesigner must not read the compositor to decide
  anything. That would make look load-bearing through the back door.

The practical upshot: `RaidRedesigner` needs **no hook at all**, and its `OldFriendEntry` roster
is a *narrative* asset a Narrator gesture might reference (a returning grudge-holder) — but only
through the letter layer, never through the lights, and only past `WasWitnessed`.

---

## §5 Already built that we would be duplicating

Worth knowing before a line of C# is written:

| already built | where | what AtmosphericBase would duplicate |
|---|---|---|
| **band → layered sustainer count**, with hysteresis, stage ceiling, settings multiplier, bridge tool | `RustCathedralHum/Source/RM_MapComponent_BiomeAttitude.cs` | the **entire bed layer**, by ruling |
| **a soft-hook event bus** with a reflection front door and per-handler isolation | `Aftermath/Source/ChronicleEvents.cs` | a fourth event bus, if we invent one — **don't** |
| **reading another mod's state by reflection**, cached, warn-once, absent-safe | `Aftermath/Source/NinefoldBandBridge.cs` and `Ninefold/Source/ChronicleSubscriber.cs` | the whole soft-binding idiom — copy it, don't redesign it |
| **the gravship arrival hook**, both methods | `Visibility/Source/ColonyVisibilityRaidPatch.cs:100-124` | landing detection |
| **hushing biome ambient sustainers and restoring them** | `CreatureBehaviors/Source/RM_MapComponent_SilenceCue.cs` | ⚠️ see below |
| **a quantised-pulse tint that skips the dirty call on most ticks** | `UtinniPatches/Source/TwinkleFloraSpike.cs` (`TWINKLE_FLORA_SPIKE_1`) | the cost model of §2.6 step 6 |
| **1048 audio files**, incl. 6 ship-ambience sustainer defs | `src/`, mostly `Armoury/Defs/Absorbed_KotorCore/SoundDefs/` | commissioning audio for the first pass |

⚠️ **`RM_MapComponent_SilenceCue` is a live conflict, not just a precedent.** It ends this map's
`Biome.soundsAmbient` sustainers outright for a window when a silence-aura predator hunts near a
colonist, then lets `AmbientSoundManager`'s own recreation route bring them back. Its own header
records that neither `Sustainer` nor `SustainerManager` exposes a partial volume ramp (*verified
against source on the Desktop*). Two consequences:
1. **AtmosphericBase's beds cannot fade.** If the same limitation holds for our sustainers, a
   bed change is a hard stop/start and *may pop audibly* — a trade `SilenceCue` already accepts.
   L8's "sound is what survives the blackout" needs this to be true or the blackout announces
   itself with a click. `UNMEASURED — owed a Desktop check`.
2. **A hush and a bed claim can fight.** If a silence cue fires while a god holds acoustic
   territory, who wins is undefined. Worth one line in the compositor spec.

---

## §6 New mods and actuators that must exist

| thing | exists? | notes |
|---|---|---|
| **AtmosphericBase** itself | ❌ | `REACTIVE_SHIP_LIGHTING_1` (BENCH.md:425) is the filed item |
| **the Utinni signature/group pack** (RUT) | ❌ | §4.2. The biggest single piece of new work |
| **a Narrator trigger** | ❌ | §1.4. Recommend a convention in AtmosphericBase, not a new mod |
| **light fixtures aboard the Utinni** | ❌ (5 lamps) | §4.2. A ship-build pass, not a code pass |
| **`Loudness` + change event on Ninefold** | ❌ | §1.1 |
| **a landing reckoning of the front** | ❌ | §1.2 — canon rules it; nothing implements it |
| **doors as an actuator** | ⚠️ | `jecrell.doorsexpanded` is in the 2026-09-13 snapshot, but backup filenames record a retire attempt on 09-09/09-10 (`ModsConfig_before_doorsexpanded_retire_2026-09-10.xml`). **Live state `UNMEASURED — owed a Desktop check`.** No door actuator exists in our source. Canon's "door hesitations" needs a `Building_Door` open-delay hook nobody has written |
| **subsystem behavior as an actuator** | ❌ | Canon names it (`in_front`). Nothing in `src/` touches it. Entirely new |
| **holo-emitters** | ❌ | Canon defers them: *"the hologram room is NOT there at the beginning… when the Jawa get droids, they will start to 'receive visions' and build some of the first holo-emitters when resources are present."* So they are gated behind droids + `Rites`, and are **correctly out of scope**. Note L8/§2.1 also *excludes* holograms from take-over — they are the reference light that proves a chosen blackout, so a future holo actuator must not eat that exclusion |
| **a bridge tool for AtmosphericBase** | ❌ | Precedent: `JawaBenchCathedralAttitudeTools.cs`. Needed to test any of this without a 15-minute cold load |

---

## §7 Third-party mods this collides with

Not in the brief, and every one is a real risk. From the 2026-09-13 snapshot (599 entries) and
`design/RimMandrake/music_protocol.md`, which audited the audio layer on 2026-08-11.

**Sound — four mods already own ambience:**

- `swablu.ambience` (**Ambient Rim**) — *"aggregates sustainers into environmental loops."* The
  closest thing to a direct competitor for the bed layer.
- `neronix17.outerrim.core` (**Outer Rim – Core**) — *"ship/interior ambience."* Aboard the
  Utinni this is playing over the same hull.
- `dorbo.watersfx` (**LiquidSFX**) — water ambience by proximity. A *positional* ambient
  precedent, which is what acoustic territory is.
- `depscian.rimtunes` — **replaces the vanilla music manager entirely**, and
  `music_protocol.md` measured its dynamic mode already **on** (`enableDMS: True`) with an empty
  data folder. So a dynamic soundtrack is already reacting to events, unauthored. Stings landing
  under a DMS cue is `UNMEASURED — owed a Desktop check`.

So the bed layer arrives into a hull that already has **at least three** ambient systems in it
plus a dynamic music manager, and `RustCathedralHum` makes four. That is the strongest available
argument for §4.8's volume slider being a shipped requirement rather than a nicety.

**Light — four static sources, one darkness mod, one power saver:**

`zav.glowstoneforked` · `temeez.floorlights2` · `noneobsidiaexpansion.ledlightsstrip` ·
`zylle.nightlights` · `fourtoo.glowingbush` · `dark.signs` · `dawnsglow.qualcolor` ·
`wemd.realisticdarknesslight` · `juanlopez2008.lightsout`

🔴 **`juanlopez2008.lightsout` is a direct antagonist.** It is a power-saver that switches lights
off — so it will be turning off, on its own schedule, the exact fixtures the compositor is
driving. Whichever writes last wins, and the loser's state is invisible. This is not a
theoretical conflict: it is two mods writing the same field on the same tick, and it can make
L8 unprovable (a scheme's chosen black becomes indistinguishable from `lightsout` doing its job).
**Owed:** a Desktop check of whether it patches `CompGlower`/`CompPowerTrader`, and a decision —
detect and refuse to take over a fixture it manages, or ask the owner to retire it.

`wemd.realisticdarknesslight` matters for the opposite reason: it changes what darkness *looks*
like, which is the medium L8 is written against.

And design §8 question 4 — whether 1.6 vanilla supports coloured light at all, or whether it
comes only from these mods — is answered by exactly one data point in our own source:
`CompProperties_Glower` carrying `<colorPickerEnabled>true</colorPickerEnabled>` and
`<darklightToggle>true</darklightToggle>` on `GS_ImperialLamp`. That is a **vanilla 1.6 comp
field on an absorbed def**, which suggests vanilla owns the colour picker — but the def came from
a third-party pack, so it is evidence, not proof. `UNMEASURED — owed a Desktop check`.

---

## §8 What I would push back on

1. 🔴 **"Ninefold is the loudness source" is aspirational, not descriptive.** It has no loudness,
   no rank, no ordering and no change notification (§1.1). Say "Ninefold is *owed* a loudness
   API" in §2.5, or the next agent will brief a subagent to "just read the rank" and lose a run.
2. 🔴 **The dream has no canvas.** Five `AncientLamp` on the newest exported ship (§4.2). The
   take-over ruling presumes fixtures a player built, and the Utinni ships as a frozen savegame.
   Either the ship build places lights deliberately or the tapestry is unbuildable. This belongs
   in §8 of the design doc as an owed item, not buried in a hook list.
3. 🔴 **The witness ledger makes the best gesture unwitnessable.** L14 + §2.7 define a witness as
   *an awake colonist in a **lit** affected room*. L8's full black is the most dramatic thing the
   framework can do — and by that definition it is **never** witnessed, so a god may never refer
   to it. The two laws contradict each other at exactly the moment they matter most. Needs
   either a carve-out (a chosen darkness counts as lit-for-witness because the writhe is visible)
   or an explicit acceptance that the blackout is a thing the gods can never mention.
4. 🟠 **Canon says the silent EIGHT express; L6 caps the tremor at three.** `in_front`:
   *"The silent eight express through ambient micro-gestures."* L6/§2.6 step 3 caps tremor
   contributions at three. That is a narrowing of a ruled canon line and it should be recorded as
   an **amendment**, not left as an implicit contradiction — the repo's own rule is that
   inaccurate material is deleted, not superseded in place. Design §10 item 3 ("what the cap of
   three selects on") is downstream of this and cannot be answered first.
5. 🟠 **The Narrator gesture is hung on the wrong mod, and that mod's kill switch defaults off**
   (§1.4). `OracleSettings.enabled = false`. Wire the gesture to the letter layer.
6. 🟠 **`GravshipLanding` cannot deliver the landing RESET** (§1.3). It is a 94-line fog patch on
   a gen step. §6 of the design doc lists it as the landing hook; that will send someone to the
   wrong file. `Visibility` has the working pattern.
7. 🟠 **Canon's landing reckoning does not exist** (§1.2). "Landing is a RESET, no persistence
   machinery is owed" is only true because there is nothing to persist *yet* — the moment the
   reckoning is built, the reset acquires a real ordering dependency on it. Say so now.
8. 🟡 **`lightsout` will fight the compositor** (§7) and can make L8 unprovable. This is a
   two-writers-one-field conflict, and it is the kind that produces a bug report six weeks later
   phrased as "the lights are flickering wrong".
9. 🟡 **Beds may not be able to fade** (§5). `RM_MapComponent_SilenceCue`'s header records, from
   a Desktop-verified source read, that no partial volume ramp exists on `Sustainer` or
   `SustainerManager`. If that holds, every bed transition is a hard stop/start that may pop —
   and L8's "sound survives the blackout" gets announced by a click. This belongs in §8 of the
   design doc as an eighth question.
10. 🟡 **The bed layer lands into four existing ambient systems**, not one (§7). §3's "accepted
    overlap" names only `RustCathedralHum`. The real overlap is `RustCathedralHum` +
    `swablu.ambience` + `neronix17.outerrim.core` + `dorbo.watersfx`, under a music manager whose
    dynamic mode is already on. The volume slider is therefore a **requirement**, and one slider
    may not be enough.
11. 🟡 **Don't invent a fourth event bus.** `ChronicleEvents` already is one, with a reflection
    front door and two proven bindings (§1.6). §2.8's "code door" should be *subscribe to the
    spine + expose a claim API*, stated explicitly, or someone will write a fifth.
12. 🟢 **Claimant ids must be strings, never god ordinals** (§4.1). `NINEFOLD_ENUM_ORDER_SAVE_TRAP_1`
    is a live save-format trap and a persisted ordinal inherits it.

---

## §9 UNMEASURED register — owed a Desktop check

Beyond design §8's seven. None of these was guessed at here.

| # | question | why it matters |
|---|---|---|
| A | Is `jecrell.doorsexpanded` in the **live** `ModsConfig.xml`? | Whether canon's door actuator has any hardware; the backups record a retire attempt |
| B | Does `juanlopez2008.lightsout` patch `CompGlower` or `CompPowerTrader`? | §7 — whether it can overwrite the compositor, and whether L8 is provable |
| C | Can `AncientLamp`'s glow colour be set at runtime? | It is 5 of the 6 light-bearing things on the shipped ship |
| D | Does vanilla 1.6 own `colorPickerEnabled`, or does a mod add it? | Design §8 q4; our only evidence is one absorbed def we do not deploy |
| E | Do `Sustainer`/`SustainerManager` still lack a partial volume ramp in 1.6? | §5 — whether beds can fade or must pop |
| F | Do `swablu.ambience` / `neronix17.outerrim.core` / `depscian.rimtunes` duck for anything? | Whether four ambient systems can coexist audibly |
| G | Live active mod count and whether `guy762.MM.KotORCore` is still active | Whether `GS_ImperialLamp` (our only colour-adjustable fixture) is deployable |
| H | What a hush from `RM_MapComponent_SilenceCue` does to a framework-owned bed | An undefined interaction between two of our own mods |
