# Graffiti concept log (verbatim questions and answers)

## Stage 1, run rm-role-designer-1794718990 (2026-11-14 21:10 PST): sent

Claim: Graffiti turns a colony's walls into a record of its people (punk tags and sigils whose quality is the painter's art skill; marks about people that move mood, opinion and occasionally a confrontation).
Attack: in a real colony it may play as a decal pack with mood numbers: the social layer either rarely fires or becomes a permanent mood tax. Proven only on staged sites over short runs.
Picture: a lived-in wall after weeks: a few tags, one mockery with a reply over it, one grudge, versus a wall of stacked debuffs and a message stream. The live walk shows which.
Review: rm-judge a1c41e1db1e3b8a64 passed all three; fixed: proof wording names the two open contradictions; 'and scrubbed' removed from flagship option C.

### a_live_walk

Graffiti is already built and its loop reported all 22 north-star bars proven on 2026-11-08 (two of those claims are still open: whether the vandal art still carries Earth-style signs, and that the proof lives in a loop clone the pipeline cannot rerun), so before any new design we propose a live walk of what exists: a lived-in colony save after several in-game weeks on ordinary walls, with a painting spree, recreation tagging, a raid's exit tags and a trader visit, and the shipped vandal marks at play zoom. It measures what we would otherwise ask you to predict: whether the social layer stays occasional or becomes a mood tax, whether the vandal art still carries Earth-style signs, and scrawl versus tally on a lived-in wall, which you asked to see again. Which way: (a) you watch it with us in one sitting, (b) an agent walks it and brings you a short set of zoomed shots, or (c) not now, argue the root first?

### a_root

Proposed root, in one sentence: "Graffiti turns a colony's walls into a record of its people: punk tags and ideoligion sigils whose quality comes from the painter's art skill, and marks about people (mockery, tribute, memorials, insults) that move mood, opinion and now and then a confrontation, all readable at play zoom in any RimWorld game." Our strongest doubt about it: in a real colony it may play as a decal pack with mood numbers attached, either the social layer almost never fires or it becomes a permanent mood tax, and only the walk can tell which. Is this the root, or which word would you change?

### a_flagship

Which scene should be Graffiti's face, the first showcase a player sees? (A) A lived-in colony wall: a mockery naming someone, a reply painted over it, a confrontation. (B) A spree corridor: one pawn's break leaving many visibly different punk marks, a skilled piece beside an ugly scrawl. (C) After a raid: the raiders' exit tags troubling the colony until the wall is retaken. The walk would show all three, so you can also answer after it.

## Stage 1, run rm-role-designer-1794721794 (2026-11-14 ~9:50 PM PST): his answers recorded

- a_root (OWNER:1794721657820999692, his words): "(1) mostly, but it should also include Raiders that oppress with left-behind threats and marks for future attacks."
  Root as recorded folds in his clause. Designer note for stage 2: exit tags (troubling until retaken) are built; a breach lure exists but the colony paints it; no mark raiders leave shapes a LATER attack (inv_raider_future_marks, absent). Argue after the walk.
- a_live_walk (OWNER:1794721663101232395, by card): (b) an agent walks, brings zoomed shots, keeps the save. Item RIMMANDRAKE_WALK_GRAFFITI_LIVED_IN_WALL_WEEKS_NOT_MINUTES.
- a_flagship (OWNER:1794721668326415311, by card): decide after the walk; stays open.

## Stage 2, run rm-role-designer-1794722090 (2026-11-14 21:58 PST): sent

Measured, not asked: c_vandal_signage settled. The shipped vandal_0..vandal_3 are abstract spray tags; the hazard bolt and prohibition sign are gone (GRAFFITI_VANDAL_REDRAW_TWO_SIGNS_GONE_LEGIT is stale). c_proof_home and c_site_settings are script gaps, routed to stage 3.

Claim: a raider mark bears on a future attack when the same faction's next raid acts on it.
Attack: a raid weeks later is the storyteller's; if the mark changes when or how hard, the player cannot trace it to the wall, and if it only changes where, it may go unnoticed. Marks also weather away in a few weeks, which bounds any threat.
Picture: (a) their next raid comes at the tagged wall, so he scrubs it, fortifies it, or builds a killbox behind it; (b) a letter and a sooner or larger raid; (c) a letter only.
Review: rm-judge a1e871e9d2b85d5c6 struck the first draft on two false phrases (marks also weather away; raider marks carry no breach lure); fixed in its own words.
a_flagship stays deferred to RIMMANDRAKE_WALK_GRAFFITI_LIVED_IN_WALL_WEEKS_NOT_MINUTES (his card).

### a_raider_next_attack

You added raiders who leave threats and marks for future attacks. Built today: a raid leaving your map paints its marks on your outer walls, and colonists feel 'enemy marks on our walls', a small mood penalty that grows with the number of marks, until someone scrubs them or the paint weathers away (a few weeks). Nothing yet links a mark to the NEXT attack. Which link: (a) aim: while that faction's mark stands, its next raid comes at the marked wall, so you choose between scrubbing it, fortifying there, or building a killbox behind it; (b) pressure: while the mark stands, that faction's next raid comes sooner or larger, announced by a letter; (c) threat only: a letter naming the faction and its promise to return, with no change to the raid itself? We recommend (a): you can watch it work, it gives you a choice, and part of it exists (breaching raids already aim at a wall carrying a colonist-painted warning glyph; raiders' own marks don't carry that lure yet); (b) adds difficulty you cannot trace back to the wall.

## Stage 2, run rm-role-designer-1794728785 (2026-11-14 23:47 PST): both asks answered

- a_flagship (OWNER:1794728091811038301, his words): "It's not easy for me to understand this decision, but I'd say B." → showcase 1 is the spree corridor; his lean, revisit cheaply at the showcase stage.
- a_raider_next_attack (OWNER:1794728164229812842, by card): "Sooner or bigger raid" → (b) pressure, over our recommended (a) aim.
  What moved us: his pick, not a new argument. Our objection to (b) was untraceable difficulty; the letter he chose is the trace. Derived (agent, undoable, d_raider_pressure_traceable): the letter names the faction and its standing mark; the last mark scrubbed or weathered lifts the pressure; sooner-vs-larger and its size are Mod Settings tuning.
- No ask is sent; no core contradiction is open (c_proof_home, c_site_settings are script gaps routed to stage 3). Stage 2 done.

## Stage 3, run rm-role-designer-1794729618 (2026-11-15 ~00:10 PST): written

- sheet.md, tree.json (28 leaves, one walk), plan.md, scenes.json (28 scenes, 4 showcases, 3 coverage_rest), floor.json.
- Filed: RIMMANDRAKE_CHECK_GRAFFITI_SITE_SETTINGS_SIX_OF_EIGHT (c_site_settings; acceptance test watched failing),
  RIMMANDRAKE_BUILD_GRAFFITI_RAIDER_PRESSURE_LETTER_NAMES_THE_WALL (d_raider_pressure, no build yet),
  RIMMANDRAKE_SCRIPT_GRAFFITI_CORRIDOR_WALK_AND_WALL_LOSS_SCENES (flagship corridor, wall loss, walk entry points).
  c_proof_home routes to the existing RIMMANDRAKE_CLAIM_GRAFFITI_MUST_SHOWS_TWELVE_LEFT_BARE, named on twelve scenes.
