# NINEFOLD_LAUNCH_POSTFIX_FALSE_FIRE_1 — Ta'Baa is fed by FAILED gravship launches

Found by code review 2026-09-06 (DIRTY_CODE_REVIEW_STANDING_LOOP_1), `src/RimMandrake/Ninefold/Source/Patch_GravshipLaunched.cs` line ~29.

`CompLaunchable.TryLaunch(PlanetTile, TransportersArrivalAction)` is `void` with early returns before the launch: not spawned, no transporter group, `!CanLaunch()`, destination beyond fuel range (Log.Error or silent). The Postfix runs unconditionally, so a failed attempt still calls `GameComponent_Ninefold.Notify_Launched`, spiking Ta'Baa's satiation and resetting his erosion clock for a launch that never happened.

## spec
Prefix captures `__state` = (parent.Spawned && comp.CanLaunch() && destination within range) using the same checks TryLaunch makes; Postfix fires only when `__state` is true. Better: postfix a method that runs only on a real launch if one exists (`CompLaunchable` → the skyfaller/`TransportPodsArrivalAction` creation) — verify in the decompiled source before choosing.

## verify
```
PROVE   quicktest: a launch attempt with CanLaunch()==false (no fuel) leaves Ta'Baa's satiation unchanged; a real launch changes it once
EXPECT  two readings via the Ninefold debug/read surface, before/after each attempt
LIES    a postfix that fires twice on a real launch (if the chosen hook is also called on retry) — count, don't just check non-zero
```

## FOUNDRY, 2026-09-07: fixed source-side, exactly the "Better:" route this item names — live PROVE/EXPECT still owed

Found independently via an adversarial fresh-context code review of an EARLIER same-day self-fix (which itself only gated on `CanLaunch()` and missed the distance-vs-`MinFuelLevelInGroup` guard this item's own first paragraph names) — same root defect, same line, this item just got there first.

**Fixed, matching this item's own "Better:" suggestion**: rather than replicating TryLaunch's guard chain in the Prefix (drift-prone, and I'd already gotten it wrong once), `Patch_GravshipLaunched.cs` now gates on `CompLaunchable.lastLaunchTick` (public field), which vanilla itself sets unconditionally immediately after EVERY guard clause passes and before any pod is processed — verified via RimSage against the decompiled source, not assumed. Prefix captures it, Postfix credits Ta'Baa only if it changed. This is immune to any future guard-chain change, unlike a replicated check list. Commit `572413c0`, adversarially re-reviewed and marked CLEAN (`64e09460`).

**Not done**: the live PROVE/EXPECT this item's own verify section wants (a real quicktest: a no-fuel launch attempt leaves Ta'Baa unchanged, a real launch changes it once) — needs a game-up session with a gravship set up to fail-then-succeed a launch, not attempted this pass. `needs game-up` stands. Left `doing`, blocked rather than closed — the fix is source-complete and independently reviewed, but per this project's own doctrine a live check on a mechanism never observed running still counts as owed.

## 2026-09-07 (FOUNDRY) — game-up session: a real gravship departure DOES NOT call `CompLaunchable.TryLaunch` at all — the patch's own target is wrong for the "gravship" the title names

Live session on a custom 13-mod minimal list, `mandrake.rm.ninefold` active, 0
config/crossref/patch errors on load. Went to actually exercise the fix and
found something that changes what a live check here even means:

**`Building_GravEngine` (RimWorld's real Odyssey gravship engine) is a plain
`Building` — it has no `CompLaunchable` at all** (confirmed:
`grep class Building_GravEngine` shows `: Building, IRenameable`, no comp
list; a full-repo `CompProperties_Launchable` search across every Odyssey Defs
file finds it on exactly `AncientTransportPod`/`AncientTransportPod_Special`
and vanilla `TransportPod`/`Shuttle` — never on the gravship). Odyssey's real
gravship departure runs through `Building_GravEngine`'s own
`InitiateTakeoff`/`WorldComponent_GravshipController` machinery, a completely
separate code path from `CompLaunchable.TryLaunch`.

⇒ **`Patch_GravshipLaunched` (patching `CompLaunchable.TryLaunch`) never fires
on an actual gravship launch, successful or failed.** It only ever fires for
the OTHER things that carry `CompLaunchable` — ordinary transport pods and
shuttles. The `Patch_GravshipLaunched.cs` file's own header comment ("vanilla's
single entry point for every launch this comp can make — shuttle, transport
pod, and gravship alike... Odyssey's gravship uses the same CompLaunchable")
is factually wrong about the gravship half, and has been since the file was
written — this is a **pre-existing bug in the ORIGINAL feature's design**, not
something today's `lastLaunchTick` fix introduced or could fix. The `Notify_
Launched` hook is still real and still useful — it just means "a transport pod
or shuttle launched" for `divine_satiation_engine.md`'s "each launch/
relocation" line, not "the colony's gravship relocated," which is what the
design doc and this item's own title both actually describe.

**Consequence for THIS item's live check**: `jawa/gravship_launch` (the
bridge's only ready-made launch tool) drives `Building_GravEngine`, so
using it to "prove" this fix would have proven nothing — it never reaches
the patched method at all. Caught before making that mistake.

**What WAS checked**: no companion tool on the current bridge surface calls
`CompLaunchable.TryLaunch` on a plain pod/shuttle either — `jawa/
gravship_launch*` is gravship-only, and `CompLaunchable`'s own launch
Command_Action (`StartChoosingDestination(TryLaunch)`, read via RimSage) both
(a) needs a world-tile-choosing UI step no current bridge tool drives, and
(b) is DISABLED (never invokes its own `.action` delegate) whenever
`CanLaunch()` is false — meaning the negative half of this item's own PROVE
line can't be produced through the gizmo either; a disabled button can't be
clicked to prove clicking it does nothing. `TryLaunch` is reachable ONLY by
adding a small new companion `[Tool]` that calls it directly (a `rimbridge-
companion` job, not a same-session bolt-on) or by giving a real pod a
fueling port + fuel + a loaded pawn and completing the full player UI flow by
hand.

**Verdict**: source-side fix (`572413c0`) still stands and is still correctly
described as the right hook (`lastLaunchTick`) for WHATEVER launches through
`CompLaunchable` — the bug this item is actually about IS real, for
pods/shuttles. But this item's title and this item's own live-verify plan
both frame it as a GRAVSHIP check, and that check is not just "not yet run,"
it targets a code path that doesn't exist for gravships in the shipped game.
Left `doing`, blocked. Recommend the owner rule on scope: (a) rename/refile
this as a pod/shuttle-scoped fix and file a NEW, separate item for gravships
specifically (`Building_GravEngine`'s own takeoff path has no Ninefold hook
at all right now — a real gap, not a false-fire), or (b) if gravship coverage
was the actual intent, this whole patch needs to move to a different Harmony
target (`Building_GravEngine.InitiateTakeoff` or similar) before any live
check on "gravship" makes sense. Either way, a NEW companion tool
(`jawa/transporter_launch` or similar, calling `CompLaunchable.TryLaunch`
directly, bypassing the gizmo/world-targeter UI) is needed before the
pod/shuttle version of this PROVE/EXPECT can be run live at all.
