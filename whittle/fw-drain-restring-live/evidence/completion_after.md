### GimmeSomeSlack (as of 2026-11-11)

**Headline:** 90.0% of 30 inventory entries verified working at L2+ (10.0% with a failing latest L2 row); art explicitly accepted 43.9% of in-use slots (+56.1% only seen, unchanged, in an owner whole-mod walk); settledness **slowing** (bugs filed last 2 wk 4 vs prior 2 wk 9); 5 open bug items; 0 items waiting on the owner. No composite score: the parts do not share a unit.

**1. Inventory** 30 entries: {'ThingDef': 4, 'JobDef': 1, 'HediffDef': 1, 'Switch': 24}. Raw def types: {'MapMeshFlagDef': 2, 'ThingDef': 4, 'DesignationDef': 1, 'JobDef': 1, 'WorkGiverDef': 1, 'ThingStyleDef': 40, 'HediffDef': 1, 'HistoryEventDef': 1}.

**2. Works** {'works': 27, 'broken': 3} from 164 live proof runs (164 result files), 31 L2+ verify events, 0 player truths; 0 'works' credited by label match only, 7 only by an owner whole-mod walk (UNROUTABLE_CORD_BUILD_DIVE_THROUGH_WALLS L4 2026-10-16 @fc932419a783: GimmeSomeSlack all looks great! Verified.).

| type | works | broken | offline-only | unverified |
|---|---|---|---|---|
| HediffDef | 1 | 0 | 0 | 0 |
| JobDef | 1 | 0 | 0 | 0 |
| Switch | 21 | 3 | 0 | 0 |
| ThingDef | 4 | 0 | 0 | 0 |

Broken (3): keepWiresOnGravship <- GSS_SWITCHES_PROVE_LAST_FOUR_STANDING:A2 (2026-10-29); cutWiresOnOwnerChange <- GSS_SWITCHES_PROVE_LAST_FOUR_STANDING:A2 (2026-10-29); slideUnder <- GSS_SWITCHES_PROVE_LAST_FOUR_STANDING:A2 (2026-10-29)

Unverified (0): 

**3. Art** 125 live texture slots, 114 reached by a def texPath or C# literal; owner-accepted 53 (50 in use). By class: {'owner-kept (not referenced by a def texPath or C# literal)': 3, 'owner-kept': 49, 'owner-kept-sheet': 1, 'owner-walked (not referenced by a def texPath or C# literal)': 8, 'owner-walked': 64}. Regen-looping (>=2 rounds): none. texPaths with no art: 0 of 24 [].

**4. Waiting on owner** 0: 

**5. Settledness (ISO week starting)**

| week | bugs filed | code reviews | defects from code review | live runs | MOD fail rows / MOD rows | L2 verifies not-pass / all | live-found bugs | refiled |
|---|---|---|---|---|---|---|---|---|
| 2026-09-28 | 0 | 0 | 0 | 126 | 55 / 2280 | 0 / 0 | 0 | 0 |
| 2026-10-05 | 0 | 98 | 0 | 25 | 26 / 1974 | 0 / 5 | 0 | 0 |
| 2026-10-12 | 2 | 123 | 0 | 7 | 4 / 234 | 1 / 3 | 2 | 0 |
| 2026-10-19 | 3 | 55 | 0 | 3 | 3 / 20 | 0 / 5 | 2 | 1 |
| 2026-10-26 | 4 | 49 | 1 | 0 | 0 / 0 | 6 / 7 | 3 | 0 |
| 2026-11-02 | 4 | 9 | 0 | 1 | 0 / 145 | 8 / 11 | 3 | 1 |
| 2026-11-09 | 0 | 75 | 0 | 2 | 0 / 36 | 0 / 0 | 0 | 0 |

Refiled/regression items: 2 ['GSS_RECOLOR_CHECK_FIX_NECKED_JUNCTIONS', 'GSS_WATER_STUB_FIX_PASSED_LAST_WEEK']
