# RimMandrake: AtmosphericBase — validation walk

subject: src/RimMandrake/AtmosphericBase  (packageId `mandrake.rm.atmosphericbase`)
deps: none (loadAfter Ludeon.RimWorld only; no Harmony)
list: minimal
status-hint: **Phases 1-2 BUILT 2026-10-11, never run live** (`ATMOSPHERIC_BASE_BUILD_PROGRAM_1`): capability
discovery, the hard exclusion list, the per-thing "Hand glow to Atmospheric Base" / "Take glow back" buttons (riding
`Find.ReverseDesignatorDatabase`, no Harmony), the scenario-decides switch, exact restore of the CompGlower colour override
on release (radius is never written; it belongs to `_Shared/LightLedger`). Phase 2: schemes as data
(`RM_AtmosphericSchemeDef`, shipped `RM_Scheme_Lamplight` default + `RM_Scheme_Fireflies`), default groups
(ship/rooms/halls/exterior) plus registered groups, and the compositor driving ONE mood -- palette-index only (L4),
written only on change, unlit fixtures skipped, real time. Five Mod Settings. Phases 3-10 (territory, tremor, gestures,
sound, witness ledger, def hooks, library, consumers) are not built. The definition is
`design/RimMandrake/atmospheric_base_mod_definition.md`. Script: `src/RimMandrake/AtmosphericBase/validation.py`
(chains `take_over_proof`, `one_mood_proof`), selftests `selftest_atmosphericbase.py` (mock + planted breaks) and
`selftest_atmosphericbase_kernel.py` (C# kernel against the real CompGlower).

## must be true

*Lines from the definition's laws and §2.1. A line whose phase is not built says so; it is not a gap in Phase 1.*

- Only emitters explicitly handed to the framework are ever driven — a glowing animal, a worn
  item, a plant and a hologram are never touched, no matter what claim is live.
  → take_over_proof.excluded_glowers_never_accepted
- An emitter is discovered by capability (a player-owned building with a CompGlower), never by a def whitelist, and
  the four exclusions are decided before capability. → take_over_proof.static_no_harmony_no_def_edit_gates_and_settings
- With no consumer registered and no player selection, the mod drives nothing and the colony
  is lit exactly as vanilla would light it. → take_over_proof.untaken_neighbour_untouched
- Release returns a fixture to exactly the colour it had when handed over — the override field itself, so a lamp
  with no override gets none back — and its radius is never written, so a LightLedger owner's dimming survives. → take_over_proof.take_drive_release_restores_exactly
- The hand-over buttons are hidden on a map whose scenario decides. → take_over_proof.scenario_decides_hides_the_button
- Turning the hand-over button switch off hides the buttons. → take_over_proof.button_switch_hides_the_button
- A held fixture released after a save and reload still gets its prior glow back.
  → take_over_proof.release_after_save_reload_restores
- A held fixture that leaves the map (uninstalled, minified, flown away) is given its own glow back.
  → UNCOVERED live: minified/uninstalled is `Prune` (Release on unspawned); flown away is `MapRemoved` (field-only restore,
  the map is out of `Find.Maps`). Static gates `[gate] RestoreFieldOnly` and `Release`; no component drives either live
- A gesture always restores the state underneath it exactly, including when it is interrupted
  by a higher-ranked gesture, and including across a save and reload mid-gesture. → UNCOVERED: Phase 5 not built
- No live claim survives a landing: the reset is total. → UNCOVERED live: a mood lives on the map's component, and
  `MapRemoved` clears it with the held fixtures; a landed ship's new map starts with none. No component lands a ship
- With power lost, no emitter is driven and no bed plays. → one_mood_proof.unlit_fixture_not_driven (UNMEASURED stub:
  the compositor skips `!CompGlower.Glows`, static gate `[gate] g.Glows`; beds are Phase 6, not built)
- Every colour an emitter is ever set to comes from its scheme's declared palette — the
  framework never produces an interpolated value, so the Graphic/Material cache is bounded by
  the sum of the palettes in play and never grows with time. → one_mood_proof.one_mood_drives_a_palette_member
  (and `Drive` refuses a non-member colour; the kernel selftest samples 60,000 pattern values; static `[L4]` refuses a Lerp)
- Only emitters whose quantised value changed on a given evaluation are written and dirtied.
  → one_mood_proof.only_changed_fixtures_are_written (kernel selftest: 200 fixtures × 6000 evaluations write exactly the
  index changes, under 0.5%)
- One mood on one group drives only that group's held fixtures; a held fixture outside the group, and every untaken
  fixture, shows its own glow. → one_mood_proof.outside_the_group_shows_its_own_glow,
  one_mood_proof.untaken_neighbour_untouched_by_the_mood
- Animation off shows every held fixture's own glow; the default off with no mood pushed does the same.
  → one_mood_proof.compositor_switch_off_shows_own_glow, one_mood_proof.default_mood_switch
- Turning either channel off in Mod Settings leaves the other working, and turning both off
  leaves the game indistinguishable from the mod being absent.
  → take_over_proof.light_channel_off_refuses_and_releases (light half; the sound channel is Phase 6, not built)
- No Harmony patch alters a vanilla or third-party def; the take-over is additive and
  reversible per thing. → take_over_proof.static_no_harmony_no_def_edit_gates_and_settings

## anti-guessing notes

- RULED OUT: a Harmony postfix on GetGizmos is needed for a per-thing button — `GizmoGridDrawer.DrawGizmoGridFor`
  asks every designator in `Find.ReverseDesignatorDatabase.AllDesignators` for `CreateReverseDesignationGizmo`, and
  `AllDesignators` returns the database's own list (RimSage 1.6). `Reinit()` replaces that list, so registration is
  re-checked by reference every frame; the static check goes red if that comparison is lost.
- RULED OUT: restoring the effective `GlowColor` is "exact" — CompGlower reads `glowColorOverride ?? Props.glowColor`,
  so writing the def colour back leaves an override where there was none. The kernel selftest asserts the difference.
- RULED OUT: the C# selftest can run `SetGlowColorInternal` — under .NET Framework it throws TypeLoadException
  ("Non-abstract, non-.cctor method in an interface", from `IThingGlower` in `ShouldBeLitNow`); Unity's Mono loads it.
  The selftest swaps in a field-only writer, so the lit regrid branch is proven only by the live proof.
- RULED OUT: snapshotting the radius and writing it back on release — every radius write goes through
  `_Shared/LightLedger` (LIGHT_LEDGER_ONE_1), and a written-back radius would erase a dimming another owner applied
  while the lamp was held. `selftest_lightledger.py` caught the first draft; the static check `[light-ledger]` guards it.
  Phase 2 carries brightness in the PALETTE instead (GlowGrid.GroundGlowAt reads the max channel of the accumulated
  glow, so a darker entry is a dimmer light) and needs no ledger modifier at all.
- RULED OUT: a hallway RoomRoleDef to tell halls from rooms -- vanilla's RoomRoles.xml has none (RimSage 1.6); a
  corridor reads as role `Room` or `None`. The "halls" default group is those two roles indoors.
- RULED OUT: `ParseHelper.ParseColorInt` in the .NET Framework selftest -- MissingMethodException on a `String.Split`
  overload Unity's Mono has. The selftest splits the "(r,g,b,a)" integers itself; the game parses the def normally.
- RULED OUT: restoring a held fixture through `SetGlowColorInternal` when its map is removed -- the map is already out
  of `Find.Maps` when `MapComponent.MapRemoved` runs (`Game.DeinitAndRemoveMap`), so `MapHeld` cannot be trusted; the
  field-only write is used, and the fixture re-reads it when it spawns again.

## extended

- E1. Removing the mod from a save leaves any held fixture at its driven colour (CompGlower Scribes the override)
  -> UNBUILT; Phase 1 drives only through its API, so nothing is driven unless a consumer or the proof does it.

## the walk

Phase 0 answered 2026-09-19 (L10 stands: `MapComponentUpdate` runs while paused). Step 1 is built and is what
`take_over_proof` checks; step 2 is built and is what `one_mood_proof` checks; steps 3-9 wait on the phases that build
them (3+ blocked on ATMOSPHERIC_BASE_CANVAS_1 and NINEFOLD_LOUDNESS_FRONT_1). What the walk has to prove, in order:

1. [D] Take over one light by its own button, confirm the framework drives it, release it,
   confirm the light returns to its prior colour and radius.
2. [B] Push one mood on one group; read back what the compositor says is showing; confirm it
   matches and that untaken lights nearby are unchanged.
3. [B] Push a second mood at a lower rank and confirm **territory**, not colour-mixing — every
   driven emitter must hold a colour from exactly one of the two palettes.
4. [B] Push a third, fourth and fifth mood; confirm at most three tremor contributors, each in
   its own palette.
5. [B] Play the Narrator's gesture over a live alarm; confirm it wins, and that the alarm is
   exactly restored afterwards.
6. [L] Pause the game mid-gesture; confirm the gesture continues (or record that L10 is void).
7. [B] Cut power; confirm silence in both channels.
8. [B] Land; confirm every claim is gone.
9. [D] Save mid-gesture, reload, confirm the substrate is what it was.

## north star

state: DRAFT
validated-hash:

⚠️ **DRAFT — BINDS NOTHING.** Per `design/RimMandrake/north_star_validation_spec.md` §3, a
DRAFT checklist cannot fail a mod and cannot green one. Written 2026-09-16 on the **Mac
laptop** — no game, no def dump, and RimSage has never connected there — so every line traces
to the owner's own words in that evening's sitting, to `canon.yml`, or to a file on disk. Only
the owner promotes a line to a bar.

🔴 **This walk names a mod that does not exist.** Validating it binds a vision, not a build,
and every line will fail on the day the code first runs. That is the intended state, and the
WreckedMachines precedent covers it.

🛑 **THE DEFINITION STOPS HERE — owner ruling, 2026-09-17, verbatim:** *"I'm not sure we should
worry about how to automate these tests at this time. please stop the north star definition here
and file it as TBD for now in terms of these highly subtle nuances until we can play with it
live first."*

- **This section is finished as a statement of intent and is NOT to be refined further** until he
  has played the mod. Do not add bars, split bars, reword bars or chase the remaining nuance.
- **How these bars get automated is TBD** — deliberately unanswered. `NORTHSTAR_MOTION_FRAMES_1`
  (the frame-sequence judge, ruled earlier this same walk) and the material-cache count that
  replaced the smooth-fade bar both stand as recorded work and are **not to be built on spec**
  for this mod; they wait on live play. `NORTH_STAR_ATMOSPHERIC_TBD_1`.
- **Final shape: 28 bars — 22 must-show, 6 cannot-show.** Recorded here so a later reader can tell
  a finished-and-stopped section from an abandoned one.
- ⚠️ It stays **DRAFT**, and that is the ruling rather than an omission. He did not validate it,
  so per spec §3 it fails nothing and greens nothing — which is the correct state for a vision
  recorded ahead of the code and ahead of any way to check it.
- 🔑 The same instinct as his hear-axis condition six hours earlier (*"don't block on it, it's
  just part of the playtest"*), now applied to the subtle end of the visual axis: the bars are
  worth writing down and are not worth automating before he has seen the thing move.

✅ **The missing third axis is RULED — owner, 2026-09-17.** The spec provided a **show** axis
(visual) and a **read** axis (text), and this mod's whole sound channel — beds, stings,
acoustic territory — was judgeable by neither. He chose to specify a **`must hear`** axis, with
one condition, verbatim: *"but don't block on it, it's just part of the playtest."*

🔑 So the sound channel gets real lines, but **the hear axis is never a gate** — it cannot hold
this mod or any other, and its lines are judged when he plays rather than before it ships. Sound
work proceeds without waiting for the axis to exist. `NORTH_STAR_HEAR_AXIS_1`.

✅ **A bar here may cite several frames — owner ruling, 2026-09-17.** Walking this checklist
surfaced that **10 of the 23 bars it then carried were about CHANGE rather than a state**, while `judge.py` took
`shots[-1]` under a prompt telling the model to answer about that image alone:
`territory_boundary_moves`, `tremor_reads_as_third_presence`, `dark_is_never_still`,
`blackout_angers_visibly`, `stripping_fixtures_angers_visibly`, `narrator_arrival_unmistakable`,
`narrator_restores_substrate`, `god_identity_on_two_channels`, `speed_lives_in_few_fixtures`,
`never_interpolated_colour`. He ruled the judge takes an ordered sequence for such a line —
spec §4b, owed on `NORTHSTAR_MOTION_FRAMES_1`. `alarm_distinct_from_every_mood` joined them
later in the same walk, making **11** — its bar is a comparison against the mood schemes, so it
needs their captures too, not only its own.

🔑 One consequence lands on this list rather than on the machinery: **a sequence proves something
CHANGED, never that it changed SMOOTHLY.** So `never_interpolated_colour` is not an eye's
question at any frame count and wants a material-cache count instead.

Provenance tag per line: 🗣 his verbatim words or a ruling of his · 📐 measured from a file on
disk this pass · 🤔 my inference, weakest, cut freely.

### the experience  (OWNER'S WORDS — verbatim)

2026-09-16, commissioning the mod:

> *"It treats the grid of player lights as a tapestry to swirl patterns around creatively."*
>
> *"Onboard the Utinni, the players don't change the color of the lights, the gods do."*

The image he reached for when asked what makes the Narrator unmistakable — and the reason the
whole framework needs a restore-what-was-underneath layer:

> *"The narrator, I was imagining now, might suddenly bring up the brightness of the lights to
> a bright white... he speaks... and then slowly dim back to whatever was going on."*

And the sentence that decides what darkness means here:

> *"Let it go absolutely black, but there will almost be a little motion, a little flickering,
> a writhing that lets you know that it's not a power outage. It's there for a reason. Figure
> it out."*

2026-09-17, second sitting — **what the gods themselves are, and what a dark ship means.** Asked
how a blackout could ever be referred to, given the old rule required a lit room:

> *"The blackout IS the thing referred to. The gods REALLY don't like blackouts. Fix that right
> now! It becomes absolutely witnessed and referencable once resolved. And the gods will also be
> holograms that work by themselves, without power."*

And on the canvas, told that the ship holds 11 light-capable things among 2002:

> *"We will add some lights for sure, and they will be irregular. The player can add more lights.
> Removing lights below a threshold will anger the gods."*

🔑 The through-line: **the ship is not alive, and it must still feel inhabited.** Canon forbids
a ship with moods of its own (`canon.yml` `narrator`, 2026-08-30 — no integrating self, no ego,
no self-description). So every effect this mod produces has to read as *somebody using the
wiring*, never as the building emoting. A pretty ambience that reads as a mood of the ship is a
failure of this mod even if the player likes it.

🔑 The second sitting sharpens that into something checkable: **the tenants have bodies.** A god
is a hologram that runs on nothing, so it is present in a dark ship, it is never something the
framework drives, and the wiring is its voice rather than its self. That is why stripping the
wiring is an injury (they get angry) and why a blackout is the loudest thing that can happen —
the gods are still standing there when the lights go.

### must show

**Two gods sharing one hull**
- [ ] `territory_boundary_visible` — 🗣 two claimants hold visibly separate areas and a player
      can point at where one ends and the other begins. Ruled: "a pattern that swirls between
      one and the other"; canon.yml `in_front`: "different colored areas even perhaps that
      slowly move throughout the ship".
- [ ] `territory_boundary_moves` — 🗣 that boundary is seen to travel, not merely to exist. A
      static split is a different and lesser thing.
- [ ] `tremor_reads_as_third_presence` — 🗣📐 a god beyond the top two is visible as *someone
      else stirring* without holding territory, in a palette that is its own. Canon: the silent
      eight express through "flickers in their palettes".

**Darkness**
- [ ] `dark_is_never_still` — 🗣 a chosen darkness always carries motion, so it cannot be read
      as a power failure. Ruled: "a little flickering, a writhing that lets you know that it's
      not a power outage".
- [ ] `dark_leaves_reference_light` — 🗣 light the framework does not control stays lit through
      a blackout scene, proving the black was chosen.
- [ ] `god_visible_through_a_blackout` — 🗣 when the power is gone, the god is still there to
      look at: its hologram is lit and unaffected. Ruled 2026-09-17, "holograms that work by
      themselves, without power". This is the line that makes a dark room a witnessed room.
- [ ] `blackout_angers_visibly` — 🗣 once power returns, the lights show that the gods took the
      outage badly — the restored scheme is not simply the one that was running before. Ruled:
      "The gods REALLY don't like blackouts."

**The canvas the ship actually has**
- [ ] `pattern_reads_on_an_irregular_scatter` — 🗣 the swirl and the moving boundary read as
      intentional across fixtures that are unevenly placed. Ruled 2026-09-17: the authored lights
      "will be irregular", so anything that only looks right on a lattice fails here.
- [ ] `stripping_fixtures_angers_visibly` — 🗣 tearing out the ship's lights past the threshold
      visibly changes how the remaining ones behave. Ruled: "Removing lights below a threshold
      will anger the gods."

**The Narrator**
- [ ] `narrator_arrival_unmistakable` — 🗣 his arrival is recognisable on FIRST encounter with no
      text explaining it: the reserved rise to bright white, held, then released.
- [ ] `narrator_restores_substrate` — 🗣 the lights return to exactly what they were doing before
      he spoke. This is the half that makes the other half legible.

**Identity and legibility**
- [ ] `god_identity_on_two_channels` — 🗣 a god is recognisable by hue in a still frame AND by
      motion in a dim one, so losing either channel does not lose identity.
- [ ] `alarm_distinct_from_every_mood` — 🗣 an alarm is recognisable without any text by a player
      who knows the ship: its behaviour is distinguishable from every mood scheme this mod ships.
      Learning is allowed; reading a label is not. **Ruled 2026-09-17**, replacing an
      agent-inferred *"reads as an alarm at a glance, no learning required"* bar that collided
      with `reads_as_tenants_not_as_the_ship` — a warning legible on sight reads as the ship
      warning you, which canon forbids. ⚠️ The bar is worded against the DIFFERENCE because that
      is what a frame sequence can settle; *"a player who has learned it"* appears in no frame and
      the judge cannot stand in for that player. Id renamed rather than reused — permitted only
      because this checklist is DRAFT and has never bound.
- [ ] `speed_lives_in_few_fixtures` — 🗣 a handful of fixtures carry the fast movement while the
      mass moves slowly, reading as a real alarm panel rather than a uniform strobe.
- [ ] `partial_scheme_reads_as_itself` — 🗣 a god holding only part of the grid reads as that god,
      not as something broken or half-finished. **Promoted 2026-09-17.** With the lights irregular
      and few, a partial claim is the normal case rather than an edge one. Cost he accepted: it
      constrains how few fixtures a claim may cover, decided before the ship's light count exists.
- [ ] `two_gods_told_apart_in_one_view` — 🗣 two simultaneous claimants are distinguishable at play
      zoom in a single view. **Promoted 2026-09-17** over the stated objection that it largely
      restates `territory_boundary_visible` and that its camera constraint belongs on how evidence
      is captured; he took it anyway, so both stand and the overlap is deliberate.
- [ ] `omen_told_from_mood_in_one_cycle` — 🗣 a warning's arrival is distinguishable from ongoing
      atmosphere within one cycle of the pattern. **Promoted 2026-09-17** over the stated objection
      that `alarm_distinct_from_every_mood` already covers the ground; this one adds a time bound,
      which no other bar carries. ⚠️ Two bars over one requirement: if either is ever edited, edit
      both, or they will come to disagree.

**The law that is easiest to break while looking good**
- [ ] `reads_as_tenants_not_as_the_ship` — 📐 every effect reads as somebody using the wiring,
      never as the building having a feeling. Canon `narrator`: no integrating self, no ego, no
      moods-of-the-ship.
      **Split into four by ruling 2026-09-17**, from one bar reading *"a glowing animal, worn gear,
      a plant and a hologram keep their own light in every scene"* — one bar cannot be staged or
      settled with four subjects in frame at once. Each below is one scene a component can build.
- [ ] `animal_keeps_its_own_light` — 🗣 a glowing animal's own light is untouched in every scene.
- [ ] `gear_keeps_its_own_light` — 🗣 worn gear that glows keeps its glow in every scene.
- [ ] `plant_keeps_its_own_light` — 🗣 a glowing plant keeps its light in every scene.
- [ ] `hologram_keeps_its_own_light` — 🗣 a god's hologram is lit exactly as itself in every
      scene, blackout included. 🔴 The strictest of the four: a hologram is a god's body
      (2026-09-17), so a scheme dimming one is the framework driving the speaker instead of the
      channel. ⚠️ Deliberately paired with `never_dims_a_god` rather than folded into it — this
      one asks that the hologram is right, that one that nothing made it wrong, and the pairing
      is the same duplication spec §10.6 licenses where a validated line guards an enforcement
      from being quietly weakened.

### cannot show

- [ ] `never_the_ship_emoting` — 📐 any effect that reads as the ship itself expressing a mood.
      The inverse of `reads_as_tenants_not_as_the_ship`, stated separately because it is the one
      failure a pleasing demo hides best.
- [ ] `never_white_but_the_narrator` — 🗣 bright white dominant in any scheme or god signature
      that is not his.
- [ ] `never_an_uninterruptible_alarm` — 🗣 an alarm the Narrator cannot cut through, or an alarm
      left broken after he has finished.
- [ ] `never_a_claim_surviving_a_landing` — 🗣 a mood visibly bleeding through the landing reset.
- [ ] `never_dims_a_god` — 🗣 a god's hologram darkened, tinted or extinguished by anything this
      mod does, including a full blackout scheme. Ruled 2026-09-17: the holograms "work by
      themselves, without power", so the framework touching one is it driving the speaker.
- [ ] `never_tremor_reads_as_territory` — 🗣 the third god's stirring grown loud enough to be
      mistaken for one of the two holding ground. **Promoted 2026-09-17** as a rejection rather
      than a positive bar, because one sequence where the tremor reads as a claim settles it. Cost
      he accepted: a ceiling on how expressive the silent eight may be, and they are the part of
      the cast with the least design behind them.

### resolved off this list — owner rulings, 2026-09-17

Recorded so the absence reads as a decision and nobody restores either one.

- **`default_scheme_is_livable` — CUT.** Its "restrained enough to live under" wording was an
  agent's, not his, and living under something appears in no frame or sequence, so no judge could
  settle it. ⚠️ The cost he accepted: gentle-by-default is now written down nowhere a check can
  see, so a later agent shipping a light show as the shipped default is caught only by him
  opening a colony.
- **`never_interpolated_colour` — MOVED off the eye.** It described a Material leak
  (`TWINKLE_FLORA_SPIKE_1`: a continuously varying colour mints a cached Material per value
  forever) and asserted the symptom and the defect were the same thing. They are not: a frame
  sequence proves that a colour changed, never that it changed *smoothly*, at any frame count. It
  becomes a count of cached materials, owed on `NORTHSTAR_MOTION_FRAMES_1`. ⚠️ It cannot be built
  yet — this mod has no code — and a lint owed is not a lint built.

### candidate lines

**Empty — all four were promoted with him on 2026-09-17, none left parked.** Recorded so the
absence reads as a decision: `partial_scheme_reads_as_itself`,
`two_gods_told_apart_in_one_view`, `omen_told_from_mood_in_one_cycle` and
`never_tremor_reads_as_territory` are all bars now, the last of them as a rejection. Two were
promoted over a stated overlap objection; both notes are on the lines themselves.
