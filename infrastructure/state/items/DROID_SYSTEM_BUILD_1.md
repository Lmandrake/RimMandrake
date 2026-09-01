# DROID_SYSTEM_BUILD_1 — build the unifying droid platform

REOPENED by the owner 2026-08-29 (verbatim): "We've fallen in love with the full
droid item and would like you to fully work it out into a buildable spec. The
idea is that we will not build on any one of the packs, they all have too many
flaws. Rather, we will borrow from them and make our own... We would want to
port all the droids in the game to that one platform, whether we make it or not."

## Spec
`design/Jawa/droid_system_build_spec.md` — architecture (own DLL + HAR substrate,
packs demoted to asset libraries), five-state engine mapping, 14-unit C# work
breakdown, three port waves + strays, phase plan with per-phase proofs.
Design intent: `design/Jawa/droid_system_spec.md`. Verb authority:
`design/Jawa/droid_verbs_decisions.json` (FROZEN).

## Verify
Phase 0 proof on quicktest: pilot chassis (gonk) completes
spawn → ion-down → capture → bolt → wipe → kill → rebuild → detonation-scales-
with-charge, plus the edge-case matrix (caravan, pod, surgery-on-object,
storyteller targeting, no-food-need, drafted at 0 power).

## Criteria
- [x] Owner rules the §8 opens (name, race granularity, JDS identity, port timing)
      — all four closed 2026-09-01 (three already ruled 2026-08-29); see
      `canon.yml` `droid_system`. **Build greenlit, no longer parked.**
- [ ] Phase 0 skeleton + pilot proven live
- [ ] Port manifest MEASURED (census sweep) and waves 1-3 executed at save boundaries
- [ ] Packs' redundant systems in Cherry Picker; DroidsAreMachines retired per-wave
