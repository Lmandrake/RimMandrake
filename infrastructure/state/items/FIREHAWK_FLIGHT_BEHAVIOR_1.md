# FIREHAWK_FLIGHT_BEHAVIOR_1 — donor-style wing flap → real flight animation

## history
v1 (below, superseded): a `PawnRenderNodeProperties_Spastic` wing-split render
tree was identified as riding a vanilla engine class (zero new C#) and later
actually built (`RUT_FireHawkRenderTree.xml`: custom `RUT_FireHawkBody` +
`PawnRenderTreeDef` wing overlay). Owner's own live test found it broken:
standing still sideways with no visible flap, and north missing one wing
entirely with the other misaligned. Root cause is architectural, not a bug to
patch — Spastic drives a small idle wiggle on ONE static texture per node; it
was never a per-facing, per-frame flying animation, and nothing keeps a single
wing texture aligned across four facings. `CLAUDE.md` and
`skills/generating-rimworld-sprites/SKILL.md` were corrected 2026-09-19 with
the real mechanism: `PawnKindDef.flyingAnimationFramePathPrefix`, a whole-body
directional flip-book, MEASURED against Core's Chicken via `resources.assets`
extraction (UnityPy) and frame-diffed to confirm real pose change.

## done this pass — retired the broken mechanism
- `RUT_PyrelandsFauna.xml`: `RUT_FireHawk`'s `<race><body>` reverted
  `RUT_FireHawkBody` → vanilla `Bird`; `<renderTree>RUT_FireHawk</renderTree>`
  removed entirely.
- `RUT_FireHawkRenderTree.xml` deleted (the custom BodyDef + BodyPartGroupDef +
  Spastic PawnRenderTreeDef).
- PawnKindDef texPath reverted `FireHawk_Body` → `FireHawk` (the original
  complete flattened sprite, body+wings baked in — the wing-cropped
  `FireHawk_Body_*` split art existed only to pair with the Spastic overlay).
- Deleted the 6 now-orphaned PNGs: `FireHawk_Body_{north,east,south}.png`,
  `FireHawk_Wing_{north,east,south}.png`.
- `validate_patch.py --live`: 0 errors, 0 warnings. `deploy_custom_mods.py
  --prune --apply` on UtinniPatches: 8 files, VERIFIED in sync.
- **The flight STAT is untouched and was already correct**: `MaxFlightTime 30`,
  `FlightCooldown 5`, `flightStartChanceOnJobStart 0.15`, `flightSpeedFactor
  2.5`, `canFlyIntoMap`/`canLeaveMapFlying` all still on `RUT_FireHawk`'s
  `<race>` block, landed by an earlier pass ("Flyers fly" standing rule,
  `3785aac81`). FireHawk still flies; it just draws its correct static sprite
  instead of a broken wing overlay while doing so.
- Needs a restart to take effect (defs parse at startup only) — not yet taken,
  batching with other pending def changes rather than restarting for this
  alone.

## owed — the real flip-book animation
### attempt 1, 2026-09-19 (background subagent) — blocked on art-gen quota, wiring deferred
Filed 15 artpipe jobs (`FireHawk_Flying_<1-5>_<north|east|south>.png`, 5 frames
— tucked/upstroke-peak/full-spread/downstroke-power/recovery). **All 15
failed immediately**: the codex channel is quota-exhausted account-wide until
**2026-09-21 09:32** (confirmed from `worker_stderr_tail` on each
`infrastructure/artpipe/failed/rut_firehawk_flying_*.manifest.json`). No
local codex/gemini CLI fallback exists in this environment; gemini is
policy-disabled for this daemon ($0 budget). **No PNGs were fabricated** —
correctly refused rather than faking placeholder art.

The subagent also wired `flyingAnimation*` fields onto the PawnKindDef
pointing at those not-yet-existing frames, reasoning from CLAUDE.md's "never
block flight waiting on frames." **That wiring was reverted before commit**:
the CLAUDE.md guidance covers fields being *absent* (no animation defined at
all, definitely safe); it says nothing about fields *present* pointing at
missing texture files, and the subagent's own report flagged this exact gap
as unverified (RimSage/engine access unavailable on this machine). Given
`flightStartChanceOnJobStart 0.15` means FireHawk will actually attempt to
fly in the live, actively-played campaign, shipping an unverified "what
happens when GetBestFlyAnimation's texture lookup misses" is the same class
of mistake this item already cost once (a visibly broken flying animal the
owner had to catch live). Reverting costs nothing — the block is preserved
below, ready to re-apply once art exists.

**Re-do once art lands**: run
`python3 src/RimMandrake/Utils/artpipe/requeue_quota_failures.py` after
2026-09-21 09:32 to regenerate the 15 filed jobs (already sitting in
`infrastructure/artpipe/failed/rut_firehawk_flying_*.json`, committed this
pass), then re-add this exact block as a sibling of `<lifeStages>` on
`RUT_FireHawk`'s PawnKindDef, deploy, and **verify live — step ticks to an
actual takeoff, not a standing screenshot** — before considering the missing-
texture-fallback question settled one way or the other:

```xml
<flyingAnimationFramePathPrefix>Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_Flying_</flyingAnimationFramePathPrefix>
<flyingAnimationFrameCount>5</flyingAnimationFrameCount>
<flyingAnimationTicksPerFrame>2</flyingAnimationTicksPerFrame>
<flyingAnimationDrawSize>1.35</flyingAnimationDrawSize>
<flyingAnimationDrawSizeIsMultiplier>false</flyingAnimationDrawSizeIsMultiplier>
<flyingAnimationInheritColors>true</flyingAnimationInheritColors>
```

Frame count (5, Locust's) and `ticksPerFrame` (2) are defaults, not gates —
adjust freely once real art is in hand. **One measured finding worth
keeping**: read live against all 5 vanilla flyers in the
`2026-09-19T18-15-44Z` def dump rather than trusting CLAUDE.md's single
Chicken example — Chicken is the ONLY one of the five using
`flyingAnimationDrawSizeIsMultiplier=true` (2.4); Duck (1.7), Goose (1.35),
Sparrow (2) and Locust (1) all use `false` with an absolute cell size. The
block above follows the 4-of-5 majority (`false`, absolute `1.35` against
this creature's 1.1 grounded adult drawSize) rather than copying Chicken's
outlier pattern — if a future pass copies CLAUDE.md's Chicken example
verbatim without re-checking this, it's copying the minority case.

## sweep — other flying Pyrelands roster kinds
`RUT_FireWasp` also carries `MaxFlightTime`/flight race fields (from the same
"Flyers fly" pass) and has no render-tree/Spastic wiring to retire — it never
got one. It is in the same "flies, no animation frames yet" state as FireHawk
now is, and is an equally in-scope target for the flip-book work above when
picked up. `RUT_FurnaceBeast` is a quadruped, not a flier. Ash'karr's biome
`wildAnimals` lists reference donor birds (not our art to rewire here) — not
re-swept this pass, see the v1 sweep note above for the original scope.

## done this pass, 2026-09-24 (FOUNDRY) — art landed, wired, live-partial
### art was already generated — do not re-file the "attempt 2" job
`infrastructure/artpipe/done/rut_firehawk_flying_{1..5}_{north,east,south}.manifest.json`
show all 15 frames **generated and status:ok** (codex, 2026-09-19, i.e. the
quota-block noted above cleared before this pass started — the item's own
"owed" section was stale). PNGs live in
`infrastructure/artpipe/_artsrc/rut_firehawk_flying_<N>_<dir>/*.png`, all
256×256 RGBA, clean transparent corners (`validate_sprite.py --describe`),
and a visual contact-sheet review (`Transient/`-scratch, not committed) shows
a real 5-frame tuck→full-spread→recovery wingbeat cycle per facing, correct
per-facing framing (north=rear, south=front, east=profile) per the style
brief. **Nothing was regenerated.**

### installed and wired
Copied to
`src/RimUtinni/UtinniPatches/Textures/Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_Flying_<1-5>_<north|east|south>.png`.
`RUT_PyrelandsFauna.xml`'s `RUT_FireHawk` `PawnKindDef` gets the exact block
this item already specced (frameCount 5, ticksPerFrame 2, drawSize 1.35,
multiplier false, inheritColors true, prefix
`Things/Pawn/Animal/Pyrelands/FireHawk/FireHawk_Flying_`) as a sibling of
`<lifeStages>`. `validate_patch.py --live` (full 621-mod def set): **0
errors, 0 warnings**. Deployed via `deploy_custom_mods.py --mod UtinniPatches
--apply` (18 files, VERIFIED in sync — this also carried along another
FOUNDRY thread's concurrent `WEEPINGSTONES_RM_MOD_BUILD_1` changes in the
same mod folder, untouched/unedited by this pass, git-committed separately).

### live: grounded render confirmed, mid-air frame NOT caught
Two full-list (621-mod) restarts this pass (first auto-loaded the campaign
save and hard-crashed ~30s in on a pre-existing, unrelated bug — repeating
`RimWorldRealFoW.MapComponentSeenFog.IncrementSeen IndexOutOfRangeException`
while ticking existing colonists Timofei/Eduard/Rachel; nothing in the
stack trace names FireHawk, UtinniPatches or WeepingStones — worth a look by
whoever owns RealFoW compat, not filed here). `start_debug_game_ready`
quicktest-worldgen on the full 621-mod list then hit the OTHER documented
failure mode (`quicktest-crashes-full-modlist-use-cheap-mechanism-list`):
looping `Could not execute post-long-event action` NREs, `hasCurrentGame`
never true. **Built a one-off `modset_builder.py` "firehawk" tier**
(`BRIDGE + mandrake.rut.patches`, 10 mods incl. all 5 DLC) to get a clean,
fast (18s) quicktest instead — not added to the tracked `TIERS` table in the
repo, script discarded after use; worth adding for real if this creature
gets touched again.

On that tier: `jawa/spawn_pawn RUT_FireHawk` spawns clean, faction Salvagers,
and **the grounded sprite renders correctly** — confirmed by direct
screenshot (`rimworld/screenshot_cell_rect`, small crop) showing the
ash-grey/ember-orange bird, not a magenta placeholder. `MaxFlightTime`,
`flightStartChanceOnJobStart 0.15` etc. are untouched and present (measured
via `jawa/get_defs` equivalent — actually just confirmed by the def not
erroring and the pawn walking at the expected speed).

**Did not catch a live takeoff.** Tracked position over ~35 minutes of
simulated ticks (`step_game_ticks`, hundreds of calls in windows of
20–900 ticks) and dozens of distinct movement segments (job-starts, by proxy)
— no segment showed the large per-tick displacement a `flightSpeedFactor 2.5`
hop would produce, and no screenshot (~25 taken, both wide `take_screenshot`
and cropped `screenshot_cell_rect`, after fixing two real traps below) caught
a wing-spread pose. Tried luring a hunt job with a wild (`faction: none`)
Chicken 30 tiles off — the pawn did not path toward it in the observed
window (likely needs real hunger buildup, not available in a fresh
quicktest). At `flightStartChanceOnJobStart 0.15` this is either bad luck
across enough job-starts that it shouldn't be, or (more likely) each
short local-wander job only lasts a handful of ticks once airborne, well
under this session's ~20–60-tick sampling grain — I could easily have
straddled a real flight window without a frame landing inside it. **This is
inconclusive, not a negative finding — do not read "not caught" as "art
doesn't render in flight."**

Two real bridge traps hit and fixed mid-session, worth keeping in
`skills/rimbridge/references/traps.md` if not already covered:
- **The Debug log window reopens over the map even with `jawa/clear_ui`
  called every time**, once an error has occurred earlier in the session —
  `rimworld/close_window {"windowType": "LudeonTK.EditWindow_Log"}` before
  `clear_ui` is needed too, matching traps.md's existing note.
- **A camera `jump_camera_to_cell` + `set_camera_zoom` while paused can
  render a STALE frame** — two consecutive screenshots at genuinely
  different requested positions came back byte-identical until a small
  `step_game_ticks` (5) was inserted between the camera move and the shot.
  Matches the existing pause+screenshot staleness trap, generalised to
  camera moves.
- Also (separately) confirmed the existing fog trap the hard way: the first
  spawn point happened to be inside an unrevealed/fogged patch of the
  quicktest starting base — `jawa/list_pawns` reported `spawned: true` the
  whole time but nothing rendered at that position at any zoom. Respawning
  in the open fixed it instantly. Worth a `traps.md` line: fog silently
  drops a pawn from the RENDER, never from the API.

### state
Left **`doing`**, not closed — the item's own bar ("verify live — step ticks
to an actual takeoff, not a standing screenshot") is not yet met. The
mechanism and art are shipped and validated; only the positive live sighting
is outstanding.

### 🔴 owner ruling, told to FOUNDRY this session — stop trying to screenshot flight
Verbatim: *"Don't try to capture images of flight. It doesn't work."* Said
directly to a FOUNDRY window while this item's bridge-holder was mid-attempt at
exactly this (25 screenshots over ~35 minutes, no catch — see above). ⛔ (a) and
(b) below are screenshot-hunting strategies and are RULED OUT by this — do not
spend more bridge time trying to photograph a mid-air frame, however the
sampling is tuned. **(c) is now the required approach**, not a nice-to-have.

**NEXT** for whoever picks this back up: (c) add a debug `[Tool]` (see
`rimbridge-companion` skill) that reads `Pawn_FlightTracker`'s current state on
a pawn directly — `CanEverFly`/whatever field indicates "airborne now" — making
verification a deterministic state read instead of a probabilistic screenshot
hunt, for this and every future flyer. ~~(a) sample much more densely...~~ and
~~(b) get the pawn genuinely hungry first...~~ are superseded by the ruling
above — do not pursue either.

### 🔴🔴 owner ruling, THIRD repetition, same session — do not live-test flight unattended at all
Verbatim, said again while this bridge hold was still live: *"For the third
time, do not do live testing of flyers without a human present. It doesn't
work."* This is broader than the screenshot ban two paragraphs up — it rules
out **any** unattended FOUNDRY solo bridge session hunting a live flight
sighting, not just the screenshot method. Filed at the standing-rule level too
(`CLAUDE.md`, "If it flies in the fiction, it flies in the game" section) so
this stops needing re-discovery per item. **Whoever is holding the bridge for
this item right now: stop the unattended hunt.** The positive live sighting
bar on this item is only closable two ways from here: (c) above (a
deterministic state-read tool, buildable and provable without the owner
watching), or a joint session where the owner is actually present and looking.
Do not open another unattended bridge session against this item's live-verify
bar.

`RUT_FireWasp` is unchanged this pass — still next-wave, same "flies, no
animation frames yet" state as before.
