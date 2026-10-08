# FLYER_STABLE_BODY_GATE_1 — no flyer static is approved unless it can become a stable-body flip-book

> Owner, 2026-10-08 (relayed to the study helper by BENCH): *"We probably want to go back and look at all the flyers
> to do a similar study of how you can prompt correctly to stabilize that body for the flyers. There's a lot of flyers
> that we're going to need to regenerate as soon as we get the official versions looking good in the static imagery.
> We don't want to settle on static images that look good but cannot be converted to flyers."*
>
> And on the construction reference: *"The Star Wars donor mod did have some excellent stable flyers. They simply
> were extremely cartoonish, so we can't use them, but they are good to study."*

**Study (read first):** `Transient/flyer_stable_body_study_2026-10-08.md`. Census: `Transient/flyer_census_2026-10-08.csv`
(script `Transient/flyer_census_2026-10-08.py`, which carries a sanity probe). Sheets:
`Transient/flyer_study_2026-10-08/{sample,keeps}_contact.png`. Pilot it builds on and must be reconciled with:
`Transient/sketto_design_2026-10-08.md` (every `[R]` value in study §3 is an assumption until that pilot lands).

## spec
- 72 flyers MEASURED 2026-10-08 (64 of ours by `MaxFlightTime`, 2 should-fly, 1 owner call, 5 donor-only). Not one has
  a flip-book that is both our style and body-locked: 38 none, 15 donor-cartoon copies, 13 generated (9 of them one frame),
  5 donor bundle, 1 borrowed vanilla chicken.
- 13 of the 19 judgeable owner-KEPT statics fail or partly fail the gate (study §2).
- Recipe (study §3.1): a body master per facing with wings folded, then wing-only transparent layers per pose,
  composited offline, so the body is identical by construction. This produces whole-body flip-book PNGs. It is never a
  Spastic wing render-tree.
- Gate G1–G5 plus the flip-book body-lock test (study §3.2); `flyer:` column on review sheets (§3.5).
- Regeneration order: tiers 0–4 in study §4, about 762 jobs base for 65 flyers (about 1,000 with sex and juvenile variants).

## scope
The regeneration of every flyer's static body (where it fails the gate) and its flip-book, in study §4 order.
Also the tooling recommendations in §4 (`fill_queue` `flyer`/`plan` flag, `flipbook_compose.py`, `enact` and sheet
changes). Related: `FLYER_FLIPBOOK_ART_1` (its frame-chain recipe is the unlocked shape this item replaces; fold it in
or supersede it, which is BENCH's call). Outside art: `MaxFlightTime` is owed on `RM_BloodropMoth` and `RSW_FacetMoth`,
and `RM_Thozzik`'s family has no wings drawn.

## criteria
- The Sketto pilot's measured threshold replaces every `[R]` value in the study.
- No flyer's static is ruled `keep` on a sheet without its `flyer:` cell showing.
- Each regenerated flip-book passes the body-lock test, by its script's exit code, before he sees it.
- Flight is verified by a `Pawn_FlightTracker` state read and never by an unattended live visual hunt.

NEXT: decide whether to hold the 28 in-flight `regen_gt_pekopeko_flying_*` / `regen_gt_hawkbat_flying_j_*` jobs (unlocked recipe), then reconcile study §3 `[R]` values with the Sketto pilot.
