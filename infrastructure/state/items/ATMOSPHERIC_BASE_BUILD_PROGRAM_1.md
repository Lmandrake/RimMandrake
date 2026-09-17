# ATMOSPHERIC_BASE_BUILD_PROGRAM_1 — the ambient framework the gods speak through

Design is DONE and is not to be re-derived: `design/RimMandrake/atmospheric_base_mod_definition.md`
holds fifteen laws, the object model, and §9's verbatim record of every ruling from the owner's
sitting on 2026-09-16. The DRAFT north star is
`design/validation_walks/RimMandrake/AtmosphericBase.md` (18 lines; DRAFT binds nothing until he
validates). Candidate schemes to react to:
`Transient/dynamiclighting_scheme_catalog_DRAFT_2026-09-16.md`.

🔴 **Read the laws before writing a line.** Four of them will be violated by the obvious
implementation: colour must be quantised (L4), blending is by allocation and never by
colour-mixing (L5), only changed emitters may be written and dirtied (§2.6 step 6), and darkness
must carry motion (L8).

## spec

**Both channels ship together** — his ruling, against light-first. So nothing here is releasable
until Phase 6 lands; the phase order below is build order, not release order.

### Phase 0 — DESKTOP ONLY. Seven questions, no code.

Spec §8 is the whole of this phase. Nothing else starts until it answers, because two of the
seven can void a law:

1. 🔴 Does a per-frame hook exist that runs **while the game is paused**? **L10 falls if not** —
   every gesture would freeze the instant a letter pauses the game, including the Narrator's.
   If the answer is no, stop and bring the owner the choice between game-time gestures and a
   different trigger point; do not silently build game-time.
2. 🔴 What does changing a **live glow colour** cost, at 10 / 100 / 500 emitters? The whole cost
   model rests on it. ⚠️ `TWINKLE_FLORA_SPIKE_1` measured a *sprite tint*, not a cast glow —
   different subsystem, and its numbers do not transfer. Do not cite them as if they did.
3. Can glow colour and radius be set at runtime on the fixtures the live mod stack actually
   ships (glowstoneforked, floorlights2, ledlightsstrip, nightlights, plus vanilla)?
4. Does 1.6 vanilla support coloured light at all, or does it come only from those mods?
5. Do positioned looping Sustainers behave acceptably when the mix changes as the camera moves?
6. What happens to lights and Sustainers during gravship **flight**?
7. Is a fully-dark fixture distinguishable from an unpowered one to the game's own light grid?

Deliverable: answers recorded on this item with the instrument used for each, plus an explicit
go/no-go on L10.

### Phase 1 — the skeleton and the take-over

Mod scaffold at `src/RimMandrake/AtmosphericBase` (`mandrake.rm.atmosphericbase`, namespace
`RimMandrake.AtmosphericBase`, prefix `RM_`, `loadAfter` Ludeon.RimWorld only, no Harmony patch
that alters any def). Capability discovery (§2.1) — never a def whitelist. The per-thing opt-in
button, and the scenario-decides path. The exclusion list is a hard bar: glowing animals, worn
equipment, plants, holograms are never touched. Release must restore the fixture's prior colour
and radius exactly.

### Phase 2 — one mood, quantised, cheap

Groups (§2.2), schemes as data (§2.3), and the compositor driving ONE mood. This is where L4 and
the dirty-only-on-change rule are proven, and where question 2's cost is re-measured against
real code rather than predicted.

### Phase 3 — territory

Two moods, allocation over the union of their groups, and a boundary that moves on its own slow
clock. This is the mod's signature and the thing canon already describes; if it does not read as
two presences, nothing later will save it.

### Phase 4 — the tremor

Moods ranked third and below, capped at three, each in its own palette (L6). It must never grow
loud enough to be mistaken for territory.

### Phase 5 — gestures, and the Narrator

Finite claims that composite above moods and restore the substrate exactly (L13). The reserved
white and its enforcement (L11). The Narrator above everything including a live alarm (L12).
Save/reload mid-gesture must restore correctly.

