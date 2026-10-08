# Huge Things full GPT review: triage

Source: `Transient/huge_things_bounds_2026-10-07/GPT_FULL_REVIEW.md` (item `HUGE_THINGS_GPT_REVIEW_1`). IDs are GPT's: `<part><section>.<n>`.

**How claims were checked.** Every bug finding was read against our code at `c954ccdca`. Every engine claim was checked against the RimWorld 1.6 decompile through RimSage. GPT's own engine links point at the `Chillu1/RimWorldDecompiled` mirror, which is not pinned to our build, so none of them count as measurements. Three verification passes ran: plants (A), titans and concept (B/D), and seam and tests (C).

There are four buckets:
- **fix-now**: verified and mechanical, or already ruled by the owner. Filed for FOUNDRY.
- **owner**: needs his decision. The questions are below.
- **later**: an idea. Nothing is filed.
- **rejected**: the reason is given.

## Counts

| bucket | findings (328 numbered GPT findings; each ID counted once, in its first bucket) |
|---|---|
| fix-now | 46, filed as 9 items |
| owner | 18, asked as 8 questions plus one scope note |
| later | 247 (nearly all of sections 4–6) |
| rejected | 17 (12 of them are praise or confirmation, not findings) |

## Section 3 — bugs (every one)

| ID | verdict on 1.6 | bucket | filed / question |
|---|---|---|---|
| A3.1 already-sealed room can be closed with a pawn inside | CONFIRMED (`RM_HugeClaimsKernel.cs:130,168`; 1.6 `TryRecoverFromUnwalkablePosition` only rescues a pawn standing on an unwalkable cell) | owner | Q6 |
| A3.2 one giant can split a corridor in two | CONFIRMED (`Reach` seeds from every window-border cell) | owner | Q6 |
| A3.3 `accepted.Sort` throws away the safe closure order | CONFIRMED. It only matters when a later spawn fails, so it is lower severity than GPT says | fix-now | PLANT_FOOTPRINT_HARDENING_1 |
| A3.4 interaction-cell guard misses blueprints/frames and multiple cells | CONFIRMED (`MapComponent_HugeFootprints.cs:310`; 1.6 `InteractionCellsWhenAt` and `GenConstruct.NotBlockingAnyInteractionCells` resolve `entityDefToBuild`) | fix-now | PLANT_INTERACTION_GUARDS_1 |
| A3.5 an item move can fail half-way, leaving an item unspawned | CONFIRMED on exceptional paths (`:252` DeSpawn outside try; `:261` fallback unguarded) | owner | Q8 |
| A3.6 moving an item fires real despawn events (quest "Despawned", reservations) | CONFIRMED (1.6 `Thing.DeSpawn`) | fix-now (skip `questTags` items) + owner (policy) | PLANT_INTERACTION_GUARDS_1, Q8 |
| A3.7 the damage dedup key merges distinct same-tick projectiles | CONFIRMED (`Building_TrunkBlocker.cs:61-63`; 1.6 `Bullet.Impact` has one DamageInfo per projectile) | fix-now (dedup only area events; a single projectile forwards un-deduped) | PLANT_INTERACTION_GUARDS_1 |
| A3.8 growth is read before vanilla applies that tick's growth | CONFIRMED (1.6 `Plant.TickLong`: `base.TickLong()` runs before `growthInt +=`) | fix-now | PLANT_FOOTPRINT_HARDENING_1 |
| A3.9 a rejected renderer still gets single-quad selection | CONFIRMED, and it is intentional in the code | owner | Q7 |
| A3.10 unmeasured graphics (immature/leafless/polluted) get adult collision | CONFIRMED (`CompHugeFootprint.cs:163`; 1.6 `Plant.Graphic` switches) | owner | Q7 |
| A3.11 the pending/relabel passes ignore the refresh budget | CONFIRMED (stall size UNMEASURED) | fix-now (pending index, relabel on change) | PLANT_FOOTPRINT_HARDENING_1 |
| A3.12 malformed opt-in data reaches runtime | PARTLY (ConfigErrors exists but omits ranges and null `<li>`; nothing consults it at runtime) | fix-now | PLANT_FOOTPRINT_HARDENING_1 |
| B3.1 corpse destroyed inside `Pawn.Kill`'s own spawn | CONFIRMED lifecycle (1.6 `Kill` keeps using the corpse after placement); a crash is not proven | fix-now (defer one tick, revalidate) | CORPSE_SITE_SAFETY_1 |
| B3.2 conversion destroys identity, gear and resurrection | CONFIRMED (1.6 `Corpse.Destroy` → `PostCorpseDestroy`) | owner | Q1 |
| B3.3 site spawn result ignored; the 4×4 edifice wipes buildings under it | CONFIRMED (`isEdifice` defaults true; `SpawningWipes`) | fix-now (check result, keep the corpse on failure, never wipe) | CORPSE_SITE_SAFETY_1 |
| B3.4 impassable obstacles prevent the wake that would smash them | CONFIRMED in mechanism. Card #1 (2026-09-09) already rules "smashes through anything built" | fix-now (owed by ruling) | TITAN_BREAKTHROUGH_CLEARING_1 |
| B3.5 thick roof only slows, at the anchor cell | CONFIRMED (`Patch_ThickRoofAvoidance.cs:84,105`). Card #1 rules "a titan never paths under rock". The downgrade to slowing was an agent's, not his | fix-now (owed by ruling) | TITAN_ROOF_AVOIDANCE_1 |
| B3.6 multi-cell buildings take one blow per covered cell | CONFIRMED (1.6 `ThingGrid.Register` registers every cell) | fix-now | TITAN_WAKE_FIXES_1 |
| B3.7 a redundant `Position` assignment fires the wake | CONFIRMED (1.6 setter returns early when the value is equal; the postfix still runs) | fix-now | TITAN_WAKE_FIXES_1 |
| B3.8 flying titans crush ground objects | CONFIRMED (`Pawn.Flying` exists in 1.6; never checked) | fix-now | TITAN_WAKE_FIXES_1 |
| B3.9 a rotten or scaria corpse becomes a fresh pool | CONFIRMED | owner (eligibility); the ordering half is in B3.1 | Q1 |
| B3.10 extra butcher products (body parts, base products) are dropped | CONFIRMED (1.6 `Pawn.ButcherProducts`) | owner | Q1 |
| B3.11 the pool is decremented before placement succeeds | CONFIRMED (1.6 `GenPlace.TryPlaceThing` can leave a remainder) | fix-now | CORPSE_SITE_SAFETY_1 |
| B3.12 a missing yield def leaves a never-draining pool | CONFIRMED | fix-now | CORPSE_SITE_SAFETY_1 |
| B3.13 disabling the corpse feature leaves existing sites ticking and harvested | CONFIRMED | owner | Q2 |
| B3.14 yield jumps ~41% at T2 | CONFIRMED (`sqrt(4/8)` → 1.0) | owner | Q3 |
| B3.15 Large Pawns' own wall-break is still on | CONFIRMED. The closed item orders it OFF; no code does it | fix-now (owed by ruling) | LARGEPAWNS_BRIDGE_HARDENING_1 |
| B3.16 a bridge failure leaves a half-rewritten config and a false success log | CONFIRMED | fix-now | LARGEPAWNS_BRIDGE_HARDENING_1 |
| B3.17 Large Pawns force-in rows pin adult size while tier uses current size | PARTLY (row precedence inside Large Pawns is not checked) | later (needs Large Pawns API read; fold into the bridge item's investigation) | — |
| B3.18 / C3.4 a race growing past its base size never gets the wake comp | CONFIRMED (1.6 `Pawn.BodySize = factor × base`; `DefQualifies` uses base only) | fix-now | TITAN_WAKE_FIXES_1 |
| B3.19 / C3.6 / D3.3 numeric settings not validated on load | CONFIRMED (only 3 fields sanitised; `ThresholdsValid` accepts ∞) | fix-now | HUGETHINGS_SETTINGS_HARDENING_1 |
| C3.1 local-border reachability can allow a globally trapping closure | CONFIRMED (same as A3.1/A3.2) | owner | Q6 |
| C3.2 item destinations are reserved for sources the planner then refuses | CONFIRMED in kernel and production (`PlanItemMoves` before `Planner.Plan`) | fix-now | PLANT_FOOTPRINT_HARDENING_1 |
| C3.3 pawn hitbox ignores female/alternate body graphics | CONFIRMED (1.6 `PawnRenderNode_AnimalPart.GraphicFor`) | fix-now | PLANT_INTERACTION_GUARDS_1 |
| C3.5 movement-triggered smash cannot breach a blocked route | CONFIRMED (= B3.4) | fix-now (owed by ruling) | TITAN_BREAKTHROUGH_CLEARING_1 |
| C3.7 validation.py restores defaults, not the user's settings | CONFIRMED for trunk and wake (`_restore` → `DEFAULTS`; trunk hard-codes True) | fix-now | HUGETHINGS_TEST_HONESTY_1 |
| C3.8 a zero-scale fuzz run prints ALL PASS having run nothing | CONFIRMED by reading (`dotnet` is absent, so it was not run) | fix-now | HUGETHINGS_TEST_HONESTY_1 |
| C3.9 `python -O` turns every offline assert into a pass | CONFIRMED | fix-now | HUGETHINGS_TEST_HONESTY_1 |
| C3.10 explosion redirect ignores `ignoredThings` for the blocker | CONFIRMED (1.6 `ExplosionDamageThing` checks `ignoredThings` on the swapped-in plant) | fix-now | PLANT_INTERACTION_GUARDS_1 |
| D3.1 / D1.4 thick roofs traversable | = B3.5 | fix-now (ruling) | TITAN_ROOF_AVOIDANCE_1 |
| D3.2 GiantSmash stops before the plant falls | = B3.4 | fix-now (ruling) | TITAN_BREAKTHROUGH_CLEARING_1 |
| D3.4 corpse site is damage-proof cover | CONFIRMED (`useHitPoints=false`; 1.6 `DamageWorker.Apply`) | owner | Q4 |
| D3.5 existing sites under the animal-master-off promise | = B3.13 | owner | Q2 |
| D3.6 alternate graphics get collision from another picture | = A3.10 | owner | Q7 |

## Sections 1, 2 and 4 — review, implementation, challenges

| ID(s) | bucket | note |
|---|---|---|
| A2.3 Reconcile/RealizePending lack per-owner exception isolation | fix-now | CONFIRMED `:103,110,138`. In PLANT_FOOTPRINT_HARDENING_1 |
| A2.6 / C2.8 / D2.5 ThingsUnderMouse HashSet+lambda allocation on every 2+ list | fix-now | CONFIRMED `HugeThingsCore.cs:140-145`. In PLANT_FOOTPRINT_HARDENING_1 |
| A2.7 / D1.5 trunk-damage checkbox says "cover" but controls damage; no translation keys | fix-now | CONFIRMED `RM_HugeThingsSettings.cs:137`. In HUGETHINGS_SETTINGS_HARDENING_1 |
| B2.4 position hook probes comps before reading the wake gate | fix-now | CONFIRMED. In TITAN_WAKE_FIXES_1 |
| B2.6 roof comment claims a "40-hour" step; 1.6 `CostToPayThisTick` caps a step at about 450 ticks | fix-now | CONFIRMED. The comment fix rides TITAN_ROOF_AVOIDANCE_1 |
| B4.6 rubble chance is per footprint cell (about 5.6 attempts per 4×4 step) | fix-now (label "per footprint cell") | HUGETHINGS_SETTINGS_HARDENING_1. Whether to roll once per step is later |
| C2.5a fuzz header says "whole-board" but floods the window | fix-now | HUGETHINGS_TEST_HONESTY_1 |
| C2.5c CaseCache discards selection when blocking is off; no recompute counter | fix-now | HUGETHINGS_TEST_HONESTY_1 |
| C2.5d PawnHitbox union never fuzzed | fix-now (the kernel half) | HUGETHINGS_TEST_HONESTY_1 |
| C2.6 boundary nudges sit inside the oracle's ambiguity band | fix-now | HUGETHINGS_TEST_HONESTY_1 |
| C4.9 / D2.1 exact-namespace patch discovery silently drops a moved patch | fix-now (startup assertion) | PLANT_FOOTPRINT_HARDENING_1 |
| B1.6, D1.7, D5.7 corpse harvest needs player control | owner | Q5 |
| B1.2 the closed item overstates completion (corpse camps, scavenger draw, footfall warning, titan events) | owner-visible note | Cards #4–5 are ruled, and no live item carries camps, scavengers or footfall-warned events. This is reported to him, not filed (it is scope, his call) |
| B1.7 spoilage ignores temperature | later | |
| B1.4, D4.3 Large Pawns absent means a 1-cell titan | later | Diagnostics or status line |
| A2.5, D2.4, A4.1, C4.8, B4.5 entity-count and performance benchmarks | later | Belongs to the live walk (`huge_titan_walk_plan_2026-10-07.md`) |
| A2.10–A2.20 status of the earlier GPT_REVIEW findings | later | Covered by the bug rows above |
| A2.21, B2.1, C2.2, C2.3, C2.9, C4.4 kernels are not engine coverage; validation.py is static-only | later | Already the known shape. TITANIC_BODYSIZE_TEST_RACE_1 owns the not-driven titan rows |
| C2.4 settings roundtrip doesn't exercise Scribe | later | Needs a save/load harness |
| C2.5b CaseSmashStep doesn't drive production routes | later | Needs the game |
| B2.5, B4.10 harvest progress lost on job replacement | later | |
| B2.7 crush-rule ConfigErrors / precedence | later | |
| B2.8, C4.3, C1.5 effective vs pending restart settings display; reset to defaults | later | |
| B2.11, B4.1–B4.4, C4.7, D4.10 walk-plan adversarial lanes (sealed lane, protected objects, corpse lifecycle matrix) | later | Feed the walk plan when it runs |
| A1.3, A1.4, A1.5, A1.7, D1.2, D1.6, D1.8, D1.9, D1.10 concept notes (overlay, inspect summary, roster audit) | later | |
| A4.2–A4.12, B4.7–B4.12, C4.1–C4.6, D4.1–D4.9 remaining challenges | later | Flight-over-trunk policy (A4.6), gravship departure (A4.9), raids vs blockers (A4.10), layer scoping (D4.9), forced displacement (C4.5/D4.1) are the notable ones |

## Sections 5 and 6 — opportunities and extensions

All of these are **later** (nothing filed): A5.1–A5.8, B5.1–B5.8, C5.1–C5.6, D5.1–D5.12, A6.1–A6.29, B6.1–B6.32, C6.1–C6.20, D6.1–D6.45.

The strongest ideas, in priority order:
1. **Footprint and tier inspector overlay** (A5.3, B5.1, C5.2, D5.3): solid, deferred and accessible cells, plus tier and crush role. It serves players, compatibility diagnosis and the walk at once.
2. **Public queries and coarse events** (A5.1–5.2, B5.3, D5.1–5.2): `RealizedGroundCells`, `OwnersAtCell`, `Footstep`, `OwnerDestroyed`, `CorpseSiteCreated`. Every sibling-mod idea below rides on these.
3. **Generic corpse product pool** (B5.5, D5.9, B6.11–12, D6.25): mechanical titans such as the borehulk yield salvage through the same harvest job (WreckedMachines, AssailantSalvage).
4. **Three campaign integrations that exercise different foundations** (D6.45): a warned desert salvage passage (AcousticScanner footfalls → Traces → Wreckage); a contested corpse camp (RimProperty, TheBazaar, Inhabited, RaidRedesigner); a seabed whale-fall on `RM_SeabedLayer` (B6.21, C6.19, D6.33).
5. **Ecology hooks**: TheRot decomposer succession on exhausted sites (B6.3, D6.17); FlowWorks treats realized trunk cells as opt-in hydraulic obstacles (A6.3, D6.19); ExplosiveGrowth soak-driven footprint growth (A6.2, D6.18).
6. **Ideology**: "waste nothing" and "leave the elder standing" precepts, plus a First Cut ritual (A6.22, B6.28–29, D6.37–39).
7. **Crush-rule explainer** in dev mode: "why does this survive?" (B5.2, D5.5).

Rule check: no idea needs worldgen. D6.43 is explicitly map-gen only. Heat ideas route to vanilla temperature, and titan appearances outside the home biome stay scripted events (card #5).

## Rejected

| ID(s) | reason |
|---|---|
| A2.8, B2.9, D2.3 migrate the old TitanicCreatures settings file | The mod never shipped to players, and the merge design measured no such file on the owner's machine. There is nothing to migrate |
| B1.5, B4.7 protect friendly titans' owners from wake damage | Card #5: *"Wake damage applies to any structure including the player's — that is the point."* (The inspect-UI half is in later) |
| B1.8 "untouched sites disappear in about a week" wording | A documentation nit inside the yield/spoilage question. It is folded into Q3 rather than filed |
| GPT's claim that the Chillu1 mirror is 1.6 (part B preface) | Not a finding about the mod. Every engine claim was re-measured on 1.6 via RimSage instead |
| C2.5e measured masks checked against the same tool | Generic. Independent ground truth for "ground contact" is the owner's eye on the walk, already planned |
| A1.1, A1.2, A1.6, A2.1, A2.2, B1.1, B1.9, C1.1, C1.2, C2.1, D1.1, D2.2 | Praise or confirmation, not findings |

## Owner questions (plain language, ready for a card)

**Q1 — What happens to a giant's body when it becomes a harvest site?** When a colossal creature dies, its body is deleted and replaced by a meat-and-leather pile. That loses its name, any gear, any chance of resurrection, and extras like horns or ivory. A body that had already rotted also comes back as fresh meat. How should it work?
- (a) Keep the real body inside the site. Name, resurrection, funerals and extra parts survive, and rot carries over. This is the most work and the safest.
- (b) Only fresh, wild, unnamed carcasses become sites. Tamed, named or rotten ones stay ordinary corpses. This is simple, but those giants then lie as a one-cell corpse.
- (c) Keep the pile, but copy the extra parts and the rot state into it. This is the middle road. Names and resurrection are still lost.

**Q2 — If corpse sites are switched off mid-game, what happens to the ones already on the map?**
- (a) They stay and can still be harvested, but they stop spoiling and no new ones appear.
- (b) They disappear and their meat and leather are lost.
- (c) They turn back into ordinary corpses. This is only possible with Q1 (a).

**Q3 — Meat and leather jump about 40% the instant a creature reaches body size 8 (Tier 2). Smooth it, or keep the jump?**
- (a) Smooth curve: yield grows steadily with size.
- (b) Keep the jump: tiers feel distinct, and a Tier 2 kill is a noticeable prize.

**Q4 — A titan carcass is currently indestructible cover in a firefight. Should it be?**
- (a) Yes, indestructible cover (current).
- (b) Gunfire and explosions eat into its remaining meat and leather.
- (c) It has ordinary hit points and can be blown apart.

**Q5 — Should miners carve up a titan carcass automatically, or only when you mark it?**
- (a) Automatically, like now.
- (b) Only when designated, like hunting an animal.
- (c) Automatically, with a pause button on each carcass.

**Q6 — A growing giant plant can close the last gap of a sealed room with a colonist inside, or cut a path in two. The safety check only looks a short distance around the plant. How strict should it be?**
- (a) A stricter local rule: never close a gap that would split any open area near the plant. Roots end up with more walk-through gaps.
- (b) A full map check before each root cell closes. This is exact, but it costs speed on maps with big forests.
- (c) Keep it as is, and send a letter ("a colonist is trapped by the Pale Tree — cut it") when it happens.

**Q7 — Young, leafless or polluted versions of a giant plant have different art from the adult, but they all get the adult's solid trunk shape. Which fix?**
- (a) Measure every art version of every giant plant. This is exact, and it is art-tool work.
- (b) Until a version is measured, it gets no solid trunk, so colonists walk through it.
- (c) Keep using the adult shape for all of them.

**Q8 — When roots grow over a cell holding items, the items are moved to a free cell nearby. Rarely the move can fail and lose an item, and a move can disturb a quest item or a haul in progress. Which rule?**
- (a) Never move items. The root waits until the cell has been hauled clear.
- (b) Move them with a full undo, plus a safe holding box if a move fails. This needs more code.
- (c) Keep moving items, but skip quest items and anything someone is about to carry.

**Also for him (scope, not a defect):** cards #4 and #5 of 2026-09-09 rule corpse camps, scavenger draw, and titan events with footfall warnings. None of them is built, and no live item carries them.
