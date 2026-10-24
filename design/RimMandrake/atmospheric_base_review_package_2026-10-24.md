# AtmosphericBase: review package (2026-10-24)

This package is for an outside reviewer (GPT), who should review it, extend it and debug it. After that it
goes back to the owner as question cards. The package is self-contained. Every claim gives a `file:line`, a
measured number, or the word **inference**. Repo paths are relative to the repo root. The owner's mirror is
`D:\Luke\dev\RimMandrake\`.

The owner's request, verbatim: *"Package up the whole atmospheric base mod tests and definition and improve its
definition, conceptual execution, and three suggestions on superior implementation including efficiency,
aesthetic appearance, and novelty. Then send it to GPT for review enhancement debugging and further expansion.
Then return it to me for question cards with evidence and pros and cons."*

## 0. Sources, and what this package cannot know

| what | where |
|---|---|
| spec, 17 laws L1-L17 | `design/RimMandrake/atmospheric_base_mod_definition.md` (635 lines; laws at :39-121) |
| scheme catalog (DRAFT, 7 families) | `design/RimMandrake/atmospheric_base_scheme_catalog.md` (622 lines) |
| build programme, Phases 0-10, Phase 0 engine answers | `infrastructure/state/items/ATMOSPHERIC_BASE_BUILD_PROGRAM_1.md` (321 lines) |
| north-star walk (DRAFT, stopped by the owner 2026-09-17) | `design/validation_walks/RimMandrake/AtmosphericBase.md` (345 lines) |
| proof plan | `design/RimMandrake/atmospheric_base_proof_plan_2026-10-23.md` (140 lines) |
| code | `src/RimMandrake/AtmosphericBase/Source/` (11 .cs plus `Kernel/` 3 .cs), `Defs/RM_AtmosphericSchemes.xml` |
| tests | `Source/SelfTest/Program.cs`, `selftest_atmosphericbase.py`, `selftest_atmosphericbase_kernel.py`, `validation.py`, `proof_atmosphere.py` |

The mod has **never run live**. Every result below is either offline (a stub bridge, kernel selftests, or
reading the code) or a structural read of decompiled engine code. No millisecond figure exists for any part of
this mod. The newest offline proof, `D:\ClaudeWork\rimmandrake\scratch\proof_atmosphere\proof_atmosphere_offline_20261023T202928.json`,
holds two rows. P1 (`hook_in_source`) passes. D1 (`default_gentle_disk`) passes: flashers 0, never dark, no
white anywhere.

> **Owner ruling, 2026-10-24:** *"Do not plan for colorblind or photosensitive at all. Maximize aesthetics."* No
> accessibility or flash-rate accommodation is designed or tested; GPT's accessibility findings (review file) are
> void. Gentle-by-default remains, as his 2026-09-16 taste ruling.

## 1. The mod in plain words, by phase

**The idea.** A ship's own light fixtures become a slow, shifting tapestry. On the Utinni, nine gods live in
the ship's wiring, and they show their moods through which lamps carry their colours and how those colours
move. Without the Utinni the patterns are simply beautiful: gentle by default and never a light show. A dark
room always holds a little motion, so a chosen dark never reads as a power cut. When the Narrator speaks, the
lights rise briefly to a reserved white and then dim back. Aboard the Utinni the gods choose the colours, never
the player.

| phase | state | what the player sees |
|---|---|---|
| 1 take-over | BUILT, not live | On any glowing building, a button reading "Let Atmospheric Base drive this glow", and "Take glow back" to undo it. Animals, gear, plants and holograms never get the button. Taking a light back restores its colour exactly. A light that is minified, moved or flown away goes back to its own colour. |
| 2 one mood | BUILT, not live | The handed-over lamps run "Lamplight". Each room's lamps step up and back through three warm ambers on a 120 s cycle, and each room runs on its own phase. Nothing else changes. |
| 3 territory | BUILT offline (31400b41ac), not deployed | When two consumers push moods, each holds a share of the lamps (60/40 by default). The boundary between the shares rotates around the ship's centre once every 900 s, with an 8% ragged edge. No colour is ever mixed. |
| 4 tremor | BUILT offline, not deployed | The third, fourth and fifth moods appear only as brief 0.8 s flickers in their own palettes. Each fixture gets one chance in four per 30 s slot, and at most 4% of the lamps flicker at once. |
| 5 gestures, Narrator, alarm | NOT BUILT | Planned: the Narrator rises to white in under a second, holds while the letter is open, then dims back over 4-8 s. The alarm is distinct from every mood. Every gesture restores what was under it. |
| 6 sound | NOT BUILT | Beds and stings, with acoustic territory, and the camera as the listener |
| 7 witness ledger | NOT BUILT | Nothing visible. It lets a god's letter refer only to things a colonist really saw. |
| 8 def hooks | NOT BUILT | An XML-only mod can bind a signal to a scheme, a group and a kind |
| 9 library, showcase | NOT BUILT | A showcase in Mod Settings that cycles the flagship schemes |
| 10 consumers | NOT BUILT | Ninefold supplies rank, Oracle the Narrator, Aftermath the omens, GravshipLanding the reset |

Shipped schemes (`Defs/RM_AtmosphericSchemes.xml`):

- **RM_Scheme_Lamplight** (RoomBreath, 120 s): (204,150,92), (224,168,104), (244,188,118).
- **RM_Scheme_Fireflies** (Sparks, 40 s): (210,158,94), (234,176,106), (255,196,120). Each spark lasts 2.5 s,
  and a fixture sparks in one slot of every two.

There is no dark scheme, no flasher scheme and no Narrator white.

## 2. As built against the spec

### 2.1 Built and matching the spec

- **Exclusions are checked first** (`Kernel/RM_AtmosphericKernel.cs:39-54`): pawns, plants, apparel and
  equipment, then holograms. That satisfies §2.1 and L16. A fixture that is not lit is never driven, because
  the compositor skips it when `!Glows` (`RM_AtmosphericCompositor.cs`, the driven loop at :205-214). That
  satisfies L9.
- **The pattern returns a palette index and never a colour** (`Kernel/RM_SchemeKernel.cs:110-144`).
  `RM_PaletteGuard` checks membership again at the write (`RM_MapComponent_AtmosphericBase.cs:126`). That
  satisfies L4 by construction.
- **Only changes are written.** `RM_ChangeTracker` (`RM_SchemeKernel.cs:193-216`) satisfies §2.6 step 6.
- **Real time.** The compositor reads `Time.realtimeSinceStartup` (`RM_AtmosphericCompositor.cs:164`) inside
  `MapComponentUpdate`, which runs while paused (Phase 0 Q1). That satisfies L10.
- **Rank is read, never computed.** `RankedMoods` sorts consumer-supplied ranks
  (`RM_MapComponent_AtmosphericBase.cs:186-199`), which satisfies §2.5.
- **The territory boundary is clamped.** The period is at least 240 s and the lead share lies between 0.5 and
  0.8 (`RM_TerritoryKernel.cs:40,71,112`). The tremor cap is 3 and its fraction is at most 0.10
  (`:194-195`). Both satisfy L5 and L6.
- **No Harmony, no def edits.** The per-thing buttons are reverse designators. `validation.py` checks this
  statically.

### 2.2 Not built

Not built: Phase 5 (L12, L13), the dark or writhe pattern that L8 needs, L17 anger, sound (§3), the witness
ledger (§2.7, L14), the def hook door (§2.8), the showcase (§5) and every consumer (§6). The API
(`RM_AtmosphericBaseAPI.cs`) offers PushMood, ReleaseMood, groups, TakeOver, Release, Showing and
SetScenarioDecides. It has **no gesture door and no witness door**. Two items block the work:
`ATMOSPHERIC_BASE_CANVAS_1` (the canvas has only 11 lights among 2002 things on `Gravship_v2_ring`, and the
anger threshold is not ruled) and `NINEFOLD_LOUDNESS_FRONT_1` (Ninefold has no loudness value to supply as
rank).

### 2.3 Where the code contradicts or under-delivers a law

| # | law | what the code does | evidence | severity |
|---|---|---|---|---|
| K1 | **L3** "elsewhere a gentle scheme runs from install" | The default mood drives only fixtures the player has handed over (`MapComponentUpdate` returns early when `taken.Count == 0`). A fresh install shows **nothing** until the player clicks lamps one at a time. | `RM_MapComponent_AtmosphericBase.cs:146` | High. The ruled opt-in button (§2.1) and L3 pull against each other, and the spec never says which wins. That is question Q1. |
| K2 | **L11** "no scheme may take [white] as a dominant colour" | The rule is enforced per palette entry only when **all three channels are at least 200**. A cream such as (255,240,199) passes, and a cool white such as (199,230,255) passes. "Dominant" is never assessed. | `RM_SchemeKernel.cs:43,58` | Medium. Today's palettes are amber and safe. The first god palette with a pale tint could read as the Narrator. |
| K3 | **L4/L2** taste: the default must be visible | The Lamplight entries sit within 2-40 of vanilla lamp amber in every channel; the low entry is within 10. Vanilla StandingLamp and WallLamp are **(214,148,94)** (Core `Buildings_Furniture.xml:1361,1471`). The repo labels (217,217,208) as "a vanilla standing lamp" in three places, but that value is the Royalty ethereal light (`Ethereal_Various.xml:144`). Filed as lesson `20261024T034106Z-FOUNDRY-atmos-substrate-not-vanilla-lamp`. | `Defs/RM_AtmosphericSchemes.xml:9`, `proof_atmosphere.py:880`, `SelfTest/Program.cs:452` | Medium. **Inference:** on vanilla lamps the gentle default may be hard to perceive, so it would look like nothing happened. The proof's stand-in substrate is near-white when the real one is amber. |
| K4 | **L7** "the framework chooses which fixtures play that role" | Flashers are the lowest `Mix(id,7)` hashes, with no spatial spread, so every flasher could land in one room. | `RM_SchemeKernel.cs:148-156` | Low today (no shipped scheme has flashers). Medium once alarms exist. |
| K5 | **L6** fairness | When the tremor exceeds its cap, the flickering fixtures with the lowest `Mix(id,23)` win at every instant. The same ids are always preferred whenever they flicker, regardless of which god is louder. | `RM_TerritoryKernel.cs:238-246` | Low. **Inference:** under heavy tremor the same few lamps would always twitch. |
| K6 | **L10** real time | Evaluation runs every 6 **frames** (`:75,157`), so the rate is fps/6: 5 Hz at 30 fps and 24 Hz at 144 fps. The pattern itself is a function of real time. Only its sampling depends on fps, so a 0.8 s flicker gets 4 samples at 30 fps. | `RM_AtmosphericCompositor.cs:75,157` | Low. Visible only for fast elements such as flashers, tremor and the planned Narrator rise. |
| K7 | cost (§2.6) | `Drive` calls `IsTaken`, which is a linear scan of `taken` for every write, so the cost is O(writes x taken). Each evaluation allocates new `List`s (driven, union, tremor, sources, members) and builds a string key. `drivenIds` is built and never read. | `RM_MapComponent_AtmosphericBase.cs:64-75,125`, `RM_AtmosphericCompositor.cs:205,218,230,253-261,275,279` | Low at 11 fixtures. **Inference:** about 5-10 KB of garbage per evaluation at 200 fixtures, or about 50-100 KB/s at 60 fps. Not measured. |
| K8 | §2.1 hologram exclusion | The check is the `RM_AtmosphericExcluded` extension **or** the substring "holo" in the defName or thingClass. The selftest proves that "Hollow" is not "holo". | `RM_AtmosphericKernel.cs:39-54` | Low. A hologram def without "holo" in its name and without the extension would be driven. The campaign's god holograms must carry the extension, and nothing enforces that. |
| K9 | §2.6 territory shape | The boundary is a wedge in bearing order around the centroid of the union. **Inference:** on a ring ship it reads as a clock hand sweeping round, which is mechanical rather than "areas that slowly move throughout the ship" (canon `in_front`). | `RM_TerritoryKernel.cs:141` | Aesthetic. Section 6, proposal A. |

### 2.4 Documents that disagree with each other

- The programme and queue say "15 laws". The spec has **17** (L16 and L17 were added on 2026-09-17,
  definition:578-583).
- The queue says the north star has 23 bars. The walk has **28** (22 must-show and 6 cannot-show).
- The walk's status hint says "Phases 1-2 BUILT … never run live" (walk:6). That is stale: Phases 3-4 were
  built offline on 2026-10-23.
- **Sound.** The walk says the owner "chose to specify a must hear axis… never a gate" (walk:149-154). The
  programme says `NORTH_STAR_HEAR_AXIS_1` was "dropped 2026-09-17, no hear axis owed" (programme, watch out).
  Both agree that sound never gates. They disagree on whether the walk carries hear lines at all.
- Spec §5 contains the sentence *"Every worldgen-irrelevant toggle here is safe mid-save; none of it is."*
  It cannot be parsed, and it reads like a sentence garbled during an edit.

## 3. The tests

### 3.1 Inventory

| layer | file | what it is | laws covered |
|---|---|---|---|
| kernel selftest (C#, 80 Checks) | `Source/SelfTest/Program.cs`, run by `selftest_atmosphericbase_kernel.py` | pure kernels with no game | L11 white refused; L8 dark rules (only with mayGoDark; a Steady scheme never black); L4 (60,000 samples all in the palette); RoomBreath 19-21 changes per 5 cycles; Sparks at rest over 90% of the time; L7 flasher count and stability; place and group mapping; changed-only writes (under 0.5% of evaluations write); the shipped defs parse; rank order; territory on 11 irregular fixtures (the leader holds 7, each fixture changes hands at least twice per turn, at most 2 changes per step); 200 fixtures (at most 4 changes per step); tuning clamps; tremor (cap 3, own palette, 4% of 300, the louder god wins); exclusions ("Hollow" is not "holo"); CompGlower members bound; release leaves no override |
| mutation selftest (py) | `selftest_atmosphericbase.py` | about 37 source mutations planted against a mock bridge; each must turn a check red | no-Harmony, no-def-edit, gates, exclusions, L9 unlit, changed-only, computed colour, Lerp, game time instead of real time, palette guard, moods not scribed, rank sort, territory and tremor switches, tremor drawn in the leader's palette |
| live validation (bridge) | `validation.py`, 23 components | Phase 1-4 chains on a live map | take, drive and release restore exactly; an untaken neighbour is untouched; channel off refuses and releases; the button switch and scenario-decides hide the button; one mood drives a palette member; only changed fixtures are written; outside the group shows its own glow; compositor off shows own glow; the default switch; release after a mood restores; territory gives every fixture one claimant in one palette; both gods hold ground; the boundary moves; tremor at most 3 in its own palette; release after territory restores |
| proof (bridge, V/R/G clocks) | `proof_atmosphere.py` (1225 lines) | V: the shipped `Evaluate(comp,t)` on a virtual clock, three seeds (t0 = 1000, 1000+0.37P, 86400.5). R: real frames while paused. G: save and reload. | S1 sampler sees, S2 static control, S3 deterministic, L4, W1 changed-only, L5a-e, L5d period clamp, L6a-c, L8, L9, L10 runs while paused, L11a never white, L11b white scheme rejected, L12/L13/N1, D2 default gentle live, D3 no light show (at most 6 changes per minute, gap at least 2.0 s), C1 cost (provisional budget 0.1 ms per Evaluate per 100 fixtures), X1 kernel and V clock agree, R1 reload, R2 left as found, Z1 log budget |
| bad models | `proof_atmosphere.py --selftest` | 12 planted wrong mods: off_palette, static_boundary, mixed, tremor30, white, no_restore, pause_fails, no_hook, no_fixtures, blind, leaky, phase5 | proves the proof can fail |

### 3.2 What is not covered

- **Nothing has run live.** `validation.py` and `proof_atmosphere.py` have only stub runs. The live territory
  proof is owed (31400b41ac).
- Three validation components are stubs: `release_after_save_reload_restores` (UNMEASURED),
  `unlit_fixture_not_driven`, and `territory_boundary_visible_and_tremor_reads_as_presence` (a human looks).
- These walk lines are UNCOVERED by design: restore after minify or fly-away (live), gesture restore
  (Phase 5), landing reset (live), and sound beds.
- **L8** is UNMEASURED even in the good model, because no dark scheme exists. **L12, L13 and N1** read
  UNMEASURED/HARNESS because Phase 5 is unbuilt.
- **L1, L2, L14, L15, L16 (live) and L17** have no row at all.
- **Gentle by default** has no automated bar. The owner cut `default_scheme_is_livable` and accepted that.
  D3 checks only for the absence of a light show. Nothing checks that the default is **perceptible** at
  all (K3).
- **Cost** has no ms figure. Phase 0 Q2 is a structural read: each colour write is a DeRegister plus
  Register with an O(lights on map) linear scan, plus one map-wide job per frame (programme:180-210). The
  programme's re-measurement "at the end of Phase 2 and again at the end of Phase 6, on the owner's real mod
  list" (programme:121) has not been done.

### 3.3 Honest weaknesses of the instruments

- **Kernel against engine.** Under .NET Framework, `SetGlowColorInternal` cannot run, so the lit regrid
  branch is proven only live (`selftest_atmosphericbase_kernel.py`). On the Mac the kernel selftest exits 2,
  which means UNMEASURED.
- **The V clock proves the function, not the frame loop.** It calls `Evaluate` at chosen times, so it cannot
  see K6 (fps-dependent sampling), frame hitches, or what happens when two maps evaluate in the same frame.
  R covers only "moves while paused".
- **The substrate stand-in is wrong.** `proof_atmosphere.py:880` uses (217,217,208) as the "vanilla lamp".
  Any check of distance from the substrate is therefore calibrated against a near-white, not against amber.
- **Site dependence.** A row is UNMEASURED/SITE below 10 lit fixtures spread over at least 8 cells. The owner's
  real ship has 11 light-capable things (§9a C1), so every live row on the real ship is one lamp from being
  unmeasurable.
- **C1 times `Evaluate` with a Stopwatch.** It does not see the engine's regrid jobs that the writes trigger
  on the next frame, so this mod's cost is under-counted (inference). `jawa/map_comp_timing` cannot see this
  mod at all, because it times only `MapComponentTick` (proof plan §2).
- **Time dependence.** Territory needs one full turn (900 s, or 240 s at the clamp). The V clock makes the
  wait free, but any live human look at "the boundary moves" needs 4-15 real minutes per sitting.

## 4. An improved definition

Each change is marked **[P]** (a proposal that changes meaning, so the owner rules) or **[C]** (a clarification
that adds a number or resolves wording without changing intent).

**L3 [P].** *"Aboard the Utinni the player never chooses. Elsewhere, at install, a gentle scheme runs on every
eligible fixture on the player's maps, and each fixture has a 'take glow back' button."* This inverts the
opt-in for non-Utinni play only. The other options are in question Q1. Evidence for the change: K1.

**L4 [C].** Add: *"A scheme palette must be perceptibly distinct from the fixture's own glow. At least one
entry lies at least 60 (max-channel difference) from every vanilla lamp colour it will commonly replace,
(214,148,94) included."* The threshold of 60 is a proposal (the shipped high entry is 40 away) to be confirmed by eye. Evidence: K3.

**L5 [C].** Add speed bounds in fixtures, not only in period: *"The boundary moves at least one fixture per
120 s while two moods hold, and changes at most 2 fixtures (or 2% of the union, whichever is larger) per 4 s."*
The kernel already shows at most 2 changes per step on 11 fixtures and at most 4 on 200 (selftest). This
makes the bar the law's own instead of the code's.

**L6 [C].** Resolve §10 Q3 as *"the three loudest"* (what the code does), and add: *"When more fixtures want
to flicker than the instant cap allows, the winners rotate per slot, so no fixture is favoured."* Evidence: K5.

**L7 [C].** Add: *"Flashers are spread. No two share a room while a room without a flasher remains in the
group, and flasherCount never exceeds max(1, 10% of the group)."* Evidence: K4.

**L8 [P].** Rewrite: *"A chosen dark is a scheme whose palette includes full black (0,0,0) and at least one
ember (max channel 8-40). In any 4 s window, at least one fixture in each dark room shows an ember or changes.
Lights the framework does not hold stay lit."* Why: Phase 0 Q7 found that a (0,0,0) glow is invisible to the
grid, the same as unpowered. So "absolutely black with a little motion" has to be carried by **embers**. Each
ember is a nonzero, dim, moving entry. The 4 s figure and the ember band are proposals.

**L9 [C].** Define unlit as "`CompGlower.Glows` is false". That covers loss of power **and** the player
switching the lamp off. Whether switching off counts as a blackout for L17 is question Q6.

**L10 [C].** Add: *"The compositor samples at a fixed real-time rate, 10 Hz, independent of frame rate."*
Evidence: K6.

**L11 [P].** Rewrite: *"White is any colour with saturation below 0.20 and value above 0.70 (HSV, on the
0-255 channels). No scheme may hold such an entry. The Narrator's white is a single reserved token,
`RM_NarratorWhite`, which only the Narrator gesture may write. The palette guard admits it only while that
gesture is live."* Evidence: K2. As built, the guard would also refuse the Narrator's own white, because the
guard admits only scheme palettes, and the white scheme is refused (inference from `RM_PaletteGuard` and
`RM_SchemeKernel.cs:58`).

**L12/L13 [C].** Bring in the catalog's IV-1 as law: *"The Narrator is a preemption layer above allocation,
never a claimant. During the hold no fixture moves: flashers and tremor are suppressed. On return, every scheme
resumes at the phase it would have reached had it never stopped."* That costs nothing, because the patterns
are already pure functions of real time (`RM_SchemeKernel.cs:110`). The ruled preemption of the alarm
(L12 "including a live raid alarm") stands. The catalog's three options for an alarm exemption are therefore
**closed** by L12 and must not be reopened silently.

**L17 [C].** Spell out the inputs, so the build is ready when CANVAS_1 rules: *"Anger is computed from (a) a
power blackout over held fixtures, measured as a duration, and (b) the held, lit fixture count falling below
a ruled threshold, which is either a fraction of the map's high-water mark or an absolute number. It is
reported to consumers as an event. AtmosphericBase never acts on it (L2)."*

**§2.1 [C].** *"A god hologram def must carry `RM_AtmosphericExcluded`. The 'holo' substring is a fallback
only."* Evidence: K8.

**§5 [C].** Replace the garbled sentence with *"Every toggle here is safe to change mid-save."* The code
already releases everything when the light channel is switched off (`RM_MapComponent_AtmosphericBase.cs:147`).

**Counts [C].** Fix "15 laws" to 17 and "23 bars" to 28 wherever they appear. Refresh the walk's status hint.

## 5. Conceptual execution: how it should feel

These are the intended feelings. The timings come from the shipped settings and the catalog. Items marked
⟂ are not built.

**A day aboard the Utinni** (two gods engaged, three restless)

| real time | what you see | mechanism |
|---|---|---|
| 0:00 | The halls run in one god's ember-reds, the dormitories in another's sea-greens. Each colour breathes slowly, room by room. | Territory 60/40 across the union of the two groups (L5); RoomBreath, 120 s |
| 0:00-15:00 | The red ground drifts across the ship. About every 40 s one lamp at the edge changes hands. Nobody notices one change, but everyone notices the ship looks different after lunch. | Boundary period 900 s, ragged 0.08 |
| any 30 s | One lamp somewhere flickers violet for less than a second, then a different lamp flickers ochre. | Tremor: up to 3 silent gods, 0.8 s, at most 4% at once (L6) |
| on a deed | Ninefold makes the red god louder: its share grows and the boundary leans. | Rank from Ninefold ⟂ (NINEFOLD_LOUDNESS_FRONT_1) |

**A raid**

| real time | what you see | mechanism |
|---|---|---|
| alarm | A few fixtures, spread one per room, beat fast in alarm colours. The mass keeps the gods' territory. You can tell the alarm from every mood. | Alarm gesture ⟂; flashers L7 |
| fighting | The light really lights the fight. A cruel god's territory may be badly lit for shooting. | L2, L15 |
| power cut | The held lamps go silent. Untaken lamps also fail, but the gods' holograms still stand lit in the dark. | L9, L16 |
| power back | Lamps resume at the phase the clock has reached. The gods are angry, and a later letter refers to the blackout. | L17 ⟂, witness ledger ⟂ (the blackout is the referent once resolved) |

**A quiet night** (a god chooses the dark)

| real time | what you see | mechanism |
|---|---|---|
| dusk | The god's rooms ease down through deeper and deeper palette entries to full black. | A dark scheme ⟂ (L8) |
| night | Most fixtures are black. Every few seconds one ember wanders across a room and goes out, like something moving behind the walls. Untaken lights in the kitchen stay steady, which proves the dark is chosen. | L8 embers, as proposed in §4 |
| dawn | The god releases its mood and the gentle default (or the next-loudest god) takes the ground back. | Reallocation, changed fixtures only |

**A Narrator moment** (an authored letter arrives, and the game pauses)

| real time | what you see | mechanism |
|---|---|---|
| +0.0-0.8 s | White spreads from the fixture nearest the subject to the whole ship, nearest neighbour first. | Narrator RISE ⟂; real time while paused (L10) |
| letter open | Everything holds white and **perfectly still**: no flashers, no tremor. | HOLD (catalog IV-1) |
| close +0-6 s | Lamps dim back one by one to exactly what each would be showing now. A boundary that "moved" during the hold has moved; nothing rewinds. | RETURN; pure function of time; L13 restores |

## 6. Three better implementations

The three proposals are deliberately different in kind:

- **A** changes the *shape* of territory (aesthetic).
- **B** changes the *engine* (efficiency).
- **C** changes the *medium* (novelty).

They can be combined, and §7 recommends a combination.

Two cost terms are fixed by the engine for every option (Phase 0 Q2, programme:180-210):

- **W** is the colour writes per second. Each write costs one O(L) scan and shift, where L is the registered
  lights on the map, plus a flood fill of that light's diameter squared (about 29x29 cells for a 14-tile
  lamp).
- **E** is the per-evaluation overhead.

The present build has E = O(T) work + O(T) allocation + O(writes x T) lookups, with T the number of taken
fixtures, at 10 Hz on 60 fps.

### A. "Tides through the hull": geodesic territory on the room graph

**What changes.** Replace the centroid wedge (`RM_TerritoryKernel.cs:141`) with a front that travels **through
the ship's architecture**. Each claimant gets an anchor:

- the group's registered shrine, if it has one;
- otherwise its fixtures' medoid.

On a membership change (already checked every 60 frames), compute every fixture's **door-graph distance**
from each anchor, as a BFS over rooms and doors. Ownership is then a moving threshold:

- a fixture belongs to the lead when `d_lead(f) - d_other(f) < θ(t)`;
- θ(t) oscillates slowly (period ≥ 240 s, the existing clamp) between bounds set by `leadShare`;
- the ragged edge stays as the existing per-fixture jitter.

**Efficiency.**

- Sort the union once by `d_lead - d_other` on each membership change.
- At each evaluation, move θ and flip only the fixtures between the old and new θ, found by bisection: O(log T
  + changed).
- Preallocated arrays, so there is no allocation per evaluation.
- Writes fall to the true front size. On 11 fixtures that is about one write per 40 s at the shipped 900 s
  period (inference, from the same share math as the wedge).
- Room-graph BFS is O(rooms + doors) per membership change. A gravship has tens of rooms (inference).

**Aesthetic.**

- The god's colour seeps **along corridors and through doors**. It floods a room, then the next.
- On a ring ship the colour advances both ways round the ring from the shrine and meets the other god on the
  far side.
- Motion language: tide and breath, advancing and receding, never rotating.
- It matches canon's "different colored areas … that slowly move throughout the ship" more literally than a
  sweep (inference).

**Novelty.** Light territory that respects walls and doors, so a god "holds a wing". The four other ambient
or lighting mods surveyed (§9a C5) colour by fixture or by room, not by a moving front through the room graph.
That is an inference from the survey, not exhaustive.

**Risks.**

- An open-plan ship with one big room degenerates to bearing order, so keep the wedge as the fallback.
- The anchor rule is a new authored choice (question Q2).
- Doors that open and close do not change room membership, but a wall rebuilt mid-game does. It is cheap to
  recompute.

**What survives.** All of Phases 1-4 except one kernel function. The series and pick proof contract and the
rows L5a-e are unchanged. The kernel selftest needs a new geometry case: a ring and a branching hull.

### B. "Only when it changes": a sparse event scheduler

**What changes.** Invert every pattern so that it answers "when does fixture f next change index?". Each one
is analytic:

- RoomBreath: the next step boundary of `(t/period + phase) x len`.
- Sparks: the next slot start, or the next intra-spark step, which follows from the same hash.
- Flasher: the next `flasherPeriod` multiple.
- Tremor: the next slot.
- Territory: the next `StepsPerTurn` boundary.

Keep a binary heap of `(nextTime, fixture, generation)` in preallocated arrays. Each frame:

1. Pop everything due up to `now`.
2. Compute the index with the **same** pure function as today.
3. Write.
4. Push the fixture's next time.

A claim change bumps a generation counter, which lazily invalidates the stale heap entries and re-seeds only
the affected group.

**Efficiency.**

- Per-frame cost is O(due x log T) instead of O(T) every 6 frames. An idle Lamplight on 200 fixtures in 4 rooms
  is 200 x 4 steps / 120 s, about 6.7 fixture events per second, against 10 full 200-fixture scans (2000
  fixture visits) per second today (arithmetic from the shipped Def and
  `PingPong`; inference about the build).
- No per-frame allocation.
- Event times are exact, so **K6 disappears**: a 0.8 s flicker lasts 0.8 s at any fps.
- It makes a write **budget** natural. At most K writes per map per frame, with the overflow deferred to the
  next frame. That caps the worst engine term (N x O(L) re-register) under load, for example a 200-fixture
  Narrator rise at about 50 per frame over 4 frames, which is also the shape of the "nearest-neighbour spread".
- `Drive` loses the O(T) `IsTaken` scan, because the heap holds a direct index into `taken`.

**Aesthetic.** Unchanged by default, which is the point. It also makes **temporal** effects affordable that
the current loop cannot draw: a Narrator rise with frame-exact sequencing, an ember that crawls across six
fixtures at 0.15 s per hop, and a deliberate "breath held" stillness costing zero work.

**Novelty.** Low on screen, high in engineering: a light scheduler whose cost scales with what changes rather
than with how much is lit.

**Risks.**

- More code paths: generation counters, and re-seeding on territory or claim changes.
- The V clock must become "advance to t", which is still deterministic and pure. Row X1 (the kernel and the V
  clock agree) is the guard.
- A bug shows as a lamp that stops (a missed re-push). Add a cheap sweep every 10 s that re-seeds any fixture
  with no heap entry.

**What survives.** Every kernel, scheme, Def, API call, proof row and selftest. Only `RM_Compositor.Update` and
`Evaluate` internals change, plus one new kernel function per pattern (`NextChange`). Each new function can be
tested against brute-force sampling with the existing 60,000-sample harness.

### C. "Light that is not wiring": a drawn halo layer over held fixtures

**What changes.** The glow grid keeps doing what only it can do: real illumination (L2, L15), as a slow,
quantised, low-change base. A second, **drawn** layer carries the expressive motion: a soft additive halo
quad at each held fixture, plus thin "veins" along the walls between fixtures in the same territory, drawn
from `MapComponentUpdate`. Colour is set per draw through a property block on **one** material. The material
cache never sees a new colour, so the L4 leak cannot happen, and motion and fades may be smooth.

The halo layer also renders the two things the grid cannot:

- the L8 writhe in absolute black, because a halo can move in a cell the grid has at (0,0,0);
- the Narrator's white wash as a screen-space lift that needs no re-register of every glower.

**Efficiency.**

- The grid's write rate W can drop by about an order of magnitude, because the base can change, say, once per
  minute (inference).
- Drawing T quads per frame instanced is one draw call per material (inference). Unity's instanced draw is
  cheap at hundreds of quads, but it is a per-frame cost even while idle. Not measured, and owed before
  committing.
- No glow-grid work at all for the Narrator, the tremor, or the dark writhe.

**Aesthetic.**

- Light that *moves like a living thing*: halos that swell, veins that carry colour from lamp to lamp,
  embers in true black.
- Palette logic: the base stays in the quantised god palette, and the halo is the same hue at lower alpha.
  Identity still rides on hue and motion (§4).
- The risk is that a drawn layer reads as **paint, not light**. An additive glow that lights no floor can
  look fake next to vanilla's lighting overlay (inference). It must be judged by eye.

**Novelty.** High. Inference: no RimWorld mod known to the repo draws a living vein layer between real
fixtures. It is also the only one of the three proposals that could make "darkness writhes" literal.

**Risks.**

- It strains **L2/L15**: the expressive layer illuminates nothing, so a god's "cruel lighting" would have to
  stay on the base.
- It strains **L16**: halos must never sit on holograms.
- Draw order and zoom: halos need to fade at far zoom. Screenshots taken by other mods may capture them.
- Shader availability: it must use a stock RimWorld or Unity additive shader, since no asset bundle is planned
  (inference).
- Mods that recolour the grid (`juanlopez2008.lightsout`, §9a C5) would no longer collide on the expressive
  layer, which is a benefit.
- Hard limit: it **cannot** satisfy "the ship's existing lights are the tapestry" if it replaces the base
  rather than accompanies it. So the base must keep moving, even if slowly.

**What survives.** Take-over, exclusions, schemes, territory and tremor kernels: the layer reads the same
`(fixture -> scheme, index)` output. New pieces: the draw code, a per-scheme "halo" field, and a proof row
that can see a drawn layer. That row needs a screenshot judge, because no bridge read sees draws
(inference).

### Summary

| | efficiency | aesthetic | novelty | risk | existing work kept |
|---|---|---|---|---|---|
| A tides | writes = front size; O(log T) per eval; zero alloc | architectural seep, tide not sweep | medium-high | low (wedge fallback) | ~95% |
| B scheduler | O(due log T); fps-independent; write budget | unchanged; enables fine timing | low on screen | medium (missed re-push) | ~100% of contracts |
| C halo layer | grid writes way down; per-frame draw cost unmeasured | living, smooth, true-black writhe; may read as paint | high | high (L2/L15/L16 strain, look unproven) | kernels yes, new draw path |

## 7. Recommendation

1. **Run Phases 1-4 live first, with no new code.** Nothing here has been seen in a game, and two premises
   need a live look before any proposal is chosen:
   - K3: is the default even visible on vanilla amber?
   - Is cost (C1, plus the next-frame regrid) small at 11 and at 200 fixtures?

   Fix the three mislabelled substrate constants (K3) before that run. They are code edits for a builder
   seat.
2. **Adopt B as the engine** before Phase 5. Phase 5's Narrator rise, alarm flashers and L8 embers are
   exactly the fast, timed elements on which the current 6-frame loop is weakest (K6, K7), and B keeps every
   contract.
3. **Adopt A as the territory kernel.** It is cheap, keeps the proof rows, and is the strongest single
   aesthetic gain toward "areas that slowly move throughout the ship". Keep the wedge as the fallback.
4. **Treat C as a bounded spike**, limited to L8 embers in black and the Narrator wash, judged by the owner on
   screenshots. Do not make it the medium unless he likes how it looks. It is the most novel option and the
   most at odds with L2 and with "the existing lights are the tapestry".

## 8. Questions only the owner can answer

**Q1. What does a fresh install show off the Utinni?** Evidence: K1 (`RM_MapComponent_AtmosphericBase.cs:146`),
L3 at definition:49, the per-thing opt-in at definition:134-137.

| option | pro | con |
|---|---|---|
| a. Nothing until you hand lamps over (as built) | Respects the opt-in ruling literally. Zero surprise. | L3's "gentle scheme runs from install" never happens. Most players never see the mod. |
| b. A settings button, "hand over every lamp on this map" | One click shows the mod. The opt-in survives. | It is still a step the player has to find. |
| c. Off the Utinni, take every eligible lamp at install, with "take glow back" per lamp | L3 is literal. The mod is visible immediately. | It reverses the opt-in. Other mods' lamps change colour unasked. |

**Q2. Territory shape.** Evidence: K9 (`RM_TerritoryKernel.cs:141`), proposal A, canon `in_front` quoted at
definition:60-63.

| option | pro | con |
|---|---|---|
| a. The rotating wedge (as built) | Built, tested, and works on any layout | Reads as a clock hand on a ring ship (inference) |
| b. Tides through doors (A), wedge as fallback | Architectural, legible: a god holds a wing | One more kernel and a new anchor rule (shrine or medoid) |
| c. Per-god choice: shape is part of a god's motion signature | Shape becomes a second identity channel (§4) | More to author in the signature sitting |

**Q3. The default palette against real lamp amber.** Evidence: K3. Vanilla is (214,148,94) (Core
`Buildings_Furniture.xml:1361`). Lamplight runs from (204,150,92) to (244,188,118).

| option | pro | con |
|---|---|---|
| a. Keep it | Barely there, the most gentle | May read as "nothing happened" (inference, needs a look) |
| b. Widen it: a deeper low end and a brighter high end, still warm | Visible breathing, still restrained | Slightly less work light at the low end (§5 warns) |
| c. Make the palette relative to each fixture's own colour | Works on any lighting mod's lamps | Breaks the "one fixed palette per scheme" cache bound unless quantised per base colour |

**Q4. May a drawn layer carry expression (proposal C)?** Evidence: §6 C. Phase 0 Q7: a (0,0,0) glow is
invisible to the grid.

| option | pro | con |
|---|---|---|
| a. No: the glow grid only | Every effect is real light (L2) | L8 "absolutely black with motion" must use dim embers |
| b. Yes, only for embers in black and the Narrator wash | True-black writhe; a cheap Narrator | A second visual language to keep consistent |
| c. Yes, as the main expressive medium | The most alive and the most novel | Strains "the existing lights are the tapestry" and L2. May look like paint. |

**Q5. What counts as "white" (L11)?** Evidence: K2 (`RM_SchemeKernel.cs:43,58`). As built, (255,240,199) passes.

| option | pro | con |
|---|---|---|
| a. All channels at least 200 (as built) | Simple, already tested | Pale creams and ice-blues slip through and may read as the Narrator |
| b. Saturation below 0.20 and value above 0.70 is white | Catches near-whites of every tint | Forbids pale god palettes, such as a moonlight god |
| c. One reserved token, and anything within a set distance of it is banned | Precise, and the Narrator's look is one value | Needs the Narrator's white chosen now (§10 Q2) |

**Q6. When the player switches a held lamp off, is that a blackout?** Evidence: L9 and L17
(definition:80-84, 111-115). The code skips `!Glows`, so the light falls silent.

| option | pro | con |
|---|---|---|
| a. Yes, it counts toward anger like a power cut | One rule. Handing a lamp to the gods means something. | Feels punitive for ordinary switching |
| b. Silent, but no anger; only power loss and stripping anger | Matches L17's wording exactly | A loophole: switch everything off without power loss |
| c. Hide the off switch on held lamps aboard the Utinni | Removes the question on the Utinni | Takes a vanilla control away. Needs a Harmony patch or a gizmo filter (the build forbids Harmony) |

**Q7. What happens next, in order?** Evidence: §7. Nothing has run live. Phase 5 is unbuilt.

| option | pro | con |
|---|---|---|
| a. Live run of Phases 1-4 and cost measurement, then B, then Phase 5 | Every later choice rests on seen evidence | Slowest to anything new on screen |
| b. Phase 5 (Narrator, alarm) on the current engine now | The Narrator moment sooner | It is built on the loop weakest at fast effects (K6, K7) |
| c. A and B together, then the live run | One refactor and one look | A larger change goes to its first live run unseen |

**Q8. Does the walk carry "must hear" lines?** Evidence: walk:149-154 against the programme's watch out
(`NORTH_STAR_HEAR_AXIS_1` dropped). Both say sound never gates.

| option | pro | con |
|---|---|---|
| a. Keep the lines as playtest notes, never gates | Sound intent survives in writing | Two documents keep saying different things unless one is edited |
| b. Delete the hear lines; sound lives only in Phase 6 playtesting | One story | The intent for acoustic territory is lost from the walk |


## 9. Owner decisions (question cards, 2026-10-23 evening)

1. **Install:** a settings button "hand over every lamp on this map"; the per-lamp opt-in survives.
2. **Territory:** *"The various gods should [be] associated with many such patterns. In the [Utinni]-aligned version they will be player settings."* (typed; his words as recorded) - per-god shapes/patterns; off the Utinni they are player settings. Tides through doors (A) is one such shape; the wedge stays available.
3. **Palette:** widen it (deeper low end, brighter high end, still warm); fix the (217,217,208) mislabel (real vanilla lamp is (214,148,94)).
4. **Drawn layer:** only for embers in black and the Narrator wash; ordinary patterns stay real lamp light.
5. **White:** one reserved token; anything near it is banned (the Narrator's exact white is chosen at calibration).
6. **Lamp switched off by hand:** silent, no anger; only power loss and stripping anger (L17).
7. **Order:** live run of phases 1-4 with cost measured, then the faster engine (B), then Phase 5.
8. **Walk "must hear" lines:** kept as playtest notes that never gate.
9. **Another mod/player edits a held lamp:** *"It is released. In Utinni this displeases gods."* - release the lamp, keep the edit; aboard the Utinni the edit angers the gods (new rule, to be written into the definition).
10. **Reload:** restart gently from the start of the pattern (so no clock offset or gesture state is saved; a long-uptime double clock is not required for reload).
11. **Earlier same day:** no colour-blind/photosensitivity planning; maximise aesthetics.
12. **Who sees the Nine (god-patterns Q1):** *"Only works on gravships in Utinni. That's the lore."* - the Nine's patterns exist only on gravships in the Utinni campaign. Off the Utinni there are no gods: the neutral, unnamed beautiful patterns (player-selectable) are all there is. *(My reading; it supersedes decision 2's "player settings for the Nine" - the player-settings surface now covers the neutral patterns only.)*
13. **Hot colours:** keep Sh'kaar's hottest entry visibly gold, Rekko leans bronze; no near-white shimmer exception.
14. **Dark gods:** Full is Full (truly dark at Full), Gentle keeps a floor.
15. **Boundary:** authored pairings for canon pairs (Ishko/Ta'Baa, Sh'kaar hunting Ishko), the leader's shape elsewhere.