### Phase 6 — sound

Beds first, then stings, then acoustic territory, on the same claims (§3). Camera is the
listener. ⛔ `src/RimUtinni/RustCathedralHum` is **not to be touched** — the overlap is accepted
by ruling, and the mitigation is a volume control in this mod's own settings.

### Phase 7 — the witness ledger

§2.7, narrow by design. Exists so a god's letter can never claim a witness that was not there
(L14).

### Phase 8 — the two hook doors

Code API, then the def-driven API (§2.8). The def half is what lets an XML-only mod join.

### Phase 9 — the library and the showcase

The scheme catalog's admissible entries, and Mod Settings per spec §5: per-channel toggles, the
gentle default, group selection, the showcase, and this mod's own bed volume.

### Phase 10 — the consumers

Wire what already exists: `Ninefold` as the loudness/rank source, `Oracle` for the Narrator's
gesture (and its authored-letter equivalent, since canon says v1's Narrator is pre-authored
prose, not the LLM), `Aftermath`/`AftermathRites` for omen telegraphs, `GravshipLanding` for the
reset. `RaidRedesigner` is deliberately NOT a consumer — it is the other half of L2, acting on
the world directly. Detail: `Transient/atmosphericbase_hook_ecosystem_DRAFT_2026-09-16.md`.

## verify

- Phase 0: each answer names its instrument. An unanswerable question is recorded `UNMEASURED`,
  never guessed, and never inferred from a doc — several repo docs assert engine facts that trace
  to an earlier agent's prose.
- Phases 1-5: the walk's steps 1-9 in `design/validation_walks/RimMandrake/AtmosphericBase.md`,
  which cannot be authored concretely until Phase 0 answers.
- L4 has a mechanical check available and it should be built early: assert that every colour ever
  handed to an emitter is a member of a declared palette. A visible smooth fade is the leak's
  symptom, so the check and the north star's `never_interpolated_colour` line are looking at the
  same defect from two sides.
- Cost is re-measured at the end of Phase 2 and again at the end of Phase 6, on the owner's real
  mod list, not on the minimal one.

## criteria

Done means: both channels working; two gods legibly sharing a hull with a moving boundary; the
tremor present and never mistakable for territory; the Narrator's gesture unmistakable on first
encounter and restoring exactly; a chosen blackout that cannot be read as a power fault; nothing
driven that was not handed over; the code and def hooks both exercised by a real consumer; and
Mod Settings that degrade to indistinguishable-from-absent with everything off.

## watch out

- ⚠️ **The design doc supersedes its own earlier ruling and says so.** An earlier decision in the
  same sitting had this mod shipping alarm hardware — a strobe, a wall beacon, a floor strip. It
  was replaced outright by the take-over button, and the flasher role moved to the scheme (L7).
  Build no fixtures.
- ⚠️ **Rank is read, never computed here.** Canon's `in_front` already rules that loudness decides
  actuator priority, and `Ninefold` already computes satiation from deeds. A second ranking
  system inside this mod would be a competing answer to a settled question.
- ⚠️ **L2 is a boundary, not a limitation.** If a god should attract raiders, that belongs in
  `RaidRedesigner` and not here. The lights are an output device.
- ⚠️ **L1 is the law a good demo hides.** Everything must read as tenants using the wiring, never
  as the ship having feelings — canon forbids moods-of-the-ship. A beautiful ambience that reads
  as the ship emoting is a failure even if it is liked.
- ⚠️ The sound half is currently unbindable by the north-star system: it has a show axis and a
  read axis and nothing for audio. Tracked as `NORTH_STAR_HEAR_AXIS_1`; do not let Phase 6 ship
  believing a walk covers it.
- 📐 `RUT_HumLayers.xml` claims no audio pipeline exists in this repo. Measured false 2026-09-16:
  1048 custom audio files, including six ship-ambience sustainer defs and metal-creaking loops in
  `src/RimStarWars/Armoury/Defs/Absorbed_KotorCore/SoundDefs/`. Phase 6 needs no commissioned
  audio to start.
