# NINEFOLD_GRAVSHIP_HOOK_SCOPE_1 — owner ruling needed

Split from `NINEFOLD_LAUNCH_POSTFIX_FALSE_FIRE_1` (2026-09-07 finding, filed
2026-09-08): `Patch_GravshipLaunched.cs` patches `CompLaunchable.TryLaunch`, but
Odyssey's real gravship (`Building_GravEngine`) is a plain `Building` with no
`CompLaunchable` at all — its departure runs through a completely separate
`InitiateTakeoff`/`WorldComponent_GravshipController` path. The patch has never
once fired on an actual gravship launch, successful or failed; it only fires for
ordinary transport pods and shuttles, which do carry `CompLaunchable`. This is a
pre-existing design bug (the patch's own header comment claims gravships share
the hook), not something the parent item's `lastLaunchTick` fix introduced.

## spec
Owner picks one:
- **(a) Rescope**: rename/refile this as a pod/shuttle-only Ninefold hook
  ("each launch/relocation" in `divine_satiation_engine.md` reads as any
  `CompLaunchable` departure, not specifically the gravship) — no code change
  needed beyond documentation, and file a NEW, separate item for actual
  gravship coverage (`Building_GravEngine`'s own takeoff has no Ninefold hook
  at all right now — a real gap, not a false-fire).
- **(b) Retarget**: if gravship coverage was the real intent, move
  `Patch_GravshipLaunched` to a different Harmony target
  (`Building_GravEngine.InitiateTakeoff` or equivalent, confirm exact method
  via RimSage before writing) so it actually fires on what its name promises.

Either way, proving the pod/shuttle version of the parent item's PROVE/EXPECT
live also needs a new companion tool (`jawa/transporter_launch` or similar)
calling `CompLaunchable.TryLaunch` directly — no current bridge tool reaches it
without a full player UI flow (fuel port + fuel + loaded pawn) or a
`rimbridge-companion` build session.

## verify
Owner states which of (a)/(b), or a third option. Whoever picks this up files
the follow-on gravship-coverage item (if (a)) or retargets the patch (if (b)).

## criteria
- [ ] Owner ruling recorded.
- [ ] `NINEFOLD_LAUNCH_POSTFIX_FALSE_FIRE_1`'s title/spec updated to match
  whichever scope is chosen, so it stops reading as a gravship check.
